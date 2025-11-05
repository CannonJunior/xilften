"""
Genre Service

Manages genre taxonomy including seeding and retrieval operations.
"""

import logging
from typing import List, Dict, Any, Optional
import uuid

from backend.services.database_service import get_database_service

logger = logging.getLogger(__name__)


# ============================================================================
# GENRE TAXONOMY DEFINITIONS
# ============================================================================

# Film Noir (10 sub-genres)
FILM_NOIR_SUBGENRES = [
    {"name": "Classic Noir", "slug": "classic-noir", "description": "Traditional noir films from the 1940s-1950s"},
    {"name": "Neo-Noir", "slug": "neo-noir", "description": "Modern interpretations of noir themes"},
    {"name": "Tech Noir", "slug": "tech-noir", "description": "Noir combined with science fiction and technology"},
    {"name": "Erotic Noir", "slug": "erotic-noir", "description": "Noir with strong erotic or sexual themes"},
    {"name": "Sci-Fi Noir", "slug": "sci-fi-noir", "description": "Noir set in futuristic or science fiction settings"},
    {"name": "Horror Noir", "slug": "horror-noir", "description": "Noir blended with horror elements"},
    {"name": "Comedy Noir", "slug": "comedy-noir", "description": "Noir with comedic or satirical elements"},
    {"name": "Psychological Noir", "slug": "psychological-noir", "description": "Focus on mental states and psychological tension"},
    {"name": "Period Noir", "slug": "period-noir", "description": "Noir set in specific historical periods"},
    {"name": "Action Noir", "slug": "action-noir", "description": "Noir with heavy action sequences"},
]

# Science Fiction (8 sub-genres)
SCIENCE_FICTION_SUBGENRES = [
    {"name": "Hard Sci-Fi", "slug": "hard-sci-fi", "description": "Scientific accuracy and technical detail"},
    {"name": "Space Opera", "slug": "space-opera", "description": "Epic adventures in space"},
    {"name": "Cyberpunk", "slug": "cyberpunk", "description": "High tech, low life dystopian futures"},
    {"name": "Time Travel", "slug": "time-travel", "description": "Stories involving temporal mechanics"},
    {"name": "Post-Apocalyptic", "slug": "post-apocalyptic", "description": "Worlds after catastrophic events"},
    {"name": "Alien Invasion", "slug": "alien-invasion", "description": "Extraterrestrial encounters and conflicts"},
    {"name": "Dystopian", "slug": "dystopian", "description": "Oppressive societal structures"},
    {"name": "AI & Robotics", "slug": "ai-robotics", "description": "Artificial intelligence and robots"},
]

# Documentary (6 sub-genres)
DOCUMENTARY_SUBGENRES = [
    {"name": "True Crime", "slug": "true-crime-doc", "description": "Real criminal cases and investigations"},
    {"name": "Nature & Wildlife", "slug": "nature-wildlife", "description": "Natural world and animal life"},
    {"name": "Historical", "slug": "historical-doc", "description": "Historical events and figures"},
    {"name": "Political", "slug": "political-doc", "description": "Political systems and events"},
    {"name": "Social Issue", "slug": "social-issue-doc", "description": "Social problems and movements"},
    {"name": "Biographical", "slug": "biographical-doc", "description": "Real people's lives and achievements"},
]

# Comedy (8 sub-genres)
COMEDY_SUBGENRES = [
    {"name": "Romantic Comedy", "slug": "romantic-comedy", "description": "Romance with comedic elements"},
    {"name": "Dark Comedy", "slug": "dark-comedy", "description": "Humor derived from dark or morbid subjects"},
    {"name": "Satire", "slug": "satire", "description": "Comedic criticism of society"},
    {"name": "Slapstick", "slug": "slapstick", "description": "Physical comedy and exaggerated situations"},
    {"name": "Parody", "slug": "parody", "description": "Humorous imitation of other works"},
    {"name": "Sitcom Style", "slug": "sitcom-style", "description": "Situational comedy format"},
    {"name": "Cringe Comedy", "slug": "cringe-comedy", "description": "Humor from awkward situations"},
    {"name": "Absurdist", "slug": "absurdist", "description": "Illogical and nonsensical humor"},
]

# Anime (6 sub-genres)
ANIME_SUBGENRES = [
    {"name": "Shonen", "slug": "shonen", "description": "Action-oriented anime for young males"},
    {"name": "Shojo", "slug": "shojo", "description": "Romance and drama for young females"},
    {"name": "Seinen", "slug": "seinen", "description": "Mature themes for adult males"},
    {"name": "Mecha", "slug": "mecha", "description": "Giant robots and mechanical suits"},
    {"name": "Isekai", "slug": "isekai", "description": "Transported to another world"},
    {"name": "Slice of Life", "slug": "slice-of-life", "description": "Everyday life and experiences"},
]

# Action (5 sub-genres)
ACTION_SUBGENRES = [
    {"name": "Martial Arts", "slug": "martial-arts", "description": "Hand-to-hand combat and martial arts"},
    {"name": "Superhero", "slug": "superhero", "description": "Superpowered heroes and villains"},
    {"name": "Spy/Espionage", "slug": "spy-espionage", "description": "Secret agents and covert operations"},
    {"name": "Military", "slug": "military", "description": "Armed forces and warfare"},
    {"name": "Heist", "slug": "heist", "description": "Elaborate theft and robbery plots"},
]

# International Iranian Cinema (4 sub-genres)
IRANIAN_CINEMA_SUBGENRES = [
    {"name": "Social Realism", "slug": "iranian-social-realism", "description": "Realistic portrayal of Iranian society"},
    {"name": "Poetic Cinema", "slug": "iranian-poetic", "description": "Artistic and symbolic storytelling"},
    {"name": "New Wave", "slug": "iranian-new-wave", "description": "Iranian New Wave movement"},
    {"name": "Historical Drama", "slug": "iranian-historical", "description": "Iranian historical narratives"},
]

# Main genre categories
GENRE_CATEGORIES = {
    "film-noir": {
        "name": "Film Noir",
        "slug": "film-noir",
        "description": "Dark, atmospheric crime dramas with moral ambiguity",
        "subgenres": FILM_NOIR_SUBGENRES,
    },
    "science-fiction": {
        "name": "Science Fiction",
        "slug": "science-fiction",
        "description": "Speculative fiction based on scientific concepts",
        "subgenres": SCIENCE_FICTION_SUBGENRES,
    },
    "documentary": {
        "name": "Documentary",
        "slug": "documentary",
        "description": "Non-fiction films documenting reality",
        "subgenres": DOCUMENTARY_SUBGENRES,
    },
    "comedy": {
        "name": "Comedy",
        "slug": "comedy",
        "description": "Films intended to provoke laughter",
        "subgenres": COMEDY_SUBGENRES,
    },
    "anime": {
        "name": "Anime",
        "slug": "anime",
        "description": "Japanese animation with diverse styles",
        "subgenres": ANIME_SUBGENRES,
    },
    "action": {
        "name": "Action",
        "slug": "action",
        "description": "High-energy physical feats and combat",
        "subgenres": ACTION_SUBGENRES,
    },
    "iranian-cinema": {
        "name": "International Iranian Cinema",
        "slug": "iranian-cinema",
        "description": "Films from Iran's rich cinematic tradition",
        "subgenres": IRANIAN_CINEMA_SUBGENRES,
    },
    "multi-genre": {
        "name": "Multi-Genre",
        "slug": "multi-genre",
        "description": "Films spanning multiple genres",
        "subgenres": [],  # No sub-genres for multi-genre
    },
}


class GenreService:
    """Service for managing genre taxonomy."""

    def __init__(self):
        """Initialize genre service."""
        self.db_service = get_database_service()

    def seed_genres(self, force: bool = False) -> Dict[str, Any]:
        """
        Seed genre taxonomy into database.

        Args:
            force (bool): If True, delete existing genres and reseed

        Returns:
            Dict: Result with counts of seeded genres
        """
        logger.info("🎭 Starting genre seeding process...")

        # Check if genres already exist
        existing = self.db_service.list_genres()
        if existing and not force:
            logger.info(f"✅ Genres already seeded ({len(existing)} genres found)")
            return {
                "success": True,
                "message": "Genres already seeded",
                "main_genres": len([g for g in existing if not g.get('parent_genre_id')]),
                "subgenres": len([g for g in existing if g.get('parent_genre_id')]),
                "total": len(existing),
            }

        if force and existing:
            logger.warning("⚠️  Force flag set - clearing existing genres")
            # TODO: Add delete_all_genres method if needed

        # Seed main genres and subgenres
        main_count = 0
        sub_count = 0

        for category_key, category_data in GENRE_CATEGORIES.items():
            # Create main genre
            main_genre_id = str(uuid.uuid4())
            genre_data = {
                "id": main_genre_id,
                "name": category_data["name"],
                "slug": category_data["slug"],
                "genre_category": category_key,
                "description": category_data["description"],
                "parent_genre_id": None,
                "is_active": True,
            }

            try:
                self.db_service.create_genre(genre_data)
                main_count += 1
                logger.info(f"  ✅ Created main genre: {category_data['name']}")
            except Exception as e:
                logger.error(f"  ❌ Failed to create genre {category_data['name']}: {e}")
                continue

            # Create subgenres
            for subgenre in category_data["subgenres"]:
                subgenre_data = {
                    "id": str(uuid.uuid4()),
                    "name": subgenre["name"],
                    "slug": subgenre["slug"],
                    "genre_category": category_key,
                    "description": subgenre.get("description"),
                    "parent_genre_id": main_genre_id,
                    "is_active": True,
                }

                try:
                    self.db_service.create_genre(subgenre_data)
                    sub_count += 1
                except Exception as e:
                    logger.error(f"    ❌ Failed to create subgenre {subgenre['name']}: {e}")

        logger.info("=" * 80)
        logger.info(f"✅ Genre seeding complete!")
        logger.info(f"  Main genres: {main_count}")
        logger.info(f"  Subgenres: {sub_count}")
        logger.info(f"  Total: {main_count + sub_count}")
        logger.info("=" * 80)

        return {
            "success": True,
            "message": "Genres seeded successfully",
            "main_genres": main_count,
            "subgenres": sub_count,
            "total": main_count + sub_count,
        }

    def get_genre_hierarchy(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get complete genre hierarchy organized by category.

        Returns:
            Dict: Genre hierarchy grouped by category
        """
        all_genres = self.db_service.list_genres()

        # Group by category
        hierarchy = {}
        for genre in all_genres:
            category = genre.get("genre_category", "other")
            if category not in hierarchy:
                hierarchy[category] = {
                    "main": None,
                    "subgenres": [],
                }

            if genre.get("parent_genre_id"):
                hierarchy[category]["subgenres"].append(genre)
            else:
                hierarchy[category]["main"] = genre

        return hierarchy

    def get_main_genres(self) -> List[Dict[str, Any]]:
        """
        Get all main genres (no parent).

        Returns:
            List[Dict]: Main genres
        """
        all_genres = self.db_service.list_genres()
        return [g for g in all_genres if not g.get("parent_genre_id")]

    def get_subgenres(self, parent_genre_id: str) -> List[Dict[str, Any]]:
        """
        Get subgenres for a specific parent genre.

        Args:
            parent_genre_id (str): Parent genre ID

        Returns:
            List[Dict]: Subgenres
        """
        all_genres = self.db_service.list_genres()
        return [g for g in all_genres if g.get("parent_genre_id") == parent_genre_id]

    def get_genres_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all genres in a specific category.

        Args:
            category (str): Genre category slug

        Returns:
            List[Dict]: Genres in category
        """
        return self.db_service.list_genres(category=category)

    def get_all_genres(
        self,
        category: Optional[str] = None,
        include_inactive: bool = False,
        parent_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all genres with optional filtering.

        Args:
            category (str, optional): Filter by genre category
            include_inactive (bool): Include inactive genres
            parent_only (bool): Only return parent genres (no sub-genres)

        Returns:
            List[Dict]: Filtered list of genres
        """
        # Get base list
        if category:
            genres = self.db_service.list_genres(category=category)
        else:
            genres = self.db_service.list_genres()

        # Apply filters
        filtered = genres

        if not include_inactive:
            filtered = [g for g in filtered if g.get("is_active", True)]

        if parent_only:
            filtered = [g for g in filtered if not g.get("parent_genre_id")]

        return filtered


# Global service instance
_genre_service: Optional[GenreService] = None


def get_genre_service() -> GenreService:
    """
    Get or create global genre service instance.

    Returns:
        GenreService: Global service instance
    """
    global _genre_service
    if _genre_service is None:
        _genre_service = GenreService()
    return _genre_service
