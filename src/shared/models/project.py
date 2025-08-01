"""
Project Model
=============

Data model for projects in the AAS Data Modeling framework.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from .base_model import BaseModel
import json
import uuid

@dataclass
class Project(BaseModel):
    """Project data model."""
    
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    name: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    file_count: int = 0
    total_size: int = 0
    is_public: bool = False
    access_level: str = "private"
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the model."""
        super().__post_init__()
    
    def validate(self) -> bool:
        """Validate project data."""
        if not self.name or not self.name.strip():
            raise ValueError("Project name is required")
        
        if len(self.name) > 255:
            raise ValueError("Project name must be less than 255 characters")
        
        if len(self.description) > 1000:
            raise ValueError("Project description must be less than 1000 characters")
        
        if self.file_count < 0:
            raise ValueError("File count cannot be negative")
        
        if self.total_size < 0:
            raise ValueError("Total size cannot be negative")
        
        valid_access_levels = ["private", "public", "shared"]
        if self.access_level not in valid_access_levels:
            raise ValueError(f"Access level must be one of: {valid_access_levels}")
        
        # No custom ID validation needed - using BaseModel.id
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        data['tags'] = json.dumps(self.tags) if self.tags else "[]"
        data['metadata'] = json.dumps(self.metadata) if self.metadata else "{}"
        # Map project_id to the correct field for database
        if hasattr(self, 'project_id') and self.project_id:
            data['project_id'] = self.project_id
        # Ensure all required fields are present
        required_fields = ['project_id', 'name', 'description', 'tags', 'file_count', 'total_size', 'is_public', 'access_level']
        for field in required_fields:
            if field not in data and hasattr(self, field):
                data[field] = getattr(self, field)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create from dictionary from database."""
        # Parse tags JSON
        if 'tags' in data and isinstance(data['tags'], str):
            try:
                data['tags'] = json.loads(data['tags'])
            except json.JSONDecodeError:
                data['tags'] = []
        
        # Parse metadata JSON
        if 'metadata' in data and isinstance(data['metadata'], str):
            try:
                data['metadata'] = json.loads(data['metadata'])
            except json.JSONDecodeError:
                data['metadata'] = {}
        
        return super().from_dict(data) 