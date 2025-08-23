"""
Physics Modeling Registry Repository

This repository provides data access operations for the physics modeling registry table
with integrated enterprise features and async database operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from src.engine.database import ConnectionManager
from src.engine.database.factory import DatabaseFactory
from ..models.physics_modeling_registry import PhysicsModelingRegistry

logger = logging.getLogger(__name__)


class PhysicsModelingRegistryRepository:
    """
    Repository for physics modeling registry operations
    
    Provides async CRUD operations and advanced querying capabilities
    for physics modeling registry data with enterprise features.
    """
    
    def __init__(self):
        """Initialize the repository with database connection"""
        self.connection_manager: Optional[ConnectionManager] = None
        self.table_name = "physics_modeling_registry"
    
    async def initialize(self) -> None:
        """Async initialization of database connection"""
        try:
            self.connection_manager = await DatabaseFactory.create_connection_manager()
            logger.info("Physics Modeling Registry Repository initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize repository: {e}")
            raise
    
    async def create(self, model: PhysicsModelingRegistry) -> Optional[str]:
        """
        Async create a new physics modeling registry entry
        
        Args:
            model: PhysicsModelingRegistry model instance
            
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
                    model_id, model_name, model_type, physics_domain, model_version,
                    description, parameters, constraints, mesh_config, solver_config,
                    status, lifecycle_stage, created_by, created_at, updated_by, updated_at,
                    validation_status, validation_score, quality_metrics,
                    compliance_type, compliance_status, compliance_score,
                    last_audit_date, next_audit_date, audit_details,
                    security_event_type, threat_assessment, security_score,
                    last_security_scan, security_details,
                    performance_trend, optimization_suggestions, last_optimization_date,
                    enterprise_metrics, tags, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                data['model_id'], data['model_name'], data['model_type'],
                data['physics_domain'], data['model_version'], data['description'],
                str(data['parameters']), str(data['constraints']),
                str(data['mesh_config']) if data['mesh_config'] else None,
                str(data['solver_config']) if data['solver_config'] else None,
                data['status'], data['lifecycle_stage'], data['created_by'],
                data['created_at'], data['updated_by'], data['updated_at'],
                data['validation_status'], data['validation_score'],
                str(data['quality_metrics']),
                data['compliance_type'], data['compliance_status'], data['compliance_score'],
                data['last_audit_date'], data['next_audit_date'], data['audit_details'],
                data['security_event_type'], data['threat_assessment'], data['security_score'],
                data['last_security_scan'], data['security_details'],
                data['performance_trend'], str(data['optimization_suggestions']) if data['optimization_suggestions'] else None,
                data['last_optimization_date'], str(data['enterprise_metrics']) if data['enterprise_metrics'] else None,
                str(data['tags']), str(data['metadata'])
            )
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, values)
                await conn.commit()
                
            logger.info(f"Created physics modeling registry entry: {model.model_id}")
            return model.model_id
            
        except Exception as e:
            logger.error(f"Failed to create physics modeling registry entry: {e}")
            return None
    
    async def get_by_id(self, model_id: str) -> Optional[PhysicsModelingRegistry]:
        """
        Async retrieve physics modeling registry entry by ID
        
        Args:
            model_id: Unique identifier for the model
            
        Returns:
            PhysicsModelingRegistry instance or None if not found
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} WHERE model_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (model_id,))
                row = await cursor.fetchone()
                
            if row:
                return await self._row_to_model(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve physics modeling registry entry: {e}")
            return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[PhysicsModelingRegistry]:
        """
        Async retrieve all physics modeling registry entries with pagination
        
        Args:
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of PhysicsModelingRegistry instances
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
            logger.error(f"Failed to retrieve physics modeling registry entries: {e}")
            return []
    
    async def update(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """
        Async update physics modeling registry entry
        
        Args:
            model_id: Unique identifier for the model
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
                if field in ['parameters', 'constraints', 'quality_metrics', 'optimization_suggestions', 'enterprise_metrics', 'tags', 'metadata']:
                    update_fields.append(f"{field} = ?")
                    values.append(str(value))
                elif field in ['mesh_config', 'solver_config', 'audit_details', 'security_details']:
                    if value is not None:
                        update_fields.append(f"{field} = ?")
                        values.append(str(value))
                else:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            values.append(datetime.utcnow().isoformat())
            
            # Add model_id for WHERE clause
            values.append(model_id)
            
            query = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE model_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, values)
                await conn.commit()
                
            logger.info(f"Updated physics modeling registry entry: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update physics modeling registry entry: {e}")
            return False
    
    async def delete(self, model_id: str) -> bool:
        """
        Async delete physics modeling registry entry
        
        Args:
            model_id: Unique identifier for the model
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"DELETE FROM {self.table_name} WHERE model_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (model_id,))
                await conn.commit()
                
            logger.info(f"Deleted physics modeling registry entry: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete physics modeling registry entry: {e}")
            return False
    
    async def search_by_type(self, model_type: str) -> List[PhysicsModelingRegistry]:
        """
        Async search physics modeling registry entries by model type
        
        Args:
            model_type: Type of physics model to search for
            
        Returns:
            List of matching PhysicsModelingRegistry instances
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
            logger.error(f"Failed to search physics modeling registry entries: {e}")
            return []
    
    async def get_by_compliance_status(self, compliance_status: str) -> List[PhysicsModelingRegistry]:
        """
        Async get physics modeling registry entries by compliance status
        
        Args:
            compliance_status: Compliance status to filter by
            
        Returns:
            List of matching PhysicsModelingRegistry instances
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} WHERE compliance_status = ? ORDER BY created_at DESC"
            
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
            logger.error(f"Failed to get physics modeling registry entries by compliance status: {e}")
            return []
    
    async def get_by_security_score_range(self, min_score: float, max_score: float) -> List[PhysicsModelingRegistry]:
        """
        Async get physics modeling registry entries by security score range
        
        Args:
            min_score: Minimum security score
            max_score: Maximum security score
            
        Returns:
            List of matching PhysicsModelingRegistry instances
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT * FROM {self.table_name} WHERE security_score BETWEEN ? AND ? ORDER BY security_score DESC"
            
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
            logger.error(f"Failed to get physics modeling registry entries by security score range: {e}")
            return []
    
    async def count_by_status(self, status: str) -> int:
        """
        Async count physics modeling registry entries by status
        
        Args:
            status: Status to count
            
        Returns:
            Count of entries with the specified status
        """
        if not self.connection_manager:
            await self.initialize()
        
        try:
            query = f"SELECT COUNT(*) FROM {self.table_name} WHERE status = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(query, (status,))
                result = await cursor.fetchone()
                
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to count physics modeling registry entries: {e}")
            return 0
    
    async def _row_to_model(self, row: tuple) -> Optional[PhysicsModelingRegistry]:
        """
        Async convert database row to PhysicsModelingRegistry model
        
        Args:
            row: Database row tuple
            
        Returns:
            PhysicsModelingRegistry instance or None if conversion failed
        """
        try:
            # This is a simplified conversion - in practice, you'd map column names
            # to model fields based on your actual database schema
            model_data = {
                'model_id': row[0],
                'model_name': row[1],
                'model_type': row[2],
                'physics_domain': row[3],
                'model_version': row[4],
                'description': row[5],
                'parameters': eval(row[6]) if row[6] else {},
                'constraints': eval(row[7]) if row[7] else {},
                'mesh_config': eval(row[8]) if row[8] else None,
                'solver_config': eval(row[9]) if row[9] else None,
                'status': row[10],
                'lifecycle_stage': row[11],
                'created_by': row[12],
                'created_at': datetime.fromisoformat(row[13]) if row[13] else None,
                'updated_by': row[14],
                'updated_at': datetime.fromisoformat(row[15]) if row[15] else None,
                'validation_status': row[16],
                'validation_score': row[17],
                'quality_metrics': eval(row[18]) if row[18] else {},
                'compliance_type': row[19],
                'compliance_status': row[20],
                'compliance_score': row[21],
                'last_audit_date': datetime.fromisoformat(row[22]) if row[22] else None,
                'next_audit_date': datetime.fromisoformat(row[23]) if row[23] else None,
                'audit_details': eval(row[24]) if row[24] else None,
                'security_event_type': row[25],
                'threat_assessment': row[26],
                'security_score': row[27],
                'last_security_scan': datetime.fromisoformat(row[28]) if row[28] else None,
                'security_details': eval(row[29]) if row[29] else None,
                'performance_trend': row[30],
                'optimization_suggestions': eval(row[31]) if row[31] else None,
                'last_optimization_date': datetime.fromisoformat(row[32]) if row[32] else None,
                'enterprise_metrics': eval(row[33]) if row[33] else None,
                'tags': eval(row[34]) if row[34] else [],
                'metadata': eval(row[35]) if row[35] else {}
            }
            
            return PhysicsModelingRegistry(**model_data)
            
        except Exception as e:
            logger.error(f"Failed to convert row to model: {e}")
            return None
    
    async def close(self) -> None:
        """Async cleanup of database connections"""
        if self.connection_manager:
            await self.connection_manager.close()
            logger.info("Physics Modeling Registry Repository connections closed")
