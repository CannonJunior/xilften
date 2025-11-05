"""
Database Service

Handles database operations for DuckDB including migrations and CRUD operations.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from config.database import db_manager

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations."""

    def __init__(self):
        """Initialize database service."""
        self.migrations_dir = Path(__file__).parent.parent.parent / "database" / "migrations"

    def get_connection(self):
        """Get DuckDB connection from manager."""
        return db_manager.get_duckdb_connection()

    def run_migrations(self):
        """Run all pending database migrations."""
        logger.info("🔄 Checking for pending migrations...")

        conn = self.get_connection()

        try:
            # Get applied migrations
            try:
                result = conn.execute(
                    "SELECT migration_name FROM migrations ORDER BY id"
                ).fetchall()
                applied = set(row[0] for row in result)
            except Exception:
                # Migrations table doesn't exist yet
                applied = set()

            # Find all migration files
            migration_files = sorted(self.migrations_dir.glob("*.sql"))

            pending = []
            for file_path in migration_files:
                migration_name = file_path.stem
                if migration_name not in applied:
                    pending.append((migration_name, file_path))

            if not pending:
                logger.info("✅ No pending migrations. Database is up to date.")
                return

            logger.info(f"Found {len(pending)} pending migration(s)")

            # Apply each migration
            for migration_name, file_path in pending:
                logger.info(f"  Applying migration: {migration_name}")
                sql = file_path.read_text()
                conn.execute(sql)
                logger.info(f"  ✅ Applied: {migration_name}")

            logger.info("✅ All migrations applied successfully!")

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise

    # ========================================================================
    # MEDIA CRUD OPERATIONS
    # ========================================================================

    def create_media(self, media_data: Dict[str, Any]) -> str:
        """
        Create a new media entry.

        Args:
            media_data (Dict): Media data

        Returns:
            str: ID of created media
        """
        conn = self.get_connection()

        # Generate ID if not provided
        if 'id' not in media_data:
            import uuid
            media_data['id'] = str(uuid.uuid4())

        # Convert JSON fields to strings
        if 'production_countries' in media_data and isinstance(media_data['production_countries'], (list, dict)):
            media_data['production_countries'] = json.dumps(media_data['production_countries'])

        if 'spoken_languages' in media_data and isinstance(media_data['spoken_languages'], (list, dict)):
            media_data['spoken_languages'] = json.dumps(media_data['spoken_languages'])

        if 'custom_fields' in media_data and isinstance(media_data['custom_fields'], dict):
            media_data['custom_fields'] = json.dumps(media_data['custom_fields'])

        # Build INSERT query
        columns = list(media_data.keys())
        placeholders = ['?' for _ in columns]

        query = f"""
            INSERT INTO media ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        conn.execute(query, [media_data[col] for col in columns])

        logger.info(f"Created media: {media_data['id']}")
        return media_data['id']

    def get_media(self, media_id: str) -> Optional[Dict[str, Any]]:
        """
        Get media by ID.

        Args:
            media_id (str): Media ID

        Returns:
            Optional[Dict]: Media data or None
        """
        conn = self.get_connection()

        result = conn.execute(
            "SELECT * FROM media WHERE id = ?",
            [media_id]
        ).fetchone()

        if result:
            columns = [desc[0] for desc in conn.description]
            media = dict(zip(columns, result))

            # Parse JSON fields
            for field in ['production_countries', 'spoken_languages', 'custom_fields']:
                if media.get(field):
                    try:
                        media[field] = json.loads(media[field])
                    except Exception:
                        pass

            return media

        return None

    def list_media(
        self,
        limit: int = 20,
        offset: int = 0,
        media_type: Optional[str] = None,
        genre_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        List media with pagination and filters.

        Args:
            limit (int): Number of results per page
            offset (int): Offset for pagination
            media_type (str, optional): Filter by media type
            genre_ids (List[str], optional): Filter by genre IDs

        Returns:
            Dict: {'items': [...], 'total': int}
        """
        conn = self.get_connection()

        # Build query
        where_clauses = []
        params = []

        if media_type:
            where_clauses.append("m.media_type = ?")
            params.append(media_type)

        if genre_ids:
            where_clauses.append(
                f"m.id IN (SELECT media_id FROM media_genres WHERE genre_id IN ({','.join('?' * len(genre_ids))}))"
            )
            params.extend(genre_ids)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Count total
        count_query = f"SELECT COUNT(*) FROM media m {where_sql}"
        total = conn.execute(count_query, params).fetchone()[0]

        # Get items
        query = f"""
            SELECT m.* FROM media m
            {where_sql}
            ORDER BY m.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        result = conn.execute(query, params).fetchall()

        columns = [desc[0] for desc in conn.description]
        items = []
        for row in result:
            media = dict(zip(columns, row))

            # Parse JSON fields
            for field in ['production_countries', 'spoken_languages', 'custom_fields']:
                if media.get(field):
                    try:
                        media[field] = json.loads(media[field])
                    except Exception:
                        pass

            items.append(media)

        return {
            'items': items,
            'total': total
        }

    def update_media(self, media_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update media entry.

        Args:
            media_id (str): Media ID
            updates (Dict): Fields to update

        Returns:
            bool: True if updated successfully
        """
        conn = self.get_connection()

        # Convert JSON fields
        for field in ['production_countries', 'spoken_languages', 'custom_fields']:
            if field in updates and isinstance(updates[field], (list, dict)):
                updates[field] = json.dumps(updates[field])

        # Add updated_at timestamp
        updates['updated_at'] = datetime.utcnow()

        # Build UPDATE query
        set_clauses = [f"{key} = ?" for key in updates.keys()]
        values = list(updates.values())
        values.append(media_id)

        query = f"""
            UPDATE media
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """

        result = conn.execute(query, values)

        logger.info(f"Updated media: {media_id}")
        return result.rowcount > 0

    def delete_media(self, media_id: str) -> bool:
        """
        Delete media entry.

        Args:
            media_id (str): Media ID

        Returns:
            bool: True if deleted successfully
        """
        conn = self.get_connection()

        result = conn.execute(
            "DELETE FROM media WHERE id = ?",
            [media_id]
        )

        logger.info(f"Deleted media: {media_id}")
        return result.rowcount > 0

    # ========================================================================
    # GENRE OPERATIONS
    # ========================================================================

    def create_genre(self, genre_data: Dict[str, Any]) -> str:
        """
        Create a new genre.

        Args:
            genre_data (Dict): Genre data

        Returns:
            str: ID of created genre
        """
        conn = self.get_connection()

        if 'id' not in genre_data:
            import uuid
            genre_data['id'] = str(uuid.uuid4())

        columns = list(genre_data.keys())
        placeholders = ['?' for _ in columns]

        query = f"""
            INSERT INTO genres ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        conn.execute(query, [genre_data[col] for col in columns])

        return genre_data['id']

    def list_genres(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all genres.

        Args:
            category (str, optional): Filter by genre category

        Returns:
            List[Dict]: List of genres
        """
        conn = self.get_connection()

        if category:
            query = "SELECT * FROM genres WHERE genre_category = ? ORDER BY name"
            params = [category]
        else:
            query = "SELECT * FROM genres ORDER BY genre_category, name"
            params = []

        result = conn.execute(query, params).fetchall()

        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]

    # ========================================================================
    # WATCH HISTORY OPERATIONS
    # ========================================================================

    def add_watch_history(self, history_data: Dict[str, Any]) -> str:
        """
        Add watch history entry.

        Args:
            history_data (Dict): Watch history data

        Returns:
            str: ID of created history entry
        """
        conn = self.get_connection()

        if 'id' not in history_data:
            import uuid
            history_data['id'] = str(uuid.uuid4())

        if 'watched_at' not in history_data:
            history_data['watched_at'] = datetime.utcnow()

        columns = list(history_data.keys())
        placeholders = ['?' for _ in columns]

        query = f"""
            INSERT INTO watch_history ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        conn.execute(query, [history_data[col] for col in columns])

        return history_data['id']

    def get_watch_history(
        self,
        media_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get watch history.

        Args:
            media_id (str, optional): Filter by media ID
            limit (int): Max number of results

        Returns:
            List[Dict]: Watch history entries
        """
        conn = self.get_connection()

        if media_id:
            query = """
                SELECT * FROM watch_history
                WHERE media_id = ?
                ORDER BY watched_at DESC
                LIMIT ?
            """
            params = [media_id, limit]
        else:
            query = """
                SELECT * FROM watch_history
                ORDER BY watched_at DESC
                LIMIT ?
            """
            params = [limit]

        result = conn.execute(query, params).fetchall()

        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]


# Global service instance
_database_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """
    Get or create global database service instance.

    Returns:
        DatabaseService: Global service instance
    """
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service
