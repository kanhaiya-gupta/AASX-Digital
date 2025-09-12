"""
Data Processing Demo for Physics Modeling
Demonstrates the usage of DataPreprocessor, MeshGenerator, ConstraintEnforcer, and PerformanceOptimizer
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any
from datetime import datetime

from .data_preprocessor import DataPreprocessor, PreprocessingConfig
from .mesh_generator import MeshGenerator, MeshConfig, MeshType, ElementType
from .constraint_enforcer import ConstraintEnforcer, ConstraintConfig, ConstraintDefinition, ConstraintType, ConstraintSeverity
from .performance_optimizer import PerformanceOptimizer, OptimizationConfig, OptimizationStrategy, ResourceConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_data_preprocessing() -> None:
    """Demonstrate data preprocessing capabilities"""
    logger.info("🔄 Starting Data Preprocessing Demo")
    
    # Create preprocessor with custom configuration
    config = PreprocessingConfig(
        normalize_data=True,
        remove_outliers=True,
        outlier_threshold=2.5,
        fill_missing=True,
        fill_strategy="interpolate",
        scale_features=True,
        scale_method="minmax",
        validate_physics_constraints=True
    )
    
    preprocessor = DataPreprocessor(config)
    
    # Create sample data with missing values and outliers
    sample_data = np.array([
        [1.0, 2.0, 3.0, np.nan, 5.0],
        [6.0, 7.0, 8.0, 9.0, 10.0],
        [11.0, 12.0, 13.0, 14.0, 15.0],
        [16.0, 17.0, 18.0, 19.0, 20.0],
        [21.0, 22.0, 23.0, 24.0, 25.0],
        [100.0, 27.0, 28.0, 29.0, 30.0]  # Outlier
    ])
    
    # Preprocess different types of data
    data_types = ["temperature", "pressure", "displacement", "strain"]
    
    for data_type in data_types:
        logger.info(f"🔄 Preprocessing {data_type} data...")
        
        # Add some physics-specific data
        if data_type == "temperature":
            data = sample_data + 273.15  # Convert to Kelvin
        elif data_type == "pressure":
            data = sample_data * 1e5  # Convert to Pa
        else:
            data = sample_data
        
        result = await preprocessor.preprocess_data(data, data_type)
        
        if result['success']:
            logger.info(f"✅ {data_type} preprocessing completed")
            logger.info(f"   Processing time: {result['processing_time']:.3f}s")
            logger.info(f"   Data ready: {result['final_validation']['data_ready']}")
            logger.info(f"   Violations: {len(result['validation_results'].get('violations', []))}")
        else:
            logger.error(f"❌ {data_type} preprocessing failed: {result.get('error', 'Unknown error')}")
    
    # Get preprocessing summary
    summary = await preprocessor.get_preprocessing_summary()
    logger.info(f"📊 Preprocessing Summary:")
    logger.info(f"   Total operations: {summary['total_operations']}")
    logger.info(f"   Success rate: {summary['success_rate']:.2%}")
    logger.info(f"   Average processing time: {summary['average_processing_time']:.3f}s")

async def demo_mesh_generation() -> None:
    """Demonstrate mesh generation capabilities"""
    logger.info("🔄 Starting Mesh Generation Demo")
    
    # Create mesh generator with custom configuration
    config = MeshConfig(
        mesh_type=MeshType.UNSTRUCTURED,
        element_type=ElementType.TRIANGLE,
        resolution=0.5,
        quality_threshold=0.4,
        smoothing_iterations=3,
        use_adaptive_refinement=True
    )
    
    mesh_generator = MeshGenerator(config)
    
    # Create sample geometry data
    geometry_data = {
        'vertices': np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
            [0.5, 0.5]
        ]),
        'faces': np.array([
            [0, 1, 4],
            [1, 2, 4],
            [2, 3, 4],
            [3, 0, 4]
        ]),
        'dimensions': 1.0
    }
    
    # Generate meshes for different physics types
    physics_types = ["structural", "thermal", "fluid", "electromagnetic"]
    
    for physics_type in physics_types:
        logger.info(f"🔄 Generating {physics_type} mesh...")
        
        result = await mesh_generator.generate_mesh(geometry_data, physics_type)
        
        if result['success']:
            logger.info(f"✅ {physics_type} mesh generation completed")
            logger.info(f"   Generation time: {result['generation_time']:.3f}s")
            logger.info(f"   Total vertices: {result['mesh_statistics']['total_vertices']}")
            logger.info(f"   Total elements: {result['mesh_statistics']['total_elements']}")
            logger.info(f"   Overall quality: {result['quality_assessment']['overall_quality']:.3f}")
        else:
            logger.error(f"❌ {physics_type} mesh generation failed: {result.get('error', 'Unknown error')}")
    
    # Get mesh generation summary
    summary = await mesh_generator.get_mesh_generation_summary()
    logger.info(f"📊 Mesh Generation Summary:")
    logger.info(f"   Total operations: {summary['total_operations']}")
    logger.info(f"   Success rate: {summary['success_rate']:.2%}")
    logger.info(f"   Average generation time: {summary['average_generation_time']:.3f}s")
    logger.info(f"   Average quality score: {summary['average_quality_score']:.3f}")

async def demo_constraint_enforcement() -> None:
    """Demonstrate constraint enforcement capabilities"""
    logger.info("🔄 Starting Constraint Enforcement Demo")
    
    # Create constraint enforcer with custom configuration
    config = ConstraintConfig(
        enforce_constraints=True,
        allow_violations=False,
        max_violations=5,
        auto_correction=True,
        correction_method="projection"
    )
    
    constraint_enforcer = ConstraintEnforcer(config)
    
    # Register various physics constraints
    constraints = [
        ConstraintDefinition(
            name="yield_strength",
            constraint_type=ConstraintType.INEQUALITY,
            expression="stress - yield_strength",
            parameters={"yield_strength": 250e6},  # 250 MPa
            severity=ConstraintSeverity.ERROR,
            tolerance=1e6,
            description="Stress must not exceed yield strength",
            physics_domain="structural"
        ),
        ConstraintDefinition(
            name="temperature_limit",
            constraint_type=ConstraintType.BOUND,
            expression="temperature - max_temp",
            parameters={"max_temp": 1000.0},  # 1000 K
            severity=ConstraintSeverity.WARNING,
            tolerance=10.0,
            description="Temperature must be below maximum",
            physics_domain="thermal"
        ),
        ConstraintDefinition(
            name="volume_conservation",
            constraint_type=ConstraintType.PHYSICAL,
            expression="volume_change",
            parameters={"max_change": 0.01},  # 1% change
            severity=ConstraintSeverity.ERROR,
            tolerance=0.001,
            description="Volume must be conserved",
            physics_domain="fluid"
        )
    ]
    
    # Register constraints
    for constraint in constraints:
        success = await constraint_enforcer.register_constraint(constraint)
        if success:
            logger.info(f"✅ Constraint registered: {constraint.name}")
        else:
            logger.error(f"❌ Failed to register constraint: {constraint.name}")
    
    # Test constraint enforcement with different data
    test_cases = [
        {
            "name": "structural_data",
            "data": {"stress": 300e6, "temperature": 298.15, "volume": 1.0},
            "physics_type": "structural"
        },
        {
            "name": "thermal_data",
            "data": {"stress": 100e6, "temperature": 1200.0, "volume": 1.0},
            "physics_type": "thermal"
        },
        {
            "name": "fluid_data",
            "data": {"stress": 50e6, "temperature": 298.15, "volume": 1.02},
            "physics_type": "fluid"
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"🔄 Testing constraints for {test_case['name']}...")
        
        result = await constraint_enforcer.enforce_constraints(
            test_case['data'], 
            test_case['physics_type']
        )
        
        if result['success']:
            logger.info(f"✅ Constraints enforced successfully")
            logger.info(f"   Violations detected: {result['violations_detected']}")
            logger.info(f"   Violations corrected: {result['violations_corrected']}")
            logger.info(f"   Enforcement time: {result['enforcement_time']:.3f}s")
        else:
            logger.error(f"❌ Constraint enforcement failed: {result.get('error', 'Unknown error')}")
    
    # Get constraint enforcement summary
    summary = await constraint_enforcer.get_constraint_enforcement_summary()
    logger.info(f"📊 Constraint Enforcement Summary:")
    logger.info(f"   Total enforcements: {summary['total_enforcements']}")
    logger.info(f"   Success rate: {summary['success_rate']:.2%}")
    logger.info(f"   Total violations detected: {summary['total_violations_detected']}")
    logger.info(f"   Total violations corrected: {summary['total_violations_corrected']}")

async def demo_performance_optimization() -> None:
    """Demonstrate performance optimization capabilities"""
    logger.info("🔄 Starting Performance Optimization Demo")
    
    # Create performance optimizer with custom configuration
    opt_config = OptimizationConfig(
        strategy=OptimizationStrategy.GENETIC_ALGORITHM,
        max_iterations=100,
        population_size=20,
        mutation_rate=0.15,
        crossover_rate=0.85
    )
    
    resource_config = ResourceConfig(
        max_cpu_usage=0.7,
        max_memory_usage=0.7,
        max_gpu_usage=0.8,
        enable_resource_monitoring=True
    )
    
    optimizer = PerformanceOptimizer(opt_config, resource_config)
    
    # Define objective functions for different optimization problems
    def structural_optimization(parameters):
        """Minimize weight while maintaining strength"""
        weight = parameters.get('weight', 1.0)
        strength = parameters.get('strength', 100.0)
        target_strength = 200.0
        
        # Penalty for insufficient strength
        strength_penalty = max(0, target_strength - strength) * 1000
        
        return weight + strength_penalty
    
    def thermal_optimization(parameters):
        """Minimize thermal resistance"""
        thickness = parameters.get('thickness', 0.01)
        conductivity = parameters.get('conductivity', 50.0)
        
        # Thermal resistance = thickness / conductivity
        thermal_resistance = thickness / conductivity
        
        # Penalty for unrealistic values
        thickness_penalty = max(0, thickness - 0.1) * 1000
        conductivity_penalty = max(0, 10.0 - conductivity) * 1000
        
        return thermal_resistance + thickness_penalty + conductivity_penalty
    
    def fluid_optimization(parameters):
        """Minimize pressure drop"""
        diameter = parameters.get('diameter', 0.1)
        length = parameters.get('length', 1.0)
        velocity = parameters.get('velocity', 5.0)
        
        # Simplified pressure drop calculation
        pressure_drop = length * velocity**2 / (diameter**5)
        
        # Penalty for unrealistic values
        diameter_penalty = max(0, 0.01 - diameter) * 1000
        length_penalty = max(0, length - 10.0) * 1000
        
        return pressure_drop + diameter_penalty + length_penalty
    
    # Test different optimization strategies
    optimization_problems = [
        {
            "name": "structural_optimization",
            "objective_function": structural_optimization,
            "initial_parameters": {"weight": 2.0, "strength": 150.0},
            "constraints": [
                {"parameter": "weight", "min": 0.1, "max": 5.0},
                {"parameter": "strength", "min": 100.0, "max": 300.0}
            ]
        },
        {
            "name": "thermal_optimization",
            "objective_function": thermal_optimization,
            "initial_parameters": {"thickness": 0.02, "conductivity": 30.0},
            "constraints": [
                {"parameter": "thickness", "min": 0.001, "max": 0.1},
                {"parameter": "conductivity", "min": 10.0, "max": 100.0}
            ]
        },
        {
            "name": "fluid_optimization",
            "objective_function": fluid_optimization,
            "initial_parameters": {"diameter": 0.05, "length": 2.0, "velocity": 3.0},
            "constraints": [
                {"parameter": "diameter", "min": 0.01, "max": 0.2},
                {"parameter": "length", "min": 0.1, "max": 10.0},
                {"parameter": "velocity", "min": 1.0, "max": 20.0}
            ]
        }
    ]
    
    # Test different optimization strategies
    strategies = [
        OptimizationStrategy.GRADIENT_DESCENT,
        OptimizationStrategy.GENETIC_ALGORITHM,
        OptimizationStrategy.PARTICLE_SWARM
    ]
    
    for strategy in strategies:
        logger.info(f"🔄 Testing {strategy.value} optimization...")
        
        # Update optimizer configuration
        optimizer.opt_config.strategy = strategy
        
        for problem in optimization_problems:
            logger.info(f"   Optimizing {problem['name']}...")
            
            result = await optimizer.optimize_performance(
                problem['objective_function'],
                problem['initial_parameters'],
                problem['constraints'],
                f"{strategy.value}_{problem['name']}"
            )
            
            if result['success']:
                logger.info(f"     ✅ Optimization completed")
                logger.info(f"     Initial objective: {result['initial_objective']:.6f}")
                logger.info(f"     Final objective: {result['optimal_objective']:.6f}")
                logger.info(f"     Improvement: {result['improvement']:.6f}")
                logger.info(f"     Iterations: {result['iterations']}")
                logger.info(f"     Converged: {result['converged']}")
            else:
                logger.error(f"     ❌ Optimization failed: {result.get('error', 'Unknown error')}")
    
    # Get optimization summary
    summary = await optimizer.get_optimization_summary()
    logger.info(f"📊 Performance Optimization Summary:")
    logger.info(f"   Total optimizations: {summary['total_optimizations']}")
    logger.info(f"   Success rate: {summary['success_rate']:.2%}")
    logger.info(f"   Average optimization time: {summary['average_optimization_time']:.3f}s")
    logger.info(f"   Average improvement: {summary['average_improvement']:.6f}")
    
    # Get resource usage summary
    resource_summary = await optimizer.get_resource_usage_summary()
    logger.info(f"📊 Resource Usage Summary:")
    logger.info(f"   Average CPU usage: {resource_summary['average_usage']['cpu']:.2%}")
    logger.info(f"   Average memory usage: {resource_summary['average_usage']['memory']:.2%}")
    logger.info(f"   Average GPU usage: {resource_summary['average_usage']['gpu']:.2%}")

async def demo_integrated_workflow() -> None:
    """Demonstrate integrated workflow using all components"""
    logger.info("🔄 Starting Integrated Workflow Demo")
    
    # Create all components
    preprocessor = DataPreprocessor()
    mesh_generator = MeshGenerator()
    constraint_enforcer = ConstraintEnforcer()
    optimizer = PerformanceOptimizer()
    
    # Simulate a complete physics modeling workflow
    logger.info("🔄 Simulating complete physics modeling workflow...")
    
    # Step 1: Data preprocessing
    logger.info("   Step 1: Preprocessing simulation data...")
    simulation_data = np.random.rand(100, 5) * 1000  # Random simulation data
    preprocessing_result = await preprocessor.preprocess_data(simulation_data, "multiphysics")
    
    if not preprocessing_result['success']:
        logger.error("❌ Data preprocessing failed, aborting workflow")
        return
    
    logger.info("   ✅ Data preprocessing completed")
    
    # Step 2: Mesh generation
    logger.info("   Step 2: Generating computational mesh...")
    geometry_data = {
        'vertices': np.random.rand(50, 3) * 10,
        'faces': np.random.randint(0, 50, (100, 3)),
        'dimensions': 10.0
    }
    
    mesh_result = await mesh_generator.generate_mesh(geometry_data, "multiphysics")
    
    if not mesh_result['success']:
        logger.error("❌ Mesh generation failed, aborting workflow")
        return
    
    logger.info("   ✅ Mesh generation completed")
    
    # Step 3: Constraint enforcement
    logger.info("   Step 3: Enforcing physics constraints...")
    
    # Register some constraints
    await constraint_enforcer.register_constraint(
        ConstraintDefinition(
            name="energy_conservation",
            constraint_type=ConstraintType.PHYSICAL,
            expression="energy_balance",
            parameters={"tolerance": 0.01},
            physics_domain="multiphysics"
        )
    )
    
    # Create simulation parameters
    simulation_params = {
        'time_step': 0.001,
        'max_iterations': 1000,
        'convergence_tolerance': 1e-6,
        'energy_in': 1000.0,
        'energy_out': 999.5
    }
    
    constraint_result = await constraint_enforcer.enforce_constraints(
        simulation_params, "multiphysics"
    )
    
    if not constraint_result['success']:
        logger.error("❌ Constraint enforcement failed, aborting workflow")
        return
    
    logger.info("   ✅ Constraint enforcement completed")
    
    # Step 4: Performance optimization
    logger.info("   Step 4: Optimizing simulation parameters...")
    
    def simulation_objective(parameters):
        """Minimize simulation time while maintaining accuracy"""
        time_step = parameters.get('time_step', 0.001)
        max_iterations = parameters.get('max_iterations', 1000)
        
        # Simplified objective: minimize time step and iterations
        objective = time_step * 1000 + max_iterations / 1000
        
        # Penalty for too small time step (numerical instability)
        if time_step < 0.0001:
            objective += 1000
        
        # Penalty for too many iterations (slow convergence)
        if max_iterations > 2000:
            objective += 1000
        
        return objective
    
    optimization_result = await optimizer.optimize_performance(
        simulation_objective,
        {'time_step': 0.001, 'max_iterations': 1000},
        [
            {'parameter': 'time_step', 'min': 0.0001, 'max': 0.01},
            {'parameter': 'max_iterations', 'min': 100, 'max': 2000}
        ],
        'simulation_optimization'
    )
    
    if not optimization_result['success']:
        logger.error("❌ Performance optimization failed, aborting workflow")
        return
    
    logger.info("   ✅ Performance optimization completed")
    
    # Workflow summary
    logger.info("🎉 Complete workflow simulation finished successfully!")
    logger.info(f"   Final optimized parameters: {optimization_result['optimal_parameters']}")
    logger.info(f"   Overall improvement: {optimization_result['improvement']:.6f}")
    logger.info(f"   Total workflow time: {preprocessing_result['processing_time'] + mesh_result['generation_time'] + constraint_result['enforcement_time'] + optimization_result['optimization_time']:.3f}s")

async def main() -> None:
    """Main demo function"""
    logger.info("🚀 Starting Physics Modeling Data Processing Demo")
    logger.info("=" * 60)
    
    try:
        # Run individual component demos
        await demo_data_preprocessing()
        logger.info("-" * 40)
        
        await demo_mesh_generation()
        logger.info("-" * 40)
        
        await demo_constraint_enforcement()
        logger.info("-" * 40)
        
        await demo_performance_optimization()
        logger.info("-" * 40)
        
        # Run integrated workflow demo
        await demo_integrated_workflow()
        
        logger.info("=" * 60)
        logger.info("🎉 All demos completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())





