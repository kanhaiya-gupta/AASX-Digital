"""
Message Bus
==========

Central message routing and distribution system for synchronous and asynchronous operations.
"""

import asyncio
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Callable, Set, Tuple
from collections import defaultdict, deque
from datetime import datetime
import uuid

from .types import Message, MessageType, MessageHandler, Subscription, Priority
from .interfaces import MessageBusProtocol


logger = logging.getLogger(__name__)


class MessageBus:
    """Synchronous message bus for message routing and distribution"""
    
    def __init__(self, name: str = "MessageBus"):
        self.name = name
        self._subscribers: Dict[MessageType, List[MessageHandler]] = defaultdict(list)
        self._subscriptions: Dict[str, Subscription] = {}
        self._destinations: Dict[str, Callable[[Message], None]] = {}
        self._pending_requests: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._enabled = True
        self._max_subscribers = 100
        self._stats = {
            'messages_published': 0,
            'messages_sent': 0,
            'requests_processed': 0,
            'errors': 0
        }
    
    def publish(self, message: Message) -> bool:
        """
        Publish a message to all subscribers.
        
        Args:
            message: The message to publish
            
        Returns:
            bool: True if message was published successfully
        """
        if not self._enabled:
            logger.warning(f"MessageBus {self.name} is disabled, ignoring message: {message.id}")
            return False
        
        if not isinstance(message, Message):
            logger.error(f"Invalid message type: {type(message)}")
            return False
        
        try:
            with self._lock:
                subscribers = self._subscribers.get(message.type, [])
                
                if not subscribers:
                    logger.debug(f"No subscribers for message type: {message.type.value}")
                    return True
                
                # Sort subscribers by priority
                sorted_subscribers = sorted(subscribers, key=lambda h: h.priority, reverse=True)
                
                # Call subscribers
                for handler_info in sorted_subscribers:
                    if not handler_info.enabled:
                        continue
                    
                    try:
                        handler_info.handler(message)
                        logger.debug(f"Handler {handler_info.handler_id} processed message: {message.id}")
                    except Exception as e:
                        logger.error(f"Error in message handler {handler_info.handler_id}: {e}")
                        self._stats['errors'] += 1
                
                self._stats['messages_published'] += 1
                logger.debug(f"Message {message.id} published to {len(sorted_subscribers)} subscribers")
                return True
                
        except Exception as e:
            logger.error(f"Error publishing message {message.id}: {e}")
            self._stats['errors'] += 1
            return False
    
    def subscribe(self, message_type: MessageType, handler: Callable[[Message], None], 
                  priority: int = 0, queue_name: Optional[str] = None) -> str:
        """
        Subscribe to messages of a specific type.
        
        Args:
            message_type: Type of message to subscribe to
            handler: Function to call when message is received
            priority: Handler priority (higher numbers execute first)
            queue_name: Optional queue name for message processing
            
        Returns:
            str: Subscription ID for later removal
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        handler_info = MessageHandler(
            message_type=message_type,
            handler=handler,
            priority=priority,
            queue_name=queue_name
        )
        
        subscription = Subscription(
            subscriber_id=handler_info.handler_id,
            message_type=message_type
        )
        
        with self._lock:
            self._subscribers[message_type].append(handler_info)
            self._subscriptions[subscription.subscription_id] = subscription
            
            # Check max subscribers limit
            if len(self._subscribers[message_type]) > self._max_subscribers:
                logger.warning(f"Max subscribers ({self._max_subscribers}) exceeded for message type: {message_type.value}")
        
        logger.debug(f"Registered subscription {subscription.subscription_id} for message type: {message_type.value}")
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from messages.
        
        Args:
            subscription_id: ID of the subscription to remove
            
        Returns:
            bool: True if subscription was removed
        """
        with self._lock:
            subscription = self._subscriptions.get(subscription_id)
            if not subscription:
                logger.warning(f"Subscription {subscription_id} not found")
                return False
            
            # Remove from subscribers
            message_type = subscription.message_type
            if message_type in self._subscribers:
                # Find and remove the handler
                for handler_info in self._subscribers[message_type]:
                    if handler_info.handler_id == subscription.subscriber_id:
                        self._subscribers[message_type].remove(handler_info)
                        break
                
                # Clean up empty lists
                if not self._subscribers[message_type]:
                    del self._subscribers[message_type]
            
            # Remove from subscriptions
            del self._subscriptions[subscription_id]
        
        logger.debug(f"Unregistered subscription {subscription_id}")
        return True
    
    def send(self, message: Message, destination: str) -> bool:
        """
        Send a message to a specific destination.
        
        Args:
            message: The message to send
            destination: Destination identifier
            
        Returns:
            bool: True if message was sent successfully
        """
        if not self._enabled:
            logger.warning(f"MessageBus {self.name} is disabled, ignoring send to: {destination}")
            return False
        
        try:
            with self._lock:
                if destination not in self._destinations:
                    logger.warning(f"Destination {destination} not found")
                    return False
                
                destination_handler = self._destinations[destination]
                destination_handler(message)
                
                self._stats['messages_sent'] += 1
                logger.debug(f"Message {message.id} sent to destination: {destination}")
                return True
                
        except Exception as e:
            logger.error(f"Error sending message {message.id} to {destination}: {e}")
            self._stats['errors'] += 1
            return False
    
    def register_destination(self, destination: str, handler: Callable[[Message], None]) -> bool:
        """
        Register a destination handler.
        
        Args:
            destination: Destination identifier
            handler: Function to handle messages sent to this destination
            
        Returns:
            bool: True if destination was registered
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        with self._lock:
            self._destinations[destination] = handler
        
        logger.debug(f"Registered destination: {destination}")
        return True
    
    def unregister_destination(self, destination: str) -> bool:
        """
        Unregister a destination.
        
        Args:
            destination: Destination identifier to remove
            
        Returns:
            bool: True if destination was removed
        """
        with self._lock:
            if destination not in self._destinations:
                logger.warning(f"Destination {destination} not found")
                return False
            
            del self._destinations[destination]
        
        logger.debug(f"Unregistered destination: {destination}")
        return True
    
    def request(self, message: Message, destination: str, timeout: Optional[float] = None) -> Optional[Message]:
        """
        Send a request and wait for a response.
        
        Args:
            message: The request message
            destination: Destination identifier
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            Optional[Message]: Response message or None if timeout
        """
        if not self._enabled:
            logger.warning(f"MessageBus {self.name} is disabled, ignoring request to: {destination}")
            return None
        
        try:
            # Generate correlation ID if not present
            if not message.correlation_id:
                message.correlation_id = str(uuid.uuid4())
            
            # Set reply-to for response routing
            reply_to = f"reply_{uuid.uuid4()}"
            message.reply_to = reply_to
            
            # Create response waiter
            response_received = threading.Event()
            response_data = {'message': None, 'received': False}
            
            def response_handler(response_msg: Message):
                if response_msg.correlation_id == message.correlation_id:
                    response_data['message'] = response_msg
                    response_data['received'] = True
                    response_received.set()
            
            # Register temporary response handler
            response_subscription_id = self.subscribe(MessageType.RESPONSE, response_handler)
            
            try:
                # Send the request
                if not self.send(message, destination):
                    return None
                
                # Wait for response
                if timeout:
                    if response_received.wait(timeout):
                        self._stats['requests_processed'] += 1
                        return response_data['message']
                    else:
                        logger.warning(f"Request timeout after {timeout} seconds")
                        return None
                else:
                    response_received.wait()
                    self._stats['requests_processed'] += 1
                    return response_data['message']
                    
            finally:
                # Clean up response handler
                self.unsubscribe(response_subscription_id)
                
        except Exception as e:
            logger.error(f"Error in request to {destination}: {e}")
            self._stats['errors'] += 1
            return None
    
    def get_subscription_count(self, message_type: Optional[MessageType] = None) -> int:
        """
        Get the number of subscriptions.
        
        Args:
            message_type: Optional message type to count subscriptions for
            
        Returns:
            int: Number of subscriptions
        """
        with self._lock:
            if message_type:
                return len(self._subscribers.get(message_type, []))
            else:
                return len(self._subscriptions)
    
    def clear_subscriptions(self, message_type: Optional[MessageType] = None) -> None:
        """
        Clear all subscriptions or subscriptions for a specific message type.
        
        Args:
            message_type: Optional message type to clear subscriptions for
        """
        with self._lock:
            if message_type:
                # Remove subscriptions for specific message type
                subscriptions_to_remove = []
                for sub_id, subscription in self._subscriptions.items():
                    if subscription.message_type == message_type:
                        subscriptions_to_remove.append(sub_id)
                
                for sub_id in subscriptions_to_remove:
                    del self._subscriptions[sub_id]
                
                if message_type in self._subscribers:
                    del self._subscribers[message_type]
                
                logger.info(f"Cleared {len(subscriptions_to_remove)} subscriptions for message type: {message_type.value}")
            else:
                # Clear all subscriptions
                count = len(self._subscriptions)
                self._subscribers.clear()
                self._subscriptions.clear()
                logger.info(f"Cleared all {count} subscriptions")
    
    def enable(self) -> None:
        """Enable the message bus"""
        self._enabled = True
        logger.info(f"MessageBus {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the message bus"""
        self._enabled = False
        logger.info(f"MessageBus {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if the message bus is enabled"""
        return self._enabled
    
    def set_max_subscribers(self, max_subscribers: int) -> None:
        """Set the maximum number of subscribers per message type"""
        if max_subscribers < 0:
            raise ValueError("Max subscribers must be non-negative")
        self._max_subscribers = max_subscribers
        logger.debug(f"Max subscribers set to {max_subscribers}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        with self._lock:
            return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset message bus statistics"""
        with self._lock:
            self._stats = {
                'messages_published': 0,
                'messages_sent': 0,
                'requests_processed': 0,
                'errors': 0
            }


class AsyncMessageBus(MessageBus):
    """Asynchronous message bus for message routing and distribution"""
    
    def __init__(self, name: str = "AsyncMessageBus"):
        super().__init__(name)
        self._async_subscribers: Dict[MessageType, List[MessageHandler]] = defaultdict(list)
        self._async_destinations: Dict[str, Callable[[Message], None]] = {}
        self._response_waiters: Dict[str, asyncio.Future] = {}
    
    def publish_async(self, message: Message) -> bool:
        """
        Publish a message asynchronously to all subscribers.
        
        Args:
            message: The message to publish
            
        Returns:
            bool: True if message was scheduled for publication
        """
        if not self._enabled:
            logger.warning(f"AsyncMessageBus {self.name} is disabled, ignoring message: {message.id}")
            return False
        
        try:
            # Schedule async publication
            asyncio.create_task(self._publish_async_internal(message))
            return True
        except Exception as e:
            logger.error(f"Error scheduling async message publication {message.id}: {e}")
            return False
    
    async def _publish_async_internal(self, message: Message) -> None:
        """Internal async message publication method"""
        try:
            with self._lock:
                sync_subscribers = self._subscribers.get(message.type, [])
                async_subscribers = self._async_subscribers.get(message.type, [])
                
                # Combine and sort subscribers by priority
                all_subscribers = sorted(
                    sync_subscribers + async_subscribers,
                    key=lambda h: h.priority,
                    reverse=True
                )
                
                if not all_subscribers:
                    logger.debug(f"No subscribers for async message type: {message.type.value}")
                    return
                
                # Call subscribers
                for handler_info in all_subscribers:
                    if not handler_info.enabled:
                        continue
                    
                    try:
                        if handler_info.is_async:
                            await handler_info.handler(message)
                        else:
                            # Run sync handlers in executor to avoid blocking
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, handler_info.handler, message)
                        
                        logger.debug(f"Async handler {handler_info.handler_id} processed message: {message.id}")
                    except Exception as e:
                        logger.error(f"Error in async message handler {handler_info.handler_id}: {e}")
                        self._stats['errors'] += 1
                
                self._stats['messages_published'] += 1
                logger.debug(f"Async message {message.id} published to {len(all_subscribers)} subscribers")
                
        except Exception as e:
            logger.error(f"Error in async message publication {message.id}: {e}")
            self._stats['errors'] += 1
    
    def send_async(self, message: Message, destination: str) -> bool:
        """
        Send a message asynchronously to a specific destination.
        
        Args:
            message: The message to send
            destination: Destination identifier
            
        Returns:
            bool: True if message was scheduled for sending
        """
        if not self._enabled:
            logger.warning(f"AsyncMessageBus {self.name} is disabled, ignoring async send to: {destination}")
            return False
        
        try:
            # Schedule async sending
            asyncio.create_task(self._send_async_internal(message, destination))
            return True
        except Exception as e:
            logger.error(f"Error scheduling async message sending {message.id} to {destination}: {e}")
            return False
    
    async def _send_async_internal(self, message: Message, destination: str) -> None:
        """Internal async message sending method"""
        try:
            with self._lock:
                if destination in self._destinations:
                    destination_handler = self._destinations[destination]
                    # Run sync handler in executor
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, destination_handler, message)
                elif destination in self._async_destinations:
                    destination_handler = self._async_destinations[destination]
                    await destination_handler(message)
                else:
                    logger.warning(f"Destination {destination} not found")
                    return
                
                self._stats['messages_sent'] += 1
                logger.debug(f"Async message {message.id} sent to destination: {destination}")
                
        except Exception as e:
            logger.error(f"Error in async message sending {message.id} to {destination}: {e}")
            self._stats['errors'] += 1
    
    async def request_async(self, message: Message, destination: str, timeout: Optional[float] = None) -> Optional[Message]:
        """
        Send a request asynchronously and wait for a response.
        
        Args:
            message: The request message
            destination: Destination identifier
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            Optional[Message]: Response message or None if timeout
        """
        if not self._enabled:
            logger.warning(f"AsyncMessageBus {self.name} is disabled, ignoring async request to: {destination}")
            return None
        
        try:
            # Generate correlation ID if not present
            if not message.correlation_id:
                message.correlation_id = str(uuid.uuid4())
            
            # Set reply-to for response routing
            reply_to = f"reply_{uuid.uuid4()}"
            message.reply_to = reply_to
            
            # Create response future
            response_future = asyncio.Future()
            self._response_waiters[message.correlation_id] = response_future
            
            # Register response handler
            def response_handler(response_msg: Message):
                if response_msg.correlation_id == message.correlation_id:
                    if not response_future.done():
                        response_future.set_result(response_msg)
            
            response_subscription_id = self.subscribe(MessageType.RESPONSE, response_handler)
            
            try:
                # Send the request asynchronously
                if not self.send_async(message, destination):
                    return None
                
                # Wait for response
                if timeout:
                    try:
                        response = await asyncio.wait_for(response_future, timeout)
                        self._stats['requests_processed'] += 1
                        return response
                    except asyncio.TimeoutError:
                        logger.warning(f"Async request timeout after {timeout} seconds")
                        return None
                else:
                    response = await response_future
                    self._stats['requests_processed'] += 1
                    return response
                    
            finally:
                # Clean up
                self.unsubscribe(response_subscription_id)
                if message.correlation_id in self._response_waiters:
                    del self._response_waiters[message.correlation_id]
                
        except Exception as e:
            logger.error(f"Error in async request to {destination}: {e}")
            self._stats['errors'] += 1
            return None
    
    def subscribe_async(self, message_type: MessageType, handler: Callable[[Message], None], 
                       priority: int = 0, queue_name: Optional[str] = None) -> str:
        """
        Subscribe to messages asynchronously.
        
        Args:
            message_type: Type of message to subscribe to
            handler: Async function to call when message is received
            priority: Handler priority (higher numbers execute first)
            queue_name: Optional queue name for message processing
            
        Returns:
            str: Subscription ID for later removal
        """
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError("Handler must be an async function")
        
        handler_info = MessageHandler(
            message_type=message_type,
            handler=handler,
            is_async=True,
            priority=priority,
            queue_name=queue_name
        )
        
        subscription = Subscription(
            subscriber_id=handler_info.handler_id,
            message_type=message_type
        )
        
        with self._lock:
            self._async_subscribers[message_type].append(handler_info)
            self._subscriptions[subscription.subscription_id] = subscription
        
        logger.debug(f"Registered async subscription {subscription.subscription_id} for message type: {message_type.value}")
        return subscription.subscription_id
    
    def register_async_destination(self, destination: str, handler: Callable[[Message], None]) -> bool:
        """
        Register an asynchronous destination handler.
        
        Args:
            destination: Destination identifier
            handler: Async function to handle messages sent to this destination
            
        Returns:
            bool: True if destination was registered
        """
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError("Handler must be an async function")
        
        with self._lock:
            self._async_destinations[destination] = handler
        
        logger.debug(f"Registered async destination: {destination}")
        return True
    
    def get_subscription_count(self, message_type: Optional[MessageType] = None) -> int:
        """Get the number of subscriptions including async ones"""
        with self._lock:
            if message_type:
                return (len(self._subscribers.get(message_type, [])) + 
                       len(self._async_subscribers.get(message_type, [])))
            else:
                return len(self._subscriptions)
    
    def clear_subscriptions(self, message_type: Optional[MessageType] = None) -> None:
        """Clear all subscriptions including async ones"""
        with self._lock:
            if message_type:
                # Remove subscriptions for specific message type
                subscriptions_to_remove = []
                for sub_id, subscription in self._subscriptions.items():
                    if subscription.message_type == message_type:
                        subscriptions_to_remove.append(sub_id)
                
                for sub_id in subscriptions_to_remove:
                    del self._subscriptions[sub_id]
                
                if message_type in self._subscribers:
                    del self._subscribers[message_type]
                if message_type in self._async_subscribers:
                    del self._async_subscribers[message_type]
                
                logger.info(f"Cleared {len(subscriptions_to_remove)} subscriptions for message type: {message_type.value}")
            else:
                # Clear all subscriptions
                count = len(self._subscriptions)
                self._subscribers.clear()
                self._async_subscribers.clear()
                self._subscriptions.clear()
                logger.info(f"Cleared all {count} subscriptions")
