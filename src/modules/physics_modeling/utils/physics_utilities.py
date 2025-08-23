"""
Physics Utilities for Physics Modeling
Common physics calculations, unit conversions, and validation functions
"""

import asyncio
import logging
import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class UnitSystem(Enum):
    """Unit systems for physics calculations"""
    SI = "si"
    CGS = "cgs"
    IMPERIAL = "imperial"
    CUSTOM = "custom"

class PhysicsDomain(Enum):
    """Physics domains for specialized calculations"""
    MECHANICAL = "mechanical"
    THERMAL = "thermal"
    FLUID = "fluid"
    ELECTROMAGNETIC = "electromagnetic"
    MULTI_PHYSICS = "multi_physics"

@dataclass
class PhysicalQuantity:
    """Represents a physical quantity with value and units"""
    value: float
    unit: str
    uncertainty: Optional[float] = None
    description: str = ""

@dataclass
class MaterialProperties:
    """Material properties for physics calculations"""
    density: float
    youngs_modulus: float
    poissons_ratio: float
    thermal_expansion: float
    thermal_conductivity: float
    specific_heat: float
    units: UnitSystem = UnitSystem.SI

class PhysicsUtilities:
    """Utility functions for physics modeling calculations"""

    def __init__(self):
        # Physical constants
        self.constants = {
            'G': 6.67430e-11,  # Gravitational constant (m³/kg/s²)
            'c': 299792458,    # Speed of light (m/s)
            'h': 6.62607015e-34,  # Planck constant (J⋅s)
            'k': 1.380649e-23,    # Boltzmann constant (J/K)
            'e': 1.602176634e-19, # Elementary charge (C)
            'm_e': 9.1093837015e-31,  # Electron mass (kg)
            'm_p': 1.67262192369e-27, # Proton mass (kg)
            'N_A': 6.02214076e23,     # Avogadro number
            'R': 8.314462618,         # Gas constant (J/mol/K)
            'g': 9.80665,             # Standard gravity (m/s²)
        }
        
        # Unit conversion factors
        self.unit_conversions = {
            'length': {
                'm': 1.0,
                'cm': 0.01,
                'mm': 0.001,
                'km': 1000.0,
                'in': 0.0254,
                'ft': 0.3048,
                'yd': 0.9144,
                'mi': 1609.344
            },
            'mass': {
                'kg': 1.0,
                'g': 0.001,
                'mg': 1e-6,
                'lb': 0.45359237,
                'oz': 0.028349523125
            },
            'time': {
                's': 1.0,
                'ms': 0.001,
                'min': 60.0,
                'h': 3600.0,
                'day': 86400.0
            },
            'temperature': {
                'K': 1.0,
                'C': 1.0,  # Offset conversion
                'F': 5/9,   # Scale conversion
                'R': 5/9    # Rankine to Kelvin
            }
        }
        
        self.calculation_history = []
        logger.info("✅ Physics Utilities initialized")

    async def convert_units(self, value: float, from_unit: str, to_unit: str, 
                           quantity_type: str = "length") -> float:
        """Convert between different units"""
        await asyncio.sleep(0)
        
        try:
            if quantity_type == "temperature":
                return self._convert_temperature(value, from_unit, to_unit)
            
            if quantity_type not in self.unit_conversions:
                raise ValueError(f"Unsupported quantity type: {quantity_type}")
            
            if from_unit not in self.unit_conversions[quantity_type]:
                raise ValueError(f"Unsupported from_unit: {from_unit}")
            
            if to_unit not in self.unit_conversions[quantity_type]:
                raise ValueError(f"Unsupported to_unit: {to_unit}")
            
            # Convert to base unit first, then to target unit
            base_value = value * self.unit_conversions[quantity_type][from_unit]
            result = base_value / self.unit_conversions[quantity_type][to_unit]
            
            self.calculation_history.append({
                'operation': 'unit_conversion',
                'input': {'value': value, 'from_unit': from_unit, 'to_unit': to_unit, 'type': quantity_type},
                'output': result,
                'timestamp': datetime.now()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Unit conversion failed: {str(e)}")
            raise

    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert temperature between different scales"""
        # Convert to Kelvin first
        if from_unit == 'C':
            kelvin = value + 273.15
        elif from_unit == 'F':
            kelvin = (value - 32) * 5/9 + 273.15
        elif from_unit == 'R':
            kelvin = value * 5/9
        elif from_unit == 'K':
            kelvin = value
        else:
            raise ValueError(f"Unsupported temperature unit: {from_unit}")
        
        # Convert from Kelvin to target unit
        if to_unit == 'C':
            return kelvin - 273.15
        elif to_unit == 'F':
            return (kelvin - 273.15) * 9/5 + 32
        elif to_unit == 'R':
            return kelvin * 9/5
        elif to_unit == 'K':
            return kelvin
        else:
            raise ValueError(f"Unsupported temperature unit: {to_unit}")

    async def calculate_stress(self, force: float, area: float, 
                              force_unit: str = "N", area_unit: str = "m²") -> Dict[str, Any]:
        """Calculate stress from force and area"""
        await asyncio.sleep(0)
        
        try:
            # Convert to SI units
            force_si = await self.convert_units(force, force_unit, "N", "mass")
            area_si = await self.convert_units(area, area_unit, "m²", "length")
            
            stress = force_si / area_si
            
            result = {
                'stress': stress,
                'unit': 'Pa',
                'force': force_si,
                'area': area_si,
                'calculation_type': 'stress'
            }
            
            self.calculation_history.append({
                'operation': 'stress_calculation',
                'input': {'force': force, 'force_unit': force_unit, 'area': area, 'area_unit': area_unit},
                'output': result,
                'timestamp': datetime.now()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Stress calculation failed: {str(e)}")
            raise

    async def calculate_strain(self, original_length: float, change_in_length: float,
                              original_unit: str = "m", change_unit: str = "m") -> Dict[str, Any]:
        """Calculate strain from length changes"""
        await asyncio.sleep(0)
        
        try:
            # Convert to same units
            original_si = await self.convert_units(original_length, original_unit, "m", "length")
            change_si = await self.convert_units(change_in_length, change_unit, "m", "length")
            
            strain = change_si / original_si
            
            result = {
                'strain': strain,
                'unit': 'dimensionless',
                'original_length': original_si,
                'change_in_length': change_si,
                'calculation_type': 'strain'
            }
            
            self.calculation_history.append({
                'operation': 'strain_calculation',
                'input': {'original_length': original_length, 'original_unit': original_unit, 
                         'change_in_length': change_in_length, 'change_unit': change_unit},
                'output': result,
                'timestamp': datetime.now()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Strain calculation failed: {str(e)}")
            raise

    async def calculate_thermal_expansion(self, original_length: float, 
                                        temperature_change: float, 
                                        coefficient: float,
                                        length_unit: str = "m", 
                                        temp_unit: str = "K") -> Dict[str, Any]:
        """Calculate thermal expansion"""
        await asyncio.sleep(0)
        
        try:
            # Convert to SI units
            length_si = await self.convert_units(original_length, length_unit, "m", "length")
            temp_change_si = await self.convert_units(temperature_change, temp_unit, "K", "temperature")
            
            expansion = original_length * coefficient * temp_change_si
            
            result = {
                'expansion': expansion,
                'unit': 'm',
                'original_length': length_si,
                'temperature_change': temp_change_si,
                'coefficient': coefficient,
                'calculation_type': 'thermal_expansion'
            }
            
            self.calculation_history.append({
                'operation': 'thermal_expansion_calculation',
                'input': {'original_length': original_length, 'length_unit': length_unit,
                         'temperature_change': temperature_change, 'temp_unit': temp_unit,
                         'coefficient': coefficient},
                'output': result,
                'timestamp': datetime.now()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Thermal expansion calculation failed: {str(e)}")
            raise

    async def calculate_fluid_dynamics(self, velocity: float, density: float, 
                                     viscosity: float, characteristic_length: float,
                                     velocity_unit: str = "m/s", density_unit: str = "kg/m³",
                                     viscosity_unit: str = "Pa·s", length_unit: str = "m") -> Dict[str, Any]:
        """Calculate fluid dynamics parameters (Reynolds number, etc.)"""
        await asyncio.sleep(0)
        
        try:
            # Convert to SI units
            v_si = await self.convert_units(velocity, velocity_unit, "m/s", "length")
            rho_si = await self.convert_units(density, density_unit, "kg/m³", "mass")
            mu_si = await self.convert_units(viscosity, viscosity_unit, "Pa·s", "mass")
            L_si = await self.convert_units(characteristic_length, length_unit, "m", "length")
            
            # Reynolds number
            reynolds = (rho_si * v_si * L_si) / mu_si
            
            # Mach number (assuming speed of sound in air at 20°C)
            speed_of_sound = 343.2  # m/s
            mach = v_si / speed_of_sound
            
            result = {
                'reynolds_number': reynolds,
                'mach_number': mach,
                'velocity': v_si,
                'density': rho_si,
                'viscosity': mu_si,
                'characteristic_length': L_si,
                'calculation_type': 'fluid_dynamics'
            }
            
            self.calculation_history.append({
                'operation': 'fluid_dynamics_calculation',
                'input': {'velocity': velocity, 'velocity_unit': velocity_unit,
                         'density': density, 'density_unit': density_unit,
                         'viscosity': viscosity, 'viscosity_unit': viscosity_unit,
                         'characteristic_length': characteristic_length, 'length_unit': length_unit},
                'output': result,
                'timestamp': datetime.now()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Fluid dynamics calculation failed: {str(e)}")
            raise

    async def validate_physics_constraints(self, values: Dict[str, float], 
                                         constraints: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate physics constraints on calculated values"""
        await asyncio.sleep(0)
        
        try:
            validation_results = {}
            violations = []
            
            for constraint_name, constraint_def in constraints.items():
                value = values.get(constraint_def['variable'])
                if value is None:
                    continue
                
                constraint_type = constraint_def.get('type', 'range')
                min_val = constraint_def.get('min')
                max_val = constraint_def.get('max')
                tolerance = constraint_def.get('tolerance', 1e-6)
                
                if constraint_type == 'range':
                    if min_val is not None and value < min_val - tolerance:
                        violations.append({
                            'constraint': constraint_name,
                            'variable': constraint_def['variable'],
                            'value': value,
                            'min_allowed': min_val,
                            'violation_type': 'below_minimum'
                        })
                    elif max_val is not None and value > max_val + tolerance:
                        violations.append({
                            'constraint': constraint_name,
                            'variable': constraint_def['variable'],
                            'value': value,
                            'max_allowed': max_val,
                            'violation_type': 'above_maximum'
                        })
                
                validation_results[constraint_name] = {
                    'valid': len([v for v in violations if v['constraint'] == constraint_name]) == 0,
                    'value': value,
                    'constraints': constraint_def
                }
            
            result = {
                'overall_valid': len(violations) == 0,
                'validation_results': validation_results,
                'violations': violations,
                'total_violations': len(violations)
            }
            
            self.calculation_history.append({
                'operation': 'physics_constraint_validation',
                'input': {'values': values, 'constraints': constraints},
                'output': result,
                'timestamp': datetime.now()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Physics constraint validation failed: {str(e)}")
            raise

    async def get_calculation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get calculation history"""
        await asyncio.sleep(0)
        
        if limit is None:
            return self.calculation_history
        else:
            return self.calculation_history[-limit:]

    async def clear_calculation_history(self) -> None:
        """Clear calculation history"""
        await asyncio.sleep(0)
        self.calculation_history.clear()
        logger.info("Calculation history cleared")

    async def get_physical_constants(self) -> Dict[str, float]:
        """Get physical constants"""
        await asyncio.sleep(0)
        return self.constants.copy()

    async def get_unit_conversions(self) -> Dict[str, Dict[str, float]]:
        """Get available unit conversions"""
        await asyncio.sleep(0)
        return self.unit_conversions.copy()
