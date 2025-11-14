#!/usr/bin/env python3
"""
Add a batch of popular movies to test multi-source soundtrack loading.
"""
import sys
import os
import httpx
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = "http://localhost:7575/api"

# Movies known to have soundtracks
MOVIES_TO_ADD = [
    {"tmdb_id": 278, "title": "The Shawshank Redemption"},
    {"tmdb_id": 238, "title": "The Godfather"},
    {"tmdb_id": 240, "title": "The Godfather Part II"},
    {"tmdb_id": 424, "title": "Schindler's List"},
    {"tmdb_id": 389, "title": "12 Angry Men"},
    {"tmdb_id": 129, "title": "Spirited Away"},
    {"tmdb_id": 19404, "title": "Dilwale Dulhania Le Jayenge"},
    {"tmdb_id": 155, "title": "The Dark Knight"},
    {"tmdb_id": 496243, "title": "Parasite"},
    {"tmdb_id": 372058, "title": "Your Name"},
]

async def add_movies():
    """Add movies via TMDB sync API."""
    print("=" * 80)
    print("ADDING MOVIES FOR SOUNDTRACK BATCH")
    print("=" * 80)
    print()

    added = 0
    skipped = 0
    errors = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        for movie in MOVIES_TO_ADD:
            try:
                tmdb_id = movie["tmdb_id"]
                title = movie["title"]

                print(f"📽️  Adding: {title} (TMDB: {tmdb_id})")

                response = await client.post(
                    f"{API_BASE_URL}/media/sync-from-tmdb",
                    json={"tmdb_id": tmdb_id, "media_type": "movie"}
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"   ✅ Added successfully")
                        added += 1
                    else:
                        print(f"   ⚠️  {data.get('message', 'Unknown error')}")
                        skipped += 1
                else:
                    print(f"   ❌ API error {response.status_code}")
                    errors += 1

                await asyncio.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"   ❌ Error: {e}")
                errors += 1

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Added: {added}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print("=" * 80)
    print()

    return added > 0

async def main():
    """Main execution."""
    success = await add_movies()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
