#!/usr/bin/env python3
"""
Spotify API Service for audio content integration.

This service provides methods to:
- Search for albums, artists, and tracks
- Retrieve detailed album and track information
- Fetch audio features for tracks
- Get artist information and discography
"""

import asyncio
import base64
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel

from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class SpotifyToken(BaseModel):
    """Spotify API access token model."""
    access_token: str
    token_type: str
    expires_at: datetime


class SpotifyService:
    """
    Service for interacting with Spotify Web API.

    Handles authentication, rate limiting, and provides methods for
    searching and retrieving music catalog data.
    """

    def __init__(self):
        """Initialize Spotify service with credentials from settings."""
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"

        self._token: Optional[SpotifyToken] = None
        self._http_client: Optional[httpx.AsyncClient] = None

        logger.info("🎵 SpotifyService initialized")

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def _get_access_token(self) -> str:
        """
        Get valid Spotify API access token.

        Uses client credentials flow to obtain access token.
        Caches token and refreshes when expired.

        Returns:
            str: Valid access token

        Raises:
            Exception: If authentication fails
        """
        # Check if we have a valid cached token
        if self._token and self._token.expires_at > datetime.now():
            return self._token.access_token

        # Get new token
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Spotify credentials not configured. "
                "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables."
            )

        logger.info("🔑 Requesting new Spotify access token")

        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials"
        }

        client = await self._get_http_client()
        response = await client.post(self.auth_url, headers=headers, data=data)

        if response.status_code != 200:
            logger.error(f"❌ Spotify auth failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            raise Exception(f"Spotify authentication failed: {response.status_code}")

        token_data = response.json()

        # Calculate expiration time (expires_in is in seconds)
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # 60s buffer

        self._token = SpotifyToken(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_at=expires_at
        )

        logger.info("✅ Spotify access token obtained")
        return self._token.access_token

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Spotify API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/search")
            params: Query parameters
            json_data: JSON body data

        Returns:
            Dict containing API response

        Raises:
            Exception: If request fails
        """
        token = await self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"{self.base_url}{endpoint}"

        client = await self._get_http_client()
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data
        )

        if response.status_code == 429:
            # Rate limited
            retry_after = int(response.headers.get("Retry-After", 1))
            logger.warning(f"⚠️ Rate limited, waiting {retry_after}s")
            await asyncio.sleep(retry_after)
            return await self._make_request(method, endpoint, params, json_data)

        if response.status_code not in [200, 201]:
            logger.error(f"❌ Spotify API error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            raise Exception(f"Spotify API error: {response.status_code}")

        return response.json()

    async def search_album(
        self,
        query: str,
        artist: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for albums on Spotify.

        Args:
            query: Album title search query
            artist: Optional artist name to refine search
            limit: Maximum number of results (default 10)

        Returns:
            List of album objects
        """
        search_query = f"album:{query}"
        if artist:
            search_query += f" artist:{artist}"

        params = {
            "q": search_query,
            "type": "album",
            "limit": limit
        }

        result = await self._make_request("GET", "/search", params=params)
        return result.get("albums", {}).get("items", [])

    async def get_album(self, album_id: str) -> Dict[str, Any]:
        """
        Get detailed album information.

        Args:
            album_id: Spotify album ID

        Returns:
            Album object with tracks
        """
        return await self._make_request("GET", f"/albums/{album_id}")

    async def get_album_tracks(self, album_id: str) -> List[Dict[str, Any]]:
        """
        Get tracks for an album.

        Args:
            album_id: Spotify album ID

        Returns:
            List of track objects
        """
        result = await self._make_request("GET", f"/albums/{album_id}/tracks")
        return result.get("items", [])

    async def get_track(self, track_id: str) -> Dict[str, Any]:
        """
        Get detailed track information.

        Args:
            track_id: Spotify track ID

        Returns:
            Track object
        """
        return await self._make_request("GET", f"/tracks/{track_id}")

    async def get_audio_features(self, track_id: str) -> Dict[str, Any]:
        """
        Get audio features for a track.

        Audio features include:
        - acousticness, danceability, energy, instrumentalness
        - liveness, loudness, speechiness, valence
        - tempo, time_signature, key, mode

        Args:
            track_id: Spotify track ID

        Returns:
            Audio features object
        """
        return await self._make_request("GET", f"/audio-features/{track_id}")

    async def get_artist(self, artist_id: str) -> Dict[str, Any]:
        """
        Get detailed artist information.

        Args:
            artist_id: Spotify artist ID

        Returns:
            Artist object
        """
        return await self._make_request("GET", f"/artists/{artist_id}")

    async def get_artist_albums(
        self,
        artist_id: str,
        include_groups: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get albums by an artist.

        Args:
            artist_id: Spotify artist ID
            include_groups: Album types to include (album, single, compilation, appears_on)
            limit: Maximum number of results

        Returns:
            List of album objects
        """
        params = {"limit": limit}

        if include_groups:
            params["include_groups"] = ",".join(include_groups)
        else:
            params["include_groups"] = "album,single"

        result = await self._make_request(
            "GET",
            f"/artists/{artist_id}/albums",
            params=params
        )
        return result.get("items", [])

    async def search_artist(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for artists on Spotify.

        Args:
            query: Artist name search query
            limit: Maximum number of results

        Returns:
            List of artist objects
        """
        params = {
            "q": query,
            "type": "artist",
            "limit": limit
        }

        result = await self._make_request("GET", "/search", params=params)
        return result.get("artists", {}).get("items", [])

    async def close(self):
        """Close HTTP client connection."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
            logger.info("🔌 Spotify HTTP client closed")


# Global service instance
spotify_service = SpotifyService()
