"""
Physics-Specific Event Types for Physics Modeling

This module defines physics-specific event types that are relevant to physics modeling operations,
including simulation steps, mesh operations, solver convergence, and physics validation.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4


class PhysicsEventPriority(Enum):
    """Physics event priority levels for processing order."""
    LOW = "low"           # Background operations (logging, monitoring)
    NORMAL = "normal"     # Standard physics operations
    HIGH = "high"         # Critical physics operations (convergence, errors)
    CRITICAL = "critical" # Physics failures, constraint violations


class PhysicsEventStatus(Enum):
    """Physics event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    CONVERGED = "converged"      # Physics-specific: solver converged
    FAILED = "failed"
    DIVERGED = "diverged"        # Physics-specific: solver diverged
    CONSTRAINT_VIOLATION = "constraint_violation"  # Physics constraint violated


class PhysicsEventType(Enum):
    """Physics-specific event type categories."""
    MESH_OPERATION = "mesh_operation"           # Mesh generation, refinement, quality
    SOLVER_ITERATION = "solver_iteration"       # Solver iteration steps
    CONVERGENCE_CHECK = "convergence_check"     # Convergence monitoring
    PHYSICS_VALIDATION = "physics_validation"   # Physics laws validation
    CONSTRAINT_CHECK = "constraint_check"       # Constraint enforcement
    BOUNDARY_CONDITION = "boundary_condition"   # Boundary condition application
    MATERIAL_PROPERTY = "material_property"     # Material property updates
    TIME_STEP = "time_step"                     # Time stepping (transient)
    POST_PROCESSING = "post_processing"         # Results processing
    ERROR_ANALYSIS = "error_analysis"           # Error estimation and analysis


class BasePhysicsEvent(BaseModel):
    """Base class for all physics modeling events."""
    
    # Core event properties
    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    event_type: PhysicsEventType = Field(..., description="Type of physics event")
    event_name: str = Field(..., description="Human-readable physics event name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event creation timestamp")
    
    # Physics-specific metadata
    priority: PhysicsEventPriority = Field(default=PhysicsEventPriority.NORMAL, description="Event priority level")
    status: PhysicsEventStatus = Field(default=PhysicsEventStatus.PENDING, description="Event processing status")
    
    # Physics context
    simulation_id: str = Field(..., description="Physics simulation identifier")
    twin_id: str = Field(..., description="Digital twin identifier")
    plugin_id: str = Field(..., description="Physics plugin identifier")
    
    # Event data and context
    data: Dict[str, Any] = Field(default_factory=dict, description="Physics-specific data payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional physics metadata")
    
    # Processing information
    source_service: str = Field(..., description="Service that generated the event")
    target_services: List[str] = Field(default_factory=list, description="Services that should process this event")
    
    # Error handling
    error_message: Optional[str] = Field(default=None, description="Error message if event failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts allowed")
    
    # Performance tracking
    processing_start_time: Optional[datetime] = Field(default=None, description="When processing started")
    processing_end_time: Optional[datetime] = Field(default=None, description="When processing completed")
    processing_duration: Optional[float] = Field(default=None, description="Processing duration in seconds")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    async def mark_processing_started(self) -> None:
        """Mark the event as processing started."""
        await asyncio.sleep(0)  # Pure async
        self.status = PhysicsEventStatus.PROCESSING
        self.processing_start_time = datetime.utcnow()
    
    async def mark_converged(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark the event as converged (physics-specific)."""
        await asyncio.sleep(0)  # Pure async
        self.status = PhysicsEventStatus.CONVERGED
        self.processing_end_time = datetime.utcnow()
        if self.processing_start_time:
            self.processing_duration = (self.processing_end_time - self.processing_start_time).total_seconds()
        if result:
            self.data["result"] = result
    
    async def mark_diverged(self, error_message: str) -> None:
        """Mark the event as diverged (physics-specific)."""
        await asyncio.sleep(0)  # Pure async
        self.status = PhysicsEventStatus.DIVERGED
        self.error_message = error_message
        self.processing_end_time = datetime.utcnow()
        if self.processing_start_time:
            self.processing_duration = (self.processing_end_time - self.processing_start_time).total_seconds()
    
    async def mark_constraint_violation(self, violation_details: str) -> None:
        """Mark the event as constraint violation (physics-specific)."""
        await asyncio.sleep(0)  # Pure async
        self.status = PhysicsEventStatus.CONSTRAINT_VIOLATION
        self.error_message = f"Constraint violation: {violation_details}"
        self.processing_end_time = datetime.utcnow()
        if self.processing_start_time:
            self.processing_duration = (self.processing_end_time - self.processing_start_time).total_seconds()
    
    async def mark_failed(self, error_message: str) -> None:
        """Mark the event as failed."""
        await asyncio.sleep(0)  # Pure async
        self.status = PhysicsEventStatus.FAILED
        self.error_message = error_message
        self.processing_end_time = datetime.utcnow()
        if self.processing_start_time:
            self.processing_duration = (self.processing_end_time - self.processing_start_time).total_seconds()
    
    async def can_retry(self) -> bool:
        """Check if the event can be retried."""
        await asyncio.sleep(0)  # Pure async
        return self.retry_count < self.max_retries and self.status in [
            PhysicsEventStatus.FAILED, 
            PhysicsEventStatus.DIVERGED, 
            PhysicsEventStatus.CONSTRAINT_VIOLATION
        ]
    
    async def increment_retry(self) -> None:
        """Increment the retry count."""
        await asyncio.sleep(0)  # Pure async
        self.retry_count += 1
        self.status = PhysicsEventStatus.PENDING
        self.error_message = None


class MeshOperationEvent(BasePhysicsEvent):
    """Event for mesh operations in physics modeling."""
    
    mesh_id: str = Field(..., description="Mesh identifier")
    operation_type: str = Field(..., description="Type of mesh operation")
    
    # Mesh-specific properties
    element_count: int = Field(default=0, description="Number of mesh elements")
    node_count: int = Field(default=0, description="Number of mesh nodes")
    mesh_quality: float = Field(default=0.0, description="Mesh quality metric (0-1)")
    
    # Operation details
    operation_parameters: Dict[str, Any] = Field(default_factory=dict, description="Mesh operation parameters")
    quality_threshold: float = Field(default=0.3, description="Minimum acceptable mesh quality")
    
    class Config:
        use_enum_values = True
    
    async def update_mesh_metrics(self, element_count: int, node_count: int, quality: float) -> None:
        """Update mesh metrics."""
        await asyncio.sleep(0)  # Pure async
        self.element_count = element_count
        self.node_count = node_count
        self.mesh_quality = quality
        
        # Check if quality meets threshold
        if quality < self.quality_threshold:
            await self.mark_constraint_violation(f"Mesh quality {quality:.3f} below threshold {self.quality_threshold}")


class SolverIterationEvent(BasePhysicsEvent):
    """Event for solver iteration steps in physics modeling."""
    
    iteration_number: int = Field(..., description="Current iteration number")
    max_iterations: int = Field(..., description="Maximum allowed iterations")
    
    # Solver-specific properties
    residual_norm: float = Field(default=0.0, description="Current residual norm")
    convergence_criteria: float = Field(default=1e-6, description="Convergence tolerance")
    solver_type: str = Field(..., description="Type of solver (FEM, FDM, FVM, etc.)")
    
    # Iteration details
    iteration_data: Dict[str, Any] = Field(default_factory=dict, description="Iteration-specific data")
    
    class Config:
        use_enum_values = True
    
    async def update_iteration_progress(self, iteration: int, residual: float) -> None:
        """Update iteration progress."""
        await asyncio.sleep(0)  # Pure async
        self.iteration_number = iteration
        self.residual_norm = residual
        
        # Check convergence
        if residual <= self.convergence_criteria:
            await self.mark_converged({
                "final_iteration": iteration,
                "final_residual": residual,
                "convergence_criteria": self.convergence_criteria
            })
        elif iteration >= self.max_iterations:
            await self.mark_diverged(f"Maximum iterations {self.max_iterations} reached with residual {residual:.2e}")


class ConvergenceCheckEvent(BasePhysicsEvent):
    """Event for convergence monitoring in physics modeling."""
    
    check_type: str = Field(..., description="Type of convergence check")
    check_criteria: Dict[str, Any] = Field(default_factory=dict, description="Convergence criteria")
    
    # Convergence metrics
    current_value: float = Field(default=0.0, description="Current convergence metric value")
    previous_value: float = Field(default=0.0, description="Previous convergence metric value")
    convergence_rate: float = Field(default=0.0, description="Rate of convergence")
    
    # Check results
    is_converged: bool = Field(default=False, description="Whether convergence is achieved")
    convergence_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed convergence information")
    
    class Config:
        use_enum_values = True
    
    async def perform_convergence_check(self, current: float, previous: float) -> None:
        """Perform convergence check."""
        await asyncio.sleep(0)  # Pure async
        self.current_value = current
        self.previous_value = previous
        
        # Calculate convergence rate
        if previous != 0:
            self.convergence_rate = abs((current - previous) / previous)
        
        # Check convergence based on criteria
        tolerance = self.check_criteria.get("tolerance", 1e-6)
        self.is_converged = abs(current - previous) <= tolerance
        
        if self.is_converged:
            await self.mark_converged({
                "convergence_rate": self.convergence_rate,
                "final_value": current,
                "tolerance": tolerance
            })


class PhysicsValidationEvent(BasePhysicsEvent):
    """Event for physics laws validation in physics modeling."""
    
    validation_type: str = Field(..., description="Type of physics validation")
    physics_laws: List[str] = Field(default_factory=list, description="Physics laws being validated")
    
    # Validation parameters
    validation_criteria: Dict[str, Any] = Field(default_factory=dict, description="Validation criteria")
    reference_data: Dict[str, Any] = Field(default_factory=dict, description="Reference data for validation")
    
    # Validation results
    validation_score: float = Field(default=0.0, description="Validation score (0-1)")
    violations: List[str] = Field(default_factory=list, description="List of physics law violations")
    is_valid: bool = Field(default=False, description="Whether physics validation passed")
    
    class Config:
        use_enum_values = True
    
    async def perform_physics_validation(self, score: float, violations: List[str]) -> None:
        """Perform physics validation."""
        await asyncio.sleep(0)  # Pure async
        self.validation_score = score
        self.violations = violations
        self.is_valid = score >= self.validation_criteria.get("min_score", 0.8)
        
        if self.is_valid:
            await self.mark_converged({
                "validation_score": score,
                "violations_count": len(violations),
                "status": "physics_valid"
            })
        else:
            await self.mark_constraint_violation(f"Physics validation failed with score {score:.3f}")


class ConstraintCheckEvent(BasePhysicsEvent):
    """Event for constraint checking in physics modeling."""
    
    constraint_type: str = Field(..., description="Type of constraint being checked")
    constraint_parameters: Dict[str, Any] = Field(default_factory=dict, description="Constraint parameters")
    
    # Constraint checking
    constraint_value: float = Field(default=0.0, description="Current constraint value")
    constraint_limit: float = Field(default=0.0, description="Constraint limit")
    constraint_satisfied: bool = Field(default=False, description="Whether constraint is satisfied")
    
    # Check results
    check_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed constraint check information")
    
    class Config:
        use_enum_values = True
    
    async def check_constraint(self, value: float, limit: float) -> None:
        """Check constraint satisfaction."""
        await asyncio.sleep(0)  # Pure async
        self.constraint_value = value
        self.constraint_limit = limit
        
        # Check if constraint is satisfied
        tolerance = self.constraint_parameters.get("tolerance", 0.0)
        self.constraint_satisfied = abs(value - limit) <= tolerance
        
        if self.constraint_satisfied:
            await self.mark_converged({
                "constraint_value": value,
                "constraint_limit": limit,
                "tolerance": tolerance,
                "status": "constraint_satisfied"
            })
        else:
            await self.mark_constraint_violation(
                f"Constraint violation: {value:.3f} exceeds limit {limit:.3f}"
            )


class BoundaryConditionEvent(BasePhysicsEvent):
    """Event for boundary condition application in physics modeling."""
    
    boundary_id: str = Field(..., description="Boundary identifier")
    boundary_type: str = Field(..., description="Type of boundary condition")
    
    # Boundary condition details
    boundary_parameters: Dict[str, Any] = Field(default_factory=dict, description="Boundary condition parameters")
    boundary_nodes: List[int] = Field(default_factory=list, description="Nodes on the boundary")
    
    # Application status
    application_successful: bool = Field(default=False, description="Whether boundary condition was applied successfully")
    application_details: Dict[str, Any] = Field(default_factory=dict, description="Application details")
    
    class Config:
        use_enum_values = True
    
    async def apply_boundary_condition(self, success: bool, details: Dict[str, Any]) -> None:
        """Apply boundary condition."""
        await asyncio.sleep(0)  # Pure async
        self.application_successful = success
        self.application_details = details
        
        if success:
            await self.mark_converged({
                "boundary_type": self.boundary_type,
                "nodes_count": len(self.boundary_nodes),
                "status": "boundary_applied"
            })
        else:
            await self.mark_failed(f"Failed to apply boundary condition: {details.get('error', 'Unknown error')}")


class MaterialPropertyEvent(BasePhysicsEvent):
    """Event for material property updates in physics modeling."""
    
    material_id: str = Field(..., description="Material identifier")
    property_name: str = Field(..., description="Name of material property")
    
    # Material property details
    old_value: float = Field(default=0.0, description="Previous property value")
    new_value: float = Field(default=0.0, description="New property value")
    property_unit: str = Field(default="", description="Property unit")
    
    # Update validation
    update_valid: bool = Field(default=False, description="Whether property update is valid")
    validation_rules: Dict[str, Any] = Field(default_factory=dict, description="Validation rules")
    
    class Config:
        use_enum_values = True
    
    async def update_material_property(self, old_val: float, new_val: float) -> None:
        """Update material property."""
        await asyncio.sleep(0)  # Pure async
        self.old_value = old_val
        self.new_value = new_val
        
        # Validate property update
        min_value = self.validation_rules.get("min_value", float('-inf'))
        max_value = self.validation_rules.get("max_value", float('inf'))
        
        self.update_valid = min_value <= new_val <= max_value
        
        if self.update_valid:
            await self.mark_converged({
                "property_name": self.property_name,
                "old_value": old_val,
                "new_value": new_val,
                "unit": self.property_unit,
                "status": "property_updated"
            })
        else:
            await self.mark_constraint_violation(
                f"Material property {new_val} outside valid range [{min_value}, {max_value}]"
            )


class TimeStepEvent(BasePhysicsEvent):
    """Event for time stepping in transient physics modeling."""
    
    time_step: int = Field(..., description="Current time step number")
    total_time_steps: int = Field(..., description="Total number of time steps")
    
    # Time stepping details
    current_time: float = Field(default=0.0, description="Current simulation time")
    time_step_size: float = Field(default=0.0, description="Size of current time step")
    simulation_duration: float = Field(default=0.0, description="Total simulation duration")
    
    # Time step status
    step_successful: bool = Field(default=False, description="Whether time step was successful")
    step_details: Dict[str, Any] = Field(default_factory=dict, description="Time step details")
    
    class Config:
        use_enum_values = True
    
    async def advance_time_step(self, success: bool, details: Dict[str, Any]) -> None:
        """Advance to next time step."""
        await asyncio.sleep(0)  # Pure async
        self.step_successful = success
        self.step_details = details
        
        if success:
            # Calculate progress
            progress = (self.time_step / self.total_time_steps) * 100
            await self.mark_converged({
                "time_step": self.time_step,
                "current_time": self.current_time,
                "progress": progress,
                "status": "time_step_completed"
            })
        else:
            await self.mark_failed(f"Time step {self.time_step} failed: {details.get('error', 'Unknown error')}")


class PostProcessingEvent(BasePhysicsEvent):
    """Event for post-processing operations in physics modeling."""
    
    processing_type: str = Field(..., description="Type of post-processing")
    processing_parameters: Dict[str, Any] = Field(default_factory=dict, description="Processing parameters")
    
    # Processing details
    input_data_size: int = Field(default=0, description="Size of input data")
    output_data_size: int = Field(default=0, description="Size of output data")
    processing_method: str = Field(default="", description="Processing method used")
    
    # Processing results
    processing_successful: bool = Field(default=False, description="Whether processing was successful")
    processing_results: Dict[str, Any] = Field(default_factory=dict, description="Processing results")
    
    class Config:
        use_enum_values = True
    
    async def perform_post_processing(self, success: bool, results: Dict[str, Any]) -> None:
        """Perform post-processing."""
        await asyncio.sleep(0)  # Pure async
        self.processing_successful = success
        self.processing_results = results
        
        if success:
            await self.mark_converged({
                "processing_type": self.processing_type,
                "input_size": self.input_data_size,
                "output_size": self.output_data_size,
                "method": self.processing_method,
                "status": "post_processing_completed"
            })
        else:
            await self.mark_failed(f"Post-processing failed: {results.get('error', 'Unknown error')}")


class ErrorAnalysisEvent(BasePhysicsEvent):
    """Event for error analysis in physics modeling."""
    
    analysis_type: str = Field(..., description="Type of error analysis")
    error_metrics: Dict[str, Any] = Field(default_factory=dict, description="Error metrics")
    
    # Error analysis details
    error_norm: float = Field(default=0.0, description="Error norm")
    error_threshold: float = Field(default=0.0, description="Acceptable error threshold")
    error_distribution: Dict[str, Any] = Field(default_factory=dict, description="Error distribution")
    
    # Analysis results
    analysis_successful: bool = Field(default=False, description="Whether analysis was successful")
    error_acceptable: bool = Field(default=False, description="Whether error is acceptable")
    analysis_results: Dict[str, Any] = Field(default_factory=dict, description="Analysis results")
    
    class Config:
        use_enum_values = True
    
    async def perform_error_analysis(self, success: bool, results: Dict[str, Any]) -> None:
        """Perform error analysis."""
        await asyncio.sleep(0)  # Pure async
        self.analysis_successful = success
        self.analysis_results = results
        
        if success:
            # Check if error is acceptable
            self.error_acceptable = self.error_norm <= self.error_threshold
            
            if self.error_acceptable:
                await self.mark_converged({
                    "error_norm": self.error_norm,
                    "error_threshold": self.error_threshold,
                    "status": "error_acceptable"
                })
            else:
                await self.mark_constraint_violation(
                    f"Error norm {self.error_norm:.2e} exceeds threshold {self.error_threshold:.2e}"
                )
        else:
            await self.mark_failed(f"Error analysis failed: {results.get('error', 'Unknown error')}")
