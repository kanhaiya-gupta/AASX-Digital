"""
ETL Integration for Twin Registry Population
Provides hooks and integration points with the ETL pipeline
"""

import logging
import asyncio
import sqlite3
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

from ..events.event_types import Event, create_etl_completion_event
from ..events.event_bus import EventBus

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
    """ETL pipeline integration for twin registry population"""
    
    def __init__(
        self,
        event_bus: EventBus,
        config: ETLIntegrationConfig
    ):
        self.event_bus = event_bus
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
            self.is_active = False
            raise
    
    async def stop(self) -> None:
        """Stop ETL integration monitoring"""
        try:
            if not self.is_active:
                logger.warning("ETL integration is not active")
                return
            
            self.is_active = False
            
            # Cancel polling task
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
    
    async def _poll_etl_jobs(self) -> None:
        """Poll ETL jobs for status changes"""
        while self.is_active:
            try:
                await self._check_etl_jobs()
                await asyncio.sleep(self.config.polling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ETL job polling: {e}")
                await asyncio.sleep(self.config.polling_interval)
    
    async def _check_etl_jobs(self) -> None:
        """Check ETL jobs for status changes"""
        try:
            # Get current ETL jobs from database
            current_jobs = await self._get_etl_jobs_from_db()
            
            # Check for new or updated jobs
            for job_info in current_jobs:
                await self._process_etl_job(job_info)
            
            # Cleanup old jobs if enabled
            if self.config.cleanup_old_jobs:
                await self._cleanup_old_jobs()
                
        except Exception as e:
            logger.error(f"Failed to check ETL jobs: {e}")
    
    async def _get_etl_jobs_from_db(self) -> List[ETLJobInfo]:
        """Get ETL jobs from database"""
        jobs = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Query ETL jobs table (adjust table name as needed)
                cursor.execute("""
                    SELECT 
                        job_id, status, start_time, end_time, 
                        input_file, processing_metadata, error_message
                    FROM aasx_processing 
                    WHERE status IN ('completed', 'failed', 'processing')
                    ORDER BY start_time DESC
                    LIMIT ?
                """, (self.config.batch_size,))
                
                rows = cursor.fetchall()
                
                for row in rows:
                    try:
                        # Parse datetime fields
                        start_time = datetime.fromisoformat(row[2]) if row[2] else datetime.now(timezone.utc)
                        end_time = datetime.fromisoformat(row[3]) if row[3] else None
                        
                        # Parse processing metadata
                        processing_metadata = {}
                        if row[5]:
                            try:
                                import json
                                processing_metadata = json.loads(row[5])
                            except:
                                pass
                        
                        job_info = ETLJobInfo(
                            job_id=row[0],
                            status=row[1],
                            start_time=start_time,
                            end_time=end_time,
                            input_file=row[4],
                            processing_metadata=processing_metadata,
                            error_message=row[6]
                        )
                        
                        jobs.append(job_info)
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse ETL job row: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to get ETL jobs from database: {e}")
        
        return jobs
    
    async def _process_etl_job(self, job_info: ETLJobInfo) -> None:
        """Process an ETL job for population triggers"""
        try:
            job_id = job_info.job_id
            
            # Check if this is a new job
            if job_id not in self.etl_jobs:
                self.etl_jobs[job_id] = job_info
                self.stats["total_jobs_monitored"] += 1
                logger.info(f"New ETL job detected: {job_id}")
            
            # Check for status changes
            current_job = self.etl_jobs[job_id]
            if current_job.status != job_info.status:
                current_job.status = job_info.status
                current_job.end_time = job_info.end_time
                current_job.error_message = job_info.error_message
                
                logger.info(f"ETL job {job_id} status changed to: {job_info.status}")
                
                # Handle status change
                await self._handle_etl_status_change(job_info)
            
            # Update job info
            self.etl_jobs[job_id] = job_info
            
        except Exception as e:
            logger.error(f"Failed to process ETL job {job_info.job_id}: {e}")
    
    async def _handle_etl_status_change(self, job_info: ETLJobInfo) -> None:
        """Handle ETL job status changes"""
        try:
            if job_info.status == "completed":
                await self._handle_etl_completion(job_info)
            elif job_info.status == "failed":
                await self._handle_etl_failure(job_info)
            elif job_info.status == "processing":
                await self._handle_etl_processing(job_info)
                
        except Exception as e:
            logger.error(f"Failed to handle ETL status change: {e}")
    
    async def _handle_etl_completion(self, job_info: ETLJobInfo) -> None:
        """Handle ETL job completion"""
        try:
            job_id = job_info.job_id
            
            # Add to completed jobs
            if job_id not in self.completed_jobs:
                self.completed_jobs.append(job_id)
            
            # Remove from failed jobs if present
            if job_id in self.failed_jobs:
                self.failed_jobs.remove(job_id)
            
            logger.info(f"ETL job completed: {job_id}")
            
            # Trigger population after delay
            if self.config.enable_auto_population:
                await asyncio.sleep(self.config.population_delay)
                await self._trigger_registry_population(job_info)
            
            # Execute registered callbacks
            await self._execute_callbacks("etl_completion", job_info)
            
        except Exception as e:
            logger.error(f"Failed to handle ETL completion: {e}")
    
    async def _handle_etl_failure(self, job_info: ETLJobInfo) -> None:
        """Handle ETL job failure"""
        try:
            job_id = job_info.job_id
            
            # Add to failed jobs
            if job_id not in self.failed_jobs:
                self.failed_jobs.append(job_id)
            
            # Remove from completed jobs if present
            if job_id in self.completed_jobs:
                self.completed_jobs.remove(job_id)
            
            logger.warning(f"ETL job failed: {job_id} - {job_info.error_message}")
            
            # Execute registered callbacks
            await self._execute_callbacks("etl_failure", job_info)
            
        except Exception as e:
            logger.error(f"Failed to handle ETL failure: {e}")
    
    async def _handle_etl_processing(self, job_info: ETLJobInfo) -> None:
        """Handle ETL job processing"""
        try:
            job_id = job_info.job_id
            logger.debug(f"ETL job processing: {job_id}")
            
            # Execute registered callbacks
            await self._execute_callbacks("etl_processing", job_info)
            
        except Exception as e:
            logger.error(f"Failed to handle ETL processing: {e}")
    
    async def _trigger_registry_population(self, job_info: ETLJobInfo) -> None:
        """Trigger twin registry population for completed ETL job"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Create ETL completion event
            event = create_etl_completion_event(
                source="etl_integration",
                job_id=job_info.job_id,
                input_file=job_info.input_file,
                processing_metadata=job_info.processing_metadata,
                completion_time=job_info.end_time or datetime.now(timezone.utc)
            )
            
            # Publish event
            await self.event_bus.publish(event)
            
            # Update statistics
            population_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.stats["successful_populations"] += 1
            self.stats["last_population_time"] = start_time
            
            # Update average population time
            total_time = self.stats["average_population_time"] * (self.stats["successful_populations"] - 1) + population_time
            self.stats["average_population_time"] = total_time / self.stats["successful_populations"]
            
            logger.info(f"Registry population triggered for ETL job: {job_info.job_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger registry population: {e}")
            self.stats["failed_populations"] += 1
    
    async def _execute_callbacks(self, event_type: str, job_info: ETLJobInfo) -> None:
        """Execute registered callbacks"""
        try:
            for callback in self.registered_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_type, job_info)
                    else:
                        callback(event_type, job_info)
                except Exception as e:
                    logger.error(f"Callback execution failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to execute callbacks: {e}")
    
    async def _cleanup_old_jobs(self) -> None:
        """Cleanup old ETL jobs"""
        try:
            current_time = datetime.now(timezone.utc)
            cutoff_time = current_time.timestamp() - self.config.max_job_age
            
            # Cleanup old jobs from tracking
            old_jobs = [
                job_id for job_id, job_info in self.etl_jobs.items()
                if job_info.start_time.timestamp() < cutoff_time
            ]
            
            for job_id in old_jobs:
                del self.etl_jobs[job_id]
                if job_id in self.completed_jobs:
                    self.completed_jobs.remove(job_id)
                if job_id in self.failed_jobs:
                    self.failed_jobs.remove(job_id)
            
            if old_jobs:
                logger.info(f"Cleaned up {len(old_jobs)} old ETL jobs")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for ETL events"""
        if callback not in self.registered_callbacks:
            self.registered_callbacks.append(callback)
            logger.info("ETL integration callback registered")
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback"""
        if callback in self.registered_callbacks:
            self.registered_callbacks.remove(callback)
            logger.info("ETL integration callback unregistered")
    
    async def get_etl_job_status(self, job_id: str) -> Optional[ETLJobInfo]:
        """Get status of a specific ETL job"""
        return self.etl_jobs.get(job_id)
    
    def get_etl_jobs_summary(self) -> Dict[str, Any]:
        """Get summary of ETL jobs"""
        return {
            "total_jobs": len(self.etl_jobs),
            "completed_jobs": len(self.completed_jobs),
            "failed_jobs": len(self.failed_jobs),
            "processing_jobs": len([
                job for job in self.etl_jobs.values()
                if job.status == "processing"
            ]),
            "stats": self.stats.copy()
        }
    
    async def manually_trigger_population(self, job_id: str) -> bool:
        """Manually trigger population for a specific ETL job"""
        try:
            job_info = self.etl_jobs.get(job_id)
            if not job_info:
                logger.warning(f"ETL job not found: {job_id}")
                return False
            
            if job_info.status != "completed":
                logger.warning(f"ETL job {job_id} is not completed (status: {job_info.status})")
                return False
            
            await self._trigger_registry_population(job_info)
            return True
            
        except Exception as e:
            logger.error(f"Failed to manually trigger population: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of ETL integration"""
        health_status = {
            "active": self.is_active,
            "polling_task_running": self.polling_task and not self.polling_task.done(),
            "total_jobs_monitored": self.stats["total_jobs_monitored"],
            "recent_populations": self.stats["successful_populations"],
            "failed_populations": self.stats["failed_populations"],
            "last_population": self.stats["last_population_time"].isoformat() if self.stats["last_population_time"] else None,
            "average_population_time": round(self.stats["average_population_time"], 3),
            "registered_callbacks": len(self.registered_callbacks)
        }
        
        # Check database connectivity
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM aasx_processing")
                count = cursor.fetchone()[0]
                health_status["database_accessible"] = True
                health_status["total_etl_jobs_in_db"] = count
        except Exception as e:
            health_status["database_accessible"] = False
            health_status["database_error"] = str(e)
        
        return health_status
    
    async def cleanup(self) -> None:
        """Cleanup ETL integration resources"""
        try:
            await self.stop()
            
            # Clear tracking data
            self.etl_jobs.clear()
            self.completed_jobs.clear()
            self.failed_jobs.clear()
            self.registered_callbacks.clear()
            
            logger.info("ETL integration cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during ETL integration cleanup: {e}")
            raise
