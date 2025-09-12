"""
AAS Data Modeling Engine - Integration Layer

This package provides comprehensive integration capabilities for the
AAS Data Modeling Engine, including module integration, external
communication, governance, workflow orchestration, API management,
and deployment support.

The integration layer serves as a bridge between the core engine
and external modules, providing:
- Module discovery and orchestration
- External communication and data pipelines
- Cross-module governance and compliance
- Workflow orchestration and management
- API gateway and middleware services
- Deployment and scaling support
"""

# Module Integration Services
from .module_integration import (
    ModuleDiscoveryService,
    ModuleConnectorService, 
    ModuleOrchestratorService,
    ModuleHealthMonitorService,
    ModuleDataSyncService
)

# External Communication Services
from .external_communication import (
    ModuleClient,
    EventBridge,
    DataPipeline,
    ExternalModuleRegistry
)

# Cross-Module Governance Services
from .cross_module_governance import (
    CrossModuleLineageService,
    ModuleComplianceService,
    DataQualityMonitorService,
    GovernancePolicyEnforcerService
)

# Workflow Engine Services
from .workflow_engine import (
    WorkflowEngine,
    WorkflowManager,
    TaskOrchestrator,
    WorkflowMonitor
)

# API Layer Services
from .api import (
    APIGateway,
    APIMiddleware,
    RateLimiter,
    APIVersioning,
    APIDocumentation,
    HealthCheckService
)


__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    # Module Integration
    "ModuleDiscoveryService",
    "ModuleConnectorService", 
    "ModuleOrchestratorService",
    "ModuleHealthMonitorService",
    "ModuleDataSyncService",
    
    # External Communication
    "ModuleClient",
    "EventBridge",
    "DataPipeline",
    "ExternalModuleRegistry",
    
    # Cross-Module Governance
    "CrossModuleLineageService",
    "ModuleComplianceService",
    "DataQualityMonitorService",
    "GovernancePolicyEnforcerService",
    
    # Workflow Engine
    "WorkflowEngine",
    "WorkflowManager",
    "TaskOrchestrator",
    "WorkflowMonitor",
    
    # API Layer
    "APIGateway",
    "APIMiddleware",
    "RateLimiter",
    "APIVersioning",
    "APIDocumentation",
    "HealthCheckService",
    
]
