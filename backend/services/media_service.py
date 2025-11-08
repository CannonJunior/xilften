"""
Media Service

Handles media CRUD operations, search, and TMDB integration.
"""

import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from backend.services.database_service import get_database_service
from backend.models.media import MediaFilters

logger = logging.getLogger(__name__)


class MediaService:
    """Service for managing media content."""

    def __init__(self):
        """Initialize media service."""
        self.db_service = get_database_service()

    def get_all_media(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[MediaFilters] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get paginated list of media with filtering and search.

        Args:
            page (int): Page number (1-indexed)
            page_size (int): Items per page
            filters (MediaFilters, optional): Filter criteria
            search (str, optional): Search query

        Returns:
            Dict: Paginated result with items, total, page info
        """
        offset = (page - 1) * page_size

        # Extract filter parameters
        media_type = filters.media_type if filters else None
        genre_ids = None

        # Convert genre slug to genre IDs if provided
        if filters and filters.genre:
            genre_ids = self._get_genre_ids_by_slug(filters.genre)

        # Get media from database
        result = self.db_service.list_media(
            limit=page_size,
            offset=offset,
            media_type=media_type,
            genre_ids=genre_ids
        )
        
        items = result['items']
        total = result['total']
        
        # Apply additional filters (rating, year, etc.)
        if filters:
            items = self._apply_filters(items, filters)
            total = len(items)  # Recalculate after filtering
        
        # Apply search
        if search:
            items = self._apply_search(items, search)
            total = len(items)
        
        # Apply sorting
        if filters and filters.sort_by:
            items = self._apply_sorting(items, filters.sort_by, filters.sort_order)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
        }

    def get_media_by_id(self, media_id) -> Optional[Dict[str, Any]]:
        """
        Get media by ID.

        Args:
            media_id: Media ID (str or UUID)

        Returns:
            Optional[Dict]: Media data or None
        """
        # Convert UUID to string if needed
        media_id_str = str(media_id)
        return self.db_service.get_media(media_id_str)

    def create_media(self, media_data) -> Dict[str, Any]:
        """
        Create new media entry.

        Args:
            media_data: Media data (Dict or Pydantic model)

        Returns:
            Dict: Created media data
        """
        # Convert Pydantic model to dict if needed
        if hasattr(media_data, 'model_dump'):
            data = media_data.model_dump(exclude_unset=True)
        elif hasattr(media_data, 'dict'):
            data = media_data.dict(exclude_unset=True)
        else:
            data = dict(media_data)

        # Ensure required fields
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())

        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()

        data['updated_at'] = datetime.utcnow()

        media_id = self.db_service.create_media(data)

        # Return the created media
        return self.db_service.get_media(media_id)

    def update_media(self, media_id, updates) -> Dict[str, Any]:
        """
        Update media entry.

        Args:
            media_id: Media ID (str or UUID)
            updates: Fields to update (Dict or Pydantic model)

        Returns:
            Dict: Updated media data
        """
        # Convert UUID to string if needed
        media_id_str = str(media_id)

        # Convert Pydantic model to dict if needed
        if hasattr(updates, 'model_dump'):
            data = updates.model_dump(exclude_unset=True)
        elif hasattr(updates, 'dict'):
            data = updates.dict(exclude_unset=True)
        else:
            data = dict(updates)

        data['updated_at'] = datetime.utcnow()

        success = self.db_service.update_media(media_id_str, data)

        if not success:
            return None

        # Return the updated media
        return self.db_service.get_media(media_id_str)

    def delete_media(self, media_id) -> bool:
        """
        Delete media entry.

        Args:
            media_id: Media ID (str or UUID)

        Returns:
            bool: True if successful
        """
        # Convert UUID to string if needed
        media_id_str = str(media_id)
        return self.db_service.delete_media(media_id_str)

    def search_media(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Search media by title.

        Args:
            query (str): Search query
            page (int): Page number
            page_size (int): Items per page

        Returns:
            Dict: Paginated search results
        """
        # Get all media and filter by search
        result = self.db_service.list_media(limit=1000, offset=0)
        items = result['items']

        # Filter by query
        matches = self._apply_search(items, query)
        total = len(matches)

        # Apply pagination
        offset = (page - 1) * page_size
        paginated_matches = matches[offset:offset + page_size]

        return {
            "items": paginated_matches,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
        }

    def _apply_filters(
        self,
        items: List[Dict[str, Any]],
        filters: MediaFilters
    ) -> List[Dict[str, Any]]:
        """
        Apply filters to media list.

        Args:
            items (List[Dict]): Media items
            filters (MediaFilters): Filter criteria

        Returns:
            List[Dict]: Filtered items
        """
        filtered = items

        # Rating filters
        if filters.min_rating is not None:
            filtered = [
                item for item in filtered
                if item.get('tmdb_rating') and item['tmdb_rating'] >= filters.min_rating
            ]

        if filters.max_rating is not None:
            filtered = [
                item for item in filtered
                if item.get('tmdb_rating') and item['tmdb_rating'] <= filters.max_rating
            ]

        # Year filters
        if filters.year_from is not None:
            filtered = [
                item for item in filtered
                if item.get('release_date') and 
                   int(item['release_date'][:4]) >= filters.year_from
            ]

        if filters.year_to is not None:
            filtered = [
                item for item in filtered
                if item.get('release_date') and 
                   int(item['release_date'][:4]) <= filters.year_to
            ]

        # Maturity rating filter
        if filters.maturity_rating:
            filtered = [
                item for item in filtered
                if item.get('maturity_rating') == filters.maturity_rating
            ]

        return filtered

    def _apply_search(
        self,
        items: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Apply search query to media list.

        Args:
            items (List[Dict]): Media items
            query (str): Search query

        Returns:
            List[Dict]: Matching items
        """
        query_lower = query.lower()
        
        matches = []
        for item in items:
            # Search in title
            if query_lower in item.get('title', '').lower():
                matches.append(item)
                continue
            
            # Search in original title
            if item.get('original_title') and query_lower in item['original_title'].lower():
                matches.append(item)
                continue
            
            # Search in overview
            if item.get('overview') and query_lower in item['overview'].lower():
                matches.append(item)
                continue
        
        return matches

    def _get_genre_ids_by_slug(self, genre_slug: str) -> Optional[List[str]]:
        """
        Get genre IDs by slug.

        Args:
            genre_slug (str): Genre slug to search for

        Returns:
            Optional[List[str]]: List of genre IDs matching the slug, or None
        """
        conn = self.db_service.get_connection()

        # Query to get genre ID by slug
        result = conn.execute(
            "SELECT id FROM genres WHERE slug = ?",
            [genre_slug]
        ).fetchone()

        if result:
            return [str(result[0])]

        return None

    def _apply_sorting(
        self,
        items: List[Dict[str, Any]],
        sort_by: str,
        sort_order: str = "asc"
    ) -> List[Dict[str, Any]]:
        """
        Sort media list.

        Args:
            items (List[Dict]): Media items
            sort_by (str): Field to sort by
            sort_order (str): 'asc' or 'desc'

        Returns:
            List[Dict]: Sorted items
        """
        reverse = sort_order == "desc"
        
        # Handle None values in sorting
        def sort_key(item):
            value = item.get(sort_by)
            # Put None values last
            if value is None:
                return (1, "")  # Tuple for secondary sort
            return (0, value)
        
        try:
            return sorted(items, key=sort_key, reverse=reverse)
        except Exception as e:
            logger.warning(f"Error sorting by {sort_by}: {e}")
            return items


# Global service instance
_media_service: Optional[MediaService] = None


def get_media_service() -> MediaService:
    """
    Get or create global media service instance.

    Returns:
        MediaService: Global service instance
    """
    global _media_service
    if _media_service is None:
        _media_service = MediaService()
    return _media_service


# Export singleton instance
media_service = get_media_service()
