"""
Spotify API Client.

Fetches soundtrack metadata and playback URLs from Spotify.
Requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables.
"""

import httpx
import base64
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SpotifyClient:
    """
    Client for interacting with Spotify Web API.

    Handles authentication and provides methods to search for soundtracks
    and retrieve track preview URLs.
    """

    BASE_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize Spotify client.

        Args:
            client_id (str, optional): Spotify Client ID
            client_secret (str, optional): Spotify Client Secret
        """
        import os

        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")

        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

        # Check if credentials are available
        self.enabled = bool(self.client_id and self.client_secret)

        if not self.enabled:
            logger.warning(
                "⚠️  Spotify API credentials not found. "
                "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to enable Spotify integration."
            )

    async def _get_access_token(self) -> Optional[str]:
        """
        Get or refresh Spotify access token using Client Credentials flow.

        Returns:
            str: Access token or None if authentication fails
        """
        if not self.enabled:
            return None

        # Check if current token is still valid
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # Request new token
        try:
            # Encode credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {credentials_b64}",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            data = {"grant_type": "client_credentials"}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.AUTH_URL, headers=headers, data=data)
                response.raise_for_status()

                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)  # Default 1 hour

                # Set expiration time (subtract 5 minutes for safety)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

                logger.info("✅ Spotify access token obtained")
                return self.access_token

        except Exception as e:
            logger.error(f"❌ Failed to obtain Spotify access token: {e}")
            return None

    async def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make authenticated HTTP request to Spotify API.

        Args:
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters

        Returns:
            dict: JSON response data or None if request fails
        """
        if not self.enabled:
            return None

        token = await self._get_access_token()
        if not token:
            return None

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"❌ Spotify API request failed: {e}")
                return None

    async def search_soundtrack(
        self, movie_title: str, artist: Optional[str] = None, year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for movie soundtrack on Spotify.

        Args:
            movie_title (str): Movie title to search for
            artist (str, optional): Artist/composer name
            year (int, optional): Release year

        Returns:
            list: List of album dictionaries
        """
        if not self.enabled:
            return []

        try:
            # Build search query
            query_parts = [f'"{movie_title}"']

            if artist:
                query_parts.append(f'artist:"{artist}"')

            if year:
                query_parts.append(f"year:{year}")

            query = " ".join(query_parts)

            logger.info(f"🎵 Searching Spotify for soundtrack: {movie_title}")

            response = await self._make_request(
                "search", params={"q": query, "type": "album", "limit": 10}
            )

            if not response:
                return []

            albums = response.get("albums", {}).get("items", [])

            # Filter for soundtracks
            soundtracks = []
            for album in albums:
                album_name = album.get("name", "").lower()
                if any(keyword in album_name for keyword in ["soundtrack", "score", "original"]):
                    soundtracks.append(album)

            logger.info(f"✅ Found {len(soundtracks)} soundtracks on Spotify for '{movie_title}'")

            return soundtracks

        except Exception as e:
            logger.error(f"❌ Error searching Spotify for '{movie_title}': {e}")
            return []

    async def search_album(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for albums on Spotify.

        Args:
            query (str): Search query (can include artist:, year:, etc.)
            limit (int): Maximum number of results

        Returns:
            list: List of album dictionaries
        """
        if not self.enabled:
            return []

        try:
            logger.info(f"🎵 Searching Spotify for albums: {query}")

            response = await self._make_request(
                "search", params={"q": query, "type": "album", "limit": limit}
            )

            if not response:
                return []

            albums = response.get("albums", {}).get("items", [])

            logger.info(f"✅ Found {len(albums)} albums on Spotify")

            return albums

        except Exception as e:
            logger.error(f"❌ Error searching Spotify albums: {e}")
            return []

    async def get_album_tracks(self, album_id: str) -> List[Dict[str, Any]]:
        """
        Get tracks from a Spotify album.

        Args:
            album_id (str): Spotify album ID

        Returns:
            list: List of track dictionaries
        """
        if not self.enabled:
            return []

        try:
            logger.info(f"🎵 Fetching Spotify album tracks: {album_id}")

            response = await self._make_request(f"albums/{album_id}/tracks", params={"limit": 50})

            if not response:
                return []

            tracks = response.get("items", [])

            logger.info(f"✅ Retrieved {len(tracks)} tracks from Spotify album {album_id}")

            return tracks

        except Exception as e:
            logger.error(f"❌ Error fetching Spotify album tracks for {album_id}: {e}")
            return []

    async def get_album_details(self, album_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a Spotify album.

        Args:
            album_id (str): Spotify album ID

        Returns:
            dict: Album details or None
        """
        if not self.enabled:
            return None

        try:
            logger.info(f"🎵 Fetching Spotify album details: {album_id}")

            response = await self._make_request(f"albums/{album_id}")

            if response:
                logger.info(f"✅ Retrieved Spotify album details for {album_id}")

            return response

        except Exception as e:
            logger.error(f"❌ Error fetching Spotify album details for {album_id}: {e}")
            return None

    def extract_album_metadata(self, album: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured metadata from Spotify album.

        Args:
            album (dict): Spotify album object

        Returns:
            dict: Structured soundtrack metadata
        """
        # Extract basic info
        title = album.get("name", "")
        album_id = album.get("id")
        release_date = album.get("release_date", "")

        # Extract label
        label = album.get("label")

        # Get album art
        images = album.get("images", [])
        album_art_url = images[0].get("url") if images else None

        # Total tracks
        total_tracks = album.get("total_tracks", 0)

        # Extract artists
        artists = album.get("artists", [])
        artist_names = [a.get("name") for a in artists]

        metadata = {
            "title": title,
            "spotify_album_id": album_id,
            "release_date": release_date if release_date else None,
            "label": label,
            "total_tracks": total_tracks,
            "album_art_url": album_art_url,
            "artists": artist_names,
            "album_type": "soundtrack",
        }

        return metadata

    def extract_track_data(self, track: Dict[str, Any], track_number: int) -> Dict[str, Any]:
        """
        Extract structured data from Spotify track.

        Args:
            track (dict): Spotify track object
            track_number (int): Track position

        Returns:
            dict: Structured track data
        """
        title = track.get("name", "")
        track_id = track.get("id")
        duration_ms = track.get("duration_ms")
        preview_url = track.get("preview_url")  # 30-second preview
        explicit = track.get("explicit", False)
        disc_number = track.get("disc_number", 1)

        # Extract artists
        artists = track.get("artists", [])
        artist_names = [a.get("name") for a in artists]
        artist = ", ".join(artist_names) if artist_names else ""

        # Build Spotify URI
        spotify_uri = f"spotify:track:{track_id}" if track_id else None

        track_data = {
            "track_number": track_number,
            "disc_number": disc_number,
            "title": title,
            "artist": artist,
            "duration_ms": duration_ms,
            "spotify_track_id": track_id,
            "preview_url": preview_url,
            "spotify_uri": spotify_uri,
            "explicit": explicit,
        }

        return track_data


# Global client instance
spotify_client = SpotifyClient()
