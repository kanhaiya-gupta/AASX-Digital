"""
Event Handlers for Twin Registry Population
Handles ETL events and other system events to trigger registry population
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Coroutine
from datetime import datetime, timezone
from dataclasses import dataclass

from .event_types import Event, EventType, EventPriority, EventStatus
from .event_bus import EventBus

logger = logging.getLogger(__name__)


@dataclass
class EventHandlerConfig:
    """Configuration for event handlers"""
    handler_name: str
    event_types: List[EventType]
    priority: EventPriority
    async_execution: bool = True
    retry_count: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0


class EventHandlers:
    """Event handlers for twin registry population"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.handlers: Dict[str, Callable] = {}
        self.handler_configs: Dict[str, EventHandlerConfig] = {}
        self.execution_stats: Dict[str, Dict[str, Any]] = {}
        
    async def register_handler(
        self,
        config: EventHandlerConfig,
        handler_func: Callable
    ) -> None:
        """Register an event handler"""
        try:
            # Register with event bus
            for event_type in config.event_types:
                self.event_bus.subscribe(event_type, handler_func)
            
            # Store handler and config
            self.handlers[config.handler_name] = handler_func
            self.handler_configs[config.handler_name] = config
            
            # Initialize stats
            self.execution_stats[config.handler_name] = {
                "total_events": 0,
                "successful_events": 0,
                "failed_events": 0,
                "last_execution": None,
                "average_execution_time": 0.0,
                "total_execution_time": 0.0
            }
            
            logger.info(f"Registered event handler: {config.handler_name}")
            
        except Exception as e:
            logger.error(f"Failed to register handler {config.handler_name}: {e}")
            raise
    
    async def unregister_handler(self, handler_name: str) -> None:
        """Unregister an event handler"""
        try:
            if handler_name in self.handlers:
                handler_func = self.handlers[handler_name]
                config = self.handler_configs[handler_name]
                
                # Unregister from event bus
                for event_type in config.event_types:
                    self.event_bus.unsubscribe(event_type, handler_func)
                
                # Remove from local storage
                del self.handlers[handler_name]
                del self.handler_configs[handler_name]
                del self.execution_stats[handler_name]
                
                logger.info(f"Unregistered event handler: {handler_name}")
                
        except Exception as e:
            logger.error(f"Failed to unregister handler {handler_name}: {e}")
            raise
    
    async def execute_handler(
        self,
        handler_name: str,
        event: Event,
        **kwargs
    ) -> bool:
        """Execute a specific event handler"""
        try:
            if handler_name not in self.handlers:
                logger.error(f"Handler not found: {handler_name}")
                return False
            
            config = self.handler_configs[handler_name]
            handler_func = self.handlers[handler_name]
            stats = self.execution_stats[handler_name]
            
            # Update stats
            stats["total_events"] += 1
            start_time = datetime.now(timezone.utc)
            
            # Execute handler
            if config.async_execution:
                result = await self._execute_async_handler(
                    handler_func, event, config, **kwargs
                )
            else:
                result = await self._execute_sync_handler(
                    handler_func, event, config, **kwargs
                )
            
            # Update execution stats
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            stats["last_execution"] = start_time
            stats["total_execution_time"] += execution_time
            stats["average_execution_time"] = (
                stats["total_execution_time"] / stats["total_events"]
            )
            
            if result:
                stats["successful_events"] += 1
                logger.info(f"Handler {handler_name} executed successfully")
            else:
                stats["failed_events"] += 1
                logger.warning(f"Handler {handler_name} execution failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing handler {handler_name}: {e}")
            if handler_name in self.execution_stats:
                self.execution_stats[handler_name]["failed_events"] += 1
            return False
    
    async def _execute_async_handler(
        self,
        handler_func: Callable,
        event: Event,
        config: EventHandlerConfig,
        **kwargs
    ) -> bool:
        """Execute an async event handler with retry logic"""
        for attempt in range(config.retry_count):
            try:
                # Execute with timeout
                if asyncio.iscoroutinefunction(handler_func):
                    result = await asyncio.wait_for(
                        handler_func(event, **kwargs),
                        timeout=config.timeout
                    )
                else:
                    # Handle sync functions in async context
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None, handler_func, event, **kwargs
                    )
                
                return bool(result)
                
            except asyncio.TimeoutError:
                logger.warning(
                    f"Handler {config.handler_name} timed out (attempt {attempt + 1})"
                )
                if attempt < config.retry_count - 1:
                    await asyncio.sleep(config.retry_delay)
                    
            except Exception as e:
                logger.error(
                    f"Handler {config.handler_name} failed (attempt {attempt + 1}): {e}"
                )
                if attempt < config.retry_count - 1:
                    await asyncio.sleep(config.retry_delay)
        
        return False
    
    async def _execute_sync_handler(
        self,
        handler_func: Callable,
        event: Event,
        config: EventHandlerConfig,
        **kwargs
    ) -> bool:
        """Execute a sync event handler"""
        try:
            result = handler_func(event, **kwargs)
            return bool(result)
        except Exception as e:
            logger.error(f"Sync handler {config.handler_name} failed: {e}")
            return False
    
    def get_handler_stats(self, handler_name: str) -> Optional[Dict[str, Any]]:
        """Get execution statistics for a handler"""
        return self.execution_stats.get(handler_name)
    
    def get_all_handler_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get execution statistics for all handlers"""
        return self.execution_stats.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all event handlers"""
        health_status = {
            "total_handlers": len(self.handlers),
            "active_handlers": 0,
            "handler_details": {},
            "overall_status": "healthy"
        }
        
        for handler_name, config in self.handler_configs.items():
            stats = self.execution_stats.get(handler_name, {})
            
            # Calculate success rate
            total_events = stats.get("total_events", 0)
            successful_events = stats.get("successful_events", 0)
            success_rate = (
                (successful_events / total_events * 100) if total_events > 0 else 0
            )
            
            # Determine handler status
            if total_events == 0:
                status = "idle"
            elif success_rate >= 90:
                status = "healthy"
            elif success_rate >= 70:
                status = "warning"
            else:
                status = "unhealthy"
            
            handler_detail = {
                "event_types": [et.value for et in config.event_types],
                "priority": config.priority.value,
                "async_execution": config.async_execution,
                "status": status,
                "success_rate": round(success_rate, 2),
                "total_events": total_events,
                "last_execution": stats.get("last_execution"),
                "average_execution_time": round(
                    stats.get("average_execution_time", 0.0), 3
                )
            }
            
            health_status["handler_details"][handler_name] = handler_detail
            
            if status == "healthy":
                health_status["active_handlers"] += 1
            elif status == "unhealthy":
                health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    async def cleanup(self) -> None:
        """Cleanup event handlers"""
        try:
            # Unregister all handlers
            handler_names = list(self.handlers.keys())
            for handler_name in handler_names:
                await self.unregister_handler(handler_name)
            
            logger.info("Event handlers cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during event handlers cleanup: {e}")
            raise


# Predefined handler configurations
class HandlerConfigs:
    """Predefined handler configurations for common use cases"""
    
    @staticmethod
    def file_upload_handler() -> EventHandlerConfig:
        """Configuration for file upload event handler"""
        return EventHandlerConfig(
            handler_name="file_upload_handler",
            event_types=[EventType.FILE_UPLOAD],
            priority=EventPriority.HIGH,
            async_execution=True,
            retry_count=3,
            retry_delay=2.0,
            timeout=60.0
        )
    
    @staticmethod
    def etl_completion_handler() -> EventHandlerConfig:
        """Configuration for ETL completion event handler"""
        return EventHandlerConfig(
            handler_name="etl_completion_handler",
            event_types=[EventType.ETL_COMPLETION],
            priority=EventPriority.HIGH,
            async_execution=True,
            retry_count=5,
            retry_delay=5.0,
            timeout=120.0
        )
    
    @staticmethod
    def registry_population_handler() -> EventHandlerConfig:
        """Configuration for registry population event handler"""
        return EventHandlerConfig(
            handler_name="registry_population_handler",
            event_types=[EventType.REGISTRY_POPULATION],
            priority=EventPriority.MEDIUM,
            async_execution=True,
            retry_count=3,
            retry_delay=3.0,
            timeout=90.0
        )
    
    @staticmethod
    def validation_handler() -> EventHandlerConfig:
        """Configuration for validation event handler"""
        return EventHandlerConfig(
            handler_name="validation_handler",
            event_types=[EventType.VALIDATION],
            priority=EventPriority.MEDIUM,
            async_execution=True,
            retry_count=2,
            retry_delay=1.0,
            timeout=45.0
        )
    
    @staticmethod
    def system_event_handler() -> EventHandlerConfig:
        """Configuration for system event handler"""
        return EventHandlerConfig(
            handler_name="system_event_handler",
            event_types=[EventType.SYSTEM_EVENT],
            priority=EventPriority.LOW,
            async_execution=False,
            retry_count=1,
            retry_delay=0.0,
            timeout=30.0
        )
