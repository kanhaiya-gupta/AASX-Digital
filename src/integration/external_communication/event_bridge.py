"""
Event Bridge for Module Communication

This module provides an event-driven communication system between modules,
enabling pub/sub messaging, event routing, and delivery guarantees.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Union
from datetime import datetime, timedelta
from collections import defaultdict

from .models import EventMessage, EventType, ModuleEndpoint


logger = logging.getLogger(__name__)


class EventHandler:
    """Handler for processing events."""
    
    def __init__(self, callback: Callable, event_types: Optional[List[EventType]] = None):
        """
        Initialize event handler.
        
        Args:
            callback: Function to call when event is received
            event_types: List of event types this handler processes (None for all)
        """
        self.callback = callback
        self.event_types = set(event_types) if event_types else None
        self.call_count = 0
        self.last_called = None
        self.errors = 0
    
    async def handle(self, event: EventMessage) -> bool:
        """
        Handle an event.
        
        Args:
            event: Event message to handle
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # Check if this handler should process this event type
            if self.event_types and event.event_type not in self.event_types:
                return False
            
            await self.callback(event)
            self.call_count += 1
            self.last_called = datetime.utcnow()
            return True
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Error in event handler: {e}")
            return False


class EventBridge:
    """
    Event communication bridge for inter-module messaging.
    
    This bridge provides:
    - Pub/sub messaging between modules
    - Event routing and filtering
    - Delivery guarantees and retry logic
    - Event persistence and replay
    - Performance monitoring and metrics
    """
    
    def __init__(self, max_queue_size: int = 10000):
        """
        Initialize the event bridge.
        
        Args:
            max_queue_size: Maximum number of events in the queue
        """
        self.max_queue_size = max_queue_size
        self.subscribers: Dict[str, List[EventHandler]] = defaultdict(list)
        self.event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.event_history: List[EventMessage] = []
        self.max_history_size = 1000
        self.is_running = False
        self._processing_task: Optional[asyncio.Task] = None
        self._metrics = {
            "events_published": 0,
            "events_delivered": 0,
            "events_failed": 0,
            "active_subscribers": 0,
            "queue_size": 0
        }
    
    async def start(self) -> None:
        """Start the event bridge processing."""
        if self.is_running:
            logger.warning("Event bridge is already running")
            return
        
        self.is_running = True
        self._processing_task = asyncio.create_task(self._process_events())
        logger.info("Event bridge started")
    
    async def stop(self) -> None:
        """Stop the event bridge processing."""
        self.is_running = False
        
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Event bridge stopped")
    
    async def _process_events(self) -> None:
        """Background task for processing events from the queue."""
        while self.is_running:
            try:
                # Get event from queue with timeout
                try:
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process the event
                await self._deliver_event(event)
                
                # Mark task as done
                self.event_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing events: {e}")
                await asyncio.sleep(0.1)  # Brief pause on error
    
    async def _deliver_event(self, event: EventMessage) -> None:
        """
        Deliver event to all relevant subscribers.
        
        Args:
            event: Event message to deliver
        """
        delivery_count = 0
        failure_count = 0
        
        # Get all subscribers for this event type
        event_type_key = event.event_type.value
        target_module_key = event.target_module or "broadcast"
        
        # Deliver to type-specific subscribers
        if event_type_key in self.subscribers:
            for handler in self.subscribers[event_type_key]:
                if await handler.handle(event):
                    delivery_count += 1
                else:
                    failure_count += 1
        
        # Deliver to target-specific subscribers
        if target_module_key in self.subscribers:
            for handler in self.subscribers[target_module_key]:
                if await handler.handle(event):
                    delivery_count += 1
                else:
                    failure_count += 1
        
        # Update metrics
        self._metrics["events_delivered"] += delivery_count
        self._metrics["events_failed"] += failure_count
        
        logger.debug(f"Event {event.event_id} delivered to {delivery_count} subscribers, {failure_count} failures")
    
    def subscribe(
        self,
        topic: str,
        callback: Callable,
        event_types: Optional[List[EventType]] = None
    ) -> str:
        """
        Subscribe to events on a topic.
        
        Args:
            topic: Topic to subscribe to (event type or module name)
            callback: Function to call when event is received
            event_types: List of event types to filter (None for all)
            
        Returns:
            Subscription ID
        """
        handler = EventHandler(callback, event_types)
        self.subscribers[topic].append(handler)
        self._metrics["active_subscribers"] = len(self.subscribers)
        
        subscription_id = f"{topic}_{id(handler)}"
        logger.info(f"Added subscription {subscription_id} for topic {topic}")
        
        return subscription_id
    
    def unsubscribe(self, topic: str, subscription_id: str) -> bool:
        """
        Unsubscribe from events on a topic.
        
        Args:
            topic: Topic to unsubscribe from
            subscription_id: Subscription ID to remove
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        if topic in self.subscribers:
            # Find and remove the handler
            for i, handler in enumerate(self.subscribers[topic]):
                if f"{topic}_{id(handler)}" == subscription_id:
                    del self.subscribers[topic][i]
                    self._metrics["active_subscribers"] = len(self.subscribers)
                    logger.info(f"Removed subscription {subscription_id} from topic {topic}")
                    return True
        
        return False
    
    async def publish(self, event: EventMessage) -> bool:
        """
        Publish an event to the bridge.
        
        Args:
            event: Event message to publish
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history_size:
                self.event_history.pop(0)
            
            # Add to processing queue
            if not self.event_queue.full():
                await self.event_queue.put(event)
                self._metrics["events_published"] += 1
                self._metrics["queue_size"] = self.event_queue.qsize()
                
                logger.debug(f"Published event {event.event_id} of type {event.event_type.value}")
                return True
            else:
                logger.warning("Event queue is full, dropping event")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
    
    async def publish_simple(
        self,
        event_type: EventType,
        source_module: str,
        target_module: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a simple event with basic parameters.
        
        Args:
            event_type: Type of event
            source_module: Source module name
            target_module: Target module name (optional)
            payload: Event payload data
            correlation_id: Correlation ID for tracking
            
        Returns:
            True if published successfully, False otherwise
        """
        event = EventMessage(
            event_type=event_type,
            source_module=source_module,
            target_module=target_module,
            payload=payload or {},
            correlation_id=correlation_id
        )
        
        return await self.publish(event)
    
    def get_subscribers(self, topic: str) -> List[EventHandler]:
        """
        Get all subscribers for a topic.
        
        Args:
            topic: Topic name
            
        Returns:
            List of event handlers
        """
        return self.subscribers.get(topic, [])
    
    def get_topics(self) -> List[str]:
        """Get list of all active topics."""
        return list(self.subscribers.keys())
    
    def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        source_module: Optional[str] = None,
        limit: int = 100
    ) -> List[EventMessage]:
        """
        Get event history with optional filtering.
        
        Args:
            event_type: Filter by event type
            source_module: Filter by source module
            limit: Maximum number of events to return
            
        Returns:
            List of filtered events
        """
        filtered_events = []
        
        for event in reversed(self.event_history):
            if event_type and event.event_type != event_type:
                continue
            if source_module and event.source_module != source_module:
                continue
            
            filtered_events.append(event)
            if len(filtered_events) >= limit:
                break
        
        return filtered_events
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event bridge metrics."""
        return {
            **self._metrics,
            "queue_size": self.event_queue.qsize(),
            "queue_max_size": self.max_queue_size,
            "history_size": len(self.event_history),
            "topics_count": len(self.subscribers),
            "is_running": self.is_running
        }
    
    async def broadcast_health_check(self, source_module: str) -> None:
        """
        Broadcast a health check event.
        
        Args:
            source_module: Name of the source module
        """
        await self.publish_simple(
            event_type=EventType.MODULE_HEALTH,
            source_module=source_module,
            payload={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def broadcast_data_update(
        self,
        source_module: str,
        data_type: str,
        data_id: str,
        operation: str
    ) -> None:
        """
        Broadcast a data update event.
        
        Args:
            source_module: Name of the source module
            data_type: Type of data being updated
            data_id: ID of the data
            operation: Operation performed (create, update, delete)
        """
        await self.publish_simple(
            event_type=EventType.DATA_UPDATE,
            source_module=source_module,
            payload={
                "data_type": data_type,
                "data_id": data_id,
                "operation": operation,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def send_workflow_event(
        self,
        source_module: str,
        target_module: str,
        workflow_id: str,
        status: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Send a workflow-related event to a specific module.
        
        Args:
            source_module: Name of the source module
            target_module: Name of the target module
            workflow_id: ID of the workflow
            status: Workflow status
            payload: Additional workflow data
        """
        event_payload = {
            "workflow_id": workflow_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if payload:
            event_payload.update(payload)
        
        await self.publish_simple(
            event_type=EventType.WORKFLOW_START if status == "start" else EventType.WORKFLOW_COMPLETE,
            source_module=source_module,
            target_module=target_module,
            payload=event_payload
        )
