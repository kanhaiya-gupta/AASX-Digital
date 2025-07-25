"""
Performance Monitoring Module for Digital Twins
Phase 2.2.1: Real-Time Performance Metrics
"""

import asyncio
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from .twin_manager import twin_manager

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of performance metrics"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    UPTIME = "uptime"
    DATA_POINTS = "data_points"

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    twin_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    unit: str
    description: str = ""

@dataclass
class TwinPerformance:
    """Complete performance data for a twin"""
    twin_id: str
    twin_name: str
    cpu_usage: float
    memory_usage: float
    response_time: float
    throughput: float
    error_rate: float
    uptime_seconds: int
    data_points_processed: int
    last_update: datetime
    health_score: float
    status: str

class PerformanceMonitor:
    """Real-time performance monitoring for digital twins"""
    
    def __init__(self):
        self.metrics_history: Dict[str, List[PerformanceMetric]] = {}
        self.current_performance: Dict[str, TwinPerformance] = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.alert_thresholds = {
            "cpu_usage": 80.0,  # Alert if CPU > 80%
            "memory_usage": 85.0,  # Alert if memory > 85%
            "response_time": 5.0,  # Alert if response time > 5 seconds
            "error_rate": 5.0,  # Alert if error rate > 5%
        }
        
        # Use centralized database manager from twin_manager
        self.db_manager = twin_manager.db_manager
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start the performance monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            logger.info("Performance monitoring started")
            # Don't start a separate thread - just collect metrics on demand
    
    def stop_monitoring(self):
        """Stop the performance monitoring"""
        self.monitoring_active = False
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop - now synchronous"""
        if not self.monitoring_active:
            return
        
        try:
            # Collect performance metrics
            self._collect_performance_metrics()
            
            # Check for alerts
            self._check_alerts()
            
            # Save snapshots periodically
            self._save_snapshots()
            
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
    
    def collect_metrics_now(self):
        """Collect metrics immediately (called on demand)"""
        self._monitoring_loop()
    
    def _collect_performance_metrics(self):
        """Collect performance metrics for all active twins (only for completed files)"""
        try:
            twins = twin_manager.get_all_registered_twins()
            for twin in twins:
                twin_id = twin['twin_id']
                twin_name = twin['twin_name']
                data_points = twin.get('data_points') or 0
                self._collect_twin_metrics(twin_id, twin_name, data_points)
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
    
    def _collect_twin_metrics(self, twin_id: str, twin_name: str, data_points: int):
        """Collect metrics for a specific twin"""
        try:
            # Simulate realistic performance metrics
            # In a real system, these would come from actual twin monitoring
            
            # CPU usage (simulated based on data processing activity)
            cpu_usage = min(100.0, max(5.0, (data_points / 1000) * 15 + (hash(twin_id) % 20)))
            
            # Memory usage (simulated based on twin complexity - more realistic)
            # Use a more balanced calculation that doesn't scale linearly with ID length
            base_memory = 15.0  # Base memory usage
            complexity_factor = min(20.0, len(twin_id) * 0.3)  # Cap complexity impact
            random_factor = hash(twin_id) % 25  # Random variation
            memory_usage = min(85.0, max(10.0, base_memory + complexity_factor + random_factor))
            
            # Response time (simulated based on data volume)
            response_time = max(0.1, (data_points / 10000) + (hash(twin_id) % 3))
            
            # Throughput (data points processed per second)
            throughput = max(10, data_points / 3600)  # Assuming hourly data
            
            # Error rate (simulated, typically low for healthy twins)
            error_rate = max(0.0, min(10.0, (hash(twin_id) % 5) * 0.5))
            
            # Uptime (simulated based on twin age)
            uptime_seconds = max(3600, (hash(twin_id) % 7) * 86400)  # 1-7 days
            
            # Calculate health score (0-100, higher is better)
            health_score = self._calculate_health_score(
                cpu_usage, memory_usage, response_time, error_rate
            )
            
            # Determine status based on health score
            if health_score >= 90:
                status = "excellent"
            elif health_score >= 75:
                status = "good"
            elif health_score >= 60:
                status = "fair"
            else:
                status = "poor"
            
            # Create performance object
            performance = TwinPerformance(
                twin_id=twin_id,
                twin_name=twin_name,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                response_time=response_time,
                throughput=throughput,
                error_rate=error_rate,
                uptime_seconds=uptime_seconds,
                data_points_processed=data_points,
                last_update=datetime.now(),
                health_score=health_score,
                status=status
            )
            
            # Store current performance
            self.current_performance[twin_id] = performance
            
            # Store metrics in history
            self._store_metric(twin_id, MetricType.CPU_USAGE, cpu_usage, "%")
            self._store_metric(twin_id, MetricType.MEMORY_USAGE, memory_usage, "%")
            self._store_metric(twin_id, MetricType.RESPONSE_TIME, response_time, "seconds")
            self._store_metric(twin_id, MetricType.THROUGHPUT, throughput, "points/sec")
            self._store_metric(twin_id, MetricType.ERROR_RATE, error_rate, "%")
            self._store_metric(twin_id, MetricType.UPTIME, uptime_seconds, "seconds")
            self._store_metric(twin_id, MetricType.DATA_POINTS, data_points, "points")
            
        except Exception as e:
            logger.error(f"Error collecting metrics for twin {twin_id}: {e}")
    
    def _calculate_health_score(self, cpu: float, memory: float, response_time: float, error_rate: float) -> float:
        """Calculate overall health score (0-100)"""
        # CPU score (lower is better)
        cpu_score = max(0, 100 - cpu)
        
        # Memory score (lower is better)
        memory_score = max(0, 100 - memory)
        
        # Response time score (lower is better, max 10 seconds)
        response_score = max(0, 100 - (response_time * 10))
        
        # Error rate score (lower is better)
        error_score = max(0, 100 - (error_rate * 10))
        
        # Weighted average
        health_score = (cpu_score * 0.25 + memory_score * 0.25 + 
                       response_score * 0.3 + error_score * 0.2)
        
        return round(health_score, 1)
    
    def _store_metric(self, twin_id: str, metric_type: MetricType, value: float, unit: str):
        """Store a performance metric in the database"""
        try:
            # Use existing twin event logging method
            self.db_manager.log_twin_event(
                twin_id=twin_id,
                event_type=f"performance_{metric_type.value}",
                message=f"{metric_type.value}: {value} {unit}",
                severity="info",
                user="system"
            )
            
        except Exception as e:
            logger.error(f"Error storing metric: {e}")
    
    def _check_alerts(self):
        """Check for performance alerts"""
        for twin_id, performance in self.current_performance.items():
            # Check CPU usage
            if performance.cpu_usage > self.alert_thresholds["cpu_usage"]:
                self._create_alert(twin_id, "cpu_usage", performance.cpu_usage, 
                                 self.alert_thresholds["cpu_usage"], "warning")
            
            # Check memory usage
            if performance.memory_usage > self.alert_thresholds["memory_usage"]:
                self._create_alert(twin_id, "memory_usage", performance.memory_usage,
                                 self.alert_thresholds["memory_usage"], "warning")
            
            # Check response time
            if performance.response_time > self.alert_thresholds["response_time"]:
                self._create_alert(twin_id, "response_time", performance.response_time,
                                 self.alert_thresholds["response_time"], "warning")
            
            # Check error rate
            if performance.error_rate > self.alert_thresholds["error_rate"]:
                self._create_alert(twin_id, "error_rate", performance.error_rate,
                                 self.alert_thresholds["error_rate"], "critical")
    
    def _create_alert(self, twin_id: str, alert_type: str, metric_value: float, 
                     threshold: float, severity: str):
        """Create a performance alert"""
        try:
            messages = {
                "cpu_usage": f"CPU usage {metric_value:.1f}% exceeds threshold {threshold:.1f}%",
                "memory_usage": f"Memory usage {metric_value:.1f}% exceeds threshold {threshold:.1f}%",
                "response_time": f"Response time {metric_value:.2f}s exceeds threshold {threshold:.2f}s",
                "error_rate": f"Error rate {metric_value:.1f}% exceeds threshold {threshold:.1f}%"
            }
            
            message = messages.get(alert_type, f"Performance alert: {alert_type}")
            
            # Use existing twin event logging method
            self.db_manager.log_twin_event(
                twin_id=twin_id,
                event_type=f"alert_{alert_type}",
                message=message,
                severity=severity,
                user="system"
            )
            
            logger.warning(f"Performance alert for twin {twin_id}: {message}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def _save_snapshots(self):
        """Save current performance snapshots"""
        try:
            for twin_id, performance in self.current_performance.items():
                # Use existing twin health update method
                self.db_manager.update_twin_health(
                    twin_id=twin_id,
                    health_data={
                        'overall_health': performance.health_score,
                        'performance_health': 100.0 - performance.cpu_usage,
                        'connectivity_health': 100.0 - performance.error_rate,
                        'data_health': 100.0,
                        'operational_health': 100.0 - (performance.response_time / 10.0),
                        'issues': [] if performance.health_score > 80 else ["Performance degradation detected"]
                    }
                )
            
        except Exception as e:
            logger.error(f"Error saving snapshots: {e}")
    
    async def get_twin_performance(self, twin_id: str) -> Optional[TwinPerformance]:
        """Get current performance for a specific twin"""
        # Collect metrics on demand
        self.collect_metrics_now()
        return self.current_performance.get(twin_id)
    
    async def get_all_twin_performance(self) -> List[TwinPerformance]:
        """Get current performance for all twins"""
        # Collect metrics on demand
        self.collect_metrics_now()
        return list(self.current_performance.values())
    
    async def get_performance_history(self, twin_id: str, metric_type: MetricType, 
                                    hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance history for a twin"""
        try:
            # Use existing twin events method
            events = self.db_manager.get_twin_events(twin_id, limit=100)
            
            # Filter for performance events
            performance_events = [
                event for event in events 
                if event.get('event_type', '').startswith('performance_')
            ]
            
            return performance_events
            
        except Exception as e:
            logger.error(f"Error getting performance history: {e}")
            return []
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active performance alerts"""
        try:
            # Get all twins and check for alert events
            twins = self.db_manager.get_all_registered_twins()
            alerts = []
            
            for twin in twins:
                twin_id = twin['twin_id']
                events = self.db_manager.get_twin_events(twin_id, limit=10)
                
                # Filter for alert events
                alert_events = [
                    event for event in events 
                    if event.get('event_type', '').startswith('alert_')
                ]
                
                alerts.extend(alert_events)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved"""
        try:
            # For now, just log that the alert was resolved
            logger.info(f"Alert {alert_id} marked as resolved")
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor() 