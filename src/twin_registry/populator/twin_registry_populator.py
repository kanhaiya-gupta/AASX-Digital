"""
Main Twin Registry Population Orchestrator

This is the central coordinator for all twin registry population activities.
It orchestrates the two-phase population process and manages the overall
population workflow.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path

from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from src.twin_registry.repositories.twin_registry_repository import TwinRegistryRepository
from src.twin_registry.repositories.twin_registry_metrics_repository import TwinRegistryMetricsRepository

from .phase1_upload_populator import Phase1UploadPopulator
from .phase2_etl_populator import Phase2ETLPopulator
from .population_coordinator import PopulationCoordinator
from .population_validator import PopulationValidator

logger = logging.getLogger(__name__)


class TwinRegistryPopulator:
    """
    Main orchestrator for twin registry population.
    
    Coordinates between:
    - Phase 1: File upload → Basic registry entry
    - Phase 2: ETL completion → Enhanced registry data
    - Validation and quality checks
    - Event coordination
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the population orchestrator."""
        if db_path is None:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "aasx_database.db"
        
        # Initialize database connection
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        
        # Initialize repositories
        self.registry_repo = TwinRegistryRepository(self.db_manager)
        self.metrics_repo = TwinRegistryMetricsRepository(self.db_manager)
        
        # Initialize population components
        self.phase1_populator = Phase1UploadPopulator(self.registry_repo, self.metrics_repo)
        self.phase2_populator = Phase2ETLPopulator(self.registry_repo, self.metrics_repo)
        self.coordinator = PopulationCoordinator(self.registry_repo, self.metrics_repo)
        self.validator = PopulationValidator()
        
        logger.info("Twin Registry Populator initialized successfully")
    
    async def create_basic_registry_from_upload(
        self,
        file_id: str,
        file_name: str,
        user_id: str,
        org_id: str,
        file_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Phase 1: Create basic twin registry entry after file upload.
        
        Args:
            file_id: Unique identifier for the uploaded file
            file_name: Name of the uploaded file
            user_id: ID of the user who uploaded the file
            org_id: Organization ID of the user
            file_metadata: Additional file metadata
            
        Returns:
            registry_id: The created registry ID
        """
        try:
            logger.info(f"Creating basic registry entry for file: {file_id}")
            
            # Create basic registry entry
            registry_id = await self.phase1_populator.create_basic_registry(
                file_id=file_id,
                file_name=file_name,
                user_id=user_id,
                org_id=org_id,
                file_metadata=file_metadata or {}
            )
            
            logger.info(f"Basic registry entry created successfully: {registry_id}")
            return registry_id
            
        except Exception as e:
            logger.error(f"Failed to create basic registry entry: {e}")
            raise
    
    async def enhance_registry_from_etl(
        self,
        job_id: str,
        etl_result: Dict[str, Any],
        registry_id: Optional[str] = None
    ) -> bool:
        """
        Phase 2: Enhance registry data after ETL completion.
        
        Args:
            job_id: ETL job identifier
            etl_result: Results from ETL processing
            registry_id: Optional registry ID if already known
            
        Returns:
            bool: True if enhancement successful
        """
        try:
            logger.info(f"Enhancing registry data for ETL job: {job_id}")
            
            # Find registry if not provided
            if not registry_id:
                registry_id = await self._find_registry_by_job_id(job_id)
            
            if not registry_id:
                logger.warning(f"No registry found for job ID: {job_id}")
                return False
            
            # Enhance registry with ETL data
            success = await self.phase2_populator.enhance_registry(
                registry_id=registry_id,
                job_id=job_id,
                etl_result=etl_result
            )
            
            if success:
                logger.info(f"Registry enhanced successfully for job: {job_id}")
            else:
                logger.warning(f"Registry enhancement failed for job: {job_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to enhance registry from ETL: {e}")
            raise
    
    async def populate_from_etl(
        self,
        job_id: str,
        etl_result: Dict[str, Any]
    ) -> bool:
        """
        Complete ETL-based population workflow.
        
        This method handles the complete flow from ETL completion
        to registry enhancement, including validation and metrics.
        
        Args:
            job_id: ETL job identifier
            etl_result: Results from ETL processing
            
        Returns:
            bool: True if population successful
        """
        try:
            logger.info(f"Starting complete ETL population for job: {job_id}")
            
            # Find or create registry entry
            registry_id = await self._find_registry_by_job_id(job_id)
            
            if not registry_id:
                # Create new registry entry if none exists
                registry_id = await self._create_registry_from_etl(job_id, etl_result)
            
            # Enhance with ETL data
            success = await self.enhance_registry_from_etl(job_id, etl_result, registry_id)
            
            if success:
                # Update metrics
                await self._update_population_metrics(registry_id, "etl_complete")
                logger.info(f"ETL population completed successfully for job: {job_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"ETL population failed for job {job_id}: {e}")
            raise
    
    async def get_population_status(self, registry_id: str) -> Dict[str, Any]:
        """
        Get the current population status for a registry.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            Dict containing population status information
        """
        try:
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                return {"error": "Registry not found"}
            
            # Get metrics
            metrics = await self.metrics_repo.get_latest_by_registry_id(registry_id)
            
            status = {
                "registry_id": registry_id,
                "twin_name": registry.twin_name,
                "registry_type": registry.registry_type,
                "workflow_source": registry.workflow_source,
                "integration_status": registry.integration_status,
                "lifecycle_status": registry.lifecycle_status,
                "overall_health_score": registry.overall_health_score,
                "population_phase": self._determine_population_phase(registry),
                "last_updated": registry.updated_at,
                "metrics": metrics.to_dict() if metrics else {}
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get population status: {e}")
            return {"error": str(e)}
    
    async def _find_registry_by_job_id(self, job_id: str) -> Optional[str]:
        """Find registry ID by AASX integration ID."""
        try:
            # Search for registry with matching job ID
            registries = await self.registry_repo.search(
                filters={"aasx_integration_id": job_id}
            )
            
            if registries:
                return registries[0].registry_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find registry by job ID {job_id}: {e}")
            return None
    
    async def _create_registry_from_etl(
        self,
        job_id: str,
        etl_result: Dict[str, Any]
    ) -> str:
        """Create new registry entry from ETL results."""
        try:
            # Extract basic information from ETL result
            twin_name = etl_result.get("twin_name", f"Twin_{job_id}")
            registry_type = etl_result.get("registry_type", "extraction")
            workflow_source = etl_result.get("workflow_source", "aasx_file")
            
            # Create basic registry entry
            registry_data = {
                "twin_name": twin_name,
                "registry_name": f"Registry_{twin_name}",
                "registry_type": registry_type,
                "workflow_source": workflow_source,
                "aasx_integration_id": job_id,
                "integration_status": "active",
                "lifecycle_status": "active",
                "overall_health_score": 85,  # Default health score
                "health_status": "healthy",
                "user_id": etl_result.get("user_id", "system"),
                "org_id": etl_result.get("org_id", "default"),
                "twin_category": "generic",
                "twin_type": "physical",
                "twin_priority": "normal",
                "twin_version": "1.0.0"
            }
            
            registry = await self.registry_repo.create(registry_data)
            logger.info(f"Created new registry from ETL: {registry.registry_id}")
            
            return registry.registry_id
            
        except Exception as e:
            logger.error(f"Failed to create registry from ETL: {e}")
            raise
    
    async def _update_population_metrics(self, registry_id: str, event_type: str):
        """Update population metrics with real calculated values."""
        try:
            # Import real calculation modules
            from src.twin_registry.utils.system_monitor import SystemMonitor
            from src.twin_registry.utils.metrics_calculator import MetricsCalculator
            
            # Initialize calculators
            system_monitor = SystemMonitor()
            metrics_calculator = MetricsCalculator()
            
            # Calculate real metrics
            real_metrics = await metrics_calculator.calculate_registry_metrics(registry_id)
            
            # Get real system metrics
            system_metrics = system_monitor.get_system_overview()
            
            metrics_data = {
                "registry_id": registry_id,
                "health_score": real_metrics["health_score"],
                "response_time_ms": real_metrics["response_time_ms"],
                "uptime_percentage": real_metrics["uptime_percentage"],
                "error_rate": real_metrics["error_rate"],
                "cpu_usage_percent": system_metrics.get("cpu", {}).get("usage_percent", 0.0),
                "memory_usage_percent": system_metrics.get("memory", {}).get("percent", 0.0),
                "network_throughput_mbps": system_metrics.get("network", {}).get("throughput_mbps", 0.0),
                "storage_usage_percent": system_metrics.get("storage", {}).get("percent", 0.0),
                "transaction_count": real_metrics["transaction_count"],
                "data_volume_mb": real_metrics["data_volume_mb"],
                "user_interaction_count": real_metrics["user_interaction_count"]
            }
            
            await self.metrics_repo.create(metrics_data)
            logger.debug(f"Updated population metrics with real values for registry: {registry_id}")
            
        except Exception as e:
            logger.warning(f"Failed to update population metrics: {e}")
            # Fallback to basic metrics if calculation fails
            await self._create_fallback_metrics(registry_id)
    
    async def _create_fallback_metrics(self, registry_id: str):
        """Create fallback metrics if real calculation fails."""
        try:
            fallback_metrics = {
                "registry_id": registry_id,
                "health_score": 50.0,  # Default neutral score
                "response_time_ms": 0.0,
                "uptime_percentage": 0.0,
                "error_rate": 0.0,
                "cpu_usage_percent": 0.0,
                "memory_usage_percent": 0.0,
                "network_throughput_mbps": 0.0,
                "storage_usage_percent": 0.0,
                "transaction_count": 1,
                "data_volume_mb": 0.0,
                "user_interaction_count": 1
            }
            
            await self.metrics_repo.create(fallback_metrics)
            logger.info(f"Created fallback metrics for registry: {registry_id}")
            
        except Exception as e:
            logger.error(f"Failed to create fallback metrics: {e}")
    
    def _determine_population_phase(self, registry) -> str:
        """Determine the current population phase for a registry."""
        if registry.integration_status == "pending":
            return "phase1_basic"
        elif registry.integration_status == "active":
            return "phase2_enhanced"
        elif registry.integration_status == "error":
            return "error"
        else:
            return "unknown"
    
    async def cleanup_failed_populations(self, max_age_hours: int = 24) -> int:
        """
        Clean up failed population attempts older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours for failed populations
            
        Returns:
            int: Number of cleaned up entries
        """
        try:
            # Find registries with failed status older than max_age_hours
            cutoff_time = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
            
            # This would require additional repository methods for cleanup
            # For now, return 0 as placeholder
            logger.info("Cleanup functionality not yet implemented")
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup failed populations: {e}")
            return 0
