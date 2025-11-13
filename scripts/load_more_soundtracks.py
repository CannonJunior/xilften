#!/usr/bin/env python3
"""
Load More Soundtracks Script

Queries database directly to find movies without soundtracks,
then uses the API to load soundtrack data.

Usage:
    python scripts/load_more_soundtracks.py --batch-size 10
"""

import sys
import os
import argparse
import asyncio
import logging
import httpx

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


def get_movies_without_soundtracks(limit: int = 10):
    """
    Query database to find movies without soundtracks.

    Args:
        limit (int): Maximum number of movies to return

    Returns:
        list: List of movie dictionaries
    """
    try:
        conn = db_manager.get_duckdb_connection()

        # Query movies that don't have soundtracks
        query = """
            SELECT m.id, m.title, m.release_date
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
                'release_date': row[2]
            }
            movies.append(movie)

        return movies

    except Exception as e:
        logger.error(f"❌ Error querying movies: {e}")
        return []


async def search_soundtrack_via_api(media_id: str, title: str, year: int):
    """
    Search and save soundtrack via API.

    Args:
        media_id (str): Media ID
        title (str): Movie title
        year (int): Release year

    Returns:
        dict: API response
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "media_id": media_id,
            "movie_title": title,
            "year": year
        }

        try:
            response = await client.post(
                f"{API_BASE_URL}/soundtracks/search",
                json=payload
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None


async def load_soundtracks_batch(batch_size: int = 10):
    """
    Load soundtracks for a batch of movies.

    Args:
        batch_size (int): Number of movies to process
    """
    logger.info("=" * 80)
    logger.info(f"🎵 LOADING SOUNDTRACKS (batch size: {batch_size})")
    logger.info("=" * 80)
    logger.info("")

    # Get movies without soundtracks
    logger.info(f"📊 Finding movies without soundtracks...")
    movies = get_movies_without_soundtracks(limit=batch_size)

    if not movies:
        logger.info("ℹ️  No movies found without soundtracks!")
        return

    logger.info(f"Found {len(movies)} movies without soundtracks")
    logger.info("")

    loaded = 0
    not_found = 0
    errors = 0

    for i, movie in enumerate(movies, 1):
        try:
            title = movie['title']
            media_id = movie['id']

            # Extract year from release_date
            year = None
            if movie.get('release_date'):
                try:
                    year = int(str(movie['release_date'])[:4])
                except (ValueError, TypeError):
                    pass

            logger.info(f"[{i}/{len(movies)}] 🎵 Processing: {title} ({year if year else 'Unknown'})")

            # Search and save soundtrack via API
            result = await search_soundtrack_via_api(media_id, title, year)

            if result and result.get('success'):
                logger.info(f"  ✅ Successfully loaded soundtrack!")
                loaded += 1
            else:
                message = result.get('message', 'Unknown error') if result else 'API error'
                logger.info(f"  ⚠️  {message}")
                not_found += 1

            # Rate limiting (MusicBrainz requires 1 request per second)
            await asyncio.sleep(1.5)

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
    logger.info("=" * 80)


async def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Load more soundtracks from database')
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of movies to process (default: 10)'
    )

    args = parser.parse_args()

    await load_soundtracks_batch(batch_size=args.batch_size)
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
