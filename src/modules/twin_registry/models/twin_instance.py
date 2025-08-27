"""
Twin Instance Model

Manages versioning and instances of digital twins.
"""

from src.engine.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class TwinInstance(BaseModel):
    """Model for managing twin instances and versioning"""
    
    instance_id: str
    twin_id: str
    version: int
    instance_data: Dict[str, Any]
    instance_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    created_by: Optional[str] = None
    is_active: bool = True
    parent_instance_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def create_instance(
        cls,
        twin_id: str,
        instance_data: Dict[str, Any],
        instance_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
        parent_instance_id: Optional[str] = None
    ) -> "TwinInstance":
        """Create a new twin instance"""
        now = datetime.utcnow()
        return cls(
            instance_id=str(uuid.uuid4()),
            twin_id=twin_id,
            version=1,  # Will be set by repository
            instance_data=instance_data,
            instance_metadata=instance_metadata or {},
            created_at=now,
            created_by=created_by,
            is_active=True,
            parent_instance_id=parent_instance_id
        )
    
    def update_instance_data(self, new_data: Dict[str, Any]) -> None:
        """Update instance data"""
        self.instance_data.update(new_data)
    
    def update_metadata(self, new_metadata: Dict[str, Any]) -> None:
        """Update instance metadata"""
        if self.instance_metadata is None:
            self.instance_metadata = {}
        self.instance_metadata.update(new_metadata)
    
    def deactivate(self) -> None:
        """Deactivate the instance"""
        self.is_active = False
    
    def activate(self) -> None:
        """Activate the instance"""
        self.is_active = True


class TwinInstanceQuery(BaseModel):
    """Query model for filtering twin instances"""
    
    twin_id: Optional[str] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None
    created_by: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TwinInstanceSummary(BaseModel):
    """Summary model for twin instance statistics"""
    
    total_instances: int
    active_instances: int
    latest_version: int
    instance_history: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TwinInstanceDiff(BaseModel):
    """Model for comparing twin instances"""
    
    instance_id_1: str
    instance_id_2: str
    differences: Dict[str, Any]
    added_fields: List[str]
    removed_fields: List[str]
    modified_fields: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 