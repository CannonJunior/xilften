#!/usr/bin/env python3
"""
Soundtrack Health Check and Auto-Load Script

Checks for movies without soundtrack data and automatically loads them in batches.
Uses MusicBrainz (free) API with rate limiting to avoid overwhelming the service.

Usage:
    python scripts/soundtrack_health_check.py [--batch-size N] [--dry-run]
"""

import sys
import os
import asyncio
import logging
import argparse
from typing import List, Tuple
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


class SoundtrackHealthCheck:
    """Health check and batch loader for movie soundtracks."""

    def __init__(self, batch_size: int = 10, dry_run: bool = False):
        """
        Initialize the health check.

        Args:
            batch_size (int): Number of movies to process per batch
            dry_run (bool): If True, only report stats without loading
        """
        self.conn = db_manager.get_duckdb_connection()
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.stats = {
            'total_movies': 0,
            'movies_with_soundtracks': 0,
            'movies_without_soundtracks': 0,
            'soundtracks_loaded': 0,
            'soundtracks_not_found': 0,
            'errors': 0
        }

    def get_health_stats(self) -> dict:
        """
        Get current health statistics.

        Returns:
            dict: Health stats including coverage percentage
        """
        logger.info("📊 Gathering health statistics...")

        # Total movies
        total_movies = self.conn.execute(
            "SELECT COUNT(*) FROM media WHERE media_type = 'movie'"
        ).fetchone()[0]

        # Movies with soundtracks
        movies_with_soundtracks = self.conn.execute("""
            SELECT COUNT(DISTINCT m.id)
            FROM media m
            JOIN soundtracks s ON m.id = s.media_id
            WHERE m.media_type = 'movie'
        """).fetchone()[0]

        # Movies without soundtracks
        movies_without_soundtracks = total_movies - movies_with_soundtracks

        # Calculate coverage
        coverage = (movies_with_soundtracks / total_movies * 100) if total_movies > 0 else 0

        self.stats['total_movies'] = total_movies
        self.stats['movies_with_soundtracks'] = movies_with_soundtracks
        self.stats['movies_without_soundtracks'] = movies_without_soundtracks

        return {
            'total_movies': total_movies,
            'movies_with_soundtracks': movies_with_soundtracks,
            'movies_without_soundtracks': movies_without_soundtracks,
            'coverage_percentage': coverage
        }

    def get_movies_without_soundtracks(self, limit: int = None) -> List[Tuple]:
        """
        Get movies that don't have soundtrack data.

        Args:
            limit (int, optional): Maximum number of movies to return

        Returns:
            list: List of (media_id, title, release_year) tuples
        """
        query = """
            SELECT m.id, m.title, m.release_date
            FROM media m
            LEFT JOIN soundtracks s ON m.id = s.media_id
            WHERE m.media_type = 'movie' AND s.id IS NULL
            ORDER BY m.release_date DESC
        """

        if limit:
            query += f" LIMIT {limit}"

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
                self.stats['soundtracks_loaded'] += 1
                return True
            else:
                logger.info(f"  ⚠️  No soundtrack found")
                self.stats['soundtracks_not_found'] += 1
                return False

        except Exception as e:
            logger.error(f"  ❌ Error processing {title}: {e}")
            self.stats['errors'] += 1
            return False

    async def process_batch(self, batch: List[Tuple]):
        """
        Process a batch of movies.

        Args:
            batch (list): List of (media_id, title, year) tuples
        """
        logger.info(f"📦 Processing batch of {len(batch)} movies...")

        for i, (media_id, title, year) in enumerate(batch, 1):
            logger.info(f"[{i}/{len(batch)}] ", )
            await self.load_soundtrack_for_movie(media_id, title, year)

            # Rate limiting: 1.5 seconds between requests (MusicBrainz requirement)
            if i < len(batch):
                await asyncio.sleep(1.5)

    async def run_health_check(self):
        """
        Run the full health check and load missing soundtracks.
        """
        logger.info("=" * 80)
        logger.info("🎬 SOUNDTRACK HEALTH CHECK - STARTING")
        logger.info("=" * 80)
        logger.info("")

        # Get current health stats
        health = self.get_health_stats()

        logger.info("📊 Current Status:")
        logger.info(f"  Total movies: {health['total_movies']}")
        logger.info(f"  Movies with soundtracks: {health['movies_with_soundtracks']}")
        logger.info(f"  Movies without soundtracks: {health['movies_without_soundtracks']}")
        logger.info(f"  Coverage: {health['coverage_percentage']:.1f}%")
        logger.info("")

        if health['movies_without_soundtracks'] == 0:
            logger.info("✅ All movies have soundtrack data!")
            return

        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No soundtracks will be loaded")

            # Show sample of movies without soundtracks
            sample = self.get_movies_without_soundtracks(limit=10)
            logger.info("")
            logger.info("Sample movies without soundtracks:")
            for media_id, title, year in sample:
                logger.info(f"  - {title} ({year})")
            logger.info("")
            logger.info(f"ℹ️  Total {health['movies_without_soundtracks']} movies need soundtracks")
            return

        # Load soundtracks in batches
        logger.info(f"🔄 Loading soundtracks in batches of {self.batch_size}...")
        logger.info("-" * 80)
        logger.info("")

        # Get movies without soundtracks
        movies = self.get_movies_without_soundtracks(limit=self.batch_size)

        if not movies:
            logger.info("✅ No movies need soundtrack data")
            return

        # Process the batch
        await self.process_batch(movies)

        # Print summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("SOUNDTRACK HEALTH CHECK - SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Soundtracks loaded: {self.stats['soundtracks_loaded']}")
        logger.info(f"⚠️  Soundtracks not found: {self.stats['soundtracks_not_found']}")
        logger.info(f"❌ Errors: {self.stats['errors']}")
        logger.info("")

        # Get updated health stats
        final_health = self.get_health_stats()
        logger.info("📊 Final Status:")
        logger.info(f"  Total movies: {final_health['total_movies']}")
        logger.info(f"  Movies with soundtracks: {final_health['movies_with_soundtracks']}")
        logger.info(f"  Movies without soundtracks: {final_health['movies_without_soundtracks']}")
        logger.info(f"  Coverage: {final_health['coverage_percentage']:.1f}%")
        logger.info("")

        if final_health['movies_without_soundtracks'] > 0:
            logger.info(f"ℹ️  Run again to process the next batch of {self.batch_size} movies")

        logger.info("=" * 80)


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Health check and auto-load soundtracks for movies'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of movies to process per batch (default: 10)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only show statistics without loading soundtracks'
    )

    args = parser.parse_args()

    health_check = SoundtrackHealthCheck(
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )
    await health_check.run_health_check()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
