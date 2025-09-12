"""
Metrics Collector

Centralized metrics collection, aggregation, and storage system.
Supports custom metrics, automatic collection, and multiple export formats.
"""

import time
import json
import csv
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging

from .monitoring_config import MonitoringConfig


@dataclass
class MetricValue:
    """Individual metric value with timestamp"""
    value: Union[int, float, str, bool]
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric definition with values and statistics"""
    name: str
    description: str
    unit: str
    type: str  # counter, gauge, histogram, summary
    values: deque = field(default_factory=lambda: deque(maxlen=1000))
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_value(self, value: Union[int, float, str, bool], labels: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Add a new value to the metric"""
        metric_value = MetricValue(
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            metadata=metadata or {}
        )
        self.values.append(metric_value)
    
    def record_value(self, value: Union[int, float, str, bool], metadata: Optional[Dict[str, Any]] = None):
        """Record a value to the metric (alias for add_value)"""
        self.add_value(value, metadata=metadata)
    
    def get_latest_value(self) -> Optional[MetricValue]:
        """Get the most recent value"""
        return self.values[-1] if self.values else None
    
    def get_statistics(self, window_seconds: int = 3600) -> Dict[str, Any]:
        """Calculate statistics for the given time window"""
        if not self.values:
            return {}
        
        cutoff_time = time.time() - window_seconds
        recent_values = [mv.value for mv in self.values if mv.timestamp >= cutoff_time]
        
        if not recent_values:
            return {}
        
        if isinstance(recent_values[0], (int, float)):
            return {
                "count": len(recent_values),
                "min": min(recent_values),
                "max": max(recent_values),
                "sum": sum(recent_values),
                "avg": sum(recent_values) / len(recent_values),
                "latest": recent_values[-1]
            }
        else:
            return {
                "count": len(recent_values),
                "latest": recent_values[-1]
            }
    



class MetricsCollector:
    """Centralized metrics collection and management system"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics: Dict[str, Metric] = {}
        self.custom_metrics: Dict[str, Callable] = {}
        
        # Collection state
        self._collection_task: Optional[asyncio.Task] = None
        self._running = False
        self._last_collection = time.time()
        
        # Initialize default metrics
        self._init_default_metrics()
        
        # Note: Collection is not automatically started to avoid asyncio issues
        # Call start_collection() explicitly when ready to begin collection
    
    def _init_default_metrics(self):
        """Initialize default system metrics"""
        default_metrics = [
            ("system.uptime", "System uptime in seconds", "seconds", "gauge"),
            ("system.memory.used", "Memory usage in bytes", "bytes", "gauge"),
            ("system.memory.available", "Available memory in bytes", "bytes", "gauge"),
            ("system.cpu.usage", "CPU usage percentage", "percent", "gauge"),
            ("system.disk.used", "Disk usage in bytes", "bytes", "gauge"),
            ("system.disk.available", "Available disk space in bytes", "bytes", "gauge"),
            ("system.network.bytes_sent", "Network bytes sent", "bytes", "counter"),
            ("system.network.bytes_received", "Network bytes received", "bytes", "counter"),
            ("database.connections.active", "Active database connections", "count", "gauge"),
            ("database.connections.total", "Total database connections", "count", "counter"),
            ("cache.hits", "Cache hit count", "count", "counter"),
            ("cache.misses", "Cache miss count", "count", "counter"),
            ("cache.hit_rate", "Cache hit rate", "ratio", "gauge"),
            ("api.requests.total", "Total API requests", "count", "counter"),
            ("api.requests.success", "Successful API requests", "count", "counter"),
            ("api.requests.error", "Error API requests", "count", "counter"),
            ("api.response_time", "API response time", "seconds", "histogram"),
            ("security.auth.success", "Successful authentications", "count", "counter"),
            ("security.auth.failure", "Failed authentications", "count", "counter"),
            ("security.auth.rate", "Authentication success rate", "ratio", "gauge")
        ]
        
        for name, description, unit, metric_type in default_metrics:
            self.create_metric(name, description, unit, metric_type)
    
    def create_metric(self, name: str, description: str, unit: str, metric_type: str, labels: Optional[Dict[str, str]] = None) -> Metric:
        """Create a new metric"""
        if name in self.metrics:
            self.logger.warning(f"Metric {name} already exists, returning existing metric")
            return self.metrics[name]
        
        metric = Metric(
            name=name,
            description=description,
            unit=unit,
            type=metric_type,
            labels=labels or {}
        )
        self.metrics[name] = metric
        self.logger.debug(f"Created metric: {name}")
        return metric
    
    def record_value(self, metric_name: str, value: Union[int, float, str, bool], labels: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Record a value for a metric"""
        if metric_name not in self.metrics:
            self.logger.warning(f"Metric {metric_name} not found, creating default metric")
            self.create_metric(metric_name, f"Auto-created metric: {metric_name}", "unknown", "gauge")
        
        self.metrics[metric_name].add_value(value, labels, metadata)
    
    async def increment_counter(self, metric_name: str, increment: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        if metric_name not in self.metrics:
            self.create_metric(metric_name, f"Counter: {metric_name}", "count", "counter")
        
        current_metric = self.metrics[metric_name]
        if current_metric.type != "counter":
            self.logger.warning(f"Metric {metric_name} is not a counter, converting to counter")
            current_metric.type = "counter"
        
        # Get current value or start at 0
        latest = current_metric.get_latest_value()
        current_value = latest.value if latest else 0
        new_value = current_value + increment
        
        current_metric.add_value(new_value, labels)
    
    def set_gauge(self, metric_name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        if metric_name not in self.metrics:
            self.create_metric(metric_name, f"Gauge: {metric_name}", "value", "gauge")
        
        current_metric = self.metrics[metric_name]
        if current_metric.type != "gauge":
            self.logger.warning(f"Metric {metric_name} is not a gauge, converting to gauge")
            current_metric.type = "gauge"
        
        current_metric.add_value(value, labels)
    
    def record_histogram(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        if metric_name not in self.metrics:
            self.create_metric(metric_name, f"Histogram: {metric_name}", "value", "histogram")
        
        current_metric = self.metrics[metric_name]
        if current_metric.type != "histogram":
            self.logger.warning(f"Metric {metric_name} is not a histogram, converting to histogram")
            current_metric.type = "histogram"
        
        current_metric.add_value(value, labels)
    
    def add_custom_metric(self, name: str, collector_func: Callable[[], Union[int, float, str, bool]]):
        """Add a custom metric that will be collected automatically"""
        self.custom_metrics[name] = collector_func
        self.logger.debug(f"Added custom metric collector: {name}")
    
    async def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil
            
            # System metrics
            self.set_gauge("system.uptime", time.time() - self._last_collection)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.set_gauge("system.memory.used", memory.used)
            self.set_gauge("system.memory.available", memory.available)
            self.set_gauge("system.memory.usage", memory.percent)
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.set_gauge("system.cpu.usage", cpu_percent)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.set_gauge("system.disk.used", disk.used)
            self.set_gauge("system.disk.available", disk.free)
            self.set_gauge("system.disk.usage", (disk.used / disk.total) * 100)
            
            # Network metrics
            network = psutil.net_io_counters()
            self.set_gauge("system.network.bytes_sent", network.bytes_sent)
            self.set_gauge("system.network.bytes_received", network.bytes_recv)
            
        except ImportError:
            self.logger.warning("psutil not available, skipping system metrics")
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    async def collect_custom_metrics(self):
        """Collect custom metrics from registered collectors"""
        for name, collector_func in self.custom_metrics.items():
            try:
                value = collector_func()
                self.record_value(name, value)
            except Exception as e:
                self.logger.error(f"Error collecting custom metric {name}: {e}")
    
    async def collect_metrics(self):
        """Collect all metrics"""
        if not self.config.metrics.enabled:
            return
        
        try:
            # Collect system metrics
            await self.collect_system_metrics()
            
            # Collect custom metrics
            await self.collect_custom_metrics()
            
            # Update collection timestamp
            self._last_collection = time.time()
            
            # Cleanup old metrics if needed
            self._cleanup_old_metrics()
            
        except Exception as e:
            self.logger.error(f"Error during metrics collection: {e}")
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period"""
        if not self.config.metrics.retention_period:
            return
        
        cutoff_time = time.time() - self.config.metrics.retention_period
        
        for metric in self.metrics.values():
            # Remove old values
            metric.values = deque(
                [mv for mv in metric.values if mv.timestamp >= cutoff_time],
                maxlen=metric.values.maxlen
            )
    
    async def initialize(self):
        """Initialize the metrics collector"""
        try:
            # Initialize default metrics
            self._init_default_metrics()
            
            # Start collection if enabled
            if self.config.metrics.enabled:
                await self.start_collection()
            
            self.logger.info("Metrics collector initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize metrics collector: {e}")
            raise

    async def get_health(self) -> Dict[str, Any]:
        """Get health status of the metrics collector"""
        try:
            return {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics_count": len(self.metrics),
                "custom_metrics_count": len(self.custom_metrics),
                "last_collection": self._last_collection,
                "message": "Metrics collector is operational"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "message": "Metrics collector has errors"
            }
    
    async def start_collection(self):
        """Start metrics collection"""
        if self._collection_task and not self._collection_task.done():
            return
        
        self._running = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        self.logger.info("Started metrics collection")
    
    async def stop_collection(self):
        """Stop metrics collection"""
        if not self._running:
            return
        
        self._running = False
        if self._collection_task:
            self._collection_task.cancel()
        self.logger.info("Stopped metrics collection")
    
    async def cleanup(self):
        """Cleanup metrics collector resources"""
        try:
            # Stop collection if running
            await self.stop_collection()
            
            # Clear metrics
            self.metrics.clear()
            self.custom_metrics.clear()
            
            # Reset state
            self._last_collection = time.time()
            
            self.logger.info("Metrics collector cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Failed to cleanup metrics collector: {e}")
            raise
    
    async def _collection_loop(self):
        """Main collection loop"""
        while self._running:
            try:
                await self.collect_metrics()
                await asyncio.sleep(self.config.metrics.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a specific metric by name"""
        return self.metrics.get(name)
    
    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all metrics"""
        return self.metrics.copy()
    
    async def record_metric(self, metric_name: str, metric_value: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a metric value with optional metadata"""
        try:
            if metric_name not in self.metrics:
                # Create a new metric if it doesn't exist
                self.metrics[metric_name] = Metric(
                    name=metric_name,
                    description=f"Auto-generated metric: {metric_name}",
                    unit="count",
                    type="counter"
                )
            
            # Record the metric value
            self.metrics[metric_name].record_value(metric_value, metadata=metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to record metric {metric_name}: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics data"""
        try:
            metrics_data = {}
            for name, metric in self.metrics.items():
                metrics_data[name] = {
                    "description": metric.description,
                    "unit": metric.unit,
                    "type": metric.type,
                    "latest_value": metric.get_latest_value().value if metric.get_latest_value() else None,
                    "statistics": metric.get_statistics()
                }
            return metrics_data
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return {}
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics"""
        summary = {
            "total_metrics": len(self.metrics),
            "collection_status": "running" if self._running else "stopped",
            "last_collection": self._last_collection,
            "metrics": {}
        }
        
        for name, metric in self.metrics.items():
            summary["metrics"][name] = {
                "type": metric.type,
                "unit": metric.unit,
                "description": metric.description,
                "value_count": len(metric.values),
                "latest_value": metric.get_latest_value().value if metric.get_latest_value() else None,
                "statistics": metric.get_statistics()
            }
        
        return summary
    
    def export_metrics(self, format: str = "json", filepath: Optional[Path] = None) -> Path:
        """Export metrics to file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.{format}"
            filepath = self.config.export.export_directory / filename
        
        if format == "json":
            self._export_json(filepath)
        elif format == "csv":
            self._export_csv(filepath)
        elif format == "prometheus":
            self._export_prometheus(filepath)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        self.logger.info(f"Exported metrics to {filepath}")
        return filepath
    
    def _export_json(self, filepath: Path):
        """Export metrics to JSON format"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        for name, metric in self.metrics.items():
            export_data["metrics"][name] = {
                "description": metric.description,
                "unit": metric.unit,
                "type": metric.type,
                "labels": metric.labels,
                "values": [asdict(mv) for mv in metric.values]
            }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def _export_csv(self, filepath: Path):
        """Export metrics to CSV format"""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(["metric_name", "timestamp", "value", "labels", "metadata"])
            
            # Write data
            for name, metric in self.metrics.items():
                for mv in metric.values:
                    labels_str = json.dumps(mv.labels) if mv.labels else ""
                    metadata_str = json.dumps(mv.metadata) if mv.metadata else ""
                    writer.writerow([name, mv.timestamp, mv.value, labels_str, metadata_str])
    
    def _export_prometheus(self, filepath: Path):
        """Export metrics to Prometheus format"""
        with open(filepath, 'w') as f:
            f.write("# HELP aas_data_modeling_engine_metrics\n")
            f.write("# TYPE aas_data_modeling_engine_metrics counter\n")
            
            for name, metric in self.metrics.items():
                # Write metric help
                f.write(f"# HELP {name} {metric.description}\n")
                f.write(f"# TYPE {name} {metric.type}\n")
                
                # Write metric values
                for mv in metric.values:
                    labels_str = ""
                    if mv.labels:
                        labels_str = "{" + ",".join([f'{k}="{v}"' for k, v in mv.labels.items()]) + "}"
                    
                    f.write(f"{name}{labels_str} {mv.value} {int(mv.timestamp * 1000)}\n")
    
    def reset_metrics(self):
        """Reset all metrics"""
        for metric in self.metrics.values():
            metric.values.clear()
        self.logger.info("All metrics reset")
    
    def __del__(self):
        """Cleanup on destruction"""
        # Note: Cannot call async methods in destructor
        # The collection task will be cleaned up by the event loop
        pass
