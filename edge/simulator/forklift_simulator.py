"""
Forklift IoT Simulator - Generates realistic telemetry data.
"""
import random
import time
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ForkliftState:
    """State of a simulated forklift."""
    forklift_id: int
    latitude: float
    longitude: float
    speed_kmh: float
    heading: float  # degrees
    mast_height_m: float
    mast_tilt_deg: float
    load_weight_kg: float
    operator_id: str
    is_moving: bool


class ForkliftSimulator:
    """Simulates realistic forklift behavior with GPS and sensor data."""
    
    def __init__(
        self,
        forklift_id: int,
        warehouse_bounds: Tuple[float, float, float, float],
        operators: List[str]
    ):
        """
        Initialize forklift simulator.
        
        Args:
            forklift_id: Unique forklift identifier
            warehouse_bounds: (lat_min, lat_max, lng_min, lng_max)
            operators: List of operator IDs
        """
        self.forklift_id = forklift_id
        self.lat_min, self.lat_max, self.lng_min, self.lng_max = warehouse_bounds
        self.operators = operators
        
        # Initialize state
        self.state = ForkliftState(
            forklift_id=forklift_id,
            latitude=random.uniform(self.lat_min, self.lat_max),
            longitude=random.uniform(self.lng_min, self.lng_max),
            speed_kmh=0.0,
            heading=random.uniform(0, 360),
            mast_height_m=0.0,
            mast_tilt_deg=0.0,
            load_weight_kg=0.0,
            operator_id=random.choice(operators),
            is_moving=False
        )
        
        # Simulation parameters
        self.max_speed = 20.0  # km/h
        self.max_load = 2500.0  # kg
        self.max_mast_height = 6.0  # meters
        
        # Scenario tracking
        self.scenario_timer = 0
        self.current_scenario = "idle"
    
    def update(self, dt: float = 1.0) -> Dict:
        """
        Update forklift state and return telemetry data.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            Telemetry data dictionary
        """
        self.scenario_timer += dt
        
        # Change scenarios periodically
        if self.scenario_timer > random.uniform(10, 30):
            self._select_new_scenario()
            self.scenario_timer = 0
        
        # Execute current scenario
        self._execute_scenario(dt)
        
        # Generate telemetry
        return self._generate_telemetry()
    
    def _select_new_scenario(self):
        """Select a new behavior scenario."""
        scenarios = [
            "idle",
            "normal_driving",
            "loading",
            "unloading",
            "fast_turn",  # Can trigger speed violation
            "harsh_brake",  # Can trigger braking violation
            "tilted_mast",  # Can trigger tilt violation
            "impact"  # Can trigger impact detection
        ]
        
        weights = [0.2, 0.3, 0.15, 0.15, 0.08, 0.05, 0.05, 0.02]
        self.current_scenario = random.choices(scenarios, weights=weights)[0]
    
    def _execute_scenario(self, dt: float):
        """Execute the current scenario."""
        if self.current_scenario == "idle":
            self._scenario_idle()
        
        elif self.current_scenario == "normal_driving":
            self._scenario_normal_driving(dt)
        
        elif self.current_scenario == "loading":
            self._scenario_loading()
        
        elif self.current_scenario == "unloading":
            self._scenario_unloading()
        
        elif self.current_scenario == "fast_turn":
            self._scenario_fast_turn(dt)
        
        elif self.current_scenario == "harsh_brake":
            self._scenario_harsh_brake()
        
        elif self.current_scenario == "tilted_mast":
            self._scenario_tilted_mast()
        
        elif self.current_scenario == "impact":
            self._scenario_impact()
    
    def _scenario_idle(self):
        """Idle scenario - stationary."""
        self.state.speed_kmh = 0.0
        self.state.is_moving = False
    
    def _scenario_normal_driving(self, dt: float):
        """Normal driving scenario."""
        self.state.is_moving = True
        self.state.speed_kmh = random.uniform(8, 15)  # Safe speed
        
        # Update position
        self._update_position(dt)
    
    def _scenario_loading(self):
        """Loading cargo scenario."""
        self.state.speed_kmh = 0.0
        self.state.is_moving = False
        self.state.mast_height_m = random.uniform(2, 5)
        self.state.load_weight_kg = random.uniform(500, self.max_load)
        self.state.mast_tilt_deg = random.uniform(-5, 5)  # Safe tilt
    
    def _scenario_unloading(self):
        """Unloading cargo scenario."""
        self.state.speed_kmh = 0.0
        self.state.is_moving = False
        self.state.mast_height_m = random.uniform(3, 6)
        self.state.load_weight_kg = max(0, self.state.load_weight_kg - random.uniform(100, 500))
        self.state.mast_tilt_deg = random.uniform(-5, 5)
    
    def _scenario_fast_turn(self, dt: float):
        """Fast turn scenario - can trigger speed violation."""
        self.state.is_moving = True
        self.state.speed_kmh = random.uniform(25, 35)  # Excessive speed
        self.state.heading += random.uniform(30, 60)  # Sharp turn
        self._update_position(dt)
    
    def _scenario_harsh_brake(self):
        """Harsh braking scenario."""
        self.state.speed_kmh = max(0, self.state.speed_kmh - random.uniform(15, 25))
        self.state.is_moving = self.state.speed_kmh > 0
    
    def _scenario_tilted_mast(self):
        """Tilted mast with load scenario - dangerous."""
        self.state.load_weight_kg = random.uniform(800, self.max_load)
        self.state.mast_tilt_deg = random.uniform(18, 25)  # Excessive tilt
        self.state.speed_kmh = random.uniform(5, 10)
    
    def _scenario_impact(self):
        """Impact scenario - collision detected."""
        self.state.speed_kmh = 0.0
        self.state.is_moving = False
        # Impact will be reflected in acceleration values
    
    def _update_position(self, dt: float):
        """Update GPS position based on speed and heading."""
        # Convert speed to m/s
        speed_ms = self.state.speed_kmh / 3.6
        
        # Calculate distance traveled
        distance = speed_ms * dt
        
        # Convert to lat/lng delta (approximate)
        lat_delta = (distance * math.cos(math.radians(self.state.heading))) / 111000
        lng_delta = (distance * math.sin(math.radians(self.state.heading))) / (111000 * math.cos(math.radians(self.state.latitude)))
        
        # Update position
        self.state.latitude += lat_delta
        self.state.longitude += lng_delta
        
        # Keep within warehouse bounds
        self.state.latitude = max(self.lat_min, min(self.lat_max, self.state.latitude))
        self.state.longitude = max(self.lng_min, min(self.lng_max, self.state.longitude))
        
        # Random heading changes
        if random.random() < 0.1:
            self.state.heading += random.uniform(-30, 30)
            self.state.heading = self.state.heading % 360
    
    def _generate_telemetry(self) -> Dict:
        """Generate telemetry data from current state."""
        # Calculate acceleration based on scenario
        accel_x, accel_y, accel_z = self._calculate_acceleration()
        
        return {
            "forklift_id": self.forklift_id,
            "latitude": round(self.state.latitude, 6),
            "longitude": round(self.state.longitude, 6),
            "speed_kmh": round(self.state.speed_kmh, 2),
            "acceleration_x": round(accel_x, 3),
            "acceleration_y": round(accel_y, 3),
            "acceleration_z": round(accel_z, 3),
            "mast_tilt_deg": round(self.state.mast_tilt_deg, 2),
            "load_weight_kg": round(self.state.load_weight_kg, 1),
            "mast_height_m": round(self.state.mast_height_m, 2),
            "operator_id": self.state.operator_id,
            "metadata": {
                "heading": round(self.state.heading, 1),
                "is_moving": self.state.is_moving,
                "scenario": self.current_scenario
            }
        }
    
    def _calculate_acceleration(self) -> Tuple[float, float, float]:
        """Calculate acceleration values based on scenario."""
        # Base acceleration (gravity + small vibrations)
        accel_x = random.uniform(-0.2, 0.2)
        accel_y = random.uniform(-0.2, 0.2)
        accel_z = random.uniform(0.8, 1.0)  # Gravity
        
        # Scenario-specific acceleration
        if self.current_scenario == "harsh_brake":
            accel_x = random.uniform(-2.5, -1.5)  # Harsh deceleration
        
        elif self.current_scenario == "fast_turn":
            accel_y = random.uniform(-1.5, 1.5)  # Lateral acceleration
        
        elif self.current_scenario == "impact":
            # High G-force from impact
            accel_x = random.uniform(-4.0, -2.5)
            accel_y = random.uniform(-2.0, 2.0)
            accel_z = random.uniform(0.5, 1.5)
        
        elif self.state.is_moving:
            # Normal driving acceleration
            accel_x = random.uniform(-0.5, 0.8)
            accel_y = random.uniform(-0.3, 0.3)
        
        return accel_x, accel_y, accel_z
