"""
Twin Relationship Service

Service for managing twin relationships using JSON fields.
Updated for Phase 2: JSON field operations instead of separate tables.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.database_factory import DatabaseFactory, DatabaseType
from ..models.twin_relationship import TwinRelationship, TwinRelationshipQuery, TwinRelationshipSummary
from ..repositories.twin_relationship_repository import TwinRelationshipRepository

logger = logging.getLogger(__name__)


class TwinRelationshipService:
    """Service for managing twin relationships"""
    
    def __init__(self):
        """Initialize the twin relationship service"""
        # Use the same database infrastructure as other modules
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        # Initialize central database connection
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        
        # Initialize repository with database connection
        self.relationship_repo = TwinRelationshipRepository(self.db_manager)
    
    async def initialize(self) -> None:
        """Initialize the service - no tables needed for JSON field approach"""
        try:
            # No table creation needed - all data stored in existing twin_registry tables
            logger.info("Twin Relationship Service initialized successfully (JSON field mode)")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Relationship Service: {e}")
            raise
    
    # ==================== Relationship Management ====================
    
    async def create_relationship(
        self,
        registry_id: str,
        source_twin_id: str,
        target_twin_id: str,
        relationship_type: str,
        relationship_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TwinRelationship:
        """Create a new relationship between twins"""
        try:
            # Create relationship object
            relationship = TwinRelationship.create_relationship(
                source_twin_id=source_twin_id,
                target_twin_id=target_twin_id,
                relationship_type=relationship_type,
                relationship_data=relationship_data or {},
                metadata=metadata or {}
            )
            
            # Save to database using JSON field
            await self.relationship_repo.create(registry_id, relationship)
            
            logger.info(f"Created relationship {relationship.relationship_id} between {source_twin_id} and {target_twin_id} in registry {registry_id}")
            return relationship
            
        except Exception as e:
            logger.error(f"Failed to create relationship between {source_twin_id} and {target_twin_id}: {e}")
            raise
    
    async def get_relationship(self, registry_id: str, relationship_id: str) -> Optional[TwinRelationship]:
        """Get a relationship by ID"""
        try:
            return await self.relationship_repo.get_by_id(registry_id, relationship_id)
        except Exception as e:
            logger.error(f"Failed to get relationship {relationship_id}: {e}")
            return None
    
    async def get_relationships_by_twin(self, registry_id: str, twin_id: str, query: Optional[TwinRelationshipQuery] = None) -> List[TwinRelationship]:
        """Get all relationships for a twin (as source or target)"""
        try:
            return await self.relationship_repo.get_relationships_by_twin(registry_id, twin_id, query)
        except Exception as e:
            logger.error(f"Failed to get relationships for twin {twin_id}: {e}")
            return []
    
    async def get_relationships(self, registry_id: str, query: TwinRelationshipQuery) -> List[TwinRelationship]:
        """Get relationships with filters"""
        try:
            # For now, get all relationships from the registry and filter
            # This could be optimized later with more sophisticated querying
            all_relationships = await self.relationship_repo.get_relationships_by_twin(registry_id, "", None)
            
            # Apply filters
            filtered_relationships = []
            for rel in all_relationships:
                if query.source_twin_id and rel.source_twin_id != query.source_twin_id:
                    continue
                if query.target_twin_id and rel.target_twin_id != query.target_twin_id:
                    continue
                if query.relationship_type and rel.relationship_type != query.relationship_type:
                    continue
                if query.is_active is not None and rel.is_active != query.is_active:
                    continue
                if query.created_after and rel.created_at < query.created_after:
                    continue
                if query.created_before and rel.created_at > query.created_before:
                    continue
                
                filtered_relationships.append(rel)
            
            return filtered_relationships
            
        except Exception as e:
            logger.error(f"Failed to query relationships: {e}")
            return []
    
    async def update_relationship(
        self,
        registry_id: str,
        relationship_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[TwinRelationship]:
        """Update a relationship"""
        try:
            # Get current relationship
            current = await self.relationship_repo.get_relationship(registry_id, relationship_id)
            if not current:
                logger.warning(f"Relationship {relationship_id} not found")
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(current, key):
                    setattr(current, key, value)
            
            # Update timestamp
            current.updated_at = datetime.now()
            
            # Save to database
            await self.relationship_repo.update(registry_id, relationship_id, update_data)
            
            logger.info(f"Updated relationship {relationship_id}")
            return current
            
        except Exception as e:
            logger.error(f"Failed to update relationship {relationship_id}: {e}")
            return None
    
    async def delete_relationship(self, registry_id: str, relationship_id: str) -> bool:
        """Delete a relationship"""
        try:
            result = await self.relationship_repo.delete(registry_id, relationship_id)
            if result:
                logger.info(f"Deleted relationship {relationship_id}")
            else:
                logger.warning(f"Relationship {relationship_id} not found or already deleted")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete relationship {relationship_id}: {e}")
            return False
    
    # ==================== Relationship Queries ====================
    
    async def get_relationships_by_type(self, registry_id: str, relationship_type: str) -> List[TwinRelationship]:
        """Get all relationships of a specific type"""
        try:
            query = TwinRelationshipQuery(relationship_type=relationship_type)
            return await self.get_relationships(registry_id, query)
        except Exception as e:
            logger.error(f"Failed to get relationships by type {relationship_type}: {e}")
            return []
    
    async def get_active_relationships(self, registry_id: str) -> List[TwinRelationship]:
        """Get all active relationships"""
        try:
            query = TwinRelationshipQuery(is_active=True)
            return await self.get_relationships(registry_id, query)
        except Exception as e:
            logger.error(f"Failed to get active relationships: {e}")
            return []
    
    async def get_relationships_in_date_range(
        self,
        registry_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[TwinRelationship]:
        """Get relationships created within a date range"""
        try:
            # This would need to be enhanced with proper date filtering
            # For now, get all sync history and filter
            all_relationships = await self.relationship_repo.get_relationships_by_twin(registry_id, "", None)
            
            filtered_relationships = []
            for rel in all_relationships:
                if start_date <= rel.created_at <= end_date:
                    filtered_relationships.append(rel)
            
            return filtered_relationships
            
        except Exception as e:
            logger.error(f"Failed to get relationships in date range: {e}")
            return []
    
    # ==================== Relationship Analytics ====================
    
    async def get_relationship_summary(self, registry_id: str) -> TwinRelationshipSummary:
        """Get relationship statistics and summary"""
        try:
            return await self.relationship_repo.get_relationship_summary(registry_id)
        except Exception as e:
            logger.error(f"Failed to get relationship summary: {e}")
            return TwinRelationshipSummary(
                total_relationships=0,
                active_relationships=0,
                relationship_types={},
                source_twins=[],
                target_twins=[]
            )
    
    async def get_relationship_graph(self, registry_id: str) -> Dict[str, Any]:
        """Get relationship graph data for visualization"""
        try:
            relationships = await self.relationship_repo.get_relationship_summary(registry_id)
            
            # Build graph structure
            nodes = set()
            edges = []
            
            # Add all twins as nodes
            for twin_id in relationships.source_twins:
                nodes.add(twin_id)
            for twin_id in relationships.target_twins:
                nodes.add(twin_id)
            
            # Convert to list format
            nodes_list = [{"id": twin_id, "type": "twin"} for twin_id in nodes]
            
            return {
                "nodes": nodes_list,
                "edges": edges,  # Could be enhanced to include actual relationship data
                "summary": {
                    "total_nodes": len(nodes),
                    "total_relationships": relationships.total_relationships,
                    "active_relationships": relationships.active_relationships
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get relationship graph: {e}")
            return {"nodes": [], "edges": [], "summary": {}}
    
    # ==================== Bulk Operations ====================
    
    async def create_multiple_relationships(
        self,
        registry_id: str,
        relationships_data: List[Dict[str, Any]]
    ) -> List[TwinRelationship]:
        """Create multiple relationships at once"""
        try:
            created_relationships = []
            
            for rel_data in relationships_data:
                relationship = await self.create_relationship(
                    registry_id=registry_id,
                    source_twin_id=rel_data["source_twin_id"],
                    target_twin_id=rel_data["target_twin_id"],
                    relationship_type=rel_data["relationship_type"],
                    relationship_data=rel_data.get("relationship_data"),
                    metadata=rel_data.get("metadata")
                )
                created_relationships.append(relationship)
            
            logger.info(f"Created {len(created_relationships)} relationships in registry {registry_id}")
            return created_relationships
            
        except Exception as e:
            logger.error(f"Failed to create multiple relationships: {e}")
            raise
    
    async def deactivate_relationships_by_twin(self, registry_id: str, twin_id: str) -> int:
        """Deactivate all relationships for a specific twin"""
        try:
            # Get all relationships for the twin
            relationships = await self.get_relationships_by_twin(registry_id, twin_id)
            
            # Deactivate each relationship
            deactivated_count = 0
            for relationship in relationships:
                relationship.deactivate()
                await self.relationship_repo.update_relationship(registry_id, relationship)
                deactivated_count += 1
            
            logger.info(f"Deactivated {deactivated_count} relationships for twin {twin_id} in registry {registry_id}")
            return deactivated_count
            
        except Exception as e:
            logger.error(f"Failed to deactivate relationships for twin {twin_id}: {e}")
            return 0
    
    # ==================== Enhanced Query Methods ====================
    
    async def get_all_relationships(self) -> List[Dict[str, Any]]:
        """
        Get all relationships across all registries.
        This method provides the interface expected by the webapp service.
        
        Returns:
            List of relationship dictionaries
        """
        try:
            logger.info("Getting all relationships across all registries")
            
            # Import the registry repository to get all registries
            from ..repositories.twin_registry_repository import TwinRegistryRepository
            registry_repo = TwinRegistryRepository(self.db_manager)
            
            # Get all registries
            all_registries = await registry_repo.get_all()
            
            all_relationships = []
            for registry in all_registries:
                try:
                    # Get all relationships for this registry (not filtered by twin_id)
                    registry_relationships = await self.relationship_repo.get_active_relationships(registry.registry_id)
                    
                    for rel in registry_relationships:
                        relationship_dict = {
                            "relationship_id": rel.id,
                            "source_twin_id": rel.source_twin_id,
                            "source_twin_name": registry.twin_name,
                            "target_twin_id": rel.target_twin_id,
                            "relationship_type": rel.relationship_type,
                            "description": rel.relationship_data.get("description", "") if rel.relationship_data else "",
                            "created_at": rel.created_at.isoformat() if rel.created_at else "",
                            "is_active": rel.is_active,
                            "registry_type": registry.registry_type,
                            "metadata": rel.relationship_metadata
                        }
                        all_relationships.append(relationship_dict)
                        
                except Exception as e:
                    logger.warning(f"Failed to get relationships for registry {registry.registry_id}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(all_relationships)} relationships from all registries")
            return all_relationships
            
        except Exception as e:
            logger.error(f"Failed to get all relationships: {e}")
            raise 