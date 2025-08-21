"""
Subscriber
==========

Implements both synchronous and asynchronous subscribers for the pubsub system.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union, Set
from datetime import datetime
import threading
from abc import ABC, abstractmethod
import weakref

from ..types import Message, MessageType, Priority, DeliveryMode
from ..interfaces import MessageBusProtocol


logger = logging.getLogger(__name__)


class Subscriber(ABC):
    """Abstract base class for subscribers"""
    
    def __init__(self, name: str = "Subscriber"):
        self.name = name
        self.enabled = True
        self._stats = {
            'messages_received': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'last_received': None
        }
    
    @abstractmethod
    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> str:
        """Subscribe to a topic"""
        pass
    
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get subscriber statistics"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset subscriber statistics"""
        self._stats = {
            'messages_received': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'last_received': None
        }


class AsyncSubscriber(ABC):
    """Abstract base class for asynchronous subscribers"""
    
    def __init__(self, name: str = "AsyncSubscriber"):
        self.name = name
        self.enabled = True
        self._stats = {
            'messages_received': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'last_received': None
        }
    
    @abstractmethod
    async def subscribe_async(self, topic: str, handler: Callable[[Message], None]) -> str:
        """Subscribe to a topic asynchronously"""
        pass
    
    @abstractmethod
    async def unsubscribe_async(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic asynchronously"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get subscriber statistics"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset subscriber statistics"""
        self._stats = {
            'messages_received': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'last_received': None
        }


class MessageSubscriber(Subscriber):
    """Synchronous message subscriber"""
    
    def __init__(self, message_bus: MessageBusProtocol, name: str = "MessageSubscriber"):
        super().__init__(name)
        self.message_bus = message_bus
        self._lock = threading.RLock()
        self._subscriptions: Dict[str, Dict[str, Any]] = {}
        self._topic_handlers: Dict[str, List[Callable[[Message], None]]] = {}
        self._subscription_counter = 0
    
    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> str:
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic to subscribe to
            handler: Function to call when messages arrive
            
        Returns:
            str: Subscription ID for later unsubscription
        """
        if not self.enabled:
            logger.warning(f"Subscriber {self.name} is disabled")
            return ""
        
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        try:
            with self._lock:
                subscription_id = f"{self.name}_{self._subscription_counter}"
                self._subscription_counter += 1
                
                # Store subscription details
                self._subscriptions[subscription_id] = {
                    'topic': topic,
                    'handler': handler,
                    'created_at': datetime.utcnow(),
                    'active': True
                }
                
                # Add handler to topic
                if topic not in self._topic_handlers:
                    self._topic_handlers[topic] = []
                self._topic_handlers[topic].append(handler)
                
                # Subscribe via message bus
                success = self.message_bus.subscribe(
                    MessageType.EVENT,
                    self._message_handler,
                    priority=0,
                    queue_name=topic
                )
                
                if success:
                    logger.info(f"Subscribed to topic '{topic}' with ID: {subscription_id}")
                else:
                    logger.error(f"Failed to subscribe to topic '{topic}'")
                    # Clean up local state
                    del self._subscriptions[subscription_id]
                    self._topic_handlers[topic].remove(handler)
                    if not self._topic_handlers[topic]:
                        del self._topic_handlers[topic]
                    return ""
                
                return subscription_id
                
        except Exception as e:
            logger.error(f"Error subscribing to topic '{topic}': {e}")
            return ""
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            subscription_id: ID of the subscription to remove
            
        Returns:
            bool: True if unsubscription was successful
        """
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                if subscription_id not in self._subscriptions:
                    logger.warning(f"Subscription {subscription_id} not found")
                    return False
                
                subscription = self._subscriptions[subscription_id]
                topic = subscription['topic']
                handler = subscription['handler']
                
                # Remove from topic handlers
                if topic in self._topic_handlers and handler in self._topic_handlers[topic]:
                    self._topic_handlers[topic].remove(handler)
                    if not self._topic_handlers[topic]:
                        del self._topic_handlers[topic]
                
                # Remove subscription
                del self._subscriptions[subscription_id]
                
                logger.info(f"Unsubscribed from topic '{topic}' with ID: {subscription_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error unsubscribing from {subscription_id}: {e}")
            return False
    
    def _message_handler(self, message: Message) -> None:
        """Internal message handler that routes messages to topic handlers"""
        if not self.enabled:
            return
        
        try:
            self._stats['messages_received'] += 1
            self._stats['last_received'] = datetime.utcnow()
            
            # Extract topic from message headers
            topic = message.headers.get('topic')
            if not topic:
                logger.warning("Message missing topic header")
                return
            
            # Route to topic handlers
            if topic in self._topic_handlers:
                handlers = self._topic_handlers[topic]
                for handler in handlers:
                    try:
                        handler(message)
                        self._stats['messages_processed'] += 1
                        logger.debug(f"Message processed by handler for topic '{topic}'")
                    except Exception as e:
                        self._stats['messages_failed'] += 1
                        logger.error(f"Error in message handler for topic '{topic}': {e}")
            else:
                logger.debug(f"No handlers registered for topic '{topic}'")
                
        except Exception as e:
            logger.error(f"Error in message handler: {e}")
            self._stats['messages_failed'] += 1
    
    def get_subscriptions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active subscriptions"""
        with self._lock:
            return self._subscriptions.copy()
    
    def get_topic_subscriptions(self, topic: str) -> List[str]:
        """Get subscription IDs for a specific topic"""
        with self._lock:
            return [
                sub_id for sub_id, sub_info in self._subscriptions.items()
                if sub_info['topic'] == topic and sub_info['active']
            ]
    
    def clear_subscriptions(self, topic: Optional[str] = None) -> int:
        """
        Clear subscriptions for a specific topic or all subscriptions.
        
        Args:
            topic: Optional topic to clear subscriptions for
            
        Returns:
            int: Number of subscriptions cleared
        """
        with self._lock:
            if topic:
                # Clear subscriptions for specific topic
                to_remove = [
                    sub_id for sub_id, sub_info in self._subscriptions.items()
                    if sub_info['topic'] == topic
                ]
            else:
                # Clear all subscriptions
                to_remove = list(self._subscriptions.keys())
            
            for sub_id in to_remove:
                self.unsubscribe(sub_id)
            
            return len(to_remove)


class AsyncMessageSubscriber(AsyncSubscriber):
    """Asynchronous message subscriber"""
    
    def __init__(self, message_bus: MessageBusProtocol, name: str = "AsyncMessageSubscriber"):
        super().__init__(name)
        self.message_bus = message_bus
        self._async_lock = asyncio.Lock()
        self._subscriptions: Dict[str, Dict[str, Any]] = {}
        self._topic_handlers: Dict[str, List[Callable[[Message], None]]] = {}
        self._subscription_counter = 0
    
    async def subscribe_async(self, topic: str, handler: Callable[[Message], None]) -> str:
        """
        Subscribe to a topic asynchronously.
        
        Args:
            topic: Topic to subscribe to
            handler: Function to call when messages arrive
            
        Returns:
            str: Subscription ID for later unsubscription
        """
        if not self.enabled:
            logger.warning(f"AsyncSubscriber {self.name} is disabled")
            return ""
        
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        try:
            async with self._async_lock:
                subscription_id = f"{self.name}_{self._subscription_counter}"
                self._subscription_counter += 1
                
                # Store subscription details
                self._subscriptions[subscription_id] = {
                    'topic': topic,
                    'handler': handler,
                    'created_at': datetime.utcnow(),
                    'active': True
                }
                
                # Add handler to topic
                if topic not in self._topic_handlers:
                    self._topic_handlers[topic] = []
                self._topic_handlers[topic].append(handler)
                
                # Subscribe via message bus (run sync operation in executor)
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(
                    None, 
                    self.message_bus.subscribe,
                    MessageType.EVENT,
                    self._message_handler_async,
                    0,  # priority
                    topic  # queue_name
                )
                
                if success:
                    logger.info(f"Async subscribed to topic '{topic}' with ID: {subscription_id}")
                else:
                    logger.error(f"Failed to async subscribe to topic '{topic}'")
                    # Clean up local state
                    del self._subscriptions[subscription_id]
                    self._topic_handlers[topic].remove(handler)
                    if not self._topic_handlers[topic]:
                        del self._topic_handlers[topic]
                    return ""
                
                return subscription_id
                
        except Exception as e:
            logger.error(f"Error async subscribing to topic '{topic}': {e}")
            return ""
    
    async def unsubscribe_async(self, subscription_id: str) -> bool:
        """
        Unsubscribe from a topic asynchronously.
        
        Args:
            subscription_id: ID of the subscription to remove
            
        Returns:
            bool: True if unsubscription was successful
        """
        if not self.enabled:
            return False
        
        try:
            async with self._async_lock:
                if subscription_id not in self._subscriptions:
                    logger.warning(f"Subscription {subscription_id} not found")
                    return False
                
                subscription = self._subscriptions[subscription_id]
                topic = subscription['topic']
                handler = subscription['handler']
                
                # Remove from topic handlers
                if topic in self._topic_handlers and handler in self._topic_handlers[topic]:
                    self._topic_handlers[topic].remove(handler)
                    if not self._topic_handlers[topic]:
                        del self._topic_handlers[topic]
                
                # Remove subscription
                del self._subscriptions[subscription_id]
                
                logger.info(f"Async unsubscribed from topic '{topic}' with ID: {subscription_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error async unsubscribing from {subscription_id}: {e}")
            return False
    
    async def _message_handler_async(self, message: Message) -> None:
        """Internal async message handler that routes messages to topic handlers"""
        if not self.enabled:
            return
        
        try:
            self._stats['messages_received'] += 1
            self._stats['last_received'] = datetime.utcnow()
            
            # Extract topic from message headers
            topic = message.headers.get('topic')
            if not topic:
                logger.warning("Message missing topic header")
                return
            
            # Route to topic handlers
            if topic in self._topic_handlers:
                handlers = self._topic_handlers[topic]
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            # Run sync handler in executor
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, handler, message)
                        
                        self._stats['messages_processed'] += 1
                        logger.debug(f"Message processed by async handler for topic '{topic}'")
                    except Exception as e:
                        self._stats['messages_failed'] += 1
                        logger.error(f"Error in async message handler for topic '{topic}': {e}")
            else:
                logger.debug(f"No handlers registered for topic '{topic}'")
                
        except Exception as e:
            logger.error(f"Error in async message handler: {e}")
            self._stats['messages_failed'] += 1
    
    def get_subscriptions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active subscriptions"""
        return self._subscriptions.copy()
    
    def get_topic_subscriptions(self, topic: str) -> List[str]:
        """Get subscription IDs for a specific topic"""
        return [
            sub_id for sub_id, sub_info in self._subscriptions.items()
            if sub_info['topic'] == topic and sub_info['active']
        ]
    
    async def clear_subscriptions_async(self, topic: Optional[str] = None) -> int:
        """
        Clear subscriptions for a specific topic or all subscriptions asynchronously.
        
        Args:
            topic: Optional topic to clear subscriptions for
            
        Returns:
            int: Number of subscriptions cleared
        """
        async with self._async_lock:
            if topic:
                # Clear subscriptions for specific topic
                to_remove = [
                    sub_id for sub_id, sub_info in self._subscriptions.items()
                    if sub_info['topic'] == topic
                ]
            else:
                # Clear all subscriptions
                to_remove = list(self._subscriptions.keys())
            
            for sub_id in to_remove:
                await self.unsubscribe_async(sub_id)
            
            return len(to_remove)


class TopicSubscriber(MessageSubscriber):
    """Topic-specific subscriber that maintains topic state"""
    
    def __init__(self, topic: str, message_bus: MessageBusProtocol, name: str = None):
        super().__init__(message_bus, name or f"TopicSubscriber_{topic}")
        self.topic = topic
        self._topic_stats = {
            'messages_received': 0,
            'handlers_count': 0,
            'last_activity': None
        }
    
    def subscribe(self, handler: Callable[[Message], None]) -> str:
        """
        Subscribe to the configured topic.
        
        Args:
            handler: Function to call when messages arrive
            
        Returns:
            str: Subscription ID for later unsubscription
        """
        return super().subscribe(self.topic, handler)
    
    def get_topic_stats(self) -> Dict[str, Any]:
        """Get topic-specific statistics"""
        return self._topic_stats.copy()
    
    def update_handler_count(self, count: int) -> None:
        """Update the handler count for this topic"""
        self._topic_stats['handlers_count'] = count
        self._topic_stats['last_activity'] = datetime.utcnow()


class AsyncTopicSubscriber(AsyncMessageSubscriber):
    """Asynchronous topic-specific subscriber"""
    
    def __init__(self, topic: str, message_bus: MessageBusProtocol, name: str = None):
        super().__init__(message_bus, name or f"AsyncTopicSubscriber_{topic}")
        self.topic = topic
        self._topic_stats = {
            'messages_received': 0,
            'handlers_count': 0,
            'last_activity': None
        }
    
    async def subscribe_async(self, handler: Callable[[Message], None]) -> str:
        """
        Subscribe to the configured topic asynchronously.
        
        Args:
            handler: Function to call when messages arrive
            
        Returns:
            str: Subscription ID for later unsubscription
        """
        return await super().subscribe_async(self.topic, handler)
    
    def get_topic_stats(self) -> Dict[str, Any]:
        """Get topic-specific statistics"""
        return self._topic_stats.copy()
    
    def update_handler_count(self, count: int) -> None:
        """Update the handler count for this topic"""
        self._topic_stats['handlers_count'] = count
        self._topic_stats['last_activity'] = datetime.utcnow()
