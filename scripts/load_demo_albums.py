#!/usr/bin/env python3
"""
Load Demo Albums for Audio Catalog Testing.

Creates sample album data without requiring Spotify API credentials.
This demonstrates the audio catalog functionality with realistic test data.
"""

import sys
from pathlib import Path
from datetime import date

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.audio_service import get_audio_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Demo albums with realistic metadata
DEMO_ALBUMS = [
    {
        "artist": {
            "name": "Pink Floyd",
            "sort_name": "Pink Floyd",
            "artist_type": "group",
        },
        "album": {
            "title": "The Dark Side of the Moon",
            "content_type": "album",
            "release_date": date(1973, 3, 1),
            "release_year": 1973,
            "total_tracks": 10,
            "record_label": "Harvest / EMI",
        },
        "genre": "rock",
    },
    {
        "artist": {
            "name": "The Beatles",
            "sort_name": "Beatles, The",
            "artist_type": "group",
        },
        "album": {
            "title": "Abbey Road",
            "content_type": "album",
            "release_date": date(1969, 9, 26),
            "release_year": 1969,
            "total_tracks": 17,
            "record_label": "Apple Records",
        },
        "genre": "rock",
    },
    {
        "artist": {
            "name": "Miles Davis",
            "sort_name": "Davis, Miles",
            "artist_type": "person",
        },
        "album": {
            "title": "Kind of Blue",
            "content_type": "album",
            "release_date": date(1959, 8, 17),
            "release_year": 1959,
            "total_tracks": 5,
            "record_label": "Columbia",
        },
        "genre": "jazz",
    },
    {
        "artist": {
            "name": "Daft Punk",
            "sort_name": "Daft Punk",
            "artist_type": "group",
        },
        "album": {
            "title": "Random Access Memories",
            "content_type": "album",
            "release_date": date(2013, 5, 17),
            "release_year": 2013,
            "total_tracks": 13,
            "record_label": "Columbia",
        },
        "genre": "electronic",
    },
    {
        "artist": {
            "name": "Kendrick Lamar",
            "sort_name": "Lamar, Kendrick",
            "artist_type": "person",
        },
        "album": {
            "title": "good kid, m.A.A.d city",
            "content_type": "album",
            "release_date": date(2012, 10, 22),
            "release_year": 2012,
            "total_tracks": 12,
            "record_label": "Top Dawg / Aftermath / Interscope",
        },
        "genre": "hip-hop",
    },
    {
        "artist": {
            "name": "Radiohead",
            "sort_name": "Radiohead",
            "artist_type": "group",
        },
        "album": {
            "title": "OK Computer",
            "content_type": "album",
            "release_date": date(1997, 5, 21),
            "release_year": 1997,
            "total_tracks": 12,
            "record_label": "Parlophone / Capitol",
        },
        "genre": "rock",
    },
    {
        "artist": {
            "name": "Taylor Swift",
            "sort_name": "Swift, Taylor",
            "artist_type": "person",
        },
        "album": {
            "title": "1989",
            "content_type": "album",
            "release_date": date(2014, 10, 27),
            "release_year": 2014,
            "total_tracks": 13,
            "record_label": "Big Machine",
        },
        "genre": "pop",
    },
    {
        "artist": {
            "name": "Hans Zimmer",
            "sort_name": "Zimmer, Hans",
            "artist_type": "person",
        },
        "album": {
            "title": "Inception (Music from the Motion Picture)",
            "content_type": "soundtrack",
            "release_date": date(2010, 7, 13),
            "release_year": 2010,
            "total_tracks": 12,
            "record_label": "Reprise",
        },
        "genre": "soundtrack",
    },
]


def load_demo_albums():
    """
    Load demo albums into the database.

    Returns:
        dict: Statistics about loaded albums
    """
    logger.info("=" * 80)
    logger.info("🎵 LOADING DEMO ALBUMS FOR AUDIO CATALOG")
    logger.info("=" * 80)
    logger.info("")

    audio_service = get_audio_service()

    stats = {
        "total": len(DEMO_ALBUMS),
        "artists_created": 0,
        "albums_created": 0,
        "albums_skipped": 0,
    }

    for i, demo in enumerate(DEMO_ALBUMS, 1):
        logger.info(f"[{i}/{stats['total']}] Processing: {demo['artist']['name']} - {demo['album']['title']}")

        try:
            # Check if artist exists
            conn = audio_service.get_connection()
            existing_artist = conn.execute(
                "SELECT id FROM audio_artists WHERE name = ?",
                [demo["artist"]["name"]]
            ).fetchone()

            if existing_artist:
                artist_id = existing_artist[0]
                logger.info(f"   ✅ Artist already exists: {demo['artist']['name']}")
            else:
                # Create artist
                artist_id = audio_service.create_artist(demo["artist"])
                stats["artists_created"] += 1
                logger.info(f"   ✅ Created artist: {demo['artist']['name']} (ID: {artist_id})")

            # Check if album exists
            existing_album = conn.execute(
                "SELECT id FROM audio_content WHERE title = ? AND primary_artist_id = ?",
                [demo["album"]["title"], artist_id]
            ).fetchone()

            if existing_album:
                logger.info(f"   ⚠️  Album already exists: {demo['album']['title']}")
                stats["albums_skipped"] += 1
                continue

            # Create album
            album_data = {
                **demo["album"],
                "primary_artist_id": artist_id,
            }

            album_id = audio_service.create_audio_content(album_data)
            stats["albums_created"] += 1

            logger.info(
                f"   ✅ Created album: {demo['album']['title']} "
                f"(ID: {album_id}, Tracks: {demo['album']['total_tracks']})"
            )

        except Exception as e:
            logger.error(f"   ❌ Error loading album: {e}")

    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 DEMO ALBUM LOADING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total albums processed: {stats['total']}")
    logger.info(f"👤 Artists created: {stats['artists_created']}")
    logger.info(f"💿 Albums created: {stats['albums_created']}")
    logger.info(f"⚠️  Albums skipped (already exist): {stats['albums_skipped']}")
    logger.info("=" * 80)

    return stats


if __name__ == "__main__":
    load_demo_albums()
