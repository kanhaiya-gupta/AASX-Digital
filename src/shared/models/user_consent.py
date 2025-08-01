#!/usr/bin/env python3
"""
User Consent Model
=================

Data model for user consent tracking in federated learning scenarios.
Handles consent management, privacy levels, and compliance tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import json
import uuid

from .base_model import BaseModel


@dataclass(kw_only=True)
class UserConsent(BaseModel):
    """
    User Consent Model for Federated Learning
    
    Tracks user consent for federated learning participation,
    ensuring compliance with privacy regulations and data protection laws.
    """
    
    # Required fields (no defaults)
    user_id: str
    
    # Primary identifier
    consent_id: str = field(default_factory=lambda: f"consent_{uuid.uuid4().hex[:8]}")
    
    # Consent information
    consent_type: str = "federated_learning"
    consent_given: bool = False
    consent_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Privacy and compliance
    data_privacy_level: str = "private"  # private, shared, public
    consent_terms_version: str = "1.0"
    consent_terms: Optional[str] = None
    
    # Associated entities
    project_id: Optional[str] = None
    file_id: Optional[str] = None
    
    # Additional data
    metadata: Optional[str] = None  # JSON string for additional consent data
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validate the model after initialization"""
        self.validate()
    
    def validate(self) -> bool:
        """
        Validate the UserConsent model
        
        Returns:
            bool: True if valid, raises ValueError if invalid
        """
        # Required fields
        if not self.user_id:
            raise ValueError("user_id is required")
        
        if not self.consent_id:
            raise ValueError("consent_id is required")
        
        # Validate consent_type
        valid_consent_types = ["federated_learning", "data_sharing", "analytics", "research"]
        if self.consent_type not in valid_consent_types:
            raise ValueError(f"consent_type must be one of: {valid_consent_types}")
        
        # Validate data_privacy_level
        valid_privacy_levels = ["private", "shared", "public"]
        if self.data_privacy_level not in valid_privacy_levels:
            raise ValueError(f"data_privacy_level must be one of: {valid_privacy_levels}")
        
        # Validate timestamps
        try:
            datetime.fromisoformat(self.consent_timestamp)
            datetime.fromisoformat(self.created_at)
            datetime.fromisoformat(self.updated_at)
        except ValueError:
            raise ValueError("Invalid timestamp format. Use ISO format.")
        
        # Validate metadata if present
        if self.metadata:
            try:
                json.loads(self.metadata)
            except json.JSONDecodeError:
                raise ValueError("metadata must be valid JSON")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert UserConsent to dictionary
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            'consent_id': self.consent_id,
            'user_id': self.user_id,
            'consent_type': self.consent_type,
            'consent_given': self.consent_given,
            'consent_timestamp': self.consent_timestamp,
            'data_privacy_level': self.data_privacy_level,
            'consent_terms_version': self.consent_terms_version,
            'consent_terms': self.consent_terms,
            'project_id': self.project_id,
            'file_id': self.file_id,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserConsent':
        """
        Create UserConsent from dictionary
        
        Args:
            data: Dictionary containing consent data
            
        Returns:
            UserConsent: New UserConsent instance
        """
        return cls(**data)
    
    def update_consent(self, consent_given: bool, consent_terms: Optional[str] = None) -> None:
        """
        Update consent status
        
        Args:
            consent_given: New consent status
            consent_terms: Updated consent terms (optional)
        """
        self.consent_given = consent_given
        self.consent_timestamp = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        if consent_terms:
            self.consent_terms = consent_terms
        
        self.validate()
    
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Set metadata as JSON string
        
        Args:
            metadata: Dictionary to store as JSON
        """
        self.metadata = json.dumps(metadata)
        self.updated_at = datetime.now().isoformat()
        self.validate()
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get metadata as dictionary
        
        Returns:
            Optional[Dict[str, Any]]: Metadata dictionary or None
        """
        if self.metadata:
            try:
                return json.loads(self.metadata)
            except json.JSONDecodeError:
                return None
        return None
    
    def is_active(self) -> bool:
        """
        Check if consent is active (given and not expired)
        
        Returns:
            bool: True if consent is active
        """
        if not self.consent_given:
            return False
        
        # Check if consent is older than 1 year (configurable)
        consent_date = datetime.fromisoformat(self.consent_timestamp)
        expiry_date = consent_date.replace(year=consent_date.year + 1)
        
        return datetime.now() < expiry_date
    
    def revoke_consent(self) -> None:
        """Revoke consent"""
        self.consent_given = False
        self.consent_timestamp = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.validate()
    
    def __str__(self) -> str:
        """String representation"""
        status = "ACTIVE" if self.is_active() else "INACTIVE"
        return f"UserConsent({self.consent_id}, user={self.user_id}, type={self.consent_type}, status={status})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"UserConsent(consent_id='{self.consent_id}', user_id='{self.user_id}', consent_type='{self.consent_type}', consent_given={self.consent_given})" 