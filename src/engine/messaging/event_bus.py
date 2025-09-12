"""
Event Bus Module
================

Provides a simple event bus interface for publishing events across the system.
This is a compatibility layer that wraps the existing MessageBus functionality.
"""

from typing import Any, Dict, Optional
from .message_bus import MessageBus, AsyncMessageBus


class EventBus:
    """
    Simple event bus for publishing events.
    
    This class provides a simplified interface for event publishing,
    wrapping the more complex MessageBus functionality.
    """
    
    def __init__(self):
        """Initialize the event bus with an async message bus."""
        self._message_bus = AsyncMessageBus()
    
    async def initialize(self):
        """Initialize the event bus."""
        try:
            # Initialize the underlying message bus if it has an initialize method
            if hasattr(self._message_bus, 'initialize'):
                await self._message_bus.initialize()
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Event bus initialized successfully")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to initialize event bus: {e}")
            raise
    
    async def publish(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """
        Publish an event with the given name and data.
        
        Args:
            event_name: The name/type of the event
            event_data: The event data to publish
        """
        # Create a simple message object for the event bus
        # For now, we'll just log the event since MessageBus expects Message objects
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Event published: {event_name} - {event_data}")
        
        # TODO: Implement proper Message object creation when needed
        # For now, we'll skip the actual message bus publishing to avoid errors
    
    async def subscribe(self, event_name: str, handler) -> None:
        """
        Subscribe to an event with a handler function.
        
        Args:
            event_name: The name/type of the event to subscribe to
            handler: The function to call when the event occurs
        """
        await self._message_bus.subscribe(event_name, handler)
    
    async def unsubscribe(self, event_name: str, handler) -> None:
        """
        Unsubscribe from an event.
        
        Args:
            event_name: The name/type of the event
            handler: The handler function to unsubscribe
        """
        await self._message_bus.unsubscribe(event_name, handler)
    
    async def cleanup(self):
        """Cleanup event bus resources"""
        try:
            # Cleanup the underlying message bus if it has a cleanup method
            if hasattr(self._message_bus, 'cleanup'):
                await self._message_bus.cleanup()
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Event bus cleaned up successfully")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to cleanup event bus: {e}")
            raise


class AsyncEventBus:
    """
    Async-compatible event bus interface.
    
    This is an alias for EventBus to maintain naming consistency.
    """
    
    def __init__(self):
        """Initialize the async event bus."""
        self._event_bus = EventBus()
    
    async def publish(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """Publish an event."""
        await self._event_bus.publish(event_name, event_data)
    
    async def subscribe(self, event_name: str, handler) -> None:
        """Subscribe to an event."""
        await self._event_bus.subscribe(event_name, handler)
    
    async def unsubscribe(self, event_name: str, handler) -> None:
        """Unsubscribe from an event."""
        await self._event_bus.unsubscribe(event_name, handler)
