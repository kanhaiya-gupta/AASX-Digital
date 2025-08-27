"""
Physics Modeling Event Manager

This module provides the main event management system that orchestrates all event handling,
routes events to appropriate handlers, and manages the event processing pipeline.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Type
from datetime import datetime
from collections import defaultdict, deque
from dataclasses import dataclass

from .event_types import (
    BasePhysicsEvent,
    EventType,
    EventStatus,
    EventPriority
)
from .event_handlers import (
    BaseEventHandler,
    SimulationEventHandler,
    MLTrainingEventHandler,
    ValidationEventHandler,
    ComplianceEventHandler,
    ServiceEventHandler
)

logger = logging.getLogger(__name__)


@dataclass
class EventSubscription:
    """Event subscription configuration."""
    service_name: str
    event_types: List[EventType]
    handler: Callable
    priority: EventPriority = EventPriority.NORMAL
    filters: Optional[Dict[str, Any]] = None


class EventQueue:
    """Priority-based event queue for processing events."""
    
    def __init__(self):
        self.queues = {
            EventPriority.CRITICAL: deque(),
            EventPriority.HIGH: deque(),
            EventPriority.NORMAL: deque(),
            EventPriority.LOW: deque()
        }
        self._lock = asyncio.Lock()
    
    async def enqueue(self, event: BasePhysicsEvent) -> None:
        """Add an event to the appropriate priority queue."""
        await asyncio.sleep(0)  # Pure async
        
        async with self._lock:
            self.queues[event.priority].append(event)
            logger.debug(f"Enqueued event {event.event_id} with priority {event.priority.value}")
    
    async def dequeue(self) -> Optional[BasePhysicsEvent]:
        """Get the next event to process based on priority."""
        await asyncio.sleep(0)  # Pure async
        
        async with self._lock:
            # Process in priority order: CRITICAL -> HIGH -> NORMAL -> LOW
            for priority in [EventPriority.CRITICAL, EventPriority.HIGH, EventPriority.NORMAL, EventPriority.LOW]:
                if self.queues[priority]:
                    event = self.queues[priority].popleft()
                    logger.debug(f"Dequeued event {event.event_id} with priority {priority.value}")
                    return event
        
        return None
    
    async def size(self) -> Dict[EventPriority, int]:
        """Get the current size of each priority queue."""
        await asyncio.sleep(0)  # Pure async
        
        async with self._lock:
            return {priority: len(queue) for priority, queue in self.queues.items()}
    
    async def clear(self) -> None:
        """Clear all event queues."""
        await asyncio.sleep(0)  # Pure async
        
        async with self._lock:
            for queue in self.queues.values():
                queue.clear()
            logger.info("All event queues cleared")


class PhysicsModelingEventManager:
    """Main event manager for the physics modeling system."""
    
    def __init__(self):
        self.event_queue = EventQueue()
        self.handlers: Dict[EventType, BaseEventHandler] = {}
        self.subscriptions: List[EventSubscription] = []
        self.middleware: List[Callable] = []
        self.error_handlers: List[Callable] = []
        self.processing = False
        self.max_workers = 5
        self.workers: List[asyncio.Task] = []
        
        # Initialize default handlers
        self._initialize_handlers()
        
        # Performance tracking
        self.stats = {
            "events_processed": 0,
            "events_failed": 0,
            "events_retried": 0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0
        }
    
    def _initialize_handlers(self) -> None:
        """Initialize the default event handlers."""
        self.handlers = {
            EventType.SIMULATION: SimulationEventHandler(),
            EventType.ML_TRAINING: MLTrainingEventHandler(),
            EventType.VALIDATION: ValidationEventHandler(),
            EventType.COMPLIANCE: ComplianceEventHandler(),
            EventType.SERVICE: ServiceEventHandler()
        }
        
        logger.info("Initialized default event handlers")
    
    async def start(self) -> None:
        """Start the event manager and worker processes."""
        await asyncio.sleep(0)  # Pure async
        
        if self.processing:
            logger.warning("Event manager is already running")
            return
        
        self.processing = True
        logger.info("Starting Physics Modeling Event Manager")
        
        # Start worker processes
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"Started {self.max_workers} event processing workers")
    
    async def stop(self) -> None:
        """Stop the event manager and worker processes."""
        await asyncio.sleep(0)  # Pure async
        
        if not self.processing:
            logger.warning("Event manager is not running")
            return
        
        logger.info("Stopping Physics Modeling Event Manager")
        self.processing = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Event manager stopped")
    
    async def publish_event(self, event: BasePhysicsEvent) -> str:
        """Publish an event to the event system."""
        await asyncio.sleep(0)  # Pure async
        
        # Add event to queue
        await self.event_queue.enqueue(event)
        
        # Notify subscribers
        await self._notify_subscribers(event)
        
        logger.info(f"Published event {event.event_id} of type {event.event_type.value}")
        return event.event_id
    
    async def subscribe(self, subscription: EventSubscription) -> None:
        """Subscribe to specific event types."""
        await asyncio.sleep(0)  # Pure async
        
        self.subscriptions.append(subscription)
        logger.info(f"Service {subscription.service_name} subscribed to {len(subscription.event_types)} event types")
    
    async def unsubscribe(self, service_name: str) -> None:
        """Unsubscribe a service from all events."""
        await asyncio.sleep(0)  # Pure async
        
        self.subscriptions = [sub for sub in self.subscriptions if sub.service_name != service_name]
        logger.info(f"Service {service_name} unsubscribed from all events")
    
    async def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the event processing pipeline."""
        await asyncio.sleep(0)  # Pure async
        
        self.middleware.append(middleware)
        logger.info(f"Added middleware: {middleware.__name__}")
    
    async def add_error_handler(self, error_handler: Callable) -> None:
        """Add an error handler to the event processing pipeline."""
        await asyncio.sleep(0)  # Pure async
        
        self.error_handlers.append(error_handler)
        logger.info(f"Added error handler: {error_handler.__name__}")
    
    async def get_event_status(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific event."""
        await asyncio.sleep(0)  # Pure async
        
        # This would typically query a database or storage system
        # For now, return a placeholder
        return {
            "event_id": event_id,
            "status": "unknown",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system performance statistics."""
        await asyncio.sleep(0)  # Pure async
        
        queue_sizes = await self.event_queue.size()
        
        return {
            "processing": self.processing,
            "active_workers": len([w for w in self.workers if not w.done()]),
            "queue_sizes": queue_sizes,
            "total_events": sum(queue_sizes.values()),
            "stats": self.stats.copy()
        }
    
    async def _worker(self, worker_name: str) -> None:
        """Worker process for processing events."""
        await asyncio.sleep(0)  # Pure async
        
        logger.info(f"Started event processing worker: {worker_name}")
        
        while self.processing:
            try:
                # Get next event from queue
                event = await self.event_queue.dequeue()
                if not event:
                    await asyncio.sleep(0.1)  # Small delay if no events
                    continue
                
                # Process the event
                await self._process_event(event, worker_name)
                
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in worker {worker_name}: {str(e)}")
                await asyncio.sleep(1)  # Delay before retrying
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _process_event(self, event: BasePhysicsEvent, worker_name: str) -> None:
        """Process a single event."""
        await asyncio.sleep(0)  # Pure async
        
        start_time = datetime.utcnow()
        
        try:
            # Mark event as processing
            await event.mark_processing_started()
            
            # Run middleware
            for middleware_func in self.middleware:
                try:
                    event = await middleware_func(event)
                except Exception as e:
                    logger.error(f"Middleware error: {str(e)}")
            
            # Get appropriate handler
            handler = self.handlers.get(event.event_type)
            if not handler:
                raise ValueError(f"No handler found for event type: {event.event_type.value}")
            
            # Process event
            result = await handler.process_event(event)
            
            # Update statistics
            await self._update_stats(start_time, True)
            
            logger.info(f"Worker {worker_name} successfully processed event {event.event_id}")
            
        except Exception as e:
            # Handle processing error
            error_msg = f"Error processing event {event.event_id}: {str(e)}"
            logger.error(error_msg)
            
            # Mark event as failed
            await event.mark_failed(error_msg)
            
            # Run error handlers
            for error_handler in self.error_handlers:
                try:
                    await error_handler(event, e)
                except Exception as eh_error:
                    logger.error(f"Error in error handler: {str(eh_error)}")
            
            # Update statistics
            await self._update_stats(start_time, False)
            
            # Check if event can be retried
            if await event.can_retry():
                await event.increment_retry()
                await self.event_queue.enqueue(event)
                logger.info(f"Re-queued event {event.event_id} for retry")
                self.stats["events_retried"] += 1
    
    async def _notify_subscribers(self, event: BasePhysicsEvent) -> None:
        """Notify all subscribers about a new event."""
        await asyncio.sleep(0)  # Pure async
        
        for subscription in self.subscriptions:
            if event.event_type in subscription.event_types:
                try:
                    # Check if event matches subscription filters
                    if self._event_matches_filters(event, subscription.filters):
                        await subscription.handler(event)
                except Exception as e:
                    logger.error(f"Error notifying subscriber {subscription.service_name}: {str(e)}")
    
    def _event_matches_filters(self, event: BasePhysicsEvent, filters: Optional[Dict[str, Any]]) -> bool:
        """Check if an event matches subscription filters."""
        if not filters:
            return True
        
        for key, value in filters.items():
            if hasattr(event, key):
                event_value = getattr(event, key)
                if event_value != value:
                    return False
            else:
                return False
        
        return True
    
    async def _update_stats(self, start_time: datetime, success: bool) -> None:
        """Update processing statistics."""
        await asyncio.sleep(0)  # Pure async
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        self.stats["events_processed"] += 1
        if not success:
            self.stats["events_failed"] += 1
        
        # Update average processing time
        total_time = self.stats["total_processing_time"] + processing_time
        total_events = self.stats["events_processed"]
        self.stats["average_processing_time"] = total_time / total_events
        self.stats["total_processing_time"] = total_time
    
    async def create_simulation_event(self, simulation_id: str, simulation_type: str, 
                                    twin_id: str, plugin_id: str, **kwargs) -> BasePhysicsEvent:
        """Create a physics simulation event."""
        await asyncio.sleep(0)  # Pure async
        
        from .event_types import PhysicsSimulationEvent
        
        event = PhysicsSimulationEvent(
            event_type=EventType.SIMULATION,
            event_name=f"Simulation: {simulation_type}",
            source_service="simulation_engine",
            target_services=["simulation_service", "metrics_service"],
            simulation_id=simulation_id,
            simulation_type=simulation_type,
            twin_id=twin_id,
            plugin_id=plugin_id,
            **kwargs
        )
        
        return event
    
    async def create_ml_training_event(self, training_id: str, model_type: str, 
                                     dataset_id: str, **kwargs) -> BasePhysicsEvent:
        """Create an ML training event."""
        await asyncio.sleep(0)  # Pure async
        
        from .event_types import MLTrainingEvent
        
        event = MLTrainingEvent(
            event_type=EventType.ML_TRAINING,
            event_name=f"ML Training: {model_type}",
            source_service="ml_service",
            target_services=["training_service", "metrics_service"],
            training_id=training_id,
            model_type=model_type,
            dataset_id=dataset_id,
            **kwargs
        )
        
        return event
    
    async def create_validation_event(self, validation_id: str, validation_type: str, 
                                    model_id: str, **kwargs) -> BasePhysicsEvent:
        """Create a validation event."""
        await asyncio.sleep(0)  # Pure async
        
        from .event_types import ValidationEvent
        
        event = ValidationEvent(
            event_type=EventType.VALIDATION,
            event_name=f"Validation: {validation_type}",
            source_service="validation_service",
            target_services=["compliance_service", "metrics_service"],
            validation_id=validation_id,
            validation_type=validation_type,
            model_id=model_id,
            **kwargs
        )
        
        return event
    
    async def create_compliance_event(self, compliance_id: str, compliance_type: str, 
                                   regulatory_framework: str, **kwargs) -> BasePhysicsEvent:
        """Create a compliance event."""
        await asyncio.sleep(0)  # Pure async
        
        from .event_types import ComplianceEvent
        
        event = ComplianceEvent(
            event_type=EventType.COMPLIANCE,
            event_name=f"Compliance: {compliance_type}",
            source_service="compliance_service",
            target_services=["audit_service", "metrics_service"],
            compliance_id=compliance_id,
            compliance_type=compliance_type,
            regulatory_framework=regulatory_framework,
            **kwargs
        )
        
        return event
    
    async def create_service_event(self, service_id: str, operation: str, **kwargs) -> BasePhysicsEvent:
        """Create a service event."""
        await asyncio.sleep(0)  # Pure async
        
        from .event_types import ServiceEvent
        
        event = ServiceEvent(
            event_type=EventType.SERVICE,
            event_name=f"Service: {operation}",
            source_service=service_id,
            target_services=["monitoring_service", "metrics_service"],
            service_id=service_id,
            operation=operation,
            **kwargs
        )
        
        return event


