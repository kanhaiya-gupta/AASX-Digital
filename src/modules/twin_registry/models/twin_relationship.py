"""
Twin Relationship Model

Manages parent-child relationships and hierarchies between digital twins.
"""

from src.engine.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class TwinRelationship(BaseModel):
    """Model for managing relationships between digital twins"""
    
    relationship_id: str
    source_twin_id: str
    target_twin_id: str
    relationship_type: str  # parent-child, sibling, dependency, etc.
    relationship_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def create_relationship(
        cls,
        source_twin_id: str,
        target_twin_id: str,
        relationship_type: str,
        relationship_data: Optional[Dict[str, Any]] = None
    ) -> "TwinRelationship":
        """Create a new twin relationship"""
        now = datetime.utcnow()
        return cls(
            relationship_id=str(uuid.uuid4()),
            source_twin_id=source_twin_id,
            target_twin_id=target_twin_id,
            relationship_type=relationship_type,
            relationship_data=relationship_data or {},
            created_at=now,
            updated_at=now,
            is_active=True
        )
    
    def update_relationship_data(self, new_data: Dict[str, Any]) -> None:
        """Update relationship data"""
        if self.relationship_data is None:
            self.relationship_data = {}
        self.relationship_data.update(new_data)
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the relationship"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate the relationship"""
        self.is_active = True
        self.updated_at = datetime.utcnow()


class TwinRelationshipQuery(BaseModel):
    """Query model for filtering twin relationships"""
    
    source_twin_id: Optional[str] = None
    target_twin_id: Optional[str] = None
    relationship_type: Optional[str] = None
    is_active: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TwinRelationshipSummary(BaseModel):
    """Summary model for twin relationship statistics"""
    
    total_relationships: int
    active_relationships: int
    relationship_types: Dict[str, int]
    source_twins: List[str]
    target_twins: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 