"""
Genre Taxonomy Seeding Script for XILFTEN.

Seeds the database with 8 primary genre categories and 50+ sub-genres
based on research conducted for the project.
"""

import sys
from pathlib import Path
import duckdb
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Genre taxonomy data
GENRE_DATA = {
    "film-noir": {
        "name": "Film Noir",
        "description": "Stylized crime dramas with morally ambiguous protagonists, high-contrast visuals, and urban settings",
        "sub_genres": [
            {
                "name": "Neo-Noir",
                "slug": "neo-noir",
                "description": "Modern subversion of classic noir tropes (1970s-present)"
            },
            {
                "name": "Tech-Noir",
                "slug": "tech-noir",
                "description": "Noir with sci-fi elements (Blade Runner, The Terminator)"
            },
            {
                "name": "Neon-Noir",
                "slug": "neon-noir",
                "description": "Vibrant neon palettes, hyper-stylized aesthetics"
            },
            {
                "name": "Superhero-Noir",
                "slug": "superhero-noir",
                "description": "Contemporary noir themes in superhero narratives"
            },
            {
                "name": "Noir Western",
                "slug": "noir-western",
                "description": "Hybrid genre blending noir with western settings"
            },
            {
                "name": "Classic Noir",
                "slug": "classic-noir",
                "description": "1940s-1950s American film noir"
            }
        ]
    },

    "sci-fi": {
        "name": "Science Fiction",
        "description": "Speculative fiction exploring technological and scientific concepts, future societies, and space exploration",
        "sub_genres": [
            {
                "name": "Cyberpunk",
                "slug": "cyberpunk",
                "description": "Dystopian near-futures with AI, cyberware, and societal collapse"
            },
            {
                "name": "Hard Sci-Fi",
                "slug": "hard-sci-fi",
                "description": "Technology-focused with scientific realism and concept-heavy narratives"
            },
            {
                "name": "Soft Sci-Fi",
                "slug": "soft-sci-fi",
                "description": "Character-focused, exploring emotional and sociological impacts of technology"
            },
            {
                "name": "Space Opera",
                "slug": "space-opera",
                "description": "Galaxy-spanning adventure narratives with common space travel"
            },
            {
                "name": "Military Sci-Fi",
                "slug": "military-sci-fi",
                "description": "Futuristic warfare and advanced battle technology"
            },
            {
                "name": "Steampunk",
                "slug": "steampunk",
                "description": "Victorian-era technology aesthetics"
            },
            {
                "name": "Post-Apocalyptic",
                "slug": "post-apocalyptic",
                "description": "Survival stories after civilization collapse"
            },
            {
                "name": "Dystopian",
                "slug": "dystopian",
                "description": "Oppressive societal control and totalitarian futures"
            },
            {
                "name": "Time Travel",
                "slug": "time-travel",
                "description": "Temporal paradoxes and alternate timelines"
            }
        ]
    },

    "documentary": {
        "name": "Documentary",
        "description": "Non-fiction films documenting reality, based on factual events and real people",
        "sub_genres": [
            # Bill Nichols Documentary Modes
            {
                "name": "Observational Documentary",
                "slug": "observational-documentary",
                "description": "Fly-on-the-wall, cinema verité style with unobtrusive camera"
            },
            {
                "name": "Expository Documentary",
                "slug": "expository-documentary",
                "description": "Educational format with voice-of-God narration"
            },
            {
                "name": "Poetic Documentary",
                "slug": "poetic-documentary",
                "description": "Abstract, experimental, mood-focused over factual truth"
            },
            {
                "name": "Participatory Documentary",
                "slug": "participatory-documentary",
                "description": "Filmmaker actively engages subjects through interviews"
            },
            {
                "name": "Reflexive Documentary",
                "slug": "reflexive-documentary",
                "description": "Self-aware, meta-commentary on documentary-making process"
            },
            {
                "name": "Performative Documentary",
                "slug": "performative-documentary",
                "description": "Filmmaker's personal experience, subjective truth"
            },
            # Content Categories
            {
                "name": "Nature/Wildlife Documentary",
                "slug": "nature-wildlife-documentary",
                "description": "Natural world and animal behavior documentation"
            },
            {
                "name": "True Crime Documentary",
                "slug": "true-crime-documentary",
                "description": "Real criminal cases and investigations"
            },
            {
                "name": "Historical Documentary",
                "slug": "historical-documentary",
                "description": "Historical events and periods"
            },
            {
                "name": "Political Documentary",
                "slug": "political-documentary",
                "description": "Political events and social justice issues"
            },
            {
                "name": "Biographical Documentary",
                "slug": "biographical-documentary",
                "description": "Life stories of real people"
            },
            {
                "name": "Scientific Documentary",
                "slug": "scientific-documentary",
                "description": "Scientific discoveries and explanations"
            },
            {
                "name": "Music/Arts Documentary",
                "slug": "music-arts-documentary",
                "description": "Music and arts culture documentation"
            }
        ]
    },

    "comedy": {
        "name": "Comedy",
        "description": "Films designed to provoke laughter and amusement through humor and wit",
        "sub_genres": [
            {
                "name": "Slapstick Comedy",
                "slug": "slapstick",
                "description": "Exaggerated physical stunts and gags"
            },
            {
                "name": "Romantic Comedy",
                "slug": "rom-com",
                "description": "Love and humor combined, typically with happy endings"
            },
            {
                "name": "Dark Comedy",
                "slug": "dark-comedy",
                "description": "Humor from taboo subjects like death, war, or illness"
            },
            {
                "name": "Screwball Comedy",
                "slug": "screwball-comedy",
                "description": "Fast-paced witty dialogue in the 1930s-1940s style"
            },
            {
                "name": "Parody/Spoof",
                "slug": "parody",
                "description": "Satirizes other film genres or classic films"
            },
            {
                "name": "Action Comedy",
                "slug": "action-comedy",
                "description": "Fast-paced action with comedic elements"
            },
            {
                "name": "Mockumentary",
                "slug": "mockumentary",
                "description": "Faux-documentary format for comedic effect"
            },
            {
                "name": "Satire",
                "slug": "satire",
                "description": "Social and political commentary through humor"
            }
        ]
    },

    "anime": {
        "name": "Anime",
        "description": "Japanese animated productions with distinctive visual styles and storytelling",
        "sub_genres": [
            # Demographic Categories
            {
                "name": "Shonen Anime",
                "slug": "shonen",
                "description": "Targeted at teen boys (12-18) with action and adventure"
            },
            {
                "name": "Seinen Anime",
                "slug": "seinen",
                "description": "For young men (18-40) with mature and psychological themes"
            },
            {
                "name": "Shoujo Anime",
                "slug": "shoujo",
                "description": "Targeted at teen girls with romance focus"
            },
            {
                "name": "Josei Anime",
                "slug": "josei",
                "description": "For adult women with realistic romance and drama"
            },
            {
                "name": "Kodomomuke Anime",
                "slug": "kodomomuke",
                "description": "Children's anime with simple stories and themes"
            },
            # Theme Categories
            {
                "name": "Isekai Anime",
                "slug": "isekai",
                "description": "Reincarnation or transportation to another world"
            },
            {
                "name": "Mecha Anime",
                "slug": "mecha",
                "description": "Giant robots piloted by humans"
            },
            {
                "name": "Slice of Life Anime",
                "slug": "slice-of-life-anime",
                "description": "Everyday activities and relationships"
            },
            {
                "name": "Fantasy Anime",
                "slug": "fantasy-anime",
                "description": "Magic, mythical creatures, and alternate worlds"
            },
            {
                "name": "Sports Anime",
                "slug": "sports-anime",
                "description": "Competition and athletic achievement"
            },
            {
                "name": "Romance Anime",
                "slug": "romance-anime",
                "description": "Love stories and relationships"
            },
            {
                "name": "Psychological Anime",
                "slug": "psychological-anime",
                "description": "Mental and emotional exploration"
            },
            {
                "name": "Horror Anime",
                "slug": "horror-anime",
                "description": "Supernatural or psychological terror"
            }
        ]
    },

    "action": {
        "name": "Action",
        "description": "Fast-paced films featuring physical action sequences, combat, and high-energy stunts",
        "sub_genres": [
            {
                "name": "Martial Arts",
                "slug": "martial-arts",
                "description": "Hand-to-hand combat and melee weapons"
            },
            {
                "name": "Kung Fu",
                "slug": "kung-fu",
                "description": "Chinese martial arts cinema"
            },
            {
                "name": "Wuxia",
                "slug": "wuxia",
                "description": "Chinese martial arts fantasy"
            },
            {
                "name": "Superhero",
                "slug": "superhero",
                "description": "Characters with supernatural abilities"
            },
            {
                "name": "Spy/Espionage",
                "slug": "spy-espionage",
                "description": "Secret missions and special gadgets"
            },
            {
                "name": "Action Thriller",
                "slug": "action-thriller",
                "description": "Suspense combined with action sequences"
            },
            {
                "name": "Disaster Films",
                "slug": "disaster",
                "description": "Natural catastrophes and survival scenarios"
            },
            {
                "name": "Military Action",
                "slug": "military-action",
                "description": "War scenarios and tactical combat"
            }
        ]
    },

    "iranian-cinema": {
        "name": "Iranian Cinema",
        "description": "Iranian film movements known for poetic realism and humanist themes",
        "sub_genres": [
            {
                "name": "Iranian New Wave",
                "slug": "iranian-new-wave",
                "description": "Cinema-ye Motafavet, 1960s-1970s grassroots movement"
            },
            {
                "name": "Popular Art Cinema",
                "slug": "popular-art-cinema",
                "description": "Broader audience appeal beyond educated elite"
            },
            {
                "name": "Neorealist Cinema",
                "slug": "neorealist-cinema",
                "description": "Italian Neorealism influence with everyday life focus"
            },
            {
                "name": "Minimalist Art Cinema",
                "slug": "minimalist-art-cinema",
                "description": "Poetry in everyday life, blurring fiction and reality"
            }
        ]
    },

    "multi-genre": {
        "name": "Multi-Genre",
        "description": "Films that blend multiple genre conventions and can't be classified under a single category",
        "sub_genres": []  # Multi-genre is handled through tags, not sub-genres
    }
}


def seed_genres(conn: duckdb.DuckDBPyConnection, dry_run: bool = False):
    """
    Seed the genres table with all genre taxonomy data.

    Args:
        conn: DuckDB connection
        dry_run: If True, only show what would be seeded
    """
    logger.info("=" * 80)
    logger.info("🌱 Starting Genre Taxonomy Seeding")
    logger.info("=" * 80)
    logger.info(f"🔧 Dry run: {dry_run}")
    logger.info("")

    total_parent_genres = len(GENRE_DATA)
    total_sub_genres = sum(len(data["sub_genres"]) for data in GENRE_DATA.values())

    logger.info(f"📊 Statistics:")
    logger.info(f"   - Parent genres: {total_parent_genres}")
    logger.info(f"   - Sub-genres: {total_sub_genres}")
    logger.info(f"   - Total genres: {total_parent_genres + total_sub_genres}")
    logger.info("")

    if dry_run:
        for category_slug, genre_data in GENRE_DATA.items():
            logger.info(f"[DRY RUN] Would create parent genre: {genre_data['name']} ({category_slug})")
            for sub_genre in genre_data["sub_genres"]:
                logger.info(f"[DRY RUN]   - Sub-genre: {sub_genre['name']} ({sub_genre['slug']})")
        logger.info("")
        logger.info("ℹ️  This was a dry run. No changes were made.")
        return

    seeded_count = 0
    skipped_count = 0

    try:
        for category_slug, genre_data in GENRE_DATA.items():
            # Check if parent genre already exists
            existing = conn.execute(
                "SELECT id FROM genres WHERE slug = ?",
                [category_slug]
            ).fetchone()

            if existing:
                logger.info(f"⏭️  Skipping existing parent genre: {genre_data['name']}")
                parent_id = existing[0]
                skipped_count += 1
            else:
                # Insert parent genre
                result = conn.execute("""
                    INSERT INTO genres (name, slug, genre_category, description, is_active)
                    VALUES (?, ?, ?, ?, TRUE)
                    RETURNING id
                """, [
                    genre_data["name"],
                    category_slug,
                    category_slug,
                    genre_data["description"]
                ])
                parent_id = result.fetchone()[0]
                logger.info(f"✅ Created parent genre: {genre_data['name']} ({category_slug})")
                seeded_count += 1

            # Insert sub-genres
            for sub_genre in genre_data["sub_genres"]:
                existing_sub = conn.execute(
                    "SELECT id FROM genres WHERE slug = ?",
                    [sub_genre["slug"]]
                ).fetchone()

                if existing_sub:
                    logger.info(f"   ⏭️  Skipping existing sub-genre: {sub_genre['name']}")
                    skipped_count += 1
                else:
                    conn.execute("""
                        INSERT INTO genres (name, slug, parent_genre_id, genre_category, description, is_active)
                        VALUES (?, ?, ?, ?, ?, TRUE)
                    """, [
                        sub_genre["name"],
                        sub_genre["slug"],
                        parent_id,
                        category_slug,
                        sub_genre["description"]
                    ])
                    logger.info(f"   ✅ Created sub-genre: {sub_genre['name']} ({sub_genre['slug']})")
                    seeded_count += 1

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 Seeding Summary")
        logger.info("=" * 80)
        logger.info(f"✅ Created: {seeded_count}")
        logger.info(f"⏭️  Skipped: {skipped_count}")
        logger.info(f"📁 Total: {seeded_count + skipped_count}")
        logger.info("")
        logger.info("🎉 Genre seeding completed successfully!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Genre seeding failed: {str(e)}")
        raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed XILFTEN genre taxonomy")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be seeded without making changes"
    )

    args = parser.parse_args()

    # Connect to database
    try:
        conn = duckdb.connect(str(settings.duckdb_database_path))
        logger.info(f"✅ Connected to database: {settings.duckdb_database_path}")
        logger.info("")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {str(e)}")
        sys.exit(1)

    try:
        seed_genres(conn, dry_run=args.dry_run)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
