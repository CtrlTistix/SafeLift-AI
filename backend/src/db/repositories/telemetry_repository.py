"""
Telemetry repository for time-series data queries.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, func
from sqlalchemy.orm import Session

from ..models import Telemetry
from .base import BaseRepository


class TelemetryRepository(BaseRepository[Telemetry]):
    """Repository for Telemetry model with time-series queries."""
    
    def __init__(self, db: Session):
        super().__init__(Telemetry, db)
    
    def get_by_forklift(
        self,
        forklift_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Telemetry]:
        """Get telemetry data for a specific forklift."""
        return (
            self.db.query(self.model)
            .filter(self.model.forklift_id == forklift_id)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_date_range(
        self,
        forklift_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Telemetry]:
        """Get telemetry data within a date range."""
        return (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.forklift_id == forklift_id,
                    self.model.timestamp >= start_date,
                    self.model.timestamp <= end_date
                )
            )
            .order_by(self.model.timestamp)
            .all()
        )
    
    def get_latest(self, forklift_id: int) -> Optional[Telemetry]:
        """Get the most recent telemetry data for a forklift."""
        return (
            self.db.query(self.model)
            .filter(self.model.forklift_id == forklift_id)
            .order_by(desc(self.model.timestamp))
            .first()
        )
    
    def get_last_n_minutes(
        self,
        forklift_id: int,
        minutes: int = 60
    ) -> List[Telemetry]:
        """Get telemetry data from the last N minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.forklift_id == forklift_id,
                    self.model.timestamp >= cutoff_time
                )
            )
            .order_by(self.model.timestamp)
            .all()
        )
    
    def get_all_latest_positions(self) -> List[Telemetry]:
        """Get the latest position for all forklifts."""
        # Subquery to get latest timestamp for each forklift
        subquery = (
            self.db.query(
                self.model.forklift_id,
                func.max(self.model.timestamp).label('max_timestamp')
            )
            .group_by(self.model.forklift_id)
            .subquery()
        )
        
        # Join with main query to get full records
        return (
            self.db.query(self.model)
            .join(
                subquery,
                and_(
                    self.model.forklift_id == subquery.c.forklift_id,
                    self.model.timestamp == subquery.c.max_timestamp
                )
            )
            .all()
        )
