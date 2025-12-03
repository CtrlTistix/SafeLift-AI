"""
Pydantic schemas for events.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EventBase(BaseModel):
    """Base event schema."""
    type: str = Field(..., description="Event type classification")
    severity: int = Field(..., ge=1, le=5, description="Event severity (1-5)")
    source: str = Field(..., description="Event source identifier")
    metadata: Optional[Dict[str, Any]] = None


class EventCreate(EventBase):
    """Schema for creating a new event."""
    forklift_id: Optional[int] = None


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    type: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=5)
    metadata: Optional[Dict[str, Any]] = None


class EventResponse(EventBase):
    """Schema for event response."""
    id: int
    timestamp: datetime
    forklift_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class EventFilter(BaseModel):
    """Schema for filtering events."""
    severity: Optional[int] = Field(None, ge=1, le=5)
    type: Optional[str] = None
    source: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    forklift_id: Optional[int] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
