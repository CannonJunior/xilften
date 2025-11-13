#!/usr/bin/env python3
"""
Multi-Source Soundtrack Loading Script

Loads soundtracks for movies using multiple data sources (IMDB, MusicBrainz, etc.)
with detailed reporting on which sources were successful.

Usage:
    python scripts/load_soundtracks_multi_source.py --batch-size 10
    python scripts/load_soundtracks_multi_source.py --batch-size 5 --test-movie "Blade Runner"
"""

import sys
import os
import argparse
import asyncio
import logging
import httpx
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:7575/api"


def get_movies_without_soundtracks(limit: int = 10) -> List[Dict]:
    """
    Query database to find movies without soundtracks.

    Args:
        limit (int): Maximum number of movies to return

    Returns:
        list: List of movie dictionaries with id, title, release_date, imdb_id
    """
    try:
        conn = db_manager.get_duckdb_connection()

        # Query movies that don't have soundtracks, include IMDB ID for better matching
        query = """
            SELECT m.id, m.title, m.release_date, m.imdb_id
            FROM media m
            WHERE m.media_type = 'movie'
            AND m.id NOT IN (SELECT DISTINCT media_id FROM soundtracks)
            ORDER BY m.popularity_score DESC NULLS LAST
            LIMIT ?
        """

        results = conn.execute(query, [limit]).fetchall()

        movies = []
        for row in results:
            movie = {
                'id': row[0],
                'title': row[1],
                'release_date': row[2],
                'imdb_id': row[3]
            }
            movies.append(movie)

        return movies

    except Exception as e:
        logger.error(f"❌ Error querying movies: {e}")
        return []


async def search_soundtrack_via_api(
    media_id: str,
    title: str,
    year: Optional[int],
    imdb_id: Optional[str] = None
) -> Dict:
    """
    Search and save soundtrack via API with multi-source support.

    Args:
        media_id (str): Media ID
        title (str): Movie title
        year (int, optional): Release year
        imdb_id (str, optional): IMDB ID for better matching

    Returns:
        dict: API response with source information
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "media_id": media_id,
            "movie_title": title,
            "year": year
        }

        # Add IMDB ID if available
        if imdb_id:
            payload["imdb_id"] = imdb_id

        try:
            response = await client.post(
                f"{API_BASE_URL}/soundtracks/search",
                json=payload
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return {"success": False, "message": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"success": False, "message": str(e)}


async def load_soundtracks_batch(batch_size: int = 10, test_movie: Optional[str] = None):
    """
    Load soundtracks for a batch of movies using multi-source approach.

    Args:
        batch_size (int): Number of movies to process
        test_movie (str, optional): Specific movie title to test
    """
    logger.info("=" * 80)
    logger.info(f"🎵 MULTI-SOURCE SOUNDTRACK LOADING (batch size: {batch_size})")
    logger.info("=" * 80)
    logger.info("")

    # Get movies without soundtracks
    if test_movie:
        logger.info(f"🔍 Searching for specific movie: {test_movie}")
        conn = db_manager.get_duckdb_connection()
        query = """
            SELECT m.id, m.title, m.release_date, m.imdb_id
            FROM media m
            WHERE m.media_type = 'movie'
            AND LOWER(m.title) LIKE LOWER(?)
            AND m.id NOT IN (SELECT DISTINCT media_id FROM soundtracks)
            LIMIT 1
        """
        results = conn.execute(query, [f"%{test_movie}%"]).fetchall()
        movies = [{
            'id': row[0],
            'title': row[1],
            'release_date': row[2],
            'imdb_id': row[3]
        } for row in results]
    else:
        logger.info(f"📊 Finding movies without soundtracks...")
        movies = get_movies_without_soundtracks(limit=batch_size)

    if not movies:
        logger.info("ℹ️  No movies found without soundtracks!")
        return

    logger.info(f"Found {len(movies)} movies without soundtracks")
    logger.info("")

    # Track results by source
    loaded = 0
    not_found = 0
    errors = 0
    source_stats = {}

    for i, movie in enumerate(movies, 1):
        try:
            title = movie['title']
            media_id = movie['id']
            imdb_id = movie.get('imdb_id')

            # Extract year from release_date
            year = None
            if movie.get('release_date'):
                try:
                    year = int(str(movie['release_date'])[:4])
                except (ValueError, TypeError):
                    pass

            imdb_info = f" [IMDB: {imdb_id}]" if imdb_id else ""
            logger.info(f"[{i}/{len(movies)}] 🎵 Processing: {title} ({year if year else 'Unknown'}){imdb_info}")

            # Search and save soundtrack via API
            result = await search_soundtrack_via_api(media_id, title, year, imdb_id)

            if result and result.get('success'):
                # Extract source information if available
                source = result.get('source', 'unknown')
                source_stats[source] = source_stats.get(source, 0) + 1

                logger.info(f"  ✅ Successfully loaded from {source.upper()}!")
                logger.info(f"     Tracks: {result.get('tracks_count', 'unknown')}")
                loaded += 1
            else:
                message = result.get('message', 'Unknown error') if result else 'API error'
                logger.info(f"  ⚠️  {message}")
                not_found += 1

            # Rate limiting (be respectful to IMDB)
            await asyncio.sleep(2.0)

        except Exception as e:
            logger.error(f"  ❌ Error processing {movie.get('title', 'Unknown')}: {e}")
            errors += 1

    logger.info("")
    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"✅ Soundtracks loaded: {loaded}")
    logger.info(f"⚠️  Soundtracks not found: {not_found}")
    logger.info(f"❌ Errors: {errors}")

    if source_stats:
        logger.info("")
        logger.info("📊 BY SOURCE:")
        for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {source.upper()}: {count}")

    logger.info("=" * 80)


async def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Load soundtracks from multiple sources (IMDB, MusicBrainz, etc.)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of movies to process (default: 10)'
    )
    parser.add_argument(
        '--test-movie',
        type=str,
        help='Test with a specific movie title'
    )

    args = parser.parse_args()

    await load_soundtracks_batch(
        batch_size=args.batch_size,
        test_movie=args.test_movie
    )
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
