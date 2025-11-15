"""
Audio Service

Manages audio content (albums, singles), artists, tracks, and audio genres.
Provides CRUD operations for the audio catalog system.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import json

from backend.services.database_service import get_database_service

logger = logging.getLogger(__name__)


class AudioService:
    """Service for managing audio catalog data."""

    def __init__(self):
        """Initialize audio service."""
        self.db_service = get_database_service()

    def get_connection(self):
        """Get database connection."""
        return self.db_service.get_connection()

    # ========================================================================
    # AUDIO GENRE OPERATIONS
    # ========================================================================

    def create_audio_genre(self, genre_data: Dict[str, Any]) -> str:
        """
        Create a new audio genre.

        Args:
            genre_data (Dict): Genre data (name, slug, description, etc.)

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
            INSERT INTO audio_genres ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        conn.execute(query, [genre_data[col] for col in columns])
        logger.info(f"Created audio genre: {genre_data['name']}")

        return genre_data['id']

    def get_audio_genre(self, genre_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audio genre by ID.

        Args:
            genre_id (str): Genre UUID

        Returns:
            Optional[Dict]: Genre data or None
        """
        conn = self.get_connection()

        result = conn.execute(
            "SELECT * FROM audio_genres WHERE id = ?",
            [genre_id]
        ).fetchone()

        if result:
            columns = [desc[0] for desc in conn.description]
            return dict(zip(columns, result))

        return None

    def list_audio_genres(
        self,
        parent_genre_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List audio genres.

        Args:
            parent_genre_id (str, optional): Filter by parent genre (None = top-level only)

        Returns:
            List[Dict]: List of genres
        """
        conn = self.get_connection()

        if parent_genre_id is not None:
            query = """
                SELECT * FROM audio_genres
                WHERE parent_genre_id = ?
                ORDER BY name
            """
            params = [parent_genre_id]
        else:
            query = """
                SELECT * FROM audio_genres
                WHERE parent_genre_id IS NULL
                ORDER BY name
            """
            params = []

        result = conn.execute(query, params).fetchall()

        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]

    def update_audio_genre(
        self,
        genre_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update audio genre.

        Args:
            genre_id (str): Genre UUID
            updates (Dict): Fields to update

        Returns:
            bool: True if updated successfully
        """
        conn = self.get_connection()

        updates['updated_at'] = datetime.utcnow()

        set_clauses = [f"{key} = ?" for key in updates.keys()]
        values = list(updates.values())
        values.append(genre_id)

        query = f"""
            UPDATE audio_genres
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """

        result = conn.execute(query, values)
        logger.info(f"Updated audio genre: {genre_id}")

        return result.rowcount > 0

    def delete_audio_genre(self, genre_id: str) -> bool:
        """
        Delete audio genre.

        Args:
            genre_id (str): Genre UUID

        Returns:
            bool: True if deleted successfully
        """
        conn = self.get_connection()

        result = conn.execute(
            "DELETE FROM audio_genres WHERE id = ?",
            [genre_id]
        )

        logger.info(f"Deleted audio genre: {genre_id}")
        return result.rowcount > 0

    # ========================================================================
    # ARTIST OPERATIONS
    # ========================================================================

    def create_artist(self, artist_data: Dict[str, Any]) -> str:
        """
        Create a new artist.

        Args:
            artist_data (Dict): Artist data

        Returns:
            str: ID of created artist
        """
        conn = self.get_connection()

        if 'id' not in artist_data:
            import uuid
            artist_data['id'] = str(uuid.uuid4())

        columns = list(artist_data.keys())
        placeholders = ['?' for _ in columns]

        query = f"""
            INSERT INTO artists ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        conn.execute(query, [artist_data[col] for col in columns])
        logger.info(f"Created artist: {artist_data['name']}")

        return artist_data['id']

    def get_artist(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """
        Get artist by ID.

        Args:
            artist_id (str): Artist UUID

        Returns:
            Optional[Dict]: Artist data or None
        """
        conn = self.get_connection()

        result = conn.execute(
            "SELECT * FROM artists WHERE id = ?",
            [artist_id]
        ).fetchone()

        if result:
            columns = [desc[0] for desc in conn.description]
            return dict(zip(columns, result))

        return None

    def list_artists(
        self,
        limit: int = 20,
        offset: int = 0,
        artist_type: Optional[str] = None,
        country: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        List artists with pagination and filters.

        Args:
            limit (int): Number of results per page
            offset (int): Offset for pagination
            artist_type (str, optional): Filter by artist type
            country (str, optional): Filter by country code
            sort_by (str): Sort field (default: name)
            sort_order (str): Sort order (asc/desc)

        Returns:
            Dict: {'items': [...], 'total': int}
        """
        conn = self.get_connection()

        where_clauses = []
        params = []

        if artist_type:
            where_clauses.append("artist_type = ?")
            params.append(artist_type)

        if country:
            where_clauses.append("country = ?")
            params.append(country)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Count total
        count_query = f"SELECT COUNT(*) FROM artists {where_sql}"
        total = conn.execute(count_query, params).fetchone()[0]

        # Validate sort fields
        valid_sorts = ["name", "sort_name", "created_at", "spotify_popularity"]
        if sort_by not in valid_sorts:
            sort_by = "name"

        order_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        # Get items
        query = f"""
            SELECT * FROM artists
            {where_sql}
            ORDER BY {sort_by} {order_direction}
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        result = conn.execute(query, params).fetchall()

        columns = [desc[0] for desc in conn.description]
        items = [dict(zip(columns, row)) for row in result]

        return {
            'items': items,
            'total': total
        }

    def update_artist(
        self,
        artist_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update artist.

        Args:
            artist_id (str): Artist UUID
            updates (Dict): Fields to update

        Returns:
            bool: True if updated successfully
        """
        conn = self.get_connection()

        updates['updated_at'] = datetime.utcnow()

        set_clauses = [f"{key} = ?" for key in updates.keys()]
        values = list(updates.values())
        values.append(artist_id)

        query = f"""
            UPDATE artists
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """

        result = conn.execute(query, values)
        logger.info(f"Updated artist: {artist_id}")

        return result.rowcount > 0

    def delete_artist(self, artist_id: str) -> bool:
        """
        Delete artist.

        Args:
            artist_id (str): Artist UUID

        Returns:
            bool: True if deleted successfully
        """
        conn = self.get_connection()

        result = conn.execute(
            "DELETE FROM artists WHERE id = ?",
            [artist_id]
        )

        logger.info(f"Deleted artist: {artist_id}")
        return result.rowcount > 0

    # ========================================================================
    # AUDIO CONTENT OPERATIONS (Albums, Singles, EPs)
    # ========================================================================

    def create_audio_content(self, content_data: Dict[str, Any]) -> str:
        """
        Create audio content (album, single, EP, etc.).

        Args:
            content_data (Dict): Audio content data

        Returns:
            str: ID of created audio content
        """
        conn = self.get_connection()

        if 'id' not in content_data:
            import uuid
            content_data['id'] = str(uuid.uuid4())

        columns = list(content_data.keys())
        placeholders = ['?' for _ in columns]

        query = f"""
            INSERT INTO audio_content ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        conn.execute(query, [content_data[col] for col in columns])
        logger.info(f"Created audio content: {content_data['title']}")

        return content_data['id']

    def get_audio_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audio content by ID.

        Args:
            content_id (str): Audio content UUID

        Returns:
            Optional[Dict]: Audio content data or None
        """
        conn = self.get_connection()

        result = conn.execute(
            "SELECT * FROM audio_content WHERE id = ?",
            [content_id]
        ).fetchone()

        if result:
            columns = [desc[0] for desc in conn.description]
            content = dict(zip(columns, result))

            # Get primary artist
            content['primary_artist'] = self.get_artist(content['primary_artist_id'])

            # Get genres
            content['genres'] = self._get_audio_content_genres(conn, content_id)

            # Get all artists (including featured, etc.)
            content['artists'] = self._get_audio_content_artists(conn, content_id)

            return content

        return None

    def list_audio_content(
        self,
        limit: int = 20,
        offset: int = 0,
        content_type: Optional[str] = None,
        artist_id: Optional[str] = None,
        genre_id: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        sort_by: str = "title",
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        List audio content with pagination and filters.

        Args:
            limit (int): Number of results per page
            offset (int): Offset for pagination
            content_type (str, optional): Filter by content type
            artist_id (str, optional): Filter by artist
            genre_id (str, optional): Filter by genre
            year_from (int, optional): Filter by release year (from)
            year_to (int, optional): Filter by release year (to)
            sort_by (str): Sort field
            sort_order (str): Sort order (asc/desc)

        Returns:
            Dict: {'items': [...], 'total': int}
        """
        conn = self.get_connection()

        where_clauses = []
        params = []

        if content_type:
            where_clauses.append("ac.content_type = ?")
            params.append(content_type)

        if artist_id:
            where_clauses.append("ac.primary_artist_id = ?")
            params.append(artist_id)

        if genre_id:
            where_clauses.append(
                "ac.id IN (SELECT audio_content_id FROM audio_content_genres WHERE genre_id = ?)"
            )
            params.append(genre_id)

        if year_from:
            where_clauses.append("ac.release_year >= ?")
            params.append(year_from)

        if year_to:
            where_clauses.append("ac.release_year <= ?")
            params.append(year_to)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Count total
        count_query = f"SELECT COUNT(*) FROM audio_content ac {where_sql}"
        total = conn.execute(count_query, params).fetchone()[0]

        # Validate sort fields
        valid_sorts = ["title", "release_date", "release_year", "created_at", "spotify_popularity"]
        if sort_by not in valid_sorts:
            sort_by = "title"

        order_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        # Get items
        query = f"""
            SELECT ac.* FROM audio_content ac
            {where_sql}
            ORDER BY ac.{sort_by} {order_direction}
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        result = conn.execute(query, params).fetchall()

        columns = [desc[0] for desc in conn.description]
        items = []
        for row in result:
            content = dict(zip(columns, row))

            # Get primary artist
            content['primary_artist'] = self.get_artist(content['primary_artist_id'])

            # Get genres
            content['genres'] = self._get_audio_content_genres(conn, content['id'])

            items.append(content)

        return {
            'items': items,
            'total': total
        }

    def _get_audio_content_genres(
        self,
        conn,
        content_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get genres for audio content.

        Args:
            conn: Database connection
            content_id (str): Audio content UUID

        Returns:
            List[Dict]: List of genre dictionaries
        """
        query = """
            SELECT g.id, g.name, g.slug, g.description
            FROM audio_genres g
            INNER JOIN audio_content_genres acg ON g.id = acg.genre_id
            WHERE acg.audio_content_id = ?
            ORDER BY g.name
        """

        result = conn.execute(query, [content_id]).fetchall()

        genres = []
        for row in result:
            genres.append({
                'id': row[0],
                'name': row[1],
                'slug': row[2],
                'description': row[3]
            })

        return genres

    def _get_audio_content_artists(
        self,
        conn,
        content_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all artists for audio content (including featured, etc.).

        Args:
            conn: Database connection
            content_id (str): Audio content UUID

        Returns:
            List[Dict]: List of artist dictionaries with role
        """
        query = """
            SELECT a.*, aa.role, aa.display_order
            FROM artists a
            INNER JOIN audio_artists aa ON a.id = aa.artist_id
            WHERE aa.audio_content_id = ?
            ORDER BY aa.display_order, a.name
        """

        result = conn.execute(query, [content_id]).fetchall()

        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]

    def update_audio_content(
        self,
        content_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update audio content.

        Args:
            content_id (str): Audio content UUID
            updates (Dict): Fields to update

        Returns:
            bool: True if updated successfully
        """
        conn = self.get_connection()

        updates['updated_at'] = datetime.utcnow()

        set_clauses = [f"{key} = ?" for key in updates.keys()]
        values = list(updates.values())
        values.append(content_id)

        query = f"""
            UPDATE audio_content
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """

        result = conn.execute(query, values)
        logger.info(f"Updated audio content: {content_id}")

        return result.rowcount > 0

    def delete_audio_content(self, content_id: str) -> bool:
        """
        Delete audio content.

        Args:
            content_id (str): Audio content UUID

        Returns:
            bool: True if deleted successfully
        """
        conn = self.get_connection()

        result = conn.execute(
            "DELETE FROM audio_content WHERE id = ?",
            [content_id]
        )

        logger.info(f"Deleted audio content: {content_id}")
        return result.rowcount > 0

    def add_genre_to_content(
        self,
        content_id: str,
        genre_id: str,
        relevance_score: float = 1.0
    ) -> bool:
        """
        Associate genre with audio content.

        Args:
            content_id (str): Audio content UUID
            genre_id (str): Genre UUID
            relevance_score (float): Relevance score (0.0-1.0)

        Returns:
            bool: True if added successfully
        """
        conn = self.get_connection()

        try:
            conn.execute(
                """
                INSERT INTO audio_content_genres (audio_content_id, genre_id, relevance_score)
                VALUES (?, ?, ?)
                """,
                [content_id, genre_id, relevance_score]
            )
            logger.info(f"Added genre {genre_id} to content {content_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding genre to content: {e}")
            return False

    # ========================================================================
    # AUDIO TRACK OPERATIONS
    # ========================================================================

    def create_audio_track(self, track_data: Dict[str, Any]) -> str:
        """
        Create audio track.

        Args:
            track_data (Dict): Track data

        Returns:
            str: ID of created track
        """
        conn = self.get_connection()

        if 'id' not in track_data:
            import uuid
            track_data['id'] = str(uuid.uuid4())

        columns = list(track_data.keys())
        placeholders = ['?' for _ in columns]

        query = f"""
            INSERT INTO audio_tracks ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        conn.execute(query, [track_data[col] for col in columns])
        logger.info(f"Created audio track: {track_data['title']}")

        return track_data['id']

    def get_audio_track(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audio track by ID.

        Args:
            track_id (str): Track UUID

        Returns:
            Optional[Dict]: Track data or None
        """
        conn = self.get_connection()

        result = conn.execute(
            "SELECT * FROM audio_tracks WHERE id = ?",
            [track_id]
        ).fetchone()

        if result:
            columns = [desc[0] for desc in conn.description]
            return dict(zip(columns, result))

        return None

    def list_tracks_by_content(
        self,
        audio_content_id: str
    ) -> List[Dict[str, Any]]:
        """
        List tracks for an audio content (album/single).

        Args:
            audio_content_id (str): Audio content UUID

        Returns:
            List[Dict]: List of tracks
        """
        conn = self.get_connection()

        query = """
            SELECT * FROM audio_tracks
            WHERE audio_content_id = ?
            ORDER BY disc_number, track_number
        """

        result = conn.execute(query, [audio_content_id]).fetchall()

        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]

    def update_audio_track(
        self,
        track_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update audio track.

        Args:
            track_id (str): Track UUID
            updates (Dict): Fields to update

        Returns:
            bool: True if updated successfully
        """
        conn = self.get_connection()

        updates['updated_at'] = datetime.utcnow()

        set_clauses = [f"{key} = ?" for key in updates.keys()]
        values = list(updates.values())
        values.append(track_id)

        query = f"""
            UPDATE audio_tracks
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """

        result = conn.execute(query, values)
        logger.info(f"Updated audio track: {track_id}")

        return result.rowcount > 0

    def delete_audio_track(self, track_id: str) -> bool:
        """
        Delete audio track.

        Args:
            track_id (str): Track UUID

        Returns:
            bool: True if deleted successfully
        """
        conn = self.get_connection()

        result = conn.execute(
            "DELETE FROM audio_tracks WHERE id = ?",
            [track_id]
        )

        logger.info(f"Deleted audio track: {track_id}")
        return result.rowcount > 0


# Global service instance
_audio_service: Optional[AudioService] = None


def get_audio_service() -> AudioService:
    """
    Get or create global audio service instance.

    Returns:
        AudioService: Global service instance
    """
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService()
    return _audio_service
