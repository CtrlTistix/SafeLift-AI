"""
WebSocket connection manager for real-time event broadcasting.
"""
from typing import Dict, Set, List
from fastapi import WebSocket
from ...core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts messages.
    """
    
    def __init__(self):
        # Store active connections
        self.active_connections: Set[WebSocket] = set()
        # Store connections by room/channel
        self.rooms: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room: str = "default"):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            room: Room/channel name (default: "default")
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Add to room
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(websocket)
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}, Room: {room}")
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
        """
        self.active_connections.discard(websocket)
        
        # Remove from all rooms
        for room in self.rooms.values():
            room.discard(websocket)
        
        logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            message: Message data to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict, room: str = None):
        """
        Broadcast a message to all connections or a specific room.
        
        Args:
            message: Message data to broadcast
            room: Optional room name (if None, broadcast to all)
        """
        if room and room in self.rooms:
            connections = self.rooms[room]
        else:
            connections = self.active_connections
        
        # Send to all connections
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connection_count(self, room: str = None) -> int:
        """
        Get the number of active connections.
        
        Args:
            room: Optional room name
            
        Returns:
            Number of connections
        """
        if room and room in self.rooms:
            return len(self.rooms[room])
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()
