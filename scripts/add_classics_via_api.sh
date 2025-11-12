#!/bin/bash
# Add classic movies via API for soundtrack testing

echo "🎬 Adding classic movies with known soundtracks..."

# Classic movies with iconic soundtracks
# The Godfather (1972)
curl -s -X POST "http://localhost:7575/api/media/fetch-tmdb" \
  -H "Content-Type: application/json" \
  -d '{"tmdb_id": 238, "media_type": "movie"}' | python3 -m json.tool

sleep 1

# Star Wars (1977)
curl -s -X POST "http://localhost:7575/api/media/fetch-tmdb" \
  -H "Content-Type: application/json" \
  -d '{"tmdb_id": 11, "media_type": "movie"}' | python3 -m json.tool

sleep 1

# Pulp Fiction (1994)
curl -s -X POST "http://localhost:7575/api/media/fetch-tmdb" \
  -H "Content-Type: application/json" \
  -d '{"tmdb_id": 680, "media_type": "movie"}' | python3 -m json.tool

sleep 1

# The Lion King (1994)
curl -s -X POST "http://localhost:7575/api/media/fetch-tmdb" \
  -H "Content-Type: application/json" \
  -d '{"tmdb_id": 8587, "media_type": "movie"}' | python3 -m json.tool

echo ""
echo "✅ Classic movies added! Now loading soundtracks..."
