"""
Events router for safety event management.
"""
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.event import EventCreate, EventResponse, EventFilter
from ...services.event_service import EventService
from ..dependencies.auth import CurrentUser, OperatorUser

router = APIRouter()


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: OperatorUser
):
    """
    Create a new safety event (operator role required).
    
    - **type**: Event type classification
    - **severity**: Risk level (1-5)
    - **source**: Camera or sensor identifier
    - **metadata**: Additional event data (flexible JSON)
    """
    event_service = EventService(db)
    return event_service.create_event(event_data)


@router.get("", response_model=List[EventResponse])
async def get_events(
    severity: int = None,
    type: str = None,
    source: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends()
):
    """
    Get list of events with optional filtering.
    
    - **severity**: Filter by severity level (1-5)
    - **type**: Filter by event type
    - **source**: Filter by event source
    - **skip**: Number of events to skip (pagination)
    - **limit**: Maximum number of events to return (max 1000)
    """
    event_service = EventService(db)
    
    filter_params = EventFilter(
        severity=severity,
        type=type,
        source=source,
        skip=skip,
        limit=min(limit, 1000)
    )
    
    return event_service.get_events(filter_params)


@router.get("/critical", response_model=List[EventResponse])
async def get_critical_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends()
):
    """
    Get critical severity events (severity >= 4).
    """
    event_service = EventService(db)
    return event_service.get_critical_events(skip, limit)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUser
):
    """Get a specific event by ID."""
    event_service = EventService(db)
    event = event_service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event
