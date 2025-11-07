#!/usr/bin/env python3
"""
MCP Server for Movie Genre Classification

This Model Context Protocol server provides tools for classifying movies
into TMDB-standard genres based on their metadata.
"""

import json
import logging
from typing import Any, Dict, List
import duckdb
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TMDB Official 19 Genres
TMDB_GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "History",
    "Horror",
    "Music",
    "Mystery",
    "Romance",
    "Science Fiction",
    "Thriller",
    "TV Movie",
    "War",
    "Western"
]

# Database configuration
DATABASE_PATH = "./database/xilften.duckdb"


def get_db_connection():
    """
    Get database connection.

    Returns:
        duckdb.Connection: Database connection
    """
    return duckdb.connect(DATABASE_PATH)


def classify_movie_genre(movie_data: Dict[str, Any]) -> List[str]:
    """
    Classify a movie into TMDB genres based on its metadata.

    Args:
        movie_data: Dictionary containing movie information
            - title: str
            - overview: str
            - genres: List[str] (from TMDB)
            - custom_fields: Dict

    Returns:
        List[str]: List of TMDB genre names (2-3 most relevant)
    """
    title = movie_data.get('title', '')
    overview = movie_data.get('overview', '')
    existing_genres = movie_data.get('genres', [])

    # If movie already has TMDB genres from import, use them
    if existing_genres:
        # Filter to only TMDB-standard genres
        tmdb_genres = [g for g in existing_genres if g in TMDB_GENRES]
        if tmdb_genres:
            return tmdb_genres[:3]  # TMDB recommends 2-3 genres max

    # Otherwise, classify based on keywords in title and overview
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


def update_movie_genres(movie_id: str, genres: List[str]) -> None:
    """
    Update movie genres in database.

    Args:
        movie_id: Movie UUID
        genres: List of genre names to assign
    """
    conn = get_db_connection()

    try:
        # First, remove existing genre associations
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
                logger.warning(f"  ⚠️  Genre not found in database: {genre_name}")

        # Update media updated_at timestamp
        conn.execute(
            "UPDATE media SET updated_at = ? WHERE id = ?",
            [datetime.now().isoformat(), movie_id]
        )

    except Exception as e:
        logger.error(f"Error updating genres for movie {movie_id}: {e}")
        raise
    finally:
        conn.close()


def classify_all_movies(limit: int = None) -> Dict[str, Any]:
    """
    Classify all movies in the database.

    Args:
        limit: Optional limit on number of movies to process

    Returns:
        Dict with results summary
    """
    conn = get_db_connection()

    try:
        # Fetch movies
        query = """
            SELECT
                id,
                title,
                overview,
                custom_fields
            FROM media
            WHERE media_type = 'movie'
            ORDER BY title
        """

        if limit:
            query += f" LIMIT {limit}"

        movies = conn.execute(query).fetchall()
        logger.info(f"📊 Found {len(movies)} movies to classify")

        successful = 0
        failed = 0

        for movie_data in movies:
            movie_id, title, overview, custom_fields_raw = movie_data

            try:
                logger.info(f"🎬 Classifying: {title}")

                # Parse custom fields
                custom_fields = json.loads(custom_fields_raw) if custom_fields_raw else {}
                tmdb_data = custom_fields.get('tmdb_data', {})

                # Get existing genres from TMDB data (stored during import)
                existing_genres = []

                # Build movie data dict
                movie_info = {
                    'title': title,
                    'overview': overview or '',
                    'genres': existing_genres,
                    'custom_fields': custom_fields
                }

                # Classify genres
                genres = classify_movie_genre(movie_info)
                logger.info(f"  📝 Detected genres: {', '.join(genres)}")

                # Update database
                update_movie_genres(movie_id, genres)

                successful += 1

            except Exception as e:
                logger.error(f"  ❌ Failed to classify {title}: {e}")
                failed += 1

        return {
            "success": True,
            "total_processed": len(movies),
            "successful": successful,
            "failed": failed
        }

    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        conn.close()


def get_genre_statistics() -> Dict[str, Any]:
    """
    Get statistics about genre usage in the database.

    Returns:
        Dict with genre statistics
    """
    conn = get_db_connection()

    try:
        # Count movies per genre
        stats = conn.execute("""
            SELECT
                g.name,
                COUNT(mg.media_id) as movie_count
            FROM genres g
            LEFT JOIN media_genres mg ON g.id = mg.genre_id
            WHERE g.parent_genre_id IS NULL  -- Only main genres
            GROUP BY g.name
            ORDER BY movie_count DESC, g.name
        """).fetchall()

        return {
            "success": True,
            "genres": [
                {"name": name, "count": count}
                for name, count in stats
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        conn.close()


# MCP Tool Definitions
MCP_TOOLS = {
    "classify_movie": {
        "description": "Classify a single movie into TMDB genres",
        "inputSchema": {
            "type": "object",
            "properties": {
                "movie_id": {"type": "string", "description": "Movie UUID"},
                "title": {"type": "string"},
                "overview": {"type": "string"},
                "genres": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["movie_id"]
        }
    },
    "classify_all_movies": {
        "description": "Classify all movies in the database",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Optional limit on number of movies"}
            }
        }
    },
    "get_genre_statistics": {
        "description": "Get genre usage statistics",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
}


def main():
    """Main entry point for direct execution."""
    import sys

    print("=" * 80)
    print("🎬 Movie Genre Classification Tool")
    print("=" * 80)
    print()

    # Check for command line arguments
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

    # Run classification
    result = classify_all_movies(limit=limit)

    print()
    print("=" * 80)
    if result["success"]:
        print("✅ Classification Complete!")
        print("=" * 80)
        print(f"Total processed: {result['total_processed']}")
        print(f"Successful: {result['successful']}")
        print(f"Failed: {result['failed']}")
    else:
        print("❌ Classification Failed!")
        print("=" * 80)
        print(f"Error: {result['error']}")
    print()

    # Show statistics
    print("📊 Genre Statistics:")
    print("-" * 80)
    stats = get_genre_statistics()
    if stats["success"]:
        for genre in stats["genres"][:10]:  # Top 10
            print(f"  {genre['name']:30s} {genre['count']:3d} movies")
    print()


if __name__ == "__main__":
    main()
