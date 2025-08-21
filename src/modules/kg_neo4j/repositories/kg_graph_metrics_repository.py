"""
Knowledge Graph Metrics Repository

Updated to use our new comprehensive database schema.
Handles knowledge graph metrics operations with the new kg_graph_metrics table.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.base_repository import BaseRepository
from src.kg_neo4j.models.kg_graph_metrics import (
    KGGraphMetrics,
    KGGraphMetricsQuery,
    KGGraphMetricsSummary
)

logger = logging.getLogger(__name__)


class KGGraphMetricsRepository(BaseRepository[KGGraphMetrics]):
    """Repository for managing knowledge graph metrics data with new comprehensive schema."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        """Initialize the knowledge graph metrics repository."""
        super().__init__(db_manager, KGGraphMetrics)
        logger.info("Knowledge Graph Metrics Repository initialized with new schema")
    
    def _get_table_name(self) -> str:
        """Get the table name for this repository."""
        return "kg_graph_metrics"
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for this table."""
        return [
            "metric_id", "graph_id", "timestamp", "health_score", "response_time_ms", "uptime_percentage",
            "error_rate", "neo4j_connection_status", "neo4j_query_response_time_ms", "neo4j_import_speed_nodes_per_sec",
            "neo4j_import_speed_rels_per_sec", "neo4j_memory_usage_mb", "neo4j_disk_usage_mb",
            "graph_traversal_speed_ms", "graph_query_complexity_score", "graph_visualization_performance",
            "graph_analysis_accuracy", "user_interaction_count", "query_execution_count", "visualization_view_count",
            "export_operation_count", "data_freshness_score", "data_completeness_score", "data_consistency_score",
            "data_accuracy_score", "cpu_usage_percent", "memory_usage_percent", "network_throughput_mbps",
            "storage_usage_percent", "performance_trends", "resource_utilization_trends", "user_activity",
            "query_patterns", "compliance_status", "security_events", "graph_analytics", "relationship_patterns"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for knowledge graph metrics table."""
        return "metric_id"
    
    def _deserialize_json_fields(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize JSON fields from database row."""
        import json
        
        # Fields that are stored as JSON strings
        json_fields = [
            'performance_trends', 'resource_utilization_trends', 'user_activity',
            'query_patterns', 'compliance_status', 'security_events', 
            'graph_analytics', 'relationship_patterns'
        ]
        
        deserialized_row = dict(row)
        for field in json_fields:
            if field in deserialized_row and deserialized_row[field]:
                try:
                    if isinstance(deserialized_row[field], str):
                        deserialized_row[field] = json.loads(deserialized_row[field])
                except (json.JSONDecodeError, TypeError):
                    # If deserialization fails, keep the original value
                    logger.warning(f"Failed to deserialize JSON field {field}: {deserialized_row[field]}")
        
        return deserialized_row
    
    async def initialize(self) -> None:
        """Initialize the repository - tables already exist from Phase 1."""
        try:
            logger.info("Knowledge Graph Metrics Repository ready - tables already exist")
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Graph Metrics Repository: {e}")
            raise
    
    async def create_metrics(self, metrics: KGGraphMetrics) -> KGGraphMetrics:
        """Create new knowledge graph metrics entry."""
        try:
            # Get columns excluding the auto-generated primary key
            columns = [col for col in self._get_columns() if col != self._get_primary_key_column()]
            
            # Debug: Print column count
            logger.info(f"🔍 DEBUG: SQL columns count: {len(columns)}")
            
            sql = f"""
            INSERT INTO kg_graph_metrics (
                {', '.join(columns)}
            ) VALUES ({', '.join(['?' for _ in columns])})
            """
            
            # Convert dictionary/list fields to JSON strings for SQLite compatibility
            import json
            performance_trends_json = json.dumps(metrics.performance_trends) if metrics.performance_trends else '{}'
            resource_utilization_trends_json = json.dumps(metrics.resource_utilization_trends) if metrics.resource_utilization_trends else '{}'
            user_activity_json = json.dumps(metrics.user_activity) if metrics.user_activity else '{}'
            query_patterns_json = json.dumps(metrics.query_patterns) if metrics.query_patterns else '{}'
            compliance_status_json = json.dumps(metrics.compliance_status) if metrics.compliance_status else '{}'
            security_events_json = json.dumps(metrics.security_events) if metrics.security_events else '{}'
            graph_analytics_json = json.dumps(metrics.graph_analytics) if metrics.graph_analytics else '{}'
            relationship_patterns_json = json.dumps(metrics.relationship_patterns) if metrics.relationship_patterns else '{}'
            
            params = (
                metrics.graph_id, metrics.timestamp, metrics.health_score, metrics.response_time_ms,
                metrics.uptime_percentage, metrics.error_rate, metrics.neo4j_connection_status,
                metrics.neo4j_query_response_time_ms, metrics.neo4j_import_speed_nodes_per_sec,
                metrics.neo4j_import_speed_rels_per_sec, metrics.neo4j_memory_usage_mb, metrics.neo4j_disk_usage_mb,
                metrics.graph_traversal_speed_ms, metrics.graph_query_complexity_score, metrics.graph_visualization_performance,
                metrics.graph_analysis_accuracy, metrics.user_interaction_count, metrics.query_execution_count,
                metrics.visualization_view_count, metrics.export_operation_count, metrics.data_freshness_score,
                metrics.data_completeness_score, metrics.data_consistency_score, metrics.data_accuracy_score,
                metrics.cpu_usage_percent, metrics.memory_usage_percent, metrics.network_throughput_mbps,
                metrics.storage_usage_percent, performance_trends_json, resource_utilization_trends_json,
                user_activity_json, query_patterns_json, compliance_status_json, security_events_json,
                graph_analytics_json, relationship_patterns_json
            )
            
            # Debug: Print params count
            logger.info(f"🔍 DEBUG: Params count: {len(params)}")
            
            await self.db_manager.execute_update(sql, params)
            logger.info(f"✅ Created knowledge graph metrics entry for graph: {metrics.graph_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to create knowledge graph metrics: {e}")
            raise
    
    async def get_by_graph_id(self, graph_id: str, limit: int = 100) -> List[KGGraphMetrics]:
        """Get metrics by graph ID."""
        try:
            sql = "SELECT * FROM kg_graph_metrics WHERE graph_id = ? ORDER BY timestamp DESC LIMIT ?"
            result = await self.db_manager.execute_query(sql, (graph_id, limit))
            
            metrics = []
            for row in result:
                # Deserialize JSON fields before creating the model
                deserialized_row = self._deserialize_json_fields(row)
                metrics.append(KGGraphMetrics(**deserialized_row))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by graph_id {graph_id}: {e}")
            return []
    
    async def get_summary(self) -> KGGraphMetricsSummary:
        """Get summary statistics for knowledge graph metrics."""
        try:
            # Get total metrics count
            total_sql = "SELECT COUNT(*) as total FROM kg_graph_metrics"
            total_result = await self.db_manager.execute_query(total_sql)
            total_metrics = total_result[0]['total'] if total_result else 0
            
            # Get average health score
            health_sql = "SELECT AVG(health_score) as avg_health FROM kg_graph_metrics WHERE health_score IS NOT NULL"
            health_result = await self.db_manager.execute_query(health_sql)
            avg_health_score = health_result[0]['avg_health'] if health_result and health_result[0]['avg_health'] else 0.0
            
            # Get average response time
            response_sql = "SELECT AVG(response_time_ms) as avg_response FROM kg_graph_metrics WHERE response_time_ms IS NOT NULL"
            response_result = await self.db_manager.execute_query(response_sql)
            avg_response_time = response_result[0]['avg_response'] if response_result and response_result[0]['avg_response'] else 0.0
            
            # Get total user interactions
            interactions_sql = "SELECT SUM(user_interaction_count) as total_interactions FROM kg_graph_metrics WHERE user_interaction_count IS NOT NULL"
            interactions_result = await self.db_manager.execute_query(interactions_sql)
            total_user_interactions = interactions_result[0]['total_interactions'] if interactions_result and interactions_result[0]['total_interactions'] else 0
            
            # Get total queries executed
            queries_sql = "SELECT SUM(query_execution_count) as total_queries FROM kg_graph_metrics WHERE query_execution_count IS NOT NULL"
            queries_result = await self.db_manager.execute_query(queries_sql)
            total_queries_executed = queries_result[0]['total_queries'] if queries_result and queries_result[0]['total_queries'] else 0
            
            # Get average data quality (using data_accuracy_score as the main quality indicator)
            quality_sql = "SELECT AVG(data_accuracy_score) as avg_quality FROM kg_graph_metrics WHERE data_accuracy_score IS NOT NULL"
            quality_result = await self.db_manager.execute_query(quality_sql)
            avg_data_quality = quality_result[0]['avg_quality'] if quality_result and quality_result[0]['avg_quality'] else 0.0
            
            # Determine performance trend (simplified)
            performance_trend = "stable"  # This could be calculated from historical data
            
            return KGGraphMetricsSummary(
                total_metrics=total_metrics,
                avg_health_score=avg_health_score,
                avg_response_time=avg_response_time,
                total_user_interactions=total_user_interactions,
                total_queries_executed=total_queries_executed,
                avg_data_quality=avg_data_quality,
                performance_trend=performance_trend
            )
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return KGGraphMetricsSummary(
                total_metrics=0,
                avg_health_score=0.0,
                avg_response_time=0.0,
                total_user_interactions=0,
                total_queries_executed=0,
                avg_data_quality=0.0,
                performance_trend="unknown"
            )
    
    async def get_by_timestamp_range(self, start_timestamp: datetime, end_timestamp: datetime, limit: int = 100) -> List[KGGraphMetrics]:
        """Get metrics by timestamp range."""
        try:
            sql = "SELECT * FROM kg_graph_metrics WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC LIMIT ?"
            params = (start_timestamp.isoformat(), end_timestamp.isoformat(), limit)
            result = await self.db_manager.execute_query(sql, params)
            
            metrics = []
            for row in result:
                metrics.append(KGGraphMetrics(**row))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by timestamp range: {e}")
            return []
    
    async def get_latest_metrics_by_graph_id(self, graph_id: str) -> Optional[KGGraphMetrics]:
        """Get the latest metrics for a specific graph."""
        try:
            sql = "SELECT * FROM kg_graph_metrics WHERE graph_id = ? ORDER BY timestamp DESC LIMIT 1"
            result = await self.db_manager.execute_query(sql, (graph_id,))
            
            if result and len(result) > 0:
                return KGGraphMetrics(**result[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest metrics for graph_id {graph_id}: {e}")
            return None
    
    async def get_metrics_by_health_score(self, min_health_score: int, max_health_score: int, limit: int = 100) -> List[KGGraphMetrics]:
        """Get metrics within a health score range."""
        try:
            sql = "SELECT * FROM kg_graph_metrics WHERE health_score BETWEEN ? AND ? ORDER BY timestamp DESC LIMIT ?"
            params = (min_health_score, max_health_score, limit)
            result = await self.db_manager.execute_query(sql, params)
            
            metrics = []
            for row in result:
                metrics.append(KGGraphMetrics(**row))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by health score range: {e}")
            return []
    
    async def get_metrics_by_neo4j_status(self, connection_status: str, limit: int = 100) -> List[KGGraphMetrics]:
        """Get metrics by Neo4j connection status."""
        try:
            sql = "SELECT * FROM kg_graph_metrics WHERE neo4j_connection_status = ? ORDER BY timestamp DESC LIMIT ?"
            result = await self.db_manager.execute_query(sql, (connection_status, limit))
            
            metrics = []
            for row in result:
                metrics.append(KGGraphMetrics(**row))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics by Neo4j status {connection_status}: {e}")
            return []
    
    async def get_performance_metrics_by_graph_id(self, graph_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get performance-focused metrics for a specific graph."""
        try:
            sql = """
            SELECT timestamp, graph_traversal_speed_ms, graph_query_complexity_score, 
                   graph_visualization_performance, graph_analysis_accuracy, 
                   neo4j_query_response_time_ms, response_time_ms
            FROM kg_graph_metrics 
            WHERE graph_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            result = await self.db_manager.execute_query(sql, (graph_id, limit))
            
            performance_metrics = []
            for row in result:
                performance_metrics.append({
                    'timestamp': row['timestamp'],
                    'traversal_speed': row['graph_traversal_speed_ms'],
                    'query_complexity': row['graph_query_complexity_score'],
                    'visualization_performance': row['graph_visualization_performance'],
                    'analysis_accuracy': row['graph_analysis_accuracy'],
                    'neo4j_response_time': row['neo4j_query_response_time_ms'],
                    'overall_response_time': row['response_time_ms']
                })
            
            return performance_metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics for graph_id {graph_id}: {e}")
            return []
    
    async def get_user_activity_metrics_by_graph_id(self, graph_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user activity metrics for a specific graph."""
        try:
            sql = """
            SELECT timestamp, user_interaction_count, query_execution_count, 
                   visualization_view_count, export_operation_count
            FROM kg_graph_metrics 
            WHERE graph_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            result = await self.db_manager.execute_query(sql, (graph_id, limit))
            
            activity_metrics = []
            for row in result:
                activity_metrics.append({
                    'timestamp': row['timestamp'],
                    'interactions': row['user_interaction_count'],
                    'queries': row['query_execution_count'],
                    'visualizations': row['visualization_view_count'],
                    'exports': row['export_operation_count']
                })
            
            return activity_metrics
            
        except Exception as e:
            logger.error(f"Error getting user activity metrics for graph_id {graph_id}: {e}")
            return []
    
    async def get_data_quality_metrics_by_graph_id(self, graph_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get data quality metrics for a specific graph."""
        try:
            sql = """
            SELECT timestamp, data_freshness_score, data_completeness_score, 
                   data_consistency_score, data_accuracy_score
            FROM kg_graph_metrics 
            WHERE graph_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            result = await self.db_manager.execute_query(sql, (graph_id, limit))
            
            quality_metrics = []
            for row in result:
                quality_metrics.append({
                    'timestamp': row['timestamp'],
                    'freshness': row['data_freshness_score'],
                    'completeness': row['data_completeness_score'],
                    'consistency': row['data_consistency_score'],
                    'accuracy': row['data_accuracy_score']
                })
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error getting data quality metrics for graph_id {graph_id}: {e}")
            return []
    
    async def get_system_resource_metrics_by_graph_id(self, graph_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get system resource metrics for a specific graph."""
        try:
            sql = """
            SELECT timestamp, cpu_usage_percent, memory_usage_percent, 
                   network_throughput_mbps, storage_usage_percent,
                   neo4j_memory_usage_mb, neo4j_disk_usage_mb
            FROM kg_graph_metrics 
            WHERE graph_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            result = await self.db_manager.execute_query(sql, (graph_id, limit))
            
            resource_metrics = []
            for row in result:
                resource_metrics.append({
                    'timestamp': row['timestamp'],
                    'cpu_usage': row['cpu_usage_percent'],
                    'memory_usage': row['memory_usage_percent'],
                    'network_throughput': row['network_throughput_mbps'],
                    'storage_usage': row['storage_usage_percent'],
                    'neo4j_memory': row['neo4j_memory_usage_mb'],
                    'neo4j_disk': row['neo4j_disk_usage_mb']
                })
            
            return resource_metrics
            
        except Exception as e:
            logger.error(f"Error getting system resource metrics for graph_id {graph_id}: {e}")
            return []
    
    async def get_neo4j_performance_metrics_by_graph_id(self, graph_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get Neo4j-specific performance metrics for a specific graph."""
        try:
            sql = """
            SELECT timestamp, neo4j_connection_status, neo4j_query_response_time_ms,
                   neo4j_import_speed_nodes_per_sec, neo4j_import_speed_rels_per_sec,
                   neo4j_memory_usage_mb, neo4j_disk_usage_mb
            FROM kg_graph_metrics 
            WHERE graph_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            result = await self.db_manager.execute_query(sql, (graph_id, limit))
            
            neo4j_metrics = []
            for row in result:
                neo4j_metrics.append({
                    'timestamp': row['timestamp'],
                    'connection_status': row['neo4j_connection_status'],
                    'query_response_time': row['neo4j_query_response_time_ms'],
                    'import_speed_nodes': row['neo4j_import_speed_nodes_per_sec'],
                    'import_speed_rels': row['neo4j_import_speed_rels_per_sec'],
                    'memory_usage': row['neo4j_memory_usage_mb'],
                    'disk_usage': row['neo4j_disk_usage_mb']
                })
            
            return neo4j_metrics
            
        except Exception as e:
            logger.error(f"Error getting Neo4j performance metrics for graph_id {graph_id}: {e}")
            return []
    
    async def update_metrics(self, metric_id: int, updates: Dict[str, Any]) -> bool:
        """Update specific metrics fields."""
        try:
            # Build dynamic UPDATE query
            set_clauses = []
            params = []
            
            for field, value in updates.items():
                if field in self._get_columns() and field != 'metric_id':
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
            
            if not set_clauses:
                logger.warning("No valid fields to update")
                return False
            
            # Add timestamp update and metric_id for WHERE clause
            set_clauses.append("timestamp = ?")
            params.append(datetime.now().isoformat())
            params.append(metric_id)
            
            sql = f"UPDATE kg_graph_metrics SET {', '.join(set_clauses)} WHERE metric_id = ?"
            
            await self.db_manager.execute_update(sql, params)
            logger.info(f"✅ Updated metrics entry {metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update metrics {metric_id}: {e}")
            return False
    
    async def delete_metrics_by_graph_id(self, graph_id: str) -> bool:
        """Delete all metrics for a specific graph."""
        try:
            sql = "DELETE FROM kg_graph_metrics WHERE graph_id = ?"
            await self.db_manager.execute_update(sql, (graph_id,))
            logger.info(f"✅ Deleted all metrics for graph {graph_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete metrics for graph {graph_id}: {e}")
            return False
    
    async def get_metrics_trends_by_graph_id(self, graph_id: str, days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics trends over a specified number of days."""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date.replace(day=end_date.day - days)
            
            # Get all metrics in the date range
            metrics = await self.get_by_timestamp_range(start_date, end_date, 1000)
            
            # Filter by graph_id and organize by metric type
            trends = {
                'health_scores': [],
                'response_times': [],
                'user_activity': [],
                'data_quality': [],
                'system_resources': [],
                'neo4j_performance': []
            }
            
            for metric in metrics:
                if metric.graph_id == graph_id:
                    # Health scores trend
                    if metric.health_score is not None:
                        trends['health_scores'].append({
                            'timestamp': metric.timestamp,
                            'value': metric.health_score
                        })
                    
                    # Response times trend
                    if metric.response_time_ms is not None:
                        trends['response_times'].append({
                            'timestamp': metric.timestamp,
                            'value': metric.response_time_ms
                        })
                    
                    # User activity trend
                    if metric.user_interaction_count is not None:
                        trends['user_activity'].append({
                            'timestamp': metric.timestamp,
                            'value': metric.user_interaction_count
                        })
                    
                    # Data quality trend
                    if metric.data_quality_score is not None:
                        trends['data_quality'].append({
                            'timestamp': metric.timestamp,
                            'value': metric.data_quality_score
                        })
                    
                    # System resources trend
                    if metric.cpu_usage_percent is not None:
                        trends['system_resources'].append({
                            'timestamp': metric.timestamp,
                            'cpu': metric.cpu_usage_percent,
                            'memory': metric.memory_usage_percent or 0
                        })
                    
                    # Neo4j performance trend
                    if metric.neo4j_query_response_time_ms is not None:
                        trends['neo4j_performance'].append({
                            'timestamp': metric.timestamp,
                            'query_time': metric.neo4j_query_response_time_ms,
                            'connection_status': metric.neo4j_connection_status
                        })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting metrics trends for graph_id {graph_id}: {e}")
            return {}
    
    async def cleanup_old_metrics(self, days_to_keep: int = 90) -> int:
        """Clean up old metrics data to prevent database bloat."""
        try:
            cutoff_date = datetime.now().replace(day=datetime.now().day - days_to_keep)
            
            sql = "DELETE FROM kg_graph_metrics WHERE timestamp < ?"
            result = await self.db_manager.execute_update(sql, (cutoff_date.isoformat(),))
            
            logger.info(f"✅ Cleaned up metrics older than {days_to_keep} days")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old metrics: {e}")
            return 0
