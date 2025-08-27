"""
Federated Learning Models Package
================================

Enterprise-grade data models for federated learning module using engine BaseModel.
Includes computed fields, Certificate Manager parity methods, and comprehensive enterprise features.

FEATURES:
- 9 computed fields for business intelligence
- 4 Certificate Manager parity methods (validate_integrity, update_health_metrics, generate_summary, export_data)
- 8 additional enterprise async methods
- Query models for API filtering
- Summary models for analytics and reporting
- 100% database schema compatibility
"""

from .federated_learning_registry import (
    FederatedLearningRegistry,
    FederatedLearningRegistryQuery,
    FederatedLearningRegistrySummary
)
from .federated_learning_metrics import (
    FederatedLearningMetrics,
    FederatedLearningMetricsQuery,
    FederatedLearningMetricsSummary
)

__all__ = [
    # Main Models
    'FederatedLearningRegistry',
    'FederatedLearningMetrics',
    
    # Query Models
    'FederatedLearningRegistryQuery',
    'FederatedLearningMetricsQuery',
    
    # Summary Models
    'FederatedLearningRegistrySummary',
    'FederatedLearningMetricsSummary',
] 