"""
Publisher
=========

Implements both synchronous and asynchronous publishers for the pubsub system.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
import threading
from abc import ABC, abstractmethod

from ..types import Message, MessageType, Priority, DeliveryMode
from ..interfaces import MessageBusProtocol


logger = logging.getLogger(__name__)


class Publisher(ABC):
    """Abstract base class for publishers"""
    
    def __init__(self, name: str = "Publisher"):
        self.name = name
        self.enabled = True
        self._stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'last_published': None
        }
    
    @abstractmethod
    def publish(self, topic: str, message: Any, **kwargs) -> bool:
        """Publish a message to a topic"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get publisher statistics"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset publisher statistics"""
        self._stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'last_published': None
        }


class AsyncPublisher(ABC):
    """Abstract base class for asynchronous publishers"""
    
    def __init__(self, name: str = "AsyncPublisher"):
        self.name = name
        self.enabled = True
        self._stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'last_published': None
        }
    
    @abstractmethod
    async def publish_async(self, topic: str, message: Any, **kwargs) -> bool:
        """Publish a message to a topic asynchronously"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get publisher statistics"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset publisher statistics"""
        self._stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'last_published': None
        }


class MessagePublisher(Publisher):
    """Synchronous message publisher"""
    
    def __init__(self, message_bus: MessageBusProtocol, name: str = "MessagePublisher"):
        super().__init__(name)
        self.message_bus = message_bus
        self._lock = threading.RLock()
    
    def publish(self, topic: str, message: Any, **kwargs) -> bool:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            message: Message content
            **kwargs: Additional message properties
            
        Returns:
            bool: True if message was published successfully
        """
        if not self.enabled:
            logger.warning(f"Publisher {self.name} is disabled")
            return False
        
        try:
            with self._lock:
                # Create message object
                msg = Message(
                    type=MessageType.EVENT,
                    payload=message,
                    headers={'topic': topic, **kwargs.get('headers', {})},
                    metadata={'publisher': self.name, 'topic': topic, **kwargs.get('metadata', {})},
                    source=self.name,
                    destination=topic,
                    priority=kwargs.get('priority', Priority.NORMAL),
                    delivery_mode=kwargs.get('delivery_mode', DeliveryMode.AT_LEAST_ONCE),
                    ttl=kwargs.get('ttl', None)
                )
                
                # Publish via message bus
                success = self.message_bus.publish(msg)
                
                if success:
                    self._stats['messages_published'] += 1
                    self._stats['messages_delivered'] += 1
                    self._stats['last_published'] = datetime.utcnow()
                    logger.debug(f"Message published to topic '{topic}' by {self.name}")
                else:
                    self._stats['messages_published'] += 1
                    self._stats['messages_failed'] += 1
                    logger.error(f"Failed to publish message to topic '{topic}'")
                
                return success
                
        except Exception as e:
            self._stats['messages_published'] += 1
            self._stats['messages_failed'] += 1
            logger.error(f"Error publishing message to topic '{topic}': {e}")
            return False
    
    def publish_batch(self, topic: str, messages: List[Any], **kwargs) -> Dict[str, int]:
        """
        Publish multiple messages to a topic.
        
        Args:
            topic: Topic to publish to
            messages: List of messages to publish
            **kwargs: Additional message properties
            
        Returns:
            Dict[str, int]: Statistics about the batch operation
        """
        if not self.enabled:
            logger.warning(f"Publisher {self.name} is disabled")
            return {'published': 0, 'delivered': 0, 'failed': 0}
        
        results = {'published': 0, 'delivered': 0, 'failed': 0}
        
        for message in messages:
            try:
                if self.publish(topic, message, **kwargs):
                    results['delivered'] += 1
                else:
                    results['failed'] += 1
                results['published'] += 1
            except Exception as e:
                logger.error(f"Error in batch publish: {e}")
                results['failed'] += 1
                results['published'] += 1
        
        logger.info(f"Batch publish completed: {results['delivered']}/{results['published']} messages delivered")
        return results


class AsyncMessagePublisher(AsyncPublisher):
    """Asynchronous message publisher"""
    
    def __init__(self, message_bus: MessageBusProtocol, name: str = "AsyncMessagePublisher"):
        super().__init__(name)
        self.message_bus = message_bus
        self._async_lock = asyncio.Lock()
    
    async def publish_async(self, topic: str, message: Any, **kwargs) -> bool:
        """
        Publish a message to a topic asynchronously.
        
        Args:
            topic: Topic to publish to
            message: Message content
            **kwargs: Additional message properties
            
        Returns:
            bool: True if message was published successfully
        """
        if not self.enabled:
            logger.warning(f"AsyncPublisher {self.name} is disabled")
            return False
        
        try:
            async with self._async_lock:
                # Create message object
                msg = Message(
                    type=MessageType.EVENT,
                    payload=message,
                    headers={'topic': topic, **kwargs.get('headers', {})},
                    metadata={'publisher': self.name, 'topic': topic, **kwargs.get('metadata', {})},
                    source=self.name,
                    destination=topic,
                    priority=kwargs.get('priority', Priority.NORMAL),
                    delivery_mode=kwargs.get('delivery_mode', DeliveryMode.AT_LEAST_ONCE),
                    ttl=kwargs.get('ttl', None)
                )
                
                # Publish via message bus
                success = await self.message_bus.publish_async(msg)
                
                if success:
                    self._stats['messages_published'] += 1
                    self._stats['messages_delivered'] += 1
                    self._stats['last_published'] = datetime.utcnow()
                    logger.debug(f"Message published asynchronously to topic '{topic}' by {self.name}")
                else:
                    self._stats['messages_published'] += 1
                    self._stats['messages_failed'] += 1
                    logger.error(f"Failed to publish message asynchronously to topic '{topic}'")
                
                return success
                
        except Exception as e:
            self._stats['messages_published'] += 1
            self._stats['messages_failed'] += 1
            logger.error(f"Error publishing message asynchronously to topic '{topic}': {e}")
            return False
    
    async def publish_batch_async(self, topic: str, messages: List[Any], **kwargs) -> Dict[str, int]:
        """
        Publish multiple messages to a topic asynchronously.
        
        Args:
            topic: Topic to publish to
            messages: List of messages to publish
            **kwargs: Additional message properties
            
        Returns:
            Dict[str, int]: Statistics about the batch operation
        """
        if not self.enabled:
            logger.warning(f"AsyncPublisher {self.name} is disabled")
            return {'published': 0, 'delivered': 0, 'failed': 0}
        
        results = {'published': 0, 'delivered': 0, 'failed': 0}
        
        # Create tasks for all messages
        tasks = []
        for message in messages:
            task = asyncio.create_task(self._publish_single_async(topic, message, **kwargs))
            tasks.append(task)
        
        # Wait for all tasks to complete
        try:
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in completed_results:
                if isinstance(result, Exception):
                    logger.error(f"Error in async batch publish: {result}")
                    results['failed'] += 1
                elif result:
                    results['delivered'] += 1
                else:
                    results['failed'] += 1
                results['published'] += 1
                
        except Exception as e:
            logger.error(f"Error in async batch publish: {e}")
            results['failed'] += len(messages)
            results['published'] += len(messages)
        
        logger.info(f"Async batch publish completed: {results['delivered']}/{results['published']} messages delivered")
        return results
    
    async def _publish_single_async(self, topic: str, message: Any, **kwargs) -> bool:
        """Helper method to publish a single message asynchronously"""
        try:
            return await self.publish_async(topic, message, **kwargs)
        except Exception as e:
            logger.error(f"Error in single async publish: {e}")
            return False


class TopicPublisher(Publisher):
    """Topic-specific publisher that maintains topic state"""
    
    def __init__(self, topic: str, message_bus: MessageBusProtocol, name: str = None):
        super().__init__(name or f"TopicPublisher_{topic}")
        self.topic = topic
        self.message_bus = message_bus
        self._lock = threading.RLock()
        self._topic_stats = {
            'messages_sent': 0,
            'subscribers_count': 0,
            'last_activity': None
        }
    
    def publish(self, message: Any, **kwargs) -> bool:
        """
        Publish a message to the configured topic.
        
        Args:
            message: Message content
            **kwargs: Additional message properties
            
        Returns:
            bool: True if message was published successfully
        """
        return super().publish(self.topic, message, **kwargs)
    
    def get_topic_stats(self) -> Dict[str, Any]:
        """Get topic-specific statistics"""
        with self._lock:
            return self._topic_stats.copy()
    
    def update_subscriber_count(self, count: int) -> None:
        """Update the subscriber count for this topic"""
        with self._lock:
            self._topic_stats['subscribers_count'] = count
            self._topic_stats['last_activity'] = datetime.utcnow()


class AsyncTopicPublisher(AsyncPublisher):
    """Asynchronous topic-specific publisher"""
    
    def __init__(self, topic: str, message_bus: MessageBusProtocol, name: str = None):
        super().__init__(name or f"AsyncTopicPublisher_{topic}")
        self.topic = topic
        self.message_bus = message_bus
        self._async_lock = asyncio.Lock()
        self._topic_stats = {
            'messages_sent': 0,
            'subscribers_count': 0,
            'last_activity': None
        }
    
    async def publish_async(self, message: Any, **kwargs) -> bool:
        """
        Publish a message to the configured topic asynchronously.
        
        Args:
            message: Message content
            **kwargs: Additional message properties
            
        Returns:
            bool: True if message was published successfully
        """
        return await super().publish_async(self.topic, message, **kwargs)
    
    def get_topic_stats(self) -> Dict[str, Any]:
        """Get topic-specific statistics"""
        return self._topic_stats.copy()
    
    def update_subscriber_count(self, count: int) -> None:
        """Update the subscriber count for this topic"""
        self._topic_stats['subscribers_count'] = count
        self._topic_stats['last_activity'] = datetime.utcnow()
