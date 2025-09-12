"""
Solver Demo for Physics Modeling

This module demonstrates how to use all the new solvers (FDM, FVM, PINN)
with the solver factory, showing solver selection, creation, and execution.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from .solver_factory import SolverFactory
from .finite_difference_solver import FiniteDifferenceSolver
from .finite_volume_solver import FiniteVolumeSolver
from .pinn_solver import PINNSolver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_solver_factory() -> None:
    """Demonstrate the solver factory capabilities."""
    logger.info("=== Solver Factory Demo ===")
    
    # Create solver factory
    factory = SolverFactory()
    
    # Get all available solver types
    solver_types = await factory.get_all_solver_types()
    logger.info(f"Available solver types: {solver_types}")
    
    # Get solver statistics
    stats = await factory.get_solver_statistics()
    logger.info(f"Total solvers: {stats['total_solvers']}")
    logger.info(f"Solver types: {stats['solver_types']}")
    
    # Show capability summary
    logger.info("=== Solver Capabilities ===")
    for solver_type, capabilities in stats['capability_summary'].items():
        logger.info(f"{solver_type}: {capabilities}")
    
    # Show performance summary
    logger.info("=== Performance Benchmarks ===")
    for solver_type, performance in stats['performance_summary'].items():
        logger.info(f"{solver_type}: {performance}")


async def demo_solver_recommendations() -> None:
    """Demonstrate solver recommendation system."""
    logger.info("=== Solver Recommendations Demo ===")
    
    factory = SolverFactory()
    
    # Example 1: Heat conduction problem
    heat_problem = {
        'physics_type': 'heat_conduction',
        'dimensions': 1,
        'accuracy': 'medium',
        'performance': 'high',
        'grid_points': 1000,
        'simple_geometry': True
    }
    
    logger.info("--- Heat Conduction Problem ---")
    recommendations = await factory.get_solver_recommendations(heat_problem)
    
    for i, rec in enumerate(recommendations[:3]):  # Top 3
        logger.info(f"{i+1}. {rec['solver_type']} (Score: {rec['score']})")
        for reason in rec['reasoning'][:3]:  # Top 3 reasons
            logger.info(f"   - {reason}")
    
    # Example 2: CFD problem
    cfd_problem = {
        'physics_type': 'cfd',
        'dimensions': 2,
        'accuracy': 'high',
        'performance': 'medium',
        'grid_points': 5000,
        'complex_geometry': True,
        'multiphysics': True
    }
    
    logger.info("--- CFD Problem ---")
    recommendations = await factory.get_solver_recommendations(cfd_problem)
    
    for i, rec in enumerate(recommendations[:3]):
        logger.info(f"{i+1}. {rec['solver_type']} (Score: {rec['score']})")
        for reason in rec['reasoning'][:3]:
            logger.info(f"   - {reason}")
    
    # Example 3: Inverse problem
    inverse_problem = {
        'physics_type': 'inverse_problem',
        'dimensions': 1,
        'accuracy': 'high',
        'performance': 'low',
        'grid_points': 1000,
        'inverse_problem': True
    }
    
    logger.info("--- Inverse Problem ---")
    recommendations = await factory.get_solver_recommendations(inverse_problem)
    
    for i, rec in enumerate(recommendations[:3]):
        logger.info(f"{i+1}. {rec['solver_type']} (Score: {rec['score']})")
        for reason in rec['reasoning'][:3]:
            logger.info(f"   - {reason}")


async def demo_optimal_solver_selection() -> None:
    """Demonstrate optimal solver selection."""
    logger.info("=== Optimal Solver Selection Demo ===")
    
    factory = SolverFactory()
    
    # Problem: Heat conduction with high accuracy
    problem_requirements = {
        'physics_type': 'heat_conduction',
        'dimensions': 2,
        'accuracy': 'high',
        'performance': 'medium',
        'grid_points': 2000,
        'simple_geometry': True
    }
    
    logger.info("--- Problem Requirements ---")
    for key, value in problem_requirements.items():
        logger.info(f"  {key}: {value}")
    
    # Get optimal solver
    optimal_solver = await factory.get_optimal_solver(problem_requirements)
    
    if optimal_solver:
        logger.info(f"✅ Optimal solver selected: {optimal_solver.solver_name}")
        solver_info = await optimal_solver.get_solver_info()
        logger.info(f"Solver type: {solver_info['solver_type']}")
        logger.info(f"Supported physics: {solver_info['supported_physics_types']}")
    else:
        logger.warning("❌ No suitable solver found")


async def demo_fdm_solver() -> None:
    """Demonstrate FDM solver capabilities."""
    logger.info("=== FDM Solver Demo ===")
    
    # Create FDM solver
    fdm_solver = FiniteDifferenceSolver()
    await fdm_solver.initialize()
    
    # Set solver parameters
    await fdm_solver.set_parameters({
        'grid_spacing': 0.01,
        'time_step': 0.001,
        'max_iterations': 500
    })
    
    # Solve heat conduction problem
    heat_problem = {
        'physics_type': 'heat_conduction',
        'problem_data': {
            'length': 1.0,
            'thermal_diffusivity': 1e-4,
            'initial_temp': 100.0,
            'boundary_temp_left': 0.0,
            'boundary_temp_right': 0.0,
            'simulation_time': 0.5
        }
    }
    
    logger.info("Solving heat conduction problem with FDM...")
    result = await fdm_solver.solve(heat_problem)
    
    logger.info(f"✅ FDM solution completed in {result['execution_time']:.3f}s")
    logger.info(f"Grid points: {result['grid_info']['spacing']}")
    logger.info(f"Converged: {result['convergence_info']['converged']}")
    logger.info(f"Final residual: {result['convergence_info']['final_residual']:.2e}")


async def demo_fvm_solver() -> None:
    """Demonstrate FVM solver capabilities."""
    logger.info("=== FVM Solver Demo ===")
    
    # Create FVM solver
    fvm_solver = FiniteVolumeSolver()
    await fvm_solver.initialize()
    
    # Set solver parameters
    await fvm_solver.set_parameters({
        'cell_count': 200,
        'flux_scheme': 'upwind',
        'cfl_number': 0.5
    })
    
    # Solve CFD problem
    cfd_problem = {
        'physics_type': 'cfd',
        'problem_data': {
            'domain_length': 1.0,
            'fluid_density': 1.0,
            'fluid_viscosity': 1e-3,
            'inlet_velocity': 1.0,
            'simulation_time': 1.0
        }
    }
    
    logger.info("Solving CFD problem with FVM...")
    result = await fvm_solver.solve(cfd_problem)
    
    logger.info(f"✅ FVM solution completed in {result['execution_time']:.3f}s")
    logger.info(f"Cell count: {result['mesh_info']['cell_count']}")
    logger.info(f"Flux scheme: {result['solver_parameters']['flux_scheme']}")
    logger.info(f"CFL number: {result['solver_parameters']['cfl_number']}")


async def demo_pinn_solver() -> None:
    """Demonstrate PINN solver capabilities."""
    logger.info("=== PINN Solver Demo ===")
    
    # Create PINN solver
    pinn_solver = PINNSolver()
    await pinn_solver.initialize()
    
    # Set solver parameters
    await pinn_solver.set_parameters({
        'network_architecture': [5, 10, 10, 5, 1],
        'learning_rate': 0.001,
        'max_epochs': 1000
    })
    
    # Solve PDE problem
    pde_problem = {
        'physics_type': 'pde',
        'problem_data': {
            'domain_bounds': [0.0, 1.0],
            'time_bounds': [0.0, 1.0],
            'equation_type': 'heat_equation'
        }
    }
    
    logger.info("Solving PDE problem with PINN...")
    result = await pinn_solver.solve(pde_problem)
    
    logger.info(f"✅ PINN solution completed in {result['execution_time']:.3f}s")
    logger.info(f"Network architecture: {result['network_info']['architecture']}")
    logger.info(f"Total parameters: {result['network_info']['total_parameters']}")
    logger.info(f"Training epochs: {result['training_info']['epochs']}")
    logger.info(f"Final loss: {result['training_info']['final_loss']:.6f}")


async def demo_solver_comparison() -> None:
    """Demonstrate solver comparison for the same problem."""
    logger.info("=== Solver Comparison Demo ===")
    
    # Define a common problem (heat conduction)
    common_problem = {
        'physics_type': 'heat_conduction',
        'problem_data': {
            'length': 1.0,
            'thermal_diffusivity': 1e-4,
            'initial_temp': 100.0,
            'boundary_temp_left': 0.0,
            'boundary_temp_right': 0.0,
            'simulation_time': 0.3
        }
    }
    
    # Test FDM solver
    logger.info("--- Testing FDM Solver ---")
    fdm_solver = FiniteDifferenceSolver()
    await fdm_solver.initialize()
    
    start_time = datetime.utcnow()
    fdm_result = await fdm_solver.solve(common_problem)
    fdm_time = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(f"FDM execution time: {fdm_time:.3f}s")
    logger.info(f"FDM converged: {fdm_result['convergence_info']['converged']}")
    
    # Test FVM solver
    logger.info("--- Testing FVM Solver ---")
    fvm_solver = FiniteVolumeSolver()
    await fvm_solver.initialize()
    await fvm_solver.set_parameters({'cell_count': 100})
    
    start_time = datetime.utcnow()
    fvm_result = await fvm_solver.solve(common_problem)
    fvm_time = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(f"FVM execution time: {fvm_time:.3f}s")
    logger.info(f"FVM converged: {fvm_result['convergence_info']['converged']}")
    
    # Test PINN solver (shorter training for demo)
    logger.info("--- Testing PINN Solver ---")
    pinn_solver = PINNSolver()
    await pinn_solver.initialize()
    await pinn_solver.set_parameters({'max_epochs': 100})  # Reduced for demo
    
    start_time = datetime.utcnow()
    pinn_result = await pinn_solver.solve(common_problem)
    pinn_time = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(f"PINN execution time: {pinn_time:.3f}s")
    logger.info(f"PINN converged: {pinn_result['training_info']['converged']}")
    
    # Summary
    logger.info("=== Comparison Summary ===")
    logger.info(f"FDM:  {fdm_time:.3f}s, Converged: {fdm_result['convergence_info']['converged']}")
    logger.info(f"FVM:  {fvm_time:.3f}s, Converged: {fvm_result['convergence_info']['converged']}")
    logger.info(f"PINN: {pinn_time:.3f}s, Converged: {pinn_result['training_info']['converged']}")


async def main() -> None:
    """Main demo function."""
    logger.info("🚀 Starting Comprehensive Solver Demo")
    
    try:
        # Run all demos
        await demo_solver_factory()
        await asyncio.sleep(1)
        
        await demo_solver_recommendations()
        await asyncio.sleep(1)
        
        await demo_optimal_solver_selection()
        await asyncio.sleep(1)
        
        await demo_fdm_solver()
        await asyncio.sleep(1)
        
        await demo_fvm_solver()
        await asyncio.sleep(1)
        
        await demo_pinn_solver()
        await asyncio.sleep(1)
        
        await demo_solver_comparison()
        
        logger.info("🎉 All solver demos completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())





