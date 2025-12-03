"""
Tests for safety rules engine.
"""
import pytest
from src.services.safety_rules_engine import SafetyRulesEngine, SafetyViolation
from src.schemas.telemetry import TelemetryCreate


def test_impact_detection():
    """Test impact detection rule."""
    engine = SafetyRulesEngine()
    
    # Create telemetry with high G-force
    telemetry = TelemetryCreate(
        forklift_id=1,
        acceleration_x=3.0,
        acceleration_y=1.0,
        acceleration_z=2.0
    )
    
    violations = engine.evaluate_telemetry(telemetry)
    
    assert len(violations) == 1
    assert violations[0].rule_type == "impact_detection"
    assert violations[0].severity >= 4


def test_speed_violation():
    """Test speed violation rule."""
    engine = SafetyRulesEngine()
    
    # Create telemetry with excessive speed
    telemetry = TelemetryCreate(
        forklift_id=1,
        speed_kmh=30.0  # Above default threshold of 25
    )
    
    violations = engine.evaluate_telemetry(telemetry)
    
    assert len(violations) == 1
    assert violations[0].rule_type == "speed_violation"
    assert "30.0 km/h" in violations[0].title


def test_mast_tilt_with_load():
    """Test mast tilt with load rule."""
    engine = SafetyRulesEngine()
    
    # Create telemetry with tilted mast and load
    telemetry = TelemetryCreate(
        forklift_id=1,
        mast_tilt_deg=20.0,  # Above default threshold of 15
        load_weight_kg=500.0
    )
    
    violations = engine.evaluate_telemetry(telemetry)
    
    assert len(violations) == 1
    assert violations[0].rule_type == "mast_tilt_violation"
    assert violations[0].severity >= 4


def test_excessive_braking():
    """Test excessive braking force rule."""
    engine = SafetyRulesEngine()
    
    # Create telemetry with harsh braking
    telemetry = TelemetryCreate(
        forklift_id=1,
        acceleration_x=-2.0,  # Negative indicates braking
        speed_kmh=20.0
    )
    
    violations = engine.evaluate_telemetry(telemetry)
    
    assert len(violations) == 1
    assert violations[0].rule_type == "excessive_braking"


def test_no_violations():
    """Test normal operation with no violations."""
    engine = SafetyRulesEngine()
    
    # Create telemetry with safe values
    telemetry = TelemetryCreate(
        forklift_id=1,
        speed_kmh=15.0,
        acceleration_x=0.5,
        acceleration_y=0.3,
        acceleration_z=0.2,
        mast_tilt_deg=5.0,
        load_weight_kg=100.0
    )
    
    violations = engine.evaluate_telemetry(telemetry)
    
    assert len(violations) == 0


def test_proximity_check():
    """Test proximity violation check."""
    engine = SafetyRulesEngine()
    
    # Two positions very close together (same lat/lng almost)
    forklift_pos = (40.7580, -73.9855)
    other_positions = [(40.7580, -73.9854)]  # Very close
    
    violation = engine.check_proximity(forklift_pos, other_positions)
    
    assert violation is not None
    assert violation.rule_type == "proximity_violation"
