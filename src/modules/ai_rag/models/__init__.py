"""
AI RAG Models Package
Contains data models for the AI RAG module following the established pattern
Enhanced with enterprise-grade computed fields, business intelligence methods, and comprehensive Query/Summary models
NOW INCLUDES ALL METHODS THAT CERTIFICATE MANAGER HAS:
- validate_integrity()
- update_health_metrics()
- generate_summary()
- export_data()

ENHANCED WITH ADDITIONAL COMPUTED FIELDS:
- processing_efficiency_score, data_volume_score (Registry)
- system_efficiency_score, user_engagement_score (Metrics)
- session_efficiency_score, cost_efficiency_score (Operations)
"""

from .ai_rag_registry import (
    AIRagRegistry,
    AIRagRegistryQuery,
    AIRagRegistrySummary
)
from .ai_rag_metrics import (
    AIRagMetrics,
    AIRagMetricsQuery,
    AIRagMetricsSummary
)
from .ai_rag_operations import (
    AIRagOperations,
    AIRagOperationsQuery,
    AIRagOperationsSummary
)

__all__ = [
    # Main Models
    'AIRagRegistry',
    'AIRagMetrics',
    'AIRagOperations',
    
    # Query Models
    'AIRagRegistryQuery',
    'AIRagMetricsQuery',
    'AIRagOperationsQuery',
    
    # Summary Models
    'AIRagRegistrySummary',
    'AIRagMetricsSummary',
    'AIRagOperationsSummary',
    
    # Enterprise Features
    # - Business Intelligence Properties (9 computed fields per model)
    # - Risk Assessment Methods
    # - Optimization Suggestions
    # - Compliance Validation
    # - Performance Analytics
    # - Maintenance Scheduling
    # - Enterprise Health Monitoring
    # - RAG Capability Analytics
    # - All Certificate Manager Methods
    # - Additional AI RAG Specific Computed Fields
]
