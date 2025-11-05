"""
Recommendation Service.

Multi-criteria recommendation engine with weighted scoring.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import logging
from datetime import datetime
import time

from config.database import db_manager
from backend.models.recommendation import (
    CriteriaPresetCreate,
    CriteriaPresetUpdate,
    ScoredMedia,
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for recommendation generation and criteria management."""

    def __init__(self):
        """Initialize recommendation service."""
        self.db = db_manager

    # ========== Criteria Preset CRUD ==========

    def get_all_presets(self) -> List[Dict[str, Any]]:
        """
        Get all criteria presets.

        Returns:
            list: List of preset dictionaries
        """
        conn = self.db.get_duckdb_connection()

        result = conn.execute("""
            SELECT * FROM recommendation_criteria
            ORDER BY is_default DESC, use_count DESC, name
        """).fetchall()

        columns = [desc[0] for desc in conn.description]
        presets = [dict(zip(columns, row)) for row in result]

        # Convert types
        import json
        for preset in presets:
            for key, value in preset.items():
                if isinstance(value, UUID):
                    preset[key] = str(value)
                elif isinstance(value, datetime):
                    preset[key] = value.isoformat() + "Z"
                elif key == "criteria_config" and isinstance(value, str):
                    # Parse JSON string to dictionary
                    preset[key] = json.loads(value)

        return presets

    def get_preset_by_id(self, preset_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get preset by ID.

        Args:
            preset_id: Preset UUID

        Returns:
            dict: Preset data or None
        """
        conn = self.db.get_duckdb_connection()

        result = conn.execute(
            "SELECT * FROM recommendation_criteria WHERE id = ?",
            [str(preset_id)]
        ).fetchone()

        if not result:
            return None

        columns = [desc[0] for desc in conn.description]
        preset = dict(zip(columns, result))

        # Convert types
        import json
        for key, value in preset.items():
            if isinstance(value, UUID):
                preset[key] = str(value)
            elif isinstance(value, datetime):
                preset[key] = value.isoformat() + "Z"
            elif key == "criteria_config" and isinstance(value, str):
                # Parse JSON string to dictionary
                preset[key] = json.loads(value)

        return preset

    def create_preset(self, preset_data: CriteriaPresetCreate) -> Dict[str, Any]:
        """
        Create new criteria preset.

        Args:
            preset_data: Preset creation data

        Returns:
            dict: Created preset
        """
        conn = self.db.get_duckdb_connection()

        import json
        criteria_json = json.dumps(preset_data.criteria_config)

        result = conn.execute("""
            INSERT INTO recommendation_criteria (name, description, criteria_config, is_default)
            VALUES (?, ?, ?, ?)
            RETURNING id
        """, [
            preset_data.name,
            preset_data.description,
            criteria_json,
            preset_data.is_default
        ])

        preset_id = result.fetchone()[0]
        logger.info(f"Created criteria preset: {preset_id}")

        return self.get_preset_by_id(UUID(str(preset_id)))

    def update_preset(
        self,
        preset_id: UUID,
        updates: CriteriaPresetUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Update existing preset.

        Args:
            preset_id: Preset UUID
            updates: Fields to update

        Returns:
            dict: Updated preset or None
        """
        conn = self.db.get_duckdb_connection()

        # Check if exists
        existing = self.get_preset_by_id(preset_id)
        if not existing:
            return None

        update_dict = updates.model_dump(exclude_unset=True)
        if not update_dict:
            return existing

        # Handle JSON serialization
        if 'criteria_config' in update_dict:
            import json
            update_dict['criteria_config'] = json.dumps(update_dict['criteria_config'])

        set_clauses = [f"{col} = ?" for col in update_dict.keys()]
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values = list(update_dict.values())
        values.append(str(preset_id))

        query = f"""
            UPDATE recommendation_criteria
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """

        conn.execute(query, values)
        logger.info(f"Updated criteria preset: {preset_id}")

        return self.get_preset_by_id(preset_id)

    def delete_preset(self, preset_id: UUID) -> bool:
        """
        Delete preset.

        Args:
            preset_id: Preset UUID

        Returns:
            bool: True if deleted
        """
        conn = self.db.get_duckdb_connection()

        existing = self.get_preset_by_id(preset_id)
        if not existing:
            return False

        conn.execute(
            "DELETE FROM recommendation_criteria WHERE id = ?",
            [str(preset_id)]
        )

        logger.info(f"Deleted criteria preset: {preset_id}")
        return True

    def increment_use_count(self, preset_id: UUID):
        """
        Increment use count for a preset.

        Args:
            preset_id: Preset UUID
        """
        conn = self.db.get_duckdb_connection()

        conn.execute("""
            UPDATE recommendation_criteria
            SET use_count = use_count + 1
            WHERE id = ?
        """, [str(preset_id)])

    def seed_default_presets(self):
        """
        Seed database with default criteria presets if none exist.

        This is called automatically on server startup to ensure defaults are available.
        """
        conn = self.db.get_duckdb_connection()

        # Check if any presets exist
        count = conn.execute("SELECT COUNT(*) FROM recommendation_criteria").fetchone()[0]

        if count > 0:
            logger.info(f"Recommendation presets already seeded ({count} presets found)")
            return

        logger.info("No recommendation presets found, seeding defaults...")

        default_presets = [
            {
                "name": "High Quality Sci-Fi",
                "description": "Top-rated science fiction films with strong ratings and popularity",
                "is_default": True,
                "criteria_config": {
                    "genres": {"weight": 0.9, "values": ["sci-fi", "cyberpunk", "space-opera", "dystopian", "hard-sci-fi"]},
                    "tmdb_rating": {"weight": 0.8, "min": 7.0},
                    "popularity_score": {"weight": 0.3, "min": 50.0},
                    "runtime": {"weight": 0.2, "min": 90, "max": 180}
                }
            },
            {
                "name": "Friday Night Action",
                "description": "High-energy action films perfect for weekend entertainment",
                "is_default": True,
                "criteria_config": {
                    "genres": {"weight": 1.0, "values": ["action", "action-comedy", "superhero", "spy-espionage"]},
                    "tmdb_rating": {"weight": 0.5, "min": 6.5},
                    "runtime": {"weight": 0.3, "min": 90, "max": 150},
                    "maturity_rating": {"weight": 0.2, "values": ["PG-13", "R"]}
                }
            },
            {
                "name": "Hidden Gems",
                "description": "High-quality but less popular films that deserve more attention",
                "is_default": False,
                "criteria_config": {
                    "tmdb_rating": {"weight": 1.0, "min": 7.5},
                    "popularity_score": {"weight": 0.8, "max": 100.0}
                }
            },
        ]

        for preset_data in default_presets:
            try:
                preset_create = CriteriaPresetCreate(**preset_data)
                self.create_preset(preset_create)
                logger.info(f"✅ Seeded preset: {preset_data['name']}")
            except Exception as e:
                logger.error(f"Failed to seed preset '{preset_data['name']}': {str(e)}")

        logger.info(f"Seeded {len(default_presets)} default recommendation presets")

    # ========== Recommendation Generation ==========

    def generate_recommendations(
        self,
        criteria_config: Dict[str, Dict[str, Any]],
        limit: int = 10,
        exclude_ids: Optional[List[UUID]] = None,
        min_score: Optional[float] = None
    ) -> Tuple[List[ScoredMedia], int, float]:
        """
        Generate recommendations using multi-criteria scoring.

        Args:
            criteria_config: Criteria configuration dictionary
            limit: Maximum number of results
            exclude_ids: Media IDs to exclude
            min_score: Minimum score threshold

        Returns:
            tuple: (scored_media_list, total_candidates, execution_time_ms)
        """
        start_time = time.time()

        conn = self.db.get_duckdb_connection()

        # Get all media from database
        query = "SELECT * FROM media"
        params = []

        if exclude_ids:
            placeholders = ','.join(['?' for _ in exclude_ids])
            query += f" WHERE id NOT IN ({placeholders})"
            params = [str(id) for id in exclude_ids]

        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]
        media_list = [dict(zip(columns, row)) for row in result]

        total_candidates = len(media_list)
        logger.info(f"Evaluating {total_candidates} media items against criteria")

        # Score each media item
        scored_items = []
        for media in media_list:
            score, breakdown, matched = self._score_media(media, criteria_config)

            # Apply minimum score filter
            if min_score is not None and score < min_score:
                continue

            scored_items.append(ScoredMedia(
                media=self._serialize_media(media),
                score=score,
                score_breakdown=breakdown,
                matched_criteria=matched
            ))

        # Sort by score (descending)
        scored_items.sort(key=lambda x: x.score, reverse=True)

        # Limit results
        scored_items = scored_items[:limit]

        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        logger.info(
            f"Generated {len(scored_items)} recommendations in {execution_time:.2f}ms"
        )

        return scored_items, total_candidates, execution_time

    def _score_media(
        self,
        media: Dict[str, Any],
        criteria_config: Dict[str, Dict[str, Any]]
    ) -> Tuple[float, Dict[str, float], List[str]]:
        """
        Calculate weighted score for a media item against criteria.

        Args:
            media: Media dictionary
            criteria_config: Criteria configuration

        Returns:
            tuple: (total_score, score_breakdown, matched_criteria)
        """
        total_weight = 0.0
        weighted_score = 0.0
        score_breakdown = {}
        matched_criteria = []

        for criterion_name, criterion_config in criteria_config.items():
            weight = criterion_config.get('weight', 0.5)

            # Get criterion score (0-1)
            criterion_score = self._evaluate_criterion(
                media,
                criterion_name,
                criterion_config
            )

            if criterion_score is not None:
                total_weight += weight
                weighted_score += criterion_score * weight
                score_breakdown[criterion_name] = criterion_score

                if criterion_score > 0.5:  # Threshold for "matched"
                    matched_criteria.append(criterion_name)

        # Normalize final score
        final_score = weighted_score / total_weight if total_weight > 0 else 0.0

        return final_score, score_breakdown, matched_criteria

    def _evaluate_criterion(
        self,
        media: Dict[str, Any],
        criterion_name: str,
        criterion_config: Dict[str, Any]
    ) -> Optional[float]:
        """
        Evaluate a single criterion for a media item.

        Returns score between 0 and 1, or None if criterion doesn't apply.

        Args:
            media: Media dictionary
            criterion_name: Name of criterion
            criterion_config: Criterion configuration

        Returns:
            float: Score (0-1) or None
        """
        # Map criterion names to media fields
        field_value = media.get(criterion_name)

        if field_value is None:
            return None

        # Handle different criterion types
        if 'values' in criterion_config:
            # Categorical match (exact match)
            acceptable_values = criterion_config['values']
            if field_value in acceptable_values:
                return 1.0
            else:
                return 0.0

        elif 'value' in criterion_config:
            # Exact value match
            if field_value == criterion_config['value']:
                return 1.0
            else:
                return 0.0

        elif 'min' in criterion_config or 'max' in criterion_config:
            # Numeric range
            min_val = criterion_config.get('min')
            max_val = criterion_config.get('max')

            try:
                numeric_value = float(field_value)

                if min_val is not None and max_val is not None:
                    # Both bounds specified
                    if min_val <= numeric_value <= max_val:
                        # Linear scoring within range
                        range_width = max_val - min_val
                        if range_width > 0:
                            # Score closer to midpoint higher
                            midpoint = (min_val + max_val) / 2
                            distance_from_mid = abs(numeric_value - midpoint)
                            score = 1.0 - (distance_from_mid / (range_width / 2))
                            return max(0.0, min(1.0, score))
                        else:
                            return 1.0
                    else:
                        return 0.0

                elif min_val is not None:
                    # Only minimum specified
                    if numeric_value >= min_val:
                        # Normalized score (diminishing returns above threshold)
                        excess = numeric_value - min_val
                        return min(1.0, 0.7 + (excess / (min_val * 2)))
                    else:
                        # Penalty for being below minimum
                        deficit = min_val - numeric_value
                        return max(0.0, 1.0 - (deficit / min_val))

                elif max_val is not None:
                    # Only maximum specified
                    if numeric_value <= max_val:
                        return 1.0
                    else:
                        # Penalty for exceeding maximum
                        excess = numeric_value - max_val
                        return max(0.0, 1.0 - (excess / max_val))

            except (ValueError, TypeError):
                return None

        return None

    def _serialize_media(self, media: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize media dictionary (convert UUIDs, dates, etc.).

        Args:
            media: Media dictionary

        Returns:
            dict: Serialized media
        """
        serialized = {}
        for key, value in media.items():
            if isinstance(value, UUID):
                serialized[key] = str(value)
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat() + "Z"
            else:
                serialized[key] = value

        return serialized


# Singleton instance
recommendation_service = RecommendationService()
