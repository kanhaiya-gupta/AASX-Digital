"""
Module Integration Package

This package provides core services for discovering, connecting to, and orchestrating
external task modules within the AAS Data Modeling Engine.

The module integration layer acts as an orchestration layer between the engine
and external task modules, enabling seamless coordination and workflow management
without modifying the protected engine core.
"""

from .module_discovery import ModuleDiscoveryService
from .module_connector import ModuleConnectorService
from .module_orchestrator import ModuleOrchestratorService
from .module_health_monitor import ModuleHealthMonitorService
from .module_data_sync import ModuleDataSyncService
from .certificate_manager_integration import CertificateManagerIntegration, IntegrationStatus, IntegrationType, CertificateOperation, IntegrationRequest, IntegrationResponse

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    "ModuleDiscoveryService",
    "ModuleConnectorService", 
    "ModuleOrchestratorService",
    "ModuleHealthMonitorService",
    "ModuleDataSyncService",
    "CertificateManagerIntegration",
    "IntegrationStatus",
    "IntegrationType", 
    "CertificateOperation",
    "IntegrationRequest",
    "IntegrationResponse"
]
