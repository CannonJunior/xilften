"""Pydantic models package."""

from .media import (
    MediaBase,
    MediaCreate,
    MediaUpdate,
    MediaResponse,
    MediaListResponse,
    MediaFilters,
    TMDBFetchRequest,
)
from .genre import (
    GenreBase,
    GenreCreate,
    GenreUpdate,
    GenreResponse,
    GenreListResponse,
    GenreFilters,
)

__all__ = [
    # Media models
    "MediaBase",
    "MediaCreate",
    "MediaUpdate",
    "MediaResponse",
    "MediaListResponse",
    "MediaFilters",
    "TMDBFetchRequest",
    # Genre models
    "GenreBase",
    "GenreCreate",
    "GenreUpdate",
    "GenreResponse",
    "GenreListResponse",
    "GenreFilters",
]
