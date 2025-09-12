"""
Twin Registry Services Module

This module provides thin table operations for Twin Registry database tables,
leveraging engine infrastructure for enterprise features.

Services:
- TwinRegistryService: Handles twin_registry table operations
- TwinRegistryMetricsService: Handles twin_registry_metrics table operations

All business logic is delegated to core services. These services are thin
and focused solely on table CRUD operations with enterprise-grade features.
"""

from .twin_registry_service import TwinRegistryService
from .twin_registry_metrics_service import TwinRegistryMetricsService

__all__ = [
    "TwinRegistryService",
    "TwinRegistryMetricsService"
]

# Service Standards Compliance
__service_standards__ = {
    "TwinRegistryService": {
        "compliance": "World-Class",
        "features": [
            "Thin service (table operations only)",
            "Engine infrastructure integration",
            "Performance monitoring and profiling",
            "Security and RBAC integration",
            "Event-driven architecture",
            "Comprehensive logging and audit"
        ]
    },
    "TwinRegistryMetricsService": {
        "compliance": "World-Class",
        "features": [
            "Thin service (table operations only)",
            "Engine infrastructure integration",
            "Performance monitoring and profiling",
            "Security and RBAC integration",
            "Event-driven architecture",
            "Comprehensive logging and audit"
        ]
    }
}
