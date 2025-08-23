"""
AI RAG Graph Structure Model
============================

Represents the complete graph structure with nodes, edges, and analytics.
"""

import json
from typing import Dict, Any, List, Optional, Union, Set
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator
from src.engine.models.base_model import BaseModel as EngineBaseModel

from .graph_node import GraphNode
from .graph_edge import GraphEdge


class GraphStructure(EngineBaseModel):
    """
    Graph Structure Model
    
    Represents the complete graph structure with nodes, edges,
    and comprehensive graph-level analytics and properties.
    """
    
    # Core Identification
    graph_id: str = Field(..., description="Unique identifier for the graph")
    graph_name: str = Field(..., description="Human-readable name for the graph")
    graph_type: str = Field(..., description="Type of graph: entity_relationship, knowledge_graph, dependency_graph")
    graph_category: str = Field(..., description="Category: technical, business, operational")
    
    # Graph Components
    nodes: List[GraphNode] = Field(default_factory=list, description="List of graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="List of graph edges")
    
    # Graph Properties
    properties: str = Field(default="{}", description="JSON string of graph-level properties")
    metadata: str = Field(default="{}", description="JSON string of graph metadata")
    
    # Graph Analytics
    node_count: int = Field(default=0, description="Total number of nodes")
    edge_count: int = Field(default=0, description="Total number of edges")
    graph_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Graph density")
    graph_diameter: int = Field(default=0, description="Graph diameter (longest shortest path)")
    average_clustering: float = Field(default=0.0, ge=0.0, le=1.0, description="Average clustering coefficient")
    connected_components: int = Field(default=1, description="Number of connected components")
    
    # Quality Metrics
    overall_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall graph quality score")
    validation_status: str = Field(default="pending", description="Status: pending, validated, failed")
    validation_errors: str = Field(default="[]", description="JSON array of validation errors")
    
    # Graph Context
    source_documents: str = Field(default="[]", description="JSON array of source document IDs")
    source_entities: str = Field(default="[]", description="JSON array of source entities")
    source_relationships: str = Field(default="[]", description="JSON array of source relationships")
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    created_by: str = Field(..., description="User/system that created the graph")
    
    # Computed Properties
    @property
    def properties_dict(self) -> Dict[str, Any]:
        """Get properties as a Python dictionary."""
        try:
            return json.loads(self.properties) if self.properties else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def metadata_dict(self) -> Dict[str, Any]:
        """Get metadata as a Python dictionary."""
        try:
            return json.loads(self.metadata) if self.metadata else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def validation_errors_list(self) -> List[str]:
        """Get validation errors as a Python list."""
        try:
            return json.loads(self.validation_errors) if self.validation_errors else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def source_documents_list(self) -> List[str]:
        """Get source documents as a Python list."""
        try:
            return json.loads(self.source_documents) if self.source_documents else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def source_entities_list(self) -> List[Dict[str, Any]]:
        """Get source entities as a Python list."""
        try:
            return json.loads(self.source_entities) if self.source_entities else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def source_relationships_list(self) -> List[Dict[str, Any]]:
        """Get source relationships as a Python list."""
        try:
            return json.loads(self.source_relationships) if self.source_relationships else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def is_validated(self) -> bool:
        """Check if graph is validated."""
        return self.validation_status == "validated"
    
    @property
    def has_validation_errors(self) -> bool:
        """Check if graph has validation errors."""
        return len(self.validation_errors_list) > 0
    
    @property
    def is_high_quality(self) -> bool:
        """Check if graph has high quality."""
        return self.overall_quality_score >= 0.8
    
    @property
    def is_dense(self) -> bool:
        """Check if graph is dense."""
        return self.graph_density >= 0.5
    
    @property
    def is_sparse(self) -> bool:
        """Check if graph is sparse."""
        return self.graph_density <= 0.2
    
    @property
    def is_connected(self) -> bool:
        """Check if graph is fully connected."""
        return self.connected_components == 1
    
    @property
    def node_ids_set(self) -> Set[str]:
        """Get set of all node IDs."""
        return {node.node_id for node in self.nodes}
    
    @property
    def edge_ids_set(self) -> Set[str]:
        """Get set of all edge IDs."""
        return {edge.edge_id for edge in self.edges}
    
    # Validators
    @validator('graph_type')
    def validate_graph_type(cls, v):
        """Validate graph type."""
        allowed_types = ['entity_relationship', 'knowledge_graph', 'dependency_graph']
        if v not in allowed_types:
            raise ValueError(f'graph_type must be one of: {allowed_types}')
        return v
    
    @validator('graph_category')
    def validate_graph_category(cls, v):
        """Validate graph category."""
        allowed_categories = ['technical', 'business', 'operational']
        if v not in allowed_categories:
            raise ValueError(f'graph_category must be one of: {allowed_categories}')
        return v
    
    @validator('validation_status')
    def validate_validation_status(cls, v):
        """Validate validation status."""
        allowed_statuses = ['pending', 'validated', 'failed']
        if v not in allowed_statuses:
            raise ValueError(f'validation_status must be one of: {allowed_statuses}')
        return v
    
    @validator('overall_quality_score')
    def validate_quality_score(cls, v):
        """Validate quality score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('overall_quality_score must be between 0.0 and 1.0')
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
    
    @root_validator
    def validate_metadata_json(cls, values):
        """Validate that metadata is valid JSON."""
        metadata = values.get('metadata')
        if metadata:
            try:
                json.loads(metadata)
            except json.JSONDecodeError:
                raise ValueError('metadata must be valid JSON')
        return values
    
    # Business Logic Methods
    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        if node.node_id not in self.node_ids_set:
            self.nodes.append(node)
            self.node_count = len(self.nodes)
            self.updated_at = datetime.now().isoformat()
            self._recalculate_analytics()
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node from the graph."""
        self.nodes = [node for node in self.nodes if node.node_id != node_id]
        # Remove edges connected to this node
        self.edges = [edge for edge in self.edges 
                     if edge.source_node_id != node_id and edge.target_node_id != node_id]
        self.node_count = len(self.nodes)
        self.edge_count = len(self.edges)
        self.updated_at = datetime.now().isoformat()
        self._recalculate_analytics()
    
    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        if edge.edge_id not in self.edge_ids_set:
            # Verify both nodes exist
            if edge.source_node_id in self.node_ids_set and edge.target_node_id in self.node_ids_set:
                self.edges.append(edge)
                self.edge_count = len(self.edges)
                self.updated_at = datetime.now().isoformat()
                self._recalculate_analytics()
            else:
                raise ValueError(f"Edge {edge.edge_id} references non-existent nodes")
    
    def remove_edge(self, edge_id: str) -> None:
        """Remove an edge from the graph."""
        self.edges = [edge for edge in self.edges if edge.edge_id != edge_id]
        self.edge_count = len(self.edges)
        self.updated_at = datetime.now().isoformat()
        self._recalculate_analytics()
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """Get an edge by ID."""
        for edge in self.edges:
            if edge.edge_id == edge_id:
                return edge
        return None
    
    def get_node_neighbors(self, node_id: str) -> List[GraphNode]:
        """Get all neighboring nodes of a given node."""
        neighbors = []
        for edge in self.edges:
            if edge.source_node_id == node_id:
                neighbor = self.get_node(edge.target_node_id)
                if neighbor:
                    neighbors.append(neighbor)
            elif edge.target_node_id == node_id and not edge.is_directed:
                neighbor = self.get_node(edge.source_node_id)
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors
    
    def get_node_edges(self, node_id: str) -> List[GraphEdge]:
        """Get all edges connected to a given node."""
        return [edge for edge in self.edges 
                if edge.source_node_id == node_id or edge.target_node_id == node_id]
    
    def add_property(self, key: str, value: Any) -> None:
        """Add a property to the graph."""
        props = self.properties_dict
        props[key] = value
        self.properties = json.dumps(props)
        self.updated_at = datetime.now().isoformat()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the graph."""
        meta = self.metadata_dict
        meta[key] = value
        self.metadata = json.dumps(meta)
        self.updated_at = datetime.now().isoformat()
    
    def add_source_document(self, document_id: str) -> None:
        """Add a source document ID."""
        docs = self.source_documents_list
        if document_id not in docs:
            docs.append(document_id)
            self.source_documents = json.dumps(docs)
            self.updated_at = datetime.now().isoformat()
    
    def add_source_entity(self, entity: Dict[str, Any]) -> None:
        """Add a source entity."""
        entities = self.source_entities_list
        entities.append(entity)
        self.source_entities = json.dumps(entities)
        self.updated_at = datetime.now().isoformat()
    
    def add_source_relationship(self, relationship: Dict[str, Any]) -> None:
        """Add a source relationship."""
        relationships = self.source_relationships_list
        relationships.append(relationship)
        self.source_relationships = json.dumps(relationships)
        self.updated_at = datetime.now().isoformat()
    
    def add_validation_error(self, error: str) -> None:
        """Add a validation error."""
        errors = self.validation_errors_list
        errors.append(error)
        self.validation_errors = json.dumps(errors)
        self.validation_status = "failed"
        self.updated_at = datetime.now().isoformat()
    
    def mark_validated(self) -> None:
        """Mark graph as validated."""
        self.validation_status = "validated"
        self.updated_at = datetime.now().isoformat()
    
    def _recalculate_analytics(self) -> None:
        """Recalculate graph analytics."""
        self.node_count = len(self.nodes)
        self.edge_count = len(self.edges)
        
        # Calculate graph density
        if self.node_count > 1:
            max_edges = self.node_count * (self.node_count - 1)
            self.graph_density = self.edge_count / max_edges
        else:
            self.graph_density = 0.0
        
        # Calculate connected components (simplified)
        if self.node_count == 0:
            self.connected_components = 0
        elif self.edge_count == 0:
            self.connected_components = self.node_count
        else:
            # Simple connected component calculation
            visited = set()
            components = 0
            
            for node in self.nodes:
                if node.node_id not in visited:
                    components += 1
                    self._dfs_component(node.node_id, visited)
            
            self.connected_components = components
        
        # Calculate overall quality score
        self._calculate_overall_quality()
    
    def _dfs_component(self, node_id: str, visited: Set[str]) -> None:
        """DFS to find connected component."""
        visited.add(node_id)
        for edge in self.edges:
            if edge.source_node_id == node_id and edge.target_node_id not in visited:
                self._dfs_component(edge.target_node_id, visited)
            elif edge.target_node_id == node_id and not edge.is_directed and edge.source_node_id not in visited:
                self._dfs_component(edge.source_node_id, visited)
    
    def _calculate_overall_quality(self) -> None:
        """Calculate overall quality score."""
        if not self.nodes:
            self.overall_quality_score = 0.0
            return
        
        # Calculate average node quality
        node_quality_sum = sum(node.quality_score for node in self.nodes)
        avg_node_quality = node_quality_sum / len(self.nodes)
        
        # Calculate average edge quality
        edge_quality_sum = sum(edge.quality_score for edge in self.edges) if self.edges else 0
        avg_edge_quality = edge_quality_sum / len(self.edges) if self.edges else 0
        
        # Calculate structure quality
        structure_quality = 0.0
        if self.node_count > 0:
            # Reward for reasonable density
            if 0.1 <= self.graph_density <= 0.8:
                structure_quality += 0.3
            elif self.graph_density > 0:
                structure_quality += 0.1
            
            # Reward for connectivity
            if self.is_connected:
                structure_quality += 0.2
        
        # Overall score (40% nodes, 30% edges, 30% structure)
        self.overall_quality_score = (
            avg_node_quality * 0.4 +
            avg_edge_quality * 0.3 +
            structure_quality * 0.3
        )
    
    def validate_structure(self) -> Dict[str, Any]:
        """Validate the graph structure."""
        errors = []
        warnings = []
        
        # Check for orphaned nodes
        connected_nodes = set()
        for edge in self.edges:
            connected_nodes.add(edge.source_node_id)
            connected_nodes.add(edge.target_node_id)
        
        orphaned_nodes = self.node_ids_set - connected_nodes
        if orphaned_nodes:
            warnings.append(f"Found {len(orphaned_nodes)} orphaned nodes")
        
        # Check for self-loops
        self_loops = [edge for edge in self.edges 
                     if edge.source_node_id == edge.target_node_id]
        if self_loops:
            warnings.append(f"Found {len(self_loops)} self-loop edges")
        
        # Check for duplicate edges
        edge_pairs = set()
        for edge in self.edges:
            pair = (edge.source_node_id, edge.target_node_id)
            if pair in edge_pairs:
                errors.append(f"Duplicate edge found: {edge.edge_id}")
            edge_pairs.add(pair)
        
        # Check node consistency
        for node in self.nodes:
            if node.graph_id != self.graph_id:
                errors.append(f"Node {node.node_id} has mismatched graph_id")
        
        # Check edge consistency
        for edge in self.edges:
            if edge.graph_id != self.graph_id:
                errors.append(f"Edge {edge.edge_id} has mismatched graph_id")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "orphaned_nodes": len(orphaned_nodes),
            "self_loops": len(self_self_loops),
            "duplicate_edges": len([e for e in errors if "Duplicate edge" in e])
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph structure to dictionary."""
        return {
            "graph_id": self.graph_id,
            "graph_name": self.graph_name,
            "graph_type": self.graph_type,
            "graph_category": self.graph_category,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "properties": self.properties_dict,
            "metadata": self.metadata_dict,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "graph_density": self.graph_density,
            "graph_diameter": self.graph_diameter,
            "average_clustering": self.average_clustering,
            "connected_components": self.connected_components,
            "overall_quality_score": self.overall_quality_score,
            "validation_status": self.validation_status,
            "validation_errors": self.validation_errors_list,
            "source_documents": self.source_documents_list,
            "source_entities": self.source_entities_list,
            "source_relationships": self.source_relationships_list,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "is_validated": self.is_validated,
            "has_validation_errors": self.has_validation_errors,
            "is_high_quality": self.is_high_quality,
            "is_dense": self.is_dense,
            "is_sparse": self.is_sparse,
            "is_connected": self.is_connected
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"GraphStructure(id='{self.graph_id}', name='{self.graph_name}', nodes={self.node_count}, edges={self.edge_count})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"GraphStructure(graph_id='{self.graph_id}', graph_name='{self.graph_name}', graph_type='{self.graph_type}', node_count={self.node_count}, edge_count={self.edge_count}, quality={self.overall_quality_score})"
