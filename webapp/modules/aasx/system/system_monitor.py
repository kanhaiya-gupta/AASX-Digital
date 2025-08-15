"""
System Monitor Service

Provides real-time system health monitoring, resource usage tracking,
and system performance metrics for the AASX-ETL platform.
"""

import psutil
import platform
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SystemHealth:
    """System health status information"""
    status: str  # 'healthy', 'warning', 'critical'
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    temperature: Optional[float] = None
    uptime: float = 0.0
    load_average: Optional[List[float]] = None

@dataclass
class ResourceMetrics:
    """Detailed resource usage metrics"""
    timestamp: datetime
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    network: Dict[str, Any]
    processes: Dict[str, Any]

class SystemMonitor:
    """Real-time system monitoring service"""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitoring_interval = 5.0  # seconds
        self.health_history: List[SystemHealth] = []
        self.max_history_size = 1000
        self.alert_thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0
        }
    
    def start_monitoring(self) -> bool:
        """Start continuous system monitoring"""
        try:
            self.is_monitoring = True
            logger.info("🚀 System monitoring started")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start system monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop continuous system monitoring"""
        try:
            self.is_monitoring = False
            logger.info("🛑 System monitoring stopped")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to stop system monitoring: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        try:
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'hostname': platform.node(),
                'python_version': platform.python_version(),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Failed to get system info: {e}")
            return {}
    
    def get_current_health(self) -> SystemHealth:
        """Get current system health status"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network metrics
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Uptime
            uptime = time.time() - psutil.boot_time()
            
            # Load average (Linux only)
            load_average = None
            try:
                load_average = psutil.getloadavg()
            except AttributeError:
                pass  # Windows doesn't have load average
            
            # Determine health status
            status = self._determine_health_status(cpu_percent, memory_percent, disk_percent)
            
            health = SystemHealth(
                status=status,
                timestamp=datetime.now(),
                cpu_usage=cpu_percent,
                memory_usage=memory_percent,
                disk_usage=disk_percent,
                network_io=network_io,
                uptime=uptime,
                load_average=load_average
            )
            
            # Store in history
            self._store_health_record(health)
            
            return health
            
        except Exception as e:
            logger.error(f"❌ Failed to get system health: {e}")
            return self._get_error_health_status()
    
    def get_resource_metrics(self) -> ResourceMetrics:
        """Get detailed resource usage metrics"""
        try:
            # CPU details
            cpu_metrics = {
                'percent': psutil.cpu_percent(interval=1, percpu=True),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'count': psutil.cpu_count(),
                'count_logical': psutil.cpu_count(logical=True),
                'stats': psutil.cpu_stats()._asdict()
            }
            
            # Memory details
            memory = psutil.virtual_memory()
            memory_metrics = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'swap': psutil.swap_memory()._asdict()
            }
            
            # Disk details
            disk_metrics = {
                'partitions': [p._asdict() for p in psutil.disk_partitions()],
                'usage': psutil.disk_usage('/')._asdict(),
                'io_counters': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None
            }
            
            # Network details
            network_metrics = {
                'io_counters': psutil.net_io_counters()._asdict(),
                'connections': len(psutil.net_connections()),
                'interfaces': psutil.net_if_addrs()
            }
            
            # Process count
            process_metrics = {
                'total': len(psutil.pids()),
                'running': len([p for p in psutil.process_iter() if p.status() == 'running']),
                'sleeping': len([p for p in psutil.process_iter() if p.status() == 'sleeping']),
                'stopped': len([p for p in psutil.process_iter() if p.status() == 'stopped'])
            }
            
            return ResourceMetrics(
                timestamp=datetime.now(),
                cpu=cpu_metrics,
                memory=memory_metrics,
                disk=disk_metrics,
                network=network_metrics,
                processes=process_metrics
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource metrics: {e}")
            return self._get_error_resource_metrics()
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get system health history for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_records = [
                asdict(record) for record in self.health_history
                if record.timestamp > cutoff_time
            ]
            return recent_records
        except Exception as e:
            logger.error(f"❌ Failed to get health history: {e}")
            return []
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over specified hours"""
        try:
            history = self.get_health_history(hours)
            if not history:
                return {}
            
            # Calculate trends
            cpu_trend = self._calculate_trend([h['cpu_usage'] for h in history])
            memory_trend = self._calculate_trend([h['memory_usage'] for h in history])
            disk_trend = self._calculate_trend([h['disk_usage'] for h in history])
            
            # Calculate averages
            avg_cpu = sum(h['cpu_usage'] for h in history) / len(history)
            avg_memory = sum(h['memory_usage'] for h in history) / len(history)
            avg_disk = sum(h['disk_usage'] for h in history) / len(history)
            
            return {
                'trends': {
                    'cpu': cpu_trend,
                    'memory': memory_trend,
                    'disk': disk_trend
                },
                'averages': {
                    'cpu': round(avg_cpu, 2),
                    'memory': round(avg_memory, 2),
                    'disk': round(avg_disk, 2)
                },
                'period_hours': hours,
                'data_points': len(history)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance trends: {e}")
            return {}
    
    def set_alert_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """Update alert thresholds"""
        try:
            self.alert_thresholds.update(thresholds)
            logger.info(f"✅ Alert thresholds updated: {thresholds}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update alert thresholds: {e}")
            return False
    
    def get_alert_thresholds(self) -> Dict[str, float]:
        """Get current alert thresholds"""
        return self.alert_thresholds.copy()
    
    def _determine_health_status(self, cpu: float, memory: float, disk: float) -> str:
        """Determine overall system health status"""
        if (cpu >= self.alert_thresholds['cpu_critical'] or 
            memory >= self.alert_thresholds['memory_critical'] or 
            disk >= self.alert_thresholds['disk_critical']):
            return 'critical'
        elif (cpu >= self.alert_thresholds['cpu_warning'] or 
              memory >= self.alert_thresholds['memory_warning'] or 
              disk >= self.alert_thresholds['disk_warning']):
            return 'warning'
        else:
            return 'healthy'
    
    def _store_health_record(self, health: SystemHealth):
        """Store health record in history"""
        self.health_history.append(health)
        
        # Maintain history size limit
        if len(self.health_history) > self.max_history_size:
            self.health_history.pop(0)
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return 'stable'
        
        recent_avg = sum(values[-5:]) / min(5, len(values))
        older_avg = sum(values[:5]) / min(5, len(values))
        
        if recent_avg > older_avg * 1.1:
            return 'increasing'
        elif recent_avg < older_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_error_health_status(self) -> SystemHealth:
        """Return error health status when monitoring fails"""
        return SystemHealth(
            status='error',
            timestamp=datetime.now(),
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            network_io={},
            uptime=0.0
        )
    
    def _get_error_resource_metrics(self) -> ResourceMetrics:
        """Return error resource metrics when monitoring fails"""
        return ResourceMetrics(
            timestamp=datetime.now(),
            cpu={},
            memory={},
            disk={},
            network={},
            processes={}
        )

