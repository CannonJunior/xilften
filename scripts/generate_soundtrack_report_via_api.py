#!/usr/bin/env python3
"""
Generate a comprehensive soundtrack report using the API.
"""
import asyncio
import httpx
import sys
from collections import defaultdict

API_BASE_URL = "http://localhost:7575/api"

async def generate_report():
    """Generate soundtrack report via API."""
    print("=" * 80)
    print("SOUNDTRACK INGESTION REPORT")
    print("=" * 80)
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get all media
        print("📊 Fetching all media...")
        media_response = await client.get(f"{API_BASE_URL}/media?limit=100")

        if media_response.status_code != 200:
            print(f"❌ Failed to fetch media: HTTP {media_response.status_code}")
            return False

        media_data = media_response.json()
        all_movies = media_data.get('data', {}).get('items', [])
        total_movies = len(all_movies)

        print(f"   Found {total_movies} movies in database")
        print()

        # Check soundtracks for each movie
        print("🎵 Checking soundtracks...")
        print()

        movies_with_soundtracks = []
        movies_without_soundtracks = []
        source_stats = defaultdict(int)
        total_tracks = 0

        for i, movie in enumerate(all_movies, 1):
            media_id = movie['id']
            title = movie['title']
            year = movie.get('release_date', 'Unknown')[:4] if movie.get('release_date') else 'Unknown'

            # Check if soundtrack exists
            soundtrack_response = await client.get(f"{API_BASE_URL}/soundtracks/{media_id}")

            if soundtrack_response.status_code == 200:
                soundtrack_data = soundtrack_response.json()
                if soundtrack_data.get('success') and soundtrack_data.get('data'):
                    soundtrack = soundtrack_data['data']
                    source = soundtrack.get('source', 'unknown')
                    tracks_count = soundtrack.get('total_tracks', 0)

                    source_stats[source] += 1
                    total_tracks += tracks_count
                    movies_with_soundtracks.append({
                        'title': title,
                        'year': year,
                        'source': source,
                        'tracks': tracks_count
                    })
                    status = f"✅ {source.upper()}: {tracks_count} tracks"
                else:
                    movies_without_soundtracks.append({'title': title, 'year': year})
                    status = "⚠️  No soundtrack"
            else:
                movies_without_soundtracks.append({'title': title, 'year': year})
                status = "⚠️  No soundtrack"

            print(f"   [{i:2d}/{total_movies}] {title} ({year}): {status}")

        print()
        print("=" * 80)
        print("📈 SUMMARY")
        print("=" * 80)
        print(f"Total Movies: {total_movies}")
        print(f"✅ With Soundtracks: {len(movies_with_soundtracks)}")
        print(f"⚠️  Without Soundtracks: {len(movies_without_soundtracks)}")
        print(f"📊 Total Tracks: {total_tracks}")
        print()

        if source_stats:
            print("🎵 BY SOURCE:")
            for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(movies_with_soundtracks) * 100) if movies_with_soundtracks else 0
                print(f"   {source.upper():15s}: {count:2d} movies ({percentage:5.1f}%)")
            print()

        if movies_without_soundtracks:
            print("⚠️  MOVIES WITHOUT SOUNDTRACKS:")
            for movie in movies_without_soundtracks[:10]:  # Show first 10
                print(f"   • {movie['title']} ({movie['year']})")

            if len(movies_without_soundtracks) > 10:
                print(f"   ... and {len(movies_without_soundtracks) - 10} more")
            print()

        print("=" * 80)
        return True

if __name__ == "__main__":
    try:
        success = asyncio.run(generate_report())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
