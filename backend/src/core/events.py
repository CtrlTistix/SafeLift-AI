"""
Event bus for decoupled alert broadcasting and system events.
Allows components to publish and subscribe to events without tight coupling.
"""
from typing import Callable, Dict, List, Any
from collections import defaultdict
from .logging import get_logger

logger = get_logger(__name__)


class EventBus:
    """
    Simple event bus implementation for pub/sub pattern.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Remove a subscription."""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from event: {event_type}")
    
    def publish(self, event_type: str, data: Any):
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: Type of event
            data: Event data to pass to subscribers
        """
        logger.debug(f"Publishing event: {event_type}")
        
        for callback in self._subscribers.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in event subscriber for {event_type}: {str(e)}")
    
    def clear(self):
        """Clear all subscriptions."""
        self._subscribers.clear()


# Global event bus instance
event_bus = EventBus()


# Event type constants
class EventType:
    """Standard event types in the system."""
    
    # Safety alerts
    ALERT_CREATED = "alert.created"
    ALERT_RESOLVED = "alert.resolved"
    
    # Telemetry events
    TELEMETRY_RECEIVED = "telemetry.received"
    TELEMETRY_PROCESSED = "telemetry.processed"
    
    # Safety rule violations
    IMPACT_DETECTED = "safety.impact"
    SPEED_VIOLATION = "safety.speed"
    TILT_VIOLATION = "safety.tilt"
    BRAKING_VIOLATION = "safety.braking"
    PROXIMITY_VIOLATION = "safety.proximity"
    RESTRICTED_ZONE = "safety.restricted_zone"
    OUTSIDE_HOURS = "safety.outside_hours"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
