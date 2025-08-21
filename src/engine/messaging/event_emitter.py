"""
Event Emitter
============

Core event emission and subscription system for synchronous and asynchronous operations.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Set
from collections import defaultdict
from datetime import datetime
import threading
import weakref

from .types import Event, EventType, EventHandler
from .interfaces import EventEmitterProtocol


logger = logging.getLogger(__name__)


class EventEmitter:
    """Synchronous event emitter for handling events"""
    
    def __init__(self, name: str = "EventEmitter"):
        self.name = name
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._once_handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._handler_registry: Dict[str, EventHandler] = {}
        self._lock = threading.RLock()
        self._enabled = True
        self._max_listeners = 10
        self._stats = {
            'events_emitted': 0,
            'handlers_called': 0,
            'errors': 0
        }
    
    def emit(self, event: Event) -> bool:
        """
        Emit an event to all registered handlers.
        
        Args:
            event: The event to emit
            
        Returns:
            bool: True if event was emitted successfully
        """
        if not self._enabled:
            logger.warning(f"EventEmitter {self.name} is disabled, ignoring event: {event.name}")
            return False
        
        if not isinstance(event, Event):
            logger.error(f"Invalid event type: {type(event)}")
            return False
        
        try:
            with self._lock:
                # Get all handlers for this event type
                handlers = self._handlers.get(event.type, [])
                once_handlers = self._once_handlers.get(event.type, [])
                
                # Combine handlers and sort by priority
                all_handlers = sorted(
                    handlers + once_handlers,
                    key=lambda h: h.priority,
                    reverse=True
                )
                
                if not all_handlers:
                    logger.debug(f"No handlers registered for event: {event.name}")
                    return True
                
                # Call handlers
                for handler_info in all_handlers:
                    if not handler_info.enabled:
                        continue
                    
                    try:
                        handler_info.handler(event)
                        self._stats['handlers_called'] += 1
                        logger.debug(f"Handler {handler_info.handler_id} processed event: {event.name}")
                    except Exception as e:
                        logger.error(f"Error in event handler {handler_info.handler_id}: {e}")
                        self._stats['errors'] += 1
                
                # Remove once handlers
                if once_handlers:
                    self._once_handlers[event.type] = []
                    for handler_info in once_handlers:
                        self._remove_handler_from_registry(handler_info.handler_id)
                
                self._stats['events_emitted'] += 1
                logger.debug(f"Event {event.name} emitted to {len(all_handlers)} handlers")
                return True
                
        except Exception as e:
            logger.error(f"Error emitting event {event.name}: {e}")
            self._stats['errors'] += 1
            return False
    
    def on(self, event_type: EventType, handler: Callable[[Event], None], priority: int = 0) -> str:
        """
        Register an event handler.
        
        Args:
            event_type: Type of event to listen for
            handler: Function to call when event occurs
            priority: Handler priority (higher numbers execute first)
            
        Returns:
            str: Handler ID for later removal
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        handler_info = EventHandler(
            event_type=event_type,
            handler=handler,
            priority=priority
        )
        
        with self._lock:
            self._handlers[event_type].append(handler_info)
            self._handler_registry[handler_info.handler_id] = handler_info
            
            # Check max listeners limit
            if len(self._handlers[event_type]) > self._max_listeners:
                logger.warning(f"Max listeners ({self._max_listeners}) exceeded for event type: {event_type.value}")
        
        logger.debug(f"Registered handler {handler_info.handler_id} for event type: {event_type.value}")
        return handler_info.handler_id
    
    def once(self, event_type: EventType, handler: Callable[[Event], None]) -> str:
        """
        Register a one-time event handler.
        
        Args:
            event_type: Type of event to listen for
            handler: Function to call when event occurs
            
        Returns:
            str: Handler ID for later removal
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        handler_info = EventHandler(
            event_type=event_type,
            handler=handler,
            priority=0
        )
        
        with self._lock:
            self._once_handlers[event_type].append(handler_info)
            self._handler_registry[handler_info.handler_id] = handler_info
        
        logger.debug(f"Registered one-time handler {handler_info.handler_id} for event type: {event_type.value}")
        return handler_info.handler_id
    
    def off(self, handler_id: str) -> bool:
        """
        Unregister an event handler.
        
        Args:
            handler_id: ID of the handler to remove
            
        Returns:
            bool: True if handler was removed
        """
        with self._lock:
            handler_info = self._handler_registry.get(handler_id)
            if not handler_info:
                logger.warning(f"Handler {handler_id} not found")
                return False
            
            # Remove from appropriate list
            if handler_info in self._handlers[handler_info.event_type]:
                self._handlers[handler_info.event_type].remove(handler_info)
            elif handler_info in self._once_handlers[handler_info.event_type]:
                self._once_handlers[handler_info.event_type].remove(handler_info)
            
            # Remove from registry
            del self._handler_registry[handler_id]
            
            # Clean up empty lists
            if not self._handlers[handler_info.event_type]:
                del self._handlers[handler_info.event_type]
            if not self._once_handlers[handler_info.event_type]:
                del self._once_handlers[handler_info.event_type]
        
        logger.debug(f"Unregistered handler {handler_id}")
        return True
    
    def get_handler_count(self, event_type: Optional[EventType] = None) -> int:
        """
        Get the number of registered handlers.
        
        Args:
            event_type: Optional event type to count handlers for
            
        Returns:
            int: Number of handlers
        """
        with self._lock:
            if event_type:
                return (len(self._handlers.get(event_type, [])) + 
                       len(self._once_handlers.get(event_type, [])))
            else:
                return len(self._handler_registry)
    
    def clear_handlers(self, event_type: Optional[EventType] = None) -> None:
        """
        Clear all handlers or handlers for a specific event type.
        
        Args:
            event_type: Optional event type to clear handlers for
        """
        with self._lock:
            if event_type:
                # Remove handlers for specific event type
                handlers_to_remove = []
                for handler_id, handler_info in self._handler_registry.items():
                    if handler_info.event_type == event_type:
                        handlers_to_remove.append(handler_id)
                
                for handler_id in handlers_to_remove:
                    del self._handler_registry[handler_id]
                
                if event_type in self._handlers:
                    del self._handlers[event_type]
                if event_type in self._once_handlers:
                    del self._once_handlers[event_type]
                
                logger.info(f"Cleared {len(handlers_to_remove)} handlers for event type: {event_type.value}")
            else:
                # Clear all handlers
                count = len(self._handler_registry)
                self._handlers.clear()
                self._once_handlers.clear()
                self._handler_registry.clear()
                logger.info(f"Cleared all {count} handlers")
    
    def enable(self) -> None:
        """Enable the event emitter"""
        self._enabled = True
        logger.info(f"EventEmitter {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the event emitter"""
        self._enabled = False
        logger.info(f"EventEmitter {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if the event emitter is enabled"""
        return self._enabled
    
    def set_max_listeners(self, max_listeners: int) -> None:
        """Set the maximum number of listeners per event type"""
        if max_listeners < 0:
            raise ValueError("Max listeners must be non-negative")
        self._max_listeners = max_listeners
        logger.debug(f"Max listeners set to {max_listeners}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event emitter statistics"""
        with self._lock:
            return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset event emitter statistics"""
        with self._lock:
            self._stats = {
                'events_emitted': 0,
                'handlers_called': 0,
                'errors': 0
            }
    
    def _remove_handler_from_registry(self, handler_id: str) -> None:
        """Remove a handler from the registry"""
        if handler_id in self._handler_registry:
            del self._handler_registry[handler_id]


class AsyncEventEmitter(EventEmitter):
    """Asynchronous event emitter for handling events"""
    
    def __init__(self, name: str = "AsyncEventEmitter"):
        super().__init__(name)
        self._loop = None
        self._async_handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._async_once_handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
    
    def emit_async(self, event: Event) -> bool:
        """
        Emit an event asynchronously to all registered handlers.
        
        Args:
            event: The event to emit
            
        Returns:
            bool: True if event was scheduled for emission
        """
        if not self._enabled:
            logger.warning(f"AsyncEventEmitter {self.name} is disabled, ignoring event: {event.name}")
            return False
        
        try:
            # Schedule async emission
            asyncio.create_task(self._emit_async_internal(event))
            return True
        except Exception as e:
            logger.error(f"Error scheduling async event emission {event.name}: {e}")
            return False
    
    async def _emit_async_internal(self, event: Event) -> None:
        """Internal async event emission method"""
        try:
            with self._lock:
                # Get all handlers for this event type
                sync_handlers = self._handlers.get(event.type, [])
                once_handlers = self._once_handlers.get(event.type, [])
                async_handlers = self._async_handlers.get(event.type, [])
                async_once_handlers = self._async_once_handlers.get(event.type, [])
                
                # Combine handlers and sort by priority
                all_handlers = sorted(
                    sync_handlers + once_handlers + async_handlers + async_once_handlers,
                    key=lambda h: h.priority,
                    reverse=True
                )
                
                if not all_handlers:
                    logger.debug(f"No handlers registered for async event: {event.name}")
                    return
                
                # Call handlers
                for handler_info in all_handlers:
                    if not handler_info.enabled:
                        continue
                    
                    try:
                        if handler_info.is_async:
                            await handler_info.handler(event)
                        else:
                            # Run sync handlers in executor to avoid blocking
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, handler_info.handler, event)
                        
                        self._stats['handlers_called'] += 1
                        logger.debug(f"Async handler {handler_info.handler_id} processed event: {event.name}")
                    except Exception as e:
                        logger.error(f"Error in async event handler {handler_info.handler_id}: {e}")
                        self._stats['errors'] += 1
                
                # Remove once handlers
                if once_handlers:
                    self._once_handlers[event.type] = []
                    for handler_info in once_handlers:
                        self._remove_handler_from_registry(handler_info.handler_id)
                
                if async_once_handlers:
                    self._async_once_handlers[event.type] = []
                    for handler_info in async_once_handlers:
                        self._remove_handler_from_registry(handler_info.handler_id)
                
                self._stats['events_emitted'] += 1
                logger.debug(f"Async event {event.name} emitted to {len(all_handlers)} handlers")
                
        except Exception as e:
            logger.error(f"Error in async event emission {event.name}: {e}")
            self._stats['errors'] += 1
    
    def on_async(self, event_type: EventType, handler: Callable[[Event], None], priority: int = 0) -> str:
        """
        Register an asynchronous event handler.
        
        Args:
            event_type: Type of event to listen for
            handler: Async function to call when event occurs
            priority: Handler priority (higher numbers execute first)
            
        Returns:
            str: Handler ID for later removal
        """
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError("Handler must be an async function")
        
        handler_info = EventHandler(
            event_type=event_type,
            handler=handler,
            is_async=True,
            priority=priority
        )
        
        with self._lock:
            self._async_handlers[event_type].append(handler_info)
            self._handler_registry[handler_info.handler_id] = handler_info
        
        logger.debug(f"Registered async handler {handler_info.handler_id} for event type: {event_type.value}")
        return handler_info.handler_id
    
    def once_async(self, event_type: EventType, handler: Callable[[Event], None]) -> str:
        """
        Register a one-time asynchronous event handler.
        
        Args:
            event_type: Type of event to listen for
            handler: Async function to call when event occurs
            
        Returns:
            str: Handler ID for later removal
        """
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError("Handler must be an async function")
        
        handler_info = EventHandler(
            event_type=event_type,
            handler=handler,
            is_async=True,
            priority=0
        )
        
        with self._lock:
            self._async_once_handlers[event_type].append(handler_info)
            self._handler_registry[handler_info.handler_id] = handler_info
        
        logger.debug(f"Registered async one-time handler {handler_info.handler_id} for event type: {event_type.value}")
        return handler_info.handler_id
    
    def get_handler_count(self, event_type: Optional[EventType] = None) -> int:
        """Get the number of registered handlers including async ones"""
        with self._lock:
            if event_type:
                return (len(self._handlers.get(event_type, [])) + 
                       len(self._once_handlers.get(event_type, [])) +
                       len(self._async_handlers.get(event_type, [])) +
                       len(self._async_once_handlers.get(event_type, [])))
            else:
                return len(self._handler_registry)
    
    def clear_handlers(self, event_type: Optional[EventType] = None) -> None:
        """Clear all handlers including async ones"""
        with self._lock:
            if event_type:
                # Remove handlers for specific event type
                handlers_to_remove = []
                for handler_id, handler_info in self._handler_registry.items():
                    if handler_info.event_type == event_type:
                        handlers_to_remove.append(handler_id)
                
                for handler_id in handlers_to_remove:
                    del self._handler_registry[handler_id]
                
                if event_type in self._handlers:
                    del self._handlers[event_type]
                if event_type in self._once_handlers:
                    del self._once_handlers[event_type]
                if event_type in self._async_handlers:
                    del self._async_handlers[event_type]
                if event_type in self._async_once_handlers:
                    del self._async_once_handlers[event_type]
                
                logger.info(f"Cleared {len(handlers_to_remove)} handlers for event type: {event_type.value}")
            else:
                # Clear all handlers
                count = len(self._handler_registry)
                self._handlers.clear()
                self._once_handlers.clear()
                self._async_handlers.clear()
                self._async_once_handlers.clear()
                self._handler_registry.clear()
                logger.info(f"Cleared all {count} handlers")
