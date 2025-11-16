#!/usr/bin/env python3
"""
Seed Audio Genre Taxonomy

Populates the audio_genres table with a comprehensive music genre taxonomy.
Creates main genres and their sub-genres with appropriate metadata.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.audio_service import get_audio_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Music genre taxonomy
AUDIO_GENRES = {
    "Rock": {
        "color_code": "#E74C3C",
        "icon_name": "guitar",
        "description": "Rock music and its various forms",
        "subgenres": [
            {"name": "Classic Rock", "description": "Rock from the 60s-80s era"},
            {"name": "Alternative Rock", "description": "Independent and alternative rock styles"},
            {"name": "Hard Rock", "description": "Heavy, aggressive rock music"},
            {"name": "Indie Rock", "description": "Independent rock with DIY ethos"},
            {"name": "Progressive Rock", "description": "Complex, experimental rock"},
            {"name": "Punk Rock", "description": "Fast, raw, rebellious rock"},
        ],
    },
    "Pop": {
        "color_code": "#FF69B4",
        "icon_name": "star",
        "description": "Popular mainstream music",
        "subgenres": [
            {"name": "Dance Pop", "description": "Upbeat, danceable pop music"},
            {"name": "Synth Pop", "description": "Synthesizer-driven pop"},
            {"name": "Indie Pop", "description": "Independent pop with alternative influences"},
            {"name": "K-Pop", "description": "Korean pop music"},
            {"name": "Teen Pop", "description": "Pop targeted at teenage audiences"},
        ],
    },
    "Hip Hop": {
        "color_code": "#9B59B6",
        "icon_name": "microphone",
        "description": "Hip hop and rap music",
        "subgenres": [
            {"name": "Trap", "description": "Bass-heavy hip hop subgenre"},
            {"name": "Conscious Hip Hop", "description": "Socially aware rap"},
            {"name": "Gangsta Rap", "description": "Street-oriented hip hop"},
            {"name": "Alternative Hip Hop", "description": "Experimental rap music"},
            {"name": "Old School Hip Hop", "description": "Classic hip hop from the 80s-90s"},
        ],
    },
    "Electronic": {
        "color_code": "#3498DB",
        "icon_name": "waveform",
        "description": "Electronic and dance music",
        "subgenres": [
            {"name": "House", "description": "Four-on-the-floor electronic dance music"},
            {"name": "Techno", "description": "Detroit-originated electronic music"},
            {"name": "Trance", "description": "Hypnotic, melodic electronic music"},
            {"name": "Dubstep", "description": "Bass-heavy electronic music"},
            {"name": "Drum and Bass", "description": "Fast breakbeat electronic music"},
            {"name": "Ambient", "description": "Atmospheric, experimental electronic"},
        ],
    },
    "Jazz": {
        "color_code": "#F39C12",
        "icon_name": "saxophone",
        "description": "Jazz and improvisational music",
        "subgenres": [
            {"name": "Bebop", "description": "Fast, complex jazz style"},
            {"name": "Smooth Jazz", "description": "Mellow, accessible jazz"},
            {"name": "Free Jazz", "description": "Experimental, avant-garde jazz"},
            {"name": "Fusion", "description": "Jazz blended with rock/funk"},
            {"name": "Latin Jazz", "description": "Jazz with Latin rhythms"},
        ],
    },
    "Classical": {
        "color_code": "#8E44AD",
        "icon_name": "piano",
        "description": "Classical and orchestral music",
        "subgenres": [
            {"name": "Baroque", "description": "Classical music from 1600-1750"},
            {"name": "Romantic", "description": "Expressive 19th century classical"},
            {"name": "Contemporary Classical", "description": "Modern classical composition"},
            {"name": "Opera", "description": "Theatrical classical vocal performance"},
            {"name": "Chamber Music", "description": "Small ensemble classical music"},
        ],
    },
    "R&B": {
        "color_code": "#E67E22",
        "icon_name": "heart",
        "description": "Rhythm and blues, soul music",
        "subgenres": [
            {"name": "Soul", "description": "Gospel-influenced R&B"},
            {"name": "Contemporary R&B", "description": "Modern R&B with pop elements"},
            {"name": "Neo-Soul", "description": "Modern soul with jazz/funk influences"},
            {"name": "Funk", "description": "Groove-oriented R&B"},
        ],
    },
    "Country": {
        "color_code": "#D35400",
        "icon_name": "cowboy-hat",
        "description": "Country and folk music",
        "subgenres": [
            {"name": "Bluegrass", "description": "Acoustic country with fast tempos"},
            {"name": "Outlaw Country", "description": "Rebellious country music"},
            {"name": "Country Pop", "description": "Country with pop crossover appeal"},
            {"name": "Alternative Country", "description": "Independent country music"},
        ],
    },
    "Metal": {
        "color_code": "#2C3E50",
        "icon_name": "skull",
        "description": "Heavy metal and subgenres",
        "subgenres": [
            {"name": "Thrash Metal", "description": "Fast, aggressive metal"},
            {"name": "Death Metal", "description": "Extreme, heavy metal"},
            {"name": "Black Metal", "description": "Dark, atmospheric extreme metal"},
            {"name": "Power Metal", "description": "Melodic, fantasy-themed metal"},
            {"name": "Progressive Metal", "description": "Complex, technical metal"},
        ],
    },
    "Reggae": {
        "color_code": "#27AE60",
        "icon_name": "palm-tree",
        "description": "Reggae and Caribbean music",
        "subgenres": [
            {"name": "Dub", "description": "Instrumental reggae with heavy bass"},
            {"name": "Dancehall", "description": "Jamaican dance music"},
            {"name": "Ska", "description": "Upbeat Jamaican music"},
        ],
    },
    "Blues": {
        "color_code": "#34495E",
        "icon_name": "music",
        "description": "Blues music and derivatives",
        "subgenres": [
            {"name": "Delta Blues", "description": "Acoustic Mississippi blues"},
            {"name": "Chicago Blues", "description": "Electric urban blues"},
            {"name": "Blues Rock", "description": "Blues-influenced rock music"},
        ],
    },
    "Folk": {
        "color_code": "#16A085",
        "icon_name": "leaf",
        "description": "Folk and traditional music",
        "subgenres": [
            {"name": "Contemporary Folk", "description": "Modern folk music"},
            {"name": "Singer-Songwriter", "description": "Solo acoustic performances"},
            {"name": "Folk Rock", "description": "Folk with rock instrumentation"},
        ],
    },
    "Latin": {
        "color_code": "#C0392B",
        "icon_name": "fire",
        "description": "Latin American music",
        "subgenres": [
            {"name": "Salsa", "description": "Cuban dance music"},
            {"name": "Reggaeton", "description": "Latin urban music"},
            {"name": "Bachata", "description": "Dominican romantic music"},
            {"name": "Cumbia", "description": "Colombian folk-dance music"},
        ],
    },
    "World": {
        "color_code": "#1ABC9C",
        "icon_name": "globe",
        "description": "Non-Western traditional music",
        "subgenres": [
            {"name": "Afrobeat", "description": "West African funk fusion"},
            {"name": "Flamenco", "description": "Spanish folk music"},
            {"name": "Celtic", "description": "Irish/Scottish traditional music"},
        ],
    },
    "Soundtrack": {
        "color_code": "#F1C40F",
        "icon_name": "film",
        "description": "Film and game soundtracks",
        "subgenres": [
            {"name": "Film Score", "description": "Orchestral movie soundtracks"},
            {"name": "Video Game Music", "description": "Game soundtracks"},
            {"name": "Musical Theatre", "description": "Broadway/stage music"},
        ],
    },
}


def create_slug(name: str) -> str:
    """
    Create URL-friendly slug from genre name.

    Args:
        name (str): Genre name

    Returns:
        str: URL-friendly slug
    """
    return name.lower().replace(" ", "-").replace("&", "and")


async def seed_genres():
    """
    Seed audio genres into the database.

    Returns:
        dict: Statistics about seeded genres
    """
    logger.info("=" * 80)
    logger.info("🎵 SEEDING AUDIO GENRE TAXONOMY")
    logger.info("=" * 80)
    logger.info("")

    audio_service = get_audio_service()

    stats = {"main_genres": 0, "subgenres": 0, "total": 0, "errors": 0}

    # First pass: Create main genres
    logger.info("📊 Creating main genres...")
    logger.info("")

    main_genre_ids = {}

    for genre_name, genre_info in AUDIO_GENRES.items():
        try:
            genre_data = {
                "name": genre_name,
                "slug": create_slug(genre_name),
                "description": genre_info["description"],
                "color_code": genre_info["color_code"],
                "icon_name": genre_info["icon_name"],
                "parent_genre_id": None,
            }

            genre_id = audio_service.create_audio_genre(genre_data)
            main_genre_ids[genre_name] = genre_id
            stats["main_genres"] += 1

            logger.info(
                f"   ✅ {genre_name} (slug: {genre_data['slug']}, color: {genre_info['color_code']})"
            )

        except Exception as e:
            logger.error(f"   ❌ Error creating {genre_name}: {e}")
            stats["errors"] += 1

    logger.info("")
    logger.info(f"✅ Created {stats['main_genres']} main genres")
    logger.info("")

    # Second pass: Create subgenres
    logger.info("📊 Creating subgenres...")
    logger.info("")

    for genre_name, genre_info in AUDIO_GENRES.items():
        if genre_name not in main_genre_ids:
            continue

        parent_id = main_genre_ids[genre_name]

        logger.info(f"   {genre_name}:")

        for subgenre_info in genre_info.get("subgenres", []):
            try:
                subgenre_data = {
                    "name": subgenre_info["name"],
                    "slug": create_slug(subgenre_info["name"]),
                    "description": subgenre_info["description"],
                    "parent_genre_id": parent_id,
                }

                audio_service.create_audio_genre(subgenre_data)
                stats["subgenres"] += 1

                logger.info(f"      ✅ {subgenre_info['name']}")

            except Exception as e:
                logger.error(f"      ❌ Error creating {subgenre_info['name']}: {e}")
                stats["errors"] += 1

        logger.info("")

    stats["total"] = stats["main_genres"] + stats["subgenres"]

    logger.info("=" * 80)
    logger.info("📊 GENRE SEEDING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"✅ Main genres: {stats['main_genres']}")
    logger.info(f"✅ Subgenres: {stats['subgenres']}")
    logger.info(f"✅ Total genres: {stats['total']}")

    if stats["errors"] > 0:
        logger.warning(f"⚠️  Errors: {stats['errors']}")

    logger.info("=" * 80)

    return stats


def main():
    """
    Main entry point.
    """
    try:
        asyncio.run(seed_genres())
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
