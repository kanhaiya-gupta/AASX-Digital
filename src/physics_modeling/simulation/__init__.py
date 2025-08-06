"""
Common simulation infrastructure for physics modeling framework.

This module provides shared simulation components that all plugins can use.
These components handle preprocessing, postprocessing, result processing, and visualization.
"""

from .base_simulation import BaseSimulation
from .simulation_engine import SimulationEngine
from .result_processor import ResultProcessor
from .visualization import Visualization
from .export import Export

__all__ = [
    'BaseSimulation',
    'SimulationEngine', 
    'ResultProcessor',
    'Visualization',
    'Export'
] 