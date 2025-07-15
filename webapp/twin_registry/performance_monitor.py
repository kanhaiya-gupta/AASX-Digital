"""
Performance Monitoring Module for Digital Twins
Phase 2.2.1: Real-Time Performance Metrics
"""

import asyncio
import json
import sqlite3
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

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
    
    def __init__(self, db_path: str = "data/twin_registry.db"):
        self.db_path = db_path
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
        
        # Initialize database
        self._init_database()
        
        # Start monitoring
        self.start_monitoring()
    
    def _init_database(self):
        """Initialize performance monitoring database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Performance metrics history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    threshold_value REAL NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Performance snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    twin_id TEXT NOT NULL,
                    twin_name TEXT NOT NULL,
                    cpu_usage REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    response_time REAL NOT NULL,
                    throughput REAL NOT NULL,
                    error_rate REAL NOT NULL,
                    uptime_seconds INTEGER NOT NULL,
                    data_points_processed INTEGER NOT NULL,
                    health_score REAL NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Performance monitoring database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing performance database: {e}")
    
    def start_monitoring(self):
        """Start the performance monitoring thread"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop the performance monitoring thread"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self._collect_performance_metrics()
                self._check_alerts()
                self._save_snapshots()
                time.sleep(30)  # Collect metrics every 30 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_performance_metrics(self):
        """Collect performance metrics for all active twins"""
        try:
            # Get all active twins from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT twin_id, twin_name, status, last_sync, data_points
                FROM twin_aasx_relationships
                WHERE status = 'active'
            ''')
            twins = cursor.fetchall()
            conn.close()
            
            for twin in twins:
                twin_id, twin_name, status, last_sync, data_points = twin
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (twin_id, metric_type, value, timestamp, unit)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                twin_id,
                metric_type.value,
                value,
                datetime.now().isoformat(),
                unit
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing metric: {e}")
    
    def _check_alerts(self):
        """Check for performance alerts"""
        for twin_id, performance in self.current_performance.items():
            # Check CPU usage
            if performance.cpu_usage > self.alert_thresholds["cpu_usage"]:
                self._create_alert(twin_id, "high_cpu", performance.cpu_usage, 
                                 self.alert_thresholds["cpu_usage"], "warning")
            
            # Check memory usage
            if performance.memory_usage > self.alert_thresholds["memory_usage"]:
                self._create_alert(twin_id, "high_memory", performance.memory_usage,
                                 self.alert_thresholds["memory_usage"], "warning")
            
            # Check response time
            if performance.response_time > self.alert_thresholds["response_time"]:
                self._create_alert(twin_id, "slow_response", performance.response_time,
                                 self.alert_thresholds["response_time"], "warning")
            
            # Check error rate
            if performance.error_rate > self.alert_thresholds["error_rate"]:
                self._create_alert(twin_id, "high_error_rate", performance.error_rate,
                                 self.alert_thresholds["error_rate"], "critical")
    
    def _create_alert(self, twin_id: str, alert_type: str, metric_value: float, 
                     threshold: float, severity: str):
        """Create a performance alert"""
        try:
            messages = {
                "high_cpu": f"CPU usage ({metric_value:.1f}%) exceeds threshold ({threshold}%)",
                "high_memory": f"Memory usage ({metric_value:.1f}%) exceeds threshold ({threshold}%)",
                "slow_response": f"Response time ({metric_value:.2f}s) exceeds threshold ({threshold}s)",
                "high_error_rate": f"Error rate ({metric_value:.1f}%) exceeds threshold ({threshold}%)"
            }
            
            message = messages.get(alert_type, f"Performance alert: {alert_type}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_alerts 
                (twin_id, alert_type, metric_value, threshold_value, message, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                twin_id,
                alert_type,
                metric_value,
                threshold,
                message,
                severity
            ))
            
            conn.commit()
            conn.close()
            
            logger.warning(f"Performance alert for twin {twin_id}: {message}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def _save_snapshots(self):
        """Save current performance snapshots"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for twin_id, performance in self.current_performance.items():
                cursor.execute('''
                    INSERT INTO performance_snapshots 
                    (twin_id, twin_name, cpu_usage, memory_usage, response_time, 
                     throughput, error_rate, uptime_seconds, data_points_processed, 
                     health_score, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    performance.twin_id,
                    performance.twin_name,
                    performance.cpu_usage,
                    performance.memory_usage,
                    performance.response_time,
                    performance.throughput,
                    performance.error_rate,
                    performance.uptime_seconds,
                    performance.data_points_processed,
                    performance.health_score,
                    performance.status
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving snapshots: {e}")
    
    async def get_twin_performance(self, twin_id: str) -> Optional[TwinPerformance]:
        """Get current performance for a specific twin"""
        return self.current_performance.get(twin_id)
    
    async def get_all_twin_performance(self) -> List[TwinPerformance]:
        """Get current performance for all twins"""
        return list(self.current_performance.values())
    
    async def get_performance_history(self, twin_id: str, metric_type: MetricType, 
                                    hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance history for a twin"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT value, timestamp, unit
                FROM performance_metrics
                WHERE twin_id = ? AND metric_type = ? AND timestamp > ?
                ORDER BY timestamp ASC
            ''', (twin_id, metric_type.value, cutoff_time.isoformat()))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "value": row[0],
                    "timestamp": row[1],
                    "unit": row[2]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting performance history: {e}")
            return []
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active performance alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT twin_id, alert_type, metric_value, threshold_value, 
                       message, severity, timestamp
                FROM performance_alerts
                WHERE status = 'active'
                ORDER BY timestamp DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "twin_id": row[0],
                    "alert_type": row[1],
                    "metric_value": row[2],
                    "threshold_value": row[3],
                    "message": row[4],
                    "severity": row[5],
                    "timestamp": row[6]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    async def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE performance_alerts
                SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor() 