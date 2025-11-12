#!/usr/bin/env python3
"""
Add Classic Movies for Soundtrack Testing

Adds well-known classic movies that are guaranteed to have soundtracks
in MusicBrainz for testing the soundtrack feature.

Usage:
    python scripts/add_classic_movies_for_soundtrack_test.py
"""

import sys
import os
import asyncio
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.tmdb_client import tmdb_client
from backend.services.media_service import media_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Classic movies known to have soundtracks in MusicBrainz
CLASSIC_MOVIES = [
    # Iconic soundtracks
    {"title": "The Godfather", "year": 1972, "tmdb_id": 238},
    {"title": "Star Wars", "year": 1977, "tmdb_id": 11},
    {"title": "Pulp Fiction", "year": 1994, "tmdb_id": 680},
    {"title": "The Lion King", "year": 1994, "tmdb_id": 8587},
    {"title": "Titanic", "year": 1997, "tmdb_id": 597},
    {"title": "Inception", "year": 2010, "tmdb_id": 27205},
    {"title": "Interstellar", "year": 2014, "tmdb_id": 157336},
    {"title": "Guardians of the Galaxy", "year": 2014, "tmdb_id": 118340},
]


async def add_classic_movies():
    """Add classic movies to the database."""
    logger.info("=" * 80)
    logger.info("🎬 ADDING CLASSIC MOVIES FOR SOUNDTRACK TESTING")
    logger.info("=" * 80)
    logger.info("")

    added_count = 0
    skipped_count = 0

    for movie in CLASSIC_MOVIES:
        try:
            title = movie["title"]
            tmdb_id = movie["tmdb_id"]

            logger.info(f"📽️  Processing: {title} ({movie['year']})")

            # Check if already exists
            existing = media_service.get_media_by_tmdb_id(tmdb_id)
            if existing:
                logger.info(f"  ⏭️  Already exists in database")
                skipped_count += 1
                continue

            # Fetch from TMDB
            logger.info(f"  🔍 Fetching from TMDB (ID: {tmdb_id})...")
            media_data = await tmdb_client.fetch_movie_details(tmdb_id)

            if not media_data:
                logger.warning(f"  ⚠️  Could not fetch from TMDB")
                continue

            # Save to database
            media_id = media_service.create_media(media_data)
            logger.info(f"  ✅ Added to database (ID: {media_id})")
            added_count += 1

            # Rate limiting
            await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"  ❌ Error adding {movie['title']}: {e}")

    logger.info("")
    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"✅ Movies added: {added_count}")
    logger.info(f"⏭️  Movies skipped (already exist): {skipped_count}")
    logger.info(f"📊 Total processed: {len(CLASSIC_MOVIES)}")
    logger.info("=" * 80)
    logger.info("")
    logger.info("🎵 Next step: Run soundtrack health check to load soundtracks")
    logger.info("   python scripts/soundtrack_health_check.py --batch-size 5")
    logger.info("")


async def main():
    """Main execution."""
    await add_classic_movies()
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
