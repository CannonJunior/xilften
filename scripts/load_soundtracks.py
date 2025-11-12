#!/usr/bin/env python3
"""
Load Soundtracks for All Movies

Searches for and loads soundtrack data for all movies in the database.
Uses MusicBrainz (free) as primary source and Spotify (optional) for enhancement.

Usage:
    python scripts/load_soundtracks.py [--limit N] [--force]
"""

import sys
import os
import asyncio
import logging
import argparse
from typing import Dict, Any
from datetime import datetime

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


class SoundtrackLoader:
    """Loads soundtracks for all movies in the database."""

    def __init__(self, limit: int = None, force: bool = False):
        """
        Initialize the soundtrack loader.

        Args:
            limit (int, optional): Maximum number of movies to process
            force (bool, optional): Force reload even if soundtrack exists
        """
        self.conn = db_manager.get_duckdb_connection()
        self.limit = limit
        self.force = force
        self.stats = {
            'total_movies': 0,
            'soundtracks_found': 0,
            'soundtracks_not_found': 0,
            'already_existed': 0,
            'errors': 0,
            'tracks_loaded': 0
        }

    def get_movies_to_process(self):
        """
        Get list of movies that need soundtrack data.

        Returns:
            list: List of (media_id, title, release_year) tuples
        """
        logger.info("📊 Fetching movies from database...")

        if self.force:
            # Get all movies, regardless of whether they have soundtracks
            query = """
                SELECT id, title, release_date
                FROM media
                WHERE media_type = 'movie'
                ORDER BY release_date DESC
            """
        else:
            # Only get movies without soundtracks
            query = """
                SELECT m.id, m.title, m.release_date
                FROM media m
                LEFT JOIN soundtracks s ON m.id = s.media_id
                WHERE m.media_type = 'movie' AND s.id IS NULL
                ORDER BY m.release_date DESC
            """

        if self.limit:
            query += f" LIMIT {self.limit}"

        results = self.conn.execute(query).fetchall()

        movies = []
        for row in results:
            media_id, title, release_date = row

            # Extract year from release_date
            year = None
            if release_date:
                try:
                    year = int(str(release_date)[:4])
                except (ValueError, TypeError):
                    pass

            movies.append((media_id, title, year))

        logger.info(f"✅ Found {len(movies)} movies to process")
        return movies

    async def load_soundtrack_for_movie(self, media_id: str, title: str, year: int = None):
        """
        Load soundtrack for a specific movie.

        Args:
            media_id (str): Media ID
            title (str): Movie title
            year (int, optional): Release year

        Returns:
            bool: True if soundtrack was found and loaded
        """
        try:
            logger.info(f"🎵 Processing: {title} ({year if year else 'Unknown'})")

            # Check if already exists (unless force mode)
            if not self.force:
                existing = soundtrack_service.get_soundtrack_by_media_id(media_id)
                if existing:
                    logger.info(f"  ⏭️  Soundtrack already exists (skipping)")
                    self.stats['already_existed'] += 1
                    return True

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
                self.stats['soundtracks_found'] += 1
                self.stats['tracks_loaded'] += track_count
                return True
            else:
                logger.info(f"  ⚠️  No soundtrack found")
                self.stats['soundtracks_not_found'] += 1
                return False

        except Exception as e:
            logger.error(f"  ❌ Error processing {title}: {e}")
            self.stats['errors'] += 1
            return False

    async def load_all_soundtracks(self):
        """
        Load soundtracks for all movies in the database.
        """
        logger.info("=" * 80)
        logger.info("🎬 SOUNDTRACK LOADING - STARTING")
        logger.info("=" * 80)

        # Get movies to process
        movies = self.get_movies_to_process()
        self.stats['total_movies'] = len(movies)

        if not movies:
            logger.info("ℹ️  No movies need soundtrack data")
            return

        logger.info("")
        logger.info(f"Processing {len(movies)} movies...")
        logger.info("-" * 80)

        # Process each movie with rate limiting
        for i, (media_id, title, year) in enumerate(movies, 1):
            logger.info(f"[{i}/{len(movies)}] ", )

            await self.load_soundtrack_for_movie(media_id, title, year)

            # Rate limiting: 1 second between requests (MusicBrainz requirement)
            if i < len(movies):
                await asyncio.sleep(1.5)  # 1.5 seconds to be safe

        # Print summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("SOUNDTRACK LOADING - SUMMARY")
        logger.info("=" * 80)
        logger.info(f"📊 Total movies processed: {self.stats['total_movies']}")
        logger.info(f"✅ Soundtracks found: {self.stats['soundtracks_found']}")
        logger.info(f"⚠️  Soundtracks not found: {self.stats['soundtracks_not_found']}")
        logger.info(f"⏭️  Already existed: {self.stats['already_existed']}")
        logger.info(f"❌ Errors: {self.stats['errors']}")
        logger.info(f"🎵 Total tracks loaded: {self.stats['tracks_loaded']}")
        logger.info("")

        # Success rate
        if self.stats['total_movies'] > 0:
            success_rate = (self.stats['soundtracks_found'] + self.stats['already_existed']) / self.stats['total_movies'] * 100
            logger.info(f"📈 Success rate: {success_rate:.1f}%")

        logger.info("=" * 80)


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Load soundtracks for movies in the database')
    parser.add_argument('--limit', type=int, help='Maximum number of movies to process')
    parser.add_argument('--force', action='store_true', help='Force reload even if soundtrack exists')

    args = parser.parse_args()

    loader = SoundtrackLoader(limit=args.limit, force=args.force)
    await loader.load_all_soundtracks()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
