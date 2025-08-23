"""
Knowledge Graph Neo4j Integration Package

Integration layer for connecting KG Neo4j with other modules and external systems.
Provides integration coordinators, webhook notifications, and cross-module communication.
"""

from .integration_coordinator import KGNeo4jIntegrationCoordinator, IntegrationWorkflow
from .module_integrations import (
    AASXIntegration,
    TwinRegistryIntegration,
    AIRAGIntegration,
    BaseModuleIntegration,
    get_integration,
    get_available_integrations
)
from .webhook_manager import WebhookManager, WebhookEndpoint, WebhookDelivery
from .external_api_client import ExternalAPIClient, APIConfig, APIResponse

__all__ = [
    # Core Integration
    'KGNeo4jIntegrationCoordinator',
    'IntegrationWorkflow',
    
    # Module Integrations
    'AASXIntegration',
    'TwinRegistryIntegration',
    'AIRAGIntegration',
    'BaseModuleIntegration',
    'get_integration',
    'get_available_integrations',
    
    # External Communication
    'WebhookManager',
    'WebhookEndpoint',
    'WebhookDelivery',
    'ExternalAPIClient',
    'APIConfig',
    'APIResponse'
]
