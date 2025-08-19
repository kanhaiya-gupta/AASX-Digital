"""
Base Model
==========

Base class for all data models with common fields and validation.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel):
    """Base class for all data models."""
    
    # Generic ID field - subclasses should override with specific ID field names
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(), description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary."""
        # Convert sqlite3.Row to dict if needed
        if hasattr(data, 'keys'):  # sqlite3.Row object
            data = dict(data)
        
        # Convert ISO strings back to datetime
        for key in ['created_at', 'updated_at']:
            if key in data and isinstance(data[key], str):
                data[key] = datetime.fromisoformat(data[key])
        
        return cls(**data)
    
    def update(self, **kwargs):
        """Update model fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def validate(self) -> bool:
        """Validate model data. Override in subclasses."""
        return True 