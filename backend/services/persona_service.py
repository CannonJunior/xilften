"""
Persona Service

Manages critic personas for CAG-enhanced AI interactions.
Loads persona profiles, sample reviews, and MCP system prompts.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PersonaSampleReview(BaseModel):
    """Sample review from a persona."""
    film: str
    year: int
    excerpt: str
    rating: str
    key_themes: List[str]


class PersonaProfile(BaseModel):
    """Complete persona profile."""
    id: str
    name: str
    title: str
    years_active: str
    publication: str
    style_characteristics: List[str]
    voice_profile: Dict[str, str]
    mcp_system_prompt: str
    sample_reviews: List[PersonaSampleReview]
    signature_phrases: List[str]
    critical_focus: List[str]


class CAGCache:
    """Context-Augmented Generation cache for persona data."""

    def __init__(self, max_size_mb: float = 10.0):
        """
        Initialize CAG cache.

        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.current_persona_id: Optional[str] = None
        self.loaded_data: Dict = {}
        self.current_size_bytes: int = 0

    def load_persona(self, persona: PersonaProfile) -> None:
        """
        Load persona data into cache.

        Args:
            persona: Persona profile to load
        """
        # Clear existing data if switching personas
        if self.current_persona_id and self.current_persona_id != persona.id:
            self.clear()

        # Calculate size of persona data
        persona_json = persona.model_dump_json()
        persona_size = len(persona_json.encode('utf-8'))

        if persona_size > self.max_size_bytes:
            raise ValueError(f"Persona data ({persona_size} bytes) exceeds cache limit ({self.max_size_bytes} bytes)")

        self.loaded_data = persona.model_dump()
        self.current_persona_id = persona.id
        self.current_size_bytes = persona_size

        logger.info(f"✅ Loaded persona '{persona.name}' into CAG cache ({persona_size} bytes)")

    def get_system_prompt(self) -> Optional[str]:
        """Get MCP system prompt for current persona."""
        return self.loaded_data.get('mcp_system_prompt')

    def get_sample_reviews(self) -> List[Dict]:
        """Get sample reviews for current persona."""
        return self.loaded_data.get('sample_reviews', [])

    def get_voice_profile(self) -> Dict[str, str]:
        """Get voice profile for current persona."""
        return self.loaded_data.get('voice_profile', {})

    def clear(self) -> None:
        """Clear cache."""
        logger.info(f"🧹 Clearing CAG cache (was: {self.current_persona_id})")
        self.current_persona_id = None
        self.loaded_data = {}
        self.current_size_bytes = 0

    def get_metrics(self) -> Dict:
        """Get cache metrics."""
        return {
            "current_persona": self.current_persona_id,
            "size_used_bytes": self.current_size_bytes,
            "size_used_mb": round(self.current_size_bytes / (1024 * 1024), 3),
            "size_limit_bytes": self.max_size_bytes,
            "size_limit_mb": round(self.max_size_bytes / (1024 * 1024), 1),
            "usage_percent": round((self.current_size_bytes / self.max_size_bytes) * 100, 2),
            "available_bytes": self.max_size_bytes - self.current_size_bytes,
            "available_mb": round((self.max_size_bytes - self.current_size_bytes) / (1024 * 1024), 3)
        }


class PersonaService:
    """Service for managing critic personas."""

    def __init__(self):
        """Initialize persona service."""
        self.personas_dir = Path(__file__).parent.parent / "data" / "personas"
        self.personas: Dict[str, PersonaProfile] = {}
        self.cag_cache = CAGCache(max_size_mb=10.0)
        self._load_personas()

    def _load_personas(self) -> None:
        """Load all persona profiles from JSON files."""
        if not self.personas_dir.exists():
            logger.warning(f"⚠️  Personas directory not found: {self.personas_dir}")
            return

        for persona_file in self.personas_dir.glob("*.json"):
            try:
                with open(persona_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    persona = PersonaProfile(**data)
                    self.personas[persona.id] = persona
                    logger.info(f"📚 Loaded persona: {persona.name}")
            except Exception as e:
                logger.error(f"❌ Failed to load persona from {persona_file}: {e}")

        logger.info(f"✅ Loaded {len(self.personas)} personas")

    def list_personas(self) -> List[Dict]:
        """
        List all available personas.

        Returns:
            List of persona summaries
        """
        return [
            {
                "id": p.id,
                "name": p.name,
                "title": p.title,
                "years_active": p.years_active,
                "publication": p.publication
            }
            for p in self.personas.values()
        ]

    def get_persona(self, persona_id: str) -> Optional[PersonaProfile]:
        """
        Get persona by ID.

        Args:
            persona_id: Persona identifier

        Returns:
            Persona profile or None
        """
        return self.personas.get(persona_id)

    def load_persona_to_cache(self, persona_id: str) -> Dict:
        """
        Load persona into CAG cache.

        Args:
            persona_id: Persona to load

        Returns:
            Cache metrics after loading
        """
        persona = self.get_persona(persona_id)
        if not persona:
            raise ValueError(f"Persona not found: {persona_id}")

        self.cag_cache.load_persona(persona)
        return self.cag_cache.get_metrics()

    def get_current_persona_prompt(self) -> Optional[str]:
        """Get MCP system prompt for currently loaded persona."""
        return self.cag_cache.get_system_prompt()

    def get_current_persona_context(self) -> Dict:
        """Get full context for currently loaded persona."""
        return {
            "system_prompt": self.cag_cache.get_system_prompt(),
            "sample_reviews": self.cag_cache.get_sample_reviews(),
            "voice_profile": self.cag_cache.get_voice_profile()
        }

    def clear_cache(self) -> Dict:
        """
        Clear CAG cache.

        Returns:
            Cache metrics after clearing
        """
        self.cag_cache.clear()
        return self.cag_cache.get_metrics()

    def get_cache_metrics(self) -> Dict:
        """Get current cache metrics."""
        return self.cag_cache.get_metrics()


# Singleton instance
_persona_service: Optional[PersonaService] = None


def get_persona_service() -> PersonaService:
    """Get persona service singleton."""
    global _persona_service
    if _persona_service is None:
        _persona_service = PersonaService()
    return _persona_service
