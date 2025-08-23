"""
Document Model
=============

Pydantic model for document processing operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from src.engine.models.base_model import BaseModel as EngineBaseModel


class Document(EngineBaseModel):
    """
    Document Model - Pure Async Implementation
    
    Represents document processing and storage for AI RAG operations.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    # Primary Identification
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique document identifier")
    registry_id: str = Field(..., description="Associated AI RAG registry ID")
    file_path: str = Field(..., description="File path")
    file_type: str = Field(..., description="File type")
    
    # Document Properties
    file_size: Optional[int] = Field(None, description="File size in bytes")
    content_hash: Optional[str] = Field(None, description="Content hash for integrity")
    processing_status: str = Field(default="pending", description="Processing status")
    
    # Processing Information
    processing_start_time: Optional[str] = Field(None, description="Processing start timestamp")
    processing_end_time: Optional[str] = Field(None, description="Processing end timestamp")
    processing_duration_ms: Optional[float] = Field(None, description="Processing duration in milliseconds")
    
    # Content Information
    content_summary: Optional[str] = Field(None, description="Content summary")
    extracted_text: Optional[str] = Field(None, description="Extracted text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
    # Quality Metrics
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score (0.0-1.0)")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    
    # Processing Configuration
    processor_config: Dict[str, Any] = Field(default_factory=dict, description="Processor configuration")
    extraction_config: Dict[str, Any] = Field(default_factory=dict, description="Extraction configuration")
    
    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
        validate_assignment = True
        arbitrary_types_allowed = True
    
    # Validators
    @validator('processing_status')
    def validate_processing_status(cls, v):
        """Validate processing status"""
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Processing status must be one of: {valid_statuses}')
        return v
    
    @validator('file_type')
    def validate_file_type(cls, v):
        """Validate file type"""
        valid_types = [
            'pdf', 'docx', 'txt', 'jpg', 'png', 'gif', 'py', 'js', 'java', 
            'xlsx', 'csv', 'dwg', 'step', 'stl', 'graphml', 'gml', 'json', 'yaml', 'xml'
        ]
        if v.lower() not in valid_types:
            raise ValueError(f'File type must be one of: {valid_types}')
        return v.lower()
    
    @validator('quality_score', 'confidence_score')
    def validate_score_fields(cls, v):
        """Validate score fields"""
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v
    
    # Async methods for database operations
    async def save_to_database(self) -> bool:
        """Save the document to database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def update_in_database(self) -> bool:
        """Update the document in database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    async def delete_from_database(self) -> bool:
        """Delete the document from database - to be implemented with repository"""
        # This will be implemented when we create the repository
        raise NotImplementedError("Repository not yet implemented")
    
    # Business logic methods
    def is_processed(self) -> bool:
        """Check if the document is processed"""
        return self.processing_status == "completed"
    
    def is_failed(self) -> bool:
        """Check if the document processing failed"""
        return self.processing_status == "failed"
    
    def is_pending(self) -> bool:
        """Check if the document is pending processing"""
        return self.processing_status == "pending"
    
    def is_processing(self) -> bool:
        """Check if the document is currently being processed"""
        return self.processing_status == "processing"
    
    def get_processing_time(self) -> Optional[float]:
        """Get processing time in milliseconds"""
        if self.processing_start_time and self.processing_end_time:
            start = datetime.fromisoformat(self.processing_start_time)
            end = datetime.fromisoformat(self.processing_end_time)
            return (end - start).total_seconds() * 1000
        return None
    
    def get_file_extension(self) -> str:
        """Get file extension from file path"""
        return self.file_path.split('.')[-1].lower()
    
    def get_file_name(self) -> str:
        """Get file name from file path"""
        return self.file_path.split('/')[-1]
    
    def get_directory_path(self) -> str:
        """Get directory path from file path"""
        return '/'.join(self.file_path.split('/')[:-1])
    
    def is_text_based(self) -> bool:
        """Check if the document is text-based"""
        text_types = ['txt', 'py', 'js', 'java', 'json', 'yaml', 'xml']
        return self.file_type in text_types
    
    def is_image_based(self) -> bool:
        """Check if the document is image-based"""
        image_types = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']
        return self.file_type in image_types
    
    def is_document_based(self) -> bool:
        """Check if the document is document-based"""
        document_types = ['pdf', 'docx', 'doc', 'rtf']
        return self.file_type in document_types
    
    def is_spreadsheet_based(self) -> bool:
        """Check if the document is spreadsheet-based"""
        spreadsheet_types = ['xlsx', 'xls', 'csv', 'ods']
        return self.file_type in spreadsheet_types
    
    def is_cad_based(self) -> bool:
        """Check if the document is CAD-based"""
        cad_types = ['dwg', 'step', 'stp', 'stl', 'iges', 'iges']
        return self.file_type in cad_types
    
    def get_processor_type(self) -> str:
        """Get the appropriate processor type for this document"""
        if self.is_text_based():
            return "TextProcessor"
        elif self.is_image_based():
            return "ImageProcessor"
        elif self.is_document_based():
            return "DocumentProcessor"
        elif self.is_spreadsheet_based():
            return "SpreadsheetProcessor"
        elif self.is_cad_based():
            return "CADProcessor"
        else:
            return "GenericProcessor"
    
    def update_processing_status(self, status: str, **kwargs):
        """Update processing status and related fields"""
        self.processing_status = status
        self.updated_at = datetime.now().isoformat()
        
        if status == "processing" and not self.processing_start_time:
            self.processing_start_time = datetime.now().isoformat()
        elif status in ["completed", "failed", "cancelled"] and not self.processing_end_time:
            self.processing_end_time = datetime.now().isoformat()
            if self.processing_start_time:
                processing_time = self.get_processing_time()
                if processing_time:
                    self.processing_duration_ms = processing_time
        
        # Update additional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_validation_error(self, error: str):
        """Add a validation error"""
        if error not in self.validation_errors:
            self.validation_errors.append(error)
    
    def clear_validation_errors(self):
        """Clear all validation errors"""
        self.validation_errors.clear()
    
    def has_validation_errors(self) -> bool:
        """Check if there are validation errors"""
        return len(self.validation_errors) > 0
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        return {
            "has_errors": self.has_validation_errors(),
            "error_count": len(self.validation_errors),
            "errors": self.validation_errors.copy(),
            "quality_score": self.quality_score,
            "confidence_score": self.confidence_score
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
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Document':
        """Create model from JSON string"""
        data = json.loads(json_str)
        return cls(**data)
    
    @classmethod
    def create_document(cls, registry_id: str, file_path: str, file_type: str, **kwargs) -> 'Document':
        """Create a new document with required fields"""
        return cls(
            registry_id=registry_id,
            file_path=file_path,
            file_type=file_type,
            **kwargs
        )
    
    @classmethod
    def create_pending_document(cls, registry_id: str, file_path: str, file_type: str, **kwargs) -> 'Document':
        """Create a new document in pending status"""
        return cls(
            registry_id=registry_id,
            file_path=file_path,
            file_type=file_type,
            processing_status="pending",
            **kwargs
        )
