"""
Module Health Monitor Service

This service continuously monitors the health and performance of all
discovered modules, providing real-time status information and alerts
when modules become unhealthy or experience performance issues.

The health monitor integrates with the engine's monitoring system to
provide comprehensive health tracking across the entire ecosystem.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict

from .models import ModuleInfo, ModuleStatus, ModuleHealth


logger = logging.getLogger(__name__)


class ModuleHealthMonitorService:
    """
    Service for monitoring the health and performance of all modules.
    
    This service provides continuous health monitoring, performance tracking,
    alerting, and integration with the engine's monitoring system.
    """
    
    def __init__(self, monitoring_interval: int = 60, alert_threshold: int = 3):
        """
        Initialize the module health monitor service.
        
        Args:
            monitoring_interval: Interval in seconds between health checks
            alert_threshold: Number of consecutive failures before alerting
        """
        self.monitoring_interval = monitoring_interval
        self.alert_threshold = alert_threshold
        self.is_monitoring = False
        self.last_monitoring_cycle = None
        
        # Health tracking
        self.module_health: Dict[str, ModuleHealth] = {}
        self.health_history: Dict[str, List[ModuleHealth]] = defaultdict(list)
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.performance_metrics: Dict[str, List[Dict]] = defaultdict(list)
        
        # Alerting
        self.alert_callbacks: List[Callable] = []
        self.active_alerts: Dict[str, Dict] = {}
        self.alert_history: List[Dict] = []
        
        # Performance thresholds
        self.performance_thresholds = {
            "response_time_ms": 1000,  # 1 second
            "error_rate": 0.05,  # 5%
            "availability": 0.95  # 95%
        }
    
    async def start_monitoring(self) -> None:
        """Start the continuous health monitoring process."""
        if self.is_monitoring:
            logger.warning("Module health monitoring is already running")
            return
        
        self.is_monitoring = True
        logger.info("Starting module health monitoring service")
        
        # Run monitoring as a background task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def _monitoring_loop(self) -> None:
        """Background task for continuous monitoring."""
        try:
            while self.is_monitoring:
                await self.perform_health_check_cycle()
                await asyncio.sleep(self.monitoring_interval)
        except Exception as e:
            logger.error(f"Error in module health monitoring service: {e}")
            self.is_monitoring = False
            raise
    
    async def stop_monitoring(self) -> None:
        """Stop the continuous health monitoring process."""
        self.is_monitoring = False
        
        # Cancel the background task if it exists
        if hasattr(self, '_monitoring_task') and self._monitoring_task:
            try:
                self._monitoring_task.cancel()
                await self._monitoring_task
            except asyncio.CancelledError:
                pass  # Expected when cancelling
            except Exception as e:
                logger.warning(f"Error cancelling monitoring task: {e}")
        
        logger.info("Stopped module health monitoring service")
    
    async def perform_health_check_cycle(self) -> None:
        """Perform a complete health check cycle for all modules."""
        logger.debug("Starting health check cycle")
        start_time = datetime.utcnow()
        
        try:
            # Get list of modules to monitor
            modules_to_check = self._get_modules_to_monitor()
            
            # Perform health checks in parallel
            health_check_tasks = []
            for module_name in modules_to_check:
                task = asyncio.create_task(self._check_module_health(module_name))
                health_check_tasks.append(task)
            
            # Wait for all health checks to complete
            if health_check_tasks:
                await asyncio.gather(*health_check_tasks, return_exceptions=True)
            
            # Process health check results
            await self._process_health_check_results()
            
            # Update monitoring cycle timestamp
            self.last_monitoring_cycle = start_time
            
            logger.debug(f"Health check cycle completed for {len(modules_to_check)} modules")
            
        except Exception as e:
            logger.error(f"Error during health check cycle: {e}")
    
    def _get_modules_to_monitor(self) -> List[str]:
        """Get list of module names to monitor."""
        # This would typically come from the discovery service
        # For now, return a static list based on what we know exists
        return [
            "twin_registry",
            "aasx",
            "ai_rag",
            "kg_neo4j",
            "federated_learning",
            "physics_modeling",
            "certificate_manager"
        ]
    
    async def _process_health_check_results(self) -> None:
        """Process the results of health checks and trigger any necessary actions."""
        try:
            # Analyze health trends
            for module_name, health_record in self.module_health.items():
                # Check for consecutive failures
                recent_history = self.health_history[module_name][-5:]  # Last 5 checks
                failure_count = sum(1 for h in recent_history if h.status == ModuleStatus.ERROR)
                
                if failure_count >= 3:
                    logger.warning(f"Module {module_name} has {failure_count} consecutive failures")
                    # Could trigger alert here
                
                # Check for performance degradation
                if health_record.response_time_ms and health_record.response_time_ms > 1000:
                    logger.warning(f"Module {module_name} has slow response time: {health_record.response_time_ms}ms")
            
            # Update overall system health
            total_modules = len(self.module_health)
            healthy_modules = sum(1 for h in self.module_health.values() if h.status == ModuleStatus.ONLINE)
            health_percentage = (healthy_modules / total_modules * 100) if total_modules > 0 else 0
            
            logger.debug(f"Overall system health: {health_percentage:.1f}% ({healthy_modules}/{total_modules} modules healthy)")
            
        except Exception as e:
            logger.error(f"Error processing health check results: {e}")
    
    async def _check_module_health(self, module_name: str) -> None:
        """Check the health of a specific module."""
        try:
            start_time = time.time()
            
            # Perform health check (placeholder implementation)
            health_status = await self._perform_module_health_check(module_name)
            
            response_time = (time.time() - start_time) * 1000
            
            # Create health record
            health_record = ModuleHealth(
                module_id=health_status.get("module_id", "unknown"),
                status=self._determine_health_status(health_status),
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                error_message=health_status.get("error_message"),
                details=health_status
            )
            
            # Update health tracking
            self.module_health[module_name] = health_record
            self.health_history[module_name].append(health_record)
            
            # Keep only recent history
            if len(self.health_history[module_name]) > 100:
                self.health_history[module_name] = self.health_history[module_name][-100:]
            
            # Update performance metrics
            self._update_performance_metrics(module_name, health_record)
            
            # Check for alerts
            await self._check_for_alerts(module_name, health_record)
            
            logger.debug(f"Health check completed for {module_name}: {health_record.status.value}")
            
        except Exception as e:
            logger.error(f"Error checking health of module {module_name}: {e}")
            # Record failed health check
            failed_health = ModuleHealth(
                module_id="unknown",
                status=ModuleStatus.ERROR,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
            self.module_health[module_name] = failed_health
            self.health_history[module_name].append(failed_health)
    
    async def _perform_module_health_check(self, module_name: str) -> Dict[str, Any]:
        """Perform actual health check on a module."""
        # This is a placeholder implementation
        # In a real system, this would:
        # 1. Check if module is accessible
        # 2. Test basic functionality
        # 3. Measure response times
        # 4. Check resource usage
        
        try:
            # Simulate health check
            import random
            import uuid
            
            # Random health status for demonstration
            health_statuses = ["healthy", "degraded", "error"]
            status = random.choices(health_statuses, weights=[0.8, 0.15, 0.05])[0]
            
            health_data = {
                "module_id": str(uuid.uuid4()),
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "uptime": random.randint(100, 10000),
                "memory_usage_mb": random.uniform(50, 500),
                "cpu_usage_percent": random.uniform(5, 80)
            }
            
            if status == "error":
                health_data["error_message"] = "Simulated error for testing"
            
            return health_data
            
        except Exception as e:
            return {
                "module_id": "unknown",
                "status": "error",
                "error_message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _determine_health_status(self, health_status: Dict[str, Any]) -> ModuleStatus:
        """Determine ModuleStatus from health check results."""
        status_str = health_status.get("status", "unknown")
        
        if status_str == "healthy":
            return ModuleStatus.ONLINE
        elif status_str == "degraded":
            return ModuleStatus.DEGRADED
        elif status_str == "error":
            return ModuleStatus.ERROR
        else:
            return ModuleStatus.UNKNOWN
    
    def _update_performance_metrics(self, module_name: str, health_record: ModuleHealth) -> None:
        """Update performance metrics for a module."""
        metrics = {
            "timestamp": health_record.last_check,
            "response_time_ms": health_record.response_time_ms,
            "status": health_record.status.value,
            "error_message": health_record.error_message
        }
        
        self.performance_metrics[module_name].append(metrics)
        
        # Keep only recent metrics
        if len(self.performance_metrics[module_name]) > 1000:
            self.performance_metrics[module_name] = self.performance_metrics[module_name][-1000:]
    
    async def _check_for_alerts(self, module_name: str, health_record: ModuleHealth) -> None:
        """Check if health status warrants an alert."""
        try:
            if health_record.status in [ModuleStatus.ERROR, ModuleStatus.DEGRADED]:
                self.failure_counts[module_name] += 1
                
                if self.failure_counts[module_name] >= self.alert_threshold:
                    await self._trigger_alert(module_name, health_record)
            else:
                # Reset failure count on success
                self.failure_counts[module_name] = 0
                
                # Clear active alert if exists
                if module_name in self.active_alerts:
                    await self._clear_alert(module_name)
                    
        except Exception as e:
            logger.error(f"Error checking for alerts for {module_name}: {e}")
    
    async def _trigger_alert(self, module_name: str, health_record: ModuleHealth) -> None:
        """Trigger an alert for a module."""
        try:
            alert = {
                "alert_id": f"{module_name}_{int(time.time())}",
                "module_name": module_name,
                "alert_type": "health_issue",
                "severity": "high" if health_record.status == ModuleStatus.ERROR else "medium",
                "message": f"Module {module_name} is experiencing health issues: {health_record.status.value}",
                "details": {
                    "status": health_record.status.value,
                    "error_message": health_record.error_message,
                    "response_time_ms": health_record.response_time_ms,
                    "failure_count": self.failure_counts[module_name]
                },
                "triggered_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            self.active_alerts[module_name] = alert
            self.alert_history.append(alert)
            
            # Keep only recent alert history
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
            
            # Call alert callbacks
            await self._notify_alert_callbacks(alert)
            
            logger.warning(f"Alert triggered for module {module_name}: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Error triggering alert for {module_name}: {e}")
    
    async def _clear_alert(self, module_name: str) -> None:
        """Clear an active alert for a module."""
        try:
            if module_name in self.active_alerts:
                alert = self.active_alerts[module_name]
                alert["is_active"] = False
                alert["cleared_at"] = datetime.utcnow().isoformat()
                
                del self.active_alerts[module_name]
                
                logger.info(f"Alert cleared for module {module_name}")
                
        except Exception as e:
            logger.error(f"Error clearing alert for {module_name}: {e}")
    
    async def _notify_alert_callbacks(self, alert: Dict) -> None:
        """Notify all registered alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def register_alert_callback(self, callback: Callable) -> None:
        """Register a callback function for alerts."""
        self.alert_callbacks.append(callback)
        logger.info(f"Registered alert callback: {callback.__name__}")
    
    def unregister_alert_callback(self, callback: Callable) -> None:
        """Unregister an alert callback function."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
            logger.info(f"Unregistered alert callback: {callback.__name__}")
    
    def get_module_health(self, module_name: str) -> Optional[ModuleHealth]:
        """Get current health status of a specific module."""
        return self.module_health.get(module_name)
    
    def get_all_module_health(self) -> Dict[str, ModuleHealth]:
        """Get health status of all modules."""
        return self.module_health.copy()
    
    def get_health_history(self, module_name: str, limit: int = 100) -> List[ModuleHealth]:
        """Get health history for a specific module."""
        history = self.health_history.get(module_name, [])
        return history[-limit:] if history else []
    
    def get_performance_metrics(self, module_name: str, limit: int = 100) -> List[Dict]:
        """Get performance metrics for a specific module."""
        metrics = self.performance_metrics.get(module_name, [])
        return metrics[-limit:] if metrics else []
    
    def get_active_alerts(self) -> Dict[str, Dict]:
        """Get all currently active alerts."""
        return self.active_alerts.copy()
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get alert history with optional limit."""
        return self.alert_history[-limit:] if self.alert_history else []
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring service status."""
        return {
            "is_monitoring": self.is_monitoring,
            "last_monitoring_cycle": self.last_monitoring_cycle,
            "monitoring_interval": self.monitoring_interval,
            "total_modules_monitored": len(self.module_health),
            "active_alerts": len(self.active_alerts),
            "total_alerts": len(self.alert_history),
            "performance_metrics_count": sum(len(metrics) for metrics in self.performance_metrics.values())
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of all module health statuses."""
        if not self.module_health:
            return {"total_modules": 0, "status_counts": {}}
        
        status_counts = defaultdict(int)
        for health in self.module_health.values():
            status_counts[health.status.value] += 1
        
        return {
            "total_modules": len(self.module_health),
            "status_counts": dict(status_counts),
            "overall_health": self._calculate_overall_health(),
            "modules_with_issues": [
                name for name, health in self.module_health.items()
                if health.status in [ModuleStatus.ERROR, ModuleStatus.DEGRADED]
            ]
        }
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall system health."""
        if not self.module_health:
            return "unknown"
        
        total_modules = len(self.module_health)
        healthy_modules = sum(
            1 for health in self.module_health.values()
            if health.status == ModuleStatus.ONLINE
        )
        
        health_percentage = healthy_modules / total_modules
        
        if health_percentage >= 0.95:
            return "excellent"
        elif health_percentage >= 0.85:
            return "good"
        elif health_percentage >= 0.70:
            return "fair"
        else:
            return "poor"
