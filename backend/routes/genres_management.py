"""
Genre Management Routes

API endpoints for seeding TMDB genres and classifying movies.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import logging
import uuid
from datetime import datetime

from config.database import DatabaseManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/genres-management", tags=["genres-management"])

db_manager = DatabaseManager()

# TMDB Official 19 Genres with TMDB IDs
TMDB_GENRES = [
    {"tmdb_id": 28, "name": "Action"},
    {"tmdb_id": 12, "name": "Adventure"},
    {"tmdb_id": 16, "name": "Animation"},
    {"tmdb_id": 35, "name": "Comedy"},
    {"tmdb_id": 80, "name": "Crime"},
    {"tmdb_id": 99, "name": "Documentary"},
    {"tmdb_id": 18, "name": "Drama"},
    {"tmdb_id": 10751, "name": "Family"},
    {"tmdb_id": 14, "name": "Fantasy"},
    {"tmdb_id": 36, "name": "History"},
    {"tmdb_id": 27, "name": "Horror"},
    {"tmdb_id": 10402, "name": "Music"},
    {"tmdb_id": 9648, "name": "Mystery"},
    {"tmdb_id": 10749, "name": "Romance"},
    {"tmdb_id": 878, "name": "Science Fiction"},
    {"tmdb_id": 53, "name": "Thriller"},
    {"tmdb_id": 10770, "name": "TV Movie"},
    {"tmdb_id": 10752, "name": "War"},
    {"tmdb_id": 37, "name": "Western"}
]


@router.post("/seed-tmdb-genres")
async def seed_tmdb_genres():
    """
    Seed TMDB's official 19 genres into the database.

    Returns:
        dict: Summary of seeding results
    """
    try:
        conn = db_manager.get_duckdb_connection()

        added = 0
        skipped = 0

        for genre_data in TMDB_GENRES:
            tmdb_id = genre_data["tmdb_id"]
            name = genre_data["name"]
            slug = name.lower().replace(" ", "-")

            # Check if genre already exists
            existing = conn.execute(
                "SELECT id FROM genres WHERE LOWER(name) = LOWER(?) OR tmdb_genre_id = ?",
                [name, tmdb_id]
            ).fetchone()

            if existing:
                logger.info(f"Skipped: {name} (already exists)")
                skipped += 1
            else:
                # Insert genre
                genre_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO genres (
                        id, tmdb_genre_id, name, slug, parent_genre_id,
                        genre_category, description, is_active, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    genre_id,
                    tmdb_id,
                    name,
                    slug,
                    None,  # No parent (top-level genre)
                    slug,  # Use slug as category
                    f"TMDB standard {name} genre",
                    True,
                    datetime.now().isoformat()
                ])
                logger.info(f"Added: {name} (TMDB ID: {tmdb_id})")
                added += 1

        return {
            "success": True,
            "data": {
                "added": added,
                "skipped": skipped,
                "total": len(TMDB_GENRES)
            }
        }

    except Exception as e:
        logger.error(f"Failed to seed TMDB genres: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def classify_movie_genre(movie_data: dict) -> list:
    """
    Classify a movie into TMDB genres based on its metadata.

    Args:
        movie_data: Dictionary containing movie information

    Returns:
        List[str]: List of TMDB genre names (2-3 most relevant)
    """
    title = movie_data.get('title', '')
    overview = movie_data.get('overview', '')

    text = f"{title} {overview}".lower()
    detected_genres = []

    # Keyword-based classification
    genre_keywords = {
        "Action": ["action", "fight", "battle", "combat", "explosion", "chase", "martial arts"],
        "Adventure": ["adventure", "quest", "journey", "expedition", "treasure", "explorer"],
        "Animation": ["animated", "animation", "cartoon", "anime"],
        "Comedy": ["comedy", "funny", "humor", "laugh", "comic", "hilarious"],
        "Crime": ["crime", "criminal", "detective", "investigation", "murder", "heist", "gangster"],
        "Documentary": ["documentary", "real story", "true story", "real life"],
        "Drama": ["drama", "emotional", "tragedy", "family drama", "relationship"],
        "Family": ["family", "children", "kids", "all ages"],
        "Fantasy": ["fantasy", "magic", "wizard", "mythical", "supernatural", "dragon"],
        "History": ["historical", "history", "period", "war", "revolution", "based on"],
        "Horror": ["horror", "scary", "terror", "frightening", "monster", "zombie", "ghost"],
        "Music": ["music", "musical", "concert", "song", "performance"],
        "Mystery": ["mystery", "suspense", "enigma", "secret", "puzzle"],
        "Romance": ["romance", "romantic", "love", "relationship", "love story"],
        "Science Fiction": ["sci-fi", "science fiction", "future", "space", "alien", "robot", "technology"],
        "Thriller": ["thriller", "suspense", "tension", "psychological"],
        "TV Movie": ["tv movie", "television"],
        "War": ["war", "military", "soldier", "battle", "combat", "army"],
        "Western": ["western", "cowboy", "frontier", "gunslinger"]
    }

    for genre, keywords in genre_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected_genres.append(genre)

    # Default to Drama if no genres detected
    if not detected_genres:
        detected_genres = ["Drama"]

    # Return top 2-3 most relevant genres
    return detected_genres[:3]


@router.post("/classify-movies")
async def classify_movies(
    background_tasks: BackgroundTasks,
    limit: Optional[int] = None
):
    """
    Classify all movies and assign TMDB genres.

    Args:
        limit: Optional limit on number of movies to process

    Returns:
        dict: Summary of classification task
    """
    try:
        conn = db_manager.get_duckdb_connection()

        # Fetch movies
        query = """
            SELECT
                id,
                title,
                overview
            FROM media
            WHERE media_type = 'movie'
            ORDER BY title
        """

        if limit:
            query += f" LIMIT {limit}"

        movies = conn.execute(query).fetchall()
        logger.info(f"Starting classification of {len(movies)} movies")

        # Process movies in background
        def classify_movies_task():
            successful = 0
            failed = 0

            for movie_data in movies:
                movie_id, title, overview = movie_data

                try:
                    logger.info(f"Classifying: {title}")

                    # Build movie data dict
                    movie_info = {
                        'title': title,
                        'overview': overview or ''
                    }

                    # Classify genres
                    genres = classify_movie_genre(movie_info)
                    logger.info(f"  Detected genres: {', '.join(genres)}")

                    # Remove existing genre associations
                    conn = db_manager.get_duckdb_connection()
                    conn.execute(
                        "DELETE FROM media_genres WHERE media_id = ?",
                        [movie_id]
                    )

                    # Insert new genre associations
                    for genre_name in genres:
                        # Find genre ID by name (case-insensitive)
                        genre_result = conn.execute(
                            "SELECT id FROM genres WHERE LOWER(name) = LOWER(?)",
                            [genre_name]
                        ).fetchone()

                        if genre_result:
                            genre_id = genre_result[0]
                            conn.execute(
                                "INSERT INTO media_genres (media_id, genre_id) VALUES (?, ?)",
                                [movie_id, genre_id]
                            )
                            logger.info(f"  ✅ Added genre: {genre_name}")
                        else:
                            logger.warning(f"  ⚠️  Genre not found: {genre_name}")

                    # Update media updated_at timestamp
                    conn.execute(
                        "UPDATE media SET updated_at = ? WHERE id = ?",
                        [datetime.now().isoformat(), movie_id]
                    )

                    successful += 1

                except Exception as e:
                    logger.error(f"  ❌ Failed to classify {title}: {e}")
                    failed += 1

            logger.info(f"Classification complete: {successful} successful, {failed} failed")

        # Start background task
        background_tasks.add_task(classify_movies_task)

        return {
            "success": True,
            "data": {
                "message": "Classification started in background",
                "total_movies": len(movies),
                "note": "Check server logs for progress"
            }
        }

    except Exception as e:
        logger.error(f"Failed to start classification: {e}")
        raise HTTPException(status_code=500, detail=str(e))
