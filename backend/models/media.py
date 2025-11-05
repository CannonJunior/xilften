"""
Media Pydantic models for data validation.

Models for movies, TV shows, anime, and documentaries.
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator


class MediaBase(BaseModel):
    """
    Base media model with common fields.
    """

    title: str = Field(..., min_length=1, max_length=500, description="Media title")
    original_title: Optional[str] = Field(None, max_length=500, description="Original title")
    media_type: str = Field(
        ..., description="Media type: movie, tv, anime, documentary"
    )
    release_date: Optional[date] = Field(None, description="Release date")
    runtime: Optional[int] = Field(None, ge=0, description="Runtime in minutes")
    overview: Optional[str] = Field(None, description="Overview/description")
    tagline: Optional[str] = Field(None, max_length=500, description="Tagline")

    tmdb_rating: Optional[float] = Field(
        None, ge=0.0, le=10.0, description="TMDB rating (0-10)"
    )
    tmdb_vote_count: Optional[int] = Field(None, ge=0, description="TMDB vote count")
    user_rating: Optional[float] = Field(
        None, ge=0.0, le=10.0, description="User's personal rating"
    )
    popularity_score: Optional[float] = Field(None, ge=0, description="Popularity score")

    maturity_rating: Optional[str] = Field(None, max_length=20, description="Maturity rating")
    recommended_age_min: Optional[int] = Field(None, ge=0, le=100)
    recommended_age_max: Optional[int] = Field(None, ge=0, le=100)

    original_language: Optional[str] = Field(None, max_length=10, description="Language code")
    production_countries: Optional[List[str]] = Field(default_factory=list)
    spoken_languages: Optional[List[str]] = Field(default_factory=list)

    poster_path: Optional[str] = Field(None, max_length=500, description="Poster image path")
    backdrop_path: Optional[str] = Field(None, max_length=500, description="Backdrop image path")
    trailer_url: Optional[str] = Field(None, max_length=500, description="Trailer URL")

    status: Optional[str] = Field(
        None, max_length=50, description="Status: Released, In Production, etc."
    )

    custom_fields: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Custom user-defined fields"
    )

    @validator("media_type")
    def validate_media_type(cls, v):
        """
        Validate media type.

        Args:
            v (str): Media type

        Returns:
            str: Validated media type

        Raises:
            ValueError: If media type is invalid
        """
        allowed_types = ["movie", "tv", "anime", "documentary"]
        if v.lower() not in allowed_types:
            raise ValueError(f"Media type must be one of: {', '.join(allowed_types)}")
        return v.lower()

    @validator("maturity_rating")
    def validate_maturity_rating(cls, v):
        """
        Validate maturity rating.

        Args:
            v (str): Maturity rating

        Returns:
            str: Validated maturity rating
        """
        if v is None:
            return v

        allowed_ratings = [
            "G",
            "PG",
            "PG-13",
            "R",
            "NC-17",
            "TV-Y",
            "TV-Y7",
            "TV-G",
            "TV-PG",
            "TV-14",
            "TV-MA",
        ]
        if v.upper() not in allowed_ratings:
            return v  # Allow custom ratings
        return v.upper()


class MediaCreate(MediaBase):
    """
    Model for creating new media.
    """

    tmdb_id: Optional[int] = Field(None, description="TMDB ID if fetching from TMDB")
    imdb_id: Optional[str] = Field(None, max_length=20, description="IMDB ID")


class MediaUpdate(BaseModel):
    """
    Model for updating existing media.
    All fields are optional.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    original_title: Optional[str] = Field(None, max_length=500)
    release_date: Optional[date] = None
    runtime: Optional[int] = Field(None, ge=0)
    overview: Optional[str] = None
    tagline: Optional[str] = Field(None, max_length=500)

    tmdb_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    user_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    popularity_score: Optional[float] = Field(None, ge=0)

    maturity_rating: Optional[str] = Field(None, max_length=20)
    recommended_age_min: Optional[int] = Field(None, ge=0, le=100)
    recommended_age_max: Optional[int] = Field(None, ge=0, le=100)

    poster_path: Optional[str] = Field(None, max_length=500)
    backdrop_path: Optional[str] = Field(None, max_length=500)
    trailer_url: Optional[str] = Field(None, max_length=500)

    status: Optional[str] = Field(None, max_length=50)
    custom_fields: Optional[Dict[str, Any]] = None


class MediaResponse(MediaBase):
    """
    Model for media response (includes database fields).
    """

    id: UUID = Field(..., description="Media UUID")
    tmdb_id: Optional[int] = Field(None, description="TMDB ID")
    imdb_id: Optional[str] = Field(None, max_length=20, description="IMDB ID")

    genres: Optional[List[Dict[str, str]]] = Field(
        default_factory=list, description="List of genres"
    )
    cast: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Cast members"
    )
    crew: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Crew members"
    )

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_synced_tmdb: Optional[datetime] = Field(None, description="Last TMDB sync")

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    """
    Model for paginated media list response.
    """

    items: List[MediaResponse] = Field(..., description="List of media items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")


class MediaFilters(BaseModel):
    """
    Model for media filtering parameters.
    """

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    media_type: Optional[str] = Field(None, description="Filter by media type")
    genre: Optional[str] = Field(None, description="Filter by genre slug")
    min_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Minimum rating")
    max_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Maximum rating")
    year_from: Optional[int] = Field(None, ge=1900, le=2100, description="From year")
    year_to: Optional[int] = Field(None, ge=1900, le=2100, description="To year")
    maturity_rating: Optional[str] = Field(None, description="Maturity rating filter")

    sort_by: str = Field(
        default="title",
        description="Sort field: title, release_date, rating, popularity",
    )
    sort_order: str = Field(default="asc", description="Sort order: asc or desc")
    search: Optional[str] = Field(None, description="Search query")

    @validator("sort_by")
    def validate_sort_by(cls, v):
        """Validate sort_by field."""
        allowed_fields = ["title", "release_date", "rating", "popularity", "created_at"]
        if v not in allowed_fields:
            raise ValueError(f"sort_by must be one of: {', '.join(allowed_fields)}")
        return v

    @validator("sort_order")
    def validate_sort_order(cls, v):
        """Validate sort_order field."""
        if v.lower() not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v.lower()


class TMDBFetchRequest(BaseModel):
    """
    Model for fetching media from TMDB.
    """

    tmdb_id: int = Field(..., ge=1, description="TMDB ID")
    media_type: str = Field(..., description="Media type: movie or tv")

    @validator("media_type")
    def validate_media_type(cls, v):
        """Validate media type for TMDB fetch."""
        if v.lower() not in ["movie", "tv"]:
            raise ValueError("media_type must be 'movie' or 'tv' for TMDB fetch")
        return v.lower()
