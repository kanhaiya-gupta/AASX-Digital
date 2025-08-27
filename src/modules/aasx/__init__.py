"""
AASX Module

A comprehensive module for AASX file processing, extraction, and generation.
Built with pure async architecture for high-performance operations.

Features:
- Pure async design for all operations
- Comprehensive AASX processing workflows
- Integration with multiple data sources
- Performance monitoring and metrics
- Event-driven architecture
- Automatic database population
"""

__version__ = "2.4.0"  # Updated for pure async architecture
__author__ = "AAS Data Modeling Team"
__description__ = "Pure async AASX processing module with comprehensive workflows"

# Core Components
# Note: AasxProcessor class moved to client layer

# Models (Pure Async)
from .models import (
    AasxProcessing,
    AasxProcessingMetrics,
    create_aasx_processing_job,
    create_aasx_processing_metrics
)

# Services (Pure Async)
from .services.aasx_processing_service import AASXProcessingService
from .services.aasx_processing_metrics_service import ProcessingMetricsService

# Repositories (Pure Async)
from .repositories.aasx_processing_repository import AasxProcessingRepository
from .repositories.aasx_processing_metrics_repository import AasxProcessingMetricsRepository

# Events (Pure Async)
from .events.event_manager import EventManager

# Integration (Pure Async)
from .integration.external_processor import ExternalProcessor
from .integration.api_client import APIClient

# Utilities (Pure Async)
from .utils.validation_utils import ValidationEngine
from .utils.format_utils import FormatConverter

# Configuration (Pure Async)
from .config.settings import AASXConfig
from .config.validation_rules import ValidationRulesConfig



__all__ = [
    # Core
    # Note: AasxProcessor class moved to client layer
    
    # Models (Pure Async)
    'AasxProcessing',
    'AasxProcessingMetrics',
    'create_aasx_processing_job',
    'create_aasx_processing_metrics',
    
    # Services (Pure Async)
    'AASXProcessingService',
    'ProcessingMetricsService',
    
    # Repositories (Pure Async)
    'AasxProcessingRepository',
    'AasxProcessingMetricsRepository',
    
    # Events (Pure Async)
    'EventManager',
    
    # Integration (Pure Async)
    'ExternalProcessor',
    'APIClient',
    
    # Utilities (Pure Async)
    'ValidationEngine',
    'FormatConverter',
    
    # Configuration (Pure Async)
    'AASXConfig',
    'ValidationRulesConfig'
] 