"""
Dynamic types for physics modeling framework.

This module defines the core data structures and interfaces for the physics modeling framework.
These types are used to define physics parameters, equations, and plugin capabilities.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum


class ParameterType(Enum):
    """Types of physics parameters."""
    SCALAR = "scalar"
    VECTOR = "vector"
    MATRIX = "matrix"
    TENSOR = "tensor"
    STRING = "string"
    BOOLEAN = "boolean"


class UnitSystem(Enum):
    """Supported unit systems."""
    SI = "si"
    IMPERIAL = "imperial"
    CUSTOM = "custom"


@dataclass
class PhysicsParameter:
    """
    Represents a physics parameter with metadata.
    
    This is used to define parameters that can be configured for physics models.
    """
    name: str
    parameter_type: ParameterType
    description: str
    default_value: Any = None
    unit: str = ""
    unit_system: UnitSystem = UnitSystem.SI
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate_value(self, value: Any) -> bool:
        """
        Validate a parameter value.
        
        Args:
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        if self.required and value is None:
            return False
            
        if self.min_value is not None and value < self.min_value:
            return False
            
        if self.max_value is not None and value > self.max_value:
            return False
            
        return True


@dataclass
class PhysicsEquation:
    """
    Represents a physics equation with metadata.
    
    This is used to define mathematical equations used in physics models.
    """
    name: str
    equation: str  # Mathematical expression as string
    description: str
    variables: List[str] = field(default_factory=list)
    constants: Dict[str, float] = field(default_factory=dict)
    units: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SolverCapability:
    """
    Represents solver capabilities for a physics type.
    
    This defines what types of problems a solver can handle.
    """
    name: str
    description: str
    problem_types: List[str] = field(default_factory=list)
    supported_physics: List[str] = field(default_factory=list)
    accuracy_level: str = "standard"  # low, standard, high, expert
    performance_rating: str = "medium"  # low, medium, high
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DynamicPhysicsType:
    """
    Represents a dynamic physics type definition.
    
    This is the core data structure that defines a physics type with its
    parameters, equations, and solver capabilities.
    """
    type_id: str
    name: str
    category: str  # thermal, structural, fluid, multi_physics, etc.
    description: str
    version: str = "1.0.0"
    parameters: List[PhysicsParameter] = field(default_factory=list)
    equations: List[PhysicsEquation] = field(default_factory=list)
    solver_capabilities: List[SolverCapability] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_parameter(self, name: str) -> Optional[PhysicsParameter]:
        """Get a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None
    
    def get_equation(self, name: str) -> Optional[PhysicsEquation]:
        """Get an equation by name."""
        for eq in self.equations:
            if eq.name == name:
                return eq
        return None
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate a set of parameters against this physics type.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in parameters:
                errors[param.name] = f"Required parameter '{param.name}' is missing"
            elif param.name in parameters:
                if not param.validate_value(parameters[param.name]):
                    errors[param.name] = f"Invalid value for parameter '{param.name}'"
        
        return errors


class PhysicsPlugin(ABC):
    """
    Abstract base class for physics plugins.
    
    All physics plugins must extend this class and implement the required methods.
    This is the core interface that users implement to create custom physics types.
    """
    
    def __init__(self):
        """Initialize the physics plugin."""
        self.model_data: Optional[Dict[str, Any]] = None
        self.physics_type: Optional[DynamicPhysicsType] = None
    
    @abstractmethod
    def get_physics_type(self) -> DynamicPhysicsType:
        """
        Return the physics type definition for this plugin.
        
        This method must be implemented by all plugins to define their
        physics type, parameters, and capabilities.
        
        Returns:
            DynamicPhysicsType definition
        """
        pass
    
    @abstractmethod
    def solve(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a physics problem using this plugin.
        
        This is the main method that users implement to perform their
        specific physics calculations.
        
        Args:
            parameters: Dictionary of parameter values for the simulation
            
        Returns:
            Dictionary containing simulation results
        """
        pass
    
    def preprocess(self, model_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess data before solving.
        
        This method can be overridden to perform data preprocessing.
        The base implementation returns the model_data as-is.
        
        Args:
            model_data: Extracted data from ETL process
            parameters: Simulation parameters
            
        Returns:
            Preprocessed data
        """
        return model_data
    
    def postprocess(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess results after solving.
        
        This method can be overridden to perform result postprocessing.
        The base implementation returns the results as-is.
        
        Args:
            results: Raw simulation results
            
        Returns:
            Postprocessed results
        """
        return results
    
    def validate_input(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate input parameters.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        physics_type = self.get_physics_type()
        return physics_type.validate_parameters(parameters)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get plugin metadata.
        
        Returns:
            Plugin metadata dictionary
        """
        return {
            'class_name': self.__class__.__name__,
            'module_name': self.__class__.__module__,
            'physics_type': self.get_physics_type().type_id if self.physics_type else None
        }


# Type aliases for convenience
PhysicsParameters = List[PhysicsParameter]
PhysicsEquations = List[PhysicsEquation]
SolverCapabilities = List[SolverCapability] 