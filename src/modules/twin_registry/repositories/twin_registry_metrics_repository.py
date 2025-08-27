"""
Twin Registry Metrics Repository

Data access layer for twin registry metrics and performance monitoring.
Handles metrics data for the new twin_registry_metrics table.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from src.engine.database.connection_manager import ConnectionManager
from ..models.twin_registry_metrics import (
    TwinRegistryMetrics,
    MetricsQuery,
    MetricsSummary
)

logger = logging.getLogger(__name__)


class TwinRegistryMetricsRepository:
    """Repository for managing twin registry metrics data with new comprehensive schema."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the metrics repository with engine connection manager."""
        self.connection_manager = connection_manager
        self.table_name = "twin_registry_metrics"
        logger.info("Twin Registry Metrics Repository initialized with new schema and engine")
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        return "twin_registry_metrics"
    
    def _get_columns(self) -> List[str]:
        """Get the column names for this repository."""
        return [
            "metric_id", "registry_id", "timestamp", "health_score", "uptime_percentage",
            "twin_sync_speed_sec", "relationship_update_speed_sec", "lifecycle_transition_speed_sec",
            "twin_registry_efficiency", "twin_management_performance", "twin_category_performance_stats",
            "resource_utilization_trends", "user_activity", "twin_operation_patterns",
            "compliance_status", "security_events", "twin_registry_analytics", "category_effectiveness",
            "workflow_performance", "twin_size_performance_efficiency", "performance_trends",
            "quality_trends", "usage_trends", "time_based_analytics", "created_at", "updated_at"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name."""
        return "metric_id"
    
    async def initialize(self) -> None:
        """Initialize the repository - tables already exist from Phase 1."""
        try:
            # Tables are already created by our migration script
            logger.info("Twin Registry Metrics Repository ready - tables already exist")
        except Exception as e:
            logger.error(f"Failed to initialize Metrics Repository: {e}")
            raise
    
    async def create_metrics(self, metrics: TwinRegistryMetrics) -> TwinRegistryMetrics:
        """Create new metrics entry."""
        try:
            sql = """
            INSERT INTO twin_registry_metrics (
                registry_id, timestamp, health_score, uptime_percentage, twin_sync_speed_sec,
                relationship_update_speed_sec, lifecycle_transition_speed_sec, twin_registry_efficiency,
                twin_management_performance, twin_category_performance_stats, resource_utilization_trends,
                user_activity, twin_operation_patterns, compliance_status, security_events,
                twin_registry_analytics, category_effectiveness, workflow_performance,
                twin_size_performance_efficiency, performance_trends, quality_trends, usage_trends,
                time_based_analytics, created_at, updated_at
            ) VALUES (:registry_id, :timestamp, :health_score, :uptime_percentage, :twin_sync_speed_sec,
                :relationship_update_speed_sec, :lifecycle_transition_speed_sec, :twin_registry_efficiency,
                :twin_management_performance, :twin_category_performance_stats, :resource_utilization_trends,
                :user_activity, :twin_operation_patterns, :compliance_status, :security_events,
                :twin_registry_analytics, :category_effectiveness, :workflow_performance,
                :twin_size_performance_efficiency, :performance_trends, :quality_trends, :usage_trends,
                :time_based_analytics, :created_at, :updated_at)
            """
            
            params = {
                'registry_id': metrics.registry_id,
                'timestamp': metrics.timestamp,
                'health_score': metrics.health_score,
                'uptime_percentage': metrics.uptime_percentage,
                'twin_sync_speed_sec': metrics.twin_sync_speed_sec,
                'relationship_update_speed_sec': metrics.relationship_update_speed_sec,
                'lifecycle_transition_speed_sec': metrics.lifecycle_transition_speed_sec,
                'twin_registry_efficiency': metrics.twin_registry_efficiency,
                'twin_management_performance': metrics.twin_management_performance,
                'twin_category_performance_stats': metrics.twin_category_performance_stats,
                'resource_utilization_trends': metrics.resource_utilization_trends,
                'user_activity': metrics.user_activity,
                'twin_operation_patterns': metrics.twin_operation_patterns,
                'compliance_status': metrics.compliance_status,
                'security_events': metrics.security_events,
                'twin_registry_analytics': metrics.twin_registry_analytics,
                'category_effectiveness': metrics.category_effectiveness,
                'workflow_performance': metrics.workflow_performance,
                'twin_size_performance_efficiency': metrics.twin_size_performance_efficiency,
                'performance_trends': metrics.performance_trends,
                'quality_trends': metrics.quality_trends,
                'usage_trends': metrics.usage_trends,
                'time_based_analytics': metrics.time_based_analytics,
                'created_at': metrics.created_at,
                'updated_at': metrics.updated_at
            }
            
            await self.connection_manager.execute_update(sql, params)
            
            logger.info(f"Created metrics entry for registry {metrics.registry_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to create metrics entry: {e}")
            raise
    
    def get_by_id(self, metric_id: int) -> Optional[TwinRegistryMetrics]:
        """Get metrics by ID."""
        try:
            sql = "SELECT * FROM twin_registry_metrics WHERE metric_id = ?"
            
            with self.db_manager.connection_manager.get_cursor() as cursor:
                cursor.execute(sql, (metric_id,))
                row = cursor.fetchone()
            
            if row:
                return self._row_to_metrics(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get metrics by ID {metric_id}: {e}")
            raise
    
    def get_by_registry_id(self, registry_id: str, limit: int = 100) -> List[TwinRegistryMetrics]:
        """Get metrics for a specific registry, ordered by timestamp."""
        try:
            sql = "SELECT * FROM twin_registry_metrics WHERE registry_id = ? ORDER BY timestamp DESC LIMIT ?"
            
            with self.db_manager.connection_manager.get_cursor() as cursor:
                cursor.execute(sql, (registry_id, limit))
                rows = cursor.fetchall()
            
            return [self._row_to_metrics(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get metrics for registry {registry_id}: {e}")
            raise
    
    async def get_latest_by_registry_id(self, registry_id: str) -> Optional[TwinRegistryMetrics]:
        """Get the latest metrics for a specific registry."""
        try:
            sql = "SELECT * FROM twin_registry_metrics WHERE registry_id = :registry_id ORDER BY timestamp DESC LIMIT 1"
            
            result = await self.connection_manager.execute_query(sql, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                return self._row_to_metrics(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest metrics for registry {registry_id}: {e}")
            raise
    
    async def query_metrics(self, query: MetricsQuery) -> List[TwinRegistryMetrics]:
        """Query metrics with filters."""
        try:
            sql = "SELECT * FROM twin_registry_metrics WHERE 1=1"
            params = {}
            
            if query.registry_id:
                sql += " AND registry_id = :registry_id"
                params['registry_id'] = query.registry_id
            
            if query.start_timestamp:
                sql += " AND timestamp >= :start_timestamp"
                params['start_timestamp'] = query.start_timestamp.isoformat()
            
            if query.end_timestamp:
                sql += " AND timestamp <= :end_timestamp"
                params['end_timestamp'] = query.end_timestamp.isoformat()
            
            if query.min_health_score is not None:
                sql += " AND health_score >= :min_health_score"
                params['min_health_score'] = query.min_health_score
            
            if query.max_health_score is not None:
                sql += " AND health_score <= :max_health_score"
                params['max_health_score'] = query.max_health_score
            
            sql += " ORDER BY timestamp DESC"
            
            result = await self.connection_manager.execute_query(sql, params)
            
            return [self._row_to_metrics(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            raise
    
    async def update_metrics(self, metrics: TwinRegistryMetrics) -> TwinRegistryMetrics:
        """Update existing metrics entry."""
        try:
            sql = """
            UPDATE twin_registry_metrics SET
                health_score = :health_score, response_time_ms = :response_time_ms, uptime_percentage = :uptime_percentage, error_rate = :error_rate,
                cpu_usage_percent = :cpu_usage_percent, memory_usage_percent = :memory_usage_percent, network_throughput_mbps = :network_throughput_mbps,
                storage_usage_percent = :storage_usage_percent, transaction_count = :transaction_count, data_volume_mb = :data_volume_mb,
                user_interaction_count = :user_interaction_count, lifecycle_events = :lifecycle_events, performance_trends = :performance_trends,
                user_activity = :user_activity, compliance_status = :compliance_status, security_events = :security_events
            WHERE metric_id = :metric_id
            """
            
            params = {
                'health_score': metrics.health_score,
                'response_time_ms': metrics.response_time_ms,
                'uptime_percentage': metrics.uptime_percentage,
                'error_rate': metrics.error_rate,
                'cpu_usage_percent': metrics.cpu_usage_percent,
                'memory_usage_percent': metrics.memory_usage_percent,
                'network_throughput_mbps': metrics.network_throughput_mbps,
                'storage_usage_percent': metrics.storage_usage_percent,
                'transaction_count': metrics.transaction_count,
                'data_volume_mb': metrics.data_volume_mb,
                'user_interaction_count': metrics.user_interaction_count,
                'lifecycle_events': self._serialize_json(metrics.lifecycle_events),
                'performance_trends': self._serialize_json(metrics.performance_trends),
                'user_activity': self._serialize_json(metrics.user_activity),
                'compliance_status': self._serialize_json(metrics.compliance_status),
                'security_events': self._serialize_json(metrics.security_events),
                'metric_id': metrics.metric_id
            }
            
            await self.connection_manager.execute_update(sql, params)
            
            logger.info(f"Updated metrics entry: {metrics.metric_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            raise
    
    async def delete_metrics(self, metric_id: int) -> bool:
        """Delete metrics by ID."""
        try:
            sql = "DELETE FROM twin_registry_metrics WHERE metric_id = :metric_id"
            
            await self.connection_manager.execute_update(sql, {"metric_id": metric_id})
            
            logger.info(f"Deleted metrics entry: {metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete metrics {metric_id}: {e}")
            raise
    
    async def get_summary(self) -> MetricsSummary:
        """Get metrics summary statistics."""
        try:
            # Total metrics
            total_result = await self.connection_manager.execute_query("SELECT COUNT(*) as count FROM twin_registry_metrics", {})
            total = total_result[0]['count'] if total_result and len(total_result) > 0 else 0
            
            # Average health score
            avg_health_result = await self.connection_manager.execute_query("SELECT AVG(health_score) as avg_health FROM twin_registry_metrics WHERE health_score IS NOT NULL", {})
            avg_health = avg_health_result[0]['avg_health'] if avg_health_result and len(avg_health_result) > 0 else 0.0
            
            # Average response time
            avg_response_result = await self.connection_manager.execute_query("SELECT AVG(uptime_percentage) as avg_uptime FROM twin_registry_metrics WHERE uptime_percentage IS NOT NULL", {})
            avg_response = avg_response_result[0]['avg_uptime'] if avg_response_result and len(avg_response_result) > 0 else 0.0
            
            # By registry
            by_registry_result = await self.connection_manager.execute_query("SELECT registry_id, COUNT(*) as count FROM twin_registry_metrics GROUP BY registry_id", {})
            by_registry = {row['registry_id']: row['count'] for row in by_registry_result}
            
            # By timestamp (group by hour)
            by_timestamp_result = await self.connection_manager.execute_query("""
                SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hour, COUNT(*) as count
                FROM twin_registry_metrics 
                GROUP BY hour 
                ORDER BY hour DESC 
                LIMIT 24
            """, {})
            by_timestamp = {row['hour']: row['count'] for row in by_timestamp_result}
            
            return MetricsSummary(
                total_metrics=total,
                average_health_score=float(avg_health),
                average_uptime_percentage=float(avg_response),
                metrics_by_registry=by_registry,
                metrics_by_timestamp=by_timestamp
            )
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            raise
    
    async def cleanup_old_metrics(self, days_to_keep: int = 30) -> int:
        """Clean up old metrics data."""
        try:
            sql = "DELETE FROM twin_registry_metrics WHERE timestamp < datetime('now', '-{} days')".format(days_to_keep)
            
            await self.connection_manager.execute_update(sql, {})
            
            logger.info(f"Cleaned up old metrics entries (older than {days_to_keep} days)")
            return 1  # Return 1 to indicate success, actual count would need separate query
            
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
            raise
    
    def _row_to_metrics(self, row) -> TwinRegistryMetrics:
        """Convert database row to TwinRegistryMetrics model."""
        try:
            return TwinRegistryMetrics(
                metric_id=row['metric_id'],
                registry_id=row['registry_id'],
                timestamp=self._parse_datetime(row['timestamp']),
                health_score=row['health_score'],
                uptime_percentage=row['uptime_percentage'],
                twin_sync_speed_sec=row['twin_sync_speed_sec'],
                relationship_update_speed_sec=row['relationship_update_speed_sec'],
                lifecycle_transition_speed_sec=row['lifecycle_transition_speed_sec'],
                twin_registry_efficiency=row['twin_registry_efficiency'],
                twin_management_performance=self._deserialize_json(row['twin_management_performance']),
                twin_category_performance_stats=self._deserialize_json(row['twin_category_performance_stats']),
                resource_utilization_trends=self._deserialize_json(row['resource_utilization_trends']),
                user_activity=self._deserialize_json(row['user_activity']),
                twin_operation_patterns=self._deserialize_json(row['twin_operation_patterns']),
                compliance_status=self._deserialize_json(row['compliance_status']),
                security_events=self._deserialize_json(row['security_events']),
                twin_registry_analytics=self._deserialize_json(row['twin_registry_analytics']),
                category_effectiveness=self._deserialize_json(row['category_effectiveness']),
                workflow_performance=self._deserialize_json(row['workflow_performance']),
                twin_size_performance_efficiency=self._deserialize_json(row['twin_size_performance_efficiency']),
                performance_trends=self._deserialize_json(row['performance_trends']),
                quality_trends=self._deserialize_json(row['quality_trends']),
                usage_trends=self._deserialize_json(row['usage_trends']),
                time_based_analytics=self._deserialize_json(row['time_based_analytics'])
            )
        except Exception as e:
            logger.error(f"Failed to convert row to TwinRegistryMetrics: {e}")
            raise
    
    def _parse_datetime(self, value) -> Optional[datetime]:
        """Parse datetime from string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except:
            return None
    
    def _serialize_json(self, data) -> str:
        """Serialize data to JSON string."""
        if data is None:
            return "[]" if isinstance(data, list) else "{}"
        try:
            import json
            return json.dumps(data)
        except:
            return "[]" if isinstance(data, list) else "{}"
    
    def _deserialize_json(self, data) -> Any:
        """Deserialize JSON string to data."""
        if not data:
            return [] if "events" in data else {}
        try:
            import json
            return json.loads(data)
        except:
            return [] if "events" in data else {}
