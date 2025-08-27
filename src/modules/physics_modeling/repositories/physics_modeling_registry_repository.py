"""
Physics Modeling Registry Repository

This repository provides data access operations for the physics modeling registry table
with integrated enterprise features and async database operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from src.engine.database import ConnectionManager
from ..models.physics_modeling_registry import PhysicsModelingRegistry

logger = logging.getLogger(__name__)


class PhysicsModelingRegistryRepository:
    """
    Repository for physics modeling registry operations
    
    Provides async CRUD operations and advanced querying capabilities
    for physics modeling registry data with enterprise features.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the repository with database connection"""
        self.connection_manager = connection_manager
        self.table_name = "physics_modeling_registry"
    
    async def create(self, model: PhysicsModelingRegistry) -> Optional[str]:
        """
        Async create a new physics modeling registry entry
        
        Args:
            model: PhysicsModelingRegistry model instance
            
        Returns:
            Created model ID or None if failed
        """
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
                ) VALUES (:model_id, :model_name, :model_type, :physics_domain, :model_version, :description, :parameters, :constraints, :mesh_config, :solver_config, :status, :lifecycle_stage, :created_by, :created_at, :updated_by, :updated_at, :validation_status, :validation_score, :quality_metrics, :compliance_type, :compliance_status, :compliance_score, :last_audit_date, :next_audit_date, :audit_details, :security_event_type, :threat_assessment, :security_score, :last_security_scan, :security_details, :performance_trend, :optimization_suggestions, :last_optimization_date, :enterprise_metrics, :tags, :metadata)
            """
            
            # Prepare parameters with proper handling of complex types
            params = {
                'model_id': data['model_id'],
                'model_name': data['model_name'],
                'model_type': data['model_type'],
                'physics_domain': data['physics_domain'],
                'model_version': data['model_version'],
                'description': data['description'],
                'parameters': str(data['parameters']),
                'constraints': str(data['constraints']),
                'mesh_config': str(data['mesh_config']) if data['mesh_config'] else None,
                'solver_config': str(data['solver_config']) if data['solver_config'] else None,
                'status': data['status'],
                'lifecycle_stage': data['lifecycle_stage'],
                'created_by': data['created_by'],
                'created_at': data['created_at'],
                'updated_by': data['updated_by'],
                'updated_at': data['updated_at'],
                'validation_status': data['validation_status'],
                'validation_score': data['validation_score'],
                'quality_metrics': str(data['quality_metrics']),
                'compliance_type': data['compliance_type'],
                'compliance_status': data['compliance_status'],
                'compliance_score': data['compliance_score'],
                'last_audit_date': data['last_audit_date'],
                'next_audit_date': data['next_audit_date'],
                'audit_details': data['audit_details'],
                'security_event_type': data['security_event_type'],
                'threat_assessment': data['threat_assessment'],
                'security_score': data['security_score'],
                'last_security_scan': data['last_security_scan'],
                'security_details': data['security_details'],
                'performance_trend': data['performance_trend'],
                'optimization_suggestions': str(data['optimization_suggestions']) if data['optimization_suggestions'] else None,
                'last_optimization_date': data['last_optimization_date'],
                'enterprise_metrics': str(data['enterprise_metrics']) if data['enterprise_metrics'] else None,
                'tags': str(data['tags']),
                'metadata': str(data['metadata'])
            }
            
            await self.connection_manager.execute_update(query, params)
                
            logger.info(f"Created physics modeling registry entry: {model.model_id}")
            return model.model_id
            
        except Exception as e:
            logger.error(f"Failed to create physics modeling registry entry: {e}")
            return None
    
    async def get_by_id(self, model_id: str) -> Optional[PhysicsModelingRegistry]:
        """
        Async get physics modeling registry entry by ID
        
        Args:
            model_id: Unique model identifier
            
        Returns:
            PhysicsModelingRegistry instance or None if not found
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE model_id = :model_id"
            
            result = await self.connection_manager.execute_query(query, {"model_id": model_id})
            
            if result and len(result) > 0:
                row = result[0]
                return PhysicsModelingRegistry(**row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting physics modeling registry by ID: {e}")
            return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[PhysicsModelingRegistry]:
        """
        Async get all physics modeling registry entries with pagination
        
        Args:
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of PhysicsModelingRegistry instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            
            result = await self.connection_manager.execute_query(query, {"limit": limit, "offset": offset})
            
            models = []
            for row in result:
                models.append(PhysicsModelingRegistry(**row))
            return models
            
        except Exception as e:
            logger.error(f"Error getting all physics modeling registry entries: {e}")
            return []
    
    async def update(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """
        Async update physics modeling registry entry
        
        Args:
            model_id: Unique model identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Prepare SET clause and parameters
            set_clause = ', '.join([f"{key} = :{key}" for key in updates.keys()])
            params = updates.copy()
            params['model_id'] = model_id
            
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE model_id = :model_id"
            
            await self.connection_manager.execute_update(query, params)
                
            logger.info(f"Updated physics modeling registry entry: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating physics modeling registry entry: {e}")
            return False
    
    async def delete(self, model_id: str) -> bool:
        """
        Async delete physics modeling registry entry
        
        Args:
            model_id: Unique model identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE model_id = :model_id"
            
            await self.connection_manager.execute_update(query, {"model_id": model_id})
                
            logger.info(f"Deleted physics modeling registry entry: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting physics modeling registry entry: {e}")
            return False
    
    async def search_by_type(self, model_type: str) -> List[PhysicsModelingRegistry]:
        """
        Async search physics modeling registry entries by model type
        
        Args:
            model_type: Type of physics model to search for
            
        Returns:
            List of matching PhysicsModelingRegistry instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE model_type = :model_type ORDER BY created_at DESC"
            
            result = await self.connection_manager.execute_query(query, {"model_type": model_type})
            
            models = []
            for row in result:
                models.append(PhysicsModelingRegistry(**row))
            return models
            
        except Exception as e:
            logger.error(f"Error searching physics modeling registry entries: {e}")
            return []
    
    async def get_by_compliance_status(self, compliance_status: str) -> List[PhysicsModelingRegistry]:
        """
        Async get physics modeling registry entries by compliance status
        
        Args:
            compliance_status: Compliance status to filter by
            
        Returns:
            List of matching PhysicsModelingRegistry instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE compliance_status = :compliance_status ORDER BY created_at DESC"
            
            result = await self.connection_manager.execute_query(query, {"compliance_status": compliance_status})
            
            models = []
            for row in result:
                models.append(PhysicsModelingRegistry(**row))
            return models
            
        except Exception as e:
            logger.error(f"Error getting physics modeling registry entries by compliance status: {e}")
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
        try:
            query = f"SELECT * FROM {self.table_name} WHERE security_score BETWEEN :min_score AND :max_score ORDER BY security_score DESC"
            
            result = await self.connection_manager.execute_query(query, {"min_score": min_score, "max_score": max_score})
            
            models = []
            for row in result:
                models.append(PhysicsModelingRegistry(**row))
            return models
            
        except Exception as e:
            logger.error(f"Error getting physics modeling registry entries by security score range: {e}")
            return []
    
    async def count_by_status(self, status: str) -> int:
        """
        Async count physics modeling registry entries by status
        
        Args:
            status: Status to count
            
        Returns:
            Count of entries with the specified status
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE status = :status"
            
            result = await self.connection_manager.execute_query(query, {"status": status})
            
            return result[0]['count'] if result and len(result) > 0 else 0
            
        except Exception as e:
            logger.error(f"Error counting physics modeling registry entries: {e}")
            return 0
    
    async def get_by_status(self, status: str, limit: int = 100) -> List[PhysicsModelingRegistry]:
        """
        Async get physics modeling registry entries by status
        
        Args:
            status: Model status to filter by
            limit: Maximum number of entries to return
            
        Returns:
            List of PhysicsModelingRegistry instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE status = :status ORDER BY created_at DESC LIMIT :limit"
            
            result = await self.connection_manager.execute_query(query, {"status": status, "limit": limit})
            
            models = []
            for row in result:
                models.append(PhysicsModelingRegistry(**row))
            return models
            
        except Exception as e:
            logger.error(f"Error getting physics modeling registry entries by status: {e}")
            return []
    
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
