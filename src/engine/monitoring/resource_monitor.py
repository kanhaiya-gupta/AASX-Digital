"""
Resource Monitor

Comprehensive system resource monitoring for the AAS Data Modeling Engine.
Monitors CPU, memory, disk, network, and application-specific resource usage.
"""

import time
import asyncio
import psutil
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

from .monitoring_config import MonitoringConfig


@dataclass
class ResourceUsage:
    """Resource usage measurement"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_available: int
    memory_total: int
    disk_percent: float
    disk_used: int
    disk_available: int
    disk_total: int
    network_bytes_sent: int
    network_bytes_recv: int
    network_packets_sent: int
    network_packets_recv: int


@dataclass
class DatabaseResourceUsage:
    """Database-specific resource usage"""
    timestamp: float
    active_connections: int
    total_connections: int
    connection_pool_size: int
    query_queue_length: int
    active_transactions: int
    database_size: int
    cache_hit_rate: float


@dataclass
class CacheResourceUsage:
    """Cache-specific resource usage"""
    timestamp: float
    cache_size: int
    cache_entries: int
    memory_usage: int
    hit_rate: float
    miss_rate: float
    eviction_count: int
    expiration_count: int


class ResourceMonitor:
    """Comprehensive system resource monitoring system"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Resource data storage
        self.resource_history: List[ResourceUsage] = []
        self.database_resource_history: List[DatabaseResourceUsage] = []
        self.cache_resource_history: List[CacheResourceUsage] = []
        
        # Monitoring state
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        self._start_time = time.time()
        
        # Resource thresholds
        self._cpu_threshold = 80.0
        self._memory_threshold = 85.0
        self._disk_threshold = 90.0
        
        # Custom resource collectors
        self._custom_collectors: Dict[str, Callable] = {}
        
        # Note: Monitoring is not automatically started to avoid asyncio issues
        # Call start_monitoring() explicitly when ready to begin monitoring
    
    def add_custom_collector(self, name: str, collector_func: Callable[[], Dict[str, Any]]):
        """Add a custom resource collector"""
        self._custom_collectors[name] = collector_func
        self.logger.debug(f"Added custom resource collector: {name}")
    
    async def collect_system_resources(self) -> ResourceUsage:
        """Collect current system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network usage
            network = psutil.net_io_counters()
            
            # Create resource usage record
            resource_usage = ResourceUsage(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_available=memory.available,
                memory_total=memory.total,
                disk_percent=(disk.used / disk.total) * 100,
                disk_used=disk.used,
                disk_available=disk.free,
                disk_total=disk.total,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                network_packets_sent=network.packets_sent,
                network_packets_recv=network.packets_recv
            )
            
            # Store in history
            self.resource_history.append(resource_usage)
            
            # Cleanup old history if needed
            self._cleanup_resource_history()
            
            # Check thresholds and log warnings
            self._check_resource_thresholds(resource_usage)
            
            return resource_usage
            
        except Exception as e:
            self.logger.error(f"Error collecting system resources: {e}")
            raise
    
    async def collect_database_resources(self) -> Optional[DatabaseResourceUsage]:
        """Collect database-specific resource usage"""
        if not self.config.resources.monitor_database_connections:
            return None
        
        try:
            # Import database components
            from ..database.database_factory import DatabaseFactory
            from ..database.connection_pool import ConnectionPoolManager
            
            # Get database factory and connection pools
            factory = DatabaseFactory()
            pools = factory.get_connection_pools()
            
            if not pools:
                return None
            
            # Aggregate connection information
            total_connections = 0
            active_connections = 0
            pool_size = 0
            
            for pool_name, pool in pools.items():
                try:
                    pool_status = pool.health_check_all_pools()
                    for db_name, is_healthy in pool_status.items():
                        total_connections += 1
                        if is_healthy:
                            active_connections += 1
                    
                    # Get pool size if available
                    if hasattr(pool, 'get_pool_size'):
                        pool_size += pool.get_pool_size()
                    
                except Exception as e:
                    self.logger.warning(f"Error checking pool {pool_name}: {e}")
            
            # Create database resource usage record
            db_usage = DatabaseResourceUsage(
                timestamp=time.time(),
                active_connections=active_connections,
                total_connections=total_connections,
                connection_pool_size=pool_size,
                query_queue_length=0,  # Placeholder - implement if available
                active_transactions=0,  # Placeholder - implement if available
                database_size=0,  # Placeholder - implement if available
                cache_hit_rate=0.0  # Placeholder - implement if available
            )
            
            # Store in history
            self.database_resource_history.append(db_usage)
            
            # Cleanup old history
            self._cleanup_database_history()
            
            return db_usage
            
        except Exception as e:
            self.logger.error(f"Error collecting database resources: {e}")
            return None
    
    async def collect_cache_resources(self) -> Optional[CacheResourceUsage]:
        """Collect cache-specific resource usage"""
        if not self.config.resources.monitor_cache_usage:
            return None
        
        try:
            # Import cache components
            from ..caching.cache_manager import CacheManager
            
            # Get cache manager and stats
            cache_manager = CacheManager()
            cache_stats = cache_manager.get_stats()
            
            # Extract cache metrics
            cache_usage = CacheResourceUsage(
                timestamp=time.time(),
                cache_size=cache_stats.get('cache_size', 0),
                cache_entries=cache_stats.get('total_entries', 0),
                memory_usage=cache_stats.get('memory_usage', 0),
                hit_rate=cache_stats.get('hit_rate', 0.0),
                miss_rate=1.0 - cache_stats.get('hit_rate', 0.0),
                eviction_count=cache_stats.get('eviction_count', 0),
                expiration_count=cache_stats.get('expiration_count', 0)
            )
            
            # Store in history
            self.cache_resource_history.append(cache_usage)
            
            # Cleanup old history
            self._cleanup_cache_history()
            
            return cache_usage
            
        except Exception as e:
            self.logger.error(f"Error collecting cache resources: {e}")
            return None
    
    async def collect_custom_resources(self) -> Dict[str, Any]:
        """Collect custom resource metrics"""
        custom_metrics = {}
        
        for name, collector_func in self._custom_collectors.items():
            try:
                metrics = collector_func()
                custom_metrics[name] = {
                    "timestamp": time.time(),
                    "metrics": metrics
                }
            except Exception as e:
                self.logger.error(f"Error collecting custom resource {name}: {e}")
                custom_metrics[name] = {
                    "timestamp": time.time(),
                    "error": str(e)
                }
        
        return custom_metrics
    
    async def collect_all_resources(self) -> Dict[str, Any]:
        """Collect all resource metrics"""
        resources = {
            "timestamp": time.time(),
            "system": None,
            "database": None,
            "cache": None,
            "custom": {}
        }
        
        try:
            # Collect system resources
            if self.config.resources.monitor_cpu or self.config.resources.monitor_memory or self.config.resources.monitor_disk or self.config.resources.monitor_network:
                resources["system"] = await self.collect_system_resources()
            
            # Collect database resources
            if self.config.resources.monitor_database_connections:
                resources["database"] = await self.collect_database_resources()
            
            # Collect cache resources
            if self.config.resources.monitor_cache_usage:
                resources["cache"] = await self.collect_cache_resources()
            
            # Collect custom resources
            if self._custom_collectors:
                resources["custom"] = await self.collect_custom_resources()
            
        except Exception as e:
            self.logger.error(f"Error collecting resources: {e}")
        
        return resources
    
    def _cleanup_resource_history(self):
        """Clean up old resource history"""
        if len(self.resource_history) > 1000:  # Keep last 1000 measurements
            self.resource_history = self.resource_history[-1000:]
    
    def _cleanup_database_history(self):
        """Clean up old database resource history"""
        if len(self.database_resource_history) > 500:  # Keep last 500 measurements
            self.database_resource_history = self.database_resource_history[-500:]
    
    def _cleanup_cache_history(self):
        """Clean up old cache resource history"""
        if len(self.cache_resource_history) > 500:  # Keep last 500 measurements
            self.cache_resource_history = self.cache_resource_history[-500:]
    
    def _check_resource_thresholds(self, resource_usage: ResourceUsage):
        """Check resource usage against thresholds and log warnings"""
        warnings = []
        
        if resource_usage.cpu_percent > self._cpu_threshold:
            warnings.append(f"CPU usage high: {resource_usage.cpu_percent:.1f}%")
        
        if resource_usage.memory_percent > self._memory_threshold:
            warnings.append(f"Memory usage high: {resource_usage.memory_percent:.1f}%")
        
        if resource_usage.disk_percent > self._disk_threshold:
            warnings.append(f"Disk usage high: {resource_usage.disk_percent:.1f}%")
        
        for warning in warnings:
            self.logger.warning(warning)
    
    def get_resource_summary(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get resource usage summary for the specified time window"""
        cutoff_time = time.time() - (window_minutes * 60)
        
        # Filter recent system resources
        recent_resources = [r for r in self.resource_history if r.timestamp >= cutoff_time]
        
        if not recent_resources:
            return {"error": "No resource data available for the specified time window"}
        
        # Calculate averages
        avg_cpu = sum(r.cpu_percent for r in recent_resources) / len(recent_resources)
        avg_memory = sum(r.memory_percent for r in recent_resources) / len(recent_resources)
        avg_disk = sum(r.disk_percent for r in recent_resources) / len(recent_resources)
        
        # Find peaks
        max_cpu = max(r.cpu_percent for r in recent_resources)
        max_memory = max(r.memory_percent for r in recent_resources)
        max_disk = max(r.disk_percent for r in recent_resources)
        
        # Calculate network totals
        total_bytes_sent = sum(r.network_bytes_sent for r in recent_resources)
        total_bytes_recv = sum(r.network_bytes_recv for r in recent_resources)
        
        summary = {
            "time_window_minutes": window_minutes,
            "measurements_count": len(recent_resources),
            "system_resources": {
                "cpu": {
                    "average": avg_cpu,
                    "maximum": max_cpu,
                    "current": recent_resources[-1].cpu_percent if recent_resources else 0
                },
                "memory": {
                    "average": avg_memory,
                    "maximum": max_memory,
                    "current": recent_resources[-1].memory_percent if recent_resources else 0,
                    "available_gb": recent_resources[-1].memory_available / (1024**3) if recent_resources else 0
                },
                "disk": {
                    "average": avg_disk,
                    "maximum": max_disk,
                    "current": recent_resources[-1].disk_percent if recent_resources else 0,
                    "available_gb": recent_resources[-1].disk_available / (1024**3) if recent_resources else 0
                },
                "network": {
                    "total_bytes_sent_mb": total_bytes_sent / (1024**2),
                    "total_bytes_received_mb": total_bytes_recv / (1024**2)
                }
            }
        }
        
        # Add database resources if available
        recent_db_resources = [r for r in self.database_resource_history if r.timestamp >= cutoff_time]
        if recent_db_resources:
            avg_active_connections = sum(r.active_connections for r in recent_db_resources) / len(recent_db_resources)
            max_active_connections = max(r.active_connections for r in recent_db_resources)
            
            summary["database_resources"] = {
                "active_connections": {
                    "average": avg_active_connections,
                    "maximum": max_active_connections,
                    "current": recent_db_resources[-1].active_connections if recent_db_resources else 0
                }
            }
        
        # Add cache resources if available
        recent_cache_resources = [r for r in self.cache_resource_history if r.timestamp >= cutoff_time]
        if recent_cache_resources:
            avg_hit_rate = sum(r.hit_rate for r in recent_cache_resources) / len(recent_cache_resources)
            
            summary["cache_resources"] = {
                "hit_rate": {
                    "average": avg_hit_rate,
                    "current": recent_cache_resources[-1].hit_rate if recent_cache_resources else 0
                },
                "cache_entries": recent_cache_resources[-1].cache_entries if recent_cache_resources else 0
            }
        
        return summary
    
    def get_resource_trends(self, metric: str, window_minutes: int = 60) -> Dict[str, Any]:
        """Get resource usage trends for a specific metric"""
        cutoff_time = time.time() - (window_minutes * 60)
        
        if metric == "cpu":
            data = [(r.timestamp, r.cpu_percent) for r in self.resource_history if r.timestamp >= cutoff_time]
        elif metric == "memory":
            data = [(r.timestamp, r.memory_percent) for r in self.resource_history if r.timestamp >= cutoff_time]
        elif metric == "disk":
            data = [(r.timestamp, r.disk_percent) for r in self.resource_history if r.timestamp >= cutoff_time]
        elif metric == "network_sent":
            data = [(r.timestamp, r.network_bytes_sent) for r in self.resource_history if r.timestamp >= cutoff_time]
        elif metric == "network_recv":
            data = [(r.timestamp, r.network_bytes_recv) for r in self.resource_history if r.timestamp >= cutoff_time]
        else:
            return {"error": f"Unknown metric: {metric}"}
        
        if not data:
            return {"error": f"No data available for {metric}"}
        
        # Sort by timestamp
        data.sort(key=lambda x: x[0])
        
        # Calculate trend (simple linear regression)
        n = len(data)
        sum_x = sum(x[0] for x in data)
        sum_y = sum(x[1] for x in data)
        sum_xy = sum(x[0] * x[1] for x in data)
        sum_x2 = sum(x[0] ** 2 for x in data)
        
        if n * sum_x2 - sum_x ** 2 == 0:
            slope = 0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Determine trend direction
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "metric": metric,
            "time_window_minutes": window_minutes,
            "data_points": n,
            "trend": trend,
            "slope": slope,
            "values": data[-10:] if len(data) > 10 else data  # Last 10 values
        }
    
    def set_thresholds(self, cpu: Optional[float] = None, memory: Optional[float] = None, disk: Optional[float] = None):
        """Set resource usage thresholds"""
        if cpu is not None:
            self._cpu_threshold = cpu
            self.logger.info(f"CPU threshold set to {cpu}%")
        
        if memory is not None:
            self._memory_threshold = memory
            self.logger.info(f"Memory threshold set to {memory}%")
        
        if disk is not None:
            self._disk_threshold = disk
            self.logger.info(f"Disk threshold set to {disk}%")
    
    def start_monitoring(self):
        """Start automatic resource monitoring"""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Started resource monitoring")
    
    def stop_monitoring(self):
        """Stop automatic resource monitoring"""
        if not self._running:
            return
        
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
        self.logger.info("Stopped resource monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                # Collect all resources
                await self.collect_all_resources()
                
                # Wait for next collection interval
                await asyncio.sleep(self.config.resources.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in resource monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def export_resource_data(self, format: str = "json", filepath: Optional[Path] = None) -> Path:
        """Export resource data to file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resources_{timestamp}.{format}"
            filepath = self.config.export.export_directory / filename
        
        if format == "json":
            self._export_json(filepath)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        self.logger.info(f"Exported resource data to {filepath}")
        return filepath
    
    def _export_json(self, filepath: Path):
        """Export resource data to JSON format"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "resource_summary": self.get_resource_summary(),
            "system_resources": [self._resource_usage_to_dict(r) for r in self.resource_history[-100:]],  # Last 100
            "database_resources": [self._db_usage_to_dict(r) for r in self.database_resource_history[-100:]],
            "cache_resources": [self._cache_usage_to_dict(r) for r in self.cache_resource_history[-100:]]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def _resource_usage_to_dict(self, usage: ResourceUsage) -> Dict[str, Any]:
        """Convert ResourceUsage to dictionary"""
        return {
            "timestamp": usage.timestamp,
            "cpu_percent": usage.cpu_percent,
            "memory_percent": usage.memory_percent,
            "memory_used_gb": usage.memory_used / (1024**3),
            "memory_available_gb": usage.memory_available / (1024**3),
            "disk_percent": usage.disk_percent,
            "disk_used_gb": usage.disk_used / (1024**3),
            "disk_available_gb": usage.disk_available / (1024**3),
            "network_bytes_sent_mb": usage.network_bytes_sent / (1024**2),
            "network_bytes_recv_mb": usage.network_bytes_recv / (1024**2)
        }
    
    def _db_usage_to_dict(self, usage: DatabaseResourceUsage) -> Dict[str, Any]:
        """Convert DatabaseResourceUsage to dictionary"""
        return {
            "timestamp": usage.timestamp,
            "active_connections": usage.active_connections,
            "total_connections": usage.total_connections,
            "connection_pool_size": usage.connection_pool_size,
            "query_queue_length": usage.query_queue_length,
            "active_transactions": usage.active_transactions,
            "database_size_gb": usage.database_size / (1024**3),
            "cache_hit_rate": usage.cache_hit_rate
        }
    
    def _cache_usage_to_dict(self, usage: CacheResourceUsage) -> Dict[str, Any]:
        """Convert CacheResourceUsage to dictionary"""
        return {
            "timestamp": usage.timestamp,
            "cache_size_mb": usage.cache_size / (1024**2),
            "cache_entries": usage.cache_entries,
            "memory_usage_mb": usage.memory_usage / (1024**2),
            "hit_rate": usage.hit_rate,
            "miss_rate": usage.miss_rate,
            "eviction_count": usage.eviction_count,
            "expiration_count": usage.expiration_count
        }
    
    def reset_resource_data(self):
        """Reset all resource data"""
        self.resource_history.clear()
        self.database_resource_history.clear()
        self.cache_resource_history.clear()
        self.logger.info("All resource data reset")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_monitoring()
