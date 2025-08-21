"""
Base Services Package - Service Infrastructure Foundation
=======================================================

Provides the foundational infrastructure for all business logic services:
- BaseService: Abstract base class for all services
- ServiceRegistry: Service discovery and registration
- ServiceFactory: Service instantiation and management
- ServiceStatus: Service status enumeration
- ServiceCreationStrategy: Service creation strategy enumeration
"""

from .base_service import BaseService
from .service_registry import ServiceRegistry, ServiceStatus, ServiceInfo
from .service_factory import ServiceFactory, ServiceCreationStrategy, ServiceDefinition

__all__ = [
    # Base Service
    'BaseService',
    
    # Service Registry
    'ServiceRegistry',
    'ServiceStatus', 
    'ServiceInfo',
    
    # Service Factory
    'ServiceFactory',
    'ServiceCreationStrategy',
    'ServiceDefinition',
]

__version__ = "2.0.0"
__author__ = "AAS Data Modeling Engine Team"

# Convenience function to get the global service registry
_global_registry = None

def get_global_registry() -> ServiceRegistry:
    """Get the global service registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ServiceRegistry()
    return _global_registry

def set_global_registry(registry: ServiceRegistry) -> None:
    """Set the global service registry instance."""
    global _global_registry
    _global_registry = registry

# Convenience function to get the global service factory
_global_factory = None

def get_global_factory() -> ServiceFactory:
    """Get the global service factory instance."""
    global _global_factory
    if _global_factory is None:
        registry = get_global_registry()
        _global_factory = ServiceFactory(registry)
    return _global_factory

def set_global_factory(factory: ServiceFactory) -> None:
    """Set the global service factory instance."""
    global _global_factory
    _global_factory = factory

# Package-level features
def initialize_base_services():
    """Initialize the base services infrastructure."""
    registry = get_global_registry()
    factory = get_global_factory()
    
    print("🚀 AAS Data Modeling Engine - Base Services Infrastructure Initialized")
    print(f"📦 Version: {__version__}")
    print(f"🏭 Service Registry: {type(registry).__name__}")
    print(f"🏭 Service Factory: {type(factory).__name__}")
    print("✨ Ready for service registration and management!")

def get_base_services_info() -> dict:
    """Get information about the base services infrastructure."""
    registry = get_global_registry()
    factory = get_global_factory()
    
    return {
        'version': __version__,
        'author': __author__,
        'registry_info': registry.get_registry_info() if registry else None,
        'factory_info': factory.get_service_statistics() if factory else None,
        'registry_uptime': str(registry.get_uptime()) if registry else None,
        'factory_uptime': str(factory.get_uptime()) if factory else None
    }

# Auto-initialize when package is imported
if __name__ != "__main__":
    # This will run when the package is imported
    pass
