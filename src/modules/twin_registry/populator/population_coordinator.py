"""
Population Coordinator

Manages the overall population workflow and coordinates between different
population phases. Handles phase transitions, error recovery, and ensures
data consistency across the population process.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum

from src.twin_registry.repositories.twin_registry_repository import TwinRegistryRepository
from src.twin_registry.repositories.twin_registry_metrics_repository import TwinRegistryMetricsRepository

from .phase1_upload_populator import Phase1UploadPopulator
from .phase2_etl_populator import Phase2ETLPopulator

logger = logging.getLogger(__name__)


class PopulationPhase(Enum):
    """Enumeration of population phases."""
    NOT_STARTED = "not_started"
    PHASE1_BASIC = "phase1_basic"
    PHASE1_COMPLETE = "phase1_complete"
    PHASE2_PROCESSING = "phase2_processing"
    PHASE2_COMPLETE = "phase2_complete"
    ERROR = "error"
    COMPLETED = "completed"


class PopulationStatus(Enum):
    """Enumeration of population statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class PopulationCoordinator:
    """
    Coordinates the overall population workflow.
    
    Manages:
    - Phase transitions
    - Error handling and recovery
    - Data consistency validation
    - Population state tracking
    - Rollback operations
    """
    
    def __init__(
        self,
        registry_repo: TwinRegistryRepository,
        metrics_repo: TwinRegistryMetricsRepository
    ):
        """Initialize the population coordinator."""
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        self.phase1_populator = Phase1UploadPopulator(registry_repo, metrics_repo)
        self.phase2_populator = Phase2ETLPopulator(registry_repo, metrics_repo)
        
        logger.info("Population Coordinator initialized")
    
    async def start_population_workflow(
        self,
        file_id: str,
        file_name: str,
        user_id: str,
        org_id: str,
        file_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start the complete population workflow.
        
        Args:
            file_id: Unique identifier for the uploaded file
            file_name: Name of the uploaded file
            user_id: ID of the user who uploaded the file
            org_id: Organization ID of the user
            file_metadata: Additional file metadata
            
        Returns:
            Dict containing workflow status and registry information
        """
        try:
            logger.info(f"Starting population workflow for file: {file_id}")
            
            # Phase 1: Create basic registry
            phase1_result = await self._execute_phase1(
                file_id, file_name, user_id, org_id, file_metadata
            )
            
            if not phase1_result["success"]:
                logger.error(f"Phase 1 failed for file {file_id}: {phase1_result['error']}")
                return {
                    "success": False,
                    "error": f"Phase 1 failed: {phase1_result['error']}",
                    "phase": PopulationPhase.ERROR.value,
                    "registry_id": None
                }
            
            registry_id = phase1_result["registry_id"]
            logger.info(f"Phase 1 completed successfully for registry: {registry_id}")
            
            # Return workflow status
            return {
                "success": True,
                "registry_id": registry_id,
                "phase": PopulationPhase.PHASE1_COMPLETE.value,
                "status": PopulationStatus.COMPLETED.value,
                "message": "Phase 1 completed, ready for ETL processing",
                "next_phase": "phase2_etl",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Population workflow failed for file {file_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "phase": PopulationPhase.ERROR.value,
                "registry_id": None
            }
    
    async def continue_to_phase2(
        self,
        registry_id: str,
        job_id: str,
        etl_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Continue population workflow to Phase 2 (ETL enhancement).
        
        Args:
            registry_id: Registry identifier
            job_id: ETL job identifier
            etl_result: Results from ETL processing
            
        Returns:
            Dict containing Phase 2 status and results
        """
        try:
            logger.info(f"Continuing to Phase 2 for registry: {registry_id}")
            
            # Validate registry exists and is ready for Phase 2
            validation_result = await self._validate_phase2_readiness(registry_id)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "phase": PopulationPhase.ERROR.value
                }
            
            # Execute Phase 2
            phase2_result = await self._execute_phase2(registry_id, job_id, etl_result)
            
            if not phase2_result["success"]:
                logger.error(f"Phase 2 failed for registry {registry_id}: {phase2_result['error']}")
                return {
                    "success": False,
                    "error": f"Phase 2 failed: {phase2_result['error']}",
                    "phase": PopulationPhase.ERROR.value
                }
            
            logger.info(f"Phase 2 completed successfully for registry: {registry_id}")
            
            return {
                "success": True,
                "registry_id": registry_id,
                "phase": PopulationPhase.PHASE2_COMPLETE.value,
                "status": PopulationStatus.COMPLETED.value,
                "message": "Phase 2 completed, registry fully populated",
                "etl_job_id": job_id,
                "completion_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Phase 2 failed for registry {registry_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "phase": PopulationPhase.ERROR.value
            }
    
    async def get_population_progress(self, registry_id: str) -> Dict[str, Any]:
        """
        Get the current population progress for a registry.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            Dict containing population progress information
        """
        try:
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                return {
                    "error": "Registry not found",
                    "phase": PopulationPhase.NOT_STARTED.value
                }
            
            # Determine current phase
            current_phase = self._determine_current_phase(registry)
            
            # Get progress details
            progress_details = await self._get_phase_progress(registry_id, current_phase)
            
            return {
                "registry_id": registry_id,
                "twin_name": registry.twin_name,
                "current_phase": current_phase.value,
                "integration_status": registry.integration_status,
                "lifecycle_status": registry.lifecycle_status,
                "overall_health_score": registry.overall_health_score,
                "progress_percentage": progress_details["percentage"],
                "phase_details": progress_details["details"],
                "last_updated": registry.updated_at,
                "estimated_completion": progress_details.get("estimated_completion"),
                "next_steps": progress_details.get("next_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to get population progress: {e}")
            return {
                "error": str(e),
                "phase": PopulationPhase.ERROR.value
            }
    
    async def rollback_population(
        self,
        registry_id: str,
        target_phase: Optional[PopulationPhase] = None
    ) -> Dict[str, Any]:
        """
        Rollback population to a specific phase or completely.
        
        Args:
            registry_id: Registry identifier
            target_phase: Target phase to rollback to (None = complete rollback)
            
        Returns:
            Dict containing rollback status
        """
        try:
            logger.info(f"Rolling back population for registry: {registry_id}")
            
            if target_phase is None:
                # Complete rollback - delete registry
                success = await self.phase1_populator.rollback_basic_registry(registry_id)
                
                if success:
                    return {
                        "success": True,
                        "message": "Population completely rolled back",
                        "registry_id": registry_id,
                        "current_phase": PopulationPhase.NOT_STARTED.value
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to rollback population",
                        "registry_id": registry_id
                    }
            else:
                # Partial rollback to specific phase
                rollback_result = await self._rollback_to_phase(registry_id, target_phase)
                return rollback_result
            
        except Exception as e:
            logger.error(f"Rollback failed for registry {registry_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "registry_id": registry_id
            }
    
    async def _execute_phase1(
        self,
        file_id: str,
        file_name: str,
        user_id: str,
        org_id: str,
        file_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute Phase 1 population."""
        try:
            registry_id = await self.phase1_populator.create_basic_registry(
                file_id=file_id,
                file_name=file_name,
                user_id=user_id,
                org_id=org_id,
                file_metadata=file_metadata
            )
            
            return {
                "success": True,
                "registry_id": registry_id,
                "phase": PopulationPhase.PHASE1_BASIC.value
            }
            
        except Exception as e:
            logger.error(f"Phase 1 execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "phase": PopulationPhase.ERROR.value
            }
    
    async def _execute_phase2(
        self,
        registry_id: str,
        job_id: str,
        etl_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Phase 2 population."""
        try:
            success = await self.phase2_populator.enhance_registry(
                registry_id=registry_id,
                job_id=job_id,
                etl_result=etl_result
            )
            
            if success:
                return {
                    "success": True,
                    "phase": PopulationPhase.PHASE2_COMPLETE.value
                }
            else:
                return {
                    "success": False,
                    "error": "Registry enhancement failed",
                    "phase": PopulationPhase.ERROR.value
                }
                
        except Exception as e:
            logger.error(f"Phase 2 execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "phase": PopulationPhase.ERROR.value
            }
    
    async def _validate_phase2_readiness(self, registry_id: str) -> Dict[str, Any]:
        """Validate that registry is ready for Phase 2."""
        try:
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                return {
                    "valid": False,
                    "error": "Registry not found"
                }
            
            # Check if Phase 1 is complete
            if registry.integration_status not in ["pending", "uploaded"]:
                return {
                    "valid": False,
                    "error": f"Registry not ready for Phase 2. Current status: {registry.integration_status}"
                }
            
            return {
                "valid": True,
                "current_status": registry.integration_status
            }
            
        except Exception as e:
            logger.error(f"Phase 2 validation failed: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _determine_current_phase(self, registry) -> PopulationPhase:
        """Determine the current population phase for a registry."""
        integration_status = registry.integration_status
        lifecycle_status = registry.lifecycle_status
        
        if integration_status == "pending":
            return PopulationPhase.PHASE1_BASIC
        elif integration_status == "uploaded":
            return PopulationPhase.PHASE1_COMPLETE
        elif integration_status == "processing":
            return PopulationPhase.PHASE2_PROCESSING
        elif integration_status == "active" and lifecycle_status == "active":
            return PopulationPhase.PHASE2_COMPLETE
        elif integration_status == "error":
            return PopulationPhase.ERROR
        else:
            return PopulationPhase.NOT_STARTED
    
    async def _get_phase_progress(
        self,
        registry_id: str,
        current_phase: PopulationPhase
    ) -> Dict[str, Any]:
        """Get progress details for the current phase."""
        progress_map = {
            PopulationPhase.NOT_STARTED: {"percentage": 0, "details": "Not started"},
            PopulationPhase.PHASE1_BASIC: {"percentage": 25, "details": "Creating basic registry"},
            PopulationPhase.PHASE1_COMPLETE: {"percentage": 50, "details": "Basic registry created, waiting for ETL"},
            PopulationPhase.PHASE2_PROCESSING: {"percentage": 75, "details": "ETL processing in progress"},
            PopulationPhase.PHASE2_COMPLETE: {"percentage": 100, "details": "Population completed"},
            PopulationPhase.ERROR: {"percentage": 0, "details": "Error occurred"}
        }
        
        progress = progress_map.get(current_phase, {"percentage": 0, "details": "Unknown phase"})
        
        # Add phase-specific details
        if current_phase == PopulationPhase.PHASE2_PROCESSING:
            # Get ETL progress details
            registry = await self.registry_repo.get_by_id(registry_id)
            if registry and hasattr(registry, 'registry_metadata'):
                metadata = registry.registry_metadata or {}
                if "etl_start_time" in metadata:
                    progress["details"] = f"ETL processing since {metadata['etl_start_time']}"
        
        # Add next steps
        progress["next_steps"] = self._get_next_steps(current_phase)
        
        return progress
    
    def _get_next_steps(self, current_phase: PopulationPhase) -> List[str]:
        """Get the next steps for the current phase."""
        steps_map = {
            PopulationPhase.NOT_STARTED: ["Upload file to start population"],
            PopulationPhase.PHASE1_BASIC: ["Wait for file upload completion", "Proceed to ETL processing"],
            PopulationPhase.PHASE1_COMPLETE: ["Start ETL processing", "Monitor ETL progress"],
            PopulationPhase.PHASE2_PROCESSING: ["Monitor ETL completion", "Validate extracted data"],
            PopulationPhase.PHASE2_COMPLETE: ["Registry fully populated", "Ready for use"],
            PopulationPhase.ERROR: ["Review error details", "Fix issues", "Restart population"]
        }
        
        return steps_map.get(current_phase, ["Unknown phase"])
    
    async def _rollback_to_phase(
        self,
        registry_id: str,
        target_phase: PopulationPhase
    ) -> Dict[str, Any]:
        """Rollback to a specific phase."""
        try:
            if target_phase == PopulationPhase.PHASE1_BASIC:
                # Rollback to basic registry state
                update_data = {
                    "integration_status": "pending",
                    "lifecycle_status": "created",
                    "overall_health_score": 0,
                    "health_status": "unknown",
                    "updated_at": datetime.now(timezone.utc)
                }
                
                success = await self.registry_repo.update(registry_id, update_data)
                
                if success:
                    return {
                        "success": True,
                        "message": f"Rolled back to {target_phase.value}",
                        "current_phase": target_phase.value
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to rollback registry status"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Rollback to {target_phase.value} not implemented"
                }
                
        except Exception as e:
            logger.error(f"Phase rollback failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup_failed_populations(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Clean up failed population attempts.
        
        Args:
            max_age_hours: Maximum age in hours for failed populations
            
        Returns:
            Dict containing cleanup results
        """
        try:
            logger.info(f"Cleaning up failed populations older than {max_age_hours} hours")
            
            # Find registries with error status
            failed_registries = await self._find_failed_registries()
            
            cleaned_count = 0
            for registry in failed_registries:
                # Check if registry is old enough to clean up
                if self._is_registry_old_enough(registry, max_age_hours):
                    success = await self.phase1_populator.rollback_basic_registry(registry.registry_id)
                    if success:
                        cleaned_count += 1
            
            return {
                "success": True,
                "cleaned_count": cleaned_count,
                "total_failed": len(failed_registries),
                "message": f"Cleaned up {cleaned_count} failed populations"
            }
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _find_failed_registries(self) -> List:
        """Find registries with failed status."""
        try:
            # This would query for registries with error status
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            logger.error(f"Failed to find failed registries: {e}")
            return []
    
    def _is_registry_old_enough(self, registry, max_age_hours: int) -> bool:
        """Check if registry is old enough to be cleaned up."""
        try:
            if not registry.updated_at:
                return False
            
            # Parse timestamp and check age
            if isinstance(registry.updated_at, str):
                updated_time = datetime.fromisoformat(registry.updated_at.replace('Z', '+00:00'))
            else:
                updated_time = registry.updated_at
            
            age_hours = (datetime.now(timezone.utc) - updated_time).total_seconds() / 3600
            return age_hours >= max_age_hours
            
        except Exception as e:
            logger.warning(f"Failed to check registry age: {e}")
            return False
