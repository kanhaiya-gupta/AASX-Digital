"""
Solver Factory for Physics Modeling

This module provides a factory for creating and managing different types of solvers,
with intelligent solver selection based on physics problem requirements.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime

from .base_solver import BaseSolver
from .finite_difference_solver import FiniteDifferenceSolver
from .finite_volume_solver import FiniteVolumeSolver
from .pinn_solver import PINNSolver
from .structural_solver import StructuralSolver
from .thermal_solver import ThermalSolver

logger = logging.getLogger(__name__)


class SolverFactory:
    """
    Factory for creating and managing physics solvers.
    
    Provides intelligent solver selection based on problem requirements,
    solver capabilities, and performance characteristics.
    """
    
    def __init__(self):
        """Initialize the solver factory."""
        self.available_solvers = {
            'FDM': FiniteDifferenceSolver,
            'FVM': FiniteVolumeSolver,
            'PINN': PINNSolver,
            'Structural': StructuralSolver,
            'Thermal': ThermalSolver
        }
        
        # Solver capability mapping
        self.solver_capabilities = {
            'FDM': {
                'physics_types': ['heat_conduction', 'wave_propagation', 'diffusion', 'fluid_dynamics'],
                'dimensions': [1, 2, 3],
                'accuracy': 'medium',
                'performance': 'high',
                'memory_usage': 'low',
                'best_for': ['Simple geometries', 'Regular grids', 'Linear problems']
            },
            'FVM': {
                'physics_types': ['cfd', 'conservation_laws', 'multiphysics', 'transport_phenomena'],
                'dimensions': [1, 2, 3],
                'accuracy': 'high',
                'performance': 'medium',
                'memory_usage': 'medium',
                'best_for': ['Complex geometries', 'Conservation laws', 'Multiphysics']
            },
            'PINN': {
                'physics_types': ['pde', 'ode', 'inverse_problem', 'data_driven_discovery'],
                'dimensions': [1, 2, 3],
                'accuracy': 'variable',
                'performance': 'low',
                'memory_usage': 'high',
                'best_for': ['Inverse problems', 'Data-driven discovery', 'Complex PDEs']
            },
            'Structural': {
                'physics_types': ['structural_mechanics', 'elasticity', 'plasticity'],
                'dimensions': [1, 2, 3],
                'accuracy': 'high',
                'performance': 'high',
                'memory_usage': 'medium',
                'best_for': ['Solid mechanics', 'Structural analysis', 'Material modeling']
            },
            'Thermal': {
                'physics_types': ['heat_transfer', 'thermal_analysis', 'conduction', 'convection'],
                'dimensions': [1, 2, 3],
                'accuracy': 'high',
                'performance': 'high',
                'memory_usage': 'low',
                'best_for': ['Thermal analysis', 'Heat transfer', 'Temperature fields']
            }
        }
        
        # Performance benchmarks (execution time in seconds for standard problems)
        self.performance_benchmarks = {
            'FDM': {'small': 0.1, 'medium': 1.0, 'large': 10.0},
            'FVM': {'small': 0.5, 'medium': 5.0, 'large': 50.0},
            'PINN': {'small': 10.0, 'medium': 100.0, 'large': 1000.0},
            'Structural': {'small': 0.2, 'medium': 2.0, 'large': 20.0},
            'Thermal': {'small': 0.15, 'medium': 1.5, 'large': 15.0}
        }
        
        logger.info("✅ Solver Factory initialized with comprehensive solver capabilities")

    async def create_solver(self, solver_type: str, **kwargs) -> Optional[BaseSolver]:
        """
        Create a solver instance of the specified type.
        
        Args:
            solver_type: Type of solver to create
            **kwargs: Additional parameters for solver initialization
            
        Returns:
            Solver instance or None if creation fails
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            if solver_type not in self.available_solvers:
                logger.error(f"Unknown solver type: {solver_type}")
                return None
            
            # Create solver instance
            solver_class = self.available_solvers[solver_type]
            solver = solver_class()
            
            # Initialize solver
            if not await solver.initialize():
                logger.error(f"Failed to initialize {solver_type} solver")
                return None
            
            # Set additional parameters if provided
            if kwargs:
                await solver.set_parameters(kwargs)
            
            logger.info(f"✅ Created and initialized {solver_type} solver")
            return solver
            
        except Exception as e:
            logger.error(f"Failed to create {solver_type} solver: {e}")
            return None

    async def get_solver_recommendations(self, problem_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get solver recommendations based on problem requirements.
        
        Args:
            problem_requirements: Dictionary containing problem specifications
            
        Returns:
            List of solver recommendations with scores and reasoning
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            recommendations = []
            
            for solver_type, capabilities in self.solver_capabilities.items():
                score = 0
                reasoning = []
                
                # Check physics type compatibility
                required_physics = problem_requirements.get('physics_type', '')
                if required_physics in capabilities['physics_types']:
                    score += 30
                    reasoning.append(f"Supports required physics type: {required_physics}")
                else:
                    reasoning.append(f"Does not support physics type: {required_physics}")
                
                # Check dimension compatibility
                required_dimensions = problem_requirements.get('dimensions', 1)
                if required_dimensions in capabilities['dimensions']:
                    score += 20
                    reasoning.append(f"Supports {required_dimensions}D problems")
                else:
                    reasoning.append(f"Does not support {required_dimensions}D problems")
                
                # Check accuracy requirements
                required_accuracy = problem_requirements.get('accuracy', 'medium')
                if required_accuracy == 'high' and capabilities['accuracy'] == 'high':
                    score += 25
                    reasoning.append("Meets high accuracy requirements")
                elif required_accuracy == 'medium':
                    score += 15
                    reasoning.append("Meets medium accuracy requirements")
                
                # Check performance requirements
                required_performance = problem_requirements.get('performance', 'medium')
                if required_performance == 'high' and capabilities['performance'] == 'high':
                    score += 15
                    reasoning.append("Meets high performance requirements")
                elif required_performance == 'medium':
                    score += 10
                    reasoning.append("Meets medium performance requirements")
                
                # Check memory constraints
                memory_constraint = problem_requirements.get('memory_constraint', 'medium')
                if memory_constraint == 'low' and capabilities['memory_usage'] == 'low':
                    score += 10
                    reasoning.append("Meets low memory requirements")
                elif memory_constraint == 'medium':
                    score += 5
                    reasoning.append("Meets medium memory requirements")
                
                # Add solver-specific advantages
                if solver_type == 'PINN' and problem_requirements.get('inverse_problem', False):
                    score += 20
                    reasoning.append("Excellent for inverse problems")
                
                if solver_type == 'FVM' and problem_requirements.get('complex_geometry', False):
                    score += 15
                    reasoning.append("Excellent for complex geometries")
                
                if solver_type == 'FDM' and problem_requirements.get('simple_geometry', True):
                    score += 10
                    reasoning.append("Efficient for simple geometries")
                
                recommendations.append({
                    'solver_type': solver_type,
                    'score': score,
                    'reasoning': reasoning,
                    'capabilities': capabilities,
                    'performance_estimate': self._estimate_performance(solver_type, problem_requirements)
                })
            
            # Sort by score (highest first)
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Generated {len(recommendations)} solver recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate solver recommendations: {e}")
            return []

    async def get_optimal_solver(self, problem_requirements: Dict[str, Any]) -> Optional[BaseSolver]:
        """
        Get the optimal solver for the given problem requirements.
        
        Args:
            problem_requirements: Dictionary containing problem specifications
            
        Returns:
            Optimal solver instance or None if no suitable solver found
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Get recommendations
            recommendations = await self.get_solver_recommendations(problem_requirements)
            
            if not recommendations:
                logger.warning("No suitable solver found for the given requirements")
                return None
            
            # Get the top recommendation
            top_recommendation = recommendations[0]
            
            if top_recommendation['score'] < 50:
                logger.warning(f"Best solver score ({top_recommendation['score']}) is below threshold")
                return None
            
            # Create the optimal solver
            optimal_solver = await self.create_solver(top_recommendation['solver_type'])
            
            if optimal_solver:
                logger.info(f"✅ Created optimal solver: {top_recommendation['solver_type']} (score: {top_recommendation['score']})")
            
            return optimal_solver
            
        except Exception as e:
            logger.error(f"Failed to get optimal solver: {e}")
            return None

    def _estimate_performance(self, solver_type: str, problem_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate solver performance for the given problem."""
        try:
            # Determine problem size
            grid_points = problem_requirements.get('grid_points', 1000)
            if grid_points < 1000:
                size_category = 'small'
            elif grid_points < 10000:
                size_category = 'medium'
            else:
                size_category = 'large'
            
            # Get benchmark performance
            benchmark_time = self.performance_benchmarks[solver_type][size_category]
            
            # Adjust for problem complexity
            complexity_factor = 1.0
            if problem_requirements.get('nonlinear', False):
                complexity_factor *= 2.0
            if problem_requirements.get('multiphysics', False):
                complexity_factor *= 1.5
            if problem_requirements.get('high_accuracy', False):
                complexity_factor *= 1.3
            
            estimated_time = benchmark_time * complexity_factor
            
            return {
                'estimated_execution_time': estimated_time,
                'size_category': size_category,
                'complexity_factor': complexity_factor,
                'confidence': 'medium'
            }
            
        except Exception as e:
            logger.error(f"Failed to estimate performance: {e}")
            return {
                'estimated_execution_time': 0.0,
                'size_category': 'unknown',
                'complexity_factor': 1.0,
                'confidence': 'low'
            }

    async def get_solver_capabilities(self, solver_type: str) -> Optional[Dict[str, Any]]:
        """Get detailed capabilities for a specific solver type."""
        await asyncio.sleep(0)  # Pure async
        
        if solver_type not in self.solver_capabilities:
            return None
        
        return self.solver_capabilities[solver_type].copy()

    async def get_all_solver_types(self) -> List[str]:
        """Get list of all available solver types."""
        await asyncio.sleep(0)  # Pure async
        return list(self.available_solvers.keys())

    async def validate_solver_compatibility(self, solver_type: str, problem_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if a specific solver is compatible with the problem requirements.
        
        Args:
            solver_type: Type of solver to validate
            problem_requirements: Problem specifications
            
        Returns:
            Validation result with compatibility details
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            if solver_type not in self.solver_capabilities:
                return {
                    'compatible': False,
                    'reason': f"Unknown solver type: {solver_type}",
                    'score': 0
                }
            
            capabilities = self.solver_capabilities[solver_type]
            validation_result = {
                'compatible': True,
                'issues': [],
                'warnings': [],
                'score': 100
            }
            
            # Check physics type compatibility
            required_physics = problem_requirements.get('physics_type', '')
            if required_physics and required_physics not in capabilities['physics_types']:
                validation_result['compatible'] = False
                validation_result['issues'].append(f"Physics type '{required_physics}' not supported")
                validation_result['score'] -= 30
            
            # Check dimension compatibility
            required_dimensions = problem_requirements.get('dimensions', 1)
            if required_dimensions not in capabilities['dimensions']:
                validation_result['compatible'] = False
                validation_result['issues'].append(f"{required_dimensions}D problems not supported")
                validation_result['score'] -= 20
            
            # Check accuracy requirements
            required_accuracy = problem_requirements.get('accuracy', 'medium')
            if required_accuracy == 'high' and capabilities['accuracy'] != 'high':
                validation_result['warnings'].append("High accuracy requirement may not be met")
                validation_result['score'] -= 10
            
            # Check performance requirements
            required_performance = problem_requirements.get('performance', 'medium')
            if required_performance == 'high' and capabilities['performance'] != 'high':
                validation_result['warnings'].append("High performance requirement may not be met")
                validation_result['score'] -= 10
            
            # Ensure score doesn't go below 0
            validation_result['score'] = max(0, validation_result['score'])
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate solver compatibility: {e}")
            return {
                'compatible': False,
                'reason': f"Validation error: {e}",
                'score': 0
            }

    async def get_solver_statistics(self) -> Dict[str, Any]:
        """Get statistics about available solvers."""
        await asyncio.sleep(0)  # Pure async
        
        stats = {
            'total_solvers': len(self.available_solvers),
            'solver_types': list(self.available_solvers.keys()),
            'capability_summary': {},
            'performance_summary': {}
        }
        
        # Generate capability summary
        for solver_type, capabilities in self.solver_capabilities.items():
            stats['capability_summary'][solver_type] = {
                'supported_physics_types': len(capabilities['physics_types']),
                'dimensions': capabilities['dimensions'],
                'accuracy': capabilities['accuracy'],
                'performance': capabilities['performance']
            }
        
        # Generate performance summary
        for solver_type, benchmarks in self.performance_benchmarks.items():
            stats['performance_summary'][solver_type] = {
                'small_problem_time': benchmarks['small'],
                'medium_problem_time': benchmarks['medium'],
                'large_problem_time': benchmarks['large']
            }
        
        return stats
