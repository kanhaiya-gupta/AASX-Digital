"""
Boundary Conditions and Constraints for Physics Modeling

This module defines the BoundaryConditions class and related components for handling
boundary conditions and constraints in physics-based simulations.
"""

import json
import logging
import numpy as np
import copy
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class BoundaryType(Enum):
    """Types of boundary conditions"""
    DIRICHLET = "dirichlet"  # Fixed value
    NEUMANN = "neumann"      # Fixed gradient/flux
    ROBIN = "robin"          # Mixed condition
    PERIODIC = "periodic"    # Periodic condition
    SYMMETRY = "symmetry"    # Symmetry condition
    CONTACT = "contact"      # Contact condition

class PhysicsType(Enum):
    """Types of physics for boundary conditions"""
    THERMAL = "thermal"
    STRUCTURAL = "structural"
    FLUID = "fluid"
    ELECTROMAGNETIC = "electromagnetic"
    MULTI_PHYSICS = "multi_physics"

@dataclass
class BoundaryCondition:
    """
    Individual boundary condition specification
    
    This class represents a single boundary condition applied to a specific
    boundary or region of the geometry.
    """
    
    name: str
    boundary_type: BoundaryType
    physics_type: PhysicsType
    variable: str  # e.g., "temperature", "displacement", "velocity", "pressure"
    
    # Condition parameters
    value: Optional[Union[float, np.ndarray, Callable]] = None
    gradient: Optional[Union[float, np.ndarray, Callable]] = None
    coefficient: Optional[float] = None  # For Robin conditions
    
    # Spatial and temporal dependencies
    spatial_function: Optional[Callable] = None
    temporal_function: Optional[Callable] = None
    
    # Applied to specific geometry entities
    geometry_entities: List[str] = field(default_factory=list)  # Boundary/region names
    vertex_indices: Optional[List[int]] = None
    element_indices: Optional[List[int]] = None
    
    # Metadata
    description: str = ""
    units: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate boundary condition after initialization"""
        self.validate_condition()
    
    def validate_condition(self) -> bool:
        """Validate boundary condition parameters"""
        errors = []
        
        # Check required parameters based on boundary type
        if self.boundary_type == BoundaryType.DIRICHLET:
            if self.value is None:
                errors.append("Dirichlet condition requires a value")
        
        elif self.boundary_type == BoundaryType.NEUMANN:
            if self.gradient is None:
                errors.append("Neumann condition requires a gradient/flux value")
        
        elif self.boundary_type == BoundaryType.ROBIN:
            if self.value is None or self.coefficient is None:
                errors.append("Robin condition requires both value and coefficient")
        
        # Check physics type compatibility
        valid_variables = self._get_valid_variables_for_physics()
        if self.variable not in valid_variables:
            errors.append(f"Variable '{self.variable}' not valid for physics type '{self.physics_type.value}'")
        
        if errors:
            logger.warning(f"Boundary condition validation errors for {self.name}: {errors}")
            return False
        
        return True
    
    def _get_valid_variables_for_physics(self) -> List[str]:
        """Get valid variables for a given physics type"""
        variable_map = {
            PhysicsType.THERMAL: ["temperature", "heat_flux", "heat_transfer_coefficient"],
            PhysicsType.STRUCTURAL: ["displacement", "force", "pressure", "stress", "acceleration"],
            PhysicsType.FLUID: ["velocity", "pressure", "temperature", "turbulence", "heat_flux"],
            PhysicsType.ELECTROMAGNETIC: ["electric_field", "magnetic_field", "voltage", "current", "current_density"],
            PhysicsType.MULTI_PHYSICS: ["temperature", "displacement", "velocity", "pressure", "electric_field", "interface", "coupling", "current_density", "reaction_rate", "sensor"]
        }
        return variable_map.get(self.physics_type, [])
    
    def evaluate(self, position: np.ndarray = None, time: float = 0.0) -> Union[float, np.ndarray]:
        """Evaluate the boundary condition at given position and time"""
        result = 0.0
        
        # Get base value
        if self.value is not None:
            if callable(self.value):
                result = self.value(position, time)
            else:
                result = self.value
        
        # Apply spatial function if provided
        if self.spatial_function is not None and position is not None:
            spatial_factor = self.spatial_function(position)
            if isinstance(result, (int, float)):
                result *= spatial_factor
            else:
                result = result * spatial_factor
        
        # Apply temporal function if provided
        if self.temporal_function is not None:
            temporal_factor = self.temporal_function(time)
            if isinstance(result, (int, float)):
                result *= temporal_factor
            else:
                result = result * temporal_factor
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert boundary condition to dictionary representation"""
        return {
            "name": self.name,
            "boundary_type": self.boundary_type.value,
            "physics_type": self.physics_type.value,
            "variable": self.variable,
            "value": self.value,
            "gradient": self.gradient,
            "coefficient": self.coefficient,
            "geometry_entities": self.geometry_entities,
            "vertex_indices": self.vertex_indices,
            "element_indices": self.element_indices,
            "description": self.description,
            "units": self.units,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoundaryCondition':
        """Create boundary condition from dictionary representation"""
        # Convert enum values
        data['boundary_type'] = BoundaryType(data['boundary_type'])
        data['physics_type'] = PhysicsType(data['physics_type'])
        
        return cls(**data)
    
    def __str__(self) -> str:
        return f"BoundaryCondition({self.name}, {self.boundary_type.value}, {self.variable})"
    
    def __repr__(self) -> str:
        return f"BoundaryCondition(name='{self.name}', boundary_type={self.boundary_type.value}, variable='{self.variable}')"
    
    def copy(self) -> 'BoundaryCondition':
        """Create a deep copy of the boundary condition"""
        return copy.deepcopy(self)
    
    def __eq__(self, other: object) -> bool:
        """Compare boundary conditions for equality"""
        if not isinstance(other, BoundaryCondition):
            return False
        
        return (self.name == other.name and
                self.boundary_type == other.boundary_type and
                self.physics_type == other.physics_type and
                self.variable == other.variable and
                self.value == other.value and
                self.gradient == other.gradient and
                self.coefficient == other.coefficient and
                self.geometry_entities == other.geometry_entities and
                self.vertex_indices == other.vertex_indices and
                self.element_indices == other.element_indices and
                self.description == other.description and
                self.units == other.units and
                self.properties == other.properties)


@dataclass
class BoundaryConditions:
    """
    Collection of boundary conditions for physics modeling
    
    This class manages multiple boundary conditions for a physics simulation,
    organizing them by physics type and boundary regions.
    """
    
    name: str
    physics_type: PhysicsType
    
    # Boundary conditions organized by region
    conditions: Dict[str, BoundaryCondition] = field(default_factory=dict)
    
    # Global settings
    default_conditions: Dict[str, Any] = field(default_factory=dict)
    solver_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def add_condition(self, condition: BoundaryCondition) -> None:
        """Add a boundary condition"""
        # Allow physics type mismatches for multi-physics collections
        if condition.physics_type != self.physics_type and self.physics_type != PhysicsType.MULTI_PHYSICS:
            logger.warning(f"Physics type mismatch: condition {condition.physics_type} vs collection {self.physics_type}")
        
        self.conditions[condition.name] = condition
    
    def remove_condition(self, condition_name: str) -> None:
        """Remove a boundary condition"""
        if condition_name in self.conditions:
            del self.conditions[condition_name]
        else:
            logger.warning(f"Boundary condition '{condition_name}' not found")
    
    def get_condition(self, condition_name: str) -> Optional[BoundaryCondition]:
        """Get a specific boundary condition"""
        return self.conditions.get(condition_name)
    
    def get_conditions_by_type(self, boundary_type: BoundaryType) -> List[BoundaryCondition]:
        """Get all conditions of a specific boundary type"""
        return [cond for cond in self.conditions.values() if cond.boundary_type == boundary_type]
    
    def get_conditions_by_variable(self, variable: str) -> List[BoundaryCondition]:
        """Get all conditions for a specific variable"""
        return [cond for cond in self.conditions.values() if cond.variable == variable]
    
    def get_conditions_by_region(self, region_name: str) -> List[BoundaryCondition]:
        """Get all conditions applied to a specific region"""
        return [cond for cond in self.conditions.values() if region_name in cond.geometry_entities]
    
    def validate_all_conditions(self) -> bool:
        """Validate all boundary conditions"""
        all_valid = True
        for condition in self.conditions.values():
            if not condition.validate_condition():
                all_valid = False
        
        return all_valid
    
    def get_condition_summary(self) -> Dict[str, Any]:
        """Get a summary of all boundary conditions"""
        summary = {
            "total_conditions": len(self.conditions),
            "by_type": {},
            "by_variable": {},
            "by_region": {}
        }
        
        # Count by boundary type
        for boundary_type in BoundaryType:
            count = len(self.get_conditions_by_type(boundary_type))
            if count > 0:
                summary["by_type"][boundary_type.value] = count
        
        # Count by variable
        variables = set(cond.variable for cond in self.conditions.values())
        for variable in variables:
            count = len(self.get_conditions_by_variable(variable))
            summary["by_variable"][variable] = count
        
        # Count by region
        regions = set()
        for condition in self.conditions.values():
            regions.update(condition.geometry_entities)
        
        for region in regions:
            count = len(self.get_conditions_by_region(region))
            summary["by_region"][region] = count
        
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert boundary conditions to dictionary representation"""
        return {
            "name": self.name,
            "physics_type": self.physics_type.value,
            "conditions": {name: cond.to_dict() for name, cond in self.conditions.items()},
            "default_conditions": self.default_conditions,
            "solver_settings": self.solver_settings,
            "description": self.description,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoundaryConditions':
        """Create boundary conditions from dictionary representation"""
        # Convert physics type
        data['physics_type'] = PhysicsType(data['physics_type'])
        
        # Convert conditions
        conditions_data = data.pop('conditions', {})
        data['conditions'] = {}
        
        bc = cls(**data)
        
        # Add conditions
        for name, cond_data in conditions_data.items():
            condition = BoundaryCondition.from_dict(cond_data)
            bc.add_condition(condition)
        
        return bc
    
    def to_json(self) -> str:
        """Convert boundary conditions to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BoundaryConditions':
        """Create boundary conditions from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        return f"BoundaryConditions({self.name}, {self.physics_type.value}, {len(self.conditions)} conditions)"
    
    def __repr__(self) -> str:
        return f"BoundaryConditions(name='{self.name}', physics_type={self.physics_type.value})"
    
    def copy(self) -> 'BoundaryConditions':
        """Create a deep copy of the boundary conditions"""
        return copy.deepcopy(self)
    
    def __eq__(self, other: object) -> bool:
        """Compare boundary conditions collections for equality"""
        if not isinstance(other, BoundaryConditions):
            return False
        
        return (self.name == other.name and
                self.physics_type == other.physics_type and
                self.conditions == other.conditions and
                self.default_conditions == other.default_conditions and
                self.solver_settings == other.solver_settings and
                self.description == other.description and
                self.properties == other.properties)


# Predefined boundary condition templates
class BoundaryConditionTemplates:
    """Templates for common boundary conditions"""
    
    @staticmethod
    def thermal_insulated_wall() -> BoundaryCondition:
        """Thermal insulated wall boundary condition"""
        return BoundaryCondition(
            name="thermal_insulated_wall",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.THERMAL,
            variable="heat_flux",
            gradient=0.0,
            description="Insulated wall with zero heat flux",
            units="W/m²"
        )
    
    @staticmethod
    def thermal_fixed_temperature(temperature: float = 25.0) -> BoundaryCondition:
        """Thermal fixed temperature boundary condition"""
        return BoundaryCondition(
            name="thermal_fixed_temperature",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.THERMAL,
            variable="temperature",
            value=temperature,
            description=f"Fixed temperature boundary at {temperature}°C",
            units="°C"
        )
    
    @staticmethod
    def thermal_convection(ambient_temp: float = 25.0, h_coeff: float = 10.0) -> BoundaryCondition:
        """Thermal convection boundary condition"""
        return BoundaryCondition(
            name="thermal_convection",
            boundary_type=BoundaryType.ROBIN,
            physics_type=PhysicsType.THERMAL,
            variable="temperature",
            value=ambient_temp,
            coefficient=h_coeff,
            description=f"Convection with ambient {ambient_temp}°C, h={h_coeff} W/(m²·K)",
            units="°C"
        )
    
    @staticmethod
    def thermal_heat_source(heat_flux: float = 1000.0) -> BoundaryCondition:
        """Thermal heat source boundary condition"""
        return BoundaryCondition(
            name="thermal_heat_source",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.THERMAL,
            variable="heat_flux",
            gradient=heat_flux,
            description=f"Heat source with flux {heat_flux} W/m²",
            units="W/m²"
        )
    
    @staticmethod
    def thermal_radiation(emissivity: float = 0.8, ambient_temp: float = 25.0, sky_temp: float = None) -> BoundaryCondition:
        """Thermal radiation boundary condition"""
        # Use sky_temp if provided, otherwise use ambient_temp
        temperature = sky_temp if sky_temp is not None else ambient_temp
        
        return BoundaryCondition(
            name="thermal_radiation",
            boundary_type=BoundaryType.ROBIN,
            physics_type=PhysicsType.THERMAL,
            variable="temperature",
            value=temperature,
            coefficient=emissivity * 5.67e-8,  # Stefan-Boltzmann constant
            description=f"Radiation with emissivity {emissivity}, ambient {temperature}°C",
            units="°C"
        )
    
    @staticmethod
    def structural_fixed_support() -> BoundaryCondition:
        """Structural fixed support boundary condition"""
        return BoundaryCondition(
            name="structural_fixed_support",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.STRUCTURAL,
            variable="displacement",
            value=0.0,
            description="Fixed support with zero displacement",
            units="m"
        )
    
    @staticmethod
    def structural_gravity_load() -> BoundaryCondition:
        """Structural gravity load"""
        return BoundaryCondition(
            name="structural_gravity_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=9.81,
            description="Gravity load (9.81 m/s²)",
            units="m/s²"
        )
    
    @staticmethod
    def structural_acceleration_load(acceleration: float = 9.81) -> BoundaryCondition:
        """Structural acceleration load"""
        return BoundaryCondition(
            name="structural_acceleration_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=acceleration,
            description=f"Acceleration load of {acceleration} m/s²",
            units="m/s²"
        )
    
    @staticmethod
    def structural_centrifugal_load(angular_velocity: float = 10.0, radius: float = 1.0) -> BoundaryCondition:
        """Structural centrifugal load"""
        centrifugal_accel = angular_velocity**2 * radius
        return BoundaryCondition(
            name="structural_centrifugal_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=centrifugal_accel,
            description=f"Centrifugal load: ω={angular_velocity} rad/s, r={radius} m",
            units="m/s²"
        )
    
    @staticmethod
    def structural_rotational_load(angular_velocity: float = 10.0) -> BoundaryCondition:
        """Structural rotational load"""
        return BoundaryCondition(
            name="structural_rotational_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=angular_velocity,
            description=f"Rotational load of {angular_velocity} rad/s",
            units="rad/s"
        )
    
    @staticmethod
    def structural_thermal_load(temperature: float = 100.0, expansion_coeff: float = 1e-5, 
                               temperature_difference: float = None) -> BoundaryCondition:
        """Structural thermal load"""
        # Use temperature_difference if provided, otherwise use temperature
        temp_value = temperature_difference if temperature_difference is not None else temperature
        
        return BoundaryCondition(
            name="structural_thermal_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=temp_value,
            properties={"expansion_coefficient": expansion_coeff},
            description=f"Thermal load at {temp_value}°C",
            units="°C"
        )
    
    @staticmethod
    def structural_impact_load(velocity: float = 10.0, mass: float = 1000.0, duration: float = 0.1) -> BoundaryCondition:
        """Structural impact load"""
        impact_force = 0.5 * mass * velocity**2
        return BoundaryCondition(
            name="structural_impact_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=impact_force,
            properties={"impact_duration": duration},
            description=f"Impact load: v={velocity} m/s, m={mass} kg, t={duration} s",
            units="N"
        )
    
    @staticmethod
    def structural_point_load(force: float = 1000.0) -> BoundaryCondition:
        """Structural point load"""
        return BoundaryCondition(
            name="structural_point_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=force,
            description=f"Point load of {force} N",
            units="N"
        )
    
    @staticmethod
    def structural_uniform_load(pressure: float = 1000.0) -> BoundaryCondition:
        """Structural uniform distributed load"""
        return BoundaryCondition(
            name="structural_uniform_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=pressure,
            description=f"Uniform distributed load of {pressure} Pa",
            units="Pa"
        )
    
    @staticmethod
    def structural_pressure_load(pressure: float = 1e6) -> BoundaryCondition:
        """Structural pressure load boundary condition"""
        return BoundaryCondition(
            name="structural_pressure_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=pressure,
            description=f"Pressure load of {pressure} Pa",
            units="Pa"
        )
    
    @staticmethod
    def structural_force_load(force: float = 1000.0) -> BoundaryCondition:
        """Structural force load boundary condition"""
        return BoundaryCondition(
            name="structural_force_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.STRUCTURAL,
            variable="force",
            gradient=force,
            description=f"Force load of {force} N",
            units="N"
        )
    
    @staticmethod
    def fluid_inlet_velocity(velocity: float = 1.0) -> BoundaryCondition:
        """Fluid inlet velocity boundary condition"""
        return BoundaryCondition(
            name="fluid_inlet_velocity",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.FLUID,
            variable="velocity",
            value=velocity,
            description=f"Fluid inlet velocity of {velocity} m/s",
            units="m/s"
        )
    
    @staticmethod
    def fluid_outlet_pressure(pressure: float = 101325.0) -> BoundaryCondition:
        """Fluid outlet pressure boundary condition"""
        return BoundaryCondition(
            name="fluid_outlet_pressure",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.FLUID,
            variable="pressure",
            value=pressure,
            description=f"Fluid outlet pressure of {pressure} Pa",
            units="Pa"
        )
    
    @staticmethod
    def fluid_inlet_temperature(temperature: float = 25.0) -> BoundaryCondition:
        """Fluid inlet temperature boundary condition"""
        return BoundaryCondition(
            name="fluid_inlet_temperature",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.FLUID,
            variable="temperature",
            value=temperature,
            description=f"Fluid inlet temperature of {temperature}°C",
            units="°C"
        )
    
    @staticmethod
    def fluid_wall_condition() -> BoundaryCondition:
        """Fluid wall boundary condition"""
        return BoundaryCondition(
            name="fluid_wall_condition",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.FLUID,
            variable="velocity",
            value=0.0,
            description="No-slip wall condition",
            units="m/s"
        )
    
    @staticmethod
    def fluid_moving_wall(velocity: float = 0.0) -> BoundaryCondition:
        """Fluid moving wall boundary condition"""
        return BoundaryCondition(
            name="fluid_moving_wall",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.FLUID,
            variable="velocity",
            value=velocity,
            description=f"Moving wall with velocity {velocity} m/s",
            units="m/s"
        )
    
    @staticmethod
    def fluid_rotating_wall(angular_velocity: float = 10.0, radius: float = 1.0, 
                           axis_origin: np.ndarray = None, axis_direction: np.ndarray = None) -> BoundaryCondition:
        """Fluid rotating wall boundary condition"""
        tangential_velocity = angular_velocity * radius
        properties = {}
        if axis_origin is not None:
            properties["axis_origin"] = axis_origin.tolist()
        if axis_direction is not None:
            properties["axis_direction"] = axis_direction.tolist()
        
        return BoundaryCondition(
            name="fluid_rotating_wall",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.FLUID,
            variable="velocity",
            value=tangential_velocity,
            properties=properties,
            description=f"Rotating wall: ω={angular_velocity} rad/s, r={radius} m",
            units="m/s"
        )
    
    @staticmethod
    def fluid_symmetry_condition() -> BoundaryCondition:
        """Fluid symmetry boundary condition"""
        return BoundaryCondition(
            name="fluid_symmetry_condition",
            boundary_type=BoundaryType.SYMMETRY,
            physics_type=PhysicsType.FLUID,
            variable="velocity",
            description="Symmetry boundary condition",
            units="m/s"
        )
    
    @staticmethod
    def fluid_free_surface() -> BoundaryCondition:
        """Fluid free surface boundary condition"""
        return BoundaryCondition(
            name="fluid_free_surface",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.FLUID,
            variable="pressure",
            value=101325.0,
            description="Free surface with atmospheric pressure",
            units="Pa"
        )
    
    @staticmethod
    def fluid_heat_source(heat_flux: float = 100.0) -> BoundaryCondition:
        """Fluid heat source boundary condition"""
        return BoundaryCondition(
            name="fluid_heat_source",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.FLUID,
            variable="heat_flux",
            gradient=heat_flux,
            description=f"Fluid heat source with flux {heat_flux} W/m²",
            units="W/m²"
        )
    
    @staticmethod
    def fluid_solid_inlet(velocity: float = 1.0, particle_concentration: float = 0.1) -> BoundaryCondition:
        """Fluid-solid mixture inlet"""
        return BoundaryCondition(
            name="fluid_solid_inlet",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.FLUID,
            variable="velocity",
            value=velocity,
            properties={"particle_concentration": particle_concentration},
            description=f"Fluid-solid inlet: v={velocity} m/s, c={particle_concentration}",
            units="m/s"
        )
    
    @staticmethod
    def fluid_pressure_load(pressure: float = 1e6) -> BoundaryCondition:
        """Fluid pressure load"""
        return BoundaryCondition(
            name="fluid_pressure_load",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.FLUID,
            variable="pressure",
            gradient=pressure,
            description=f"Fluid pressure load of {pressure} Pa",
            units="Pa"
        )
    
    @staticmethod
    def electromagnetic_voltage(voltage: float = 12.0) -> BoundaryCondition:
        """Electromagnetic voltage boundary condition"""
        return BoundaryCondition(
            name="electromagnetic_voltage",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.ELECTROMAGNETIC,
            variable="voltage",
            value=voltage,
            description=f"Voltage boundary of {voltage} V",
            units="V"
        )
    
    @staticmethod
    def electromagnetic_current_density(current_density: float = 1000.0) -> BoundaryCondition:
        """Electromagnetic current density boundary condition"""
        return BoundaryCondition(
            name="electromagnetic_current_density",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.ELECTROMAGNETIC,
            variable="current_density",
            gradient=current_density,
            description=f"Current density of {current_density} A/m²",
            units="A/m²"
        )
    
    @staticmethod
    def electromagnetic_magnetic_field(field_strength: float = 1.0, magnetic_flux_density: float = None) -> BoundaryCondition:
        """Electromagnetic magnetic field boundary condition"""
        # Use magnetic_flux_density if provided, otherwise use field_strength
        field_value = magnetic_flux_density if magnetic_flux_density is not None else field_strength
        
        return BoundaryCondition(
            name="electromagnetic_magnetic_field",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.ELECTROMAGNETIC,
            variable="magnetic_field",
            value=field_value,
            description=f"Magnetic field strength of {field_value} T",
            units="T"
        )
    
    @staticmethod
    def electrical_current_density(current_density: float = 1000.0) -> BoundaryCondition:
        """Electrical current density boundary condition"""
        return BoundaryCondition(
            name="electrical_current_density",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.ELECTROMAGNETIC,
            variable="current_density",
            gradient=current_density,
            description=f"Electrical current density of {current_density} A/m²",
            units="A/m²"
        )
    
    @staticmethod
    def electrochemical_reaction(reaction_rate: float = 1e-3, faradaic_efficiency: float = 0.95, 
                                cell_voltage: float = 1.8) -> BoundaryCondition:
        """Electrochemical reaction boundary condition"""
        return BoundaryCondition(
            name="electrochemical_reaction",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.MULTI_PHYSICS,
            variable="reaction_rate",
            gradient=reaction_rate,
            properties={
                "faradaic_efficiency": faradaic_efficiency,
                "cell_voltage": cell_voltage
            },
            description=f"Electrochemical reaction: rate={reaction_rate} mol/(m²·s), η={faradaic_efficiency}",
            units="mol/(m²·s)"
        )
    
    @staticmethod
    def electrochemical_current_density(current_density: float = 1000.0) -> BoundaryCondition:
        """Electrochemical current density boundary condition"""
        return BoundaryCondition(
            name="electrochemical_current_density",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.MULTI_PHYSICS,
            variable="current_density",
            gradient=current_density,
            description=f"Electrochemical current density of {current_density} A/m²",
            units="A/m²"
        )
    
    @staticmethod
    def chemical_reaction(reaction_rate: float = 1e-3, activation_energy: float = 50000.0) -> BoundaryCondition:
        """Chemical reaction boundary condition"""
        return BoundaryCondition(
            name="chemical_reaction",
            boundary_type=BoundaryType.NEUMANN,
            physics_type=PhysicsType.MULTI_PHYSICS,
            variable="reaction_rate",
            gradient=reaction_rate,
            properties={"activation_energy": activation_energy},
            description=f"Chemical reaction: rate={reaction_rate} mol/(m³·s), Ea={activation_energy} J/mol",
            units="mol/(m³·s)"
        )
    
    @staticmethod
    def fsi_interface_condition() -> BoundaryCondition:
        """Fluid-structure interaction interface condition"""
        return BoundaryCondition(
            name="fsi_interface_condition",
            boundary_type=BoundaryType.CONTACT,
            physics_type=PhysicsType.MULTI_PHYSICS,
            variable="interface",
            description="Fluid-structure interaction interface",
            units=""
        )
    
    @staticmethod
    def thermal_structural_coupling() -> BoundaryCondition:
        """Thermal-structural coupling condition"""
        return BoundaryCondition(
            name="thermal_structural_coupling",
            boundary_type=BoundaryType.ROBIN,
            physics_type=PhysicsType.MULTI_PHYSICS,
            variable="coupling",
            value=1.0,
            coefficient=1.0,
            description="Thermal-structural coupling condition",
            units=""
        )
    
    @staticmethod
    def electromagnetic_thermal_coupling() -> BoundaryCondition:
        """Electromagnetic-thermal coupling condition"""
        return BoundaryCondition(
            name="electromagnetic_thermal_coupling",
            boundary_type=BoundaryType.ROBIN,
            physics_type=PhysicsType.MULTI_PHYSICS,
            variable="coupling",
            value=1.0,
            coefficient=1.0,
            description="Electromagnetic-thermal coupling condition",
            units=""
        )
    
    @staticmethod
    def sensor_monitoring(sensor_type: str = "temperature", threshold: float = 100.0) -> BoundaryCondition:
        """Sensor monitoring boundary condition"""
        return BoundaryCondition(
            name="sensor_monitoring",
            boundary_type=BoundaryType.DIRICHLET,
            physics_type=PhysicsType.MULTI_PHYSICS,
            variable="sensor",
            value=threshold,
            properties={"sensor_type": sensor_type},
            description=f"{sensor_type} sensor monitoring with threshold {threshold}",
            units=""
        )
    
    @staticmethod
    def symmetry_condition() -> BoundaryCondition:
        """General symmetry boundary condition"""
        return BoundaryCondition(
            name="symmetry_condition",
            boundary_type=BoundaryType.SYMMETRY,
            physics_type=PhysicsType.MULTI_PHYSICS,
            variable="symmetry",
            description="Symmetry boundary condition",
            units=""
        )