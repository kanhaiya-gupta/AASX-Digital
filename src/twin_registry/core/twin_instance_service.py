"""
Twin Instance Service

Manages twin instances including:
- Creating and managing twin instances
- Instance lifecycle management
- Instance history tracking
- Instance rollback capabilities
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from src.shared.services.base_service import BaseService
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.twin_registry.models.twin_instance import TwinInstance
from src.twin_registry.repositories.twin_instance_repository import TwinInstanceRepository

logger = logging.getLogger(__name__)


class TwinInstanceService(BaseService):
    """
    Service for managing twin instances.
    
    Provides functionality for:
    - Creating and managing twin instances
    - Instance lifecycle management
    - Instance history tracking
    - Instance rollback capabilities
    """
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize the twin instance service."""
        super().__init__(db_manager)
        self.instance_repo = TwinInstanceRepository(db_manager)
        logger.info("Twin Instance Service initialized")
    
    async def initialize(self) -> None:
        """Initialize the instance service."""
        try:
            await self.instance_repo.initialize()
            logger.info("Twin Instance Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Instance Service: {e}")
            raise
    
    async def create_instance(
        self,
        twin_id: str,
        instance_data: Dict[str, Any],
        instance_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new instance for a twin.
        
        Args:
            twin_id: ID of the twin
            instance_data: Data for the instance
            instance_metadata: Additional metadata
            created_by: User who created the instance
            
        Returns:
            Dictionary with instance details and status
        """
        try:
            logger.info(f"Creating instance for twin: {twin_id}")
            
            # Deactivate current active instance
            await self._deactivate_current_instance(twin_id)
            
            # Create new instance
            instance = TwinInstance(
                id=str(uuid.uuid4()),
                twin_id=twin_id,
                instance_data=instance_data,
                instance_metadata=instance_metadata or {},
                created_by=created_by,
                created_at=datetime.utcnow().isoformat(),
                is_active=True,
                version=await self._get_next_version(twin_id)
            )
            
            # Save to database
            saved_instance = await self.instance_repo.create(instance)
            
            return {
                "success": True,
                "instance": self._convert_instance_to_dict(saved_instance),
                "message": "Instance created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create instance: {e}")
            return {
                "success": False,
                "error": str(e),
                "instance": None
            }
    
    async def get_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Get a specific instance by ID.
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            Dictionary with instance details
        """
        try:
            logger.info(f"Getting instance: {instance_id}")
            
            instance = await self.instance_repo.get_by_id(instance_id)
            
            if instance:
                return {
                    "success": True,
                    "instance": self._convert_instance_to_dict(instance)
                }
            else:
                return {
                    "success": False,
                    "error": "Instance not found",
                    "instance": None
                }
                
        except Exception as e:
            logger.error(f"Failed to get instance {instance_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "instance": None
            }
    
    async def get_twin_instances(
        self,
        twin_id: str,
        active_only: bool = True,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get instances for a specific twin.
        
        Args:
            twin_id: ID of the twin
            active_only: Whether to return only active instances
            limit: Maximum number of instances to return
            
        Returns:
            Dictionary with instances and metadata
        """
        try:
            logger.info(f"Getting instances for twin: {twin_id}")
            
            instances = await self.instance_repo.get_by_twin_id(twin_id, active_only)
            
            # Apply limit
            if limit and len(instances) > limit:
                instances = instances[:limit]
            
            return {
                "success": True,
                "instances": [self._convert_instance_to_dict(i) for i in instances],
                "count": len(instances),
                "twin_id": twin_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get instances for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "instances": [],
                "count": 0
            }
    
    async def get_active_instance(self, twin_id: str) -> Dict[str, Any]:
        """
        Get the currently active instance for a twin.
        
        Args:
            twin_id: ID of the twin
            
        Returns:
            Dictionary with active instance details
        """
        try:
            logger.info(f"Getting active instance for twin: {twin_id}")
            
            instance = await self.instance_repo.get_active_instance(twin_id)
            
            if instance:
                return {
                    "success": True,
                    "instance": self._convert_instance_to_dict(instance)
                }
            else:
                return {
                    "success": False,
                    "error": "No active instance found",
                    "instance": None
                }
                
        except Exception as e:
            logger.error(f"Failed to get active instance for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "instance": None
            }
    
    async def update_instance(
        self,
        instance_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an instance.
        
        Args:
            instance_id: ID of the instance
            update_data: Data to update
            
        Returns:
            Dictionary with update status
        """
        try:
            logger.info(f"Updating instance: {instance_id}")
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            success = await self.instance_repo.update(instance_id, update_data)
            
            if success:
                # Get updated instance
                instance = await self.instance_repo.get_by_id(instance_id)
                return {
                    "success": True,
                    "instance": self._convert_instance_to_dict(instance),
                    "message": "Instance updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update instance",
                    "instance": None
                }
                
        except Exception as e:
            logger.error(f"Failed to update instance {instance_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "instance": None
            }
    
    async def rollback_to_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Rollback to a specific instance.
        
        Args:
            instance_id: ID of the instance to rollback to
            
        Returns:
            Dictionary with rollback status
        """
        try:
            logger.info(f"Rolling back to instance: {instance_id}")
            
            # Get the target instance
            target_instance = await self.instance_repo.get_by_id(instance_id)
            if not target_instance:
                return {
                    "success": False,
                    "error": "Target instance not found",
                    "instance": None
                }
            
            # Deactivate current active instance
            await self._deactivate_current_instance(target_instance.twin_id)
            
            # Activate the target instance
            success = await self.instance_repo.update(instance_id, {
                "is_active": True,
                "updated_at": datetime.utcnow().isoformat()
            })
            
            if success:
                return {
                    "success": True,
                    "instance": self._convert_instance_to_dict(target_instance),
                    "message": "Rollback completed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to activate target instance",
                    "instance": None
                }
                
        except Exception as e:
            logger.error(f"Failed to rollback to instance {instance_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "instance": None
            }
    
    async def delete_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Delete an instance.
        
        Args:
            instance_id: ID of the instance to delete
            
        Returns:
            Dictionary with deletion status
        """
        try:
            logger.info(f"Deleting instance: {instance_id}")
            
            success = await self.instance_repo.delete(instance_id)
            
            return {
                "success": success,
                "message": "Instance deleted successfully" if success else "Instance not found",
                "instance_id": instance_id
            }
            
        except Exception as e:
            logger.error(f"Failed to delete instance {instance_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "instance_id": instance_id
            }
    
    async def get_instance_history(
        self,
        twin_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get instance history for a twin.
        
        Args:
            twin_id: ID of the twin
            limit: Maximum number of history records to return
            
        Returns:
            Dictionary with instance history
        """
        try:
            logger.info(f"Getting instance history for twin: {twin_id}")
            
            history = await self.instance_repo.get_instance_history(twin_id, limit)
            
            return {
                "success": True,
                "history": [self._convert_instance_to_dict(i) for i in history],
                "count": len(history),
                "twin_id": twin_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get instance history for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "history": [],
                "count": 0
            }
    
    async def _deactivate_current_instance(self, twin_id: str) -> None:
        """Deactivate the currently active instance for a twin."""
        try:
            current_instance = await self.instance_repo.get_active_instance(twin_id)
            if current_instance:
                await self.instance_repo.deactivate_instance(current_instance.id)
                logger.info(f"Deactivated current instance for twin: {twin_id}")
        except Exception as e:
            logger.error(f"Failed to deactivate current instance for twin {twin_id}: {e}")
    
    async def _get_next_version(self, twin_id: str) -> int:
        """Get the next version number for a twin."""
        try:
            instances = await self.instance_repo.get_by_twin_id(twin_id, active_only=False)
            if instances:
                return max(i.version for i in instances) + 1
            return 1
        except Exception as e:
            logger.error(f"Failed to get next version for twin {twin_id}: {e}")
            return 1
    
    def _convert_instance_to_dict(self, instance: TwinInstance) -> Dict[str, Any]:
        """Convert a TwinInstance object to dictionary."""
        return {
            "id": instance.id,
            "twin_id": instance.twin_id,
            "instance_data": instance.instance_data,
            "instance_metadata": instance.instance_metadata,
            "created_by": instance.created_by,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
            "is_active": instance.is_active,
            "version": instance.version
        } 