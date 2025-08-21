"""
Topic Manager
=============

Implements both synchronous and asynchronous topic managers for the pubsub system.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime
import threading
from abc import ABC, abstractmethod
import re

from ..types import Message, MessageType, Priority, DeliveryMode
from ..interfaces import MessageBusProtocol


logger = logging.getLogger(__name__)


class TopicManager(ABC):
    """Abstract base class for topic managers"""
    
    def __init__(self, name: str = "TopicManager"):
        self.name = name
        self.enabled = True
        self._stats = {
            'topics_created': 0,
            'topics_deleted': 0,
            'topics_active': 0,
            'last_activity': None
        }
    
    @abstractmethod
    def create_topic(self, topic_name: str, **kwargs) -> bool:
        """Create a new topic"""
        pass
    
    @abstractmethod
    def delete_topic(self, topic_name: str) -> bool:
        """Delete a topic"""
        pass
    
    @abstractmethod
    def topic_exists(self, topic_name: str) -> bool:
        """Check if a topic exists"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get topic manager statistics"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset topic manager statistics"""
        self._stats = {
            'topics_created': 0,
            'topics_deleted': 0,
            'topics_active': 0,
            'last_activity': None
        }


class AsyncTopicManager(ABC):
    """Abstract base class for asynchronous topic managers"""
    
    def __init__(self, name: str = "AsyncTopicManager"):
        self.name = name
        self.enabled = True
        self._stats = {
            'topics_created': 0,
            'topics_deleted': 0,
            'topics_active': 0,
            'last_activity': None
        }
    
    @abstractmethod
    async def create_topic_async(self, topic_name: str, **kwargs) -> bool:
        """Create a new topic asynchronously"""
        pass
    
    @abstractmethod
    async def delete_topic_async(self, topic_name: str) -> bool:
        """Delete a topic asynchronously"""
        pass
    
    @abstractmethod
    async def topic_exists_async(self, topic_name: str) -> bool:
        """Check if a topic exists asynchronously"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get topic manager statistics"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset topic manager statistics"""
        self._stats = {
            'topics_created': 0,
            'topics_deleted': 0,
            'topics_active': 0,
            'last_activity': None
        }


class MessageTopicManager(TopicManager):
    """Synchronous topic manager for message-based systems"""
    
    def __init__(self, message_bus: MessageBusProtocol, name: str = "MessageTopicManager"):
        super().__init__(name)
        self.message_bus = message_bus
        self._lock = threading.RLock()
        self._topics: Dict[str, Dict[str, Any]] = {}
        self._topic_patterns: Dict[str, str] = {}
        self._topic_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Topic naming rules
        self._topic_name_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_\-\.]*$')
        self._max_topic_length = 255
        self._reserved_prefixes = {'system.', 'internal.', 'temp.'}
    
    def create_topic(self, topic_name: str, **kwargs) -> bool:
        """
        Create a new topic.
        
        Args:
            topic_name: Name of the topic to create
            **kwargs: Additional topic properties
            
        Returns:
            bool: True if topic was created successfully
        """
        if not self.enabled:
            logger.warning(f"TopicManager {self.name} is disabled")
            return False
        
        if not self._validate_topic_name(topic_name):
            logger.error(f"Invalid topic name: {topic_name}")
            return False
        
        try:
            with self._lock:
                if topic_name in self._topics:
                    logger.warning(f"Topic '{topic_name}' already exists")
                    return False
                
                # Create topic metadata
                topic_metadata = {
                    'name': topic_name,
                    'created_at': datetime.utcnow(),
                    'created_by': kwargs.get('created_by', 'system'),
                    'description': kwargs.get('description', ''),
                    'max_subscribers': kwargs.get('max_subscribers', 1000),
                    'max_message_size': kwargs.get('max_message_size', 1024 * 1024),  # 1MB
                    'retention_policy': kwargs.get('retention_policy', 'default'),
                    'access_control': kwargs.get('access_control', {}),
                    'tags': kwargs.get('tags', []),
                    'active': True
                }
                
                # Store topic information
                self._topics[topic_name] = {
                    'metadata': topic_metadata,
                    'subscribers_count': 0,
                    'messages_count': 0,
                    'last_message_at': None,
                    'created_at': datetime.utcnow()
                }
                
                # Store metadata separately for easy access
                self._topic_metadata[topic_name] = topic_metadata
                
                # Update statistics
                self._stats['topics_created'] += 1
                self._stats['topics_active'] += 1
                self._stats['last_activity'] = datetime.utcnow()
                
                logger.info(f"Topic '{topic_name}' created successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error creating topic '{topic_name}': {e}")
            return False
    
    def delete_topic(self, topic_name: str) -> bool:
        """
        Delete a topic.
        
        Args:
            topic_name: Name of the topic to delete
            
        Returns:
            bool: True if topic was deleted successfully
        """
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                if topic_name not in self._topics:
                    logger.warning(f"Topic '{topic_name}' does not exist")
                    return False
                
                # Check if topic has active subscribers
                if self._topics[topic_name]['subscribers_count'] > 0:
                    logger.warning(f"Cannot delete topic '{topic_name}' with active subscribers")
                    return False
                
                # Remove topic
                del self._topics[topic_name]
                if topic_name in self._topic_metadata:
                    del self._topic_metadata[topic_name]
                
                # Update statistics
                self._stats['topics_deleted'] += 1
                self._stats['topics_active'] -= 1
                self._stats['last_activity'] = datetime.utcnow()
                
                logger.info(f"Topic '{topic_name}' deleted successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting topic '{topic_name}': {e}")
            return False
    
    def topic_exists(self, topic_name: str) -> bool:
        """
        Check if a topic exists.
        
        Args:
            topic_name: Name of the topic to check
            
        Returns:
            bool: True if topic exists
        """
        with self._lock:
            return topic_name in self._topics
    
    def get_topic_info(self, topic_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a topic.
        
        Args:
            topic_name: Name of the topic
            
        Returns:
            Optional[Dict[str, Any]]: Topic information or None if not found
        """
        with self._lock:
            if topic_name in self._topics:
                return self._topics[topic_name].copy()
            return None
    
    def get_all_topics(self) -> List[str]:
        """Get all topic names"""
        with self._lock:
            return list(self._topics.keys())
    
    def get_topics_by_pattern(self, pattern: str) -> List[str]:
        """
        Get topics matching a pattern.
        
        Args:
            pattern: Regex pattern to match topic names
            
        Returns:
            List[str]: List of matching topic names
        """
        try:
            regex = re.compile(pattern)
            with self._lock:
                return [topic for topic in self._topics.keys() if regex.match(topic)]
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
            return []
    
    def update_topic_metadata(self, topic_name: str, **kwargs) -> bool:
        """
        Update topic metadata.
        
        Args:
            topic_name: Name of the topic
            **kwargs: Metadata fields to update
            
        Returns:
            bool: True if update was successful
        """
        if not self.enabled:
            return False
        
        try:
            with self._lock:
                if topic_name not in self._topics:
                    logger.warning(f"Topic '{topic_name}' does not exist")
                    return False
                
                # Update metadata
                for key, value in kwargs.items():
                    if key in self._topic_metadata[topic_name]:
                        self._topic_metadata[topic_name][key] = value
                        logger.debug(f"Updated topic '{topic_name}' metadata: {key} = {value}")
                
                self._stats['last_activity'] = datetime.utcnow()
                return True
                
        except Exception as e:
            logger.error(f"Error updating topic '{topic_name}' metadata: {e}")
            return False
    
    def increment_subscriber_count(self, topic_name: str, delta: int = 1) -> bool:
        """
        Increment the subscriber count for a topic.
        
        Args:
            topic_name: Name of the topic
            delta: Amount to increment by (can be negative)
            
        Returns:
            bool: True if update was successful
        """
        try:
            with self._lock:
                if topic_name not in self._topics:
                    return False
                
                new_count = self._topics[topic_name]['subscribers_count'] + delta
                if new_count < 0:
                    new_count = 0
                
                self._topics[topic_name]['subscribers_count'] = new_count
                self._topics[topic_name]['last_message_at'] = datetime.utcnow()
                return True
                
        except Exception as e:
            logger.error(f"Error updating subscriber count for topic '{topic_name}': {e}")
            return False
    
    def increment_message_count(self, topic_name: str, delta: int = 1) -> bool:
        """
        Increment the message count for a topic.
        
        Args:
            topic_name: Name of the topic
            delta: Amount to increment by
            
        Returns:
            bool: True if update was successful
        """
        try:
            with self._lock:
                if topic_name not in self._topics:
                    return False
                
                self._topics[topic_name]['messages_count'] += delta
                self._topics[topic_name]['last_message_at'] = datetime.utcnow()
                return True
                
        except Exception as e:
            logger.error(f"Error updating message count for topic '{topic_name}': {e}")
            return False
    
    def _validate_topic_name(self, topic_name: str) -> bool:
        """
        Validate a topic name.
        
        Args:
            topic_name: Topic name to validate
            
        Returns:
            bool: True if topic name is valid
        """
        if not topic_name or not isinstance(topic_name, str):
            return False
        
        if len(topic_name) > self._max_topic_length:
            return False
        
        if not self._topic_name_pattern.match(topic_name):
            return False
        
        # Check for reserved prefixes
        for prefix in self._reserved_prefixes:
            if topic_name.startswith(prefix):
                return False
        
        return True
    
    def get_topic_statistics(self) -> Dict[str, Any]:
        """Get comprehensive topic statistics"""
        with self._lock:
            total_subscribers = sum(topic['subscribers_count'] for topic in self._topics.values())
            total_messages = sum(topic['messages_count'] for topic in self._topics.values())
            
            return {
                'total_topics': len(self._topics),
                'active_topics': self._stats['topics_active'],
                'total_subscribers': total_subscribers,
                'total_messages': total_messages,
                'topics_created': self._stats['topics_created'],
                'topics_deleted': self._stats['topics_deleted'],
                'last_activity': self._stats['last_activity']
            }


class AsyncMessageTopicManager(AsyncTopicManager):
    """Asynchronous topic manager for message-based systems"""
    
    def __init__(self, message_bus: MessageBusProtocol, name: str = "AsyncMessageTopicManager"):
        super().__init__(name)
        self.message_bus = message_bus
        self._async_lock = asyncio.Lock()
        self._topics: Dict[str, Dict[str, Any]] = {}
        self._topic_patterns: Dict[str, str] = {}
        self._topic_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Topic naming rules
        self._topic_name_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_\-\.]*$')
        self._max_topic_length = 255
        self._reserved_prefixes = {'system.', 'internal.', 'temp.'}
    
    async def create_topic_async(self, topic_name: str, **kwargs) -> bool:
        """
        Create a new topic asynchronously.
        
        Args:
            topic_name: Name of the topic to create
            **kwargs: Additional topic properties
            
        Returns:
            bool: True if topic was created successfully
        """
        if not self.enabled:
            logger.warning(f"AsyncTopicManager {self.name} is disabled")
            return False
        
        if not self._validate_topic_name(topic_name):
            logger.error(f"Invalid topic name: {topic_name}")
            return False
        
        try:
            async with self._async_lock:
                if topic_name in self._topics:
                    logger.warning(f"Topic '{topic_name}' already exists")
                    return False
                
                # Create topic metadata
                topic_metadata = {
                    'name': topic_name,
                    'created_at': datetime.utcnow(),
                    'created_by': kwargs.get('created_by', 'system'),
                    'description': kwargs.get('description', ''),
                    'max_subscribers': kwargs.get('max_subscribers', 1000),
                    'max_message_size': kwargs.get('max_message_size', 1024 * 1024),  # 1MB
                    'retention_policy': kwargs.get('retention_policy', 'default'),
                    'access_control': kwargs.get('access_control', {}),
                    'tags': kwargs.get('tags', []),
                    'active': True
                }
                
                # Store topic information
                self._topics[topic_name] = {
                    'metadata': topic_metadata,
                    'subscribers_count': 0,
                    'messages_count': 0,
                    'last_message_at': None,
                    'created_at': datetime.utcnow()
                }
                
                # Store metadata separately for easy access
                self._topic_metadata[topic_name] = topic_metadata
                
                # Update statistics
                self._stats['topics_created'] += 1
                self._stats['topics_active'] += 1
                self._stats['last_activity'] = datetime.utcnow()
                
                logger.info(f"Topic '{topic_name}' created asynchronously successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error creating topic '{topic_name}' asynchronously: {e}")
            return False
    
    async def delete_topic_async(self, topic_name: str) -> bool:
        """
        Delete a topic asynchronously.
        
        Args:
            topic_name: Name of the topic to delete
            
        Returns:
            bool: True if topic was deleted successfully
        """
        if not self.enabled:
            return False
        
        try:
            async with self._async_lock:
                if topic_name not in self._topics:
                    logger.warning(f"Topic '{topic_name}' does not exist")
                    return False
                
                # Check if topic has active subscribers
                if self._topics[topic_name]['subscribers_count'] > 0:
                    logger.warning(f"Cannot delete topic '{topic_name}' with active subscribers")
                    return False
                
                # Remove topic
                del self._topics[topic_name]
                if topic_name in self._topic_metadata:
                    del self._topic_metadata[topic_name]
                
                # Update statistics
                self._stats['topics_deleted'] += 1
                self._stats['topics_active'] -= 1
                self._stats['last_activity'] = datetime.utcnow()
                
                logger.info(f"Topic '{topic_name}' deleted asynchronously successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting topic '{topic_name}' asynchronously: {e}")
            return False
    
    async def topic_exists_async(self, topic_name: str) -> bool:
        """
        Check if a topic exists asynchronously.
        
        Args:
            topic_name: Name of the topic to check
            
        Returns:
            bool: True if topic exists
        """
        return topic_name in self._topics
    
    def get_topic_info(self, topic_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a topic.
        
        Args:
            topic_name: Name of the topic
            
        Returns:
            Optional[Dict[str, Any]]: Topic information or None if not found
        """
        if topic_name in self._topics:
            return self._topics[topic_name].copy()
        return None
    
    def get_all_topics(self) -> List[str]:
        """Get all topic names"""
        return list(self._topics.keys())
    
    def get_topics_by_pattern(self, pattern: str) -> List[str]:
        """
        Get topics matching a pattern.
        
        Args:
            pattern: Regex pattern to match topic names
            
        Returns:
            List[str]: List of matching topic names
        """
        try:
            regex = re.compile(pattern)
            return [topic for topic in self._topics.keys() if regex.match(topic)]
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
            return []
    
    async def update_topic_metadata_async(self, topic_name: str, **kwargs) -> bool:
        """
        Update topic metadata asynchronously.
        
        Args:
            topic_name: Name of the topic
            **kwargs: Metadata fields to update
            
        Returns:
            bool: True if update was successful
        """
        if not self.enabled:
            return False
        
        try:
            async with self._async_lock:
                if topic_name not in self._topics:
                    logger.warning(f"Topic '{topic_name}' does not exist")
                    return False
                
                # Update metadata
                for key, value in kwargs.items():
                    if key in self._topic_metadata[topic_name]:
                        self._topic_metadata[topic_name][key] = value
                        logger.debug(f"Updated topic '{topic_name}' metadata: {key} = {value}")
                
                self._stats['last_activity'] = datetime.utcnow()
                return True
                
        except Exception as e:
            logger.error(f"Error updating topic '{topic_name}' metadata asynchronously: {e}")
            return False
    
    async def increment_subscriber_count_async(self, topic_name: str, delta: int = 1) -> bool:
        """
        Increment the subscriber count for a topic asynchronously.
        
        Args:
            topic_name: Name of the topic
            delta: Amount to increment by (can be negative)
            
        Returns:
            bool: True if update was successful
        """
        try:
            async with self._async_lock:
                if topic_name not in self._topics:
                    return False
                
                new_count = self._topics[topic_name]['subscribers_count'] + delta
                if new_count < 0:
                    new_count = 0
                
                self._topics[topic_name]['subscribers_count'] = new_count
                self._topics[topic_name]['last_message_at'] = datetime.utcnow()
                return True
                
        except Exception as e:
            logger.error(f"Error updating subscriber count for topic '{topic_name}' asynchronously: {e}")
            return False
    
    async def increment_message_count_async(self, topic_name: str, delta: int = 1) -> bool:
        """
        Increment the message count for a topic asynchronously.
        
        Args:
            topic_name: Name of the topic
            delta: Amount to increment by
            
        Returns:
            bool: True if update was successful
        """
        try:
            async with self._async_lock:
                if topic_name not in self._topics:
                    return False
                
                self._topics[topic_name]['messages_count'] += delta
                self._topics[topic_name]['last_message_at'] = datetime.utcnow()
                return True
                
        except Exception as e:
            logger.error(f"Error updating message count for topic '{topic_name}' asynchronously: {e}")
            return False
    
    def _validate_topic_name(self, topic_name: str) -> bool:
        """
        Validate a topic name.
        
        Args:
            topic_name: Topic name to validate
            
        Returns:
            bool: True if topic name is valid
        """
        if not topic_name or not isinstance(topic_name, str):
            return False
        
        if len(topic_name) > self._max_topic_length:
            return False
        
        if not self._topic_name_pattern.match(topic_name):
            return False
        
        # Check for reserved prefixes
        for prefix in self._reserved_prefixes:
            if topic_name.startswith(prefix):
                return False
        
        return True
    
    def get_topic_statistics(self) -> Dict[str, Any]:
        """Get comprehensive topic statistics"""
        total_subscribers = sum(topic['subscribers_count'] for topic in self._topics.values())
        total_messages = sum(topic['messages_count'] for topic in self._topics.values())
        
        return {
            'total_topics': len(self._topics),
            'active_topics': self._stats['topics_active'],
            'total_subscribers': total_subscribers,
            'total_messages': total_messages,
            'topics_created': self._stats['topics_created'],
            'topics_deleted': self._stats['topics_deleted'],
            'last_activity': self._stats['last_activity']
        }
