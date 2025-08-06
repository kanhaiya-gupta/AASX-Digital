"""
Core components for the Physics Modeling Framework.

This module contains the essential components that form the foundation
of the physics modeling framework. These components are static and never change.
"""

from .dynamic_types import (
    PhysicsParameter,
    PhysicsEquation,
    SolverCapability,
    DynamicPhysicsType,
    PhysicsPlugin
)

from .plugin_manager import PluginManager
from .model_factory import ModelFactory, PhysicsModel
from .registry import Registry

__all__ = [
    # Dynamic types
    'PhysicsParameter',
    'PhysicsEquation', 
    'SolverCapability',
    'DynamicPhysicsType',
    'PhysicsPlugin',
    
    # Core components
    'PluginManager',
    'ModelFactory',
    'PhysicsModel',
    'Registry'
] 