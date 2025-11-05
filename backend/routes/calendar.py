"""
Calendar API Routes.

Endpoints for calendar events and watch scheduling.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from uuid import UUID
from datetime import date
import logging

from backend.models.calendar import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
)
from backend.services.calendar_service import calendar_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== Calendar Event Endpoints ==========

@router.get("/events", response_model=List[CalendarEventResponse])
async def list_events(
    start_date: Optional[date] = Query(None, description="Filter events after this date"),
    end_date: Optional[date] = Query(None, description="Filter events before this date"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    media_id: Optional[UUID] = Query(None, description="Filter by media ID"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get all calendar events with optional filters.

    Returns:
        List[CalendarEventResponse]: List of calendar events
    """
    try:
        events, total = calendar_service.get_all_events(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            media_id=media_id,
            completed=completed,
            limit=limit,
            offset=offset
        )

        return events

    except Exception as e:
        logger.error(f"Error listing events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list events: {str(e)}")


@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_event(event_id: UUID):
    """
    Get specific calendar event by ID.

    Args:
        event_id: Event UUID

    Returns:
        CalendarEventResponse: Event details

    Raises:
        HTTPException: If event not found
    """
    try:
        event = calendar_service.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch event: {str(e)}")


@router.post("/events", response_model=CalendarEventResponse, status_code=201)
async def create_event(event_data: CalendarEventCreate):
    """
    Create new calendar event.

    Args:
        event_data: Event creation data

    Returns:
        CalendarEventResponse: Created event

    Raises:
        HTTPException: If creation fails
    """
    try:
        event = calendar_service.create_event(event_data)
        return event
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(event_id: UUID, updates: CalendarEventUpdate):
    """
    Update existing calendar event.

    Args:
        event_id: Event UUID
        updates: Fields to update

    Returns:
        CalendarEventResponse: Updated event

    Raises:
        HTTPException: If event not found
    """
    try:
        event = calendar_service.update_event(event_id, updates)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")


@router.delete("/events/{event_id}", status_code=204)
async def delete_event(event_id: UUID):
    """
    Delete calendar event.

    Args:
        event_id: Event UUID

    Raises:
        HTTPException: If event not found
    """
    try:
        deleted = calendar_service.delete_event(event_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Event not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")


@router.post("/events/{event_id}/complete", response_model=CalendarEventResponse)
async def complete_event(event_id: UUID):
    """
    Mark calendar event as completed.

    Args:
        event_id: Event UUID

    Returns:
        CalendarEventResponse: Updated event

    Raises:
        HTTPException: If event not found
    """
    try:
        event = calendar_service.complete_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing event {event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete event: {str(e)}")


# ========== Calendar View Endpoints ==========

@router.get("/month/{year}/{month}", response_model=List[CalendarEventResponse])
async def get_month_events(
    year: int,
    month: int
):
    """
    Get all events for a specific month.

    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)

    Returns:
        List[CalendarEventResponse]: Events in the month
    """
    try:
        events = calendar_service.get_events_by_month(year, month)
        return events
    except Exception as e:
        logger.error(f"Error fetching month events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch month events: {str(e)}")


@router.get("/upcoming", response_model=List[CalendarEventResponse])
async def get_upcoming_events(
    days: int = Query(7, ge=1, le=90, description="Number of days to look ahead"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results")
):
    """
    Get upcoming events within the next N days.

    Args:
        days: Number of days to look ahead
        limit: Maximum number of results

    Returns:
        List[CalendarEventResponse]: Upcoming events
    """
    try:
        events = calendar_service.get_upcoming_events(days=days, limit=limit)
        return events
    except Exception as e:
        logger.error(f"Error fetching upcoming events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch upcoming events: {str(e)}")
