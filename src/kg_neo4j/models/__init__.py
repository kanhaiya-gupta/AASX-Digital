"""
Knowledge Graph Models Package
Contains data models for the Knowledge Graph module following the established pattern
"""

from .kg_graph_registry import KGGraphRegistry
from .kg_graph_metrics import KGGraphMetrics

__all__ = [
    'KGGraphRegistry',
    'KGGraphMetrics'
]
