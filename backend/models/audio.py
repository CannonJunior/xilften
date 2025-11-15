"""
Audio Pydantic models for data validation.

Models for audio content (albums, singles), artists, tracks, and genres.
"""

from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


# ============================================================
# AUDIO GENRE MODELS
# ============================================================

class AudioGenreBase(BaseModel):
    """
    Base audio genre model with common fields.
    """

    name: str = Field(..., min_length=1, max_length=100, description="Genre name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")
    description: Optional[str] = Field(None, description="Genre description")
    color_code: Optional[str] = Field(None, max_length=20, description="Color code for UI visualization")
    icon_name: Optional[str] = Field(None, max_length=50, description="Icon identifier")


class AudioGenreCreate(AudioGenreBase):
    """
    Model for creating new audio genre.
    """

    parent_genre_id: Optional[UUID] = Field(None, description="Parent genre UUID for sub-genres")


class AudioGenreUpdate(BaseModel):
    """
    Model for updating existing audio genre.
    All fields are optional.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color_code: Optional[str] = Field(None, max_length=20)
    icon_name: Optional[str] = Field(None, max_length=50)


class AudioGenreResponse(AudioGenreBase):
    """
    Model for audio genre response (includes database fields).
    """

    id: UUID = Field(..., description="Genre UUID")
    parent_genre_id: Optional[UUID] = Field(None, description="Parent genre UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# ============================================================
# ARTIST MODELS
# ============================================================

class ArtistBase(BaseModel):
    """
    Base artist model with common fields.
    """

    name: str = Field(..., min_length=1, max_length=500, description="Artist name")
    sort_name: Optional[str] = Field(None, max_length=500, description="Name for alphabetical sorting")
    artist_type: Optional[str] = Field(
        None,
        max_length=50,
        description="Artist type: person, group, orchestra, choir, character, other"
    )
    bio: Optional[str] = Field(None, description="Artist biography")
    country: Optional[str] = Field(None, max_length=10, description="ISO country code")
    begin_date: Optional[date] = Field(None, description="Birth date or formation date")
    end_date: Optional[date] = Field(None, description="Death date or disbandment date")
    image_url: Optional[str] = Field(None, max_length=500, description="Artist image URL")


class ArtistCreate(ArtistBase):
    """
    Model for creating new artist.
    """

    musicbrainz_id: Optional[UUID] = Field(None, description="MusicBrainz artist ID")
    spotify_id: Optional[str] = Field(None, max_length=100, description="Spotify artist ID")
    spotify_followers: Optional[int] = Field(None, ge=0, description="Spotify follower count")
    spotify_popularity: Optional[int] = Field(None, ge=0, le=100, description="Spotify popularity (0-100)")


class ArtistUpdate(BaseModel):
    """
    Model for updating existing artist.
    All fields are optional.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=500)
    sort_name: Optional[str] = Field(None, max_length=500)
    artist_type: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None
    country: Optional[str] = Field(None, max_length=10)
    begin_date: Optional[date] = None
    end_date: Optional[date] = None
    image_url: Optional[str] = Field(None, max_length=500)
    spotify_followers: Optional[int] = Field(None, ge=0)
    spotify_popularity: Optional[int] = Field(None, ge=0, le=100)


class ArtistResponse(ArtistBase):
    """
    Model for artist response (includes database fields).
    """

    id: UUID = Field(..., description="Artist UUID")
    musicbrainz_id: Optional[UUID] = Field(None, description="MusicBrainz ID")
    spotify_id: Optional[str] = Field(None, description="Spotify ID")
    spotify_followers: Optional[int] = Field(None, description="Spotify followers")
    spotify_popularity: Optional[int] = Field(None, description="Spotify popularity (0-100)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_synced_musicbrainz: Optional[datetime] = Field(None, description="Last MusicBrainz sync")
    last_synced_spotify: Optional[datetime] = Field(None, description="Last Spotify sync")

    class Config:
        from_attributes = True


# ============================================================
# AUDIO CONTENT MODELS (Albums, Singles, EPs)
# ============================================================

class AudioContentBase(BaseModel):
    """
    Base audio content model with common fields.
    """

    title: str = Field(..., min_length=1, max_length=500, description="Album/Single title")
    content_type: str = Field(
        ...,
        max_length=50,
        description="Content type: album, single, ep, compilation, soundtrack"
    )
    release_date: Optional[date] = Field(None, description="Release date")
    release_year: Optional[int] = Field(None, ge=1900, le=2100, description="Release year")
    total_tracks: Optional[int] = Field(None, ge=0, description="Total number of tracks")
    total_duration_ms: Optional[int] = Field(None, ge=0, description="Total duration in milliseconds")
    cover_art_url: Optional[str] = Field(None, max_length=500, description="Cover art URL")
    cover_art_small_url: Optional[str] = Field(None, max_length=500, description="Small cover art URL")
    cover_art_large_url: Optional[str] = Field(None, max_length=500, description="Large cover art URL")
    record_label: Optional[str] = Field(None, max_length=200, description="Record label")
    copyright_text: Optional[str] = Field(None, description="Copyright information")


class AudioContentCreate(AudioContentBase):
    """
    Model for creating new audio content.
    """

    primary_artist_id: UUID = Field(..., description="Primary artist UUID")
    musicbrainz_id: Optional[UUID] = Field(None, description="MusicBrainz release ID")
    spotify_id: Optional[str] = Field(None, max_length=100, description="Spotify album ID")
    spotify_popularity: Optional[int] = Field(None, ge=0, le=100, description="Spotify popularity (0-100)")


class AudioContentUpdate(BaseModel):
    """
    Model for updating existing audio content.
    All fields are optional.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content_type: Optional[str] = Field(None, max_length=50)
    release_date: Optional[date] = None
    release_year: Optional[int] = Field(None, ge=1900, le=2100)
    total_tracks: Optional[int] = Field(None, ge=0)
    total_duration_ms: Optional[int] = Field(None, ge=0)
    cover_art_url: Optional[str] = Field(None, max_length=500)
    record_label: Optional[str] = Field(None, max_length=200)
    copyright_text: Optional[str] = None
    spotify_popularity: Optional[int] = Field(None, ge=0, le=100)


class AudioContentResponse(AudioContentBase):
    """
    Model for audio content response (includes database fields).
    """

    id: UUID = Field(..., description="Audio content UUID")
    primary_artist_id: UUID = Field(..., description="Primary artist UUID")
    musicbrainz_id: Optional[UUID] = Field(None, description="MusicBrainz ID")
    spotify_id: Optional[str] = Field(None, description="Spotify ID")
    spotify_popularity: Optional[int] = Field(None, description="Spotify popularity")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_synced_musicbrainz: Optional[datetime] = Field(None, description="Last MusicBrainz sync")
    last_synced_spotify: Optional[datetime] = Field(None, description="Last Spotify sync")

    # Optional nested data
    primary_artist: Optional[ArtistResponse] = Field(None, description="Primary artist details")
    genres: Optional[List[AudioGenreResponse]] = Field(default_factory=list, description="Associated genres")

    class Config:
        from_attributes = True


# ============================================================
# AUDIO TRACK MODELS
# ============================================================

class AudioTrackBase(BaseModel):
    """
    Base audio track model with common fields.
    """

    title: str = Field(..., min_length=1, max_length=500, description="Track title")
    track_number: Optional[int] = Field(None, ge=1, description="Track number")
    disc_number: int = Field(default=1, ge=1, description="Disc number")
    duration_ms: int = Field(..., ge=0, description="Duration in milliseconds")
    explicit: bool = Field(default=False, description="Explicit content flag")


class AudioTrackCreate(AudioTrackBase):
    """
    Model for creating new audio track.
    """

    audio_content_id: UUID = Field(..., description="Parent audio content UUID")
    musicbrainz_id: Optional[UUID] = Field(None, description="MusicBrainz recording ID")
    spotify_id: Optional[str] = Field(None, max_length=100, description="Spotify track ID")
    isrc: Optional[str] = Field(None, max_length=20, description="International Standard Recording Code")

    # Spotify Audio Features
    spotify_preview_url: Optional[str] = Field(None, max_length=500, description="30-second preview URL")
    acousticness: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Acousticness (0.0-1.0)")
    danceability: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Danceability (0.0-1.0)")
    energy: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Energy (0.0-1.0)")
    instrumentalness: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Instrumentalness (0.0-1.0)")
    liveness: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Liveness (0.0-1.0)")
    loudness: Optional[Decimal] = Field(None, description="Loudness in dB")
    speechiness: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Speechiness (0.0-1.0)")
    valence: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Valence/positivity (0.0-1.0)")
    tempo: Optional[Decimal] = Field(None, ge=0.0, description="Tempo in BPM")
    time_signature: Optional[int] = Field(None, ge=1, description="Time signature")
    key: Optional[int] = Field(None, ge=0, le=11, description="Key (0-11, C to B)")
    mode: Optional[int] = Field(None, ge=0, le=1, description="Mode (0=minor, 1=major)")


class AudioTrackUpdate(BaseModel):
    """
    Model for updating existing audio track.
    All fields are optional.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    track_number: Optional[int] = Field(None, ge=1)
    disc_number: Optional[int] = Field(None, ge=1)
    duration_ms: Optional[int] = Field(None, ge=0)
    explicit: Optional[bool] = None
    spotify_preview_url: Optional[str] = Field(None, max_length=500)


class AudioTrackResponse(AudioTrackBase):
    """
    Model for audio track response (includes database fields).
    """

    id: UUID = Field(..., description="Track UUID")
    audio_content_id: UUID = Field(..., description="Parent audio content UUID")
    musicbrainz_id: Optional[UUID] = Field(None, description="MusicBrainz ID")
    spotify_id: Optional[str] = Field(None, description="Spotify ID")
    isrc: Optional[str] = Field(None, description="ISRC code")

    # Spotify Audio Features
    spotify_preview_url: Optional[str] = Field(None, description="Preview URL")
    acousticness: Optional[Decimal] = Field(None, description="Acousticness")
    danceability: Optional[Decimal] = Field(None, description="Danceability")
    energy: Optional[Decimal] = Field(None, description="Energy")
    instrumentalness: Optional[Decimal] = Field(None, description="Instrumentalness")
    liveness: Optional[Decimal] = Field(None, description="Liveness")
    loudness: Optional[Decimal] = Field(None, description="Loudness")
    speechiness: Optional[Decimal] = Field(None, description="Speechiness")
    valence: Optional[Decimal] = Field(None, description="Valence")
    tempo: Optional[Decimal] = Field(None, description="Tempo")
    time_signature: Optional[int] = Field(None, description="Time signature")
    key: Optional[int] = Field(None, description="Musical key")
    mode: Optional[int] = Field(None, description="Mode")

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_synced_musicbrainz: Optional[datetime] = Field(None, description="Last MusicBrainz sync")
    last_synced_spotify: Optional[datetime] = Field(None, description="Last Spotify sync")

    class Config:
        from_attributes = True


# ============================================================
# LIST RESPONSE MODELS
# ============================================================

class AudioGenreListResponse(BaseModel):
    """
    Model for audio genre list response.
    """

    items: List[AudioGenreResponse] = Field(..., description="List of genres")
    total: int = Field(..., ge=0, description="Total number of genres")


class ArtistListResponse(BaseModel):
    """
    Model for artist list response.
    """

    items: List[ArtistResponse] = Field(..., description="List of artists")
    total: int = Field(..., ge=0, description="Total number of artists")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, description="Items per page")


class AudioContentListResponse(BaseModel):
    """
    Model for audio content list response.
    """

    items: List[AudioContentResponse] = Field(..., description="List of audio content")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, description="Items per page")


class AudioTrackListResponse(BaseModel):
    """
    Model for audio track list response.
    """

    items: List[AudioTrackResponse] = Field(..., description="List of tracks")
    total: int = Field(..., ge=0, description="Total number of tracks")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, description="Items per page")


# ============================================================
# FILTER MODELS
# ============================================================

class AudioContentFilters(BaseModel):
    """
    Filters for audio content queries.
    """

    content_type: Optional[str] = Field(None, description="Filter by content type")
    artist_id: Optional[UUID] = Field(None, description="Filter by artist")
    genre_id: Optional[UUID] = Field(None, description="Filter by genre")
    year_from: Optional[int] = Field(None, ge=1900, le=2100, description="From year")
    year_to: Optional[int] = Field(None, ge=1900, le=2100, description="To year")
    sort_by: str = Field(default="title", description="Sort field")
    sort_order: str = Field(default="asc", description="Sort order: asc or desc")


class ArtistFilters(BaseModel):
    """
    Filters for artist queries.
    """

    artist_type: Optional[str] = Field(None, description="Filter by artist type")
    country: Optional[str] = Field(None, description="Filter by country")
    sort_by: str = Field(default="name", description="Sort field")
    sort_order: str = Field(default="asc", description="Sort order: asc or desc")
