"""
Event repository with specialized queries.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from ..models import Event
from .base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """Repository for Event model with custom queries."""
    
    def __init__(self, db: Session):
        super().__init__(Event, db)
    
    def get_by_severity(
        self,
        severity: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """Get events filtered by severity."""
        return (
            self.db.query(self.model)
            .filter(self.model.severity == severity)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_type(
        self,
        event_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """Get events filtered by type."""
        return (
            self.db.query(self.model)
            .filter(self.model.type == event_type)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """Get events within a date range."""
        return (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.timestamp >= start_date,
                    self.model.timestamp <= end_date
                )
            )
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_forklift(
        self,
        forklift_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """Get events for a specific forklift."""
        return (
            self.db.query(self.model)
            .filter(self.model.forklift_id == forklift_id)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recent(self, limit: int = 50) -> List[Event]:
        """Get most recent events."""
        return (
            self.db.query(self.model)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
            .all()
        )
    
    def get_critical_events(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """Get critical severity events (severity >= 4)."""
        return (
            self.db.query(self.model)
            .filter(self.model.severity >= 4)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
