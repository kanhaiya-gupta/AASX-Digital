"""
Registry Service - Core System Service
=====================================

Provides centralized service registration and discovery for the entire system.
This service extends the base service infrastructure with advanced registry capabilities.

Features:
- Service registration and discovery
- Service metadata management
- Service dependency tracking
- Service health aggregation
- Service routing and load balancing
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from ..base import BaseService
from ...models.base_model import BaseModel
from ...repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


@dataclass
class ServiceMetadata:
    """Service metadata for registration."""
    service_id: str
    service_name: str
    service_type: str
    version: str
    status: str
    health_score: float
    last_heartbeat: datetime
    capabilities: List[str]
    dependencies: List[str]
    endpoints: Dict[str, str]
    metadata: Dict[str, Any]


class RegistryService(BaseService[BaseModel, BaseRepository]):
    """
    Core registry service for system-wide service management.
    
    Provides:
    - Service registration and discovery
    - Service health monitoring
    - Service dependency management
    - Service routing and load balancing
    """

    def __init__(self, repository: Optional[BaseRepository] = None):
        super().__init__(repository, "RegistryService")
        
        # Service registry
        self._services: Dict[str, ServiceMetadata] = {}
        self._service_types: Dict[str, Set[str]] = {}
        self._service_endpoints: Dict[str, Dict[str, str]] = {}
        
        # Health tracking
        self._health_history: Dict[str, List[Dict[str, Any]]] = {}
        self._health_thresholds = {
            'critical': 0.3,
            'warning': 0.7,
            'healthy': 1.0
        }
        
        # Load balancing
        self._load_balancers: Dict[str, List[str]] = {}
        self._round_robin_index: Dict[str, int] = {}
        
        logger.info("Registry service initialized")

    async def _initialize_service_resources(self) -> None:
        """Initialize registry service resources."""
        # Initialize health monitoring
        await self._start_health_monitoring()
        
        # Initialize service discovery
        await self._discover_existing_services()
        
        logger.info("Registry service resources initialized")

    async def _cleanup_service_resources(self) -> None:
        """Cleanup registry service resources."""
        # Stop health monitoring
        await self._stop_health_monitoring()
        
        # Cleanup service registrations
        await self._cleanup_all_services()
        
        logger.info("Registry service resources cleaned up")

    async def _discover_existing_services(self) -> None:
        """Discover existing services in the system."""
        try:
            # This method can be used to discover services from external sources
            # For now, we'll just log that discovery is complete
            logger.info("Service discovery completed")
        except Exception as e:
            logger.error(f"Failed to discover existing services: {e}")

    async def check_circular_dependencies(self) -> List[List[str]]:
        """Check for circular dependencies between services."""
        try:
            circular_deps = []
            visited = set()
            rec_stack = set()
            
            def dfs(service_id: str, path: List[str]) -> None:
                if service_id in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(service_id)
                    cycle = path[cycle_start:] + [service_id]
                    circular_deps.append(cycle)
                    return
                
                if service_id in visited:
                    return
                
                visited.add(service_id)
                rec_stack.add(service_id)
                path.append(service_id)
                
                if service_id in self._services:
                    service = self._services[service_id]
                    for dep in service.dependencies:
                        if dep in self._services:
                            dfs(dep, path.copy())
                
                rec_stack.remove(service_id)
                path.pop()
            
            # Check all services
            for service_id in self._services:
                if service_id not in visited:
                    dfs(service_id, [])
            
            return circular_deps
            
        except Exception as e:
            logger.error(f"Failed to check circular dependencies: {e}")
            return []

    async def get_service_info(self) -> Dict[str, Any]:
        """Get registry service information."""
        return {
            'service_name': self.service_name,
            'total_services': len(self._services),
            'service_types': list(self._service_types.keys()),
            'health_status': self.health_status,
            'uptime': str(self.get_uptime()),
            'last_health_check': self.last_health_check.isoformat()
        }

    # Service Registration and Discovery

    async def register_service(self, service_id: str, service_name: str, 
                             service_type: str, version: str = "1.0.0",
                             capabilities: List[str] = None, 
                             dependencies: List[str] = None,
                             endpoints: Dict[str, str] = None,
                             metadata: Dict[str, Any] = None) -> bool:
        """
        Register a new service in the registry.
        
        Args:
            service_id: Unique service identifier
            service_name: Human-readable service name
            service_type: Type/category of service
            version: Service version
            capabilities: List of service capabilities
            dependencies: List of service dependencies
            endpoints: Service endpoints (API, health, etc.)
            metadata: Additional service metadata
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            if service_id in self._services:
                logger.warning(f"Service {service_id} already registered, updating")
            
            # Create service metadata
            service_meta = ServiceMetadata(
                service_id=service_id,
                service_name=service_name,
                service_type=service_type,
                version=version,
                status='active',
                health_score=1.0,
                last_heartbeat=datetime.now(),
                capabilities=capabilities or [],
                dependencies=dependencies or [],
                endpoints=endpoints or {},
                metadata=metadata or {}
            )
            
            # Register service
            self._services[service_id] = service_meta
            
            # Update service type index
            if service_type not in self._service_types:
                self._service_types[service_type] = set()
            self._service_types[service_type].add(service_id)
            
            # Update endpoints index
            self._service_endpoints[service_id] = endpoints or {}
            
            # Initialize health tracking
            self._health_history[service_id] = []
            
            # Initialize load balancer
            if service_type not in self._load_balancers:
                self._load_balancers[service_type] = []
            self._load_balancers[service_type].append(service_id)
            self._round_robin_index[service_type] = 0
            
            logger.info(f"Service {service_id} ({service_name}) registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service_id}: {e}")
            return False

    async def unregister_service(self, service_id: str) -> bool:
        """
        Unregister a service from the registry.
        
        Args:
            service_id: Service identifier to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if service_id not in self._services:
                logger.warning(f"Service {service_id} not found in registry")
                return False
            
            service_meta = self._services[service_id]
            service_type = service_meta.service_type
            
            # Remove from services
            del self._services[service_id]
            
            # Remove from service types
            if service_type in self._service_types:
                self._service_types[service_type].discard(service_id)
                if not self._service_types[service_type]:
                    del self._service_types[service_type]
            
            # Remove from endpoints
            if service_id in self._service_endpoints:
                del self._service_endpoints[service_id]
            
            # Remove from health tracking
            if service_id in self._health_history:
                del self._health_history[service_id]
            
            # Remove from load balancers
            if service_type in self._load_balancers:
                self._load_balancers[service_type].remove(service_id)
                if not self._load_balancers[service_type]:
                    del self._load_balancers[service_type]
                    del self._round_robin_index[service_type]
            
            logger.info(f"Service {service_id} unregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service {service_id}: {e}")
            return False

    async def discover_service(self, service_type: str = None, 
                             capability: str = None) -> List[ServiceMetadata]:
        """
        Discover services based on criteria.
        
        Args:
            service_type: Filter by service type
            capability: Filter by required capability
            
        Returns:
            List of matching service metadata
        """
        try:
            matching_services = []
            
            for service_id, service_meta in self._services.items():
                # Check if service is active
                if service_meta.status != 'active':
                    continue
                
                # Filter by service type
                if service_type and service_meta.service_type != service_type:
                    continue
                
                # Filter by capability
                if capability and capability not in service_meta.capabilities:
                    continue
                
                matching_services.append(service_meta)
            
            logger.debug(f"Discovered {len(matching_services)} services matching criteria")
            return matching_services
            
        except Exception as e:
            logger.error(f"Service discovery failed: {e}")
            return []

    async def get_service(self, service_id: str) -> Optional[ServiceMetadata]:
        """
        Get service metadata by ID.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Service metadata or None if not found
        """
        return self._services.get(service_id)

    async def list_services(self, service_type: str = None) -> List[ServiceMetadata]:
        """
        List all registered services.
        
        Args:
            service_type: Optional filter by service type
            
        Returns:
            List of service metadata
        """
        if service_type:
            return [meta for meta in self._services.values() 
                   if meta.service_type == service_type]
        return list(self._services.values())

    # Health Monitoring

    async def _start_health_monitoring(self) -> None:
        """Start health monitoring for all services."""
        logger.info("Starting health monitoring for all services")
        
        # Schedule periodic health checks
        asyncio.create_task(self._health_monitoring_loop())

    async def _stop_health_monitoring(self) -> None:
        """Stop health monitoring."""
        logger.info("Stopping health monitoring")

    async def _health_monitoring_loop(self) -> None:
        """Main health monitoring loop."""
        while self.is_active:
            try:
                await self._check_all_services_health()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)

    async def _check_all_services_health(self) -> None:
        """Check health of all registered services."""
        for service_id in list(self._services.keys()):
            try:
                await self._check_service_health(service_id)
            except Exception as e:
                logger.error(f"Failed to check health for service {service_id}: {e}")

    async def _check_service_health(self, service_id: str) -> None:
        """Check health of a specific service."""
        try:
            service_meta = self._services[service_id]
            
            # Simulate health check (in real implementation, this would call service endpoints)
            health_score = await self._perform_service_health_check(service_meta)
            
            # Update service health
            service_meta.health_score = health_score
            service_meta.last_heartbeat = datetime.now()
            
            # Update status based on health score
            if health_score <= self._health_thresholds['critical']:
                service_meta.status = 'critical'
            elif health_score <= self._health_thresholds['warning']:
                service_meta.status = 'warning'
            else:
                service_meta.status = 'healthy'
            
            # Record health history
            health_record = {
                'timestamp': datetime.now().isoformat(),
                'health_score': health_score,
                'status': service_meta.status
            }
            self._health_history[service_id].append(health_record)
            
            # Keep only last 100 health records
            if len(self._health_history[service_id]) > 100:
                self._health_history[service_id] = self._health_history[service_id][-100:]
            
            logger.debug(f"Service {service_id} health: {health_score:.2f} ({service_meta.status})")
            
        except Exception as e:
            logger.error(f"Health check failed for service {service_id}: {e}")

    async def _perform_service_health_check(self, service_meta: ServiceMetadata) -> float:
        """
        Perform actual health check for a service.
        
        In a real implementation, this would:
        - Call service health endpoints
        - Check response times
        - Verify service functionality
        - Return health score (0.0 to 1.0)
        """
        # For now, simulate health check
        # In production, implement actual health checking logic
        import random
        return random.uniform(0.8, 1.0)

    async def get_system_health_summary(self) -> Dict[str, Any]:
        """
        Get overall system health summary.
        
        Returns:
            System health summary with service counts and overall status
        """
        try:
            total_services = len(self._services)
            healthy_services = sum(1 for s in self._services.values() if s.status == 'healthy')
            warning_services = sum(1 for s in self._services.values() if s.status == 'warning')
            critical_services = sum(1 for s in self._services.values() if s.status == 'critical')
            
            overall_health = 'healthy'
            if critical_services > 0:
                overall_health = 'critical'
            elif warning_services > 0:
                overall_health = 'warning'
            
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_health': overall_health,
                'total_services': total_services,
                'healthy_services': healthy_services,
                'warning_services': warning_services,
                'critical_services': critical_services,
                'health_percentage': (healthy_services / total_services * 100) if total_services > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health summary: {e}")
            return {'error': str(e)}

    # Load Balancing

    async def get_service_instance(self, service_type: str, 
                                 strategy: str = 'round_robin') -> Optional[str]:
        """
        Get a service instance for load balancing.
        
        Args:
            service_type: Type of service needed
            strategy: Load balancing strategy ('round_robin', 'health_based', 'random')
            
        Returns:
            Service ID or None if no service available
        """
        try:
            if service_type not in self._load_balancers:
                return None
            
            available_services = [sid for sid in self._load_balancers[service_type]
                                if self._services[sid].status in ['healthy', 'warning']]
            
            if not available_services:
                return None
            
            if strategy == 'round_robin':
                return self._get_round_robin_instance(service_type, available_services)
            elif strategy == 'health_based':
                return self._get_health_based_instance(available_services)
            elif strategy == 'random':
                import random
                return random.choice(available_services)
            else:
                return available_services[0]  # Default to first available
                
        except Exception as e:
            logger.error(f"Load balancing failed for {service_type}: {e}")
            return None

    def _get_round_robin_instance(self, service_type: str, 
                                 available_services: List[str]) -> str:
        """Get next service instance using round-robin strategy."""
        if service_type not in self._round_robin_index:
            self._round_robin_index[service_type] = 0
        
        current_index = self._round_robin_index[service_type]
        service_id = available_services[current_index % len(available_services)]
        
        # Update index for next request
        self._round_robin_index[service_type] = (current_index + 1) % len(available_services)
        
        return service_id

    def _get_health_based_instance(self, available_services: List[str]) -> str:
        """Get service instance with best health score."""
        best_service = None
        best_health = -1
        
        for service_id in available_services:
            health_score = self._services[service_id].health_score
            if health_score > best_health:
                best_health = health_score
                best_service = service_id
        
        return best_service or available_services[0]

    # Service Dependencies

    async def get_service_dependencies(self, service_id: str) -> List[str]:
        """Get dependencies for a service."""
        service_meta = self._services.get(service_id)
        return service_meta.dependencies if service_meta else []

    async def get_dependent_services(self, service_id: str) -> List[str]:
        """Get services that depend on the specified service."""
        dependent_services = []
        for sid, service_meta in self._services.items():
            if service_id in service_meta.dependencies:
                dependent_services.append(sid)
        return dependent_services

    async def check_dependency_health(self, service_id: str) -> Dict[str, Any]:
        """Check health of service dependencies."""
        try:
            dependencies = await self.get_service_dependencies(service_id)
            dependency_health = {}
            
            for dep_id in dependencies:
                dep_meta = self._services.get(dep_id)
                if dep_meta:
                    dependency_health[dep_id] = {
                        'name': dep_meta.service_name,
                        'status': dep_meta.status,
                        'health_score': dep_meta.health_score,
                        'last_heartbeat': dep_meta.last_heartbeat.isoformat()
                    }
                else:
                    dependency_health[dep_id] = {'status': 'not_found'}
            
            return {
                'service_id': service_id,
                'dependencies': dependency_health,
                'overall_dependency_health': 'healthy' if all(
                    dep['status'] in ['healthy', 'warning'] for dep in dependency_health.values()
                ) else 'critical'
            }
            
        except Exception as e:
            logger.error(f"Failed to check dependency health for {service_id}: {e}")
            return {'error': str(e)}

    # Cleanup

    async def _cleanup_all_services(self) -> None:
        """Cleanup all service registrations."""
        try:
            service_ids = list(self._services.keys())
            for service_id in service_ids:
                await self.unregister_service(service_id)
        except Exception as e:
            logger.error(f"Failed to cleanup services: {e}")

    # Statistics and Reporting

    async def get_registry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics."""
        try:
            return {
                'total_services': len(self._services),
                'service_types': {st: len(services) for st, services in self._service_types.items()},
                'health_distribution': {
                    'healthy': sum(1 for s in self._services.values() if s.status == 'healthy'),
                    'warning': sum(1 for s in self._services.values() if s.status == 'warning'),
                    'critical': sum(1 for s in self._services.values() if s.status == 'critical')
                },
                'load_balancers': {st: len(services) for st, services in self._load_balancers.items()},
                'uptime': str(self.get_uptime()),
                'last_health_check': self.last_health_check.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get registry statistics: {e}")
            return {'error': str(e)}
