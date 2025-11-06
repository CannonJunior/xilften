"""
Sample Media Seeder

Creates sample media entries for testing the frontend carousel and calendar.
"""

import sys
from pathlib import Path
import uuid
from datetime import datetime, date

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_sample_media():
    """
    Seed sample media data for testing.

    Returns:
        dict: Statistics about seeded data
    """
    conn = db_manager.get_duckdb_connection()

    # Check if we already have media
    count = conn.execute("SELECT COUNT(*) FROM media").fetchone()[0]
    if count > 0:
        logger.info(f"📊 Media already seeded ({count} items found)")
        return {"message": "Already seeded", "count": count}

    logger.info("🎬 Seeding sample media data...")

    # Sample media data (mix of sci-fi, action, noir, and anime)
    sample_media = [
        {
            "id": str(uuid.uuid4()),
            "tmdb_id": 603,
            "imdb_id": "tt0133093",
            "title": "The Matrix",
            "original_title": "The Matrix",
            "media_type": "movie",
            "release_date": date(1999, 3, 31),
            "runtime": 136,
            "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.",
            "tagline": "Welcome to the Real World",
            "tmdb_rating": 8.2,
            "tmdb_vote_count": 24000,
            "popularity_score": 145.5,
            "maturity_rating": "R",
            "original_language": "en",
            "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "backdrop_path": "/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
            "status": "Released",
        },
        {
            "id": str(uuid.uuid4()),
            "tmdb_id": 155,
            "imdb_id": "tt0816692",
            "title": "The Dark Knight",
            "original_title": "The Dark Knight",
            "media_type": "movie",
            "release_date": date(2008, 7, 18),
            "runtime": 152,
            "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations.",
            "tagline": "Why So Serious?",
            "tmdb_rating": 8.5,
            "tmdb_vote_count": 32000,
            "popularity_score": 189.3,
            "maturity_rating": "PG-13",
            "original_language": "en",
            "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "backdrop_path": "/nMKdUUepR0i5zn0y1T4CsSB5chy.jpg",
            "status": "Released",
        },
        {
            "id": str(uuid.uuid4()),
            "tmdb_id": 78,
            "imdb_id": "tt0083658",
            "title": "Blade Runner",
            "original_title": "Blade Runner",
            "media_type": "movie",
            "release_date": date(1982, 6, 25),
            "runtime": 117,
            "overview": "In the smog-choked dystopian Los Angeles of 2019, blade runner Rick Deckard is called out of retirement to terminate a quartet of replicants.",
            "tagline": "Man has made his match... now it's his problem",
            "tmdb_rating": 7.9,
            "tmdb_vote_count": 13000,
            "popularity_score": 98.7,
            "maturity_rating": "R",
            "original_language": "en",
            "poster_path": "/63N9uy8nd9j7Eog2axPQ8lbr3Wj.jpg",
            "backdrop_path": "/6aIb2GH98x17PqiJ5qqBwwFrDTR.jpg",
            "status": "Released",
        },
        {
            "id": str(uuid.uuid4()),
            "tmdb_id": 13,
            "imdb_id": "tt0109830",
            "title": "Forrest Gump",
            "original_title": "Forrest Gump",
            "media_type": "movie",
            "release_date": date(1994, 7, 6),
            "runtime": 142,
            "overview": "A man with a low IQ has accomplished great things in his life and been present during significant historic events.",
            "tagline": "The world will never be the same once you've seen it through the eyes of Forrest Gump.",
            "tmdb_rating": 8.5,
            "tmdb_vote_count": 26000,
            "popularity_score": 156.2,
            "maturity_rating": "PG-13",
            "original_language": "en",
            "poster_path": "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
            "backdrop_path": "/7c9UVPPiTPltouxRVY6N9uugaVA.jpg",
            "status": "Released",
        },
        {
            "id": str(uuid.uuid4()),
            "tmdb_id": 550,
            "imdb_id": "tt0137523",
            "title": "Fight Club",
            "original_title": "Fight Club",
            "media_type": "movie",
            "release_date": date(1999, 10, 15),
            "runtime": 139,
            "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy.",
            "tagline": "Mischief. Mayhem. Soap.",
            "tmdb_rating": 8.4,
            "tmdb_vote_count": 28000,
            "popularity_score": 167.8,
            "maturity_rating": "R",
            "original_language": "en",
            "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
            "backdrop_path": "/hZkgoQYus5vegHoetLkCJzb17zJ.jpg",
            "status": "Released",
        },
        {
            "id": str(uuid.uuid4()),
            "tmdb_id": 680,
            "imdb_id": "tt0110413",
            "title": "Pulp Fiction",
            "original_title": "Pulp Fiction",
            "media_type": "movie",
            "release_date": date(1994, 10, 14),
            "runtime": 154,
            "overview": "A burger-loving hit man, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling crime caper.",
            "tagline": "You won't know the facts until you've seen the fiction.",
            "tmdb_rating": 8.5,
            "tmdb_vote_count": 27000,
            "popularity_score": 178.9,
            "maturity_rating": "R",
            "original_language": "en",
            "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
            "backdrop_path": "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
            "status": "Released",
        },
        {
            "id": str(uuid.uuid4()),
            "tmdb_id": 27205,
            "imdb_id": "tt1375666",
            "title": "Inception",
            "original_title": "Inception",
            "media_type": "movie",
            "release_date": date(2010, 7, 16),
            "runtime": 148,
            "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to regain his old life.",
            "tagline": "Your mind is the scene of the crime",
            "tmdb_rating": 8.4,
            "tmdb_vote_count": 34000,
            "popularity_score": 194.5,
            "maturity_rating": "PG-13",
            "original_language": "en",
            "poster_path": "/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
            "backdrop_path": "/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
            "status": "Released",
        },
        {
            "id": str(uuid.uuid4()),
            "tmdb_id": 157336,
            "imdb_id": "tt2380307",
            "title": "Interstellar",
            "original_title": "Interstellar",
            "media_type": "movie",
            "release_date": date(2014, 11, 7),
            "runtime": 169,
            "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel.",
            "tagline": "Mankind was born on Earth. It was never meant to die here.",
            "tmdb_rating": 8.4,
            "tmdb_vote_count": 33000,
            "popularity_score": 188.2,
            "maturity_rating": "PG-13",
            "original_language": "en",
            "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "backdrop_path": "/xu9zaAevzQ5nnrsXN6JcahLnG4i.jpg",
            "status": "Released",
        },
    ]

    # Insert sample media
    for media_data in sample_media:
        try:
            conn.execute("""
                INSERT INTO media (
                    id, tmdb_id, imdb_id, title, original_title, media_type,
                    release_date, runtime, overview, tagline, tmdb_rating,
                    tmdb_vote_count, popularity_score, maturity_rating,
                    original_language, poster_path, backdrop_path, status
                ) VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?
                )
            """, [
                media_data["id"],
                media_data["tmdb_id"],
                media_data["imdb_id"],
                media_data["title"],
                media_data["original_title"],
                media_data["media_type"],
                media_data["release_date"],
                media_data["runtime"],
                media_data["overview"],
                media_data["tagline"],
                media_data["tmdb_rating"],
                media_data["tmdb_vote_count"],
                media_data["popularity_score"],
                media_data["maturity_rating"],
                media_data["original_language"],
                media_data["poster_path"],
                media_data["backdrop_path"],
                media_data["status"],
            ])
            logger.info(f"✅ Seeded: {media_data['title']}")
        except Exception as e:
            logger.error(f"❌ Failed to seed {media_data['title']}: {e}")

    seeded_count = conn.execute("SELECT COUNT(*) FROM media").fetchone()[0]
    logger.info(f"✨ Seeded {seeded_count} media items")

    return {"message": "Seeded successfully", "count": seeded_count}


def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("🎬 XILFTEN Sample Media Seeder")
    logger.info("=" * 80)

    try:
        result = seed_sample_media()
        logger.info(f"✅ {result['message']}: {result['count']} items")
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        raise

    logger.info("=" * 80)


if __name__ == "__main__":
    main()
