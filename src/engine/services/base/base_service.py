"""
Base Service - Abstract Base Class for All Services
==================================================

Provides the foundation for all business logic services with:
- Common service lifecycle methods
- Error handling and logging
- Performance monitoring integration
- Audit trail support
- Service health monitoring
- Configuration management
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union, TypeVar, Generic
from datetime import datetime, timedelta
from functools import wraps
import traceback

from ...models.base_model import BaseModel, AuditInfo
from ...repositories.base_repository import BaseRepository
from ...models.enums import EventType, SystemCategory, SecurityLevel

# Type variables for generic services
T = TypeVar('T', bound=BaseModel)
R = TypeVar('R', bound=BaseRepository)

logger = logging.getLogger(__name__)


class BaseService(ABC, Generic[T, R]):
    """
    Abstract base class for all business logic services.
    
    Provides common functionality for:
    - Service lifecycle management
    - Error handling and logging
    - Performance monitoring
    - Audit trail support
    - Health monitoring
    - Configuration management
    """

    def __init__(self, repository: Optional[R] = None, service_name: str = None):
        """
        Initialize the base service.
        
        Args:
            repository: The repository instance for data access
            service_name: Human-readable name for this service
        """
        self.repository = repository
        self.service_name = service_name or self.__class__.__name__
        self.start_time = datetime.now()
        self.is_active = True
        
        # Service configuration
        self.config = self._load_service_config()
        
        # Performance tracking
        self.operation_metrics = {}
        self.performance_thresholds = self.config.get('performance_thresholds', {})
        
        # Health monitoring
        self.health_status = 'healthy'
        self.last_health_check = datetime.now()
        self.health_check_interval = timedelta(minutes=5)
        
        # Audit trail
        self.audit_enabled = self.config.get('audit_enabled', True)
        self.audit_events = []
        
        # Service registry
        self.dependencies = []
        self.dependent_services = []
        
        logger.info(f"Initialized {self.service_name} service")

    def _load_service_config(self) -> Dict[str, Any]:
        """Load service-specific configuration."""
        # This would load from configuration files or environment
        # For now, return default configuration
        return {
            'audit_enabled': True,
            'performance_thresholds': {
                'max_operation_time_ms': 5000,
                'max_error_rate': 0.05,
                'max_memory_usage_mb': 512
            },
            'retry_config': {
                'max_retries': 3,
                'retry_delay_ms': 1000,
                'exponential_backoff': True
            },
            'cache_config': {
                'enabled': True,
                'ttl_minutes': 30,
                'max_size': 1000
            }
        }

    # Service Lifecycle Methods

    async def start(self) -> bool:
        """Start the service and initialize resources."""
        try:
            logger.info(f"Starting {self.service_name} service")
            
            # Initialize repository if available
            if self.repository:
                await self._initialize_repository()
            
            # Initialize service-specific resources
            await self._initialize_service_resources()
            
            # Perform health check
            await self._perform_health_check()
            
            self.is_active = True
            logger.info(f"{self.service_name} service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {self.service_name} service: {e}")
            self.health_status = 'critical'
            return False

    async def stop(self) -> bool:
        """Stop the service and cleanup resources."""
        try:
            logger.info(f"Stopping {self.service_name} service")
            
            # Cleanup service-specific resources
            await self._cleanup_service_resources()
            
            # Cleanup repository if available
            if self.repository:
                await self._cleanup_repository()
            
            self.is_active = False
            logger.info(f"{self.service_name} service stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {self.service_name} service: {e}")
            return False

    async def restart(self) -> bool:
        """Restart the service."""
        logger.info(f"Restarting {self.service_name} service")
        await self.stop()
        await asyncio.sleep(1)  # Brief pause between stop/start
        return await self.start()

    # Abstract Methods (must be implemented by subclasses)

    @abstractmethod
    async def _initialize_service_resources(self) -> None:
        """Initialize service-specific resources."""
        pass

    @abstractmethod
    async def _cleanup_service_resources(self) -> None:
        """Cleanup service-specific resources."""
        pass

    @abstractmethod
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status."""
        pass

    # Repository Management

    async def _initialize_repository(self) -> None:
        """Initialize the repository connection."""
        if self.repository and hasattr(self.repository, 'initialize'):
            await self.repository.initialize()

    async def _cleanup_repository(self) -> None:
        """Cleanup repository connections."""
        if self.repository and hasattr(self.repository, 'cleanup'):
            await self.repository.cleanup()

    # Performance Monitoring

    def performance_decorator(self, operation_name: str = None):
        """Decorator to measure operation performance."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                op_name = operation_name or func.__name__
                start_time = datetime.now()
                
                try:
                    result = await func(*args, **kwargs)
                    operation_time = (datetime.now() - start_time).total_seconds() * 1000
                    self._record_operation_metrics(op_name, operation_time, success=True)
                    return result
                    
                except Exception as e:
                    operation_time = (datetime.now() - start_time).total_seconds() * 1000
                    self._record_operation_metrics(op_name, operation_time, success=False, error=str(e))
                    raise
                    
            return wrapper
        return decorator

    def _record_operation_metrics(self, operation_name: str, operation_time: float, 
                                 success: bool, error: str = None) -> None:
        """Record operation performance metrics."""
        if operation_name not in self.operation_metrics:
            self.operation_metrics[operation_name] = {
                'count': 0,
                'success_count': 0,
                'error_count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'last_error': None,
                'last_operation': None
            }
        
        metrics = self.operation_metrics[operation_name]
        metrics['count'] += 1
        metrics['total_time'] += operation_time
        metrics['avg_time'] = metrics['total_time'] / metrics['count']
        metrics['min_time'] = min(metrics['min_time'], operation_time)
        metrics['max_time'] = max(metrics['max_time'], operation_time)
        metrics['last_operation'] = datetime.now()
        
        if success:
            metrics['success_count'] += 1
        else:
            metrics['error_count'] += 1
            metrics['last_error'] = error

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.operation_metrics:
            return {'message': 'No operations recorded yet'}
        
        total_operations = sum(m['count'] for m in self.operation_metrics.values())
        total_success = sum(m['success_count'] for m in self.operation_metrics.values())
        total_errors = sum(m['error_count'] for m in self.operation_metrics.values())
        
        overall_success_rate = (total_success / total_operations) if total_operations > 0 else 0
        overall_error_rate = (total_errors / total_operations) if total_operations > 0 else 0
        
        return {
            'service_name': self.service_name,
            'total_operations': total_operations,
            'overall_success_rate': overall_success_rate,
            'overall_error_rate': overall_error_rate,
            'operation_details': self.operation_metrics,
            'uptime': str(datetime.now() - self.start_time),
            'health_status': self.health_status
        }

    # Health Monitoring

    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'service_name': self.service_name,
            'status': 'healthy',
            'checks': {},
            'overall_score': 100.0
        }
        
        # Check service status
        service_healthy = self.is_active
        health_status['checks']['service_status'] = {
            'status': 'healthy' if service_healthy else 'unhealthy',
            'details': 'Service is active and running' if service_healthy else 'Service is inactive'
        }
        
        # Check repository health
        if self.repository:
            repo_healthy = await self._check_repository_health()
            health_status['checks']['repository'] = {
                'status': 'healthy' if repo_healthy else 'unhealthy',
                'details': 'Repository connection healthy' if repo_healthy else 'Repository connection failed'
            }
        else:
            health_status['checks']['repository'] = {
                'status': 'not_applicable',
                'details': 'No repository configured for this service'
            }
        
        # Check performance health
        performance_healthy = self._check_performance_health()
        health_status['checks']['performance'] = {
            'status': 'healthy' if performance_healthy else 'warning',
            'details': 'Performance within acceptable limits' if performance_healthy else 'Performance issues detected'
        }
        
        # Calculate overall score
        healthy_checks = sum(1 for check in health_status['checks'].values() 
                           if check['status'] == 'healthy')
        total_checks = len([c for c in health_status['checks'].values() 
                           if c['status'] != 'not_applicable'])
        
        if total_checks > 0:
            health_status['overall_score'] = (healthy_checks / total_checks) * 100
        
        # Set overall status
        if health_status['overall_score'] >= 90:
            health_status['status'] = 'healthy'
        elif health_status['overall_score'] >= 70:
            health_status['status'] = 'warning'
        else:
            health_status['status'] = 'critical'
        
        self.health_status = health_status['status']
        self.last_health_check = datetime.now()
        
        return health_status

    async def _check_repository_health(self) -> bool:
        """Check repository health status."""
        try:
            if hasattr(self.repository, 'perform_health_check'):
                return await self.repository.perform_health_check()
            elif hasattr(self.repository, '_validate_connection'):
                return self.repository._validate_connection()
            else:
                return True  # Assume healthy if no health check method
        except Exception as e:
            logger.error(f"Repository health check failed: {e}")
            return False

    def _check_performance_health(self) -> bool:
        """Check if performance is within acceptable limits."""
        if not self.operation_metrics:
            return True
        
        # Check for high error rates
        for operation, metrics in self.operation_metrics.items():
            total_ops = metrics.get('count', 0)
            error_ops = metrics.get('error_count', 0)
            
            if total_ops > 0 and (error_ops / total_ops) > 0.1:  # 10% error rate
                return False
            
            # Check for slow operations
            if metrics.get('avg_time', 0) > 5000:  # 5 seconds
                return False
        
        return True

    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        # Check if health check is due
        if datetime.now() - self.last_health_check > self.health_check_interval:
            return await self._perform_health_check()
        
        return {
            'timestamp': self.last_health_check.isoformat(),
            'service_name': self.service_name,
            'status': self.health_status,
            'last_check': self.last_health_check.isoformat(),
            'uptime': str(datetime.now() - self.start_time)
        }

    # Error Handling

    def handle_error(self, operation: str, error: Exception, context: Dict[str, Any] = None) -> None:
        """Handle and log service errors."""
        error_context = {
            'service_name': self.service_name,
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        logger.error(f"Service error in {self.service_name}: {error_context}")
        
        # Record error in metrics
        if operation in self.operation_metrics:
            self.operation_metrics[operation]['last_error'] = str(error)
        
        # Update health status if critical
        if isinstance(error, (ConnectionError, TimeoutError)):
            self.health_status = 'critical'
    
    def _log_operation(self, operation: str, details: str = None) -> None:
        """Log service operation for tracking and debugging."""
        log_message = f"Operation: {operation}"
        if details:
            log_message += f" - {details}"
        
        logger.info(f"{self.service_name}: {log_message}")
        
        # Record operation in metrics
        if operation not in self.operation_metrics:
            self.operation_metrics[operation] = {
                'count': 0,
                'last_execution': None,
                'total_time_ms': 0,
                'last_error': None
            }
        
        self.operation_metrics[operation]['count'] += 1
        self.operation_metrics[operation]['last_execution'] = datetime.now().isoformat()

    # Audit Trail

    async def log_audit_event(self, event_type, system_category, message: str, 
                             details: Dict[str, Any], security_level: SecurityLevel = SecurityLevel.INTERNAL) -> None:
        """Log audit event with business domain signature for compliance and tracking."""
        if not self.audit_enabled:
            return
        
        # Convert enum values to strings for storage
        event_type_str = event_type.value if hasattr(event_type, 'value') else str(event_type)
        system_category_str = system_category.value if hasattr(system_category, 'value') else str(system_category)
        
        audit_event = {
            'timestamp': datetime.now().isoformat(),
            'service_name': self.service_name,
            'event_type': event_type_str,
            'system_category': system_category_str,
            'message': message,
            'details': details,
            'security_level': security_level.value,
            'session_id': getattr(self, 'session_id', None)
        }
        
        self.audit_events.append(audit_event)
        
        # Keep only recent audit events (last 1000)
        if len(self.audit_events) > 1000:
            self.audit_events = self.audit_events[-1000:]
        
        logger.info(f"Audit event logged: {event_type_str} - {message}")

    def get_audit_trail(self, entity_id: str = None, event_type: str = None, 
                        start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get audit trail with optional filtering."""
        filtered_events = self.audit_events
        
        if entity_id:
            filtered_events = [e for e in filtered_events if e['entity_id'] == entity_id]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e['event_type'] == event_type]
        
        if start_date:
            filtered_events = [e for e in filtered_events 
                             if datetime.fromisoformat(e['timestamp']) >= start_date]
        
        if end_date:
            filtered_events = [e for e in filtered_events 
                             if datetime.fromisoformat(e['timestamp']) <= end_date]
        
        return filtered_events

    # Configuration Management

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update service configuration."""
        self.config.update(new_config)
        logger.info(f"Configuration updated for {self.service_name}")

    def get_config(self, key: str = None) -> Any:
        """Get service configuration."""
        if key:
            return self.config.get(key)
        return self.config

    # Dependency Management

    def add_dependency(self, service_name: str, service_instance: 'BaseService') -> None:
        """Add a service dependency."""
        self.dependencies.append({
            'name': service_name,
            'instance': service_instance,
            'added_at': datetime.now()
        })
        logger.info(f"Added dependency: {service_name}")

    def remove_dependency(self, service_name: str) -> None:
        """Remove a service dependency."""
        self.dependencies = [d for d in self.dependencies if d['name'] != service_name]
        logger.info(f"Removed dependency: {service_name}")

    def get_dependencies(self) -> List[Dict[str, Any]]:
        """Get list of service dependencies."""
        return [{'name': d['name'], 'added_at': d['added_at']} for d in self.dependencies]

    # Utility Methods

    def is_service_healthy(self) -> bool:
        """Check if service is healthy."""
        return self.health_status == 'healthy' and self.is_active

    def get_uptime(self) -> timedelta:
        """Get service uptime."""
        return datetime.now() - self.start_time

    def get_service_statistics(self) -> Dict[str, Any]:
        """Get comprehensive service statistics."""
        return {
            'service_name': self.service_name,
            'uptime': str(self.get_uptime()),
            'health_status': self.health_status,
            'is_active': self.is_active,
            'total_operations': sum(m['count'] for m in self.operation_metrics.values()),
            'dependencies_count': len(self.dependencies),
            'audit_events_count': len(self.audit_events),
            'last_health_check': self.last_health_check.isoformat()
        }
