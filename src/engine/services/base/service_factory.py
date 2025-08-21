"""
Service Factory - Service Instantiation and Management
====================================================

Provides service creation and management with:
- Service instantiation with proper dependencies
- Configuration management
- Service pooling and caching
- Lazy loading support
- Dependency resolution
- Service lifecycle management
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Type, TypeVar, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import weakref

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceCreationStrategy(Enum):
    """Service creation strategy enumeration."""
    SINGLETON = "singleton"      # Single instance per service type
    PROTOTYPE = "prototype"      # New instance each time
    POOLED = "pooled"           # Pool of instances
    LAZY = "lazy"               # Create on first access


@dataclass
class ServiceDefinition:
    """Service definition container."""
    name: str
    service_type: Type
    factory_func: Optional[Callable] = None
    dependencies: List[str] = None
    config: Dict[str, Any] = None
    strategy: ServiceCreationStrategy = ServiceCreationStrategy.SINGLETON
    pool_size: int = 5
    max_instances: int = 100
    ttl_minutes: int = 30
    metadata: Dict[str, Any] = None


class ServiceFactory:
    """
    Factory for creating and managing service instances.
    
    Provides:
    - Service instantiation with dependency injection
    - Configuration management and validation
    - Service pooling and caching
    - Lazy loading support
    - Service lifecycle management
    """

    def __init__(self, registry=None):
        """
        Initialize the service factory.
        
        Args:
            registry: Service registry instance for dependency resolution
        """
        self.registry = registry
        self._service_definitions: Dict[str, ServiceDefinition] = {}
        self._instances: Dict[str, Any] = {}
        self._instance_pools: Dict[str, List[Any]] = {}
        self._instance_metadata: Dict[str, Dict[str, Any]] = {}
        self._creation_times: Dict[str, datetime] = {}
        self._access_counts: Dict[str, int] = {}
        
        logger.info("Service factory initialized")

    # Service Definition Management

    def register_service_definition(self, name: str, service_type: Type, 
                                   factory_func: Optional[Callable] = None,
                                   dependencies: List[str] = None,
                                   config: Dict[str, Any] = None,
                                   strategy: ServiceCreationStrategy = ServiceCreationStrategy.SINGLETON,
                                   pool_size: int = 5,
                                   max_instances: int = 100,
                                   ttl_minutes: int = 30,
                                   metadata: Dict[str, Any] = None) -> bool:
        """
        Register a service definition.
        
        Args:
            name: Unique service name
            service_type: Type/class of the service
            factory_func: Custom factory function for creating instances
            dependencies: List of service names this service depends on
            config: Service configuration
            strategy: Service creation strategy
            pool_size: Size of instance pool (for POOLED strategy)
            max_instances: Maximum number of instances to create
            ttl_minutes: Time-to-live for instances in minutes
            metadata: Additional service metadata
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            if name in self._service_definitions:
                logger.warning(f"Service definition {name} already registered, updating")
            
            service_def = ServiceDefinition(
                name=name,
                service_type=service_type,
                factory_func=factory_func,
                dependencies=dependencies or [],
                config=config or {},
                strategy=strategy,
                pool_size=pool_size,
                max_instances=max_instances,
                ttl_minutes=ttl_minutes,
                metadata=metadata or {}
            )
            
            self._service_definitions[name] = service_def
            
            # Initialize instance tracking
            self._instances[name] = None
            self._instance_pools[name] = []
            self._instance_metadata[name] = {}
            self._creation_times[name] = datetime.now()
            self._access_counts[name] = 0
            
            logger.info(f"Service definition {name} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service definition {name}: {e}")
            return False

    async def unregister_service_definition(self, name: str) -> bool:
        """
        Unregister a service definition.
        
        Args:
            name: Name of the service definition to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if name not in self._service_definitions:
                logger.warning(f"Service definition {name} not found")
                return False
            
            # Cleanup instances
            await self._cleanup_service_instances(name)
            
            # Remove definition and tracking
            del self._service_definitions[name]
            del self._instances[name]
            del self._instance_pools[name]
            del self._instance_metadata[name]
            del self._creation_times[name]
            del self._access_counts[name]
            
            logger.info(f"Service definition {name} unregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service definition {name}: {e}")
            return False

    def get_service_definition(self, name: str) -> Optional[ServiceDefinition]:
        """
        Get service definition by name.
        
        Args:
            name: Name of the service definition
            
        Returns:
            ServiceDefinition object or None if not found
        """
        return self._service_definitions.get(name)

    def list_service_definitions(self) -> List[str]:
        """Get list of all registered service definition names."""
        return list(self._service_definitions.keys())

    # Service Instance Creation

    async def create_service(self, name: str, **kwargs) -> Optional[Any]:
        """
        Create a service instance.
        
        Args:
            name: Name of the service to create
            **kwargs: Additional arguments for service creation
            
        Returns:
            Service instance or None if creation failed
        """
        try:
            if name not in self._service_definitions:
                logger.error(f"Service definition {name} not found")
                return None
            
            service_def = self._service_definitions[name]
            self._access_counts[name] += 1
            
            # Check if we should create a new instance based on strategy
            if service_def.strategy == ServiceCreationStrategy.SINGLETON:
                return await self._get_or_create_singleton(name, **kwargs)
            elif service_def.strategy == ServiceCreationStrategy.PROTOTYPE:
                return await self._create_prototype(name, **kwargs)
            elif service_def.strategy == ServiceCreationStrategy.POOLED:
                return await self._get_or_create_pooled_instance(name, **kwargs)
            elif service_def.strategy == ServiceCreationStrategy.LAZY:
                return await self._get_or_create_lazy_instance(name, **kwargs)
            else:
                logger.error(f"Unknown service creation strategy: {service_def.strategy}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create service {name}: {e}")
            return None

    async def _get_or_create_singleton(self, name: str, **kwargs) -> Optional[Any]:
        """Get or create singleton instance."""
        if self._instances[name] is None:
            instance = await self._create_instance(name, **kwargs)
            if instance:
                self._instances[name] = instance
                self._instance_metadata[name] = {
                    'created_at': datetime.now(),
                    'strategy': 'singleton',
                    'access_count': 0
                }
            return instance
        else:
            # Update access count
            if name in self._instance_metadata:
                self._instance_metadata[name]['access_count'] += 1
            return self._instances[name]

    async def _create_prototype(self, name: str, **kwargs) -> Optional[Any]:
        """Create new prototype instance."""
        return await self._create_instance(name, **kwargs)

    async def _get_or_create_pooled_instance(self, name: str, **kwargs) -> Optional[Any]:
        """Get or create pooled instance."""
        service_def = self._service_definitions[name]
        pool = self._instance_pools[name]
        
        # Try to get from pool
        if pool:
            instance = pool.pop()
            # Update access count
            if name in self._instance_metadata:
                self._instance_metadata[name]['access_count'] += 1
            return instance
        
        # Create new instance if pool is empty and we haven't reached max
        current_instances = len(pool) + (1 if self._instances[name] else 0)
        if current_instances < service_def.max_instances:
            instance = await self._create_instance(name, **kwargs)
            if instance:
                self._instances[name] = instance
                self._instance_metadata[name] = {
                    'created_at': datetime.now(),
                    'strategy': 'pooled',
                    'access_count': 1
                }
            return instance
        else:
            logger.warning(f"Maximum instances reached for service {name}")
            return None

    async def _get_or_create_lazy_instance(self, name: str, **kwargs) -> Optional[Any]:
        """Get or create lazy instance."""
        if self._instances[name] is None:
            instance = await self._create_instance(name, **kwargs)
            if instance:
                self._instances[name] = instance
                self._instance_metadata[name] = {
                    'created_at': datetime.now(),
                    'strategy': 'lazy',
                    'access_count': 1
                }
            return instance
        else:
            # Update access count
            if name in self._instance_metadata:
                self._instance_metadata[name]['access_count'] += 1
            return self._instances[name]

    async def _create_instance(self, name: str, **kwargs) -> Optional[Any]:
        """Create a new service instance."""
        try:
            service_def = self._service_definitions[name]
            
            # Resolve dependencies
            resolved_dependencies = await self._resolve_dependencies(service_def.dependencies)
            
            # Create instance using factory function or constructor
            if service_def.factory_func:
                instance = service_def.factory_func(**resolved_dependencies, **kwargs)
            else:
                # Use constructor with resolved dependencies
                constructor_kwargs = {**resolved_dependencies, **kwargs}
                instance = service_def.service_type(**constructor_kwargs)
            
            # Initialize instance if it has start method
            if hasattr(instance, 'start'):
                await instance.start()
            
            logger.info(f"Created instance of service {name}")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create instance of service {name}: {e}")
            return None

    async def _resolve_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Resolve service dependencies."""
        resolved = {}
        
        for dep_name in dependencies:
            if self.registry:
                dep_instance = self.registry.get_service(dep_name)
                if dep_instance:
                    resolved[dep_name] = dep_instance
                else:
                    logger.warning(f"Dependency {dep_name} not found in registry")
            else:
                logger.warning(f"No registry available for dependency resolution")
        
        return resolved

    # Service Instance Management

    async def get_service(self, name: str) -> Optional[Any]:
        """
        Get existing service instance.
        
        Args:
            name: Name of the service
            
        Returns:
            Service instance or None if not found
        """
        if name not in self._service_definitions:
            return None
        
        service_def = self._service_definitions[name]
        
        if service_def.strategy == ServiceCreationStrategy.SINGLETON:
            return self._instances[name]
        elif service_def.strategy == ServiceCreationStrategy.PROTOTYPE:
            # For prototype, always create new instance
            return await self.create_service(name)
        elif service_def.strategy == ServiceCreationStrategy.POOLED:
            # For pooled, try to get from pool or create new
            return await self._get_or_create_pooled_instance(name)
        elif service_def.strategy == ServiceCreationStrategy.LAZY:
            return self._instances[name]
        else:
            return None

    def return_to_pool(self, name: str, instance: Any) -> bool:
        """
        Return instance to pool (for pooled strategy).
        
        Args:
            name: Name of the service
            instance: Instance to return to pool
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if name not in self._service_definitions:
                return False
            
            service_def = self._service_definitions[name]
            if service_def.strategy != ServiceCreationStrategy.POOLED:
                return False
            
            pool = self._instance_pools[name]
            if len(pool) < service_def.pool_size:
                pool.append(instance)
                logger.debug(f"Returned instance to pool for service {name}")
                return True
            else:
                logger.debug(f"Pool full for service {name}, discarding instance")
                return False
                
        except Exception as e:
            logger.error(f"Failed to return instance to pool for service {name}: {e}")
            return False

    async def _cleanup_service_instances(self, name: str) -> None:
        """Cleanup service instances."""
        try:
            # Stop and cleanup singleton instance
            if self._instances[name] and hasattr(self._instances[name], 'stop'):
                await self._instances[name].stop()
            
            # Stop and cleanup pooled instances
            pool = self._instance_pools[name]
            for instance in pool:
                if hasattr(instance, 'stop'):
                    await instance.stop()
            
            # Clear tracking
            self._instances[name] = None
            self._instance_pools[name].clear()
            
        except Exception as e:
            logger.error(f"Failed to cleanup instances for service {name}: {e}")

    # Configuration Management

    def update_service_config(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Update configuration for a service.
        
        Args:
            name: Name of the service
            config: New configuration
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if name not in self._service_definitions:
                logger.error(f"Service definition {name} not found")
                return False
            
            service_def = self._service_definitions[name]
            service_def.config.update(config)
            
            # Update existing instances if they have update_config method
            if self._instances[name] and hasattr(self._instances[name], 'update_config'):
                self._instances[name].update_config(config)
            
            # Update pooled instances
            for instance in self._instance_pools[name]:
                if hasattr(instance, 'update_config'):
                    instance.update_config(config)
            
            logger.info(f"Configuration updated for service {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration for service {name}: {e}")
            return False

    def get_service_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a service.
        
        Args:
            name: Name of the service
            
        Returns:
            Service configuration or None if not found
        """
        service_def = self._service_definitions.get(name)
        return service_def.config if service_def else None

    # Service Lifecycle Management

    async def start_all_services(self) -> Dict[str, bool]:
        """
        Start all singleton and lazy services.
        
        Returns:
            Dictionary mapping service names to start success status
        """
        results = {}
        
        for name, service_def in self._service_definitions.items():
            if service_def.strategy in [ServiceCreationStrategy.SINGLETON, ServiceCreationStrategy.LAZY]:
                try:
                    # Create instance if it doesn't exist
                    if self._instances[name] is None:
                        instance = await self.create_service(name)
                        if instance:
                            results[name] = True
                        else:
                            results[name] = False
                    else:
                        # Instance already exists, just start it
                        if hasattr(self._instances[name], 'start'):
                            success = await self._instances[name].start()
                            results[name] = success
                        else:
                            results[name] = True
                except Exception as e:
                    logger.error(f"Failed to start service {name}: {e}")
                    results[name] = False
        
        return results

    async def stop_all_services(self) -> Dict[str, bool]:
        """
        Stop all services.
        
        Returns:
            Dictionary mapping service names to stop success status
        """
        results = {}
        
        for name in self._service_definitions:
            try:
                success = await self._cleanup_service_instances(name)
                results[name] = success
            except Exception as e:
                logger.error(f"Failed to stop service {name}: {e}")
                results[name] = False
        
        return results

    # Monitoring and Statistics

    def get_service_statistics(self, name: str = None) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Args:
            name: Specific service name or None for all services
            
        Returns:
            Service statistics
        """
        if name:
            return self._get_single_service_statistics(name)
        else:
            return self._get_all_services_statistics()

    def _get_single_service_statistics(self, name: str) -> Dict[str, Any]:
        """Get statistics for a single service."""
        if name not in self._service_definitions:
            return {'error': f'Service {name} not found'}
        
        service_def = self._service_definitions[name]
        metadata = self._instance_metadata.get(name, {})
        
        return {
            'name': name,
            'type': service_def.service_type.__name__,
            'strategy': service_def.strategy.value,
            'dependencies': service_def.dependencies,
            'config': service_def.config,
            'pool_size': service_def.pool_size,
            'max_instances': service_def.max_instances,
            'ttl_minutes': service_def.ttl_minutes,
            'has_instance': self._instances[name] is not None,
            'pool_count': len(self._instance_pools[name]),
            'access_count': self._access_counts[name],
            'created_at': metadata.get('created_at'),
            'strategy_info': metadata.get('strategy'),
            'instance_access_count': metadata.get('access_count', 0)
        }

    def _get_all_services_statistics(self) -> Dict[str, Any]:
        """Get statistics for all services."""
        total_services = len(self._service_definitions)
        total_instances = sum(1 for inst in self._instances.values() if inst is not None)
        total_pooled = sum(len(pool) for pool in self._instance_pools.values())
        
        strategy_counts = {}
        for service_def in self._service_definitions.values():
            strategy = service_def.strategy.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            'total_services': total_services,
            'total_instances': total_instances,
            'total_pooled_instances': total_pooled,
            'strategy_distribution': strategy_counts,
            'services': {name: self._get_single_service_statistics(name) 
                        for name in self._service_definitions.keys()}
        }

    def get_uptime(self) -> timedelta:
        """Get factory uptime."""
        return datetime.now() - min(self._creation_times.values()) if self._creation_times else timedelta(0)
