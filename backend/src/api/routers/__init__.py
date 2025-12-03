"""Routers module initialization."""
from .auth import router as auth_router
from .events import router as events_router
from .telemetry import router as telemetry_router

__all__ = [
    "auth_router",
    "events_router",
    "telemetry_router"
]
