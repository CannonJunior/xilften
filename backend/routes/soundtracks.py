"""
Soundtrack API Routes.

Provides endpoints for searching, retrieving, and managing movie soundtracks.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.soundtrack_service import soundtrack_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/soundtracks", tags=["soundtracks"])


# Request/Response Models
class SoundtrackSearchRequest(BaseModel):
    """Request model for soundtrack search."""

    media_id: str = Field(..., description="Media ID from database")
    movie_title: str = Field(..., description="Movie title to search for")
    year: Optional[int] = Field(None, description="Release year (optional)")


class TrackResponse(BaseModel):
    """Response model for a soundtrack track."""

    id: str
    track_number: int
    disc_number: int
    title: str
    artist: Optional[str] = None
    duration_ms: Optional[int] = None
    spotify_track_id: Optional[str] = None
    preview_url: Optional[str] = None
    spotify_uri: Optional[str] = None


class SoundtrackResponse(BaseModel):
    """Response model for soundtrack details."""

    id: str
    media_id: str
    title: str
    release_date: Optional[str] = None
    label: Optional[str] = None
    musicbrainz_id: Optional[str] = None
    spotify_album_id: Optional[str] = None
    album_art_url: Optional[str] = None
    total_tracks: Optional[int] = None
    album_type: Optional[str] = None
    created_at: str
    tracks: List[TrackResponse] = []


class SoundtrackSearchResponse(BaseModel):
    """Response model for soundtrack search operation."""

    success: bool
    soundtrack_id: Optional[str] = None
    message: str


# Endpoints
@router.get("/{media_id}", response_model=List[SoundtrackResponse])
async def get_soundtracks_for_media(media_id: str):
    """
    Get all soundtracks for a specific media item.

    Args:
        media_id (str): Media ID

    Returns:
        List[SoundtrackResponse]: List of soundtracks with tracks
    """
    try:
        logger.info(f"🎵 Fetching soundtracks for media: {media_id}")

        # Get soundtrack IDs for this media
        soundtrack_ids = soundtrack_service.get_soundtrack_by_media_id(media_id)

        if not soundtrack_ids:
            logger.info(f"ℹ️  No soundtracks found for media {media_id}")
            return []

        # Get full soundtrack details for each ID
        soundtracks = []
        for soundtrack_id in soundtrack_ids:
            soundtrack_data = soundtrack_service.get_soundtrack_with_tracks(soundtrack_id)
            if soundtrack_data:
                soundtracks.append(soundtrack_data)

        logger.info(f"✅ Found {len(soundtracks)} soundtrack(s) for media {media_id}")
        return soundtracks

    except Exception as e:
        logger.error(f"❌ Error fetching soundtracks for media {media_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch soundtracks: {str(e)}")


@router.get("/details/{soundtrack_id}", response_model=SoundtrackResponse)
async def get_soundtrack_details(soundtrack_id: str):
    """
    Get detailed information about a specific soundtrack.

    Args:
        soundtrack_id (str): Soundtrack ID

    Returns:
        SoundtrackResponse: Soundtrack details with full track listing
    """
    try:
        logger.info(f"🎵 Fetching soundtrack details: {soundtrack_id}")

        soundtrack_data = soundtrack_service.get_soundtrack_with_tracks(soundtrack_id)

        if not soundtrack_data:
            logger.warning(f"⚠️  Soundtrack not found: {soundtrack_id}")
            raise HTTPException(status_code=404, detail="Soundtrack not found")

        logger.info(f"✅ Retrieved soundtrack: {soundtrack_data.get('title')}")
        return soundtrack_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching soundtrack {soundtrack_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch soundtrack: {str(e)}")


@router.post("/search", response_model=SoundtrackSearchResponse)
async def search_and_save_soundtrack(request: SoundtrackSearchRequest):
    """
    Search for and save a movie soundtrack.

    This endpoint triggers a search across MusicBrainz and Spotify
    to find soundtrack data for the specified movie.

    Args:
        request (SoundtrackSearchRequest): Search request with media_id, movie_title, and optional year

    Returns:
        SoundtrackSearchResponse: Search result with soundtrack_id if successful
    """
    try:
        logger.info(f"🎵 Searching soundtrack for: {request.movie_title} ({request.year})")

        # Perform search and save
        soundtrack_id = await soundtrack_service.search_and_save_soundtrack(
            media_id=request.media_id,
            movie_title=request.movie_title,
            year=request.year
        )

        if soundtrack_id:
            logger.info(f"✅ Successfully saved soundtrack: {soundtrack_id}")
            return SoundtrackSearchResponse(
                success=True,
                soundtrack_id=soundtrack_id,
                message=f"Successfully found and saved soundtrack for '{request.movie_title}'"
            )
        else:
            logger.warning(f"⚠️  No soundtrack found for: {request.movie_title}")
            return SoundtrackSearchResponse(
                success=False,
                soundtrack_id=None,
                message=f"No soundtrack found for '{request.movie_title}'"
            )

    except Exception as e:
        logger.error(f"❌ Error searching soundtrack for {request.movie_title}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search soundtrack: {str(e)}"
        )


@router.delete("/{soundtrack_id}")
async def delete_soundtrack(soundtrack_id: str):
    """
    Delete a soundtrack and all associated tracks.

    Args:
        soundtrack_id (str): Soundtrack ID to delete

    Returns:
        dict: Success message
    """
    try:
        logger.info(f"🗑️  Deleting soundtrack: {soundtrack_id}")

        from config.database import db_manager
        conn = db_manager.get_duckdb_connection()

        # Check if soundtrack exists
        check_query = "SELECT COUNT(*) FROM soundtracks WHERE id = ?"
        result = conn.execute(check_query, [soundtrack_id]).fetchone()

        if result[0] == 0:
            raise HTTPException(status_code=404, detail="Soundtrack not found")

        # Delete soundtrack (cascade will delete tracks)
        delete_query = "DELETE FROM soundtracks WHERE id = ?"
        conn.execute(delete_query, [soundtrack_id])

        logger.info(f"✅ Deleted soundtrack: {soundtrack_id}")
        return {"success": True, "message": f"Soundtrack {soundtrack_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting soundtrack {soundtrack_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete soundtrack: {str(e)}")


@router.get("/stats/count")
async def get_soundtrack_count():
    """
    Get the total count of soundtracks in the database.

    Returns:
        dict: JSON object with 'count' field containing the total number of soundtracks
    """
    try:
        logger.info("📊 Fetching soundtrack count")

        from config.database import db_manager
        conn = db_manager.get_duckdb_connection()

        # Count total soundtracks
        count_query = "SELECT COUNT(*) FROM soundtracks"
        result = conn.execute(count_query).fetchone()

        count = result[0] if result else 0

        logger.info(f"✅ Total soundtracks: {count}")
        return {"count": count}

    except Exception as e:
        logger.error(f"❌ Error fetching soundtrack count: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch soundtrack count: {str(e)}")
