#!/usr/bin/env python3
"""
Populate 3D Criteria for All Movies

This script uses the MovieCriteriaAnalyzer MCP tool to generate
storytelling, characters, and cohesive_vision scores for all movies
in the database that don't already have these scores.

Usage:
    python scripts/populate_3d_criteria.py [--force] [--limit N]

Options:
    --force: Overwrite existing scores
    --limit N: Only process N movies (for testing)
    --dry-run: Show what would be done without making changes
"""

import sys
import os
import asyncio
import argparse
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.database_service import get_database_service
from backend.services.ollama_client import OllamaClient
from backend.mcp.criteria_analyzer import get_criteria_analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Populate 3D criteria scores for movies')
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing scores')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of movies to process')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    args = parser.parse_args()

    logger.info("🎬 Starting 3D Criteria Population Script")
    logger.info(f"⚙️  Force: {args.force}, Limit: {args.limit or 'None'}, "
               f"Dry-run: {args.dry_run}")

    # Initialize services
    try:
        db_service = get_database_service()
        ollama = OllamaClient()
        analyzer = get_criteria_analyzer(ollama)

        logger.info("✅ Services initialized")

    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        return 1

    # Get all movies from database using DuckDB directly
    try:
        import duckdb
        from config.settings import settings

        conn = duckdb.connect(settings.duckdb_database_path)

        query = """
            SELECT
                id, title, original_title, overview, release_date,
                tmdb_rating, custom_fields
            FROM media
            WHERE media_type = 'movie'
            ORDER BY title
        """

        if args.limit:
            query += f" LIMIT {args.limit}"

        movies = conn.execute(query).fetchall()
        columns = ['id', 'title', 'original_title', 'overview', 'release_date',
                  'tmdb_rating', 'custom_fields']
        movies = [dict(zip(columns, row)) for row in movies]

        logger.info(f"📊 Found {len(movies)} movies in database")

    except Exception as e:
        logger.error(f"❌ Failed to query movies: {e}")
        return 1

    # Get genres for each movie
    def get_movie_genres(movie_id):
        """Get genres for a movie."""
        try:
            query = """
                SELECT g.name
                FROM genres g
                JOIN media_genres mg ON g.id = mg.genre_id
                WHERE mg.media_id = ?
            """
            genre_rows = conn.execute(query, (movie_id,)).fetchall()
            return [row[0] for row in genre_rows]
        except Exception:
            return []

    # Process movies
    processed = 0
    skipped = 0
    updated = 0
    errors = 0

    for i, movie in enumerate(movies, 1):
        movie_id = movie['id']
        title = movie['title']
        custom_fields = movie.get('custom_fields') or {}

        # Check if scores already exist
        has_scores = all(
            key in custom_fields
            for key in ['storytelling', 'characters', 'cohesive_vision']
        )

        if has_scores and not args.force:
            logger.info(f"⏭️  [{i}/{len(movies)}] Skipping '{title}' (already has scores)")
            skipped += 1
            continue

        try:
            # Get genres
            genres = get_movie_genres(movie_id)

            # Extract release year
            release_year = None
            if movie.get('release_date'):
                try:
                    release_year = int(str(movie['release_date'])[:4])
                except Exception:
                    pass

            # Analyze movie
            logger.info(f"🔍 [{i}/{len(movies)}] Analyzing '{title}'...")

            scores = await analyzer.analyze_movie(
                title=title,
                overview=movie.get('overview'),
                genres=genres,
                release_year=release_year,
                tmdb_rating=movie.get('tmdb_rating')
            )

            # Update custom_fields
            custom_fields.update(scores)

            if not args.dry_run:
                # Update database
                update_query = """
                    UPDATE media
                    SET custom_fields = ?
                    WHERE id = ?
                """
                import json
                conn.execute(
                    update_query,
                    (json.dumps(custom_fields), movie_id)
                )
                logger.info(f"✅ [{i}/{len(movies)}] Updated '{title}': "
                           f"S={scores['storytelling']:.1f}, "
                           f"C={scores['characters']:.1f}, "
                           f"V={scores['cohesive_vision']:.1f}")
                updated += 1
            else:
                logger.info(f"🔍 [{i}/{len(movies)}] [DRY-RUN] Would update '{title}': "
                           f"S={scores['storytelling']:.1f}, "
                           f"C={scores['characters']:.1f}, "
                           f"V={scores['cohesive_vision']:.1f}")
                updated += 1

            processed += 1

            # Small delay to avoid overwhelming Ollama
            await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"❌ [{i}/{len(movies)}] Error processing '{title}': {e}")
            errors += 1
            continue

    # Summary
    logger.info("=" * 60)
    logger.info("📊 SUMMARY")
    logger.info(f"Total movies: {len(movies)}")
    logger.info(f"Processed: {processed}")
    logger.info(f"Updated: {updated}")
    logger.info(f"Skipped: {skipped}")
    logger.info(f"Errors: {errors}")
    logger.info("=" * 60)

    if args.dry_run:
        logger.info("ℹ️  This was a DRY-RUN. No changes were made to the database.")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
