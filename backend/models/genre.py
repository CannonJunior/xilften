"""
Genre Pydantic models for data validation.

Models for genre taxonomy and hierarchical structure.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class GenreBase(BaseModel):
    """
    Base genre model with common fields.
    """

    name: str = Field(..., min_length=1, max_length=100, description="Genre name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")
    genre_category: Optional[str] = Field(
        None,
        max_length=100,
        description="Genre category: film-noir, sci-fi, documentary, etc.",
    )
    description: Optional[str] = Field(None, description="Genre description")
    is_active: bool = Field(default=True, description="Is genre active")


class GenreCreate(GenreBase):
    """
    Model for creating new genre.
    """

    tmdb_genre_id: Optional[int] = Field(None, description="TMDB genre ID")
    parent_genre_id: Optional[UUID] = Field(None, description="Parent genre UUID for sub-genres")


class GenreUpdate(BaseModel):
    """
    Model for updating existing genre.
    All fields are optional.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class GenreResponse(GenreBase):
    """
    Model for genre response (includes database fields).
    """

    id: UUID = Field(..., description="Genre UUID")
    tmdb_genre_id: Optional[int] = Field(None, description="TMDB genre ID")
    parent_genre_id: Optional[UUID] = Field(None, description="Parent genre UUID")
    sub_genres: Optional[List["GenreResponse"]] = Field(
        default_factory=list, description="Sub-genres (children)"
    )
    media_count: Optional[int] = Field(None, ge=0, description="Number of media with this genre")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# Update forward references
GenreResponse.model_rebuild()


class GenreListResponse(BaseModel):
    """
    Model for genre list response.
    """

    items: List[GenreResponse] = Field(..., description="List of genres")
    total: int = Field(..., ge=0, description="Total number of genres")


class GenreFilters(BaseModel):
    """
    Model for genre filtering parameters.
    """

    category: Optional[str] = Field(None, description="Filter by genre category")
    include_inactive: bool = Field(default=False, description="Include inactive genres")
    parent_only: bool = Field(default=False, description="Only return parent genres (no sub-genres)")
