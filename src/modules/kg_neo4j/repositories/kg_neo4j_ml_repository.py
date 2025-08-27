"""
Knowledge Graph Neo4j ML Registry Repository

Pure async implementation using src.engine.database.connection_manager.
Provides data access layer for ML training registry operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from src.engine.database.connection_manager import ConnectionManager
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
        self.table_name = "kg_neo4j_ml_registry"
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
            # Convert model to dict for insertion
            data = ml_registry.dict()
            
            # Build INSERT query dynamically
            columns = list(data.keys())
            placeholders = [f":{col}" for col in columns]
            
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            # Execute raw SQL
            await self.connection_manager.execute_update(query, data)
            
            # Get the created record ID (this would need to be handled differently with execute_update)
            # For now, we'll return the registry as is
            logger.info(f"Created ML registry entry: {ml_registry.ml_registry_id}")
            return ml_registry
            
        except Exception as e:
            logger.error(f"Failed to create ML registry entry: {e}")
            raise
    
    async def get_by_id(self, ml_registry_id: str) -> Optional[KGNeo4jMLRegistry]:
        """Get ML registry entry by ID asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ml_registry_id = :ml_registry_id"
            result = await self.connection_manager.execute_query(query, {"ml_registry_id": ml_registry_id})
            
            if result and len(result) > 0:
                return KGNeo4jMLRegistry(**result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get ML registry entry by ID {ml_registry_id}: {e}")
            raise
    
    async def get_by_graph_id(self, graph_id: str) -> List[KGNeo4jMLRegistry]:
        """Get all ML registry entries for a specific graph asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE graph_id = :graph_id"
            result = await self.connection_manager.execute_query(query, {"graph_id": graph_id})
            
            return [KGNeo4jMLRegistry(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get ML registry entries for graph {graph_id}: {e}")
            raise
    
    async def get_by_model_type(self, model_type: str) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries by model type asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE model_type = :model_type"
            result = await self.connection_manager.execute_query(query, {"model_type": model_type})
            
            return [KGNeo4jMLRegistry(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by model type {model_type}: {e}")
            raise
    
    async def get_by_training_status(self, training_status: str) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries by training status asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE training_status = :training_status"
            result = await self.connection_manager.execute_query(query, {"training_status": training_status})
            
            return [KGNeo4jMLRegistry(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by training status {training_status}: {e}")
            raise
    
    async def get_by_deployment_status(self, deployment_status: str) -> List[KGNeo4jMLRegistry]:
        """Get ML registry entries by deployment status asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE deployment_status = :deployment_status"
            result = await self.connection_manager.execute_query(query, {"deployment_status": deployment_status})
            
            return [KGNeo4jMLRegistry(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get ML registry entries by deployment status {deployment_status}: {e}")
            raise
    
    async def update(self, ml_registry: KGNeo4jMLRegistry) -> KGNeo4jMLRegistry:
        """Update an existing ML registry entry asynchronously"""
        try:
            # Update timestamp
            ml_registry.updated_at = datetime.now(timezone.utc)
            
            # Convert model to dict for update
            data = ml_registry.dict(exclude={'ml_registry_id'})
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in data.keys()]
            query = f"""
                UPDATE {self.table_name} 
                SET {', '.join(set_clauses)}
                WHERE ml_registry_id = :ml_registry_id
            """
            
            # Add ml_registry_id to params
            params = {**data, "ml_registry_id": ml_registry.ml_registry_id}
            
            # Execute raw SQL
            await self.connection_manager.execute_update(query, params)
            
            logger.info(f"Updated ML registry entry: {ml_registry.ml_registry_id}")
            return ml_registry
            
        except Exception as e:
            logger.error(f"Failed to update ML registry entry {ml_registry.ml_registry_id}: {e}")
            raise
    
    async def delete(self, ml_registry_id: str) -> bool:
        """Delete an ML registry entry asynchronously"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE ml_registry_id = :ml_registry_id"
            await self.connection_manager.execute_update(query, {"ml_registry_id": ml_registry_id})
            
            logger.info(f"Deleted ML registry entry: {ml_registry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete ML registry entry {ml_registry_id}: {e}")
            raise
    
    # ==================== Query Operations ====================
    
    async def query(self, query_params: KGNeo4jMLRegistryQuery) -> List[KGNeo4jMLRegistry]:
        """Query ML registry entries with filters asynchronously"""
        try:
            # Build query with filters
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            params = {}
            
            if query_params.graph_id:
                query += " AND graph_id = :graph_id"
                params["graph_id"] = query_params.graph_id
            if query_params.model_type:
                query += " AND model_type = :model_type"
                params["model_type"] = query_params.model_type
            if query_params.training_status:
                query += " AND training_status = :training_status"
                params["training_status"] = query_params.training_status
            if query_params.deployment_status:
                query += " AND deployment_status = :deployment_status"
                params["deployment_status"] = query_params.deployment_status
            if query_params.user_id:
                query += " AND user_id = :user_id"
                params["user_id"] = query_params.user_id
            if query_params.org_id:
                query += " AND org_id = :org_id"
                params["org_id"] = query_params.org_id
            if query_params.dept_id:
                query += " AND dept_id = :dept_id"
                params["dept_id"] = query_params.dept_id
            
            # Add pagination
            query += " LIMIT :limit OFFSET :offset"
            params["limit"] = query_params.limit
            params["offset"] = query_params.offset
            
            result = await self.connection_manager.execute_query(query, params)
            
            return [KGNeo4jMLRegistry(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to query ML registry entries: {e}")
            raise
    
    async def get_total_count(self) -> int:
        """Get total count of ML registry entries asynchronously"""
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            result = await self.connection_manager.execute_query(query, {})
            return result[0]['total'] if result and len(result) > 0 else 0
            
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
            query = f"SELECT * FROM {self.table_name} WHERE final_accuracy BETWEEN :min_accuracy AND :max_accuracy"
            result = await self.connection_manager.execute_query(query, {"min_accuracy": min_accuracy, "max_accuracy": max_accuracy})
            
            return [KGNeo4jMLRegistry(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get models by accuracy range: {e}")
            raise
    
    async def get_models_by_user(self, user_id: str, org_id: str, dept_id: Optional[str] = None) -> List[KGNeo4jMLRegistry]:
        """Get models by user with optional department filter asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE user_id = :user_id AND org_id = :org_id"
            params = {"user_id": user_id, "org_id": org_id}
            
            if dept_id:
                query += " AND dept_id = :dept_id"
                params["dept_id"] = dept_id
            
            result = await self.connection_manager.execute_query(query, params)
            
            return [KGNeo4jMLRegistry(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get models by user {user_id}: {e}")
            raise
    
    # ==================== Summary & Analytics ====================
    
    async def get_summary(self) -> KGNeo4jMLRegistrySummary:
        """Get comprehensive summary of ML registry asynchronously"""
        try:
            # Get total models
            total_query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            total_result = await self.connection_manager.execute_query(total_query, {})
            total_models = total_result[0]['total'] if total_result and len(total_result) > 0 else 0
            
            # Get active training sessions
            active_query = f"SELECT COUNT(*) as total FROM {self.table_name} WHERE training_status = :status"
            active_result = await self.connection_manager.execute_query(active_query, {"status": "in_progress"})
            active_sessions = active_result[0]['total'] if active_result and len(active_result) > 0 else 0
            
            # Get completed models
            completed_query = f"SELECT COUNT(*) as total FROM {self.table_name} WHERE training_status = :status"
            completed_result = await self.connection_manager.execute_query(completed_query, {"status": "completed"})
            completed_models = completed_result[0]['total'] if completed_result and len(completed_result) > 0 else 0
            
            # Get deployed models
            deployed_query = f"SELECT COUNT(*) as total FROM {self.table_name} WHERE deployment_status = :status"
            deployed_result = await self.connection_manager.execute_query(deployed_query, {"status": "deployed"})
            deployed_models = deployed_result[0]['total'] if deployed_result and len(deployed_result) > 0 else 0
            
            # Calculate average accuracy
            accuracy_query = f"SELECT final_accuracy FROM {self.table_name} WHERE final_accuracy IS NOT NULL"
            accuracy_result = await self.connection_manager.execute_query(accuracy_query, {})
            
            if accuracy_result:
                avg_accuracy = sum(row['final_accuracy'] for row in accuracy_result if 'final_accuracy' in row and row['final_accuracy']) / len(accuracy_result)
            else:
                avg_accuracy = 0.0
            
            # Calculate average training duration
            duration_query = f"SELECT training_duration_seconds FROM {self.table_name} WHERE training_duration_seconds IS NOT NULL"
            duration_result = await self.connection_manager.execute_query(duration_query, {})
            
            if duration_result:
                avg_duration = sum(row['training_duration_seconds'] for row in duration_result if 'training_duration_seconds' in row and row['training_duration_seconds']) / len(duration_result)
            else:
                avg_duration = 0.0
            
            # Get model type distribution
            type_query = f"SELECT model_type FROM {self.table_name}"
            type_result = await self.connection_manager.execute_query(type_query, {})
            
            type_distribution = {}
            for row in type_result:
                model_type = row['model_type'] if 'model_type' in row else 'unknown'
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


