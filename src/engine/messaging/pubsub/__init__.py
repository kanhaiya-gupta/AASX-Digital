"""
Publish-Subscribe System Package
===============================

Provides a robust publish-subscribe system for decoupled communication:
- Publisher: Publishes messages to topics
- Subscriber: Subscribes to topics and receives messages
- TopicManager: Manages topics and their lifecycle
"""

from .publisher import (
    Publisher, AsyncPublisher,
    MessagePublisher, AsyncMessagePublisher,
    TopicPublisher, AsyncTopicPublisher
)
from .subscriber import (
    Subscriber, AsyncSubscriber,
    MessageSubscriber, AsyncMessageSubscriber,
    TopicSubscriber, AsyncTopicSubscriber
)
from .topic_manager import (
    TopicManager, AsyncTopicManager,
    MessageTopicManager, AsyncMessageTopicManager
)

__all__ = [
    # Abstract base classes
    'Publisher',
    'AsyncPublisher',
    'Subscriber',
    'AsyncSubscriber',
    'TopicManager',
    'AsyncTopicManager',
    
    # Concrete implementations
    'MessagePublisher',
    'AsyncMessagePublisher',
    'TopicPublisher',
    'AsyncTopicPublisher',
    'MessageSubscriber',
    'AsyncMessageSubscriber',
    'TopicSubscriber',
    'AsyncTopicSubscriber',
    'MessageTopicManager',
    'AsyncMessageTopicManager'
]
