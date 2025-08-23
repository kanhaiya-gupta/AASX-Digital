"""
Knowledge Graph Neo4j Event Bus

Asynchronous event distribution system for decoupled communication between components.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional, Set
from datetime import datetime, timezone
from collections import defaultdict, deque
from dataclasses import dataclass

from .event_types import KGNeo4jEvent, EventStatus, EventPriority

logger = logging.getLogger(__name__)


@dataclass
class EventSubscription:
    """Event subscription with handler and filter criteria."""
    
    handler: Callable[[KGNeo4jEvent], Any]
    event_types: Optional[Set[str]] = None
    priority_filter: Optional[EventPriority] = None
    source_filter: Optional[str] = None
    graph_id_filter: Optional[str] = None
    active: bool = True
    subscription_id: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize subscription metadata."""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if not self.subscription_id:
            self.subscription_id = f"sub_{int(self.created_at.timestamp())}_{id(self)}"


class KGNeo4jEventBus:
    """Asynchronous event bus for Knowledge Graph Neo4j events."""
    
    def __init__(self, max_queue_size: int = 1000, worker_count: int = 4):
        """Initialize the event bus."""
        self.max_queue_size = max_queue_size
        self.worker_count = worker_count
        
        # Event queues by priority
        self.event_queues: Dict[EventPriority, deque] = {
            priority: deque(maxlen=max_queue_size) for priority in EventPriority
        }
        
        # Event subscriptions
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.type_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        
        # Processing state
        self.is_running = False
        self.workers: List[asyncio.Task] = []
        self.processing_stats = {
            "events_processed": 0,
            "events_failed": 0,
            "events_queued": 0,
            "active_subscriptions": 0
        }
        
        logger.info("Knowledge Graph Neo4j Event Bus initialized")
    
    async def start(self) -> None:
        """Start the event bus and worker processes."""
        if self.is_running:
            logger.warning("Event bus is already running")
            return
        
        self.is_running = True
        
        # Start worker processes
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"Event bus started with {self.worker_count} workers")
    
    async def stop(self) -> None:
        """Stop the event bus and worker processes."""
        if not self.is_running:
            logger.warning("Event bus is not running")
            return
        
        self.is_running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to complete
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Event bus stopped")
    
    async def publish(self, event: KGNeo4jEvent) -> bool:
        """Publish an event to the bus."""
        try:
            if not self.is_running:
                logger.warning("Cannot publish event: Event bus is not running")
                return False
            
            # Add event to appropriate priority queue
            self.event_queues[event.priority].append(event)
            self.processing_stats["events_queued"] += 1
            
            logger.debug(f"Event {event.event_id} published to {event.priority.name} queue")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_id}: {e}")
            return False
    
    def subscribe(
        self,
        handler: Callable[[KGNeo4jEvent], Any],
        event_types: Optional[List[str]] = None,
        priority_filter: Optional[EventPriority] = None,
        source_filter: Optional[str] = None,
        graph_id_filter: Optional[str] = None
    ) -> str:
        """Subscribe to events with optional filters."""
        try:
            subscription = EventSubscription(
                handler=handler,
                event_types=set(event_types) if event_types else None,
                priority_filter=priority_filter,
                source_filter=source_filter,
                graph_id_filter=graph_id_filter
            )
            
            # Store subscription
            self.subscriptions[subscription.subscription_id] = subscription
            self.processing_stats["active_subscriptions"] += 1
            
            # Index by event type for efficient lookup
            if event_types:
                for event_type in event_types:
                    self.type_subscriptions[event_type].add(subscription.subscription_id)
            else:
                # Subscribe to all event types
                self.type_subscriptions["*"].add(subscription.subscription_id)
            
            logger.info(f"Subscription {subscription.subscription_id} created for event types: {event_types or 'all'}")
            return subscription.subscription_id
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        try:
            if subscription_id not in self.subscriptions:
                logger.warning(f"Subscription {subscription_id} not found")
                return False
            
            subscription = self.subscriptions[subscription_id]
            
            # Remove from type subscriptions
            if subscription.event_types:
                for event_type in subscription.event_types:
                    self.type_subscriptions[event_type].discard(subscription_id)
            else:
                self.type_subscriptions["*"].discard(subscription_id)
            
            # Remove subscription
            del self.subscriptions[subscription_id]
            self.processing_stats["active_subscriptions"] -= 1
            
            logger.info(f"Subscription {subscription_id} removed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove subscription {subscription_id}: {e}")
            return False
    
    async def _worker(self, worker_name: str) -> None:
        """Worker process for processing events."""
        logger.info(f"Worker {worker_name} started")
        
        while self.is_running:
            try:
                # Process events by priority (highest first)
                event = await self._get_next_event()
                if event:
                    await self._process_event(event, worker_name)
                else:
                    # No events, wait a bit
                    await asyncio.sleep(0.1)
                    
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)  # Wait before retrying
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _get_next_event(self) -> Optional[KGNeo4jEvent]:
        """Get the next event from priority queues."""
        for priority in reversed(list(EventPriority)):  # Process highest priority first
            queue = self.event_queues[priority]
            if queue:
                return queue.popleft()
        return None
    
    async def _process_event(self, event: KGNeo4jEvent, worker_name: str) -> None:
        """Process a single event."""
        try:
            event.update_status(EventStatus.PROCESSING)
            start_time = datetime.now(timezone.utc)
            
            logger.debug(f"Worker {worker_name} processing event {event.event_id}")
            
            # Find matching subscriptions
            matching_subscriptions = self._find_matching_subscriptions(event)
            
            if not matching_subscriptions:
                logger.debug(f"No subscriptions found for event {event.event_id}")
                event.update_status(EventStatus.COMPLETED)
                return
            
            # Process event with all matching subscriptions
            results = []
            for subscription in matching_subscriptions:
                try:
                    if subscription.active:
                        result = await self._execute_handler(subscription.handler, event)
                        results.append(result)
                    else:
                        logger.debug(f"Skipping inactive subscription {subscription.subscription_id}")
                        
                except Exception as e:
                    logger.error(f"Handler execution failed for subscription {subscription.subscription_id}: {e}")
                    results.append({"error": str(e)})
            
            # Update event status
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            event.processing_time_ms = processing_time
            
            if any("error" in result for result in results):
                event.update_status(EventStatus.FAILED, "Some handlers failed")
                self.processing_stats["events_failed"] += 1
            else:
                event.update_status(EventStatus.COMPLETED)
                self.processing_stats["events_processed"] += 1
            
            logger.debug(f"Event {event.event_id} processed by {len(matching_subscriptions)} handlers in {processing_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")
            event.update_status(EventStatus.FAILED, str(e))
            self.processing_stats["events_failed"] += 1
    
    def _find_matching_subscriptions(self, event: KGNeo4jEvent) -> List[EventSubscription]:
        """Find subscriptions that match the event."""
        matching_subscriptions = []
        
        # Get subscriptions for this event type
        event_type_subscriptions = self.type_subscriptions.get(event.event_type, set())
        all_type_subscriptions = self.type_subscriptions.get("*", set())
        
        # Combine all relevant subscription IDs
        relevant_subscription_ids = event_type_subscriptions | all_type_subscriptions
        
        for subscription_id in relevant_subscription_ids:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription or not subscription.active:
                continue
            
            # Check filters
            if self._subscription_matches_event(subscription, event):
                matching_subscriptions.append(subscription)
        
        return matching_subscriptions
    
    def _subscription_matches_event(self, subscription: EventSubscription, event: KGNeo4jEvent) -> bool:
        """Check if subscription matches event based on filters."""
        # Priority filter
        if subscription.priority_filter and event.priority != subscription.priority_filter:
            return False
        
        # Source filter
        if subscription.source_filter and event.source != subscription.source_filter:
            return False
        
        # Graph ID filter (for events that have graph_id)
        if subscription.graph_id_filter and hasattr(event, 'graph_id'):
            if event.graph_id != subscription.graph_id_filter:
                return False
        
        return True
    
    async def _execute_handler(self, handler: Callable, event: KGNeo4jEvent) -> Any:
        """Execute an event handler."""
        if asyncio.iscoroutinefunction(handler):
            return await handler(event)
        else:
            # Handle synchronous handlers
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, handler, event)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        queue_sizes = {
            priority.name: len(queue) for priority, queue in self.event_queues.items()
        }
        
        return {
            **self.processing_stats,
            "queue_sizes": queue_sizes,
            "is_running": self.is_running,
            "worker_count": len(self.workers),
            "subscription_count": len(self.subscriptions)
        }
    
    def clear_queues(self) -> None:
        """Clear all event queues."""
        for queue in self.event_queues.values():
            queue.clear()
        logger.info("All event queues cleared")
    
    async def wait_for_empty_queues(self, timeout: float = 30.0) -> bool:
        """Wait for all queues to be empty."""
        start_time = datetime.now(timezone.utc)
        
        while timeout > 0:
            total_events = sum(len(queue) for queue in self.event_queues.values())
            if total_events == 0:
                return True
            
            await asyncio.sleep(0.1)
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            timeout -= 0.1
        
        return False
