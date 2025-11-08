"""
AI Routes

API endpoints for AI-powered features:
- Content mashup generation
- High-concept story pitches
- Personalized recommendations
- Similar title discovery
- General media chat

All endpoints support both regular and streaming responses.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.services.cag_service import (
    get_cag_service,
    MashupRequest,
    HighConceptRequest,
    RecommendationRequest,
    SimilarTitlesRequest,
    ChatRequest,
    CAGResponse
)
from backend.mcp.movie_detector import get_movie_detector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI"])


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Any = None
    error: str = None


# =============================================================================
# MASHUP ENDPOINTS
# =============================================================================

@router.post("/mashup", response_model=APIResponse)
async def generate_mashup(request: MashupRequest):
    """
    Generate a creative content mashup from multiple media references.

    **Example Request**:
    ```json
    {
      "user_query": "Fantasy action with serious drama like Chernobyl",
      "references": [
        {
          "title": "World of Warcraft",
          "media_type": "game",
          "aspects": ["fantasy", "action"]
        },
        {
          "title": "Chernobyl",
          "media_type": "tv",
          "aspects": ["serious drama", "tension"]
        }
      ],
      "detail_level": "simple",
      "temperature": 0.8
    }
    ```

    **Detail Levels**:
    - `simple`: Concise mashup with key points
    - `detailed`: Comprehensive breakdown with full analysis

    **Returns**: Creative mashup concept with movie names enriched with icons
    """
    try:
        logger.info(f"📬 Received mashup request: {request.user_query}")
        service = get_cag_service()
        result = await service.generate_mashup(request)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Enrich response with movie detection
        detector = get_movie_detector()
        enriched_result = detector.enrich_response_with_metadata(result.content)

        return APIResponse(
            success=True,
            data={
                "content": enriched_result['enriched_text'],
                "metadata": {
                    **result.metadata,
                    "detected_movies": enriched_result['detected_movies'],
                    "detection_count": enriched_result['detection_count'],
                    "poster_gallery_html": enriched_result['poster_gallery_html']
                }
            }
        )

    except Exception as e:
        logger.error(f"❌ Mashup endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mashup/stream")
async def generate_mashup_stream(request: MashupRequest):
    """
    Generate a creative content mashup with streaming response.

    Same parameters as `/mashup`, but returns Server-Sent Events (SSE) stream.

    **Returns**: Streaming text chunks as they're generated
    """
    try:
        logger.info(f"📬 Received streaming mashup request: {request.user_query}")
        service = get_cag_service()

        async def event_stream():
            """Generate SSE events."""
            async for chunk in service.generate_mashup_stream(request):
                yield f"data: {chunk}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    except Exception as e:
        logger.error(f"❌ Streaming mashup endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# HIGH-CONCEPT ENDPOINTS
# =============================================================================

@router.post("/high-concept", response_model=APIResponse)
async def generate_high_concept(request: HighConceptRequest):
    """
    Generate an original high-concept story pitch inspired by references.

    **Example Request**:
    ```json
    {
      "references": [
        {
          "title": "His Girl Friday",
          "aspects": ["witty dialogue"]
        },
        {
          "title": "Game of Thrones",
          "aspects": ["action", "political intrigue"]
        },
        {
          "title": "Casablanca",
          "aspects": ["plot structure", "romance"]
        }
      ],
      "extraction_focus": "Witty banter, political intrigue, romantic tension",
      "pitch_type": "full",
      "temperature": 0.9
    }
    ```

    **Pitch Types**:
    - `full`: Complete pitch with acts, characters, and structure
    - `logline`: Multiple concise logline options

    **Returns**: Original story concept with movie names enriched with icons
    """
    try:
        logger.info(f"📬 Received high-concept request with {len(request.references)} references")
        service = get_cag_service()
        result = await service.generate_high_concept(request)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Enrich response with movie detection
        detector = get_movie_detector()
        enriched_result = detector.enrich_response_with_metadata(result.content)

        return APIResponse(
            success=True,
            data={
                "content": enriched_result['enriched_text'],
                "metadata": {
                    **result.metadata,
                    "detected_movies": enriched_result['detected_movies'],
                    "detection_count": enriched_result['detection_count'],
                    "poster_gallery_html": enriched_result['poster_gallery_html']
                }
            }
        )

    except Exception as e:
        logger.error(f"❌ High-concept endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# RECOMMENDATION ENDPOINTS
# =============================================================================

@router.post("/recommend", response_model=APIResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized media recommendations.

    **Example Request**:
    ```json
    {
      "user_query": "Something dark and philosophical",
      "user_preferences": {
        "genres": ["sci-fi", "thriller"],
        "favorite_directors": ["Denis Villeneuve", "Christopher Nolan"],
        "preferred_runtime": "90-150 minutes"
      },
      "viewing_history": [
        "Blade Runner 2049",
        "Arrival",
        "The Prestige"
      ],
      "mood_based": false,
      "temperature": 0.7
    }
    ```

    **Mood-Based Recommendations**:
    Set `mood_based: true` to get recommendations based on current emotional state.

    **Returns**: Personalized recommendations with movie names enriched with icons
    """
    try:
        logger.info(f"📬 Received recommendation request: {request.user_query}")
        service = get_cag_service()
        result = await service.generate_recommendations(request)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Enrich response with movie detection
        detector = get_movie_detector()
        enriched_result = detector.enrich_response_with_metadata(result.content)

        return APIResponse(
            success=True,
            data={
                "content": enriched_result['enriched_text'],
                "metadata": {
                    **result.metadata,
                    "detected_movies": enriched_result['detected_movies'],
                    "detection_count": enriched_result['detection_count'],
                    "poster_gallery_html": enriched_result['poster_gallery_html']
                }
            }
        )

    except Exception as e:
        logger.error(f"❌ Recommendation endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/similar", response_model=APIResponse)
async def find_similar_titles(request: SimilarTitlesRequest):
    """
    Find titles similar to a reference.

    **Example Request**:
    ```json
    {
      "reference_title": "Blade Runner",
      "match_aspects": ["tone", "visual style", "themes"],
      "count": 7,
      "temperature": 0.6
    }
    ```

    **Match Aspects** (optional):
    - `tone`: Emotional feel and atmosphere
    - `genre`: Genre and sub-genre
    - `style`: Visual and narrative style
    - `themes`: Thematic content
    - `pacing`: Story pacing and structure

    **Returns**: Similar titles with movie names enriched with icons
    """
    try:
        logger.info(f"📬 Received similar titles request for: {request.reference_title}")
        service = get_cag_service()
        result = await service.find_similar_titles(request)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Enrich response with movie detection
        detector = get_movie_detector()
        enriched_result = detector.enrich_response_with_metadata(result.content)

        return APIResponse(
            success=True,
            data={
                "content": enriched_result['enriched_text'],
                "metadata": {
                    **result.metadata,
                    "detected_movies": enriched_result['detected_movies'],
                    "detection_count": enriched_result['detection_count'],
                    "poster_gallery_html": enriched_result['poster_gallery_html']
                }
            }
        )

    except Exception as e:
        logger.error(f"❌ Similar titles endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CHAT ENDPOINTS
# =============================================================================

@router.post("/chat", response_model=APIResponse)
async def chat(request: ChatRequest):
    """
    General chat about media topics.

    **Example Request**:
    ```json
    {
      "user_message": "What makes Iranian cinema unique?",
      "conversation_history": [
        {
          "role": "user",
          "content": "Tell me about film noir"
        },
        {
          "role": "assistant",
          "content": "Film noir is a cinematic style..."
        }
      ],
      "temperature": 0.7
    }
    ```

    **Conversation History** (optional):
    Include previous messages to maintain context across multiple exchanges.

    **Returns**: Conversational response about media with movie names enriched with icons
    """
    try:
        logger.info(f"📬 Received chat message: {request.user_message[:50]}...")
        service = get_cag_service()
        result = await service.chat(request)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Enrich response with movie detection
        detector = get_movie_detector()
        enriched_result = detector.enrich_response_with_metadata(result.content)

        return APIResponse(
            success=True,
            data={
                "content": enriched_result['enriched_text'],
                "metadata": {
                    **result.metadata,
                    "detected_movies": enriched_result['detected_movies'],
                    "detection_count": enriched_result['detection_count'],
                    "poster_gallery_html": enriched_result['poster_gallery_html']
                }
            }
        )

    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses in real-time.

    Same parameters as `/chat`, but returns Server-Sent Events (SSE) stream.

    **Returns**: Streaming text chunks as they're generated
    """
    try:
        logger.info(f"📬 Received streaming chat request: {request.user_message[:50]}...")
        service = get_cag_service()

        async def event_stream():
            """Generate SSE events."""
            async for chunk in service.chat_stream(request):
                yield f"data: {chunk}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    except Exception as e:
        logger.error(f"❌ Streaming chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# STATUS ENDPOINTS
# =============================================================================

@router.get("/status", response_model=APIResponse)
async def ai_status():
    """
    Check AI service status and capabilities.

    **Returns**: Status of Ollama, available models, and service health
    """
    try:
        service = get_cag_service()

        # Check Ollama health
        ollama_healthy = await service.ollama.health_check()

        # List available models
        models = await service.ollama.list_models()

        return APIResponse(
            success=True,
            data={
                "ollama": {
                    "healthy": ollama_healthy,
                    "base_url": service.ollama.base_url,
                    "default_model": service.ollama.default_model,
                    "available_models": [
                        {
                            "name": model.get("name"),
                            "size": model.get("size"),
                            "family": model.get("details", {}).get("family")
                        }
                        for model in models
                    ]
                },
                "chromadb": {
                    "media_collection": service.media_collection.name,
                    "mashup_collection": service.mashup_collection.name,
                },
                "capabilities": [
                    "content_mashup",
                    "high_concept_pitch",
                    "personalized_recommendations",
                    "similar_titles",
                    "media_chat"
                ]
            }
        )

    except Exception as e:
        logger.error(f"❌ Status endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=APIResponse)
async def list_templates():
    """
    List all available prompt templates.

    **Returns**: Names and descriptions of available templates
    """
    try:
        from backend.services.prompts import PROMPT_TEMPLATES

        templates_info = [
            {
                "name": name,
                "description": template.description,
                "has_example": bool(template.example_input and template.example_output)
            }
            for name, template in PROMPT_TEMPLATES.items()
        ]

        return APIResponse(
            success=True,
            data={
                "templates": templates_info,
                "count": len(templates_info)
            }
        )

    except Exception as e:
        logger.error(f"❌ Templates endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
