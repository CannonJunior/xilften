#!/usr/bin/env python3
"""
MCP Tool: Sync Genres from TMDB

This Model Context Protocol tool:
1. Fetches official TMDB genre list
2. Updates or creates genres in our database with TMDB IDs
3. Fetches genre data for all movies from TMDB
4. Associates movies with their genres

Usage:
    python scripts/sync_genres_from_tmdb.py [--dry-run]
"""

import os
import sys
import requests
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from config.database import get_duckdb

settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TMDB_API_KEY = settings.tmdb_api_key
TMDB_BASE_URL = settings.tmdb_base_url


# Official TMDB genre mapping based on their API
TMDB_GENRES = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western"
}


def fetch_tmdb_genres() -> List[Dict]:
    """
    Fetch official genre list from TMDB API.

    Returns:
        List of genre dictionaries with id and name
    """
    logger.info("🎬 Fetching genres from TMDB API...")

    url = f"{TMDB_BASE_URL}/genre/movie/list"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        genres = data.get("genres", [])

        logger.info(f"✅ Fetched {len(genres)} genres from TMDB")
        return genres

    except requests.RequestException as e:
        logger.error(f"❌ Failed to fetch genres from TMDB: {e}")
        return []


def create_genre_slug(name: str) -> str:
    """
    Create URL-friendly slug from genre name.

    Args:
        name: Genre name

    Returns:
        Slugified name
    """
    return name.lower().replace(" ", "-").replace("&", "and")


def sync_tmdb_genres_to_database(genres: List[Dict], conn=None, dry_run: bool = False) -> Dict[int, str]:
    """
    Sync TMDB genres to database.

    Args:
        genres: List of TMDB genre dictionaries
        conn: Database connection (optional, will create if not provided)
        dry_run: If True, don't actually update database

    Returns:
        Mapping of TMDB genre ID to UUID
    """
    logger.info("💾 Syncing genres to database...")

    close_conn = False
    if conn is None:
        conn = get_duckdb()
        close_conn = True

    genre_id_map = {}

    try:
        for genre in genres:
            tmdb_id = genre["id"]
            name = genre["name"]
            slug = create_genre_slug(name)

            # Check if genre already exists by TMDB ID or name
            result = conn.execute("""
                SELECT id, tmdb_genre_id
                FROM genres
                WHERE tmdb_genre_id = ? OR name = ?
            """, [tmdb_id, name]).fetchone()

            if result:
                genre_uuid = result[0]
                existing_tmdb_id = result[1]

                # Update TMDB ID if missing
                if existing_tmdb_id is None and not dry_run:
                    conn.execute("""
                        UPDATE genres
                        SET tmdb_genre_id = ?, slug = ?
                        WHERE id = ?
                    """, [tmdb_id, slug, genre_uuid])
                    logger.info(f"  ↻ Updated {name} with TMDB ID {tmdb_id}")
                else:
                    logger.info(f"  ✓ Genre {name} already exists")

                genre_id_map[tmdb_id] = str(genre_uuid)
            else:
                # Create new genre
                if not dry_run:
                    result = conn.execute("""
                        INSERT INTO genres (tmdb_genre_id, name, slug, genre_category, description, is_active)
                        VALUES (?, ?, ?, ?, ?, TRUE)
                        RETURNING id
                    """, [tmdb_id, name, slug, slug, f"{name} movies from TMDB"]).fetchone()

                    genre_uuid = str(result[0])
                    genre_id_map[tmdb_id] = genre_uuid
                    logger.info(f"  + Created genre {name} (TMDB ID: {tmdb_id})")
                else:
                    logger.info(f"  [DRY RUN] Would create genre {name}")

        if not dry_run:
            conn.commit()

        logger.info(f"✅ Synced {len(genres)} genres to database")
        return genre_id_map

    except Exception as e:
        logger.error(f"❌ Error syncing genres: {e}")
        conn.rollback()
        raise
    finally:
        if close_conn:
            conn.close()


def fetch_movie_genres_from_tmdb(tmdb_id: int) -> List[int]:
    """
    Fetch genre IDs for a specific movie from TMDB.

    Args:
        tmdb_id: TMDB movie ID

    Returns:
        List of TMDB genre IDs
    """
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        genre_ids = [g["id"] for g in data.get("genres", [])]
        return genre_ids

    except requests.RequestException as e:
        logger.error(f"  ❌ Failed to fetch genres for movie {tmdb_id}: {e}")
        return []


def associate_movies_with_genres(conn=None, dry_run: bool = False):
    """
    Fetch genres for all movies and create associations.

    Args:
        conn: Database connection (optional, will create if not provided)
        dry_run: If True, don't actually update database
    """
    logger.info("🎥 Associating movies with genres...")

    close_conn = False
    if conn is None:
        conn = get_duckdb()
        close_conn = True

    try:
        # Get all movies with TMDB IDs
        movies = conn.execute("""
            SELECT id, tmdb_id, title
            FROM media
            WHERE tmdb_id IS NOT NULL
            ORDER BY title
        """).fetchall()

        logger.info(f"📊 Found {len(movies)} movies to process")

        # Get genre mapping
        genre_map = {}
        genres = conn.execute("""
            SELECT id, tmdb_genre_id
            FROM genres
            WHERE tmdb_genre_id IS NOT NULL
        """).fetchall()

        for genre_row in genres:
            genre_uuid, tmdb_id = genre_row
            genre_map[tmdb_id] = str(genre_uuid)

        logger.info(f"📝 Loaded {len(genre_map)} genre mappings")

        success_count = 0
        skip_count = 0
        error_count = 0

        for movie_row in movies:
            movie_uuid, tmdb_id, title = movie_row
            movie_uuid = str(movie_uuid)

            # Check if already has genres
            existing_genres = conn.execute("""
                SELECT COUNT(*) FROM media_genres WHERE media_id = ?
            """, [movie_uuid]).fetchone()[0]

            if existing_genres > 0:
                logger.info(f"  ⏭️  Skipping {title} (already has {existing_genres} genres)")
                skip_count += 1
                continue

            # Fetch genres from TMDB
            genre_ids = fetch_movie_genres_from_tmdb(tmdb_id)

            if not genre_ids:
                logger.warning(f"  ⚠️  No genres found for {title}")
                error_count += 1
                continue

            # Associate with genres
            for genre_id in genre_ids:
                if genre_id not in genre_map:
                    logger.warning(f"  ⚠️  Unknown genre ID {genre_id} for {title}")
                    continue

                genre_uuid = genre_map[genre_id]

                if not dry_run:
                    try:
                        conn.execute("""
                            INSERT INTO media_genres (media_id, genre_id)
                            VALUES (?, ?)
                            ON CONFLICT DO NOTHING
                        """, [movie_uuid, genre_uuid])
                    except Exception as e:
                        logger.error(f"  ❌ Error associating genre: {e}")
                        continue

            genre_names = [TMDB_GENRES.get(gid, str(gid)) for gid in genre_ids]
            logger.info(f"  ✓ {title}: {', '.join(genre_names)}")
            success_count += 1

            # Rate limiting
            time.sleep(0.25)

        if not dry_run:
            conn.commit()

        logger.info(f"""
✅ Genre association complete:
   - Successfully processed: {success_count}
   - Skipped (already have genres): {skip_count}
   - Errors: {error_count}
   - Total: {len(movies)}
        """)

    except Exception as e:
        logger.error(f"❌ Error associating genres: {e}")
        conn.rollback()
        raise
    finally:
        if close_conn:
            conn.close()


def main():
    """
    Main execution function.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="MCP Tool: Sync genres from TMDB and associate with movies"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making database changes"
    )

    args = parser.parse_args()

    logger.info("="*80)
    logger.info("🎬 TMDB Genre Sync MCP Tool")
    logger.info("="*80)

    if args.dry_run:
        logger.info("⚠️  DRY RUN MODE - No database changes will be made")

    # Step 1: Fetch TMDB genres
    tmdb_genres = fetch_tmdb_genres()
    if not tmdb_genres:
        logger.error("❌ Failed to fetch genres from TMDB. Exiting.")
        sys.exit(1)

    # Create shared database connection
    conn = get_duckdb()
    try:
        # Step 2: Sync to database
        genre_id_map = sync_tmdb_genres_to_database(tmdb_genres, conn=conn, dry_run=args.dry_run)

        # Step 3: Associate movies with genres
        associate_movies_with_genres(conn=conn, dry_run=args.dry_run)

        logger.info("="*80)
        logger.info("✨ Genre sync complete!")
        logger.info("="*80)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
