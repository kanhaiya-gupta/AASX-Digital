"""
Knowledge Graph Models Package
Contains data models for the Knowledge Graph module following the established pattern
Enhanced with enterprise-grade computed fields, business intelligence methods, and comprehensive Query/Summary models
NOW INCLUDES ALL METHODS THAT CERTIFICATE MANAGER HAS:
- validate_integrity()
- update_health_metrics()
- generate_summary()
- export_data()
"""

from .kg_graph_registry import (
    KGGraphRegistry,
    KGGraphRegistryQuery,
    KGGraphRegistrySummary
)
from .kg_graph_metrics import (
    KGGraphMetrics,
    KGGraphMetricsQuery,
    KGGraphMetricsSummary
)
from .kg_neo4j_ml_registry import (
    KGNeo4jMLRegistry,
    KGNeo4jMLRegistryQuery,
    KGNeo4jMLRegistrySummary
)

__all__ = [
    # Main Models
    'KGGraphRegistry',
    'KGNeo4jMLRegistry',
    'KGGraphMetrics',

    # Query Models
    'KGGraphRegistryQuery',
    'KGNeo4jMLRegistryQuery',
    'KGGraphMetricsQuery',

    # Summary Models
    'KGGraphRegistrySummary',
    'KGNeo4jMLRegistrySummary',
    'KGGraphMetricsSummary',

    # Enterprise Features
    # - Business Intelligence Properties
    # - Risk Assessment Methods
    # - Optimization Suggestions
    # - Compliance Validation
    # - Performance Analytics
    # - Maintenance Scheduling
    # - Enterprise Health Monitoring
    # - ML Training Analytics
    # - Knowledge Graph Analytics
    
    # Additional Methods (Matching Certificate Manager)
    # - validate_integrity() - Data integrity validation
    # - update_health_metrics() - Health metrics updates
    # - generate_summary() - Comprehensive summary generation
    # - export_data() - Data export functionality
]
