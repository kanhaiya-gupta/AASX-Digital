"""
Real-time Utilities

This module provides comprehensive real-time utilities for real-time event processing,
real-time data handling, and real-time operations.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any, Tuple, Callable, Coroutine
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class RealTimeEvent(Enum):
    """Real-time event types"""
    DATA_UPDATE = "data_update"
    STATUS_CHANGE = "status_change"
    ALERT = "alert"
    NOTIFICATION = "notification"
    METRIC_UPDATE = "metric_update"
    PERFORMANCE_UPDATE = "performance_update"
    QUALITY_UPDATE = "quality_update"
    COMPLIANCE_UPDATE = "compliance_update"
    SECURITY_UPDATE = "security_update"
    WORKFLOW_UPDATE = "workflow_update"


class RealTimeProcessor(Enum):
    """Real-time processor types"""
    STREAM = "stream"
    BATCH = "batch"
    EVENT_DRIVEN = "event_driven"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    REQUEST_RESPONSE = "request_response"
    ASYNC_QUEUE = "async_queue"
    WEBSOCKET = "websocket"
    SERVER_SENT_EVENTS = "server_sent_events"
    MESSAGE_QUEUE = "message_queue"
    REAL_TIME_DATABASE = "real_time_database"


@dataclass
class RealTimeConfig:
    """Configuration for real-time operations"""
    processor_type: RealTimeProcessor = RealTimeProcessor.STREAM
    batch_size: int = 100
    timeout: int = 30
    retry_count: int = 3
    buffer_size: int = 1000
    flush_interval: float = 1.0
    enable_compression: bool = True
    enable_encryption: bool = False
    enable_monitoring: bool = True


class RealTimeUtils:
    """
    Real-time utilities and processing service
    
    Handles:
    - Real-time event processing and routing
    - Real-time data streaming and batching
    - Real-time notifications and alerts
    - Real-time performance monitoring
    - Real-time workflow coordination
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the real-time utilities service"""
        self.real_time_events = list(RealTimeEvent)
        self.real_time_processors = list(RealTimeProcessor)
        
        # Real-time storage and metadata
        self.real_time_events_data: Dict[str, Dict[str, Any]] = {}
        self.real_time_processors_config: Dict[str, Dict[str, Any]] = {}
        self.real_time_history: List[Dict[str, Any]] = []
        
        # Real-time locks and queues
        self.real_time_locks: Dict[str, asyncio.Lock] = {}
        self.real_time_queue: asyncio.Queue = asyncio.Queue()
        self.event_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.real_time_stats = {
            "total_events_processed": 0,
            "successful": 0,
            "failed": 0,
            "average_processing_time": 0.0,
            "total_data_processed": 0,
            "active_connections": 0
        }
        
        # Real-time processors
        self.active_processors: Dict[str, asyncio.Task] = {}
        self.processor_configs: Dict[str, RealTimeConfig] = {}
        
        # Initialize default real-time processors
        self._initialize_default_processors()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Real-time utilities service initialized successfully")
    
    async def process_real_time_event(
        self,
        event_type: RealTimeEvent,
        event_data: Dict[str, Any],
        processor_type: RealTimeProcessor = RealTimeProcessor.STREAM,
        config: Optional[RealTimeConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a real-time event with the specified processor
        
        Args:
            event_type: Type of real-time event to process
            event_data: Event data to process
            processor_type: Type of processor to use
            config: Real-time configuration
            metadata: Additional metadata for the event processing
            
        Returns:
            Dictionary containing event processing results and metadata
        """
        start_time = time.time()
        event_processing_id = f"event_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_event_processing_params(event_type, event_data, processor_type)
            
            # Get processor configuration
            processor_config = config or self._get_default_processor_config(processor_type)
            
            # Prepare data for event processing
            prepared_data = await self._prepare_data_for_event_processing(event_data, event_type)
            
            # Process real-time event
            processing_result = await self._process_real_time_event(
                prepared_data, event_type, processor_config, metadata
            )
            
            # Create metadata
            event_metadata = await self._create_event_processing_metadata(
                event_processing_id, event_type, event_data, processor_type, processor_config, metadata
            )
            
            # Store event processing results
            event_processing_info = {
                "id": event_processing_id,
                "event_type": event_type.value,
                "event_data": prepared_data,
                "processor_type": processor_type.value,
                "processor_config": processor_config.__dict__,
                "result": processing_result,
                "metadata": event_metadata,
                "processed_at": time.time(),
                "processing_time": time.time() - start_time,
                "status": "success"
            }
            
            self.real_time_events_data[event_processing_id] = event_processing_info
            self.real_time_history.append(event_processing_info)
            
            # Update statistics
            await self._update_real_time_stats(True, time.time() - start_time, len(str(prepared_data)))
            
            logger.info(f"Real-time event processed successfully: {event_processing_id}")
            return event_processing_info
            
        except Exception as e:
            await self._update_real_time_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to process real-time event: {str(e)}")
            raise
    
    async def process_real_time_events_batch(
        self,
        events_data: List[Tuple[RealTimeEvent, Dict[str, Any]]],
        processor_type: RealTimeProcessor = RealTimeProcessor.BATCH,
        config: Optional[RealTimeConfig] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple real-time events in batch
        
        Args:
            events_data: List of tuples containing event types and event data
            processor_type: Type of processor to use
            config: Real-time configuration
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of event processing results
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch real-time event processing: {batch_id}")
        
        # Create tasks for concurrent event processing
        tasks = []
        for i, (event_type, event_data) in enumerate(events_data):
            task = asyncio.create_task(
                self.process_real_time_event(event_type, event_data, processor_type, config, {
                    "batch_id": batch_id,
                    "batch_index": i,
                    **(batch_metadata or {})
                })
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process real-time event {i} in batch {batch_id}: {str(result)}")
                results.append({
                    "id": f"failed_{batch_id}_{i}",
                    "status": "failed",
                    "error": str(result),
                    "batch_id": batch_id,
                    "batch_index": i
                })
            else:
                results.append(result)
        
        logger.info(f"Batch real-time event processing completed: {batch_id}, {len(results)} results")
        return results
    
    async def start_real_time_stream(
        self,
        stream_name: str,
        processor_type: RealTimeProcessor = RealTimeProcessor.STREAM,
        config: Optional[RealTimeConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a real-time data stream
        
        Args:
            stream_name: Name of the stream to start
            processor_type: Type of processor to use
            config: Real-time configuration
            metadata: Additional metadata for the stream
            
        Returns:
            Stream start result
        """
        if stream_name in self.active_processors:
            raise ValueError(f"Stream already active: {stream_name}")
        
        try:
            # Get processor configuration
            processor_config = config or self._get_default_processor_config(processor_type)
            
            # Create stream processor task
            stream_task = asyncio.create_task(
                self._run_real_time_stream(stream_name, processor_config, metadata)
            )
            
            # Store active processor
            self.active_processors[stream_name] = stream_task
            self.processor_configs[stream_name] = processor_config
            
            # Create metadata
            stream_metadata = await self._create_stream_metadata(
                stream_name, processor_type, processor_config, metadata
            )
            
            stream_info = {
                "stream_name": stream_name,
                "processor_type": processor_type.value,
                "processor_config": processor_config.__dict__,
                "metadata": stream_metadata,
                "started_at": time.time(),
                "status": "active"
            }
            
            self.real_time_history.append(stream_info)
            
            logger.info(f"Real-time stream started successfully: {stream_name}")
            return stream_info
            
        except Exception as e:
            logger.error(f"Failed to start real-time stream: {str(e)}")
            raise
    
    async def stop_real_time_stream(self, stream_name: str) -> Dict[str, Any]:
        """
        Stop a real-time data stream
        
        Args:
            stream_name: Name of the stream to stop
            
        Returns:
            Stream stop result
        """
        if stream_name not in self.active_processors:
            raise ValueError(f"Stream not found: {stream_name}")
        
        try:
            # Cancel stream processor task
            stream_task = self.active_processors[stream_name]
            stream_task.cancel()
            
            # Wait for task to complete
            try:
                await stream_task
            except asyncio.CancelledError:
                pass
            
            # Remove from active processors
            del self.active_processors[stream_name]
            del self.processor_configs[stream_name]
            
            stream_info = {
                "stream_name": stream_name,
                "stopped_at": time.time(),
                "status": "stopped"
            }
            
            self.real_time_history.append(stream_info)
            
            logger.info(f"Real-time stream stopped successfully: {stream_name}")
            return stream_info
            
        except Exception as e:
            logger.error(f"Failed to stop real-time stream: {str(e)}")
            raise
    
    async def get_real_time_stream_info(self, stream_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a real-time stream
        
        Args:
            stream_name: Name of the stream
            
        Returns:
            Stream information
        """
        if stream_name not in self.active_processors:
            raise ValueError(f"Stream not found: {stream_name}")
        
        stream_task = self.active_processors[stream_name]
        processor_config = self.processor_configs[stream_name]
        
        return {
            "stream_name": stream_name,
            "processor_type": processor_config.processor_type.value,
            "processor_config": processor_config.__dict__,
            "task_status": stream_task.done(),
            "started_at": time.time() - stream_task.get_loop().time(),
            "status": "active"
        }
    
    async def list_active_streams(self) -> List[Dict[str, Any]]:
        """
        List all active real-time streams
        
        Returns:
            List of active streams
        """
        streams = []
        
        for stream_name in self.active_processors:
            stream_info = await self.get_real_time_stream_info(stream_name)
            streams.append(stream_info)
        
        return streams
    
    async def send_real_time_notification(
        self,
        notification_type: str,
        message: str,
        recipients: List[str],
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a real-time notification
        
        Args:
            notification_type: Type of notification
            message: Notification message
            recipients: List of recipients
            priority: Notification priority
            metadata: Additional metadata for the notification
            
        Returns:
            Notification result
        """
        notification_id = f"notification_{int(time.time() * 1000)}"
        
        try:
            # Create notification data
            notification_data = {
                "id": notification_id,
                "type": notification_type,
                "message": message,
                "recipients": recipients,
                "priority": priority,
                "timestamp": time.time(),
                "metadata": metadata or {}
            }
            
            # Add to event queue for processing
            await self.event_queue.put(notification_data)
            
            # Create metadata
            notification_metadata = await self._create_notification_metadata(
                notification_id, notification_type, message, recipients, priority, metadata
            )
            
            notification_info = {
                "id": notification_id,
                "type": notification_type,
                "message": message,
                "recipients": recipients,
                "priority": priority,
                "metadata": notification_metadata,
                "sent_at": time.time(),
                "status": "sent"
            }
            
            self.real_time_history.append(notification_info)
            
            logger.info(f"Real-time notification sent successfully: {notification_id}")
            return notification_info
            
        except Exception as e:
            logger.error(f"Failed to send real-time notification: {str(e)}")
            raise
    
    async def get_real_time_info(self, processing_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a real-time operation
        
        Args:
            processing_id: ID of the real-time operation
            
        Returns:
            Real-time operation information
        """
        for operation_info in self.real_time_history:
            if operation_info.get("id") == processing_id:
                return operation_info
        
        raise ValueError(f"Real-time operation not found: {processing_id}")
    
    async def get_real_time_history(
        self,
        event_type: Optional[RealTimeEvent] = None,
        processor_type: Optional[RealTimeProcessor] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get real-time operation history
        
        Args:
            event_type: Filter by event type
            processor_type: Filter by processor type
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of real-time operation history entries
        """
        history = self.real_time_history
        
        if event_type:
            history = [h for h in history if h.get("event_type") == event_type.value]
        
        if processor_type:
            history = [h for h in history if h.get("processor_type") == processor_type.value]
        
        # Sort by processing time (newest first)
        history.sort(key=lambda x: x.get("processed_at", x.get("started_at", x.get("sent_at", 0))), reverse=True)
        
        return history[offset:offset + limit]
    
    async def get_real_time_statistics(self) -> Dict[str, Any]:
        """
        Get real-time operation statistics
        
        Returns:
            Real-time operation statistics
        """
        stats = self.real_time_stats.copy()
        stats["active_streams"] = len(self.active_processors)
        stats["queue_size"] = self.real_time_queue.qsize()
        stats["event_queue_size"] = self.event_queue.qsize()
        return stats
    
    async def cleanup_expired_real_time_data(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired real-time data
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of operations cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_operations = []
        for operation_info in self.real_time_history:
            operation_time = operation_info.get("processed_at", operation_info.get("started_at", operation_info.get("sent_at", 0)))
            if current_time - operation_time > max_age_seconds:
                expired_operations.append(operation_info.get("id"))
        
        # Remove expired operations
        self.real_time_history = [
            op for op in self.real_time_history
            if op.get("id") not in expired_operations
        ]
        
        logger.info(f"Cleaned up {len(expired_operations)} expired real-time operations")
        return len(expired_operations)
    
    # Private helper methods
    
    def _initialize_default_processors(self):
        """Initialize default real-time processors"""
        # Stream processor
        self.processor_configs["default_stream"] = RealTimeConfig(
            processor_type=RealTimeProcessor.STREAM,
            batch_size=100,
            timeout=30,
            retry_count=3,
            buffer_size=1000,
            flush_interval=1.0,
            enable_compression=True,
            enable_encryption=False,
            enable_monitoring=True
        )
        
        # Batch processor
        self.processor_configs["default_batch"] = RealTimeConfig(
            processor_type=RealTimeProcessor.BATCH,
            batch_size=500,
            timeout=60,
            retry_count=2,
            buffer_size=5000,
            flush_interval=5.0,
            enable_compression=True,
            enable_encryption=False,
            enable_monitoring=True
        )
        
        # Event-driven processor
        self.processor_configs["default_event_driven"] = RealTimeConfig(
            processor_type=RealTimeProcessor.EVENT_DRIVEN,
            batch_size=50,
            timeout=15,
            retry_count=5,
            buffer_size=500,
            flush_interval=0.5,
            enable_compression=False,
            enable_encryption=False,
            enable_monitoring=True
        )
    
    def _start_background_tasks(self):
        """Start background tasks for real-time processing"""
        # Start event processor
        asyncio.create_task(self._event_processor_worker())
        
        # Start real-time queue processor
        asyncio.create_task(self._real_time_queue_worker())
        
        # Start monitoring task
        asyncio.create_task(self._monitoring_worker())
    
    async def _validate_event_processing_params(
        self,
        event_type: RealTimeEvent,
        event_data: Dict[str, Any],
        processor_type: RealTimeProcessor
    ):
        """Validate event processing parameters"""
        if not isinstance(event_type, RealTimeEvent):
            raise ValueError("Invalid event type")
        
        if not event_data:
            raise ValueError("Event data cannot be empty")
        
        if not isinstance(event_data, dict):
            raise ValueError("Event data must be a dictionary")
        
        if not isinstance(processor_type, RealTimeProcessor):
            raise ValueError("Invalid processor type")
    
    def _get_default_processor_config(self, processor_type: RealTimeProcessor) -> RealTimeConfig:
        """Get default processor configuration"""
        config_key = f"default_{processor_type.value}"
        if config_key in self.processor_configs:
            return self.processor_configs[config_key]
        
        # Return default stream config if specific config not found
        return self.processor_configs["default_stream"]
    
    async def _prepare_data_for_event_processing(
        self,
        event_data: Dict[str, Any],
        event_type: RealTimeEvent
    ) -> Dict[str, Any]:
        """Prepare data for event processing"""
        # Add event context to data
        prepared_data = event_data.copy()
        prepared_data["_event_context"] = {
            "event_type": event_type.value,
            "timestamp": time.time(),
            "processing_id": f"ctx_{int(time.time() * 1000)}"
        }
        return prepared_data
    
    async def _process_real_time_event(
        self,
        data: Dict[str, Any],
        event_type: RealTimeEvent,
        processor_config: RealTimeConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process a real-time event"""
        try:
            processor_type = processor_config.processor_type
            
            if processor_type == RealTimeProcessor.STREAM:
                return await self._process_stream_event(data, event_type, processor_config, metadata)
            elif processor_type == RealTimeProcessor.BATCH:
                return await self._process_batch_event(data, event_type, processor_config, metadata)
            elif processor_type == RealTimeProcessor.EVENT_DRIVEN:
                return await self._process_event_driven_event(data, event_type, processor_config, metadata)
            else:
                return await self._process_generic_event(data, event_type, processor_config, metadata)
        
        except Exception as e:
            logger.error(f"Error processing real-time event: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "event_type": event_type.value
            }
    
    async def _process_stream_event(
        self,
        data: Dict[str, Any],
        event_type: RealTimeEvent,
        processor_config: RealTimeConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process a stream event"""
        try:
            # Simulate stream processing
            stream_result = {
                "success": True,
                "processor_type": "stream",
                "event_type": event_type.value,
                "processing_timestamp": time.time(),
                "stream_id": f"stream_{int(time.time() * 1000)}"
            }
            
            return stream_result
        
        except Exception as e:
            return {
                "success": False,
                "processor_type": "stream",
                "error": str(e)
            }
    
    async def _process_batch_event(
        self,
        data: Dict[str, Any],
        event_type: RealTimeEvent,
        processor_config: RealTimeConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process a batch event"""
        try:
            # Simulate batch processing
            batch_result = {
                "success": True,
                "processor_type": "batch",
                "event_type": event_type.value,
                "batch_size": processor_config.batch_size,
                "processing_timestamp": time.time(),
                "batch_id": f"batch_{int(time.time() * 1000)}"
            }
            
            return batch_result
        
        except Exception as e:
            return {
                "success": False,
                "processor_type": "batch",
                "error": str(e)
            }
    
    async def _process_event_driven_event(
        self,
        data: Dict[str, Any],
        event_type: RealTimeEvent,
        processor_config: RealTimeConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process an event-driven event"""
        try:
            # Simulate event-driven processing
            event_driven_result = {
                "success": True,
                "processor_type": "event_driven",
                "event_type": event_type.value,
                "processing_timestamp": time.time(),
                "event_id": f"event_{int(time.time() * 1000)}"
            }
            
            return event_driven_result
        
        except Exception as e:
            return {
                "success": False,
                "processor_type": "event_driven",
                "error": str(e)
            }
    
    async def _process_generic_event(
        self,
        data: Dict[str, Any],
        event_type: RealTimeEvent,
        processor_config: RealTimeConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process a generic event"""
        try:
            # Simulate generic processing
            generic_result = {
                "success": True,
                "processor_type": "generic",
                "event_type": event_type.value,
                "processing_timestamp": time.time(),
                "generic_id": f"generic_{int(time.time() * 1000)}"
            }
            
            return generic_result
        
        except Exception as e:
            return {
                "success": False,
                "processor_type": "generic",
                "error": str(e)
            }
    
    async def _run_real_time_stream(
        self,
        stream_name: str,
        processor_config: RealTimeConfig,
        metadata: Optional[Dict[str, Any]]
    ):
        """Run a real-time stream processor"""
        try:
            logger.info(f"Starting real-time stream: {stream_name}")
            
            # Simulate stream processing
            while True:
                try:
                    # Process stream data
                    await asyncio.sleep(processor_config.flush_interval)
                    
                    # Check if task is cancelled
                    if asyncio.current_task().cancelled():
                        break
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in stream {stream_name}: {str(e)}")
                    await asyncio.sleep(1)  # Wait before retrying
            
            logger.info(f"Real-time stream stopped: {stream_name}")
        
        except asyncio.CancelledError:
            logger.info(f"Real-time stream cancelled: {stream_name}")
        except Exception as e:
            logger.error(f"Error in real-time stream {stream_name}: {str(e)}")
    
    async def _event_processor_worker(self):
        """Background worker for processing events"""
        try:
            while True:
                try:
                    # Get event from queue
                    event_data = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                    
                    # Process event
                    await self._process_event_notification(event_data)
                    
                    # Mark task as done
                    self.event_queue.task_done()
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in event processor worker: {str(e)}")
                    await asyncio.sleep(1)
        
        except asyncio.CancelledError:
            logger.info("Event processor worker cancelled")
        except Exception as e:
            logger.error(f"Error in event processor worker: {str(e)}")
    
    async def _real_time_queue_worker(self):
        """Background worker for processing real-time queue"""
        try:
            while True:
                try:
                    # Get data from queue
                    data = await asyncio.wait_for(self.real_time_queue.get(), timeout=1.0)
                    
                    # Process data
                    await self._process_real_time_data(data)
                    
                    # Mark task as done
                    self.real_time_queue.task_done()
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in real-time queue worker: {str(e)}")
                    await asyncio.sleep(1)
        
        except asyncio.CancelledError:
            logger.info("Real-time queue worker cancelled")
        except Exception as e:
            logger.error(f"Error in real-time queue worker: {str(e)}")
    
    async def _monitoring_worker(self):
        """Background worker for monitoring real-time operations"""
        try:
            while True:
                try:
                    # Update monitoring statistics
                    await self._update_monitoring_stats()
                    
                    # Wait before next update
                    await asyncio.sleep(10)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring worker: {str(e)}")
                    await asyncio.sleep(10)
        
        except asyncio.CancelledError:
            logger.info("Monitoring worker cancelled")
        except Exception as e:
            logger.error(f"Error in monitoring worker: {str(e)}")
    
    async def _process_event_notification(self, event_data: Dict[str, Any]):
        """Process an event notification"""
        try:
            # Simulate event notification processing
            notification_id = event_data.get("id")
            logger.info(f"Processing event notification: {notification_id}")
            
            # Add to real-time history
            self.real_time_history.append({
                "id": notification_id,
                "type": "event_notification",
                "data": event_data,
                "processed_at": time.time(),
                "status": "processed"
            })
            
        except Exception as e:
            logger.error(f"Error processing event notification: {str(e)}")
    
    async def _process_real_time_data(self, data: Dict[str, Any]):
        """Process real-time data"""
        try:
            # Simulate real-time data processing
            data_id = data.get("id", f"data_{int(time.time() * 1000)}")
            logger.info(f"Processing real-time data: {data_id}")
            
            # Add to real-time history
            self.real_time_history.append({
                "id": data_id,
                "type": "real_time_data",
                "data": data,
                "processed_at": time.time(),
                "status": "processed"
            })
            
        except Exception as e:
            logger.error(f"Error processing real-time data: {str(e)}")
    
    async def _update_monitoring_stats(self):
        """Update monitoring statistics"""
        try:
            # Update active connections count
            self.real_time_stats["active_connections"] = len(self.active_processors)
            
            # Update queue sizes
            self.real_time_stats["queue_size"] = self.real_time_queue.qsize()
            self.real_time_stats["event_queue_size"] = self.event_queue.qsize()
            
        except Exception as e:
            logger.error(f"Error updating monitoring stats: {str(e)}")
    
    async def _create_event_processing_metadata(
        self,
        event_processing_id: str,
        event_type: RealTimeEvent,
        event_data: Dict[str, Any],
        processor_type: RealTimeProcessor,
        processor_config: RealTimeConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for event processing operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "event_type": event_type.value,
            "processor_type": processor_type.value,
            "processor_config_hash": hash(str(processor_config.__dict__)),
            "data_hash": hash(str(event_data)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _create_stream_metadata(
        self,
        stream_name: str,
        processor_type: RealTimeProcessor,
        processor_config: RealTimeConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for stream operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "stream_name": stream_name,
            "processor_type": processor_type.value,
            "processor_config_hash": hash(str(processor_config.__dict__)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _create_notification_metadata(
        self,
        notification_id: str,
        notification_type: str,
        message: str,
        recipients: List[str],
        priority: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for notification operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "notification_type": notification_type,
            "message_hash": hash(message),
            "recipients_count": len(recipients),
            "priority": priority,
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _update_real_time_stats(self, success: bool, processing_time: float, data_size: int):
        """Update real-time statistics"""
        self.real_time_stats["total_events_processed"] += 1
        
        if success:
            self.real_time_stats["successful"] += 1
            self.real_time_stats["total_data_processed"] += data_size
        else:
            self.real_time_stats["failed"] += 1
        
        # Update average processing time
        total_successful = self.real_time_stats["successful"]
        if total_successful > 0:
            current_avg = self.real_time_stats["average_processing_time"]
            self.real_time_stats["average_processing_time"] = (
                (current_avg * (total_successful - 1) + processing_time) / total_successful
            )
