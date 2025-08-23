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
from .core.aasx_processor import AasxProcessor

# Models (Pure Async)
from .models import (
    AasxProcessing,
    AasxProcessingMetrics,
    create_aasx_processing_job,
    create_aasx_processing_metrics
)

# Services (Pure Async)
from .services.aasx_processing_service import AasxProcessingService
from .services.processing_metrics_service import ProcessingMetricsService

# Repositories (Pure Async)
from .repositories.aasx_processing_repository import AasxProcessingRepository
from .repositories.processing_metrics_repository import ProcessingMetricsRepository

# Events (Pure Async)
from .events.event_manager import EventManager

# Integration (Pure Async)
from .integration.external_tools import ExternalToolsIntegration
from .integration.api_client import ApiClient

# Utilities (Pure Async)
from .utils.validation import ValidationUtils
from .utils.format_converter import FormatConverter

# Configuration (Pure Async)
from .config.aasx_config import AASXConfig
from .config.validation_rules_config import ValidationRulesConfig

# Populator (Pure Async)
from .populator.test_data_generator import TestDataGenerator

__all__ = [
    # Core
    'AasxProcessor',
    
    # Models (Pure Async)
    'AasxProcessing',
    'AasxProcessingMetrics',
    'create_aasx_processing_job',
    'create_aasx_processing_metrics',
    
    # Services (Pure Async)
    'AasxProcessingService',
    'ProcessingMetricsService',
    
    # Repositories (Pure Async)
    'AasxProcessingRepository',
    'ProcessingMetricsRepository',
    
    # Events (Pure Async)
    'EventManager',
    
    # Integration (Pure Async)
    'ExternalToolsIntegration',
    'ApiClient',
    
    # Utilities (Pure Async)
    'ValidationUtils',
    'FormatConverter',
    
    # Configuration (Pure Async)
    'AASXConfig',
    'ValidationRulesConfig',
    
    # Populator (Pure Async)
    'TestDataGenerator'
] 