"""
Services Package - AAS Data Modeling Engine
==========================================

This package provides a comprehensive service layer for the AAS Data Modeling Engine,
implementing a modular, scalable architecture for business operations.

Service Layers:
1. Base Service Infrastructure - Foundation services and patterns
2. Core System Services - System-level services (registry, metrics, health)
3. Business Domain Services - Core business logic services
4. Authentication Services - User and access management (planned)
5. Data Governance Services - Data lineage and quality (planned)
6. Integration Services - External system integration (planned)

Architecture:
- Modular design with clear separation of concerns
- Service registry for discovery and management
- Factory pattern for service instantiation
- Observer pattern for cross-service communication
- Comprehensive monitoring and health checks
"""

# Base Service Infrastructure
from .base import (
    BaseService, ServiceRegistry, ServiceStatus, ServiceInfo,
    ServiceFactory, ServiceCreationStrategy, ServiceDefinition,
    get_global_registry, get_global_factory,
    set_global_registry, set_global_factory,
    initialize_base_services, get_base_services_info
)

# Core System Services
from .core_system import (
    RegistryService, MetricsService, HealthService,
    initialize_core_system_services
)

# Business Domain Services
from .business_domain import (
    OrganizationService, ProjectService, FileService, WorkflowService,
    initialize_business_domain_services, get_business_domain_services_info,
    stop_business_domain_services
)

# Package version
__version__ = "3.0.0"

# Export all components
__all__ = [
    # Base Service Infrastructure
    'BaseService', 'ServiceRegistry', 'ServiceStatus', 'ServiceInfo',
    'ServiceFactory', 'ServiceCreationStrategy', 'ServiceDefinition',
    'get_global_registry', 'get_global_factory',
    'set_global_registry', 'set_global_factory',
    'initialize_base_services', 'get_base_services_info',
    
    # Core System Services
    'RegistryService', 'MetricsService', 'HealthService', 'initialize_core_system_services',
    
    # Business Domain Services
    'OrganizationService', 'ProjectService', 'FileService', 'WorkflowService',
    'initialize_business_domain_services', 'get_business_domain_services_info',
    'stop_business_domain_services',
    
    # Package Info
    '__version__'
]

async def initialize_services():
    """Initialize the complete services infrastructure."""
    # Initialize base services
    initialize_base_services()
    
    # Initialize core system services
    await initialize_core_system_services()
    
    # Initialize business domain services
    await initialize_business_domain_services()
    
    print("🚀 AAS Data Modeling Engine - Services Package Initialized")
    print(f"📦 Version: {__version__}")
    print("🏭 Service Layers: Base Infrastructure, Core System Services, Business Domain Services")
    print("🔧 Status: All service layers operational")
    print("✨ Next: Implement authentication and data governance services")

async def get_services_info():
    """Get comprehensive information about all services."""
    try:
        services_info = {
            'package_version': __version__,
            'base_services': get_base_services_info(),
            'core_system_services': await get_core_system_services_info(),
            'business_domain_services': await get_business_domain_services_info()
        }
        
        return services_info
        
    except Exception as e:
        return {
            'package_version': __version__,
            'error': f"Failed to get services info: {e}"
        }

async def stop_all_services():
    """Stop all services gracefully."""
    try:
        # Stop business domain services
        await stop_business_domain_services()
        
        # Stop core system services
        await stop_core_system_services()
        
        print("🛑 All services stopped gracefully")
        
    except Exception as e:
        print(f"❌ Error stopping services: {e}")

# Import core system services info function
from .core_system import get_core_system_services_info, stop_core_system_services
