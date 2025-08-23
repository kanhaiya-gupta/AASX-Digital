"""
Knowledge Graph Neo4j Event Manager

Main orchestrator for the event-driven automation system.
Manages event bus, handlers, and provides high-level event management interface.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
import uuid

from .event_bus import KGNeo4jEventBus
from .event_handlers import (
    get_handler,
    get_available_handlers,
    BaseEventHandler
)
from .event_types import (
    KGNeo4jEvent,
    GraphCreationEvent,
    GraphStatusChangeEvent,
    Neo4jOperationEvent,
    AIInsightsEvent,
    HealthMonitoringEvent,
    EventPriority,
    EventStatus,
    create_event
)

logger = logging.getLogger(__name__)


class KGNeo4jEventManager:
    """Main event manager for Knowledge Graph Neo4j operations."""
    
    def __init__(self, max_queue_size: int = 1000, worker_count: int = 4):
        """Initialize the event manager."""
        self.event_bus = KGNeo4jEventBus(max_queue_size, worker_count)
        self.handlers: Dict[str, BaseEventHandler] = {}
        self.is_initialized = False
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Performance tracking
        self.total_events_processed = 0
        self.total_events_failed = 0
        self.start_time = datetime.now(timezone.utc)
        
        logger.info("Knowledge Graph Neo4j Event Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize the event manager and start the event bus."""
        try:
            # Initialize all handlers
            await self._initialize_handlers()
            
            # Start the event bus
            await self.event_bus.start()
            
            # Set up default event subscriptions
            await self._setup_default_subscriptions()
            
            self.is_initialized = True
            logger.info("Knowledge Graph Neo4j Event Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize event manager: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Clean up the event manager and stop the event bus."""
        try:
            # Stop the event bus
            await self.event_bus.stop()
            
            # Clear handlers
            self.handlers.clear()
            
            self.is_initialized = False
            logger.info("Knowledge Graph Neo4j Event Manager cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _initialize_handlers(self) -> None:
        """Initialize all event handlers."""
        available_handlers = get_available_handlers()
        
        for handler_type in available_handlers:
            try:
                handler = get_handler(handler_type)
                self.handlers[handler_type] = handler
                logger.debug(f"Handler {handler_type} initialized")
            except Exception as e:
                logger.error(f"Failed to initialize handler {handler_type}: {e}")
    
    async def _setup_default_subscriptions(self) -> None:
        """Set up default event subscriptions for all handlers."""
        # Subscribe handlers to their respective event types
        subscription_mappings = {
            "graph_lifecycle": ["graph_creation", "graph_status_change"],
            "neo4j_operation": ["neo4j_operation"],
            "ai_insights": ["ai_insights"],
            "health_monitoring": ["health_monitoring"]
        }
        
        for handler_type, event_types in subscription_mappings.items():
            if handler_type in self.handlers:
                handler = self.handlers[handler_type]
                
                # Subscribe handler to event types
                subscription_id = self.event_bus.subscribe(
                    handler=handler.handle,
                    event_types=event_types
                )
                
                logger.debug(f"Handler {handler_type} subscribed to events: {event_types}")
    
    # High-level event publishing methods
    
    async def publish_graph_creation(
        self,
        file_id: str,
        graph_name: str,
        workflow_source: str = "aasx_file",
        graph_config: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        dept_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL
    ) -> str:
        """Publish a graph creation event."""
        event = GraphCreationEvent(
            event_id=str(uuid.uuid4()),
            file_id=file_id,
            graph_name=graph_name,
            workflow_source=workflow_source,
            graph_config=graph_config or {},
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            priority=priority
        )
        
        success = await self.event_bus.publish(event)
        if success:
            self._record_event(event)
            logger.info(f"Graph creation event published for {graph_name} from {workflow_source}")
            return event.event_id
        else:
            raise RuntimeError("Failed to publish graph creation event")
    
    async def publish_graph_status_change(
        self,
        graph_id: str,
        old_status: Dict[str, Any],
        new_status: Dict[str, Any],
        change_reason: str = "manual_update",
        change_source: str = "system",
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        dept_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL
    ) -> str:
        """Publish a graph status change event."""
        event = GraphStatusChangeEvent(
            event_id=str(uuid.uuid4()),
            graph_id=graph_id,
            old_status=old_status,
            new_status=new_status,
            change_reason=change_reason,
            change_source=change_source,
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            priority=priority
        )
        
        success = await self.event_bus.publish(event)
        if success:
            self._record_event(event)
            logger.info(f"Graph status change event published for {graph_id}")
            return event.event_id
        else:
            raise RuntimeError("Failed to publish graph status change event")
    
    async def publish_neo4j_operation(
        self,
        graph_id: str,
        operation_type: str,
        operation_config: Optional[Dict[str, Any]] = None,
        neo4j_connection_id: Optional[str] = None,
        cypher_query: Optional[str] = None,
        query_parameters: Optional[Dict[str, Any]] = None,
        batch_size: Optional[int] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        dept_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL
    ) -> str:
        """Publish a Neo4j operation event."""
        event = Neo4jOperationEvent(
            event_id=str(uuid.uuid4()),
            graph_id=graph_id,
            operation_type=operation_type,
            operation_config=operation_config or {},
            neo4j_connection_id=neo4j_connection_id,
            cypher_query=cypher_query,
            query_parameters=query_parameters,
            batch_size=batch_size,
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            priority=priority
        )
        
        success = await self.event_bus.publish(event)
        if success:
            self._record_event(event)
            logger.info(f"Neo4j operation event published for {graph_id}: {operation_type}")
            return event.event_id
        else:
            raise RuntimeError("Failed to publish Neo4j operation event")
    
    async def publish_ai_insights(
        self,
        graph_id: str,
        ai_operation_type: str,
        ai_model_version: Optional[str] = None,
        confidence_score: Optional[float] = None,
        analysis_data: Optional[Dict[str, Any]] = None,
        insights_count: Optional[int] = None,
        processing_duration_ms: Optional[float] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        dept_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL
    ) -> str:
        """Publish an AI insights event."""
        event = AIInsightsEvent(
            event_id=str(uuid.uuid4()),
            graph_id=graph_id,
            ai_operation_type=ai_operation_type,
            ai_model_version=ai_model_version,
            confidence_score=confidence_score,
            analysis_data=analysis_data or {},
            insights_count=insights_count,
            processing_duration_ms=processing_duration_ms,
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            priority=priority
        )
        
        success = await self.event_bus.publish(event)
        if success:
            self._record_event(event)
            logger.info(f"AI insights event published for {graph_id}: {ai_operation_type}")
            return event.event_id
        else:
            raise RuntimeError("Failed to publish AI insights event")
    
    async def publish_health_monitoring(
        self,
        graph_id: str,
        health_metric_type: str,
        current_value: float,
        threshold_value: float,
        severity: str = "warning",
        alert_message: str = "",
        recommended_action: Optional[str] = None,
        historical_trend: Optional[List[float]] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        dept_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL
    ) -> str:
        """Publish a health monitoring event."""
        event = HealthMonitoringEvent(
            event_id=str(uuid.uuid4()),
            graph_id=graph_id,
            health_metric_type=health_metric_type,
            current_value=current_value,
            threshold_value=threshold_value,
            severity=severity,
            alert_message=alert_message,
            recommended_action=recommended_action,
            historical_trend=historical_trend,
            user_id=user_id,
            org_id=org_id,
            dept_id=dept_id,
            priority=priority
        )
        
        success = await self.event_bus.publish(event)
        if success:
            self._record_event(event)
            logger.info(f"Health monitoring event published for {graph_id}: {health_metric_type}")
            return event.event_id
        else:
            raise RuntimeError("Failed to publish health monitoring event")
    
    # Event management methods
    
    def _record_event(self, event: KGNeo4jEvent) -> None:
        """Record an event in the history."""
        event_record = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "priority": event.priority.name,
            "status": event.status.value,
            "source": event.source
        }
        
        self.event_history.append(event_record)
        
        # Maintain history size limit
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
    
    async def get_event_status(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific event."""
        # Search in event history
        for event_record in self.event_history:
            if event_record["event_id"] == event_id:
                return event_record
        
        return None
    
    async def get_recent_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent events with optional filtering."""
        events = self.event_history[-limit:] if limit > 0 else self.event_history
        
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        return events
    
    # Statistics and monitoring methods
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get event manager statistics."""
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        return {
            "is_initialized": self.is_initialized,
            "uptime_seconds": uptime,
            "total_events_processed": self.total_events_processed,
            "total_events_failed": self.total_events_failed,
            "event_history_size": len(self.event_history),
            "active_handlers": len(self.handlers),
            "start_time": self.start_time.isoformat()
        }
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get statistics for all handlers."""
        return {
            handler_type: handler.get_stats()
            for handler_type, handler in self.handlers.items()
        }
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics including event bus stats."""
        return {
            "event_manager": self.get_manager_stats(),
            "event_bus": self.event_bus.get_stats(),
            "handlers": self.get_handler_stats()
        }
    
    # Health check methods
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check."""
        try:
            # Check event bus health
            event_bus_stats = self.event_bus.get_stats()
            event_bus_healthy = event_bus_stats["is_running"]
            
            # Check handler health
            handler_stats = self.get_handler_stats()
            handlers_healthy = all(
                handler["success_rate"] > 0.8 
                for handler in handler_stats.values()
            )
            
            # Overall health
            overall_healthy = event_bus_healthy and handlers_healthy
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "components": {
                    "event_bus": {
                        "status": "healthy" if event_bus_healthy else "unhealthy",
                        "is_running": event_bus_healthy
                    },
                    "handlers": {
                        "status": "healthy" if handlers_healthy else "unhealthy",
                        "count": len(handler_stats)
                    }
                },
                "overall_health": overall_healthy
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    # Utility methods
    
    async def wait_for_empty_queues(self, timeout: float = 30.0) -> bool:
        """Wait for all event queues to be empty."""
        return await self.event_bus.wait_for_empty_queues(timeout)
    
    def clear_event_history(self) -> None:
        """Clear the event history."""
        self.event_history.clear()
        logger.info("Event history cleared")
    
    async def restart_event_bus(self) -> None:
        """Restart the event bus."""
        try:
            await self.event_bus.stop()
            await asyncio.sleep(1)  # Brief pause
            await self.event_bus.start()
            logger.info("Event bus restarted successfully")
        except Exception as e:
            logger.error(f"Failed to restart event bus: {e}")
            raise
