"""
Real-Time Monitoring Service for Twin Registry

Provides continuous monitoring and real-time updates of twin registry metrics
including system resources, performance, and health scores.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json

from .system_monitor import SystemMonitor
from .metrics_calculator import MetricsCalculator

logger = logging.getLogger(__name__)


class RealTimeMonitor:
    """
    Real-time monitoring service for twin registry metrics.
    
    Continuously monitors system resources and updates metrics
    in real-time for active twin registries.
    """
    
    def __init__(self, db_path: str = "data/aasx_database.db", update_interval: int = 30):
        """
        Initialize the real-time monitor.
        
        Args:
            db_path: Path to the database file
            update_interval: Update interval in seconds
        """
        self.db_path = db_path
        self.update_interval = update_interval
        self.system_monitor = SystemMonitor()
        self.metrics_calculator = MetricsCalculator(db_path)
        self.monitoring_active = False
        self.monitored_registries = set()
        self.update_callbacks = []
        self.monitoring_task = None
        
    async def start_monitoring(self):
        """Start real-time monitoring."""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        try:
            logger.info("🚀 Starting real-time monitoring...")
            self.monitoring_active = True
            
            # Start the monitoring task
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Start system monitoring
            self.system_monitor.start_monitoring()
            
            logger.info("✅ Real-time monitoring started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start real-time monitoring: {e}")
            self.monitoring_active = False
            raise
    
    async def stop_monitoring(self):
        """Stop real-time monitoring."""
        if not self.monitoring_active:
            logger.warning("Monitoring is not active")
            return
        
        try:
            logger.info("🛑 Stopping real-time monitoring...")
            self.monitoring_active = False
            
            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Stop system monitoring
            self.system_monitor.stop_monitoring()
            
            logger.info("✅ Real-time monitoring stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping real-time monitoring: {e}")
    
    async def add_registry_to_monitoring(self, registry_id: str):
        """
        Add a registry to real-time monitoring.
        
        Args:
            registry_id: Registry identifier to monitor
        """
        try:
            self.monitored_registries.add(registry_id)
            logger.info(f"Added registry {registry_id} to real-time monitoring")
            
            # Immediately update metrics for this registry
            await self._update_registry_metrics(registry_id)
            
        except Exception as e:
            logger.error(f"Failed to add registry {registry_id} to monitoring: {e}")
    
    async def remove_registry_from_monitoring(self, registry_id: str):
        """
        Remove a registry from real-time monitoring.
        
        Args:
            registry_id: Registry identifier to stop monitoring
        """
        try:
            self.monitored_registries.discard(registry_id)
            logger.info(f"Removed registry {registry_id} from real-time monitoring")
            
        except Exception as e:
            logger.error(f"Failed to remove registry {registry_id} from monitoring: {e}")
    
    def add_update_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Add a callback function to be called when metrics are updated.
        
        Args:
            callback: Function to call with (registry_id, metrics_data)
        """
        self.update_callbacks.append(callback)
        logger.debug(f"Added update callback: {callback.__name__}")
    
    def remove_update_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Remove an update callback function.
        
        Args:
            callback: Function to remove
        """
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
            logger.debug(f"Removed update callback: {callback.__name__}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self.monitoring_active:
                # Update metrics for all monitored registries
                for registry_id in list(self.monitored_registries):
                    try:
                        await self._update_registry_metrics(registry_id)
                    except Exception as e:
                        logger.error(f"Failed to update metrics for registry {registry_id}: {e}")
                
                # Wait for next update cycle
                await asyncio.sleep(self.update_interval)
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            self.monitoring_active = False
    
    async def _update_registry_metrics(self, registry_id: str):
        """
        Update metrics for a specific registry.
        
        Args:
            registry_id: Registry identifier
        """
        try:
            # Get real-time system metrics
            system_metrics = self.system_monitor.get_system_overview()
            
            # Calculate real registry metrics
            registry_metrics = await self.metrics_calculator.calculate_registry_metrics(registry_id)
            
            # Combine system and registry metrics
            updated_metrics = {
                "registry_id": registry_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "health_score": registry_metrics["health_score"],
                "response_time_ms": registry_metrics["response_time_ms"],
                "uptime_percentage": registry_metrics.get("uptime_percentage", 0.0),
                "error_rate": registry_metrics["error_rate"],
                "cpu_usage_percent": system_metrics.get("cpu", {}).get("usage_percent", 0.0),
                "memory_usage_percent": system_metrics.get("memory", {}).get("percent", 0.0),
                "network_throughput_mbps": system_metrics.get("network", {}).get("throughput_mbps", 0.0),
                "storage_usage_percent": system_metrics.get("storage", {}).get("percent", 0.0),
                "transaction_count": registry_metrics["transaction_count"],
                "data_volume_mb": registry_metrics["data_volume_mb"],
                "user_interaction_count": registry_metrics["user_interaction_count"],
                "system_load": system_metrics.get("load_average", [0, 0, 0]),
                "disk_io": self.system_monitor.get_performance_metrics()
            }
            
            # Store updated metrics
            await self._store_updated_metrics(registry_id, updated_metrics)
            
            # Notify callbacks
            await self._notify_update_callbacks(registry_id, updated_metrics)
            
            logger.debug(f"Updated real-time metrics for registry: {registry_id}")
            
        except Exception as e:
            logger.error(f"Failed to update metrics for registry {registry_id}: {e}")
    
    async def _store_updated_metrics(self, registry_id: str, metrics_data: Dict[str, Any]):
        """
        Store updated metrics in the database.
        
        Args:
            registry_id: Registry identifier
            metrics_data: Updated metrics data
        """
        try:
            # Import here to avoid circular imports
            from src.twin_registry.repositories.twin_registry_metrics_repository import TwinRegistryMetricsRepository
            from src.twin_registry.models.twin_registry_metrics import TwinRegistryMetrics
            from src.shared.database.connection_manager import DatabaseConnectionManager
            from src.shared.database.base_manager import BaseDatabaseManager
            from datetime import datetime, timezone
            
            # Initialize repository
            connection_manager = DatabaseConnectionManager(Path(self.db_path))
            db_manager = BaseDatabaseManager(connection_manager)
            metrics_repo = TwinRegistryMetricsRepository(db_manager)
            
            # Create TwinRegistryMetrics model instance with correct fields
            metrics_model = TwinRegistryMetrics(
                registry_id=registry_id,
                timestamp=datetime.now(timezone.utc),
                health_score=metrics_data.get("health_score", 0.0),
                response_time_ms=metrics_data.get("response_time_ms", 0.0),
                throughput_ops_per_sec=metrics_data.get("throughput_ops_per_sec", 0.0),
                error_rate=metrics_data.get("error_rate", 0.0),
                availability_percent=metrics_data.get("availability_percent", 100.0),
                resource_usage={
                    "cpu_usage_percent": metrics_data.get("cpu_usage_percent", 0.0),
                    "memory_usage_percent": metrics_data.get("memory_usage_percent", 0.0),
                    "network_throughput_mbps": metrics_data.get("network_throughput_mbps", 0.0),
                    "storage_usage_percent": metrics_data.get("storage_usage_percent", 0.0),
                    "uptime_percentage": metrics_data.get("uptime_percentage", 0.0)
                },
                performance_indicators={
                    "transaction_count": metrics_data.get("transaction_count", 0),
                    "data_volume_mb": metrics_data.get("data_volume_mb", 0.0),
                    "user_interaction_count": metrics_data.get("user_interaction_count", 0)
                },
                quality_metrics={},
                compliance_metrics={},
                security_metrics={},
                business_metrics={},
                custom_metrics={},
                alerts=[],
                recommendations=[]
            )
            
            # Store the updated metrics using the correct method
            metrics_repo.create_metrics(metrics_model)
            
        except Exception as e:
            logger.error(f"Failed to store updated metrics for registry {registry_id}: {e}")
    
    async def _notify_update_callbacks(self, registry_id: str, metrics_data: Dict[str, Any]):
        """
        Notify all registered callbacks about metrics updates.
        
        Args:
            registry_id: Registry identifier
            metrics_data: Updated metrics data
        """
        for callback in self.update_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(registry_id, metrics_data)
                else:
                    callback(registry_id, metrics_data)
            except Exception as e:
                logger.error(f"Error in update callback {callback.__name__}: {e}")
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get current monitoring status.
        
        Returns:
            Dict containing monitoring status information
        """
        return {
            "monitoring_active": self.monitoring_active,
            "monitored_registries_count": len(self.monitored_registries),
            "monitored_registries": list(self.monitored_registries),
            "update_interval_seconds": self.update_interval,
            "update_callbacks_count": len(self.update_callbacks),
            "system_monitoring_active": self.system_monitor.is_monitoring_active()
        }
    
    async def get_live_metrics(self, registry_id: str) -> Optional[Dict[str, Any]]:
        """
        Get live metrics for a specific registry.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            Dict containing live metrics or None if not found
        """
        if registry_id not in self.monitored_registries:
            return None
        
        try:
            # Get current system metrics
            system_metrics = self.system_monitor.get_system_overview()
            
            # Get current registry metrics
            registry_metrics = await self.metrics_calculator.calculate_registry_metrics(registry_id)
            
            # Combine and return live metrics
            live_metrics = {
                "registry_id": registry_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "health_score": registry_metrics["health_score"],
                "response_time_ms": registry_metrics["response_time_ms"],
                "uptime_percentage": registry_metrics.get("uptime_percentage", 0.0),
                "error_rate": registry_metrics["error_rate"],
                "cpu_usage_percent": system_metrics.get("cpu", {}).get("usage_percent", 0.0),
                "memory_usage_percent": system_metrics.get("memory", {}).get("percent", 0.0),
                "network_throughput_mbps": system_metrics.get("network", {}).get("throughput_mbps", 0.0),
                "storage_usage_percent": system_metrics.get("storage", {}).get("percent", 0.0),
                "transaction_count": registry_metrics["transaction_count"],
                "data_volume_mb": registry_metrics["data_volume_mb"],
                "user_interaction_count": registry_metrics["user_interaction_count"],
                "system_load": system_metrics.get("load_average", [0, 0, 0]),
                "disk_io": self.system_monitor.get_performance_metrics()
            }
            
            return live_metrics
            
        except Exception as e:
            logger.error(f"Failed to get live metrics for registry {registry_id}: {e}")
            return None
    
    async def get_all_live_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get live metrics for all monitored registries.
        
        Returns:
            Dict mapping registry_id to live metrics
        """
        all_metrics = {}
        
        for registry_id in self.monitored_registries:
            metrics = await self.get_live_metrics(registry_id)
            if metrics:
                all_metrics[registry_id] = metrics
        
        return all_metrics
    
    def set_update_interval(self, interval_seconds: int):
        """
        Set the update interval for monitoring.
        
        Args:
            interval_seconds: New update interval in seconds
        """
        if interval_seconds < 5:
            logger.warning("Update interval too low, setting to minimum 5 seconds")
            interval_seconds = 5
        
        self.update_interval = interval_seconds
        logger.info(f"Updated monitoring interval to {interval_seconds} seconds")
    
    def is_monitoring_registry(self, registry_id: str) -> bool:
        """
        Check if a registry is being monitored.
        
        Args:
            registry_id: Registry identifier
            
        Returns:
            bool: True if being monitored
        """
        return registry_id in self.monitored_registries


# Global real-time monitor instance
_global_monitor = None

def get_global_monitor(db_path: str = "data/aasx_database.db") -> RealTimeMonitor:
    """
    Get or create the global real-time monitor instance.
    
    Args:
        db_path: Path to database file
        
    Returns:
        RealTimeMonitor instance
    """
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = RealTimeMonitor(db_path)
    
    return _global_monitor

async def start_global_monitoring(db_path: str = "data/aasx_database.db"):
    """Start the global real-time monitoring service."""
    monitor = get_global_monitor(db_path)
    await monitor.start_monitoring()

async def stop_global_monitoring():
    """Stop the global real-time monitoring service."""
    global _global_monitor
    
    if _global_monitor:
        await _global_monitor.stop_monitoring()
        _global_monitor = None
