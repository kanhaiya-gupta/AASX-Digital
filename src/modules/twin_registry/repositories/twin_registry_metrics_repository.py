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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                metrics.registry_id,
                metrics.timestamp,
                metrics.health_score,
                metrics.uptime_percentage,
                metrics.twin_sync_speed_sec,
                metrics.relationship_update_speed_sec,
                metrics.lifecycle_transition_speed_sec,
                metrics.twin_registry_efficiency,
                metrics.twin_management_performance,
                metrics.twin_category_performance_stats,
                metrics.resource_utilization_trends,
                metrics.user_activity,
                metrics.twin_operation_patterns,
                metrics.compliance_status,
                metrics.security_events,
                metrics.twin_registry_analytics,
                metrics.category_effectiveness,
                metrics.workflow_performance,
                metrics.twin_size_performance_efficiency,
                metrics.performance_trends,
                metrics.quality_trends,
                metrics.usage_trends,
                metrics.time_based_analytics,
                metrics.created_at,
                metrics.updated_at
            )
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(sql, params)
                await conn.commit()
                
                # Get the auto-generated metric_id
                metrics.metric_id = cursor.lastrowid
            
            logger.info(f"Created metrics entry: {metrics.metric_id} for registry: {metrics.registry_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to create metrics: {e}")
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
            sql = "SELECT * FROM twin_registry_metrics WHERE registry_id = ? ORDER BY timestamp DESC LIMIT 1"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(sql, (registry_id,))
                row = await cursor.fetchone()
            
            if row:
                return self._row_to_metrics(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest metrics for registry {registry_id}: {e}")
            raise
    
    async def query_metrics(self, query: MetricsQuery) -> List[TwinRegistryMetrics]:
        """Query metrics with filters."""
        try:
            sql = "SELECT * FROM twin_registry_metrics WHERE 1=1"
            params = []
            
            if query.registry_id:
                sql += " AND registry_id = ?"
                params.append(query.registry_id)
            
            if query.start_timestamp:
                sql += " AND timestamp >= ?"
                params.append(query.start_timestamp.isoformat())
            
            if query.end_timestamp:
                sql += " AND timestamp <= ?"
                params.append(query.end_timestamp.isoformat())
            
            if query.min_health_score is not None:
                sql += " AND health_score >= ?"
                params.append(query.min_health_score)
            
            if query.max_health_score is not None:
                sql += " AND health_score <= ?"
                params.append(query.max_health_score)
            
            sql += " ORDER BY timestamp DESC"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(sql, params)
                rows = await cursor.fetchall()
            
            return [self._row_to_metrics(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            raise
    
    async def update_metrics(self, metrics: TwinRegistryMetrics) -> TwinRegistryMetrics:
        """Update existing metrics entry."""
        try:
            sql = """
            UPDATE twin_registry_metrics SET
                health_score = ?, response_time_ms = ?, uptime_percentage = ?, error_rate = ?,
                cpu_usage_percent = ?, memory_usage_percent = ?, network_throughput_mbps = ?,
                storage_usage_percent = ?, transaction_count = ?, data_volume_mb = ?,
                user_interaction_count = ?, lifecycle_events = ?, performance_trends = ?,
                user_activity = ?, compliance_status = ?, security_events = ?
            WHERE metric_id = ?
            """
            
            params = (
                metrics.health_score,
                metrics.response_time_ms,
                metrics.uptime_percentage,
                metrics.error_rate,
                metrics.cpu_usage_percent,
                metrics.memory_usage_percent,
                metrics.network_throughput_mbps,
                metrics.storage_usage_percent,
                metrics.transaction_count,
                metrics.data_volume_mb,
                metrics.user_interaction_count,
                self._serialize_json(metrics.lifecycle_events),
                self._serialize_json(metrics.performance_trends),
                self._serialize_json(metrics.user_activity),
                self._serialize_json(metrics.compliance_status),
                self._serialize_json(metrics.security_events),
                metrics.metric_id
            )
            
            async with self.connection_manager.get_connection() as conn:
                await conn.execute(sql, params)
                await conn.commit()
            
            logger.info(f"Updated metrics entry: {metrics.metric_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            raise
    
    async def delete_metrics(self, metric_id: int) -> bool:
        """Delete metrics by ID."""
        try:
            sql = "DELETE FROM twin_registry_metrics WHERE metric_id = ?"
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(sql, (metric_id,))
                await conn.commit()
                
                deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted metrics entry: {metric_id}")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete metrics {metric_id}: {e}")
            raise
    
    async def get_summary(self) -> MetricsSummary:
        """Get metrics summary statistics."""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Total metrics
                cursor = await conn.execute("SELECT COUNT(*) FROM twin_registry_metrics")
                total = (await cursor.fetchone())[0]
                
                # Average health score
                cursor = await conn.execute("SELECT AVG(health_score) FROM twin_registry_metrics WHERE health_score IS NOT NULL")
                avg_health = (await cursor.fetchone())[0] or 0.0
                
                # Average response time
                cursor = await conn.execute("SELECT AVG(uptime_percentage) FROM twin_registry_metrics WHERE uptime_percentage IS NOT NULL")
                avg_response = (await cursor.fetchone())[0] or 0.0
                
                # By registry
                cursor = await conn.execute("SELECT registry_id, COUNT(*) FROM twin_registry_metrics GROUP BY registry_id")
                by_registry = {row[0]: row[1] for row in await cursor.fetchall()}
                
                # By timestamp (group by hour)
                cursor = await conn.execute("""
                    SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hour, COUNT(*) 
                    FROM twin_registry_metrics 
                    GROUP BY hour 
                    ORDER BY hour DESC 
                    LIMIT 24
                """)
                by_timestamp = {row[0]: row[1] for row in await cursor.fetchall()}
            
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
            
            async with self.connection_manager.get_connection() as conn:
                cursor = await conn.execute(sql)
                await conn.commit()
                
                deleted_count = cursor.rowcount
            logger.info(f"Cleaned up {deleted_count} old metrics entries (older than {days_to_keep} days)")
            return deleted_count
            
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
