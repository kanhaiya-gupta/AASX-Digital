"""
AI RAG Graph Node Model
=======================

Represents individual nodes in the knowledge graph.
"""

import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator
from src.engine.models.base_model import BaseModel as EngineBaseModel


class GraphNode(EngineBaseModel):
    """
    Graph Node Model
    
    Represents a node in the knowledge graph with properties,
    metadata, and validation capabilities.
    """
    
    # Core Identification
    node_id: str = Field(..., description="Unique identifier for the node")
    node_type: str = Field(..., description="Type of node: entity, concept, document, process")
    node_label: str = Field(..., description="Human-readable label for the node")
    
    # Node Properties
    properties: str = Field(default="{}", description="JSON string of node properties")
    attributes: str = Field(default="[]", description="JSON array of node attributes")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in node extraction")
    
    # Content Information
    content_hash: Optional[str] = Field(None, description="Hash of node content for deduplication")
    source_text: Optional[str] = Field(None, description="Original text that generated this node")
    source_document_id: Optional[str] = Field(None, description="ID of source document")
    
    # Positional Information
    position_x: Optional[float] = Field(None, description="X coordinate for visualization")
    position_y: Optional[float] = Field(None, description="Y coordinate for visualization")
    layer: Optional[int] = Field(default=0, description="Layer/level in the graph hierarchy")
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    created_by: str = Field(..., description="User/system that created the node")
    
    # Graph Context
    graph_id: str = Field(..., description="ID of the graph this node belongs to")
    cluster_id: Optional[str] = Field(None, description="Cluster/community this node belongs to")
    
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
        """Check if node is validated."""
        return self.validation_status == "validated"
    
    @property
    def has_validation_errors(self) -> bool:
        """Check if node has validation errors."""
        return len(self.validation_errors_list) > 0
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if node has high confidence."""
        return self.confidence_score >= 0.8
    
    @property
    def is_high_quality(self) -> bool:
        """Check if node has high quality."""
        return self.quality_score >= 0.8
    
    # Validators
    @validator('node_type')
    def validate_node_type(cls, v):
        """Validate node type."""
        allowed_types = ['entity', 'concept', 'document', 'process']
        if v not in allowed_types:
            raise ValueError(f'node_type must be one of: {allowed_types}')
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
    
    @root_validator
    def validate_properties_json(cls, values):
        """Validate that properties is valid JSON."""
        properties = values.get('properties')
        if properties:
            try:
                json.loads(properties)
            except json.JSONDecodeError:
                raise ValueError('properties must be valid JSON')
        return values
    
    # Business Logic Methods
    def add_property(self, key: str, value: Any) -> None:
        """Add a property to the node."""
        props = self.properties_dict
        props[key] = value
        self.properties = json.dumps(props)
        self.updated_at = datetime.now().isoformat()
    
    def remove_property(self, key: str) -> None:
        """Remove a property from the node."""
        props = self.properties_dict
        if key in props:
            del props[key]
            self.properties = json.dumps(props)
            self.updated_at = datetime.now().isoformat()
    
    def add_attribute(self, attribute: Dict[str, Any]) -> None:
        """Add an attribute to the node."""
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
        """Mark node as validated."""
        self.validation_status = "validated"
        self.updated_at = datetime.now().isoformat()
    
    def update_position(self, x: float, y: float) -> None:
        """Update node position."""
        self.position_x = x
        self.position_y = y
        self.updated_at = datetime.now().isoformat()
    
    def update_layer(self, layer: int) -> None:
        """Update node layer."""
        self.layer = layer
        self.updated_at = datetime.now().isoformat()
    
    def calculate_quality_score(self) -> float:
        """Calculate quality score based on various factors."""
        score = 0.0
        
        # Confidence score (40% weight)
        score += self.confidence_score * 0.4
        
        # Validation status (30% weight)
        if self.is_validated:
            score += 0.3
        elif self.has_validation_errors:
            score += 0.0
        else:
            score += 0.15  # Partial credit for pending
        
        # Properties completeness (20% weight)
        props = self.properties_dict
        if props:
            # Score based on number of meaningful properties
            meaningful_props = len([k for k, v in props.items() if v and str(v).strip()])
            if meaningful_props >= 3:
                score += 0.2
            elif meaningful_props >= 1:
                score += 0.1
        
        # Source information (10% weight)
        if self.source_text and self.source_document_id:
            score += 0.1
        
        self.quality_score = min(score, 1.0)
        return self.quality_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "node_label": self.node_label,
            "properties": self.properties_dict,
            "attributes": self.attributes_list,
            "confidence_score": self.confidence_score,
            "content_hash": self.content_hash,
            "source_text": self.source_text,
            "source_document_id": self.source_document_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "layer": self.layer,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "graph_id": self.graph_id,
            "cluster_id": self.cluster_id,
            "quality_score": self.quality_score,
            "validation_status": self.validation_status,
            "validation_errors": self.validation_errors_list,
            "is_validated": self.is_validated,
            "has_validation_errors": self.has_validation_errors,
            "is_high_confidence": self.is_high_confidence,
            "is_high_quality": self.is_high_quality
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"GraphNode(id='{self.node_id}', type='{self.node_type}', label='{self.node_label}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"GraphNode(node_id='{self.node_id}', node_type='{self.node_type}', node_label='{self.node_label}', graph_id='{self.graph_id}', quality_score={self.quality_score})"
