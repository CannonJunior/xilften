#!/usr/bin/env python3
"""
API-Only Multi-Source Soundtrack Loading Script

Loads soundtracks for movies using the API exclusively (no direct database access).
This allows the script to run while the server is active.

Usage:
    python scripts/load_soundtracks_api_only.py --batch-size 10
"""

import sys
import argparse
import asyncio
import logging
import httpx
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:7575/api"


async def get_movies_via_api(limit: int = 10) -> List[Dict]:
    """
    Query API to get movies without soundtracks.

    Args:
        limit (int): Maximum number of movies to return

    Returns:
        list: List of movie dictionaries
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get all movies first
            response = await client.get(f"{API_BASE_URL}/media?limit=100")

            if response.status_code != 200:
                logger.error(f"API error {response.status_code}")
                return []

            data = response.json()
            all_movies = data.get('data', {}).get('items', [])

            # Filter for movies only
            movies = [m for m in all_movies if m.get('media_type') == 'movie']

            # Now check which ones don't have soundtracks
            movies_without_soundtracks = []

            for movie in movies[:limit * 3]:  # Check more than limit to ensure we get enough
                media_id = movie.get('id')
                if not media_id:
                    continue

                # Check if this movie has a soundtrack
                soundtrack_response = await client.get(f"{API_BASE_URL}/soundtracks/{media_id}")

                if soundtrack_response.status_code == 404:
                    # No soundtrack found
                    movies_without_soundtracks.append(movie)

                    if len(movies_without_soundtracks) >= limit:
                        break

                # Rate limit
                await asyncio.sleep(0.1)

            return movies_without_soundtracks

    except Exception as e:
        logger.error(f"Error querying API: {e}")
        return []


async def search_soundtrack_via_api(
    media_id: str,
    title: str,
    year: Optional[int],
    imdb_id: Optional[str] = None
) -> Dict:
    """
    Search and save soundtrack via API.

    Args:
        media_id (str): Media ID
        title (str): Movie title
        year (int, optional): Release year
        imdb_id (str, optional): IMDB ID

    Returns:
        dict: API response with source information
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "media_id": media_id,
            "movie_title": title,
            "year": year
        }

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


async def load_soundtracks_batch(batch_size: int = 10):
    """
    Load soundtracks for a batch of movies using API only.

    Args:
        batch_size (int): Number of movies to process
    """
    logger.info("=" * 80)
    logger.info(f"🎵 LOADING SOUNDTRACKS (batch size: {batch_size})")
    logger.info("=" * 80)
    logger.info("")

    logger.info(f"📊 Finding movies without soundtracks...")
    movies = await get_movies_via_api(limit=batch_size)

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

            # Rate limiting
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
        description='Load soundtracks from multiple sources using API only'
    )
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
