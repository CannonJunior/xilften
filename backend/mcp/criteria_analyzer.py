"""
MCP Tool: Movie Criteria Analyzer

Analyzes movies and generates three criteria scores:
- Storytelling (0-10): Plot structure, narrative coherence, pacing
- Characters (0-10): Character development, depth, relationships
- Cohesive Vision (0-10): Visual style, thematic consistency, directorial vision
"""

import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class MovieCriteriaAnalyzer:
    """
    Analyzes movies to generate 3D criteria scores using AI-powered analysis.
    """

    def __init__(self, ollama_client):
        """
        Initialize the criteria analyzer.

        Args:
            ollama_client: Ollama client for AI inference
        """
        self.ollama = ollama_client
        self.model = "llama3.2:latest"

    async def analyze_movie(
        self,
        title: str,
        overview: Optional[str] = None,
        genres: Optional[list] = None,
        release_year: Optional[int] = None,
        tmdb_rating: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Analyze a movie and generate criteria scores.

        Args:
            title: Movie title
            overview: Movie overview/description
            genres: List of genres
            release_year: Year of release
            tmdb_rating: TMDB rating

        Returns:
            Dict with storytelling, characters, and cohesive_vision scores (0-10)
        """
        try:
            prompt = self._build_analysis_prompt(
                title, overview, genres, release_year, tmdb_rating
            )

            response = await self.ollama.chat(
                user_message=prompt,
                model=self.model,
                temperature=0.3  # Lower temperature for more consistent scoring
            )

            scores = self._parse_scores(response or "")

            logger.info(f"✅ Analyzed '{title}': S={scores['storytelling']}, "
                       f"C={scores['characters']}, V={scores['cohesive_vision']}")

            return scores

        except Exception as e:
            logger.error(f"❌ Error analyzing movie '{title}': {e}")
            # Return default middle-range scores on error
            return {
                "storytelling": 5.0,
                "characters": 5.0,
                "cohesive_vision": 5.0
            }

    def _build_analysis_prompt(
        self,
        title: str,
        overview: Optional[str],
        genres: Optional[list],
        release_year: Optional[int],
        tmdb_rating: Optional[float]
    ) -> str:
        """
        Build the analysis prompt for the AI.

        Args:
            title: Movie title
            overview: Movie overview
            genres: List of genres
            release_year: Year of release
            tmdb_rating: TMDB rating

        Returns:
            Analysis prompt string
        """
        prompt = f"""You are a film critic analyzing movies across three criteria. Rate the following movie on a scale of 0-10 for each criterion.

**Movie Information:**
- Title: {title}
- Year: {release_year or 'Unknown'}
- Genres: {', '.join(genres) if genres else 'Unknown'}
- Rating: {tmdb_rating or 'Unknown'}/10
- Overview: {overview or 'No overview available'}

**Criteria Definitions:**

1. **Storytelling (0-10)**: Rate the plot structure, narrative coherence, pacing, and story quality.
   - 0-2: Weak or incoherent plot
   - 3-4: Basic but flawed storytelling
   - 5-6: Solid, competent narrative
   - 7-8: Strong, engaging story
   - 9-10: Masterful storytelling

2. **Characters (0-10)**: Rate character development, depth, relationships, and performances.
   - 0-2: Flat, underdeveloped characters
   - 3-4: Basic characterization
   - 5-6: Well-defined characters
   - 7-8: Deep, compelling characters
   - 9-10: Iconic, transformative characters

3. **Cohesive Vision (0-10)**: Rate visual style, thematic consistency, directorial vision, and artistic coherence.
   - 0-2: Inconsistent or generic
   - 3-4: Some visual identity
   - 5-6: Clear visual style
   - 7-8: Strong artistic vision
   - 9-10: Iconic, revolutionary vision

**Instructions:**
Based on your knowledge of this film, provide scores for each criterion. Consider the film's genre, era, and reputation when scoring. Be objective and consistent.

**Response Format (JSON only, no explanation):**
{{
  "storytelling": X.X,
  "characters": X.X,
  "cohesive_vision": X.X,
  "reasoning": "Brief 1-2 sentence justification"
}}

Respond with ONLY the JSON object, nothing else."""

        return prompt

    def _parse_scores(self, response_text: str) -> Dict[str, float]:
        """
        Parse AI response to extract scores.

        Args:
            response_text: Raw AI response

        Returns:
            Dict with parsed scores
        """
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")

            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)

            # Validate and clamp scores
            scores = {
                "storytelling": self._clamp_score(data.get("storytelling", 5.0)),
                "characters": self._clamp_score(data.get("characters", 5.0)),
                "cohesive_vision": self._clamp_score(data.get("cohesive_vision", 5.0))
            }

            return scores

        except Exception as e:
            logger.warning(f"⚠️  Failed to parse scores: {e}. Using heuristic.")
            return self._heuristic_scores(response_text)

    def _heuristic_scores(self, response_text: str) -> Dict[str, float]:
        """
        Generate heuristic scores if parsing fails.

        Args:
            response_text: AI response text

        Returns:
            Dict with heuristic scores
        """
        # Look for numbers in the response
        import re
        numbers = re.findall(r'\d+\.?\d*', response_text)

        if len(numbers) >= 3:
            return {
                "storytelling": self._clamp_score(float(numbers[0])),
                "characters": self._clamp_score(float(numbers[1])),
                "cohesive_vision": self._clamp_score(float(numbers[2]))
            }

        # Default to middle scores
        return {
            "storytelling": 5.0,
            "characters": 5.0,
            "cohesive_vision": 5.0
        }

    def _clamp_score(self, score: float) -> float:
        """
        Clamp score to 0-10 range.

        Args:
            score: Raw score

        Returns:
            Clamped score (0-10)
        """
        return max(0.0, min(10.0, float(score)))


# Global instance getter
_analyzer_instance = None


def get_criteria_analyzer(ollama_client) -> MovieCriteriaAnalyzer:
    """
    Get or create the global criteria analyzer instance.

    Args:
        ollama_client: Ollama client

    Returns:
        MovieCriteriaAnalyzer instance
    """
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = MovieCriteriaAnalyzer(ollama_client)
    return _analyzer_instance
