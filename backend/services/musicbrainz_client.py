"""
MusicBrainz API Client.

Fetches soundtrack and music metadata from MusicBrainz open database.
"""

import httpx
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class MusicBrainzClient:
    """
    Client for interacting with MusicBrainz API.

    MusicBrainz is a free, open music encyclopedia that collects music metadata.
    """

    BASE_URL = "https://musicbrainz.org/ws/2"

    # User-Agent is REQUIRED by MusicBrainz API
    USER_AGENT = "Xilften/1.0.0 (https://github.com/yourusername/xilften)"

    # Rate limiting: 1 request per second
    RATE_LIMIT_DELAY = 1.0

    def __init__(self):
        """
        Initialize MusicBrainz client.
        """
        self.last_request_time = 0.0

    async def _rate_limit(self):
        """
        Enforce rate limiting to comply with MusicBrainz API guidelines.

        MusicBrainz allows 1 request per second.
        """
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - time_since_last)

        self.last_request_time = asyncio.get_event_loop().time()

    async def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to MusicBrainz API.

        Args:
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters

        Returns:
            dict: JSON response data

        Raises:
            httpx.HTTPError: If request fails
        """
        await self._rate_limit()

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"User-Agent": self.USER_AGENT, "Accept": "application/json"}

        params = params or {}
        params["fmt"] = "json"  # Request JSON format

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"MusicBrainz API request failed: {e}")
                raise

    async def search_soundtrack(
        self, movie_title: str, year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for movie soundtrack by movie title.

        Args:
            movie_title (str): Movie title to search for
            year (int, optional): Release year to narrow search

        Returns:
            list: List of soundtrack release dictionaries
        """
        try:
            # Build search query
            # MusicBrainz uses Lucene query syntax
            query_parts = [f'"{movie_title}"']

            if year:
                # Search within ±1 year range
                query_parts.append(f"date:[{year-1} TO {year+1}]")

            # Search for soundtrack releases
            query_parts.append('type:"soundtrack"')

            query = " AND ".join(query_parts)

            logger.info(f"🎵 Searching MusicBrainz for soundtrack: {movie_title}")

            response = await self._make_request(
                "release", params={"query": query, "limit": 10}
            )

            releases = response.get("releases", [])

            logger.info(f"✅ Found {len(releases)} soundtrack results for '{movie_title}'")

            return releases

        except Exception as e:
            logger.error(f"❌ Error searching MusicBrainz for '{movie_title}': {e}")
            return []

    async def get_release_details(
        self, release_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific release.

        Args:
            release_id (str): MusicBrainz release ID (MBID)

        Returns:
            dict: Detailed release information with tracks
        """
        try:
            logger.info(f"🎵 Fetching MusicBrainz release details: {release_id}")

            response = await self._make_request(
                f"release/{release_id}",
                params={"inc": "recordings+artist-credits+release-groups+labels"},
            )

            logger.info(f"✅ Retrieved release details for {release_id}")

            return response

        except Exception as e:
            logger.error(f"❌ Error fetching release details for {release_id}: {e}")
            return None

    async def get_release_with_tracks(
        self, release_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get release with full track listing.

        Args:
            release_id (str): MusicBrainz release ID

        Returns:
            dict: Release with media and tracks
        """
        try:
            logger.info(f"🎵 Fetching MusicBrainz release with tracks: {release_id}")

            response = await self._make_request(
                f"release/{release_id}",
                params={"inc": "recordings+artist-credits+media"},
            )

            logger.info(f"✅ Retrieved {len(response.get('media', []))} media for {release_id}")

            return response

        except Exception as e:
            logger.error(f"❌ Error fetching release with tracks for {release_id}: {e}")
            return None

    def extract_soundtrack_metadata(self, release: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured metadata from MusicBrainz release.

        Args:
            release (dict): MusicBrainz release object

        Returns:
            dict: Structured soundtrack metadata
        """
        # Extract basic info
        title = release.get("title", "")
        release_id = release.get("id")
        date = release.get("date", "")

        # Extract label
        label = None
        label_info = release.get("label-info", [])
        if label_info:
            label = label_info[0].get("label", {}).get("name")

        # Count tracks
        media = release.get("media", [])
        total_tracks = sum(m.get("track-count", 0) for m in media)

        # Get cover art URL (if available)
        cover_art_url = None
        if release_id:
            cover_art_url = f"https://coverartarchive.org/release/{release_id}/front-500"

        metadata = {
            "title": title,
            "musicbrainz_id": release_id,
            "release_date": date if date else None,
            "label": label,
            "total_tracks": total_tracks,
            "album_art_url": cover_art_url,
            "album_type": "soundtrack",
        }

        return metadata

    def extract_tracks(self, release: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract track listing from MusicBrainz release.

        Args:
            release (dict): MusicBrainz release with media

        Returns:
            list: List of track dictionaries
        """
        tracks = []

        media_list = release.get("media", [])

        for disc_num, media in enumerate(media_list, 1):
            track_list = media.get("tracks", [])

            for track in track_list:
                # Extract track info
                track_number = track.get("position", 0)
                title = track.get("title", "")
                length_ms = track.get("length")  # in milliseconds

                # Extract recording info
                recording = track.get("recording", {})
                recording_id = recording.get("id")

                # Extract artist
                artist_credit = recording.get("artist-credit", [])
                artist = ""
                if artist_credit:
                    artist = artist_credit[0].get("name", "")

                track_data = {
                    "track_number": track_number,
                    "disc_number": disc_num,
                    "title": title,
                    "artist": artist,
                    "duration_ms": length_ms,
                    "musicbrainz_recording_id": recording_id,
                }

                tracks.append(track_data)

        return tracks


# Global client instance
musicbrainz_client = MusicBrainzClient()
