"""
Certificate Metrics Service
Business logic for certificate metrics and analytics operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func

from ..models.certificates_metrics import (
    CertificateMetrics,
    PerformanceTrend,
    MetricCategory,
    MetricPriority,
    RealTimeAnalytics,
    BusinessMetrics,
    EnterpriseMetrics
)
from ..repositories.certificates_metrics_repository import CertificatesMetricsRepository
from ..models.certificates_registry import CertificateRegistry

logger = logging.getLogger(__name__)


class CertificatesMetricsService:
    """
    Business logic service for certificate metrics and analytics
    Coordinates metrics operations using models and repositories
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repository = CertificatesMetricsRepository(db_session)
    
    async def create_metrics(
        self,
        certificate_id: str,
        metric_category: MetricCategory,
        metric_name: str,
        metric_value: float,
        metric_unit: str,
        priority: MetricPriority = MetricPriority.MEDIUM,
        **kwargs
    ) -> CertificateMetrics:
        """
        Create new metrics entry
        """
        try:
            # Generate metrics ID
            metrics_id = str(uuid4())
            
            # Create metrics data
            metrics_data = {
                "metrics_id": metrics_id,
                "certificate_id": certificate_id,
                "metric_category": metric_category,
                "metric_name": metric_name,
                "metric_value": metric_value,
                "metric_unit": metric_unit,
                "priority": priority,
                "recorded_at": datetime.utcnow(),
                **kwargs
            }
            
            # Create metrics instance
            metrics = CertificateMetrics(**metrics_data)
            
            # Save to database
            created_metrics = await self.repository.create(metrics)
            
            logger.info(f"Created metrics {metric_name} for certificate {certificate_id}")
            return created_metrics
            
        except Exception as e:
            logger.error(f"Error creating metrics: {e}")
            raise
    
    async def get_metrics(self, metrics_id: str) -> Optional[CertificateMetrics]:
        """
        Retrieve specific metrics by ID
        """
        try:
            return await self.repository.get_by_id(metrics_id)
        except Exception as e:
            logger.error(f"Error retrieving metrics {metrics_id}: {e}")
            raise
    
    async def get_certificate_metrics(
        self,
        certificate_id: str,
        category: Optional[MetricCategory] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CertificateMetrics]:
        """
        Get metrics for a specific certificate
        """
        try:
            return await self.repository.get_by_certificate_id(
                certificate_id, category, limit, offset
            )
        except Exception as e:
            logger.error(f"Error retrieving metrics for certificate {certificate_id}: {e}")
            raise
    
    async def update_metrics(
        self,
        metrics_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[CertificateMetrics]:
        """
        Update existing metrics
        """
        try:
            # Add timestamp for update
            update_data["updated_at"] = datetime.utcnow()
            
            updated_metrics = await self.repository.update(metrics_id, update_data)
            
            if updated_metrics:
                logger.info(f"Updated metrics {metrics_id}")
            
            return updated_metrics
            
        except Exception as e:
            logger.error(f"Error updating metrics {metrics_id}: {e}")
            raise
    
    async def delete_metrics(self, metrics_id: str) -> bool:
        """
        Delete metrics entry
        """
        try:
            success = await self.repository.delete(metrics_id)
            
            if success:
                logger.info(f"Deleted metrics {metrics_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting metrics {metrics_id}: {e}")
            raise
    
    async def record_performance_metrics(
        self,
        certificate_id: str,
        performance_data: Dict[str, float],
        user_id: str
    ) -> List[CertificateMetrics]:
        """
        Record multiple performance metrics for a certificate
        """
        try:
            created_metrics = []
            
            for metric_name, metric_value in performance_data.items():
                metrics = await self.create_metrics(
                    certificate_id=certificate_id,
                    metric_category=MetricCategory.PERFORMANCE,
                    metric_name=metric_name,
                    metric_value=metric_value,
                    metric_unit="percentage",
                    priority=MetricPriority.HIGH,
                    recorded_by=user_id
                )
                created_metrics.append(metrics)
            
            logger.info(f"Recorded {len(created_metrics)} performance metrics for certificate {certificate_id}")
            return created_metrics
            
        except Exception as e:
            logger.error(f"Error recording performance metrics: {e}")
            raise
    
    async def record_usage_metrics(
        self,
        certificate_id: str,
        usage_data: Dict[str, int],
        user_id: str
    ) -> List[CertificateMetrics]:
        """
        Record usage metrics for a certificate
        """
        try:
            created_metrics = []
            
            for metric_name, metric_value in usage_data.items():
                metrics = await self.create_metrics(
                    certificate_id=certificate_id,
                    metric_category=MetricCategory.USAGE,
                    metric_name=metric_name,
                    metric_value=float(metric_value),
                    metric_unit="count",
                    priority=MetricPriority.MEDIUM,
                    recorded_by=user_id
                )
                created_metrics.append(metrics)
            
            logger.info(f"Recorded {len(created_metrics)} usage metrics for certificate {certificate_id}")
            return created_metrics
            
        except Exception as e:
            logger.error(f"Error recording usage metrics: {e}")
            raise
    
    async def record_quality_metrics(
        self,
        certificate_id: str,
        quality_data: Dict[str, float],
        user_id: str
    ) -> List[CertificateMetrics]:
        """
        Record quality assessment metrics
        """
        try:
            created_metrics = []
            
            for metric_name, metric_value in quality_data.items():
                metrics = await self.create_metrics(
                    certificate_id=certificate_id,
                    metric_category=MetricCategory.QUALITY,
                    metric_name=metric_name,
                    metric_value=metric_value,
                    metric_unit="score",
                    priority=MetricPriority.HIGH,
                    recorded_by=user_id
                )
                created_metrics.append(metrics)
            
            logger.info(f"Recorded {len(created_metrics)} quality metrics for certificate {certificate_id}")
            return created_metrics
            
        except Exception as e:
            logger.error(f"Error recording quality metrics: {e}")
            raise
    
    async def get_performance_trends(
        self,
        certificate_id: str,
        metric_name: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance trends for a specific metric over time
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            metrics = await self.repository.get_metrics_by_date_range(
                certificate_id, metric_name, start_date, end_date
            )
            
            if not metrics:
                return {
                    "trend": PerformanceTrend.STABLE,
                    "data_points": 0,
                    "average_value": 0,
                    "trend_direction": "no_data"
                }
            
            # Sort by date
            sorted_metrics = sorted(metrics, key=lambda m: m.recorded_at or datetime.min)
            
            # Calculate trend
            values = [m.metric_value for m in sorted_metrics]
            if len(values) >= 2:
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg * 1.1:
                    trend = PerformanceTrend.IMPROVING
                    direction = "increasing"
                elif second_avg < first_avg * 0.9:
                    trend = PerformanceTrend.DECLINING
                    direction = "decreasing"
                else:
                    trend = PerformanceTrend.STABLE
                    direction = "stable"
            else:
                trend = PerformanceTrend.STABLE
                direction = "insufficient_data"
            
            return {
                "trend": trend,
                "data_points": len(metrics),
                "average_value": sum(values) / len(values),
                "trend_direction": direction,
                "values": values,
                "dates": [m.recorded_at.isoformat() if m.recorded_at else None for m in sorted_metrics]
            }
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            raise
    
    async def calculate_certificate_score(
        self,
        certificate_id: str,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall certificate score based on various metrics
        """
        try:
            # Default weights if not provided
            if weights is None:
                weights = {
                    "quality": 0.4,
                    "performance": 0.3,
                    "usage": 0.2,
                    "compliance": 0.1
                }
            
            # Get metrics by category
            quality_metrics = await self.repository.get_by_certificate_id(
                certificate_id, MetricCategory.QUALITY, limit=1000
            )
            performance_metrics = await self.repository.get_by_certificate_id(
                certificate_id, MetricCategory.PERFORMANCE, limit=1000
            )
            usage_metrics = await self.repository.get_by_certificate_id(
                certificate_id, MetricCategory.USAGE, limit=1000
            )
            
            # Calculate category scores
            scores = {}
            
            if quality_metrics:
                scores["quality"] = sum(m.metric_value for m in quality_metrics) / len(quality_metrics)
            else:
                scores["quality"] = 0
            
            if performance_metrics:
                scores["performance"] = sum(m.metric_value for m in performance_metrics) / len(performance_metrics)
            else:
                scores["performance"] = 0
            
            if usage_metrics:
                # Normalize usage metrics (assuming higher usage is better)
                max_usage = max(m.metric_value for m in usage_metrics) if usage_metrics else 1
                scores["usage"] = sum(m.metric_value / max_usage for m in usage_metrics) / len(usage_metrics) * 100
            else:
                scores["usage"] = 0
            
            # Calculate weighted overall score
            overall_score = sum(
                scores.get(category, 0) * weight
                for category, weight in weights.items()
            )
            
            return {
                "certificate_id": certificate_id,
                "overall_score": round(overall_score, 2),
                "category_scores": scores,
                "weights": weights,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating certificate score: {e}")
            raise
    
    async def get_metrics_analytics(
        self,
        org_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive metrics analytics
        """
        try:
            analytics = await self.repository.get_metrics_analytics(
                org_id, start_date, end_date
            )
            
            # Add computed insights
            if analytics.get("total_metrics", 0) > 0:
                # Calculate averages by category
                for category in MetricCategory:
                    category_key = f"{category.value}_count"
                    category_value_key = f"{category.value}_avg_value"
                    
                    if analytics.get(category_key, 0) > 0:
                        analytics[category_value_key] = analytics.get(
                            f"{category.value}_total_value", 0
                        ) / analytics[category_key]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting metrics analytics: {e}")
            raise
    
    async def bulk_update_metrics(
        self,
        metrics_ids: List[str],
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Bulk update multiple metrics entries
        """
        try:
            results = {
                "successful": [],
                "failed": [],
                "total_processed": len(metrics_ids)
            }
            
            for metrics_id in metrics_ids:
                try:
                    success = await self.repository.update(metrics_id, update_data)
                    
                    if success:
                        results["successful"].append(metrics_id)
                    else:
                        results["failed"].append(metrics_id)
                        
                except Exception as e:
                    logger.error(f"Error updating metrics {metrics_id}: {e}")
                    results["failed"].append(metrics_id)
            
            logger.info(f"Bulk update completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            raise
    
    async def get_metrics_statistics(
        self,
        org_id: Optional[str] = None,
        category: Optional[MetricCategory] = None
    ) -> Dict[str, Any]:
        """
        Get metrics statistics and summaries
        """
        try:
            return await self.repository.get_metrics_statistics(org_id, category)
        except Exception as e:
            logger.error(f"Error getting metrics statistics: {e}")
            raise
    
    async def validate_metrics_integrity(self, metrics_id: str) -> bool:
        """
        Validate metrics data integrity
        """
        try:
            metrics = await self.repository.get_by_id(metrics_id)
            if not metrics:
                return False
            
            # Validate required fields
            required_fields = [
                metrics.metrics_id,
                metrics.certificate_id,
                metrics.metric_category,
                metrics.metric_name,
                metrics.metric_value,
                metrics.metric_unit
            ]
            
            if not all(required_fields):
                return False
            
            # Validate metric value (should be numeric)
            if not isinstance(metrics.metric_value, (int, float)):
                return False
            
            # Validate metric name
            if not metrics.metric_name or len(metrics.metric_name.strip()) == 0:
                return False
            
            # Validate metric unit
            if not metrics.metric_unit or len(metrics.metric_unit.strip()) == 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating metrics integrity: {e}")
            return False
    
    async def get_metrics_health_status(self, metrics_id: str) -> Dict[str, Any]:
        """
        Get metrics health and status information
        """
        try:
            metrics = await self.repository.get_by_id(metrics_id)
            if not metrics:
                return {"status": "not_found", "health": "unknown"}
            
            health_indicators = {
                "data_completeness": 0,
                "value_validity": "unknown",
                "age_hours": 0,
                "issues": []
            }
            
            # Check data completeness
            required_fields = [
                "metric_category", "metric_name", "metric_value",
                "metric_unit", "priority"
            ]
            
            complete_fields = sum(
                1 for field in required_fields 
                if getattr(metrics, field) is not None
            )
            health_indicators["data_completeness"] = (complete_fields / len(required_fields)) * 100
            
            # Check value validity
            if isinstance(metrics.metric_value, (int, float)):
                if metrics.metric_value >= 0:
                    health_indicators["value_validity"] = "valid"
                else:
                    health_indicators["value_validity"] = "negative_value"
                    health_indicators["issues"].append("negative_value")
            else:
                health_indicators["value_validity"] = "invalid_type"
                health_indicators["issues"].append("invalid_value_type")
            
            # Calculate age
            if metrics.recorded_at:
                age = datetime.utcnow() - metrics.recorded_at
                health_indicators["age_hours"] = age.total_seconds() / 3600
            
            # Identify issues
            if health_indicators["data_completeness"] < 100:
                health_indicators["issues"].append("incomplete_data")
            
            if health_indicators["age_hours"] > 24:
                health_indicators["issues"].append("stale_data")
            
            # Determine overall health
            if health_indicators["data_completeness"] == 100 and health_indicators["value_validity"] == "valid" and not health_indicators["issues"]:
                health_indicators["health"] = "healthy"
            elif health_indicators["data_completeness"] >= 80 and len(health_indicators["issues"]) <= 1:
                health_indicators["health"] = "warning"
            else:
                health_indicators["health"] = "critical"
            
            return health_indicators
            
        except Exception as e:
            logger.error(f"Error getting metrics health status: {e}")
            return {"status": "error", "health": "unknown", "error": str(e)}
    
    async def export_metrics_data(
        self,
        metrics_ids: List[str],
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export metrics data in specified format
        """
        try:
            metrics_list = []
            for metrics_id in metrics_ids:
                metrics = await self.repository.get_by_id(metrics_id)
                if metrics:
                    metrics_list.append(metrics.model_dump())
            
            export_data = {
                "export_info": {
                    "format": format,
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_metrics": len(metrics_list)
                },
                "metrics": metrics_list
            }
            
            logger.info(f"Exported {len(metrics_list)} metrics in {format} format")
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting metrics data: {e}")
            raise
    
    async def cleanup_old_metrics(
        self,
        certificate_id: str,
        keep_days: int = 90
    ) -> Dict[str, Any]:
        """
        Clean up old metrics data, keeping only recent entries
        """
        try:
            # Get all metrics for the certificate
            all_metrics = await self.repository.get_by_certificate_id(
                certificate_id, limit=10000, offset=0
            )
            
            if not all_metrics:
                return {
                    "message": "No metrics to clean up",
                    "total_metrics": 0,
                    "metrics_kept": 0,
                    "metrics_removed": 0
                }
            
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=keep_days)
            
            # Filter metrics to keep and remove
            metrics_to_keep = [
                m for m in all_metrics
                if m.recorded_at and m.recorded_at >= cutoff_date
            ]
            metrics_to_remove = [
                m for m in all_metrics
                if m.recorded_at and m.recorded_at < cutoff_date
            ]
            
            # Remove old metrics
            removed_count = 0
            for metrics in metrics_to_remove:
                try:
                    success = await self.repository.delete(metrics.metrics_id)
                    if success:
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove metrics {metrics.metrics_id}: {e}")
            
            return {
                "message": "Cleanup completed",
                "total_metrics": len(all_metrics),
                "metrics_kept": len(metrics_to_keep),
                "metrics_removed": removed_count,
                "cleanup_criteria": {
                    "keep_days": keep_days,
                    "cutoff_date": cutoff_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error during metrics cleanup: {e}")
            raise
    
    async def get_real_time_analytics(
        self,
        certificate_id: str,
        time_window_minutes: int = 60
    ) -> RealTimeAnalytics:
        """
        Get real-time analytics for a certificate
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=time_window_minutes)
            
            # Get recent metrics
            recent_metrics = await self.repository.get_metrics_by_date_range(
                certificate_id, None, start_time, end_time
            )
            
            # Calculate real-time statistics
            if recent_metrics:
                values = [m.metric_value for m in recent_metrics]
                avg_value = sum(values) / len(values)
                min_value = min(values)
                max_value = max(values)
                
                # Calculate trend (simple linear regression)
                if len(values) >= 2:
                    x_values = [(m.recorded_at - start_time).total_seconds() / 60 for m in recent_metrics]
                    y_values = values
                    
                    # Simple linear regression
                    n = len(x_values)
                    sum_x = sum(x_values)
                    sum_y = sum(y_values)
                    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
                    sum_x2 = sum(x * x for x in x_values)
                    
                    if n * sum_x2 - sum_x * sum_x != 0:
                        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                        trend = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
                    else:
                        trend = "stable"
                else:
                    trend = "insufficient_data"
            else:
                avg_value = min_value = max_value = 0
                trend = "no_data"
            
            return RealTimeAnalytics(
                certificate_id=certificate_id,
                time_window_minutes=time_window_minutes,
                data_points=len(recent_metrics),
                average_value=avg_value,
                min_value=min_value,
                max_value=max_value,
                trend=trend,
                last_updated=end_time
            )
            
        except Exception as e:
            logger.error(f"Error getting real-time analytics: {e}")
            raise
