"""
Dynamic Physics Modeling Framework

A modular, extensible framework for physics-based modeling and simulation
that can adapt to any industry, physics type, or use case requirements.
"""

from typing import Dict, List, Optional, Any
from .core.dynamic_types import DynamicPhysicsType
from .core.plugin_manager import PhysicsPluginManager
from .core.model_factory import DynamicModelFactory
from .core.registry import Registry


class DynamicPhysicsModelingFramework:
    """
    Main entry point for the dynamic physics modeling framework.
    
    This class provides a unified interface for managing physics types,
    plugins, solvers, and use cases in a dynamic, database-driven manner.
    """
    
    def __init__(self):
        """Initialize the dynamic physics modeling framework."""
        self.plugin_manager = PhysicsPluginManager()
        self.model_factory = DynamicModelFactory()
        self.registry = Registry()
        
    def get_available_physics_types(self) -> List[str]:
        """Get list of available physics types."""
        return self.registry.get_physics_types()
    
    def create_physics_model(self, physics_type: str, parameters: Dict[str, Any]) -> Any:
        """Create a physics model instance."""
        return self.model_factory.create_model(physics_type, parameters)
    
    def register_plugin(self, plugin_path: str) -> bool:
        """Register a new physics plugin."""
        return self.plugin_manager.register_plugin(plugin_path)
    
    def get_solver_capabilities(self, physics_type: str) -> List[str]:
        """Get available solvers for a physics type."""
        return self.registry.get_solvers_for_physics_type(physics_type)


# Version information
__version__ = "1.0.0"
__author__ = "Dynamic Physics Modeling Team"
__description__ = "Dynamic, modular physics modeling framework"

# Export main classes
__all__ = [
    "DynamicPhysicsModelingFramework",
    "DynamicPhysicsType",
    "PhysicsPluginManager", 
    "DynamicModelFactory",
    "Registry"
] 