"""
Physics ML Registry Model

This model represents the machine learning models (PINNs, etc.) registry table with integrated
enterprise features for ML compliance, security, and performance monitoring.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field, validator
from src.engine.models import BaseModel
import asyncio


class PhysicsMLRegistry(BaseModel):
    """
    Physics ML Registry Model
    
    Represents machine learning models (PINNs, hybrid physics-ML) with integrated enterprise features
    for ML compliance tracking, security monitoring, and performance analytics.
    """
    
    # Core ML Model Fields
    ml_model_id: str = Field(..., description="Unique identifier for the ML model")
    model_name: str = Field(..., description="Name of the ML model")
    model_type: str = Field(..., description="Type of ML model (PINN, hybrid, neural_ode, etc.)")
    physics_domain: str = Field(..., description="Physics domain the ML model addresses")
    ml_framework: str = Field(..., description="ML framework used (PyTorch, TensorFlow, JAX, etc.)")
    model_version: str = Field(..., description="Version of the ML model")
    description: Optional[str] = Field(None, description="Detailed description of the ML model")
    
    # ML Model Architecture
    architecture: Dict[str, Any] = Field(..., description="Neural network architecture details")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Training hyperparameters")
    loss_functions: List[str] = Field(..., description="Loss functions used (physics + ML)")
    optimization_config: Optional[Dict[str, Any]] = Field(None, description="Optimization configuration")
    
    # Training and Validation
    training_status: str = Field(default="not_started", description="Training status")
    training_progress: Optional[float] = Field(None, ge=0.0, le=1.0, description="Training progress (0-1)")
    validation_metrics: Dict[str, float] = Field(default_factory=dict, description="Validation metrics")
    test_metrics: Optional[Dict[str, float]] = Field(None, description="Test set metrics")
    
    # Physics Integration
    physics_constraints: List[str] = Field(default_factory=list, description="Physics constraints enforced")
    conservation_laws: List[str] = Field(default_factory=list, description="Conservation laws implemented")
    boundary_conditions: Optional[Dict[str, Any]] = Field(None, description="Boundary conditions")
    initial_conditions: Optional[Dict[str, Any]] = Field(None, description="Initial conditions")
    
    # Model Status and Lifecycle
    status: str = Field(default="draft", description="Current status of the ML model")
    lifecycle_stage: str = Field(default="development", description="Current lifecycle stage")
    created_by: str = Field(..., description="User who created the ML model")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_by: Optional[str] = Field(None, description="User who last updated the ML model")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # ML-Specific Enterprise Features (Integrated)
    ml_compliance_type: Optional[str] = Field(None, description="Type of ML compliance requirement")
    ml_compliance_status: str = Field(default="pending", description="ML compliance status")
    ml_compliance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="ML compliance score (0-1)")
    ml_security_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="ML security score (0-1)")
    ml_performance_trend: Optional[str] = Field(None, description="ML performance trend analysis")
    ml_optimization_suggestions: Optional[Dict[str, Any]] = Field(None, description="ML optimization suggestions")
    last_ml_optimization_date: Optional[datetime] = Field(None, description="Last ML optimization date")
    enterprise_ml_metrics: Optional[Dict[str, Any]] = Field(None, description="Additional enterprise ML metrics")
    
    # Model Artifacts and Deployment
    model_path: Optional[str] = Field(None, description="Path to saved model artifacts")
    model_size: Optional[int] = Field(None, description="Model size in bytes")
    inference_latency: Optional[float] = Field(None, description="Inference latency in milliseconds")
    deployment_status: str = Field(default="not_deployed", description="Deployment status")
    
    # Metadata and Tags
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "ml_model_id": "pinn_heat_transfer_001",
                "model_name": "PINN Heat Transfer Solver",
                "model_type": "PINN",
                "physics_domain": "thermodynamics",
                "ml_framework": "PyTorch",
                "model_version": "1.0.0",
                "architecture": {"layers": [64, 128, 64], "activation": "tanh"},
                "loss_functions": ["mse", "physics_loss"],
                "training_status": "completed",
                "ml_compliance_status": "compliant",
                "ml_security_score": 0.92
            }
        }
    
    @validator('ml_compliance_score', 'ml_security_score', 'training_progress')
    def validate_score_range(cls, v):
        """Validate score fields are within 0-1 range"""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate ML model status"""
        valid_statuses = ['draft', 'training', 'active', 'inactive', 'deprecated', 'archived']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v
    
    @validator('training_status')
    def validate_training_status(cls, v):
        """Validate training status"""
        valid_training_statuses = ['not_started', 'in_progress', 'completed', 'failed', 'paused']
        if v not in valid_training_statuses:
            raise ValueError(f'Training status must be one of: {valid_training_statuses}')
        return v
    
    async def validate_ml_architecture(self) -> bool:
        """Async validation of ML model architecture"""
        await asyncio.sleep(0)  # Ensure async context
        
        # Basic validation logic
        if not self.architecture:
            return False
        
        # Check required architecture components
        required_components = ["layers", "activation"]
        if not all(component in self.architecture for component in required_components):
            return False
        
        # Validate layers configuration
        layers = self.architecture.get("layers", [])
        if not isinstance(layers, list) or len(layers) < 2:
            return False
        
        return True
    
    async def calculate_ml_compliance_score(self) -> float:
        """Async calculation of ML compliance score"""
        await asyncio.sleep(0)  # Ensure async context
        
        # Placeholder for ML compliance scoring logic
        base_score = 0.7
        
        # Adjust based on training status
        if self.training_status == "completed":
            base_score += 0.2
        elif self.training_status == "failed":
            base_score -= 0.3
        
        # Adjust based on validation metrics
        if self.validation_metrics and "accuracy" in self.validation_metrics:
            accuracy = self.validation_metrics["accuracy"]
            if accuracy > 0.9:
                base_score += 0.1
            elif accuracy < 0.7:
                base_score -= 0.1
        
        # Adjust based on ML security score
        if self.ml_security_score:
            base_score = (base_score + self.ml_security_score) / 2
        
        return min(1.0, max(0.0, base_score))
    
    async def update_ml_security_metrics(self, security_event: str, risk_level: str) -> None:
        """Async update of ML security metrics"""
        await asyncio.sleep(0)  # Ensure async context
        
        # Update security score based on risk level
        risk_scores = {"low": 0.9, "medium": 0.7, "high": 0.5, "critical": 0.3}
        self.ml_security_score = risk_scores.get(risk_level, 0.5)
        
        # Update metadata with security event
        if "security_events" not in self.metadata:
            self.metadata["security_events"] = []
        
        self.metadata["security_events"].append({
            "event": security_event,
            "risk_level": risk_level,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def evaluate_physics_constraints(self) -> Dict[str, bool]:
        """Async evaluation of physics constraints compliance"""
        await asyncio.sleep(0)  # Ensure async context
        
        constraint_results = {}
        
        # Evaluate each physics constraint
        for constraint in self.physics_constraints:
            # Placeholder for constraint evaluation logic
            constraint_results[constraint] = True
        
        return constraint_results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ML model to dictionary"""
        return {
            "ml_model_id": self.ml_model_id,
            "model_name": self.model_name,
            "model_type": self.model_type,
            "physics_domain": self.physics_domain,
            "ml_framework": self.ml_framework,
            "model_version": self.model_version,
            "training_status": self.training_status,
            "ml_compliance_status": self.ml_compliance_status,
            "ml_security_score": self.ml_security_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
