"""
Review Service.

Service layer for managing user reviews and ratings.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import logging
from datetime import date
import json

from config.database import db_manager
from backend.models.review import (
    ReviewCreate,
    ReviewUpdate,
)

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for review and rating management."""

    def __init__(self):
        """Initialize review service."""
        self.db = db_manager

    # ========== Review CRUD ==========

    def get_all_reviews(
        self,
        media_id: Optional[UUID] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get all reviews with optional filters.

        Args:
            media_id: Filter by media ID
            min_rating: Minimum rating filter
            max_rating: Maximum rating filter
            start_date: Filter reviews after this date
            end_date: Filter reviews before this date
            tags: Filter by tags (any match)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            tuple: (reviews list, total count)
        """
        conn = self.db.get_duckdb_connection()

        # Build WHERE clause
        where_clauses = []
        params = []

        if media_id:
            where_clauses.append("media_id = ?")
            params.append(str(media_id))

        if min_rating is not None:
            where_clauses.append("rating >= ?")
            params.append(min_rating)

        if max_rating is not None:
            where_clauses.append("rating <= ?")
            params.append(max_rating)

        if start_date:
            where_clauses.append("watched_date >= ?")
            params.append(str(start_date))

        if end_date:
            where_clauses.append("watched_date <= ?")
            params.append(str(end_date))

        # Note: Tag filtering with JSON would need DuckDB JSON functions
        # For now, we'll filter in Python if tags are provided

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        count_query = f"SELECT COUNT(*) FROM user_reviews WHERE {where_sql}"
        total = conn.execute(count_query, params).fetchone()[0]

        # Get reviews
        query = f"""
            SELECT * FROM user_reviews
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]
        reviews = [dict(zip(columns, row)) for row in result]

        # Filter by tags if provided
        if tags:
            reviews = [r for r in reviews if self._has_any_tag(r.get('tags'), tags)]

        # Convert types
        reviews = [self._serialize_review(review) for review in reviews]

        return reviews, total

    def get_review_by_id(self, review_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get review by ID.

        Args:
            review_id: Review UUID

        Returns:
            dict: Review data or None
        """
        conn = self.db.get_duckdb_connection()

        result = conn.execute(
            "SELECT * FROM user_reviews WHERE id = ?",
            [str(review_id)]
        ).fetchone()

        if not result:
            return None

        columns = [desc[0] for desc in conn.description]
        review = dict(zip(columns, result))

        return self._serialize_review(review)

    def create_review(self, review_data: ReviewCreate) -> Dict[str, Any]:
        """
        Create new review.

        Args:
            review_data: Review creation data

        Returns:
            dict: Created review
        """
        conn = self.db.get_duckdb_connection()

        # Serialize tags to JSON
        tags_json = json.dumps(review_data.tags) if review_data.tags else None

        result = conn.execute("""
            INSERT INTO user_reviews (
                media_id, rating, review_text,
                watched_date, rewatch_count, tags
            )
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id
        """, [
            str(review_data.media_id),
            review_data.rating,
            review_data.review_text,
            str(review_data.watched_date) if review_data.watched_date else None,
            review_data.rewatch_count,
            tags_json
        ])

        review_id = result.fetchone()[0]
        logger.info(f"Created review: {review_id}")

        return self.get_review_by_id(UUID(str(review_id)))

    def update_review(
        self,
        review_id: UUID,
        updates: ReviewUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Update existing review.

        Args:
            review_id: Review UUID
            updates: Fields to update

        Returns:
            dict: Updated review or None
        """
        conn = self.db.get_duckdb_connection()

        # Check if exists
        existing = self.get_review_by_id(review_id)
        if not existing:
            return None

        update_dict = updates.model_dump(exclude_unset=True)
        if not update_dict:
            return existing

        # Handle tags JSON serialization
        if 'tags' in update_dict and update_dict['tags'] is not None:
            update_dict['tags'] = json.dumps(update_dict['tags'])

        # Build SET clause
        set_clauses = []
        values = []

        for key, value in update_dict.items():
            if value is not None and isinstance(value, date):
                value = str(value)

            set_clauses.append(f"{key} = ?")
            values.append(value)

        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(str(review_id))

        query = f"""
            UPDATE user_reviews
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """

        conn.execute(query, values)
        logger.info(f"Updated review: {review_id}")

        return self.get_review_by_id(review_id)

    def delete_review(self, review_id: UUID) -> bool:
        """
        Delete review.

        Args:
            review_id: Review UUID

        Returns:
            bool: True if deleted
        """
        conn = self.db.get_duckdb_connection()

        existing = self.get_review_by_id(review_id)
        if not existing:
            return False

        conn.execute(
            "DELETE FROM user_reviews WHERE id = ?",
            [str(review_id)]
        )

        logger.info(f"Deleted review: {review_id}")
        return True

    # ========== Review Statistics ==========

    def get_media_reviews(self, media_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all reviews for a specific media item.

        Args:
            media_id: Media UUID

        Returns:
            list: Reviews for the media
        """
        reviews, _ = self.get_all_reviews(media_id=media_id, limit=1000)
        return reviews

    def get_review_stats(self, media_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Get review statistics.

        Args:
            media_id: Optional media ID to filter by

        Returns:
            dict: Review statistics
        """
        conn = self.db.get_duckdb_connection()

        where_clause = "WHERE media_id = ?" if media_id else ""
        params = [str(media_id)] if media_id else []

        # Get basic stats
        stats_query = f"""
            SELECT
                COUNT(*) as total_reviews,
                AVG(rating) as average_rating,
                SUM(rewatch_count) as total_rewatches
            FROM user_reviews
            {where_clause}
        """

        result = conn.execute(stats_query, params).fetchone()
        total_reviews, average_rating, total_rewatches = result

        # Get rating distribution
        dist_query = f"""
            SELECT
                CASE
                    WHEN rating < 2 THEN '0-2'
                    WHEN rating < 4 THEN '2-4'
                    WHEN rating < 6 THEN '4-6'
                    WHEN rating < 8 THEN '6-8'
                    ELSE '8-10'
                END as rating_range,
                COUNT(*) as count
            FROM user_reviews
            {where_clause}
            GROUP BY rating_range
            ORDER BY rating_range
        """

        dist_result = conn.execute(dist_query, params).fetchall()
        rating_distribution = {row[0]: row[1] for row in dist_result}

        # Get most common tags (needs JSON parsing)
        # For now, return empty list
        most_common_tags = []

        return {
            "total_reviews": total_reviews or 0,
            "average_rating": round(average_rating, 2) if average_rating else None,
            "rating_distribution": rating_distribution,
            "most_common_tags": most_common_tags,
            "total_rewatches": total_rewatches or 0
        }

    # ========== Helper Methods ==========

    def _serialize_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize review dictionary (convert UUIDs, dates, parse JSON).

        Args:
            review: Review dictionary

        Returns:
            dict: Serialized review
        """
        from datetime import datetime

        serialized = {}
        for key, value in review.items():
            if isinstance(value, UUID):
                serialized[key] = str(value)
            elif isinstance(value, (datetime, date)):
                serialized[key] = value.isoformat() if value else None
            elif key == 'tags' and isinstance(value, str):
                # Parse JSON tags
                try:
                    serialized[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    serialized[key] = []
            else:
                serialized[key] = value

        return serialized

    def _has_any_tag(self, review_tags: Any, filter_tags: List[str]) -> bool:
        """
        Check if review has any of the filter tags.

        Args:
            review_tags: Review tags (could be string JSON or list)
            filter_tags: Tags to filter by

        Returns:
            bool: True if any tag matches
        """
        if not review_tags or not filter_tags:
            return False

        # Parse tags if string
        if isinstance(review_tags, str):
            try:
                review_tags = json.loads(review_tags)
            except (json.JSONDecodeError, TypeError):
                return False

        if not isinstance(review_tags, list):
            return False

        return any(tag in filter_tags for tag in review_tags)


# Singleton instance
review_service = ReviewService()
