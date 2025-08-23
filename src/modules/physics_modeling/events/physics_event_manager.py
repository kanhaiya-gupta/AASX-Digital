"""
Physics-Specific Event Manager for Physics Modeling

This module provides a focused event management system specifically for physics modeling operations
including mesh operations, solver iterations, convergence monitoring, and physics validation.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from collections import defaultdict

from .physics_event_types import (
    BasePhysicsEvent,
    PhysicsEventType,
    PhysicsEventStatus,
    PhysicsEventPriority
)

logger = logging.getLogger(__name__)


class PhysicsEventManager:
    """Event manager specifically for physics modeling operations."""
    
    def __init__(self):
        self.event_handlers: Dict[PhysicsEventType, List[Callable]] = defaultdict(list)
        self.event_history: List[BasePhysicsEvent] = []
        self.max_history_size = 1000
        self.processing = False
        
        # Physics-specific metrics
        self.physics_metrics = {
            "total_events": 0,
            "converged_events": 0,
            "diverged_events": 0,
            "constraint_violations": 0,
            "failed_events": 0,
            "average_processing_time": 0.0
        }
    
    async def start(self) -> None:
        """Start the physics event manager."""
        await asyncio.sleep(0)  # Pure async
        self.processing = True
        logger.info("Physics Event Manager started")
    
    async def stop(self) -> None:
        """Stop the physics event manager."""
        await asyncio.sleep(0)  # Pure async
        self.processing = False
        logger.info("Physics Event Manager stopped")
    
    async def register_handler(self, event_type: PhysicsEventType, handler: Callable) -> None:
        """Register a handler for a specific physics event type."""
        await asyncio.sleep(0)  # Pure async
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type.value} events")
    
    async def publish_event(self, event: BasePhysicsEvent) -> str:
        """Publish a physics event."""
        await asyncio.sleep(0)  # Pure async
        
        if not self.processing:
            logger.warning("Event manager not running, event not processed")
            return event.event_id
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Update metrics
        self.physics_metrics["total_events"] += 1
        
        # Process event
        await self._process_event(event)
        
        logger.info(f"Published physics event: {event.event_id} ({event.event_type.value})")
        return event.event_id
    
    async def _process_event(self, event: BasePhysicsEvent) -> None:
        """Process a physics event."""
        await asyncio.sleep(0)  # Pure async
        
        start_time = datetime.utcnow()
        
        try:
            # Mark as processing
            await event.mark_processing_started()
            
            # Get handlers for this event type
            handlers = self.event_handlers.get(event.event_type, [])
            
            if not handlers:
                logger.warning(f"No handlers registered for event type: {event.event_type.value}")
                return
            
            # Execute all handlers
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {str(e)}")
            
            # Update metrics based on final status
            await self._update_metrics(event)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_average_processing_time(processing_time)
            
        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {str(e)}")
            await event.mark_failed(str(e))
    
    async def _update_metrics(self, event: BasePhysicsEvent) -> None:
        """Update physics-specific metrics."""
        await asyncio.sleep(0)  # Pure async
        
        if event.status == PhysicsEventStatus.CONVERGED:
            self.physics_metrics["converged_events"] += 1
        elif event.status == PhysicsEventStatus.DIVERGED:
            self.physics_metrics["diverged_events"] += 1
        elif event.status == PhysicsEventStatus.CONSTRAINT_VIOLATION:
            self.physics_metrics["constraint_violations"] += 1
        elif event.status == PhysicsEventStatus.FAILED:
            self.physics_metrics["failed_events"] += 1
    
    async def _update_average_processing_time(self, processing_time: float) -> None:
        """Update average processing time."""
        await asyncio.sleep(0)  # Pure async
        
        total_events = self.physics_metrics["total_events"]
        current_avg = self.physics_metrics["average_processing_time"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_events - 1)) + processing_time) / total_events
        self.physics_metrics["average_processing_time"] = new_avg
    
    async def get_physics_metrics(self) -> Dict[str, Any]:
        """Get physics-specific metrics."""
        await asyncio.sleep(0)  # Pure async
        
        # Calculate additional metrics
        total_events = self.physics_metrics["total_events"]
        if total_events > 0:
            convergence_rate = self.physics_metrics["converged_events"] / total_events
            failure_rate = (self.physics_metrics["failed_events"] + self.physics_metrics["diverged_events"]) / total_events
        else:
            convergence_rate = 0.0
            failure_rate = 0.0
        
        return {
            **self.physics_metrics,
            "convergence_rate": convergence_rate,
            "failure_rate": failure_rate,
            "processing": self.processing,
            "history_size": len(self.event_history)
        }
    
    async def get_events_by_type(self, event_type: PhysicsEventType) -> List[BasePhysicsEvent]:
        """Get all events of a specific type."""
        await asyncio.sleep(0)  # Pure async
        return [event for event in self.event_history if event.event_type == event_type]
    
    async def get_events_by_status(self, status: PhysicsEventStatus) -> List[BasePhysicsEvent]:
        """Get all events with a specific status."""
        await asyncio.sleep(0)  # Pure async
        return [event for event in self.event_history if event.status == status]
    
    async def get_recent_events(self, count: int = 10) -> List[BasePhysicsEvent]:
        """Get the most recent events."""
        await asyncio.sleep(0)  # Pure async
        return self.event_history[-count:] if self.event_history else []
    
    async def clear_history(self) -> None:
        """Clear event history."""
        await asyncio.sleep(0)  # Pure async
        self.event_history.clear()
        logger.info("Event history cleared")
    
    # Physics-specific event creation methods
    
    async def create_mesh_operation_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                        mesh_id: str, operation_type: str, **kwargs) -> BasePhysicsEvent:
        """Create a mesh operation event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import MeshOperationEvent
        
        event = MeshOperationEvent(
            event_type=PhysicsEventType.MESH_OPERATION,
            event_name=f"Mesh Operation: {operation_type}",
            source_service="mesh_service",
            target_services=["simulation_service", "quality_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            mesh_id=mesh_id,
            operation_type=operation_type,
            **kwargs
        )
        
        return event
    
    async def create_solver_iteration_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                          iteration_number: int, max_iterations: int,
                                          solver_type: str, **kwargs) -> BasePhysicsEvent:
        """Create a solver iteration event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import SolverIterationEvent
        
        event = SolverIterationEvent(
            event_type=PhysicsEventType.SOLVER_ITERATION,
            event_name=f"Solver Iteration: {solver_type}",
            source_service="solver_service",
            target_services=["monitoring_service", "convergence_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            iteration_number=iteration_number,
            max_iterations=max_iterations,
            solver_type=solver_type,
            **kwargs
        )
        
        return event
    
    async def create_convergence_check_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                           check_type: str, **kwargs) -> BasePhysicsEvent:
        """Create a convergence check event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import ConvergenceCheckEvent
        
        event = ConvergenceCheckEvent(
            event_type=PhysicsEventType.CONVERGENCE_CHECK,
            event_name=f"Convergence Check: {check_type}",
            source_service="convergence_service",
            target_services=["monitoring_service", "simulation_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            check_type=check_type,
            **kwargs
        )
        
        return event
    
    async def create_physics_validation_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                            validation_type: str, physics_laws: List[str], **kwargs) -> BasePhysicsEvent:
        """Create a physics validation event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import PhysicsValidationEvent
        
        event = PhysicsValidationEvent(
            event_type=PhysicsEventType.PHYSICS_VALIDATION,
            event_name=f"Physics Validation: {validation_type}",
            source_service="validation_service",
            target_services=["compliance_service", "simulation_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            validation_type=validation_type,
            physics_laws=physics_laws,
            **kwargs
        )
        
        return event
    
    async def create_constraint_check_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                         constraint_type: str, **kwargs) -> BasePhysicsEvent:
        """Create a constraint check event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import ConstraintCheckEvent
        
        event = ConstraintCheckEvent(
            event_type=PhysicsEventType.CONSTRAINT_CHECK,
            event_name=f"Constraint Check: {constraint_type}",
            source_service="constraint_service",
            target_services=["simulation_service", "monitoring_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            constraint_type=constraint_type,
            **kwargs
        )
        
        return event
    
    async def create_boundary_condition_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                           boundary_id: str, boundary_type: str, **kwargs) -> BasePhysicsEvent:
        """Create a boundary condition event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import BoundaryConditionEvent
        
        event = BoundaryConditionEvent(
            event_type=PhysicsEventType.BOUNDARY_CONDITION,
            event_name=f"Boundary Condition: {boundary_type}",
            source_service="boundary_service",
            target_services=["simulation_service", "monitoring_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            boundary_id=boundary_id,
            boundary_type=boundary_type,
            **kwargs
        )
        
        return event
    
    async def create_material_property_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                          material_id: str, property_name: str, **kwargs) -> BasePhysicsEvent:
        """Create a material property event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import MaterialPropertyEvent
        
        event = MaterialPropertyEvent(
            event_type=PhysicsEventType.MATERIAL_PROPERTY,
            event_name=f"Material Property: {property_name}",
            source_service="material_service",
            target_services=["simulation_service", "validation_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            material_id=material_id,
            property_name=property_name,
            **kwargs
        )
        
        return event
    
    async def create_time_step_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                   time_step: int, total_time_steps: int, **kwargs) -> BasePhysicsEvent:
        """Create a time step event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import TimeStepEvent
        
        event = TimeStepEvent(
            event_type=PhysicsEventType.TIME_STEP,
            event_name=f"Time Step: {time_step}/{total_time_steps}",
            source_service="time_stepping_service",
            target_services=["simulation_service", "monitoring_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            time_step=time_step,
            total_time_steps=total_time_steps,
            **kwargs
        )
        
        return event
    
    async def create_post_processing_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                        processing_type: str, **kwargs) -> BasePhysicsEvent:
        """Create a post-processing event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import PostProcessingEvent
        
        event = PostProcessingEvent(
            event_type=PhysicsEventType.POST_PROCESSING,
            event_name=f"Post-Processing: {processing_type}",
            source_service="post_processing_service",
            target_services=["results_service", "visualization_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            processing_type=processing_type,
            **kwargs
        )
        
        return event
    
    async def create_error_analysis_event(self, simulation_id: str, twin_id: str, plugin_id: str,
                                       analysis_type: str, **kwargs) -> BasePhysicsEvent:
        """Create an error analysis event."""
        await asyncio.sleep(0)  # Pure async
        
        from .physics_event_types import ErrorAnalysisEvent
        
        event = ErrorAnalysisEvent(
            event_type=PhysicsEventType.ERROR_ANALYSIS,
            event_name=f"Error Analysis: {analysis_type}",
            source_service="error_analysis_service",
            target_services=["quality_service", "simulation_service"],
            simulation_id=simulation_id,
            twin_id=twin_id,
            plugin_id=plugin_id,
            analysis_type=analysis_type,
            **kwargs
        )
        
        return event
