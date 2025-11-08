"""
Calendar Event Service.

Service layer for managing calendar events and watch schedules.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import logging
from datetime import date, datetime, time

from config.database import db_manager
from backend.models.calendar import (
    CalendarEventCreate,
    CalendarEventUpdate,
)

logger = logging.getLogger(__name__)


class CalendarService:
    """Service for calendar event management."""

    def __init__(self):
        """Initialize calendar service."""
        self.db = db_manager

    # ========== Calendar Event CRUD ==========

    def get_all_events(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        event_type: Optional[str] = None,
        media_id: Optional[UUID] = None,
        completed: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get all calendar events with optional filters.

        Args:
            start_date: Filter events after this date
            end_date: Filter events before this date
            event_type: Filter by event type
            media_id: Filter by media ID
            completed: Filter by completion status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            tuple: (events list, total count)
        """
        conn = self.db.get_duckdb_connection()

        # Build WHERE clause
        where_clauses = []
        params = []

        if start_date:
            where_clauses.append("event_date >= ?")
            params.append(str(start_date))

        if end_date:
            where_clauses.append("event_date <= ?")
            params.append(str(end_date))

        if event_type:
            where_clauses.append("event_type = ?")
            params.append(event_type)

        if media_id:
            where_clauses.append("media_id = ?")
            params.append(str(media_id))

        if completed is not None:
            where_clauses.append("completed = ?")
            params.append(completed)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        count_query = f"SELECT COUNT(*) FROM calendar_events WHERE {where_sql}"
        total = conn.execute(count_query, params).fetchone()[0]

        # Get events
        query = f"""
            SELECT * FROM calendar_events
            WHERE {where_sql}
            ORDER BY event_date DESC, event_time DESC NULLS LAST, created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]
        events = [dict(zip(columns, row)) for row in result]

        # Convert types
        events = [self._serialize_event(event) for event in events]

        return events, total

    def get_event_by_id(self, event_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get calendar event by ID.

        Args:
            event_id: Event UUID

        Returns:
            dict: Event data or None
        """
        conn = self.db.get_duckdb_connection()

        result = conn.execute(
            "SELECT * FROM calendar_events WHERE id = ?",
            [str(event_id)]
        ).fetchone()

        if not result:
            return None

        columns = [desc[0] for desc in conn.description]
        event = dict(zip(columns, result))

        return self._serialize_event(event)

    def create_event(self, event_data: CalendarEventCreate) -> Dict[str, Any]:
        """
        Create new calendar event.

        Args:
            event_data: Event creation data

        Returns:
            dict: Created event
        """
        import uuid

        conn = self.db.get_duckdb_connection()

        # Generate UUID for the event
        event_id = str(uuid.uuid4())

        result = conn.execute("""
            INSERT INTO calendar_events (
                id, media_id, event_type, event_date, event_time,
                title, description, location,
                icon, color,
                reminder_enabled, reminder_minutes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """, [
            event_id,
            str(event_data.media_id) if event_data.media_id else None,
            event_data.event_type.value,
            str(event_data.event_date),
            str(event_data.event_time) if event_data.event_time else None,
            event_data.title,
            event_data.description,
            event_data.location,
            event_data.icon,
            event_data.color,
            event_data.reminder_enabled,
            event_data.reminder_minutes
        ])

        event_id = result.fetchone()[0]
        logger.info(f"Created calendar event: {event_id}")

        return self.get_event_by_id(UUID(str(event_id)))

    def update_event(
        self,
        event_id: UUID,
        updates: CalendarEventUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Update existing calendar event.

        Args:
            event_id: Event UUID
            updates: Fields to update

        Returns:
            dict: Updated event or None
        """
        conn = self.db.get_duckdb_connection()

        # Check if exists
        existing = self.get_event_by_id(event_id)
        if not existing:
            return None

        update_dict = updates.model_dump(exclude_unset=True)
        if not update_dict:
            return existing

        # Handle enum conversion
        if 'event_type' in update_dict and update_dict['event_type']:
            update_dict['event_type'] = update_dict['event_type'].value

        # Build SET clause
        set_clauses = []
        values = []

        for key, value in update_dict.items():
            if value is not None:
                if isinstance(value, (date, time)):
                    value = str(value)
                elif isinstance(value, UUID):
                    value = str(value)

            set_clauses.append(f"{key} = ?")
            values.append(value)

        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(str(event_id))

        query = f"""
            UPDATE calendar_events
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """

        conn.execute(query, values)
        logger.info(f"Updated calendar event: {event_id}")

        return self.get_event_by_id(event_id)

    def delete_event(self, event_id: UUID) -> bool:
        """
        Delete calendar event.

        Args:
            event_id: Event UUID

        Returns:
            bool: True if deleted
        """
        conn = self.db.get_duckdb_connection()

        existing = self.get_event_by_id(event_id)
        if not existing:
            return False

        conn.execute(
            "DELETE FROM calendar_events WHERE id = ?",
            [str(event_id)]
        )

        logger.info(f"Deleted calendar event: {event_id}")
        return True

    def complete_event(self, event_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Mark calendar event as completed.

        Args:
            event_id: Event UUID

        Returns:
            dict: Updated event or None
        """
        conn = self.db.get_duckdb_connection()

        existing = self.get_event_by_id(event_id)
        if not existing:
            return None

        conn.execute("""
            UPDATE calendar_events
            SET completed = TRUE,
                completed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, [str(event_id)])

        logger.info(f"Completed calendar event: {event_id}")
        return self.get_event_by_id(event_id)

    def get_events_by_month(self, year: int, month: int) -> List[Dict[str, Any]]:
        """
        Get all events for a specific month.

        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)

        Returns:
            list: Events in the month
        """
        from calendar import monthrange

        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        events, _ = self.get_all_events(
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

        return events

    def get_upcoming_events(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get upcoming events within the next N days.

        Args:
            days: Number of days to look ahead
            limit: Maximum number of results

        Returns:
            list: Upcoming events
        """
        from datetime import timedelta

        today = date.today()
        end_date = today + timedelta(days=days)

        events, _ = self.get_all_events(
            start_date=today,
            end_date=end_date,
            completed=False,
            limit=limit
        )

        return events

    # ========== Helper Methods ==========

    def _serialize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize event dictionary (convert UUIDs, dates, etc.).

        Args:
            event: Event dictionary

        Returns:
            dict: Serialized event
        """
        serialized = {}
        for key, value in event.items():
            if isinstance(value, UUID):
                serialized[key] = str(value)
            elif isinstance(value, (datetime, date, time)):
                serialized[key] = value.isoformat() if value else None
            else:
                serialized[key] = value

        return serialized


# Singleton instance
calendar_service = CalendarService()
