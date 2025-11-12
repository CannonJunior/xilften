"""
Movie Name Detector MCP Tool

Automatically detects movie names in AI Assistant responses and enriches them
with visual indicators (icons/images).
"""

import re
import logging
import json
import asyncio
from typing import List, Dict, Tuple, Optional
from config.database import db_manager
from backend.services.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class MovieNameDetector:
    """
    MCP tool that detects movie names in text and adds visual indicators.

    This tool:
    1. Loads all movie titles from the database into memory (cached)
    2. Scans AI response text for any movie name matches
    3. Adds a movie icon (🎬) before each detected movie name
    4. Prepares for future enhancement: adding poster thumbnails
    """

    # Movie icon to insert before detected movie names
    MOVIE_ICON = "🎬"

    def __init__(self):
        """
        Initialize the movie detector.
        """
        self._movie_titles_cache: Optional[List[Dict[str, str]]] = None
        self._cache_loaded = False
        self._ollama_client = OllamaClient()

    def _load_movie_titles(self) -> List[Dict[str, str]]:
        """
        Load all movie titles from the database.

        Returns:
            List[Dict[str, str]]: List of dicts with 'title', 'id', 'poster_path'
        """
        if self._cache_loaded and self._movie_titles_cache is not None:
            return self._movie_titles_cache

        try:
            conn = db_manager.get_duckdb_connection()

            # Query all media titles from the database
            query = """
                SELECT
                    id,
                    title,
                    original_title,
                    poster_path,
                    media_type
                FROM media
                WHERE media_type IN ('movie', 'tv', 'anime', 'documentary')
                ORDER BY LENGTH(title) DESC
            """

            result = conn.execute(query).fetchall()

            # Build cache with title variations
            self._movie_titles_cache = []
            for row in result:
                media_id, title, original_title, poster_path, media_type = row

                # Add main title
                self._movie_titles_cache.append({
                    'title': title,
                    'id': media_id,
                    'poster_path': poster_path,
                    'media_type': media_type
                })

                # Add original title if different
                if original_title and original_title != title:
                    self._movie_titles_cache.append({
                        'title': original_title,
                        'id': media_id,
                        'poster_path': poster_path,
                        'media_type': media_type
                    })

            self._cache_loaded = True
            logger.info(f"📊 Loaded {len(self._movie_titles_cache)} movie titles into cache")

            return self._movie_titles_cache

        except Exception as e:
            logger.error(f"❌ Failed to load movie titles: {e}")
            return []

    def refresh_cache(self):
        """
        Force refresh the movie titles cache.

        Call this when new movies are added to the database.
        """
        self._cache_loaded = False
        self._movie_titles_cache = None
        self._load_movie_titles()
        logger.info("🔄 Movie titles cache refreshed")

    def _validate_context(self, matched_text: str, surrounding_context: str,
                          movie_title: str, media_type: str) -> bool:
        """
        Use LLM to validate if the matched text actually refers to the movie/show.

        Args:
            matched_text (str): The text that matched the movie title
            surrounding_context (str): The full sentence or paragraph containing the match
            movie_title (str): The official movie/show title from database
            media_type (str): Type of media (movie, tv, anime, documentary)

        Returns:
            bool: True if valid movie reference, False if coincidental match
        """
        # Build context-aware prompt
        media_type_label = {
            'movie': 'movie',
            'tv': 'TV series',
            'anime': 'anime series',
            'documentary': 'documentary'
        }.get(media_type, 'media')

        user_message = f"""You are analyzing whether a text mention refers to a specific {media_type_label}.

Movie/Show Title: "{movie_title}"
Matched Text in Context: "{matched_text}"
Full Context: "{surrounding_context}"

Question: Does the matched text "{matched_text}" in this context actually refer to the {media_type_label} titled "{movie_title}"?

Consider:
- Is this referring to a person's name rather than the {media_type_label}?
- Is this referring to a concept, place, or other entity?
- Is the context clearly about {media_type_label}s, films, or entertainment?

Answer with ONLY "YES" if it refers to the {media_type_label}, or "NO" if it's a coincidental match.

Answer:"""

        try:
            # Use fast, small model for quick validation
            # Run async call in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    self._ollama_client.chat(
                        user_message=user_message,
                        model="qwen2.5:3b",
                        temperature=0.1,  # Low temperature for consistent yes/no answers
                        max_tokens=10
                    )
                )
            finally:
                loop.close()

            if response is None:
                logger.warning(f"⚠️ No response from LLM for '{matched_text}'")
                return True  # Fail open

            answer = response.strip().upper()
            is_valid = answer.startswith('YES')

            logger.debug(f"🔍 Context validation for '{matched_text}': {answer} -> {is_valid}")
            return is_valid

        except Exception as e:
            logger.warning(f"⚠️ Context validation failed for '{matched_text}': {e}")
            # On error, default to accepting the match (fail open)
            return True

    def _extract_surrounding_context(self, text: str, start: int, end: int,
                                      context_chars: int = 200) -> str:
        """
        Extract surrounding context around a match for validation.

        Args:
            text (str): Full text
            start (int): Match start position
            end (int): Match end position
            context_chars (int): Number of characters to extract on each side

        Returns:
            str: Surrounding context
        """
        # Extract context before and after the match
        context_start = max(0, start - context_chars)
        context_end = min(len(text), end + context_chars)

        context = text[context_start:context_end].strip()
        return context

    def _find_movie_mentions(self, text: str, validate_context: bool = True) -> List[Tuple[str, Dict[str, str], int, int]]:
        """
        Find all movie title mentions in the text.

        Args:
            text (str): Input text to scan
            validate_context (bool): Whether to use LLM to validate context (default: True)

        Returns:
            List of tuples: (matched_title, movie_data, start_pos, end_pos)
        """
        movies = self._load_movie_titles()
        matches = []

        for movie in movies:
            title = movie['title']

            # Create regex pattern that matches the title as a whole word/phrase
            # Case-insensitive, word boundary aware
            pattern = re.compile(
                r'\b' + re.escape(title) + r'\b',
                re.IGNORECASE
            )

            # Find all occurrences
            for match in pattern.finditer(text):
                matches.append((
                    match.group(),  # Matched text (preserves original case)
                    movie,          # Movie data
                    match.start(),  # Start position
                    match.end()     # End position
                ))

        # Sort by position (earliest first) and remove overlaps
        # Longer titles are prioritized due to DESC sort in query
        matches.sort(key=lambda x: x[2])

        # Remove overlapping matches (keep longer/earlier ones)
        filtered_matches = []
        last_end = -1

        for match in matches:
            start = match[2]
            if start >= last_end:
                filtered_matches.append(match)
                last_end = match[3]

        # Validate context using LLM if enabled
        if validate_context and filtered_matches:
            validated_matches = []

            for matched_text, movie_data, start, end in filtered_matches:
                # Extract surrounding context
                context = self._extract_surrounding_context(text, start, end)

                # Validate using LLM
                is_valid = self._validate_context(
                    matched_text=matched_text,
                    surrounding_context=context,
                    movie_title=movie_data['title'],
                    media_type=movie_data['media_type']
                )

                if is_valid:
                    validated_matches.append((matched_text, movie_data, start, end))
                else:
                    logger.info(f"🚫 Filtered out coincidental match: '{matched_text}' in context: \"{context[:50]}...\"")

            return validated_matches

        return filtered_matches

    def enrich_response(self, text: str) -> str:
        """
        Enrich AI response text by adding movie icons before detected movie names.

        Args:
            text (str): Original AI response text

        Returns:
            str: Enriched text with movie icons
        """
        matches = self._find_movie_mentions(text)

        if not matches:
            return text

        # Build enriched text by inserting icons
        enriched_parts = []
        last_pos = 0

        for matched_text, movie_data, start, end in matches:
            # Add text before the match
            enriched_parts.append(text[last_pos:start])

            # Add icon + movie name
            enriched_parts.append(f"{self.MOVIE_ICON} {matched_text}")

            last_pos = end

        # Add remaining text
        enriched_parts.append(text[last_pos:])

        enriched_text = ''.join(enriched_parts)

        logger.info(f"🎬 Detected {len(matches)} movie mentions in response")

        return enriched_text

    def enrich_response_with_metadata(self, text: str) -> Dict[str, any]:
        """
        Enrich AI response and return both enriched text and metadata.

        Args:
            text (str): Original AI response text

        Returns:
            Dict with 'enriched_text' and 'detected_movies' metadata
        """
        matches = self._find_movie_mentions(text)

        # Build enriched text
        enriched_parts = []
        last_pos = 0
        detected_movies = []

        for matched_text, movie_data, start, end in matches:
            # Add text before the match
            enriched_parts.append(text[last_pos:start])

            # Add icon + movie name
            enriched_parts.append(f"{self.MOVIE_ICON} {matched_text}")

            # Collect metadata
            detected_movies.append({
                'matched_text': matched_text,
                'movie_id': movie_data['id'],
                'title': movie_data['title'],
                'poster_path': movie_data['poster_path'],
                'media_type': movie_data['media_type'],
                'position': start
            })

            last_pos = end

        # Add remaining text
        enriched_parts.append(text[last_pos:])

        enriched_text = ''.join(enriched_parts)

        logger.info(f"🎬 Detected {len(detected_movies)} movie mentions in response")

        # Get unique movies for poster gallery
        poster_html = self._generate_poster_gallery_html(detected_movies)

        return {
            'enriched_text': enriched_text,
            'detected_movies': detected_movies,
            'detection_count': len(detected_movies),
            'poster_gallery_html': poster_html
        }

    def _generate_poster_gallery_html(self, detected_movies: List[Dict]) -> str:
        """
        Generate HTML for poster gallery from detected movies.

        Args:
            detected_movies (List[Dict]): List of detected movie metadata

        Returns:
            str: HTML string for poster gallery
        """
        # Get unique movies (deduplicate by movie_id)
        unique_movies = {}
        for movie in detected_movies:
            if movie['movie_id'] not in unique_movies:
                unique_movies[movie['movie_id']] = movie

        if not unique_movies:
            return ''

        # Build HTML
        html_parts = ['<div class="ai-poster-gallery">']

        for movie in unique_movies.values():
            poster_path = movie.get('poster_path')
            if not poster_path:
                continue  # Skip movies without posters

            # TMDB image base URL
            poster_url = f"https://image.tmdb.org/t/p/w200{poster_path}"
            movie_id = movie['movie_id']
            title = movie['title']

            # Create draggable poster HTML
            poster_html = f'''
                <div class="ai-poster-item">
                    <img
                        src="{poster_url}"
                        alt="{title}"
                        class="ai-poster-image media-poster"
                        draggable="true"
                        data-media-id="{movie_id}"
                        data-media-title="{title}"
                    />
                    <div class="ai-poster-title">{title}</div>
                </div>
            '''
            html_parts.append(poster_html)

        html_parts.append('</div>')

        return ''.join(html_parts)


# Global singleton instance
_movie_detector_instance: Optional[MovieNameDetector] = None


def get_movie_detector() -> MovieNameDetector:
    """
    Get the singleton MovieNameDetector instance.

    Returns:
        MovieNameDetector: The detector instance
    """
    global _movie_detector_instance

    if _movie_detector_instance is None:
        _movie_detector_instance = MovieNameDetector()

    return _movie_detector_instance
