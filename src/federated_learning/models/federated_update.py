"""
Federated Update Model
=====================

Data model for federated learning updates.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

class FederatedUpdate(BaseModel):
    """Model for federated learning updates"""
    
    # Basic identification
    twin_id: str = Field(..., description="ID of the twin that generated this update")
    session_id: str = Field(..., description="Federation session ID")
    round_number: int = Field(..., description="Federation round number")
    
    # Model parameters
    model_parameters: Dict[str, Any] = Field(default_factory=dict, description="Updated model parameters")
    model_type: str = Field(default="federated_model", description="Type of model")
    model_version: str = Field(default="1.0.0", description="Model version")
    
    # Training metrics
    training_metrics: Dict[str, Any] = Field(default_factory=dict, description="Training performance metrics")
    data_size: int = Field(default=0, description="Size of training data used")
    
    # Privacy and security
    privacy_applied: bool = Field(default=False, description="Whether differential privacy was applied")
    noise_scale: Optional[float] = Field(default=None, description="Noise scale for differential privacy")
    encryption: Dict[str, Any] = Field(default_factory=dict, description="Encryption metadata")
    
    # Validation and quality
    validation_passed: bool = Field(default=False, description="Whether update passed validation")
    quality_score: Optional[float] = Field(default=None, description="Quality assessment score")
    
    # Timestamps
    training_timestamp: datetime = Field(default_factory=datetime.now, description="When training was completed")
    created_at: datetime = Field(default_factory=datetime.now, description="When update was created")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()
    
    def validate_update(self) -> bool:
        """Validate the update"""
        # Check required fields
        if not self.twin_id or not self.session_id:
            return False
        
        # Check model parameters
        if not self.model_parameters:
            return False
        
        # Check training metrics
        if not self.training_metrics:
            return False
        
        # Check data size
        if self.data_size <= 0:
            return False
        
        return True
    
    def get_weight(self) -> float:
        """Calculate weight for aggregation"""
        # Base weight from data size
        size_weight = min(self.data_size / 1000.0, 1.0)
        
        # Performance weight from accuracy
        accuracy = self.training_metrics.get('accuracy', 0.5)
        performance_weight = max(accuracy, 0.1)
        
        # Quality weight
        quality_weight = self.quality_score or 1.0
        
        # Combine weights
        combined_weight = 0.5 * size_weight + 0.3 * performance_weight + 0.2 * quality_weight
        
        return combined_weight
    
    def apply_privacy(self, epsilon: float = 1.0) -> 'FederatedUpdate':
        """Apply differential privacy to the update"""
        import random
        
        # Create a copy
        private_update = self.copy()
        
        # Add noise to model parameters
        for key, value in private_update.model_parameters.items():
            if isinstance(value, (int, float)):
                noise = random.gauss(0, epsilon)
                private_update.model_parameters[key] = value + noise
        
        # Update privacy metadata
        private_update.privacy_applied = True
        private_update.noise_scale = epsilon
        
        return private_update 