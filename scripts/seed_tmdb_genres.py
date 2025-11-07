#!/usr/bin/env python3
"""
Seed TMDB Official 19 Genres

This script seeds the 19 official TMDB genres into the database.
"""

import duckdb
import uuid
from datetime import datetime

# TMDB Official 19 Genres with TMDB IDs
TMDB_GENRES = [
    {"tmdb_id": 28, "name": "Action"},
    {"tmdb_id": 12, "name": "Adventure"},
    {"tmdb_id": 16, "name": "Animation"},
    {"tmdb_id": 35, "name": "Comedy"},
    {"tmdb_id": 80, "name": "Crime"},
    {"tmdb_id": 99, "name": "Documentary"},
    {"tmdb_id": 18, "name": "Drama"},
    {"tmdb_id": 10751, "name": "Family"},
    {"tmdb_id": 14, "name": "Fantasy"},
    {"tmdb_id": 36, "name": "History"},
    {"tmdb_id": 27, "name": "Horror"},
    {"tmdb_id": 10402, "name": "Music"},
    {"tmdb_id": 9648, "name": "Mystery"},
    {"tmdb_id": 10749, "name": "Romance"},
    {"tmdb_id": 878, "name": "Science Fiction"},
    {"tmdb_id": 53, "name": "Thriller"},
    {"tmdb_id": 10770, "name": "TV Movie"},
    {"tmdb_id": 10752, "name": "War"},
    {"tmdb_id": 37, "name": "Western"}
]

DATABASE_PATH = "./database/xilften.duckdb"


def seed_tmdb_genres():
    """Seed TMDB genres into database."""
    conn = duckdb.connect(DATABASE_PATH)

    print("=" * 80)
    print("🎬 Seeding TMDB Genres")
    print("=" * 80)
    print()

    added = 0
    skipped = 0

    for genre_data in TMDB_GENRES:
        tmdb_id = genre_data["tmdb_id"]
        name = genre_data["name"]
        slug = name.lower().replace(" ", "-")

        # Check if genre already exists
        existing = conn.execute(
            "SELECT id FROM genres WHERE LOWER(name) = LOWER(?) OR tmdb_genre_id = ?",
            [name, tmdb_id]
        ).fetchone()

        if existing:
            print(f"  ⏭️  Skipped: {name} (already exists)")
            skipped += 1
        else:
            # Insert genre
            genre_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO genres (
                    id, tmdb_genre_id, name, slug, parent_genre_id,
                    genre_category, description, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                genre_id,
                tmdb_id,
                name,
                slug,
                None,  # No parent (top-level genre)
                slug,  # Use slug as category
                f"TMDB standard {name} genre",
                True,
                datetime.now().isoformat()
            ])
            print(f"  ✅ Added: {name} (TMDB ID: {tmdb_id})")
            added += 1

    conn.close()

    print()
    print("=" * 80)
    print("✅ Seeding Complete!")
    print("=" * 80)
    print(f"Added: {added}")
    print(f"Skipped: {skipped}")
    print(f"Total: {len(TMDB_GENRES)}")
    print()


if __name__ == "__main__":
    seed_tmdb_genres()
