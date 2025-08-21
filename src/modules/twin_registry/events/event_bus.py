"""
Event Bus Implementation

Provides a centralized event bus for the twin registry population system.
Handles event publishing, subscription, and routing to appropriate handlers.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Coroutine
from datetime import datetime, timezone
from collections import defaultdict

from .event_types import Event, EventType, EventPriority, EventStatus

logger = logging.getLogger(__name__)


class EventBus:
    """
    Centralized event bus for twin registry population system.
    
    Features:
    - Event publishing and subscription
    - Event routing and filtering
    - Async event handling
    - Event persistence and logging
    - Error handling and recovery
    """
    
    def __init__(self):
        """Initialize the event bus."""
        # Event subscriptions by type
        self.subscriptions: Dict[EventType, List[Callable]] = defaultdict(list)
        
        # Event subscriptions by priority
        self.priority_subscriptions: Dict[EventPriority, List[Callable]] = defaultdict(list)
        
        # Global event handlers
        self.global_handlers: List[Callable] = []
        
        # Event queue for async processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        
        # Event processing task
        self.processing_task: Optional[asyncio.Task] = None
        
        # Event statistics
        self.stats = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "active_subscriptions": 0
        }
        
        # Event history (in-memory, could be extended to database)
        self.event_history: List[Event] = []
        self.max_history_size = 1000
        
        logger.info("Event Bus initialized")
    
    async def start(self):
        """Start the event bus processing."""
        if self.processing_task and not self.processing_task.done():
            logger.warning("Event bus already running")
            return
        
        self.processing_task = asyncio.create_task(self._process_events())
        logger.info("Event bus started")
    
    async def stop(self):
        """Stop the event bus processing."""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            self.processing_task = None
        
        logger.info("Event bus stopped")
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[Event], Coroutine[Any, Any, None]],
        priority: Optional[EventPriority] = None
    ) -> str:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Async function to handle events
            priority: Optional priority filter
            
        Returns:
            str: Subscription ID
        """
        subscription_id = f"sub_{len(self.subscriptions[event_type])}_{event_type.value}"
        
        # Add to type-based subscriptions
        self.subscriptions[event_type].append(handler)
        
        # Add to priority-based subscriptions if specified
        if priority:
            self.priority_subscriptions[priority].append(handler)
        
        # Add to global handlers
        self.global_handlers.append(handler)
        
        self.stats["active_subscriptions"] += 1
        logger.info(f"Added subscription {subscription_id} for {event_type.value}")
        
        return subscription_id
    
    def unsubscribe(self, event_type: EventType, handler: Callable) -> bool:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: Type of events to unsubscribe from
            handler: Handler function to remove
            
        Returns:
            bool: True if unsubscribed successfully
        """
        if event_type in self.subscriptions:
            if handler in self.subscriptions[event_type]:
                self.subscriptions[event_type].remove(handler)
                self.stats["active_subscriptions"] -= 1
                logger.info(f"Removed subscription for {event_type.value}")
                return True
        
        # Remove from global handlers
        if handler in self.global_handlers:
            self.global_handlers.remove(handler)
        
        return False
    
    async def publish(self, event: Event) -> bool:
        """
        Publish an event to the event bus.
        
        Args:
            event: Event to publish
            
        Returns:
            bool: True if published successfully
        """
        try:
            # Add to event queue for async processing
            await self.event_queue.put(event)
            
            # Add to event history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history_size:
                self.event_history.pop(0)
            
            self.stats["events_published"] += 1
            logger.debug(f"Published event: {event.event_type.value} (ID: {event.event_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    async def publish_sync(self, event: Event) -> bool:
        """
        Publish an event synchronously (immediate processing).
        
        Args:
            event: Event to publish
            
        Returns:
            bool: True if processed successfully
        """
        try:
            # Process event immediately
            await self._process_event(event)
            return True
            
        except Exception as e:
            logger.error(f"Failed to process event synchronously: {e}")
            return False
    
    async def _process_events(self):
        """Process events from the queue."""
        logger.info("Event processing loop started")
        
        while True:
            try:
                # Get event from queue
                event = await self.event_queue.get()
                
                # Process the event
                await self._process_event(event)
                
                # Mark task as done
                self.event_queue.task_done()
                
            except asyncio.CancelledError:
                logger.info("Event processing loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                self.stats["events_failed"] += 1
    
    async def _process_event(self, event: Event):
        """Process a single event."""
        try:
            logger.debug(f"Processing event: {event.event_type.value} (ID: {event.event_id})")
            
            # Get handlers for this event type
            handlers = self.subscriptions.get(event.event_type, [])
            
            # Add global handlers
            handlers.extend(self.global_handlers)
            
            # Remove duplicates while preserving order
            unique_handlers = []
            seen = set()
            for handler in handlers:
                if handler not in seen:
                    unique_handlers.append(handler)
                    seen.add(handler)
            
            # Execute handlers
            if unique_handlers:
                await self._execute_handlers(event, unique_handlers)
            else:
                logger.debug(f"No handlers found for event type: {event.event_type.value}")
            
            self.stats["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")
            self.stats["events_failed"] += 1
    
    async def _execute_handlers(self, event: Event, handlers: List[Callable]):
        """Execute event handlers."""
        # Create tasks for all handlers
        tasks = []
        for handler in handlers:
            task = asyncio.create_task(self._execute_handler(event, handler))
            tasks.append(task)
        
        # Wait for all handlers to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any handler failures
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Handler {i} failed for event {event.event_id}: {result}")
    
    async def _execute_handler(self, event: Event, handler: Callable):
        """Execute a single event handler."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Handler execution failed: {e}")
            raise
    
    def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        limit: Optional[int] = None
    ) -> List[Event]:
        """
        Get event history with optional filtering.
        
        Args:
            event_type: Filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        if event_type:
            filtered_events = [e for e in self.event_history if e.event_type == event_type]
        else:
            filtered_events = self.event_history.copy()
        
        if limit:
            filtered_events = filtered_events[-limit:]
        
        return filtered_events
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            **self.stats,
            "queue_size": self.event_queue.qsize(),
            "history_size": len(self.event_history),
            "is_running": self.processing_task is not None and not self.processing_task.done()
        }
    
    def clear_history(self):
        """Clear event history."""
        self.event_history.clear()
        logger.info("Event history cleared")
    
    async def wait_for_event(
        self,
        event_type: EventType,
        timeout: Optional[float] = None
    ) -> Optional[Event]:
        """
        Wait for a specific event type to occur.
        
        Args:
            event_type: Type of event to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            Event if found, None if timeout
        """
        start_time = datetime.now(timezone.utc)
        
        while True:
            # Check if timeout exceeded
            if timeout:
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                if elapsed > timeout:
                    return None
            
            # Check event history for matching event
            for event in reversed(self.event_history):
                if event.event_type == event_type:
                    return event
            
            # Wait a bit before checking again
            await asyncio.sleep(0.1)
    
    async def wait_for_events(
        self,
        event_types: List[EventType],
        timeout: Optional[float] = None,
        all_required: bool = True
    ) -> List[Event]:
        """
        Wait for multiple event types to occur.
        
        Args:
            event_types: List of event types to wait for
            timeout: Maximum time to wait in seconds
            all_required: Whether all event types are required
            
        Returns:
            List of found events
        """
        start_time = datetime.now(timezone.utc)
        found_events = []
        found_types = set()
        
        while True:
            # Check if timeout exceeded
            if timeout:
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                if elapsed > timeout:
                    break
            
            # Check event history for matching events
            for event in reversed(self.event_history):
                if event.event_type in event_types and event.event_type not in found_types:
                    found_events.append(event)
                    found_types.add(event.event_type)
                    
                    # Check if we have all required events
                    if all_required and len(found_events) == len(event_types):
                        return found_events
                    elif not all_required and len(found_events) > 0:
                        return found_events
            
            # Wait a bit before checking again
            await asyncio.sleep(0.1)
        
        return found_events
    
    def get_subscription_count(self, event_type: Optional[EventType] = None) -> int:
        """
        Get the number of active subscriptions.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            Number of subscriptions
        """
        if event_type:
            return len(self.subscriptions.get(event_type, []))
        else:
            return sum(len(handlers) for handlers in self.subscriptions.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the event bus."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stats": self.get_stats(),
            "subscriptions": self.get_subscription_count(),
            "queue_health": "healthy"
        }
        
        # Check queue health
        queue_size = self.event_queue.qsize()
        if queue_size > 100:
            health_status["queue_health"] = "warning"
            health_status["status"] = "degraded"
        elif queue_size > 1000:
            health_status["queue_health"] = "critical"
            health_status["status"] = "unhealthy"
        
        # Check processing task health
        if self.processing_task:
            if self.processing_task.done():
                health_status["status"] = "unhealthy"
                health_status["processing_task"] = "stopped"
            else:
                health_status["processing_task"] = "running"
        else:
            health_status["processing_task"] = "not_started"
        
        return health_status
