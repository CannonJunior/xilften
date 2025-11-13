"""
IMDB Soundtrack Source.

Scrapes soundtrack data from IMDB movie pages.
"""

import logging
import re
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
import httpx

from .base import SoundtrackSource, SoundtrackMetadata, SoundtrackTrack

logger = logging.getLogger(__name__)


class IMDBSoundtrackSource(SoundtrackSource):
    """
    IMDB soundtrack data source.

    Scrapes soundtrack information from IMDB movie pages.
    """

    def __init__(self):
        """Initialize IMDB soundtrack source."""
        super().__init__("imdb")
        self.base_url = "https://www.imdb.com"
        self.timeout = 30.0

    async def search_soundtrack(
        self,
        movie_title: str,
        year: Optional[int] = None,
        imdb_id: Optional[str] = None
    ) -> Optional[Tuple[SoundtrackMetadata, List[SoundtrackTrack]]]:
        """
        Search for soundtrack on IMDB.

        Args:
            movie_title (str): Movie title
            year (int, optional): Release year
            imdb_id (str, optional): IMDB ID (e.g., "tt0133093")

        Returns:
            tuple: (SoundtrackMetadata, List[SoundtrackTrack]) or None
        """
        try:
            # If no IMDB ID provided, search for it
            if not imdb_id:
                imdb_id = await self._search_movie(movie_title, year)
                if not imdb_id:
                    logger.info(f"Could not find IMDB ID for {movie_title}")
                    return None

            # Fetch soundtrack page
            soundtrack_url = f"{self.base_url}/title/{imdb_id}/soundtrack"

            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(
                    soundtrack_url,
                    headers={"User-Agent": "Mozilla/5.0"}
                )

                if response.status_code != 200:
                    logger.warning(f"IMDB returned status {response.status_code}")
                    return None

            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract soundtrack data
            tracks = self._extract_tracks(soup)

            if not tracks:
                logger.info(f"No soundtrack tracks found on IMDB for {imdb_id}")
                return None

            # Create metadata
            metadata = SoundtrackMetadata(
                title=f"{movie_title} - Original Soundtrack",
                album_type="soundtrack",
                external_id=imdb_id,
                external_url=soundtrack_url,
                total_tracks=len(tracks),
                source="imdb"
            )

            logger.info(f"✅ Found {len(tracks)} tracks on IMDB for {movie_title}")
            return (metadata, tracks)

        except Exception as e:
            logger.error(f"Error fetching IMDB soundtrack for {movie_title}: {e}")
            return None

    async def _search_movie(self, title: str, year: Optional[int] = None) -> Optional[str]:
        """
        Search IMDB for movie and return IMDB ID.

        Args:
            title (str): Movie title
            year (int, optional): Release year

        Returns:
            str: IMDB ID (e.g., "tt0133093") or None
        """
        try:
            search_url = f"{self.base_url}/find"
            params = {"q": title, "s": "tt", "ttype": "ft"}

            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(
                    search_url,
                    params=params,
                    headers={"User-Agent": "Mozilla/5.0"}
                )

                if response.status_code != 200:
                    return None

            soup = BeautifulSoup(response.text, 'lxml')

            # Find first result
            results = soup.select('section[data-testid="find-results-section-title"] ul li')

            for result in results[:3]:  # Check first 3 results
                link = result.select_one('a')
                if not link:
                    continue

                href = link.get('href', '')
                match = re.search(r'/title/(tt\d+)/', href)
                if match:
                    imdb_id = match.group(1)

                    # If year provided, try to verify
                    if year:
                        year_span = result.select_one('.ipc-metadata-list-summary-item__li')
                        if year_span and str(year) in year_span.text:
                            return imdb_id
                    else:
                        return imdb_id

            return None

        except Exception as e:
            logger.error(f"Error searching IMDB for {title}: {e}")
            return None

    def _extract_tracks(self, soup: BeautifulSoup) -> List[SoundtrackTrack]:
        """
        Extract soundtrack tracks from IMDB page.

        Args:
            soup (BeautifulSoup): Parsed HTML

        Returns:
            List[SoundtrackTrack]: List of tracks
        """
        tracks = []
        track_num = 1

        # IMDB soundtrack page has tracks in a list
        soundtrack_items = soup.select('.ipc-metadata-list__item')

        if not soundtrack_items:
            # Try older format
            soundtrack_items = soup.select('.soundTrack')

        for item in soundtrack_items:
            try:
                # Extract track title
                title_elem = item.select_one('.ipc-metadata-list-summary-item__t')
                if not title_elem:
                    title_elem = item.select_one('div')

                if not title_elem:
                    continue

                track_title = title_elem.text.strip()
                if not track_title:
                    continue

                # Extract artist if present
                artist = None
                artist_match = re.search(r'(?:Written|Performed|By)\s+by\s+([^(\n]+)', item.text)
                if artist_match:
                    artist = artist_match.group(1).strip()

                track = SoundtrackTrack(
                    title=track_title,
                    artist=artist,
                    track_number=track_num,
                    disc_number=1
                )

                tracks.append(track)
                track_num += 1

            except Exception as e:
                logger.warning(f"Error parsing track: {e}")
                continue

        return tracks

    def is_available(self) -> bool:
        """
        Check if IMDB source is available.

        Returns:
            bool: Always True (no API keys needed)
        """
        return True

    def get_priority(self) -> int:
        """
        Get source priority.

        Returns:
            int: 20 (lower priority than MusicBrainz)
        """
        return 20

    def supports_imdb_lookup(self) -> bool:
        """
        Check if source supports IMDB ID lookup.

        Returns:
            bool: True
        """
        return True
