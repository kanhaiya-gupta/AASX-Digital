"""
AI RAG Metrics Service
======================

Business logic layer for AI RAG metrics operations.
Handles performance monitoring, health scoring, and analytics.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from src.modules.ai_rag.models.ai_rag_metrics import AIRagMetrics
from src.modules.ai_rag.repositories.ai_rag_metrics_repository import AIRagMetricsRepository
from src.modules.ai_rag.repositories.ai_rag_registry_repository import AIRagRegistryRepository

logger = logging.getLogger(__name__)


class AIRagMetricsService:
    """
    AI RAG Metrics Service - Pure Async Implementation
    
    Orchestrates AI RAG metrics operations including:
    - Performance monitoring and alerting
    - Health score calculation and trending
    - Anomaly detection
    - Performance optimization recommendations
    """
    
    def __init__(self, metrics_repo: AIRagMetricsRepository,
                 registry_repo: AIRagRegistryRepository):
        """Initialize service with required repositories"""
        self.metrics_repo = metrics_repo
        self.registry_repo = registry_repo
    
    async def create_metrics(self, metrics_data: Dict[str, Any]) -> Optional[AIRagMetrics]:
        """Create new AI RAG metrics with validation"""
        try:
            logger.info(f"Creating metrics for registry: {metrics_data.get('registry_id', 'Unknown')}")
            
            # Create metrics instance
            metrics = AIRagMetrics(**metrics_data)
            
            # Validate metrics before creation
            if not await self._validate_metrics(metrics):
                logger.error("Metrics validation failed")
                return None
            
            # Create in database
            success = await self.metrics_repo.create(metrics)
            if not success:
                logger.error("Failed to create metrics in database")
                return None
            
            # Update registry health score
            await self._update_registry_health(metrics.registry_id)
            
            logger.info(f"Successfully created metrics: {metrics.metric_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error creating metrics: {e}")
            return None
    
    async def get_metrics_by_id(self, metric_id: int) -> Optional[AIRagMetrics]:
        """Get AI RAG metrics by ID"""
        try:
            return await self.metrics_repo.get_by_id(metric_id)
        except Exception as e:
            logger.error(f"Error getting metrics by ID: {e}")
            return None
    
    async def get_metrics_by_registry(self, registry_id: str, limit: int = 100) -> List[AIRagMetrics]:
        """Get AI RAG metrics by registry ID with sorting"""
        try:
            metrics = await self.metrics_repo.get_by_registry_id(registry_id)
            return metrics[:limit]
        except Exception as e:
            logger.error(f"Error getting metrics by registry: {e}")
            return []
    
    async def get_latest_metrics(self, registry_id: str) -> Optional[AIRagMetrics]:
        """Get latest metrics for a registry"""
        try:
            return await self.metrics_repo.get_latest_by_registry_id(registry_id)
        except Exception as e:
            logger.error(f"Error getting latest metrics: {e}")
            return None
    
    async def update_metrics(self, metric_id: int, update_data: Dict[str, Any]) -> bool:
        """Update existing AI RAG metrics"""
        try:
            logger.info(f"Updating metrics: {metric_id}")
            
            # Get existing metrics
            metrics = await self.metrics_repo.get_by_id(metric_id)
            if not metrics:
                logger.error(f"Metrics not found: {metric_id}")
                return False
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(metrics, key):
                    setattr(metrics, key, value)
            
            # Validate updated metrics
            if not await self._validate_metrics(metrics):
                logger.error("Updated metrics validation failed")
                return False
            
            # Update timestamp
            metrics.update_timestamp()
            
            # Save to database
            success = await self.metrics_repo.update(metrics)
            if success:
                logger.info(f"Successfully updated metrics: {metric_id}")
                
                # Update registry health score
                await self._update_registry_health(metrics.registry_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            return False
    
    async def delete_metrics(self, metric_id: int) -> bool:
        """Delete AI RAG metrics"""
        try:
            logger.info(f"Deleting metrics: {metric_id}")
            
            # Get metrics to find registry_id before deletion
            metrics = await self.metrics_repo.get_by_id(metric_id)
            registry_id = metrics.registry_id if metrics else None
            
            # Delete from database
            success = await self.metrics_repo.delete(metric_id)
            if success:
                logger.info(f"Successfully deleted metrics: {metric_id}")
                
                # Update registry health score if registry exists
                if registry_id:
                    await self._update_registry_health(registry_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting metrics: {e}")
            return False
    
    async def get_health_metrics(self, registry_id: str, limit: int = 100) -> List[AIRagMetrics]:
        """Get health-focused metrics for a registry"""
        try:
            return await self.metrics_repo.get_health_metrics(registry_id, limit)
        except Exception as e:
            logger.error(f"Error getting health metrics: {e}")
            return []
    
    async def get_performance_metrics(self, registry_id: str, limit: int = 100) -> List[AIRagMetrics]:
        """Get performance-focused metrics for a registry"""
        try:
            return await self.metrics_repo.get_performance_metrics(registry_id, limit)
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return []
    
    async def calculate_health_trends(self, registry_id: str, days: int = 30) -> Dict[str, Any]:
        """Calculate health trends over specified period"""
        try:
            logger.info(f"Calculating health trends for registry: {registry_id}")
            
            # Get metrics for the period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            metrics = await self.metrics_repo.get_by_registry_id(registry_id)
            
            # Filter by date range
            period_metrics = []
            for metric in metrics:
                try:
                    metric_date = datetime.fromisoformat(metric.timestamp.replace('Z', '+00:00'))
                    if start_date <= metric_date <= end_date:
                        period_metrics.append(metric)
                except:
                    continue
            
            if not period_metrics:
                return {"error": "No metrics found for the specified period"}
            
            # Calculate trends
            trends = {
                "period_days": days,
                "total_metrics": len(period_metrics),
                "health_score": {
                    "current": period_metrics[0].health_score if period_metrics else 0,
                    "average": sum(m.health_score or 0 for m in period_metrics) / len(period_metrics),
                    "trend": self._calculate_trend([m.health_score or 0 for m in period_metrics])
                },
                "response_time": {
                    "current": period_metrics[0].response_time_ms if period_metrics else 0,
                    "average": sum(m.response_time_ms or 0 for m in period_metrics) / len(period_metrics),
                    "trend": self._calculate_trend([m.response_time_ms or 0 for m in period_metrics])
                },
                "error_rate": {
                    "current": period_metrics[0].error_rate if period_metrics else 0,
                    "average": sum(m.error_rate or 0 for m in period_metrics) / len(period_metrics),
                    "trend": self._calculate_trend([m.error_rate or 0 for m in period_metrics])
                },
                "uptime": {
                    "current": period_metrics[0].uptime_percentage if period_metrics else 0,
                    "average": sum(m.uptime_percentage or 0 for m in period_metrics) / len(period_metrics),
                    "trend": self._calculate_trend([m.uptime_percentage or 0 for m in period_metrics])
                }
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating health trends: {e}")
            return {"error": str(e)}
    
    async def detect_anomalies(self, registry_id: str, sensitivity: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics data"""
        try:
            logger.info(f"Detecting anomalies for registry: {registry_id}")
            
            # Get recent metrics
            metrics = await self.metrics_repo.get_by_registry_id(registry_id)
            if len(metrics) < 10:  # Need minimum data points
                return []
            
            # Calculate baseline statistics
            health_scores = [m.health_score or 0 for m in metrics[:20]]
            response_times = [m.response_time_ms or 0 for m in metrics[:20]]
            error_rates = [m.error_rate or 0 for m in metrics[:20]]
            
            anomalies = []
            
            # Check for health score anomalies
            if health_scores:
                baseline_health = sum(health_scores) / len(health_scores)
                health_std = self._calculate_std(health_scores)
                
                for metric in metrics[:10]:  # Check recent metrics
                    if metric.health_score is not None:
                        z_score = abs((metric.health_score - baseline_health) / health_std) if health_std > 0 else 0
                        if z_score > sensitivity:
                            anomalies.append({
                                "metric_id": metric.metric_id,
                                "timestamp": metric.timestamp,
                                "type": "health_score_anomaly",
                                "value": metric.health_score,
                                "baseline": baseline_health,
                                "z_score": z_score,
                                "severity": "high" if z_score > 3 else "medium"
                            })
            
            # Check for response time anomalies
            if response_times:
                baseline_response = sum(response_times) / len(response_times)
                response_std = self._calculate_std(response_times)
                
                for metric in metrics[:10]:
                    if metric.response_time_ms is not None:
                        z_score = abs((metric.response_time_ms - baseline_response) / response_std) if response_std > 0 else 0
                        if z_score > sensitivity:
                            anomalies.append({
                                "metric_id": metric.metric_id,
                                "timestamp": metric.timestamp,
                                "type": "response_time_anomaly",
                                "value": metric.response_time_ms,
                                "baseline": baseline_response,
                                "z_score": z_score,
                                "severity": "high" if z_score > 3 else "medium"
                            })
            
            # Check for error rate anomalies
            if error_rates:
                baseline_error = sum(error_rates) / len(error_rates)
                error_std = self._calculate_std(error_rates)
                
                for metric in metrics[:10]:
                    if metric.error_rate is not None:
                        z_score = abs((metric.error_rate - baseline_error) / error_std) if error_std > 0 else 0
                        if z_score > sensitivity:
                            anomalies.append({
                                "metric_id": metric.metric_id,
                                "timestamp": metric.timestamp,
                                "type": "error_rate_anomaly",
                                "value": metric.error_rate,
                                "baseline": baseline_error,
                                "z_score": z_score,
                                "severity": "high" if z_score > 3 else "medium"
                            })
            
            logger.info(f"Detected {len(anomalies)} anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    async def get_performance_recommendations(self, registry_id: str) -> List[Dict[str, Any]]:
        """Get performance optimization recommendations"""
        try:
            logger.info(f"Generating performance recommendations for registry: {registry_id}")
            
            # Get latest metrics
            latest_metrics = await self.metrics_repo.get_latest_by_registry_id(registry_id)
            if not latest_metrics:
                return []
            
            recommendations = []
            
            # Health score recommendations
            if latest_metrics.health_score is not None:
                if latest_metrics.health_score < 70:
                    recommendations.append({
                        "type": "health_score",
                        "priority": "high",
                        "message": "Health score is critically low. Immediate attention required.",
                        "action": "Review system configuration and check for errors"
                    })
                elif latest_metrics.health_score < 85:
                    recommendations.append({
                        "type": "health_score",
                        "priority": "medium",
                        "message": "Health score could be improved.",
                        "action": "Monitor performance and optimize configuration"
                    })
            
            # Response time recommendations
            if latest_metrics.response_time_ms is not None:
                if latest_metrics.response_time_ms > 1000:
                    recommendations.append({
                        "type": "response_time",
                        "priority": "high",
                        "message": "Response time is very high. Performance degradation detected.",
                        "action": "Check system resources and optimize queries"
                    })
                elif latest_metrics.response_time_ms > 500:
                    recommendations.append({
                        "type": "response_time",
                        "priority": "medium",
                        "message": "Response time could be improved.",
                        "action": "Consider caching and query optimization"
                    })
            
            # Error rate recommendations
            if latest_metrics.error_rate is not None:
                if latest_metrics.error_rate > 0.05:
                    recommendations.append({
                        "type": "error_rate",
                        "priority": "high",
                        "message": "Error rate is high. System reliability issues detected.",
                        "action": "Investigate error logs and fix underlying issues"
                    })
                elif latest_metrics.error_rate > 0.02:
                    recommendations.append({
                        "type": "error_rate",
                        "priority": "medium",
                        "message": "Error rate could be improved.",
                        "action": "Review error patterns and implement fixes"
                    })
            
            # Uptime recommendations
            if latest_metrics.uptime_percentage is not None:
                if latest_metrics.uptime_percentage < 95:
                    recommendations.append({
                        "type": "uptime",
                        "priority": "high",
                        "message": "Uptime is below acceptable threshold.",
                        "action": "Investigate downtime causes and implement redundancy"
                    })
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def get_metrics_summary(self, org_id: str) -> Dict[str, Any]:
        """Get comprehensive metrics summary for organization"""
        try:
            logger.info(f"Generating metrics summary for org: {org_id}")
            
            # Get all registries for organization
            registries = await self.registry_repo.get_by_org_id(org_id)
            
            summary = {
                "total_registries": len(registries),
                "total_metrics": 0,
                "average_health_score": 0.0,
                "average_response_time": 0.0,
                "average_error_rate": 0.0,
                "average_uptime": 0.0,
                "health_distribution": {
                    "excellent": 0,
                    "good": 0,
                    "fair": 0,
                    "poor": 0,
                    "critical": 0
                },
                "performance_alerts": 0
            }
            
            total_health = 0
            total_response_time = 0
            total_error_rate = 0
            total_uptime = 0
            registry_count = 0
            
            for registry in registries:
                try:
                    # Get latest metrics for each registry
                    latest_metrics = await self.metrics_repo.get_latest_by_registry_id(registry.registry_id)
                    if latest_metrics:
                        summary["total_metrics"] += 1
                        
                        # Accumulate values for averages
                        if latest_metrics.health_score is not None:
                            total_health += latest_metrics.health_score
                            registry_count += 1
                            
                            # Categorize health scores
                            if latest_metrics.health_score >= 90:
                                summary["health_distribution"]["excellent"] += 1
                            elif latest_metrics.health_score >= 80:
                                summary["health_distribution"]["good"] += 1
                            elif latest_metrics.health_score >= 70:
                                summary["health_distribution"]["fair"] += 1
                            elif latest_metrics.health_score >= 60:
                                summary["health_distribution"]["poor"] += 1
                            else:
                                summary["health_distribution"]["critical"] += 1
                        
                        if latest_metrics.response_time_ms is not None:
                            total_response_time += latest_metrics.response_time_ms
                        
                        if latest_metrics.error_rate is not None:
                            total_error_rate += latest_metrics.error_rate
                        
                        if latest_metrics.uptime_percentage is not None:
                            total_uptime += latest_metrics.uptime_percentage
                        
                        # Count performance alerts
                        if (latest_metrics.health_score is not None and latest_metrics.health_score < 70) or \
                           (latest_metrics.response_time_ms is not None and latest_metrics.response_time_ms > 1000) or \
                           (latest_metrics.error_rate is not None and latest_metrics.error_rate > 0.05):
                            summary["performance_alerts"] += 1
                            
                except Exception as e:
                    logger.warning(f"Error processing metrics for registry {registry.registry_id}: {e}")
                    continue
            
            # Calculate averages
            if registry_count > 0:
                summary["average_health_score"] = total_health / registry_count
                summary["average_response_time"] = total_response_time / registry_count
                summary["average_error_rate"] = total_error_rate / registry_count
                summary["average_uptime"] = total_uptime / registry_count
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating metrics summary: {e}")
            return {}
    
    # Private helper methods
    
    async def _validate_metrics(self, metrics: AIRagMetrics) -> bool:
        """Validate metrics before database operations"""
        try:
            # Check required fields
            if not metrics.registry_id:
                logger.error("Metrics missing registry_id")
                return False
            
            # Check value ranges
            if metrics.health_score is not None and (metrics.health_score < 0 or metrics.health_score > 100):
                logger.error("Health score out of valid range")
                return False
            
            if metrics.response_time_ms is not None and metrics.response_time_ms < 0:
                logger.error("Response time cannot be negative")
                return False
            
            if metrics.error_rate is not None and (metrics.error_rate < 0 or metrics.error_rate > 1):
                logger.error("Error rate out of valid range")
                return False
            
            if metrics.uptime_percentage is not None and (metrics.uptime_percentage < 0 or metrics.uptime_percentage > 100):
                logger.error("Uptime percentage out of valid range")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Metrics validation error: {e}")
            return False
    
    async def _update_registry_health(self, registry_id: str) -> None:
        """Update registry health score based on latest metrics"""
        try:
            # This would typically call the registry service
            # For now, we'll just log the action
            logger.debug(f"Registry health update triggered for: {registry_id}")
        except Exception as e:
            logger.warning(f"Error updating registry health: {e}")
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        try:
            if len(values) < 2:
                return "stable"
            
            # Simple linear regression slope
            n = len(values)
            x_sum = sum(range(n))
            y_sum = sum(values)
            xy_sum = sum(i * val for i, val in enumerate(values))
            x2_sum = sum(i * i for i in range(n))
            
            slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
            
            if slope > 0.01:
                return "improving"
            elif slope < -0.01:
                return "declining"
            else:
                return "stable"
                
        except Exception:
            return "stable"
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation of values"""
        try:
            if len(values) < 2:
                return 0.0
            
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
            return variance ** 0.5
            
        except Exception:
            return 0.0
