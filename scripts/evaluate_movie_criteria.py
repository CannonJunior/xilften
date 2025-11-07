#!/usr/bin/env python3
"""
Movie Criteria Evaluation Script

Uses Ollama LLM to evaluate movies on three criteria:
- Storytelling (0-10)
- Characters (0-10)
- Cohesive Vision (0-10)

This script is designed to be easily reusable with customizable prompts.
"""

import requests
import json
import duckdb
import time
import sys
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime


# ============================================================================
# CONFIGURATION - Modify these to customize evaluation
# ============================================================================

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:3b"

# System prompt that defines the evaluation task
SYSTEM_PROMPT = """You are an expert film critic and analyst. Your task is to evaluate movies on three specific criteria, rating each from 0-10.

**Criteria Definitions:**

1. **Storytelling (0-10)**: Narrative structure, plot coherence, pacing, story arc, emotional impact through narrative
   - 0-3: Poor/incoherent story
   - 4-6: Functional but unremarkable
   - 7-8: Strong, well-crafted narrative
   - 9-10: Masterful storytelling

2. **Characters (0-10)**: Character development, depth, believability, memorable performances, emotional connection
   - 0-3: Flat/forgettable characters
   - 4-6: Adequate character work
   - 7-8: Well-developed, engaging characters
   - 9-10: Iconic, deeply realized characters

3. **Cohesive Vision (0-10)**: Visual style, thematic consistency, directorial vision, world-building, artistic unity
   - 0-3: Inconsistent or lacking vision
   - 4-6: Competent but generic
   - 7-8: Strong, distinctive style
   - 9-10: Visionary, groundbreaking

Respond ONLY with three numbers separated by commas, in this exact format: storytelling,characters,vision
Example: 8.5,7.0,9.2"""

# Movie-specific prompt template
# Available variables: {title}, {year}, {overview}, {genres}, {director}, {runtime}
MOVIE_PROMPT_TEMPLATE = """Evaluate this movie:

Title: {title} ({year})
Director: {director}
Genres: {genres}
Runtime: {runtime} minutes

Overview: {overview}

Rate this movie on the three criteria (storytelling, characters, cohesive_vision).
Respond with only three numbers separated by commas."""

# Database configuration
DATABASE_PATH = "./database/xilften.duckdb"

# Processing options
BATCH_SIZE = 10  # Number of movies to process before saving progress
DELAY_BETWEEN_REQUESTS = 0.5  # Seconds to wait between API calls
MAX_RETRIES = 3  # Number of times to retry failed requests


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def call_ollama(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """
    Call Ollama API with a prompt.

    Args:
        prompt: The user prompt
        system_prompt: System prompt defining the task

    Returns:
        str: Model response
    """
    url = f"{OLLAMA_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # Lower temperature for more consistent scoring
            "top_p": 0.9,
        }
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    result = response.json()
    return result.get("response", "").strip()


def parse_scores(response: str) -> Optional[Tuple[float, float, float]]:
    """
    Parse LLM response to extract three scores.

    Args:
        response: LLM response text

    Returns:
        Tuple of (storytelling, characters, vision) or None if parsing fails
    """
    # Try to find three comma-separated numbers
    # Pattern matches: "8.5,7.0,9.2" or "8.5, 7.0, 9.2" etc.
    pattern = r'(\d+\.?\d*)\s*,\s*(\d+\.?\d*)\s*,\s*(\d+\.?\d*)'
    match = re.search(pattern, response)

    if match:
        try:
            storytelling = float(match.group(1))
            characters = float(match.group(2))
            vision = float(match.group(3))

            # Validate scores are in range 0-10
            if all(0 <= score <= 10 for score in [storytelling, characters, vision]):
                return (storytelling, characters, vision)
        except ValueError:
            pass

    return None


def evaluate_movie(movie: Dict, retry_count: int = 0) -> Optional[Tuple[float, float, float]]:
    """
    Evaluate a single movie using LLM.

    Args:
        movie: Movie data dictionary
        retry_count: Current retry attempt

    Returns:
        Tuple of scores or None if evaluation fails
    """
    # Extract movie information
    title = movie.get('title', 'Unknown')
    year = movie.get('release_date', 'N/A')[:4] if movie.get('release_date') else 'N/A'
    overview = movie.get('overview', 'No overview available')
    genres = ', '.join(movie.get('genres', []))
    runtime = movie.get('runtime', 'Unknown')

    # Extract director from custom_fields
    custom_fields = json.loads(movie.get('custom_fields', '{}')) if isinstance(movie.get('custom_fields'), str) else movie.get('custom_fields', {})
    tmdb_data = custom_fields.get('tmdb_data', {})
    director = tmdb_data.get('director', 'Unknown')

    # Build prompt
    prompt = MOVIE_PROMPT_TEMPLATE.format(
        title=title,
        year=year,
        director=director,
        genres=genres if genres else 'Unknown',
        runtime=runtime,
        overview=overview[:500]  # Limit overview length
    )

    try:
        # Call LLM
        response = call_ollama(prompt)
        print(f"  LLM response: {response}")

        # Parse scores
        scores = parse_scores(response)

        if scores:
            return scores
        else:
            print(f"  ⚠️  Failed to parse scores from response: {response}")
            if retry_count < MAX_RETRIES:
                print(f"  🔄 Retrying... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(1)
                return evaluate_movie(movie, retry_count + 1)
            return None

    except Exception as e:
        print(f"  ❌ Error evaluating movie: {e}")
        if retry_count < MAX_RETRIES:
            print(f"  🔄 Retrying... (attempt {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(2)
            return evaluate_movie(movie, retry_count + 1)
        return None


def update_movie_scores(conn, movie_id: str, storytelling: float, characters: float, vision: float):
    """
    Update movie scores in database.

    Args:
        conn: Database connection
        movie_id: Movie UUID
        storytelling: Storytelling score
        characters: Characters score
        vision: Cohesive vision score
    """
    # Get current custom_fields
    result = conn.execute(
        "SELECT custom_fields FROM media WHERE id = ?",
        [movie_id]
    ).fetchone()

    if result:
        custom_fields = json.loads(result[0]) if result[0] else {}

        # Update scores
        custom_fields['storytelling'] = round(storytelling, 1)
        custom_fields['characters'] = round(characters, 1)
        custom_fields['cohesive_vision'] = round(vision, 1)

        # Update in database
        conn.execute("""
            UPDATE media
            SET custom_fields = json_merge_patch(
                COALESCE(custom_fields, '{}')::JSON,
                ?::JSON
            )::VARCHAR,
            updated_at = ?
            WHERE id = ?
        """, [
            json.dumps(custom_fields),
            datetime.now().isoformat(),
            movie_id
        ])


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("=" * 80)
    print("🎬 Movie Criteria Evaluation Script")
    print("=" * 80)
    print(f"Model: {OLLAMA_MODEL}")
    print(f"Database: {DATABASE_PATH}")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    # Check if we should process all or specific movies
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            print(f"📊 Processing first {limit} movies")
        except ValueError:
            print("⚠️  Invalid limit argument, processing all movies")
    else:
        print("📊 Processing all movies")

    print()

    # Connect to database
    print("🔌 Connecting to database...")
    conn = duckdb.connect(DATABASE_PATH)

    # Fetch movies
    query = """
        SELECT id, title, release_date, overview, runtime, custom_fields
        FROM media
        WHERE media_type = 'movie'
        ORDER BY title
    """

    if limit:
        query += f" LIMIT {limit}"

    movies = conn.execute(query).fetchall()

    print(f"✅ Found {len(movies)} movies to evaluate\n")

    # Process movies
    successful = 0
    failed = 0
    skipped = 0

    for i, movie_data in enumerate(movies, 1):
        movie_id, title, release_date, overview, runtime, custom_fields_raw = movie_data

        # Parse custom fields to check genres
        custom_fields = json.loads(custom_fields_raw) if custom_fields_raw else {}

        # Build movie dict
        movie = {
            'id': movie_id,
            'title': title,
            'release_date': release_date,
            'overview': overview,
            'runtime': runtime,
            'custom_fields': custom_fields,
            'genres': []  # Would need to join with genres table for accurate data
        }

        print(f"[{i}/{len(movies)}] Evaluating: {title}")

        # Evaluate
        scores = evaluate_movie(movie)

        if scores:
            storytelling, characters, vision = scores
            print(f"  ✅ Scores: S={storytelling}, C={characters}, V={vision}")

            # Update database
            update_movie_scores(conn, movie_id, storytelling, characters, vision)
            successful += 1
        else:
            print(f"  ❌ Failed to evaluate")
            failed += 1

        # Rate limiting
        if i < len(movies):
            time.sleep(DELAY_BETWEEN_REQUESTS)

        # Progress checkpoint
        if i % BATCH_SIZE == 0:
            print(f"\n📊 Progress: {i}/{len(movies)} movies processed")
            print(f"   ✅ Successful: {successful}")
            print(f"   ❌ Failed: {failed}")
            print()

    # Final summary
    print("\n" + "=" * 80)
    print("🎉 Evaluation Complete!")
    print("=" * 80)
    print(f"✅ Successfully evaluated: {successful} movies")
    print(f"❌ Failed: {failed} movies")
    print(f"📊 Total processed: {len(movies)} movies")
    print()

    conn.close()


if __name__ == "__main__":
    main()
