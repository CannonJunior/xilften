#!/usr/bin/env python3
"""
Load Soundtracks via API

Uses the soundtrack API to load soundtracks for movies without them.
Works alongside the running server.

Usage:
    python scripts/load_soundtracks_via_api.py --batch-size 10
"""

import sys
import os
import argparse
import asyncio
import logging
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:7575/api"


async def get_movies_without_soundtracks(limit: int = 10):
    """Get movies that don't have soundtracks yet."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get all movies
        response = await client.get(f"{API_BASE_URL}/media/movies")
        response.raise_for_status()
        movies = response.json()

        # Filter movies without soundtracks
        movies_without_soundtracks = []

        for movie in movies[:limit * 3]:  # Check more than we need
            media_id = movie['id']

            # Check if movie has soundtrack
            soundtrack_response = await client.get(
                f"{API_BASE_URL}/soundtracks/{media_id}"
            )

            if soundtrack_response.status_code == 200:
                soundtracks = soundtrack_response.json()
                if not soundtracks:
                    movies_without_soundtracks.append(movie)

            if len(movies_without_soundtracks) >= limit:
                break

        return movies_without_soundtracks[:limit]


async def search_soundtrack(media_id: str, title: str, year: int):
    """Search and save soundtrack for a movie."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "media_id": media_id,
            "movie_title": title,
            "year": year
        }

        response = await client.post(
            f"{API_BASE_URL}/soundtracks/search",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            return result
        else:
            logger.error(f"Failed to search soundtrack: {response.status_code}")
            return None


async def load_soundtracks_batch(batch_size: int = 10):
    """Load soundtracks for a batch of movies."""
    logger.info("=" * 80)
    logger.info(f"🎵 LOADING SOUNDTRACKS VIA API (batch size: {batch_size})")
    logger.info("=" * 80)
    logger.info("")

    # Get movies without soundtracks
    logger.info(f"📊 Finding movies without soundtracks...")
    movies = await get_movies_without_soundtracks(limit=batch_size)

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

            # Search and save soundtrack
            result = await search_soundtrack(media_id, title, year)

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
    parser = argparse.ArgumentParser(description='Load soundtracks via API')
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
