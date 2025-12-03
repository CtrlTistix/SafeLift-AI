from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models import Event
from ..websocket import manager

router = APIRouter()


class EventCreate(BaseModel):
    type: str = Field(..., description="Event type (e.g., person_near_forklift, collision_risk)")
    severity: int = Field(..., ge=1, le=5, description="Severity level from 1 (low) to 5 (critical)")
    source: str = Field(..., description="Source identifier (e.g., camera_1, sensor_2)")
    metadata: Optional[dict] = Field(default={}, description="Additional event metadata")


class EventResponse(BaseModel):
    id: int
    timestamp: datetime
    type: str
    severity: int
    source: str
    metadata: dict

    class Config:
        from_attributes = True


@router.get("/events", response_model=List[EventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[int] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Event)
    
    if severity is not None:
        query = query.filter(Event.severity == severity)
    
    if type is not None:
        query = query.filter(Event.type == type)
    
    events = query.order_by(Event.timestamp.desc()).offset(skip).limit(limit).all()
    return events


@router.post("/events", response_model=EventResponse, status_code=201)
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    db_event = Event(
        type=event.type,
        severity=event.severity,
        source=event.source,
        metadata=event.metadata
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    await manager.broadcast(db_event.to_dict())
    
    return db_event


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event
