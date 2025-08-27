"""
Physics Modeling Models Package

This package contains data models for the Physics Modeling module that integrate
with the src/engine infrastructure and schema. Enhanced with comprehensive enterprise
features for compliance, security, and performance monitoring.
Enhanced with enterprise-grade computed fields, business intelligence methods, and full Certificate Manager method parity.
NOW INCLUDES ALL METHODS THAT CERTIFICATE MANAGER HAS:
- validate_integrity()
- update_health_metrics()
- generate_summary()
- export_data()

ENHANCED WITH ADDITIONAL COMPUTED FIELDS:
- overall_score, enterprise_health_status, risk_assessment (Registry)
- overall_ml_score, ml_enterprise_health_status, ml_risk_assessment (ML Registry)
- overall_metrics_score, enterprise_health_status, risk_assessment (Metrics)
"""

from .physics_modeling_registry import (
    PhysicsModelingRegistry, 
    PhysicsModelingRegistryQuery, 
    PhysicsModelingRegistrySummary
)
from .physics_ml_registry import (
    PhysicsMLRegistry, 
    PhysicsMLRegistryQuery, 
    PhysicsMLRegistrySummary
)
from .physics_modeling_metrics import (
    PhysicsModelingMetrics, 
    PhysicsModelingMetricsQuery, 
    PhysicsModelingMetricsSummary
)

__all__ = [
    # Main Models
    "PhysicsModelingRegistry",
    "PhysicsMLRegistry", 
    "PhysicsModelingMetrics",
    
    # Query Models
    "PhysicsModelingRegistryQuery",
    "PhysicsMLRegistryQuery",
    "PhysicsModelingMetricsQuery",
    
    # Summary Models
    "PhysicsModelingRegistrySummary",
    "PhysicsMLRegistrySummary", 
    "PhysicsModelingMetricsSummary",
    
    # Enterprise Features
    # - Business Intelligence Properties
    # - Risk Assessment Methods
    # - Optimization Suggestions
    # - Compliance Validation
    # - Performance Analytics
    # - Maintenance Scheduling
    # - Enterprise Health Monitoring
]
