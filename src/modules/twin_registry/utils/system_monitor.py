"""
System Resource Monitoring for Twin Registry Metrics

Provides real-time monitoring of system resources including CPU, memory, storage,
and network usage for accurate metrics calculation.
"""

import psutil
import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class SystemMonitor:
    """
    Real-time system resource monitoring for twin registry metrics.
    
    Provides accurate CPU, memory, storage, and network usage data
    instead of hardcoded values.
    """
    
    def __init__(self):
        """Initialize the system monitor."""
        self._last_network_io = None
        self._last_network_time = None
        self._monitoring_active = False
        
    def start_monitoring(self):
        """Start continuous monitoring (for future real-time updates)."""
        self._monitoring_active = True
        logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self._monitoring_active = False
        logger.info("System monitoring stopped")
    
    def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage.
        
        Returns:
            float: CPU usage percentage (0.0 to 100.0)
        """
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            logger.warning(f"Failed to get CPU usage: {e}")
            return 0.0
    
    def get_memory_usage(self) -> float:
        """
        Get current memory usage percentage.
        
        Returns:
            float: Memory usage percentage (0.0 to 100.0)
        """
        try:
            memory = psutil.virtual_memory()
            return memory.percent
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0
    
    def get_memory_details(self) -> Dict[str, Any]:
        """
        Get detailed memory information.
        
        Returns:
            Dict containing memory details
        """
        try:
            memory = psutil.virtual_memory()
            return {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent,
                "free_gb": round(memory.free / (1024**3), 2)
            }
        except Exception as e:
            logger.warning(f"Failed to get memory details: {e}")
            return {}
    
    def get_storage_usage(self, path: str = "/") -> float:
        """
        Get storage usage percentage for a given path.
        
        Args:
            path: Path to check storage usage for
            
        Returns:
            float: Storage usage percentage (0.0 to 100.0)
        """
        try:
            disk = psutil.disk_usage(path)
            return (disk.used / disk.total) * 100
        except Exception as e:
            logger.warning(f"Failed to get storage usage for {path}: {e}")
            return 0.0
    
    def get_storage_details(self, path: str = "/") -> Dict[str, Any]:
        """
        Get detailed storage information.
        
        Args:
            path: Path to check storage usage for
            
        Returns:
            Dict containing storage details
        """
        try:
            disk = psutil.disk_usage(path)
            return {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": (disk.used / disk.total) * 100
            }
        except Exception as e:
            logger.warning(f"Failed to get storage details for {path}: {e}")
            return {}
    
    def get_network_throughput(self) -> float:
        """
        Get current network throughput in Mbps.
        
        Returns:
            float: Network throughput in Mbps
        """
        try:
            current_io = psutil.net_io_counters()
            current_time = time.time()
            
            if self._last_network_io and self._last_network_time:
                # Calculate throughput based on difference
                time_diff = current_time - self._last_network_time
                bytes_diff = (current_io.bytes_sent + current_io.bytes_recv) - \
                           (self._last_network_io.bytes_sent + self._last_network_io.bytes_recv)
                
                # Convert to Mbps
                throughput_mbps = (bytes_diff * 8) / (time_diff * 1024 * 1024)
            else:
                throughput_mbps = 0.0
            
            # Update for next calculation
            self._last_network_io = current_io
            self._last_network_time = current_time
            
            return max(0.0, throughput_mbps)
            
        except Exception as e:
            logger.warning(f"Failed to get network throughput: {e}")
            return 0.0
    
    def get_network_details(self) -> Dict[str, Any]:
        """
        Get detailed network information.
        
        Returns:
            Dict containing network details
        """
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "throughput_mbps": self.get_network_throughput()
            }
        except Exception as e:
            logger.warning(f"Failed to get network details: {e}")
            return {}
    
    def get_process_metrics(self, process_name: str = None) -> Dict[str, Any]:
        """
        Get metrics for specific process or current process.
        
        Args:
            process_name: Name of process to monitor (None for current)
            
        Returns:
            Dict containing process metrics
        """
        try:
            if process_name:
                # Find process by name
                processes = []
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        processes.append(proc)
                
                if not processes:
                    return {}
                
                # Use first matching process
                process = processes[0]
            else:
                # Use current process
                process = psutil.Process()
            
            with process.oneshot():
                return {
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "memory_mb": round(process.memory_info().rss / (1024**2), 2),
                    "num_threads": process.num_threads(),
                    "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 0,
                    "status": process.status()
                }
                
        except Exception as e:
            logger.warning(f"Failed to get process metrics: {e}")
            return {}
    
    def get_system_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive system overview.
        
        Returns:
            Dict containing all system metrics
        """
        try:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cpu": {
                    "usage_percent": self.get_cpu_usage(),
                    "count": psutil.cpu_count(),
                    "freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else 0
                },
                "memory": self.get_memory_details(),
                "storage": self.get_storage_details(),
                "network": self.get_network_details(),
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            logger.error(f"Failed to get system overview: {e}")
            return {}
    
    def get_database_storage_usage(self, db_path: str = "data/aasx_database.db") -> Dict[str, Any]:
        """
        Get specific database storage usage.
        
        Args:
            db_path: Path to database file
            
        Returns:
            Dict containing database storage details
        """
        try:
            db_file = Path(db_path)
            if not db_file.exists():
                return {"error": "Database file not found"}
            
            # Get database file size
            db_size_bytes = db_file.stat().st_size
            db_size_mb = round(db_size_bytes / (1024**2), 2)
            
            # Get directory storage usage
            db_dir = db_file.parent
            storage_details = self.get_storage_details(str(db_dir))
            
            return {
                "database_size_mb": db_size_mb,
                "database_size_bytes": db_size_bytes,
                "directory_path": str(db_dir),
                "directory_storage": storage_details
            }
            
        except Exception as e:
            logger.warning(f"Failed to get database storage usage: {e}")
            return {}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance-related metrics.
        
        Returns:
            Dict containing performance metrics
        """
        try:
            # Get system load averages
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            # Get disk I/O statistics
            disk_io = psutil.disk_io_counters()
            
            return {
                "load_average_1min": load_avg[0] if len(load_avg) > 0 else 0,
                "load_average_5min": load_avg[1] if len(load_avg) > 1 else 0,
                "load_average_15min": load_avg[2] if len(load_avg) > 2 else 0,
                "disk_read_mb": round(disk_io.read_bytes / (1024**2), 2),
                "disk_write_mb": round(disk_io.write_bytes / (1024**2), 2),
                "disk_read_count": disk_io.read_count,
                "disk_write_count": disk_io.write_count
            }
            
        except Exception as e:
            logger.warning(f"Failed to get performance metrics: {e}")
            return {}
    
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is currently active."""
        return self._monitoring_active


# Convenience function for quick metrics
def get_system_metrics() -> Dict[str, Any]:
    """
    Quick function to get basic system metrics.
    
    Returns:
        Dict containing basic system metrics
    """
    monitor = SystemMonitor()
    return {
        "cpu_usage_percent": monitor.get_cpu_usage(),
        "memory_usage_percent": monitor.get_memory_usage(),
        "storage_usage_percent": monitor.get_storage_usage(),
        "network_throughput_mbps": monitor.get_network_throughput()
    }
