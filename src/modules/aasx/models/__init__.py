"""
AASX Models Module

This module provides Pydantic models for AASX processing operations.
All models extend the engine BaseModel and support pure async operations.
"""

from .aasx_processing import (
    AasxProcessing,
    create_aasx_processing_job  # Pure async factory
)

from .aasx_processing_metrics import (
    AasxProcessingMetrics,
    create_aasx_processing_metrics,  # Pure async factory
    MetricsQuery,
    MetricsSummary
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    # Main Models
    'AasxProcessing',
    'AasxProcessingMetrics',
    
    # Pure Async Factory Functions
    'create_aasx_processing_job',
    'create_aasx_processing_metrics',
    
    # Query and Summary Models
    'MetricsQuery',
    'MetricsSummary'
]
