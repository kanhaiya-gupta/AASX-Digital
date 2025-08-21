"""
Twin Relationship Repository

Data access layer for twin relationship management using JSON fields.
Updated for Phase 2: JSON field operations instead of separate tables.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.base_repository import BaseRepository
from src.twin_registry.models.twin_relationship import TwinRelationship, TwinRelationshipQuery

logger = logging.getLogger(__name__)


class TwinRelationshipRepository(BaseRepository[TwinRelationship]):
    """Repository for managing twin relationships using JSON fields."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        """Initialize the twin relationship repository."""
        super().__init__(db_manager, TwinRelationship)
        logger.info("Twin Relationship Repository initialized (JSON field mode)")
    
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
        logger.info("Twin Relationship Repository initialized (JSON field mode)")
    
    async def create(self, registry_id: str, relationship: TwinRelationship) -> TwinRelationship:
        """Create a new relationship by adding to the JSON field."""
        try:
            # Get current relationships from the registry
            current_relationships = await self._get_relationships_json(registry_id)
            
            # Add new relationship
            relationship_dict = {
                "id": relationship.id,
                "source_twin_id": relationship.source_twin_id,
                "target_twin_id": relationship.target_twin_id,
                "relationship_type": relationship.relationship_type,
                "relationship_data": relationship.relationship_data or {},
                "relationship_metadata": relationship.relationship_metadata or {},
                "created_by": relationship.created_by,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_active": relationship.is_active,
                "strength": relationship.strength,
                "direction": relationship.direction
            }
            
            current_relationships.append(relationship_dict)
            
            # Update the JSON field
            query = """
            UPDATE twin_registry 
            SET relationships = ?, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = ?
            """
            await self.execute_query(query, (json.dumps(current_relationships), registry_id))
            
            logger.info(f"Created relationship: {relationship.id} in registry {registry_id}")
            return relationship
            
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            raise
    
    async def get_by_id(self, registry_id: str, relationship_id: str) -> Optional[TwinRelationship]:
        """Get a relationship by ID from the JSON field."""
        try:
            relationships = await self._get_relationships_json(registry_id)
            
            for rel in relationships:
                if rel.get("id") == relationship_id:
                    return self._dict_to_relationship(rel)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get relationship {relationship_id}: {e}")
            return None
    
    async def get_by_twin_id(self, registry_id: str, twin_id: str, limit: int = 50) -> List[TwinRelationship]:
        """Get all relationships for a specific twin from the JSON field."""
        try:
            relationships = await self._get_relationships_json(registry_id)
            
            # Filter by twin_id (either source or target) and limit results
            twin_relationships = [
                rel for rel in relationships 
                if rel.get("source_twin_id") == twin_id or rel.get("target_twin_id") == twin_id
            ]
            twin_relationships.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return [self._dict_to_relationship(rel) for rel in twin_relationships[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to get relationships for twin {twin_id}: {e}")
            return []
    
    async def get_relationships_by_twin(self, registry_id: str, twin_id: str, query: Optional[TwinRelationshipQuery] = None) -> List[TwinRelationship]:
        """Get all relationships for a specific twin from the JSON field (alias for get_by_twin_id)."""
        return await self.get_by_twin_id(registry_id, twin_id, limit=50)
    
    async def get_by_type(self, registry_id: str, relationship_type: str, limit: int = 50) -> List[TwinRelationship]:
        """Get all relationships of a specific type from the JSON field."""
        try:
            relationships = await self._get_relationships_json(registry_id)
            
            # Filter by relationship type and limit results
            type_relationships = [
                rel for rel in relationships 
                if rel.get("relationship_type") == relationship_type
            ]
            type_relationships.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return [self._dict_to_relationship(rel) for rel in type_relationships[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to get relationships of type {relationship_type}: {e}")
            return []
    
    async def get_active_relationships(self, registry_id: str) -> List[TwinRelationship]:
        """Get all active relationships from the JSON field."""
        try:
            relationships = await self._get_relationships_json(registry_id)
            
            # Filter active relationships
            active_relationships = [rel for rel in relationships if rel.get("is_active", True)]
            active_relationships.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return [self._dict_to_relationship(rel) for rel in active_relationships]
            
        except Exception as e:
            logger.error(f"Failed to get active relationships: {e}")
            return []
    
    async def update(self, registry_id: str, relationship_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a relationship in the JSON field."""
        try:
            relationships = await self._get_relationships_json(registry_id)
            
            # Find and update the relationship
            for i, rel in enumerate(relationships):
                if rel.get("id") == relationship_id:
                    # Update fields
                    for key, value in update_data.items():
                        if key in ['relationship_data', 'relationship_metadata']:
                            relationships[i][key] = value
                        elif key == 'updated_at':
                            relationships[i][key] = datetime.now(timezone.utc).isoformat()
                        else:
                            relationships[i][key] = value
                    break
            
            # Update the JSON field
            query = """
            UPDATE twin_registry 
            SET relationships = ?, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = ?
            """
            await self.execute_query(query, (json.dumps(relationships), registry_id))
            
            logger.info(f"Updated relationship: {relationship_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update relationship {relationship_id}: {e}")
            return False
    
    async def deactivate_relationship(self, registry_id: str, relationship_id: str) -> bool:
        """Deactivate a relationship in the JSON field."""
        try:
            relationships = await self._get_relationships_json(registry_id)
            
            # Find and deactivate the relationship
            for i, rel in enumerate(relationships):
                if rel.get("id") == relationship_id:
                    relationships[i]["is_active"] = False
                    relationships[i]["updated_at"] = datetime.now(timezone.utc).isoformat()
                    break
            
            # Update the JSON field
            query = """
            UPDATE twin_registry 
            SET relationships = ?, updated_at = CURRENT_TIMESTAMP
            WHERE registry_id = ?
            """
            await self.execute_query(query, (json.dumps(relationships), registry_id))
            
            logger.info(f"Deactivated relationship: {relationship_id} in registry {registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate relationship {relationship_id}: {e}")
            return False
    
    async def delete(self, registry_id: str, relationship_id: str) -> bool:
        """Delete a relationship from the JSON field."""
        try:
            relationships = await self._get_relationships_json(registry_id)
            
            # Remove the relationship
            original_count = len(relationships)
            relationships = [rel for rel in relationships if rel.get("id") != relationship_id]
            
            if len(relationships) < original_count:
                # Update the JSON field
                query = """
                UPDATE twin_registry 
                SET relationships = ?, updated_at = CURRENT_TIMESTAMP
                WHERE registry_id = ?
                """
                await self.execute_query(query, (json.dumps(relationships), registry_id))
                
                logger.info(f"Deleted relationship: {relationship_id} from registry {registry_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete relationship {relationship_id}: {e}")
            return False
    
    async def get_relationships_in_date_range(self, registry_id: str, start_date: datetime, end_date: datetime) -> List[TwinRelationship]:
        """Get relationships created within a date range from the JSON field."""
        try:
            relationships = await self._get_relationships_json(registry_id)
            
            # Filter by date range
            start_iso = start_date.isoformat()
            end_iso = end_date.isoformat()
            
            date_filtered = [
                rel for rel in relationships
                if start_iso <= rel.get("created_at", "") <= end_iso
            ]
            date_filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return [self._dict_to_relationship(rel) for rel in date_filtered]
            
        except Exception as e:
            logger.error(f"Failed to get relationships in date range: {e}")
            return []
    
    async def get_relationship_network(self, registry_id: str, twin_id: str, depth: int = 2) -> List[TwinRelationship]:
        """Get relationship network around a twin up to specified depth."""
        try:
            relationships = await self._get_relationships_json(registry_id)
            
            # Build network starting from the target twin
            network = set()
            visited = set()
            to_visit = [(twin_id, 0)]  # (twin_id, current_depth)
            
            while to_visit:
                current_twin, current_depth = to_visit.pop(0)
                
                if current_depth > depth or current_twin in visited:
                    continue
                
                visited.add(current_twin)
                
                # Find all relationships involving this twin
                for rel in relationships:
                    if rel.get("is_active", True):
                        if rel.get("source_twin_id") == current_twin:
                            network.add(rel["id"])
                            if current_depth < depth:
                                to_visit.append((rel.get("target_twin_id"), current_depth + 1))
                        elif rel.get("target_twin_id") == current_twin:
                            network.add(rel["id"])
                            if current_depth < depth:
                                to_visit.append((rel.get("source_twin_id"), current_depth + 1))
            
            # Convert back to relationship objects
            network_relationships = [
                rel for rel in relationships if rel.get("id") in network
            ]
            network_relationships.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return [self._dict_to_relationship(rel) for rel in network_relationships]
            
        except Exception as e:
            logger.error(f"Failed to get relationship network for twin {twin_id}: {e}")
            return []
    
    async def _get_relationships_json(self, registry_id: str) -> List[Dict[str, Any]]:
        """Get the relationships JSON field from the registry."""
        query = "SELECT relationships FROM twin_registry WHERE registry_id = ?"
        result = await self.fetch_one(query, (registry_id,))
        
        if result and result.get("relationships"):
            try:
                return json.loads(result["relationships"])
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in relationships field for registry {registry_id}")
                return []
        
        return []
    
    def _dict_to_relationship(self, rel_dict: Dict[str, Any]) -> TwinRelationship:
        """Convert dictionary to TwinRelationship object."""
        return TwinRelationship(
            id=rel_dict.get("id"),
            source_twin_id=rel_dict.get("source_twin_id"),
            target_twin_id=rel_dict.get("target_twin_id"),
            relationship_type=rel_dict.get("relationship_type"),
            relationship_data=rel_dict.get("relationship_data", {}),
            relationship_metadata=rel_dict.get("relationship_metadata", {}),
            created_by=rel_dict.get("created_by"),
            created_at=rel_dict.get("created_at"),
            updated_at=rel_dict.get("updated_at"),
            is_active=rel_dict.get("is_active", True),
            strength=rel_dict.get("strength", 1.0),
            direction=rel_dict.get("direction", "bidirectional")
        ) 