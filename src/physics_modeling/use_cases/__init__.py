"""
Physics Modeling Use Cases

This package contains real-world use cases and examples demonstrating
how physics-based modeling can be applied to solve practical engineering problems.
"""

from .thermal_analysis import ThermalAnalysisUseCases
from .structural_analysis import StructuralAnalysisUseCases
from .fluid_dynamics import FluidDynamicsUseCases
from .multi_physics import MultiPhysicsUseCases
from .industrial_applications import IndustrialUseCases

__all__ = [
    'ThermalAnalysisUseCases',
    'StructuralAnalysisUseCases', 
    'FluidDynamicsUseCases',
    'MultiPhysicsUseCases',
    'IndustrialUseCases'
]