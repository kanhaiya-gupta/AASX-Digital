"""
Physics Modeling Metrics Repository

This repository provides data access operations for the physics modeling metrics table
with integrated enterprise features and async database operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from src.engine.database import ConnectionManager
from ..models.physics_modeling_metrics import PhysicsModelingMetrics

logger = logging.getLogger(__name__)


class PhysicsModelingMetricsRepository:
    """
    Repository for physics modeling metrics operations
    
    Provides async CRUD operations and advanced querying capabilities
    for physics modeling metrics data with enterprise features.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the repository with database connection"""
        self.connection_manager = connection_manager
        self.table_name = "physics_modeling_metrics"
    
    async def create(self, metric: PhysicsModelingMetrics) -> Optional[str]:
        """
        Async create a new physics modeling metrics entry
        
        Args:
            metric: PhysicsModelingMetrics model instance
            
        Returns:
            Created metric ID or None if failed
        """
        try:
            # Prepare data for insertion
            data = metric.dict()
            data['timestamp'] = datetime.utcnow().isoformat()
            data['collection_date'] = datetime.utcnow().isoformat()
            
            # Execute insert query
            query = f"""
                INSERT INTO {self.table_name} (
                    metric_id, metric_name, metric_type, metric_category, metric_value,
                    metric_unit, model_id, ml_model_id, simulation_id, solver_id, plugin_id,
                    timestamp, collection_date, valid_from, valid_until, confidence_level,
                    data_quality_score, validation_status, validation_notes,
                    enterprise_metric_type, enterprise_metric_value, enterprise_metric_timestamp,
                    enterprise_metadata, compliance_tracking_status, compliance_tracking_score,
                    compliance_tracking_details, security_metrics_status, security_metrics_score,
                    security_metrics_details, performance_analytics_status, performance_analytics_score,
                    performance_analytics_details, warning_threshold, critical_threshold,
                    alert_status, alert_history, tags, metadata
                ) VALUES (:metric_id, :metric_name, :metric_type, :metric_category, :metric_value, :metric_unit, :model_id, :ml_model_id, :simulation_id, :solver_id, :plugin_id, :timestamp, :collection_date, :valid_from, :valid_until, :confidence_level, :data_quality_score, :validation_status, :validation_notes, :enterprise_metric_type, :enterprise_metric_value, :enterprise_metric_timestamp, :enterprise_metadata, :compliance_tracking_status, :compliance_tracking_score, :compliance_tracking_details, :security_metrics_status, :security_metrics_score, :security_metrics_details, :performance_analytics_status, :performance_analytics_score, :performance_analytics_details, :warning_threshold, :critical_threshold, :alert_status, :alert_history, :tags, :metadata)
            """
            
            # Prepare parameters with proper handling of complex types
            params = {
                'metric_id': data['metric_id'],
                'metric_name': data['metric_name'],
                'metric_type': data['metric_type'],
                'metric_category': data['metric_category'],
                'metric_value': data['metric_value'],
                'metric_unit': data['metric_unit'],
                'model_id': data['model_id'],
                'ml_model_id': data['ml_model_id'],
                'simulation_id': data['simulation_id'],
                'solver_id': data['solver_id'],
                'plugin_id': data['plugin_id'],
                'timestamp': data['timestamp'],
                'collection_date': data['collection_date'],
                'valid_from': data['valid_from'],
                'valid_until': data['valid_until'],
                'confidence_level': data['confidence_level'],
                'data_quality_score': data['data_quality_score'],
                'validation_status': data['validation_status'],
                'validation_notes': data['validation_notes'],
                'enterprise_metric_type': data['enterprise_metric_type'],
                'enterprise_metric_value': data['enterprise_metric_value'],
                'enterprise_metric_timestamp': data['enterprise_metric_timestamp'],
                'enterprise_metadata': str(data['enterprise_metadata']) if data['enterprise_metadata'] else None,
                'compliance_tracking_status': data['compliance_tracking_status'],
                'compliance_tracking_score': data['compliance_tracking_score'],
                'compliance_tracking_details': str(data['compliance_tracking_details']) if data['compliance_tracking_details'] else None,
                'security_metrics_status': data['security_metrics_status'],
                'security_metrics_score': data['security_metrics_score'],
                'security_metrics_details': str(data['security_metrics_details']) if data['security_metrics_details'] else None,
                'performance_analytics_status': data['performance_analytics_status'],
                'performance_analytics_score': data['performance_analytics_score'],
                'performance_analytics_details': str(data['performance_analytics_details']) if data['performance_analytics_details'] else None,
                'warning_threshold': data['warning_threshold'],
                'critical_threshold': data['critical_threshold'],
                'alert_status': data['alert_status'],
                'alert_history': str(data['alert_history']),
                'tags': str(data['tags']),
                'metadata': str(data['metadata'])
            }
            
            await self.connection_manager.execute_update(query, params)
                
            logger.info(f"Created physics modeling metrics entry: {metric.metric_id}")
            return metric.metric_id
            
        except Exception as e:
            logger.error(f"Failed to create physics modeling metrics entry: {e}")
            return None
    
    async def get_by_id(self, metric_id: str) -> Optional[PhysicsModelingMetrics]:
        """
        Async get physics modeling metrics entry by ID
        
        Args:
            metric_id: Unique metric identifier
            
        Returns:
            PhysicsModelingMetrics instance or None if not found
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE metric_id = :metric_id"
            
            result = await self.connection_manager.execute_query(query, {"metric_id": metric_id})
            
            if result and len(result) > 0:
                row = result[0]
                return PhysicsModelingMetrics(**row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting physics modeling metrics by ID: {e}")
            return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[PhysicsModelingMetrics]:
        """
        Async get all physics modeling metrics entries with pagination
        
        Args:
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of PhysicsModelingMetrics instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY timestamp DESC LIMIT :limit OFFSET :offset"
            
            result = await self.connection_manager.execute_query(query, {"limit": limit, "offset": offset})
            
            metrics = []
            for row in result:
                metrics.append(PhysicsModelingMetrics(**row))
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting all physics modeling metrics entries: {e}")
            return []
    
    async def update(self, metric_id: str, updates: Dict[str, Any]) -> bool:
        """
        Async update physics modeling metrics entry
        
        Args:
            metric_id: Unique metric identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Add updated timestamp
            updates['timestamp'] = datetime.utcnow().isoformat()
            
            # Prepare SET clause and parameters
            set_clause = ', '.join([f"{key} = :{key}" for key in updates.keys()])
            params = updates.copy()
            params['metric_id'] = metric_id
            
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE metric_id = :metric_id"
            
            await self.connection_manager.execute_update(query, params)
                
            logger.info(f"Updated physics modeling metrics entry: {metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating physics modeling metrics entry: {e}")
            return False
    
    async def delete(self, metric_id: str) -> bool:
        """
        Async delete physics modeling metrics entry
        
        Args:
            metric_id: Unique metric identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE metric_id = :metric_id"
            
            await self.connection_manager.execute_update(query, {"metric_id": metric_id})
                
            logger.info(f"Deleted physics modeling metrics entry: {metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting physics modeling metrics entry: {e}")
            return False
    
    async def get_by_model_id(self, model_id: str, limit: int = 100) -> List[PhysicsModelingMetrics]:
        """
        Async get physics modeling metrics entries by model ID
        
        Args:
            model_id: Model identifier to filter by
            limit: Maximum number of entries to return
            
        Returns:
            List of PhysicsModelingMetrics instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE model_id = :model_id ORDER BY timestamp DESC LIMIT :limit"
            
            result = await self.connection_manager.execute_query(query, {"model_id": model_id, "limit": limit})
            
            metrics = []
            for row in result:
                metrics.append(PhysicsModelingMetrics(**row))
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting physics modeling metrics by model ID: {e}")
            return []
    
    async def get_by_ml_model_id(self, ml_model_id: str) -> List[PhysicsModelingMetrics]:
        """
        Async get physics modeling metrics by associated ML model ID
        
        Args:
            ml_model_id: Associated ML model ID
            
        Returns:
            List of matching PhysicsModelingMetrics instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ml_model_id = :ml_model_id ORDER BY timestamp DESC"
            
            result = await self.connection_manager.execute_query(query, {"ml_model_id": ml_model_id})
            
            metrics = []
            for row in result:
                metrics.append(PhysicsModelingMetrics(**row))
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting physics modeling metrics by ML model ID: {e}")
            return []
    
    async def get_by_metric_type(self, metric_type: str) -> List[PhysicsModelingMetrics]:
        """
        Async get physics modeling metrics by metric type
        
        Args:
            metric_type: Type of metric to filter by
            
        Returns:
            List of matching PhysicsModelingMetrics instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE metric_type = :metric_type ORDER BY timestamp DESC"
            
            result = await self.connection_manager.execute_query(query, {"metric_type": metric_type})
            
            metrics = []
            for row in result:
                metrics.append(PhysicsModelingMetrics(**row))
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting physics modeling metrics by metric type: {e}")
            return []
    
    async def get_by_time_range(self, start_time: datetime, end_time: datetime) -> List[PhysicsModelingMetrics]:
        """
        Async get physics modeling metrics within a time range
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of matching PhysicsModelingMetrics instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE timestamp BETWEEN :start_time AND :end_time ORDER BY timestamp DESC"
            
            result = await self.connection_manager.execute_query(query, {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()})
            
            metrics = []
            for row in result:
                metrics.append(PhysicsModelingMetrics(**row))
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting physics modeling metrics by time range: {e}")
            return []
    
    async def get_by_alert_status(self, alert_status: str) -> List[PhysicsModelingMetrics]:
        """
        Async get physics modeling metrics by alert status
        
        Args:
            alert_status: Alert status to filter by
            
        Returns:
            List of matching PhysicsModelingMetrics instances
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE alert_status = :alert_status ORDER BY timestamp DESC"
            
            result = await self.connection_manager.execute_query(query, {"alert_status": alert_status})
            
            metrics = []
            for row in result:
                metrics.append(PhysicsModelingMetrics(**row))
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting physics modeling metrics by alert status: {e}")
            return []
    
    async def get_recent_metrics(self, hours: int = 24) -> List[PhysicsModelingMetrics]:
        """
        Async get recent physics modeling metrics from the last N hours
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent PhysicsModelingMetrics instances
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            query = f"SELECT * FROM {self.table_name} WHERE timestamp >= :cutoff_time ORDER BY timestamp DESC"
            
            result = await self.connection_manager.execute_query(query, {"cutoff_time": cutoff_time.isoformat()})
            
            metrics = []
            for row in result:
                metrics.append(PhysicsModelingMetrics(**row))
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting recent physics modeling metrics: {e}")
            return []
    
    async def count_by_metric_type(self, metric_type: str) -> int:
        """
        Async count physics modeling metrics by metric type
        
        Args:
            metric_type: Metric type to count
            
        Returns:
            Count of metrics with the specified type
        """
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE metric_type = :metric_type"
            
            result = await self.connection_manager.execute_query(query, {"metric_type": metric_type})
            
            return result[0]['count'] if result and len(result) > 0 else 0
            
        except Exception as e:
            logger.error(f"Error counting physics modeling metrics: {e}")
            return 0
    
    async def _row_to_model(self, row: tuple) -> Optional[PhysicsModelingMetrics]:
        """
        Async convert database row to PhysicsModelingMetrics model
        
        Args:
            row: Database row tuple
            
        Returns:
            PhysicsModelingMetrics instance or None if conversion failed
        """
        try:
            # This is a simplified conversion - in practice, you'd map column names
            # to model fields based on your actual database schema
            model_data = {
                'metric_id': row[0],
                'metric_name': row[1],
                'metric_type': row[2],
                'metric_category': row[3],
                'metric_value': row[4],
                'metric_unit': row[5],
                'model_id': row[6],
                'ml_model_id': row[7],
                'simulation_id': row[8],
                'solver_id': row[9],
                'plugin_id': row[10],
                'timestamp': datetime.fromisoformat(row[11]) if row[11] else None,
                'collection_date': datetime.fromisoformat(row[12]) if row[12] else None,
                'valid_from': datetime.fromisoformat(row[13]) if row[13] else None,
                'valid_until': datetime.fromisoformat(row[14]) if row[14] else None,
                'confidence_level': row[15],
                'data_quality_score': row[16],
                'validation_status': row[17],
                'validation_notes': row[18],
                'enterprise_metric_type': row[19],
                'enterprise_metric_value': row[20],
                'enterprise_metric_timestamp': datetime.fromisoformat(row[21]) if row[21] else None,
                'enterprise_metadata': eval(row[22]) if row[22] else None,
                'compliance_tracking_status': row[23],
                'compliance_tracking_score': row[24],
                'compliance_tracking_details': eval(row[25]) if row[25] else None,
                'security_metrics_status': row[26],
                'security_metrics_score': row[27],
                'security_metrics_details': eval(row[28]) if row[28] else None,
                'performance_analytics_status': row[29],
                'performance_analytics_score': row[30],
                'performance_analytics_details': eval(row[31]) if row[31] else None,
                'warning_threshold': row[32],
                'critical_threshold': row[33],
                'alert_status': row[34],
                'alert_history': eval(row[35]) if row[35] else [],
                'tags': eval(row[36]) if row[36] else [],
                'metadata': eval(row[37]) if row[37] else {}
            }
            
            return PhysicsModelingMetrics(**model_data)
            
        except Exception as e:
            logger.error(f"Failed to convert row to model: {e}")
            return None
    
    async def close(self) -> None:
        """Async cleanup of database connections"""
        if self.connection_manager:
            await self.connection_manager.close()
            logger.info("Physics Modeling Metrics Repository connections closed")
