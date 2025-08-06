"""
Twin Relationship Repository

Data access layer for managing twin relationships.
"""

from src.shared.repositories.base_repository import BaseRepository
from src.shared.database.connection_manager import DatabaseConnectionManager
from ..models.twin_relationship import TwinRelationship, TwinRelationshipQuery, TwinRelationshipSummary
from typing import List, Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class TwinRelationshipRepository(BaseRepository):
    """Repository for managing twin relationships"""
    
    def __init__(self):
        super().__init__()
        self.table_name = "twin_relationships"
    
    async def create_table(self) -> None:
        """Create the twin_relationships table if it doesn't exist"""
        query = """
        CREATE TABLE IF NOT EXISTS twin_relationships (
            relationship_id TEXT PRIMARY KEY,
            source_twin_id TEXT NOT NULL,
            target_twin_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            relationship_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (source_twin_id) REFERENCES digital_twins(twin_id),
            FOREIGN KEY (target_twin_id) REFERENCES digital_twins(twin_id)
        )
        """
        await self.execute_query(query)
        logger.info(f"Created table {self.table_name}")
    
    async def create_relationship(self, relationship: TwinRelationship) -> TwinRelationship:
        """Create a new twin relationship"""
        query = """
        INSERT INTO twin_relationships (
            relationship_id, source_twin_id, target_twin_id, relationship_type,
            relationship_data, created_at, updated_at, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            relationship.relationship_id,
            relationship.source_twin_id,
            relationship.target_twin_id,
            relationship.relationship_type,
            json.dumps(relationship.relationship_data or {}),
            relationship.created_at.isoformat(),
            relationship.updated_at.isoformat() if relationship.updated_at else relationship.created_at.isoformat(),
            relationship.is_active
        )
        
        await self.execute_query(query, values)
        logger.info(f"Created relationship {relationship.relationship_id}")
        return relationship
    
    async def get_relationship(self, relationship_id: str) -> Optional[TwinRelationship]:
        """Get a relationship by ID"""
        query = "SELECT * FROM twin_relationships WHERE relationship_id = ?"
        result = await self.fetch_one(query, (relationship_id,))
        
        if result:
            return self._row_to_relationship(result)
        return None
    
    async def get_relationships_by_twin(self, twin_id: str, query: Optional[TwinRelationshipQuery] = None) -> List[TwinRelationship]:
        """Get all relationships for a twin (as source or target)"""
        base_query = """
        SELECT * FROM twin_relationships 
        WHERE (source_twin_id = ? OR target_twin_id = ?)
        """
        params = [twin_id, twin_id]
        
        if query:
            if query.relationship_type:
                base_query += " AND relationship_type = ?"
                params.append(query.relationship_type)
            if query.is_active is not None:
                base_query += " AND is_active = ?"
                params.append(query.is_active)
            if query.created_after:
                base_query += " AND created_at >= ?"
                params.append(query.created_after.isoformat())
            if query.created_before:
                base_query += " AND created_at <= ?"
                params.append(query.created_before.isoformat())
        
        base_query += " ORDER BY created_at DESC"
        
        results = await self.fetch_all(base_query, tuple(params))
        return [self._row_to_relationship(row) for row in results]
    
    async def get_relationships(self, query: TwinRelationshipQuery) -> List[TwinRelationship]:
        """Get relationships with filtering"""
        base_query = "SELECT * FROM twin_relationships WHERE 1=1"
        params = []
        
        if query.source_twin_id:
            base_query += " AND source_twin_id = ?"
            params.append(query.source_twin_id)
        if query.target_twin_id:
            base_query += " AND target_twin_id = ?"
            params.append(query.target_twin_id)
        if query.relationship_type:
            base_query += " AND relationship_type = ?"
            params.append(query.relationship_type)
        if query.is_active is not None:
            base_query += " AND is_active = ?"
            params.append(query.is_active)
        if query.created_after:
            base_query += " AND created_at >= ?"
            params.append(query.created_after.isoformat())
        if query.created_before:
            base_query += " AND created_at <= ?"
            params.append(query.created_before.isoformat())
        
        base_query += " ORDER BY created_at DESC"
        
        results = await self.fetch_all(base_query, tuple(params))
        return [self._row_to_relationship(row) for row in results]
    
    async def update_relationship(self, relationship: TwinRelationship) -> TwinRelationship:
        """Update a relationship"""
        query = """
        UPDATE twin_relationships SET
            relationship_type = ?,
            relationship_data = ?,
            updated_at = ?,
            is_active = ?
        WHERE relationship_id = ?
        """
        values = (
            relationship.relationship_type,
            json.dumps(relationship.relationship_data or {}),
            relationship.updated_at.isoformat() if relationship.updated_at else relationship.created_at.isoformat(),
            relationship.is_active,
            relationship.relationship_id
        )
        
        await self.execute_query(query, values)
        logger.info(f"Updated relationship {relationship.relationship_id}")
        return relationship
    
    async def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship"""
        query = "DELETE FROM twin_relationships WHERE relationship_id = ?"
        result = await self.execute_query(query, (relationship_id,))
        logger.info(f"Deleted relationship {relationship_id}")
        return result.rowcount > 0
    
    async def get_relationship_summary(self) -> TwinRelationshipSummary:
        """Get relationship statistics"""
        # Total relationships
        total_query = "SELECT COUNT(*) as count FROM twin_relationships"
        total_result = await self.fetch_one(total_query)
        total_relationships = total_result['count'] if total_result else 0
        
        # Active relationships
        active_query = "SELECT COUNT(*) as count FROM twin_relationships WHERE is_active = TRUE"
        active_result = await self.fetch_one(active_query)
        active_relationships = active_result['count'] if active_result else 0
        
        # Relationships by type
        type_query = "SELECT relationship_type, COUNT(*) as count FROM twin_relationships GROUP BY relationship_type"
        type_results = await self.fetch_all(type_query)
        relationship_types = {row['relationship_type']: row['count'] for row in type_results}
        
        # Source twins
        source_query = "SELECT DISTINCT source_twin_id FROM twin_relationships"
        source_results = await self.fetch_all(source_query)
        source_twins = [row['source_twin_id'] for row in source_results]
        
        # Target twins
        target_query = "SELECT DISTINCT target_twin_id FROM twin_relationships"
        target_results = await self.fetch_all(target_query)
        target_twins = [row['target_twin_id'] for row in target_results]
        
        return TwinRelationshipSummary(
            total_relationships=total_relationships,
            active_relationships=active_relationships,
            relationship_types=relationship_types,
            source_twins=source_twins,
            target_twins=target_twins
        )
    
    def _row_to_relationship(self, row: Dict[str, Any]) -> TwinRelationship:
        """Convert database row to TwinRelationship model"""
        from datetime import datetime
        
        return TwinRelationship(
            relationship_id=row['relationship_id'],
            source_twin_id=row['source_twin_id'],
            target_twin_id=row['target_twin_id'],
            relationship_type=row['relationship_type'],
            relationship_data=json.loads(row['relationship_data']) if row['relationship_data'] else {},
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            is_active=bool(row['is_active'])
        ) 