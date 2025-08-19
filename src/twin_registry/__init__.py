"""
Twin Registry Module

A comprehensive digital twin registry system that provides:
- Twin registration and management
- Lifecycle tracking and management
- Relationship management between twins
- Instance management and versioning
- Synchronization and data consistency
- Performance monitoring and analytics

This module serves as a central hub for managing digital twins across
different workflows (extraction, generation, hybrid) without duplicating
data from other modules.
"""

__version__ = "3.0.0"
__description__ = "Digital Twin Registry System - Phase 2 Complete"

# Core Models
from .models.twin_registry import TwinRegistry, TwinRegistryQuery, TwinRegistrySummary
from .models.twin_registry_metrics import TwinRegistryMetrics, MetricsQuery, MetricsSummary

# Backward Compatibility
TwinRegistryMetadata = TwinRegistry

# Core Repositories
from .repositories.twin_registry_repository import TwinRegistryRepository
from .repositories.twin_registry_metrics_repository import TwinRegistryMetricsRepository

# Core Services
from .core.twin_registry_service import TwinRegistryService
from .core.twin_lifecycle_service import TwinLifecycleService
from .core.twin_relationship_service import TwinRelationshipService
from .core.twin_instance_service import TwinInstanceService
from .core.twin_sync_service import TwinSyncService

__all__ = [
    # Models
    "TwinRegistry",
    "TwinRegistryMetadata",  # Backward compatibility
    "TwinRegistryQuery", 
    "TwinRegistrySummary",
    "TwinRegistryMetrics",
    "MetricsQuery",
    "MetricsSummary",
    
    # Repositories
    "TwinRegistryRepository",
    "TwinRegistryMetricsRepository",
    
    # Services
    "TwinRegistryService",
    "TwinLifecycleService",
    "TwinRelationshipService", 
    "TwinInstanceService",
    "TwinSyncService"
] 