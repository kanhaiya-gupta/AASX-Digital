"""
AASX Integration Package

This package contains integration services for AASX processing operations.
"""

from .external_processor import (
    ExternalProcessor,
    ExternalProcessorError,
    create_external_processor
)

from .api_client import (
    APIClient,
    WebhookClient,
    APIError,
    create_api_client,
    create_webhook_client
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    # External processor integration
    'ExternalProcessor',
    'ExternalProcessorError',
    'create_external_processor',
    
    # API integration
    'APIClient',
    'WebhookClient',
    'APIError',
    'create_api_client',
    'create_webhook_client'
]
