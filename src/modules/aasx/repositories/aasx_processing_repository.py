"""
AASX Processing Repository

Data access layer for AASX processing operations.
Uses the engine ConnectionManager for database access with async support.
Pure raw SQL implementation for maximum performance and flexibility.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from src.engine.database.connection_manager import ConnectionManager
from ..models.aasx_processing import AasxProcessing


class AasxProcessingRepository:
    """
    Repository for AASX processing operations.
    
    Provides async CRUD operations and business logic queries
    for the aasx_processing table using pure raw SQL.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize repository with connection manager.
        
        Args:
            connection_manager: Engine connection manager instance
        """
        self.connection_manager = connection_manager
        self.table_name = "aasx_processing"
    
    async def create(self, aasx_processing: AasxProcessing) -> bool:
        """
        Create a new AASX processing record using raw SQL.
        
        Args:
            aasx_processing: AASX processing model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(aasx_processing)
            
            # Build INSERT query dynamically
            columns = list(db_data.keys())
            placeholders = [f":{col}" for col in columns]
            
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            # Use standard ConnectionManager pattern
            await self.connection_manager.execute_update(query, db_data)
                
            return True
                
        except Exception as e:
            print(f"Error creating AASX processing record: {e}")
            return False
    
    async def get_by_id(self, job_id: str) -> Optional[AasxProcessing]:
        """
        Get AASX processing record by job ID using raw SQL.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Optional[AasxProcessing]: AASX processing model or None
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE job_id = :job_id
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_query(query, {"job_id": job_id})
            
            if result and len(result) > 0:
                return self._dict_to_model(dict(result[0]))
            return None
                
        except Exception as e:
            print(f"Error retrieving AASX processing record: {e}")
            return None
    
    async def get_by_file_id(self, file_id: str) -> List[AasxProcessing]:
        """
        Get all AASX processing records for a specific file using raw SQL.
        
        Args:
            file_id: File identifier
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE file_id = :file_id
                ORDER BY created_at DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, {"file_id": file_id})
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            print(f"Error retrieving AASX processing records by file ID: {e}")
            return []
    
    async def get_by_project_id(self, project_id: str) -> List[AasxProcessing]:
        """
        Get all AASX processing records for a specific project using raw SQL.
        
        Args:
            project_id: Project identifier
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE project_id = :project_id
                ORDER BY created_at DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, {"project_id": project_id})
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            print(f"Error retrieving AASX processing records by project ID: {e}")
            return []
    
    async def get_by_status(self, status: str) -> List[AasxProcessing]:
        """
        Get all AASX processing records by status using raw SQL.
        
        Args:
            status: Processing status
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE processing_status = :status
                ORDER BY created_at DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, {"status": status})
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            print(f"Error retrieving AASX processing records by status: {e}")
            return []
    
    async def update(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update AASX processing record using raw SQL.
        
        Args:
            job_id: Unique job identifier
            update_data: Dictionary of fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not update_data:
                return True
            
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.now().isoformat()
            
            # Build UPDATE query dynamically
            set_clauses = [f"{col} = :{col}" for col in update_data.keys()]
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE job_id = :job_id
            """
            
            # Add job_id to parameters
            params = {**update_data, "job_id": job_id}
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_update(query, params)
            
            return result > 0
                
        except Exception as e:
            print(f"Error updating AASX processing record: {e}")
            return False
    
    async def delete(self, job_id: str) -> bool:
        """
        Delete AASX processing record using raw SQL.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"""
                DELETE FROM {self.table_name}
                WHERE job_id = :job_id
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_update(query, {"job_id": job_id})
            
            return result > 0
                
        except Exception as e:
            print(f"Error deleting AASX processing record: {e}")
            return False
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[AasxProcessing]:
        """
        Get all AASX processing records using raw SQL with optional pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[AasxProcessing]: List of AASX processing models
        """
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC"
            params = {}
            
            if limit is not None:
                query += " LIMIT :limit"
                params['limit'] = limit
                
            if offset is not None:
                query += " OFFSET :offset"
                params['offset'] = offset
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, params)
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            print(f"Error retrieving all AASX processing records: {e}")
            return []
    
    async def count_by_status(self, status: str) -> int:
        """
        Count AASX processing records by status using raw SQL.
        
        Args:
            status: Processing status
            
        Returns:
            int: Number of records with the specified status
        """
        try:
            query = f"""
                SELECT COUNT(*) as count
                FROM {self.table_name}
                WHERE processing_status = :status
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_query(query, {"status": status})
            
            return result[0]['count'] if result and len(result) > 0 else 0
                
        except Exception as e:
            print(f"Error counting AASX processing records by status: {e}")
            return 0
    
    async def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get processing summary statistics using raw SQL.
        
        Returns:
            Dict[str, Any]: Summary statistics
        """
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as completed_jobs,
                    COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed_jobs,
                    COUNT(CASE WHEN processing_status = 'in_progress' THEN 1 END) as in_progress_jobs,
                    AVG(processing_time) as avg_processing_time,
                    AVG(data_quality_score) as avg_quality_score
                FROM {self.table_name}
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_query(query)
            
            return dict(result[0]) if result and len(result) > 0 else {}
                
        except Exception as e:
            print(f"Error getting processing summary: {e}")
            return {}
    
    def _model_to_dict(self, model: AasxProcessing) -> Dict[str, Any]:
        """Convert Pydantic model to database dictionary."""
        data = model.model_dump()
        
        # Fields that should be stored as JSON in the database (from aasx_etl.py schema)
        json_fields = [
            # Core processing options and results
            'extraction_options', 'generation_options', 'validation_options',
            'extraction_results', 'generation_results', 'validation_results',
            'processing_metadata', 'custom_attributes', 'processing_config', 
            'tags_config', 'relationships_config', 'dependencies_config', 
            'processing_instances_config', 'audit_trail', 'regulatory_requirements', 
            'dependencies', 'child_job_ids', 'notification_emails', 'webhook_urls',
            'notification_preferences', 'quality_gates', 'quality_check_results',
            'version_history', 'change_log', 'performance_targets', 'audit_info',
            
            # Additional JSON fields from schema
            'audit_details', 'security_details', 'enterprise_metadata',
            'optimization_suggestions',
            
            # Metrics table JSON fields
            'processing_technique_performance', 'file_type_processing_stats',
            'processing_patterns', 'resource_utilization_trends', 'user_activity',
            'job_patterns', 'compliance_patterns', 'security_events',
            'aasx_analytics', 'technique_effectiveness', 'format_performance',
            'file_size_processing_efficiency'
        ]
        
        # Convert only JSON fields from Python objects to JSON strings
        for field in json_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], (dict, list)):
                    try:
                        data[field] = json.dumps(data[field])
                    except (TypeError, ValueError) as e:
                        # If JSON conversion fails, convert to string representation
                        data[field] = str(data[field])
                        print(f"Warning: Could not convert {field} to JSON, using string: {e}")
        
        return data
    
    def _dict_to_model(self, data: Dict[str, Any]) -> AasxProcessing:
        """Convert database dictionary to Pydantic model."""
        # Fields that should be stored as JSON in the database (from aasx_etl.py schema)
        json_fields = [
            # Core processing options and results
            'extraction_options', 'generation_options', 'validation_options',
            'extraction_results', 'generation_results', 'validation_results',
            'processing_metadata', 'custom_attributes', 'processing_config', 
            'tags_config', 'relationships_config', 'dependencies_config', 
            'processing_instances_config', 'audit_trail', 'regulatory_requirements', 
            'dependencies', 'child_job_ids', 'notification_emails', 'webhook_urls',
            'notification_preferences', 'quality_gates', 'quality_check_results',
            'version_history', 'change_log', 'performance_targets', 'audit_info',
            
            # Additional JSON fields from schema
            'audit_details', 'security_details', 'enterprise_metadata',
            'optimization_suggestions',
            
            # Metrics table JSON fields
            'processing_technique_performance', 'file_type_processing_stats',
            'processing_patterns', 'resource_utilization_trends', 'user_activity',
            'job_patterns', 'compliance_patterns', 'security_events',
            'aasx_analytics', 'technique_effectiveness', 'format_performance',
            'file_size_processing_efficiency'
        ]
        
        # Convert only JSON fields from JSON strings back to Python objects
        for field in json_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], str):
                    try:
                        data[field] = json.loads(data[field])
                    except (json.JSONDecodeError, TypeError):
                        # Keep as string if JSON parsing fails
                        pass
        
        return AasxProcessing(**data)
