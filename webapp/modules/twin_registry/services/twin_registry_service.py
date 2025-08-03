"""
Twin Registry Service
====================

Core service for twin registry operations following AASX module pattern.
Handles CRUD operations, pagination, and basic twin management.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import shared services and repositories
from src.shared.services.digital_twin_service import DigitalTwinService
from src.shared.services.federated_learning_service import FederatedLearningService
from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository
from src.shared.models.digital_twin import DigitalTwin

logger = logging.getLogger(__name__)

class TwinRegistryService:
    """
    Core twin registry service for managing digital twins.
    Follows the same pattern as AASX module services.
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
        
        logger.info("Twin Registry Service initialized")
    
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
            
            # Convert to dictionaries for JSON serialization
            twin_dicts = []
            for twin in paginated_twins:
                twin_dict = self._convert_twin_to_dict(twin)
                twin_dicts.append(twin_dict)
            
            # Calculate statistics
            active_count = len([t for t in filtered_twins if getattr(t, 'status', '') == 'active'])
            error_count = len([t for t in filtered_twins if getattr(t, 'status', '') == 'error'])
            
            result = {
                "twins": twin_dicts,
                "total_count": total_count,
                "active_count": active_count,
                "error_count": error_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
            
            logger.info(f"Retrieved {len(twin_dicts)} twins out of {total_count} total")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get twins: {str(e)}")
            raise Exception(f"Failed to get twins: {str(e)}")
    
    async def get_twin_by_id(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific twin by ID.
        
        Args:
            twin_id: The twin ID to retrieve
            
        Returns:
            Twin data as dictionary or None if not found
        """
        try:
            logger.info(f"Getting twin by ID: {twin_id}")
            
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                logger.warning(f"Twin not found: {twin_id}")
                return None
            
            twin_dict = self._convert_twin_to_dict(twin)
            logger.info(f"Retrieved twin: {twin_id}")
            return twin_dict
            
        except Exception as e:
            logger.error(f"Failed to get twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to get twin {twin_id}: {str(e)}")
    
    async def create_twin(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new twin using the shared digital twin service.
        
        Args:
            twin_data: Twin data dictionary
            
        Returns:
            Created twin data
        """
        try:
            logger.info(f"Creating new twin: {twin_data.get('twin_name', 'Unknown')}")
            
            # Use the shared digital twin service to create the twin
            created_twin = self.twin_service.register_digital_twin(
                twin_data.get('file_id', ''),
                twin_data
            )
            
            if not created_twin:
                raise Exception("Failed to create twin")
            
            twin_dict = self._convert_twin_to_dict(created_twin)
            logger.info(f"Successfully created twin: {twin_dict.get('twin_id')}")
            return twin_dict
            
        except Exception as e:
            logger.error(f"Failed to create twin: {str(e)}")
            raise Exception(f"Failed to create twin: {str(e)}")
    
    async def update_twin(self, twin_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing twin.
        
        Args:
            twin_id: The twin ID to update
            update_data: Data to update
            
        Returns:
            Updated twin data
        """
        try:
            logger.info(f"Updating twin: {twin_id}")
            
            # Get existing twin
            existing_twin = self.twin_repo.get_by_id(twin_id)
            if not existing_twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(existing_twin, key):
                    setattr(existing_twin, key, value)
            
            # Update timestamp
            existing_twin.updated_at = datetime.now().isoformat()
            
            # Save to repository
            updated_twin = self.twin_repo.update(existing_twin)
            if not updated_twin:
                raise Exception(f"Failed to update twin: {twin_id}")
            
            twin_dict = self._convert_twin_to_dict(updated_twin)
            logger.info(f"Successfully updated twin: {twin_id}")
            return twin_dict
            
        except Exception as e:
            logger.error(f"Failed to update twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to update twin {twin_id}: {str(e)}")
    
    async def delete_twin(self, twin_id: str) -> bool:
        """
        Delete a twin.
        
        Args:
            twin_id: The twin ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Deleting twin: {twin_id}")
            
            # Check if twin exists
            existing_twin = self.twin_repo.get_by_id(twin_id)
            if not existing_twin:
                logger.warning(f"Twin not found for deletion: {twin_id}")
                return False
            
            # Delete from repository
            success = self.twin_repo.delete(twin_id)
            
            if success:
                logger.info(f"Successfully deleted twin: {twin_id}")
            else:
                logger.error(f"Failed to delete twin: {twin_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to delete twin {twin_id}: {str(e)}")
    
    async def search_twins(self, query: str = "", twin_type: str = "", 
                          status: str = "", project_id: str = None, 
                          limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search twins by various criteria.
        
        Args:
            query: Search query string
            twin_type: Filter by twin type
            status: Filter by twin status
            project_id: Filter by project ID
            limit: Maximum number of results
            
        Returns:
            List of matching twins
        """
        try:
            logger.info(f"Searching twins - query: '{query}', type: '{twin_type}', status: '{status}'")
            
            # Get all twins
            all_twins = self.twin_repo.get_all()
            
            # Apply filters
            filtered_twins = []
            for twin in all_twins:
                # Query filter (search in name and description)
                if query:
                    twin_name = getattr(twin, 'twin_name', '').lower()
                    twin_desc = getattr(twin, 'description', '').lower()
                    if query.lower() not in twin_name and query.lower() not in twin_desc:
                        continue
                
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
            
            # Apply limit
            limited_twins = filtered_twins[:limit]
            
            # Convert to dictionaries
            twin_dicts = [self._convert_twin_to_dict(twin) for twin in limited_twins]
            
            logger.info(f"Search returned {len(twin_dicts)} twins")
            return twin_dicts
            
        except Exception as e:
            logger.error(f"Failed to search twins: {str(e)}")
            raise Exception(f"Failed to search twins: {str(e)}")
    
    async def get_twin_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive twin registry statistics.
        
        Returns:
            Dictionary with various statistics
        """
        try:
            logger.info("Getting twin registry statistics")
            
            all_twins = self.twin_repo.get_all()
            
            # Calculate statistics
            total_count = len(all_twins)
            status_counts = {}
            type_counts = {}
            project_counts = {}
            
            for twin in all_twins:
                # Status counts
                status = getattr(twin, 'status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Type counts
                twin_type = getattr(twin, 'twin_type', 'unknown')
                type_counts[twin_type] = type_counts.get(twin_type, 0) + 1
                
                # Project counts
                project_id = getattr(twin, 'project_id', 'unknown')
                project_counts[project_id] = project_counts.get(project_id, 0) + 1
            
            # Health statistics
            healthy_count = len([t for t in all_twins if getattr(t, 'health_status', '') == 'healthy'])
            warning_count = len([t for t in all_twins if getattr(t, 'health_status', '') == 'warning'])
            critical_count = len([t for t in all_twins if getattr(t, 'health_status', '') == 'critical'])
            
            statistics = {
                "total_twins": total_count,
                "status_distribution": status_counts,
                "type_distribution": type_counts,
                "project_distribution": project_counts,
                "health_distribution": {
                    "healthy": healthy_count,
                    "warning": warning_count,
                    "critical": critical_count
                },
                "last_updated": datetime.now().isoformat()
            }
            
            logger.info(f"Generated statistics for {total_count} twins")
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get twin statistics: {str(e)}")
            raise Exception(f"Failed to get twin statistics: {str(e)}")
    
    def _convert_twin_to_dict(self, twin: DigitalTwin) -> Dict[str, Any]:
        """
        Convert a DigitalTwin object to a dictionary for JSON serialization.
        
        Args:
            twin: DigitalTwin object
            
        Returns:
            Dictionary representation of the twin
        """
        try:
            twin_dict = {
                'twin_id': getattr(twin, 'twin_id', ''),
                'twin_name': getattr(twin, 'twin_name', ''),
                'status': getattr(twin, 'status', ''),
                'health_status': getattr(twin, 'health_status', ''),
                'health_score': getattr(twin, 'health_score', 0),
                'file_id': getattr(twin, 'file_id', ''),
                'project_id': getattr(twin, 'project_id', ''),
                'created_at': getattr(twin, 'created_at', ''),
                'updated_at': getattr(twin, 'updated_at', ''),
                'metadata': getattr(twin, 'metadata', {}),
                'simulation_status': getattr(twin, 'simulation_status', ''),
                'federated_participation_status': getattr(twin, 'federated_participation_status', ''),
                'data_privacy_level': getattr(twin, 'data_privacy_level', '')
            }
            
            return twin_dict
            
        except Exception as e:
            logger.error(f"Failed to convert twin to dict: {str(e)}")
            return {} 