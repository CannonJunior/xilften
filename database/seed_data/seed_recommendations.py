"""
Recommendation Presets Seeding Script for XILFTEN.

Seeds the database with default criteria presets for multi-criteria recommendations.
"""

import sys
from pathlib import Path
import duckdb
import json
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

# Default recommendation presets
PRESET_DATA = [
    {
        "name": "High Quality Sci-Fi",
        "description": "Top-rated science fiction films with strong ratings and popularity",
        "is_default": True,
        "criteria_config": {
            "genres": {
                "weight": 0.9,
                "values": ["sci-fi", "cyberpunk", "space-opera", "dystopian", "hard-sci-fi"]
            },
            "tmdb_rating": {
                "weight": 0.8,
                "min": 7.0
            },
            "popularity_score": {
                "weight": 0.3,
                "min": 50.0
            },
            "runtime": {
                "weight": 0.2,
                "min": 90,
                "max": 180
            }
        }
    },
    {
        "name": "Friday Night Action",
        "description": "High-energy action films perfect for weekend entertainment",
        "is_default": True,
        "criteria_config": {
            "genres": {
                "weight": 1.0,
                "values": ["action", "action-comedy", "superhero", "spy-espionage"]
            },
            "tmdb_rating": {
                "weight": 0.5,
                "min": 6.5
            },
            "runtime": {
                "weight": 0.3,
                "min": 90,
                "max": 150
            },
            "maturity_rating": {
                "weight": 0.2,
                "values": ["PG-13", "R"]
            }
        }
    },
    {
        "name": "Hidden Gems",
        "description": "High-quality but less popular films that deserve more attention",
        "is_default": True,
        "criteria_config": {
            "tmdb_rating": {
                "weight": 1.0,
                "min": 7.5
            },
            "popularity_score": {
                "weight": 0.8,
                "max": 100.0
            },
            "tmdb_vote_count": {
                "weight": 0.3,
                "min": 50
            }
        }
    },
    {
        "name": "Quick Watch",
        "description": "High-quality shorter films under 100 minutes",
        "is_default": False,
        "criteria_config": {
            "runtime": {
                "weight": 1.0,
                "max": 100
            },
            "tmdb_rating": {
                "weight": 0.7,
                "min": 7.0
            }
        }
    },
    {
        "name": "Epic Films",
        "description": "Long-form cinematic experiences with high ratings",
        "is_default": False,
        "criteria_config": {
            "runtime": {
                "weight": 0.9,
                "min": 150
            },
            "tmdb_rating": {
                "weight": 0.8,
                "min": 7.5
            },
            "popularity_score": {
                "weight": 0.4,
                "min": 100.0
            }
        }
    },
    {
        "name": "Artistic Documentaries",
        "description": "Well-crafted documentary films with strong ratings",
        "is_default": False,
        "criteria_config": {
            "genres": {
                "weight": 1.0,
                "values": [
                    "documentary",
                    "poetic-documentary",
                    "observational-documentary",
                    "nature-wildlife-documentary"
                ]
            },
            "tmdb_rating": {
                "weight": 0.7,
                "min": 7.0
            }
        }
    },
    {
        "name": "Neo-Noir Classics",
        "description": "Modern noir films with strong visual style and storytelling",
        "is_default": False,
        "criteria_config": {
            "genres": {
                "weight": 1.0,
                "values": ["film-noir", "neo-noir", "tech-noir", "neon-noir"]
            },
            "tmdb_rating": {
                "weight": 0.8,
                "min": 7.0
            },
            "release_year": {
                "weight": 0.3,
                "min": 1980
            }
        }
    },
    {
        "name": "Anime Favorites",
        "description": "Top-rated anime films and series across all demographics",
        "is_default": False,
        "criteria_config": {
            "genres": {
                "weight": 1.0,
                "values": [
                    "anime",
                    "shonen",
                    "seinen",
                    "shoujo",
                    "josei",
                    "isekai",
                    "mecha"
                ]
            },
            "tmdb_rating": {
                "weight": 0.7,
                "min": 7.5
            }
        }
    },
    {
        "name": "Recent Releases",
        "description": "High-quality recent films from the last 2 years",
        "is_default": False,
        "criteria_config": {
            "release_year": {
                "weight": 1.0,
                "min": 2023
            },
            "tmdb_rating": {
                "weight": 0.7,
                "min": 7.0
            },
            "popularity_score": {
                "weight": 0.5,
                "min": 50.0
            }
        }
    },
    {
        "name": "Family Friendly",
        "description": "High-quality films suitable for all ages",
        "is_default": False,
        "criteria_config": {
            "maturity_rating": {
                "weight": 1.0,
                "values": ["G", "PG"]
            },
            "tmdb_rating": {
                "weight": 0.7,
                "min": 7.0
            }
        }
    },
    {
        "name": "Iranian Cinema Collection",
        "description": "Acclaimed films from Iranian New Wave and art cinema movements",
        "is_default": False,
        "criteria_config": {
            "genres": {
                "weight": 1.0,
                "values": [
                    "iranian-cinema",
                    "iranian-new-wave",
                    "neorealist-cinema",
                    "minimalist-art-cinema"
                ]
            },
            "tmdb_rating": {
                "weight": 0.6,
                "min": 6.5
            }
        }
    },
    {
        "name": "Cult Comedies",
        "description": "Popular comedy films with unique styles and devoted followings",
        "is_default": False,
        "criteria_config": {
            "genres": {
                "weight": 1.0,
                "values": [
                    "comedy",
                    "dark-comedy",
                    "satire",
                    "mockumentary",
                    "parody"
                ]
            },
            "tmdb_rating": {
                "weight": 0.6,
                "min": 7.0
            },
            "popularity_score": {
                "weight": 0.4,
                "min": 30.0
            }
        }
    }
]


def seed_recommendations(conn: duckdb.DuckDBPyConnection, dry_run: bool = False):
    """
    Seed the recommendation_criteria table with default presets.

    Args:
        conn: DuckDB connection
        dry_run: If True, only show what would be seeded
    """
    logger.info("=" * 80)
    logger.info("🌱 Starting Recommendation Presets Seeding")
    logger.info("=" * 80)
    logger.info(f"🔧 Dry run: {dry_run}")
    logger.info("")

    logger.info(f"📊 Statistics:")
    logger.info(f"   - Total presets: {len(PRESET_DATA)}")
    logger.info(f"   - Default presets: {sum(1 for p in PRESET_DATA if p['is_default'])}")
    logger.info(f"   - Custom presets: {sum(1 for p in PRESET_DATA if not p['is_default'])}")
    logger.info("")

    if dry_run:
        for preset in PRESET_DATA:
            default_marker = "⭐" if preset["is_default"] else "  "
            logger.info(f"[DRY RUN] {default_marker} Would create preset: {preset['name']}")
            logger.info(f"           Description: {preset['description']}")
            logger.info(f"           Criteria: {len(preset['criteria_config'])} fields")
        logger.info("")
        logger.info("ℹ️  This was a dry run. No changes were made.")
        return

    seeded_count = 0
    skipped_count = 0

    try:
        for preset in PRESET_DATA:
            # Check if preset already exists by name
            existing = conn.execute(
                "SELECT id FROM recommendation_criteria WHERE name = ?",
                [preset["name"]]
            ).fetchone()

            if existing:
                logger.info(f"⏭️  Skipping existing preset: {preset['name']}")
                skipped_count += 1
            else:
                # Insert preset
                criteria_json = json.dumps(preset["criteria_config"])

                conn.execute("""
                    INSERT INTO recommendation_criteria (name, description, criteria_config, is_default)
                    VALUES (?, ?, ?, ?)
                """, [
                    preset["name"],
                    preset["description"],
                    criteria_json,
                    preset["is_default"]
                ])

                default_marker = "⭐" if preset["is_default"] else "  "
                logger.info(f"✅ {default_marker} Created preset: {preset['name']}")
                seeded_count += 1

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 Seeding Summary")
        logger.info("=" * 80)
        logger.info(f"✅ Created: {seeded_count}")
        logger.info(f"⏭️  Skipped: {skipped_count}")
        logger.info(f"📁 Total: {seeded_count + skipped_count}")
        logger.info("")
        logger.info("🎉 Recommendation preset seeding completed successfully!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Recommendation preset seeding failed: {str(e)}")
        raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed XILFTEN recommendation presets")
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
        seed_recommendations(conn, dry_run=args.dry_run)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
