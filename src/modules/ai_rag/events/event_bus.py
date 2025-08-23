"""
Event Bus for AI RAG Module.

This module implements the core event bus that handles event routing,
prioritization, filtering, and persistence for the AI RAG system.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import uuid
from dataclasses import dataclass, field

from .event_types import (
    BaseEvent, EventPriority, EventStatus, EventCategory,
    EVENT_TYPE_REGISTRY
)


@dataclass
class EventHandler:
    """Event handler configuration."""
    
    handler_id: str
    handler_func: Callable
    event_types: Set[str]
    event_categories: Set[EventCategory]
    priority: EventPriority = EventPriority.NORMAL
    is_async: bool = True
    max_execution_time: float = 30.0  # seconds
    retry_on_failure: bool = True
    max_retries: int = 3
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_execution: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_execution_time: float = 0.0


@dataclass
class EventFilter:
    """Event filtering configuration."""
    
    event_types: Optional[Set[str]] = None
    event_categories: Optional[Set[EventCategory]] = None
    priority_levels: Optional[Set[EventPriority]] = None
    source_components: Optional[Set[str]] = None
    target_components: Optional[Set[str]] = None
    project_ids: Optional[Set[str]] = None
    org_ids: Optional[Set[str]] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    custom_filter: Optional[Callable[[BaseEvent], bool]] = None


class EventBus:
    """
    Central event bus for AI RAG module.
    
    This class provides:
    - Event routing and delivery
    - Event prioritization and queuing
    - Event filtering and subscription
    - Event persistence and retrieval
    - Performance monitoring and metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the event bus."""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # Event handlers registry
        self.handlers: Dict[str, EventHandler] = {}
        self.handler_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Event queues (priority-based)
        self.event_queues: Dict[EventPriority, deque] = {
            priority: deque() for priority in EventPriority
        }
        
        # Event processing state
        self.is_running = False
        self.processing_task: Optional[asyncio.Task] = None
        self.event_processor_semaphore = asyncio.Semaphore(
            self.config.get("max_concurrent_events", 10)
        )
        
        # Event storage and persistence
        self.event_storage: List[BaseEvent] = []
        self.max_storage_size = self.config.get("max_storage_size", 10000)
        self.storage_cleanup_interval = self.config.get("storage_cleanup_interval", 3600)  # seconds
        
        # Performance metrics
        self.metrics = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "events_filtered": 0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0,
            "active_handlers": 0,
            "queue_sizes": {priority.value: 0 for priority in EventPriority}
        }
        
        # Event bus health
        self.health_status = "healthy"
        self.last_health_check = datetime.utcnow()
        self.health_check_interval = self.config.get("health_check_interval", 60)  # seconds
        
        # Initialize cleanup task
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the event bus."""
        if self.is_running:
            self.logger.warning("Event bus is already running")
            return
        
        self.logger.info("Starting AI RAG Event Bus...")
        self.is_running = True
        
        # Start event processing loop
        self.processing_task = asyncio.create_task(self._event_processing_loop())
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Start health monitoring
        asyncio.create_task(self._health_monitoring_loop())
        
        self.logger.info("AI RAG Event Bus started successfully")
    
    async def stop(self) -> None:
        """Stop the event bus."""
        if not self.is_running:
            self.logger.warning("Event bus is not running")
            return
        
        self.logger.info("Stopping AI RAG Event Bus...")
        self.is_running = False
        
        # Cancel processing tasks
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Process remaining events
        await self._process_remaining_events()
        
        self.logger.info("AI RAG Event Bus stopped successfully")
    
    async def publish_event(self, event: BaseEvent) -> str:
        """
        Publish an event to the event bus.
        
        Args:
            event: The event to publish
            
        Returns:
            Event ID for tracking
        """
        if not self.is_running:
            raise RuntimeError("Event bus is not running")
        
        # Validate event
        if not isinstance(event, BaseEvent):
            raise ValueError("Event must be an instance of BaseEvent")
        
        # Set event ID if not provided
        if not hasattr(event, 'event_id') or not event.event_id:
            event.event_id = str(uuid.uuid4())
        
        # Add to appropriate priority queue
        self.event_queues[event.priority].append(event)
        self.metrics["queue_sizes"][event.priority.value] = len(self.event_queues[event.priority])
        self.metrics["events_published"] += 1
        
        # Store event for persistence
        self._store_event(event)
        
        self.logger.debug(f"Event published: {event.event_type} (ID: {event.event_id})")
        return event.event_id
    
    async def subscribe(
        self,
        handler_func: Callable,
        event_types: Optional[List[str]] = None,
        event_categories: Optional[List[EventCategory]] = None,
        priority: EventPriority = EventPriority.NORMAL,
        **kwargs
    ) -> str:
        """
        Subscribe to events with a handler function.
        
        Args:
            handler_func: Function to handle events
            event_types: List of event types to subscribe to
            event_categories: List of event categories to subscribe to
            priority: Handler priority
            **kwargs: Additional handler configuration
            
        Returns:
            Handler ID for unsubscription
        """
        handler_id = str(uuid.uuid4())
        
        # Create event handler
        handler = EventHandler(
            handler_id=handler_id,
            handler_func=handler_func,
            event_types=set(event_types) if event_types else set(),
            event_categories=set(event_categories) if event_categories else set(),
            priority=priority,
            **kwargs
        )
        
        # Register handler
        self.handlers[handler_id] = handler
        
        # Index handler for quick lookup
        for event_type in handler.event_types:
            self.handler_index[event_type].add(handler_id)
        
        for category in handler.event_categories:
            self.handler_index[category.value].add(handler_id)
        
        self.metrics["active_handlers"] = len(self.handlers)
        
        self.logger.info(f"Handler subscribed: {handler_id} for {len(handler.event_types)} event types")
        return handler_id
    
    async def unsubscribe(self, handler_id: str) -> bool:
        """
        Unsubscribe a handler from events.
        
        Args:
            handler_id: ID of the handler to unsubscribe
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        if handler_id not in self.handlers:
            return False
        
        handler = self.handlers[handler_id]
        
        # Remove from indexes
        for event_type in handler.event_types:
            self.handler_index[event_type].discard(handler_id)
        
        for category in handler.event_categories:
            self.handler_index[category.value].discard(handler_id)
        
        # Remove handler
        del self.handlers[handler_id]
        self.metrics["active_handlers"] = len(self.handlers)
        
        self.logger.info(f"Handler unsubscribed: {handler_id}")
        return True
    
    async def get_events(
        self,
        event_filter: Optional[EventFilter] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[BaseEvent]:
        """
        Retrieve events based on filter criteria.
        
        Args:
            event_filter: Filter criteria for events
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of filtered events
        """
        if not event_filter:
            # Return all events with limit and offset
            return self.event_storage[offset:offset + limit]
        
        filtered_events = []
        for event in self.event_storage:
            if self._matches_filter(event, event_filter):
                filtered_events.append(event)
                if len(filtered_events) >= limit:
                    break
        
        return filtered_events
    
    async def get_event_by_id(self, event_id: str) -> Optional[BaseEvent]:
        """
        Retrieve a specific event by ID.
        
        Args:
            event_id: ID of the event to retrieve
            
        Returns:
            Event if found, None otherwise
        """
        for event in self.event_storage:
            if event.event_id == event_id:
                return event
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current event bus metrics."""
        # Update queue sizes
        for priority in EventPriority:
            self.metrics["queue_sizes"][priority.value] = len(self.event_queues[priority])
        
        return self.metrics.copy()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get event bus health status."""
        return {
            "status": self.health_status,
            "is_running": self.is_running,
            "active_handlers": len(self.handlers),
            "total_events_stored": len(self.event_storage),
            "queue_sizes": {priority.value: len(queue) for priority, queue in self.event_queues.items()},
            "last_health_check": self.last_health_check.isoformat(),
            "metrics": self.get_metrics()
        }
    
    async def _event_processing_loop(self) -> None:
        """Main event processing loop."""
        self.logger.info("Event processing loop started")
        
        while self.is_running:
            try:
                # Process events by priority (critical first)
                for priority in [EventPriority.CRITICAL, EventPriority.HIGH, EventPriority.NORMAL, EventPriority.LOW]:
                    if not self.event_queues[priority]:
                        continue
                    
                    # Process up to max_concurrent_events
                    events_to_process = []
                    while (len(events_to_process) < self.config.get("max_concurrent_events", 10) and 
                           self.event_queues[priority]):
                        event = self.event_queues[priority].popleft()
                        events_to_process.append(event)
                        self.metrics["queue_sizes"][priority.value] = len(self.event_queues[priority])
                    
                    # Process events concurrently
                    if events_to_process:
                        tasks = [self._process_event(event) for event in events_to_process]
                        await asyncio.gather(*tasks, return_exceptions=True)
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
                
            except Exception as e:
                self.logger.error(f"Error in event processing loop: {e}")
                await asyncio.sleep(1)  # Wait before retrying
        
        self.logger.info("Event processing loop stopped")
    
    async def _process_event(self, event: BaseEvent) -> None:
        """Process a single event."""
        async with self.event_processor_semaphore:
            start_time = datetime.utcnow()
            
            try:
                # Update event status
                event.status = EventStatus.PROCESSING
                event.started_at = start_time
                
                # Find handlers for this event
                handlers = self._find_handlers_for_event(event)
                
                if not handlers:
                    self.logger.debug(f"No handlers found for event: {event.event_type}")
                    event.status = EventStatus.COMPLETED
                    event.completed_at = datetime.utcnow()
                    self.metrics["events_filtered"] += 1
                    return
                
                # Execute handlers
                handler_tasks = []
                for handler in handlers:
                    if handler.is_active:
                        task = self._execute_handler(handler, event)
                        handler_tasks.append(task)
                
                if handler_tasks:
                    await asyncio.gather(*handler_tasks, return_exceptions=True)
                
                # Update event status
                event.status = EventStatus.COMPLETED
                event.completed_at = datetime.utcnow()
                
                # Update metrics
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                self.metrics["events_processed"] += 1
                self.metrics["total_processing_time"] += processing_time
                self.metrics["average_processing_time"] = (
                    self.metrics["total_processing_time"] / self.metrics["events_processed"]
                )
                
                self.logger.debug(f"Event processed: {event.event_type} in {processing_time:.3f}s")
                
            except Exception as e:
                self.logger.error(f"Error processing event {event.event_id}: {e}")
                event.status = EventStatus.FAILED
                event.error_message = str(e)
                self.metrics["events_failed"] += 1
    
    def _find_handlers_for_event(self, event: BaseEvent) -> List[EventHandler]:
        """Find handlers that should process this event."""
        handlers = []
        
        # Find handlers by event type
        if event.event_type in self.handler_index:
            for handler_id in self.handler_index[event.event_type]:
                if handler_id in self.handlers:
                    handlers.append(self.handlers[handler_id])
        
        # Find handlers by event category
        if event.event_category.value in self.handler_index:
            for handler_id in self.handler_index[event.event_category.value]:
                if handler_id in self.handler_index and handler_id not in [h.handler_id for h in handlers]:
                    handlers.append(self.handlers[handler_id])
        
        return handlers
    
    async def _execute_handler(self, handler: EventHandler, event: BaseEvent) -> None:
        """Execute a single event handler."""
        start_time = datetime.utcnow()
        
        try:
            # Execute handler
            if handler.is_async:
                if asyncio.iscoroutinefunction(handler.handler_func):
                    await asyncio.wait_for(
                        handler.handler_func(event),
                        timeout=handler.max_execution_time
                    )
                else:
                    # Convert sync function to async
                    await asyncio.get_event_loop().run_in_executor(
                        None, handler.handler_func, event
                    )
            else:
                # Execute sync function
                handler.handler_func(event)
            
            # Update handler metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            handler.last_execution = datetime.utcnow()
            handler.execution_count += 1
            handler.success_count += 1
            handler.total_execution_time += execution_time
            
            self.logger.debug(f"Handler {handler.handler_id} executed successfully in {execution_time:.3f}s")
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Handler {handler.handler_id} timed out after {handler.max_execution_time}s")
            handler.failure_count += 1
            
        except Exception as e:
            self.logger.error(f"Handler {handler.handler_id} failed: {e}")
            handler.failure_count += 1
            
            # Retry logic
            if handler.retry_on_failure and event.retry_count < handler.max_retries:
                event.retry_count += 1
                # Re-queue event with lower priority
                lower_priority = self._get_lower_priority(event.priority)
                self.event_queues[lower_priority].append(event)
    
    def _get_lower_priority(self, current_priority: EventPriority) -> EventPriority:
        """Get the next lower priority level."""
        priority_order = [EventPriority.CRITICAL, EventPriority.HIGH, EventPriority.NORMAL, EventPriority.LOW]
        try:
            current_index = priority_order.index(current_priority)
            if current_index < len(priority_order) - 1:
                return priority_order[current_index + 1]
        except ValueError:
            pass
        return EventPriority.LOW
    
    def _store_event(self, event: BaseEvent) -> None:
        """Store event for persistence."""
        self.event_storage.append(event)
        
        # Maintain storage size limit
        if len(self.event_storage) > self.max_storage_size:
            # Remove oldest events
            events_to_remove = len(self.event_storage) - self.max_storage_size
            self.event_storage = self.event_storage[events_to_remove:]
    
    def _matches_filter(self, event: BaseEvent, event_filter: EventFilter) -> bool:
        """Check if event matches filter criteria."""
        # Event types filter
        if event_filter.event_types and event.event_type not in event_filter.event_types:
            return False
        
        # Event categories filter
        if event_filter.event_categories and event.event_category not in event_filter.event_categories:
            return False
        
        # Priority levels filter
        if event_filter.priority_levels and event.priority not in event_filter.priority_levels:
            return False
        
        # Source components filter
        if event_filter.source_components and event.source not in event_filter.source_components:
            return False
        
        # Target components filter
        if event_filter.target_components and event.target not in event_filter.target_components:
            return False
        
        # Project IDs filter
        if event_filter.project_ids and event.project_id not in event_filter.project_ids:
            return False
        
        # Organization IDs filter
        if event_filter.org_ids and event.org_id not in event_filter.org_ids:
            return False
        
        # Date range filter
        if event_filter.date_range:
            start_date, end_date = event_filter.date_range
            if not (start_date <= event.created_at <= end_date):
                return False
        
        # Custom filter
        if event_filter.custom_filter and not event_filter.custom_filter(event):
            return False
        
        return True
    
    async def _cleanup_loop(self) -> None:
        """Periodic cleanup loop."""
        while self.is_running:
            try:
                await asyncio.sleep(self.storage_cleanup_interval)
                await self._cleanup_old_events()
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_old_events(self) -> None:
        """Clean up old events from storage."""
        cutoff_time = datetime.utcnow() - timedelta(
            days=self.config.get("event_retention_days", 30)
        )
        
        original_count = len(self.event_storage)
        self.event_storage = [
            event for event in self.event_storage
            if event.created_at > cutoff_time
        ]
        
        removed_count = original_count - len(self.event_storage)
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old events")
    
    async def _health_monitoring_loop(self) -> None:
        """Health monitoring loop."""
        while self.is_running:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_health()
            except Exception as e:
                self.logger.error(f"Error in health monitoring loop: {e}")
    
    async def _check_health(self) -> None:
        """Check event bus health."""
        try:
            # Check queue sizes
            total_queued_events = sum(len(queue) for queue in self.event_queues.values())
            
            # Check processing metrics
            if self.metrics["events_published"] > 0:
                processing_rate = self.metrics["events_processed"] / self.metrics["events_published"]
                if processing_rate < 0.8:  # Less than 80% processing rate
                    self.health_status = "degraded"
                else:
                    self.health_status = "healthy"
            
            # Check for stuck events
            if total_queued_events > 1000:
                self.health_status = "warning"
            
            self.last_health_check = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self.health_status = "unhealthy"
    
    async def _process_remaining_events(self) -> None:
        """Process remaining events when stopping."""
        remaining_events = []
        for queue in self.event_queues.values():
            remaining_events.extend(queue)
            queue.clear()
        
        if remaining_events:
            self.logger.info(f"Processing {len(remaining_events)} remaining events...")
            for event in remaining_events:
                event.status = EventStatus.CANCELLED
                self._store_event(event)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "max_concurrent_events": 10,
            "max_storage_size": 10000,
            "storage_cleanup_interval": 3600,  # 1 hour
            "event_retention_days": 30,
            "health_check_interval": 60,  # 1 minute
        }
