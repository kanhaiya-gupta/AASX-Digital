"""
Retrieval Session Model
======================

Pydantic model for RAG query session operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from src.engine.models.base_model import EngineBaseModel


class RetrievalSession(EngineBaseModel):
    """
    Retrieval Session Model - Pure Async Implementation
    
    Represents RAG query sessions for AI RAG operations.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    # Primary Identification
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique session identifier")
    registry_id: str = Field(..., description="Associated AI RAG registry ID")
    user_id: str = Field(..., description="User ID who initiated the session")
    
    # Session Information
    session_name: Optional[str] = Field(None, description="Session name")
    session_type: str = Field(default="query", description="Session type")
    session_status: str = Field(default="active", description="Session status")
    
    # Query Information
    query_text: str = Field(..., description="Query text")
    query_type: str = Field(default="general", description="Query type")
    query_parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    
    # Retrieval Configuration
    retrieval_strategy: str = Field(default="semantic", description="Retrieval strategy")
    max_results: int = Field(default=10, description="Maximum number of results")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")
    
    # Results and Performance
    retrieved_documents: List[str] = Field(default_factory=list, description="Retrieved document IDs")
    result_count: int = Field(default=0, description="Number of results retrieved")
    retrieval_time_ms: Optional[float] = Field(None, description="Retrieval time in milliseconds")
    
    # Quality and Feedback
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance score")
    user_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="User satisfaction (1-5)")
    feedback_notes: Optional[str] = Field(None, description="User feedback notes")
    
    # Session Context
    context_history: List[Dict[str, Any]] = Field(default_factory=list, description="Session context history")
    conversation_flow: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation flow")
    
    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    started_at: Optional[str] = Field(None, description="Session start timestamp")
    completed_at: Optional[str] = Field(None, description="Session completion timestamp")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
        validate_assignment = True
        arbitrary_types_allowed = True
    
    # Validators
    @validator('session_type')
    def validate_session_type(cls, v):
        """Validate session type"""
        valid_types = ['query', 'conversation', 'analysis', 'exploration', 'comparison']
        if v not in valid_types:
            raise ValueError(f'Session type must be one of: {valid_types}')
        return v
    
    @validator('session_status')
    def validate_session_status(cls, v):
        """Validate session status"""
        valid_statuses = ['active', 'paused', 'completed', 'cancelled', 'expired']
        if v not in valid_statuses:
            raise ValueError(f'Session status must be one of: {valid_statuses}')
        return v
    
    @validator('query_type')
    def validate_query_type(cls, v):
        """Validate query type"""
        valid_types = ['general', 'specific', 'comparative', 'analytical', 'creative']
        if v not in valid_types:
            raise ValueError(f'Query type must be one of: {valid_types}')
        return v
    
    @validator('retrieval_strategy')
    def validate_retrieval_strategy(cls, v):
        """Validate retrieval strategy"""
        valid_strategies = ['semantic', 'keyword', 'hybrid', 'graph', 'multi_modal']
        if v not in valid_strategies:
            raise ValueError(f'Retrieval strategy must be one of: {valid_strategies}')
        return v
    
    @validator('max_results')
    def validate_max_results(cls, v):
        """Validate max results"""
        if v <= 0 or v > 1000:
            raise ValueError('Max results must be between 1 and 1000')
        return v
    
    @validator('similarity_threshold')
    def validate_similarity_threshold(cls, v):
        """Validate similarity threshold"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Similarity threshold must be between 0.0 and 1.0')
        return v
    
    @validator('relevance_score')
    def validate_relevance_score(cls, v):
        """Validate relevance score"""
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Relevance score must be between 0.0 and 1.0')
        return v
    
    @validator('user_satisfaction')
    def validate_user_satisfaction(cls, v):
        """Validate user satisfaction"""
        if v is not None and not 1 <= v <= 5:
            raise ValueError('User satisfaction must be between 1 and 5')
        return v
    
    # Async methods for database operations
    async def save_to_database(self) -> bool:
        """Save the session to database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def update_in_database(self) -> bool:
        """Update the session in database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def delete_from_database(self) -> bool:
        """Delete the session from database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    # Business logic methods
    def is_active(self) -> bool:
        """Check if the session is active"""
        return self.session_status == "active"
    
    def is_completed(self) -> bool:
        """Check if the session is completed"""
        return self.session_status == "completed"
    
    def is_cancelled(self) -> bool:
        """Check if the session is cancelled"""
        return self.session_status == "cancelled"
    
    def get_session_duration(self) -> Optional[float]:
        """Get session duration in seconds"""
        if self.started_at and self.completed_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            return (end - start).total_seconds()
        return None
    
    def add_retrieved_document(self, document_id: str):
        """Add a retrieved document to the session"""
        if document_id not in self.retrieved_documents:
            self.retrieved_documents.append(document_id)
            self.result_count = len(self.retrieved_documents)
    
    def remove_retrieved_document(self, document_id: str):
        """Remove a retrieved document from the session"""
        if document_id in self.retrieved_documents:
            self.retrieved_documents.remove(document_id)
            self.result_count = len(self.retrieved_documents)
    
    def add_context_entry(self, entry: Dict[str, Any]):
        """Add a context entry to the session"""
        self.context_history.append({
            "timestamp": datetime.now().isoformat(),
            "entry": entry
        })
    
    def add_conversation_turn(self, turn: Dict[str, Any]):
        """Add a conversation turn to the session"""
        self.conversation_flow.append({
            "timestamp": datetime.now().isoformat(),
            "turn": turn
        })
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the session context"""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type,
            "query_text": self.query_text,
            "result_count": self.result_count,
            "context_entries": len(self.context_history),
            "conversation_turns": len(self.conversation_flow),
            "duration_seconds": self.get_session_duration()
        }
    
    def start_session(self):
        """Start the session"""
        if not self.started_at:
            self.started_at = datetime.now().isoformat()
        self.session_status = "active"
        self.updated_at = datetime.now().isoformat()
    
    def pause_session(self):
        """Pause the session"""
        self.session_status = "paused"
        self.updated_at = datetime.now().isoformat()
    
    def complete_session(self):
        """Complete the session"""
        self.session_status = "completed"
        if not self.completed_at:
            self.completed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def cancel_session(self):
        """Cancel the session"""
        self.session_status = "cancelled"
        if not self.completed_at:
            self.completed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def update_retrieval_performance(self, retrieval_time_ms: float, relevance_score: Optional[float] = None):
        """Update retrieval performance metrics"""
        self.retrieval_time_ms = retrieval_time_ms
        if relevance_score is not None:
            self.relevance_score = relevance_score
        self.updated_at = datetime.now().isoformat()
    
    def add_user_feedback(self, satisfaction: int, notes: Optional[str] = None):
        """Add user feedback to the session"""
        self.user_satisfaction = satisfaction
        if notes:
            self.feedback_notes = notes
        self.updated_at = datetime.now().isoformat()
    
    def is_high_relevance(self) -> bool:
        """Check if the session has high relevance"""
        if self.relevance_score is not None:
            return self.relevance_score >= 0.8
        return False
    
    def is_user_satisfied(self) -> bool:
        """Check if the user is satisfied"""
        if self.user_satisfaction is not None:
            return self.user_satisfaction >= 4
        return False
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'RetrievalSession':
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RetrievalSession':
        """Create model from JSON string"""
        data = json.loads(json_str)
        return cls(**data)
    
    @classmethod
    def create_session(cls, registry_id: str, user_id: str, query_text: str, **kwargs) -> 'RetrievalSession':
        """Create a new retrieval session with required fields"""
        return cls(
            registry_id=registry_id,
            user_id=user_id,
            query_text=query_text,
            **kwargs
        )
    
    @classmethod
    def create_conversation_session(cls, registry_id: str, user_id: str, query_text: str, **kwargs) -> 'RetrievalSession':
        """Create a new conversation session"""
        return cls(
            registry_id=registry_id,
            user_id=user_id,
            query_text=query_text,
            session_type="conversation",
            **kwargs
        )
