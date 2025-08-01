"""
File Model
==========

Data model for files in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
from .base_model import BaseModel
import uuid

@dataclass
class File(BaseModel):
    """File data model."""
    
    # Required fields (no defaults)
    filename: str
    original_filename: str
    project_id: str
    filepath: str
    
    # Optional fields with defaults
    file_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    size: int = 0
    description: str = ""
    status: str = "not_processed"
    file_type: str = ""
    file_type_description: str = ""
    user_id: Optional[str] = None
    upload_date: Optional[str] = None
    federated_learning: str = "not_allowed"  # "allowed", "not_allowed", "conditional"
    
    def __post_init__(self):
        """Initialize the model."""
        super().__post_init__()
    
    def validate(self) -> bool:
        """Validate file data."""
        if not self.filename or not self.filename.strip():
            raise ValueError("Filename is required")
        
        if not self.original_filename or not self.original_filename.strip():
            raise ValueError("Original filename is required")
        
        if not self.project_id:
            raise ValueError("Project ID is required")
        
        if not self.filepath:
            raise ValueError("File path is required")
        
        if self.size < 0:
            raise ValueError("File size cannot be negative")
        
        valid_statuses = ["not_processed", "processing", "processed", "failed", "cancelled"]
        if self.status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        
        return True
    
    def get_file_path(self) -> Path:
        """Get the file path as a Path object."""
        return Path(self.filepath)
    
    def exists(self) -> bool:
        """Check if the file exists on disk."""
        return self.get_file_path().exists()
    
    def get_file_size(self) -> int:
        """Get the actual file size from disk."""
        try:
            return self.get_file_path().stat().st_size
        except (OSError, FileNotFoundError):
            return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        # Ensure upload_date is set
        if not data.get('upload_date'):
            data['upload_date'] = self.created_at.isoformat()
        # Map file_id to the correct field for database
        if hasattr(self, 'file_id') and self.file_id:
            data['file_id'] = self.file_id
        # Ensure all required fields are present
        required_fields = ['file_id', 'filename', 'original_filename', 'project_id', 'filepath', 'size', 'status', 'federated_learning']
        for field in required_fields:
            if field not in data and hasattr(self, field):
                data[field] = getattr(self, field)
        return data 