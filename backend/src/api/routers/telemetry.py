"""
Telemetry router for receiving and querying sensor data.
"""
from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.telemetry import TelemetryCreate, TelemetryResponse
from ...services.telemetry_service import TelemetryService
from ..dependencies.auth import CurrentUser, OperatorUser

router = APIRouter()


@router.post("", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(
    telemetry_data: TelemetryCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: OperatorUser
):
    """
    Ingest telemetry data from a forklift.
    
    This endpoint:
    1. Saves telemetry to database
    2. Evaluates safety rules
    3. Creates alerts if violations detected
    4. Broadcasts updates via WebSocket
    
    - **forklift_id**: ID of the forklift
    - **latitude/longitude**: GPS coordinates
    - **speed_kmh**: Current speed
    - **acceleration_x/y/z**: Acceleration values
    - **mast_tilt_deg**: Mast tilt angle
    - **load_weight_kg**: Current load weight
    - **operator_id**: Operator identifier
    """
    telemetry_service = TelemetryService(db)
    return await telemetry_service.process_telemetry(telemetry_data)


@router.get("/positions", response_model=List[TelemetryResponse])
async def get_latest_positions(
    db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUser
):
    """
    Get latest position for all active forklifts.
    Useful for real-time map visualization.
    """
    telemetry_service = TelemetryService(db)
    return telemetry_service.get_latest_positions()


@router.get("/forklift/{forklift_id}", response_model=List[TelemetryResponse])
async def get_forklift_history(
    forklift_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUser = Depends()
):
    """
    Get telemetry history for a specific forklift.
    
    - **forklift_id**: ID of the forklift
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records
    """
    telemetry_service = TelemetryService(db)
    return telemetry_service.get_forklift_history(forklift_id, skip, limit)
