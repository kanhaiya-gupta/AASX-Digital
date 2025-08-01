"""
Digital Twin Model
=================

Data model for digital twins in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from .base_model import BaseModel
import json
import uuid

@dataclass
class DigitalTwin(BaseModel):
    """Digital twin data model."""
    
    file_id: str  # Required field - no default
    twin_id: str = field(init=False)  # Will be set to file_id during creation
    twin_name: str = "DT - Unknown Use Case - Unknown Project - Unknown File"
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Health monitoring fields
    health_status: str = "unknown"
    last_health_check: Optional[str] = None
    health_score: int = 0
    error_count: int = 0
    last_error_message: Optional[str] = None
    maintenance_required: bool = False
    next_maintenance_date: Optional[str] = None
    
    # Physics modeling integration fields
    extracted_data_path: Optional[str] = None
    physics_context: Dict[str, Any] = field(default_factory=dict)
    simulation_history: list = field(default_factory=list)
    last_simulation_run: Optional[str] = None
    simulation_status: str = "pending"
    model_version: Optional[str] = None
    
    # Federated Learning Standard Fields
    federated_node_id: Optional[str] = None
    federated_participation_status: str = "inactive"
    federated_model_version: Optional[str] = None
    federated_last_sync: Optional[str] = None
    federated_contribution_score: int = 0
    federated_round_number: int = 0
    federated_health_status: str = "unknown"
    
    # Privacy & Security Standard Fields
    data_privacy_level: str = "private"
    data_sharing_permissions: Dict[str, Any] = field(default_factory=dict)
    differential_privacy_epsilon: float = 1.0
    secure_aggregation_enabled: bool = True
    
    def __post_init__(self):
        """Initialize the model."""
        super().__post_init__()
        # Set twin_id to file_id for 1:1 relationship
        if hasattr(self, 'file_id') and self.file_id:
            self.twin_id = self.file_id
    
    def validate(self) -> bool:
        """Validate digital twin data."""
        if not self.twin_name or not self.twin_name.strip():
            raise ValueError("Twin name is required")
        
        if not self.file_id:
            raise ValueError("File ID is required")
        
        if len(self.twin_name) > 255:
            raise ValueError("Twin name must be less than 255 characters")
        
        # Validate status
        valid_statuses = ["created", "processing", "active", "failed", "archived"]
        if self.status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        
        # Validate health status
        valid_health_statuses = ["unknown", "healthy", "warning", "critical", "offline"]
        if self.health_status not in valid_health_statuses:
            raise ValueError(f"Health status must be one of: {valid_health_statuses}")
        
        # Validate health score
        if not 0 <= self.health_score <= 100:
            raise ValueError("Health score must be between 0 and 100")
        
        # Validate simulation status
        valid_simulation_statuses = ["pending", "running", "completed", "failed"]
        if self.simulation_status not in valid_simulation_statuses:
            raise ValueError(f"Simulation status must be one of: {valid_simulation_statuses}")
        
        # Validate federated participation status
        valid_federated_statuses = ["active", "inactive", "excluded"]
        if self.federated_participation_status not in valid_federated_statuses:
            raise ValueError(f"Federated participation status must be one of: {valid_federated_statuses}")
        
        # Validate federated health status
        valid_federated_health_statuses = ["unknown", "healthy", "warning", "critical", "offline"]
        if self.federated_health_status not in valid_federated_health_statuses:
            raise ValueError(f"Federated health status must be one of: {valid_federated_health_statuses}")
        
        # Validate data privacy level
        valid_privacy_levels = ["public", "private", "restricted"]
        if self.data_privacy_level not in valid_privacy_levels:
            raise ValueError(f"Data privacy level must be one of: {valid_privacy_levels}")
        
        # Validate differential privacy epsilon
        if self.differential_privacy_epsilon < 0:
            raise ValueError("Differential privacy epsilon must be non-negative")
        
        # Validate federated contribution score
        if not 0 <= self.federated_contribution_score <= 100:
            raise ValueError("Federated contribution score must be between 0 and 100")
        
        return True
    
    def calculate_health_score(self) -> int:
        """Calculate health score based on current state."""
        health_score = 100
        
        # ETL Status (-50 if not active)
        if self.status != "active":
            health_score -= 50
        
        # Data Integrity (-30 if missing data)
        if not self.extracted_data_path:
            health_score -= 30
        
        # Physics Context (-20 if invalid)
        if not self.physics_context:
            health_score -= 20
        
        # Recent Errors (-10 per error, max -30)
        health_score -= min(self.error_count * 10, 30)
        
        # Maintenance Required (-10 if overdue)
        if self.maintenance_required:
            health_score -= 10
        
        return max(0, health_score)
    
    def update_health_score(self) -> None:
        """Update health score based on current state."""
        self.health_score = self.calculate_health_score()
        
        # Update health status based on score
        if self.health_score >= 80:
            self.health_status = "healthy"
        elif self.health_score >= 50:
            self.health_status = "warning"
        else:
            self.health_status = "critical"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        data['metadata'] = json.dumps(self.metadata) if self.metadata else "{}"
        data['physics_context'] = json.dumps(self.physics_context) if self.physics_context else "{}"
        data['simulation_history'] = json.dumps(self.simulation_history) if self.simulation_history else "[]"
        data['data_sharing_permissions'] = json.dumps(self.data_sharing_permissions) if self.data_sharing_permissions else "{}"
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DigitalTwin':
        """Create from dictionary from database."""
        # Parse metadata JSON
        if 'metadata' in data and isinstance(data['metadata'], str):
            try:
                data['metadata'] = json.loads(data['metadata'])
            except json.JSONDecodeError:
                data['metadata'] = {}
        
        # Parse physics_context JSON
        if 'physics_context' in data and isinstance(data['physics_context'], str):
            try:
                data['physics_context'] = json.loads(data['physics_context'])
            except json.JSONDecodeError:
                data['physics_context'] = {}
        
        # Parse simulation_history JSON
        if 'simulation_history' in data and isinstance(data['simulation_history'], str):
            try:
                data['simulation_history'] = json.loads(data['simulation_history'])
            except json.JSONDecodeError:
                data['simulation_history'] = []
        
        # Parse data_sharing_permissions JSON
        if 'data_sharing_permissions' in data and isinstance(data['data_sharing_permissions'], str):
            try:
                data['data_sharing_permissions'] = json.loads(data['data_sharing_permissions'])
            except json.JSONDecodeError:
                data['data_sharing_permissions'] = {}
        
        return super().from_dict(data) 