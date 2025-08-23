"""
Federated Learning Metrics Repository
====================================

Repository for federated learning metrics operations using engine ConnectionManager.
Implements pure async patterns for optimal performance.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from src.engine.database.connection_manager import ConnectionManager
from ..models.federated_learning_metrics import FederatedLearningMetrics


class FederatedLearningMetricsRepository:
    """Repository for federated learning metrics operations"""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize repository with connection manager"""
        self.connection_manager = connection_manager
        self.table_name = "federated_learning_metrics"
    
    async def create(self, metrics: FederatedLearningMetrics) -> bool:
        """Create a new metrics entry (async)"""
        try:
            query = f"""
                INSERT INTO {self.table_name} (
                    registry_id, health_score, response_time_ms, uptime_percentage, error_rate,
                    federation_participation_speed_sec, aggregation_speed_sec, privacy_compliance_speed_sec,
                    cpu_usage_percent, memory_usage_percent, gpu_usage_percent, network_throughput_mbps,
                    enterprise_health_score, federation_efficiency_score, privacy_preservation_score,
                    quality_score, collaboration_effectiveness, risk_assessment_score, compliance_adherence,
                    created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                metrics.registry_id, metrics.health_score, metrics.response_time_ms,
                metrics.uptime_percentage, metrics.error_rate, metrics.federation_participation_speed_sec,
                metrics.aggregation_speed_sec, metrics.privacy_compliance_speed_sec,
                metrics.cpu_usage_percent, metrics.memory_usage_percent, metrics.gpu_usage_percent,
                metrics.network_throughput_mbps, metrics.enterprise_health_score,
                metrics.federation_efficiency_score, metrics.privacy_preservation_score,
                metrics.quality_score, metrics.collaboration_effectiveness,
                metrics.risk_assessment_score, metrics.compliance_adherence,
                metrics.created_at, metrics.updated_at,
                str(metrics.metadata) if metrics.metadata else None
            )
            
            await self.connection_manager.execute_query(query, params)
            return True
            
        except Exception as e:
            print(f"Error creating metrics: {e}")
            return False
    
    async def get_by_id(self, metric_id: int) -> Optional[FederatedLearningMetrics]:
        """Get metrics by ID (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE metric_id = ?"
            result = await self.connection_manager.fetch_one(query, (metric_id,))
            
            if result:
                return self._row_to_model(result)
            return None
            
        except Exception as e:
            print(f"Error fetching metrics by ID: {e}")
            return None
    
    async def get_by_registry_id(self, registry_id: str, limit: int = 100) -> List[FederatedLearningMetrics]:
        """Get metrics by registry ID (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ? ORDER BY created_at DESC LIMIT ?"
            results = await self.connection_manager.fetch_all(query, (registry_id, limit))
            
            return [self._row_to_model(row) for row in results]
            
        except Exception as e:
            print(f"Error fetching metrics by registry ID: {e}")
            return []
    
    async def get_latest_by_registry_id(self, registry_id: str) -> Optional[FederatedLearningMetrics]:
        """Get latest metrics for a registry (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ? ORDER BY created_at DESC LIMIT 1"
            result = await self.connection_manager.fetch_one(query, (registry_id,))
            
            if result:
                return self._row_to_model(result)
            return None
            
        except Exception as e:
            print(f"Error fetching latest metrics: {e}")
            return None
    
    async def get_by_time_range(self, registry_id: str, start_time: datetime, end_time: datetime) -> List[FederatedLearningMetrics]:
        """Get metrics within a time range (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ? AND created_at BETWEEN ? AND ? ORDER BY created_at ASC"
            results = await self.connection_manager.fetch_all(query, (registry_id, start_time, end_time))
            
            return [self._row_to_model(row) for row in results]
            
        except Exception as e:
            print(f"Error fetching metrics by time range: {e}")
            return []
    
    async def get_performance_trends(self, registry_id: str, days: int = 7) -> Dict[str, List[float]]:
        """Get performance trends over time (async)"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            query = f"""
                SELECT 
                    DATE(created_at) as date,
                    AVG(health_score) as avg_health,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(error_rate) as avg_error_rate,
                    AVG(cpu_usage_percent) as avg_cpu,
                    AVG(memory_usage_percent) as avg_memory
                FROM {self.table_name} 
                WHERE registry_id = ? AND created_at BETWEEN ? AND ?
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            
            results = await self.connection_manager.fetch_all(query, (registry_id, start_time, end_time))
            
            trends = {
                'dates': [],
                'health_scores': [],
                'response_times': [],
                'error_rates': [],
                'cpu_usage': [],
                'memory_usage': []
            }
            
            for row in results:
                trends['dates'].append(row['date'])
                trends['health_scores'].append(row['avg_health'] or 0.0)
                trends['response_times'].append(row['avg_response_time'] or 0.0)
                trends['error_rates'].append(row['avg_error_rate'] or 0.0)
                trends['cpu_usage'].append(row['avg_cpu'] or 0.0)
                trends['memory_usage'].append(row['avg_memory'] or 0.0)
            
            return trends
            
        except Exception as e:
            print(f"Error getting performance trends: {e}")
            return {}
    
    async def update(self, metric_id: int, update_data: Dict[str, Any]) -> bool:
        """Update metrics (async)"""
        try:
            # Build dynamic update query
            set_clauses = []
            params = []
            
            for key, value in update_data.items():
                if key == 'metadata':
                    set_clauses.append(f"{key} = ?")
                    params.append(str(value) if value else None)
                else:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = ?")
            params.append(datetime.now())
            
            # Add metric_id for WHERE clause
            params.append(metric_id)
            
            query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE metric_id = ?"
            await self.connection_manager.execute_query(query, params)
            
            return True
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
            return False
    
    async def delete(self, metric_id: int) -> bool:
        """Delete metrics (async)"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE metric_id = ?"
            await self.connection_manager.execute_query(query, (metric_id,))
            return True
            
        except Exception as e:
            print(f"Error deleting metrics: {e}")
            return False
    
    async def get_performance_summary(self, registry_id: str) -> Dict[str, Any]:
        """Get performance summary for a registry (async)"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_metrics,
                    AVG(health_score) as avg_health_score,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(uptime_percentage) as avg_uptime,
                    AVG(error_rate) as avg_error_rate,
                    AVG(cpu_usage_percent) as avg_cpu_usage,
                    AVG(memory_usage_percent) as avg_memory_usage,
                    AVG(enterprise_health_score) as avg_enterprise_health,
                    AVG(federation_efficiency_score) as avg_federation_efficiency
                FROM {self.table_name}
                WHERE registry_id = ?
            """
            
            result = await self.connection_manager.fetch_one(query, (registry_id,))
            return dict(result) if result else {}
            
        except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {}
    
    async def get_alerts(self, registry_id: str, threshold: float = 80.0) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds (async)"""
        try:
            query = f"""
                SELECT 
                    metric_id, created_at, health_score, error_rate, cpu_usage_percent, memory_usage_percent
                FROM {self.table_name}
                WHERE registry_id = ? AND (
                    health_score < ? OR 
                    error_rate > ? OR 
                    cpu_usage_percent > ? OR 
                    memory_usage_percent > ?
                )
                ORDER BY created_at DESC
                LIMIT 50
            """
            
            results = await self.connection_manager.fetch_all(query, (registry_id, threshold, 100-threshold, threshold, threshold))
            
            alerts = []
            for row in results:
                alert = {
                    'metric_id': row['metric_id'],
                    'timestamp': row['created_at'],
                    'issues': []
                }
                
                if row['health_score'] < threshold:
                    alert['issues'].append(f"Low health score: {row['health_score']}")
                if row['error_rate'] > (100-threshold):
                    alert['issues'].append(f"High error rate: {row['error_rate']}")
                if row['cpu_usage_percent'] > threshold:
                    alert['issues'].append(f"High CPU usage: {row['cpu_usage_percent']}%")
                if row['memory_usage_percent'] > threshold:
                    alert['issues'].append(f"High memory usage: {row['memory_usage_percent']}%")
                
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
    
    async def get_enterprise_metrics_summary(self) -> Dict[str, Any]:
        """Get enterprise metrics summary across all registries (async)"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_metrics,
                    AVG(enterprise_health_score) as avg_enterprise_health,
                    AVG(federation_efficiency_score) as avg_federation_efficiency,
                    AVG(privacy_preservation_score) as avg_privacy_preservation,
                    AVG(quality_score) as avg_model_quality,
                    AVG(collaboration_effectiveness) as avg_collaboration,
                    AVG(risk_assessment_score) as avg_risk_assessment,
                    AVG(compliance_adherence) as avg_compliance
                FROM {self.table_name}
                WHERE enterprise_health_score IS NOT NULL
            """
            
            result = await self.connection_manager.fetch_one(query)
            return dict(result) if result else {}
            
        except Exception as e:
            print(f"Error getting enterprise metrics summary: {e}")
            return {}
    
    def _row_to_model(self, row: Dict[str, Any]) -> FederatedLearningMetrics:
        """Convert database row to model instance"""
        # Parse JSON fields
        if row.get('metadata'):
            try:
                import json
                row['metadata'] = json.loads(row['metadata'])
            except:
                row['metadata'] = {}
        
        return FederatedLearningMetrics(**row)
