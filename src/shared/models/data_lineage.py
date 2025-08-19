"""
Data Lineage Model
==================

Data model for tracking data relationships and transformations in the AAS Data Modeling framework.
"""

from typing import Optional, Dict, Any, List
from .base_model import BaseModel
from pydantic import Field
import json
import uuid

class DataLineage(BaseModel):
    """Data lineage model for tracking data relationships and transformations."""
    
    lineage_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique lineage identifier")
    source_entity_type: str = Field(..., description="Type of source entity")
    source_entity_id: str = Field(..., description="ID of source entity")
    target_entity_type: str = Field(..., description="Type of target entity")
    target_entity_id: str = Field(..., description="ID of target entity")
    relationship_type: str = Field(..., description="Type of relationship")
    lineage_depth: int = Field(default=1, description="Depth of lineage relationship")
    confidence_score: float = Field(default=1.0, description="Confidence in relationship (0.0-1.0)")
    transformation_type: str = Field(default="none", description="Type of transformation")
    transformation_details: Dict[str, Any] = Field(default_factory=dict, description="Transformation details")
    lineage_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional lineage information")
    is_active: bool = Field(default=True, description="Active status")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    
    # Performance and tracking
    last_accessed: Optional[str] = Field(default=None, description="Last access timestamp")
    access_count: int = Field(default=0, description="Number of times accessed")
    validation_status: str = Field(default="pending", description="Validation status")
    
    # Enhanced Lineage Features (Phase 2)
    transformation_steps: List[str] = Field(default_factory=list, description="Step-by-step transformation process")
    data_quality_impact: float = Field(default=0.0, description="Impact on data quality scores")
    business_value_score: float = Field(default=0.0, description="Business value of this lineage")
    lineage_complexity: str = Field(default="simple", description="Complexity level of lineage")
    validation_rules: List[str] = Field(default_factory=list, description="Validation rules applied")
    lineage_confidence_factors: Dict[str, Any] = Field(default_factory=dict, description="Factors affecting confidence")
    lineage_impact_analysis: Dict[str, Any] = Field(default_factory=dict, description="Impact analysis results")
    
    # Dependency Management (Phase 2)
    dependency_level: str = Field(default="direct", description="Level of dependency")
    dependency_criticality: str = Field(default="low", description="Criticality of dependency")
    dependency_risk_score: float = Field(default=0.0, description="Risk assessment score")
    dependency_mitigation: Dict[str, Any] = Field(default_factory=dict, description="Risk mitigation strategies")
    dependency_alerts: List[str] = Field(default_factory=list, description="Alert configurations")
    dependency_visualization: Dict[str, Any] = Field(default_factory=dict, description="Visualization preferences")
    
    def validate(self) -> bool:
        """Validate data lineage."""
        valid_entity_types = ["file", "project", "use_case", "user", "organization"]
        if self.source_entity_type not in valid_entity_types:
            raise ValueError(f"Source entity type must be one of: {valid_entity_types}")
        
        if self.target_entity_type not in valid_entity_types:
            raise ValueError(f"Target entity type must be one of: {valid_entity_types}")
        
        valid_relationship_types = ["derived_from", "depends_on", "contains", "belongs_to", "processed_by", "owned_by"]
        if self.relationship_type not in valid_relationship_types:
            raise ValueError(f"Relationship type must be one of: {valid_relationship_types}")
        
        valid_transformation_types = ["none", "extraction", "processing", "aggregation", "filtering", "enrichment"]
        if self.transformation_type not in valid_transformation_types:
            raise ValueError(f"Transformation type must be one of: {valid_transformation_types}")
        
        valid_validation_statuses = ["pending", "validated", "invalid", "needs_review"]
        if self.validation_status not in valid_validation_statuses:
            raise ValueError(f"Validation status must be one of: {valid_validation_statuses}")
        
        # Phase 2 validation
        valid_lineage_complexities = ["simple", "moderate", "complex"]
        if self.lineage_complexity not in valid_lineage_complexities:
            raise ValueError(f"Lineage complexity must be one of: {valid_lineage_complexities}")
        
        valid_dependency_levels = ["direct", "indirect", "transitive"]
        if self.dependency_level not in valid_dependency_levels:
            raise ValueError(f"Dependency level must be one of: {valid_dependency_levels}")
        
        valid_dependency_criticalities = ["low", "medium", "high", "critical"]
        if self.dependency_criticality not in valid_dependency_criticalities:
            raise ValueError(f"Dependency criticality must be one of: {valid_dependency_criticalities}")
        
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        
        if self.lineage_depth < 1:
            raise ValueError("Lineage depth must be at least 1")
        
        if self.access_count < 0:
            raise ValueError("Access count cannot be negative")
        
        if not (-100.0 <= self.data_quality_impact <= 100.0):
            raise ValueError("Data quality impact must be between -100.0 and 100.0")
        
        if not (0.0 <= self.business_value_score <= 100.0):
            raise ValueError("Business value score must be between 0.0 and 100.0")
        
        if not (0.0 <= self.dependency_risk_score <= 100.0):
            raise ValueError("Dependency risk score must be between 0.0 and 100.0")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = super().to_dict()
        
        # Handle JSON fields
        data['transformation_details'] = json.dumps(self.transformation_details) if self.transformation_details else "{}"
        data['lineage_metadata'] = json.dumps(self.lineage_metadata) if self.lineage_metadata else "{}"
        data['transformation_steps'] = json.dumps(self.transformation_steps) if self.transformation_steps else "[]"
        data['validation_rules'] = json.dumps(self.validation_rules) if self.validation_rules else "[]"
        data['lineage_confidence_factors'] = json.dumps(self.lineage_confidence_factors) if self.lineage_confidence_factors else "{}"
        data['lineage_impact_analysis'] = json.dumps(self.lineage_impact_analysis) if self.lineage_impact_analysis else "{}"
        data['dependency_mitigation'] = json.dumps(self.dependency_mitigation) if self.dependency_mitigation else "{}"
        data['dependency_alerts'] = json.dumps(self.dependency_alerts) if self.dependency_alerts else "[]"
        data['dependency_visualization'] = json.dumps(self.dependency_visualization) if self.dependency_visualization else "{}"
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataLineage':
        """Create from dictionary from database."""
        # Parse JSON fields
        json_fields = [
            'transformation_details', 'lineage_metadata', 'transformation_steps',
            'validation_rules', 'lineage_confidence_factors', 'lineage_impact_analysis',
            'dependency_mitigation', 'dependency_alerts', 'dependency_visualization'
        ]
        
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    if field in ['transformation_steps', 'validation_rules', 'dependency_alerts']:
                        data[field] = []
                    else:
                        data[field] = {}
        
        return super().from_dict(data)
