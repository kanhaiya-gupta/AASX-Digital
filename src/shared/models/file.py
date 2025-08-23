"""
File Model
==========

Data model for files in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from .base_model import BaseModel
from pydantic import Field
import uuid

class File(BaseModel):
    """File data model with comprehensive file management fields."""
    
    # Required fields (no defaults)
    filename: str = Field(..., description="File name")
    original_filename: str = Field(..., description="Original file name")
    project_id: str = Field(..., description="Project ID")
    filepath: str = Field(..., description="File path")
    
    # Optional fields with defaults
    file_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique file identifier")
    size: int = Field(default=0, description="File size in bytes")
    description: str = Field(default="", description="File description")
    status: str = Field(default="not_processed", description="Processing status")
    file_type: str = Field(default="", description="File type")
    file_type_description: str = Field(default="", description="File type description")
    source_type: str = Field(default="manual_upload", description="Source type")
    source_url: Optional[str] = Field(default=None, description="Source URL")
    org_id: Optional[str] = Field(default=None, description="Organization ID")
    use_case_id: Optional[str] = Field(default=None, description="Use case ID")
    job_type: Optional[str] = Field(default=None, description="Job type")
    tags: Optional[str] = Field(default=None, description="File tags (JSON)")
    metadata: Optional[str] = Field(default=None, description="File metadata (JSON)")
    user_id: Optional[str] = Field(default=None, description="User ID")
    upload_date: Optional[str] = Field(default=None, description="Upload date")
    

    
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
        required_fields = [
            'file_id', 'filename', 'original_filename', 'project_id', 'filepath', 
            'size', 'status', 'file_type', 'file_type_description', 'source_type',
            'created_at'
        ]
        for field in required_fields:
            if field not in data and hasattr(self, field):
                data[field] = getattr(self, field)
        return data 