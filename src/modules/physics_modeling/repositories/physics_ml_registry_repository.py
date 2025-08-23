"""
Physics ML Registry Repository

This repository provides data access operations for the physics ML registry table
with integrated enterprise features and async database operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from src.engine.database import ConnectionManager
from src.engine.database.factory import DatabaseFactory
from ..models.physics_ml_registry import PhysicsMLRegistry

logger = logging.getLogger(__name__)


class PhysicsMLRegistryRepository:
    """
    Repository for physics ML registry operations
    
    Provides async CRUD operations and advanced querying capabilities
    for physics ML registry data with enterprise features.
    """
    
    def __init__(self):
        """Initialize the repository with database connection"""
        self.connection_manager: Optional[ConnectionManager] = None
        self.table_name = "physics_ml_registry"
    
    async def initialize(self) -> None:
        """Async initialization of database connection"""
        try:
            self.connection_manager = await DatabaseFactory.create_connection_manager()
            logger.info("Physics ML Registry Repository initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize repository: {e}")
            raise
    
    async def create(self, model: PhysicsMLRegistry) -> Optional[str]:
        """
        Async create a new physics ML registry entry
        
        Args:
            model: PhysicsMLRegistry model instance
            
        Returns:
            Created model ID or None if failed
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            # Prepare data for insertion
            data = model.dict()
            data['created_at'] = datetime.utcnow().isoformat()
            data['updated_at'] = datetime.utcnow().isoformat()
            
            # Execute insert query
            query = f"""
                INSERT INTO {self.table_name} (
                    ml_model_id, model_name, model_type, physics_domain, ml_framework,
                    model_version, description, architecture, hyperparameters, loss_functions,
                    optimization_config, training_status, training_progress, validation_metrics,
                    test_metrics, physics_constraints, conservation_laws, boundary_conditions,
                    initial_conditions, status, lifecycle_stage, created_by, created_at,
                    updated_by, updated_at, ml_compliance_type, ml_compliance_status,
                    ml_compliance_score, ml_security_score, ml_performance_trend,
                    ml_optimization_suggestions, last_ml_optimization_date,
                    enterprise_ml_metrics, model_path, model_size, inference_latency,
                    deployment_status, tags, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                data['ml_model_id'], data['model_name'], data['model_type'],
                data['physics_domain'], data['ml_framework'], data['model_version'],
                data['description'], str(data['architecture']), str(data['hyperparameters']),
                str(data['loss_functions']), str(data['optimization_config']) if data['optimization_config'] else None,
                data['training_status'], data['training_progress'], str(data['validation_metrics']),
                str(data['test_metrics']) if data['test_metrics'] else None,
                str(data['physics_constraints']), str(data['conservation_laws']),
                str(data['boundary_conditions']) if data['boundary_conditions'] else None,
                str(data['initial_conditions']) if data['initial_conditions'] else None,
                data['status'], data['lifecycle_stage'], data['created_by'],
                data['created_at'], data['updated_by'], data['updated_at'],
                data['ml_compliance_type'], data['ml_compliance_status'], data['ml_compliance_score'],
                data['ml_security_score'], data['ml_performance_trend'],
                str(data['ml_optimization_suggestions']) if data['ml_optimization_suggestions'] else None,
                data['last_ml_optimization_date'], str(data['enterprise_ml_metrics']) if data['enterprise_ml_metrics'] else None,
                data['model_path'], data['model_size'], data['inference_latency'],
                data['deployment_status'], str(data['tags']), str(data['metadata'])
            )
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, values)
                await conn.commit()
                
            logger.info(f"Created physics ML registry entry: {model.ml_model_id}")
            return model.ml_model_id
            
        except Exception as e:
            logger.error(f"Failed to create physics ML registry entry: {e}")
            return None
    
    async def get_by_id(self, ml_model_id: str) -> Optional[PhysicsMLRegistry]:
        """
        Async retrieve physics ML registry entry by ID
        
        Args:
            ml_model_id: Unique identifier for the ML model
            
        Returns:
            PhysicsMLRegistry instance or None if not found
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ml_model_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (ml_model_id,))
                row = await cursor.fetchone()
                
            if row:
                return await self._row_to_model(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve physics ML registry entry: {e}")
            return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[PhysicsMLRegistry]:
        """
        Async retrieve all physics ML registry entries with pagination
        
        Args:
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of PhysicsMLRegistry instances
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT ? OFFSET ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (limit, offset))
                rows = await cursor.fetchall()
                
            models = []
            for row in rows:
                model = await self._row_to_model(row)
                if model:
                    models.append(model)
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to retrieve physics ML registry entries: {e}")
            return []
    
    async def update(self, ml_model_id: str, updates: Dict[str, Any]) -> bool:
        """
        Async update physics ML registry entry
        
        Args:
            ml_model_id: Unique identifier for the ML model
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            # Prepare update fields
            update_fields = []
            values = []
            
            for field, value in updates.items():
                if field in ['architecture', 'hyperparameters', 'loss_functions', 'validation_metrics', 
                           'test_metrics', 'physics_constraints', 'conservation_laws', 
                           'ml_optimization_suggestions', 'enterprise_ml_metrics', 'tags', 'metadata']:
                    update_fields.append(f"{field} = ?")
                    values.append(str(value))
                elif field in ['optimization_config', 'boundary_conditions', 'initial_conditions']:
                    if value is not None:
                        update_fields.append(f"{field} = ?")
                        values.append(str(value))
                else:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            values.append(datetime.utcnow().isoformat())
            
            # Add ml_model_id for WHERE clause
            values.append(ml_model_id)
            
            query = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE ml_model_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, values)
                await conn.commit()
                
            logger.info(f"Updated physics ML registry entry: {ml_model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update physics ML registry entry: {e}")
            return False
    
    async def delete(self, ml_model_id: str) -> bool:
        """
        Async delete physics ML registry entry
        
        Args:
            ml_model_id: Unique identifier for the ML model
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"DELETE FROM {self.table_name} WHERE ml_model_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (ml_model_id,))
                await conn.commit()
                
            logger.info(f"Deleted physics ML registry entry: {ml_model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete physics ML registry entry: {e}")
            return False
    
    async def search_by_type(self, model_type: str) -> List[PhysicsMLRegistry]:
        """
        Async search physics ML registry entries by model type
        
        Args:
            model_type: Type of ML model to search for (PINN, hybrid, etc.)
            
        Returns:
            List of matching PhysicsMLRegistry instances
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} WHERE model_type = ? ORDER BY created_at DESC"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (model_type,))
                rows = await cursor.fetchall()
                
            models = []
            for row in rows:
                model = await self._row_to_model(row)
                if model:
                    models.append(model)
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to search physics ML registry entries: {e}")
            return []
    
    async def get_by_training_status(self, training_status: str) -> List[PhysicsMLRegistry]:
        """
        Async get physics ML registry entries by training status
        
        Args:
            training_status: Training status to filter by
            
        Returns:
            List of matching PhysicsMLRegistry instances
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} WHERE training_status = ? ORDER BY created_at DESC"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (training_status,))
                rows = await cursor.fetchall()
                
            models = []
            for row in rows:
                model = await self._row_to_model(row)
                if model:
                    models.append(model)
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to get physics ML registry entries by training status: {e}")
            return []
    
    async def get_by_ml_framework(self, ml_framework: str) -> List[PhysicsMLRegistry]:
        """
        Async get physics ML registry entries by ML framework
        
        Args:
            ml_framework: ML framework to filter by (PyTorch, TensorFlow, etc.)
            
        Returns:
            List of matching PhysicsMLRegistry instances
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ml_framework = ? ORDER BY created_at DESC"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (ml_framework,))
                rows = await cursor.fetchall()
                
            models = []
            for row in rows:
                model = await self._row_to_model(row)
                if model:
                    models.append(model)
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to get physics ML registry entries by ML framework: {e}")
            return []
    
    async def get_by_ml_compliance_status(self, compliance_status: str) -> List[PhysicsMLRegistry]:
        """
        Async get physics ML registry entries by ML compliance status
        
        Args:
            compliance_status: ML compliance status to filter by
            
        Returns:
            List of matching PhysicsMLRegistry instances
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ml_compliance_status = ? ORDER BY created_at DESC"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (compliance_status,))
                rows = await cursor.fetchall()
                
            models = []
            for row in rows:
                model = await self._row_to_model(row)
                if model:
                    models.append(model)
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to get physics ML registry entries by ML compliance status: {e}")
            return []
    
    async def get_by_ml_security_score_range(self, min_score: float, max_score: float) -> List[PhysicsMLRegistry]:
        """
        Async get physics ML registry entries by ML security score range
        
        Args:
            min_score: Minimum ML security score
            max_score: Maximum ML security score
            
        Returns:
            List of matching PhysicsMLRegistry instances
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ml_security_score BETWEEN ? AND ? ORDER BY ml_security_score DESC"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (min_score, max_score))
                rows = await cursor.fetchall()
                
            models = []
            for row in rows:
                model = await self._row_to_model(row)
                if model:
                    models.append(model)
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to get physics ML registry entries by ML security score range: {e}")
            return []
    
    async def count_by_training_status(self, training_status: str) -> int:
        """
        Async count physics ML registry entries by training status
        
        Args:
            training_status: Training status to count
            
        Returns:
            Count of entries with the specified training status
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT COUNT(*) FROM {self.table_name} WHERE training_status = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (training_status,))
                result = await cursor.fetchone()
                
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to count physics ML registry entries: {e}")
            return 0
    
    async def _row_to_model(self, row: tuple) -> Optional[PhysicsMLRegistry]:
        """
        Async convert database row to PhysicsMLRegistry model
        
        Args:
            row: Database row tuple
            
        Returns:
            PhysicsMLRegistry instance or None if conversion failed
        """
        try:
            # This is a simplified conversion - in practice, you'd map column names
            # to model fields based on your actual database schema
            model_data = {
                'ml_model_id': row[0],
                'model_name': row[1],
                'model_type': row[2],
                'physics_domain': row[3],
                'ml_framework': row[4],
                'model_version': row[5],
                'description': row[6],
                'architecture': eval(row[7]) if row[7] else {},
                'hyperparameters': eval(row[8]) if row[8] else {},
                'loss_functions': eval(row[9]) if row[9] else [],
                'optimization_config': eval(row[10]) if row[10] else None,
                'training_status': row[11],
                'training_progress': row[12],
                'validation_metrics': eval(row[13]) if row[13] else {},
                'test_metrics': eval(row[14]) if row[14] else None,
                'physics_constraints': eval(row[15]) if row[15] else [],
                'conservation_laws': eval(row[16]) if row[16] else [],
                'boundary_conditions': eval(row[17]) if row[17] else None,
                'initial_conditions': eval(row[18]) if row[18] else None,
                'status': row[19],
                'lifecycle_stage': row[20],
                'created_by': row[21],
                'created_at': datetime.fromisoformat(row[22]) if row[22] else None,
                'updated_by': row[23],
                'updated_at': datetime.fromisoformat(row[24]) if row[24] else None,
                'ml_compliance_type': row[25],
                'ml_compliance_status': row[26],
                'ml_compliance_score': row[27],
                'ml_security_score': row[28],
                'ml_performance_trend': row[29],
                'ml_optimization_suggestions': eval(row[30]) if row[30] else None,
                'last_ml_optimization_date': datetime.fromisoformat(row[31]) if row[31] else None,
                'enterprise_ml_metrics': eval(row[32]) if row[32] else None,
                'model_path': row[33],
                'model_size': row[34],
                'inference_latency': row[35],
                'deployment_status': row[36],
                'tags': eval(row[37]) if row[37] else [],
                'metadata': eval(row[38]) if row[38] else {}
            }
            
            return PhysicsMLRegistry(**model_data)
            
        except Exception as e:
            logger.error(f"Failed to convert row to model: {e}")
            return None
    
    async def close(self) -> None:
        """Async cleanup of database connections"""
        if self.connection_manager:
            await self.connection_manager.close()
            logger.info("Physics ML Registry Repository connections closed")
