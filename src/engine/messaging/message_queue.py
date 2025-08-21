"""
Message Queue
============

Asynchronous message processing and queue management system.
"""

import asyncio
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Callable
from collections import defaultdict, deque
from datetime import datetime
import uuid

from .types import Message, MessageType, Priority
from .interfaces import MessageQueueProtocol


logger = logging.getLogger(__name__)


class MessageQueue:
    """Synchronous message queue for message processing"""
    
    def __init__(self, name: str = "MessageQueue", max_queue_size: int = 10000):
        self.name = name
        self.max_queue_size = max_queue_size
        self._queues: Dict[str, deque] = defaultdict(deque)
        self._processors: Dict[str, List[Callable[[Message], None]]] = defaultdict(list)
        self._lock = threading.RLock()
        self._enabled = True
        self._stats = {
            'messages_enqueued': 0,
            'messages_dequeued': 0,
            'messages_processed': 0,
            'errors': 0
        }
    
    def enqueue(self, message: Message, queue_name: str = "default") -> bool:
        """
        Add a message to a queue.
        
        Args:
            message: The message to enqueue
            queue_name: Name of the queue
            
        Returns:
            bool: True if message was enqueued successfully
        """
        if not self._enabled:
            logger.warning(f"MessageQueue {self.name} is disabled, ignoring message: {message.id}")
            return False
        
        if not isinstance(message, Message):
            logger.error(f"Invalid message type: {type(message)}")
            return False
        
        try:
            with self._lock:
                queue = self._queues[queue_name]
                
                # Check queue size limit
                if len(queue) >= self.max_queue_size:
                    logger.warning(f"Queue {queue_name} is full, dropping message: {message.id}")
                    return False
                
                # Add message to queue
                queue.append(message)
                self._stats['messages_enqueued'] += 1
                
                logger.debug(f"Message {message.id} enqueued to {queue_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error enqueuing message {message.id}: {e}")
            self._stats['errors'] += 1
            return False
    
    def dequeue(self, queue_name: str = "default", timeout: Optional[float] = None) -> Optional[Message]:
        """
        Remove and return a message from a queue.
        
        Args:
            queue_name: Name of the queue
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            Optional[Message]: The message or None if timeout
        """
        try:
            with self._lock:
                queue = self._queues.get(queue_name)
                if not queue:
                    return None
                
                if timeout:
                    start_time = time.time()
                    while not queue and (time.time() - start_time) < timeout:
                        time.sleep(0.1)
                        with self._lock:
                            queue = self._queues.get(queue_name)
                
                if queue:
                    message = queue.popleft()
                    self._stats['messages_dequeued'] += 1
                    logger.debug(f"Message {message.id} dequeued from {queue_name}")
                    return message
                
                return None
                
        except Exception as e:
            logger.error(f"Error dequeuing from {queue_name}: {e}")
            self._stats['errors'] += 1
            return None
    
    def peek(self, queue_name: str = "default") -> Optional[Message]:
        """
        View the next message without removing it.
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            Optional[Message]: The next message or None if queue is empty
        """
        try:
            with self._lock:
                queue = self._queues.get(queue_name)
                if queue:
                    return queue[0]
                return None
                
        except Exception as e:
            logger.error(f"Error peeking at {queue_name}: {e}")
            self._stats['errors'] += 1
            return None
    
    def get_queue_size(self, queue_name: str = "default") -> int:
        """
        Get the number of messages in a queue.
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            int: Number of messages in the queue
        """
        try:
            with self._lock:
                queue = self._queues.get(queue_name)
                return len(queue) if queue else 0
                
        except Exception as e:
            logger.error(f"Error getting queue size for {queue_name}: {e}")
            return 0
    
    def get_queue_names(self) -> List[str]:
        """
        Get all queue names.
        
        Returns:
            List[str]: List of queue names
        """
        try:
            with self._lock:
                return list(self._queues.keys())
                
        except Exception as e:
            logger.error(f"Error getting queue names: {e}")
            return []
    
    def clear_queue(self, queue_name: str = "default") -> int:
        """
        Clear all messages from a queue.
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            int: Number of messages cleared
        """
        try:
            with self._lock:
                queue = self._queues.get(queue_name)
                if queue:
                    count = len(queue)
                    queue.clear()
                    logger.info(f"Cleared {count} messages from queue {queue_name}")
                    return count
                return 0
                
        except Exception as e:
            logger.error(f"Error clearing queue {queue_name}: {e}")
            self._stats['errors'] += 1
            return 0
    
    def delete_queue(self, queue_name: str) -> bool:
        """
        Delete a queue.
        
        Args:
            queue_name: Name of the queue to delete
            
        Returns:
            bool: True if queue was deleted
        """
        try:
            with self._lock:
                if queue_name in self._queues:
                    del self._queues[queue_name]
                    if queue_name in self._processors:
                        del self._processors[queue_name]
                    logger.info(f"Deleted queue: {queue_name}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting queue {queue_name}: {e}")
            self._stats['errors'] += 1
            return False
    
    def add_processor(self, queue_name: str, processor: Callable[[Message], None]) -> bool:
        """
        Add a message processor to a queue.
        
        Args:
            queue_name: Name of the queue
            processor: Function to process messages
            
        Returns:
            bool: True if processor was added
        """
        if not callable(processor):
            raise ValueError("Processor must be callable")
        
        try:
            with self._lock:
                self._processors[queue_name].append(processor)
                logger.debug(f"Added processor to queue: {queue_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding processor to {queue_name}: {e}")
            return False
    
    def remove_processor(self, queue_name: str, processor: Callable[[Message], None]) -> bool:
        """
        Remove a message processor from a queue.
        
        Args:
            queue_name: Name of the queue
            processor: Function to remove
            
        Returns:
            bool: True if processor was removed
        """
        try:
            with self._lock:
                if queue_name in self._processors:
                    processors = self._processors[queue_name]
                    if processor in processors:
                        processors.remove(processor)
                        logger.debug(f"Removed processor from queue: {queue_name}")
                        return True
                return False
                
        except Exception as e:
            logger.error(f"Error removing processor from {queue_name}: {e}")
            return False
    
    def process_queue(self, queue_name: str = "default", max_messages: Optional[int] = None) -> int:
        """
        Process messages from a queue.
        
        Args:
            queue_name: Name of the queue to process
            max_messages: Maximum number of messages to process (None for all)
            
        Returns:
            int: Number of messages processed
        """
        if not self._enabled:
            logger.warning(f"MessageQueue {self.name} is disabled")
            return 0
        
        try:
            processed_count = 0
            processors = self._processors.get(queue_name, [])
            
            if not processors:
                logger.warning(f"No processors registered for queue: {queue_name}")
                return 0
            
            while True:
                message = self.dequeue(queue_name, timeout=0.1)
                if not message:
                    break
                
                # Process message with all processors
                for processor in processors:
                    try:
                        processor(message)
                        self._stats['messages_processed'] += 1
                        logger.debug(f"Message {message.id} processed by processor in {queue_name}")
                    except Exception as e:
                        logger.error(f"Error in processor for message {message.id}: {e}")
                        self._stats['errors'] += 1
                
                processed_count += 1
                
                # Check max messages limit
                if max_messages and processed_count >= max_messages:
                    break
            
            logger.debug(f"Processed {processed_count} messages from queue {queue_name}")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing queue {queue_name}: {e}")
            self._stats['errors'] += 1
            return 0
    
    def enable(self) -> None:
        """Enable the message queue"""
        self._enabled = True
        logger.info(f"MessageQueue {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the message queue"""
        self._enabled = False
        logger.info(f"MessageQueue {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if the message queue is enabled"""
        return self._enabled
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message queue statistics"""
        with self._lock:
            stats = self._stats.copy()
            stats['total_queues'] = len(self._queues)
            stats['total_processors'] = sum(len(processors) for processors in self._processors.values())
            return stats
    
    def reset_stats(self) -> None:
        """Reset message queue statistics"""
        with self._lock:
            self._stats = {
                'messages_enqueued': 0,
                'messages_dequeued': 0,
                'messages_processed': 0,
                'errors': 0
            }


class AsyncMessageQueue(MessageQueue):
    """Asynchronous message queue for message processing"""
    
    def __init__(self, name: str = "AsyncMessageQueue", max_queue_size: int = 10000):
        super().__init__(name, max_queue_size)
        self._async_processors: Dict[str, List[Callable[[Message], None]]] = defaultdict(list)
        self._processing_tasks: Dict[str, asyncio.Task] = {}
    
    def enqueue_async(self, message: Message, queue_name: str = "default") -> bool:
        """
        Add a message to a queue asynchronously.
        
        Args:
            message: The message to enqueue
            queue_name: Name of the queue
            
        Returns:
            bool: True if message was enqueued successfully
        """
        if not self._enabled:
            logger.warning(f"AsyncMessageQueue {self.name} is disabled, ignoring message: {message.id}")
            return False
        
        try:
            # Schedule async enqueue
            asyncio.create_task(self._enqueue_async_internal(message, queue_name))
            return True
        except Exception as e:
            logger.error(f"Error scheduling async message enqueue {message.id}: {e}")
            return False
    
    async def _enqueue_async_internal(self, message: Message, queue_name: str) -> None:
        """Internal async message enqueue method"""
        try:
            # Run sync enqueue in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.enqueue, message, queue_name)
        except Exception as e:
            logger.error(f"Error in async message enqueue {message.id}: {e}")
            self._stats['errors'] += 1
    
    async def dequeue_async(self, queue_name: str = "default", timeout: Optional[float] = None) -> Optional[Message]:
        """
        Remove and return a message from a queue asynchronously.
        
        Args:
            queue_name: Name of the queue
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            Optional[Message]: The message or None if timeout
        """
        try:
            # Run sync dequeue in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.dequeue, queue_name, timeout)
        except Exception as e:
            logger.error(f"Error in async message dequeue from {queue_name}: {e}")
            self._stats['errors'] += 1
            return None
    
    def add_async_processor(self, queue_name: str, processor: Callable[[Message], None]) -> bool:
        """
        Add an asynchronous message processor to a queue.
        
        Args:
            queue_name: Name of the queue
            processor: Async function to process messages
            
        Returns:
            bool: True if processor was added
        """
        if not asyncio.iscoroutinefunction(processor):
            raise ValueError("Processor must be an async function")
        
        try:
            with self._lock:
                self._async_processors[queue_name].append(processor)
                logger.debug(f"Added async processor to queue: {queue_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding async processor to {queue_name}: {e}")
            return False
    
    def remove_async_processor(self, queue_name: str, processor: Callable[[Message], None]) -> bool:
        """
        Remove an asynchronous message processor from a queue.
        
        Args:
            queue_name: Name of the queue
            processor: Async function to remove
            
        Returns:
            bool: True if processor was removed
        """
        try:
            with self._lock:
                if queue_name in self._async_processors:
                    processors = self._async_processors[queue_name]
                    if processor in processors:
                        processors.remove(processor)
                        logger.debug(f"Removed async processor from queue: {queue_name}")
                        return True
                return False
                
        except Exception as e:
            logger.error(f"Error removing async processor from {queue_name}: {e}")
            return False
    
    async def process_queue_async(self, queue_name: str = "default", max_messages: Optional[int] = None) -> int:
        """
        Process messages from a queue asynchronously.
        
        Args:
            queue_name: Name of the queue to process
            max_messages: Maximum number of messages to process (None for all)
            
        Returns:
            int: Number of messages processed
        """
        if not self._enabled:
            logger.warning(f"AsyncMessageQueue {self.name} is disabled")
            return 0
        
        try:
            processed_count = 0
            sync_processors = self._processors.get(queue_name, [])
            async_processors = self._async_processors.get(queue_name, [])
            
            if not sync_processors and not async_processors:
                logger.warning(f"No processors registered for queue: {queue_name}")
                return 0
            
            while True:
                message = await self.dequeue_async(queue_name, timeout=0.1)
                if not message:
                    break
                
                # Process message with sync processors
                for processor in sync_processors:
                    try:
                        # Run sync processor in executor
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, processor, message)
                        self._stats['messages_processed'] += 1
                        logger.debug(f"Message {message.id} processed by sync processor in {queue_name}")
                    except Exception as e:
                        logger.error(f"Error in sync processor for message {message.id}: {e}")
                        self._stats['errors'] += 1
                
                # Process message with async processors
                for processor in async_processors:
                    try:
                        await processor(message)
                        self._stats['messages_processed'] += 1
                        logger.debug(f"Message {message.id} processed by async processor in {queue_name}")
                    except Exception as e:
                        logger.error(f"Error in async processor for message {message.id}: {e}")
                        self._stats['errors'] += 1
                
                processed_count += 1
                
                # Check max messages limit
                if max_messages and processed_count >= max_messages:
                    break
            
            logger.debug(f"Processed {processed_count} messages from queue {queue_name}")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing queue {queue_name} asynchronously: {e}")
            self._stats['errors'] += 1
            return 0
    
    def start_processing(self, queue_name: str = "default", interval: float = 1.0) -> bool:
        """
        Start continuous processing of a queue.
        
        Args:
            queue_name: Name of the queue to process
            interval: Processing interval in seconds
            
        Returns:
            bool: True if processing was started
        """
        if queue_name in self._processing_tasks:
            logger.warning(f"Processing already started for queue: {queue_name}")
            return False
        
        try:
            async def process_loop():
                while True:
                    try:
                        await self.process_queue_async(queue_name)
                        await asyncio.sleep(interval)
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        logger.error(f"Error in processing loop for {queue_name}: {e}")
                        await asyncio.sleep(interval)
            
            task = asyncio.create_task(process_loop())
            self._processing_tasks[queue_name] = task
            
            logger.info(f"Started continuous processing for queue: {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting processing for {queue_name}: {e}")
            return False
    
    def stop_processing(self, queue_name: str = "default") -> bool:
        """
        Stop continuous processing of a queue.
        
        Args:
            queue_name: Name of the queue to stop processing
            
        Returns:
            bool: True if processing was stopped
        """
        try:
            if queue_name in self._processing_tasks:
                task = self._processing_tasks[queue_name]
                task.cancel()
                del self._processing_tasks[queue_name]
                
                logger.info(f"Stopped continuous processing for queue: {queue_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error stopping processing for {queue_name}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message queue statistics including async processing info"""
        with self._lock:
            stats = super().get_stats()
            stats['active_processing_tasks'] = len(self._processing_tasks)
            stats['total_async_processors'] = sum(len(processors) for processors in self._async_processors.values())
            return stats
