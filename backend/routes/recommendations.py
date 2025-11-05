"""
Recommendation API Routes.

Endpoints for multi-criteria recommendation engine and criteria preset management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from uuid import UUID
import logging

from backend.models.recommendation import (
    CriteriaPresetCreate,
    CriteriaPresetUpdate,
    CriteriaPresetResponse,
    RecommendationRequest,
    RecommendationResponse,
    AvailableFieldsResponse,
    AvailableField,
)
from backend.services.recommendation_service import recommendation_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== Recommendation Generation ==========

@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendations(request: RecommendationRequest):
    """
    Generate media recommendations using multi-criteria scoring.

    Args:
        request: Recommendation request with criteria config or preset ID

    Returns:
        RecommendationResponse: Ranked recommendations with scores

    Raises:
        HTTPException: If preset not found or invalid criteria
    """
    try:
        # Determine which criteria to use
        criteria_config = None
        preset_name = None

        if request.preset_id:
            # Use preset
            preset = recommendation_service.get_preset_by_id(request.preset_id)
            if not preset:
                raise HTTPException(status_code=404, detail="Criteria preset not found")

            criteria_config = preset["criteria_config"]
            preset_name = preset["name"]

            # Increment use count
            recommendation_service.increment_use_count(request.preset_id)

        elif request.criteria_config:
            # Use custom criteria
            criteria_config = request.criteria_config

        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either preset_id or criteria_config"
            )

        # Get exclude IDs if needed
        exclude_ids = None
        if request.exclude_watched:
            # TODO: Get watched media IDs from user history
            # For now, exclude nothing
            exclude_ids = []

        # Generate recommendations
        scored_media, total_candidates, execution_time = recommendation_service.generate_recommendations(
            criteria_config=criteria_config,
            limit=request.limit,
            exclude_ids=exclude_ids,
            min_score=request.min_score
        )

        return RecommendationResponse(
            recommendations=scored_media,
            total_candidates=total_candidates,
            criteria_used=criteria_config,
            preset_name=preset_name,
            execution_time_ms=execution_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")


# ========== Criteria Preset Management ==========

@router.get("/presets", response_model=List[CriteriaPresetResponse])
async def list_presets():
    """
    Get all criteria presets.

    Returns:
        List[CriteriaPresetResponse]: List of all presets ordered by default status and usage
    """
    try:
        presets = recommendation_service.get_all_presets()
        return presets
    except Exception as e:
        logger.error(f"Error fetching presets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch presets: {str(e)}")


@router.get("/presets/{preset_id}", response_model=CriteriaPresetResponse)
async def get_preset(preset_id: UUID):
    """
    Get specific criteria preset by ID.

    Args:
        preset_id: Preset UUID

    Returns:
        CriteriaPresetResponse: Preset details

    Raises:
        HTTPException: If preset not found
    """
    try:
        preset = recommendation_service.get_preset_by_id(preset_id)
        if not preset:
            raise HTTPException(status_code=404, detail="Preset not found")
        return preset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching preset {preset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch preset: {str(e)}")


@router.post("/presets", response_model=CriteriaPresetResponse, status_code=201)
async def create_preset(preset_data: CriteriaPresetCreate):
    """
    Create new criteria preset.

    Args:
        preset_data: Preset creation data

    Returns:
        CriteriaPresetResponse: Created preset

    Raises:
        HTTPException: If creation fails
    """
    try:
        preset = recommendation_service.create_preset(preset_data)
        return preset
    except Exception as e:
        logger.error(f"Error creating preset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create preset: {str(e)}")


@router.put("/presets/{preset_id}", response_model=CriteriaPresetResponse)
async def update_preset(preset_id: UUID, updates: CriteriaPresetUpdate):
    """
    Update existing criteria preset.

    Args:
        preset_id: Preset UUID
        updates: Fields to update

    Returns:
        CriteriaPresetResponse: Updated preset

    Raises:
        HTTPException: If preset not found
    """
    try:
        preset = recommendation_service.update_preset(preset_id, updates)
        if not preset:
            raise HTTPException(status_code=404, detail="Preset not found")
        return preset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preset {preset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update preset: {str(e)}")


@router.delete("/presets/{preset_id}", status_code=204)
async def delete_preset(preset_id: UUID):
    """
    Delete criteria preset.

    Args:
        preset_id: Preset UUID

    Raises:
        HTTPException: If preset not found
    """
    try:
        deleted = recommendation_service.delete_preset(preset_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Preset not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting preset {preset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete preset: {str(e)}")


# ========== Available Fields Discovery ==========

@router.get("/available-fields", response_model=AvailableFieldsResponse)
async def get_available_fields():
    """
    Get all available fields that can be used in criteria configuration.

    Returns:
        AvailableFieldsResponse: Available fields grouped by category
    """
    try:
        # Define available fields based on media schema
        fields = [
            AvailableField(
                field_name="genres",
                field_type="array",
                display_name="Genres",
                description="Media genres (e.g., sci-fi, action, drama)",
                supports_values=True,
                example_values=["sci-fi", "action", "drama", "comedy", "horror"]
            ),
            AvailableField(
                field_name="tmdb_rating",
                field_type="number",
                display_name="TMDB Rating",
                description="Rating from The Movie Database (0-10)",
                supports_min_max=True,
                example_values=[7.0, 8.5, 9.0]
            ),
            AvailableField(
                field_name="runtime",
                field_type="number",
                display_name="Runtime",
                description="Runtime in minutes",
                supports_min_max=True,
                example_values=[90, 120, 150]
            ),
            AvailableField(
                field_name="release_year",
                field_type="number",
                display_name="Release Year",
                description="Year of release",
                supports_min_max=True,
                example_values=[2020, 2021, 2022]
            ),
            AvailableField(
                field_name="media_type",
                field_type="string",
                display_name="Media Type",
                description="Type of media (movie, tv, documentary)",
                supports_values=True,
                example_values=["movie", "tv", "documentary"]
            ),
            AvailableField(
                field_name="maturity_rating",
                field_type="string",
                display_name="Maturity Rating",
                description="Age rating (G, PG, PG-13, R, etc.)",
                supports_values=True,
                example_values=["G", "PG", "PG-13", "R", "TV-MA"]
            ),
            AvailableField(
                field_name="popularity_score",
                field_type="number",
                display_name="Popularity Score",
                description="TMDB popularity score",
                supports_min_max=True,
                example_values=[100.0, 500.0, 1000.0]
            ),
            AvailableField(
                field_name="original_language",
                field_type="string",
                display_name="Original Language",
                description="Original language code (e.g., en, es, fr)",
                supports_values=True,
                example_values=["en", "es", "fr", "ja", "ko"]
            ),
            AvailableField(
                field_name="status",
                field_type="string",
                display_name="Status",
                description="Release status (Released, Upcoming, etc.)",
                supports_values=True,
                example_values=["Released", "Upcoming", "In Production"]
            ),
        ]

        # Group fields by category
        categories = {
            "Content": ["genres", "media_type", "original_language"],
            "Quality": ["tmdb_rating", "popularity_score"],
            "Metadata": ["runtime", "release_year", "maturity_rating", "status"],
        }

        return AvailableFieldsResponse(
            fields=fields,
            categories=categories
        )

    except Exception as e:
        logger.error(f"Error fetching available fields: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch available fields: {str(e)}")
