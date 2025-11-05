"""
Media API Routes.

CRUD operations and search for media content.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
import logging

from backend.models.media import (
    MediaCreate,
    MediaUpdate,
    MediaResponse,
    MediaListResponse,
    MediaFilters,
    TMDBFetchRequest,
)
from backend.services.tmdb_client import tmdb_client
from backend.services.media_service import media_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=dict)
async def get_media_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    media_type: Optional[str] = Query(None, description="Filter by media type"),
    genre: Optional[str] = Query(None, description="Filter by genre slug"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0),
    max_rating: Optional[float] = Query(None, ge=0.0, le=10.0),
    year_from: Optional[int] = Query(None, ge=1900, le=2100),
    year_to: Optional[int] = Query(None, ge=1900, le=2100),
    maturity_rating: Optional[str] = Query(None),
    sort_by: str = Query("title", description="Sort field"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    search: Optional[str] = Query(None, description="Search query"),
):
    """
    Get paginated list of media with optional filtering.

    Args:
        page: Page number
        page_size: Items per page
        media_type: Filter by type
        genre: Filter by genre
        min_rating: Minimum rating
        max_rating: Maximum rating
        year_from: From year
        year_to: To year
        maturity_rating: Maturity rating filter
        sort_by: Sort field
        sort_order: Sort order
        search: Search query

    Returns:
        dict: Paginated media list with success status
    """
    try:
        logger.info(f"Fetching media list - page: {page}, filters applied")

        # Build filters
        filters = MediaFilters(
            media_type=media_type,
            genre=genre,
            min_rating=min_rating,
            max_rating=max_rating,
            year_from=year_from,
            year_to=year_to,
            maturity_rating=maturity_rating,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Get media from database
        result = media_service.get_all_media(page=page, page_size=page_size, filters=filters)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Error fetching media list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=dict)
async def search_media(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Search media by title and overview.

    Args:
        q: Search query
        page: Page number
        page_size: Items per page

    Returns:
        dict: Search results with success status
    """
    try:
        logger.info(f"Searching media: {q}")

        result = media_service.search_media(query=q, page=page, page_size=page_size)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Error searching media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{media_id}", response_model=dict)
async def get_media_by_id(media_id: UUID):
    """
    Get media details by ID.

    Args:
        media_id: Media UUID

    Returns:
        dict: Media details with success status

    Raises:
        HTTPException: If media not found
    """
    try:
        logger.info(f"Fetching media by ID: {media_id}")

        media = media_service.get_media_by_id(media_id)

        if not media:
            raise HTTPException(status_code=404, detail="Media not found")

        return {
            "success": True,
            "data": media,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict, status_code=201)
async def create_media(media_data: MediaCreate):
    """
    Create new media entry.

    Args:
        media_data: Media creation data

    Returns:
        dict: Created media with success status
    """
    try:
        logger.info(f"Creating new media: {media_data.title}")

        media = media_service.create_media(media_data)

        return {
            "success": True,
            "data": media,
            "message": "Media created successfully",
        }

    except Exception as e:
        logger.error(f"Error creating media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{media_id}", response_model=dict)
async def update_media(media_id: UUID, updates: MediaUpdate):
    """
    Update existing media.

    Args:
        media_id: Media UUID
        updates: Fields to update

    Returns:
        dict: Updated media with success status

    Raises:
        HTTPException: If media not found
    """
    try:
        logger.info(f"Updating media: {media_id}")

        media = media_service.update_media(media_id, updates)

        if not media:
            raise HTTPException(status_code=404, detail="Media not found")

        return {
            "success": True,
            "data": media,
            "message": "Media updated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{media_id}", response_model=dict)
async def delete_media(media_id: UUID):
    """
    Delete media entry.

    Args:
        media_id: Media UUID

    Returns:
        dict: Deletion confirmation with success status

    Raises:
        HTTPException: If media not found
    """
    try:
        logger.info(f"Deleting media: {media_id}")

        deleted = media_service.delete_media(media_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Media not found")

        return {
            "success": True,
            "message": "Media deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-tmdb", response_model=dict)
async def fetch_from_tmdb(request: TMDBFetchRequest):
    """
    Fetch media metadata from TMDB and create/update local entry.

    Args:
        request: TMDB fetch request with ID and type

    Returns:
        dict: Fetched/updated media with success status

    Raises:
        HTTPException: If TMDB fetch fails
    """
    try:
        logger.info(f"Fetching from TMDB: {request.media_type} ID {request.tmdb_id}")

        # Fetch from TMDB
        if request.media_type == "movie":
            tmdb_data = await tmdb_client.get_movie(request.tmdb_id)
            media_data_dict = tmdb_client.transform_movie_to_media(tmdb_data)
        elif request.media_type == "tv":
            tmdb_data = await tmdb_client.get_tv_show(request.tmdb_id)
            media_data_dict = tmdb_client.transform_tv_to_media(tmdb_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid media_type")

        logger.info(f"Successfully fetched: {media_data_dict['title']}")

        # Extract genres for later association
        genres_list = media_data_dict.pop("genres", [])

        # Check if media already exists with this TMDB ID
        conn = media_service.db.get_duckdb_connection()
        existing = conn.execute(
            "SELECT id FROM media WHERE tmdb_id = ?",
            [media_data_dict["tmdb_id"]]
        ).fetchone()

        if existing:
            # Update existing media
            media_id = UUID(str(existing[0]))
            media_data = MediaUpdate(**media_data_dict)
            updated_media = media_service.update_media(media_id, media_data)

            logger.info(f"Updated existing media: {media_id}")
            message = f"Media '{updated_media['title']}' updated from TMDB"
            result_media = updated_media
        else:
            # Create new media entry
            media_data = MediaCreate(**media_data_dict)
            created_media = media_service.create_media(media_data)

            logger.info(f"Created new media: {created_media['id']}")
            message = f"Media '{created_media['title']}' created from TMDB"
            result_media = created_media

        # TODO: Map TMDB genres to our genre taxonomy and create associations
        # This will be implemented when we add genre mapping functionality

        return {
            "success": True,
            "data": result_media,
            "message": message,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching from TMDB: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch from TMDB: {str(e)}")
