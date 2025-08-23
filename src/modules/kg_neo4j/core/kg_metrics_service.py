"""
Knowledge Graph Metrics Service

Heavy lifting business logic for Knowledge Graph metrics operations.
Handles complex metrics analysis, aggregation, and business intelligence.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import asdict

from src.engine.database.connection_manager import ConnectionManager
from src.kg_neo4j.repositories.kg_graph_metrics_repository import KGGraphMetricsRepository
from src.kg_neo4j.models.kg_graph_metrics import KGGraphMetrics, KGGraphMetricsQuery, KGGraphMetricsSummary

logger = logging.getLogger(__name__)


class KGMetricsService:
    """Business logic service for Knowledge Graph metrics operations."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the metrics service with connection manager."""
        self.connection_manager = connection_manager
        self.metrics_repo = KGGraphMetricsRepository(connection_manager)
        logger.info("Knowledge Graph Metrics Service initialized with pure async support")
    
    async def initialize(self) -> None:
        """Initialize the metrics service."""
        try:
            await self.metrics_repo.initialize()
            logger.info("✅ Knowledge Graph Metrics Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Metrics Service: {e}")
            raise
    
    # ==================== METRICS COLLECTION & RECORDING ====================
    
    async def record_system_metrics(
        self, 
        graph_id: str, 
        system_metrics: Dict[str, Any]
    ) -> bool:
        """Record comprehensive system metrics for a graph."""
        try:
            # Create metrics entry with system data
            metrics = KGGraphMetrics(
                graph_id=graph_id,
                timestamp=datetime.now(timezone.utc),
                health_score=system_metrics.get('health_score', 100),
                response_time_ms=system_metrics.get('response_time_ms', 0.0),
                uptime_percentage=system_metrics.get('uptime_percentage', 100.0),
                error_rate=system_metrics.get('error_rate', 0.0),
                cpu_usage_percent=system_metrics.get('cpu_usage_percent', 0.0),
                memory_usage_percent=system_metrics.get('memory_usage_percent', 0.0),
                network_throughput_mbps=system_metrics.get('network_throughput_mbps', 0.0),
                storage_usage_percent=system_metrics.get('storage_usage_percent', 0.0),
                neo4j_connection_status=system_metrics.get('neo4j_connection_status', 'disconnected'),
                neo4j_query_response_time_ms=system_metrics.get('neo4j_query_response_time_ms', 0.0),
                neo4j_memory_usage_mb=system_metrics.get('neo4j_memory_usage_mb', 0.0),
                neo4j_disk_usage_mb=system_metrics.get('neo4j_disk_usage_mb', 0.0)
            )
            
            await self.metrics_repo.create(metrics)
            logger.info(f"✅ Recorded system metrics for graph {graph_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record system metrics for graph {graph_id}: {e}")
            return False
    
    async def record_user_interaction(
        self, 
        graph_id: str, 
        interaction_type: str, 
        interaction_data: Dict[str, Any]
    ) -> bool:
        """Record user interaction metrics."""
        try:
            # Get current metrics to increment counters
            current_metrics = await self.metrics_repo.get_latest_metrics(graph_id)
            
            # Create new metrics entry
            metrics = KGGraphMetrics(
                graph_id=graph_id,
                timestamp=datetime.now(timezone.utc),
                health_score=current_metrics.health_score if current_metrics else 100,
                user_interaction_count=1,
                query_execution_count=1 if interaction_type == 'query' else 0,
                visualization_view_count=1 if interaction_type == 'visualization' else 0,
                export_operation_count=1 if interaction_type == 'export' else 0,
                user_activity={
                    'interaction_type': interaction_type,
                    'interaction_data': interaction_data,
                    'timestamp': datetime.now(timezone.utc)
                }
            )
            
            await self.metrics_repo.create(metrics)
            logger.info(f"✅ Recorded user interaction {interaction_type} for graph {graph_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record user interaction for graph {graph_id}: {e}")
            return False
    
    async def record_graph_performance(
        self, 
        graph_id: str, 
        performance_data: Dict[str, Any]
    ) -> bool:
        """Record graph performance metrics."""
        try:
            metrics = KGGraphMetrics(
                graph_id=graph_id,
                timestamp=datetime.now(timezone.utc),
                graph_traversal_speed_ms=performance_data.get('traversal_speed_ms', 0.0),
                graph_query_complexity_score=performance_data.get('query_complexity_score', 0.0),
                graph_visualization_performance=performance_data.get('visualization_performance', 0.0),
                graph_analysis_accuracy=performance_data.get('analysis_accuracy', 0.0),
                response_time_ms=performance_data.get('response_time_ms', 0.0),
                performance_trends={
                    'traversal_speed': performance_data.get('traversal_speed_ms', 0.0),
                    'query_complexity': performance_data.get('query_complexity_score', 0.0),
                    'visualization_performance': performance_data.get('visualization_performance', 0.0),
                    'analysis_accuracy': performance_data.get('analysis_accuracy', 0.0),
                    'timestamp': datetime.now(timezone.utc)
                }
            )
            
            await self.metrics_repo.create(metrics)
            logger.info(f"✅ Recorded performance metrics for graph {graph_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record performance metrics for graph {graph_id}: {e}")
            return False
    
    # ==================== METRICS ANALYSIS & BUSINESS INTELLIGENCE ====================
    
    async def get_comprehensive_metrics_summary(
        self, 
        graph_id: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive metrics summary with business intelligence insights."""
        try:
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Get metrics in date range for this graph
            metrics = await self.metrics_repo.get_by_timestamp_range(graph_id, start_date, end_date)
            
            # No need to filter since repository already filters by graph_id
            graph_metrics = metrics
            
            if not graph_metrics:
                return {
                    "graph_id": graph_id,
                    "period_days": days,
                    "message": "No metrics available for the specified period",
                    "summary_generated_at": datetime.now(timezone.utc)
                }
            
            # Calculate comprehensive summary
            summary = await self._calculate_comprehensive_summary(graph_metrics, days)
            
            # Add business intelligence insights
            insights = await self._generate_business_insights(graph_metrics, summary)
            
            return {
                "graph_id": graph_id,
                "period_days": days,
                "summary": summary,
                "insights": insights,
                "summary_generated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get comprehensive metrics summary for graph {graph_id}: {e}")
            return {"error": str(e)}
    
    async def get_performance_trends(
        self, 
        graph_id: str, 
        metric_type: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance trends for specific metric types."""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            metrics = await self.metrics_repo.get_by_timestamp_range(graph_id, start_date, end_date)
            graph_metrics = metrics
            
            if not graph_metrics:
                return {"error": "No metrics available for the specified period"}
            
            # Extract trend data based on metric type
            trend_data = await self._extract_trend_data(graph_metrics, metric_type)
            
            # Calculate trend analysis
            trend_analysis = await self._analyze_trends(trend_data)
            
            return {
                "graph_id": graph_id,
                "metric_type": metric_type,
                "period_days": days,
                "trend_data": trend_data,
                "trend_analysis": trend_analysis,
                "generated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance trends for graph {graph_id}: {e}")
            return {"error": str(e)}
    
    async def get_health_score_trend(
        self, 
        graph_id: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get health score trend analysis."""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            metrics = await self.metrics_repo.get_by_timestamp_range(graph_id, start_date, end_date)
            graph_metrics = metrics
            
            if not graph_metrics:
                return {"error": "No health metrics available for the specified period"}
            
            # Extract health scores with timestamps
            health_data = []
            for metric in graph_metrics:
                if metric.health_score is not None:
                    health_data.append({
                        'timestamp': metric.timestamp,
                        'health_score': metric.health_score,
                        'date': metric.timestamp.date().isoformat()
                    })
            
            # Sort by timestamp
            health_data.sort(key=lambda x: x['timestamp'])
            
            # Calculate trend analysis
            trend_analysis = await self._analyze_health_trend(health_data)
            
            return {
                "graph_id": graph_id,
                "period_days": days,
                "health_data": health_data,
                "trend_analysis": trend_analysis,
                "generated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get health score trend for graph {graph_id}: {e}")
            return {"error": str(e)}
    
    # ==================== METRICS CLEANUP & MAINTENANCE ====================
    
    async def cleanup_old_metrics(self, days_to_keep: int = 90) -> int:
        """Clean up old metrics data to prevent database bloat."""
        try:
            await self.metrics_repo.cleanup()
            logger.info(f"✅ Cleaned up old metrics entries")
            return 0  # Repository cleanup doesn't return count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old metrics: {e}")
            return 0
    
    async def get_metrics_storage_info(self) -> Dict[str, Any]:
        """Get information about metrics storage usage."""
        try:
            # Get total metrics count
            total_metrics = await self.metrics_repo.get_total_count()
            
            # Get oldest and newest timestamps
            oldest_metric = await self._get_oldest_metric()
            newest_metric = await self._get_newest_metric()
            
            return {
                "total_metrics": total_metrics,
                "oldest_metric_timestamp": oldest_metric.timestamp if oldest_metric else None,
                "newest_metric_timestamp": newest_metric.timestamp if newest_metric else None,
                "estimated_storage_mb": total_metrics * 0.001,  # Rough estimate
                "generated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get metrics storage info: {e}")
            return {"error": str(e)}
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    async def _calculate_comprehensive_summary(
        self, 
        metrics: List[KGGraphMetrics], 
        days: int
    ) -> Dict[str, Any]:
        """Calculate comprehensive metrics summary."""
        try:
            if not metrics:
                return {}
            
            # Extract numeric values
            health_scores = [m.health_score for m in metrics if m.health_score is not None]
            response_times = [m.response_time_ms for m in metrics if m.response_time_ms is not None]
            cpu_usage = [m.cpu_usage_percent for m in metrics if m.cpu_usage_percent is not None]
            memory_usage = [m.memory_usage_percent for m in metrics if m.memory_usage_percent is not None]
            
            # Calculate statistics
            summary = {
                "total_metrics": len(metrics),
                "period_days": days,
                "health_score": {
                    "average": sum(health_scores) / len(health_scores) if health_scores else 0,
                    "min": min(health_scores) if health_scores else 0,
                    "max": max(health_scores) if health_scores else 0,
                    "count": len(health_scores)
                },
                "response_time": {
                    "average": sum(response_times) / len(response_times) if response_times else 0,
                    "min": min(response_times) if response_times else 0,
                    "max": max(response_times) if response_times else 0,
                    "count": len(response_times)
                },
                "system_resources": {
                    "cpu_usage": {
                        "average": sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                        "max": max(cpu_usage) if cpu_usage else 0
                    },
                    "memory_usage": {
                        "average": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                        "max": max(memory_usage) if memory_usage else 0
                    }
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate comprehensive summary: {e}")
            return {}
    
    async def _generate_business_insights(
        self, 
        metrics: List[KGGraphMetrics], 
        summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate business intelligence insights from metrics."""
        try:
            insights = {
                "performance_insights": [],
                "health_insights": [],
                "resource_insights": [],
                "recommendations": []
            }
            
            # Health score insights
            if summary.get("health_score", {}).get("average", 0) < 70:
                insights["health_insights"].append("Health score is below optimal levels")
                insights["recommendations"].append("Investigate system health and performance issues")
            
            # Response time insights
            avg_response = summary.get("response_time", {}).get("average", 0)
            if avg_response > 1000:  # More than 1 second
                insights["performance_insights"].append("Response times are above acceptable thresholds")
                insights["recommendations"].append("Optimize query performance and system resources")
            
            # Resource usage insights
            cpu_avg = summary.get("system_resources", {}).get("cpu_usage", {}).get("average", 0)
            memory_avg = summary.get("system_resources", {}).get("memory_usage", {}).get("average", 0)
            
            if cpu_avg > 80:
                insights["resource_insights"].append("CPU usage is consistently high")
                insights["recommendations"].append("Consider scaling CPU resources or optimizing operations")
            
            if memory_avg > 80:
                insights["resource_insights"].append("Memory usage is consistently high")
                insights["recommendations"].append("Consider scaling memory resources or optimizing memory usage")
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to generate business insights: {e}")
            return {"error": str(e)}
    
    async def _extract_trend_data(
        self, 
        metrics: List[KGGraphMetrics], 
        metric_type: str
    ) -> List[Dict[str, Any]]:
        """Extract trend data for specific metric types."""
        try:
            trend_data = []
            
            for metric in metrics:
                if metric_type == "health_score" and metric.health_score is not None:
                    trend_data.append({
                        'timestamp': metric.timestamp,
                        'value': metric.health_score
                    })
                elif metric_type == "response_time" and metric.response_time_ms is not None:
                    trend_data.append({
                        'timestamp': metric.timestamp,
                        'value': metric.response_time_ms
                    })
                elif metric_type == "cpu_usage" and metric.cpu_usage_percent is not None:
                    trend_data.append({
                        'timestamp': metric.timestamp,
                        'value': metric.cpu_usage_percent
                    })
                elif metric_type == "memory_usage" and metric.memory_usage_percent is not None:
                    trend_data.append({
                        'timestamp': metric.timestamp,
                        'value': metric.memory_usage_percent
                    })
            
            # Sort by timestamp
            trend_data.sort(key=lambda x: x['timestamp'])
            return trend_data
            
        except Exception as e:
            logger.error(f"❌ Failed to extract trend data: {e}")
            return []
    
    async def _analyze_trends(self, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trend data and provide insights."""
        try:
            if not trend_data:
                return {"error": "No trend data available"}
            
            values = [d['value'] for d in trend_data]
            
            # Calculate trend direction
            if len(values) >= 2:
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg * 1.1:
                    trend_direction = "increasing"
                elif second_avg < first_avg * 0.9:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "insufficient_data"
            
            return {
                "trend_direction": trend_direction,
                "data_points": len(trend_data),
                "min_value": min(values) if values else 0,
                "max_value": max(values) if values else 0,
                "average_value": sum(values) / len(values) if values else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze trends: {e}")
            return {"error": str(e)}
    
    async def _analyze_health_trend(self, health_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze health score trends specifically."""
        try:
            if not health_data:
                return {"error": "No health data available"}
            
            values = [d['health_score'] for d in health_data]
            
            # Calculate trend analysis
            if len(values) >= 2:
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg:
                    trend_direction = "improving"
                elif second_avg < first_avg:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "insufficient_data"
            
            return {
                "trend_direction": trend_direction,
                "data_points": len(health_data),
                "min_health_score": min(values) if values else 0,
                "max_health_score": max(values) if values else 0,
                "average_health_score": sum(values) / len(values) if values else 0,
                "current_health_score": values[-1] if values else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze health trend: {e}")
            return {"error": str(e)}
    
    async def _get_oldest_metric(self) -> Optional[KGGraphMetrics]:
        """Get the oldest metric entry."""
        try:
            # This would need to be implemented in the repository
            # For now, return None
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get oldest metric: {e}")
            return None
    
    async def _get_newest_metric(self) -> Optional[KGGraphMetrics]:
        """Get the newest metric entry."""
        try:
            # This would need to be implemented in the repository
            # For now, return None
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get newest metric: {e}")
            return None
