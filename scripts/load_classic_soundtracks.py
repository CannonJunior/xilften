#!/usr/bin/env python3
"""
Load Soundtracks for Classic Movies

Specifically targets classic movies with known soundtracks.

Usage:
    python scripts/load_classic_soundtracks.py
"""

import sys
import os
import asyncio
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import db_manager
from backend.services.soundtrack_service import soundtrack_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Classic movies to target
CLASSIC_TITLES = [
    'The Godfather',
    'Star Wars',
    'Pulp Fiction',
    'The Lion King'
]


async def load_soundtracks_for_classics():
    """Load soundtracks for specific classic movies."""
    logger.info("=" * 80)
    logger.info("🎵 LOADING SOUNDTRACKS FOR CLASSIC MOVIES")
    logger.info("=" * 80)
    logger.info("")

    conn = db_manager.get_duckdb_connection()

    # Get classic movies from database
    query = """
        SELECT m.id, m.title, m.release_date
        FROM media m
        LEFT JOIN soundtracks s ON m.id = s.media_id
        WHERE m.media_type = 'movie'
          AND m.title IN (?, ?, ?, ?)
          AND s.id IS NULL
        ORDER BY m.release_date
    """

    movies = conn.execute(query, CLASSIC_TITLES).fetchall()

    logger.info(f"Found {len(movies)} classic movies without soundtracks")
    logger.info("")

    loaded = 0
    not_found = 0
    errors = 0

    for media_id, title, release_date in movies:
        try:
            # Extract year
            year = None
            if release_date:
                try:
                    year = int(str(release_date)[:4])
                except (ValueError, TypeError):
                    pass

            logger.info(f"🎵 Processing: {title} ({year if year else 'Unknown'})")

            # Search and save soundtrack
            soundtrack_id = await soundtrack_service.search_and_save_soundtrack(
                media_id=media_id,
                movie_title=title,
                year=year
            )

            if soundtrack_id:
                # Get track count
                soundtrack_data = soundtrack_service.get_soundtrack_with_tracks(soundtrack_id)
                track_count = len(soundtrack_data.get('tracks', []))

                logger.info(f"  ✅ Found soundtrack with {track_count} tracks")
                loaded += 1
            else:
                logger.info(f"  ⚠️  No soundtrack found")
                not_found += 1

            # Rate limiting
            await asyncio.sleep(1.5)

        except Exception as e:
            logger.error(f"  ❌ Error processing {title}: {e}")
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
    await load_soundtracks_for_classics()
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
