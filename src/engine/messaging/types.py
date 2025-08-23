"""
Messaging System Types
======================

Core data structures and types for the messaging system.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class EventType(Enum):
    """Types of events in the system"""
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_HEALTH_CHECK = "system.health_check"
    
    # Database events
    DATABASE_CONNECTED = "database.connected"
    DATABASE_DISCONNECTED = "database.disconnected"
    DATABASE_MIGRATION_STARTED = "database.migration_started"
    DATABASE_MIGRATION_COMPLETED = "database.migration_completed"
    
    # Schema events
    SCHEMA_CREATED = "schema.created"
    SCHEMA_UPDATED = "schema.updated"
    SCHEMA_DELETED = "schema.deleted"
    SCHEMA_VALIDATION_STARTED = "schema.validation_started"
    SCHEMA_VALIDATION_COMPLETED = "schema.validation_completed"
    
    # Business domain events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    ORGANIZATION_CREATED = "organization.created"
    PROJECT_CREATED = "project.created"
    
    # AI/RAG events
    AI_MODEL_TRAINED = "ai.model_trained"
    AI_EMBEDDING_GENERATED = "ai.embedding_generated"
    RAG_QUERY_EXECUTED = "rag.query_executed"
    
    # Certificate events
    CERTIFICATE_ISSUED = "certificate.issued"
    CERTIFICATE_EXPIRED = "certificate.expired"
    CERTIFICATE_REVOKED = "certificate.revoked"
    
    # Custom events
    CUSTOM = "custom"


class MessageType(Enum):
    """Types of messages in the system"""
    # Command messages
    COMMAND = "command"
    
    # Query messages
    QUERY = "query"
    
    # Event messages
    EVENT = "event"
    
    # Response messages
    RESPONSE = "response"
    
    # Error messages
    ERROR = "error"
    
    # Heartbeat messages
    HEARTBEAT = "heartbeat"


class Priority(Enum):
    """Message priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3
    CRITICAL = 4


class DeliveryMode(Enum):
    """Message delivery modes"""
    AT_MOST_ONCE = "at_most_once"      # Fire and forget
    AT_LEAST_ONCE = "at_least_once"    # Guaranteed delivery
    EXACTLY_ONCE = "exactly_once"      # Exactly once delivery


@dataclass
class Event:
    """Represents an event in the system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.CUSTOM
    name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    version: str = "1.0"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.name:
            self.name = self.type.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            'data': self.data,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'version': self.version,
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        # Parse timestamp
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Parse event type
        if isinstance(data.get('type'), str):
            try:
                data['type'] = EventType(data['type'])
            except ValueError:
                data['type'] = EventType.CUSTOM
        
        return cls(**data)


@dataclass
class Message:
    """Represents a message in the system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.EVENT
    payload: Any = None
    headers: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    destination: Optional[str] = None
    priority: Priority = Priority.NORMAL
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: Optional[int] = None  # Time to live in seconds
    
    def __post_init__(self):
        # Set default headers
        if 'message_id' not in self.headers:
            self.headers['message_id'] = self.id
        if 'timestamp' not in self.headers:
            self.headers['timestamp'] = self.timestamp.isoformat()
        if 'source' not in self.headers:
            self.headers['source'] = self.source
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'payload': self.payload,
            'headers': self.headers,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'destination': self.destination,
            'priority': self.priority.value,
            'delivery_mode': self.delivery_mode.value,
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'ttl': self.ttl
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        # Parse timestamp
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Parse message type
        if isinstance(data.get('type'), str):
            try:
                data['type'] = MessageType(data['type'])
            except ValueError:
                data['type'] = MessageType.EVENT
        
        # Parse priority
        if isinstance(data.get('priority'), int):
            try:
                data['priority'] = Priority(data['priority'])
            except ValueError:
                data['priority'] = Priority.NORMAL
        
        # Parse delivery mode
        if isinstance(data.get('delivery_mode'), str):
            try:
                data['delivery_mode'] = DeliveryMode(data['delivery_mode'])
            except ValueError:
                data['delivery_mode'] = DeliveryMode.AT_LEAST_ONCE
        
        return cls(**data)


@dataclass
class EventHandler:
    """Represents an event handler"""
    handler_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.CUSTOM
    handler: Callable = None
    is_async: bool = False
    priority: int = 0
    enabled: bool = True
    
    def __post_init__(self):
        if self.handler is None:
            raise ValueError("Handler function is required")


@dataclass
class MessageHandler:
    """Represents a message handler"""
    handler_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.EVENT
    handler: Callable = None
    is_async: bool = False
    priority: int = 0
    enabled: bool = True
    queue_name: Optional[str] = None
    
    def __post_init__(self):
        if self.handler is None:
            raise ValueError("Handler function is required")


@dataclass
class Subscription:
    """Represents a subscription to events or messages"""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str = ""
    event_type: Optional[EventType] = None
    message_type: Optional[MessageType] = None
    pattern: Optional[str] = None  # For pattern-based subscriptions
    created_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True
    
    def __post_init__(self):
        if not self.event_type and not self.message_type and not self.pattern:
            raise ValueError("Must specify event_type, message_type, or pattern")


# Type aliases for convenience
EventHandlerType = Callable[[Event], None]
AsyncEventHandlerType = Callable[[Event], None]
MessageHandlerType = Callable[[Message], None]
AsyncMessageHandlerType = Callable[[Message], None]

# Filter types
EventFilter = Callable[[Event], bool]
MessageFilter = Callable[[Message], bool]



