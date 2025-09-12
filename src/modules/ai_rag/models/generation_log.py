"""
Generation Log Model
===================

Pydantic model for AI generation log operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from src.engine.models.base_model import EngineBaseModel


class GenerationLog(EngineBaseModel):
    """
    Generation Log Model - Pure Async Implementation
    
    Represents AI generation logs for AI RAG operations.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    # Primary Identification
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique log identifier")
    registry_id: str = Field(..., description="Associated AI RAG registry ID")
    session_id: Optional[str] = Field(None, description="Associated retrieval session ID")
    
    # Generation Information
    generation_type: str = Field(..., description="Generation type")
    generation_model: str = Field(..., description="AI model used for generation")
    generation_prompt: str = Field(..., description="Generation prompt")
    generated_content: str = Field(..., description="Generated content")
    
    # Generation Configuration
    model_parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    generation_config: Dict[str, Any] = Field(default_factory=dict, description="Generation configuration")
    context_documents: List[str] = Field(default_factory=list, description="Context document IDs")
    
    # Performance Metrics
    generation_time_ms: Optional[float] = Field(None, description="Generation time in milliseconds")
    token_count: Optional[int] = Field(None, description="Number of tokens generated")
    cost_credits: Optional[float] = Field(None, description="Cost in credits/tokens")
    
    # Quality Assessment
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score (0.0-1.0)")
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance score (0.0-1.0)")
    coherence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Coherence score (0.0-1.0)")
    accuracy_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Accuracy score (0.0-1.0)")
    
    # User Feedback
    user_rating: Optional[int] = Field(None, ge=1, le=5, description="User rating (1-5)")
    user_feedback: Optional[str] = Field(None, description="User feedback text")
    feedback_timestamp: Optional[str] = Field(None, description="Feedback timestamp")
    
    # Generation Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Generation metadata")
    tags: List[str] = Field(default_factory=list, description="Generation tags")
    flags: List[str] = Field(default_factory=list, description="Generation flags")
    
    # Error Handling
    error_message: Optional[str] = Field(None, description="Error message if generation failed")
    error_code: Optional[str] = Field(None, description="Error code if generation failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    
    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    generated_at: Optional[str] = Field(None, description="Generation timestamp")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
        validate_assignment = True
        arbitrary_types_allowed = True
    
    # Validators
    @validator('generation_type')
    def validate_generation_type(cls, v):
        """Validate generation type"""
        valid_types = ['text', 'image', 'code', 'summary', 'translation', 'analysis', 'creative']
        if v not in valid_types:
            raise ValueError(f'Generation type must be one of: {valid_types}')
        return v
    
    @validator('quality_score', 'relevance_score', 'coherence_score', 'accuracy_score')
    def validate_score_fields(cls, v):
        """Validate score fields"""
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    @validator('user_rating')
    def validate_user_rating(cls, v):
        """Validate user rating"""
        if v is not None and not 1 <= v <= 5:
            raise ValueError('User rating must be between 1 and 5')
        return v
    
    @validator('token_count')
    def validate_token_count(cls, v):
        """Validate token count"""
        if v is not None and v < 0:
            raise ValueError('Token count must be non-negative')
        return v
    
    @validator('retry_count')
    def validate_retry_count(cls, v):
        """Validate retry count"""
        if v < 0:
            raise ValueError('Retry count must be non-negative')
        return v
    
    # Async methods for database operations
    async def save_to_database(self) -> bool:
        """Save the log to database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def update_in_database(self) -> bool:
        """Update the log in database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def delete_from_database(self) -> bool:
        """Delete the log from database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    # Business logic methods
    def is_successful(self) -> bool:
        """Check if generation was successful"""
        return self.error_message is None and self.error_code is None
    
    def is_failed(self) -> bool:
        """Check if generation failed"""
        return self.error_message is not None or self.error_code is not None
    
    def has_user_feedback(self) -> bool:
        """Check if user feedback exists"""
        return self.user_rating is not None or self.user_feedback is not None
    
    def is_high_quality(self) -> bool:
        """Check if generation has high quality"""
        if self.quality_score is not None:
            return self.quality_score >= 0.8
        return False
    
    def is_highly_relevant(self) -> bool:
        """Check if generation is highly relevant"""
        if self.relevance_score is not None:
            return self.relevance_score >= 0.8
        return False
    
    def is_coherent(self) -> bool:
        """Check if generation is coherent"""
        if self.coherence_score is not None:
            return self.coherence_score >= 0.7
        return False
    
    def is_accurate(self) -> bool:
        """Check if generation is accurate"""
        if self.accuracy_score is not None:
            return self.accuracy_score >= 0.8
        return False
    
    def get_overall_score(self) -> Optional[float]:
        """Calculate overall score from component scores"""
        scores = []
        if self.quality_score is not None:
            scores.append(self.quality_score)
        if self.relevance_score is not None:
            scores.append(self.relevance_score)
        if self.coherence_score is not None:
            scores.append(self.coherence_score)
        if self.accuracy_score is not None:
            scores.append(self.accuracy_score)
        
        if scores:
            return sum(scores) / len(scores)
        return None
    
    def add_context_document(self, document_id: str):
        """Add a context document to the generation"""
        if document_id not in self.context_documents:
            self.context_documents.append(document_id)
    
    def remove_context_document(self, document_id: str):
        """Remove a context document from the generation"""
        if document_id in self.context_documents:
            self.context_documents.remove(document_id)
    
    def add_tag(self, tag: str):
        """Add a tag to the generation"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from the generation"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if generation has a specific tag"""
        return tag in self.tags
    
    def add_flag(self, flag: str):
        """Add a flag to the generation"""
        if flag not in self.flags:
            self.flags.append(flag)
    
    def remove_flag(self, flag: str):
        """Remove a flag from the generation"""
        if flag in self.flags:
            self.flags.remove(flag)
    
    def has_flag(self, flag: str) -> bool:
        """Check if generation has a specific flag"""
        return flag in self.flags
    
    def update_metadata(self, key: str, value: Any):
        """Update metadata field"""
        self.metadata[key] = value
        self.updated_at = datetime.now().isoformat()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata field"""
        return self.metadata.get(key, default)
    
    def set_error(self, error_message: str, error_code: Optional[str] = None):
        """Set error information"""
        self.error_message = error_message
        self.error_code = error_code
        self.updated_at = datetime.now().isoformat()
    
    def clear_error(self):
        """Clear error information"""
        self.error_message = None
        self.error_code = None
        self.updated_at = datetime.now().isoformat()
    
    def increment_retry_count(self):
        """Increment retry count"""
        self.retry_count += 1
        self.updated_at = datetime.now().isoformat()
    
    def add_user_feedback(self, rating: int, feedback: Optional[str] = None):
        """Add user feedback"""
        self.user_rating = rating
        if feedback:
            self.user_feedback = feedback
        self.feedback_timestamp = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get a summary of the generation"""
        return {
            "log_id": self.log_id,
            "generation_type": self.generation_type,
            "generation_model": self.generation_model,
            "is_successful": self.is_successful(),
            "generation_time_ms": self.generation_time_ms,
            "token_count": self.token_count,
            "overall_score": self.get_overall_score(),
            "user_rating": self.user_rating,
            "context_document_count": len(self.context_documents),
            "tags": self.tags.copy(),
            "flags": self.flags.copy()
        }
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'GenerationLog':
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'GenerationLog':
        """Create model from JSON string"""
        data = json.loads(json_str)
        return cls(**data)
    
    @classmethod
    def create_generation_log(cls, registry_id: str, generation_type: str, 
                            generation_model: str, generation_prompt: str, 
                            generated_content: str, **kwargs) -> 'GenerationLog':
        """Create a new generation log with required fields"""
        return cls(
            registry_id=registry_id,
            generation_type=generation_type,
            generation_model=generation_model,
            generation_prompt=generation_prompt,
            generated_content=generated_content,
            **kwargs
        )
    
    @classmethod
    def create_text_generation_log(cls, registry_id: str, generation_model: str, 
                                 generation_prompt: str, generated_content: str, **kwargs) -> 'GenerationLog':
        """Create a text generation log"""
        return cls(
            registry_id=registry_id,
            generation_type="text",
            generation_model=generation_model,
            generation_prompt=generation_prompt,
            generated_content=generated_content,
            **kwargs
        )
    
    @classmethod
    def create_error_log(cls, registry_id: str, generation_type: str, 
                        generation_model: str, generation_prompt: str, 
                        error_message: str, error_code: Optional[str] = None, **kwargs) -> 'GenerationLog':
        """Create an error generation log"""
        return cls(
            registry_id=registry_id,
            generation_type=generation_type,
            generation_model=generation_model,
            generation_prompt=generation_prompt,
            generated_content="",  # Empty content for error logs
            error_message=error_message,
            error_code=error_code,
            **kwargs
        )
