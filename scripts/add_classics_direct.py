#!/usr/bin/env python3
"""
Add Classic Movies Directly to Database

Adds well-known classic movies that have soundtracks in Music Brainz.
Uses direct database insertion like load_top_grossing_movies.py

Usage:
    python scripts/add_classics_direct.py
"""

import sys
import os
import asyncio
import logging
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import db_manager
from backend.services.tmdb_client import TMDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Classic movies with iconic soundtracks
CLASSIC_MOVIES = [
    {"title": "The Godfather", "year": 1972, "tmdb_id": 238},
    {"title": "Star Wars", "year": 1977, "tmdb_id": 11},
    {"title": "Pulp Fiction", "year": 1994, "tmdb_id": 680},
    {"title": "The Lion King", "year": 1994, "tmdb_id": 8587},
]


class ClassicMovieAdder:
    """Add classic movies directly to database."""

    def __init__(self):
        """Initialize."""
        self.tmdb_client = TMDBClient()
        self.conn = db_manager.get_duckdb_connection()
        self.stats = {
            'added': 0,
            'already_exists': 0,
            'errors': 0
        }

    def movie_exists(self, tmdb_id: int) -> bool:
        """Check if movie exists."""
        query = "SELECT COUNT(*) FROM media WHERE tmdb_id = ?"
        result = self.conn.execute(query, [tmdb_id]).fetchone()
        return result[0] > 0

    async def add_movie(self, movie_info: dict):
        """Add a single movie."""
        title = movie_info['title']
        tmdb_id = movie_info['tmdb_id']

        logger.info(f"📽️  Processing: {title} ({movie_info['year']})")

        # Check if exists
        if self.movie_exists(tmdb_id):
            logger.info(f"  ⏭️  Already exists")
            self.stats['already_exists'] += 1
            return

        # Fetch from TMDB
        try:
            logger.info(f"  🔍 Fetching from TMDB...")
            movie_data = await self.tmdb_client.get_movie(tmdb_id)

            if not movie_data:
                logger.warning(f"  ⚠️  Could not fetch from TMDB")
                self.stats['errors'] += 1
                return

            # Insert into database
            insert_query = """
                INSERT INTO media (
                    id, tmdb_id, title, original_title, media_type,
                    overview, release_date, poster_path, backdrop_path,
                    tmdb_rating, tmdb_vote_count, popularity_score,
                    last_synced_tmdb, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            media_id = str(uuid.uuid4())
            now = datetime.now().isoformat()

            self.conn.execute(insert_query, [
                media_id,
                tmdb_id,
                movie_data.get('title', title),
                movie_data.get('original_title', title),
                'movie',
                movie_data.get('overview', ''),
                movie_data.get('release_date', None),
                movie_data.get('poster_path', None),
                movie_data.get('backdrop_path', None),
                movie_data.get('vote_average', 0.0),
                movie_data.get('vote_count', 0),
                movie_data.get('popularity', 0.0),
                now,
                now
            ])

            self.conn.commit()
            logger.info(f"  ✅ Added to database")
            self.stats['added'] += 1

        except Exception as e:
            logger.error(f"  ❌ Error: {e}")
            self.stats['errors'] += 1

    async def run(self):
        """Add all classic movies."""
        logger.info("=" * 80)
        logger.info("🎬 ADDING CLASSIC MOVIES")
        logger.info("=" * 80)
        logger.info("")

        for movie in CLASSIC_MOVIES:
            await self.add_movie(movie)
            await asyncio.sleep(0.5)  # Rate limiting

        logger.info("")
        logger.info("=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Added: {self.stats['added']}")
        logger.info(f"⏭️  Already exists: {self.stats['already_exists']}")
        logger.info(f"❌ Errors: {self.stats['errors']}")
        logger.info("=" * 80)


async def main():
    """Main execution."""
    adder = ClassicMovieAdder()
    await adder.run()
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
