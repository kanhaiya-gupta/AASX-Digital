"""
Knowledge Graph Metrics Repository

Pure async implementation using src.engine.database.connection_manager.
Provides data access layer for knowledge graph metrics operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from src.engine.database.connection_manager import ConnectionManager
from ..models.kg_graph_metrics import (
    KGGraphMetrics,
    KGGraphMetricsQuery,
    KGGraphMetricsSummary
)

logger = logging.getLogger(__name__)


class KGGraphMetricsRepository:
    """Repository for managing knowledge graph metrics data with pure async support."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the knowledge graph metrics repository."""
        self.connection_manager = connection_manager
        self.table_name = "kg_graph_metrics"
        logger.info("Knowledge Graph Metrics Repository initialized with pure async support")
    
    async def initialize(self) -> None:
        """Initialize the repository asynchronously."""
        try:
            # Verify connection
            await self.connection_manager.get_connection()
            logger.info("Knowledge Graph Metrics Repository initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Graph Metrics Repository: {e}")
            raise
    
    # ==================== CRUD Operations ====================
    
    async def create(self, metrics: KGGraphMetrics) -> KGGraphMetrics:
        """Create a new metrics entry asynchronously"""
        try:
            # Convert model to dict for insertion
            data = metrics.dict()
            
            # Build INSERT query dynamically
            columns = list(data.keys())
            placeholders = [f":{col}" for col in columns]
            
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            # Execute raw SQL
            await self.connection_manager.execute_update(query, data)
            
            logger.info(f"Created metrics entry: {metrics.metric_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to create metrics entry: {e}")
            raise
    
    async def get_by_id(self, metric_id: int) -> Optional[KGGraphMetrics]:
        """Get metrics entry by ID asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE metric_id = :metric_id"
            result = await self.connection_manager.execute_query(query, {"metric_id": metric_id})
            
            if result and len(result) > 0:
                return KGGraphMetrics(**result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get metrics entry by ID {metric_id}: {e}")
            raise
    
    async def get_by_graph_id(self, graph_id: str) -> List[KGGraphMetrics]:
        """Get all metrics entries for a specific graph asynchronously"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE graph_id = :graph_id"
            result = await self.connection_manager.execute_query(query, {"graph_id": graph_id})
            
            return [KGGraphMetrics(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get metrics entries for graph {graph_id}: {e}")
            raise
    
    async def get_by_timestamp_range(self, graph_id: str, start_time: datetime, end_time: datetime) -> List[KGGraphMetrics]:
        """Get metrics entries within a timestamp range asynchronously"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE graph_id = :graph_id 
                AND timestamp >= :start_time 
                AND timestamp <= :end_time
            """
            params = {
                "graph_id": graph_id,
                "start_time": start_time,
                "end_time": end_time
            }
            result = await self.connection_manager.execute_query(query, params)
            
            return [KGGraphMetrics(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get metrics entries by timestamp range: {e}")
            raise
    
    async def get_latest_metrics(self, graph_id: str) -> Optional[KGGraphMetrics]:
        """Get the latest metrics entry for a graph asynchronously"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE graph_id = :graph_id 
                ORDER BY timestamp DESC 
                LIMIT 1
            """
            result = await self.connection_manager.execute_query(query, {"graph_id": graph_id})
            
            if result and len(result) > 0:
                return KGGraphMetrics(**result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest metrics for graph {graph_id}: {e}")
            raise
    
    async def update(self, metrics: KGGraphMetrics) -> KGGraphMetrics:
        """Update an existing metrics entry asynchronously"""
        try:
            # Update timestamp
            metrics.timestamp = datetime.now(timezone.utc)
            
            # Convert model to dict for update
            data = metrics.dict(exclude={'metric_id'})
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in data.keys()]
            query = f"""
                UPDATE {self.table_name} 
                SET {', '.join(set_clauses)}
                WHERE metric_id = :metric_id
            """
            
            # Add metric_id to params
            params = {**data, "metric_id": metrics.metric_id}
            
            # Execute raw SQL
            await self.connection_manager.execute_update(query, params)
            
            logger.info(f"Updated metrics entry: {metrics.metric_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to update metrics entry {metrics.metric_id}: {e}")
            raise
    
    async def delete(self, metric_id: int) -> bool:
        """Delete a metrics entry asynchronously"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE metric_id = :metric_id"
            await self.connection_manager.execute_update(query, {"metric_id": metric_id})
            
            logger.info(f"Deleted metrics entry: {metric_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete metrics entry {metric_id}: {e}")
            raise
    
    # ==================== Query Operations ====================
    
    async def query(self, query_params: KGGraphMetricsQuery) -> List[KGGraphMetrics]:
        """Query metrics entries with filters asynchronously"""
        try:
            # Build query with filters
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            params = {}
            
            if query_params.graph_id:
                query += " AND graph_id = :graph_id"
                params["graph_id"] = query_params.graph_id
            if query_params.start_timestamp:
                query += " AND timestamp >= :start_timestamp"
                params["start_timestamp"] = query_params.start_timestamp
            if query_params.end_timestamp:
                query += " AND timestamp <= :end_timestamp"
                params["end_timestamp"] = query_params.end_timestamp
            if query_params.metric_type:
                # Filter by metric type (this would need to be implemented based on your metric_type logic)
                pass
            
            # Add pagination
            query += " LIMIT :limit OFFSET :offset"
            params["limit"] = query_params.limit
            params["offset"] = query_params.offset
            
            result = await self.connection_manager.execute_query(query, params)
            
            return [KGGraphMetrics(**row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to query metrics entries: {e}")
            raise
    
    async def get_total_count(self) -> int:
        """Get total count of metrics entries asynchronously"""
        try:
            query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            result = await self.connection_manager.execute_query(query, {})
            return result[0]['total'] if result and len(result) > 0 else 0
            
        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            raise
    
    # ==================== Business Logic Operations ====================
    
    async def get_health_metrics(self, graph_id: str, hours: int = 24) -> List[KGGraphMetrics]:
        """Get health metrics for a graph over the last N hours asynchronously"""
        try:
            from datetime import timedelta
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            return await self.get_by_timestamp_range(graph_id, start_time, end_time)
        except Exception as e:
            logger.error(f"Failed to get health metrics: {e}")
            raise
    
    async def get_performance_metrics(self, graph_id: str, hours: int = 24) -> List[KGGraphMetrics]:
        """Get performance metrics for a graph over the last N hours asynchronously"""
        try:
            from datetime import timedelta
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            metrics = await self.get_by_timestamp_range(graph_id, start_time, end_time)
            # Filter for performance-related metrics
            return [m for m in metrics if m.response_time_ms is not None or m.graph_traversal_speed_ms is not None]
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            raise
    
    async def get_neo4j_metrics(self, graph_id: str, hours: int = 24) -> List[KGGraphMetrics]:
        """Get Neo4j-specific metrics for a graph over the last N hours asynchronously"""
        try:
            from datetime import timedelta
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            metrics = await self.get_by_timestamp_range(graph_id, start_time, end_time)
            # Filter for Neo4j-related metrics
            return [m for m in metrics if m.neo4j_connection_status is not None]
        except Exception as e:
            logger.error(f"Failed to get Neo4j metrics: {e}")
            raise
    
    async def get_user_activity_metrics(self, graph_id: str, hours: int = 24) -> List[KGGraphMetrics]:
        """Get user activity metrics for a graph over the last N hours asynchronously"""
        try:
            from datetime import timedelta
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            metrics = await self.get_by_timestamp_range(graph_id, start_time, end_time)
            # Filter for user activity metrics
            return [m for m in metrics if m.user_interaction_count is not None or m.query_execution_count is not None]
        except Exception as e:
            logger.error(f"Failed to get user activity metrics: {e}")
            raise
    
    # ==================== Summary & Analytics ====================
    
    async def get_summary(self) -> KGGraphMetricsSummary:
        """Get comprehensive summary of metrics asynchronously"""
        try:
            # Get total metrics
            total_query = f"SELECT COUNT(*) as total FROM {self.table_name}"
            total_result = await self.connection_manager.execute_query(total_query, {})
            total_metrics = total_result[0]['total'] if total_result and len(total_result) > 0 else 0
            
            # Calculate average health score
            health_query = f"SELECT health_score FROM {self.table_name} WHERE health_score IS NOT NULL"
            health_result = await self.connection_manager.execute_query(health_query, {})
            
            if health_result:
                avg_health_score = sum(row['health_score'] for row in health_result if 'health_score' in row and row['health_score']) / len(health_result)
            else:
                avg_health_score = 0.0
            
            # Calculate average response time
            response_query = f"SELECT response_time_ms FROM {self.table_name} WHERE response_time_ms IS NOT NULL"
            response_result = await self.connection_manager.execute_query(response_query, {})
            
            if response_result:
                avg_response_time = sum(row['response_time_ms'] for row in response_result if 'response_time_ms' in row and row['response_time_ms']) / len(response_result)
            else:
                avg_response_time = 0.0
            
            # Calculate total user interactions
            interactions_query = f"SELECT user_interaction_count FROM {self.table_name} WHERE user_interaction_count IS NOT NULL"
            interactions_result = await self.connection_manager.execute_query(interactions_query, {})
                
                total_user_interactions = sum(row['user_interaction_count'] for row in interactions_result if 'user_interaction_count' in row and row['user_interaction_count'])
                
                # Calculate total queries executed
                queries_query = f"SELECT query_execution_count FROM {self.table_name} WHERE query_execution_count IS NOT NULL"
                queries_result = await self.connection_manager.execute_query(queries_query, {})
                
                total_queries_executed = sum(row['query_execution_count'] for row in queries_result if 'query_execution_count' in row and row['query_execution_count'])
                
                # Calculate average data quality
                quality_query = f"SELECT data_freshness_score FROM {self.table_name} WHERE data_freshness_score IS NOT NULL"
                quality_result = await self.connection_manager.execute_query(quality_query, {})
                
                if quality_result:
                    avg_data_quality = sum(row['data_freshness_score'] for row in quality_result if 'data_freshness_score' in row and row['data_freshness_score']) / len(quality_result)
                else:
                    avg_data_quality = 0.0
                
                # Determine performance trend (simplified logic)
                performance_trend = "stable"  # This would need more sophisticated logic
                
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
            logger.error(f"Failed to get metrics summary: {e}")
            raise
    
    # ==================== Cleanup ====================
    
    async def cleanup(self) -> None:
        """Cleanup repository resources asynchronously"""
        try:
            logger.info("Knowledge Graph Metrics Repository cleanup completed")
        except Exception as e:
            logger.error(f"Failed to cleanup Knowledge Graph Metrics Repository: {e}")
            raise
