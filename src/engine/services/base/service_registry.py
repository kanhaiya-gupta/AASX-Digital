"""
Service Registry - Service Discovery and Registration
===================================================

Provides centralized service management with:
- Service discovery and registration
- Dependency injection container
- Service lifecycle management
- Service health monitoring
- Service dependency resolution
- Service configuration management
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Type, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration."""
    UNKNOWN = "unknown"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class ServiceInfo:
    """Service information container."""
    name: str
    service_type: Type
    instance: Any
    status: ServiceStatus = ServiceStatus.UNKNOWN
    dependencies: List[str] = field(default_factory=list)
    dependent_services: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ServiceRegistry:
    """
    Centralized service registry for managing all services.
    
    Provides:
    - Service registration and discovery
    - Dependency injection and resolution
    - Service lifecycle management
    - Health monitoring and status tracking
    - Configuration management
    """

    def __init__(self):
        """Initialize the service registry."""
        self._services: Dict[str, ServiceInfo] = {}
        self._service_types: Dict[str, Type] = {}
        self._dependencies: Dict[str, Set[str]] = {}
        self._health_check_interval = timedelta(minutes=2)
        self._registry_start_time = datetime.now()
        self._is_initialized = False
        
        logger.info("Service registry initialized")

    # Service Registration and Discovery

    def register_service(self, name: str, service_type: Type, instance: Any, 
                        dependencies: List[str] = None, config: Dict[str, Any] = None,
                        metadata: Dict[str, Any] = None) -> bool:
        """
        Register a service with the registry.
        
        Args:
            name: Unique service name
            service_type: Type/class of the service
            instance: Service instance
            dependencies: List of service names this service depends on
            config: Service configuration
            metadata: Additional service metadata
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            if name in self._services:
                logger.warning(f"Service {name} already registered, updating existing registration")
                # Update existing service
                existing_service = self._services[name]
                existing_service.instance = instance
                existing_service.config.update(config or {})
                existing_service.metadata.update(metadata or {})
                if dependencies:
                    existing_service.dependencies = dependencies
                return True
            
            # Create new service info
            service_info = ServiceInfo(
                name=name,
                service_type=service_type,
                instance=instance,
                dependencies=dependencies or [],
                config=config or {},
                metadata=metadata or {}
            )
            
            # Register service
            self._services[name] = service_info
            self._service_types[name] = service_type
            
            # Update dependency graph
            if dependencies:
                self._dependencies[name] = set(dependencies)
                for dep in dependencies:
                    if dep in self._services:
                        self._services[dep].dependent_services.append(name)
            
            logger.info(f"Service {name} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {name}: {e}")
            return False

    def unregister_service(self, name: str) -> bool:
        """
        Unregister a service from the registry.
        
        Args:
            name: Name of the service to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if name not in self._services:
                logger.warning(f"Service {name} not found in registry")
                return False
            
            # Remove from dependency graph
            if name in self._dependencies:
                # Remove this service from dependent services
                for dep in self._dependencies[name]:
                    if dep in self._services:
                        self._services[dep].dependent_services = [
                            s for s in self._services[dep].dependent_services if s != name
                        ]
                del self._dependencies[name]
            
            # Remove from services
            del self._services[name]
            if name in self._service_types:
                del self._service_types[name]
            
            logger.info(f"Service {name} unregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service {name}: {e}")
            return False

    def get_service(self, name: str) -> Optional[Any]:
        """
        Get a service instance by name.
        
        Args:
            name: Name of the service
            
        Returns:
            Service instance or None if not found
        """
        service_info = self._services.get(name)
        return service_info.instance if service_info else None

    def get_service_info(self, name: str) -> Optional[ServiceInfo]:
        """
        Get service information by name.
        
        Args:
            name: Name of the service
            
        Returns:
            ServiceInfo object or None if not found
        """
        return self._services.get(name)

    def list_services(self) -> List[str]:
        """Get list of all registered service names."""
        return list(self._services.keys())

    def list_service_types(self) -> List[str]:
        """Get list of all registered service types."""
        return list(self._service_types.keys())

    def get_services_by_type(self, service_type: Type) -> List[str]:
        """
        Get services of a specific type.
        
        Args:
            service_type: Type to filter by
            
        Returns:
            List of service names of the specified type
        """
        return [name for name, st in self._service_types.items() if st == service_type]

    # Dependency Management

    def add_dependency(self, service_name: str, dependency_name: str) -> bool:
        """
        Add a dependency relationship between services.
        
        Args:
            service_name: Name of the service
            dependency_name: Name of the dependency
            
        Returns:
            True if dependency added successfully, False otherwise
        """
        try:
            if service_name not in self._services:
                logger.error(f"Service {service_name} not found")
                return False
            
            if dependency_name not in self._services:
                logger.error(f"Dependency {dependency_name} not found")
                return False
            
            # Add dependency
            if service_name not in self._dependencies:
                self._dependencies[service_name] = set()
            self._dependencies[service_name].add(dependency_name)
            
            # Update service info
            self._services[service_name].dependencies.append(dependency_name)
            self._services[dependency_name].dependent_services.append(service_name)
            
            logger.info(f"Added dependency: {service_name} -> {dependency_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add dependency {service_name} -> {dependency_name}: {e}")
            return False

    def remove_dependency(self, service_name: str, dependency_name: str) -> bool:
        """
        Remove a dependency relationship between services.
        
        Args:
            service_name: Name of the service
            dependency_name: Name of the dependency
            
        Returns:
            True if dependency removed successfully, False otherwise
        """
        try:
            if service_name in self._dependencies and dependency_name in self._dependencies[service_name]:
                self._dependencies[service_name].remove(dependency_name)
                
                # Update service info
                if service_name in self._services:
                    self._services[service_name].dependencies = [
                        d for d in self._services[service_name].dependencies if d != dependency_name
                    ]
                
                if dependency_name in self._services:
                    self._services[dependency_name].dependent_services = [
                        s for s in self._services[dependency_name].dependent_services if s != service_name
                    ]
                
                logger.info(f"Removed dependency: {service_name} -> {dependency_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove dependency {service_name} -> {dependency_name}: {e}")
            return False

    def get_dependencies(self, service_name: str) -> List[str]:
        """
        Get dependencies of a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of dependency names
        """
        return list(self._dependencies.get(service_name, set()))

    def get_dependent_services(self, service_name: str) -> List[str]:
        """
        Get services that depend on the specified service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of dependent service names
        """
        service_info = self._services.get(service_name)
        return service_info.dependent_services if service_info else []

    def check_circular_dependencies(self) -> List[List[str]]:
        """
        Check for circular dependencies in the service graph.
        
        Returns:
            List of circular dependency chains
        """
        def dfs(node: str, visited: Set[str], rec_stack: Set[str], path: List[str]) -> List[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            cycles = []
            for neighbor in self._dependencies.get(node, set()):
                if neighbor not in visited:
                    cycles.extend(dfs(neighbor, visited, rec_stack, path))
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
            
            rec_stack.remove(node)
            path.pop()
            return cycles
        
        visited = set()
        cycles = []
        for node in self._services.keys():
            if node not in visited:
                cycles.extend(dfs(node, visited, set(), []))
        
        return cycles

    # Service Lifecycle Management

    async def start_all_services(self) -> Dict[str, bool]:
        """
        Start all registered services.
        
        Returns:
            Dictionary mapping service names to start success status
        """
        results = {}
        logger.info("Starting all services...")
        
        # Start services in dependency order
        started_services = set()
        max_attempts = len(self._services) * 2  # Prevent infinite loops
        attempts = 0
        
        while len(started_services) < len(self._services) and attempts < max_attempts:
            attempts += 1
            
            for name, service_info in self._services.items():
                if name in started_services:
                    continue
                
                # Check if all dependencies are started
                dependencies_started = all(
                    dep in started_services for dep in service_info.dependencies
                )
                
                if dependencies_started:
                    try:
                        if hasattr(service_info.instance, 'start'):
                            success = await service_info.instance.start()
                            if success:
                                service_info.status = ServiceStatus.RUNNING
                                service_info.started_at = datetime.now()
                                started_services.add(name)
                                results[name] = True
                                logger.info(f"Service {name} started successfully")
                            else:
                                results[name] = False
                                service_info.status = ServiceStatus.ERROR
                                logger.error(f"Service {name} failed to start")
                        else:
                            # Service doesn't have start method, mark as running
                            service_info.status = ServiceStatus.RUNNING
                            started_services.add(name)
                            results[name] = True
                            logger.info(f"Service {name} marked as running (no start method)")
                    except Exception as e:
                        results[name] = False
                        service_info.status = ServiceStatus.ERROR
                        logger.error(f"Error starting service {name}: {e}")
        
        # Check for services that couldn't be started
        for name in self._services:
            if name not in started_services:
                results[name] = False
                self._services[name].status = ServiceStatus.ERROR
                logger.error(f"Service {name} could not be started due to dependency issues")
        
        self._is_initialized = True
        logger.info(f"Service startup completed. {len(started_services)}/{len(self._services)} services started")
        return results

    async def stop_all_services(self) -> Dict[str, bool]:
        """
        Stop all registered services.
        
        Returns:
            Dictionary mapping service names to stop success status
        """
        results = {}
        logger.info("Stopping all services...")
        
        # Stop services in reverse dependency order
        stopped_services = set()
        max_attempts = len(self._services) * 2
        attempts = 0
        
        while len(stopped_services) < len(self._services) and attempts < max_attempts:
            attempts += 1
            
            for name, service_info in self._services.items():
                if name in stopped_services:
                    continue
                
                # Check if no dependent services are running
                dependents_running = any(
                    dep not in stopped_services for dep in service_info.dependent_services
                )
                
                if not dependents_running:
                    try:
                        if hasattr(service_info.instance, 'stop'):
                            success = await service_info.instance.stop()
                            if success:
                                service_info.status = ServiceStatus.STOPPED
                                stopped_services.add(name)
                                results[name] = True
                                logger.info(f"Service {name} stopped successfully")
                            else:
                                results[name] = False
                                logger.error(f"Service {name} failed to stop")
                        else:
                            # Service doesn't have stop method, mark as stopped
                            service_info.status = ServiceStatus.STOPPED
                            stopped_services.add(name)
                            results[name] = True
                            logger.info(f"Service {name} marked as stopped (no stop method)")
                    except Exception as e:
                        results[name] = False
                        logger.error(f"Error stopping service {name}: {e}")
        
        self._is_initialized = False
        logger.info(f"Service shutdown completed. {len(stopped_services)}/{len(self._services)} services stopped")
        return results

    async def restart_service(self, name: str) -> bool:
        """
        Restart a specific service.
        
        Args:
            name: Name of the service to restart
            
        Returns:
            True if restart successful, False otherwise
        """
        try:
            if name not in self._services:
                logger.error(f"Service {name} not found")
                return False
            
            service_info = self._services[name]
            
            # Stop service
            if hasattr(service_info.instance, 'stop'):
                await service_info.instance.stop()
            
            service_info.status = ServiceStatus.STOPPED
            
            # Start service
            if hasattr(service_info.instance, 'start'):
                success = await service_info.instance.start()
                if success:
                    service_info.status = ServiceStatus.RUNNING
                    service_info.started_at = datetime.now()
                    logger.info(f"Service {name} restarted successfully")
                    return True
                else:
                    service_info.status = ServiceStatus.ERROR
                    logger.error(f"Service {name} failed to restart")
                    return False
            else:
                service_info.status = ServiceStatus.RUNNING
                logger.info(f"Service {name} restarted successfully (no start/stop methods)")
                return True
                
        except Exception as e:
            logger.error(f"Error restarting service {name}: {e}")
            if name in self._services:
                self._services[name].status = ServiceStatus.ERROR
            return False

    # Health Monitoring

    async def check_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Check health of all services.
        
        Returns:
            Dictionary mapping service names to health status
        """
        health_results = {}
        logger.debug("Checking health of all services...")
        
        for name, service_info in self._services.items():
            try:
                if hasattr(service_info.instance, 'get_health_status'):
                    health_status = await service_info.instance.get_health_status()
                    health_results[name] = health_status
                    service_info.health_status = health_status.get('status', 'unknown')
                    service_info.last_health_check = datetime.now()
                else:
                    # Service doesn't have health check method
                    health_results[name] = {
                        'status': 'unknown',
                        'message': 'No health check method available'
                    }
                    service_info.health_status = 'unknown'
                    
            except Exception as e:
                health_results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'message': 'Health check failed'
                }
                service_info.health_status = 'error'
                logger.error(f"Health check failed for service {name}: {e}")
        
        return health_results

    def get_overall_health_status(self) -> Dict[str, Any]:
        """
        Get overall health status of the registry.
        
        Returns:
            Overall health status information
        """
        if not self._services:
            return {
                'status': 'unknown',
                'message': 'No services registered',
                'healthy_count': 0,
                'warning_count': 0,
                'critical_count': 0,
                'total_count': 0
            }
        
        healthy_count = sum(1 for s in self._services.values() if s.health_status == 'healthy')
        warning_count = sum(1 for s in self._services.values() if s.health_status == 'warning')
        critical_count = sum(1 for s in self._services.values() if s.health_status == 'critical')
        total_count = len(self._services)
        
        # Determine overall status
        if critical_count > 0:
            overall_status = 'critical'
        elif warning_count > 0:
            overall_status = 'warning'
        elif healthy_count == total_count:
            overall_status = 'healthy'
        else:
            overall_status = 'unknown'
        
        return {
            'status': overall_status,
            'healthy_count': healthy_count,
            'warning_count': warning_count,
            'critical_count': critical_count,
            'total_count': total_count,
            'uptime': str(datetime.now() - self._registry_start_time)
        }

    # Configuration Management

    def update_service_config(self, service_name: str, config: Dict[str, Any]) -> bool:
        """
        Update configuration for a specific service.
        
        Args:
            service_name: Name of the service
            config: New configuration
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if service_name not in self._services:
                logger.error(f"Service {service_name} not found")
                return False
            
            service_info = self._services[service_name]
            service_info.config.update(config)
            
            # Update service instance if it has update_config method
            if hasattr(service_info.instance, 'update_config'):
                service_info.instance.update_config(config)
            
            logger.info(f"Configuration updated for service {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration for service {service_name}: {e}")
            return False

    def get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service configuration or None if not found
        """
        service_info = self._services.get(service_name)
        return service_info.config if service_info else None

    # Registry Information

    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get comprehensive registry information.
        
        Returns:
            Registry information and statistics
        """
        return {
            'total_services': len(self._services),
            'running_services': sum(1 for s in self._services.values() if s.status == ServiceStatus.RUNNING),
            'stopped_services': sum(1 for s in self._services.values() if s.status == ServiceStatus.STOPPED),
            'error_services': sum(1 for s in self._services.values() if s.status == ServiceStatus.ERROR),
            'healthy_services': sum(1 for s in self._services.values() if s.health_status == 'healthy'),
            'warning_services': sum(1 for s in self._services.values() if s.health_status == 'warning'),
            'critical_services': sum(1 for s in self._services.values() if s.health_status == 'critical'),
            'total_dependencies': sum(len(deps) for deps in self._dependencies.values()),
            'is_initialized': self._is_initialized,
            'uptime': str(datetime.now() - self._registry_start_time),
            'circular_dependencies': len(self.check_circular_dependencies())
        }

    def is_initialized(self) -> bool:
        """Check if the registry is initialized."""
        return self._is_initialized

    def get_uptime(self) -> timedelta:
        """Get registry uptime."""
        return datetime.now() - self._registry_start_time
