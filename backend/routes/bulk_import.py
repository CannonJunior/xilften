"""
Bulk Import Routes
API endpoints for bulk importing media from external sources
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import random
import requests
import re
import json
from datetime import datetime
import logging

from config.database import DatabaseManager

db_manager = DatabaseManager()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bulk", tags=["bulk-import"])


class TMDBMovieImport(BaseModel):
    """Movie data from TMDB for bulk import"""
    tmdb_id: int
    imdb_id: Optional[str] = None
    title: str
    original_title: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    tmdb_rating: Optional[float] = None
    tmdb_vote_count: Optional[int] = None
    popularity: Optional[float] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    original_language: Optional[str] = None
    status: Optional[str] = None
    genres: List[str] = []
    tmdb_data: Dict = {}


def generate_3d_scores(movie: TMDBMovieImport) -> tuple:
    """Generate reasonable 3D criteria scores based on rating and genre"""
    base_rating = float(movie.tmdb_rating or 7.0)

    # Base scores from TMDB rating (normalized to 0-10)
    base_score = (base_rating - 5) * 2  # Convert 5-10 rating to 0-10 score

    # Add some variance for each dimension
    storytelling = max(0, min(10, base_score + random.uniform(-1.5, 1.5)))
    characters = max(0, min(10, base_score + random.uniform(-1.5, 1.5)))
    cohesive_vision = max(0, min(10, base_score + random.uniform(-1.5, 1.5)))

    # Genre-based adjustments
    genres = movie.genres
    if 'Drama' in genres:
        characters += 0.5
        storytelling += 0.3
    if 'Science Fiction' in genres:
        cohesive_vision += 0.8
    if 'Animation' in genres:
        cohesive_vision += 0.7
    if 'Action' in genres:
        cohesive_vision += 0.4
    if 'Thriller' in genres or 'Crime' in genres:
        storytelling += 0.5

    # Clamp final values
    storytelling = round(max(0, min(10, storytelling)), 1)
    characters = round(max(0, min(10, characters)), 1)
    cohesive_vision = round(max(0, min(10, cohesive_vision)), 1)

    return storytelling, characters, cohesive_vision


@router.post("/import-tmdb-movies")
async def import_tmdb_movies(movies: List[TMDBMovieImport]):
    """
    Bulk import movies from TMDB data

    Args:
        movies: List of movie data from TMDB

    Returns:
        dict: Summary of import results
    """
    try:
        conn = db_manager.get_duckdb_connection()

        # Get existing movie IDs to avoid duplicates
        existing = conn.execute(
            "SELECT tmdb_id FROM media WHERE tmdb_id IS NOT NULL"
        ).fetchall()
        existing_ids = {row[0] for row in existing}

        # Filter out existing movies
        new_movies = [m for m in movies if m.tmdb_id not in existing_ids]

        inserted_count = 0
        skipped_count = len(movies) - len(new_movies)
        errors = []

        for movie in new_movies:
            try:
                # Generate UUID
                movie_id = str(uuid.uuid4())

                # Generate 3D scores
                storytelling, characters, cohesive_vision = generate_3d_scores(movie)

                # Build custom fields
                custom_fields = {
                    'storytelling': storytelling,
                    'characters': characters,
                    'cohesive_vision': cohesive_vision,
                    'tmdb_data': movie.tmdb_data
                }

                # Insert movie
                conn.execute("""
                    INSERT INTO media (
                        id, tmdb_id, imdb_id, title, original_title, media_type,
                        release_date, runtime, overview, tagline, tmdb_rating,
                        tmdb_vote_count, popularity_score, poster_path, backdrop_path,
                        original_language, status, custom_fields, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    movie_id,
                    movie.tmdb_id,
                    movie.imdb_id,
                    movie.title,
                    movie.original_title,
                    'movie',
                    movie.release_date,
                    movie.runtime,
                    movie.overview,
                    movie.tagline,
                    str(movie.tmdb_rating) if movie.tmdb_rating else None,
                    movie.tmdb_vote_count,
                    movie.popularity,
                    movie.poster_path,
                    movie.backdrop_path,
                    movie.original_language,
                    movie.status,
                    conn.execute("SELECT ?::JSON", [custom_fields]).fetchone()[0],
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ])

                # Insert genres
                for genre_name in movie.genres:
                    try:
                        # Find genre ID
                        genre_result = conn.execute(
                            "SELECT id FROM genres WHERE name = ?",
                            [genre_name.lower()]
                        ).fetchone()

                        if genre_result:
                            genre_id = genre_result[0]
                            conn.execute("""
                                INSERT INTO media_genres (media_id, genre_id)
                                VALUES (?, ?)
                            """, [movie_id, genre_id])
                    except Exception:
                        # Genre might not exist in taxonomy, skip
                        pass

                inserted_count += 1

                if inserted_count % 10 == 0:
                    logger.info(f"Inserted {inserted_count}/{len(new_movies)} movies...")

            except Exception as e:
                error_msg = f"{movie.title}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Error inserting movie: {error_msg}")

        return {
            "success": True,
            "data": {
                "total_submitted": len(movies),
                "inserted": inserted_count,
                "skipped": skipped_count,
                "errors": len(errors),
                "error_details": errors[:10]  # Return first 10 errors
            }
        }

    except Exception as e:
        logger.error(f"Bulk import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LLM EVALUATION ENDPOINT
# ============================================================================

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:3b"

EVALUATION_SYSTEM_PROMPT = """You are an expert film critic and analyst. Your task is to evaluate movies on three specific criteria, rating each from 0-10.

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


def call_ollama_for_evaluation(prompt: str) -> str:
    """Call Ollama API for movie evaluation"""
    url = f"{OLLAMA_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": EVALUATION_SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
        }
    }

    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()

    result = response.json()
    return result.get("response", "").strip()


def parse_evaluation_scores(response: str) -> Optional[tuple]:
    """Parse LLM response to extract three scores"""
    pattern = r'(\d+\.?\d*)\s*,\s*(\d+\.?\d*)\s*,\s*(\d+\.?\d*)'
    match = re.search(pattern, response)

    if match:
        try:
            storytelling = float(match.group(1))
            characters = float(match.group(2))
            vision = float(match.group(3))

            if all(0 <= score <= 10 for score in [storytelling, characters, vision]):
                return (storytelling, characters, vision)
        except ValueError:
            pass

    return None


@router.post("/evaluate-criteria")
async def evaluate_movie_criteria(
    background_tasks: BackgroundTasks,
    limit: Optional[int] = None
):
    """
    Evaluate movies using LLM to generate 3D criteria scores

    Args:
        limit: Optional limit on number of movies to evaluate (for testing)

    Returns:
        dict: Summary of evaluation task
    """
    try:
        conn = db_manager.get_duckdb_connection()

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

        logger.info(f"Starting evaluation of {len(movies)} movies")

        # Process movies in background
        def evaluate_movies_task():
            successful = 0
            failed = 0

            for movie_data in movies:
                movie_id, title, release_date, overview, runtime, custom_fields_raw = movie_data

                try:
                    # Parse custom fields
                    custom_fields = json.loads(custom_fields_raw) if custom_fields_raw else {}
                    tmdb_data = custom_fields.get('tmdb_data', {})

                    # Build evaluation prompt
                    year = str(release_date)[:4] if release_date else 'N/A'
                    director = tmdb_data.get('director', 'Unknown')

                    prompt = f"""Evaluate this movie:

Title: {title} ({year})
Director: {director}
Runtime: {runtime} minutes

Overview: {overview[:500] if overview else 'No overview available'}

Rate this movie on the three criteria (storytelling, characters, cohesive_vision).
Respond with only three numbers separated by commas."""

                    # Call LLM
                    response = call_ollama_for_evaluation(prompt)
                    scores = parse_evaluation_scores(response)

                    if scores:
                        storytelling, characters, vision = scores

                        # Update scores
                        custom_fields['storytelling'] = round(storytelling, 1)
                        custom_fields['characters'] = round(characters, 1)
                        custom_fields['cohesive_vision'] = round(vision, 1)

                        # Update in database
                        conn = db_manager.get_duckdb_connection()
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

                        successful += 1
                        logger.info(f"✅ {title}: S={storytelling}, C={characters}, V={vision}")
                    else:
                        failed += 1
                        logger.warning(f"❌ Failed to parse scores for {title}: {response}")

                except Exception as e:
                    failed += 1
                    logger.error(f"Error evaluating {title}: {e}")

            logger.info(f"Evaluation complete: {successful} successful, {failed} failed")

        # Start background task
        background_tasks.add_task(evaluate_movies_task)

        return {
            "success": True,
            "data": {
                "message": "Evaluation started in background",
                "total_movies": len(movies),
                "note": "Check server logs for progress"
            }
        }

    except Exception as e:
        logger.error(f"Failed to start evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
