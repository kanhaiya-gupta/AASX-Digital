"""
Data Version Model
=================

Data model for tracking data versioning and changes in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any
from .base_model import BaseModel
from pydantic import Field
import json
import uuid
from datetime import datetime

class DataVersion(BaseModel):
    """Data version model for tracking data versioning and changes."""
    
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique version identifier")
    entity_type: str = Field(..., description="Type of entity being versioned")
    entity_id: str = Field(..., description="ID of entity being versioned")
    version_number: str = Field(..., description="Semantic version number (e.g., 1.0.0)")
    version_type: str = Field(..., description="Type of version change")
    
    # Version Content
    previous_version_id: Optional[str] = Field(default=None, description="Link to previous version")
    change_summary: str = Field(default="", description="Summary of changes in this version")
    change_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed change information")
    data_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Complete data state at this version")
    
    # Change Information
    change_type: str = Field(..., description="Type of change made")
    change_reason: Optional[str] = Field(default=None, description="Why this change was made")
    change_request_id: Optional[str] = Field(default=None, description="Link to change request if applicable")
    
    # Version Metadata
    created_by: str = Field(..., description="User who created this version")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Version creation timestamp")
    is_current: bool = Field(default=False, description="Is this the current active version")
    is_deprecated: bool = Field(default=False, description="Is this version deprecated")
    deprecation_date: Optional[str] = Field(default=None, description="Deprecation date")
    deprecation_reason: Optional[str] = Field(default=None, description="Reason for deprecation")
    
    # Performance & Access
    last_accessed: Optional[str] = Field(default=None, description="Last access timestamp")
    access_count: int = Field(default=0, description="Number of times accessed")
    storage_size: int = Field(default=0, description="Size of version data in bytes")
    
    # Compliance & Audit
    compliance_status: str = Field(default="unknown", description="Compliance status")
    audit_notes: Optional[str] = Field(default=None, description="Audit notes")
    retention_expiry: Optional[str] = Field(default=None, description="Retention expiry date")
    
    def validate(self) -> bool:
        """Validate data version."""
        valid_entity_types = ["file", "project", "use_case", "user", "organization", "data_lineage", "quality_metrics"]
        if self.entity_type not in valid_entity_types:
            raise ValueError(f"Entity type must be one of: {valid_entity_types}")
        
        valid_version_types = ["major", "minor", "patch", "hotfix"]
        if self.version_type not in valid_version_types:
            raise ValueError(f"Version type must be one of: {valid_version_types}")
        
        valid_change_types = ["create", "update", "delete", "restore"]
        if self.change_type not in valid_change_types:
            raise ValueError(f"Change type must be one of: {valid_change_types}")
        
        valid_compliance_statuses = ["compliant", "non_compliant", "pending_review", "unknown"]
        if self.compliance_status not in valid_compliance_statuses:
            raise ValueError(f"Compliance status must be one of: {valid_compliance_statuses}")
        
        # Validate semantic version format (basic check)
        if not self.version_number or not self.version_number.strip():
            raise ValueError("Version number is required")
        
        # Basic semantic version validation (x.y.z format)
        version_parts = self.version_number.split('.')
        if len(version_parts) < 2 or len(version_parts) > 3:
            raise ValueError("Version number must be in format x.y or x.y.z")
        
        try:
            for part in version_parts:
                int(part)
        except ValueError:
            raise ValueError("Version number parts must be integers")
        
        if self.access_count < 0:
            raise ValueError("Access count cannot be negative")
        
        if self.storage_size < 0:
            raise ValueError("Storage size cannot be negative")
        
        return True
    
    def increment_version(self, increment_type: str = "patch") -> str:
        """Increment version number based on type."""
        if increment_type not in ["major", "minor", "patch"]:
            raise ValueError("Increment type must be major, minor, or patch")
        
        parts = [int(p) for p in self.version_number.split('.')]
        
        if increment_type == "major":
            parts[0] += 1
            parts[1] = 0
            parts[2] = 0 if len(parts) > 2 else 0
        elif increment_type == "minor":
            if len(parts) > 1:
                parts[1] += 1
                parts[2] = 0 if len(parts) > 2 else 0
            else:
                parts.append(1)
        elif increment_type == "patch":
            if len(parts) > 2:
                parts[2] += 1
            else:
                parts.append(1)
        
        return '.'.join(map(str, parts))
    
    def is_older_than(self, other_version: 'DataVersion') -> bool:
        """Check if this version is older than another version."""
        this_parts = [int(p) for p in self.version_number.split('.')]
        other_parts = [int(p) for p in other_version.version_number.split('.')]
        
        # Pad with zeros if needed
        max_len = max(len(this_parts), len(other_parts))
        this_parts.extend([0] * (max_len - len(this_parts)))
        other_parts.extend([0] * (max_len - len(other_parts)))
        
        for i in range(max_len):
            if this_parts[i] < other_parts[i]:
                return True
            elif this_parts[i] > other_parts[i]:
                return False
        
        return False  # Same version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        
        # Handle JSON fields
        data['change_details'] = json.dumps(self.change_details) if self.change_details else "{}"
        data['data_snapshot'] = json.dumps(self.data_snapshot) if self.data_snapshot else "{}"
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataVersion':
        """Create from dictionary from database."""
        # Parse JSON fields
        json_fields = ['change_details', 'data_snapshot']
        
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    data[field] = {}
        
        return super().from_dict(data)
