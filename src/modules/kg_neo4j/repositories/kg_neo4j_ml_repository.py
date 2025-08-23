"""
Knowledge Graph Neo4j ML Registry Repository

Pure async implementation using src.engine.database.connection_manager.
Provides data access layer for ML training registry operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.schema.modules.kg_neo4j import kg_neo4j_ml_registry
from ..models.kg_neo4j_ml_registry import (
    KGNeo4jMLRegistry,
    KGNeo4jMLRegistryQuery,
    KGNeo4jMLRegistrySummary
)

logger = logging.getLogger(__name__)


class KGNeo4jMLRepository:
    """Repository for ML training registry operations with pure async support"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.table = kg_neo4j_ml_registry
        logger.info("KG Neo4j ML Repository initialized")
    
    async def initialize(self) -> None:
        """Initialize the repository asynchronously"""
        try:
            # Verify connection
            await self.connection_manager.get_connection()
            logger.info("KG Neo4j ML Repository initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize KG Neo4j ML Repository: {e}")
            raise
    
    # ==================== CRUD Operations ====================
    
    async def create(self, ml_registry: KGNeo4jMLRegistry) -> KGNeo4jMLRegistry:
        """Create a new ML registry entry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Convert model to dict for insertion
                data = ml_registry.dict()
                
                # Insert into database
                query = self.table.insert()
                result = await conn.execute(query, data)
                
                # Get the created record
                created_id = result.inserted_primary_key[0]
                ml_registry.ml_registry_id = str(created_id)
                
                logger.info(f"Created ML registry entry: {ml_registry.ml_registry_id}")
                return ml_registry
                
        except Exception as e:
            logger.error(f"Failed to create ML registry entry: {e}")
            raise
    
    async def get_by_id(self, ml_registry_id: str) -> Optional[KGNeo4jMLRegistry]:
        """Get ML registry entry by ID asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.ml_registry_id == ml_registry_id)
                result = await conn.execute(query)
                row = result.fetchone()
                
                if row:
                    return KGNeo4jMLRegistry(**dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Failed to get ML registry entry by ID {ml_registry_id}: {e}")
            raise
    
    async def get_by_graph_id(self, graph_id: str) -> List[KGNeo4jMLRegistry]:
        """Get all ML registry entries for a specific graph asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.graph_id == graph_id)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGNeo4jMLRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get ML registry entries for graph {graph_id}: {e}")
            raise
    
    async def get_by_model_type(self, model_type: str) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries by model type asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.model_type == model_type)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGNeo4jMLRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by model type {model_type}: {e}")
            raise
    
    async def get_by_training_status(self, training_status: str) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries by training status asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.training_status == training_status)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGNeo4jMLRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by training status {training_status}: {e}")
            raise
    
    async def get_by_deployment_status(self, deployment_status: str) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries by deployment status asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.deployment_status == deployment_status)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGNeo4jMLRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by deployment status {deployment_status}: {e}")
            raise
    
    async def update(self, ml_registry: KGNeo4jMLRegistry) -> KGNeo4jMLRegistry:
        """Update an existing ML registry entry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Update timestamp
                ml_registry.updated_at = datetime.now(timezone.utc)
                
                # Convert model to dict for update
                data = ml_registry.dict(exclude={'ml_registry_id'})
                
                # Update in database
                query = self.table.update().where(
                    self.table.c.ml_registry_id == ml_registry.ml_registry_id
                )
                await conn.execute(query, data)
                
                logger.info(f"Updated ML registry entry: {ml_registry.ml_registry_id}")
                return ml_registry
                
        except Exception as e:
            logger.error(f"Failed to update ML registry entry {ml_registry.ml_registry_id}: {e}")
            raise
    
    async def delete(self, ml_registry_id: str) -> bool:
        """Delete an ML registry entry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.delete().where(self.table.c.ml_registry_id == ml_registry_id)
                result = await conn.execute(query)
                
                deleted = result.rowcount > 0
                if deleted:
                    logger.info(f"Deleted ML registry entry: {ml_registry_id}")
                else:
                    logger.warning(f"ML registry entry not found for deletion: {ml_registry_id}")
                
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to delete ML registry entry {ml_registry_id}: {e}")
            raise
    
    # ==================== Query Operations ====================
    
    async def query(self, query_params: KGNeo4jMLRegistryQuery) -> List[KGNeo4jMLRegistry]:
        """Query ML registry entries with filters asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Build query with filters
                query = self.table.select()
                
                if query_params.graph_id:
                    query = query.where(self.table.c.graph_id == query_params.graph_id)
                if query_params.model_type:
                    query = query.where(self.table.c.model_type == query_params.model_type)
                if query_params.training_status:
                    query = query.where(self.table.c.training_status == query_params.training_status)
                if query_params.deployment_status:
                    query = query.where(self.table.c.deployment_status == query_params.deployment_status)
                if query_params.user_id:
                    query = query.where(self.table.c.user_id == query_params.user_id)
                if query_params.org_id:
                    query = query.where(self.table.c.org_id == query_params.org_id)
                if query_params.dept_id:
                    query = query.where(self.table.c.dept_id == query_params.dept_id)
                
                # Add pagination
                query = query.limit(query_params.limit).offset(query_params.offset)
                
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGNeo4jMLRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to query ML registry entries: {e}")
            raise
    
    async def get_total_count(self) -> int:
        """Get total count of ML registry entries asynchronously"""
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
    
    async def get_active_training_sessions(self) -> List[KGNeo4jMLRegistry]:
        """Get all active training sessions asynchronously"""
        try:
            return await self.get_by_training_status("in_progress")
        except Exception as e:
            logger.error(f"Failed to get active training sessions: {e}")
            raise
    
    async def get_completed_models(self) -> List[KGNeo4jMLRegistry]:
        """Get all completed models asynchronously"""
        try:
            return await self.get_by_training_status("completed")
        except Exception as e:
            logger.error(f"Failed to get completed models: {e}")
            raise
    
    async def get_deployed_models(self) -> List[KGNeo4jMLRegistry]:
        """Get all deployed models asynchronously"""
        try:
            return await self.get_by_deployment_status("deployed")
        except Exception as e:
            logger.error(f"Failed to get deployed models: {e}")
            raise
    
    async def get_models_by_accuracy_range(self, min_accuracy: float, max_accuracy: float) -> List[KGNeo4jMLRegistry]:
        """Get models within accuracy range asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(
                    self.table.c.final_accuracy.between(min_accuracy, max_accuracy)
                )
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGNeo4jMLRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get models by accuracy range: {e}")
            raise
    
    async def get_models_by_user(self, user_id: str, org_id: str, dept_id: Optional[str] = None) -> List[KGNeo4jMLRegistry]:
        """Get models by user with optional department filter asynchronously"""
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
                
                return [KGNeo4jMLRegistry(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get models by user {user_id}: {e}")
            raise
    
    # ==================== Summary & Analytics ====================
    
    async def get_summary(self) -> KGNeo4jMLRegistrySummary:
        """Get comprehensive summary of ML registry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Get total models
                total_query = self.table.select()
                total_result = await conn.execute(total_query)
                total_models = len(total_result.fetchall())
                
                # Get active training sessions
                active_query = self.table.select().where(self.table.c.training_status == "in_progress")
                active_result = await conn.execute(active_query)
                active_sessions = len(active_result.fetchall())
                
                # Get completed models
                completed_query = self.table.select().where(self.table.c.training_status == "completed")
                completed_result = await conn.execute(completed_query)
                completed_models = len(completed_result.fetchall())
                
                # Get deployed models
                deployed_query = self.table.select().where(self.table.c.deployment_status == "deployed")
                deployed_result = await conn.execute(deployed_query)
                deployed_models = len(deployed_result.fetchall())
                
                # Calculate average accuracy
                accuracy_query = self.table.select().where(self.table.c.final_accuracy.isnot(None))
                accuracy_result = await conn.execute(accuracy_query)
                accuracy_rows = accuracy_result.fetchall()
                
                if accuracy_rows:
                    avg_accuracy = sum(row.final_accuracy for row in accuracy_rows) / len(accuracy_rows)
                else:
                    avg_accuracy = 0.0
                
                # Calculate average training duration
                duration_query = self.table.select().where(self.table.c.training_duration_seconds.isnot(None))
                duration_result = await conn.execute(duration_query)
                duration_rows = duration_result.fetchall()
                
                if duration_rows:
                    avg_duration = sum(row.training_duration_seconds for row in duration_rows) / len(duration_rows)
                else:
                    avg_duration = 0.0
                
                # Get model type distribution
                type_query = self.table.select(self.table.c.model_type)
                type_result = await conn.execute(type_query)
                type_rows = type_result.fetchall()
                
                type_distribution = {}
                for row in type_rows:
                    model_type = row.model_type
                    type_distribution[model_type] = type_distribution.get(model_type, 0) + 1
                
                # Calculate training success rate
                if total_models > 0:
                    success_rate = completed_models / total_models
                else:
                    success_rate = 0.0
                
                return KGNeo4jMLRegistrySummary(
                    total_models=total_models,
                    active_training_sessions=active_sessions,
                    completed_models=completed_models,
                    deployed_models=deployed_models,
                    avg_model_accuracy=avg_accuracy,
                    avg_training_duration=avg_duration,
                    model_type_distribution=type_distribution,
                    training_success_rate=success_rate
                )
                
        except Exception as e:
            logger.error(f"Failed to get ML registry summary: {e}")
            raise
    
    # ==================== Cleanup ====================
    
    async def cleanup(self) -> None:
        """Cleanup repository resources asynchronously"""
        try:
            logger.info("KG Neo4j ML Repository cleanup completed")
        except Exception as e:
            logger.error(f"Failed to cleanup KG Neo4j ML Repository: {e}")
            raise

