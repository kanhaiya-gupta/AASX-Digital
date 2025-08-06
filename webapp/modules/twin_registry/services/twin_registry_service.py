"""
Twin Registry Service
====================

Core service for twin registry operations following AASX module pattern.
Handles CRUD operations, pagination, and twin lifecycle management.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import shared services and repositories
from src.shared.services.digital_twin_service import DigitalTwinService
from src.federated_learning.core.federated_learning_service import FederatedLearningService
from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository
from src.shared.models.digital_twin import DigitalTwin

# Import core Twin Registry services
try:
    from src.twin_registry.core.twin_relationship_service import TwinRelationshipService
    from src.twin_registry.core.twin_instance_service import TwinInstanceService
    from src.twin_registry.core.twin_sync_service import TwinSyncService
    print("✅ Twin Registry core services imported successfully")
    CORE_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Twin Registry core services not available: {e}")
    CORE_SERVICES_AVAILABLE = False
    # Set to None for fallback
    TwinRelationshipService = None
    TwinInstanceService = None
    TwinSyncService = None

logger = logging.getLogger(__name__)

class TwinRegistryService:
    """
    Core twin registry service for managing digital twins.
    Follows the same pattern as AASX module services.
    Integrates with new core services for advanced functionality.
    """
    
    def __init__(self, db_manager):
        """Initialize the twin registry service with database manager."""
        self.db_manager = db_manager
        
        # Initialize repositories
        self.twin_repo = DigitalTwinRepository(db_manager)
        self.file_repo = FileRepository(db_manager)
        self.project_repo = ProjectRepository(db_manager)
        
        # Initialize shared services
        self.twin_service = DigitalTwinService(db_manager, self.file_repo, self.project_repo)
        self.fl_service = FederatedLearningService(self.twin_service)
        
        # Core services will be initialized in the future
        # For now, we use shared services only
        
        logger.info("Twin Registry Service initialized with core services")
    
    async def initialize(self) -> None:
        """Initialize all core services"""
        try:
            await self.core_registry_service.initialize()
            await self.lifecycle_service.initialize()
            await self.relationship_service.initialize()
            await self.instance_service.initialize()
            logger.info("All core services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize core services: {e}")
            raise
    
    async def get_all_twins(self, page: int = 1, page_size: int = 10, 
                           twin_type: str = "", status: str = "", 
                           project_id: str = None) -> Dict[str, Any]:
        """
        Get all twins with pagination and filtering.
        
        Args:
            page: Page number for pagination
            page_size: Number of twins per page
            twin_type: Filter by twin type
            status: Filter by twin status
            project_id: Filter by project ID
            
        Returns:
            Dictionary with twins, pagination info, and statistics
        """
        try:
            logger.info(f"Getting twins - page: {page}, size: {page_size}")
            
            # Get all twins from repository
            all_twins = self.twin_repo.get_all()
            logger.info(f"Found {len(all_twins)} total twins in database")
            
            # Apply filters
            filtered_twins = []
            for twin in all_twins:
                # Type filter
                if twin_type and getattr(twin, 'twin_type', '') != twin_type:
                    continue
                
                # Status filter
                if status and getattr(twin, 'status', '') != status:
                    continue
                
                # Project filter
                if project_id and getattr(twin, 'project_id', '') != project_id:
                    continue
                
                filtered_twins.append(twin)
            
            # Apply pagination
            total_count = len(filtered_twins)
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paginated_twins = filtered_twins[start_index:end_index]
            
            # Convert to dictionaries
            twin_dicts = []
            for twin in paginated_twins:
                twin_dict = self._convert_twin_to_dict(twin)
                
                # Add default lifecycle information
                twin_dict['lifecycle_status'] = 'unknown'
                twin_dict['last_lifecycle_update'] = None
                
                twin_dicts.append(twin_dict)
            
            # Calculate statistics
            active_count = len([t for t in filtered_twins if getattr(t, 'status', 'active') == 'active'])
            error_count = len([t for t in filtered_twins if getattr(t, 'status', 'error') == 'error'])
            
            result = {
                "twins": twin_dicts,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                },
                "statistics": {
                    "total_twins": total_count,
                    "active_twins": active_count,
                    "error_twins": error_count
                }
            }
            
            logger.info(f"Retrieved {len(twin_dicts)} twins out of {total_count} total")
            return result
            
        except Exception as e:
            logger.error(f"Error getting twins: {e}")
            raise
    
    async def get_twin_by_id(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific twin by ID with detailed information.
        
        Args:
            twin_id: The ID of the twin to retrieve
            
        Returns:
            Dictionary with twin information and lifecycle details
        """
        try:
            logger.info(f"Getting twin by ID: {twin_id}")
            
            # Get basic twin information
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                logger.warning(f"Twin {twin_id} not found")
                return None
            
            twin_dict = self._convert_twin_to_dict(twin)
            
            # Add lifecycle information
            try:
                lifecycle_status = await self.lifecycle_service.get_status(twin_id)
                if lifecycle_status:
                    twin_dict['lifecycle_status'] = lifecycle_status.current_status.value
                    twin_dict['last_lifecycle_update'] = lifecycle_status.last_updated.isoformat()
                    twin_dict['lifecycle_metadata'] = lifecycle_status.lifecycle_metadata
                else:
                    twin_dict['lifecycle_status'] = 'unknown'
                    twin_dict['last_lifecycle_update'] = None
                    twin_dict['lifecycle_metadata'] = {}
            except Exception as e:
                logger.warning(f"Failed to get lifecycle status for twin {twin_id}: {e}")
                twin_dict['lifecycle_status'] = 'unknown'
                twin_dict['last_lifecycle_update'] = None
                twin_dict['lifecycle_metadata'] = {}
            
            # Add health information
            try:
                health_info = await self.lifecycle_service.get_twin_health(twin_id)
                twin_dict['health_info'] = health_info
            except Exception as e:
                logger.warning(f"Failed to get health info for twin {twin_id}: {e}")
                twin_dict['health_info'] = {
                    "twin_id": twin_id,
                    "health_score": 0,
                    "error_count": 0,
                    "current_status": "unknown"
                }
            
            # Add relationships
            try:
                relationships = await self.relationship_service.get_twin_relationships(twin_id)
                twin_dict['relationships'] = [rel.dict() for rel in relationships]
            except Exception as e:
                logger.warning(f"Failed to get relationships for twin {twin_id}: {e}")
                twin_dict['relationships'] = []
            
            # Add instances
            try:
                instances = await self.instance_service.get_twin_instances(twin_id)
                twin_dict['instances'] = [inst.dict() for inst in instances]
            except Exception as e:
                logger.warning(f"Failed to get instances for twin {twin_id}: {e}")
                twin_dict['instances'] = []
            
            logger.info(f"Retrieved twin {twin_id} with detailed information")
            return twin_dict
            
        except Exception as e:
            logger.error(f"Error getting twin {twin_id}: {e}")
            raise
    
    # ==================== Lifecycle Management ====================
    
    async def start_twin(self, twin_id: str, triggered_by: Optional[str] = None) -> Dict[str, Any]:
        """Start a twin"""
        try:
            logger.info(f"Starting twin {twin_id}")
            
            # Use core lifecycle service
            success = await self.lifecycle_service.start_twin(twin_id, triggered_by)
            
            if success:
                # Get updated twin information
                twin_info = await self.get_twin_by_id(twin_id)
                return {
                    "success": True,
                    "message": f"Twin {twin_id} started successfully",
                    "twin": twin_info
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to start twin {twin_id}"
                }
                
        except Exception as e:
            logger.error(f"Error starting twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error starting twin {twin_id}: {str(e)}"
            }
    
    async def stop_twin(self, twin_id: str, triggered_by: Optional[str] = None) -> Dict[str, Any]:
        """Stop a twin"""
        try:
            logger.info(f"Stopping twin {twin_id}")
            
            # Use core lifecycle service
            success = await self.lifecycle_service.stop_twin(twin_id, triggered_by)
            
            if success:
                # Get updated twin information
                twin_info = await self.get_twin_by_id(twin_id)
                return {
                    "success": True,
                    "message": f"Twin {twin_id} stopped successfully",
                    "twin": twin_info
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to stop twin {twin_id}"
                }
                
        except Exception as e:
            logger.error(f"Error stopping twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error stopping twin {twin_id}: {str(e)}"
            }
    
    async def sync_twin(self, twin_id: str, sync_data: Optional[Dict[str, Any]] = None, triggered_by: Optional[str] = None) -> Dict[str, Any]:
        """Sync a twin"""
        try:
            logger.info(f"Syncing twin {twin_id}")
            
            # Use core lifecycle service
            success = await self.lifecycle_service.sync_twin(twin_id, sync_data, triggered_by)
            
            if success:
                # Get updated twin information
                twin_info = await self.get_twin_by_id(twin_id)
                return {
                    "success": True,
                    "message": f"Twin {twin_id} synced successfully",
                    "twin": twin_info
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to sync twin {twin_id}"
                }
                
        except Exception as e:
            logger.error(f"Error syncing twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error syncing twin {twin_id}: {str(e)}"
            }
    
    # ==================== Relationship Management ====================
    
    async def create_relationship(
        self,
        source_twin_id: str,
        target_twin_id: str,
        relationship_type: str,
        relationship_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a relationship between twins"""
        try:
            logger.info(f"Creating relationship between {source_twin_id} and {target_twin_id}")
            
            # Use core relationship service
            relationship = await self.relationship_service.create_relationship(
                source_twin_id, target_twin_id, relationship_type, relationship_data
            )
            
            return {
                "success": True,
                "message": "Relationship created successfully",
                "relationship": relationship.dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return {
                "success": False,
                "message": f"Error creating relationship: {str(e)}"
            }
    
    async def get_twin_relationships(self, twin_id: str) -> Dict[str, Any]:
        """Get all relationships for a twin"""
        try:
            logger.info(f"Getting relationships for twin {twin_id}")
            
            # Use core relationship service
            relationships = await self.relationship_service.get_twin_relationships(twin_id)
            
            return {
                "success": True,
                "relationships": [rel.dict() for rel in relationships],
                "count": len(relationships)
            }
            
        except Exception as e:
            logger.error(f"Error getting relationships for twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error getting relationships: {str(e)}",
                "relationships": [],
                "count": 0
            }
    
    # ==================== Instance Management ====================
    
    async def create_instance(
        self,
        twin_id: str,
        instance_data: Dict[str, Any],
        instance_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new instance of a twin"""
        try:
            logger.info(f"Creating instance for twin {twin_id}")
            
            # Use core instance service
            instance = await self.instance_service.create_instance(
                twin_id, instance_data, instance_metadata, created_by
            )
            
            return {
                "success": True,
                "message": "Instance created successfully",
                "instance": instance.dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating instance for twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error creating instance: {str(e)}"
            }
    
    async def get_twin_instances(self, twin_id: str) -> Dict[str, Any]:
        """Get all instances of a twin"""
        try:
            logger.info(f"Getting instances for twin {twin_id}")
            
            # Use core instance service
            instances = await self.instance_service.get_twin_instances(twin_id)
            
            return {
                "success": True,
                "instances": [inst.dict() for inst in instances],
                "count": len(instances)
            }
            
        except Exception as e:
            logger.error(f"Error getting instances for twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error getting instances: {str(e)}",
                "instances": [],
                "count": 0
            }
    
    # ==================== Registry Analytics ====================
    
    async def get_registry_summary(self) -> Dict[str, Any]:
        """Get comprehensive registry summary"""
        try:
            logger.info("Getting registry summary")
            
            # Use core registry service
            summary = await self.core_registry_service.get_registry_summary()
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error getting registry summary: {e}")
            return {
                "success": False,
                "message": f"Error getting registry summary: {str(e)}",
                "summary": {}
            }
    
    # ==================== Existing Methods (Kept for Compatibility) ====================
    
    async def create_twin(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new twin (existing functionality)"""
        try:
            logger.info("Creating new twin")
            
            # Use existing twin service
            twin = await self.twin_service.create_digital_twin(twin_data)
            
            # Register in core registry
            try:
                await self.core_registry_service.register_twin(
                    twin.twin_id,
                    twin_data.get('name', f"Twin-{twin.twin_id}"),
                    "aasx"
                )
            except Exception as e:
                logger.warning(f"Failed to register twin in core registry: {e}")
            
            return {
                "success": True,
                "message": "Twin created successfully",
                "twin": self._convert_twin_to_dict(twin)
            }
            
        except Exception as e:
            logger.error(f"Error creating twin: {e}")
            return {
                "success": False,
                "message": f"Error creating twin: {str(e)}"
            }
    
    async def update_twin(self, twin_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a twin (existing functionality)"""
        try:
            logger.info(f"Updating twin {twin_id}")
            
            # Use existing twin service
            twin = await self.twin_service.update_digital_twin(twin_id, update_data)
            
            return {
                "success": True,
                "message": "Twin updated successfully",
                "twin": self._convert_twin_to_dict(twin)
            }
            
        except Exception as e:
            logger.error(f"Error updating twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error updating twin: {str(e)}"
            }
    
    async def delete_twin(self, twin_id: str) -> Dict[str, Any]:
        """Delete a twin (existing functionality)"""
        try:
            logger.info(f"Deleting twin {twin_id}")
            
            # Unregister from core registry first
            try:
                await self.core_registry_service.unregister_twin(twin_id)
            except Exception as e:
                logger.warning(f"Failed to unregister twin from core registry: {e}")
            
            # Use existing twin service
            success = await self.twin_service.delete_digital_twin(twin_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Twin {twin_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to delete twin {twin_id}"
                }
                
        except Exception as e:
            logger.error(f"Error deleting twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error deleting twin: {str(e)}"
            }
    
    async def search_twins(self, query: str = "", twin_type: str = "", 
                          status: str = "", project_id: str = None, 
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Search twins using database"""
        try:
            logger.info(f"Searching twins with query: {query}")
            
            # Get all twins from repository
            all_twins = self.twin_repo.get_all()
            filtered_twins = []
            
            for twin in all_twins:
                # Apply filters
                if twin_type and getattr(twin, 'twin_type', '') != twin_type:
                    continue
                if status and getattr(twin, 'status', '') != status:
                    continue
                if project_id and getattr(twin, 'project_id', '') != project_id:
                    continue
                
                # Apply query filter if provided
                if query:
                    twin_name = getattr(twin, 'name', '') or getattr(twin, 'twin_name', '')
                    twin_id = getattr(twin, 'twin_id', '')
                    if query.lower() not in twin_name.lower() and query.lower() not in twin_id.lower():
                        continue
                
                filtered_twins.append(self._convert_twin_to_dict(twin))
                
                if len(filtered_twins) >= limit:
                    break
            
            logger.info(f"Found {len(filtered_twins)} twins matching search criteria")
            return filtered_twins
                
        except Exception as e:
            logger.error(f"Error searching twins: {e}")
            return []
    
    async def get_twin_statistics(self) -> Dict[str, Any]:
        """Get twin statistics from database"""
        try:
            logger.info("Getting twin statistics")
            
            # Get basic statistics from database
            all_twins = self.twin_repo.get_all()
            total_twins = len(all_twins)
            active_twins = len([t for t in all_twins if getattr(t, 'status', 'active') == 'active'])
            error_twins = len([t for t in all_twins if getattr(t, 'status', 'error') == 'error'])
            
            logger.info(f"Statistics - Total: {total_twins}, Active: {active_twins}, Error: {error_twins}")
            
            return {
                "total_twins": total_twins,
                "active_twins": active_twins,
                "error_twins": error_twins
            }
            
        except Exception as e:
            logger.error(f"Error getting twin statistics: {e}")
            return {
                "total_twins": 0,
                "active_twins": 0,
                "error_twins": 0
            }
    
    def _convert_twin_to_dict(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Convert twin model to dictionary with proper field mapping"""
        try:
            # Map database fields to API response format based on DigitalTwin model
            twin_dict = {
                "twin_id": getattr(twin, 'twin_id', ''),
                "twin_name": getattr(twin, 'twin_name', ''),
                "description": "",  # Not in current model
                "twin_type": "",  # Not in current model
                "status": getattr(twin, 'status', 'active'),
                "project_id": "",  # Not in current model
                "file_id": getattr(twin, 'file_id', ''),
                "created_at": getattr(twin, 'created_at', datetime.now()).isoformat() if hasattr(twin, 'created_at') and twin.created_at else datetime.now().isoformat(),
                "updated_at": getattr(twin, 'updated_at', datetime.now()).isoformat() if hasattr(twin, 'updated_at') and twin.updated_at else datetime.now().isoformat(),
                # Add health information from the model
                "health_score": getattr(twin, 'health_score', 0),
                "error_count": getattr(twin, 'error_count', 0),
                "health_status": getattr(twin, 'health_status', 'unknown')
            }
            
            logger.debug(f"Converted twin {twin_dict['twin_id']} to dict: {twin_dict}")
            return twin_dict
            
        except Exception as e:
            logger.error(f"Error converting twin to dict: {e}")
            # Return minimal twin info
            return {
                "twin_id": getattr(twin, 'twin_id', 'unknown'),
                "twin_name": "Error loading twin",
                "description": "",
                "twin_type": "",
                "status": "error",
                "project_id": "",
                "file_id": "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "health_score": 0,
                "error_count": 0,
                "health_status": "unknown"
            } 