"""
Safety Rules Engine - Core business logic for detecting safety violations.

This engine processes telemetry data and applies safety rules to detect:
- Impact detection (excessive G-force)
- Dangerous speed violations
- Tilted mast with load
- Excessive braking force
- Dangerous proximity
- Restricted zone entry
- Operation outside authorized hours
"""
from typing import Optional, List, Tuple
from datetime import datetime
import math

from ..core.config import settings
from ..core.logging import get_logger
from ..core.events import event_bus, EventType
from ..schemas.telemetry import TelemetryCreate

logger = get_logger(__name__)


class SafetyViolation:
    """Represents a detected safety violation."""
    
    def __init__(
        self,
        rule_type: str,
        severity: int,
        title: str,
        description: str,
        recommendation: str,
        metadata: dict
    ):
        self.rule_type = rule_type
        self.severity = severity
        self.title = title
        self.description = description
        self.recommendation = recommendation
        self.metadata = metadata


class SafetyRulesEngine:
    """
    Safety rules engine for evaluating telemetry data and detecting violations.
    """
    
    def __init__(self):
        self.impact_threshold = settings.IMPACT_THRESHOLD_G
        self.speed_threshold = settings.DANGEROUS_SPEED_KMH
        self.tilt_threshold = settings.MAST_TILT_THRESHOLD_DEG
        self.braking_threshold = settings.BRAKING_FORCE_THRESHOLD_G
        self.proximity_threshold = settings.PROXIMITY_DANGER_METERS
        self.work_start_hour = settings.WORK_START_HOUR
        self.work_end_hour = settings.WORK_END_HOUR
    
    def evaluate_telemetry(self, telemetry: TelemetryCreate) -> List[SafetyViolation]:
        """
        Evaluate telemetry data against all safety rules.
        
        Args:
            telemetry: Telemetry data to evaluate
            
        Returns:
            List of detected safety violations
        """
        violations = []
        
        # Rule 1: Impact detection
        violation = self._check_impact(telemetry)
        if violation:
            violations.append(violation)
            event_bus.publish(EventType.IMPACT_DETECTED, telemetry)
        
        # Rule 2: Dangerous speed
        violation = self._check_speed(telemetry)
        if violation:
            violations.append(violation)
            event_bus.publish(EventType.SPEED_VIOLATION, telemetry)
        
        # Rule 3: Tilted mast with load
        violation = self._check_mast_tilt(telemetry)
        if violation:
            violations.append(violation)
            event_bus.publish(EventType.TILT_VIOLATION, telemetry)
        
        # Rule 4: Excessive braking force
        violation = self._check_braking(telemetry)
        if violation:
            violations.append(violation)
            event_bus.publish(EventType.BRAKING_VIOLATION, telemetry)
        
        # Rule 5: Operation outside hours
        violation = self._check_operating_hours(telemetry)
        if violation:
            violations.append(violation)
            event_bus.publish(EventType.OUTSIDE_HOURS, telemetry)
        
        if violations:
            logger.warning(f"Detected {len(violations)} safety violations for forklift {telemetry.forklift_id}")
        
        return violations
    
    def _check_impact(self, telemetry: TelemetryCreate) -> Optional[SafetyViolation]:
        """Check for impact detection based on acceleration."""
        if not all([telemetry.acceleration_x, telemetry.acceleration_y, telemetry.acceleration_z]):
            return None
        
        # Calculate total acceleration magnitude (G-force)
        total_g = math.sqrt(
            telemetry.acceleration_x ** 2 +
            telemetry.acceleration_y ** 2 +
            telemetry.acceleration_z ** 2
        )
        
        if total_g > self.impact_threshold:
            severity = 5 if total_g > self.impact_threshold * 1.5 else 4
            
            return SafetyViolation(
                rule_type="impact_detection",
                severity=severity,
                title=f"Impact Detected: {total_g:.2f}G",
                description=f"Forklift experienced impact of {total_g:.2f}G, exceeding threshold of {self.impact_threshold}G",
                recommendation="Immediate inspection required. Check for damage to forklift and cargo. Review operator training.",
                metadata={
                    "total_g_force": total_g,
                    "threshold": self.impact_threshold,
                    "acceleration_x": telemetry.acceleration_x,
                    "acceleration_y": telemetry.acceleration_y,
                    "acceleration_z": telemetry.acceleration_z
                }
            )
        return None
    
    def _check_speed(self, telemetry: TelemetryCreate) -> Optional[SafetyViolation]:
        """Check for dangerous speed violations."""
        if not telemetry.speed_kmh:
            return None
        
        if telemetry.speed_kmh > self.speed_threshold:
            # Higher severity for extreme speeds
            severity = 5 if telemetry.speed_kmh > self.speed_threshold * 1.5 else 4
            
            return SafetyViolation(
                rule_type="speed_violation",
                severity=severity,
                title=f"Excessive Speed: {telemetry.speed_kmh:.1f} km/h",
                description=f"Forklift traveling at {telemetry.speed_kmh:.1f} km/h, exceeding safe limit of {self.speed_threshold} km/h",
                recommendation="Reduce speed immediately. Review warehouse speed limits with operator.",
                metadata={
                    "speed_kmh": telemetry.speed_kmh,
                    "threshold": self.speed_threshold
                }
            )
        return None
    
    def _check_mast_tilt(self, telemetry: TelemetryCreate) -> Optional[SafetyViolation]:
        """Check for dangerous mast tilt while carrying load."""
        if not telemetry.mast_tilt_deg or not telemetry.load_weight_kg:
            return None
        
        # Only check if carrying significant load (>10kg)
        if telemetry.load_weight_kg > 10 and abs(telemetry.mast_tilt_deg) > self.tilt_threshold:
            severity = 5 if abs(telemetry.mast_tilt_deg) > self.tilt_threshold * 1.5 else 4
            
            return SafetyViolation(
                rule_type="mast_tilt_violation",
                severity=severity,
                title=f"Dangerous Mast Tilt: {telemetry.mast_tilt_deg:.1f}°",
                description=f"Mast tilted {telemetry.mast_tilt_deg:.1f}° while carrying {telemetry.load_weight_kg:.0f}kg load",
                recommendation="Level the forklift immediately. Risk of load falling and tip-over. Ensure stable ground.",
                metadata={
                    "mast_tilt_deg": telemetry.mast_tilt_deg,
                    "load_weight_kg": telemetry.load_weight_kg,
                    "threshold": self.tilt_threshold
                }
            )
        return None
    
    def _check_braking(self, telemetry: TelemetryCreate) -> Optional[SafetyViolation]:
        """Check for excessive braking force (sudden stop)."""
        if not telemetry.acceleration_x:
            return None
        
        # Negative X acceleration indicates braking (assuming forward = +X)
        braking_force = abs(min(telemetry.acceleration_x, 0))
        
        if braking_force > self.braking_threshold:
            severity = 4 if braking_force > self.braking_threshold * 1.5 else 3
            
            return SafetyViolation(
                rule_type="excessive_braking",
                severity=severity,
                title=f"Harsh Braking: {braking_force:.2f}G",
                description=f"Sudden braking detected with force of {braking_force:.2f}G",
                recommendation="Review operating conditions. Check for obstacles or unsafe following distance.",
                metadata={
                    "braking_force_g": braking_force,
                    "threshold": self.braking_threshold,
                    "speed_kmh": telemetry.speed_kmh
                }
            )
        return None
    
    def _check_operating_hours(self, telemetry: TelemetryCreate) -> Optional[SafetyViolation]:
        """Check if operation is outside authorized hours."""
        current_hour = datetime.utcnow().hour
        
        # Check if outside working hours
        if current_hour < self.work_start_hour or current_hour >= self.work_end_hour:
            return SafetyViolation(
                rule_type="outside_hours",
                severity=3,
                title="Operation Outside Authorized Hours",
                description=f"Forklift operation detected at {current_hour:02d}:00, outside authorized hours ({self.work_start_hour:02d}:00 - {self.work_end_hour:02d}:00)",
                recommendation="Verify authorization for after-hours operation. Ensure proper supervision and lighting.",
                metadata={
                    "current_hour": current_hour,
                    "work_start_hour": self.work_start_hour,
                    "work_end_hour": self.work_end_hour,
                    "operator_id": telemetry.operator_id
                }
            )
        return None
    
    def check_proximity(
        self,
        forklift_position: Tuple[float, float],
        other_positions: List[Tuple[float, float]]
    ) -> Optional[SafetyViolation]:
        """
        Check for dangerous proximity to other objects/forklifts.
        
        Args:
            forklift_position: (lat, lng) of forklift
            other_positions: List of (lat, lng) of other objects
            
        Returns:
            SafetyViolation if proximity threshold exceeded
        """
        for other_pos in other_positions:
            distance = self._calculate_distance(forklift_position, other_pos)
            
            if distance < self.proximity_threshold:
                severity = 5 if distance < self.proximity_threshold / 2 else 4
                
                return SafetyViolation(
                    rule_type="proximity_violation",
                    severity=severity,
                    title=f"Dangerous Proximity: {distance:.1f}m",
                    description=f"Forklift within {distance:.1f}m of another object (threshold: {self.proximity_threshold}m)",
                    recommendation="Maintain safe distance. Slow down and use horn to alert nearby personnel.",
                    metadata={
                        "distance_meters": distance,
                        "threshold": self.proximity_threshold
                    }
                )
        return None
    
    @staticmethod
    def _calculate_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """
        Calculate distance in meters between two GPS coordinates using Haversine formula.
        
        Args:
            pos1: (latitude, longitude) tuple
            pos2: (latitude, longitude) tuple
            
        Returns:
            Distance in meters
        """
        lat1, lon1 = pos1
        lat2, lon2 = pos2
        
        # Earth radius in meters
        R = 6371000
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance


# Global safety engine instance
safety_engine = SafetyRulesEngine()
