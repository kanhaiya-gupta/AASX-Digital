"""
Core Physics Modeling Components

This module contains the fundamental classes for physics-based modeling:
- PhysicsModel: Base class for all physics models
- Material: Material properties and characteristics
- Geometry: Geometric representation and processing
- BoundaryConditions: Boundary conditions and constraints
"""

from .base_model import PhysicsModel
from .material import Material
from .geometry import Geometry
from .constraints import BoundaryConditions

__all__ = ['PhysicsModel', 'Material', 'Geometry', 'BoundaryConditions']