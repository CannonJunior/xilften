#!/usr/bin/env python3
"""
Ingest soundtracks for all movies in the database.

This script loads soundtracks for all movies that don't currently have them,
using the configured multi-source system (MusicBrainz primary, IMDB fallback).
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import duckdb
from backend.services.soundtrack_service import SoundtrackService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


async def ingest_all_soundtracks():
    """Ingest soundtracks for all movies without soundtracks."""

    print("=" * 80)
    print("🎵 INGESTING SOUNDTRACKS FOR ALL MOVIES")
    print("=" * 80)
    print()

    # Connect to database
    db_path = project_root / "xilften.db"
    conn = duckdb.connect(str(db_path))

    try:
        # Get all movies
        all_movies = conn.execute("""
            SELECT id, title, release_date, imdb_id, tmdb_id
            FROM media
            WHERE media_type = 'movie'
            ORDER BY title
        """).fetchall()

        total_movies = len(all_movies)
        print(f"📊 Total movies in database: {total_movies}")
        print()

        # Check which movies have soundtracks
        movies_with_soundtracks = conn.execute("""
            SELECT DISTINCT media_id
            FROM soundtracks
        """).fetchall()

        existing_soundtrack_ids = {row[0] for row in movies_with_soundtracks}

        # Filter to movies without soundtracks
        movies_to_process = [
            movie for movie in all_movies
            if movie[0] not in existing_soundtrack_ids
        ]

        movies_with = len(existing_soundtrack_ids)
        movies_without = len(movies_to_process)

        print(f"✅ Movies WITH soundtracks: {movies_with}")
        print(f"⚠️  Movies WITHOUT soundtracks: {movies_without}")
        print()

        if movies_without == 0:
            print("🎉 All movies already have soundtracks!")
            return

        print("=" * 80)
        print(f"🔄 PROCESSING {movies_without} MOVIES")
        print("=" * 80)
        print()

        # Initialize soundtrack service
        soundtrack_service = SoundtrackService(conn)

        # Track results
        loaded = 0
        not_found = 0
        errors = 0
        source_stats = {}

        for idx, movie in enumerate(movies_to_process, 1):
            media_id, title, release_date, imdb_id, tmdb_id = movie

            # Extract year from release_date
            year = None
            if release_date:
                try:
                    year = int(release_date.split('-')[0])
                except:
                    pass

            print(f"[{idx}/{movies_without}] 🎵 {title} ({year or 'N/A'})")

            try:
                # Search for soundtrack
                result = await soundtrack_service.search_and_save_soundtrack(
                    media_id=media_id,
                    movie_title=title,
                    year=year,
                    imdb_id=imdb_id
                )

                if result:
                    metadata, tracks, source = result
                    track_count = len(tracks)
                    source_stats[source] = source_stats.get(source, 0) + 1
                    print(f"   ✅ SUCCESS! Loaded from {source.upper()}: {track_count} tracks")
                    loaded += 1
                else:
                    print(f"   ⚠️  No soundtrack found")
                    not_found += 1

                # Small delay to be respectful to APIs
                await asyncio.sleep(1.0)

            except Exception as e:
                print(f"   ❌ Error: {e}")
                errors += 1
                logger.exception(f"Error processing {title}")

        print()
        print("=" * 80)
        print("📊 INGESTION SUMMARY")
        print("=" * 80)
        print(f"✅ Soundtracks loaded: {loaded}")
        print(f"⚠️  Not found: {not_found}")
        print(f"❌ Errors: {errors}")

        if source_stats:
            print()
            print("📈 BY SOURCE:")
            for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"   {source.upper()}: {count}")

        print()
        print("=" * 80)
        print("📊 FINAL STATUS")
        print("=" * 80)

        # Get final counts
        final_with = conn.execute("""
            SELECT COUNT(DISTINCT media_id) FROM soundtracks
        """).fetchone()[0]

        final_without = total_movies - final_with
        percentage = (final_with / total_movies * 100) if total_movies > 0 else 0

        print(f"Total Movies: {total_movies}")
        print(f"✅ With soundtracks: {final_with} ({percentage:.1f}%)")
        print(f"⚠️  Without soundtracks: {final_without}")
        print("=" * 80)

    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(ingest_all_soundtracks())
