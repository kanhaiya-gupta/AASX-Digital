"""
Health Service - Core System Service
===================================

Provides centralized health monitoring and management for the entire system.
This service extends the base service infrastructure with comprehensive health capabilities.

Features:
- System-wide health monitoring
- Service health aggregation
- Health check orchestration
- Health status reporting
- Proactive health management
- Health alerting and notifications
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import json

from ..base import BaseService
from ...models.base_model import BaseModel
from ...repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class HealthCheckType(Enum):
    """Types of health checks."""
    LIVENESS = "liveness"         # Is the service alive?
    READINESS = "readiness"       # Is the service ready to serve?
    STARTUP = "startup"           # Has the service started successfully?
    SHUTDOWN = "shutdown"         # Is the service shutting down gracefully?


@dataclass
class HealthCheck:
    """Individual health check definition."""
    name: str
    check_type: HealthCheckType
    description: str
    timeout_seconds: int = 30
    retry_count: int = 3
    retry_delay_seconds: int = 5
    critical: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    check_name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class ServiceHealth:
    """Health status of a service."""
    service_id: str
    service_name: str
    overall_status: HealthStatus
    checks: List[HealthCheckResult]
    last_check: datetime
    uptime: timedelta
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """Overall system health status."""
    timestamp: datetime
    overall_status: HealthStatus
    total_services: int
    healthy_services: int
    warning_services: int
    critical_services: int
    maintenance_services: int
    health_percentage: float
    services: Dict[str, ServiceHealth]
    alerts: List[Dict[str, Any]] = field(default_factory=list)


class HealthService(BaseService[BaseModel, BaseRepository]):
    """
    Core health service for system-wide health management.
    
    Provides:
    - System-wide health monitoring
    - Service health aggregation
    - Health check orchestration
    - Health status reporting
    - Proactive health management
    - Health alerting and notifications
    """

    def __init__(self, repository: Optional[BaseRepository] = None):
        super().__init__(repository, "HealthService")
        
        # Health monitoring
        self._service_health: Dict[str, ServiceHealth] = {}
        self._health_checks: Dict[str, List[HealthCheck]] = {}
        self._health_history: Dict[str, List[HealthCheckResult]] = {}
        
        # Health check orchestration
        self._check_interval = timedelta(minutes=2)
        self._health_timeout = timedelta(seconds=30)
        self._max_retries = 3
        
        # Alerting and notifications
        self._alert_thresholds = {
            'critical': 0.0,
            'warning': 0.7,
            'healthy': 1.0
        }
        self._alert_subscribers: List[Callable] = []
        self._alerts: List[Dict[str, Any]] = []
        
        # Health policies
        self._health_policies: Dict[str, Dict[str, Any]] = {}
        self._auto_remediation: Dict[str, Callable] = {}
        
        # Performance tracking
        self._health_check_stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'average_check_duration': 0.0,
            'last_check_cycle': None
        }
        
        logger.info("Health service initialized")

    async def _initialize_service_resources(self) -> None:
        """Initialize health service resources."""
        # Start health monitoring
        await self._start_health_monitoring()
        
        # Initialize default health policies
        await self._initialize_default_health_policies()
        
        # Start health check orchestration
        await self._start_health_check_orchestration()
        
        logger.info("Health service resources initialized")

    async def _cleanup_service_resources(self) -> None:
        """Cleanup health service resources."""
        # Stop health monitoring
        await self._stop_health_monitoring()
        
        # Stop health check orchestration
        await self._stop_health_check_orchestration()
        
        # Cleanup health data
        await self._cleanup_health_data()
        
        logger.info("Health service resources cleaned up")

    async def get_service_info(self) -> Dict[str, Any]:
        """Get health service information."""
        return {
            'service_name': self.service_name,
            'total_services_monitored': len(self._service_health),
            'total_health_checks': len(self._health_checks),
            'health_check_stats': self._health_check_stats,
            'health_status': self.health_status,
            'uptime': str(self.get_uptime()),
            'last_health_check': self.last_health_check.isoformat()
        }

    # Service Registration and Health Check Management

    async def register_service_health_checks(self, service_id: str, service_name: str,
                                           checks: List[HealthCheck], version: str = "1.0.0",
                                           metadata: Dict[str, Any] = None) -> bool:
        """
        Register health checks for a service.
        
        Args:
            service_id: Unique service identifier
            service_name: Human-readable service name
            checks: List of health checks
            version: Service version
            metadata: Additional service metadata
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Register health checks
            self._health_checks[service_id] = checks
            
            # Initialize service health
            service_health = ServiceHealth(
                service_id=service_id,
                service_name=service_name,
                overall_status=HealthStatus.UNKNOWN,
                checks=[],
                last_check=datetime.now(),
                uptime=timedelta(0),
                version=version,
                metadata=metadata or {}
            )
            
            self._service_health[service_id] = service_health
            
            # Initialize health history
            self._health_history[service_id] = []
            
            logger.info(f"Health checks registered for service {service_id} ({service_name})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register health checks for service {service_id}: {e}")
            return False

    async def unregister_service_health_checks(self, service_id: str) -> bool:
        """Unregister health checks for a service."""
        try:
            if service_id in self._health_checks:
                del self._health_checks[service_id]
            
            if service_id in self._service_health:
                del self._service_health[service_id]
            
            if service_id in self._health_history:
                del self._health_history[service_id]
            
            logger.info(f"Health checks unregistered for service {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister health checks for service {service_id}: {e}")
            return False

    async def add_health_check(self, service_id: str, health_check: HealthCheck) -> bool:
        """Add a health check to an existing service."""
        try:
            if service_id not in self._health_checks:
                self._health_checks[service_id] = []
            
            self._health_checks[service_id].append(health_check)
            logger.info(f"Health check {health_check.name} added to service {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add health check to service {service_id}: {e}")
            return False

    async def remove_health_check(self, service_id: str, check_name: str) -> bool:
        """Remove a health check from a service."""
        try:
            if service_id in self._health_checks:
                self._health_checks[service_id] = [
                    check for check in self._health_checks[service_id] 
                    if check.name != check_name
                ]
                logger.info(f"Health check {check_name} removed from service {service_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove health check from service {service_id}: {e}")
            return False

    # Health Check Execution

    async def _start_health_check_orchestration(self) -> None:
        """Start health check orchestration."""
        logger.info("Starting health check orchestration")
        
        # Schedule periodic health checks
        asyncio.create_task(self._health_check_orchestration_loop())

    async def _stop_health_check_orchestration(self) -> None:
        """Stop health check orchestration."""
        logger.info("Stopping health check orchestration")

    async def _health_check_orchestration_loop(self) -> None:
        """Main health check orchestration loop."""
        while self.is_active:
            try:
                await self._execute_all_health_checks()
                await asyncio.sleep(self._check_interval.total_seconds())
            except Exception as e:
                logger.error(f"Health check orchestration error: {e}")
                await asyncio.sleep(60)

    async def _execute_all_health_checks(self) -> None:
        """Execute health checks for all registered services."""
        try:
            start_time = datetime.now()
            total_checks = 0
            successful_checks = 0
            failed_checks = 0
            
            for service_id in list(self._health_checks.keys()):
                try:
                    service_results = await self._execute_service_health_checks(service_id)
                    
                    if service_results:
                        total_checks += len(service_results)
                        successful_checks += sum(1 for r in service_results if r.status != HealthStatus.CRITICAL)
                        failed_checks += sum(1 for r in service_results if r.status == HealthStatus.CRITICAL)
                        
                        # Update service health
                        await self._update_service_health(service_id, service_results)
                        
                except Exception as e:
                    logger.error(f"Failed to execute health checks for service {service_id}: {e}")
                    failed_checks += 1
            
            # Update statistics
            cycle_duration = (datetime.now() - start_time).total_seconds() * 1000
            self._health_check_stats.update({
                'total_checks': total_checks,
                'successful_checks': successful_checks,
                'failed_checks': failed_checks,
                'average_check_duration': cycle_duration / max(total_checks, 1),
                'last_check_cycle': start_time.isoformat()
            })
            
            logger.debug(f"Completed health check cycle: {total_checks} checks, {successful_checks} successful, {failed_checks} failed")
            
        except Exception as e:
            logger.error(f"Failed to execute health checks: {e}")

    async def _execute_service_health_checks(self, service_id: str) -> List[HealthCheckResult]:
        """Execute health checks for a specific service."""
        try:
            if service_id not in self._health_checks:
                return []
            
            checks = self._health_checks[service_id]
            results = []
            
            for check in checks:
                try:
                    result = await self._execute_health_check(service_id, check)
                    results.append(result)
                    
                    # Store in health history
                    if service_id not in self._health_history:
                        self._health_history[service_id] = []
                    
                    self._health_history[service_id].append(result)
                    
                    # Keep only recent history (last 1000 checks)
                    if len(self._health_history[service_id]) > 1000:
                        self._health_history[service_id] = self._health_history[service_id][-1000:]
                    
                except Exception as e:
                    logger.error(f"Failed to execute health check {check.name} for service {service_id}: {e}")
                    
                    # Create failed result
                    failed_result = HealthCheckResult(
                        check_name=check.name,
                        status=HealthStatus.CRITICAL,
                        message=f"Health check execution failed: {e}",
                        timestamp=datetime.now(),
                        duration_ms=0.0,
                        error=str(e)
                    )
                    results.append(failed_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute service health checks for {service_id}: {e}")
            return []

    async def _execute_health_check(self, service_id: str, check: HealthCheck) -> HealthCheckResult:
        """Execute a single health check."""
        start_time = datetime.now()
        
        try:
            # In a real implementation, this would call the actual health check endpoint
            # For now, we'll simulate the health check
            await asyncio.sleep(0.1)  # Simulate check duration
            
            # Simulate health check result (in production, implement actual health checking)
            import random
            success_rate = random.uniform(0.8, 1.0)
            
            if success_rate >= self._alert_thresholds['healthy']:
                status = HealthStatus.HEALTHY
                message = "Health check passed successfully"
            elif success_rate >= self._alert_thresholds['warning']:
                status = HealthStatus.WARNING
                message = "Health check passed with warnings"
            else:
                status = HealthStatus.CRITICAL
                message = "Health check failed"
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return HealthCheckResult(
                check_name=check.name,
                status=status,
                message=message,
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                details={'success_rate': success_rate}
            )
            
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return HealthCheckResult(
                check_name=check.name,
                status=HealthStatus.CRITICAL,
                message=f"Health check execution failed: {e}",
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                error=str(e)
            )

    # Service Health Management

    async def _update_service_health(self, service_id: str, check_results: List[HealthCheckResult]) -> None:
        """Update service health based on check results."""
        try:
            if service_id not in self._service_health:
                return
            
            service_health = self._service_health[service_id]
            
            # Update checks
            service_health.checks = check_results
            service_health.last_check = datetime.now()
            
            # Determine overall status
            overall_status = self._calculate_overall_health_status(check_results)
            service_health.overall_status = overall_status
            
            # Update uptime
            if hasattr(service_health, 'start_time'):
                service_health.uptime = datetime.now() - service_health.start_time
            else:
                service_health.start_time = datetime.now()
                service_health.uptime = timedelta(0)
            
            # Check for alerts
            await self._check_service_alerts(service_id, service_health)
            
            # Attempt auto-remediation if critical
            if overall_status == HealthStatus.CRITICAL:
                await self._attempt_auto_remediation(service_id, service_health)
            
            logger.debug(f"Updated health for service {service_id}: {overall_status.value}")
            
        except Exception as e:
            logger.error(f"Failed to update service health for {service_id}: {e}")

    def _calculate_overall_health_status(self, check_results: List[HealthCheckResult]) -> HealthStatus:
        """Calculate overall health status from check results."""
        if not check_results:
            return HealthStatus.UNKNOWN
        
        # Count statuses
        status_counts = {}
        for result in check_results:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Determine overall status
        if HealthStatus.CRITICAL.value in status_counts:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING.value in status_counts:
            return HealthStatus.WARNING
        elif HealthStatus.HEALTHY.value in status_counts:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    # Health Status Retrieval

    async def get_service_health(self, service_id: str) -> Optional[ServiceHealth]:
        """Get health status for a specific service."""
        return self._service_health.get(service_id)

    async def get_all_services_health(self) -> List[ServiceHealth]:
        """Get health status for all services."""
        return list(self._service_health.values())

    async def get_system_health(self) -> SystemHealth:
        """Get overall system health status."""
        try:
            total_services = len(self._service_health)
            
            if total_services == 0:
                return SystemHealth(
                    timestamp=datetime.now(),
                    overall_status=HealthStatus.UNKNOWN,
                    total_services=0,
                    healthy_services=0,
                    warning_services=0,
                    critical_services=0,
                    maintenance_services=0,
                    health_percentage=0.0,
                    services={}
                )
            
            # Count services by status
            status_counts = {
                HealthStatus.HEALTHY: 0,
                HealthStatus.WARNING: 0,
                HealthStatus.CRITICAL: 0,
                HealthStatus.MAINTENANCE: 0,
                HealthStatus.UNKNOWN: 0
            }
            
            for service_health in self._service_health.values():
                status_counts[service_health.overall_status] += 1
            
            # Calculate health percentage
            healthy_count = status_counts[HealthStatus.HEALTHY]
            health_percentage = (healthy_count / total_services) * 100
            
            # Determine overall system status
            if status_counts[HealthStatus.CRITICAL] > 0:
                overall_status = HealthStatus.CRITICAL
            elif status_counts[HealthStatus.WARNING] > 0:
                overall_status = HealthStatus.WARNING
            elif status_counts[HealthStatus.HEALTHY] > 0:
                overall_status = HealthStatus.HEALTHY
            else:
                overall_status = HealthStatus.UNKNOWN
            
            return SystemHealth(
                timestamp=datetime.now(),
                overall_status=overall_status,
                total_services=total_services,
                healthy_services=status_counts[HealthStatus.HEALTHY],
                warning_services=status_counts[HealthStatus.WARNING],
                critical_services=status_counts[HealthStatus.CRITICAL],
                maintenance_services=status_counts[HealthStatus.MAINTENANCE],
                health_percentage=health_percentage,
                services=self._service_health.copy(),
                alerts=self._alerts.copy()
            )
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return SystemHealth(
                timestamp=datetime.now(),
                overall_status=HealthStatus.UNKNOWN,
                total_services=0,
                healthy_services=0,
                warning_services=0,
                critical_services=0,
                maintenance_services=0,
                health_percentage=0.0,
                services={},
                alerts=[{'error': str(e)}]
            )

    # Health Policies and Auto-Remediation

    async def _initialize_default_health_policies(self) -> None:
        """Initialize default health policies."""
        try:
            # Default policy for critical services
            self._health_policies['critical'] = {
                'max_failure_count': 3,
                'failure_window': timedelta(minutes=5),
                'auto_remediation': True,
                'escalation_threshold': timedelta(minutes=10)
            }
            
            # Default policy for warning services
            self._health_policies['warning'] = {
                'max_failure_count': 5,
                'failure_window': timedelta(minutes=10),
                'auto_remediation': False,
                'escalation_threshold': timedelta(minutes=30)
            }
            
            logger.info("Default health policies initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default health policies: {e}")

    async def set_health_policy(self, service_id: str, policy: Dict[str, Any]) -> bool:
        """Set health policy for a service."""
        try:
            self._health_policies[service_id] = policy
            logger.info(f"Health policy set for service {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set health policy for service {service_id}: {e}")
            return False

    async def get_health_policy(self, service_id: str) -> Dict[str, Any]:
        """Get health policy for a service."""
        return self._health_policies.get(service_id, self._health_policies.get('critical', {}))

    async def register_auto_remediation(self, service_id: str, 
                                      remediation_func: Callable) -> bool:
        """Register auto-remediation function for a service."""
        try:
            self._auto_remediation[service_id] = remediation_func
            logger.info(f"Auto-remediation registered for service {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register auto-remediation for service {service_id}: {e}")
            return False

    async def _attempt_auto_remediation(self, service_id: str, 
                                      service_health: ServiceHealth) -> None:
        """Attempt auto-remediation for a critical service."""
        try:
            if service_id not in self._auto_remediation:
                logger.debug(f"No auto-remediation registered for service {service_id}")
                return
            
            policy = await self.get_health_policy(service_id)
            if not policy.get('auto_remediation', False):
                logger.debug(f"Auto-remediation disabled for service {service_id}")
                return
            
            remediation_func = self._auto_remediation[service_id]
            logger.info(f"Attempting auto-remediation for service {service_id}")
            
            # Execute remediation
            success = await remediation_func(service_id, service_health)
            
            if success:
                logger.info(f"Auto-remediation successful for service {service_id}")
            else:
                logger.warning(f"Auto-remediation failed for service {service_id}")
                
        except Exception as e:
            logger.error(f"Auto-remediation error for service {service_id}: {e}")

    # Alerting and Notifications

    async def subscribe_to_alerts(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Subscribe to health alerts."""
        try:
            self._alert_subscribers.append(callback)
            logger.info("Alert subscription added")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add alert subscription: {e}")
            return False

    async def unsubscribe_from_alerts(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Unsubscribe from health alerts."""
        try:
            if callback in self._alert_subscribers:
                self._alert_subscribers.remove(callback)
                logger.info("Alert subscription removed")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove alert subscription: {e}")
            return False

    async def _check_service_alerts(self, service_id: str, 
                                  service_health: ServiceHealth) -> None:
        """Check if service health changes warrant alerts."""
        try:
            # Check for status changes that warrant alerts
            if service_health.overall_status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'service_id': service_id,
                    'service_name': service_health.service_name,
                    'severity': service_health.overall_status.value,
                    'message': f"Service {service_health.service_name} is in {service_health.overall_status.value} status",
                    'details': {
                        'checks': [asdict(r) for r in service_health.checks],
                        'uptime': str(service_health.uptime),
                        'version': service_health.version
                    }
                }
                
                self._alerts.append(alert)
                
                # Keep only recent alerts (last 100)
                if len(self._alerts) > 100:
                    self._alerts = self._alerts[-100:]
                
                # Notify subscribers
                await self._notify_alert_subscribers(alert)
                
                logger.warning(f"Health alert generated for service {service_id}: {service_health.overall_status.value}")
                
        except Exception as e:
            logger.error(f"Failed to check service alerts for {service_id}: {e}")

    async def _notify_alert_subscribers(self, alert: Dict[str, Any]) -> None:
        """Notify all alert subscribers."""
        try:
            for callback in self._alert_subscribers:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert subscriber callback error: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to notify alert subscribers: {e}")

    async def get_alerts(self, service_id: str = None, 
                        severity: str = None, 
                        start_time: datetime = None,
                        end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get health alerts with optional filtering."""
        try:
            filtered_alerts = self._alerts.copy()
            
            if service_id:
                filtered_alerts = [a for a in filtered_alerts if a['service_id'] == service_id]
            
            if severity:
                filtered_alerts = [a for a in filtered_alerts if a['severity'] == severity]
            
            if start_time:
                filtered_alerts = [a for a in filtered_alerts 
                                 if datetime.fromisoformat(a['timestamp']) >= start_time]
            
            if end_time:
                filtered_alerts = [a for a in filtered_alerts 
                                 if datetime.fromisoformat(a['timestamp']) <= end_time]
            
            return filtered_alerts
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []

    # Health Monitoring

    async def _start_health_monitoring(self) -> None:
        """Start health monitoring."""
        logger.info("Starting health monitoring")

    async def _stop_health_monitoring(self) -> None:
        """Stop health monitoring."""
        logger.info("Stopping health monitoring")

    # Cleanup

    async def _cleanup_health_data(self) -> None:
        """Cleanup health data."""
        try:
            self._service_health.clear()
            self._health_checks.clear()
            self._health_history.clear()
            self._alerts.clear()
            self._alert_subscribers.clear()
            self._auto_remediation.clear()
            logger.info("Health data cleaned up")
        except Exception as e:
            logger.error(f"Failed to cleanup health data: {e}")

    # Manual Health Checks

    async def execute_manual_health_check(self, service_id: str) -> List[HealthCheckResult]:
        """Execute health checks for a service manually."""
        try:
            if service_id not in self._health_checks:
                logger.warning(f"No health checks registered for service {service_id}")
                return []
            
            results = await self._execute_service_health_checks(service_id)
            await self._update_service_health(service_id, results)
            
            logger.info(f"Manual health check completed for service {service_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute manual health check for service {service_id}: {e}")
            return []

    # Health Reports

    async def generate_health_report(self, service_id: str = None, 
                                   format: str = "json") -> str:
        """Generate health report."""
        try:
            if service_id:
                # Single service report
                service_health = await self.get_service_health(service_id)
                if not service_health:
                    return "Service not found"
                
                report_data = {
                    'timestamp': datetime.now().isoformat(),
                    'service_health': service_health.__dict__,
                    'health_history': self._health_history.get(service_id, [])
                }
            else:
                # System-wide report
                system_health = await self.get_system_health()
                report_data = {
                    'timestamp': datetime.now().isoformat(),
                    'system_health': system_health.__dict__,
                    'health_check_stats': self._health_check_stats,
                    'alerts': self._alerts
                }
            
            if format.lower() == "json":
                return json.dumps(report_data, default=str, indent=2)
            else:
                raise ValueError(f"Unsupported report format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to generate health report: {e}")
            return f"Error generating report: {e}"

    # Health Metrics

    async def get_health_metrics(self) -> Dict[str, Any]:
        """Get health service metrics."""
        try:
            return {
                'total_services_monitored': len(self._service_health),
                'total_health_checks': sum(len(checks) for checks in self._health_checks.values()),
                'health_check_stats': self._health_check_stats,
                'alert_counts': {
                    'total_alerts': len(self._alerts),
                    'critical_alerts': len([a for a in self._alerts if a['severity'] == 'critical']),
                    'warning_alerts': len([a for a in self._alerts if a['severity'] == 'warning'])
                },
                'service_health_distribution': {
                    'healthy': sum(1 for s in self._service_health.values() if s.overall_status == HealthStatus.HEALTHY),
                    'warning': sum(1 for s in self._service_health.values() if s.overall_status == HealthStatus.WARNING),
                    'critical': sum(1 for s in self._service_health.values() if s.overall_status == HealthStatus.CRITICAL),
                    'unknown': sum(1 for s in self._service_health.values() if s.overall_status == HealthStatus.UNKNOWN)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get health metrics: {e}")
            return {'error': str(e)}
