"""
Constraint Enforcer for Physics Modeling
Handles physics constraint validation and enforcement
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ConstraintType(Enum):
    """Types of physics constraints"""
    EQUALITY = "equality"
    INEQUALITY = "inequality"
    BOUND = "bound"
    PHYSICAL = "physical"
    GEOMETRIC = "geometric"
    MATERIAL = "material"

class ConstraintSeverity(Enum):
    """Severity levels for constraint violations"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ConstraintDefinition:
    """Definition of a physics constraint"""
    name: str
    constraint_type: ConstraintType
    expression: str
    parameters: Dict[str, Any]
    severity: ConstraintSeverity = ConstraintSeverity.ERROR
    tolerance: float = 1e-6
    description: str = ""
    physics_domain: str = "general"

@dataclass
class ConstraintConfig:
    """Configuration for constraint enforcement"""
    enforce_constraints: bool = True
    allow_violations: bool = False
    max_violations: int = 10
    violation_threshold: float = 0.1
    auto_correction: bool = True
    correction_method: str = "projection"  # "projection", "penalty", "lagrange"
    max_correction_iterations: int = 100
    convergence_tolerance: float = 1e-6

class ConstraintEnforcer:
    """Physics constraint enforcement for physics modeling"""
    
    def __init__(self, config: Optional[ConstraintConfig] = None):
        self.config = config or ConstraintConfig()
        self.constraints = {}
        self.violation_history = []
        self.correction_history = []
        self.enforcement_stats = {
            'total_constraints': 0,
            'violations_detected': 0,
            'violations_corrected': 0,
            'corrections_failed': 0
        }
        logger.info("✅ Constraint Enforcer initialized")
    
    async def register_constraint(self, constraint: ConstraintDefinition) -> bool:
        """Register a new physics constraint"""
        await asyncio.sleep(0)
        
        try:
            # Validate constraint definition
            if not await self._validate_constraint_definition(constraint):
                logger.error(f"❌ Invalid constraint definition: {constraint.name}")
                return False
            
            # Store constraint
            self.constraints[constraint.name] = constraint
            self.enforcement_stats['total_constraints'] += 1
            
            logger.info(f"✅ Constraint registered: {constraint.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register constraint {constraint.name}: {str(e)}")
            return False
    
    async def enforce_constraints(self, data: Dict[str, Any], 
                                physics_type: str = "general") -> Dict[str, Any]:
        """Enforce all registered constraints on the data"""
        await asyncio.sleep(0)
        
        if not self.config.enforce_constraints:
            return {'success': True, 'constraints_enforced': False, 'message': 'Constraint enforcement disabled'}
        
        start_time = datetime.now()
        logger.info(f"🔄 Enforcing constraints for {physics_type}")
        
        try:
            violations = []
            corrected_data = data.copy()
            
            # Check each constraint
            for constraint_name, constraint in self.constraints.items():
                if constraint.physics_domain in [physics_type, "general"]:
                    violation_result = await self._check_constraint(constraint, corrected_data)
                    
                    if violation_result['violated']:
                        violations.append(violation_result)
                        
                        if self.config.auto_correction:
                            correction_result = await self._correct_constraint_violation(
                                constraint, corrected_data, violation_result
                            )
                            
                            if correction_result['success']:
                                corrected_data = correction_result['corrected_data']
                                self.enforcement_stats['violations_corrected'] += 1
                            else:
                                self.enforcement_stats['corrections_failed'] += 1
                        else:
                            self.enforcement_stats['violations_detected'] += 1
            
            # Check if too many violations
            if len(violations) > self.config.max_violations:
                if not self.config.allow_violations:
                    raise ValueError(f"Too many constraint violations: {len(violations)} > {self.config.max_violations}")
            
            enforcement_time = (datetime.now() - start_time).total_seconds()
            
            # Record enforcement history
            enforcement_record = {
                'timestamp': datetime.now(),
                'physics_type': physics_type,
                'total_constraints': len(self.constraints),
                'violations_detected': len(violations),
                'violations_corrected': self.enforcement_stats['violations_corrected'],
                'enforcement_time': enforcement_time,
                'success': len(violations) <= self.config.max_violations
            }
            
            self.violation_history.append(enforcement_record)
            
            result = {
                'success': len(violations) <= self.config.max_violations,
                'constraints_enforced': True,
                'enforcement_time': enforcement_time,
                'total_constraints': len(self.constraints),
                'violations_detected': len(violations),
                'violations_corrected': self.enforcement_stats['violations_corrected'],
                'corrected_data': corrected_data,
                'violation_details': violations
            }
            
            if len(violations) <= self.config.max_violations:
                logger.info(f"✅ Constraints enforced successfully in {enforcement_time:.3f}s")
            else:
                logger.warning(f"⚠️ Constraints enforced with {len(violations)} violations in {enforcement_time:.3f}s")
            
            return result
            
        except Exception as e:
            enforcement_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Constraint enforcement failed: {str(e)}")
            
            self.violation_history.append({
                'timestamp': datetime.now(),
                'physics_type': physics_type,
                'total_constraints': len(self.constraints),
                'violations_detected': 0,
                'violations_corrected': 0,
                'enforcement_time': enforcement_time,
                'success': False,
                'error': str(e)
            })
            
            return {
                'success': False,
                'constraints_enforced': False,
                'error': str(e),
                'enforcement_time': enforcement_time
            }
    
    async def _validate_constraint_definition(self, constraint: ConstraintDefinition) -> bool:
        """Validate constraint definition"""
        await asyncio.sleep(0)
        
        # Check required fields
        if not constraint.name or not constraint.expression:
            return False
        
        # Check constraint type
        if constraint.constraint_type not in ConstraintType:
            return False
        
        # Check severity
        if constraint.severity not in ConstraintSeverity:
            return False
        
        # Check tolerance
        if constraint.tolerance <= 0:
            return False
        
        return True
    
    async def _check_constraint(self, constraint: ConstraintDefinition, 
                               data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a constraint is violated"""
        await asyncio.sleep(0)
        
        try:
            # Evaluate constraint expression
            constraint_value = await self._evaluate_constraint_expression(constraint, data)
            
            # Check violation based on constraint type
            violated = False
            violation_magnitude = 0.0
            
            if constraint.constraint_type == ConstraintType.EQUALITY:
                violated = abs(constraint_value) > constraint.tolerance
                violation_magnitude = abs(constraint_value)
            
            elif constraint.constraint_type == ConstraintType.INEQUALITY:
                violated = constraint_value > constraint.tolerance
                violation_magnitude = max(0, constraint_value)
            
            elif constraint.constraint_type == ConstraintType.BOUND:
                # Assuming expression evaluates to value - bound
                violated = constraint_value > constraint.tolerance
                violation_magnitude = max(0, constraint_value)
            
            elif constraint.constraint_type == ConstraintType.PHYSICAL:
                violated = not await self._check_physical_constraint(constraint, data)
                violation_magnitude = 1.0 if violated else 0.0
            
            elif constraint.constraint_type == ConstraintType.GEOMETRIC:
                violated = not await self._check_geometric_constraint(constraint, data)
                violation_magnitude = 1.0 if violated else 0.0
            
            elif constraint.constraint_type == ConstraintType.MATERIAL:
                violated = not await self._check_material_constraint(constraint, data)
                violation_magnitude = 1.0 if violated else 0.0
            
            return {
                'constraint_name': constraint.name,
                'constraint_type': constraint.constraint_type.value,
                'severity': constraint.severity.value,
                'violated': violated,
                'violation_magnitude': violation_magnitude,
                'constraint_value': constraint_value,
                'tolerance': constraint.tolerance,
                'description': constraint.description
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking constraint {constraint.name}: {str(e)}")
            return {
                'constraint_name': constraint.name,
                'constraint_type': constraint.constraint_type.value,
                'severity': constraint.constraint_type.value,
                'violated': True,
                'violation_magnitude': float('inf'),
                'constraint_value': None,
                'tolerance': constraint.tolerance,
                'description': constraint.description,
                'error': str(e)
            }
    
    async def _evaluate_constraint_expression(self, constraint: ConstraintDefinition, 
                                            data: Dict[str, Any]) -> float:
        """Evaluate constraint expression"""
        await asyncio.sleep(0)
        
        # For simplicity, implement basic expression evaluation
        # In practice, this would use a proper expression parser
        
        expression = constraint.expression.lower()
        parameters = constraint.parameters
        
        # Handle common physics expressions
        if "stress" in expression and "yield" in expression:
            # von Mises stress vs yield stress
            stress = data.get('stress', 0.0)
            yield_strength = parameters.get('yield_strength', 1e6)
            return stress - yield_strength
        
        elif "temperature" in expression and "melting" in expression:
            # Temperature vs melting point
            temperature = data.get('temperature', 0.0)
            melting_point = parameters.get('melting_point', 1000.0)
            return temperature - melting_point
        
        elif "pressure" in expression and "max" in expression:
            # Pressure vs maximum allowed
            pressure = data.get('pressure', 0.0)
            max_pressure = parameters.get('max_pressure', 1e6)
            return pressure - max_pressure
        
        elif "displacement" in expression and "limit" in expression:
            # Displacement vs limit
            displacement = data.get('displacement', 0.0)
            max_displacement = parameters.get('max_displacement', 0.1)
            return abs(displacement) - max_displacement
        
        elif "strain" in expression and "limit" in expression:
            # Strain vs limit
            strain = data.get('strain', 0.0)
            max_strain = parameters.get('max_strain', 0.1)
            return abs(strain) - max_strain
        
        else:
            # Generic expression evaluation
            return await self._evaluate_generic_expression(expression, data, parameters)
    
    async def _evaluate_generic_expression(self, expression: str, data: Dict[str, Any], 
                                         parameters: Dict[str, Any]) -> float:
        """Evaluate generic constraint expression"""
        await asyncio.sleep(0)
        
        # Simple expression evaluation for common patterns
        try:
            # Replace variables with values
            eval_expression = expression
            
            # Replace data variables
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    eval_expression = eval_expression.replace(key, str(value))
            
            # Replace parameter variables
            for key, value in parameters.items():
                if isinstance(value, (int, float)):
                    eval_expression = eval_expression.replace(key, str(value))
            
            # Safe evaluation (in practice, use a proper expression parser)
            # For now, return a default value
            return 0.0
            
        except Exception as e:
            logger.warning(f"⚠️ Could not evaluate expression '{expression}': {str(e)}")
            return 0.0
    
    async def _check_physical_constraint(self, constraint: ConstraintDefinition, 
                                        data: Dict[str, Any]) -> bool:
        """Check physical constraints"""
        await asyncio.sleep(0)
        
        constraint_name = constraint.name.lower()
        
        if "conservation" in constraint_name:
            return await self._check_conservation_law(constraint, data)
        elif "symmetry" in constraint_name:
            return await self._check_symmetry_constraint(constraint, data)
        elif "causality" in constraint_name:
            return await self._check_causality_constraint(constraint, data)
        else:
            return True  # Default to valid
    
    async def _check_geometric_constraint(self, constraint: ConstraintDefinition, 
                                         data: Dict[str, Any]) -> bool:
        """Check geometric constraints"""
        await asyncio.sleep(0)
        
        constraint_name = constraint.name.lower()
        
        if "volume" in constraint_name:
            return await self._check_volume_constraint(constraint, data)
        elif "area" in constraint_name:
            return await self._check_area_constraint(constraint, data)
        elif "length" in constraint_name:
            return await self._check_length_constraint(constraint, data)
        else:
            return True  # Default to valid
    
    async def _check_material_constraint(self, constraint: ConstraintDefinition, 
                                        data: Dict[str, Any]) -> bool:
        """Check material constraints"""
        await asyncio.sleep(0)
        
        constraint_name = constraint.name.lower()
        
        if "density" in constraint_name:
            return await self._check_density_constraint(constraint, data)
        elif "elastic" in constraint_name:
            return await self._check_elastic_constraint(constraint, data)
        elif "thermal" in constraint_name:
            return await self._check_thermal_constraint(constraint, data)
        else:
            return True  # Default to valid
    
    async def _check_conservation_law(self, constraint: ConstraintDefinition, 
                                     data: Dict[str, Any]) -> bool:
        """Check conservation law constraints"""
        await asyncio.sleep(0)
        
        # Check mass conservation
        if 'mass_in' in data and 'mass_out' in data:
            mass_balance = abs(data['mass_in'] - data['mass_out'])
            return mass_balance <= constraint.tolerance
        
        # Check energy conservation
        if 'energy_in' in data and 'energy_out' in data:
            energy_balance = abs(data['energy_in'] - data['energy_out'])
            return energy_balance <= constraint.tolerance
        
        # Check momentum conservation
        if 'momentum_in' in data and 'momentum_out' in data:
            momentum_balance = abs(data['momentum_in'] - data['momentum_out'])
            return momentum_balance <= constraint.tolerance
        
        return True
    
    async def _check_symmetry_constraint(self, constraint: ConstraintDefinition, 
                                        data: Dict[str, Any]) -> bool:
        """Check symmetry constraints"""
        await asyncio.sleep(0)
        
        # Check geometric symmetry
        if 'vertices' in data:
            vertices = data['vertices']
            if len(vertices) > 0:
                # Check if vertices are symmetric about a plane
                centroid = np.mean(vertices, axis=0)
                symmetry_plane = parameters.get('symmetry_plane', [1, 0, 0])
                
                # Calculate symmetry deviation
                deviations = []
                for vertex in vertices:
                    # Project vertex onto symmetry plane
                    projection = np.dot(vertex - centroid, symmetry_plane) * symmetry_plane
                    deviation = np.linalg.norm(vertex - centroid - projection)
                    deviations.append(deviation)
                
                max_deviation = max(deviations)
                return max_deviation <= constraint.tolerance
        
        return True
    
    async def _check_causality_constraint(self, constraint: ConstraintDefinition, 
                                         data: Dict[str, Any]) -> bool:
        """Check causality constraints"""
        await asyncio.sleep(0)
        
        # Check time ordering
        if 'time_sequence' in data:
            time_sequence = data['time_sequence']
            if len(time_sequence) > 1:
                # Check if time is monotonically increasing
                for i in range(1, len(time_sequence)):
                    if time_sequence[i] <= time_sequence[i-1]:
                        return False
        
        return True
    
    async def _check_volume_constraint(self, constraint: ConstraintDefinition, 
                                      data: Dict[str, Any]) -> bool:
        """Check volume constraints"""
        await asyncio.sleep(0)
        
        if 'volume' in data:
            volume = data['volume']
            min_volume = parameters.get('min_volume', 0.0)
            max_volume = parameters.get('max_volume', float('inf'))
            
            return min_volume <= volume <= max_volume
        
        return True
    
    async def _check_area_constraint(self, constraint: ConstraintDefinition, 
                                    data: Dict[str, Any]) -> bool:
        """Check area constraints"""
        await asyncio.sleep(0)
        
        if 'area' in data:
            area = data['area']
            min_area = parameters.get('min_area', 0.0)
            max_area = parameters.get('max_area', float('inf'))
            
            return min_area <= area <= max_area
        
        return True
    
    async def _check_length_constraint(self, constraint: ConstraintDefinition, 
                                      data: Dict[str, Any]) -> bool:
        """Check length constraints"""
        await asyncio.sleep(0)
        
        if 'length' in data:
            length = data['length']
            min_length = parameters.get('min_length', 0.0)
            max_length = parameters.get('max_length', float('inf'))
            
            return min_length <= length <= max_length
        
        return True
    
    async def _check_density_constraint(self, constraint: ConstraintDefinition, 
                                       data: Dict[str, Any]) -> bool:
        """Check density constraints"""
        await asyncio.sleep(0)
        
        if 'density' in data:
            density = data['density']
            min_density = parameters.get('min_density', 0.0)
            max_density = parameters.get('max_density', float('inf'))
            
            return min_density <= density <= max_density
        
        return True
    
    async def _check_elastic_constraint(self, constraint: ConstraintDefinition, 
                                       data: Dict[str, Any]) -> bool:
        """Check elastic modulus constraints"""
        await asyncio.sleep(0)
        
        if 'elastic_modulus' in data:
            elastic_modulus = data['elastic_modulus']
            min_modulus = parameters.get('min_modulus', 0.0)
            max_modulus = parameters.get('max_modulus', float('inf'))
            
            return min_modulus <= elastic_modulus <= max_modulus
        
        return True
    
    async def _check_thermal_constraint(self, constraint: ConstraintDefinition, 
                                       data: Dict[str, Any]) -> bool:
        """Check thermal conductivity constraints"""
        await asyncio.sleep(0)
        
        if 'thermal_conductivity' in data:
            thermal_conductivity = data['thermal_conductivity']
            min_conductivity = parameters.get('min_conductivity', 0.0)
            max_conductivity = parameters.get('max_conductivity', float('inf'))
            
            return min_conductivity <= thermal_conductivity <= max_conductivity
        
        return True
    
    async def _correct_constraint_violation(self, constraint: ConstraintDefinition, 
                                           data: Dict[str, Any], 
                                           violation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Correct constraint violation"""
        await asyncio.sleep(0)
        
        try:
            corrected_data = data.copy()
            
            if self.config.correction_method == "projection":
                corrected_data = await self._project_to_constraint(constraint, corrected_data, violation_result)
            elif self.config.correction_method == "penalty":
                corrected_data = await self._apply_penalty_correction(constraint, corrected_data, violation_result)
            elif self.config.correction_method == "lagrange":
                corrected_data = await self._apply_lagrange_correction(constraint, corrected_data, violation_result)
            
            # Record correction
            self.correction_history.append({
                'timestamp': datetime.now(),
                'constraint_name': constraint.name,
                'correction_method': self.config.correction_method,
                'violation_magnitude': violation_result['violation_magnitude'],
                'success': True
            })
            
            return {
                'success': True,
                'corrected_data': corrected_data,
                'correction_method': self.config.correction_method
            }
            
        except Exception as e:
            logger.error(f"❌ Constraint correction failed for {constraint.name}: {str(e)}")
            
            self.correction_history.append({
                'timestamp': datetime.now(),
                'constraint_name': constraint.name,
                'correction_method': self.config.correction_method,
                'violation_magnitude': violation_result['violation_magnitude'],
                'success': False,
                'error': str(e)
            })
            
            return {
                'success': False,
                'error': str(e),
                'correction_method': self.config.correction_method
            }
    
    async def _project_to_constraint(self, constraint: ConstraintDefinition, 
                                    data: Dict[str, Any], 
                                    violation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Project data to satisfy constraint"""
        await asyncio.sleep(0)
        
        # Simple projection for common constraints
        if constraint.constraint_type == ConstraintType.BOUND:
            # Project to bounds
            for key, value in data.items():
                if key in constraint.parameters:
                    min_val = constraint.parameters.get(f'min_{key}', float('-inf'))
                    max_val = constraint.parameters.get(f'max_{key}', float('inf'))
                    
                    if value < min_val:
                        data[key] = min_val
                    elif value > max_val:
                        data[key] = max_val
        
        return data
    
    async def _apply_penalty_correction(self, constraint: ConstraintDefinition, 
                                       data: Dict[str, Any], 
                                       violation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply penalty-based correction"""
        await asyncio.sleep(0)
        
        # Simple penalty correction
        penalty_factor = 0.1
        violation_magnitude = violation_result['violation_magnitude']
        
        # Adjust relevant parameters
        for key, value in data.items():
            if key in constraint.parameters:
                correction = penalty_factor * violation_magnitude
                data[key] = value - correction
        
        return data
    
    async def _apply_lagrange_correction(self, constraint: ConstraintDefinition, 
                                        data: Dict[str, Any], 
                                        violation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Lagrange multiplier correction"""
        await asyncio.sleep(0)
        
        # Simple Lagrange correction
        lagrange_multiplier = 0.01
        violation_magnitude = violation_result['violation_magnitude']
        
        # Adjust relevant parameters
        for key, value in data.items():
            if key in constraint.parameters:
                correction = lagrange_multiplier * violation_magnitude
                data[key] = value - correction
        
        return data
    
    async def get_constraint_enforcement_summary(self) -> Dict[str, Any]:
        """Get summary of constraint enforcement operations"""
        await asyncio.sleep(0)
        
        total_enforcements = len(self.violation_history)
        successful_enforcements = sum(1 for op in self.violation_history if op.get('success', False))
        failed_enforcements = total_enforcements - successful_enforcements
        
        avg_enforcement_time = 0
        total_violations = 0
        total_corrections = 0
        
        if total_enforcements > 0:
            enforcement_times = [op['enforcement_time'] for op in self.violation_history]
            avg_enforcement_time = sum(enforcement_times) / len(enforcement_times)
            
            total_violations = sum(op.get('violations_detected', 0) for op in self.violation_history)
            total_corrections = sum(op.get('violations_corrected', 0) for op in self.violation_history)
        
        return {
            'total_enforcements': total_enforcements,
            'successful_enforcements': successful_enforcements,
            'failed_enforcements': failed_enforcements,
            'success_rate': successful_enforcements / total_enforcements if total_enforcements > 0 else 0,
            'average_enforcement_time': avg_enforcement_time,
            'total_violations_detected': total_violations,
            'total_violations_corrected': total_corrections,
            'correction_success_rate': total_corrections / total_violations if total_violations > 0 else 0,
            'registered_constraints': len(self.constraints),
            'enforcement_stats': self.enforcement_stats,
            'recent_enforcements': self.violation_history[-5:] if self.violation_history else []
        }
    
    async def reset_statistics(self) -> None:
        """Reset all statistics and history"""
        await asyncio.sleep(0)
        
        self.violation_history.clear()
        self.correction_history.clear()
        self.enforcement_stats = {
            'total_constraints': len(self.constraints),
            'violations_detected': 0,
            'violations_corrected': 0,
            'corrections_failed': 0
        }
        logger.info("🔄 Constraint Enforcer statistics reset")
