"""
AI RAG Graph Edge Model
=======================

Represents relationships between nodes in the knowledge graph.
"""

import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, model_validator
from src.engine.models.base_model import EngineBaseModel


class GraphEdge(EngineBaseModel):
    """
    Graph Edge Model
    
    Represents a relationship/edge between two nodes in the knowledge graph
    with properties, weights, and validation capabilities.
    """
    
    # Core Identification
    edge_id: str = Field(..., description="Unique identifier for the edge")
    source_node_id: str = Field(..., description="ID of the source node")
    target_node_id: str = Field(..., description="ID of the target node")
    
    # Edge Properties
    relationship_type: str = Field(..., description="Type of relationship: contains, depends_on, relates_to, etc.")
    relationship_label: str = Field(..., description="Human-readable label for the relationship")
    properties: str = Field(default="{}", description="JSON string of edge properties")
    attributes: str = Field(default="[]", description="JSON array of edge attributes")
    
    # Relationship Strength
    weight: float = Field(default=1.0, ge=0.0, le=10.0, description="Relationship strength/weight")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in relationship extraction")
    
    # Direction and Type
    is_directed: bool = Field(default=True, description="Whether the relationship is directed")
    is_bidirectional: bool = Field(default=False, description="Whether the relationship works both ways")
    
    # Content Information
    source_text: Optional[str] = Field(None, description="Original text that generated this relationship")
    source_document_id: Optional[str] = Field(None, description="ID of source document")
    
    # Graph Context
    graph_id: str = Field(..., description="ID of the graph this edge belongs to")
    cluster_id: Optional[str] = Field(None, description="Cluster/community this edge belongs to")
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    created_by: str = Field(..., description="User/system that created the edge")
    
    # Quality Metrics
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall quality score")
    validation_status: str = Field(default="pending", description="Status: pending, validated, failed")
    validation_errors: str = Field(default="[]", description="JSON array of validation errors")
    
    # Computed Properties
    @property
    def properties_dict(self) -> Dict[str, Any]:
        """Get properties as a Python dictionary."""
        try:
            return json.loads(self.properties) if self.properties else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def attributes_list(self) -> List[Dict[str, Any]]:
        """Get attributes as a Python list."""
        try:
            return json.loads(self.attributes) if self.attributes else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def validation_errors_list(self) -> List[str]:
        """Get validation errors as a Python list."""
        try:
            return json.loads(self.validation_errors) if self.validation_errors else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def is_validated(self) -> bool:
        """Check if edge is validated."""
        return self.validation_status == "validated"
    
    @property
    def has_validation_errors(self) -> bool:
        """Check if edge has validation errors."""
        return len(self.validation_errors_list) > 0
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if edge has high confidence."""
        return self.confidence_score >= 0.8
    
    @property
    def is_high_quality(self) -> bool:
        """Check if edge has high quality."""
        return self.quality_score >= 0.8
    
    @property
    def is_strong_relationship(self) -> bool:
        """Check if this is a strong relationship."""
        return self.weight >= 7.0
    
    @property
    def is_weak_relationship(self) -> bool:
        """Check if this is a weak relationship."""
        return self.weight <= 3.0
    
    # Validators
    @validator('relationship_type')
    def validate_relationship_type(cls, v):
        """Validate relationship type."""
        allowed_types = [
            'contains', 'depends_on', 'relates_to', 'implements', 'extends',
            'uses', 'creates', 'modifies', 'triggers', 'follows', 'precedes',
            'similar_to', 'opposite_of', 'part_of', 'member_of', 'instance_of'
        ]
        if v not in allowed_types:
            raise ValueError(f'relationship_type must be one of: {allowed_types}')
        return v
    
    @validator('validation_status')
    def validate_validation_status(cls, v):
        """Validate validation status."""
        allowed_statuses = ['pending', 'validated', 'failed']
        if v not in allowed_statuses:
            raise ValueError(f'validation_status must be one of: {allowed_statuses}')
        return v
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        """Validate confidence score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('confidence_score must be between 0.0 and 1.0')
        return v
    
    @validator('quality_score')
    def validate_quality_score(cls, v):
        """Validate quality score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('quality_score must be between 0.0 and 1.0')
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        """Validate weight."""
        if not 0.0 <= v <= 10.0:
            raise ValueError('weight must be between 0.0 and 10.0')
        return v
    
    @model_validator(mode='after')
    def validate_properties_json(self):
        """Validate that properties is valid JSON."""
        if self.properties:
            try:
                json.loads(self.properties)
            except json.JSONDecodeError:
                raise ValueError('properties must be valid JSON')
        return self
    
    @model_validator(mode='after')
    def validate_source_target_different(self):
        """Validate that source and target nodes are different."""
        if self.source_node_id and self.target_node_id and self.source_node_id == self.target_node_id:
            raise ValueError('source_node_id and target_node_id must be different')
        return self
    
    # Business Logic Methods
    def add_property(self, key: str, value: Any) -> None:
        """Add a property to the edge."""
        props = self.properties_dict
        props[key] = value
        self.properties = json.dumps(props)
        self.updated_at = datetime.now().isoformat()
    
    def remove_property(self, key: str) -> None:
        """Remove a property from the edge."""
        props = self.properties_dict
        if key in props:
            del props[key]
            self.properties = json.dumps(props)
            self.updated_at = datetime.now().isoformat()
    
    def add_attribute(self, attribute: Dict[str, Any]) -> None:
        """Add an attribute to the edge."""
        attrs = self.attributes_list
        attrs.append(attribute)
        self.attributes = json.dumps(attrs)
        self.updated_at = datetime.now().isoformat()
    
    def add_validation_error(self, error: str) -> None:
        """Add a validation error."""
        errors = self.validation_errors_list
        errors.append(error)
        self.validation_errors = json.dumps(errors)
        self.validation_status = "failed"
        self.updated_at = datetime.now().isoformat()
    
    def mark_validated(self) -> None:
        """Mark edge as validated."""
        self.validation_status = "validated"
        self.updated_at = datetime.now().isoformat()
    
    def update_weight(self, new_weight: float) -> None:
        """Update relationship weight."""
        if 0.0 <= new_weight <= 10.0:
            self.weight = new_weight
            self.updated_at = datetime.now().isoformat()
        else:
            raise ValueError('weight must be between 0.0 and 10.0')
    
    def update_confidence(self, new_confidence: float) -> None:
        """Update confidence score."""
        if 0.0 <= new_confidence <= 1.0:
            self.confidence_score = new_confidence
            self.updated_at = datetime.now().isoformat()
        else:
            raise ValueError('confidence_score must be between 0.0 and 1.0')
    
    def make_bidirectional(self) -> None:
        """Make the relationship bidirectional."""
        self.is_bidirectional = True
        self.updated_at = datetime.now().isoformat()
    
    def make_unidirectional(self) -> None:
        """Make the relationship unidirectional."""
        self.is_bidirectional = False
        self.updated_at = datetime.now().isoformat()
    
    def calculate_quality_score(self) -> float:
        """Calculate quality score based on various factors."""
        score = 0.0
        
        # Confidence score (35% weight)
        score += self.confidence_score * 0.35
        
        # Validation status (25% weight)
        if self.is_validated:
            score += 0.25
        elif self.has_validation_errors:
            score += 0.0
        else:
            score += 0.125  # Partial credit for pending
        
        # Weight strength (20% weight)
        if self.is_strong_relationship:
            score += 0.2
        elif not self.is_weak_relationship:
            score += 0.1
        
        # Properties completeness (15% weight)
        props = self.properties_dict
        if props:
            meaningful_props = len([k for k, v in props.items() if v and str(v).strip()])
            if meaningful_props >= 2:
                score += 0.15
            elif meaningful_props >= 1:
                score += 0.075
        
        # Source information (5% weight)
        if self.source_text and self.source_document_id:
            score += 0.05
        
        self.quality_score = min(score, 1.0)
        return self.quality_score
    
    def get_reverse_relationship(self) -> 'GraphEdge':
        """Create a reverse relationship edge."""
        reverse_edge = GraphEdge(
            edge_id=f"rev_{self.edge_id}",
            source_node_id=self.target_node_id,
            target_node_id=self.source_node_id,
            relationship_type=self.relationship_type,
            relationship_label=f"reverse_{self.relationship_label}",
            properties=self.properties,
            attributes=self.attributes,
            weight=self.weight,
            confidence_score=self.confidence_score,
            is_directed=self.is_directed,
            is_bidirectional=False,  # Reverse edge is not bidirectional
            source_text=self.source_text,
            source_document_id=self.source_document_id,
            graph_id=self.graph_id,
            cluster_id=self.cluster_id,
            created_by=self.created_by
        )
        return reverse_edge
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "relationship_type": self.relationship_type,
            "relationship_label": self.relationship_label,
            "properties": self.properties_dict,
            "attributes": self.attributes_list,
            "weight": self.weight,
            "confidence_score": self.confidence_score,
            "is_directed": self.is_directed,
            "is_bidirectional": self.is_bidirectional,
            "source_text": self.source_text,
            "source_document_id": self.source_document_id,
            "graph_id": self.graph_id,
            "cluster_id": self.cluster_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "quality_score": self.quality_score,
            "validation_status": self.validation_status,
            "validation_errors": self.validation_errors_list,
            "is_validated": self.is_validated,
            "has_validation_errors": self.has_validation_errors,
            "is_high_confidence": self.is_high_confidence,
            "is_high_quality": self.is_high_quality,
            "is_strong_relationship": self.is_strong_relationship,
            "is_weak_relationship": self.is_weak_relationship
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"GraphEdge(id='{self.edge_id}', {self.source_node_id} -> {self.target_node_id}, type='{self.relationship_type}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"GraphEdge(edge_id='{self.edge_id}', source='{self.source_node_id}', target='{self.target_node_id}', type='{self.relationship_type}', weight={self.weight}, quality={self.quality_score})"
