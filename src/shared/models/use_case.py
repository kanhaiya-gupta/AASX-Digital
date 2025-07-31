"""
Use Case Model
==============

Data model for use cases in the AAS Data Modeling framework.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from .base_model import BaseModel
import json
import uuid

@dataclass
class UseCase(BaseModel):
    """Use case data model."""
    
    use_case_id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    name: str
    description: str = ""
    category: str = "general"
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the model."""
        super().__post_init__()
    
    def validate(self) -> bool:
        """Validate use case data."""
        if not self.name or not self.name.strip():
            raise ValueError("Use case name is required")
        
        if len(self.name) > 255:
            raise ValueError("Use case name must be less than 255 characters")
        
        if len(self.description) > 1000:
            raise ValueError("Use case description must be less than 1000 characters")
        
        valid_categories = ["thermal", "structural", "fluid_dynamics", "multi_physics", "industrial", "general"]
        if self.category not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        # Map use_case_id to the database column name
        if self.use_case_id:
            data['use_case_id'] = self.use_case_id
        data['metadata'] = json.dumps(self.metadata) if self.metadata else "{}"
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UseCase':
        """Create from dictionary from database."""
        # Parse metadata JSON
        if 'metadata' in data and isinstance(data['metadata'], str):
            try:
                data['metadata'] = json.loads(data['metadata'])
            except json.JSONDecodeError:
                data['metadata'] = {}
        
        return super().from_dict(data) 