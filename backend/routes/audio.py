"""
Audio API Routes.

CRUD operations for audio content (albums, singles), artists, tracks, and genres.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
import logging

from backend.models.audio import (
    # Genre models
    AudioGenreCreate,
    AudioGenreUpdate,
    AudioGenreResponse,
    AudioGenreListResponse,
    # Artist models
    ArtistCreate,
    ArtistUpdate,
    ArtistResponse,
    ArtistListResponse,
    ArtistFilters,
    # Audio content models
    AudioContentCreate,
    AudioContentUpdate,
    AudioContentResponse,
    AudioContentListResponse,
    AudioContentFilters,
    # Track models
    AudioTrackCreate,
    AudioTrackUpdate,
    AudioTrackResponse,
    AudioTrackListResponse,
)
from backend.services.audio_service import get_audio_service

logger = logging.getLogger(__name__)

router = APIRouter()
audio_service = get_audio_service()


# ============================================================================
# AUDIO GENRE ENDPOINTS
# ============================================================================

@router.get("/genres", response_model=dict)
async def get_audio_genres(
    parent_genre_id: Optional[UUID] = Query(None, description="Filter by parent genre")
):
    """
    Get list of audio genres.

    Args:
        parent_genre_id: Optional parent genre UUID to filter sub-genres

    Returns:
        dict: Audio genres with success status
    """
    try:
        logger.info(f"Fetching audio genres - parent_id: {parent_genre_id}")

        genres = audio_service.list_audio_genres(
            parent_genre_id=str(parent_genre_id) if parent_genre_id else None
        )

        return {
            "success": True,
            "data": {
                "items": genres,
                "total": len(genres)
            }
        }

    except Exception as e:
        logger.error(f"Error fetching audio genres: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/genres", response_model=dict)
async def create_audio_genre(genre: AudioGenreCreate):
    """
    Create a new audio genre.

    Args:
        genre: Audio genre data

    Returns:
        dict: Created genre ID with success status
    """
    try:
        logger.info(f"Creating audio genre: {genre.name}")

        genre_data = genre.model_dump()
        genre_id = audio_service.create_audio_genre(genre_data)

        return {
            "success": True,
            "data": {
                "id": genre_id,
                "message": f"Audio genre '{genre.name}' created successfully"
            }
        }

    except Exception as e:
        logger.error(f"Error creating audio genre: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/genres/{genre_id}", response_model=dict)
async def get_audio_genre_by_id(genre_id: UUID):
    """
    Get audio genre by ID.

    Args:
        genre_id: Genre UUID

    Returns:
        dict: Genre details with success status

    Raises:
        HTTPException: If genre not found
    """
    try:
        logger.info(f"Fetching audio genre by ID: {genre_id}")

        genre = audio_service.get_audio_genre(str(genre_id))

        if not genre:
            raise HTTPException(status_code=404, detail="Audio genre not found")

        return {
            "success": True,
            "data": genre
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching audio genre: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/genres/{genre_id}", response_model=dict)
async def update_audio_genre(genre_id: UUID, updates: AudioGenreUpdate):
    """
    Update audio genre.

    Args:
        genre_id: Genre UUID
        updates: Fields to update

    Returns:
        dict: Update status

    Raises:
        HTTPException: If genre not found
    """
    try:
        logger.info(f"Updating audio genre: {genre_id}")

        update_data = updates.model_dump(exclude_unset=True)
        success = audio_service.update_audio_genre(str(genre_id), update_data)

        if not success:
            raise HTTPException(status_code=404, detail="Audio genre not found")

        return {
            "success": True,
            "data": {
                "message": "Audio genre updated successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating audio genre: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/genres/{genre_id}", response_model=dict)
async def delete_audio_genre(genre_id: UUID):
    """
    Delete audio genre.

    Args:
        genre_id: Genre UUID

    Returns:
        dict: Delete status

    Raises:
        HTTPException: If genre not found
    """
    try:
        logger.info(f"Deleting audio genre: {genre_id}")

        success = audio_service.delete_audio_genre(str(genre_id))

        if not success:
            raise HTTPException(status_code=404, detail="Audio genre not found")

        return {
            "success": True,
            "data": {
                "message": "Audio genre deleted successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting audio genre: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ARTIST ENDPOINTS
# ============================================================================

@router.get("/artists", response_model=dict)
async def get_artists(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    artist_type: Optional[str] = Query(None, description="Filter by artist type"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
):
    """
    Get paginated list of artists with optional filtering.

    Args:
        page: Page number
        page_size: Items per page
        artist_type: Filter by artist type
        country: Filter by country code
        sort_by: Sort field
        sort_order: Sort order

    Returns:
        dict: Paginated artist list with success status
    """
    try:
        logger.info(f"Fetching artists - page: {page}, filters applied")

        offset = (page - 1) * page_size

        result = audio_service.list_artists(
            limit=page_size,
            offset=offset,
            artist_type=artist_type,
            country=country,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return {
            "success": True,
            "data": {
                "items": result['items'],
                "total": result['total'],
                "page": page,
                "page_size": page_size
            }
        }

    except Exception as e:
        logger.error(f"Error fetching artists: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/artists", response_model=dict)
async def create_artist(artist: ArtistCreate):
    """
    Create a new artist.

    Args:
        artist: Artist data

    Returns:
        dict: Created artist ID with success status
    """
    try:
        logger.info(f"Creating artist: {artist.name}")

        artist_data = artist.model_dump()
        artist_id = audio_service.create_artist(artist_data)

        return {
            "success": True,
            "data": {
                "id": artist_id,
                "message": f"Artist '{artist.name}' created successfully"
            }
        }

    except Exception as e:
        logger.error(f"Error creating artist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/{artist_id}", response_model=dict)
async def get_artist_by_id(artist_id: UUID):
    """
    Get artist by ID.

    Args:
        artist_id: Artist UUID

    Returns:
        dict: Artist details with success status

    Raises:
        HTTPException: If artist not found
    """
    try:
        logger.info(f"Fetching artist by ID: {artist_id}")

        artist = audio_service.get_artist(str(artist_id))

        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")

        return {
            "success": True,
            "data": artist
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching artist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/artists/{artist_id}", response_model=dict)
async def update_artist(artist_id: UUID, updates: ArtistUpdate):
    """
    Update artist.

    Args:
        artist_id: Artist UUID
        updates: Fields to update

    Returns:
        dict: Update status

    Raises:
        HTTPException: If artist not found
    """
    try:
        logger.info(f"Updating artist: {artist_id}")

        update_data = updates.model_dump(exclude_unset=True)
        success = audio_service.update_artist(str(artist_id), update_data)

        if not success:
            raise HTTPException(status_code=404, detail="Artist not found")

        return {
            "success": True,
            "data": {
                "message": "Artist updated successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating artist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/artists/{artist_id}", response_model=dict)
async def delete_artist(artist_id: UUID):
    """
    Delete artist.

    Args:
        artist_id: Artist UUID

    Returns:
        dict: Delete status

    Raises:
        HTTPException: If artist not found
    """
    try:
        logger.info(f"Deleting artist: {artist_id}")

        success = audio_service.delete_artist(str(artist_id))

        if not success:
            raise HTTPException(status_code=404, detail="Artist not found")

        return {
            "success": True,
            "data": {
                "message": "Artist deleted successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting artist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AUDIO CONTENT ENDPOINTS (Albums, Singles, EPs)
# ============================================================================

@router.get("/albums", response_model=dict)
async def get_audio_content(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    artist_id: Optional[UUID] = Query(None, description="Filter by artist"),
    genre_id: Optional[UUID] = Query(None, description="Filter by genre"),
    year_from: Optional[int] = Query(None, ge=1900, le=2100, description="From year"),
    year_to: Optional[int] = Query(None, ge=1900, le=2100, description="To year"),
    sort_by: str = Query("title", description="Sort field"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
):
    """
    Get paginated list of audio content with optional filtering.

    Args:
        page: Page number
        page_size: Items per page
        content_type: Filter by content type
        artist_id: Filter by artist
        genre_id: Filter by genre
        year_from: Filter by release year (from)
        year_to: Filter by release year (to)
        sort_by: Sort field
        sort_order: Sort order

    Returns:
        dict: Paginated audio content list with success status
    """
    try:
        logger.info(f"Fetching audio content - page: {page}, filters applied")

        offset = (page - 1) * page_size

        result = audio_service.list_audio_content(
            limit=page_size,
            offset=offset,
            content_type=content_type,
            artist_id=str(artist_id) if artist_id else None,
            genre_id=str(genre_id) if genre_id else None,
            year_from=year_from,
            year_to=year_to,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return {
            "success": True,
            "data": {
                "items": result['items'],
                "total": result['total'],
                "page": page,
                "page_size": page_size
            }
        }

    except Exception as e:
        logger.error(f"Error fetching audio content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/albums", response_model=dict)
async def create_audio_content(content: AudioContentCreate):
    """
    Create audio content (album, single, EP, etc.).

    Args:
        content: Audio content data

    Returns:
        dict: Created content ID with success status
    """
    try:
        logger.info(f"Creating audio content: {content.title}")

        content_data = content.model_dump()
        content_id = audio_service.create_audio_content(content_data)

        return {
            "success": True,
            "data": {
                "id": content_id,
                "message": f"Audio content '{content.title}' created successfully"
            }
        }

    except Exception as e:
        logger.error(f"Error creating audio content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/albums/{content_id}", response_model=dict)
async def get_audio_content_by_id(content_id: UUID):
    """
    Get audio content by ID.

    Args:
        content_id: Audio content UUID

    Returns:
        dict: Audio content details with success status

    Raises:
        HTTPException: If content not found
    """
    try:
        logger.info(f"Fetching audio content by ID: {content_id}")

        content = audio_service.get_audio_content(str(content_id))

        if not content:
            raise HTTPException(status_code=404, detail="Audio content not found")

        return {
            "success": True,
            "data": content
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching audio content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/albums/{content_id}", response_model=dict)
async def update_audio_content(content_id: UUID, updates: AudioContentUpdate):
    """
    Update audio content.

    Args:
        content_id: Audio content UUID
        updates: Fields to update

    Returns:
        dict: Update status

    Raises:
        HTTPException: If content not found
    """
    try:
        logger.info(f"Updating audio content: {content_id}")

        update_data = updates.model_dump(exclude_unset=True)
        success = audio_service.update_audio_content(str(content_id), update_data)

        if not success:
            raise HTTPException(status_code=404, detail="Audio content not found")

        return {
            "success": True,
            "data": {
                "message": "Audio content updated successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating audio content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/albums/{content_id}", response_model=dict)
async def delete_audio_content(content_id: UUID):
    """
    Delete audio content.

    Args:
        content_id: Audio content UUID

    Returns:
        dict: Delete status

    Raises:
        HTTPException: If content not found
    """
    try:
        logger.info(f"Deleting audio content: {content_id}")

        success = audio_service.delete_audio_content(str(content_id))

        if not success:
            raise HTTPException(status_code=404, detail="Audio content not found")

        return {
            "success": True,
            "data": {
                "message": "Audio content deleted successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting audio content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AUDIO TRACK ENDPOINTS
# ============================================================================

@router.get("/albums/{content_id}/tracks", response_model=dict)
async def get_tracks_by_content(content_id: UUID):
    """
    Get tracks for an audio content (album/single).

    Args:
        content_id: Audio content UUID

    Returns:
        dict: List of tracks with success status
    """
    try:
        logger.info(f"Fetching tracks for content: {content_id}")

        tracks = audio_service.list_tracks_by_content(str(content_id))

        return {
            "success": True,
            "data": {
                "items": tracks,
                "total": len(tracks)
            }
        }

    except Exception as e:
        logger.error(f"Error fetching tracks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tracks", response_model=dict)
async def create_track(track: AudioTrackCreate):
    """
    Create audio track.

    Args:
        track: Track data

    Returns:
        dict: Created track ID with success status
    """
    try:
        logger.info(f"Creating track: {track.title}")

        track_data = track.model_dump()
        track_id = audio_service.create_audio_track(track_data)

        return {
            "success": True,
            "data": {
                "id": track_id,
                "message": f"Track '{track.title}' created successfully"
            }
        }

    except Exception as e:
        logger.error(f"Error creating track: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracks/{track_id}", response_model=dict)
async def get_track_by_id(track_id: UUID):
    """
    Get track by ID.

    Args:
        track_id: Track UUID

    Returns:
        dict: Track details with success status

    Raises:
        HTTPException: If track not found
    """
    try:
        logger.info(f"Fetching track by ID: {track_id}")

        track = audio_service.get_audio_track(str(track_id))

        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        return {
            "success": True,
            "data": track
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching track: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tracks/{track_id}", response_model=dict)
async def update_track(track_id: UUID, updates: AudioTrackUpdate):
    """
    Update track.

    Args:
        track_id: Track UUID
        updates: Fields to update

    Returns:
        dict: Update status

    Raises:
        HTTPException: If track not found
    """
    try:
        logger.info(f"Updating track: {track_id}")

        update_data = updates.model_dump(exclude_unset=True)
        success = audio_service.update_audio_track(str(track_id), update_data)

        if not success:
            raise HTTPException(status_code=404, detail="Track not found")

        return {
            "success": True,
            "data": {
                "message": "Track updated successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating track: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tracks/{track_id}", response_model=dict)
async def delete_track(track_id: UUID):
    """
    Delete track.

    Args:
        track_id: Track UUID

    Returns:
        dict: Delete status

    Raises:
        HTTPException: If track not found
    """
    try:
        logger.info(f"Deleting track: {track_id}")

        success = audio_service.delete_audio_track(str(track_id))

        if not success:
            raise HTTPException(status_code=404, detail="Track not found")

        return {
            "success": True,
            "data": {
                "message": "Track deleted successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting track: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
