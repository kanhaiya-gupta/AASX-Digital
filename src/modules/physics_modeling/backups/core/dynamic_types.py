"""
Dynamic Physics Type System

This module provides the foundation for defining and managing physics types
in a dynamic, extensible manner. Physics types can be created, modified,
and extended without code changes.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid


@dataclass
class PhysicsParameter:
    """Represents a parameter for a physics type."""
    
    name: str
    type: str  # 'float', 'int', 'string', 'boolean', 'array', 'object'
    description: str
    default_value: Any = None
    required: bool = False
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    unit: Optional[str] = None
    validation_rules: List[str] = field(default_factory=list)


@dataclass
class PhysicsEquation:
    """Represents a mathematical equation for a physics type."""
    
    name: str
    equation: str  # LaTeX format
    description: str
    variables: List[str] = field(default_factory=list)
    constants: Dict[str, float] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)


@dataclass
class SolverCapability:
    """Represents solver capabilities for a physics type."""
    
    solver_name: str
    physics_types: List[str] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    status: str = "available"  # 'available', 'maintenance', 'deprecated'


class DynamicPhysicsType:
    """
    Dynamic physics type definition that can be created and modified at runtime.
    
    This class provides a flexible way to define physics types with their
    parameters, equations, and solver capabilities without requiring code changes.
    """
    
    def __init__(
        self,
        type_id: str,
        name: str,
        category: str,
        description: str = "",
        parameters: Optional[List[PhysicsParameter]] = None,
        equations: Optional[List[PhysicsEquation]] = None,
        solvers: Optional[List[SolverCapability]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a dynamic physics type.
        
        Args:
            type_id: Unique identifier for the physics type
            name: Human-readable name
            category: Category (e.g., 'thermal', 'structural', 'fluid')
            description: Detailed description
            parameters: List of physics parameters
            equations: List of mathematical equations
            solvers: List of solver capabilities
            metadata: Additional metadata
        """
        self.type_id = type_id
        self.name = name
        self.category = category
        self.description = description
        self.parameters = parameters or []
        self.equations = equations or []
        self.solvers = solvers or []
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_parameter(self, parameter: PhysicsParameter) -> None:
        """Add a parameter to the physics type."""
        self.parameters.append(parameter)
        self.updated_at = datetime.now()
    
    def add_equation(self, equation: PhysicsEquation) -> None:
        """Add an equation to the physics type."""
        self.equations.append(equation)
        self.updated_at = datetime.now()
    
    def add_solver(self, solver: SolverCapability) -> None:
        """Add a solver capability to the physics type."""
        self.solvers.append(solver)
        self.updated_at = datetime.now()
    
    def get_parameter(self, name: str) -> Optional[PhysicsParameter]:
        """Get a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None
    
    def validate_parameters(self, input_params: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate input parameters against the physics type definition.
        
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in input_params:
                errors[param.name] = f"Required parameter '{param.name}' is missing"
                continue
            
            if param.name in input_params:
                value = input_params[param.name]
                
                # Type validation
                if param.type == 'float' and not isinstance(value, (int, float)):
                    errors[param.name] = f"Parameter '{param.name}' must be a number"
                elif param.type == 'int' and not isinstance(value, int):
                    errors[param.name] = f"Parameter '{param.name}' must be an integer"
                elif param.type == 'string' and not isinstance(value, str):
                    errors[param.name] = f"Parameter '{param.name}' must be a string"
                elif param.type == 'boolean' and not isinstance(value, bool):
                    errors[param.name] = f"Parameter '{param.name}' must be a boolean"
                
                # Range validation
                if param.min_value is not None and value < param.min_value:
                    errors[param.name] = f"Parameter '{param.name}' must be >= {param.min_value}"
                if param.max_value is not None and value > param.max_value:
                    errors[param.name] = f"Parameter '{param.name}' must be <= {param.max_value}"
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert physics type to dictionary for storage."""
        return {
            'type_id': self.type_id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'parameters': [
                {
                    'name': p.name,
                    'type': p.type,
                    'description': p.description,
                    'default_value': p.default_value,
                    'required': p.required,
                    'min_value': p.min_value,
                    'max_value': p.max_value,
                    'unit': p.unit,
                    'validation_rules': p.validation_rules
                }
                for p in self.parameters
            ],
            'equations': [
                {
                    'name': e.name,
                    'equation': e.equation,
                    'description': e.description,
                    'variables': e.variables,
                    'constants': e.constants,
                    'conditions': e.conditions
                }
                for e in self.equations
            ],
            'solvers': [
                {
                    'solver_name': s.solver_name,
                    'physics_types': s.physics_types,
                    'capabilities': s.capabilities,
                    'performance_metrics': s.performance_metrics,
                    'status': s.status
                }
                for s in self.solvers
            ],
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DynamicPhysicsType':
        """Create physics type from dictionary."""
        # Reconstruct parameters
        parameters = []
        for p_data in data.get('parameters', []):
            param = PhysicsParameter(
                name=p_data['name'],
                type=p_data['type'],
                description=p_data['description'],
                default_value=p_data.get('default_value'),
                required=p_data.get('required', False),
                min_value=p_data.get('min_value'),
                max_value=p_data.get('max_value'),
                unit=p_data.get('unit'),
                validation_rules=p_data.get('validation_rules', [])
            )
            parameters.append(param)
        
        # Reconstruct equations
        equations = []
        for e_data in data.get('equations', []):
            equation = PhysicsEquation(
                name=e_data['name'],
                equation=e_data['equation'],
                description=e_data['description'],
                variables=e_data.get('variables', []),
                constants=e_data.get('constants', {}),
                conditions=e_data.get('conditions', [])
            )
            equations.append(equation)
        
        # Reconstruct solvers
        solvers = []
        for s_data in data.get('solvers', []):
            solver = SolverCapability(
                solver_name=s_data['solver_name'],
                physics_types=s_data.get('physics_types', []),
                capabilities=s_data.get('capabilities', {}),
                performance_metrics=s_data.get('performance_metrics', {}),
                status=s_data.get('status', 'available')
            )
            solvers.append(solver)
        
        # Create physics type
        physics_type = cls(
            type_id=data['type_id'],
            name=data['name'],
            category=data['category'],
            description=data.get('description', ''),
            parameters=parameters,
            equations=equations,
            solvers=solvers,
            metadata=data.get('metadata', {})
        )
        
        # Set timestamps
        if 'created_at' in data:
            physics_type.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            physics_type.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return physics_type
    
    def __str__(self) -> str:
        return f"DynamicPhysicsType({self.type_id}: {self.name})"
    
    def __repr__(self) -> str:
        return f"DynamicPhysicsType(type_id='{self.type_id}', name='{self.name}', category='{self.category}')" 