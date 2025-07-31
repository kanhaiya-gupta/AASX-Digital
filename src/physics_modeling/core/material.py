"""
Material Properties for Physics Modeling

This module defines the Material class and related components for handling
material properties in physics-based simulations.
"""

import json
import logging
import copy
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Material:
    """
    Material properties for physics modeling
    
    This class represents material properties used in various physics simulations
    including thermal, structural, fluid, and electromagnetic analysis.
    """
    
    name: str
    material_type: str  # "metal", "polymer", "ceramic", "fluid", "composite"
    
    # Basic properties
    density: float = 0.0  # kg/m³
    youngs_modulus: Optional[float] = None  # Pa (for structural analysis)
    poissons_ratio: Optional[float] = None  # dimensionless
    yield_strength: Optional[float] = None  # Pa
    tensile_strength: Optional[float] = None  # Pa
    max_pressure: Optional[float] = None  # Pa (for pressure vessels, tanks, etc.)
    
    # Thermal properties
    thermal_conductivity: Optional[float] = None  # W/(m·K)
    specific_heat: Optional[float] = None  # J/(kg·K)
    thermal_expansion_coefficient: Optional[float] = None  # 1/K
    emissivity: Optional[float] = None  # dimensionless
    melting_point: Optional[float] = None  # K
    
    # Fluid properties
    viscosity: Optional[float] = None  # Pa·s
    bulk_modulus: Optional[float] = None  # Pa
    
    # Electrical properties
    electrical_conductivity: Optional[float] = None  # S/m
    relative_permittivity: Optional[float] = None  # dimensionless
    relative_permeability: Optional[float] = None  # dimensionless
    ionic_conductivity: Optional[float] = None  # S/m for electrolytes
    
    # Additional properties
    properties: Dict[str, Any] = field(default_factory=dict)
    molecular_weight: Optional[float] = None  # g/mol
    
    def __post_init__(self):
        """Validate material properties after initialization"""
        self.validate_properties()
    
    def validate_properties(self) -> bool:
        """Validate material properties for physical consistency"""
        errors = []
        
        # Check for negative values where inappropriate
        if self.density < 0:
            errors.append("Density cannot be negative")
        
        if self.youngs_modulus is not None and self.youngs_modulus < 0:
            errors.append("Young's modulus cannot be negative")
        
        if self.poissons_ratio is not None:
            if self.poissons_ratio < -1 or self.poissons_ratio > 0.5:
                errors.append("Poisson's ratio must be between -1 and 0.5")
        
        if self.thermal_conductivity is not None and self.thermal_conductivity < 0:
            errors.append("Thermal conductivity cannot be negative")
        
        if self.specific_heat is not None and self.specific_heat < 0:
            errors.append("Specific heat cannot be negative")
        
        if self.viscosity is not None and self.viscosity < 0:
            errors.append("Viscosity cannot be negative")
        
        if errors:
            logger.warning(f"Material validation errors for {self.name}: {errors}")
            return False
        
        return True
    
    def get_property(self, property_name: str) -> Optional[float]:
        """Get a specific material property"""
        if hasattr(self, property_name):
            return getattr(self, property_name)
        elif property_name in self.properties:
            return self.properties[property_name]
        else:
            logger.warning(f"Property '{property_name}' not found for material '{self.name}'")
            return None
    
    def set_property(self, property_name: str, value: Any) -> None:
        """Set a material property"""
        if hasattr(self, property_name):
            setattr(self, property_name, value)
        else:
            self.properties[property_name] = value
        
        # Revalidate after setting property
        self.validate_properties()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert material to dictionary representation"""
        return {
            "name": self.name,
            "material_type": self.material_type,
            "density": self.density,
            "youngs_modulus": self.youngs_modulus,
            "poissons_ratio": self.poissons_ratio,
            "yield_strength": self.yield_strength,
            "tensile_strength": self.tensile_strength,
            "max_pressure": self.max_pressure,
            "thermal_conductivity": self.thermal_conductivity,
            "specific_heat": self.specific_heat,
            "thermal_expansion_coefficient": self.thermal_expansion_coefficient,
            "emissivity": self.emissivity,
            "melting_point": self.melting_point,
            "viscosity": self.viscosity,
            "bulk_modulus": self.bulk_modulus,
            "electrical_conductivity": self.electrical_conductivity,
            "relative_permittivity": self.relative_permittivity,
            "relative_permeability": self.relative_permeability,
            "ionic_conductivity": self.ionic_conductivity,
            "molecular_weight": self.molecular_weight,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Material':
        """Create material from dictionary representation"""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert material to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Material':
        """Create material from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def get_physics_type_compatibility(self) -> List[str]:
        """Get list of physics types this material is compatible with"""
        compatible_types = []
        
        # Check structural compatibility
        if self.youngs_modulus is not None and self.poissons_ratio is not None:
            compatible_types.append("structural")
        
        # Check thermal compatibility
        if self.thermal_conductivity is not None and self.specific_heat is not None:
            compatible_types.append("thermal")
        
        # Check fluid compatibility
        if self.viscosity is not None:
            compatible_types.append("fluid")
        
        # Check electromagnetic compatibility
        if self.electrical_conductivity is not None:
            compatible_types.append("electromagnetic")
        
        return compatible_types
    
    def __str__(self) -> str:
        return f"Material({self.name}, type={self.material_type})"
    
    def __repr__(self) -> str:
        return f"Material(name='{self.name}', material_type='{self.material_type}', density={self.density})"
    
    def copy(self) -> 'Material':
        """Create a deep copy of the material"""
        return copy.deepcopy(self)
    
    def __eq__(self, other: object) -> bool:
        """Compare materials for equality"""
        if not isinstance(other, Material):
            return False
        
        return (self.name == other.name and 
                self.material_type == other.material_type and
                self.density == other.density and
                self.youngs_modulus == other.youngs_modulus and
                self.poissons_ratio == other.poissons_ratio and
                self.yield_strength == other.yield_strength and
                self.tensile_strength == other.tensile_strength and
                self.max_pressure == other.max_pressure and
                self.thermal_conductivity == other.thermal_conductivity and
                self.specific_heat == other.specific_heat and
                self.thermal_expansion_coefficient == other.thermal_expansion_coefficient and
                self.emissivity == other.emissivity and
                self.melting_point == other.melting_point and
                self.viscosity == other.viscosity and
                self.bulk_modulus == other.bulk_modulus and
                self.electrical_conductivity == other.electrical_conductivity and
                self.relative_permittivity == other.relative_permittivity and
                self.relative_permeability == other.relative_permeability and
                self.ionic_conductivity == other.ionic_conductivity and
                self.molecular_weight == other.molecular_weight and
                self.properties == other.properties)


# Predefined material templates
class MaterialTemplates:
    """Collection of predefined material templates"""
    
    @staticmethod
    def steel() -> Material:
        """Create steel material template"""
        return Material(
            name="Steel",
            material_type="metal",
            density=7850.0,
            youngs_modulus=200e9,
            poissons_ratio=0.3,
            yield_strength=250e6,
            thermal_conductivity=50.0,
            specific_heat=460.0,
            thermal_expansion_coefficient=12e-6,
            electrical_conductivity=6.0e6
        )
    
    @staticmethod
    def aluminum() -> Material:
        """Create aluminum material template"""
        return Material(
            name="Aluminum",
            material_type="metal",
            density=2700.0,
            youngs_modulus=70e9,
            poissons_ratio=0.33,
            yield_strength=276e6,
            thermal_conductivity=237.0,
            specific_heat=900.0,
            thermal_expansion_coefficient=23e-6,
            electrical_conductivity=35.0e6
        )
    
    @staticmethod
    def water() -> Material:
        """Create water material template"""
        return Material(
            name="Water",
            material_type="fluid",
            density=1000.0,
            viscosity=1e-3,
            thermal_conductivity=0.6,
            specific_heat=4186.0,
            bulk_modulus=2.2e9
        )
    
    @staticmethod
    def air() -> Material:
        """Create air material template"""
        return Material(
            name="Air",
            material_type="fluid",
            density=1.225,
            viscosity=1.8e-5,
            thermal_conductivity=0.024,
            specific_heat=1005.0,
            bulk_modulus=1.4e5
        )
    
    @staticmethod
    def plastic() -> Material:
        """Create plastic material template"""
        return Material(
            name="Plastic",
            material_type="polymer",
            density=1200.0,
            youngs_modulus=3e9,
            poissons_ratio=0.4,
            thermal_conductivity=0.2,
            specific_heat=1500.0,
            thermal_expansion_coefficient=100e-6
        )