"""
Change Request Model
===================

Data model for managing data change workflows in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any, List
from .base_model import BaseModel
from pydantic import Field
import json
import uuid
from datetime import datetime

class ChangeRequest(BaseModel):
    """Change request model for managing data change workflows."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique change request identifier")
    title: str = Field(..., description="Change request title")
    description: str = Field(default="", description="Detailed description of the change")
    change_type: str = Field(..., description="Type of change requested")
    entity_type: str = Field(..., description="Type of entity being changed")
    entity_id: Optional[str] = Field(default=None, description="ID of entity being changed")
    requested_by: str = Field(..., description="User ID who requested the change")
    requested_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Request timestamp")
    
    # Change Details
    change_details: Dict[str, Any] = Field(default_factory=dict, description="Specific changes requested")
    current_state: Dict[str, Any] = Field(default_factory=dict, description="Current state before change")
    proposed_state: Dict[str, Any] = Field(default_factory=dict, description="Proposed state after change")
    impact_analysis: Dict[str, Any] = Field(default_factory=dict, description="Impact assessment")
    
    # Workflow Status
    status: str = Field(default="pending", description="Current workflow status")
    priority: str = Field(default="medium", description="Change priority level")
    urgency: str = Field(default="normal", description="Change urgency level")
    
    # Approval Process
    assigned_to: Optional[str] = Field(default=None, description="User assigned to review/approve")
    assigned_at: Optional[str] = Field(default=None, description="Assignment timestamp")
    review_deadline: Optional[str] = Field(default=None, description="Review deadline")
    approval_required: bool = Field(default=True, description="Whether approval is required")
    approval_chain: List[str] = Field(default_factory=list, description="Approval hierarchy")
    
    # Review & Approval
    review_notes: Optional[str] = Field(default=None, description="Review notes and comments")
    review_date: Optional[str] = Field(default=None, description="Review completion date")
    reviewed_by: Optional[str] = Field(default=None, description="User who reviewed the request")
    approval_date: Optional[str] = Field(default=None, description="Approval date")
    approved_by: Optional[str] = Field(default=None, description="User who approved the request")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection if applicable")
    
    # Implementation
    implementation_notes: Optional[str] = Field(default=None, description="Implementation notes")
    implementation_date: Optional[str] = Field(default=None, description="Implementation completion date")
    implemented_by: Optional[str] = Field(default=None, description="User who implemented the change")
    rollback_plan: Dict[str, Any] = Field(default_factory=dict, description="Rollback strategy")
    
    # Metadata & Tracking
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional information")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    
    def validate(self) -> bool:
        """Validate change request data."""
        valid_change_types = ["create", "update", "delete", "restore", "bulk_update", "schema_change"]
        if self.change_type not in valid_change_types:
            raise ValueError(f"Change type must be one of: {valid_change_types}")
        
        valid_entity_types = ["file", "project", "use_case", "user", "organization", "data_lineage", "quality_metrics"]
        if self.entity_type not in valid_entity_types:
            raise ValueError(f"Entity type must be one of: {valid_entity_types}")
        
        valid_statuses = ["pending", "under_review", "approved", "rejected", "in_progress", "completed", "cancelled"]
        if self.status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        
        valid_priorities = ["low", "medium", "high", "critical"]
        if self.priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        
        valid_urgencies = ["normal", "high", "urgent", "emergency"]
        if self.urgency not in valid_urgencies:
            raise ValueError(f"Urgency must be one of: {valid_urgencies}")
        
        if not self.title or not self.title.strip():
            raise ValueError("Change request title is required")
        
        if len(self.title) > 255:
            raise ValueError("Title must be less than 255 characters")
        
        if len(self.description) > 2000:
            raise ValueError("Description must be less than 2000 characters")
        
        return True
    
    def can_approve(self, user_id: str) -> bool:
        """Check if a user can approve this change request."""
        if self.status != "under_review":
            return False
        
        if not self.approval_required:
            return True
        
        # Check if user is in approval chain
        return user_id in self.approval_chain
    
    def can_implement(self, user_id: str) -> bool:
        """Check if a user can implement this change request."""
        return self.status == "approved" and (
            user_id == self.requested_by or 
            user_id == self.assigned_to or
            user_id == self.approved_by
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        
        # Handle JSON fields
        data['change_details'] = json.dumps(self.change_details) if self.change_details else "{}"
        data['current_state'] = json.dumps(self.current_state) if self.current_state else "{}"
        data['proposed_state'] = json.dumps(self.proposed_state) if self.proposed_state else "{}"
        data['impact_analysis'] = json.dumps(self.impact_analysis) if self.impact_analysis else "{}"
        data['approval_chain'] = json.dumps(self.approval_chain) if self.approval_chain else "[]"
        data['rollback_plan'] = json.dumps(self.rollback_plan) if self.rollback_plan else "{}"
        data['tags'] = json.dumps(self.tags) if self.tags else "[]"
        data['metadata'] = json.dumps(self.metadata) if self.metadata else "{}"
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeRequest':
        """Create from dictionary from database."""
        # Parse JSON fields
        json_fields = [
            'change_details', 'current_state', 'proposed_state', 'impact_analysis',
            'approval_chain', 'rollback_plan', 'tags', 'metadata'
        ]
        
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    if field in ['approval_chain', 'tags']:
                        data[field] = []
                    else:
                        data[field] = {}
        
        return super().from_dict(data)
