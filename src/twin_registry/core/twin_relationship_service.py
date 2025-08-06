"""
Twin Relationship Service

Manages relationships between digital twins including:
- Creating relationships between twins
- Querying relationship networks
- Managing relationship metadata
- Relationship analytics and insights
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.shared.services.base_service import BaseService
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.twin_registry.models.twin_relationship import TwinRelationship
from src.twin_registry.repositories.twin_relationship_repository import TwinRelationshipRepository

logger = logging.getLogger(__name__)


class TwinRelationshipService(BaseService):
    """
    Service for managing relationships between digital twins.
    
    Provides functionality for:
    - Creating and managing twin relationships
    - Querying relationship networks
    - Relationship analytics and insights
    - Relationship validation and constraints
    """
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize the twin relationship service."""
        super().__init__(db_manager)
        self.relationship_repo = TwinRelationshipRepository(db_manager)
        logger.info("Twin Relationship Service initialized")
    
    async def initialize(self) -> None:
        """Initialize the relationship service."""
        try:
            await self.relationship_repo.initialize()
            logger.info("Twin Relationship Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twin Relationship Service: {e}")
            raise
    
    async def create_relationship(
        self,
        source_twin_id: str,
        target_twin_id: str,
        relationship_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a relationship between two digital twins.
        
        Args:
            source_twin_id: ID of the source twin
            target_twin_id: ID of the target twin
            relationship_type: Type of relationship (e.g., 'contains', 'depends_on', 'communicates_with')
            metadata: Additional relationship metadata
            created_by: User who created the relationship
            
        Returns:
            Dictionary with relationship details and status
        """
        try:
            logger.info(f"Creating relationship: {source_twin_id} -> {target_twin_id} ({relationship_type})")
            
            # Validate relationship
            validation_result = await self._validate_relationship(
                source_twin_id, target_twin_id, relationship_type
            )
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "relationship": None
                }
            
            # Create relationship
            relationship = TwinRelationship(
                source_twin_id=source_twin_id,
                target_twin_id=target_twin_id,
                relationship_type=relationship_type,
                metadata=metadata or {},
                created_by=created_by,
                created_at=datetime.utcnow().isoformat()
            )
            
            # Save to database
            saved_relationship = await self.relationship_repo.create(relationship)
            
            return {
                "success": True,
                "relationship": self._convert_relationship_to_dict(saved_relationship),
                "message": "Relationship created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            return {
                "success": False,
                "error": str(e),
                "relationship": None
            }
    
    async def get_relationships(
        self,
        twin_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both"
    ) -> Dict[str, Any]:
        """
        Get relationships for a specific twin.
        
        Args:
            twin_id: ID of the twin
            relationship_type: Filter by relationship type
            direction: 'incoming', 'outgoing', or 'both'
            
        Returns:
            Dictionary with relationships and metadata
        """
        try:
            logger.info(f"Getting relationships for twin: {twin_id}")
            
            relationships = await self.relationship_repo.get_relationships(
                twin_id, relationship_type, direction
            )
            
            return {
                "success": True,
                "relationships": [self._convert_relationship_to_dict(r) for r in relationships],
                "count": len(relationships),
                "twin_id": twin_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get relationships: {e}")
            return {
                "success": False,
                "error": str(e),
                "relationships": [],
                "count": 0
            }
    
    async def delete_relationship(self, relationship_id: str) -> Dict[str, Any]:
        """
        Delete a relationship by ID.
        
        Args:
            relationship_id: ID of the relationship to delete
            
        Returns:
            Dictionary with deletion status
        """
        try:
            logger.info(f"Deleting relationship: {relationship_id}")
            
            success = await self.relationship_repo.delete(relationship_id)
            
            return {
                "success": success,
                "message": "Relationship deleted successfully" if success else "Relationship not found",
                "relationship_id": relationship_id
            }
            
        except Exception as e:
            logger.error(f"Failed to delete relationship: {e}")
            return {
                "success": False,
                "error": str(e),
                "relationship_id": relationship_id
            }
    
    async def get_relationship_network(
        self,
        twin_id: str,
        depth: int = 2,
        relationship_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get the relationship network around a twin.
        
        Args:
            twin_id: ID of the central twin
            depth: How many levels deep to traverse
            relationship_types: Filter by relationship types
            
        Returns:
            Dictionary with network graph and metadata
        """
        try:
            logger.info(f"Getting relationship network for twin: {twin_id} (depth: {depth})")
            
            network = await self.relationship_repo.get_network(
                twin_id, depth, relationship_types
            )
            
            return {
                "success": True,
                "network": network,
                "central_twin_id": twin_id,
                "depth": depth,
                "node_count": len(network.get("nodes", [])),
                "edge_count": len(network.get("edges", []))
            }
            
        except Exception as e:
            logger.error(f"Failed to get relationship network: {e}")
            return {
                "success": False,
                "error": str(e),
                "network": {"nodes": [], "edges": []}
            }
    
    async def get_relationship_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about relationships in the registry.
        
        Returns:
            Dictionary with relationship statistics and insights
        """
        try:
            logger.info("Getting relationship analytics")
            
            analytics = await self.relationship_repo.get_analytics()
            
            return {
                "success": True,
                "analytics": analytics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get relationship analytics: {e}")
            return {
                "success": False,
                "error": str(e),
                "analytics": {}
            }
    
    async def _validate_relationship(
        self,
        source_twin_id: str,
        target_twin_id: str,
        relationship_type: str
    ) -> Dict[str, Any]:
        """
        Validate a relationship before creation.
        
        Args:
            source_twin_id: ID of the source twin
            target_twin_id: ID of the target twin
            relationship_type: Type of relationship
            
        Returns:
            Dictionary with validation result
        """
        try:
            # Check if twins exist
            source_exists = await self.relationship_repo.twin_exists(source_twin_id)
            target_exists = await self.relationship_repo.twin_exists(target_twin_id)
            
            if not source_exists:
                return {
                    "valid": False,
                    "error": f"Source twin {source_twin_id} does not exist"
                }
            
            if not target_exists:
                return {
                    "valid": False,
                    "error": f"Target twin {target_twin_id} does not exist"
                }
            
            # Check for self-relationship
            if source_twin_id == target_twin_id:
                return {
                    "valid": False,
                    "error": "Cannot create relationship with self"
                }
            
            # Check for duplicate relationship
            existing = await self.relationship_repo.get_relationship(
                source_twin_id, target_twin_id, relationship_type
            )
            if existing:
                return {
                    "valid": False,
                    "error": f"Relationship already exists: {source_twin_id} -> {target_twin_id} ({relationship_type})"
                }
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            logger.error(f"Relationship validation failed: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def _convert_relationship_to_dict(self, relationship: TwinRelationship) -> Dict[str, Any]:
        """Convert a TwinRelationship object to dictionary."""
        return {
            "id": relationship.id,
            "source_twin_id": relationship.source_twin_id,
            "target_twin_id": relationship.target_twin_id,
            "relationship_type": relationship.relationship_type,
            "metadata": relationship.metadata,
            "created_by": relationship.created_by,
            "created_at": relationship.created_at,
            "updated_at": relationship.updated_at
        } 