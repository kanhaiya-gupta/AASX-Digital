"""
Physics Event System Example

This module demonstrates how to use the physics-specific event system for actual physics modeling operations
including mesh operations, solver iterations, convergence monitoring, and physics validation.
"""

import asyncio
import logging
from typing import Dict, Any

from .physics_event_manager import PhysicsEventManager
from .physics_event_types import PhysicsEventType, PhysicsEventStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def mesh_quality_handler(event) -> None:
    """Handle mesh operation events."""
    logger.info(f"Mesh operation: {event.operation_type}")
    logger.info(f"Mesh quality: {event.mesh_quality:.3f}")
    logger.info(f"Elements: {event.element_count}, Nodes: {event.node_count}")
    
    # Simulate mesh quality check
    if event.mesh_quality < 0.5:
        logger.warning(f"Poor mesh quality detected: {event.mesh_quality:.3f}")
    else:
        logger.info(f"Good mesh quality: {event.mesh_quality:.3f}")


async def solver_convergence_handler(event) -> None:
    """Handle solver iteration events."""
    logger.info(f"Solver iteration: {event.iteration_number}/{event.max_iterations}")
    logger.info(f"Residual norm: {event.residual_norm:.2e}")
    logger.info(f"Convergence criteria: {event.convergence_criteria:.2e}")
    
    # Simulate convergence check
    if event.residual_norm <= event.convergence_criteria:
        logger.info("Solver converged!")
    elif event.iteration_number >= event.max_iterations:
        logger.warning("Solver reached maximum iterations")


async def physics_validation_handler(event) -> None:
    """Handle physics validation events."""
    logger.info(f"Physics validation: {event.validation_type}")
    logger.info(f"Physics laws: {', '.join(event.physics_laws)}")
    logger.info(f"Validation score: {event.validation_score:.3f}")
    
    # Simulate validation check
    if event.is_valid:
        logger.info("Physics validation passed")
    else:
        logger.warning(f"Physics validation failed: {event.violations}")


async def constraint_check_handler(event) -> None:
    """Handle constraint check events."""
    logger.info(f"Constraint check: {event.constraint_type}")
    logger.info(f"Constraint value: {event.constraint_value:.3f}")
    logger.info(f"Constraint limit: {event.constraint_limit:.3f}")
    
    # Simulate constraint check
    if event.constraint_satisfied:
        logger.info("Constraint satisfied")
    else:
        logger.warning("Constraint violated")


async def demo_structural_analysis_workflow() -> None:
    """Demonstrate a structural analysis workflow using physics events."""
    logger.info("=== Structural Analysis Workflow Demo ===")
    
    # Create physics event manager
    event_manager = PhysicsEventManager()
    
    # Start the event manager
    await event_manager.start()
    
    try:
        # Register physics-specific event handlers
        await event_manager.register_handler(PhysicsEventType.MESH_OPERATION, mesh_quality_handler)
        await event_manager.register_handler(PhysicsEventType.SOLVER_ITERATION, solver_convergence_handler)
        await event_manager.register_handler(PhysicsEventType.PHYSICS_VALIDATION, physics_validation_handler)
        await event_manager.register_handler(PhysicsEventType.CONSTRAINT_CHECK, constraint_check_handler)
        
        # Simulation parameters
        simulation_id = "struct_sim_001"
        twin_id = "bridge_twin_001"
        plugin_id = "structural_fem_plugin"
        
        # 1. Mesh Generation Event
        logger.info("--- Step 1: Mesh Generation ---")
        mesh_event = await event_manager.create_mesh_operation_event(
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            mesh_id="bridge_mesh_001",
            operation_type="generation",
            element_count=50000,
            node_count=150000,
            mesh_quality=0.85,
            quality_threshold=0.3
        )
        
        await event_manager.publish_event(mesh_event)
        
        # 2. Solver Iteration Events (simulate FEM solving)
        logger.info("--- Step 2: FEM Solver Iterations ---")
        for iteration in range(1, 6):
            residual = 1e-3 * (0.5 ** iteration)  # Simulate decreasing residual
            
            solver_event = await event_manager.create_solver_iteration_event(
                simulation_id=simulation_id,
                twin_id=twin_id,
                plugin_id=plugin_id,
                iteration_number=iteration,
                max_iterations=100,
                solver_type="FEM",
                residual_norm=residual,
                convergence_criteria=1e-6
            )
            
            await event_manager.publish_event(solver_event)
            
            # Update iteration progress
            await solver_event.update_iteration_progress(iteration, residual)
            
            await asyncio.sleep(0.1)  # Small delay for demo
        
        # 3. Physics Validation Event
        logger.info("--- Step 3: Physics Validation ---")
        validation_event = await event_manager.create_physics_validation_event(
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            validation_type="structural_mechanics",
            physics_laws=["Hooke's Law", "Equilibrium", "Compatibility"],
            validation_criteria={"min_score": 0.8},
            reference_data={"elastic_modulus": 200e9, "poisson_ratio": 0.3}
        )
        
        # Simulate validation
        await validation_event.perform_physics_validation(0.92, [])
        await event_manager.publish_event(validation_event)
        
        # 4. Constraint Check Event
        logger.info("--- Step 4: Constraint Check ---")
        constraint_event = await event_manager.create_constraint_check_event(
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            constraint_type="displacement_limit",
            constraint_parameters={"tolerance": 0.001},
            constraint_value=0.008,
            constraint_limit=0.010
        )
        
        # Simulate constraint check
        await constraint_event.check_constraint(0.008, 0.010)
        await event_manager.publish_event(constraint_event)
        
        # 5. Post-Processing Event
        logger.info("--- Step 5: Post-Processing ---")
        post_event = await event_manager.create_post_processing_event(
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            processing_type="stress_analysis",
            input_data_size=50000,
            output_data_size=50000,
            processing_method="von_mises_stress"
        )
        
        # Simulate post-processing
        await post_event.perform_post_processing(True, {"max_stress": 150e6, "min_stress": -50e6})
        await event_manager.publish_event(post_event)
        
        # Wait for events to be processed
        await asyncio.sleep(1)
        
        # Get physics-specific metrics
        metrics = await event_manager.get_physics_metrics()
        logger.info("=== Physics Event Metrics ===")
        logger.info(f"Total events: {metrics['total_events']}")
        logger.info(f"Converged events: {metrics['converged_events']}")
        logger.info(f"Diverged events: {metrics['diverged_events']}")
        logger.info(f"Constraint violations: {metrics['constraint_violations']}")
        logger.info(f"Failed events: {metrics['failed_events']}")
        logger.info(f"Convergence rate: {metrics['convergence_rate']:.2%}")
        logger.info(f"Failure rate: {metrics['failure_rate']:.2%}")
        logger.info(f"Average processing time: {metrics['average_processing_time']:.3f}s")
        
        # Get events by type
        mesh_events = await event_manager.get_events_by_type(PhysicsEventType.MESH_OPERATION)
        solver_events = await event_manager.get_events_by_type(PhysicsEventType.SOLVER_ITERATION)
        
        logger.info(f"Mesh events: {len(mesh_events)}")
        logger.info(f"Solver events: {len(solver_events)}")
        
        # Get recent events
        recent_events = await event_manager.get_recent_events(5)
        logger.info(f"Recent events: {len(recent_events)}")
        
    finally:
        # Stop the event manager
        await event_manager.stop()


async def demo_thermal_analysis_workflow() -> None:
    """Demonstrate a thermal analysis workflow using physics events."""
    logger.info("=== Thermal Analysis Workflow Demo ===")
    
    # Create physics event manager
    event_manager = PhysicsEventManager()
    
    # Start the event manager
    await event_manager.start()
    
    try:
        # Register handlers
        await event_manager.register_handler(PhysicsEventType.MESH_OPERATION, mesh_quality_handler)
        await event_manager.register_handler(PhysicsEventType.TIME_STEP, lambda e: logger.info(f"Time step: {e.time_step}/{e.total_time_steps}"))
        await event_manager.register_handler(PhysicsEventType.BOUNDARY_CONDITION, lambda e: logger.info(f"Boundary condition: {e.boundary_type}"))
        
        # Simulation parameters
        simulation_id = "thermal_sim_001"
        twin_id = "engine_twin_001"
        plugin_id = "thermal_fdm_plugin"
        
        # 1. Mesh Operation Event
        logger.info("--- Step 1: Thermal Mesh Generation ---")
        mesh_event = await event_manager.create_mesh_operation_event(
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            mesh_id="engine_thermal_mesh_001",
            operation_type="thermal_optimization",
            element_count=25000,
            node_count=75000,
            mesh_quality=0.78,
            quality_threshold=0.3
        )
        
        await event_manager.publish_event(mesh_event)
        
        # 2. Boundary Condition Events
        logger.info("--- Step 2: Boundary Conditions ---")
        bc_events = [
            ("heat_source", "heat_flux", {"heat_flux": 1000, "area": 0.1}),
            ("cooling_surface", "convection", {"heat_transfer_coeff": 50, "ambient_temp": 25}),
            ("insulation", "adiabatic", {"thermal_resistance": 0.1})
        ]
        
        for bc_id, bc_type, bc_params in bc_events:
            bc_event = await event_manager.create_boundary_condition_event(
                simulation_id=simulation_id,
                twin_id=twin_id,
                plugin_id=plugin_id,
                boundary_id=bc_id,
                boundary_type=bc_type,
                boundary_parameters=bc_params,
                boundary_nodes=list(range(100 * bc_events.index((bc_id, bc_type, bc_params)), 
                                        100 * (bc_events.index((bc_id, bc_type, bc_params)) + 1)))
            )
            
            # Simulate boundary condition application
            await bc_event.apply_boundary_condition(True, {"status": "applied", "nodes_processed": 100})
            await event_manager.publish_event(bc_event)
        
        # 3. Time Stepping Events (transient thermal analysis)
        logger.info("--- Step 3: Time Stepping ---")
        total_steps = 10
        for step in range(1, total_steps + 1):
            time_event = await event_manager.create_time_step_event(
                simulation_id=simulation_id,
                twin_id=twin_id,
                plugin_id=plugin_id,
                time_step=step,
                total_time_steps=total_steps,
                current_time=step * 0.1,  # 0.1 seconds per step
                time_step_size=0.1,
                simulation_duration=1.0
            )
            
            # Simulate time step advancement
            success = step != 5  # Simulate failure at step 5
            details = {"max_temp": 150 + step * 5, "min_temp": 25 + step * 2} if success else {"error": "Numerical instability"}
            
            await time_event.advance_time_step(success, details)
            await event_manager.publish_event(time_event)
            
            await asyncio.sleep(0.1)
        
        # 4. Material Property Event
        logger.info("--- Step 4: Material Properties ---")
        material_event = await event_manager.create_material_property_event(
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            material_id="steel_thermal",
            property_name="thermal_conductivity",
            old_value=45.0,
            new_value=50.0,
            property_unit="W/m·K",
            validation_rules={"min_value": 20.0, "max_value": 100.0}
        )
        
        # Simulate material property update
        await material_event.update_material_property(45.0, 50.0)
        await event_manager.publish_event(material_event)
        
        # Wait for processing
        await asyncio.sleep(1)
        
        # Get metrics
        metrics = await event_manager.get_physics_metrics()
        logger.info("=== Thermal Analysis Metrics ===")
        logger.info(f"Total events: {metrics['total_events']}")
        logger.info(f"Converged events: {metrics['converged_events']}")
        logger.info(f"Failed events: {metrics['failed_events']}")
        logger.info(f"Constraint violations: {metrics['constraint_violations']}")
        
    finally:
        await event_manager.stop()


async def main() -> None:
    """Main demo function."""
    logger.info("Starting Physics Event System Demo")
    
    # Run different physics workflow demos
    await demo_structural_analysis_workflow()
    await asyncio.sleep(1)
    
    await demo_thermal_analysis_workflow()
    
    logger.info("Physics Event System Demo completed!")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())





