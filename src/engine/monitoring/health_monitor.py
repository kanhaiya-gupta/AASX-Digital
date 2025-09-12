"""
Health Monitor

Comprehensive health monitoring system for all components of the AAS Data Modeling Engine.
Provides real-time health status, failure detection, and alerting capabilities.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

from .monitoring_config import MonitoringConfig


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check definition"""
    name: str
    description: str
    check_function: Callable[[], Awaitable[Dict[str, Any]]]
    timeout: float = 10.0
    critical: bool = False
    dependencies: List[str] = field(default_factory=list)
    last_check: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    check_interval: float = 30.0  # seconds


@dataclass
class ComponentHealth:
    """Health status for a system component"""
    name: str
    status: HealthStatus
    last_check: datetime
    response_time: float
    details: Dict[str, Any]
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class HealthMonitor:
    """Centralized health monitoring system"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Health checks storage
        self.health_checks: Dict[str, HealthCheck] = {}
        self.component_health: Dict[str, ComponentHealth] = {}
        
        # Monitoring state
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        self._start_time = time.time()
        
        # Initialize default health checks
        self._init_default_health_checks()
        
        # Note: Monitoring is not automatically started to avoid asyncio issues
        # Call start_monitoring() explicitly when ready to begin monitoring
    
    def _init_default_health_checks(self):
        """Initialize default health checks for core components"""
        # Database health check
        self.add_health_check(
            name="database",
            description="Database connectivity and performance",
            check_function=self._check_database_health,
            critical=True,
            timeout=5.0
        )
        
        # Cache health check
        self.add_health_check(
            name="cache",
            description="Cache system health and performance",
            check_function=self._check_cache_health,
            critical=False,
            timeout=3.0
        )
        
        # Security system health check
        self.add_health_check(
            name="security",
            description="Security system health and functionality",
            check_function=self._check_security_health,
            critical=True,
            timeout=5.0
        )
        
        # Messaging system health check
        self.add_health_check(
            name="messaging",
            description="Event messaging system health",
            check_function=self._check_messaging_health,
            critical=False,
            timeout=3.0
        )
        
        # System resources health check
        self.add_health_check(
            name="system_resources",
            description="System resource usage and availability",
            check_function=self._check_system_resources,
            critical=False,
            timeout=5.0
        )
    
    def add_health_check(self, name: str, description: str, check_function: Callable[[], Awaitable[Dict[str, Any]]], 
                        timeout: float = 10.0, critical: bool = False, dependencies: Optional[List[str]] = None,
                        check_interval: float = 30.0) -> HealthCheck:
        """Add a new health check"""
        if name in self.health_checks:
            self.logger.warning(f"Health check {name} already exists, updating existing check")
        
        health_check = HealthCheck(
            name=name,
            description=description,
            check_function=check_function,
            timeout=timeout,
            critical=critical,
            dependencies=dependencies or [],
            check_interval=check_interval
        )
        
        self.health_checks[name] = health_check
        self.logger.debug(f"Added health check: {name}")
        return health_check
    
    def remove_health_check(self, name: str):
        """Remove a health check"""
        if name in self.health_checks:
            del self.health_checks[name]
            self.logger.debug(f"Removed health check: {name}")
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Import database components
            from ..database.database_factory import DatabaseFactory
            from ..database.connection_pool import ConnectionPoolManager
            
            # Check if database factory is accessible
            factory = DatabaseFactory()
            pools = factory.get_connection_pools()
            
            if not pools:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "No database connection pools available",
                    "details": {"pools_count": 0}
                }
            
            # Check each pool's health
            pool_health = {}
            total_connections = 0
            active_connections = 0
            
            for pool_name, pool in pools.items():
                try:
                    pool_status = pool.health_check_all_pools()
                    pool_health[pool_name] = pool_status
                    
                    # Count connections
                    for db_name, is_healthy in pool_status.items():
                        if is_healthy:
                            active_connections += 1
                        total_connections += 1
                        
                except Exception as e:
                    pool_health[pool_name] = {"error": str(e)}
            
            # Determine overall status
            if active_connections == 0:
                status = HealthStatus.UNHEALTHY
            elif active_connections < total_connections:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "status": status,
                "message": f"Database health check completed",
                "details": {
                    "total_pools": len(pools),
                    "active_connections": active_connections,
                    "total_connections": total_connections,
                    "pool_health": pool_health
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Database health check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache system health"""
        try:
            # Import cache components
            from ..caching.cache_manager import CacheManager
            
            # Check if cache manager is accessible
            cache_manager = CacheManager()
            cache_stats = cache_manager.get_stats()
            
            # Analyze cache performance
            hit_rate = cache_stats.get('hit_rate', 0)
            total_requests = cache_stats.get('total_requests', 0)
            
            if total_requests == 0:
                status = HealthStatus.UNKNOWN
            elif hit_rate < 0.5:  # Less than 50% hit rate
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "status": status,
                "message": f"Cache health check completed",
                "details": {
                    "hit_rate": hit_rate,
                    "total_requests": total_requests,
                    "cache_stats": cache_stats
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Cache health check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_security_health(self) -> Dict[str, Any]:
        """Check security system health"""
        try:
            # Import security components
            from ..security.encryption import EncryptionManager
            from ..security.security_utils import SecurityUtils
            
            # Check encryption manager
            encryption_mgr = EncryptionManager()
            encryption_status = encryption_mgr.get_status()
            
            # Check security utils
            security_utils = SecurityUtils()
            utils_status = security_utils.get_status()
            
            # Determine overall status
            if encryption_status.get('status') == 'error' or utils_status.get('status') == 'error':
                status = HealthStatus.UNHEALTHY
            elif encryption_status.get('status') == 'warning' or utils_status.get('status') == 'warning':
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "status": status,
                "message": f"Security health check completed",
                "details": {
                    "encryption": encryption_status,
                    "security_utils": utils_status
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Security health check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_messaging_health(self) -> Dict[str, Any]:
        """Check messaging system health"""
        try:
            # Import messaging components
            from ..messaging.event_bus import EventBus
            
            # Check if event bus is accessible
            event_bus = EventBus()
            bus_status = event_bus.get_status()
            
            # Determine status based on event bus health
            if bus_status.get('status') == 'error':
                status = HealthStatus.UNHEALTHY
            elif bus_status.get('status') == 'warning':
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "status": status,
                "message": f"Messaging health check completed",
                "details": {
                    "event_bus": bus_status
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Messaging health check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Determine status based on resource usage
            if cpu_percent > 90 or memory_percent > 95 or disk_percent > 95:
                status = HealthStatus.UNHEALTHY
            elif cpu_percent > 80 or memory_percent > 85 or disk_percent > 90:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "status": status,
                "message": f"System resources health check completed",
                "details": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory_percent,
                    "disk_usage": disk_percent,
                    "memory_available": memory.available,
                    "disk_available": disk.free
                }
            }
            
        except ImportError:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": "psutil not available, cannot check system resources",
                "details": {"error": "psutil not installed"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"System resources health check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def run_health_check(self, name: str) -> ComponentHealth:
        """Run a specific health check"""
        if name not in self.health_checks:
            raise ValueError(f"Health check {name} not found")
        
        health_check = self.health_checks[name]
        start_time = time.time()
        
        try:
            # Check dependencies first
            for dep in health_check.dependencies:
                if dep in self.component_health:
                    dep_health = self.component_health[dep]
                    if dep_health.status == HealthStatus.UNHEALTHY:
                        return ComponentHealth(
                            name=name,
                            status=HealthStatus.UNHEALTHY,
                            last_check=datetime.now(),
                            response_time=time.time() - start_time,
                            details={"dependency_failure": dep},
                            error_message=f"Dependency {dep} is unhealthy"
                        )
            
            # Run the health check with timeout
            try:
                result = await asyncio.wait_for(
                    health_check.check_function(),
                    timeout=health_check.timeout
                )
                
                status = result.get("status", HealthStatus.UNKNOWN)
                message = result.get("message", "Health check completed")
                details = result.get("details", {})
                error_message = result.get("error_message")
                
                # Update health check status
                health_check.last_check = datetime.now()
                health_check.last_status = status
                health_check.last_error = error_message
                
                if status == HealthStatus.HEALTHY:
                    health_check.consecutive_failures = 0
                else:
                    health_check.consecutive_failures += 1
                
            except asyncio.TimeoutError:
                status = HealthStatus.UNHEALTHY
                message = f"Health check timed out after {health_check.timeout} seconds"
                details = {"timeout": health_check.timeout}
                error_message = "Timeout"
                health_check.consecutive_failures += 1
                
            except Exception as e:
                status = HealthStatus.UNHEALTHY
                message = f"Health check failed with exception: {str(e)}"
                details = {"error": str(e)}
                error_message = str(e)
                health_check.consecutive_failures += 1
            
            # Create component health record
            component_health = ComponentHealth(
                name=name,
                status=status,
                last_check=datetime.now(),
                response_time=time.time() - start_time,
                details=details,
                error_message=error_message
            )
            
            # Store the result
            self.component_health[name] = component_health
            
            return component_health
            
        except Exception as e:
            self.logger.error(f"Error running health check {name}: {e}")
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.now(),
                response_time=time.time() - start_time,
                details={"error": str(e)},
                error_message=str(e)
            )
    
    async def run_all_health_checks(self) -> Dict[str, ComponentHealth]:
        """Run all health checks"""
        results = {}
        
        for name in self.health_checks:
            try:
                result = await self.run_health_check(name)
                results[name] = result
            except Exception as e:
                self.logger.error(f"Error running health check {name}: {e}")
        
        return results
    
    def get_overall_health(self) -> HealthStatus:
        """Get overall system health status"""
        if not self.component_health:
            return HealthStatus.UNKNOWN
        
        # Check if any critical components are unhealthy
        for name, health in self.component_health.items():
            if name in self.health_checks:
                health_check = self.health_checks[name]
                if health_check.critical and health.status == HealthStatus.UNHEALTHY:
                    return HealthStatus.UNHEALTHY
        
        # Check if any components are unhealthy
        unhealthy_count = sum(1 for h in self.component_health.values() if h.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for h in self.component_health.values() if h.status == HealthStatus.DEGRADED)
        
        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        overall_status = self.get_overall_health()
        
        summary = {
            "overall_status": overall_status.value,
            "uptime": time.time() - self._start_time,
            "total_checks": len(self.health_checks),
            "last_check": None,
            "components": {},
            "critical_components": [],
            "unhealthy_components": [],
            "degraded_components": []
        }
        
        # Analyze component health
        for name, health in self.component_health.items():
            summary["components"][name] = {
                "status": health.status.value,
                "last_check": health.last_check.isoformat() if health.last_check else None,
                "response_time": health.response_time,
                "error_message": health.error_message,
                "details": health.details
            }
            
            # Categorize components
            if name in self.health_checks and self.health_checks[name].critical:
                summary["critical_components"].append(name)
            
            if health.status == HealthStatus.UNHEALTHY:
                summary["unhealthy_components"].append(name)
            elif health.status == HealthStatus.DEGRADED:
                summary["degraded_components"].append(name)
            
            # Update last check time
            if health.last_check:
                if summary["last_check"] is None or health.last_check > datetime.fromisoformat(summary["last_check"]):
                    summary["last_check"] = health.last_check.isoformat()
        
        return summary
    
    async def get_component_health(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Get health status for a specific component.
        
        Args:
            component_name: Name of the component to check
            
        Returns:
            Component health data or None if component not found
        """
        try:
            if component_name not in self.component_health:
                # Run a health check for this component if it exists
                if component_name in self.health_checks:
                    await self.run_health_check(component_name)
                else:
                    return None
            
            health = self.component_health.get(component_name)
            if not health:
                return None
            
            return {
                "name": health.name,
                "status": health.status.value,
                "last_check": health.last_check.isoformat() if health.last_check else None,
                "response_time": health.response_time,
                "details": health.details,
                "error_message": health.error_message,
                "metadata": health.metadata
            }
            
        except Exception as e:
            self.logger.error(f"Error getting component health for {component_name}: {e}")
            return None
    
    async def start_monitoring(self):
        """Start automatic health monitoring"""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Started health monitoring")
    
    async def stop_monitoring(self):
        """Stop automatic health monitoring"""
        if not self._running:
            return
        
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
        self.logger.info("Stopped health monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                # Run all health checks
                await self.run_all_health_checks()
                
                # Check for critical failures
                overall_health = self.get_overall_health()
                if overall_health == HealthStatus.UNHEALTHY:
                    self.logger.critical("System health is UNHEALTHY - critical components are failing!")
                
                # Wait for next check interval
                await asyncio.sleep(self.config.health.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def cleanup(self):
        """Cleanup health monitor resources"""
        try:
            # Stop monitoring if running
            await self.stop_monitoring()
            
            # Clear health checks and component health
            self.health_checks.clear()
            self.component_health.clear()
            
            self.logger.info("Health monitor cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Failed to cleanup health monitor: {e}")
            raise
    
    def __del__(self):
        """Cleanup on destruction"""
        # Note: Cannot call async methods in destructor
        # The monitoring task will be cleaned up by the event loop
        pass
