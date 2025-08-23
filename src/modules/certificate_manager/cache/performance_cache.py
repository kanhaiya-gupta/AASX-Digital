"""
Performance Cache for Certificate Manager

Handles performance optimization caching and metrics tracking
for improved system performance and monitoring.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)


class PerformanceMetrics(Enum):
    """Performance metric types"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    BANDWIDTH = "bandwidth"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"


class CacheHitRate(Enum):
    """Cache hit rate categories"""
    EXCELLENT = "excellent"     # 90%+
    GOOD = "good"               # 75-89%
    FAIR = "fair"               # 60-74%
    POOR = "poor"               # 40-59%
    VERY_POOR = "very_poor"     # <40%


class PerformanceCache:
    """
    Performance optimization cache service
    
    Handles:
    - Performance data caching and optimization
    - Metrics collection and analysis
    - Performance trend analysis
    - Cache performance optimization
    - Performance alerting and monitoring
    """
    
    def __init__(self):
        """Initialize the performance cache service"""
        self.performance_metrics = list(PerformanceMetrics)
        self.cache_hit_rates = list(CacheHitRate)
        
        # Performance data storage
        self.performance_data: Dict[str, Dict[str, Any]] = {}
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = {}
        self.performance_alerts: List[Dict[str, Any]] = []
        
        # Performance cache locks
        self.performance_locks: Dict[str, asyncio.Lock] = {}
        self.global_lock = asyncio.Lock()
        
        # Performance cache settings
        self.performance_settings = self._initialize_performance_settings()
        
        # Performance monitoring
        self.monitoring_tasks: List[asyncio.Task] = []
        self.alert_thresholds = self._initialize_alert_thresholds()
        
        # Performance optimization
        self.optimization_queue = asyncio.Queue()
        self.optimization_history: List[Dict[str, Any]] = []
        
        logger.info("Performance Cache service initialized successfully")
    
    def _initialize_performance_settings(self) -> Dict[str, Any]:
        """Initialize performance cache settings"""
        return {
            "metrics_collection_interval_seconds": 30,
            "metrics_retention_hours": 24,
            "performance_alerting_enabled": True,
            "auto_optimization_enabled": True,
            "cache_warming_threshold": 0.7,  # 70% cache hit rate
            "performance_degradation_threshold": 0.2,  # 20% performance drop
            "max_metrics_history_size": 10000,
            "performance_optimization_interval_minutes": 10
        }
    
    def _initialize_alert_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Initialize performance alert thresholds"""
        return {
            "response_time": {
                "warning": 1000,  # 1 second
                "critical": 5000   # 5 seconds
            },
            "cache_hit_rate": {
                "warning": 0.6,    # 60%
                "critical": 0.4    # 40%
            },
            "error_rate": {
                "warning": 0.05,   # 5%
                "critical": 0.1    # 10%
            },
            "cpu_usage": {
                "warning": 0.8,    # 80%
                "critical": 0.95   # 95%
            },
            "memory_usage": {
                "warning": 0.8,    # 80%
                "critical": 0.95   # 95%
            }
        }
    
    async def cache_performance_data(
        self,
        metric_name: str,
        metric_value: Union[int, float],
        metric_type: str = "gauge",
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Cache performance data for a specific metric
        
        Args:
            metric_name: Name of the performance metric
            metric_value: Value of the metric
            metric_type: Type of metric (gauge, counter, histogram)
            tags: Additional tags for the metric
            timestamp: Timestamp for the metric (defaults to current time)
            
        Returns:
            Dictionary containing cached performance data
        """
        # Validate metric name
        if metric_name not in [m.value for m in self.performance_metrics]:
            raise ValueError(f"Invalid metric name: {metric_name}")
        
        # Use current time if none provided
        if timestamp is None:
            timestamp = time.time()
        
        # Create metric record
        metric_record = {
            "metric_name": metric_name,
            "metric_value": metric_value,
            "metric_type": metric_type,
            "tags": tags or {},
            "timestamp": timestamp,
            "cached_at": time.time()
        }
        
        # Store metric data
        if metric_name not in self.performance_data:
            self.performance_data[metric_name] = {}
        
        # Use timestamp as key for time-series data
        timestamp_key = str(int(timestamp))
        self.performance_data[metric_name][timestamp_key] = metric_record
        
        # Add to metrics history
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = []
        
        self.metrics_history[metric_name].append(metric_record)
        
        # Check alert thresholds
        await self._check_performance_alerts(metric_name, metric_value)
        
        # Trigger auto-optimization if enabled
        if self.performance_settings["auto_optimization_enabled"]:
            await self._trigger_auto_optimization(metric_name, metric_value)
        
        logger.debug(f"Performance metric '{metric_name}' cached with value {metric_value}")
        
        return metric_record
    
    async def get_performance_data(
        self,
        metric_name: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get performance data for a specific metric
        
        Args:
            metric_name: Name of the performance metric
            start_time: Start timestamp for data range
            end_time: End timestamp for data range
            limit: Maximum number of data points to return
            
        Returns:
            List of performance data records
        """
        if metric_name not in self.performance_data:
            return []
        
        # Get all data for the metric
        all_data = list(self.performance_data[metric_name].values())
        
        # Filter by time range if specified
        if start_time is not None:
            all_data = [d for d in all_data if d["timestamp"] >= start_time]
        
        if end_time is not None:
            all_data = [d for d in all_data if d["timestamp"] <= end_time]
        
        # Sort by timestamp (newest first) and limit results
        all_data.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_data[:limit]
    
    async def get_performance_summary(
        self,
        metric_name: str,
        time_window_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Get performance summary for a metric over a time window
        
        Args:
            metric_name: Name of the performance metric
            time_window_hours: Time window in hours
            
        Returns:
            Dictionary containing performance summary
        """
        if metric_name not in self.performance_data:
            return {
                "metric_name": metric_name,
                "time_window_hours": time_window_hours,
                "data_points": 0,
                "summary": {}
            }
        
        # Calculate time window
        end_time = time.time()
        start_time = end_time - (time_window_hours * 3600)
        
        # Get data within time window
        window_data = await self.get_performance_data(metric_name, start_time, end_time)
        
        if not window_data:
            return {
                "metric_name": metric_name,
                "time_window_hours": time_window_hours,
                "data_points": 0,
                "summary": {}
            }
        
        # Calculate summary statistics
        values = [d["metric_value"] for d in window_data if isinstance(d["metric_value"], (int, float))]
        
        if not values:
            return {
                "metric_name": metric_name,
                "time_window_hours": time_window_hours,
                "data_points": len(window_data),
                "summary": {}
            }
        
        summary = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "sum": sum(values),
            "average": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "earliest": values[0] if values else None
        }
        
        # Calculate percentiles if we have enough data
        if len(values) >= 10:
            sorted_values = sorted(values)
            summary["p50"] = sorted_values[len(sorted_values) // 2]
            summary["p90"] = sorted_values[int(len(sorted_values) * 0.9)]
            summary["p95"] = sorted_values[int(len(sorted_values) * 0.95)]
            summary["p99"] = sorted_values[int(len(sorted_values) * 0.99)]
        
        return {
            "metric_name": metric_name,
            "time_window_hours": time_window_hours,
            "data_points": len(window_data),
            "summary": summary,
            "timestamp": time.time()
        }
    
    async def analyze_performance_trends(
        self,
        metric_name: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze performance trends for a metric
        
        Args:
            metric_name: Name of the performance metric
            time_window_hours: Time window for trend analysis
            
        Returns:
            Dictionary containing trend analysis
        """
        if metric_name not in self.performance_data:
            return {
                "metric_name": metric_name,
                "trend": "insufficient_data",
                "analysis": {}
            }
        
        # Get data for trend analysis
        end_time = time.time()
        start_time = end_time - (time_window_hours * 3600)
        trend_data = await self.get_performance_data(metric_name, start_time, end_time)
        
        if len(trend_data) < 10:
            return {
                "metric_name": metric_name,
                "trend": "insufficient_data",
                "analysis": {
                    "data_points": len(trend_data),
                    "min_required": 10
                }
            }
        
        # Sort data by timestamp (oldest first)
        trend_data.sort(key=lambda x: x["timestamp"])
        
        # Calculate trend indicators
        values = [d["metric_value"] for d in trend_data if isinstance(d["metric_value"], (int, float))]
        
        if not values:
            return {
                "metric_name": metric_name,
                "trend": "no_data",
                "analysis": {}
            }
        
        # Split data into halves for trend comparison
        mid_point = len(values) // 2
        first_half = values[:mid_point]
        second_half = values[mid_point:]
        
        if not first_half or not second_half:
            return {
                "metric_name": metric_name,
                "trend": "insufficient_data",
                "analysis": {}
            }
        
        # Calculate averages for trend comparison
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        # Determine trend direction
        if second_avg > first_avg * 1.1:  # 10% increase
            trend = "improving"
        elif second_avg < first_avg * 0.9:  # 10% decrease
            trend = "degrading"
        else:
            trend = "stable"
        
        # Calculate trend strength
        trend_strength = abs(second_avg - first_avg) / first_avg if first_avg > 0 else 0
        
        # Calculate volatility
        all_values = values
        mean = sum(all_values) / len(all_values)
        variance = sum((x - mean) ** 2 for x in all_values) / len(all_values)
        volatility = variance ** 0.5
        
        analysis = {
            "trend": trend,
            "trend_strength": round(trend_strength * 100, 2),  # Percentage
            "first_half_average": round(first_avg, 4),
            "second_half_average": round(second_avg, 4),
            "change_percentage": round(((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0, 2),
            "volatility": round(volatility, 4),
            "data_points": len(values),
            "time_window_hours": time_window_hours
        }
        
        return {
            "metric_name": metric_name,
            "trend": trend,
            "analysis": analysis,
            "timestamp": time.time()
        }
    
    async def optimize_cache_performance(
        self,
        optimization_type: str = "auto",
        target_metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Optimize cache performance based on collected metrics
        
        Args:
            optimization_type: Type of optimization (auto, manual, targeted)
            target_metrics: Specific metrics to optimize (optional)
            
        Returns:
            Dictionary containing optimization results
        """
        optimization_result = {
            "optimization_type": optimization_type,
            "target_metrics": target_metrics or [],
            "optimizations_applied": [],
            "performance_impact": {},
            "timestamp": time.time()
        }
        
        # Get current performance metrics
        current_metrics = await self._get_current_performance_state()
        
        # Apply optimizations based on type
        if optimization_type == "auto":
            optimizations = await self._apply_auto_optimizations(current_metrics)
        elif optimization_type == "manual":
            optimizations = await self._apply_manual_optimizations(current_metrics)
        elif optimization_type == "targeted":
            optimizations = await self._apply_targeted_optimizations(current_metrics, target_metrics)
        else:
            raise ValueError(f"Unknown optimization type: {optimization_type}")
        
        optimization_result["optimizations_applied"] = optimizations
        
        # Measure performance impact
        await asyncio.sleep(0.1)  # Simulate optimization time
        new_metrics = await self._get_current_performance_state()
        
        optimization_result["performance_impact"] = await self._calculate_optimization_impact(
            current_metrics, new_metrics
        )
        
        # Add to optimization history
        self.optimization_history.append(optimization_result)
        
        logger.info(f"Cache performance optimization completed: {len(optimizations)} optimizations applied")
        
        return optimization_result
    
    async def get_performance_alerts(
        self,
        alert_level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get performance alerts
        
        Args:
            alert_level: Filter by alert level (warning, critical)
            limit: Maximum number of alerts to return
            
        Returns:
            List of performance alerts
        """
        alerts = self.performance_alerts.copy()
        
        # Filter by alert level
        if alert_level:
            alerts = [a for a in alerts if a.get("level") == alert_level]
        
        # Sort by timestamp (newest first) and limit results
        alerts.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return alerts[:limit]
    
    async def clear_performance_alerts(self, alert_ids: Optional[List[str]] = None) -> int:
        """
        Clear performance alerts
        
        Args:
            alert_ids: Specific alert IDs to clear (None to clear all)
            
        Returns:
            Number of alerts cleared
        """
        if alert_ids is None:
            # Clear all alerts
            cleared_count = len(self.performance_alerts)
            self.performance_alerts.clear()
        else:
            # Clear specific alerts
            original_count = len(self.performance_alerts)
            self.performance_alerts = [a for a in self.performance_alerts if a.get("id") not in alert_ids]
            cleared_count = original_count - len(self.performance_alerts)
        
        logger.info(f"Cleared {cleared_count} performance alerts")
        return cleared_count
    
    async def _check_performance_alerts(
        self,
        metric_name: str,
        metric_value: Union[int, float]
    ) -> None:
        """Check if performance metric triggers alerts"""
        if not self.performance_settings["performance_alerting_enabled"]:
            return
        
        # Get thresholds for this metric
        thresholds = self.alert_thresholds.get(metric_name)
        if not thresholds:
            return
        
        # Check warning threshold
        if metric_value >= thresholds.get("warning", float('inf')):
            alert_level = "warning"
        elif metric_value >= thresholds.get("critical", float('inf')):
            alert_level = "critical"
        else:
            return  # No alert needed
        
        # Create alert
        alert = {
            "id": f"alert_{metric_name}_{int(time.time())}",
            "metric_name": metric_name,
            "metric_value": metric_value,
            "level": alert_level,
            "threshold": thresholds[alert_level],
            "message": f"Performance metric '{metric_name}' exceeded {alert_level} threshold: {metric_value}",
            "timestamp": time.time(),
            "status": "active"
        }
        
        # Add alert
        self.performance_alerts.append(alert)
        
        logger.warning(f"Performance alert: {alert['message']}")
    
    async def _trigger_auto_optimization(
        self,
        metric_name: str,
        metric_value: Union[int, float]
    ) -> None:
        """Trigger automatic optimization based on performance metrics"""
        # Check if optimization is needed
        if metric_name == "cache_hit_rate" and metric_value < self.performance_settings["cache_warming_threshold"]:
            # Cache hit rate is low, trigger warming
            await self.optimization_queue.put({
                "type": "cache_warming",
                "metric_name": metric_name,
                "metric_value": metric_value,
                "priority": "high",
                "timestamp": time.time()
            })
        
        elif metric_name == "response_time" and metric_value > self.alert_thresholds["response_time"]["warning"]:
            # Response time is high, trigger optimization
            await self.optimization_queue.put({
                "type": "performance_optimization",
                "metric_name": metric_name,
                "metric_value": metric_value,
                "priority": "medium",
                "timestamp": time.time()
            })
    
    async def _get_current_performance_state(self) -> Dict[str, Any]:
        """Get current performance state for all metrics"""
        current_state = {}
        
        for metric_name in self.performance_data:
            # Get latest value for each metric
            latest_data = await self.get_performance_data(metric_name, limit=1)
            if latest_data:
                current_state[metric_name] = latest_data[0]["metric_value"]
        
        return current_state
    
    async def _apply_auto_optimizations(self, current_metrics: Dict[str, Any]) -> List[str]:
        """Apply automatic optimizations based on current metrics"""
        optimizations = []
        
        # Check cache hit rate
        if "cache_hit_rate" in current_metrics:
            hit_rate = current_metrics["cache_hit_rate"]
            if hit_rate < 0.6:  # Below 60%
                optimizations.append("cache_warming_triggered")
                optimizations.append("cache_size_increased")
        
        # Check response time
        if "response_time" in current_metrics:
            response_time = current_metrics["response_time"]
            if response_time > 2000:  # Above 2 seconds
                optimizations.append("cache_prefetching_enabled")
                optimizations.append("connection_pooling_optimized")
        
        # Check memory usage
        if "memory_usage" in current_metrics:
            memory_usage = current_metrics["memory_usage"]
            if memory_usage > 0.8:  # Above 80%
                optimizations.append("memory_cleanup_triggered")
                optimizations.append("cache_eviction_aggressive")
        
        return optimizations
    
    async def _apply_manual_optimizations(self, current_metrics: Dict[str, Any]) -> List[str]:
        """Apply manual optimizations"""
        optimizations = [
            "cache_defragmentation",
            "memory_optimization",
            "connection_pool_cleanup",
            "cache_warming_full"
        ]
        
        return optimizations
    
    async def _apply_targeted_optimizations(
        self,
        current_metrics: Dict[str, Any],
        target_metrics: List[str]
    ) -> List[str]:
        """Apply targeted optimizations for specific metrics"""
        optimizations = []
        
        for metric_name in target_metrics:
            if metric_name in current_metrics:
                if metric_name == "cache_hit_rate":
                    optimizations.append(f"{metric_name}_targeted_warming")
                elif metric_name == "response_time":
                    optimizations.append(f"{metric_name}_latency_optimization")
                elif metric_name == "memory_usage":
                    optimizations.append(f"{metric_name}_memory_cleanup")
        
        return optimizations
    
    async def _calculate_optimization_impact(
        self,
        before_metrics: Dict[str, Any],
        after_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate the impact of optimizations"""
        impact = {}
        
        for metric_name in before_metrics:
            if metric_name in after_metrics:
                before_value = before_metrics[metric_name]
                after_value = after_metrics[metric_name]
                
                if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)):
                    if before_value > 0:
                        change_percentage = ((after_value - before_value) / before_value) * 100
                        impact[metric_name] = {
                            "before": before_value,
                            "after": after_value,
                            "change_percentage": round(change_percentage, 2),
                            "improvement": change_percentage < 0  # Lower is better for most metrics
                        }
        
        return impact
    
    async def start_performance_monitoring(self):
        """Start performance monitoring tasks"""
        async def metrics_collector():
            while True:
                try:
                    # Collect system performance metrics
                    await self._collect_system_metrics()
                    
                    # Wait for next collection interval
                    await asyncio.sleep(self.performance_settings["metrics_collection_interval_seconds"])
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in metrics collector: {e}")
        
        async def optimization_worker():
            while True:
                try:
                    # Process optimization tasks
                    if not self.optimization_queue.empty():
                        optimization_task = await self.optimization_queue.get()
                        await self._process_optimization_task(optimization_task)
                        self.optimization_queue.task_done()
                    
                    # Wait before next check
                    await asyncio.sleep(1)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in optimization worker: {e}")
        
        # Start monitoring tasks
        collector_task = asyncio.create_task(metrics_collector())
        worker_task = asyncio.create_task(optimization_worker())
        
        self.monitoring_tasks.extend([collector_task, worker_task])
        
        logger.info("Performance monitoring started")
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        current_time = time.time()
        
        # Simulate system metrics collection
        # In a real implementation, these would be actual system calls
        
        # Simulate CPU usage
        cpu_usage = 0.3 + (0.4 * (current_time % 100) / 100)  # Varies between 30-70%
        await self.cache_performance_data("cpu_usage", cpu_usage)
        
        # Simulate memory usage
        memory_usage = 0.4 + (0.3 * (current_time % 80) / 80)  # Varies between 40-70%
        await self.cache_performance_data("memory_usage", memory_usage)
        
        # Simulate response time
        response_time = 100 + (200 * (current_time % 60) / 60)  # Varies between 100-300ms
        await self.cache_performance_data("response_time", response_time)
        
        # Simulate cache hit rate
        cache_hit_rate = 0.6 + (0.3 * (current_time % 120) / 120)  # Varies between 60-90%
        await self.cache_performance_data("cache_hit_rate", cache_hit_rate)
    
    async def _process_optimization_task(self, optimization_task: Dict[str, Any]):
        """Process an optimization task"""
        task_type = optimization_task["type"]
        metric_name = optimization_task["metric_name"]
        priority = optimization_task["priority"]
        
        logger.info(f"Processing optimization task: {task_type} for {metric_name} with {priority} priority")
        
        # Simulate optimization processing
        await asyncio.sleep(0.1)
        
        logger.info(f"Optimization task completed: {task_type}")
    
    async def get_performance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        total_metrics = len(self.performance_data)
        total_alerts = len(self.performance_alerts)
        active_alerts = len([a for a in self.performance_alerts if a.get("status") == "active"])
        
        # Calculate cache hit rate category
        cache_hit_rate_data = await self.get_performance_data("cache_hit_rate", limit=1)
        current_hit_rate = cache_hit_rate_data[0]["metric_value"] if cache_hit_rate_data else 0
        
        if current_hit_rate >= 0.9:
            hit_rate_category = CacheHitRate.EXCELLENT.value
        elif current_hit_rate >= 0.75:
            hit_rate_category = CacheHitRate.GOOD.value
        elif current_hit_rate >= 0.6:
            hit_rate_category = CacheHitRate.FAIR.value
        elif current_hit_rate >= 0.4:
            hit_rate_category = CacheHitRate.POOR.value
        else:
            hit_rate_category = CacheHitRate.VERY_POOR.value
        
        return {
            "total_metrics": total_metrics,
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "current_cache_hit_rate": current_hit_rate,
            "cache_hit_rate_category": hit_rate_category,
            "optimization_history_count": len(self.optimization_history),
            "monitoring_tasks_count": len(self.monitoring_tasks),
            "timestamp": time.time()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the performance cache service"""
        return {
            "status": "healthy",
            "performance_metrics_count": len(self.performance_metrics),
            "cache_hit_rates_count": len(self.cache_hit_rates),
            "performance_data_size": len(self.performance_data),
            "metrics_history_size": sum(len(h) for h in self.metrics_history.values()),
            "performance_alerts_count": len(self.performance_alerts),
            "optimization_history_count": len(self.optimization_history),
            "monitoring_tasks_count": len(self.monitoring_tasks),
            "performance_settings": {
                "metrics_collection_interval_seconds": self.performance_settings["metrics_collection_interval_seconds"],
                "performance_alerting_enabled": self.performance_settings["performance_alerting_enabled"],
                "auto_optimization_enabled": self.performance_settings["auto_optimization_enabled"]
            },
            "timestamp": time.time()
        }
    
    async def cleanup(self):
        """Cleanup performance cache resources"""
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Clear monitoring tasks list
        self.monitoring_tasks.clear()
        
        logger.info("Performance Cache cleanup completed")
