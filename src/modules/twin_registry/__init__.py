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

Pure async implementation for modern architecture.
"""

__version__ = "3.3.0"
__description__ = "Digital Twin Registry System - Pure Async Implementation with Phase 3 Complete (Event System & Automation)"

# Core Models & Factory Functions
from .models.twin_registry import (
    TwinRegistry, 
    TwinRegistryQuery, 
    TwinRegistrySummary,
    create_twin_registry
)
from .models.twin_registry_metrics import (
    TwinRegistryMetrics, 
    MetricsQuery, 
    MetricsSummary,
    create_metrics
)

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

# Event System
from .events import TwinRegistryEventManager, EventType, EventPriority

__all__ = [
    # Models
    "TwinRegistry",
    "TwinRegistryMetadata",  # Backward compatibility
    "TwinRegistryQuery", 
    "TwinRegistrySummary",
    "TwinRegistryMetrics",
    "MetricsQuery",
    "MetricsSummary",
    
    # Factory Functions
    "create_twin_registry",
    "create_metrics",
    
    # Repositories
    "TwinRegistryRepository",
    "TwinRegistryMetricsRepository",
    
    # Services
    "TwinRegistryService",
    "TwinLifecycleService",
    "TwinRelationshipService", 
    "TwinInstanceService",
    "TwinSyncService",
    
    # Event System
    "TwinRegistryEventManager",
    "EventType",
    "EventPriority"
] 