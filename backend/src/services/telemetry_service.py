"""
Telemetry service with safety rules validation.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from ..db.repositories.telemetry_repository import TelemetryRepository
from ..db.models import Telemetry, Alert, Event
from ..schemas.telemetry import TelemetryCreate
from ..core.logging import get_logger
from ..core.events import event_bus, EventType
from .safety_rules_engine import safety_engine, SafetyViolation

logger = get_logger(__name__)


class TelemetryService:
    """Service for processing telemetry data with safety validation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = TelemetryRepository(db)
    
    async def process_telemetry(self, telemetry_data: TelemetryCreate) -> Telemetry:
        """
        Process incoming telemetry data.
        
        1. Save telemetry to database
        2. Evaluate against safety rules
        3. Create alerts if violations detected
        4. Publish events for real-time updates
        
        Args:
            telemetry_data: Telemetry data to process
            
        Returns:
            Created telemetry record
        """
        # Save telemetry data
        telemetry = self.repository.create(telemetry_data.model_dump())
        logger.info(f"Telemetry saved for forklift {telemetry_data.forklift_id}")
        
        # Evaluate safety rules
        violations = safety_engine.evaluate_telemetry(telemetry_data)
        
        # Create alerts and events for violations
        for violation in violations:
            await self._create_alert_from_violation(telemetry, violation)
        
        # Publish telemetry received event
        event_bus.publish(EventType.TELEMETRY_RECEIVED, telemetry)
        
        return telemetry
    
    async def _create_alert_from_violation(
        self,
        telemetry: Telemetry,
        violation: SafetyViolation
    ):
        """Create an alert and event from a safety violation."""
        # Create event
        event = Event(
            type=violation.rule_type,
            severity=violation.severity,
            source=f"forklift_{telemetry.forklift_id}",
            forklift_id=telemetry.forklift_id,
            metadata=violation.metadata
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        # Create alert
        alert = Alert(
            event_id=event.id,
            rule_type=violation.rule_type,
            severity=violation.severity,
            title=violation.title,
            description=violation.description,
            recommendation=violation.recommendation
        )
        self.db.add(alert)
        self.db.commit()
        
        logger.warning(f"Alert created: {violation.title}")
        event_bus.publish(EventType.ALERT_CREATED, alert)
    
    def get_latest_positions(self) -> List[Telemetry]:
        """Get latest position for all active forklifts."""
        return self.repository.get_all_latest_positions()
    
    def get_forklift_history(
        self,
        forklift_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Telemetry]:
        """Get telemetry history for a forklift."""
        return self.repository.get_by_forklift(forklift_id, skip, limit)
