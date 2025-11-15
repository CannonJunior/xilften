#!/usr/bin/env python3
"""
Ingest soundtracks for all movies in the database using API endpoints.

This script loads soundtracks for all movies that don't currently have them,
using the configured multi-source system (MusicBrainz primary, IMDB fallback).
"""

import asyncio
import sys
from pathlib import Path
import httpx
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# API base URL
API_BASE = "http://localhost:7575/api"


async def ingest_all_soundtracks():
    """Ingest soundtracks for all movies without soundtracks via API."""

    print("=" * 80)
    print("🎵 INGESTING SOUNDTRACKS FOR ALL MOVIES (API-based)")
    print("=" * 80)
    print()

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Get all movies
            print("📡 Fetching all movies from API...")
            response = await client.get(f"{API_BASE}/media", params={"limit": 1000})

            if response.status_code != 200:
                print(f"❌ Failed to fetch movies: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return

            response_data = response.json()

            # Extract items from nested structure
            if "data" in response_data and "items" in response_data["data"]:
                all_items = response_data["data"]["items"]
            else:
                all_items = response_data if isinstance(response_data, list) else []

            # Filter to movies only
            movies = [m for m in all_items if m.get("media_type") == "movie"]

            total_movies = len(movies)
            print(f"📊 Total movies in database: {total_movies}")
            print()

            # Check which movies have soundtracks
            movies_with_soundtracks = set()
            movies_without_soundtracks = []

            for movie in movies:
                media_id = movie.get("id")

                # Check if movie has soundtracks
                soundtrack_response = await client.get(f"{API_BASE}/soundtracks/{media_id}")

                if soundtrack_response.status_code == 200:
                    soundtrack_data = soundtrack_response.json()
                    if soundtrack_data and len(soundtrack_data) > 0:
                        movies_with_soundtracks.add(media_id)
                    else:
                        movies_without_soundtracks.append(movie)
                else:
                    # No soundtrack found
                    movies_without_soundtracks.append(movie)

            movies_with = len(movies_with_soundtracks)
            movies_without = len(movies_without_soundtracks)

            print(f"✅ Movies WITH soundtracks: {movies_with}")
            print(f"⚠️  Movies WITHOUT soundtracks: {movies_without}")
            print()

            if movies_without == 0:
                print("🎉 All movies already have soundtracks!")
                return

            print("=" * 80)
            print(f"🔄 PROCESSING {movies_without} MOVIES")
            print("=" * 80)
            print()

            # Track results
            loaded = 0
            not_found = 0
            errors = 0
            source_stats = {}

            for idx, movie in enumerate(movies_without_soundtracks, 1):
                media_id = movie.get("id")
                title = movie.get("title")
                release_date = movie.get("release_date")
                imdb_id = movie.get("imdb_id")

                # Extract year from release_date
                year = None
                if release_date:
                    try:
                        year = int(release_date.split('-')[0])
                    except:
                        pass

                print(f"[{idx}/{movies_without}] 🎵 {title} ({year or 'N/A'})")

                try:
                    # Search for soundtrack via API
                    search_payload = {
                        "media_id": media_id,
                        "movie_title": title,
                        "year": year
                    }

                    search_response = await client.post(
                        f"{API_BASE}/soundtracks/search",
                        json=search_payload
                    )

                    if search_response.status_code == 200:
                        result = search_response.json()

                        if result and result.get("tracks"):
                            track_count = len(result["tracks"])
                            source = result.get("source", "unknown")
                            source_stats[source] = source_stats.get(source, 0) + 1
                            print(f"   ✅ SUCCESS! Loaded from {source.upper()}: {track_count} tracks")
                            loaded += 1
                        else:
                            print(f"   ⚠️  No soundtrack found")
                            not_found += 1
                    elif search_response.status_code == 404:
                        print(f"   ⚠️  No soundtrack found")
                        not_found += 1
                    else:
                        print(f"   ❌ Error: HTTP {search_response.status_code}")
                        print(f"   Response: {search_response.text}")
                        errors += 1

                    # Small delay to be respectful to APIs
                    await asyncio.sleep(1.0)

                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    errors += 1
                    logger.exception(f"Error processing {title}")

            print()
            print("=" * 80)
            print("📊 INGESTION SUMMARY")
            print("=" * 80)
            print(f"✅ Soundtracks loaded: {loaded}")
            print(f"⚠️  Not found: {not_found}")
            print(f"❌ Errors: {errors}")

            if source_stats:
                print()
                print("📈 BY SOURCE:")
                for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {source.upper()}: {count}")

            print()
            print("=" * 80)
            print("📊 FINAL STATUS")
            print("=" * 80)

            # Get final counts
            final_with = movies_with + loaded
            final_without = total_movies - final_with
            percentage = (final_with / total_movies * 100) if total_movies > 0 else 0

            print(f"Total Movies: {total_movies}")
            print(f"✅ With soundtracks: {final_with} ({percentage:.1f}%)")
            print(f"⚠️  Without soundtracks: {final_without}")
            print("=" * 80)

        except Exception as e:
            logger.exception("Fatal error during ingestion")
            print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    asyncio.run(ingest_all_soundtracks())
