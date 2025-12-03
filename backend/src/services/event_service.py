"""
Event service for managing safety events.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..db.repositories.event_repository import EventRepository
from ..db.models import Event
from ..schemas.event import EventCreate, EventFilter
from ..core.logging import get_logger
from ..core.events import event_bus, EventType

logger = get_logger(__name__)


class EventService:
    """Service for managing safety events."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = EventRepository(db)
    
    def create_event(self, event_data: EventCreate) -> Event:
        """Create a new event."""
        event = self.repository.create(event_data.model_dump())
        logger.info(f"Event created: {event.type} - severity {event.severity}")
        
        # Publish event for WebSocket broadcast
        event_bus.publish(EventType.TELEMETRY_PROCESSED, event)
        
        return event
    
    def get_event(self, event_id: int) -> Optional[Event]:
        """Get a single event by ID."""
        return self.repository.get(event_id)
    
    def get_events(self, filter_params: EventFilter) -> List[Event]:
        """
        Get events with filtering.
        
        Args:
            filter_params: Filter parameters (severity, type, date range, etc.)
            
        Returns:
            List of events matching filters
        """
        filters = {}
        
        if filter_params.severity:
            return self.repository.get_by_severity(
                filter_params.severity,
                filter_params.skip,
                filter_params.limit
            )
        
        if filter_params.type:
            return self.repository.get_by_type(
                filter_params.type,
                filter_params.skip,
                filter_params.limit
            )
        
        if filter_params.forklift_id:
            return self.repository.get_by_forklift(
                filter_params.forklift_id,
                filter_params.skip,
                filter_params.limit
            )
        
        if filter_params.start_date and filter_params.end_date:
            return self.repository.get_by_date_range(
                filter_params.start_date,
                filter_params.end_date,
                filter_params.skip,
                filter_params.limit
            )
        
        # Default: return recent events
        return self.repository.get_recent(filter_params.limit)
    
    def get_critical_events(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """Get critical severity events."""
        return self.repository.get_critical_events(skip, limit)
