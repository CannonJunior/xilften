"""
Movie Name Detector MCP Tool

Automatically detects movie names in AI Assistant responses and enriches them
with visual indicators (icons/images).
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from config.database import db_manager

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

    def _find_movie_mentions(self, text: str) -> List[Tuple[str, Dict[str, str], int, int]]:
        """
        Find all movie title mentions in the text.

        Args:
            text (str): Input text to scan

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
