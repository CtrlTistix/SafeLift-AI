"""
SafeLift-AI Backend - Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config import settings
from src.core.logging import get_logger
from src.core.events import event_bus, EventType
from src.db.session import init_db, get_db
from src.services.auth_service import AuthService
from src.api.routers import auth_router, events_router, telemetry_router
from src.api.middlewares import (
    LoggingMiddleware,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from src.websocket.routes import router as websocket_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Create default users if none exist
    db = next(get_db())
    auth_service = AuthService(db)
    auth_service.initialize_default_users()
    db.close()
    
    # Publish startup event
    event_bus.publish(EventType.SYSTEM_STARTUP, {"version": settings.APP_VERSION})
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    event_bus.publish(EventType.SYSTEM_SHUTDOWN, {})


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time forklift safety monitoring system with IoT telemetry and AI-powered safety rules engine",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(events_router, prefix="/api/events", tags=["Events"])
app.include_router(telemetry_router, prefix="/api/telemetry", tags=["Telemetry"])

# Register WebSocket router
app.include_router(websocket_router, tags=["WebSocket"])


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
