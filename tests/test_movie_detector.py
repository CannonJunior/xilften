"""
Unit tests for MovieNameDetector MCP tool
"""

import pytest
from backend.mcp.movie_detector import MovieNameDetector


class TestMovieNameDetector:
    """Test cases for movie name detection and enrichment."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = MovieNameDetector()

    def test_enrich_response_no_movies(self):
        """
        Test that text without movie names is returned unchanged.
        """
        text = "This is a test sentence with no movie names."
        result = self.detector.enrich_response(text)
        assert result == text

    def test_enrich_response_single_movie(self):
        """
        Test detection of a single movie name.
        """
        # Assuming "Blade Runner" is in the database
        text = "I really enjoyed watching Blade Runner last night."
        result = self.detector.enrich_response(text)

        # Should contain movie icon before Blade Runner
        assert "🎬 Blade Runner" in result
        assert result.startswith("I really enjoyed watching 🎬")

    def test_enrich_response_multiple_movies(self):
        """
        Test detection of multiple movie names.
        """
        text = "Blade Runner and The Matrix are both great sci-fi films."
        result = self.detector.enrich_response(text)

        # Should have icons before both movies
        assert "🎬 Blade Runner" in result
        assert "🎬 The Matrix" in result

    def test_enrich_response_case_insensitive(self):
        """
        Test that movie detection is case-insensitive.
        """
        text = "blade runner is a classic film."
        result = self.detector.enrich_response(text)

        # Should still detect "blade runner" despite lowercase
        assert "🎬" in result

    def test_enrich_response_with_metadata(self):
        """
        Test enrichment with metadata return.
        """
        text = "I recommend Blade Runner for sci-fi fans."
        result = self.detector.enrich_response_with_metadata(text)

        # Check structure
        assert "enriched_text" in result
        assert "detected_movies" in result
        assert "detection_count" in result

        # Check enriched text has icon
        assert "🎬 Blade Runner" in result["enriched_text"]

        # Check metadata
        if result["detection_count"] > 0:
            assert len(result["detected_movies"]) == result["detection_count"]
            movie = result["detected_movies"][0]
            assert "movie_id" in movie
            assert "title" in movie
            assert "poster_path" in movie

    def test_no_overlapping_matches(self):
        """
        Test that overlapping movie titles don't create duplicate icons.
        """
        # If database contains both "The Matrix" and "Matrix"
        text = "The Matrix is a groundbreaking film."
        result = self.detector.enrich_response(text)

        # Should only have one icon (for the longer title)
        icon_count = result.count("🎬")
        assert icon_count == 1

    def test_refresh_cache(self):
        """
        Test cache refresh functionality.
        """
        # Initial load
        self.detector._load_movie_titles()
        initial_cache = self.detector._movie_titles_cache

        # Refresh
        self.detector.refresh_cache()
        refreshed_cache = self.detector._movie_titles_cache

        # Both should be lists (content may be same)
        assert isinstance(initial_cache, list)
        assert isinstance(refreshed_cache, list)

    def test_empty_text(self):
        """
        Test handling of empty text.
        """
        text = ""
        result = self.detector.enrich_response(text)
        assert result == ""

    def test_text_with_punctuation(self):
        """
        Test movie detection with surrounding punctuation.
        """
        text = "Have you seen Blade Runner? It's amazing!"
        result = self.detector.enrich_response(text)

        # Should detect movie name even with punctuation
        assert "🎬 Blade Runner" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
