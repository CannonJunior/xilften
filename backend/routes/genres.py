"""
Genre API Routes.

CRUD operations for genre taxonomy.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from uuid import UUID
import logging

from backend.models.genre import (
    GenreCreate,
    GenreUpdate,
    GenreResponse,
    GenreListResponse,
    GenreFilters,
)
from backend.services.genre_service import get_genre_service

logger = logging.getLogger(__name__)

# Get genre service instance
genre_service = get_genre_service()

router = APIRouter()


@router.get("", response_model=dict)
async def get_genres(
    category: Optional[str] = Query(None, description="Filter by genre category"),
    include_inactive: bool = Query(False, description="Include inactive genres"),
    parent_only: bool = Query(False, description="Only return parent genres"),
):
    """
    Get list of genres with optional filtering.

    Args:
        category: Filter by genre category
        include_inactive: Include inactive genres
        parent_only: Only return parent genres

    Returns:
        dict: Genre list with success status
    """
    try:
        logger.info(f"Fetching genres - category: {category}")

        genres = genre_service.get_all_genres(
            category=category,
            include_inactive=include_inactive,
            parent_only=parent_only
        )

        return {
            "success": True,
            "data": genres,
        }

    except Exception as e:
        logger.error(f"Error fetching genres: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{genre_id}", response_model=dict)
async def get_genre_by_id(genre_id: UUID):
    """
    Get genre details by ID.

    Args:
        genre_id: Genre UUID

    Returns:
        dict: Genre details with success status

    Raises:
        HTTPException: If genre not found
    """
    try:
        logger.info(f"Fetching genre by ID: {genre_id}")

        genre = genre_service.get_genre_by_id(genre_id)

        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")

        return {
            "success": True,
            "data": genre,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching genre: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict, status_code=201)
async def create_genre(genre_data: GenreCreate):
    """
    Create new genre.

    Args:
        genre_data: Genre creation data

    Returns:
        dict: Created genre with success status
    """
    try:
        logger.info(f"Creating new genre: {genre_data.name}")

        genre = genre_service.create_genre(genre_data)

        return {
            "success": True,
            "data": genre,
            "message": "Genre created successfully",
        }

    except Exception as e:
        logger.error(f"Error creating genre: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{genre_id}", response_model=dict)
async def update_genre(genre_id: UUID, updates: GenreUpdate):
    """
    Update existing genre.

    Args:
        genre_id: Genre UUID
        updates: Fields to update

    Returns:
        dict: Updated genre with success status

    Raises:
        HTTPException: If genre not found
    """
    try:
        logger.info(f"Updating genre: {genre_id}")

        genre = genre_service.update_genre(genre_id, updates)

        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")

        return {
            "success": True,
            "data": genre,
            "message": "Genre updated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating genre: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{genre_id}", response_model=dict)
async def delete_genre(genre_id: UUID):
    """
    Delete genre.

    Args:
        genre_id: Genre UUID

    Returns:
        dict: Deletion confirmation with success status

    Raises:
        HTTPException: If genre not found
    """
    try:
        logger.info(f"Deleting genre: {genre_id}")

        deleted = genre_service.delete_genre(genre_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Genre not found")

        return {
            "success": True,
            "message": "Genre deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting genre: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
