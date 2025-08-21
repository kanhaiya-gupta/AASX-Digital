"""
Data Quality Monitor Service

This service monitors data quality across all external modules,
providing quality metrics, alerts, and quality improvement
recommendations for the AAS Data Modeling Engine.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from .models import QualityMetric, QualityStatus


logger = logging.getLogger(__name__)


class DataQualityMonitorService:
    """
    Service for monitoring data quality across all modules.
    
    This service provides:
    - Data quality metrics collection and monitoring
    - Quality threshold management and alerts
    - Quality trend analysis and reporting
    - Quality improvement recommendations
    """
    
    def __init__(self):
        """Initialize the data quality monitor service."""
        self.quality_metrics: Dict[UUID, QualityMetric] = {}
        self.module_metrics: Dict[str, List[UUID]] = {}  # module_name -> metric_ids
        self.quality_thresholds: Dict[str, Dict[str, Any]] = {}  # metric_name -> thresholds
        self.quality_alerts: List[Dict[str, Any]] = []
        self.is_monitoring = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Initialize default quality thresholds
        self._initialize_default_thresholds()
    
    def _initialize_default_thresholds(self) -> None:
        """Initialize default quality thresholds for common metrics."""
        default_thresholds = {
            "completeness": {
                "excellent": 0.95,
                "good": 0.85,
                "acceptable": 0.70,
                "poor": 0.50,
                "critical": 0.30
            },
            "accuracy": {
                "excellent": 0.98,
                "good": 0.90,
                "acceptable": 0.80,
                "poor": 0.60,
                "critical": 0.40
            },
            "consistency": {
                "excellent": 0.95,
                "good": 0.85,
                "acceptable": 0.75,
                "poor": 0.55,
                "critical": 0.35
            },
            "timeliness": {
                "excellent": 0.90,
                "good": 0.80,
                "acceptable": 0.70,
                "poor": 0.50,
                "critical": 0.30
            },
            "validity": {
                "excellent": 0.95,
                "good": 0.85,
                "acceptable": 0.75,
                "poor": 0.55,
                "critical": 0.35
            }
        }
        
        for metric_name, thresholds in default_thresholds.items():
            self.quality_thresholds[metric_name] = thresholds
    
    async def start_quality_monitoring(self) -> None:
        """Start automatic quality monitoring."""
        if self.is_monitoring:
            logger.warning("Quality monitoring is already running")
            return
        
        self.is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._quality_monitoring_loop())
        logger.info("Started data quality monitoring")
    
    async def stop_quality_monitoring(self) -> None:
        """Stop automatic quality monitoring."""
        self.is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped data quality monitoring")
    
    async def _quality_monitoring_loop(self) -> None:
        """Background task for monitoring quality metrics."""
        while self.is_monitoring:
            try:
                await self._process_quality_checks()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in quality monitoring loop: {e}")
                await asyncio.sleep(10)  # Brief pause on error
    
    async def _process_quality_checks(self) -> None:
        """Process quality checks and generate alerts."""
        logger.debug("Processing quality checks...")
        
        # Check for metrics that need attention
        for metric in self.quality_metrics.values():
            if self._should_generate_alert(metric):
                await self._generate_quality_alert(metric)
    
    def record_quality_metric(
        self,
        metric_name: str,
        metric_value: float,
        module_name: str,
        data_id: str,
        metric_description: str = "",
        metric_unit: str = "percentage",
        threshold_min: Optional[float] = None,
        threshold_max: Optional[float] = None,
        target_value: Optional[float] = None
    ) -> QualityMetric:
        """
        Record a new quality metric.
        
        Args:
            metric_name: Name of the quality metric
            metric_value: Value of the metric
            module_name: Name of the module
            data_id: ID of the data being measured
            metric_description: Description of the metric
            metric_unit: Unit of measurement
            threshold_min: Minimum acceptable value
            threshold_max: Maximum acceptable value
            target_value: Target/optimal value
            
        Returns:
            Created QualityMetric instance
        """
        # Determine quality status based on thresholds
        quality_status = self._determine_quality_status(metric_name, metric_value)
        
        # Create quality metric
        metric = QualityMetric(
            metric_name=metric_name,
            metric_description=metric_description,
            metric_value=metric_value,
            metric_unit=metric_unit,
            threshold_min=threshold_min or self._get_threshold(metric_name, "poor"),
            threshold_max=threshold_max or self._get_threshold(metric_name, "excellent"),
            target_value=target_value or self._get_threshold(metric_name, "excellent"),
            quality_status=quality_status,
            module_name=module_name,
            data_id=data_id
        )
        
        # Store metric
        self.quality_metrics[metric.metric_id] = metric
        
        # Update module index
        if module_name not in self.module_metrics:
            self.module_metrics[module_name] = []
        self.module_metrics[module_name].append(metric.metric_id)
        
        logger.info(f"Recorded quality metric: {metric_name} = {metric_value} ({quality_status.value}) for {module_name}")
        return metric
    
    def _determine_quality_status(self, metric_name: str, metric_value: float) -> QualityStatus:
        """Determine quality status based on thresholds."""
        thresholds = self.quality_thresholds.get(metric_name, {})
        
        if not thresholds:
            return QualityStatus.UNKNOWN
        
        if metric_value >= thresholds.get("excellent", 0.95):
            return QualityStatus.EXCELLENT
        elif metric_value >= thresholds.get("good", 0.85):
            return QualityStatus.GOOD
        elif metric_value >= thresholds.get("acceptable", 0.70):
            return QualityStatus.ACCEPTABLE
        elif metric_value >= thresholds.get("poor", 0.50):
            return QualityStatus.POOR
        else:
            return QualityStatus.CRITICAL
    
    def _get_threshold(self, metric_name: str, level: str) -> float:
        """Get threshold value for a metric and level."""
        thresholds = self.quality_thresholds.get(metric_name, {})
        return thresholds.get(level, 0.0)
    
    def _should_generate_alert(self, metric: QualityMetric) -> bool:
        """Determine if an alert should be generated for a metric."""
        # Generate alerts for poor and critical quality
        return metric.quality_status in [QualityStatus.POOR, QualityStatus.CRITICAL]
    
    async def _generate_quality_alert(self, metric: QualityMetric) -> None:
        """Generate a quality alert for a metric."""
        alert = {
            "alert_id": str(UUID.uuid4()),
            "metric_id": str(metric.metric_id),
            "metric_name": metric.metric_name,
            "module_name": metric.module_name,
            "data_id": metric.data_id,
            "quality_status": metric.quality_status.value,
            "metric_value": metric.metric_value,
            "threshold": metric.threshold_min,
            "alert_message": f"Quality alert: {metric.metric_name} = {metric.metric_value} ({metric.quality_status.value}) for {metric.module_name}",
            "generated_at": datetime.utcnow().isoformat(),
            "severity": "high" if metric.quality_status == QualityStatus.CRITICAL else "medium"
        }
        
        self.quality_alerts.append(alert)
        logger.warning(f"Quality alert generated: {alert['alert_message']}")
    
    def get_quality_metrics_by_module(self, module_name: str, limit: Optional[int] = None) -> List[QualityMetric]:
        """Get quality metrics for a specific module."""
        if module_name not in self.module_metrics:
            return []
        
        metric_ids = self.module_metrics[module_name]
        metrics = [self.quality_metrics[metric_id] for metric_id in metric_ids if metric_id in self.quality_metrics]
        
        # Sort by measurement time (newest first)
        metrics.sort(key=lambda m: m.measured_at, reverse=True)
        
        if limit:
            metrics = metrics[:limit]
        
        return metrics
    
    def get_quality_metrics_by_name(self, metric_name: str, limit: Optional[int] = None) -> List[QualityMetric]:
        """Get all metrics with a specific name."""
        metrics = [metric for metric in self.quality_metrics.values() if metric.metric_name == metric_name]
        
        # Sort by measurement time (newest first)
        metrics.sort(key=lambda m: m.measured_at, reverse=True)
        
        if limit:
            metrics = metrics[:limit]
        
        return metrics
    
    def get_quality_trend(
        self,
        metric_name: str,
        module_name: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get quality trend for a specific metric and module.
        
        Args:
            metric_name: Name of the metric
            module_name: Name of the module
            days: Number of days to look back
            
        Returns:
            List of trend data points
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        metrics = self.get_quality_metrics_by_module(module_name)
        metrics = [m for m in metrics if m.metric_name == metric_name and m.measured_at >= cutoff_date]
        
        # Sort by measurement time
        metrics.sort(key=lambda m: m.measured_at)
        
        trend_data = []
        for metric in metrics:
            trend_data.append({
                "timestamp": metric.measured_at.isoformat(),
                "value": metric.metric_value,
                "status": metric.quality_status.value,
                "threshold_min": metric.threshold_min,
                "threshold_max": metric.threshold_max
            })
        
        return trend_data
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get summary of all quality metrics."""
        total_metrics = len(self.quality_metrics)
        total_modules = len(self.module_metrics)
        total_alerts = len(self.quality_alerts)
        
        # Count by quality status
        status_counts = {}
        for metric in self.quality_metrics.values():
            status = metric.quality_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by metric name
        metric_name_counts = {}
        for metric in self.quality_metrics.values():
            name = metric.metric_name
            metric_name_counts[name] = metric_name_counts.get(name, 0) + 1
        
        # Calculate average quality scores by module
        module_averages = {}
        for module_name, metric_ids in self.module_metrics.items():
            if not metric_ids:
                continue
            
            module_metrics = [self.quality_metrics[metric_id] for metric_id in metric_ids if metric_id in self.quality_metrics]
            if module_metrics:
                avg_score = sum(m.metric_value for m in module_metrics) / len(module_metrics)
                module_averages[module_name] = round(avg_score, 2)
        
        return {
            "total_metrics": total_metrics,
            "modules_monitored": total_modules,
            "total_alerts": total_alerts,
            "quality_status_distribution": status_counts,
            "metric_distribution": metric_name_counts,
            "module_averages": module_averages,
            "is_monitoring": self.is_monitoring
        }
    
    def set_quality_thresholds(
        self,
        metric_name: str,
        thresholds: Dict[str, float]
    ) -> bool:
        """
        Set quality thresholds for a specific metric.
        
        Args:
            metric_name: Name of the metric
            thresholds: Dictionary of threshold levels and values
            
        Returns:
            True if set successfully, False otherwise
        """
        required_levels = ["excellent", "good", "acceptable", "poor", "critical"]
        
        # Validate thresholds
        for level in required_levels:
            if level not in thresholds:
                logger.error(f"Missing required threshold level: {level}")
                return False
        
        # Ensure thresholds are in descending order
        if not (thresholds["excellent"] >= thresholds["good"] >= thresholds["acceptable"] >= thresholds["poor"] >= thresholds["critical"]):
            logger.error("Thresholds must be in descending order")
            return False
        
        self.quality_thresholds[metric_name] = thresholds
        logger.info(f"Set quality thresholds for {metric_name}: {thresholds}")
        return True
    
    def get_quality_recommendations(self, module_name: str) -> List[Dict[str, Any]]:
        """
        Get quality improvement recommendations for a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            List of improvement recommendations
        """
        recommendations = []
        
        if module_name not in self.module_metrics:
            return recommendations
        
        # Get recent metrics for the module
        recent_metrics = self.get_quality_metrics_by_module(module_name, limit=100)
        
        # Group by metric name and analyze trends
        metric_groups = {}
        for metric in recent_metrics:
            if metric.metric_name not in metric_groups:
                metric_groups[metric.metric_name] = []
            metric_groups[metric.metric_name].append(metric)
        
        for metric_name, metrics in metric_groups.items():
            if len(metrics) < 2:
                continue
            
            # Sort by time
            metrics.sort(key=lambda m: m.measured_at)
            
            # Calculate trend
            recent_values = [m.metric_value for m in metrics[-5:]]  # Last 5 measurements
            if len(recent_values) >= 2:
                trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
                
                # Generate recommendations based on trend and current status
                current_metric = metrics[-1]
                
                if current_metric.quality_status in [QualityStatus.POOR, QualityStatus.CRITICAL]:
                    if trend < 0:
                        recommendations.append({
                            "metric_name": metric_name,
                            "current_value": current_metric.metric_value,
                            "current_status": current_metric.quality_status.value,
                            "trend": "declining",
                            "recommendation": f"Immediate action required: {metric_name} quality is declining and currently {current_metric.quality_status.value}",
                            "priority": "high"
                        })
                    else:
                        recommendations.append({
                            "metric_name": metric_name,
                            "current_value": current_metric.metric_value,
                            "current_status": current_metric.quality_status.value,
                            "trend": "improving",
                            "recommendation": f"Continue monitoring: {metric_name} quality is improving but still {current_metric.quality_status.value}",
                            "priority": "medium"
                        })
                elif trend < 0:
                    recommendations.append({
                        "metric_name": metric_name,
                        "current_value": current_metric.metric_value,
                        "current_status": current_metric.quality_status.value,
                        "trend": "declining",
                        "recommendation": f"Monitor closely: {metric_name} quality is declining",
                        "priority": "medium"
                    })
        
        return recommendations
    
    def export_quality_report(self, format: str = "json") -> str:
        """
        Export quality report in specified format.
        
        Args:
            format: Export format (json, csv, etc.)
            
        Returns:
            Exported report as string
        """
        if format.lower() == "json":
            import json
            data = {
                "summary": self.get_quality_summary(),
                "quality_alerts": self.quality_alerts,
                "exported_at": datetime.utcnow().isoformat()
            }
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def cleanup_old_metrics(self, days_old: int = 90) -> int:
        """
        Clean up old quality metrics.
        
        Args:
            days_old: Remove metrics older than this many days
            
        Returns:
            Number of metrics removed
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        metrics_to_remove = []
        for metric_id, metric in self.quality_metrics.items():
            if metric.measured_at < cutoff_date:
                metrics_to_remove.append(metric_id)
        
        for metric_id in metrics_to_remove:
            self._remove_metric(metric_id)
        
        logger.info(f"Cleaned up {len(metrics_to_remove)} old quality metrics")
        return len(metrics_to_remove)
    
    def _remove_metric(self, metric_id: UUID) -> None:
        """Remove a quality metric and update indexes."""
        if metric_id not in self.quality_metrics:
            return
        
        metric = self.quality_metrics[metric_id]
        
        # Remove from module index
        if metric.module_name in self.module_metrics:
            self.module_metrics[metric.module_name] = [
                mid for mid in self.module_metrics[metric.module_name] if mid != metric_id
            ]
        
        # Remove metric
        del self.quality_metrics[metric_id]
