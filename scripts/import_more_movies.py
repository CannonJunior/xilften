#!/usr/bin/env python3
"""
Import Additional Movies from TMDB

This script fetches popular movies from TMDB and imports them into the database.
Uses the bulk import endpoint to add movies with automatic genre classification.
"""

import os
import sys
import requests
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Settings

settings = Settings()

TMDB_API_KEY = settings.tmdb_api_key
TMDB_BASE_URL = settings.tmdb_base_url
API_BASE_URL = f"http://localhost:{settings.app_port}"


def fetch_tmdb_movie_details(tmdb_id: int) -> dict:
    """Fetch detailed movie information from TMDB."""
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "append_to_response": "credits,external_ids"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_popular_movies(page: int = 1) -> list:
    """Fetch popular movies from TMDB."""
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "page": page,
        "language": "en-US"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])


def convert_to_import_format(movie_data: dict) -> dict:
    """Convert TMDB movie data to import format."""
    # Get genres from TMDB
    genres = [g["name"] for g in movie_data.get("genres", [])]

    # Get credits info
    credits = movie_data.get("credits", {})
    crew = credits.get("crew", [])
    cast = credits.get("cast", [])

    # Find key crew members
    director = next((p["name"] for p in crew if p["job"] == "Director"), "Unknown")
    screenplay = ", ".join([p["name"] for p in crew if p["job"] in ["Screenplay", "Writer"]][:3]) or "Unknown"
    cinematography = next((p["name"] for p in crew if p["job"] == "Director of Photography"), "Unknown")
    music = next((p["name"] for p in crew if p["department"] == "Sound" and "Music" in p["job"]), "Unknown")
    editing = next((p["name"] for p in crew if p["job"] == "Editor"), "Unknown")

    # Get top cast
    starring = ", ".join([p["name"] for p in cast[:5]])

    # Get production companies
    production_companies = ", ".join([c["name"] for c in movie_data.get("production_companies", [])[:3]])

    # Get languages
    languages = ", ".join([l["english_name"] for l in movie_data.get("spoken_languages", [])])

    # Get external IDs
    external_ids = movie_data.get("external_ids", {})
    imdb_id = external_ids.get("imdb_id")

    return {
        "tmdb_id": movie_data["id"],
        "imdb_id": imdb_id,
        "title": movie_data.get("title", ""),
        "original_title": movie_data.get("original_title"),
        "release_date": movie_data.get("release_date"),
        "runtime": movie_data.get("runtime"),
        "overview": movie_data.get("overview"),
        "tagline": movie_data.get("tagline"),
        "tmdb_rating": movie_data.get("vote_average"),
        "tmdb_vote_count": movie_data.get("vote_count"),
        "popularity": movie_data.get("popularity"),
        "poster_path": movie_data.get("poster_path"),
        "backdrop_path": movie_data.get("backdrop_path"),
        "original_language": movie_data.get("original_language"),
        "status": movie_data.get("status"),
        "genres": genres,
        "tmdb_data": {
            "director": director,
            "screenplay": screenplay,
            "cinematography": cinematography,
            "music": music,
            "editing": editing,
            "starring": starring,
            "production_companies": production_companies,
            "languages": languages,
            "budget": movie_data.get("budget", 0),
            "box_office": movie_data.get("revenue", 0)
        }
    }


def import_movies_to_database(movies: list) -> dict:
    """Import movies to database via bulk import endpoint."""
    url = f"{API_BASE_URL}/api/bulk/import-tmdb-movies"

    response = requests.post(url, json=movies)
    response.raise_for_status()
    return response.json()


def main(count: int = 20, start_page: int = 6):
    """
    Import movies from TMDB.

    Args:
        count: Number of movies to import
        start_page: Starting page number (default 6, as pages 1-5 likely already imported)
    """
    print(f"🎬 Fetching {count} movies from TMDB (starting at page {start_page})...")

    if not TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY not set in environment variables")
        print("   Set TMDB_API_KEY in .env file")
        return 1

    movies_to_import = []
    current_page = start_page

    try:
        while len(movies_to_import) < count:
            print(f"\n📄 Fetching page {current_page}...")
            popular_movies = fetch_popular_movies(current_page)

            for movie in popular_movies:
                if len(movies_to_import) >= count:
                    break

                tmdb_id = movie["id"]
                title = movie.get("title", "Unknown")

                print(f"  Fetching details for: {title} (ID: {tmdb_id})")

                try:
                    # Get full movie details
                    details = fetch_tmdb_movie_details(tmdb_id)

                    # Convert to import format
                    import_data = convert_to_import_format(details)
                    movies_to_import.append(import_data)

                    print(f"    ✅ {title}")

                    # Rate limiting
                    time.sleep(0.25)  # 4 requests per second

                except Exception as e:
                    print(f"    ❌ Error fetching {title}: {e}")
                    continue

            current_page += 1

        print(f"\n📦 Importing {len(movies_to_import)} movies to database...")
        result = import_movies_to_database(movies_to_import)

        # Extract data from nested response
        data = result.get('data', result)  # Handle both nested and flat responses

        print(f"\n✅ Import complete!")
        print(f"   Imported: {data.get('inserted', 0)} movies")
        print(f"   Skipped (duplicates): {data.get('skipped', 0)} movies")
        print(f"   Errors: {data.get('errors', 0)}")

        if data.get('error_details'):
            print(f"\n   Error details:")
            for err in data.get('error_details', [])[:5]:
                print(f"     - {err}")

        # Run genre classification
        print(f"\n🏷️  Classifying genres for new movies...")
        classify_url = f"{API_BASE_URL}/api/genres-management/classify-movies"
        classify_response = requests.post(classify_url)

        if classify_response.status_code == 200:
            print(f"   ✅ Genre classification started")
        else:
            print(f"   ⚠️  Genre classification may need to be run manually")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import additional movies from TMDB")
    parser.add_argument("--count", type=int, default=20, help="Number of movies to import (default: 20)")
    parser.add_argument("--start-page", type=int, default=6, help="Starting page number (default: 6)")

    args = parser.parse_args()

    sys.exit(main(args.count, args.start_page))
