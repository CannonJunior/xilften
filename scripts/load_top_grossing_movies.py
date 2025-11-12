#!/usr/bin/env python3
"""
Load Top Grossing Movies from TMDB

Fetches the top 10 highest-grossing movies for each year from 2000 to 2025
and adds them to the database.

Usage:
    python scripts/load_top_grossing_movies.py
"""

import sys
import os
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings
from config.database import db_manager
from backend.services.tmdb_client import TMDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TopGrossingMovieLoader:
    """Loads top-grossing movies by year from TMDB."""

    def __init__(self):
        """Initialize the loader."""
        self.tmdb_client = TMDBClient()
        self.conn = db_manager.get_duckdb_connection()
        self.stats = {
            'total_fetched': 0,
            'new_added': 0,
            'already_exists': 0,
            'errors': 0
        }

    async def fetch_top_movies_for_year(self, year: int, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch top grossing movies for a specific year.

        Args:
            year (int): The year to fetch movies for
            top_n (int): Number of top movies to fetch (default: 10)

        Returns:
            List[Dict]: List of movie data dictionaries
        """
        logger.info(f"📅 Fetching top {top_n} movies for {year}...")

        try:
            # TMDB discover endpoint allows sorting by revenue
            # We'll fetch movies released in the specified year, sorted by revenue
            params = {
                'primary_release_year': year,
                'sort_by': 'revenue.desc',
                'page': 1,
                'include_adult': False,
                'language': 'en-US'
            }

            # Make request to TMDB discover endpoint
            movies = await self.tmdb_client.discover_movies(filters=params)

            if not movies:
                logger.warning(f"⚠️  No results for {year}")
                return []

            # Get the top N movies
            movies = movies[:top_n]

            logger.info(f"✅ Found {len(movies)} movies for {year}")
            return movies

        except Exception as e:
            logger.error(f"❌ Error fetching movies for {year}: {e}")
            return []

    def movie_exists(self, tmdb_id: int) -> bool:
        """
        Check if a movie already exists in the database.

        Args:
            tmdb_id (int): TMDB ID of the movie

        Returns:
            bool: True if movie exists, False otherwise
        """
        query = "SELECT COUNT(*) FROM media WHERE tmdb_id = ?"
        result = self.conn.execute(query, [tmdb_id]).fetchone()
        return result[0] > 0

    def add_movie_to_database(self, movie_data: Dict[str, Any]) -> bool:
        """
        Add a movie to the database.

        Args:
            movie_data (Dict): Movie data from TMDB

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if movie already exists
            if self.movie_exists(movie_data['id']):
                logger.debug(f"⏭️  Movie already exists: {movie_data['title']}")
                self.stats['already_exists'] += 1
                return False

            # Prepare data for insertion
            insert_query = """
                INSERT INTO media (
                    id, tmdb_id, title, original_title, media_type,
                    overview, release_date, poster_path, backdrop_path,
                    tmdb_rating, tmdb_vote_count, popularity_score,
                    last_synced_tmdb, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # Generate UUID for the media entry
            import uuid
            media_id = str(uuid.uuid4())

            # Extract data
            title = movie_data.get('title', 'Unknown')
            original_title = movie_data.get('original_title', title)
            overview = movie_data.get('overview', '')
            release_date = movie_data.get('release_date', None)
            poster_path = movie_data.get('poster_path', None)
            backdrop_path = movie_data.get('backdrop_path', None)
            tmdb_rating = movie_data.get('vote_average', 0.0)
            tmdb_vote_count = movie_data.get('vote_count', 0)
            popularity_score = movie_data.get('popularity', 0.0)
            tmdb_id = movie_data['id']

            now = datetime.now().isoformat()

            # Insert movie
            self.conn.execute(insert_query, [
                media_id,
                tmdb_id,
                title,
                original_title,
                'movie',
                overview,
                release_date,
                poster_path,
                backdrop_path,
                tmdb_rating,
                tmdb_vote_count,
                popularity_score,
                now,
                now
            ])

            logger.info(f"✅ Added: {title} ({release_date[:4] if release_date else 'Unknown'})")
            self.stats['new_added'] += 1
            return True

        except Exception as e:
            logger.error(f"❌ Error adding movie {movie_data.get('title', 'Unknown')}: {e}")
            self.stats['errors'] += 1
            return False

    async def load_all_years(self, start_year: int = 2000, end_year: int = 2025, top_n: int = 10):
        """
        Load top grossing movies for all years in the range.

        Args:
            start_year (int): Starting year (default: 2000)
            end_year (int): Ending year (default: 2025)
            top_n (int): Number of top movies per year (default: 10)
        """
        logger.info(f"🎬 Starting to load top {top_n} movies for years {start_year}-{end_year}")
        logger.info("=" * 80)

        for year in range(start_year, end_year + 1):
            # Fetch movies for this year
            movies = await self.fetch_top_movies_for_year(year, top_n)
            self.stats['total_fetched'] += len(movies)

            # Add each movie to the database
            for movie in movies:
                self.add_movie_to_database(movie)

            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)

        # Print summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("LOADING COMPLETE - SUMMARY")
        logger.info("=" * 80)
        logger.info(f"📊 Total movies fetched: {self.stats['total_fetched']}")
        logger.info(f"✅ New movies added: {self.stats['new_added']}")
        logger.info(f"⏭️  Already existed: {self.stats['already_exists']}")
        logger.info(f"❌ Errors: {self.stats['errors']}")
        logger.info("")

        # Success rate
        if self.stats['total_fetched'] > 0:
            success_rate = (self.stats['new_added'] + self.stats['already_exists']) / self.stats['total_fetched'] * 100
            logger.info(f"📈 Success rate: {success_rate:.1f}%")


async def main():
    """Main execution function."""
    loader = TopGrossingMovieLoader()

    # Load top 10 movies for each year from 2000 to 2025
    await loader.load_all_years(start_year=2000, end_year=2025, top_n=10)

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
