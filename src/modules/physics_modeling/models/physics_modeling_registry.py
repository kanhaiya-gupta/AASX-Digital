"""
Physics Modeling Registry Model

This model represents the main physics modeling registry table with integrated
enterprise features for compliance, security, and performance monitoring.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import Field, validator
from src.engine.models import BaseModel
import asyncio


class PhysicsModelingRegistry(BaseModel):
    """
    Physics Modeling Registry Model
    
    Represents traditional physics models with integrated enterprise features
    for compliance tracking, security monitoring, and performance analytics.
    """
    
    # Core Physics Modeling Fields
    model_id: str = Field(..., description="Unique identifier for the physics model")
    model_name: str = Field(..., description="Name of the physics model")
    model_type: str = Field(..., description="Type of physics model (structural, thermal, fluid, etc.)")
    physics_domain: str = Field(..., description="Physics domain (mechanics, thermodynamics, electromagnetics, etc.)")
    model_version: str = Field(..., description="Version of the physics model")
    description: Optional[str] = Field(None, description="Detailed description of the model")
    
    # Model Configuration
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters and configuration")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Physical constraints and boundary conditions")
    mesh_config: Optional[Dict[str, Any]] = Field(None, description="Mesh generation configuration")
    solver_config: Optional[Dict[str, Any]] = Field(None, description="Solver configuration and settings")
    
    # Model Status and Lifecycle
    status: str = Field(default="draft", description="Current status of the model")
    lifecycle_stage: str = Field(default="development", description="Current lifecycle stage")
    created_by: str = Field(..., description="User who created the model")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_by: Optional[str] = Field(None, description="User who last updated the model")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Validation and Quality
    validation_status: str = Field(default="pending", description="Validation status")
    validation_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Validation score (0-1)")
    quality_metrics: Dict[str, float] = Field(default_factory=dict, description="Quality metrics and scores")
    
    # Enterprise Compliance Features (Integrated)
    compliance_type: Optional[str] = Field(None, description="Type of compliance requirement")
    compliance_status: str = Field(default="pending", description="Compliance status")
    compliance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Compliance score (0-1)")
    last_audit_date: Optional[datetime] = Field(None, description="Last compliance audit date")
    next_audit_date: Optional[datetime] = Field(None, description="Next scheduled audit date")
    audit_details: Optional[Dict[str, Any]] = Field(None, description="Audit details and findings")
    
    # Enterprise Security Features (Integrated)
    security_event_type: Optional[str] = Field(None, description="Type of security event")
    threat_assessment: Optional[str] = Field(None, description="Threat assessment level")
    security_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Security score (0-1)")
    last_security_scan: Optional[datetime] = Field(None, description="Last security scan date")
    security_details: Optional[Dict[str, Any]] = Field(None, description="Security details and findings")
    
    # Enterprise Performance Features (Integrated)
    performance_trend: Optional[str] = Field(None, description="Performance trend analysis")
    optimization_suggestions: Optional[Dict[str, Any]] = Field(None, description="Optimization suggestions")
    last_optimization_date: Optional[datetime] = Field(None, description="Last optimization date")
    enterprise_metrics: Optional[Dict[str, Any]] = Field(None, description="Additional enterprise metrics")
    
    # Metadata and Tags
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "model_id": "structural_beam_001",
                "model_name": "Steel Beam Structural Analysis",
                "model_type": "structural",
                "physics_domain": "mechanics",
                "model_version": "1.0.0",
                "description": "Finite element analysis of steel beam under load",
                "parameters": {"length": 10.0, "width": 0.2, "height": 0.3},
                "status": "active",
                "created_by": "engineer@company.com",
                "compliance_status": "compliant",
                "security_score": 0.95
            }
        }
    
    @validator('compliance_score', 'security_score', 'validation_score')
    def validate_score_range(cls, v):
        """Validate score fields are within 0-1 range"""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate model status"""
        valid_statuses = ['draft', 'active', 'inactive', 'deprecated', 'archived']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v
    
    @validator('lifecycle_stage')
    def validate_lifecycle_stage(cls, v):
        """Validate lifecycle stage"""
        valid_stages = ['development', 'testing', 'validation', 'production', 'maintenance']
        if v not in valid_stages:
            raise ValueError(f'Lifecycle stage must be one of: {valid_stages}')
        return v
    
    async def validate_model_parameters(self) -> bool:
        """Async validation of model parameters"""
        await asyncio.sleep(0)  # Ensure async context
        
        # Basic validation logic
        if not self.parameters:
            return False
        
        # Check required parameters based on model type
        if self.model_type == "structural":
            required_params = ["length", "width", "height"]
            if not all(param in self.parameters for param in required_params):
                return False
        
        return True
    
    async def calculate_compliance_score(self) -> float:
        """Async calculation of compliance score"""
        await asyncio.sleep(0)  # Ensure async context
        
        # Placeholder for compliance scoring logic
        base_score = 0.8
        
        # Adjust based on validation status
        if self.validation_status == "passed":
            base_score += 0.1
        elif self.validation_status == "failed":
            base_score -= 0.2
        
        # Adjust based on security score
        if self.security_score:
            base_score = (base_score + self.security_score) / 2
        
        return min(1.0, max(0.0, base_score))
    
    async def update_security_metrics(self, event_type: str, threat_level: str) -> None:
        """Async update of security metrics"""
        await asyncio.sleep(0)  # Ensure async context
        
        self.security_event_type = event_type
        self.threat_assessment = threat_level
        self.last_security_scan = datetime.utcnow()
        
        # Update security score based on threat level
        threat_scores = {"low": 0.9, "medium": 0.7, "high": 0.5, "critical": 0.3}
        self.security_score = threat_scores.get(threat_level, 0.5)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "model_type": self.model_type,
            "physics_domain": self.physics_domain,
            "model_version": self.model_version,
            "status": self.status,
            "compliance_status": self.compliance_status,
            "security_score": self.security_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
