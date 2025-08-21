"""
Phase 1: Upload Population Handler

Handles the creation of basic twin registry entries immediately after file upload.
This phase creates minimal registry information that will be enhanced later
during ETL processing.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.twin_registry.repositories.twin_registry_repository import TwinRegistryRepository
from src.twin_registry.repositories.twin_registry_metrics_repository import TwinRegistryMetricsRepository

logger = logging.getLogger(__name__)


class Phase1UploadPopulator:
    """
    Handles Phase 1 population: File upload → Basic registry entry.
    
    Creates basic twin registry entries with minimal information
    immediately after file upload, before ETL processing begins.
    """
    
    def __init__(
        self,
        registry_repo: TwinRegistryRepository,
        metrics_repo: TwinRegistryMetricsRepository
    ):
        """Initialize Phase 1 upload populator."""
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        logger.info("Phase 1 Upload Populator initialized")
    
    async def create_basic_registry(
        self,
        file_id: str,
        file_name: str,
        user_id: str,
        org_id: str,
        file_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create basic twin registry entry after file upload.
        
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
            logger.info(f"Creating basic registry for file: {file_id} ({file_name})")
            
            # Generate twin and registry IDs
            twin_id = str(uuid.uuid4())
            registry_id = str(uuid.uuid4())
            
            # Extract file information
            file_extension = self._get_file_extension(file_name)
            twin_category = self._determine_twin_category(file_name, file_metadata)
            twin_type = self._determine_twin_type(file_extension, file_metadata)
            
            # Create basic registry data
            registry_data = {
                "registry_id": registry_id,
                "twin_id": twin_id,
                "twin_name": self._generate_twin_name(file_name, file_id),
                "registry_name": f"Registry_{file_id}",
                "twin_category": twin_category,
                "twin_type": twin_type,
                "twin_priority": "normal",
                "twin_version": "1.0.0",
                "registry_type": "extraction",  # Default to extraction for uploads
                "workflow_source": "aasx_file",
                "integration_status": "pending",  # Will be updated after ETL
                "overall_health_score": 0,  # No health data yet
                "health_status": "unknown",
                "lifecycle_status": "created",
                "lifecycle_phase": "development",
                "operational_status": "stopped",
                "availability_status": "offline",
                "sync_status": "pending",
                "sync_frequency": "manual",
                "performance_score": 0.0,
                "data_quality_score": 0.0,
                "reliability_score": 0.0,
                "compliance_score": 0.0,
                "security_level": "internal",
                "access_control_level": "user",
                "encryption_enabled": False,
                "audit_logging_enabled": True,
                "user_id": user_id,
                "org_id": org_id,
                "owner_team": None,
                "steward_user_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "activated_at": None,
                "last_accessed_at": None,
                "last_modified_at": None,
                "registry_config": self._create_basic_config(file_extension),
                "registry_metadata": self._create_basic_metadata(file_id, file_name, file_metadata),
                "custom_attributes": {},
                "tags": self._generate_basic_tags(file_name, file_extension),
                "relationships": [],
                "dependencies": [],
                "instances": []
            }
            
            # Create registry entry
            registry = await self.registry_repo.create(registry_data)
            
            # Create initial metrics entry
            await self._create_initial_metrics(registry_id)
            
            logger.info(f"Basic registry created successfully: {registry_id}")
            return registry_id
            
        except Exception as e:
            logger.error(f"Failed to create basic registry: {e}")
            raise
    
    async def update_upload_status(
        self,
        registry_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update the upload status for a registry.
        
        Args:
            registry_id: Registry identifier
            status: New status (uploading, uploaded, failed)
            error_message: Error message if status is failed
            
        Returns:
            bool: True if update successful
        """
        try:
            update_data = {
                "integration_status": status,
                "updated_at": datetime.now(timezone.utc)
            }
            
            if error_message:
                update_data["sync_error_message"] = error_message
                update_data["sync_error_count"] = 1
            
            # Update registry
            success = await self.registry_repo.update(registry_id, update_data)
            
            if success:
                logger.info(f"Updated upload status for registry {registry_id}: {status}")
            else:
                logger.warning(f"Failed to update upload status for registry {registry_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update upload status: {e}")
            return False
    
    async def mark_upload_complete(
        self,
        registry_id: str,
        upload_result: Dict[str, Any]
    ) -> bool:
        """
        Mark upload as complete and prepare for ETL processing.
        
        Args:
            registry_id: Registry identifier
            upload_result: Results from upload processing
            
        Returns:
            bool: True if marking successful
        """
        try:
            # Extract upload information
            file_size = upload_result.get("file_size", 0)
            upload_time = upload_result.get("upload_time", 0)
            file_hash = upload_result.get("file_hash", "")
            
            # Update registry with upload completion data
            update_data = {
                "integration_status": "uploaded",
                "sync_status": "completed",
                "last_sync_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "registry_metadata": {
                    "upload_completion_time": datetime.now(timezone.utc).isoformat(),
                    "file_size_bytes": file_size,
                    "upload_duration_ms": upload_time,
                    "file_hash": file_hash,
                    "upload_status": "success"
                }
            }
            
            success = await self.registry_repo.update(registry_id, update_data)
            
            if success:
                logger.info(f"Marked upload complete for registry: {registry_id}")
                # Update metrics
                await self._update_upload_metrics(registry_id, upload_result)
            else:
                logger.warning(f"Failed to mark upload complete for registry: {registry_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to mark upload complete: {e}")
            return False
    
    def _get_file_extension(self, file_name: str) -> str:
        """Extract file extension from filename."""
        try:
            return file_name.split('.')[-1].lower() if '.' in file_name else ""
        except Exception:
            return ""
    
    def _determine_twin_category(self, file_name: str, file_metadata: Optional[Dict[str, Any]]) -> str:
        """Determine twin category based on filename and metadata."""
        if file_metadata and "twin_category" in file_metadata:
            return file_metadata["twin_category"]
        
        # Simple heuristics based on filename
        file_lower = file_name.lower()
        
        if any(word in file_lower for word in ["manufacturing", "production", "factory"]):
            return "manufacturing"
        elif any(word in file_lower for word in ["energy", "power", "solar", "wind"]):
            return "energy"
        elif any(word in file_lower for word in ["component", "part", "assembly"]):
            return "component"
        elif any(word in file_lower for word in ["facility", "building", "plant"]):
            return "facility"
        elif any(word in file_lower for word in ["process", "workflow", "pipeline"]):
            return "process"
        else:
            return "generic"
    
    def _determine_twin_type(self, file_extension: str, file_metadata: Optional[Dict[str, Any]]) -> str:
        """Determine twin type based on file extension and metadata."""
        if file_metadata and "twin_type" in file_metadata:
            return file_metadata["twin_type"]
        
        # Default to physical for AASX files
        return "physical"
    
    def _generate_twin_name(self, file_name: str, file_id: str) -> str:
        """Generate a human-readable twin name."""
        # Remove file extension
        base_name = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
        
        # Clean up the name
        clean_name = base_name.replace('_', ' ').replace('-', ' ').title()
        
        # If name is too long, truncate and add ID
        if len(clean_name) > 50:
            clean_name = clean_name[:47] + "..."
        
        return clean_name or f"Twin_{file_id[:8]}"
    
    def _create_basic_config(self, file_extension: str) -> Dict[str, Any]:
        """Create basic registry configuration."""
        return {
            "file_type": file_extension,
            "processing_mode": "automatic",
            "quality_checks": True,
            "backup_enabled": True,
            "version_control": True
        }
    
    def _create_basic_metadata(
        self,
        file_id: str,
        file_name: str,
        file_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create basic registry metadata."""
        metadata = {
            "file_id": file_id,
            "file_name": file_name,
            "upload_timestamp": datetime.now(timezone.utc).isoformat(),
            "population_phase": "phase1_basic",
            "source": "file_upload"
        }
        
        if file_metadata:
            metadata.update(file_metadata)
        
        return metadata
    
    def _generate_basic_tags(self, file_name: str, file_extension: str) -> list:
        """Generate basic tags for the registry."""
        tags = ["upload", "pending_etl"]
        
        if file_extension:
            tags.append(f"file_type:{file_extension}")
        
        # Add tags based on filename patterns
        file_lower = file_name.lower()
        if "test" in file_lower:
            tags.append("test_data")
        if "production" in file_lower:
            tags.append("production")
        if "sample" in file_lower:
            tags.append("sample")
        
        return tags
    
    async def _create_initial_metrics(self, registry_id: str):
        """Create initial metrics entry for the registry with real system values."""
        try:
            # Import real calculation modules
            from src.twin_registry.utils.system_monitor import SystemMonitor
            from src.twin_registry.utils.metrics_calculator import MetricsCalculator
            
            # Initialize calculators
            system_monitor = SystemMonitor()
            metrics_calculator = MetricsCalculator()
            
            # Get real system metrics for initial state
            system_metrics = system_monitor.get_system_overview()
            
            # Calculate initial registry metrics
            initial_metrics = await metrics_calculator.calculate_registry_metrics(registry_id)
            
            metrics_data = {
                "registry_id": registry_id,
                "health_score": initial_metrics["health_score"],
                "response_time_ms": initial_metrics["response_time_ms"],
                "uptime_percentage": initial_metrics["uptime_percentage"],
                "error_rate": initial_metrics["error_rate"],
                "cpu_usage_percent": system_metrics.get("cpu", {}).get("usage_percent", 0.0),
                "memory_usage_percent": system_metrics.get("memory", {}).get("percent", 0.0),
                "network_throughput_mbps": system_metrics.get("network", {}).get("throughput_mbps", 0.0),
                "storage_usage_percent": system_metrics.get("storage", {}).get("percent", 0.0),
                "transaction_count": initial_metrics["transaction_count"],
                "data_volume_mb": initial_metrics["data_volume_mb"],
                "user_interaction_count": initial_metrics["user_interaction_count"]
            }
            
            await self.metrics_repo.create(metrics_data)
            logger.debug(f"Created initial metrics with real values for registry: {registry_id}")
            
        except Exception as e:
            logger.warning(f"Failed to create initial metrics: {e}")
            # Fallback to basic metrics if calculation fails
            await self._create_fallback_initial_metrics(registry_id)
    
    async def _create_fallback_initial_metrics(self, registry_id: str):
        """Create fallback initial metrics if real calculation fails."""
        try:
            fallback_metrics = {
                "registry_id": registry_id,
                "health_score": 0.0,  # Initial state
                "response_time_ms": 0.0,
                "uptime_percentage": 0.0,
                "error_rate": 0.0,
                "cpu_usage_percent": 0.0,
                "memory_usage_percent": 0.0,
                "network_throughput_mbps": 0.0,
                "storage_usage_percent": 0.0,
                "transaction_count": 0,
                "data_volume_mb": 0.0,
                "user_interaction_count": 0
            }
            
            await self.metrics_repo.create(fallback_metrics)
            logger.info(f"Created fallback initial metrics for registry: {registry_id}")
            
        except Exception as e:
            logger.error(f"Failed to create fallback initial metrics: {e}")
    
    async def _update_upload_metrics(self, registry_id: str, upload_result: Dict[str, Any]):
        """Update metrics with upload completion data."""
        try:
            # This would update the metrics table with upload-specific data
            # For now, just log the update
            logger.debug(f"Upload metrics update for registry: {registry_id}")
            
        except Exception as e:
            logger.warning(f"Failed to update upload metrics: {e}")
    
    async def rollback_basic_registry(self, registry_id: str) -> bool:
        """
        Rollback basic registry creation if upload fails.
        
        Args:
            registry_id: Registry identifier to rollback
            
        Returns:
            bool: True if rollback successful
        """
        try:
            logger.info(f"Rolling back basic registry: {registry_id}")
            
            # Delete the registry entry
            success = await self.registry_repo.delete(registry_id)
            
            if success:
                logger.info(f"Successfully rolled back registry: {registry_id}")
            else:
                logger.warning(f"Failed to rollback registry: {registry_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rollback basic registry: {e}")
            return False
