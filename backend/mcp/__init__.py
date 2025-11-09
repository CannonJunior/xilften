"""
MCP (Model Context Protocol) tools for XILFTEN.

Custom tools that enhance AI responses with domain-specific functionality.
"""

from .movie_detector import MovieNameDetector
from .criteria_analyzer import MovieCriteriaAnalyzer, get_criteria_analyzer

__all__ = ["MovieNameDetector", "MovieCriteriaAnalyzer", "get_criteria_analyzer"]
