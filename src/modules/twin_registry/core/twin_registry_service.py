"""
Twin Registry Service

Main service for orchestrating twin registry operations.
Updated for Phase 3: Event System & Automation with pure async support.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from src.engine.database.connection_manager import ConnectionManager
from ..models.twin_registry import TwinRegistry, TwinRegistryQuery, create_twin_registry
from ..models.twin_lifecycle import TwinLifecycleEvent, LifecycleEventType, LifecycleStatusEnum
from ..repositories.twin_registry_repository import TwinRegistryRepository
from ..repositories.twin_relationship_repository import TwinRelationshipRepository
from ..repositories.twin_instance_repository import TwinInstanceRepository
from ..repositories.twin_lifecycle_repository import TwinLifecycleRepository
from ..events import TwinRegistryEventManager, EventType, EventPriority, TwinRegistryEvent
from ..integration import IntegrationCoordinator, FileUploadIntegrationConfig, ETLIntegrationConfig, AIRAGIntegrationConfig

logger = logging.getLogger(__name__)


class TwinRegistryService:
    """Main service for twin registry operations - Pure async implementation with Phase 3 complete"""
    
    def __init__(self):
        """Initialize the twin registry service"""
        # Use the new engine database infrastructure
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        # Initialize central database connection using engine
        self.connection_manager = ConnectionManager(db_path)
        
        # Initialize repositories with database connection
        self.registry_repo = TwinRegistryRepository(self.connection_manager)
        self.relationship_repo = TwinRelationshipRepository(self.connection_manager)
        self.instance_repo = TwinInstanceRepository(self.connection_manager)
        self.lifecycle_repo = TwinLifecycleRepository(self.connection_manager)
        
        # Initialize event manager for automation
        self.event_manager = TwinRegistryEventManager(self)
        
        # Initialize integration coordinator for external system integration
        self.integration_coordinator: Optional[IntegrationCoordinator] = None
        
        logger.info("Twin Registry Service initialized with Phase 3 capabilities")
    
    async def initialize(self) -> None:
        """Initialize the service with event-driven automation and integration"""
        try:
            # Initialize repositories
            await self.registry_repo.initialize()
            
            # Start the event manager for automation
            await self.event_manager.start()
            
            # Initialize integration coordinator with default configurations
            await self._initialize_integrations()
            
            logger.info("Twin Registry Service initialized successfully with Phase 3 complete")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Registry Service: {e}")
            raise
    
    async def _initialize_integrations(self) -> None:
        """Initialize integration components with default configurations"""
        try:
            # Create default configurations
            file_upload_config = FileUploadIntegrationConfig(
                database_path=Path("data/aasx_database.db"),
                watch_directory=Path("uploads"),
                enable_auto_population=True
            )
            
            etl_config = ETLIntegrationConfig(
                database_path=Path("data/aasx_database.db"),
                enable_auto_population=True
            )
            
            ai_rag_config = AIRAGIntegrationConfig(
                api_endpoint="http://localhost:8000/ai-rag",
                enable_auto_enhancement=True
            )
            
            # Initialize integration coordinator
            self.integration_coordinator = IntegrationCoordinator(
                self, 
                self.event_manager
            )
            
            await self.integration_coordinator.initialize_integrations(
                database_path=Path("data/aasx_database.db"),
                file_upload_config=file_upload_config,
                etl_config=etl_config,
                ai_rag_config=ai_rag_config
            )
            
            # Start all integrations
            await self.integration_coordinator.start_all_integrations()
            
            logger.info("Integration components initialized and started successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize integrations: {e}")
            # Don't fail the entire service if integrations fail
            logger.warning("Service will continue without integration capabilities")
    
    async def cleanup(self) -> None:
        """Cleanup resources and stop event manager and integrations."""
        try:
            # Stop integration coordinator
            if self.integration_coordinator:
                await self.integration_coordinator.cleanup()
            
            # Stop event manager
            if hasattr(self, 'event_manager'):
                await self.event_manager.stop()
                
            logger.info("Twin Registry Service cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to cleanup Twin Registry Service: {e}")
            raise
    
    # ==================== Twin Registration ====================
    
    async def register_twin(
        self, 
        twin_id: str, 
        registry_name: str, 
        registry_type: str = "extraction", 
        workflow_source: str = "aasx_file", 
        user_id: str = None, 
        org_id: str = None,
        dept_id: Optional[str] = None
    ) -> TwinRegistry:
        """Register a twin in the registry with pure async support"""
        try:
            # Create registry entry using our new pure async factory function
            registry = await create_twin_registry(
                twin_id=twin_id,
                twin_name=f"Twin_{twin_id}", # Placeholder, actual name might need to be fetched
                registry_name=registry_name,
                registry_type=registry_type,
                workflow_source=workflow_source,
                user_id=user_id or "system",
                org_id=org_id or "system",
                dept_id=dept_id  # Added dept_id for complete traceability
            )
            
            # Save to database
            await self.registry_repo.create_registry(registry)
            
            # Create initial lifecycle event
            event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.CREATED,
                event_data={"registry_name": registry_name, "registry_type": registry_type}
            )
            await self.lifecycle_repo.create_event(registry.registry_id, event)
            
            logger.info(f"Registered twin {twin_id} in registry")
            return registry
            
        except Exception as e:
            logger.error(f"Failed to register twin {twin_id}: {e}")
            raise
    
    async def unregister_twin(self, twin_id: str) -> bool:
        """Unregister a twin from the registry"""
        try:
            # Get registry entry first
            registry = await self.registry_repo.get_by_twin_id(twin_id)
            if not registry:
                logger.warning(f"Twin {twin_id} not found in registry")
                return False
            
            # Create deletion event
            event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.DELETED
            )
            await self.lifecycle_repo.create_event(registry.registry_id, event)
            
            # Update registry entry status using pure async method
            await registry.update_lifecycle_status("deprecated")
            await self.registry_repo.update_registry(registry)
            
            logger.info(f"Unregistered twin {twin_id} from registry")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister twin {twin_id}: {e}")
            raise
    
    # ==================== Twin Lifecycle Management ====================
    
    async def start_twin(self, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Start a twin"""
        try:
            # Get registry entry
            registry = await self.registry_repo.get_by_twin_id(twin_id)
            if not registry:
                raise ValueError(f"Twin {twin_id} not found in registry")
            
            # Create start event
            event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.STARTED,
                triggered_by=triggered_by
            )
            await self.lifecycle_repo.create_event(registry.registry_id, event)
            
            # Update lifecycle status using pure async method
            await registry.update_lifecycle_status("active")
            await registry.update_operational_status("running")
            await self.registry_repo.update_registry(registry)
            
            logger.info(f"Started twin {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start twin {twin_id}: {e}")
            raise
    
    async def stop_twin(self, twin_id: str, triggered_by: Optional[str] = None) -> bool:
        """Stop a twin"""
        try:
            # Get registry entry
            registry = await self.registry_repo.get_by_twin_id(twin_id)
            if not registry:
                raise ValueError(f"Twin {twin_id} not found in registry")
            
            # Create stop event
            event = TwinLifecycleEvent.create_event(
                twin_id=twin_id,
                event_type=LifecycleEventType.STOPPED,
                triggered_by=triggered_by
            )
            await self.lifecycle_repo.create_event(registry.registry_id, event)
            
            # Update lifecycle status using pure async method
            await registry.update_lifecycle_status("suspended")
            await registry.update_operational_status("stopped")
            await self.registry_repo.update_registry(registry)
            
            logger.info(f"Stopped twin {twin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop twin {twin_id}: {e}")
            raise
    
    # ==================== Registry Queries ====================
    
    async def get_registry_by_id(self, registry_id: str) -> Optional[TwinRegistry]:
        """Get registry entry by ID"""
        try:
            return await self.registry_repo.get_by_id(registry_id)
        except Exception as e:
            logger.error(f"Failed to get registry {registry_id}: {e}")
            return None
    
    async def get_registry_by_twin_id(self, twin_id: str) -> Optional[TwinRegistry]:
        """Get registry entry by twin ID"""
        try:
            return await self.registry_repo.get_by_twin_id(twin_id)
        except Exception as e:
            logger.error(f"Failed to get registry for twin {twin_id}: {e}")
            return None
    
    async def query_registries(self, query: TwinRegistryQuery) -> List[TwinRegistry]:
        """Query registries with filters"""
        try:
            return await self.registry_repo.query_registries(query)
        except Exception as e:
            logger.error(f"Failed to query registries: {e}")
            return []
    
    async def get_registry_summary(self) -> Dict[str, Any]:
        """Get registry statistics and summary"""
        try:
            # Get basic counts
            total_registries = await self.registry_repo.get_total_count()
            
            # Get counts by type
            extraction_count = await self.registry_repo.get_count_by_type("extraction")
            generation_count = await self.registry_repo.get_count_by_type("generation")
            hybrid_count = await self.registry_repo.get_count_by_type("hybrid")
            
            # Get counts by status
            active_count = await self.registry_repo.get_count_by_status("active")
            inactive_count = await self.registry_repo.get_count_by_status("inactive")
            error_count = await self.registry_repo.get_count_by_status("error")
            
            return {
                "total_registries": total_registries,
                "by_type": {
                    "extraction": extraction_count,
                    "generation": generation_count,
                    "hybrid": hybrid_count
                },
                "by_status": {
                    "active": active_count,
                    "inactive": inactive_count,
                    "error": error_count
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get registry summary: {e}")
            return {}
    
    # ==================== Health & Status Management ====================
    
    async def update_health_score(self, twin_id: str, health_score: int) -> bool:
        """Update health score for a twin using pure async method"""
        try:
            registry = await self.registry_repo.get_by_twin_id(twin_id)
            if not registry:
                raise ValueError(f"Twin {twin_id} not found in registry")
            
            # Use pure async method
            await registry.update_health_score(health_score)
            await self.registry_repo.update_registry(registry)
            
            logger.info(f"Updated health score for twin {twin_id} to {health_score}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update health score for twin {twin_id}: {e}")
            return False
    
    async def update_integration_status(self, twin_id: str, status: str) -> bool:
        """Update integration status for a twin using pure async method"""
        try:
            registry = await self.registry_repo.get_by_twin_id(twin_id)
            if not registry:
                raise ValueError(f"Twin {twin_id} not found in registry")
            
            # Use pure async method for integration status
            registry.integration_status = status
            await self.registry_repo.update_registry(registry)
            
            logger.info(f"Updated integration status for twin {twin_id} to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update integration status for twin {twin_id}: {e}")
            return False
    
    # ==================== Enhanced Query Methods ====================
    
    async def get_all_twins(self, page: int = 1, page_size: int = 10, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get all twins with pagination and filtering.
        This method provides the interface expected by the webapp service.
        
        Args:
            page: Page number for pagination
            page_size: Number of twins per page
            filters: Dictionary of filters to apply
            
        Returns:
            Dictionary with twins, pagination info, and statistics
        """
        try:
            logger.info(f"Getting all twins - page: {page}, size: {page_size}, filters: {filters}")
            
            # Build query from filters
            query = TwinRegistryQuery()
            if filters:
                if filters.get('twin_type'):
                    query.twin_type = filters['twin_type']
                if filters.get('status'):
                    query.integration_status = filters['status']
                if filters.get('project_id'):
                    # Note: project_id filtering would need to be implemented in repository
                    pass
            
            # Get registries with pagination
            registries = await self.registry_repo.query_registries(query)
            
            # Apply pagination
            total_count = len(registries)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_registries = registries[start_idx:end_idx]
            
            # Convert to dictionaries for webapp compatibility
            twins_data = []
            for registry in paginated_registries:
                twin_dict = registry.to_dict()
                twins_data.append(twin_dict)
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            
            return {
                "twins": twins_data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages
                },
                "statistics": {
                    "total_twins": total_count,
                    "active_twins": len([r for r in registries if r.integration_status == "active"]),
                    "error_twins": len([r for r in registries if r.integration_status == "error"])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get all twins: {e}")
            raise
    
    async def get_twin_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for all twins.
        This method provides the interface expected by the webapp service.
        
        Returns:
            Dictionary with twin statistics
        """
        try:
            logger.info("Getting twin statistics")
            
            # Get registry summary
            summary = await self.get_registry_summary()
            
            # Get additional statistics
            total_registries = summary.get("total_registries", 0)
            
            # Get status distribution
            status_distribution = summary.get("by_status", {})
            
            # Get type distribution
            type_distribution = summary.get("by_type", {})
            
            # Calculate health distribution (this would need health score data)
            health_distribution = {
                "healthy": 0,
                "warning": 0,
                "critical": 0,
                "unknown": 0
            }
            
            # Get all registries to calculate health distribution
            all_registries = await self.registry_repo.get_all()
            for registry in all_registries:
                if registry.overall_health_score >= 80:
                    health_distribution["healthy"] += 1
                elif registry.overall_health_score >= 50:
                    health_distribution["warning"] += 1
                elif registry.overall_health_score > 0:
                    health_distribution["critical"] += 1
                else:
                    health_distribution["unknown"] += 1
            
            return {
                "total_twins": total_registries,
                "active_count": status_distribution.get("active", 0),
                "error_count": status_distribution.get("error", 0),
                "status_distribution": status_distribution,
                "type_distribution": type_distribution,
                "health_distribution": health_distribution,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get twin statistics: {e}")
            raise
    
    async def get_twin_metrics(self, twin_id: str, time_range: str = "30d") -> List[Dict[str, Any]]:
        """
        Get metrics for a specific twin.
        This method provides the interface expected by the webapp service.
        
        Args:
            twin_id: The ID of the twin
            time_range: Time range for metrics (e.g., "7d", "30d", "90d")
            
        Returns:
            List of metrics dictionaries
        """
        try:
            logger.info(f"Getting metrics for twin {twin_id}, time range: {time_range}")
            
            # Get registry for the twin
            registry = await self.registry_repo.get_by_twin_id(twin_id)
            if not registry:
                logger.warning(f"Twin {twin_id} not found in registry")
                return []
            
            # For now, return basic metrics from registry
            # In a full implementation, this would query the metrics table
            metrics = [
                {
                    "metric_id": f"metric_{registry.registry_id}_001",
                    "registry_id": registry.registry_id,
                    "timestamp": datetime.now().isoformat(),
                    "health_score": registry.overall_health_score,
                    "response_time_ms": 150.0,  # Placeholder
                    "error_rate": 0.02,  # Placeholder
                    "note": "Basic metrics from registry - full metrics table integration pending"
                }
            ]
            
            logger.info(f"Retrieved {len(metrics)} metrics for twin {twin_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics for twin {twin_id}: {e}")
            raise
    
    async def get_all_metrics(self, time_range: str = "30d") -> List[Dict[str, Any]]:
        """
        Get all metrics across all twins.
        This method provides the interface expected by the webapp service.
        
        Args:
            time_range: Time range for metrics (e.g., "7d", "30d", "90d")
            
        Returns:
            List of metrics dictionaries
        """
        try:
            logger.info(f"Getting all metrics, time range: {time_range}")
            
            # Get all registries
            all_registries = await self.registry_repo.get_all()
            
            # For now, return basic metrics from registries
            # In a full implementation, this would query the metrics table
            all_metrics = []
            for registry in all_registries:
                metric = {
                    "metric_id": f"metric_{registry.registry_id}_001",
                    "registry_id": registry.registry_id,
                    "twin_name": registry.twin_name,
                    "registry_type": registry.registry_type,
                    "timestamp": datetime.now().isoformat(),
                    "health_score": registry.overall_health_score,
                    "response_time_ms": 150.0,  # Placeholder
                    "error_rate": 0.02,  # Placeholder
                    "note": "Basic metrics from registry - full metrics table integration pending"
                }
                all_metrics.append(metric)
            
            logger.info(f"Retrieved {len(all_metrics)} metrics from all registries")
            return all_metrics
            
        except Exception as e:
            logger.error(f"Failed to get all metrics: {e}")
            raise
    
    async def get_twin_by_id(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific twin by ID.
        This method provides the interface expected by the webapp service.
        
        Args:
            twin_id: The ID of the twin to retrieve
            
        Returns:
            Twin dictionary or None if not found
        """
        try:
            logger.info(f"Getting twin by ID: {twin_id}")
            
            # Get registry for the twin
            registry = await self.registry_repo.get_by_twin_id(twin_id)
            if not registry:
                logger.warning(f"Twin {twin_id} not found in registry")
                return None
            
            # Convert to dictionary for webapp compatibility
            twin_dict = registry.to_dict()
            
            logger.info(f"Retrieved twin {twin_id} successfully")
            return twin_dict
            
        except Exception as e:
            logger.error(f"Failed to get twin {twin_id}: {e}")
            raise
    
    async def search_twins(self, query: str, filters: Dict[str, Any] = None, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Search twins by query string and filters.
        This method provides the interface expected by the webapp service.
        
        Args:
            query: Search query string
            filters: Dictionary of filters to apply
            page: Page number for pagination
            page_size: Number of twins per page
            
        Returns:
            Dictionary with search results, pagination info, and statistics
        """
        try:
            logger.info(f"Searching twins with query: '{query}', filters: {filters}, page: {page}, size: {page_size}")
            
            # Build query from filters
            registry_query = TwinRegistryQuery()
            if filters:
                if filters.get('twin_type'):
                    registry_query.twin_type = filters['twin_type']
                if filters.get('status'):
                    registry_query.integration_status = filters['status']
                if filters.get('project_id'):
                    # Note: project_id filtering would need to be implemented in repository
                    pass
            
            # Get all registries and filter by search query
            all_registries = await self.registry_repo.query_registries(registry_query)
            
            # Apply text search (simple string matching for now)
            search_results = []
            for registry in all_registries:
                # Search in twin_name, registry_name, and other text fields
                searchable_text = f"{registry.twin_name} {registry.registry_name} {registry.registry_type}".lower()
                if query.lower() in searchable_text:
                    search_results.append(registry)
            
            # Apply pagination
            total_count = len(search_results)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_results = search_results[start_idx:end_idx]
            
            # Convert to dictionaries for webapp compatibility
            twins_data = []
            for registry in paginated_results:
                twin_dict = registry.to_dict()
                twins_data.append(twin_dict)
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            
            return {
                "twins": twins_data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages
                },
                "search_info": {
                    "query": query,
                    "filters": filters,
                    "results_count": total_count
                },
                "statistics": {
                    "total_twins": total_count,
                    "active_twins": len([r for r in search_results if r.integration_status == "active"]),
                    "error_twins": len([r for r in search_results if r.integration_status == "error"])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to search twins: {e}")
            raise
    
    # ==================== Event-Driven Automation ====================
    
    async def trigger_file_upload_event(
        self,
        file_id: str,
        file_name: str,
        file_type: str,
        project_id: Optional[str] = None,
        processed_by: Optional[str] = None,
        org_id: Optional[str] = None,
        dept_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Trigger a file upload event to automatically create a twin.
        This is the main entry point for automatic twin creation.
        """
        try:
            logger.info(f"Triggering file upload event for file {file_id}")
            
            # Create and emit the event
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
            
            await self.event_manager.emit_event(event)
            logger.info(f"File upload event triggered for file {file_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger file upload event for file {file_id}: {e}")
            raise
    
    async def trigger_etl_success_event(
        self,
        twin_id: str,
        processing_time: float,
        records_processed: int,
        success_rate: float = 1.0,
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Trigger an ETL success event to automatically create metrics.
        This is the main entry point for automatic metrics creation.
        """
        try:
            logger.info(f"Triggering ETL success event for twin {twin_id}")
            
            # Create and emit the event
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
            
            await self.event_manager.emit_event(event)
            logger.info(f"ETL success event triggered for twin {twin_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger ETL success event for twin {twin_id}: {e}")
            raise
    
    async def trigger_etl_failure_event(
        self,
        twin_id: str,
        error_message: str,
        failure_reason: str = "etl_failure",
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Trigger an ETL failure event to update twin status.
        This is the main entry point for automatic status updates on failure.
        """
        try:
            logger.info(f"Triggering ETL failure event for twin {twin_id}")
            
            # Create and emit the event
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
            
            await self.event_manager.emit_event(event)
            logger.info(f"ETL failure event triggered for twin {twin_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger ETL failure event for twin {twin_id}: {e}")
            raise
    
    async def get_event_manager_status(self) -> Dict[str, Any]:
        """Get the current status of the event manager."""
        try:
            return {
                "is_running": self.event_manager.is_running,
                "queue_size": self.event_manager.event_queue.qsize(),
                "registered_handlers": {
                    event_type.value: len(handlers) 
                    for event_type, handlers in self.event_manager.handlers.items()
                }
            }
        except Exception as e:
            logger.error(f"Failed to get event manager status: {e}")
            return {"error": str(e)}
    
    # ==================== Integration Management ====================
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get the current status of all integration components."""
        try:
            if not self.integration_coordinator:
                return {"error": "Integration coordinator not initialized"}
            
            return await self.integration_coordinator.get_coordinator_status()
            
        except Exception as e:
            logger.error(f"Failed to get integration status: {e}")
            return {"error": str(e)}
    
    async def get_integration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all integration components."""
        try:
            if not self.integration_coordinator:
                return {"error": "Integration coordinator not initialized"}
            
            return await self.integration_coordinator.get_integration_metrics()
            
        except Exception as e:
            logger.error(f"Failed to get integration metrics: {e}")
            return {"error": str(e)}
    
    async def trigger_integrated_workflow(
        self,
        workflow_type: str,
        **workflow_params
    ) -> Dict[str, Any]:
        """Trigger an integrated workflow across all integration components."""
        try:
            if not self.integration_coordinator:
                return {"error": "Integration coordinator not initialized"}
            
            if workflow_type == "file_upload":
                # Trigger file upload workflow
                await self.integration_coordinator.trigger_file_upload_workflow(
                    file_id=workflow_params.get("file_id"),
                    file_name=workflow_params.get("file_name"),
                    file_type=workflow_params.get("file_type"),
                    user_id=workflow_params.get("user_id"),
                    org_id=workflow_params.get("org_id"),
                    dept_id=workflow_params.get("dept_id"),
                    project_id=workflow_params.get("project_id")
                )
                return {"status": "success", "workflow": "file_upload", "message": "Workflow triggered successfully"}
            
            else:
                return {"error": f"Unknown workflow type: {workflow_type}"}
                
        except Exception as e:
            logger.error(f"Failed to trigger integrated workflow: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get comprehensive health status of the entire service."""
        try:
            health_status = {
                "service": "Twin Registry Service",
                "version": "3.3.0",
                "phase": "Phase 3 Complete - Event System & Automation",
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy"
            }
            
            # Check event manager health
            try:
                event_status = await self.get_event_manager_status()
                health_status["event_manager"] = event_status
                if event_status.get("error"):
                    health_status["overall_status"] = "degraded"
            except Exception as e:
                health_status["event_manager"] = {"error": str(e)}
                health_status["overall_status"] = "degraded"
            
            # Check integration health
            try:
                integration_status = await self.get_integration_status()
                health_status["integrations"] = integration_status
                if integration_status.get("overall_health") == "critical":
                    health_status["overall_status"] = "critical"
                elif integration_status.get("overall_health") == "degraded" and health_status["overall_status"] != "critical":
                    health_status["overall_status"] = "degraded"
            except Exception as e:
                health_status["integrations"] = {"error": str(e)}
                health_status["overall_status"] = "degraded"
            
            # Check database connectivity
            try:
                # Simple database connectivity check
                await self.registry_repo.get_total_count()
                health_status["database"] = {"status": "healthy", "connected": True}
            except Exception as e:
                health_status["database"] = {"status": "error", "connected": False, "error": str(e)}
                health_status["overall_status"] = "critical"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Failed to perform health check: {e}")
            return {
                "service": "Twin Registry Service",
                "version": "3.3.0",
                "phase": "Phase 3 Complete - Event System & Automation",
                "timestamp": datetime.now().isoformat(),
                "overall_status": "unknown",
                "error": str(e)
            } 