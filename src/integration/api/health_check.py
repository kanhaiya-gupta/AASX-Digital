"""
Health Check Service

This module provides comprehensive health monitoring and status checking
for the AAS Data Modeling Engine API, including system health, component
status, and performance metrics.

The health check service handles:
- System health monitoring
- Component status checking
- Performance metrics collection
- Health endpoint management
- Alerting and notifications
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(str, Enum):
    """Component types for health checking."""
    DATABASE = "database"
    WORKFLOW_ENGINE = "workflow_engine"
    MODULE_ORCHESTRATOR = "module_orchestrator"
    MODULE_REGISTRY = "module_registry"
    API_GATEWAY = "api_gateway"
    RATE_LIMITER = "rate_limiter"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"


@dataclass
class HealthCheck:
    """Represents a health check result."""
    
    name: str
    status: HealthStatus
    component_type: ComponentType
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "status": self.status.value,
            "component_type": self.component_type.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "response_time_ms": self.response_time_ms,
            "error": self.error
        }


@dataclass
class ComponentHealth:
    """Represents the health status of a component."""
    
    name: str
    component_type: ComponentType
    status: HealthStatus
    last_check: datetime
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    total_checks: int = 0
    total_failures: int = 0
    average_response_time: float = 0.0
    health_checks: List[HealthCheck] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "last_check": self.last_check.isoformat(),
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "consecutive_failures": self.consecutive_failures,
            "total_checks": self.total_checks,
            "total_failures": self.total_failures,
            "average_response_time": self.average_response_time,
            "success_rate": (self.total_checks - self.total_failures) / max(self.total_checks, 1) * 100,
            "recent_health_checks": [check.to_dict() for check in self.health_checks[-5:]]  # Last 5 checks
        }


class HealthCheckService:
    """
    Comprehensive health check service.
    
    Monitors system health, component status, and provides
    health endpoints for external monitoring systems.
    """
    
    def __init__(self):
        """Initialize the health check service."""
        self.components: Dict[str, ComponentHealth] = {}
        self.health_checks: Dict[str, Callable] = {}
        self.is_running = False
        self.check_interval = 30  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Performance thresholds
        self.thresholds = {
            "response_time_warning": 1000,  # 1 second
            "response_time_critical": 5000,  # 5 seconds
            "consecutive_failures_warning": 3,
            "consecutive_failures_critical": 10
        }
        
        # Initialize default components
        self._setup_default_components()
        
        logger.info("Health Check service initialized")
    
    def _setup_default_components(self) -> None:
        """Setup default system components for health monitoring."""
        now = datetime.utcnow()
        
        # System component
        system_component = ComponentHealth(
            name="system",
            component_type=ComponentType.SYSTEM,
            status=HealthStatus.HEALTHY,
            last_check=now
        )
        
        # API Gateway component
        api_gateway_component = ComponentHealth(
            name="api_gateway",
            component_type=ComponentType.API_GATEWAY,
            status=HealthStatus.HEALTHY,
            last_check=now
        )
        
        # Workflow Engine component
        workflow_engine_component = ComponentHealth(
            name="workflow_engine",
            component_type=ComponentType.WORKFLOW_ENGINE,
            status=HealthStatus.HEALTHY,
            last_check=now
        )
        
        # Module Orchestrator component
        module_orchestrator_component = ComponentHealth(
            name="module_orchestrator",
            component_type=ComponentType.MODULE_ORCHESTRATOR,
            status=HealthStatus.HEALTHY,
            last_check=now
        )
        
        # Module Registry component
        module_registry_component = ComponentHealth(
            name="module_registry",
            component_type=ComponentType.MODULE_REGISTRY,
            status=HealthStatus.HEALTHY,
            last_check=now
        )
        
        # Rate Limiter component
        rate_limiter_component = ComponentHealth(
            name="rate_limiter",
            component_type=ComponentType.RATE_LIMITER,
            status=HealthStatus.HEALTHY,
            last_check=now
        )
        
        # Add components
        self.add_component(system_component)
        self.add_component(api_gateway_component)
        self.add_component(workflow_engine_component)
        self.add_component(module_orchestrator_component)
        self.add_component(module_registry_component)
        self.add_component(rate_limiter_component)
        
        logger.info("Default health check components configured")
    
    def add_component(self, component: ComponentHealth) -> None:
        """Add a new component for health monitoring."""
        self.components[component.name] = component
        logger.info(f"Health check component added: {component.name}")
    
    def remove_component(self, name: str) -> bool:
        """Remove a component from health monitoring."""
        if name in self.components:
            del self.components[name]
            logger.info(f"Health check component removed: {name}")
            return True
        return False
    
    def get_component(self, name: str) -> Optional[ComponentHealth]:
        """Get a component by name."""
        return self.components.get(name)
    
    def register_health_check(self, component_name: str, check_function: Callable) -> None:
        """Register a health check function for a component."""
        self.health_checks[component_name] = check_function
        logger.info(f"Health check function registered for component: {component_name}")
    
    def unregister_health_check(self, component_name: str) -> bool:
        """Unregister a health check function."""
        if component_name in self.health_checks:
            del self.health_checks[component_name]
            logger.info(f"Health check function unregistered for component: {component_name}")
            return True
        return False
    
    async def start_health_monitoring(self) -> None:
        """Start the health monitoring service."""
        if self.is_running:
            logger.warning("Health monitoring is already running")
            return
        
        self.is_running = True
        self.health_check_task = asyncio.create_task(self._health_monitoring_loop())
        logger.info("Health monitoring started")
    
    async def stop_health_monitoring(self) -> None:
        """Stop the health monitoring service."""
        if not self.is_running:
            logger.warning("Health monitoring is not running")
            return
        
        self.is_running = False
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health monitoring stopped")
    
    async def _health_monitoring_loop(self) -> None:
        """Main health monitoring loop."""
        logger.info("Starting health monitoring loop")
        
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                logger.info("Health monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info("Health monitoring loop stopped")
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks for all components."""
        for component_name, component in self.components.items():
            try:
                await self._check_component_health(component_name, component)
            except Exception as e:
                logger.error(f"Error checking health for component {component_name}: {e}")
                await self._update_component_status(component_name, HealthStatus.UNKNOWN, str(e))
    
    async def _check_component_health(self, component_name: str, component: ComponentHealth) -> None:
        """Check the health of a specific component."""
        start_time = time.time()
        
        try:
            # Check if there's a registered health check function
            if component_name in self.health_checks:
                check_function = self.health_checks[component_name]
                result = await check_function()
                
                if isinstance(result, dict):
                    status = result.get("status", HealthStatus.UNKNOWN)
                    message = result.get("message", "")
                    details = result.get("details", {})
                    error = result.get("error")
                else:
                    status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                    message = "Health check completed"
                    details = {}
                    error = None
            else:
                # Use default health check logic
                status, message, details, error = await self._default_health_check(component_name)
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Create health check result
            health_check = HealthCheck(
                name=component_name,
                status=status,
                component_type=component.component_type,
                message=message,
                details=details,
                response_time_ms=response_time,
                error=error
            )
            
            # Update component health
            await self._update_component_health(component_name, health_check)
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_msg = f"Health check failed: {str(e)}"
            
            health_check = HealthCheck(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                component_type=component.component_type,
                message=error_msg,
                error=error_msg,
                response_time_ms=response_time
            )
            
            await self._update_component_health(component_name, health_check)
    
    async def _default_health_check(self, component_name: str) -> tuple[HealthStatus, str, Dict[str, Any], Optional[str]]:
        """Default health check logic for components."""
        # This is a placeholder - in a real implementation, you would have
        # specific health check logic for each component type
        return HealthStatus.HEALTHY, "Component is healthy", {}, None
    
    async def _update_component_health(self, component_name: str, health_check: HealthCheck) -> None:
        """Update component health based on health check result."""
        component = self.components[component_name]
        
        # Update component statistics
        component.total_checks += 1
        component.last_check = datetime.utcnow()
        
        # Update response time average
        if health_check.response_time_ms is not None:
            total_time = component.average_response_time * (component.total_checks - 1)
            component.average_response_time = (total_time + health_check.response_time_ms) / component.total_checks
        
        # Update health status
        if health_check.status == HealthStatus.HEALTHY:
            component.status = HealthStatus.HEALTHY
            component.last_success = datetime.utcnow()
            component.consecutive_failures = 0
        else:
            component.total_failures += 1
            component.consecutive_failures += 1
            component.last_failure = datetime.utcnow()
            
            # Determine status based on consecutive failures
            if component.consecutive_failures >= self.thresholds["consecutive_failures_critical"]:
                component.status = HealthStatus.UNHEALTHY
            elif component.consecutive_failures >= self.thresholds["consecutive_failures_warning"]:
                component.status = HealthStatus.DEGRADED
        
        # Add health check to history
        component.health_checks.append(health_check)
        
        # Keep only recent health checks (last 100)
        if len(component.health_checks) > 100:
            component.health_checks = component.health_checks[-100:]
        
        logger.debug(f"Component {component_name} health updated: {health_check.status.value}")
    
    async def _update_component_status(self, component_name: str, status: HealthStatus, message: str) -> None:
        """Update component status without running health checks."""
        if component_name in self.components:
            component = self.components[component_name]
            component.status = status
            component.last_check = datetime.utcnow()
            
            if status == HealthStatus.HEALTHY:
                component.last_success = datetime.utcnow()
            else:
                component.last_failure = datetime.utcnow()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of overall system health."""
        total_components = len(self.components)
        healthy_components = sum(1 for c in self.components.values() if c.status == HealthStatus.HEALTHY)
        degraded_components = sum(1 for c in self.components.values() if c.status == HealthStatus.DEGRADED)
        unhealthy_components = sum(1 for c in self.components.values() if c.status == HealthStatus.UNHEALTHY)
        
        # Calculate overall health percentage
        health_percentage = (healthy_components / total_components) * 100 if total_components > 0 else 0
        
        # Determine overall status
        if health_percentage >= 90:
            overall_status = HealthStatus.HEALTHY
        elif health_percentage >= 70:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        return {
            "status": overall_status.value,
            "health_percentage": round(health_percentage, 1),
            "total_components": total_components,
            "healthy_components": healthy_components,
            "degraded_components": degraded_components,
            "unhealthy_components": unhealthy_components,
            "timestamp": datetime.utcnow().isoformat(),
            "monitoring_active": self.is_running
        }
    
    def get_component_health(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed health information for a specific component."""
        component = self.get_component(component_name)
        if not component:
            return None
        
        return component.to_dict()
    
    def get_all_components_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health information for all components."""
        return {
            name: component.to_dict()
            for name, component in self.components.items()
        }
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get comprehensive health metrics."""
        metrics = {
            "overall_health": self.get_health_summary(),
            "components": self.get_all_components_health(),
            "thresholds": self.thresholds,
            "monitoring_config": {
                "check_interval_seconds": self.check_interval,
                "is_running": self.is_running
            }
        }
        
        # Add performance metrics
        total_response_time = 0
        total_checks = 0
        
        for component in self.components.values():
            if component.average_response_time > 0:
                total_response_time += component.average_response_time
                total_checks += 1
        
        if total_checks > 0:
            metrics["performance"] = {
                "average_response_time_ms": round(total_response_time / total_checks, 2),
                "total_health_checks": sum(c.total_checks for c in self.components.values()),
                "total_failures": sum(c.total_failures for c in self.components.values())
            }
        
        return metrics
    
    def set_threshold(self, threshold_name: str, value: Union[int, float]) -> None:
        """Set a health check threshold."""
        if threshold_name in self.thresholds:
            self.thresholds[threshold_name] = value
            logger.info(f"Health check threshold updated: {threshold_name} = {value}")
        else:
            logger.warning(f"Unknown threshold: {threshold_name}")
    
    def set_check_interval(self, interval_seconds: int) -> None:
        """Set the health check interval."""
        self.check_interval = interval_seconds
        logger.info(f"Health check interval updated: {interval_seconds} seconds")
    
    def force_health_check(self, component_name: str) -> bool:
        """Force an immediate health check for a component."""
        if component_name not in self.components:
            logger.warning(f"Component not found: {component_name}")
            return False
        
        # Schedule immediate health check
        asyncio.create_task(self._check_component_health(component_name, self.components[component_name]))
        logger.info(f"Forced health check scheduled for component: {component_name}")
        return True
    
    def get_health_alerts(self) -> List[Dict[str, Any]]:
        """Get health alerts based on thresholds."""
        alerts = []
        
        for component_name, component in self.components.items():
            # Check response time alerts
            if component.average_response_time > self.thresholds["response_time_critical"]:
                alerts.append({
                    "level": "critical",
                    "component": component_name,
                    "message": f"Response time critical: {component.average_response_time:.2f}ms",
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif component.average_response_time > self.thresholds["response_time_warning"]:
                alerts.append({
                    "level": "warning",
                    "component": component_name,
                    "message": f"Response time warning: {component.average_response_time:.2f}ms",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Check consecutive failures alerts
            if component.consecutive_failures >= self.thresholds["consecutive_failures_critical"]:
                alerts.append({
                    "level": "critical",
                    "component": component_name,
                    "message": f"Critical consecutive failures: {component.consecutive_failures}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif component.consecutive_failures >= self.thresholds["consecutive_failures_warning"]:
                alerts.append({
                    "level": "warning",
                    "component": component_name,
                    "message": f"Warning consecutive failures: {component.consecutive_failures}",
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return alerts
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the current status of the health check service."""
        return {
            "service": "Health Check Service",
            "status": "running" if self.is_running else "stopped",
            "components_monitored": len(self.components),
            "health_checks_registered": len(self.health_checks),
            "check_interval_seconds": self.check_interval,
            "last_updated": datetime.utcnow().isoformat()
        }
