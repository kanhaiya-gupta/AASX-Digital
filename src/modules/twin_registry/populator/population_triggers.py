"""
Population Triggers

Handles automatic population triggers based on system events such as:
- File uploads
- ETL pipeline completion
- AI/RAG processing completion
- Scheduled population tasks
- Manual triggers
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum

from src.twin_registry.repositories.twin_registry_repository import TwinRegistryRepository
from src.twin_registry.repositories.twin_registry_metrics_repository import TwinRegistryMetricsRepository

from .twin_registry_populator import TwinRegistryPopulator

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Enumeration of trigger types."""
    FILE_UPLOAD = "file_upload"
    ETL_COMPLETION = "etl_completion"
    AI_RAG_COMPLETION = "ai_rag_completion"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    SYSTEM_EVENT = "system_event"


class TriggerStatus(Enum):
    """Enumeration of trigger statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"


class PopulationTriggers:
    """
    Manages automatic population triggers.
    
    Handles:
    - Event-based triggers
    - Scheduled triggers
    - Manual triggers
    - Trigger validation
    - Trigger execution
    """
    
    def __init__(
        self,
        registry_repo: TwinRegistryRepository,
        metrics_repo: TwinRegistryMetricsRepository,
        populator: TwinRegistryPopulator
    ):
        """Initialize population triggers."""
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        self.populator = populator
        
        # Trigger registry
        self.triggers: Dict[str, Dict[str, Any]] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Scheduled tasks
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info("Population Triggers initialized")
    
    async def register_file_upload_trigger(
        self,
        trigger_id: str,
        file_patterns: Optional[List[str]] = None,
        auto_populate: bool = True
    ) -> bool:
        """
        Register a file upload trigger.
        
        Args:
            trigger_id: Unique identifier for the trigger
            file_patterns: File patterns to match (e.g., ["*.aasx", "*.json"])
            auto_populate: Whether to automatically populate on upload
            
        Returns:
            bool: True if registration successful
        """
        try:
            trigger_config = {
                "trigger_id": trigger_id,
                "trigger_type": TriggerType.FILE_UPLOAD.value,
                "file_patterns": file_patterns or ["*"],
                "auto_populate": auto_populate,
                "status": TriggerStatus.PENDING.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_triggered": None,
                "trigger_count": 0,
                "success_count": 0,
                "failure_count": 0
            }
            
            self.triggers[trigger_id] = trigger_config
            
            # Register event handler
            if trigger_id not in self.event_handlers:
                self.event_handlers[trigger_id] = []
            
            logger.info(f"Registered file upload trigger: {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register file upload trigger: {e}")
            return False
    
    async def register_etl_completion_trigger(
        self,
        trigger_id: str,
        job_types: Optional[List[str]] = None,
        auto_enhance: bool = True
    ) -> bool:
        """
        Register an ETL completion trigger.
        
        Args:
            trigger_id: Unique identifier for the trigger
            job_types: ETL job types to monitor (e.g., ["extraction", "generation"])
            auto_enhance: Whether to automatically enhance registry on ETL completion
            
        Returns:
            bool: True if registration successful
        """
        try:
            trigger_config = {
                "trigger_id": trigger_id,
                "trigger_type": TriggerType.ETL_COMPLETION.value,
                "job_types": job_types or ["extraction", "generation"],
                "auto_enhance": auto_enhance,
                "status": TriggerStatus.PENDING.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_triggered": None,
                "trigger_count": 0,
                "success_count": 0,
                "failure_count": 0
            }
            
            self.triggers[trigger_id] = trigger_config
            
            # Register event handler
            if trigger_id not in self.event_handlers:
                self.event_handlers[trigger_id] = []
            
            logger.info(f"Registered ETL completion trigger: {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register ETL completion trigger: {e}")
            return False
    
    async def register_scheduled_trigger(
        self,
        trigger_id: str,
        schedule_interval: timedelta,
        population_task: Callable,
        enabled: bool = True
    ) -> bool:
        """
        Register a scheduled population trigger.
        
        Args:
            trigger_id: Unique identifier for the trigger
            schedule_interval: Time interval between executions
            population_task: Async function to execute
            enabled: Whether the trigger is enabled
            
        Returns:
            bool: True if registration successful
        """
        try:
            trigger_config = {
                "trigger_id": trigger_id,
                "trigger_type": TriggerType.SCHEDULED.value,
                "schedule_interval": schedule_interval,
                "population_task": population_task,
                "status": TriggerStatus.ENABLED.value if enabled else TriggerStatus.DISABLED.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_triggered": None,
                "next_scheduled": datetime.now(timezone.utc) + schedule_interval,
                "trigger_count": 0,
                "success_count": 0,
                "failure_count": 0
            }
            
            self.triggers[trigger_id] = trigger_config
            
            # Start scheduled task if enabled
            if enabled:
                await self._start_scheduled_task(trigger_id)
            
            logger.info(f"Registered scheduled trigger: {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register scheduled trigger: {e}")
            return False
    
    async def trigger_file_upload(
        self,
        file_id: str,
        file_name: str,
        user_id: str,
        org_id: str,
        file_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger population for a file upload.
        
        Args:
            file_id: Unique identifier for the uploaded file
            file_name: Name of the uploaded file
            user_id: ID of the user who uploaded the file
            org_id: Organization ID of the user
            file_metadata: Additional file metadata
            
        Returns:
            Dict containing trigger execution results
        """
        try:
            logger.info(f"Triggering file upload population for: {file_id}")
            
            # Find matching triggers
            matching_triggers = self._find_matching_file_triggers(file_name)
            
            if not matching_triggers:
                logger.info(f"No matching triggers found for file: {file_name}")
                return {
                    "success": False,
                    "message": "No matching triggers found",
                    "file_id": file_id
                }
            
            # Execute triggers
            results = []
            for trigger_id in matching_triggers:
                trigger_result = await self._execute_file_upload_trigger(
                    trigger_id, file_id, file_name, user_id, org_id, file_metadata
                )
                results.append(trigger_result)
                
                # Update trigger statistics
                await self._update_trigger_statistics(trigger_id, trigger_result["success"])
            
            # Check overall success
            overall_success = any(result["success"] for result in results)
            
            return {
                "success": overall_success,
                "file_id": file_id,
                "trigger_results": results,
                "message": f"Executed {len(results)} triggers"
            }
            
        except Exception as e:
            logger.error(f"File upload trigger failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id
            }
    
    async def trigger_etl_completion(
        self,
        job_id: str,
        etl_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger population for ETL completion.
        
        Args:
            job_id: ETL job identifier
            etl_result: Results from ETL processing
            
        Returns:
            Dict containing trigger execution results
        """
        try:
            logger.info(f"Triggering ETL completion population for job: {job_id}")
            
            # Find matching triggers
            job_type = etl_result.get("job_type", "extraction")
            matching_triggers = self._find_matching_etl_triggers(job_type)
            
            if not matching_triggers:
                logger.info(f"No matching ETL triggers found for job type: {job_type}")
                return {
                    "success": False,
                    "message": "No matching ETL triggers found",
                    "job_id": job_id
                }
            
            # Execute triggers
            results = []
            for trigger_id in matching_triggers:
                trigger_result = await self._execute_etl_completion_trigger(
                    trigger_id, job_id, etl_result
                )
                results.append(trigger_result)
                
                # Update trigger statistics
                await self._update_trigger_statistics(trigger_id, trigger_result["success"])
            
            # Check overall success
            overall_success = any(result["success"] for result in results)
            
            return {
                "success": overall_success,
                "job_id": job_id,
                "trigger_results": results,
                "message": f"Executed {len(results)} ETL triggers"
            }
            
        except Exception as e:
            logger.error(f"ETL completion trigger failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "job_id": job_id
            }
    
    async def manual_trigger(
        self,
        trigger_id: str,
        trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Manually trigger a population process.
        
        Args:
            trigger_id: Trigger identifier
            trigger_data: Data for the trigger execution
            
        Returns:
            Dict containing trigger execution results
        """
        try:
            logger.info(f"Manual trigger requested for: {trigger_id}")
            
            if trigger_id not in self.triggers:
                return {
                    "success": False,
                    "error": f"Trigger not found: {trigger_id}"
                }
            
            trigger = self.triggers[trigger_id]
            
            # Execute based on trigger type
            if trigger["trigger_type"] == TriggerType.FILE_UPLOAD.value:
                result = await self._execute_file_upload_trigger(
                    trigger_id,
                    trigger_data.get("file_id"),
                    trigger_data.get("file_name"),
                    trigger_data.get("user_id"),
                    trigger_data.get("org_id"),
                    trigger_data.get("file_metadata")
                )
            elif trigger["trigger_type"] == TriggerType.ETL_COMPLETION.value:
                result = await self._execute_etl_completion_trigger(
                    trigger_id,
                    trigger_data.get("job_id"),
                    trigger_data.get("etl_result", {})
                )
            else:
                result = {
                    "success": False,
                    "error": f"Unsupported trigger type: {trigger['trigger_type']}"
                }
            
            # Update trigger statistics
            if "success" in result:
                await self._update_trigger_statistics(trigger_id, result["success"])
            
            return result
            
        except Exception as e:
            logger.error(f"Manual trigger failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_matching_file_triggers(self, file_name: str) -> List[str]:
        """Find triggers that match the given file name."""
        matching_triggers = []
        
        for trigger_id, trigger in self.triggers.items():
            if trigger["trigger_type"] != TriggerType.FILE_UPLOAD.value:
                continue
            
            if trigger["status"] != TriggerStatus.PENDING.value:
                continue
            
            # Check file patterns
            file_patterns = trigger.get("file_patterns", ["*"])
            if self._file_matches_patterns(file_name, file_patterns):
                matching_triggers.append(trigger_id)
        
        return matching_triggers
    
    def _find_matching_etl_triggers(self, job_type: str) -> List[str]:
        """Find triggers that match the given ETL job type."""
        matching_triggers = []
        
        for trigger_id, trigger in self.triggers.items():
            if trigger["trigger_type"] != TriggerType.ETL_COMPLETION.value:
                continue
            
            if trigger["status"] != TriggerStatus.PENDING.value:
                continue
            
            # Check job types
            job_types = trigger.get("job_types", [])
            if not job_types or job_type in job_types:
                matching_triggers.append(trigger_id)
        
        return matching_triggers
    
    def _file_matches_patterns(self, file_name: str, patterns: List[str]) -> bool:
        """Check if file name matches any of the patterns."""
        for pattern in patterns:
            if pattern == "*":
                return True
            elif pattern.startswith("*."):
                extension = pattern[1:]  # Remove *
                if file_name.endswith(extension):
                    return True
            elif pattern == file_name:
                return True
        
        return False
    
    async def _execute_file_upload_trigger(
        self,
        trigger_id: str,
        file_id: str,
        file_name: str,
        user_id: str,
        org_id: str,
        file_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a file upload trigger."""
        try:
            # Update trigger status
            self.triggers[trigger_id]["status"] = TriggerStatus.PROCESSING.value
            self.triggers[trigger_id]["last_triggered"] = datetime.now(timezone.utc).isoformat()
            
            # Execute population
            result = await self.populator.create_basic_registry_from_upload(
                file_id=file_id,
                file_name=file_name,
                user_id=user_id,
                org_id=org_id,
                file_metadata=file_metadata
            )
            
            # Update trigger status
            self.triggers[trigger_id]["status"] = TriggerStatus.COMPLETED.value
            
            return {
                "success": True,
                "trigger_id": trigger_id,
                "registry_id": result,
                "message": "File upload trigger executed successfully"
            }
            
        except Exception as e:
            logger.error(f"File upload trigger execution failed: {e}")
            self.triggers[trigger_id]["status"] = TriggerStatus.FAILED.value
            
            return {
                "success": False,
                "trigger_id": trigger_id,
                "error": str(e)
            }
    
    async def _execute_etl_completion_trigger(
        self,
        trigger_id: str,
        job_id: str,
        etl_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an ETL completion trigger."""
        try:
            # Update trigger status
            self.triggers[trigger_id]["status"] = TriggerStatus.PROCESSING.value
            self.triggers[trigger_id]["last_triggered"] = datetime.now(timezone.utc).isoformat()
            
            # Execute population
            result = await self.populator.populate_from_etl(
                job_id=job_id,
                etl_result=etl_result
            )
            
            # Update trigger status
            self.triggers[trigger_id]["status"] = TriggerStatus.COMPLETED.value
            
            return {
                "success": result,
                "trigger_id": trigger_id,
                "job_id": job_id,
                "message": "ETL completion trigger executed successfully"
            }
            
        except Exception as e:
            logger.error(f"ETL completion trigger execution failed: {e}")
            self.triggers[trigger_id]["status"] = TriggerStatus.FAILED.value
            
            return {
                "success": False,
                "trigger_id": trigger_id,
                "error": str(e)
            }
    
    async def _start_scheduled_task(self, trigger_id: str):
        """Start a scheduled task for a trigger."""
        try:
            trigger = self.triggers[trigger_id]
            schedule_interval = trigger["schedule_interval"]
            population_task = trigger["population_task"]
            
            async def scheduled_execution():
                while trigger["status"] == TriggerStatus.ENABLED.value:
                    try:
                        # Execute the population task
                        await population_task()
                        
                        # Update trigger statistics
                        await self._update_trigger_statistics(trigger_id, True)
                        
                        # Schedule next execution
                        trigger["next_scheduled"] = datetime.now(timezone.utc) + schedule_interval
                        
                        # Wait for next execution
                        await asyncio.sleep(schedule_interval.total_seconds())
                        
                    except Exception as e:
                        logger.error(f"Scheduled task execution failed: {e}")
                        await self._update_trigger_statistics(trigger_id, False)
                        
                        # Wait before retry
                        await asyncio.sleep(60)  # 1 minute retry delay
            
            # Create and start the task
            task = asyncio.create_task(scheduled_execution())
            self.scheduled_tasks[trigger_id] = task
            
            logger.info(f"Started scheduled task for trigger: {trigger_id}")
            
        except Exception as e:
            logger.error(f"Failed to start scheduled task: {e}")
    
    async def _update_trigger_statistics(self, trigger_id: str, success: bool):
        """Update trigger execution statistics."""
        if trigger_id in self.triggers:
            trigger = self.triggers[trigger_id]
            trigger["trigger_count"] += 1
            
            if success:
                trigger["success_count"] += 1
            else:
                trigger["failure_count"] += 1
    
    async def get_trigger_status(self, trigger_id: str) -> Dict[str, Any]:
        """Get the current status of a trigger."""
        if trigger_id not in self.triggers:
            return {"error": "Trigger not found"}
        
        trigger = self.triggers[trigger_id]
        return {
            "trigger_id": trigger_id,
            "trigger_type": trigger["trigger_type"],
            "status": trigger["status"],
            "created_at": trigger["created_at"],
            "last_triggered": trigger["last_triggered"],
            "trigger_count": trigger["trigger_count"],
            "success_count": trigger["success_count"],
            "failure_count": trigger["failure_count"],
            "success_rate": trigger["success_count"] / max(trigger["trigger_count"], 1)
        }
    
    async def disable_trigger(self, trigger_id: str) -> bool:
        """Disable a trigger."""
        try:
            if trigger_id not in self.triggers:
                return False
            
            self.triggers[trigger_id]["status"] = TriggerStatus.DISABLED.value
            
            # Stop scheduled task if running
            if trigger_id in self.scheduled_tasks:
                task = self.scheduled_tasks[trigger_id]
                task.cancel()
                del self.scheduled_tasks[trigger_id]
            
            logger.info(f"Disabled trigger: {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable trigger: {e}")
            return False
    
    async def enable_trigger(self, trigger_id: str) -> bool:
        """Enable a trigger."""
        try:
            if trigger_id not in self.triggers:
                return False
            
            trigger = self.triggers[trigger_id]
            trigger["status"] = TriggerStatus.PENDING.value
            
            # Start scheduled task if applicable
            if trigger["trigger_type"] == TriggerType.SCHEDULED.value:
                await self._start_scheduled_task(trigger_id)
            
            logger.info(f"Enabled trigger: {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable trigger: {e}")
            return False
    
    async def cleanup_triggers(self) -> Dict[str, Any]:
        """Clean up all triggers and stop scheduled tasks."""
        try:
            # Stop all scheduled tasks
            for trigger_id, task in self.scheduled_tasks.items():
                task.cancel()
            
            self.scheduled_tasks.clear()
            
            # Clear triggers
            trigger_count = len(self.triggers)
            self.triggers.clear()
            
            logger.info(f"Cleaned up {trigger_count} triggers")
            
            return {
                "success": True,
                "cleaned_triggers": trigger_count,
                "stopped_tasks": len(self.scheduled_tasks)
            }
            
        except Exception as e:
            logger.error(f"Trigger cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
