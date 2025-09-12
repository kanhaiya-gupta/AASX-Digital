"""
Physics Modeling Event Types

This module defines the core event types for the physics modeling system,
including base events and specialized event types for different operations.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4


class EventPriority(Enum):
    """Event priority levels for processing order."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(Enum):
    """Event type categories."""
    SIMULATION = "simulation"
    ML_TRAINING = "ml_training"
    VALIDATION = "validation"
    COMPLIANCE = "compliance"
    SERVICE = "service"
    SYSTEM = "system"


class BasePhysicsEvent(BaseModel):
    """Base class for all physics modeling events."""
    
    # Core event properties
    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of event")
    event_name: str = Field(..., description="Human-readable event name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event creation timestamp")
    
    # Event metadata
    priority: EventPriority = Field(default=EventPriority.NORMAL, description="Event priority level")
    status: EventStatus = Field(default=EventStatus.PENDING, description="Event processing status")
    
    # Event data and context
    data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")
    
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
        self.status = EventStatus.PROCESSING
        self.processing_start_time = datetime.utcnow()
    
    async def mark_completed(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark the event as completed."""
        await asyncio.sleep(0)  # Pure async
        self.status = EventStatus.COMPLETED
        self.processing_end_time = datetime.utcnow()
        if self.processing_start_time:
            self.processing_duration = (self.processing_end_time - self.processing_start_time).total_seconds()
        if result:
            self.data["result"] = result
    
    async def mark_failed(self, error_message: str) -> None:
        """Mark the event as failed."""
        await asyncio.sleep(0)  # Pure async
        self.status = EventStatus.FAILED
        self.error_message = error_message
        self.processing_end_time = datetime.utcnow()
        if self.processing_start_time:
            self.processing_duration = (self.processing_end_time - self.processing_start_time).total_seconds()
    
    async def can_retry(self) -> bool:
        """Check if the event can be retried."""
        await asyncio.sleep(0)  # Pure async
        return self.retry_count < self.max_retries and self.status == EventStatus.FAILED
    
    async def increment_retry(self) -> None:
        """Increment the retry count."""
        await asyncio.sleep(0)  # Pure async
        self.retry_count += 1
        self.status = EventStatus.PENDING
        self.error_message = None


class PhysicsSimulationEvent(BasePhysicsEvent):
    """Event for physics simulation operations."""
    
    simulation_id: str = Field(..., description="Unique simulation identifier")
    simulation_type: str = Field(..., description="Type of physics simulation")
    twin_id: str = Field(..., description="Digital twin identifier for simulation")
    plugin_id: str = Field(..., description="Plugin identifier for simulation")
    
    # Simulation parameters
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Simulation parameters")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Physics constraints")
    
    # Simulation state
    current_step: int = Field(default=0, description="Current simulation step")
    total_steps: int = Field(default=1, description="Total simulation steps")
    progress_percentage: float = Field(default=0.0, description="Simulation progress (0-100)")
    
    class Config:
        use_enum_values = True
    
    async def update_progress(self, current_step: int, total_steps: int) -> None:
        """Update simulation progress."""
        await asyncio.sleep(0)  # Pure async
        self.current_step = current_step
        self.total_steps = total_steps
        self.progress_percentage = (current_step / total_steps) * 100 if total_steps > 0 else 0


class MLTrainingEvent(BasePhysicsEvent):
    """Event for machine learning training operations."""
    
    training_id: str = Field(..., description="Unique training identifier")
    model_type: str = Field(..., description="Type of ML model (PINN, etc.)")
    dataset_id: str = Field(..., description="Training dataset identifier")
    
    # Training parameters
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Training hyperparameters")
    training_config: Dict[str, Any] = Field(default_factory=dict, description="Training configuration")
    
    # Training state
    current_epoch: int = Field(default=0, description="Current training epoch")
    total_epochs: int = Field(default=1, description="Total training epochs")
    current_loss: float = Field(default=0.0, description="Current training loss")
    best_loss: float = Field(default=float('inf'), description="Best training loss achieved")
    
    class Config:
        use_enum_values = True
    
    async def update_training_progress(self, epoch: int, loss: float) -> None:
        """Update training progress."""
        await asyncio.sleep(0)  # Pure async
        self.current_epoch = epoch
        self.current_loss = loss
        if loss < self.best_loss:
            self.best_loss = loss
        self.progress_percentage = (epoch / self.total_epochs) * 100 if self.total_epochs > 0 else 0


class ValidationEvent(BasePhysicsEvent):
    """Event for model validation operations."""
    
    validation_id: str = Field(..., description="Unique validation identifier")
    model_id: str = Field(..., description="Model being validated")
    validation_type: str = Field(..., description="Type of validation")
    
    # Validation parameters
    validation_criteria: Dict[str, Any] = Field(default_factory=dict, description="Validation criteria")
    test_data: Dict[str, Any] = Field(default_factory=dict, description="Test data for validation")
    
    # Validation results
    validation_score: Optional[float] = Field(default=None, description="Validation score")
    validation_passed: Optional[bool] = Field(default=None, description="Whether validation passed")
    validation_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed validation results")
    
    class Config:
        use_enum_values = True
    
    async def set_validation_result(self, score: float, passed: bool, details: Dict[str, Any]) -> None:
        """Set validation results."""
        await asyncio.sleep(0)  # Pure async
        self.validation_score = score
        self.validation_passed = passed
        self.validation_details = details


class ComplianceEvent(BasePhysicsEvent):
    """Event for compliance monitoring operations."""
    
    compliance_id: str = Field(..., description="Unique compliance identifier")
    compliance_type: str = Field(..., description="Type of compliance check")
    regulatory_framework: str = Field(..., description="Regulatory framework being checked")
    
    # Compliance parameters
    compliance_rules: Dict[str, Any] = Field(default_factory=dict, description="Compliance rules to check")
    audit_requirements: Dict[str, Any] = Field(default_factory=dict, description="Audit requirements")
    
    # Compliance results
    compliance_score: Optional[float] = Field(default=None, description="Compliance score")
    compliance_status: Optional[str] = Field(default=None, description="Compliance status")
    violations: List[str] = Field(default_factory=list, description="List of compliance violations")
    
    class Config:
        use_enum_values = True
    
    async def set_compliance_result(self, score: float, status: str, violations: List[str]) -> None:
        """Set compliance results."""
        await asyncio.sleep(0)  # Pure async
        self.compliance_score = score
        self.compliance_status = status
        self.violations = violations


class ServiceEvent(BasePhysicsEvent):
    """Event for service-level operations."""
    
    service_id: str = Field(..., description="Service identifier")
    operation: str = Field(..., description="Operation being performed")
    
    # Service state
    service_status: str = Field(default="unknown", description="Current service status")
    health_score: Optional[float] = Field(default=None, description="Service health score")
    
    # Performance metrics
    response_time: Optional[float] = Field(default=None, description="Service response time")
    throughput: Optional[float] = Field(default=None, description="Service throughput")
    error_rate: Optional[float] = Field(default=None, description="Service error rate")
    
    class Config:
        use_enum_values = True
    
    async def update_service_metrics(self, health_score: float, response_time: float, 
                                   throughput: float, error_rate: float) -> None:
        """Update service performance metrics."""
        await asyncio.sleep(0)  # Pure async
        self.health_score = health_score
        self.response_time = response_time
        self.throughput = throughput
        self.error_rate = error_rate





