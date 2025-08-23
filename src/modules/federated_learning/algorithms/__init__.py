"""
Federated Learning Algorithms Package
====================================

Core algorithmic implementations for federated learning operations.
Provides various aggregation strategies, privacy mechanisms, and optimization techniques.
"""

from .fedavg import (
    FedAvgAlgorithm,
    FedAvgConfig,
    FedAvgMetrics
)

from .secure_aggregation import (
    SecureAggregationAlgorithm,
    SecureAggregationConfig,
    SecureAggregationMetrics
)

from .differential_privacy import (
    DifferentialPrivacyAlgorithm,
    DifferentialPrivacyConfig,
    DifferentialPrivacyMetrics
)

from .performance_weighting import (
    PerformanceWeightingAlgorithm,
    PerformanceWeightingConfig,
    PerformanceWeightingMetrics
)

from .hybrid_learning import (
    HybridLearningAlgorithm,
    HybridLearningConfig,
    HybridLearningMetrics
)

from .algorithm_optimizer import (
    AlgorithmOptimizer,
    OptimizationStrategy,
    OptimizationMetrics
)

__all__ = [
    # FedAvg Algorithm
    'FedAvgAlgorithm',
    'FedAvgConfig',
    'FedAvgMetrics',
    
    # Secure Aggregation
    'SecureAggregationAlgorithm',
    'SecureAggregationConfig',
    'SecureAggregationMetrics',
    
    # Differential Privacy
    'DifferentialPrivacyAlgorithm',
    'DifferentialPrivacyConfig',
    'DifferentialPrivacyMetrics',
    
    # Performance Weighting
    'PerformanceWeightingAlgorithm',
    'PerformanceWeightingConfig',
    'PerformanceWeightingMetrics',
    
    # Hybrid Learning
    'HybridLearningAlgorithm',
    'HybridLearningConfig',
    'HybridLearningMetrics',
    
    # Algorithm Optimizer
    'AlgorithmOptimizer',
    'OptimizationStrategy',
    'OptimizationMetrics',
] 