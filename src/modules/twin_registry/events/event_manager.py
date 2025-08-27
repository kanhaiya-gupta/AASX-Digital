"""
Twin Registry Event Manager

Implements event-driven automation for twin registry operations.
Phase 3: Event System & Automation with pure async support.

Handles:
- Automatic twin creation on file upload
- Metrics creation on ETL completion
- Lifecycle event management
- Performance monitoring events
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Coroutine
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from ..models.twin_registry import TwinRegistry, create_twin_registry
from ..models.twin_registry_metrics import TwinRegistryMetrics, create_metrics
from ..core.twin_registry_service import TwinRegistryService

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types for twin registry operations."""
    FILE_UPLOAD = "file_upload"
    ETL_SUCCESS = "etl_success"
    ETL_FAILURE = "etl_failure"
    TWIN_CREATED = "twin_created"
    TWIN_UPDATED = "twin_updated"
    TWIN_DELETED = "twin_deleted"
    METRICS_CREATED = "metrics_created"
    LIFECYCLE_CHANGE = "lifecycle_change"
    PERFORMANCE_ALERT = "performance_alert"
    HEALTH_CHECK = "health_check"


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TwinRegistryEvent:
    """Event data structure for twin registry operations."""
    event_type: EventType
    priority: EventPriority
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    correlation_id: Optional[str] = None


class EventHandler:
    """Base class for event handlers."""
    
    async def handle(self, event: TwinRegistryEvent) -> bool:
        """Handle an event. Return True if successful."""
        raise NotImplementedError


class TwinRegistryEventManager:
    """Main event manager for twin registry operations."""
    
    def __init__(self, twin_service: TwinRegistryService):
        """Initialize the event manager."""
        self.twin_service = twin_service
        self.handlers: Dict[EventType, List[EventHandler]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        self.worker_task: Optional[asyncio.Task] = None
        
        # Register default handlers
        self._register_default_handlers()
        
        logger.info("Twin Registry Event Manager initialized")
    
    def _register_default_handlers(self) -> None:
        """Register default event handlers."""
        # File upload handler - creates twins automatically
        self.register_handler(EventType.FILE_UPLOAD, FileUploadEventHandler(self.twin_service))
        
        # ETL success handler - creates metrics automatically
        self.register_handler(EventType.ETL_SUCCESS, ETLSuccessEventHandler(self.twin_service))
        
        # ETL failure handler - updates twin status
        self.register_handler(EventType.ETL_FAILURE, ETLFailureEventHandler(self.twin_service))
        
        # Lifecycle change handler - tracks twin state changes
        self.register_handler(EventType.LIFECYCLE_CHANGE, LifecycleChangeEventHandler(self.twin_service))
        
        # Performance alert handler - monitors twin health
        self.register_handler(EventType.PERFORMANCE_ALERT, PerformanceAlertEventHandler(self.twin_service))
        
        logger.info("Default event handlers registered")
    
    def register_handler(self, event_type: EventType, handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type.value}")
    
    async def emit_event(self, event: TwinRegistryEvent) -> None:
        """Emit an event to the event queue."""
        await self.event_queue.put(event)
        logger.debug(f"Emitted event: {event.event_type.value}")
    
    async def start(self) -> None:
        """Start the event processing worker."""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_task = asyncio.create_task(self._event_worker())
        logger.info("Twin Registry Event Manager started")
    
    async def stop(self) -> None:
        """Stop the event processing worker."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Twin Registry Event Manager stopped")
    
    async def _event_worker(self) -> None:
        """Main event processing worker."""
        while self.is_running:
            try:
                # Get event from queue with timeout
                try:
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process the event
                await self._process_event(event)
                
                # Mark task as done
                self.event_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in event worker: {e}")
                await asyncio.sleep(1)  # Brief pause on error
    
    async def _process_event(self, event: TwinRegistryEvent) -> None:
        """Process a single event."""
        try:
            handlers = self.handlers.get(event.event_type, [])
            
            if not handlers:
                logger.warning(f"No handlers registered for event type: {event.event_type.value}")
                return
            
            # Execute all handlers for this event type
            tasks = [handler.handle(event) for handler in handlers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            success_count = sum(1 for r in results if r is True)
            logger.info(f"Processed event {event.event_type.value}: {success_count}/{len(handlers)} handlers successful")
            
        except Exception as e:
            logger.error(f"Failed to process event {event.event_type.value}: {e}")


class FileUploadEventHandler(EventHandler):
    """Handles file upload events by automatically creating twins."""
    
    def __init__(self, twin_service: TwinRegistryService):
        self.twin_service = twin_service
    
    async def handle(self, event: TwinRegistryEvent) -> bool:
        """Handle file upload event by creating a new twin."""
        try:
            file_data = event.data
            
            # Extract file information
            file_id = file_data.get('file_id')
            file_name = file_data.get('file_name', 'Unknown')
            file_type = file_data.get('file_type', 'unknown')
            project_id = file_data.get('project_id')
            processed_by = file_data.get('processed_by')
            org_id = file_data.get('org_id')
            dept_id = file_data.get('dept_id')
            
            if not file_id:
                logger.warning("File upload event missing file_id")
                return False
            
            # Determine twin type based on file type
            twin_type = self._determine_twin_type(file_type)
            
            # Create twin ID from file information
            twin_id = f"twin_{file_id}_{twin_type}"
            
            # Create registry name
            registry_name = f"Registry_{file_name}_{twin_type}"
            
            # Create the twin automatically
            twin = await self.twin_service.register_twin(
                twin_id=twin_id,
                registry_name=registry_name,
                registry_type=twin_type,
                workflow_source="file_upload",
                user_id=processed_by or "system",
                org_id=org_id or "system",
                dept_id=dept_id
            )
            
            logger.info(f"Automatically created twin {twin_id} for file {file_id}")
            
            # Emit twin created event
            twin_created_event = TwinRegistryEvent(
                event_type=EventType.TWIN_CREATED,
                priority=EventPriority.NORMAL,
                timestamp=datetime.now(),
                data={
                    'twin_id': twin_id,
                    'file_id': file_id,
                    'registry_id': twin.registry_id,
                    'twin_type': twin_type
                },
                source="file_upload_handler",
                correlation_id=event.correlation_id
            )
            
            # Note: We can't emit events from within handlers to avoid infinite loops
            # The main service should handle this
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle file upload event: {e}")
            return False
    
    def _determine_twin_type(self, file_type: str) -> str:
        """Determine twin type based on file type."""
        file_type_lower = file_type.lower()
        
        if 'aasx' in file_type_lower or 'aas' in file_type_lower:
            return "extraction"
        elif 'json' in file_type_lower or 'xml' in file_type_lower:
            return "generation"
        elif 'hybrid' in file_type_lower or 'combined' in file_type_lower:
            return "hybrid"
        else:
            return "generic"


class ETLSuccessEventHandler(EventHandler):
    """Handles ETL success events by creating performance metrics."""
    
    def __init__(self, twin_service: TwinRegistryService):
        self.twin_service = twin_service
    
    async def handle(self, event: TwinRegistryEvent) -> bool:
        """Handle ETL success event by creating metrics."""
        try:
            etl_data = event.data
            
            # Extract ETL information
            twin_id = etl_data.get('twin_id')
            processing_time = etl_data.get('processing_time', 0.0)
            records_processed = etl_data.get('records_processed', 0)
            success_rate = etl_data.get('success_rate', 1.0)
            
            if not twin_id:
                logger.warning("ETL success event missing twin_id")
                return False
            
            # Get the twin registry entry
            twin = await self.twin_service.get_registry_by_twin_id(twin_id)
            if not twin:
                logger.warning(f"Twin {twin_id} not found for ETL success event")
                return False
            
            # Create performance metrics
            metrics = await create_metrics(
                registry_id=twin.registry_id,
                timestamp=datetime.now(),
                health_score=min(100, int(success_rate * 100)),
                uptime_percentage=100.0,  # ETL success means 100% uptime
                twin_sync_speed_sec=processing_time,
                twin_registry_efficiency=success_rate,
                performance_trends={
                    "etl_success": True,
                    "processing_time": processing_time,
                    "records_processed": records_processed,
                    "success_rate": success_rate
                },
                time_based_analytics={
                    "last_etl": datetime.now().isoformat(),
                    "etl_count": 1
                }
            )
            
            # Save metrics to database
            # Note: This would require a metrics repository
            # For now, we'll log the metrics creation
            
            logger.info(f"Created metrics for twin {twin_id} after ETL success")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle ETL success event: {e}")
            return False


class ETLFailureEventHandler(EventHandler):
    """Handles ETL failure events by updating twin status."""
    
    def __init__(self, twin_service: TwinRegistryService):
        self.twin_service = twin_service
    
    async def handle(self, event: TwinRegistryEvent) -> bool:
        """Handle ETL failure event by updating twin status."""
        try:
            etl_data = event.data
            
            # Extract ETL failure information
            twin_id = etl_data.get('twin_id')
            error_message = etl_data.get('error_message', 'Unknown error')
            failure_reason = etl_data.get('failure_reason', 'etl_failure')
            
            if not twin_id:
                logger.warning("ETL failure event missing twin_id")
                return False
            
            # Get the twin registry entry
            twin = await self.twin_service.get_registry_by_twin_id(twin_id)
            if not twin:
                logger.warning(f"Twin {twin_id} not found for ETL failure event")
                return False
            
            # Update twin health score to reflect failure
            new_health_score = max(0, twin.overall_health_score - 20)  # Reduce health score
            await twin.update_health_score(new_health_score)
            
            # Update integration status
            await twin.update_operational_status("error")
            
            # Save updates
            await self.twin_service.registry_repo.update_registry(twin)
            
            logger.info(f"Updated twin {twin_id} status after ETL failure")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle ETL failure event: {e}")
            return False


class LifecycleChangeEventHandler(EventHandler):
    """Handles lifecycle change events."""
    
    def __init__(self, twin_service: TwinRegistryService):
        self.twin_service = twin_service
    
    async def handle(self, event: TwinRegistryEvent) -> bool:
        """Handle lifecycle change event."""
        try:
            lifecycle_data = event.data
            
            # Extract lifecycle information
            twin_id = lifecycle_data.get('twin_id')
            new_status = lifecycle_data.get('new_status')
            previous_status = lifecycle_data.get('previous_status')
            
            if not twin_id or not new_status:
                logger.warning("Lifecycle change event missing required data")
                return False
            
            logger.info(f"Twin {twin_id} lifecycle changed: {previous_status} -> {new_status}")
            
            # Additional lifecycle processing can be added here
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle lifecycle change event: {e}")
            return False


class PerformanceAlertEventHandler(EventHandler):
    """Handles performance alert events."""
    
    def __init__(self, twin_service: TwinRegistryService):
        self.twin_service = twin_service
    
    async def handle(self, event: TwinRegistryEvent) -> bool:
        """Handle performance alert event."""
        try:
            alert_data = event.data
            
            # Extract alert information
            twin_id = alert_data.get('twin_id')
            alert_type = alert_data.get('alert_type')
            alert_message = alert_data.get('alert_message')
            severity = alert_data.get('severity', 'medium')
            
            if not twin_id or not alert_type:
                logger.warning("Performance alert event missing required data")
                return False
            
            logger.warning(f"Performance alert for twin {twin_id}: {alert_type} - {alert_message}")
            
            # Additional alert processing can be added here
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle performance alert event: {e}")
            return False


# Convenience functions for emitting events
async def emit_file_upload_event(
    event_manager: TwinRegistryEventManager,
    file_id: str,
    file_name: str,
    file_type: str,
    project_id: Optional[str] = None,
    processed_by: Optional[str] = None,
    org_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> None:
    """Emit a file upload event."""
    event = TwinRegistryEvent(
        event_type=EventType.FILE_UPLOAD,
        priority=EventPriority.NORMAL,
        timestamp=datetime.now(),
        data={
            'file_id': file_id,
            'file_name': file_name,
            'file_type': file_type,
            'project_id': project_id,
            'processed_by': processed_by,
            'org_id': org_id,
            'dept_id': dept_id
        },
        source="twin_registry_service",
        correlation_id=correlation_id
    )
    await event_manager.emit_event(event)


async def emit_etl_success_event(
    event_manager: TwinRegistryEventManager,
    twin_id: str,
    processing_time: float,
    records_processed: int,
    success_rate: float = 1.0,
    correlation_id: Optional[str] = None
) -> None:
    """Emit an ETL success event."""
    event = TwinRegistryEvent(
        event_type=EventType.ETL_SUCCESS,
        priority=EventPriority.NORMAL,
        timestamp=datetime.now(),
        data={
            'twin_id': twin_id,
            'processing_time': processing_time,
            'records_processed': records_processed,
            'success_rate': success_rate
        },
        source="twin_registry_service",
        correlation_id=correlation_id
    )
    await event_manager.emit_event(event)


async def emit_etl_failure_event(
    event_manager: TwinRegistryEventManager,
    twin_id: str,
    error_message: str,
    failure_reason: str = "etl_failure",
    correlation_id: Optional[str] = None
) -> None:
    """Emit an ETL failure event."""
    event = TwinRegistryEvent(
        event_type=EventType.ETL_FAILURE,
        priority=EventPriority.HIGH,
        timestamp=datetime.now(),
        data={
            'twin_id': twin_id,
            'error_message': error_message,
            'failure_reason': failure_reason
        },
        source="twin_registry_service",
        correlation_id=correlation_id
    )
    await event_manager.emit_event(event)


