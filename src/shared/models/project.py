"""
Project Model
=============

Data model for projects in the AAS Data Modeling framework.
"""

from typing import Optional, List, Dict, Any
from .base_model import BaseModel
from pydantic import Field
import json
import uuid

class Project(BaseModel):
    """Project data model with comprehensive governance and project management fields."""
    
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique project identifier")
    name: str = Field(..., description="Project name")
    description: str = Field(default="", description="Project description")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    file_count: int = Field(default=0, description="Number of files in project")
    total_size: int = Field(default=0, description="Total size of project files")
    is_public: bool = Field(default=False, description="Public visibility")
    access_level: str = Field(default="private", description="Access level")
    user_id: Optional[str] = Field(default=None, description="Owner user ID")
    org_id: Optional[str] = Field(default=None, description="Organization ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Project metadata")
    
    # Project Governance Fields
    project_phase: str = Field(default="planning", description="Current project phase")
    priority_level: str = Field(default="medium", description="Project priority level")
    estimated_completion: Optional[str] = Field(default=None, description="Estimated completion date")
    actual_completion: Optional[str] = Field(default=None, description="Actual completion date")
    budget_allocation: float = Field(default=0.0, description="Budget allocation amount")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")
    dependencies: List[str] = Field(default_factory=list, description="Project dependencies")
    risk_mitigation: Dict[str, Any] = Field(default_factory=dict, description="Risk mitigation strategies")
    
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
        
        # Validate governance fields
        valid_phases = ["planning", "development", "testing", "deployment", "maintenance", "completed", "on_hold"]
        if self.project_phase not in valid_phases:
            raise ValueError(f"Project phase must be one of: {valid_phases}")
        
        valid_priorities = ["low", "medium", "high", "critical"]
        if self.priority_level not in valid_priorities:
            raise ValueError(f"Priority level must be one of: {valid_priorities}")
        
        if self.budget_allocation < 0:
            raise ValueError("Budget allocation cannot be negative")
        
        # No custom ID validation needed - using BaseModel.id
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        data['tags'] = json.dumps(self.tags) if self.tags else "[]"
        data['metadata'] = json.dumps(self.metadata) if self.metadata else "{}"
        
        # Handle JSON fields for governance data
        data['resource_requirements'] = json.dumps(self.resource_requirements) if self.resource_requirements else "{}"
        data['dependencies'] = json.dumps(self.dependencies) if self.dependencies else "[]"
        data['risk_mitigation'] = json.dumps(self.risk_mitigation) if self.risk_mitigation else "{}"
        
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
        
        # Parse governance JSON fields
        if 'resource_requirements' in data and isinstance(data['resource_requirements'], str):
            try:
                data['resource_requirements'] = json.loads(data['resource_requirements'])
            except json.JSONDecodeError:
                data['resource_requirements'] = {}
        
        if 'dependencies' in data and isinstance(data['dependencies'], str):
            try:
                data['dependencies'] = json.loads(data['dependencies'])
            except json.JSONDecodeError:
                data['dependencies'] = []
        
        if 'risk_mitigation' in data and isinstance(data['risk_mitigation'], str):
            try:
                data['risk_mitigation'] = json.loads(data['risk_mitigation'])
            except json.JSONDecodeError:
                data['risk_mitigation'] = {}
        
        return super().from_dict(data) 