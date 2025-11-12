#!/usr/bin/env python3
"""
Test Movie Context Validation

Tests the context-aware movie detection to ensure it correctly identifies
when a movie name mention actually refers to the movie vs. a coincidental match.

Usage:
    python scripts/test_movie_context_validation.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.mcp.movie_detector import get_movie_detector
import logging

# Configure logging to see debug output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_context_validation():
    """Run test cases for context validation."""

    detector = get_movie_detector()

    test_cases = [
        {
            'name': 'Bob Hope (person) - should NOT match movie "Hope"',
            'text': 'Bob Hope was a comedy star who entertained troops during World War II.',
            'expected_matches': 0,
            'description': 'Person name, not the movie'
        },
        {
            'name': 'Movie "Hope" - should match',
            'text': 'I really enjoyed watching the movie Hope. It was very inspiring.',
            'expected_matches': 1,
            'description': 'Clearly referring to a movie'
        },
        {
            'name': 'The Matrix reference - should match',
            'text': 'The Matrix is one of the best sci-fi films ever made.',
            'expected_matches': 1,
            'description': 'Famous movie name'
        },
        {
            'name': 'Matrix as math term - should NOT match',
            'text': 'Calculate the determinant of the matrix using row reduction.',
            'expected_matches': 0,
            'description': 'Mathematical term, not the movie'
        },
        {
            'name': 'Blade Runner reference - should match',
            'text': 'Blade Runner is a neo-noir masterpiece with incredible visuals.',
            'expected_matches': 1,
            'description': 'Clear movie reference'
        },
        {
            'name': 'General hope concept - should NOT match',
            'text': 'I have hope that things will get better soon.',
            'expected_matches': 0,
            'description': 'Abstract concept, not the movie'
        },
        {
            'name': 'Multiple movie mentions - should match both',
            'text': 'My favorite films are The Matrix and Blade Runner. They defined the cyberpunk genre.',
            'expected_matches': 2,
            'description': 'Multiple valid movie references'
        }
    ]

    print("=" * 80)
    print("MOVIE CONTEXT VALIDATION TEST")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for test in test_cases:
        print(f"Test: {test['name']}")
        print(f"Text: \"{test['text']}\"")
        print(f"Description: {test['description']}")
        print(f"Expected matches: {test['expected_matches']}")

        # Run detection with context validation
        matches = detector._find_movie_mentions(test['text'], validate_context=True)

        actual_matches = len(matches)
        print(f"Actual matches: {actual_matches}")

        if matches:
            for matched_text, movie_data, start, end in matches:
                print(f"  → Detected: '{matched_text}' ({movie_data['title']} - {movie_data['media_type']})")

        # Check if test passed
        if actual_matches == test['expected_matches']:
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
            failed += 1

        print()
        print("-" * 80)
        print()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = test_context_validation()
    sys.exit(exit_code)
