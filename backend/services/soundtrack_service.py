"""
Soundtrack Service.

Coordinates soundtrack data fetching from multiple sources and database operations.
"""

import logging
import uuid
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

from config.database import db_manager
from backend.services.musicbrainz_client import musicbrainz_client
from backend.services.spotify_client import spotify_client

logger = logging.getLogger(__name__)


class SoundtrackService:
    """
    Service for managing movie soundtracks.

    Coordinates data from MusicBrainz and Spotify, handles database operations.
    """

    def __init__(self):
        """Initialize soundtrack service."""
        self.mb_client = musicbrainz_client
        self.spotify_client = spotify_client

    async def search_and_save_soundtrack(
        self, media_id: str, movie_title: str, year: Optional[int] = None
    ) -> Optional[str]:
        """
        Search for and save soundtrack data for a movie.

        Args:
            media_id (str): Media ID from database
            movie_title (str): Movie title
            year (int, optional): Release year

        Returns:
            str: Soundtrack ID if successful, None otherwise
        """
        try:
            logger.info(f"🎵 Searching soundtrack for: {movie_title} ({year})")

            # Check if soundtrack already exists
            existing = self.get_soundtrack_by_media_id(media_id)
            if existing:
                logger.info(f"⏭️  Soundtrack already exists for {movie_title}")
                return existing[0]  # Return existing soundtrack ID

            # Search MusicBrainz first (free, comprehensive)
            mb_results = await self.mb_client.search_soundtrack(movie_title, year)

            if not mb_results:
                logger.warning(f"⚠️  No soundtracks found on MusicBrainz for {movie_title}")
                return None

            # Take the best match (first result)
            best_match = mb_results[0]
            release_id = best_match.get("id")

            if not release_id:
                logger.warning(f"⚠️  No valid release ID found for {movie_title}")
                return None

            # Get full release details with tracks
            release_details = await self.mb_client.get_release_with_tracks(release_id)

            if not release_details:
                logger.error(f"❌ Failed to fetch release details for {movie_title}")
                return None

            # Extract structured metadata
            soundtrack_metadata = self.mb_client.extract_soundtrack_metadata(release_details)
            tracks_data = self.mb_client.extract_tracks(release_details)

            # Enhance with Spotify data (optional, for preview URLs)
            if self.spotify_client.enabled:
                await self._enhance_with_spotify(soundtrack_metadata, tracks_data, movie_title, year)

            # Save to database
            soundtrack_id = self.save_soundtrack_to_db(
                media_id, soundtrack_metadata, tracks_data
            )

            if soundtrack_id:
                logger.info(f"✅ Successfully saved soundtrack for {movie_title}")
                return soundtrack_id
            else:
                logger.error(f"❌ Failed to save soundtrack for {movie_title}")
                return None

        except Exception as e:
            logger.error(f"❌ Error searching/saving soundtrack for {movie_title}: {e}")
            return None

    async def _enhance_with_spotify(
        self,
        soundtrack_metadata: Dict[str, Any],
        tracks_data: List[Dict[str, Any]],
        movie_title: str,
        year: Optional[int],
    ):
        """
        Enhance soundtrack and track data with Spotify information.

        Args:
            soundtrack_metadata (dict): MusicBrainz soundtrack metadata (modified in place)
            tracks_data (list): MusicBrainz tracks data (modified in place)
            movie_title (str): Movie title
            year (int, optional): Release year
        """
        try:
            # Search for album on Spotify
            spotify_albums = await self.spotify_client.search_soundtrack(movie_title, year=year)

            if not spotify_albums:
                logger.info(f"ℹ️  No Spotify results for {movie_title}")
                return

            # Take best match
            spotify_album = spotify_albums[0]
            album_id = spotify_album.get("id")

            if not album_id:
                return

            # Get full album details
            album_details = await self.spotify_client.get_album_details(album_id)

            if album_details:
                # Update soundtrack metadata with Spotify info
                soundtrack_metadata["spotify_album_id"] = album_id

                # If MusicBrainz didn't have album art, use Spotify's
                if not soundtrack_metadata.get("album_art_url"):
                    images = album_details.get("images", [])
                    if images:
                        soundtrack_metadata["album_art_url"] = images[0].get("url")

            # Get tracks from Spotify
            spotify_tracks = await self.spotify_client.get_album_tracks(album_id)

            if spotify_tracks:
                # Match Spotify tracks to MusicBrainz tracks by title
                self._match_spotify_tracks(tracks_data, spotify_tracks)

            logger.info(f"✅ Enhanced {movie_title} with Spotify data")

        except Exception as e:
            logger.warning(f"⚠️  Error enhancing with Spotify data: {e}")
            # Continue without Spotify enhancement

    def _match_spotify_tracks(
        self, mb_tracks: List[Dict[str, Any]], spotify_tracks: List[Dict[str, Any]]
    ):
        """
        Match Spotify tracks to MusicBrainz tracks and add preview URLs.

        Args:
            mb_tracks (list): MusicBrainz tracks (modified in place)
            spotify_tracks (list): Spotify tracks
        """
        for mb_track in mb_tracks:
            mb_title = mb_track.get("title", "").lower()

            # Find matching Spotify track
            for sp_track in spotify_tracks:
                sp_title = sp_track.get("name", "").lower()

                # Simple title matching (can be improved with fuzzy matching)
                if mb_title == sp_title:
                    # Add Spotify data to MusicBrainz track
                    mb_track["spotify_track_id"] = sp_track.get("id")
                    mb_track["preview_url"] = sp_track.get("preview_url")
                    mb_track["spotify_uri"] = f"spotify:track:{sp_track.get('id')}"
                    break

    def save_soundtrack_to_db(
        self,
        media_id: str,
        soundtrack_metadata: Dict[str, Any],
        tracks_data: List[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Save soundtrack and tracks to database.

        Args:
            media_id (str): Media ID
            soundtrack_metadata (dict): Soundtrack metadata
            tracks_data (list): List of track dictionaries

        Returns:
            str: Soundtrack ID if successful, None otherwise
        """
        try:
            conn = db_manager.get_duckdb_connection()

            # Generate soundtrack ID
            soundtrack_id = str(uuid.uuid4())

            # Prepare soundtrack insert
            soundtrack_query = """
                INSERT INTO soundtracks (
                    id, media_id, title, release_date, label,
                    musicbrainz_id, spotify_album_id,
                    album_art_url, total_tracks, album_type,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            now = datetime.now().isoformat()

            conn.execute(
                soundtrack_query,
                [
                    soundtrack_id,
                    media_id,
                    soundtrack_metadata.get("title"),
                    soundtrack_metadata.get("release_date"),
                    soundtrack_metadata.get("label"),
                    soundtrack_metadata.get("musicbrainz_id"),
                    soundtrack_metadata.get("spotify_album_id"),
                    soundtrack_metadata.get("album_art_url"),
                    soundtrack_metadata.get("total_tracks", 0),
                    soundtrack_metadata.get("album_type", "soundtrack"),
                    now,
                    now,
                ],
            )

            # Insert tracks
            track_query = """
                INSERT INTO soundtrack_tracks (
                    id, soundtrack_id, track_number, disc_number,
                    title, artist, duration_ms,
                    musicbrainz_recording_id, spotify_track_id,
                    preview_url, spotify_uri,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for track in tracks_data:
                track_id = str(uuid.uuid4())

                conn.execute(
                    track_query,
                    [
                        track_id,
                        soundtrack_id,
                        track.get("track_number", 0),
                        track.get("disc_number", 1),
                        track.get("title"),
                        track.get("artist"),
                        track.get("duration_ms"),
                        track.get("musicbrainz_recording_id"),
                        track.get("spotify_track_id"),
                        track.get("preview_url"),
                        track.get("spotify_uri"),
                        now,
                    ],
                )

            logger.info(
                f"✅ Saved soundtrack {soundtrack_id} with {len(tracks_data)} tracks"
            )

            return soundtrack_id

        except Exception as e:
            logger.error(f"❌ Error saving soundtrack to database: {e}")
            return None

    def get_soundtrack_by_media_id(self, media_id: str) -> Optional[List[str]]:
        """
        Get soundtrack IDs for a media item.

        Args:
            media_id (str): Media ID

        Returns:
            list: List of soundtrack IDs or None
        """
        try:
            conn = db_manager.get_duckdb_connection()

            query = "SELECT id FROM soundtracks WHERE media_id = ?"
            results = conn.execute(query, [media_id]).fetchall()

            if results:
                return [row[0] for row in results]

            return None

        except Exception as e:
            logger.error(f"❌ Error fetching soundtracks for media {media_id}: {e}")
            return None

    def get_soundtrack_with_tracks(self, soundtrack_id: str) -> Optional[Dict[str, Any]]:
        """
        Get soundtrack details with full track listing.

        Args:
            soundtrack_id (str): Soundtrack ID

        Returns:
            dict: Soundtrack with tracks or None
        """
        try:
            conn = db_manager.get_duckdb_connection()

            # Get soundtrack
            soundtrack_query = """
                SELECT id, media_id, title, release_date, label,
                       musicbrainz_id, spotify_album_id, album_art_url,
                       total_tracks, album_type, created_at
                FROM soundtracks
                WHERE id = ?
            """

            soundtrack_result = conn.execute(soundtrack_query, [soundtrack_id]).fetchone()

            if not soundtrack_result:
                return None

            columns = [
                "id",
                "media_id",
                "title",
                "release_date",
                "label",
                "musicbrainz_id",
                "spotify_album_id",
                "album_art_url",
                "total_tracks",
                "album_type",
                "created_at",
            ]

            soundtrack = dict(zip(columns, soundtrack_result))

            # Get tracks
            tracks_query = """
                SELECT id, track_number, disc_number, title, artist,
                       duration_ms, spotify_track_id, preview_url, spotify_uri
                FROM soundtrack_tracks
                WHERE soundtrack_id = ?
                ORDER BY disc_number, track_number
            """

            tracks_results = conn.execute(tracks_query, [soundtrack_id]).fetchall()

            track_columns = [
                "id",
                "track_number",
                "disc_number",
                "title",
                "artist",
                "duration_ms",
                "spotify_track_id",
                "preview_url",
                "spotify_uri",
            ]

            tracks = [dict(zip(track_columns, row)) for row in tracks_results]

            soundtrack["tracks"] = tracks

            return soundtrack

        except Exception as e:
            logger.error(f"❌ Error fetching soundtrack {soundtrack_id}: {e}")
            return None


# Global service instance
soundtrack_service = SoundtrackService()
