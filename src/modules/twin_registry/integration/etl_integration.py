"""
ETL Integration for Twin Registry Population
Provides hooks and integration points with the ETL pipeline
Phase 3: Event System & Automation with pure async support
"""

import logging
import asyncio
import sqlite3
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

from ..events.event_manager import TwinRegistryEventManager, EventType, EventPriority, TwinRegistryEvent
from ..core.twin_registry_service import TwinRegistryService

logger = logging.getLogger(__name__)


@dataclass
class ETLJobInfo:
    """ETL job information"""
    job_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    input_file: Optional[str] = None
    output_tables: List[str] = None
    processing_metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.output_tables is None:
            self.output_tables = []
        if self.processing_metadata is None:
            self.processing_metadata = {}


@dataclass
class ETLIntegrationConfig:
    """ETL integration configuration"""
    database_path: Path
    polling_interval: int = 30  # seconds
    status_check_timeout: int = 60  # seconds
    max_retry_attempts: int = 3
    retry_delay: int = 10  # seconds
    enable_auto_population: bool = True
    population_delay: int = 30  # seconds after ETL completion
    batch_size: int = 10
    cleanup_old_jobs: bool = True
    max_job_age: int = 86400 * 7  # 7 days in seconds


class ETLIntegration:
    """ETL pipeline integration for twin registry population - Pure async implementation"""
    
    def __init__(
        self,
        twin_service: TwinRegistryService,
        event_manager: TwinRegistryEventManager,
        config: ETLIntegrationConfig
    ):
        self.twin_service = twin_service
        self.event_manager = event_manager
        self.config = config
        self.db_path = config.database_path
        
        # Integration state
        self.is_active = False
        self.polling_task: Optional[asyncio.Task] = None
        self.registered_callbacks: List[Callable] = []
        
        # ETL job tracking
        self.etl_jobs: Dict[str, ETLJobInfo] = {}
        self.completed_jobs: List[str] = []
        self.failed_jobs: List[str] = []
        
        # Statistics
        self.stats = {
            "total_jobs_monitored": 0,
            "successful_populations": 0,
            "failed_populations": 0,
            "last_population_time": None,
            "average_population_time": 0.0
        }
    
    async def start(self) -> None:
        """Start ETL integration monitoring"""
        try:
            if self.is_active:
                logger.warning("ETL integration is already active")
                return
            
            self.is_active = True
            
            # Start polling task
            self.polling_task = asyncio.create_task(self._poll_etl_jobs())
            
            logger.info("ETL integration started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start ETL integration: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop ETL integration monitoring"""
        try:
            if not self.is_active:
                return
            
            self.is_active = False
            
            if self.polling_task:
                self.polling_task.cancel()
                try:
                    await self.polling_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("ETL integration stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop ETL integration: {e}")
            raise
    
    async def register_etl_job(self, job_info: ETLJobInfo) -> None:
        """Register a new ETL job for monitoring"""
        try:
            self.etl_jobs[job_info.job_id] = job_info
            self.stats["total_jobs_monitored"] += 1
            
            logger.info(f"Registered ETL job: {job_info.job_id}")
            
        except Exception as e:
            logger.error(f"Failed to register ETL job {job_info.job_id}: {e}")
            raise
    
    async def update_etl_job_status(self, job_id: str, status: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update the status of an ETL job"""
        try:
            if job_id not in self.etl_jobs:
                logger.warning(f"ETL job {job_id} not found")
                return
            
            job = self.etl_jobs[job_id]
            job.status = status
            
            if status == "completed":
                job.end_time = datetime.now(timezone.utc)
                self.completed_jobs.append(job_id)
                
                # Trigger ETL success event for automatic metrics creation
                await self._trigger_etl_success_event(job)
                
            elif status == "failed":
                job.end_time = datetime.now(timezone.utc)
                self.failed_jobs.append(job_id)
                
                # Trigger ETL failure event for status update
                await self._trigger_etl_failure_event(job)
            
            if metadata:
                job.processing_metadata.update(metadata)
            
            logger.info(f"Updated ETL job {job_id} status to: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update ETL job {job_id} status: {e}")
            raise
    
    async def _trigger_etl_success_event(self, job: ETLJobInfo) -> None:
        """Trigger ETL success event for automatic metrics creation"""
        try:
            # Calculate processing time
            processing_time = (job.end_time - job.start_time).total_seconds()
            
            # Extract records processed from metadata
            records_processed = job.processing_metadata.get("records_processed", 0)
            success_rate = job.processing_metadata.get("success_rate", 1.0)
            
            # Create twin ID from job info
            twin_id = f"etl_{job.job_id}"
            
            # Trigger the event using the event manager
            await self.event_manager.emit_event(
                TwinRegistryEvent(
                    event_type=EventType.ETL_SUCCESS,
                    priority=EventPriority.NORMAL,
                    timestamp=datetime.now(),
                    data={
                        'twin_id': twin_id,
                        'processing_time': processing_time,
                        'records_processed': records_processed,
                        'success_rate': success_rate,
                        'job_id': job.job_id,
                        'input_file': job.input_file
                    },
                    source="etl_integration",
                    correlation_id=job.job_id
                )
            )
            
            logger.info(f"Triggered ETL success event for job {job.job_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger ETL success event for job {job.job_id}: {e}")
    
    async def _trigger_etl_failure_event(self, job: ETLJobInfo) -> None:
        """Trigger ETL failure event for status update"""
        try:
            # Create twin ID from job info
            twin_id = f"etl_{job.job_id}"
            
            # Trigger the event using the event manager
            await self.event_manager.emit_event(
                TwinRegistryEvent(
                    event_type=EventType.ETL_FAILURE,
                    priority=EventPriority.HIGH,
                    timestamp=datetime.now(),
                    data={
                        'twin_id': twin_id,
                        'error_message': job.error_message or "Unknown ETL failure",
                        'failure_reason': "etl_pipeline_failure",
                        'job_id': job.job_id,
                        'input_file': job.input_file
                    },
                    source="etl_integration",
                    correlation_id=job.job_id
                )
            )
            
            logger.info(f"Triggered ETL failure event for job {job.job_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger ETL failure event for job {job.job_id}: {e}")
    
    async def _poll_etl_jobs(self) -> None:
        """Poll ETL jobs for status changes"""
        while self.is_active:
            try:
                # Check for completed or failed jobs
                await self._check_job_statuses()
                
                # Cleanup old jobs if enabled
                if self.config.cleanup_old_jobs:
                    await self._cleanup_old_jobs()
                
                # Wait for next polling interval
                await asyncio.sleep(self.config.polling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ETL job polling: {e}")
                await asyncio.sleep(self.config.retry_delay)
    
    async def _check_job_statuses(self) -> None:
        """Check the status of monitored ETL jobs"""
        try:
            # This would typically query the ETL system's job status
            # For now, we'll just log that we're checking
            logger.debug("Checking ETL job statuses...")
            
        except Exception as e:
            logger.error(f"Failed to check ETL job statuses: {e}")
    
    async def _cleanup_old_jobs(self) -> None:
        """Clean up old completed/failed jobs"""
        try:
            current_time = datetime.now(timezone.utc)
            jobs_to_remove = []
            
            for job_id, job in self.etl_jobs.items():
                if job.end_time:
                    age = (current_time - job.end_time).total_seconds()
                    if age > self.config.max_job_age:
                        jobs_to_remove.append(job_id)
            
            for job_id in jobs_to_remove:
                del self.etl_jobs[job_id]
                logger.debug(f"Cleaned up old ETL job: {job_id}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old ETL jobs: {e}")
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get the current status of the ETL integration"""
        try:
            return {
                "is_active": self.is_active,
                "total_jobs_monitored": self.stats["total_jobs_monitored"],
                "active_jobs": len([j for j in self.etl_jobs.values() if j.status == "running"]),
                "completed_jobs": len(self.completed_jobs),
                "failed_jobs": len(self.failed_jobs),
                "last_population_time": self.stats["last_population_time"],
                "average_population_time": self.stats["average_population_time"]
            }
        except Exception as e:
            logger.error(f"Failed to get ETL integration status: {e}")
            return {"error": str(e)}


class ETLProcessor:
    """Processes ETL jobs and triggers events"""
    
    def __init__(self, event_manager: TwinRegistryEventManager):
        self.event_manager = event_manager
    
    async def process_etl_completion(self, job_id: str, success: bool, metadata: Dict[str, Any]) -> None:
        """Process ETL completion and trigger appropriate events"""
        try:
            if success:
                # Trigger ETL success event
                await self.event_manager.emit_event(
                    TwinRegistryEvent(
                        event_type=EventType.ETL_SUCCESS,
                        priority=EventPriority.NORMAL,
                        timestamp=datetime.now(),
                        data={
                            'twin_id': f"etl_{job_id}",
                            'processing_time': metadata.get('processing_time', 0.0),
                            'records_processed': metadata.get('records_processed', 0),
                            'success_rate': metadata.get('success_rate', 1.0),
                            'job_id': job_id
                        },
                        source="etl_processor",
                        correlation_id=job_id
                    )
                )
            else:
                # Trigger ETL failure event
                await self.event_manager.emit_event(
                    TwinRegistryEvent(
                        event_type=EventType.ETL_FAILURE,
                        priority=EventPriority.HIGH,
                        timestamp=datetime.now(),
                        data={
                            'twin_id': f"etl_{job_id}",
                            'error_message': metadata.get('error_message', 'Unknown error'),
                            'failure_reason': metadata.get('failure_reason', 'etl_failure'),
                            'job_id': job_id
                        },
                        source="etl_processor",
                        correlation_id=job_id
                    )
                )
            
            logger.info(f"Processed ETL completion for job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to process ETL completion for job {job_id}: {e}")


class ETLValidator:
    """Validates ETL job data and metadata"""
    
    @staticmethod
    async def validate_job_info(job_info: ETLJobInfo) -> bool:
        """Validate ETL job information"""
        try:
            if not job_info.job_id:
                return False
            
            if not job_info.status:
                return False
            
            if not job_info.start_time:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate ETL job info: {e}")
            return False
    
    @staticmethod
    async def validate_metadata(metadata: Dict[str, Any]) -> bool:
        """Validate ETL processing metadata"""
        try:
            required_fields = ["records_processed", "processing_time"]
            
            for field in required_fields:
                if field not in metadata:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate ETL metadata: {e}")
            return False


class ETLMetricsCollector:
    """Collects and processes ETL metrics"""
    
    def __init__(self, twin_service: TwinRegistryService):
        self.twin_service = twin_service
    
    async def collect_etl_metrics(self, job_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Collect ETL metrics for analysis"""
        try:
            metrics = {
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "processing_time": metadata.get("processing_time", 0.0),
                "records_processed": metadata.get("records_processed", 0),
                "success_rate": metadata.get("success_rate", 1.0),
                "error_count": metadata.get("error_count", 0),
                "warning_count": metadata.get("warning_count", 0)
            }
            
            logger.info(f"Collected ETL metrics for job {job_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect ETL metrics for job {job_id}: {e}")
            return {}
