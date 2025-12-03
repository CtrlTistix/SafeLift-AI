"""
Pydantic schemas for telemetry data.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TelemetryBase(BaseModel):
    """Base telemetry schema."""
    forklift_id: int
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    speed_kmh: Optional[float] = Field(None, ge=0)
    acceleration_x: Optional[float] = None
    acceleration_y: Optional[float] = None
    acceleration_z: Optional[float] = None
    mast_tilt_deg: Optional[float] = Field(None, ge=-90, le=90)
    load_weight_kg: Optional[float] = Field(None, ge=0)
    mast_height_m: Optional[float] = Field(None, ge=0)
    operator_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TelemetryCreate(TelemetryBase):
    """Schema for creating telemetry data."""
    pass


class TelemetryResponse(TelemetryBase):
    """Schema for telemetry response."""
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class TelemetryBatch(BaseModel):
    """Schema for batch telemetry upload."""
    data: list[TelemetryCreate]
