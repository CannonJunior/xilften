"""
Persona API Routes

Endpoints for managing critic personas and CAG cache.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from backend.services.persona_service import get_persona_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personas", tags=["Personas"])


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Any = None
    error: str = None


class LoadPersonaRequest(BaseModel):
    """Request to load a persona."""
    persona_id: str


# =============================================================================
# PERSONA ENDPOINTS
# =============================================================================

@router.get("/list", response_model=APIResponse)
async def list_personas():
    """
    List all available critic personas.

    Returns:
        List of persona summaries (id, name, title, etc.)
    """
    try:
        persona_service = get_persona_service()
        personas = persona_service.list_personas()

        return APIResponse(
            success=True,
            data=personas
        )
    except Exception as e:
        logger.error(f"❌ Failed to list personas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{persona_id}", response_model=APIResponse)
async def get_persona(persona_id: str):
    """
    Get full persona profile by ID.

    Args:
        persona_id: Persona identifier (e.g., 'pauline_kael')

    Returns:
        Complete persona profile including sample reviews
    """
    try:
        persona_service = get_persona_service()
        persona = persona_service.get_persona(persona_id)

        if not persona:
            raise HTTPException(status_code=404, detail=f"Persona not found: {persona_id}")

        return APIResponse(
            success=True,
            data=persona.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load", response_model=APIResponse)
async def load_persona(request: LoadPersonaRequest):
    """
    Load a persona into the CAG cache.

    This loads the persona's review samples and voice profile into memory
    for use in AI-generated responses.

    Args:
        request: Contains persona_id to load

    Returns:
        Cache metrics after loading
    """
    try:
        persona_service = get_persona_service()
        metrics = persona_service.load_persona_to_cache(request.persona_id)

        logger.info(f"📚 Loaded persona '{request.persona_id}' into CAG cache")

        return APIResponse(
            success=True,
            data={
                "message": f"Persona loaded successfully",
                "persona_id": request.persona_id,
                "cache_metrics": metrics
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Failed to load persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CACHE MANAGEMENT ENDPOINTS
# =============================================================================

@router.get("/cache/metrics", response_model=APIResponse)
async def get_cache_metrics():
    """
    Get current CAG cache metrics.

    Returns:
        Cache usage statistics (size, available space, current persona)
    """
    try:
        persona_service = get_persona_service()
        metrics = persona_service.get_cache_metrics()

        return APIResponse(
            success=True,
            data=metrics
        )
    except Exception as e:
        logger.error(f"❌ Failed to get cache metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear", response_model=APIResponse)
async def clear_cache():
    """
    Clear the CAG cache.

    Removes all loaded persona data from memory.

    Returns:
        Cache metrics after clearing
    """
    try:
        persona_service = get_persona_service()
        metrics = persona_service.clear_cache()

        logger.info("🧹 CAG cache cleared")

        return APIResponse(
            success=True,
            data={
                "message": "Cache cleared successfully",
                "cache_metrics": metrics
            }
        )
    except Exception as e:
        logger.error(f"❌ Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
