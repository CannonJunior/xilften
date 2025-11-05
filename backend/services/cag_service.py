"""
CAG (Context-Augmented Generation) Service

Combines vector database retrieval with LLM generation for intelligent media recommendations.
This is NOT traditional RAG (document retrieval), but creative synthesis for media mashups.

Architecture:
1. User Query → Parse Intent
2. Extract Criteria → Query ChromaDB for similar media
3. Retrieve Context → Augment Prompt with relevant media data
4. Ollama Generation → Creative synthesis
5. Return Response

Key Features:
- Content mashup generation
- High-concept story pitches
- Personalized recommendations
- Semantic search across media database
"""

import logging
from typing import AsyncGenerator, Dict, List, Optional, Any
from pydantic import BaseModel, Field
import json

from config.database import get_chroma
from backend.services.ollama_client import get_ollama_client, OllamaMessage
from backend.services.prompts import format_prompt, get_prompt_template

logger = logging.getLogger(__name__)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class MediaReference(BaseModel):
    """Media title used as reference for mashup/generation."""
    title: str = Field(..., description="Media title")
    media_type: Optional[str] = Field(None, description="movie, tv, anime, etc.")
    aspects: Optional[List[str]] = Field(
        default=None,
        description="Specific aspects to extract (dialogue, action, tone, etc.)"
    )


class MashupRequest(BaseModel):
    """Request for content mashup generation."""
    user_query: str = Field(..., description="User's natural language query")
    references: List[MediaReference] = Field(..., description="Reference media to combine")
    detail_level: str = Field(
        default="simple",
        description="'simple' or 'detailed'"
    )
    temperature: float = Field(default=0.8, ge=0.0, le=2.0)


class HighConceptRequest(BaseModel):
    """Request for high-concept story pitch."""
    references: List[MediaReference] = Field(..., description="Inspiration sources")
    extraction_focus: str = Field(
        ...,
        description="What to extract (e.g., 'witty dialogue, political intrigue')"
    )
    pitch_type: str = Field(
        default="full",
        description="'full' pitch or 'logline' only"
    )
    temperature: float = Field(default=0.9, ge=0.0, le=2.0)


class RecommendationRequest(BaseModel):
    """Request for personalized recommendations."""
    user_query: str = Field(..., description="User's request/mood")
    user_preferences: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Genre preferences, favorite directors, etc."
    )
    viewing_history: Optional[List[str]] = Field(
        default=None,
        description="Titles user has already watched"
    )
    mood_based: bool = Field(default=False, description="Focus on current mood")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class SimilarTitlesRequest(BaseModel):
    """Request for similar title recommendations."""
    reference_title: str = Field(..., description="Title to find similar matches for")
    match_aspects: Optional[List[str]] = Field(
        default=None,
        description="Aspects to match (tone, genre, style, etc.)"
    )
    count: int = Field(default=7, ge=1, le=20)
    temperature: float = Field(default=0.6, ge=0.0, le=2.0)


class ChatRequest(BaseModel):
    """General chat request about media."""
    user_message: str = Field(..., description="User's message")
    conversation_history: Optional[List[OllamaMessage]] = Field(
        default=None,
        description="Previous conversation messages"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class CAGResponse(BaseModel):
    """Response from CAG service."""
    success: bool
    content: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# =============================================================================
# CAG SERVICE
# =============================================================================

class CAGService:
    """
    Context-Augmented Generation Service

    Orchestrates the entire CAG pipeline:
    1. Query parsing and intent extraction
    2. Vector similarity search in ChromaDB
    3. Context retrieval and enrichment
    4. Prompt construction with templates
    5. LLM generation via Ollama
    6. Response formatting and metadata

    Usage:
        service = CAGService()
        response = await service.generate_mashup(request)
        async for chunk in service.generate_mashup_stream(request):
            print(chunk)
    """

    def __init__(self):
        """Initialize CAG service with clients."""
        self.ollama = get_ollama_client()
        self.chroma = get_chroma()
        self.media_collection = self.chroma.get_collection("media_embeddings")
        self.mashup_collection = self.chroma.get_collection("mashup_concepts")
        logger.info("🧬 CAG Service initialized")


    async def _retrieve_similar_media(
        self,
        query_text: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar media from vector database.

        Args:
            query_text (str): Query to search for
            n_results (int): Number of results to return

        Returns:
            List[Dict]: Similar media metadata
        """
        try:
            # Generate embedding for query
            query_embedding = await self.ollama.generate_embedding(query_text)

            if not query_embedding:
                logger.warning("⚠️  Failed to generate query embedding")
                return []

            # Query ChromaDB
            results = self.media_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            # Format results
            similar_media = []
            if results and results.get("metadatas"):
                for i, metadata in enumerate(results["metadatas"][0]):
                    similar_media.append({
                        "metadata": metadata,
                        "distance": results["distances"][0][i] if results.get("distances") else None
                    })

            logger.info(f"✅ Retrieved {len(similar_media)} similar media items")
            return similar_media

        except Exception as e:
            logger.error(f"❌ Similar media retrieval failed: {e}")
            return []


    def _format_references(self, references: List[MediaReference]) -> str:
        """
        Format media references for prompt.

        Args:
            references (List[MediaReference]): Reference media

        Returns:
            str: Formatted reference string
        """
        formatted = []
        for ref in references:
            parts = [f"- **{ref.title}**"]
            if ref.media_type:
                parts.append(f"({ref.media_type})")
            if ref.aspects:
                parts.append(f"[Extract: {', '.join(ref.aspects)}]")
            formatted.append(" ".join(parts))

        return "\n".join(formatted)


    def _format_user_preferences(self, preferences: Optional[Dict[str, Any]]) -> str:
        """Format user preferences for prompt."""
        if not preferences:
            return "No specific preferences provided"

        lines = []
        for key, value in preferences.items():
            if isinstance(value, list):
                lines.append(f"- {key.replace('_', ' ').title()}: {', '.join(map(str, value))}")
            else:
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")

        return "\n".join(lines)


    async def generate_mashup(
        self,
        request: MashupRequest
    ) -> CAGResponse:
        """
        Generate content mashup from references.

        Args:
            request (MashupRequest): Mashup request

        Returns:
            CAGResponse: Generated mashup concept
        """
        try:
            # Select template based on detail level
            template_name = f"mashup_{request.detail_level}"

            # Format references
            references_text = self._format_references(request.references)

            # Get similar media from database (optional enrichment)
            similar_media = await self._retrieve_similar_media(
                request.user_query,
                n_results=3
            )

            # Format prompt
            system_prompt, user_prompt = format_prompt(
                template_name,
                references=references_text,
                user_query=request.user_query
            )

            if not system_prompt or not user_prompt:
                return CAGResponse(
                    success=False,
                    content="",
                    error=f"Template '{template_name}' not found"
                )

            # Generate response
            logger.info(f"🎬 Generating {request.detail_level} mashup...")
            response = await self.ollama.chat(
                user_message=user_prompt,
                system_prompt=system_prompt,
                temperature=request.temperature
            )

            if not response:
                return CAGResponse(
                    success=False,
                    content="",
                    error="LLM generation failed"
                )

            return CAGResponse(
                success=True,
                content=response,
                metadata={
                    "template": template_name,
                    "reference_count": len(request.references),
                    "similar_media_found": len(similar_media)
                }
            )

        except Exception as e:
            logger.error(f"❌ Mashup generation failed: {e}")
            return CAGResponse(
                success=False,
                content="",
                error=str(e)
            )


    async def generate_mashup_stream(
        self,
        request: MashupRequest
    ) -> AsyncGenerator[str, None]:
        """
        Generate content mashup with streaming response.

        Args:
            request (MashupRequest): Mashup request

        Yields:
            str: Response chunks
        """
        try:
            template_name = f"mashup_{request.detail_level}"
            references_text = self._format_references(request.references)

            system_prompt, user_prompt = format_prompt(
                template_name,
                references=references_text,
                user_query=request.user_query
            )

            if not system_prompt or not user_prompt:
                yield f"[Error: Template '{template_name}' not found]"
                return

            logger.info(f"🎬 Streaming {request.detail_level} mashup...")

            async for chunk in self.ollama.stream_chat(
                user_message=user_prompt,
                system_prompt=system_prompt,
                temperature=request.temperature
            ):
                yield chunk

        except Exception as e:
            logger.error(f"❌ Streaming mashup generation failed: {e}")
            yield f"[Error: {str(e)}]"


    async def generate_high_concept(
        self,
        request: HighConceptRequest
    ) -> CAGResponse:
        """
        Generate high-concept story pitch.

        Args:
            request (HighConceptRequest): High-concept request

        Returns:
            CAGResponse: Generated pitch
        """
        try:
            template_name = "logline_generator" if request.pitch_type == "logline" else "high_concept_pitch"
            references_text = self._format_references(request.references)

            system_prompt, user_prompt = format_prompt(
                template_name,
                references=references_text,
                extraction_focus=request.extraction_focus
            )

            if not system_prompt or not user_prompt:
                return CAGResponse(
                    success=False,
                    content="",
                    error=f"Template '{template_name}' not found"
                )

            logger.info(f"📝 Generating {request.pitch_type} high-concept...")
            response = await self.ollama.chat(
                user_message=user_prompt,
                system_prompt=system_prompt,
                temperature=request.temperature
            )

            if not response:
                return CAGResponse(
                    success=False,
                    content="",
                    error="LLM generation failed"
                )

            return CAGResponse(
                success=True,
                content=response,
                metadata={
                    "template": template_name,
                    "pitch_type": request.pitch_type,
                    "reference_count": len(request.references)
                }
            )

        except Exception as e:
            logger.error(f"❌ High-concept generation failed: {e}")
            return CAGResponse(
                success=False,
                content="",
                error=str(e)
            )


    async def generate_recommendations(
        self,
        request: RecommendationRequest
    ) -> CAGResponse:
        """
        Generate personalized recommendations.

        Args:
            request (RecommendationRequest): Recommendation request

        Returns:
            CAGResponse: Recommendations
        """
        try:
            template_name = "mood_recommendations" if request.mood_based else "personalized_recommendations"

            # Retrieve similar media from database
            similar_media = await self._retrieve_similar_media(
                request.user_query,
                n_results=10
            )

            if request.mood_based:
                system_prompt, user_prompt = format_prompt(
                    template_name,
                    mood=request.user_query,
                    context=self._format_user_preferences(request.user_preferences)
                )
            else:
                system_prompt, user_prompt = format_prompt(
                    template_name,
                    user_preferences=self._format_user_preferences(request.user_preferences),
                    viewing_history="\n".join(f"- {title}" for title in (request.viewing_history or [])),
                    user_query=request.user_query
                )

            if not system_prompt or not user_prompt:
                return CAGResponse(
                    success=False,
                    content="",
                    error=f"Template '{template_name}' not found"
                )

            logger.info(f"🎯 Generating recommendations...")
            response = await self.ollama.chat(
                user_message=user_prompt,
                system_prompt=system_prompt,
                temperature=request.temperature
            )

            if not response:
                return CAGResponse(
                    success=False,
                    content="",
                    error="LLM generation failed"
                )

            return CAGResponse(
                success=True,
                content=response,
                metadata={
                    "template": template_name,
                    "mood_based": request.mood_based,
                    "similar_media_found": len(similar_media)
                }
            )

        except Exception as e:
            logger.error(f"❌ Recommendation generation failed: {e}")
            return CAGResponse(
                success=False,
                content="",
                error=str(e)
            )


    async def find_similar_titles(
        self,
        request: SimilarTitlesRequest
    ) -> CAGResponse:
        """
        Find titles similar to a reference.

        Args:
            request (SimilarTitlesRequest): Similar titles request

        Returns:
            CAGResponse: Similar titles
        """
        try:
            # Retrieve similar media from database
            similar_media = await self._retrieve_similar_media(
                request.reference_title,
                n_results=request.count
            )

            match_aspects_text = ", ".join(request.match_aspects) if request.match_aspects else "all aspects"

            system_prompt, user_prompt = format_prompt(
                "similar_titles",
                reference_title=request.reference_title,
                match_aspects=match_aspects_text
            )

            if not system_prompt or not user_prompt:
                return CAGResponse(
                    success=False,
                    content="",
                    error="Template 'similar_titles' not found"
                )

            logger.info(f"🔍 Finding titles similar to '{request.reference_title}'...")
            response = await self.ollama.chat(
                user_message=user_prompt,
                system_prompt=system_prompt,
                temperature=request.temperature
            )

            if not response:
                return CAGResponse(
                    success=False,
                    content="",
                    error="LLM generation failed"
                )

            return CAGResponse(
                success=True,
                content=response,
                metadata={
                    "reference_title": request.reference_title,
                    "match_aspects": match_aspects_text,
                    "similar_media_found": len(similar_media)
                }
            )

        except Exception as e:
            logger.error(f"❌ Similar titles search failed: {e}")
            return CAGResponse(
                success=False,
                content="",
                error=str(e)
            )


    async def chat(
        self,
        request: ChatRequest
    ) -> CAGResponse:
        """
        General chat about media.

        Args:
            request (ChatRequest): Chat request

        Returns:
            CAGResponse: Chat response
        """
        try:
            system_prompt, user_prompt = format_prompt(
                "casual_chat",
                user_message=request.user_message
            )

            if not system_prompt or not user_prompt:
                return CAGResponse(
                    success=False,
                    content="",
                    error="Template 'casual_chat' not found"
                )

            logger.info(f"💬 Processing chat message...")
            response = await self.ollama.chat(
                user_message=user_prompt,
                system_prompt=system_prompt,
                conversation_history=request.conversation_history,
                temperature=request.temperature
            )

            if not response:
                return CAGResponse(
                    success=False,
                    content="",
                    error="LLM generation failed"
                )

            return CAGResponse(
                success=True,
                content=response,
                metadata={
                    "has_history": bool(request.conversation_history)
                }
            )

        except Exception as e:
            logger.error(f"❌ Chat failed: {e}")
            return CAGResponse(
                success=False,
                content="",
                error=str(e)
            )


    async def chat_stream(
        self,
        request: ChatRequest
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses.

        Args:
            request (ChatRequest): Chat request

        Yields:
            str: Response chunks
        """
        try:
            system_prompt, user_prompt = format_prompt(
                "casual_chat",
                user_message=request.user_message
            )

            if not system_prompt or not user_prompt:
                yield "[Error: Template 'casual_chat' not found]"
                return

            logger.info(f"💬 Streaming chat response...")

            async for chunk in self.ollama.stream_chat(
                user_message=user_prompt,
                system_prompt=system_prompt,
                conversation_history=request.conversation_history,
                temperature=request.temperature
            ):
                yield chunk

        except Exception as e:
            logger.error(f"❌ Streaming chat failed: {e}")
            yield f"[Error: {str(e)}]"


# Global service instance
_cag_service: Optional[CAGService] = None


def get_cag_service() -> CAGService:
    """
    Get or create global CAG service instance.

    Returns:
        CAGService: Global service instance
    """
    global _cag_service
    if _cag_service is None:
        _cag_service = CAGService()
    return _cag_service
