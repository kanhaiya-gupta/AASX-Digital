"""
Messaging System Package
========================

Provides event-driven communication between system components:
- EventEmitter: Core event emission and subscription
- MessageBus: Central message routing and distribution
- EventStore: Persistent event storage and replay
- MessageQueue: Asynchronous message processing
- EventSourcing: Event sourcing and CQRS support
- EventHandlers: Specialized event handlers for different domains
- PubSub: Publish-subscribe system for decoupled communication
"""

from .event_emitter import EventEmitter, AsyncEventEmitter
from .message_bus import MessageBus, AsyncMessageBus
from .event_store import EventStore, AsyncEventStore
from .message_queue import MessageQueue, AsyncMessageQueue
from .event_sourcing import EventSourcing, AsyncEventSourcing
from .event_handlers import (
    BaseEventHandler, DatabaseEventHandler, SchemaEventHandler, 
    BusinessEventHandler, AIEventHandler, CertificateEventHandler, 
    SystemEventHandler, EventHandlerRegistry
)
from .pubsub import (
    Publisher, AsyncPublisher, MessagePublisher, AsyncMessagePublisher,
    TopicPublisher, AsyncTopicPublisher, Subscriber, AsyncSubscriber,
    MessageSubscriber, AsyncMessageSubscriber, TopicSubscriber, AsyncTopicSubscriber,
    TopicManager, AsyncTopicManager, MessageTopicManager, AsyncMessageTopicManager
)
from .interfaces import EventEmitterProtocol, MessageBusProtocol, EventStoreProtocol
from .types import Event, Message, EventType, MessageType, Priority, DeliveryMode

__all__ = [
    # Core components
    'EventEmitter',
    'AsyncEventEmitter',
    'MessageBus',
    'AsyncMessageBus',
    'EventStore',
    'AsyncEventStore',
    'MessageQueue',
    'AsyncMessageQueue',
    'EventSourcing',
    'AsyncEventSourcing',
    
    # Event Handlers
    'BaseEventHandler',
    'DatabaseEventHandler',
    'SchemaEventHandler',
    'BusinessEventHandler',
    'AIEventHandler',
    'CertificateEventHandler',
    'SystemEventHandler',
    'EventHandlerRegistry',
    
    # PubSub System
    'Publisher',
    'AsyncPublisher',
    'MessagePublisher',
    'AsyncMessagePublisher',
    'TopicPublisher',
    'AsyncTopicPublisher',
    'Subscriber',
    'AsyncSubscriber',
    'MessageSubscriber',
    'AsyncMessageSubscriber',
    'TopicSubscriber',
    'AsyncTopicSubscriber',
    'TopicManager',
    'AsyncTopicManager',
    'MessageTopicManager',
    'AsyncMessageTopicManager',
    
    # Interfaces
    'EventEmitterProtocol',
    'MessageBusProtocol',
    'EventStoreProtocol',
    
    # Types
    'Event',
    'Message',
    'EventType',
    'MessageType',
    'Priority',
    'DeliveryMode'
]
