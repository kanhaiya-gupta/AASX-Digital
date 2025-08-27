"""
Example Usage of Physics Modeling Event System

This module demonstrates how to use the event system for various physics modeling operations
including simulations, ML training, validation, and compliance monitoring.
"""

import asyncio
import logging
from typing import Dict, Any

from .event_manager import PhysicsModelingEventManager, EventSubscription
from .event_types import EventType, EventPriority

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def simulation_event_handler(event) -> None:
    """Handle simulation events."""
    logger.info(f"Simulation event received: {event.event_id}")
    logger.info(f"Simulation type: {event.simulation_type}")
    logger.info(f"Twin ID: {event.twin_id}")
    logger.info(f"Plugin ID: {event.plugin_id}")


async def ml_training_event_handler(event) -> None:
    """Handle ML training events."""
    logger.info(f"ML training event received: {event.event_id}")
    logger.info(f"Model type: {event.model_type}")
    logger.info(f"Dataset ID: {event.dataset_id}")
    logger.info(f"Current epoch: {event.current_epoch}/{event.total_epochs}")


async def validation_event_handler(event) -> None:
    """Handle validation events."""
    logger.info(f"Validation event received: {event.event_id}")
    logger.info(f"Validation type: {event.validation_type}")
    logger.info(f"Model ID: {event.model_id}")


async def compliance_event_handler(event) -> None:
    """Handle compliance events."""
    logger.info(f"Compliance event received: {event.event_id}")
    logger.info(f"Compliance type: {event.compliance_type}")
    logger.info(f"Framework: {event.regulatory_framework}")


async def service_event_handler(event) -> None:
    """Handle service events."""
    logger.info(f"Service event received: {event.event_id}")
    logger.info(f"Service ID: {event.service_id}")
    logger.info(f"Operation: {event.operation}")


async def demo_physics_simulation_workflow() -> None:
    """Demonstrate a complete physics simulation workflow using events."""
    logger.info("=== Physics Simulation Workflow Demo ===")
    
    # Create event manager
    event_manager = PhysicsModelingEventManager()
    
    # Start the event manager
    await event_manager.start()
    
    try:
        # Subscribe to events
        await event_manager.subscribe(EventSubscription(
            service_name="simulation_monitor",
            event_types=[EventType.SIMULATION],
            handler=simulation_event_handler,
            priority=EventPriority.HIGH
        ))
        
        await event_manager.subscribe(EventSubscription(
            service_name="metrics_collector",
            event_types=[EventType.SIMULATION, EventType.ML_TRAINING, EventType.VALIDATION],
            handler=lambda e: logger.info(f"Metrics collected for event: {e.event_id}"),
            priority=EventPriority.NORMAL
        ))
        
        # Create and publish simulation events
        simulation_event = await event_manager.create_simulation_event(
            simulation_id="sim_001",
            simulation_type="structural",
            twin_id="twin_001",
            plugin_id="structural_plugin",
            parameters={"load": 1000, "material": "steel"},
            constraints={"max_displacement": 0.01}
        )
        
        await event_manager.publish_event(simulation_event)
        
        # Create and publish ML training events
        training_event = await event_manager.create_ml_training_event(
            training_id="train_001",
            model_type="PINN",
            dataset_id="dataset_001",
            hyperparameters={"learning_rate": 0.001, "epochs": 1000},
            training_config={"batch_size": 32, "validation_split": 0.2}
        )
        
        await event_manager.publish_event(training_event)
        
        # Create and publish validation events
        validation_event = await event_manager.create_validation_event(
            validation_id="val_001",
            validation_type="model_accuracy",
            model_id="model_001",
            validation_criteria={"threshold": 0.95, "min_samples": 1000},
            test_data={"size": 1000, "features": 10}
        )
        
        await event_manager.publish_event(validation_event)
        
        # Create and publish compliance events
        compliance_event = await event_manager.create_compliance_event(
            compliance_id="comp_001",
            compliance_type="regulatory",
            regulatory_framework="ISO_9001",
            compliance_rules={"quality_management": True, "documentation": True},
            audit_requirements={"annual_review": True, "external_audit": False}
        )
        
        await event_manager.publish_event(compliance_event)
        
        # Create and publish service events
        service_event = await event_manager.create_service_event(
            service_id="simulation_service",
            operation="health_check",
            service_status="healthy",
            health_score=0.95
        )
        
        await event_manager.publish_event(service_event)
        
        # Wait for events to be processed
        await asyncio.sleep(2)
        
        # Get system statistics
        stats = await event_manager.get_system_stats()
        logger.info("=== System Statistics ===")
        logger.info(f"Processing: {stats['processing']}")
        logger.info(f"Active workers: {stats['active_workers']}")
        logger.info(f"Queue sizes: {stats['queue_sizes']}")
        logger.info(f"Events processed: {stats['stats']['events_processed']}")
        logger.info(f"Events failed: {stats['stats']['events_failed']}")
        logger.info(f"Average processing time: {stats['stats']['average_processing_time']:.3f}s")
        
    finally:
        # Stop the event manager
        await event_manager.stop()


async def demo_event_priority_handling() -> None:
    """Demonstrate event priority handling."""
    logger.info("=== Event Priority Handling Demo ===")
    
    event_manager = PhysicsModelingEventManager()
    await event_manager.start()
    
    try:
        # Subscribe to all event types
        await event_manager.subscribe(EventSubscription(
            service_name="priority_demo",
            event_types=[EventType.SIMULATION, EventType.ML_TRAINING, EventType.VALIDATION],
            handler=lambda e: logger.info(f"Processing {e.priority.value} priority event: {e.event_id}"),
            priority=EventPriority.NORMAL
        ))
        
        # Create events with different priorities
        low_priority_event = await event_manager.create_simulation_event(
            simulation_id="sim_low",
            simulation_type="thermal",
            twin_id="twin_001",
            plugin_id="thermal_plugin"
        )
        low_priority_event.priority = EventPriority.LOW
        
        normal_priority_event = await event_manager.create_simulation_event(
            simulation_id="sim_normal",
            simulation_type="structural",
            twin_id="twin_001",
            plugin_id="structural_plugin"
        )
        normal_priority_event.priority = EventPriority.NORMAL
        
        high_priority_event = await event_manager.create_simulation_event(
            simulation_id="sim_high",
            simulation_type="fluid",
            twin_id="twin_001",
            plugin_id="fluid_plugin"
        )
        high_priority_event.priority = EventPriority.HIGH
        
        critical_priority_event = await event_manager.create_simulation_event(
            simulation_id="sim_critical",
            simulation_type="multi_physics",
            twin_id="twin_001",
            plugin_id="multi_physics_plugin"
        )
        critical_priority_event.priority = EventPriority.CRITICAL
        
        # Publish events in random order
        await event_manager.publish_event(normal_priority_event)
        await event_manager.publish_event(low_priority_event)
        await event_manager.publish_event(critical_priority_event)
        await event_manager.publish_event(high_priority_event)
        
        # Wait for processing
        await asyncio.sleep(3)
        
    finally:
        await event_manager.stop()


async def demo_error_handling_and_retries() -> None:
    """Demonstrate error handling and retry mechanisms."""
    logger.info("=== Error Handling and Retries Demo ===")
    
    event_manager = PhysicsModelingEventManager()
    await event_manager.start()
    
    try:
        # Add custom error handler
        async def custom_error_handler(event, error):
            logger.error(f"Custom error handler: Event {event.event_id} failed with {str(error)}")
            logger.error(f"Retry count: {event.retry_count}/{event.max_retries}")
        
        await event_manager.add_error_handler(custom_error_handler)
        
        # Subscribe to events
        await event_manager.subscribe(EventSubscription(
            service_name="error_demo",
            event_types=[EventType.SIMULATION],
            handler=lambda e: logger.info(f"Processing event: {e.event_id}"),
            priority=EventPriority.NORMAL
        ))
        
        # Create a simulation event
        simulation_event = await event_manager.create_simulation_event(
            simulation_id="sim_error_demo",
            simulation_type="structural",
            twin_id="twin_001",
            plugin_id="structural_plugin"
        )
        
        # Set low max retries for demo
        simulation_event.max_retries = 2
        
        await event_manager.publish_event(simulation_event)
        
        # Wait for processing and potential retries
        await asyncio.sleep(5)
        
        # Get final statistics
        stats = await event_manager.get_system_stats()
        logger.info(f"Events retried: {stats['stats']['events_retried']}")
        
    finally:
        await event_manager.stop()


async def main() -> None:
    """Main demo function."""
    logger.info("Starting Physics Modeling Event System Demo")
    
    # Run different demos
    await demo_physics_simulation_workflow()
    await asyncio.sleep(1)
    
    await demo_event_priority_handling()
    await asyncio.sleep(1)
    
    await demo_error_handling_and_retries()
    
    logger.info("Demo completed!")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())


