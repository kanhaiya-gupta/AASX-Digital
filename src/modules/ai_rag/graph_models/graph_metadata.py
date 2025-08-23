"""
AI RAG Graph Metadata Model
===========================

Represents graph metadata and versioning information.
"""

import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator
from src.engine.models.base_model import BaseModel as EngineBaseModel


class GraphMetadata(EngineBaseModel):
    """
    Graph Metadata Model
    
    Represents metadata and versioning information for graphs,
    separate from the actual graph structure.
    """
    
    # Core Identification
    metadata_id: str = Field(..., description="Unique identifier for the metadata record")
    graph_id: str = Field(..., description="Reference to the graph")
    
    # Version Information
    version: str = Field(default="1.0.0", description="Graph version string")
    version_major: int = Field(default=1, ge=0, description="Major version number")
    version_minor: int = Field(default=0, ge=0, description="Minor version number")
    version_patch: int = Field(default=0, ge=0, description="Patch version number")
    
    # Graph Information
    graph_name: str = Field(..., description="Human-readable name for the graph")
    graph_type: str = Field(..., description="Type of graph: entity_relationship, knowledge_graph, dependency_graph")
    graph_category: str = Field(..., description="Category: technical, business, operational")
    graph_description: Optional[str] = Field(None, description="Detailed description of the graph")
    
    # Source Information
    source_documents: str = Field(default="[]", description="JSON array of source document IDs")
    source_entities: str = Field(default="[]", description="JSON array of source entities")
    source_relationships: str = Field(default="[]", description="JSON array of source relationships")
    
    # Processing Information
    processing_status: str = Field(default="processing", description="Status: processing, completed, failed")
    processing_start_time: Optional[str] = Field(None, description="Processing start timestamp")
    processing_end_time: Optional[str] = Field(None, description="Processing end timestamp")
    processing_duration_ms: Optional[int] = Field(None, ge=0, description="Processing duration in milliseconds")
    
    # Quality Metrics
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall quality score")
    validation_status: str = Field(default="pending", description="Status: pending, validated, failed")
    validation_errors: str = Field(default="[]", description="JSON array of validation errors")
    
    # File Storage References
    output_directory: str = Field(..., description="Path to output directory containing graph files")
    graph_files: str = Field(default="[]", description="JSON array of generated graph files with paths")
    file_formats: str = Field(default="[]", description="JSON array of available export formats")
    
    # Integration References
    kg_neo4j_graph_id: Optional[str] = Field(None, description="Reference to KG Neo4j if transferred")
    aasx_integration_id: Optional[str] = Field(None, description="Reference to AASX source")
    twin_registry_id: Optional[str] = Field(None, description="Reference to Twin Registry source")
    
    # Tracing & Audit
    created_by: str = Field(..., description="User ID who created the graph")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the graph")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    dept_id: Optional[str] = Field(None, description="Department ID for traceability")
    org_id: Optional[str] = Field(None, description="Organization ID for traceability")
    
    # Performance Metrics
    generation_time_ms: Optional[int] = Field(None, ge=0, description="Graph generation time in milliseconds")
    memory_usage_mb: Optional[float] = Field(None, ge=0.0, description="Memory usage during generation in MB")
    cpu_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="CPU usage during generation in percent")
    
    # Change Tracking
    change_history: str = Field(default="[]", description="JSON array of change history entries")
    parent_version: Optional[str] = Field(None, description="Parent version ID if this is a derived version")
    change_summary: Optional[str] = Field(None, description="Summary of changes from parent version")
    
    # Computed Properties
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
    def graph_files_list(self) -> List[Dict[str, Any]]:
        """Get graph files as a Python list."""
        try:
            return json.loads(self.graph_files) if self.graph_files else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def file_formats_list(self) -> List[str]:
        """Get file formats as a Python list."""
        try:
            return json.loads(self.file_formats) if self.file_formats else []
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
    def change_history_list(self) -> List[Dict[str, Any]]:
        """Get change history as a Python list."""
        try:
            return json.loads(self.change_history) if self.change_history else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def is_processing(self) -> bool:
        """Check if graph is currently processing."""
        return self.processing_status == "processing"
    
    @property
    def is_completed(self) -> bool:
        """Check if graph processing is completed."""
        return self.processing_status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """Check if graph processing failed."""
        return self.processing_status == "failed"
    
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
        return self.quality_score >= 0.8
    
    @property
    def version_tuple(self) -> tuple:
        """Get version as a tuple for comparison."""
        return (self.version_major, self.version_minor, self.version_patch)
    
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
    
    @validator('processing_status')
    def validate_processing_status(cls, v):
        """Validate processing status."""
        allowed_statuses = ['processing', 'completed', 'failed']
        if v not in allowed_statuses:
            raise ValueError(f'processing_status must be one of: {allowed_statuses}')
        return v
    
    @validator('validation_status')
    def validate_validation_status(cls, v):
        """Validate validation status."""
        allowed_statuses = ['pending', 'validated', 'failed']
        if v not in allowed_statuses:
            raise ValueError(f'validation_status must be one of: {allowed_statuses}')
        return v
    
    @validator('quality_score')
    def validate_quality_score(cls, v):
        """Validate quality score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('quality_score must be between 0.0 and 1.0')
        return v
    
    @validator('version')
    def validate_version_format(cls, v):
        """Validate version string format."""
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('version must be in format X.Y.Z')
        return v
    
    @root_validator
    def validate_version_consistency(cls, values):
        """Validate version number consistency."""
        version = values.get('version')
        major = values.get('version_major')
        minor = values.get('version_minor')
        patch = values.get('version_patch')
        
        if version and major is not None and minor is not None and patch is not None:
            expected_version = f"{major}.{minor}.{patch}"
            if version != expected_version:
                raise ValueError(f'version {version} does not match version numbers {major}.{minor}.{patch}')
        
        return values
    
    @root_validator
    def validate_processing_times(cls, values):
        """Validate processing time consistency."""
        start_time = values.get('processing_start_time')
        end_time = values.get('processing_end_time')
        duration = values.get('processing_duration_ms')
        
        if start_time and end_time and duration:
            # Basic validation that duration is reasonable
            if duration < 0:
                raise ValueError('processing_duration_ms cannot be negative')
        
        return values
    
    # Business Logic Methods
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
    
    def add_graph_file(self, file_path: str, file_format: str, file_size: Optional[int] = None) -> None:
        """Add a generated graph file."""
        files = self.graph_files_list
        file_info = {
            "path": file_path,
            "format": file_format,
            "size_bytes": file_size,
            "added_at": datetime.now().isoformat()
        }
        files.append(file_info)
        self.graph_files = json.dumps(files)
        
        # Update file formats list
        formats = self.file_formats_list
        if file_format not in formats:
            formats.append(file_format)
            self.file_formats = json.dumps(formats)
        
        self.updated_at = datetime.now().isoformat()
    
    def add_validation_error(self, error: str) -> None:
        """Add a validation error."""
        errors = self.validation_errors_list
        errors.append(error)
        self.validation_errors = json.dumps(errors)
        self.validation_status = "failed"
        self.updated_at = datetime.now().isoformat()
    
    def mark_processing_complete(self, duration_ms: Optional[int] = None) -> None:
        """Mark processing as complete."""
        self.processing_status = "completed"
        self.processing_end_time = datetime.now().isoformat()
        if duration_ms is not None:
            self.processing_duration_ms = duration_ms
        elif self.processing_start_time:
            # Calculate duration if not provided
            start = datetime.fromisoformat(self.processing_start_time)
            end = datetime.now()
            self.processing_duration_ms = int((end - start).total_seconds() * 1000)
        
        self.updated_at = datetime.now().isoformat()
    
    def mark_processing_failed(self, error_message: str) -> None:
        """Mark processing as failed."""
        self.processing_status = "failed"
        self.processing_end_time = datetime.now().isoformat()
        self.add_validation_error(error_message)
        self.updated_at = datetime.now().isoformat()
    
    def mark_validated(self) -> None:
        """Mark graph as validated."""
        self.validation_status = "validated"
        self.updated_at = datetime.now().isoformat()
    
    def update_performance_metrics(self, generation_time_ms: int, memory_mb: float, cpu_percent: float) -> None:
        """Update performance metrics."""
        self.generation_time_ms = generation_time_ms
        self.memory_usage_mb = memory_mb
        self.cpu_usage_percent = cpu_percent
        self.updated_at = datetime.now().isoformat()
    
    def add_change_entry(self, change_type: str, description: str, changed_by: str) -> None:
        """Add a change history entry."""
        changes = self.change_history_list
        change_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": change_type,
            "description": description,
            "changed_by": changed_by,
            "version": self.version
        }
        changes.append(change_entry)
        self.change_history = json.dumps(changes)
        self.updated_at = datetime.now().isoformat()
    
    def increment_version(self, increment_type: str = "patch") -> None:
        """Increment version number."""
        if increment_type == "major":
            self.version_major += 1
            self.version_minor = 0
            self.version_patch = 0
        elif increment_type == "minor":
            self.version_minor += 1
            self.version_patch = 0
        elif increment_type == "patch":
            self.version_patch += 1
        else:
            raise ValueError('increment_type must be major, minor, or patch')
        
        self.version = f"{self.version_major}.{self.version_minor}.{self.version_patch}"
        self.updated_at = datetime.now().isoformat()
    
    def set_parent_version(self, parent_version: str, change_summary: str) -> None:
        """Set parent version and change summary."""
        self.parent_version = parent_version
        self.change_summary = change_summary
        self.updated_at = datetime.now().isoformat()
    
    def calculate_quality_score(self) -> float:
        """Calculate quality score based on various factors."""
        score = 0.0
        
        # Processing success (40% weight)
        if self.is_completed:
            score += 0.4
        elif self.is_failed:
            score += 0.0
        else:
            score += 0.2  # Partial credit for processing
        
        # Validation status (30% weight)
        if self.is_validated:
            score += 0.3
        elif self.has_validation_errors:
            score += 0.1
        else:
            score += 0.15  # Partial credit for pending
        
        # Source information completeness (20% weight)
        if self.source_documents_list and self.source_entities_list:
            score += 0.2
        elif self.source_documents_list or self.source_entities_list:
            score += 0.1
        
        # Performance efficiency (10% weight)
        if self.generation_time_ms and self.generation_time_ms < 5000:  # Less than 5 seconds
            score += 0.1
        elif self.generation_time_ms and self.generation_time_ms < 30000:  # Less than 30 seconds
            score += 0.05
        
        self.quality_score = min(score, 1.0)
        return self.quality_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "metadata_id": self.metadata_id,
            "graph_id": self.graph_id,
            "version": self.version,
            "version_major": self.version_major,
            "version_minor": self.version_minor,
            "version_patch": self.version_patch,
            "graph_name": self.graph_name,
            "graph_type": self.graph_type,
            "graph_category": self.graph_category,
            "graph_description": self.graph_description,
            "source_documents": self.source_documents_list,
            "source_entities": self.source_entities_list,
            "source_relationships": self.source_relationships_list,
            "processing_status": self.processing_status,
            "processing_start_time": self.processing_start_time,
            "processing_end_time": self.processing_end_time,
            "processing_duration_ms": self.processing_duration_ms,
            "quality_score": self.quality_score,
            "validation_status": self.validation_status,
            "validation_errors": self.validation_errors_list,
            "output_directory": self.output_directory,
            "graph_files": self.graph_files_list,
            "file_formats": self.file_formats_list,
            "kg_neo4j_graph_id": self.kg_neo4j_graph_id,
            "aasx_integration_id": self.aasx_integration_id,
            "twin_registry_id": self.twin_registry_id,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_by": self.updated_by,
            "updated_at": self.updated_at,
            "dept_id": self.dept_id,
            "org_id": self.org_id,
            "generation_time_ms": self.generation_time_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "change_history": self.change_history_list,
            "parent_version": self.parent_version,
            "change_summary": self.change_summary,
            "is_processing": self.is_processing,
            "is_completed": self.is_completed,
            "is_failed": self.is_failed,
            "is_validated": self.is_validated,
            "has_validation_errors": self.has_validation_errors,
            "is_high_quality": self.is_high_quality,
            "version_tuple": self.version_tuple
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"GraphMetadata(id='{self.metadata_id}', graph='{self.graph_id}', version='{self.version}', status='{self.processing_status}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"GraphMetadata(metadata_id='{self.metadata_id}', graph_id='{self.graph_id}', version='{self.version}', graph_name='{self.graph_name}', processing_status='{self.processing_status}', quality_score={self.quality_score})"
