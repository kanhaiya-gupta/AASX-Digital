"""
Twin Registry Models Package

Provides Pydantic models for the Twin Registry module with comprehensive enterprise features.
All models extend from src.engine.models.base_model.BaseModel for consistency.
Enhanced with enterprise-grade computed fields, business intelligence methods, and comprehensive Query/Summary models.
NOW INCLUDES ALL METHODS THAT CERTIFICATE MANAGER HAS:
- validate_integrity()
- update_health_metrics()
- generate_summary()
- export_data()

ENHANCED WITH ADDITIONAL COMPUTED FIELDS:
- overall_score, enterprise_health_status, risk_assessment (Registry)
- overall_metrics_score, system_efficiency_score, user_engagement_score (Metrics)
"""

from .twin_registry import (
    TwinRegistry, 
    TwinRegistryQuery, 
    TwinRegistrySummary,
    create_twin_registry
)
from .twin_registry_metrics import (
    TwinRegistryMetrics,
    MetricsQuery,
    MetricsSummary,
    create_metrics
)

__all__ = [
    # Main Models
    'TwinRegistry',
    'TwinRegistryMetrics',
    
    # Query & Summary Models
    'TwinRegistryQuery',
    'TwinRegistrySummary',
    'MetricsQuery',
    'MetricsSummary',
    
    # Factory Functions
    'create_twin_registry',
    'create_metrics',
    
    # Enterprise Features Available:
    # - Comprehensive enterprise compliance tracking
    # - Advanced security metrics and threat assessment
    # - Business intelligence and risk assessment
    # - Performance optimization and maintenance scheduling
    # - Real-time health monitoring and alerting
    # - Advanced filtering and querying capabilities
    # - Enterprise-grade analytics and reporting
] 