"""
Plugin-based solver system for physics modeling framework.

This module provides solver integration, registry, and management capabilities.
"""

from .plugin_system import SolverPlugin
from .registry import SolverRegistry
from .base_solver import BaseSolver

__all__ = [
    "SolverPlugin",
    "SolverRegistry", 
    "BaseSolver"
] 