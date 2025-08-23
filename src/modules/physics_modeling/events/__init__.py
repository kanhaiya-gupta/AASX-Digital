"""
Physics Modeling Events Package

This package provides a physics-specific event management system for physics modeling operations
including mesh operations, solver iterations, convergence monitoring, and physics validation.
"""

from .physics_event_types import (
    BasePhysicsEvent,
    MeshOperationEvent,
    SolverIterationEvent,
    ConvergenceCheckEvent,
    PhysicsValidationEvent,
    ConstraintCheckEvent,
    BoundaryConditionEvent,
    MaterialPropertyEvent,
    TimeStepEvent,
    PostProcessingEvent,
    ErrorAnalysisEvent,
    PhysicsEventType,
    PhysicsEventPriority,
    PhysicsEventStatus
)
from .physics_event_manager import PhysicsEventManager
from .physics_example import demo_structural_analysis_workflow, demo_thermal_analysis_workflow

__all__ = [
    # Physics Event Manager
    'PhysicsEventManager',
    
    # Physics Event Types
    'BasePhysicsEvent',
    'MeshOperationEvent',
    'SolverIterationEvent',
    'ConvergenceCheckEvent',
    'PhysicsValidationEvent',
    'ConstraintCheckEvent',
    'BoundaryConditionEvent',
    'MaterialPropertyEvent',
    'TimeStepEvent',
    'PostProcessingEvent',
    'ErrorAnalysisEvent',
    
    # Physics Event Enums
    'PhysicsEventType',
    'PhysicsEventPriority',
    'PhysicsEventStatus',
    
    # Example Functions
    'demo_structural_analysis_workflow',
    'demo_thermal_analysis_workflow'
]
