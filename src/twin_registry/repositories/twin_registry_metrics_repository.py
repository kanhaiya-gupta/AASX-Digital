"""
Twin Registry Metrics Repository

Data access layer for twin registry metrics and performance monitoring.
Handles metrics data for the new twin_registry_metrics table.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.repositories.base_repository import BaseRepository
from src.twin_registry.models.twin_registry_metrics import (
    TwinRegistryMetrics,
    MetricsQuery,
    MetricsSummary
)

logger = logging.getLogger(__name__)


class TwinRegistryMetricsRepository(BaseRepository):
    """Repository for managing twin registry metrics data."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize the metrics repository."""
        super().__init__(db_manager, TwinRegistryMetrics)
        self.table_name = "twin_registry_metrics"
        logger.info("Twin Registry Metrics Repository initialized")
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        return "twin_registry_metrics"
    
    def _get_columns(self) -> List[str]:
        """Get the column names for this repository."""
        return [
            "metric_id", "registry_id", "timestamp", "health_score", "response_time_ms",
            "throughput_ops_per_sec", "error_rate", "availability_percent", "resource_usage",
            "performance_indicators", "quality_metrics", "compliance_metrics", "security_metrics",
            "business_metrics", "custom_metrics", "alerts", "recommendations", "created_at", "updated_at"
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
    
    def create_metrics(self, metrics: TwinRegistryMetrics) -> TwinRegistryMetrics:
        """Create new metrics entry."""
        try:
            sql = """
            INSERT INTO twin_registry_metrics (
                registry_id, timestamp, health_score, response_time_ms, throughput_ops_per_sec,
                error_rate, availability_percent, resource_usage, performance_indicators,
                quality_metrics, compliance_metrics, security_metrics, business_metrics,
                custom_metrics, alerts, recommendations, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                metrics.registry_id,
                metrics.timestamp.isoformat(),
                metrics.health_score,
                metrics.response_time_ms,
                metrics.throughput_ops_per_sec,
                metrics.error_rate,
                metrics.availability_percent,
                self._serialize_json(metrics.resource_usage),
                self._serialize_json(metrics.performance_indicators),
                self._serialize_json(metrics.quality_metrics),
                self._serialize_json(metrics.compliance_metrics),
                self._serialize_json(metrics.security_metrics),
                self._serialize_json(metrics.business_metrics),
                self._serialize_json(metrics.custom_metrics),
                self._serialize_json(metrics.alerts),
                self._serialize_json(metrics.recommendations),
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            )
            
            # Use the connection manager's context manager for database operations
            with self.db_manager.connection_manager.get_cursor() as cursor:
                cursor.execute(sql, params)
                # Commit is handled automatically by the context manager
                
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
    
    def get_latest_by_registry_id(self, registry_id: str) -> Optional[TwinRegistryMetrics]:
        """Get the latest metrics for a specific registry."""
        try:
            sql = "SELECT * FROM twin_registry_metrics WHERE registry_id = ? ORDER BY timestamp DESC LIMIT 1"
            
            with self.db_manager.connection_manager.get_cursor() as cursor:
                cursor.execute(sql, (registry_id,))
                row = cursor.fetchone()
            
            if row:
                return self._row_to_metrics(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest metrics for registry {registry_id}: {e}")
            raise
    
    def query_metrics(self, query: MetricsQuery) -> List[TwinRegistryMetrics]:
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
            
            with self.db_manager.connection_manager.get_cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
            
            return [self._row_to_metrics(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            raise
    
    def update_metrics(self, metrics: TwinRegistryMetrics) -> TwinRegistryMetrics:
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
            
            with self.db_manager.connection_manager.get_cursor() as cursor:
                cursor.execute(sql, params)
                # Commit is handled automatically by the context manager
            
            logger.info(f"Updated metrics entry: {metrics.metric_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            raise
    
    def delete_metrics(self, metric_id: int) -> bool:
        """Delete metrics by ID."""
        try:
            sql = "DELETE FROM twin_registry_metrics WHERE metric_id = ?"
            
            with self.db_manager.connection_manager.get_cursor() as cursor:
                cursor.execute(sql, (metric_id,))
                # Commit is handled automatically by the context manager
                
                deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted metrics entry: {metric_id}")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete metrics {metric_id}: {e}")
            raise
    
    def get_summary(self) -> MetricsSummary:
        """Get metrics summary statistics."""
        try:
            with self.db_manager.connection_manager.get_cursor() as cursor:
                # Total metrics
                cursor.execute("SELECT COUNT(*) FROM twin_registry_metrics")
                total = cursor.fetchone()[0]
                
                # Average health score
                cursor.execute("SELECT AVG(health_score) FROM twin_registry_metrics WHERE health_score IS NOT NULL")
                avg_health = cursor.fetchone()[0] or 0.0
                
                # Average response time
                cursor.execute("SELECT AVG(response_time_ms) FROM twin_registry_metrics WHERE response_time_ms IS NOT NULL")
                avg_response = cursor.fetchone()[0] or 0.0
                
                # By registry
                cursor.execute("SELECT registry_id, COUNT(*) FROM twin_registry_metrics GROUP BY registry_id")
                by_registry = {row[0]: row[1] for row in cursor.fetchall()}
                
                # By timestamp (group by hour)
                cursor.execute("""
                    SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hour, COUNT(*) 
                    FROM twin_registry_metrics 
                    GROUP BY hour 
                    ORDER BY hour DESC 
                    LIMIT 24
                """)
                by_timestamp = {row[0]: row[1] for row in cursor.fetchall()}
            
            return MetricsSummary(
                total_metrics=total,
                average_health_score=float(avg_health),
                average_response_time=float(avg_response),
                metrics_by_registry=by_registry,
                metrics_by_timestamp=by_timestamp
            )
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            raise
    
    def cleanup_old_metrics(self, days_to_keep: int = 30) -> int:
        """Clean up old metrics data."""
        try:
            sql = "DELETE FROM twin_registry_metrics WHERE timestamp < datetime('now', '-{} days')".format(days_to_keep)
            
            with self.db_manager.connection_manager.get_cursor() as cursor:
                cursor.execute(sql)
                # Commit is handled automatically by the context manager
                
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
                response_time_ms=row['response_time_ms'],
                uptime_percentage=row['uptime_percentage'],
                error_rate=row['error_rate'],
                cpu_usage_percent=row['cpu_usage_percent'],
                memory_usage_percent=row['memory_usage_percent'],
                network_throughput_mbps=row['network_throughput_mbps'],
                storage_usage_percent=row['storage_usage_percent'],
                transaction_count=row['transaction_count'],
                data_volume_mb=row['data_volume_mb'],
                user_interaction_count=row['user_interaction_count'],
                lifecycle_events=self._deserialize_json(row['lifecycle_events']),
                performance_trends=self._deserialize_json(row['performance_trends']),
                user_activity=self._deserialize_json(row['user_activity']),
                compliance_status=self._deserialize_json(row['compliance_status']),
                security_events=self._deserialize_json(row['security_events'])
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
