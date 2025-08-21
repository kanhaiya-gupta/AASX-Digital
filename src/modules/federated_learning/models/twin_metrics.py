"""
Twin Metrics Model
=================

Data model for twin performance metrics in federated learning.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class TwinMetrics(BaseModel):
    """Model for twin performance metrics in federated learning"""
    
    # Basic identification
    twin_id: str = Field(..., description="ID of the twin")
    session_id: str = Field(..., description="Federation session ID")
    round_number: int = Field(..., description="Federation round number")
    
    # Performance metrics
    accuracy: float = Field(..., description="Model accuracy on local data")
    loss: float = Field(..., description="Training loss")
    precision: Optional[float] = Field(default=None, description="Model precision")
    recall: Optional[float] = Field(default=None, description="Model recall")
    f1_score: Optional[float] = Field(default=None, description="F1 score")
    
    # Training metrics
    training_time: float = Field(default=0.0, description="Training time in seconds")
    epochs: int = Field(default=1, description="Number of training epochs")
    learning_rate: float = Field(default=0.01, description="Learning rate used")
    
    # Data metrics
    data_size: int = Field(default=0, description="Size of training data")
    data_quality_score: Optional[float] = Field(default=None, description="Data quality assessment")
    
    # Contribution metrics
    contribution_score: float = Field(default=0.0, description="Contribution score for federation")
    participation_rate: float = Field(default=1.0, description="Participation rate in federation rounds")
    
    # Privacy metrics
    privacy_budget_used: Optional[float] = Field(default=None, description="Privacy budget consumed")
    differential_privacy_epsilon: Optional[float] = Field(default=None, description="Differential privacy epsilon")
    
    # Health metrics
    health_score: int = Field(default=100, description="Twin health score")
    federated_health_status: str = Field(default="healthy", description="Federated health status")
    
    # Timestamps
    training_start_time: datetime = Field(default_factory=datetime.now, description="When training started")
    training_end_time: datetime = Field(default_factory=datetime.now, description="When training completed")
    created_at: datetime = Field(default_factory=datetime.now, description="When metrics were created")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()
    
    def calculate_overall_score(self) -> float:
        """Calculate overall performance score"""
        # Performance component (40%)
        performance_score = (
            self.accuracy * 0.4 +
            (1 - self.loss) * 0.3 +
            (self.f1_score or 0.0) * 0.3
        )
        
        # Data quality component (30%)
        data_score = self.data_quality_score or 0.5
        
        # Contribution component (20%)
        contribution_score = min(self.contribution_score / 100.0, 1.0)
        
        # Health component (10%)
        health_score = self.health_score / 100.0
        
        # Calculate weighted average
        overall_score = (
            performance_score * 0.4 +
            data_score * 0.3 +
            contribution_score * 0.2 +
            health_score * 0.1
        )
        
        return overall_score
    
    def is_healthy(self) -> bool:
        """Check if twin is healthy for federation"""
        return (
            self.health_score >= 70 and
            self.federated_health_status in ["healthy", "warning"] and
            self.data_size > 0 and
            self.accuracy > 0.0
        )
    
    def get_training_duration(self) -> float:
        """Get training duration in seconds"""
        return (self.training_end_time - self.training_start_time).total_seconds()
    
    def update_contribution_score(self, base_score: float = 50.0) -> float:
        """Update contribution score based on current metrics"""
        # Base contribution from data size
        data_contribution = min(self.data_size / 1000.0 * 20, 20)
        
        # Performance contribution
        performance_contribution = self.accuracy * 30
        
        # Quality contribution
        quality_contribution = (self.data_quality_score or 0.5) * 20
        
        # Health contribution
        health_contribution = self.health_score / 100.0 * 30
        
        # Calculate total contribution
        total_contribution = base_score + data_contribution + performance_contribution + quality_contribution + health_contribution
        
        # Update the contribution score
        self.contribution_score = min(total_contribution, 100.0)
        
        return self.contribution_score
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for display"""
        return {
            'twin_id': self.twin_id,
            'accuracy': round(self.accuracy, 3),
            'loss': round(self.loss, 3),
            'data_size': self.data_size,
            'contribution_score': round(self.contribution_score, 1),
            'health_score': self.health_score,
            'training_time': round(self.get_training_duration(), 2),
            'overall_score': round(self.calculate_overall_score(), 3),
            'is_healthy': self.is_healthy()
        } 