"""
Twin Registry Module

Modern twin lifecycle management and registry services.
Builds on top of src/shared/ infrastructure for managing existing digital twins.

Key Features:
- Twin lifecycle management (start/stop/sync)
- Relationship management (parent-child hierarchies)
- Instance management (versioning, history)
- Registry services (registration, lookup, status)
- Monitoring (health, performance, alerts)

Note: This module manages existing digital twins created by the AASX module.
No data analysis or AASX processing - pure twin management.
"""

__version__ = "2.0.0"
__author__ = "AASX Digital Twin Analytics Framework"
__description__ = "Modern twin lifecycle management and registry services"

# Import core services for easy access
from .core.twin_registry_service import TwinRegistryService
from .core.twin_lifecycle_service import TwinLifecycleService
from .core.twin_relationship_service import TwinRelationshipService
from .core.twin_instance_service import TwinInstanceService

# Import models
from .models.twin_relationship import TwinRelationship
from .models.twin_instance import TwinInstance
from .models.twin_lifecycle import TwinLifecycleEvent
from .models.twin_registry import TwinRegistryMetadata

__all__ = [
    # Core services
    "TwinRegistryService",
    "TwinLifecycleService", 
    "TwinRelationshipService",
    "TwinInstanceService",
    
    # Models
    "TwinRelationship",
    "TwinInstance",
    "TwinLifecycleEvent",
    "TwinRegistryMetadata",
] 