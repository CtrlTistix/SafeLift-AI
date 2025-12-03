"""
WebSocket routes for real-time event streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..core.logging import get_logger
from ..core.events import event_bus, EventType
from .manager import manager

logger = get_logger(__name__)

router = APIRouter()


@router.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time event streaming.
    
    Clients connect to receive real-time updates about:
    - New safety events
    - Telemetry data
    - Alerts
    """
    await manager.connect(websocket, room="events")
    
    try:
        while True:
            # Receive messages from client (ping/pong)
            data = await websocket.receive_text()
            
            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from events WebSocket")


@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time telemetry streaming.
    
    Clients connect to receive real-time telemetry updates from all forklifts.
    """
    await manager.connect(websocket, room="telemetry")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from telemetry WebSocket")


# Event bus subscribers to broadcast events via WebSocket
def broadcast_event(data):
    """Broadcast event via WebSocket."""
    import asyncio
    asyncio.create_task(manager.broadcast({
        "type": "event",
        "data": data.__dict__ if hasattr(data, '__dict__') else str(data)
    }, room="events"))


def broadcast_telemetry(data):
    """Broadcast telemetry via WebSocket."""
    import asyncio
    asyncio.create_task(manager.broadcast({
        "type": "telemetry",
        "data": data.__dict__ if hasattr(data, '__dict__') else str(data)
    }, room="telemetry"))


# Subscribe to events
event_bus.subscribe(EventType.ALERT_CREATED, broadcast_event)
event_bus.subscribe(EventType.TELEMETRY_RECEIVED, broadcast_telemetry)
