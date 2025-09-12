"""
Embedding Model
==============

Pydantic model for vector embedding operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, ConfigDict
from src.engine.models.base_model import EngineBaseModel


class Embedding(EngineBaseModel):
    """
    Embedding Model - Pure Async Implementation
    
    Represents vector embeddings for AI RAG operations.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    # Primary Identification
    embedding_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique embedding identifier")
    document_id: str = Field(..., description="Associated document ID")
    
    # Vector Data
    vector_data: str = Field(..., description="Vector data (base64 encoded or JSON)")
    vector_dimensions: int = Field(..., description="Number of vector dimensions")
    vector_type: str = Field(default="float32", description="Vector data type")
    
    # Embedding Model Information
    embedding_model: str = Field(..., description="Embedding model name/version")
    model_provider: Optional[str] = Field(None, description="Model provider (e.g., OpenAI, HuggingFace)")
    model_parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    
    # Generation Information
    generation_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Generation timestamp")
    generation_duration_ms: Optional[float] = Field(None, description="Generation duration in milliseconds")
    generation_cost: Optional[float] = Field(None, description="Generation cost in credits/tokens")
    
    # Quality and Performance
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score (0.0-1.0)")
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Similarity threshold")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    
    # Metadata and Context
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Embedding metadata")
    context: Optional[str] = Field(None, description="Context information")
    tags: List[str] = Field(default_factory=list, description="Embedding tags")
    
    # Storage Information
    storage_location: Optional[str] = Field(None, description="Storage location identifier")
    storage_format: str = Field(default="base64", description="Storage format")
    compression_ratio: Optional[float] = Field(None, description="Compression ratio")
    
    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),  # Disable protected namespace warnings for Pydantic v2
        arbitrary_types_allowed=True,
        validate_assignment=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    )
    
    # Validators
    @validator('vector_type')
    def validate_vector_type(cls, v):
        """Validate vector type"""
        valid_types = ['float32', 'float64', 'int32', 'int64', 'uint8']
        if v not in valid_types:
            raise ValueError(f'Vector type must be one of: {valid_types}')
        return v
    
    @validator('storage_format')
    def validate_storage_format(cls, v):
        """Validate storage format"""
        valid_formats = ['base64', 'json', 'binary', 'hex']
        if v not in valid_formats:
            raise ValueError(f'Storage format must be one of: {valid_formats}')
        return v
    
    @validator('quality_score', 'similarity_threshold', 'confidence_score')
    def validate_score_fields(cls, v):
        """Validate score fields"""
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    @validator('vector_dimensions')
    def validate_vector_dimensions(cls, v):
        """Validate vector dimensions"""
        if v <= 0:
            raise ValueError('Vector dimensions must be positive')
        if v > 100000:  # Reasonable upper limit
            raise ValueError('Vector dimensions too large')
        return v
    
    # Async methods for database operations
    async def save_to_database(self) -> bool:
        """Save the embedding to database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def update_in_database(self) -> bool:
        """Update the embedding in database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def delete_from_database(self) -> bool:
        """Delete the embedding from database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    # Business logic methods
    def get_vector_size_bytes(self) -> int:
        """Calculate vector size in bytes"""
        if self.vector_type == "float32":
            return self.vector_dimensions * 4
        elif self.vector_type == "float64":
            return self.vector_dimensions * 8
        elif self.vector_type == "int32":
            return self.vector_dimensions * 4
        elif self.vector_type == "int64":
            return self.vector_dimensions * 8
        elif self.vector_type == "uint8":
            return self.vector_dimensions
        else:
            return self.vector_dimensions * 4  # Default to float32
    
    def is_high_quality(self) -> bool:
        """Check if embedding is high quality"""
        if self.quality_score is not None:
            return self.quality_score >= 0.8
        return False
    
    def is_high_confidence(self) -> bool:
        """Check if embedding has high confidence"""
        if self.confidence_score is not None:
            return self.confidence_score >= 0.9
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.embedding_model,
            "provider": self.model_provider,
            "parameters": self.model_parameters,
            "dimensions": self.vector_dimensions,
            "vector_type": self.vector_type
        }
    
    def get_generation_info(self) -> Dict[str, Any]:
        """Get generation information"""
        return {
            "timestamp": self.generation_timestamp,
            "duration_ms": self.generation_duration_ms,
            "cost": self.generation_cost,
            "quality_score": self.quality_score,
            "confidence_score": self.confidence_score
        }
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information"""
        return {
            "location": self.storage_location,
            "format": self.storage_format,
            "compression_ratio": self.compression_ratio,
            "size_bytes": self.get_vector_size_bytes(),
            "dimensions": self.vector_dimensions
        }
    
    def add_tag(self, tag: str):
        """Add a tag to the embedding"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from the embedding"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if embedding has a specific tag"""
        return tag in self.tags
    
    def get_tags_by_category(self, category: str) -> List[str]:
        """Get tags by category (e.g., 'domain', 'type', 'quality')"""
        return [tag for tag in self.tags if tag.startswith(f"{category}:")]
    
    def update_metadata(self, key: str, value: Any):
        """Update metadata field"""
        self.metadata[key] = value
        self.updated_at = datetime.now().isoformat()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata field"""
        return self.metadata.get(key, default)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Embedding':
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Embedding':
        """Create model from JSON string"""
        data = json.loads(json_str)
        return cls(**data)
    
    @classmethod
    def create_embedding(cls, document_id: str, vector_data: str, vector_dimensions: int, 
                        embedding_model: str, **kwargs) -> 'Embedding':
        """Create a new embedding with required fields"""
        return cls(
            document_id=document_id,
            vector_data=vector_data,
            vector_dimensions=vector_dimensions,
            embedding_model=embedding_model,
            **kwargs
        )
    
    @classmethod
    def create_high_quality_embedding(cls, document_id: str, vector_data: str, 
                                    vector_dimensions: int, embedding_model: str, 
                                    quality_score: float = 0.9, **kwargs) -> 'Embedding':
        """Create a high-quality embedding"""
        return cls(
            document_id=document_id,
            vector_data=vector_data,
            vector_dimensions=vector_dimensions,
            embedding_model=embedding_model,
            quality_score=quality_score,
            **kwargs
        )
