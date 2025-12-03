from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.database import engine, Base
from src.routes import events
from src import websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SafeLift-AI Backend",
    description="Real-time forklift safety monitoring system",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api", tags=["events"])
app.include_router(websocket.router, tags=["websocket"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SafeLift-AI Backend",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    return {
        "message": "SafeLift-AI Backend API",
        "docs": "/docs",
        "health": "/health"
    }
