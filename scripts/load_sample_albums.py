#!/usr/bin/env python3
"""
Load Sample Albums from Spotify.

Searches for and ingests popular albums from Spotify into the audio catalog.
Gracefully handles the case where Spotify API credentials are not configured.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.spotify_client import SpotifyClient
from backend.services.audio_service import get_audio_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample albums to search for (well-known popular albums)
SAMPLE_ALBUMS = [
    {"artist": "Pink Floyd", "album": "The Dark Side of the Moon", "year": 1973},
    {"artist": "The Beatles", "album": "Abbey Road", "year": 1969},
    {"artist": "Led Zeppelin", "album": "Led Zeppelin IV", "year": 1971},
    {"artist": "Fleetwood Mac", "album": "Rumours", "year": 1977},
    {"artist": "Michael Jackson", "album": "Thriller", "year": 1982},
    {"artist": "Nirvana", "album": "Nevermind", "year": 1991},
    {"artist": "Radiohead", "album": "OK Computer", "year": 1997},
    {"artist": "Daft Punk", "album": "Random Access Memories", "year": 2013},
    {"artist": "Kendrick Lamar", "album": "good kid, m.A.A.d city", "year": 2012},
    {"artist": "Taylor Swift", "album": "1989", "year": 2014},
]


async def search_and_load_album(
    spotify_client: SpotifyClient,
    audio_service,
    artist_name: str,
    album_name: str,
    year: int,
) -> dict:
    """
    Search for an album on Spotify and load it into the database.

    Args:
        spotify_client (SpotifyClient): Spotify API client
        audio_service: Audio service instance
        artist_name (str): Artist name
        album_name (str): Album name
        year (int): Release year

    Returns:
        dict: Result statistics
    """
    result = {"success": False, "message": "", "artists_created": 0, "albums_created": 0}

    try:
        logger.info(f"🔍 Searching for: {artist_name} - {album_name} ({year})")

        # Search Spotify for the album
        albums = await spotify_client.search_album(
            query=f"{album_name} artist:{artist_name}", limit=5
        )

        if not albums:
            result["message"] = "Album not found on Spotify"
            logger.warning(f"   ⚠️  Album not found: {artist_name} - {album_name}")
            return result

        # Get the first match
        album = albums[0]
        album_id = album.get("id")
        album_title = album.get("name")
        album_artists = album.get("artists", [])

        logger.info(f"   ✅ Found on Spotify: {album_title} (ID: {album_id})")

        # Get album details
        album_details = await spotify_client.get_album_details(album_id)

        if not album_details:
            result["message"] = "Failed to fetch album details"
            return result

        # Process primary artist
        if not album_artists:
            result["message"] = "No artists found"
            return result

        primary_artist_data = album_artists[0]
        artist_spotify_id = primary_artist_data.get("id")
        artist_name_spotify = primary_artist_data.get("name")

        # Check if artist exists
        conn = audio_service.get_connection()
        existing_artist = conn.execute(
            "SELECT id FROM audio_artists WHERE spotify_id = ?", [artist_spotify_id]
        ).fetchone()

        if existing_artist:
            artist_id = existing_artist[0]
            logger.info(f"   ✅ Artist already exists: {artist_name_spotify}")
        else:
            # Create artist
            artist_data = {
                "name": artist_name_spotify,
                "sort_name": artist_name_spotify,
                "artist_type": "group",  # Default to group
                "spotify_id": artist_spotify_id,
            }

            artist_id = audio_service.create_artist(artist_data)
            result["artists_created"] += 1
            logger.info(f"   ✅ Created artist: {artist_name_spotify} (ID: {artist_id})")

        # Check if album already exists
        existing_album = conn.execute(
            "SELECT id FROM audio_content WHERE spotify_id = ?", [album_id]
        ).fetchone()

        if existing_album:
            logger.info(f"   ⚠️  Album already exists: {album_title}")
            result["message"] = "Album already exists"
            result["success"] = True
            return result

        # Create album
        release_date_str = album_details.get("release_date", "")
        release_date = None
        release_year = None

        if release_date_str:
            try:
                release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
                release_year = release_date.year
            except ValueError:
                try:
                    release_year = int(release_date_str[:4])
                except (ValueError, IndexError):
                    pass

        images = album_details.get("images", [])
        cover_art_url = images[0].get("url") if images else None
        cover_art_small_url = images[-1].get("url") if len(images) > 1 else None
        cover_art_large_url = images[0].get("url") if images else None

        album_data = {
            "title": album_title,
            "content_type": album_details.get("album_type", "album"),
            "primary_artist_id": artist_id,
            "release_date": release_date,
            "release_year": release_year or year,
            "total_tracks": album_details.get("total_tracks"),
            "cover_art_url": cover_art_url,
            "cover_art_small_url": cover_art_small_url,
            "cover_art_large_url": cover_art_large_url,
            "record_label": album_details.get("label"),
            "spotify_id": album_id,
            "spotify_popularity": album_details.get("popularity"),
        }

        audio_content_id = audio_service.create_audio_content(album_data)
        result["albums_created"] += 1

        logger.info(
            f"   ✅ Created album: {album_title} (ID: {audio_content_id}, Tracks: {album_data['total_tracks']})"
        )

        # Get and create tracks
        tracks_data = album_details.get("tracks", {}).get("items", [])

        if tracks_data:
            logger.info(f"   🎵 Loading {len(tracks_data)} tracks...")

            for track in tracks_data:
                track_data = {
                    "audio_content_id": audio_content_id,
                    "title": track.get("name"),
                    "track_number": track.get("track_number"),
                    "disc_number": track.get("disc_number", 1),
                    "duration_ms": track.get("duration_ms"),
                    "explicit": track.get("explicit", False),
                    "spotify_id": track.get("id"),
                    "spotify_preview_url": track.get("preview_url"),
                }

                audio_service.create_audio_track(track_data)

            logger.info(f"   ✅ Created {len(tracks_data)} tracks")

        result["success"] = True
        result["message"] = f"Successfully loaded album with {len(tracks_data)} tracks"

    except Exception as e:
        result["message"] = f"Error: {str(e)}"
        logger.error(f"   ❌ Error loading album: {e}")

    return result


async def main():
    """
    Main entry point.
    """
    logger.info("=" * 80)
    logger.info("🎵 LOADING SAMPLE ALBUMS FROM SPOTIFY")
    logger.info("=" * 80)
    logger.info("")

    # Initialize services
    spotify_client = SpotifyClient()
    audio_service = get_audio_service()

    if not spotify_client.enabled:
        logger.error("=" * 80)
        logger.error("❌ SPOTIFY API NOT CONFIGURED")
        logger.error("=" * 80)
        logger.error("")
        logger.error("To use this script, set the following environment variables:")
        logger.error("  - SPOTIFY_CLIENT_ID")
        logger.error("  - SPOTIFY_CLIENT_SECRET")
        logger.error("")
        logger.error("Get credentials from: https://developer.spotify.com/dashboard")
        logger.error("=" * 80)
        sys.exit(1)

    stats = {
        "total": len(SAMPLE_ALBUMS),
        "success": 0,
        "skipped": 0,
        "errors": 0,
        "artists_created": 0,
        "albums_created": 0,
    }

    for i, sample in enumerate(SAMPLE_ALBUMS, 1):
        logger.info("")
        logger.info(f"[{i}/{stats['total']}] Processing: {sample['artist']} - {sample['album']}")

        result = await search_and_load_album(
            spotify_client,
            audio_service,
            sample["artist"],
            sample["album"],
            sample["year"],
        )

        if result["success"]:
            if result["albums_created"] > 0:
                stats["success"] += 1
            else:
                stats["skipped"] += 1
        else:
            stats["errors"] += 1

        stats["artists_created"] += result["artists_created"]
        stats["albums_created"] += result["albums_created"]

        # Rate limiting
        await asyncio.sleep(1.0)

    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 ALBUM LOADING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total albums processed: {stats['total']}")
    logger.info(f"✅ Successfully loaded: {stats['success']}")
    logger.info(f"⚠️  Already existed: {stats['skipped']}")
    logger.info(f"❌ Errors: {stats['errors']}")
    logger.info(f"👤 Artists created: {stats['artists_created']}")
    logger.info(f"💿 Albums created: {stats['albums_created']}")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
