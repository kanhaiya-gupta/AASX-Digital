"""
Knowledge Graph Repositories Package
Contains data access layer for the Knowledge Graph module following the established pattern
"""

from .kg_graph_registry_repository import KGGraphRegistryRepository
from .kg_graph_metrics_repository import KGGraphMetricsRepository

__all__ = [
    'KGGraphRegistryRepository',
    'KGGraphMetricsRepository'
]
