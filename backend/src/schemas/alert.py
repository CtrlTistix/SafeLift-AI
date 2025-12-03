"""
Pydantic schemas for alerts.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AlertBase(BaseModel):
    """Base alert schema."""
    rule_type: str
    severity: int = Field(..., ge=1, le=5)
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=500)
    recommendation: Optional[str] = Field(None, max_length=500)


class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    event_id: int


class AlertResponse(AlertBase):
    """Schema for alert response."""
    id: int
    timestamp: datetime
    event_id: int
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class AlertResolve(BaseModel):
    """Schema for resolving an alert."""
    resolved_by: int
