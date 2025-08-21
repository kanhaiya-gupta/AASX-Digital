"""
Messaging System Interfaces
==========================

Protocol interfaces for the messaging system components.
"""

from typing import Protocol, runtime_checkable, Any, Dict, List, Optional, Callable, Union
from typing_extensions import runtime_checkable

from .types import Event, Message, EventType, MessageType, EventHandler, MessageHandler, Subscription


@runtime_checkable
class EventEmitterProtocol(Protocol):
    """Protocol for event emitters"""
    
    def emit(self, event: Event) -> bool:
        """Emit an event to all registered handlers"""
        ...
    
    def emit_async(self, event: Event) -> bool:
        """Emit an event asynchronously"""
        ...
    
    def on(self, event_type: EventType, handler: Callable[[Event], None], priority: int = 0) -> str:
        """Register an event handler"""
        ...
    
    def off(self, handler_id: str) -> bool:
        """Unregister an event handler"""
        ...
    
    def once(self, event_type: EventType, handler: Callable[[Event], None]) -> str:
        """Register a one-time event handler"""
        ...
    
    def get_handler_count(self, event_type: Optional[EventType] = None) -> int:
        """Get the number of registered handlers"""
        ...
    
    def clear_handlers(self, event_type: Optional[EventType] = None) -> None:
        """Clear all handlers or handlers for a specific event type"""
        ...


@runtime_checkable
class MessageBusProtocol(Protocol):
    """Protocol for message buses"""
    
    def publish(self, message: Message) -> bool:
        """Publish a message to all subscribers"""
        ...
    
    def publish_async(self, message: Message) -> bool:
        """Publish a message asynchronously"""
        ...
    
    def subscribe(self, message_type: MessageType, handler: Callable[[Message], None], 
                  priority: int = 0, queue_name: Optional[str] = None) -> str:
        """Subscribe to messages of a specific type"""
        ...
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from messages"""
        ...
    
    def send(self, message: Message, destination: str) -> bool:
        """Send a message to a specific destination"""
        ...
    
    def send_async(self, message: Message, destination: str) -> bool:
        """Send a message asynchronously to a specific destination"""
        ...
    
    def request(self, message: Message, destination: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Send a request and wait for a response"""
        ...
    
    def request_async(self, message: Message, destination: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Send a request asynchronously and wait for a response"""
        ...
    
    def get_subscription_count(self, message_type: Optional[MessageType] = None) -> int:
        """Get the number of subscriptions"""
        ...
    
    def clear_subscriptions(self, message_type: Optional[MessageType] = None) -> None:
        """Clear all subscriptions or subscriptions for a specific message type"""
        ...


@runtime_checkable
class EventStoreProtocol(Protocol):
    """Protocol for event stores"""
    
    def store_event(self, event: Event) -> bool:
        """Store an event in the event store"""
        ...
    
    def store_event_async(self, event: Event) -> bool:
        """Store an event asynchronously"""
        ...
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """Retrieve an event by ID"""
        ...
    
    def get_events(self, event_type: Optional[EventType] = None, 
                   start_time: Optional[str] = None, end_time: Optional[str] = None,
                   limit: Optional[int] = None) -> List[Event]:
        """Retrieve events with optional filtering"""
        ...
    
    def get_events_async(self, event_type: Optional[EventType] = None,
                         start_time: Optional[str] = None, end_time: Optional[str] = None,
                         limit: Optional[int] = None) -> List[Event]:
        """Retrieve events asynchronously with optional filtering"""
        ...
    
    def replay_events(self, event_type: Optional[EventType] = None,
                      start_time: Optional[str] = None, end_time: Optional[str] = None,
                      handler: Optional[Callable[[Event], None]] = None) -> int:
        """Replay events to a handler"""
        ...
    
    def replay_events_async(self, event_type: Optional[EventType] = None,
                            start_time: Optional[str] = None, end_time: Optional[str] = None,
                            handler: Optional[Callable[[Event], None]] = None) -> int:
        """Replay events asynchronously to a handler"""
        ...
    
    def get_event_count(self, event_type: Optional[EventType] = None) -> int:
        """Get the total number of events"""
        ...
    
    def clear_events(self, event_type: Optional[EventType] = None,
                     before_time: Optional[str] = None) -> int:
        """Clear events from the store"""
        ...


@runtime_checkable
class MessageQueueProtocol(Protocol):
    """Protocol for message queues"""
    
    def enqueue(self, message: Message, queue_name: str = "default") -> bool:
        """Add a message to a queue"""
        ...
    
    def enqueue_async(self, message: Message, queue_name: str = "default") -> bool:
        """Add a message to a queue asynchronously"""
        ...
    
    def dequeue(self, queue_name: str = "default", timeout: Optional[float] = None) -> Optional[Message]:
        """Remove and return a message from a queue"""
        ...
    
    def dequeue_async(self, queue_name: str = "default", timeout: Optional[float] = None) -> Optional[Message]:
        """Remove and return a message from a queue asynchronously"""
        ...
    
    def peek(self, queue_name: str = "default") -> Optional[Message]:
        """View the next message without removing it"""
        ...
    
    def get_queue_size(self, queue_name: str = "default") -> int:
        """Get the number of messages in a queue"""
        ...
    
    def get_queue_names(self) -> List[str]:
        """Get all queue names"""
        ...
    
    def clear_queue(self, queue_name: str = "default") -> int:
        """Clear all messages from a queue"""
        ...
    
    def delete_queue(self, queue_name: str) -> bool:
        """Delete a queue"""
        ...


@runtime_checkable
class EventSourcingProtocol(Protocol):
    """Protocol for event sourcing"""
    
    def append_event(self, aggregate_id: str, event: Event) -> bool:
        """Append an event to an aggregate's event stream"""
        ...
    
    def append_event_async(self, aggregate_id: str, event: Event) -> bool:
        """Append an event asynchronously to an aggregate's event stream"""
        ...
    
    def get_events(self, aggregate_id: str, start_version: int = 0) -> List[Event]:
        """Get all events for an aggregate starting from a version"""
        ...
    
    def get_events_async(self, aggregate_id: str, start_version: int = 0) -> List[Event]:
        """Get all events for an aggregate asynchronously starting from a version"""
        ...
    
    def get_aggregate_version(self, aggregate_id: str) -> int:
        """Get the current version of an aggregate"""
        ...
    
    def snapshot_aggregate(self, aggregate_id: str, snapshot: Any, version: int) -> bool:
        """Create a snapshot of an aggregate at a specific version"""
        ...
    
    def get_latest_snapshot(self, aggregate_id: str) -> Optional[Any]:
        """Get the latest snapshot for an aggregate"""
        ...
    
    def rebuild_aggregate(self, aggregate_id: str, from_version: int = 0) -> Any:
        """Rebuild an aggregate from events"""
        ...
    
    def rebuild_aggregate_async(self, aggregate_id: str, from_version: int = 0) -> Any:
        """Rebuild an aggregate asynchronously from events"""
        ...
