"""
AASX Models Module

This module provides Pydantic models for AASX processing operations.
All models extend the engine BaseModel and support pure async operations.
Enhanced with enterprise-grade computed fields, business intelligence methods, and comprehensive Query/Summary models.
NOW INCLUDES ALL METHODS THAT CERTIFICATE MANAGER HAS:
- validate_integrity()
- update_health_metrics()
- generate_summary()
- export_data()

ENHANCED WITH ADDITIONAL COMPUTED FIELDS:
- overall_score, enterprise_health_status, risk_assessment (Processing)
- overall_metrics_score, system_efficiency_score, user_engagement_score (Metrics)
"""

from .aasx_processing import (
    AasxProcessing,
    AasxProcessingQuery,
    AasxProcessingSummary,
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
    
    # Query Models
    'AasxProcessingQuery',
    'MetricsQuery',
    
    # Summary Models
    'AasxProcessingSummary',
    'MetricsSummary',
    
    # Pure Async Factory Functions
    'create_aasx_processing_job',
    'create_aasx_processing_metrics',
    
]
