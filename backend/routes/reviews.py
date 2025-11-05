"""
Reviews API Routes.

Endpoints for user reviews and ratings.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from uuid import UUID
from datetime import date
import logging

from backend.models.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewStats,
)
from backend.services.review_service import review_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== Review Endpoints ==========

@router.get("/", response_model=List[ReviewResponse])
async def list_reviews(
    media_id: Optional[UUID] = Query(None, description="Filter by media ID"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0, description="Minimum rating"),
    max_rating: Optional[float] = Query(None, ge=0.0, le=10.0, description="Maximum rating"),
    start_date: Optional[date] = Query(None, description="Filter reviews after this date"),
    end_date: Optional[date] = Query(None, description="Filter reviews before this date"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get all reviews with optional filters.

    Returns:
        List[ReviewResponse]: List of reviews
    """
    try:
        reviews, total = review_service.get_all_reviews(
            media_id=media_id,
            min_rating=min_rating,
            max_rating=max_rating,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        return reviews

    except Exception as e:
        logger.error(f"Error listing reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list reviews: {str(e)}")


# ========== Review Statistics (must be before /{review_id}) ==========

@router.get("/stats", response_model=ReviewStats)
async def get_review_stats(
    media_id: Optional[UUID] = Query(None, description="Filter stats by media ID")
):
    """
    Get review statistics.

    Args:
        media_id: Optional media ID to filter by

    Returns:
        ReviewStats: Review statistics
    """
    try:
        stats = review_service.get_review_stats(media_id=media_id)
        return stats
    except Exception as e:
        logger.error(f"Error fetching review stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch review stats: {str(e)}")


@router.get("/media/{media_id}/reviews", response_model=List[ReviewResponse])
async def get_media_reviews(media_id: UUID):
    """
    Get all reviews for a specific media item.

    Args:
        media_id: Media UUID

    Returns:
        List[ReviewResponse]: Reviews for the media
    """
    try:
        reviews = review_service.get_media_reviews(media_id)
        return reviews
    except Exception as e:
        logger.error(f"Error fetching media reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch media reviews: {str(e)}")


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: UUID):
    """
    Get specific review by ID.

    Args:
        review_id: Review UUID

    Returns:
        ReviewResponse: Review details

    Raises:
        HTTPException: If review not found
    """
    try:
        review = review_service.get_review_by_id(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching review {review_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch review: {str(e)}")


@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(review_data: ReviewCreate):
    """
    Create new review.

    Args:
        review_data: Review creation data

    Returns:
        ReviewResponse: Created review

    Raises:
        HTTPException: If creation fails
    """
    try:
        review = review_service.create_review(review_data)
        return review
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: UUID, updates: ReviewUpdate):
    """
    Update existing review.

    Args:
        review_id: Review UUID
        updates: Fields to update

    Returns:
        ReviewResponse: Updated review

    Raises:
        HTTPException: If review not found
    """
    try:
        review = review_service.update_review(review_id, updates)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review {review_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update review: {str(e)}")


@router.delete("/{review_id}", status_code=204)
async def delete_review(review_id: UUID):
    """
    Delete review.

    Args:
        review_id: Review UUID

    Raises:
        HTTPException: If review not found
    """
    try:
        deleted = review_service.delete_review(review_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Review not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review {review_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete review: {str(e)}")
