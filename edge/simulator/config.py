"""
Simulator configuration.
"""
import os

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "admin123")

# Simulation parameters
NUM_FORKLIFTS = int(os.getenv("NUM_FORKLIFTS", "3"))
EVENT_INTERVAL = int(os.getenv("EVENT_INTERVAL", "5"))  # seconds

# Warehouse GPS boundaries (example: New York area)
WAREHOUSE_LAT_MIN = float(os.getenv("WAREHOUSE_LAT_MIN", "40.7580"))
WAREHOUSE_LAT_MAX = float(os.getenv("WAREHOUSE_LAT_MAX", "40.7620"))
WAREHOUSE_LNG_MIN = float(os.getenv("WAREHOUSE_LNG_MIN", "-73.9855"))
WAREHOUSE_LNG_MAX = float(os.getenv("WAREHOUSE_LNG_MAX", "-73.9800"))

WAREHOUSE_BOUNDS = (
    WAREHOUSE_LAT_MIN,
    WAREHOUSE_LAT_MAX,
    WAREHOUSE_LNG_MIN,
    WAREHOUSE_LNG_MAX
)

# Operators
OPERATORS = [
    "OP001",
    "OP002",
    "OP003",
    "OP004",
    "OP005"
]
