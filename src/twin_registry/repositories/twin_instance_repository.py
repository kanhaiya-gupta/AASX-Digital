"""
Twin Instance Repository

Data access layer for twin instance management using JSON fields.
Updated for Phase 2: JSON field operations instead of separate tables.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.base_repository import BaseRepository
from src.twin_registry.models.twin_instance import TwinInstance

logger = logging.getLogger(__name__)


class TwinInstanceRepository(BaseRepository[TwinInstance]):
    """Repository for managing twin instances using JSON fields."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        """Initialize the twin instance repository."""
        super().__init__(db_manager, TwinInstance)
        logger.info("Twin Instance Repository initialized (JSON field mode)")
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        return "twin_registry"
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for this table."""
        return [
            "registry_id", "twin_id", "twin_name", "registry_name", "twin_category", "twin_type",
            "twin_priority", "twin_version", "registry_type", "workflow_source", "aasx_integration_id",
            "physics_modeling_id", "federated_learning_id", "data_pipeline_id", "kg_neo4j_id",
            "certificate_manager_id", "integration_status", "overall_health_score", "health_status",
            "lifecycle_status", "lifecycle_phase", "operational_status", "availability_status",
            "sync_status", "sync_frequency", "last_sync_at", "next_sync_at", "sync_error_count",
            "sync_error_message", "performance_score", "data_quality_score", "reliability_score",
            "compliance_score", "security_level", "access_control_level", "encryption_enabled",
            "audit_logging_enabled", "user_id", "org_id", "owner_team", "steward_user_id",
            "created_at", "updated_at", "activated_at", "last_accessed_at", "last_modified_at",
            "registry_config", "registry_metadata", "custom_attributes", "tags", "relationships",
            "dependencies", "instances"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for twin registry table."""
        return "registry_id"
    
    async def initialize(self) -> None:
        """Initialize the repository - no tables needed for JSON field approach."""
        logger.info("Twin Instance Repository initialized (JSON field mode)")
    
    async def create(self, registry_id: str, instance: TwinInstance) -> TwinInstance:
        """Create a new twin instance by adding to the JSON field."""
        try:
            # Get current instances from the registry
            current_instances = await self._get_instances_json(registry_id)
            
            # Add new instance
            instance_dict = {
                "id": instance.id,
                "twin_id": instance.twin_id,
                "instance_data": instance.instance_data or {},
                "instance_metadata": instance.instance_metadata or {},
                "created_by": instance.created_by,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_active": instance.is_active,
                "version": instance.version
            }
            
            current_instances.append(instance_dict)
            
            # Update the JSON field
            query = """
            UPDATE twin_registry 
            SET instances = ?, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = ?
            """
            await self.execute_query(query, (json.dumps(current_instances), registry_id))
            
            logger.info(f"Created twin instance: {instance.id} in registry {registry_id}")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create twin instance: {e}")
            raise
    
    async def get_by_id(self, registry_id: str, instance_id: str) -> Optional[TwinInstance]:
        """Get a twin instance by ID from the JSON field."""
        try:
            instances = await self._get_instances_json(registry_id)
            
            for inst in instances:
                if inst.get("id") == instance_id:
                    return self._dict_to_instance(inst)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get twin instance {instance_id}: {e}")
            return None
    
    async def get_by_twin_id(self, registry_id: str, twin_id: str, limit: int = 50) -> List[TwinInstance]:
        """Get all instances for a specific twin from the JSON field."""
        try:
            instances = await self._get_instances_json(registry_id)
            
            # Filter by twin_id and limit results
            twin_instances = [inst for inst in instances if inst.get("twin_id") == twin_id]
            twin_instances.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return [self._dict_to_instance(inst) for inst in twin_instances[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to get instances for twin {twin_id}: {e}")
            return []
    
    async def get_instances_by_twin(self, registry_id: str, twin_id: str, limit: int = 50) -> List[TwinInstance]:
        """Get all instances for a specific twin from the JSON field (alias for get_by_twin_id)."""
        return await self.get_by_twin_id(registry_id, twin_id, limit=limit)
    
    async def get_active_instances(self, registry_id: str) -> List[TwinInstance]:
        """Get all active instances from the JSON field."""
        try:
            instances = await self._get_instances_json(registry_id)
            
            # Filter active instances
            active_instances = [inst for inst in instances if inst.get("is_active", True)]
            active_instances.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return [self._dict_to_instance(inst) for inst in active_instances]
            
        except Exception as e:
            logger.error(f"Failed to get active instances: {e}")
            return []
    
    async def update(self, registry_id: str, instance_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a twin instance in the JSON field."""
        try:
            instances = await self._get_instances_json(registry_id)
            
            # Find and update the instance
            for i, inst in enumerate(instances):
                if inst.get("id") == instance_id:
                    # Update fields
                    for key, value in update_data.items():
                        if key in ['instance_data', 'instance_metadata']:
                            instances[i][key] = value
                        elif key == 'updated_at':
                            instances[i][key] = datetime.now(timezone.utc).isoformat()
                        else:
                            instances[i][key] = value
                    break
            
            # Update the JSON field
            query = """
            UPDATE twin_registry 
            SET instances = ?, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = ?
            """
            await self.execute_query(query, (json.dumps(instances), registry_id))
            
            logger.info(f"Updated twin instance: {instance_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update twin instance {instance_id}: {e}")
            return False
    
    async def deactivate_instance(self, registry_id: str, instance_id: str) -> bool:
        """Deactivate a twin instance in the JSON field."""
        try:
            instances = await self._get_instances_json(registry_id)
            
            # Find and deactivate the instance
            for i, inst in enumerate(instances):
                if inst.get("id") == instance_id:
                    instances[i]["is_active"] = False
                    instances[i]["updated_at"] = datetime.now(timezone.utc).isoformat()
                    break
            
            # Update the JSON field
            query = """
            UPDATE twin_registry 
            SET instances = ?, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = ?
            """
            await self.execute_query(query, (json.dumps(instances), registry_id))
            
            logger.info(f"Deactivated twin instance: {instance_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate twin instance {instance_id}: {e}")
            return False
    
    async def delete(self, registry_id: str, instance_id: str) -> bool:
        """Delete a twin instance from the JSON field."""
        try:
            instances = await self._get_instances_json(registry_id)
            
            # Remove the instance
            original_count = len(instances)
            instances = [inst for inst in instances if inst.get("id") != instance_id]
            
            if len(instances) < original_count:
                # Update the JSON field
                query = """
                UPDATE twin_registry 
                SET instances = ?, updated_at = CURRENT_TIMESTAMP
                WHERE registry_id = ?
                """
                await self.execute_query(query, (json.dumps(instances), registry_id))
                
                logger.info(f"Deleted twin instance: {instance_id} from registry {registry_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete twin instance {instance_id}: {e}")
            return False
    
    async def get_instance_history(self, registry_id: str, twin_id: str, limit: int = 50) -> List[TwinInstance]:
        """Get instance history for a twin from the JSON field."""
        try:
            instances = await self._get_instances_json(registry_id)
            
            # Filter by twin_id, sort by created_at, and limit results
            twin_instances = [inst for inst in instances if inst.get("twin_id") == twin_id]
            twin_instances.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return [self._dict_to_instance(inst) for inst in twin_instances[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to get instance history for twin {twin_id}: {e}")
            return []
    
    async def _get_instances_json(self, registry_id: str) -> List[Dict[str, Any]]:
        """Get the instances JSON field from the registry."""
        query = "SELECT instances FROM twin_registry WHERE registry_id = ?"
        result = await self.fetch_one(query, (registry_id,))
        
        if result and result.get("instances"):
            try:
                return json.loads(result["instances"])
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in instances field for registry {registry_id}")
                return []
        
        return []
    
    def _dict_to_instance(self, inst_dict: Dict[str, Any]) -> TwinInstance:
        """Convert dictionary to TwinInstance object."""
        return TwinInstance(
            id=inst_dict.get("id"),
            twin_id=inst_dict.get("twin_id"),
            instance_data=inst_dict.get("instance_data", {}),
            instance_metadata=inst_dict.get("instance_metadata", {}),
            created_by=inst_dict.get("created_by"),
            created_at=inst_dict.get("created_at"),
            updated_at=inst_dict.get("updated_at"),
            is_active=inst_dict.get("is_active", True),
            version=inst_dict.get("version", 1)
        ) 