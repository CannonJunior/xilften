"""
User Review Models.

Pydantic models for user reviews and ratings.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime


class ReviewCreate(BaseModel):
    """Create new user review."""
    media_id: UUID = Field(..., description="Media UUID")
    rating: float = Field(..., ge=0.0, le=10.0, description="User rating (0-10)")
    review_text: Optional[str] = Field(None, description="Review text")
    watched_date: Optional[date] = Field(None, description="Date when media was watched")
    rewatch_count: int = Field(0, ge=0, description="Number of times rewatched")
    tags: Optional[List[str]] = Field(None, description="Emotional response tags")


class ReviewUpdate(BaseModel):
    """Update existing review."""
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    review_text: Optional[str] = None
    watched_date: Optional[date] = None
    rewatch_count: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None


class ReviewResponse(BaseModel):
    """Review response."""
    id: UUID
    media_id: UUID
    rating: float
    review_text: Optional[str]
    watched_date: Optional[date]
    rewatch_count: int
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


class ReviewWithMedia(BaseModel):
    """Review response with media details."""
    id: UUID
    media_id: UUID
    media_title: str
    media_type: str
    rating: float
    review_text: Optional[str]
    watched_date: Optional[date]
    rewatch_count: int
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


class ReviewsQuery(BaseModel):
    """Query parameters for reviews."""
    media_id: Optional[UUID] = Field(None, description="Filter by media ID")
    min_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Minimum rating")
    max_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Maximum rating")
    start_date: Optional[date] = Field(None, description="Filter reviews after this date")
    end_date: Optional[date] = Field(None, description="Filter reviews before this date")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: int = Field(50, ge=1, le=200, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class ReviewStats(BaseModel):
    """Review statistics."""
    total_reviews: int
    average_rating: Optional[float]
    rating_distribution: Dict[str, int]  # e.g., {"0-2": 5, "2-4": 10, ...}
    most_common_tags: List[tuple[str, int]]  # [(tag, count), ...]
    total_rewatches: int
