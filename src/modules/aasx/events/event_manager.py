"""
Event Management System

Event management for AASX processing operations.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable, Coroutine
from datetime import datetime, timedelta
from enum import Enum
import json
import weakref
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for AASX processing."""
    
    # File upload events
    FILE_UPLOADED = "file_uploaded"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    
    # Batch processing events
    BATCH_DETECTED = "batch_detected"
    BATCH_PROCESSING_STARTED = "batch_processing_started"
    BATCH_PROCESSING_COMPLETED = "batch_processing_completed"
    BATCH_PROCESSING_FAILED = "batch_processing_failed"
    
    # Individual processing events
    PROCESSING_STARTED = "processing_started"
    PROCESSING_COMPLETED = "processing_completed"
    PROCESSING_FAILED = "processing_failed"
    
    # ETL specific events
    ETL_STARTED = "etl_started"
    ETL_COMPLETED = "etl_completed"
    ETL_FAILED = "etl_failed"
    
    # Validation events
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    VALIDATION_FAILED = "validation_failed"
    
    # Database population events
    DATABASE_POPULATION_STARTED = "database_population_started"
    DATABASE_POPULATION_COMPLETED = "database_population_completed"
    DATABASE_POPULATION_FAILED = "database_population_failed"


class EventPriority(str, Enum):
    """Event priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Event(BaseModel):
    """Event representation."""
    
    event_type: EventType
    data: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[str] = None
    correlation_id: Optional[str] = None


class EventHandler(ABC):
    """Base class for event handlers."""
    
    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        """Handle an event."""
        pass


class LoggingEventHandler(EventHandler):
    """Event handler that logs events."""
    
    def __init__(self, name: str = "logging_handler", 
                 event_types: Optional[List[EventType]] = None,
                 log_level: str = "INFO"):
        """
        Initialize logging event handler.
        
        Args:
            name: Handler name
            event_types: Event types to handle
            log_level: Log level for events
        """
        self.name = name
        self.event_types = event_types
        self.handled_events = 0
        self.last_event_time = None
        self.log_level = log_level.upper()
        self.logger = logging.getLogger(f"aasx.events.{name}")
    
    async def handle_event(self, event: Event) -> None:
        """Process event by logging it."""
        try:
            if self.log_level == "DEBUG":
                self.logger.debug(f"Event: {event}")
            elif self.log_level == "INFO":
                self.logger.info(f"Event: {event}")
            elif self.log_level == "WARNING":
                self.logger.warning(f"Event: {event}")
            elif self.log_level == "ERROR":
                self.logger.error(f"Event: {event}")
            
            return
        except Exception as e:
            self.logger.error(f"Failed to log event: {str(e)}")
            return


class WebhookEventHandler(EventHandler):
    """Event handler that sends webhooks."""
    
    def __init__(self, name: str = "webhook_handler",
                 webhook_urls: Optional[List[str]] = None,
                 event_types: Optional[List[EventType]] = None):
        """
        Initialize webhook event handler.
        
        Args:
            name: Handler name
            webhook_urls: List of webhook URLs
            event_types: Event types to handle
        """
        self.name = name
        self.webhook_urls = webhook_urls or []
        self.event_types = event_types
    
    async def handle_event(self, event: Event) -> None:
        """Process event by sending webhook."""
        if not self.webhook_urls:
            return
        
        # Import here to avoid circular imports
        from ..integration.api_client import create_webhook_client
        from ..config.settings import get_environment_config
        
        try:
            config = get_environment_config().integration
            webhook_client = create_webhook_client(config)
            
            # Send webhook for each URL
            for url in self.webhook_urls:
                webhook_client.add_webhook_endpoint(url)
            
            result = await webhook_client.send_webhook(
                event.event_type.value,
                event.data
            )
            
            return
            
        except Exception as e:
            logger.error(f"Failed to send webhook for event {event.event_id}: {str(e)}")
            return


class DatabasePopulationEventHandler(EventHandler):
    """Handler that automatically populates database tables."""
    
    def __init__(self, processing_service, metrics_service):
        self.processing_service = processing_service
        self.metrics_service = metrics_service
    
    async def handle_event(self, event: Event) -> None:
        if event.event_type == EventType.FILE_UPLOADED:
            await self._handle_file_uploaded(event)
        elif event.event_type == EventType.ETL_COMPLETED:
            await self._handle_etl_completed(event)
        elif event.event_type == EventType.BATCH_DETECTED:
            await self._handle_batch_detected(event)
    
    async def _handle_file_uploaded(self, event: Event) -> None:
        """Automatically create processing job when file is uploaded."""
        try:
            file_id = event.data.get("file_id")
            file_path = event.data.get("file_path")
            project_id = event.data.get("project_id", "default_project")
            processed_by = event.data.get("processed_by", "system")
            org_id = event.data.get("org_id", "default_org")
            dept_id = event.data.get("dept_id")
            
            if file_id and file_path:
                # Create processing job automatically
                job_id = await self.processing_service.create_job_from_file_upload(
                    file_id, file_path, 
                    project_id=project_id,
                    processed_by=processed_by,
                    org_id=org_id,
                    dept_id=dept_id
                )
                logger.info(f"Auto-created processing job {job_id} for file {file_id}")
        except Exception as e:
            logger.error(f"Failed to create auto-processing job: {e}")
    
    async def _handle_etl_completed(self, event: Event) -> None:
        """Create metrics record when ETL completes."""
        try:
            job_id = event.data.get("job_id")
            metrics_data = event.data.get("metrics", {})
            
            if job_id and metrics_data:
                # Create metrics record automatically
                metric_id = await self.metrics_service.create_metrics_record(
                    job_id, metrics_data
                )
                logger.info(f"Auto-created metrics record {metric_id} for job {job_id}")
        except Exception as e:
            logger.error(f"Failed to create auto-metrics record: {e}")
    
    async def _handle_batch_detected(self, event: Event) -> None:
        """Handle batch processing detection."""
        try:
            files = event.data.get("files", [])
            project_id = event.data.get("project_id", "default_project")
            processed_by = event.data.get("processed_by", "system")
            org_id = event.data.get("org_id", "default_org")
            dept_id = event.data.get("dept_id")
            
            if files:
                # Create batch processing job
                batch_job_id = await self.processing_service.create_batch_job(
                    files,
                    project_id=project_id,
                    processed_by=processed_by,
                    org_id=org_id,
                    dept_id=dept_id
                )
                logger.info(f"Auto-created batch job {batch_job_id} for {len(files)} files")
        except Exception as e:
            logger.error(f"Failed to create batch job: {e}")


class EventManager:
    """Enhanced event manager for AASX processing with hybrid architecture support."""
    
    def __init__(self):
        """Initialize event manager."""
        self._handlers: List[EventHandler] = []
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._batch_detector = BatchDetector()
        self._processing_controller = ProcessingController()
        self._running = False
        self._stats = {
            "events_processed": 0,
            "events_failed": 0,
            "batch_jobs_created": 0,
            "single_jobs_created": 0
        }
    
    async def start(self):
        """Start the event manager."""
        if not self._running:
            self._running = True
            asyncio.create_task(self._process_events())
            logger.info("Event manager started")
    
    async def stop(self):
        """Stop the event manager."""
        self._running = False
        logger.info("Event manager stopped")
    
    def add_handler(self, handler: EventHandler):
        """Add an event handler."""
        self._handlers.append(handler)
    
    def remove_handler(self, handler: EventHandler):
        """Remove an event handler."""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    async def emit_event(self, event: Event):
        """Emit an event."""
        await self._event_queue.put(event)
        
        # Check for batch detection
        if event.event_type == EventType.FILE_UPLOADED:
            batch_event = await self._batch_detector.check_for_batch(event)
            if batch_event:
                await self._event_queue.put(batch_event)
    
    async def _process_events(self):
        """Process events from the queue."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                
                # Route event based on type
                if event.event_type in [EventType.FILE_UPLOADED, EventType.BATCH_DETECTED]:
                    await self._route_processing_event(event)
                
                # Handle event with all handlers
                for handler in self._handlers:
                    try:
                        await handler.handle_event(event)
                    except Exception as e:
                        logger.error(f"Handler {handler.__class__.__name__} failed: {e}")
                        self._stats["events_failed"] += 1
                
                self._stats["events_processed"] += 1
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")
                self._stats["events_failed"] += 1
    
    async def _route_processing_event(self, event: Event):
        """Route processing events to appropriate handlers."""
        if event.event_type == EventType.FILE_UPLOADED:
            # Single file - process immediately
            await self._processing_controller.process_single_file(event)
            self._stats["single_jobs_created"] += 1
            
        elif event.event_type == EventType.BATCH_DETECTED:
            # Batch detected - create batch job
            await self._processing_controller.process_batch(event)
            self._stats["batch_jobs_created"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event manager statistics."""
        return self._stats.copy()


class BatchDetector:
    """Detects when multiple file uploads should be processed as a batch."""
    
    def __init__(self, batch_window_seconds: int = 30, min_batch_size: int = 3):
        self.batch_window = batch_window_seconds
        self.min_batch_size = min_batch_size
        self._recent_uploads: List[Dict[str, Any]] = []
        self._last_batch_time = datetime.utcnow()
    
    async def check_for_batch(self, upload_event: Event) -> Optional[Event]:
        """Check if recent uploads should trigger batch processing."""
        current_time = datetime.utcnow()
        
        # Add current upload to recent list
        self._recent_uploads.append({
            "file_id": upload_event.data.get("file_id"),
            "file_path": upload_event.data.get("file_path"),
            "timestamp": current_time
        })
        
        # Clean old uploads outside batch window
        cutoff_time = current_time - timedelta(seconds=self.batch_window)
        self._recent_uploads = [
            upload for upload in self._recent_uploads 
            if upload["timestamp"] > cutoff_time
        ]
        
        # Check if we should create a batch
        if (len(self._recent_uploads) >= self.min_batch_size and 
            (current_time - self._last_batch_time).seconds > self.batch_window):
            
            self._last_batch_time = current_time
            
            # Create batch event
            batch_event = Event(
                event_type=EventType.BATCH_DETECTED,
                data={
                    "files": [upload["file_id"] for upload in self._recent_uploads],
                    "file_paths": [upload["file_path"] for upload in self._recent_uploads],
                    "batch_size": len(self._recent_uploads),
                    "detection_time": current_time.isoformat()
                },
                priority=EventPriority.HIGH
            )
            
            # Clear recent uploads after creating batch
            self._recent_uploads = []
            
            return batch_event
        
        return None


class ProcessingController:
    """Controls processing concurrency and job creation."""
    
    def __init__(self, max_concurrent_jobs: int = 5):
        self.max_concurrent = max_concurrent_jobs
        self.active_jobs = 0
        self.job_queue = asyncio.Queue()
    
    async def process_single_file(self, event: Event):
        """Process a single file upload event."""
        # For now, just log - actual processing will be handled by services
        logger.info(f"Single file processing triggered for {event.data.get('file_id')}")
    
    async def process_batch(self, event: Event):
        """Process a batch detection event."""
        # For now, just log - actual batch processing will be handled by services
        logger.info(f"Batch processing triggered for {event.data.get('batch_size')} files")


# Global event manager instance
_event_manager: Optional[EventManager] = None


def get_event_manager() -> EventManager:
    """Get the global event manager instance."""
    global _event_manager
    if _event_manager is None:
        _event_manager = EventManager()
    return _event_manager


async def start_event_manager():
    """Start the global event manager."""
    manager = get_event_manager()
    await manager.start()


async def stop_event_manager():
    """Stop the global event manager."""
    manager = get_event_manager()
    await manager.stop()


# Convenience functions for emitting events
async def emit_file_uploaded(file_id: str, file_path: str, 
                            project_id: str = "default_project",
                            processed_by: str = "system",
                            org_id: str = "default_org",
                            dept_id: Optional[str] = None,
                            source: str = "file_system"):
    """Emit file uploaded event with complete traceability parameters."""
    event = Event(
        event_type=EventType.FILE_UPLOADED,
        data={
            "file_id": file_id,
            "file_path": file_path,
            "project_id": project_id,
            "processed_by": processed_by,
            "org_id": org_id,
            "dept_id": dept_id,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        },
        priority=EventPriority.HIGH
    )
    await get_event_manager().emit_event(event)

async def emit_etl_started(job_id: str, file_id: str):
    """Emit ETL started event."""
    event = Event(
        event_type=EventType.ETL_STARTED,
        data={"job_id": job_id, "file_id": file_id},
        priority=EventPriority.NORMAL
    )
    await get_event_manager().emit_event(event)

async def emit_etl_completed(job_id: str, file_id: str, results: Dict[str, Any],
                            dept_id: Optional[str] = None):
    """Emit ETL completed event with complete traceability parameters."""
    event = Event(
        event_type=EventType.ETL_COMPLETED,
        data={
            "job_id": job_id,
            "file_id": file_id,
            "results": results,
            "dept_id": dept_id,
            "completion_time": datetime.utcnow().isoformat()
        },
        priority=EventPriority.HIGH
    )
    await get_event_manager().emit_event(event)

async def emit_etl_failed(job_id: str, file_id: str, error: str):
    """Emit ETL failed event."""
    event = Event(
        event_type=EventType.ETL_FAILED,
        data={
            "job_id": job_id, 
            "file_id": file_id, 
            "error": error,
            "failure_time": datetime.utcnow().isoformat()
        },
        priority=EventPriority.HIGH
    )
    await get_event_manager().emit_event(event)

async def emit_batch_detected(files: List[str], file_paths: List[str],
                             project_id: str = "default_project",
                             processed_by: str = "system",
                             org_id: str = "default_org",
                             dept_id: Optional[str] = None):
    """Emit batch detected event with complete traceability parameters."""
    event = Event(
        event_type=EventType.BATCH_DETECTED,
        data={
            "files": files,
            "file_paths": file_paths,
            "project_id": project_id,
            "processed_by": processed_by,
            "org_id": org_id,
            "dept_id": dept_id,
            "batch_size": len(files),
            "timestamp": datetime.utcnow().isoformat()
        },
        priority=EventPriority.HIGH
    )
    await get_event_manager().emit_event(event)
