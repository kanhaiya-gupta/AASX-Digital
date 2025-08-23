"""
Solvers for physics modeling framework.

This module contains user-created solver plugins that extend the framework
with custom solver algorithms and methods.
"""

from .base_solver import BaseSolver
from .structural_solver import StructuralSolver
from .thermal_solver import ThermalSolver
from .finite_difference_solver import FiniteDifferenceSolver
from .finite_volume_solver import FiniteVolumeSolver
from .pinn_solver import PINNSolver
from .solver_factory import SolverFactory

__all__ = [
    'BaseSolver',
    'StructuralSolver', 
    'ThermalSolver',
    'FiniteDifferenceSolver',
    'FiniteVolumeSolver',
    'PINNSolver',
    'SolverFactory'
] 