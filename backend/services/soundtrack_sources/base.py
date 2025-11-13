"""
Base Soundtrack Source Interface.

Defines the interface for soundtrack data sources (MusicBrainz, IMDB, Spotify, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SoundtrackTrack:
    """
    Represents a single track in a soundtrack.

    Attributes:
        title (str): Track title
        artist (str, optional): Artist/performer
        track_number (int): Track number in the soundtrack
        disc_number (int): Disc number (for multi-disc albums)
        duration_ms (int, optional): Track duration in milliseconds
        external_id (str, optional): External source ID
        external_url (str, optional): Link to track on external source
    """
    title: str
    artist: Optional[str] = None
    track_number: int = 0
    disc_number: int = 1
    duration_ms: Optional[int] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None


@dataclass
class SoundtrackMetadata:
    """
    Represents soundtrack album metadata.

    Attributes:
        title (str): Soundtrack title
        release_date (str, optional): Release date (ISO format)
        label (str, optional): Record label
        album_type (str): Type (soundtrack, score, compilation, etc.)
        external_id (str, optional): External source ID
        external_url (str, optional): Link to soundtrack on external source
        album_art_url (str, optional): Album cover art URL
        total_tracks (int): Total number of tracks
        source (str): Source name (musicbrainz, imdb, spotify, etc.)
    """
    title: str
    release_date: Optional[str] = None
    label: Optional[str] = None
    album_type: str = "soundtrack"
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    album_art_url: Optional[str] = None
    total_tracks: int = 0
    source: str = "unknown"


class SoundtrackSource(ABC):
    """
    Abstract base class for soundtrack data sources.

    Each source (MusicBrainz, IMDB, Spotify, etc.) should implement this interface.
    """

    def __init__(self, source_name: str):
        """
        Initialize soundtrack source.

        Args:
            source_name (str): Name of the source (e.g., "musicbrainz", "imdb")
        """
        self.source_name = source_name
        self.enabled = True
        logger.info(f"🎵 Initialized {source_name} soundtrack source")

    @abstractmethod
    async def search_soundtrack(
        self,
        movie_title: str,
        year: Optional[int] = None,
        imdb_id: Optional[str] = None
    ) -> Optional[Tuple[SoundtrackMetadata, List[SoundtrackTrack]]]:
        """
        Search for soundtrack data for a movie.

        Args:
            movie_title (str): Movie title
            year (int, optional): Release year
            imdb_id (str, optional): IMDB ID (if available)

        Returns:
            tuple: (SoundtrackMetadata, List[SoundtrackTrack]) or None if not found
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the source is available/configured.

        Returns:
            bool: True if source can be used
        """
        pass

    def get_priority(self) -> int:
        """
        Get source priority (lower is higher priority).

        Returns:
            int: Priority value (default: 100)
        """
        return 100

    def supports_imdb_lookup(self) -> bool:
        """
        Check if source supports looking up by IMDB ID.

        Returns:
            bool: True if IMDB ID lookup is supported
        """
        return False
