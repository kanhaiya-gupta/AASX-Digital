"""
Knowledge Graph Registry Repository

Pure async implementation using src.engine.database.connection_manager.
Provides data access layer for knowledge graph registry operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.schema.modules.kg_neo4j import kg_graph_registry
from ..models.kg_graph_registry import (
    KGGraphRegistry,
    KGGraphRegistryQuery,
    KGGraphRegistrySummary
)

logger = logging.getLogger(__name__)


class KGGraphRegistryRepository:
    """Repository for managing knowledge graph registry data with pure async support."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the knowledge graph registry repository."""
        self.connection_manager = connection_manager
        self.table = kg_graph_registry
        logger.info("Knowledge Graph Registry Repository initialized with pure async support")
    
    async def initialize(self) -> None:
        """Initialize the repository asynchronously."""
        try:
            # Verify connection
            await self.connection_manager.get_connection()
            logger.info("Knowledge Graph Registry Repository initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Graph Registry Repository: {e}")
            raise
    
    # ==================== CRUD Operations ====================
    
    async def create(self, registry: KGGraphRegistry) -> KGGraphRegistry:
        """Create a new graph registry entry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Convert model to dict for insertion
                data = registry.dict()
                
                # Insert into database
                query = self.table.insert()
                result = await conn.execute(query, data)
                
                # Get the created record
                created_id = result.inserted_primary_key[0]
                registry.graph_id = str(created_id)
                
                logger.info(f"Created graph registry entry: {registry.graph_id}")
                return registry
                
        except Exception as e:
            logger.error(f"Failed to create graph registry entry: {e}")
            raise
    
    async def get_by_id(self, graph_id: str) -> Optional[KGGraphRegistry]:
        """Get graph registry entry by ID asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.graph_id == graph_id)
                result = await conn.execute(query)
                row = result.fetchone()
                
                if row:
                    return KGGraphRegistry(**dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Failed to get graph registry entry by ID {graph_id}: {e}")
            raise
    
    async def get_by_file_id(self, file_id: str) -> List[KGGraphRegistry]:
        """Get graph registry entries by file ID asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.file_id == file_id)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get graph registry entries for file {file_id}: {e}")
            raise
    
    async def get_by_workflow_source(self, workflow_source: str) -> List[KGGraphRegistry]:
        """Get graph registry entries by workflow source asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.workflow_source == workflow_source)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get graph registry entries by workflow source {workflow_source}: {e}")
            raise
    
    async def get_by_user(self, user_id: str, org_id: str, dept_id: Optional[str] = None) -> List[KGGraphRegistry]:
        """Get graph registry entries by user with optional department filter asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(
                    (self.table.c.user_id == user_id) & 
                    (self.table.c.org_id == org_id)
                )
                
                if dept_id:
                    query = query.where(self.table.c.dept_id == dept_id)
                
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get graph registry entries by user {user_id}: {e}")
            raise
    
    async def get_by_health_status(self, health_status: str) -> List[KGGraphRegistry]:
        """Get graph registry entries by health status asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.health_status == health_status)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get graph registry entries by health status {health_status}: {e}")
            raise
    
    async def get_by_integration_status(self, integration_status: str) -> List[KGGraphRegistry]:
        """Get graph registry entries by integration status asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.integration_status == integration_status)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get graph registry entries by integration status {integration_status}: {e}")
            raise
    
    async def update(self, registry: KGGraphRegistry) -> KGGraphRegistry:
        """Update an existing graph registry entry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Update timestamp
                registry.updated_at = datetime.now(timezone.utc)
                
                # Convert model to dict for update
                data = registry.dict(exclude={'graph_id'})
                
                # Update in database
                query = self.table.update().where(
                    self.table.c.graph_id == registry.graph_id
                )
                await conn.execute(query, data)
                
                logger.info(f"Updated graph registry entry: {registry.graph_id}")
                return registry
                
        except Exception as e:
            logger.error(f"Failed to update graph registry entry {registry.graph_id}: {e}")
            raise
    
    async def delete(self, graph_id: str) -> bool:
        """Delete a graph registry entry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.delete().where(self.table.c.graph_id == graph_id)
                result = await conn.execute(query)
                
                deleted = result.rowcount > 0
                if deleted:
                    logger.info(f"Deleted graph registry entry: {graph_id}")
                else:
                    logger.warning(f"Graph registry entry not found for deletion: {graph_id}")
                
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to delete graph registry entry {graph_id}: {e}")
            raise
    
    # ==================== Query Operations ====================
    
    async def query(self, query_params: KGGraphRegistryQuery) -> List[KGGraphRegistry]:
        """Query graph registry entries with filters asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Build query with filters
                query = self.table.select()
                
                if query_params.graph_category:
                    query = query.where(self.table.c.graph_category == query_params.graph_category)
                if query_params.graph_type:
                    query = query.where(self.table.c.graph_type == query_params.graph_type)
                if query_params.workflow_source:
                    query = query.where(self.table.c.workflow_source == query_params.workflow_source)
                if query_params.integration_status:
                    query = query.where(self.table.c.integration_status == query_params.integration_status)
                if query_params.health_status:
                    query = query.where(self.table.c.health_status == query_params.health_status)
                if query_params.user_id:
                    query = query.where(self.table.c.user_id == query_params.user_id)
                if query_params.org_id:
                    query = query.where(self.table.c.org_id == query_params.org_id)
                
                # Add pagination
                query = query.limit(query_params.limit).offset(query_params.offset)
                
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to query graph registry entries: {e}")
            raise
    
    async def get_total_count(self) -> int:
        """Get total count of graph registry entries asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select()
                result = await conn.execute(query)
                rows = result.fetchall()
                return len(rows)
                
        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            raise
    
    # ==================== Business Logic Operations ====================
    
    async def get_active_graphs(self) -> List[KGGraphRegistry]:
        """Get all active graphs asynchronously"""
        try:
            return await self.get_by_integration_status("active")
        except Exception as e:
            logger.error(f"Failed to get active graphs: {e}")
            raise
    
    async def get_healthy_graphs(self) -> List[KGGraphRegistry]:
        """Get all healthy graphs asynchronously"""
        try:
            return await self.get_by_health_status("healthy")
        except Exception as e:
            logger.error(f"Failed to get healthy graphs: {e}")
            raise
    
    async def get_graphs_by_category(self, category: str) -> List[KGGraphRegistry]:
        """Get graphs by category asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.graph_category == category)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get graphs by category {category}: {e}")
            raise
    
    async def get_graphs_by_priority(self, priority: str) -> List[KGGraphRegistry]:
        """Get graphs by priority asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.graph_priority == priority)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get graphs by priority {priority}: {e}")
            raise
    
    # ==================== Summary & Analytics ====================
    
    async def get_summary(self) -> KGGraphRegistrySummary:
        """Get comprehensive summary of graph registry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Get total graphs
                total_query = self.table.select()
                total_result = await conn.execute(total_query)
                total_graphs = len(total_result.fetchall())
                
                # Get active graphs
                active_query = self.table.select().where(self.table.c.integration_status == "active")
                active_result = await conn.execute(active_query)
                active_graphs = len(active_result.fetchall())
                
                # Get healthy graphs
                healthy_query = self.table.select().where(self.table.c.health_status == "healthy")
                healthy_result = await conn.execute(healthy_query)
                healthy_graphs = len(healthy_result.fetchall())
                
                # Calculate total nodes and relationships
                nodes_query = self.table.select(self.table.c.total_nodes)
                nodes_result = await conn.execute(nodes_query)
                nodes_rows = nodes_result.fetchall()
                
                total_nodes = sum(row.total_nodes for row in nodes_rows if row.total_nodes)
                
                rels_query = self.table.select(self.table.c.total_relationships)
                rels_result = await conn.execute(rels_query)
                rels_rows = rels_result.fetchall()
                
                total_relationships = sum(row.total_relationships for row in rels_rows if row.total_relationships)
                
                # Get graphs by category
                category_query = self.table.select(self.table.c.graph_category)
                category_result = await conn.execute(category_query)
                category_rows = category_result.fetchall()
                
                graphs_by_category = {}
                for row in category_rows:
                    category = row.graph_category
                    graphs_by_category[category] = graphs_by_category.get(category, 0) + 1
                
                # Get graphs by status
                status_query = self.table.select(self.table.c.integration_status)
                status_result = await conn.execute(status_query)
                status_rows = status_result.fetchall()
                
                graphs_by_status = {}
                for row in status_rows:
                    status = row.integration_status
                    graphs_by_status[status] = graphs_by_status.get(status, 0) + 1
                
                return KGGraphRegistrySummary(
                    total_graphs=total_graphs,
                    active_graphs=active_graphs,
                    healthy_graphs=healthy_graphs,
                    total_nodes=total_nodes,
                    total_relationships=total_relationships,
                    graphs_by_category=graphs_by_category,
                    graphs_by_status=graphs_by_status
                )
                
        except Exception as e:
            logger.error(f"Failed to get graph registry summary: {e}")
            raise
    
    # ==================== Cleanup ====================
    
    async def cleanup(self) -> None:
        """Cleanup repository resources asynchronously"""
        try:
            logger.info("Knowledge Graph Registry Repository cleanup completed")
        except Exception as e:
            logger.error(f"Failed to cleanup Knowledge Graph Registry Repository: {e}")
            raise
