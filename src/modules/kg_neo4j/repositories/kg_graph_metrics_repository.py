"""
Knowledge Graph Metrics Repository

Pure async implementation using src.engine.database.connection_manager.
Provides data access layer for knowledge graph metrics operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from src.engine.database.connection_manager import ConnectionManager
from src.engine.database.schema.modules.kg_neo4j import kg_graph_metrics
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
        self.table = kg_graph_metrics
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
            async with self.connection_manager.get_connection() as conn:
                # Convert model to dict for insertion
                data = metrics.dict()
                
                # Insert into database
                query = self.table.insert()
                result = await conn.execute(query, data)
                
                # Get the created record
                created_id = result.inserted_primary_key[0]
                metrics.metric_id = created_id
                
                logger.info(f"Created metrics entry: {metrics.metric_id}")
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to create metrics entry: {e}")
            raise
    
    async def get_by_id(self, metric_id: int) -> Optional[KGGraphMetrics]:
        """Get metrics entry by ID asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.metric_id == metric_id)
                result = await conn.execute(query)
                row = result.fetchone()
                
                if row:
                    return KGGraphMetrics(**dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Failed to get metrics entry by ID {metric_id}: {e}")
            raise
    
    async def get_by_graph_id(self, graph_id: str) -> List[KGGraphMetrics]:
        """Get all metrics entries for a specific graph asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(self.table.c.graph_id == graph_id)
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphMetrics(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get metrics entries for graph {graph_id}: {e}")
            raise
    
    async def get_by_timestamp_range(self, graph_id: str, start_time: datetime, end_time: datetime) -> List[KGGraphMetrics]:
        """Get metrics entries within a timestamp range asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(
                    (self.table.c.graph_id == graph_id) &
                    (self.table.c.timestamp >= start_time) &
                    (self.table.c.timestamp <= end_time)
                )
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphMetrics(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get metrics entries by timestamp range: {e}")
            raise
    
    async def get_latest_metrics(self, graph_id: str) -> Optional[KGGraphMetrics]:
        """Get the latest metrics entry for a graph asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select().where(
                    self.table.c.graph_id == graph_id
                ).order_by(self.table.c.timestamp.desc()).limit(1)
                result = await conn.execute(query)
                row = result.fetchone()
                
                if row:
                    return KGGraphMetrics(**dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Failed to get latest metrics for graph {graph_id}: {e}")
            raise
    
    async def update(self, metrics: KGGraphMetrics) -> KGGraphMetrics:
        """Update an existing metrics entry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Update timestamp
                metrics.timestamp = datetime.now(timezone.utc)
                
                # Convert model to dict for update
                data = metrics.dict(exclude={'metric_id'})
                
                # Update in database
                query = self.table.update().where(
                    self.table.c.metric_id == metrics.metric_id
                )
                await conn.execute(query, data)
                
                logger.info(f"Updated metrics entry: {metrics.metric_id}")
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to update metrics entry {metrics.metric_id}: {e}")
            raise
    
    async def delete(self, metric_id: int) -> bool:
        """Delete a metrics entry asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.delete().where(self.table.c.metric_id == metric_id)
                result = await conn.execute(query)
                
                deleted = result.rowcount > 0
                if deleted:
                    logger.info(f"Deleted metrics entry: {metric_id}")
                else:
                    logger.warning(f"Metrics entry not found for deletion: {metric_id}")
                
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to delete metrics entry {metric_id}: {e}")
            raise
    
    # ==================== Query Operations ====================
    
    async def query(self, query_params: KGGraphMetricsQuery) -> List[KGGraphMetrics]:
        """Query metrics entries with filters asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                # Build query with filters
                query = self.table.select()
                
                if query_params.graph_id:
                    query = query.where(self.table.c.graph_id == query_params.graph_id)
                if query_params.start_timestamp:
                    query = query.where(self.table.c.timestamp >= query_params.start_timestamp)
                if query_params.end_timestamp:
                    query = query.where(self.table.c.timestamp <= query_params.end_timestamp)
                if query_params.metric_type:
                    # Filter by metric type (this would need to be implemented based on your metric_type logic)
                    pass
                
                # Add pagination
                query = query.limit(query_params.limit).offset(query_params.offset)
                
                result = await conn.execute(query)
                rows = result.fetchall()
                
                return [KGGraphMetrics(**dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to query metrics entries: {e}")
            raise
    
    async def get_total_count(self) -> int:
        """Get total count of metrics entries asynchronously"""
        try:
            async with self.connection_manager.get_connection() as conn:
                query = self.table.select()
                result = await conn.execute(query)
                rows = result.fetchall()
                return len(rows)
                
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
            async with self.connection_manager.get_connection() as conn:
                # Get total metrics
                total_query = self.table.select()
                total_result = await conn.execute(total_query)
                total_metrics = len(total_result.fetchall())
                
                # Calculate average health score
                health_query = self.table.select(self.table.c.health_score).where(
                    self.table.c.health_score.isnot(None)
                )
                health_result = await conn.execute(health_query)
                health_rows = health_result.fetchall()
                
                if health_rows:
                    avg_health_score = sum(row.health_score for row in health_rows) / len(health_rows)
                else:
                    avg_health_score = 0.0
                
                # Calculate average response time
                response_query = self.table.select(self.table.c.response_time_ms).where(
                    self.table.c.response_time_ms.isnot(None)
                )
                response_result = await conn.execute(response_query)
                response_rows = response_result.fetchall()
                
                if response_rows:
                    avg_response_time = sum(row.response_time_ms for row in response_rows) / len(response_rows)
                else:
                    avg_response_time = 0.0
                
                # Calculate total user interactions
                interactions_query = self.table.select(self.table.c.user_interaction_count).where(
                    self.table.c.user_interaction_count.isnot(None)
                )
                interactions_result = await conn.execute(interactions_query)
                interactions_rows = interactions_result.fetchall()
                
                total_user_interactions = sum(row.user_interaction_count for row in interactions_rows if row.user_interaction_count)
                
                # Calculate total queries executed
                queries_query = self.table.select(self.table.c.query_execution_count).where(
                    self.table.c.query_execution_count.isnot(None)
                )
                queries_result = await conn.execute(queries_query)
                queries_rows = queries_result.fetchall()
                
                total_queries_executed = sum(row.query_execution_count for row in queries_rows if row.query_execution_count)
                
                # Calculate average data quality
                quality_query = self.table.select(self.table.c.data_freshness_score).where(
                    self.table.c.data_freshness_score.isnot(None)
                )
                quality_result = await conn.execute(quality_query)
                quality_rows = quality_result.fetchall()
                
                if quality_rows:
                    avg_data_quality = sum(row.data_freshness_score for row in quality_rows) / len(quality_rows)
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
