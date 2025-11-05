"""
Calendar Event Models.

Pydantic models for calendar events and watch scheduling.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, time, datetime
from enum import Enum


class EventType(str, Enum):
    """Calendar event types."""
    WATCH = "watch"
    RELEASE = "release"
    REVIEW = "review"
    CUSTOM = "custom"


class CalendarEventCreate(BaseModel):
    """Create new calendar event."""
    media_id: Optional[UUID] = Field(None, description="Related media UUID")
    event_type: EventType = Field(..., description="Type of event")
    event_date: date = Field(..., description="Event date")
    event_time: Optional[time] = Field(None, description="Event time")
    title: Optional[str] = Field(None, max_length=200, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    location: Optional[str] = Field(None, max_length=200, description="Event location")
    icon: Optional[str] = Field(None, max_length=50, description="Icon name")
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")
    reminder_enabled: bool = Field(False, description="Enable reminder")
    reminder_minutes: Optional[int] = Field(None, ge=0, description="Minutes before event for reminder")


class CalendarEventUpdate(BaseModel):
    """Update existing calendar event."""
    media_id: Optional[UUID] = None
    event_type: Optional[EventType] = None
    event_date: Optional[date] = None
    event_time: Optional[time] = None
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    reminder_enabled: Optional[bool] = None
    reminder_minutes: Optional[int] = Field(None, ge=0)
    completed: Optional[bool] = None


class CalendarEventResponse(BaseModel):
    """Calendar event response."""
    id: UUID
    media_id: Optional[UUID]
    event_type: str
    event_date: date
    event_time: Optional[time]
    title: Optional[str]
    description: Optional[str]
    location: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    reminder_enabled: bool
    reminder_minutes: Optional[int]
    completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class CalendarEventsQuery(BaseModel):
    """Query parameters for calendar events."""
    start_date: Optional[date] = Field(None, description="Filter events after this date")
    end_date: Optional[date] = Field(None, description="Filter events before this date")
    event_type: Optional[EventType] = Field(None, description="Filter by event type")
    media_id: Optional[UUID] = Field(None, description="Filter by media ID")
    completed: Optional[bool] = Field(None, description="Filter by completion status")
    limit: int = Field(100, ge=1, le=500, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
