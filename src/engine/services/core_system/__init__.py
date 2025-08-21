"""
Core System Services Package
============================

This package contains the core system services that provide fundamental
infrastructure capabilities for the entire system.

Services:
- RegistryService: Service registration, discovery, and load balancing
- MetricsService: Metrics collection, aggregation, and analysis
- HealthService: System-wide health monitoring and management

These services extend the base service infrastructure and provide
enterprise-grade system management capabilities.
"""

from .registry_service import (
    RegistryService,
    ServiceMetadata
)

from .metrics_service import (
    MetricsService,
    MetricType,
    MetricDefinition,
    MetricValue,
    MetricAggregation
)

from .health_service import (
    HealthService,
    HealthStatus,
    HealthCheckType,
    HealthCheck,
    HealthCheckResult,
    ServiceHealth,
    SystemHealth
)

# Convenience functions for accessing core system services
async def get_registry_service() -> RegistryService:
    """Get the global registry service instance."""
    from ..base import get_global_registry
    registry = get_global_registry()
    return registry.get_service("registry_service")

async def get_metrics_service() -> MetricsService:
    """Get the global metrics service instance."""
    from ..base import get_global_registry
    registry = get_global_registry()
    return registry.get_service("metrics_service")

async def get_health_service() -> HealthService:
    """Get the global health service instance."""
    from ..base import get_global_registry
    registry = get_global_registry()
    return registry.get_service("health_service")

async def get_core_system_services_info() -> dict:
    """Get information about all core system services."""
    try:
        from ..base import get_global_registry
        registry = get_global_registry()
        
        services_info = {}
        
        # Get registry service info
        try:
            registry_service = await get_registry_service()
            services_info['registry_service'] = {
                'name': registry_service.service_name,
                'status': registry_service.get_service_status().value,
                'health': registry_service.get_health_status().value,
                'uptime': str(registry_service.get_uptime())
            }
        except Exception as e:
            services_info['registry_service'] = {'error': str(e)}
        
        # Get metrics service info
        try:
            metrics_service = await get_metrics_service()
            services_info['metrics_service'] = {
                'name': metrics_service.service_name,
                'status': metrics_service.get_service_status().value,
                'health': metrics_service.get_health_status().value,
                'uptime': str(metrics_service.get_uptime()),
                'metrics_count': len(metrics_service.get_all_metric_definitions())
            }
        except Exception as e:
            services_info['metrics_service'] = {'error': str(e)}
        
        # Get health service info
        try:
            health_service = await get_health_service()
            services_info['health_service'] = {
                'name': health_service.service_name,
                'status': health_service.get_service_status().value,
                'health': health_service.get_health_status().value,
                'uptime': str(health_service.get_uptime()),
                'monitored_services': len(health_service.get_monitored_services())
            }
        except Exception as e:
            services_info['health_service'] = {'error': str(e)}
        
        return services_info
        
    except Exception as e:
        return {'error': f"Failed to get core system services info: {e}"}

async def stop_core_system_services() -> None:
    """Stop all core system services gracefully."""
    try:
        # Stop health service
        try:
            health_service = await get_health_service()
            await health_service.stop()
        except Exception as e:
            print(f"Warning: Failed to stop health service: {e}")
        
        # Stop metrics service
        try:
            metrics_service = await get_metrics_service()
            await metrics_service.stop()
        except Exception as e:
            print(f"Warning: Failed to stop metrics service: {e}")
        
        # Stop registry service last
        try:
            registry_service = await get_registry_service()
            await registry_service.stop()
        except Exception as e:
            print(f"Warning: Failed to stop registry service: {e}")
        
        print("🛑 Core system services stopped gracefully")
        
    except Exception as e:
        print(f"❌ Error stopping core system services: {e}")

# Package-level initialization
async def initialize_core_system_services() -> None:
    """Initialize all core system services."""
    from ..base import get_global_registry, get_global_factory
    
    registry = get_global_registry()
    factory = get_global_factory()
    
    # Create and register core system services
    registry_service = RegistryService()
    metrics_service = MetricsService()
    health_service = HealthService()
    
    # Start services
    await registry_service.start()
    await metrics_service.start()
    await health_service.start()
    
    # Register services in the registry
    await registry.register_service(
        "registry_service", registry_service.service_name,
        "core_system", "1.0.0",
        capabilities=["service_registration", "service_discovery", "load_balancing"],
        dependencies=[]
    )
    
    await registry.register_service(
        "metrics_service", metrics_service.service_name,
        "core_system", "1.0.0",
        capabilities=["metrics_collection", "metrics_aggregation", "real_time_streaming"],
        dependencies=[]
    )
    
    await registry.register_service(
        "health_service", health_service.service_name,
        "core_system", "1.0.0",
        capabilities=["health_monitoring", "health_check_orchestration", "alerting"],
        dependencies=[]
    )
    
    # Register services in the factory
    factory.register_service_definition(
        "registry_service", RegistryService,
        strategy="singleton"
    )
    
    factory.register_service_definition(
        "metrics_service", MetricsService,
        strategy="singleton"
    )
    
    factory.register_service_definition(
        "health_service", HealthService,
        strategy="singleton"
    )

# Export all public components
__all__ = [
    # Services
    'RegistryService',
    'MetricsService', 
    'HealthService',
    
    # Data models
    'ServiceMetadata',
    'MetricType',
    'MetricDefinition',
    'MetricValue',
    'MetricAggregation',
    'HealthStatus',
    'HealthCheckType',
    'HealthCheck',
    'HealthCheckResult',
    'ServiceHealth',
    'SystemHealth',
    
    # Convenience functions
    'get_registry_service',
    'get_metrics_service',
    'get_health_service',
    'get_core_system_services_info',
    'stop_core_system_services',
    
    # Initialization
    'initialize_core_system_services'
]
