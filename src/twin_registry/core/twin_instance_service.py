"""
Twin Instance Service

Service for managing twin instances using JSON fields.
Updated for Phase 2: JSON field operations instead of separate tables.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from ..models.twin_instance import TwinInstance, TwinInstanceQuery
from ..repositories.twin_instance_repository import TwinInstanceRepository

logger = logging.getLogger(__name__)


class TwinInstanceService:
    """Service for managing twin instances"""
    
    def __init__(self):
        """Initialize the twin instance service"""
        # Use the same database infrastructure as other modules
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        # Initialize central database connection
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        
        # Initialize repository with database connection
        self.instance_repo = TwinInstanceRepository(self.db_manager)
    
    async def initialize(self) -> None:
        """Initialize the service - no tables needed for JSON field approach"""
        try:
            # No table creation needed - all data stored in existing twin_registry tables
            logger.info("Twin Instance Service initialized successfully (JSON field mode)")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Instance Service: {e}")
            raise
    
    # ==================== Instance Management ====================
    
    async def create_instance(
        self,
        registry_id: str,
        twin_id: str,
        instance_data: Dict[str, Any],
        instance_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> TwinInstance:
        """Create a new instance of a twin"""
        try:
            # Create instance object
            instance = TwinInstance.create_instance(
                twin_id=twin_id,
                instance_data=instance_data,
                instance_metadata=instance_metadata or {},
                created_by=created_by
            )
            
            # Save to database using JSON field
            await self.instance_repo.create(registry_id, instance)
            
            logger.info(f"Created instance {instance.id} for twin {twin_id} in registry {registry_id}")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create instance for twin {twin_id}: {e}")
            raise
    
    async def get_instance(self, registry_id: str, instance_id: str) -> Optional[TwinInstance]:
        """Get an instance by ID"""
        try:
            return await self.instance_repo.get_by_id(registry_id, instance_id)
        except Exception as e:
            logger.error(f"Failed to get instance {instance_id}: {e}")
            return None
    
    async def get_instances_by_twin(self, registry_id: str, twin_id: str, limit: int = 50) -> List[TwinInstance]:
        """Get all instances for a specific twin"""
        try:
            return await self.instance_repo.get_by_twin_id(registry_id, twin_id, limit)
        except Exception as e:
            logger.error(f"Failed to get instances for twin {twin_id}: {e}")
            return []
    
    async def get_active_instances(self, registry_id: str) -> List[TwinInstance]:
        """Get all active instances"""
        try:
            return await self.instance_repo.get_active_instances(registry_id)
        except Exception as e:
            logger.error(f"Failed to get active instances: {e}")
            return []
    
    async def update_instance(
        self,
        registry_id: str,
        instance_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update an instance"""
        try:
            result = await self.instance_repo.update(registry_id, instance_id, update_data)
            if result:
                logger.info(f"Updated instance {instance_id}")
            else:
                logger.warning(f"Instance {instance_id} not found or update failed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update instance {instance_id}: {e}")
            return False
    
    async def deactivate_instance(self, registry_id: str, instance_id: str) -> bool:
        """Deactivate an instance"""
        try:
            result = await self.instance_repo.deactivate_instance(registry_id, instance_id)
            if result:
                logger.info(f"Deactivated instance {instance_id}")
            else:
                logger.warning(f"Instance {instance_id} not found or deactivation failed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to deactivate instance {instance_id}: {e}")
            return False
    
    async def delete_instance(self, registry_id: str, instance_id: str) -> bool:
        """Delete an instance"""
        try:
            result = await self.instance_repo.delete(registry_id, instance_id)
            if result:
                logger.info(f"Deleted instance {instance_id}")
            else:
                logger.warning(f"Instance {instance_id} not found or deletion failed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete instance {instance_id}: {e}")
            return False
    
    # ==================== Instance Queries ====================
    
    async def query_instances(self, registry_id: str, query: TwinInstanceQuery) -> List[TwinInstance]:
        """Query instances with filters"""
        try:
            # For now, get all instances from the registry and filter
            # This could be optimized later with more sophisticated querying
            all_instances = await self.instance_repo.get_by_twin_id(registry_id, "", 1000)
            
            # Apply filters
            filtered_instances = []
            for inst in all_instances:
                if query.twin_id and inst.twin_id != query.twin_id:
                    continue
                if query.is_active is not None and inst.is_active != query.is_active:
                    continue
                if query.created_after and inst.created_at < query.created_after:
                    continue
                if query.created_before and inst.created_at > query.created_before:
                    continue
                
                filtered_instances.append(inst)
            
            return filtered_instances
            
        except Exception as e:
            logger.error(f"Failed to query instances: {e}")
            return []
    
    async def get_instances_by_type(self, registry_id: str, instance_type: str) -> List[TwinInstance]:
        """Get instances of a specific type"""
        try:
            # This would need to be enhanced based on how instance types are stored
            # For now, return all instances
            return await self.instance_repo.get_active_instances(registry_id)
        except Exception as e:
            logger.error(f"Failed to get instances by type {instance_type}: {e}")
            return []
    
    async def get_instances_in_date_range(
        self,
        registry_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[TwinInstance]:
        """Get instances created within a date range"""
        try:
            # This would need to be enhanced with proper date filtering
            # For now, return all instances
            return await self.instance_repo.get_active_instances(registry_id)
        except Exception as e:
            logger.error(f"Failed to get instances in date range: {e}")
            return []
    
    # ==================== Instance Analytics ====================
    
    async def get_instance_summary(self, registry_id: str) -> Dict[str, Any]:
        """Get instance statistics and summary"""
        try:
            all_instances = await self.instance_repo.get_active_instances(registry_id)
            
            total_instances = len(all_instances)
            active_instances = len([inst for inst in all_instances if inst.is_active])
            
            # Count by twin
            instances_by_twin = {}
            for inst in all_instances:
                twin_id = inst.twin_id
                instances_by_twin[twin_id] = instances_by_twin.get(twin_id, 0) + 1
            
            # Count by version
            instances_by_version = {}
            for inst in all_instances:
                version = inst.version
                instances_by_version[version] = instances_by_version.get(version, 0) + 1
            
            return {
                "total_instances": total_instances,
                "active_instances": active_instances,
                "instances_by_twin": instances_by_twin,
                "instances_by_version": instances_by_version
            }
            
        except Exception as e:
            logger.error(f"Failed to get instance summary: {e}")
            return {}
    
    async def get_instance_history(self, registry_id: str, twin_id: str, limit: int = 50) -> List[TwinInstance]:
        """Get instance history for a twin"""
        try:
            return await self.instance_repo.get_instance_history(registry_id, twin_id, limit)
        except Exception as e:
            logger.error(f"Failed to get instance history for twin {twin_id}: {e}")
            return []
    
    # ==================== Bulk Operations ====================
    
    async def create_multiple_instances(
        self,
        registry_id: str,
        instances_data: List[Dict[str, Any]]
    ) -> List[TwinInstance]:
        """Create multiple instances at once"""
        try:
            created_instances = []
            
            for inst_data in instances_data:
                instance = await self.create_instance(
                    registry_id=registry_id,
                    twin_id=inst_data["twin_id"],
                    instance_data=inst_data["instance_data"],
                    instance_metadata=inst_data.get("instance_metadata"),
                    created_by=inst_data.get("created_by")
                )
                created_instances.append(instance)
            
            logger.info(f"Created {len(created_instances)} instances in registry {registry_id}")
            return created_instances
            
        except Exception as e:
            logger.error(f"Failed to create multiple instances: {e}")
            raise
    
    async def deactivate_instances_by_twin(self, registry_id: str, twin_id: str) -> int:
        """Deactivate all instances for a specific twin"""
        try:
            instances = await self.get_instances_by_twin(registry_id, twin_id)
            deactivated_count = 0
            
            for inst in instances:
                if inst.is_active:
                    await self.deactivate_instance(registry_id, inst.id)
                    deactivated_count += 1
            
            logger.info(f"Deactivated {deactivated_count} instances for twin {twin_id}")
            return deactivated_count
            
        except Exception as e:
            logger.error(f"Failed to deactivate instances for twin {twin_id}: {e}")
            return 0
    
    # ==================== Instance Lifecycle ====================
    
    async def promote_instance(self, registry_id: str, instance_id: str) -> bool:
        """Promote an instance to production"""
        try:
            update_data = {
                "instance_metadata": {"status": "production", "promoted_at": datetime.now().isoformat()}
            }
            return await self.update_instance(registry_id, instance_id, update_data)
        except Exception as e:
            logger.error(f"Failed to promote instance {instance_id}: {e}")
            return False
    
    async def rollback_instance(self, registry_id: str, instance_id: str) -> bool:
        """Rollback an instance to previous version"""
        try:
            update_data = {
                "instance_metadata": {"status": "rollback", "rolled_back_at": datetime.now().isoformat()}
            }
            return await self.update_instance(registry_id, instance_id, update_data)
        except Exception as e:
            logger.error(f"Failed to rollback instance {instance_id}: {e}")
            return False
    
    # ==================== Enhanced Query Methods ====================
    
    async def get_all_instances(self) -> List[Dict[str, Any]]:
        """
        Get all instances across all registries.
        This method provides the interface expected by the webapp service.
        
        Returns:
            List of instance dictionaries
        """
        try:
            logger.info("Getting all instances across all registries")
            
            # Import the registry repository to get all registries
            from ..repositories.twin_registry_repository import TwinRegistryRepository
            registry_repo = TwinRegistryRepository(self.db_manager)
            
            # Get all registries
            all_registries = await registry_repo.get_all()
            
            all_instances = []
            for registry in all_registries:
                try:
                    # Get all instances for this registry (not filtered by twin_id)
                    registry_instances = await self.instance_repo.get_active_instances(registry.registry_id)
                    
                    for inst in registry_instances:
                        instance_dict = {
                            "instance_id": inst.id,
                            "registry_id": registry.registry_id,
                            "twin_id": inst.twin_id or registry.twin_id or "unknown",
                            "twin_name": registry.twin_name or "Unknown Twin",
                            "version": inst.version,
                            "instance_type": getattr(inst, 'instance_type', 'generic'),
                            "created_at": inst.created_at.isoformat() if inst.created_at else "",
                            "is_active": inst.is_active,
                            "registry_type": registry.registry_type or "unknown",
                            "metadata": inst.instance_metadata or {}
                        }
                        all_instances.append(instance_dict)
                        
                except Exception as e:
                    logger.warning(f"Failed to get instances for registry {registry.registry_id}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(all_instances)} instances from all registries")
            return all_instances
            
        except Exception as e:
            logger.error(f"Failed to get all instances: {e}")
            raise 