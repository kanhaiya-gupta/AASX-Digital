"""
Federated Learning Repositories Package
======================================

Data access layer for federated learning module using engine ConnectionManager.
"""

from .federated_learning_registry_repository import FederatedLearningRegistryRepository
from .federated_learning_metrics_repository import FederatedLearningMetricsRepository

__all__ = [
    'FederatedLearningRegistryRepository',
    'FederatedLearningMetricsRepository',
]
