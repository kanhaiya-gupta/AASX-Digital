"""
AASX Processing Metrics Repository

Data access layer for AASX processing metrics operations.
Uses the engine ConnectionManager for database access with async support.
Pure raw SQL implementation for maximum performance and flexibility.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from src.engine.database.connection_manager import ConnectionManager
from ..models.aasx_processing_metrics import AasxProcessingMetrics


class AasxProcessingMetricsRepository:
    """
    Repository for AASX processing metrics operations.
    
    Provides async CRUD operations and business logic queries
    for the aasx_processing_metrics table using pure raw SQL.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize repository with connection manager.
        
        Args:
            connection_manager: Engine connection manager instance
        """
        self.connection_manager = connection_manager
        self.table_name = "aasx_processing_metrics"
    
    async def create(self, metrics: AasxProcessingMetrics) -> bool:
        """
        Create a new AASX processing metrics record using raw SQL.
        
        Args:
            metrics: AASX processing metrics model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(metrics)
            
            # Build INSERT query dynamically
            columns = list(db_data.keys())
            placeholders = [f":{col}" for col in columns]
            
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            # Use async connection manager methods
            await self.connection_manager.execute_update(query, db_data)
                
            return True
                
        except Exception as e:
            print(f"Error creating AASX processing metrics record: {e}")
            return False
    
    async def get_by_id(self, metric_id: int) -> Optional[AasxProcessingMetrics]:
        """
        Get AASX processing metrics record by metric ID using raw SQL.
        
        Args:
            metric_id: Unique metric identifier
            
        Returns:
            Optional[AasxProcessingMetrics]: AASX processing metrics model or None
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE metric_id = :metric_id
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_query(query, {"metric_id": metric_id})
            
            if result and len(result) > 0:
                return self._dict_to_model(dict(result[0]))
            return None
                
        except Exception as e:
            print(f"Error retrieving AASX processing metrics record: {e}")
            return None
    
    async def get_by_job_id(self, job_id: str) -> List[AasxProcessingMetrics]:
        """
        Get all AASX processing metrics records for a specific job using raw SQL.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE job_id = :job_id
                ORDER BY timestamp DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, {"job_id": job_id})
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            print(f"Error retrieving AASX processing metrics by job ID: {e}")
            return []
    
    async def get_by_timestamp_range(self, start_timestamp: str, end_timestamp: str) -> List[AasxProcessingMetrics]:
        """
        Get AASX processing metrics records within a timestamp range using raw SQL.
        
        Args:
            start_timestamp: Start timestamp
            end_timestamp: End timestamp
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE timestamp >= :start_timestamp AND timestamp <= :end_timestamp
                ORDER BY timestamp DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, {
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp
            })
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            print(f"Error retrieving AASX processing metrics by timestamp range: {e}")
            return []
    
    async def get_by_health_score_range(self, min_score: int, max_score: int) -> List[AasxProcessingMetrics]:
        """
        Get AASX processing metrics records by health score range using raw SQL.
        
        Args:
            min_score: Minimum health score
            max_score: Maximum health score
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE health_score >= :min_score AND health_score <= :max_score
                ORDER BY timestamp DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query, {
                "min_score": min_score,
                "max_score": max_score
            })
            
            return [self._dict_to_model(dict(row)) for row in results]
                
        except Exception as e:
            print(f"Error retrieving AASX processing metrics by health score range: {e}")
            return []
    
    async def update(self, metric_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update AASX processing metrics record using raw SQL.
        
        Args:
            metric_id: Unique metric identifier
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
                WHERE metric_id = :metric_id
            """
            
            # Add metric_id to parameters
            params = {**update_data, "metric_id": metric_id}
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_update(query, params)
            
            return result > 0
                
        except Exception as e:
            print(f"Error updating AASX processing metrics record: {e}")
            return False
    
    async def delete(self, metric_id: int) -> bool:
        """
        Delete AASX processing metrics record using raw SQL.
        
        Args:
            metric_id: Unique metric identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"""
                DELETE FROM {self.table_name}
                WHERE metric_id = :metric_id
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_update(query, {"metric_id": metric_id})
            
            return result > 0
                
        except Exception as e:
            print(f"Error deleting AASX processing metrics record: {e}")
            return False
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[AasxProcessingMetrics]:
        """
        Get all AASX processing metrics records using raw SQL with optional pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[AasxProcessingMetrics]: List of AASX processing metrics models
        """
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY timestamp DESC"
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
            print(f"Error retrieving all AASX processing metrics records: {e}")
            return []
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary statistics using raw SQL.
        
        Returns:
            Dict[str, Any]: Summary statistics
        """
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_metrics,
                    AVG(health_score) as avg_health_score,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(uptime_percentage) as avg_uptime,
                    AVG(error_rate) as avg_error_rate,
                    AVG(extraction_speed_sec) as avg_extraction_speed,
                    AVG(generation_speed_sec) as avg_generation_speed,
                    AVG(validation_speed_sec) as avg_validation_speed
                FROM {self.table_name}
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_query(query)
            
            return dict(result[0]) if result and len(result) > 0 else {}
                
        except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {}
    
    async def get_health_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get health score trends over time using raw SQL.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List[Dict[str, Any]]: List of health trend data points
        """
        try:
            query = f"""
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour_bucket,
                    AVG(health_score) as avg_health_score,
                    COUNT(*) as metric_count
                FROM {self.table_name}
                WHERE timestamp >= datetime('now', '-{hours} hours')
                GROUP BY hour_bucket
                ORDER BY hour_bucket DESC
            """
            
            # Use async connection manager methods
            results = await self.connection_manager.execute_query(query)
            
            return [dict(row) for row in results]
                
        except Exception as e:
            print(f"Error getting health trends: {e}")
            return []
    
    async def get_resource_utilization_summary(self) -> Dict[str, Any]:
        """
        Get resource utilization summary using raw SQL.
        
        Returns:
            Dict[str, Any]: Resource utilization summary
        """
        try:
            query = f"""
                SELECT 
                    AVG(cpu_usage_percent) as avg_cpu_usage,
                    AVG(memory_usage_percent) as avg_memory_usage,
                    AVG(storage_usage_percent) as avg_storage_usage,
                    AVG(network_throughput_mbps) as avg_network_throughput,
                    AVG(disk_io_mb) as avg_disk_io
                FROM {self.table_name}
                WHERE cpu_usage_percent IS NOT NULL
            """
            
            # Use async connection manager methods
            result = await self.connection_manager.execute_query(query)
            
            return dict(result[0]) if result and len(result) > 0 else {}
                
        except Exception as e:
            print(f"Error getting resource utilization summary: {e}")
            return {}
    
    def _model_to_dict(self, model: AasxProcessingMetrics) -> Dict[str, Any]:
        """Convert Pydantic model to database dictionary."""
        data = model.model_dump()
        
        # Handle JSON fields
        json_fields = [
            'aasx_management_performance', 'aasx_category_performance_stats',
            'aasx_processing_patterns', 'resource_utilization_trends',
            'user_activity', 'file_operation_patterns', 'compliance_patterns',
            'security_events', 'processing_patterns', 'job_patterns',
            'aasx_processing_analytics', 'category_effectiveness',
            'workflow_performance', 'file_size_performance_efficiency',
            'processing_technique_performance', 'file_type_processing_stats',
            'aasx_analytics', 'technique_effectiveness', 'format_performance',
            'file_size_processing_efficiency', 'enterprise_metadata',
            'optimization_suggestions', 'audit_details', 'security_details'
        ]
        
        for field in json_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], (dict, list)):
                    data[field] = json.dumps(data[field])
        
        return data
    
    def _dict_to_model(self, data: Dict[str, Any]) -> AasxProcessingMetrics:
        """Convert database dictionary to Pydantic model."""
        # Handle JSON fields
        json_fields = [
            'aasx_management_performance', 'aasx_category_performance_stats',
            'aasx_processing_patterns', 'resource_utilization_trends',
            'user_activity', 'file_operation_patterns', 'compliance_patterns',
            'security_events', 'processing_patterns', 'job_patterns',
            'aasx_processing_analytics', 'category_effectiveness',
            'workflow_performance', 'file_size_performance_efficiency',
            'processing_technique_performance', 'file_type_processing_stats',
            'aasx_analytics', 'technique_effectiveness', 'format_performance',
            'file_size_processing_efficiency', 'enterprise_metadata',
            'optimization_suggestions', 'audit_details', 'security_details'
        ]
        
        for field in json_fields:
            if field in data and data[field] is not None:
                try:
                    if isinstance(data[field], str):
                        data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    # Keep as string if JSON parsing fails
                    pass
        
        return AasxProcessingMetrics(**data)


