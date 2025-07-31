"""
Base Model
==========

Base class for all data models with common fields and validation.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class BaseModel:
    """Base class for all data models."""
    
    # Generic ID field - subclasses should override with specific ID field names
    id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    created_at: datetime = field(default_factory=datetime.now, init=False)
    updated_at: datetime = field(default_factory=datetime.now, init=False)
    
    def __post_init__(self):
        """Initialize base fields after dataclass initialization."""
        # Only set fields if not already set (e.g., by from_dict)
        if not hasattr(self, 'id') or not self.id:
            self.id = str(uuid.uuid4())
        if not hasattr(self, 'created_at'):
            self.created_at = datetime.now()
        if not hasattr(self, 'updated_at'):
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
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
        
        # Get all fields that are init=True
        import dataclasses
        init_fields = {f.name for f in dataclasses.fields(cls) if f.init}
        filtered_data = {k: v for k, v in data.items() if k in init_fields}
        
        # Create instance with init=True fields
        instance = cls(**filtered_data)
        
        # Set id explicitly if provided
        if 'id' in data and data['id']:
            instance.id = data['id']
        
        # Set other init=False fields
        for field_info in dataclasses.fields(cls):
            if not field_info.init and field_info.name in data and field_info.name != 'id':
                setattr(instance, field_info.name, data[field_info.name])
        
        return instance
    
    def update(self, **kwargs):
        """Update model fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def validate(self) -> bool:
        """Validate model data. Override in subclasses."""
        return True 