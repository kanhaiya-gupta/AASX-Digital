"""
Federated Learning Module
=========================

A modular federated learning system that contains all FL-specific logic
while using shared infrastructure from `src/shared/`.
"""

from .core.federation_engine import FederationEngine
from .core.local_trainer import LocalTrainer
from .core.aggregation_server import AggregationServer
from .core.federated_learning_service import FederatedLearningService

__all__ = [
    'FederationEngine',
    'LocalTrainer', 
    'AggregationServer',
    'FederatedLearningService'
] 