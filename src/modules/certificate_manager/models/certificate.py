"""
Certificate Model

Main certificate data model for the Certificate Manager.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import hashlib
import json

from src.shared.models.base_model import BaseModel


class CertificateStatus(str, Enum):
    """Certificate status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    STALE = "stale"
    ARCHIVED = "archived"
    ERROR = "error"


class CertificateVisibility(str, Enum):
    """Certificate visibility enumeration."""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"


class RetentionPolicy(str, Enum):
    """Certificate retention policy enumeration."""
    KEEP_ALL = "keep_all"
    KEEP_LAST_N = "keep_last_n"
    ARCHIVE_AFTER_DAYS = "archive_after_days"
    DELETE_AFTER_DAYS = "delete_after_days"


@dataclass
class Certificate(BaseModel):
    """Certificate data model."""
    
    # Core identification - make these optional with defaults
    certificate_id: str = field(default="")
    twin_id: str = field(default="")
    
    # Basic information - make these optional with defaults
    twin_name: str = field(default="Unknown Twin")
    project_name: str = field(default="Unknown Project")
    use_case_name: str = field(default="Unknown Use Case")
    file_name: str = field(default="Unknown File")
    
    # Timestamps
    uploaded_at: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Status and versioning
    status: CertificateStatus = CertificateStatus.PENDING
    current_version: str = "1.0.0"
    
    # Visibility and access
    visibility: CertificateVisibility = CertificateVisibility.PRIVATE
    access_level: str = "project_members"
    
    # Configuration
    template_id: str = "default"
    retention_policy: RetentionPolicy = RetentionPolicy.KEEP_ALL
    
    # Security and verification
    signature: Optional[str] = None
    signature_timestamp: Optional[datetime] = None
    
    # Metadata and configuration
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization setup."""
        super().__post_init__()
        
        # Generate certificate ID if not provided
        if not self.certificate_id:
            self.certificate_id = self._generate_certificate_id()
        
        # Set twin_id if not provided
        if not self.twin_id:
            self.twin_id = self.certificate_id
    
    def _generate_certificate_id(self) -> str:
        """Generate a unique certificate ID."""
        # Use a combination of twin info and timestamp for uniqueness
        base_string = f"{self.twin_name}_{self.project_name}_{self.use_case_name}_{self.uploaded_at.isoformat()}"
        return hashlib.sha256(base_string.encode()).hexdigest()[:16]
    
    def validate_status_transition(self, new_status: CertificateStatus) -> bool:
        """Validate if a status transition is allowed."""
        valid_transitions = {
            CertificateStatus.PENDING: [CertificateStatus.IN_PROGRESS, CertificateStatus.ERROR],
            CertificateStatus.IN_PROGRESS: [CertificateStatus.READY, CertificateStatus.ERROR],
            CertificateStatus.READY: [CertificateStatus.STALE, CertificateStatus.ARCHIVED],
            CertificateStatus.STALE: [CertificateStatus.READY, CertificateStatus.ARCHIVED],
            CertificateStatus.ERROR: [CertificateStatus.IN_PROGRESS, CertificateStatus.ARCHIVED],
            CertificateStatus.ARCHIVED: []  # No transitions from archived
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def update_status(self, new_status: CertificateStatus) -> bool:
        """Update certificate status if transition is valid."""
        if self.validate_status_transition(new_status):
            self.status = new_status
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the certificate."""
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def remove_metadata(self, key: str) -> bool:
        """Remove metadata key."""
        if key in self.metadata:
            del self.metadata[key]
            self.updated_at = datetime.now()
            return True
        return False
    
    def calculate_health_score(self) -> float:
        """Calculate overall health score based on metadata."""
        # This will be enhanced in Phase 2 when we have module data
        base_score = 100.0
        
        # Reduce score for errors
        if self.status == CertificateStatus.ERROR:
            base_score -= 50
        
        # Reduce score for stale certificates
        if self.status == CertificateStatus.STALE:
            base_score -= 20
        
        return max(0.0, base_score)
    
    def is_publicly_accessible(self) -> bool:
        """Check if certificate is publicly accessible."""
        return self.visibility == CertificateVisibility.PUBLIC
    
    def can_be_exported(self) -> bool:
        """Check if certificate can be exported."""
        return self.status in [CertificateStatus.READY, CertificateStatus.STALE]
    
    def get_display_name(self) -> str:
        """Get a human-readable display name."""
        return f"Certificate - {self.twin_name} - {self.project_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert certificate to dictionary."""
        return {
            'certificate_id': self.certificate_id,
            'twin_id': self.twin_id,
            'twin_name': self.twin_name,
            'project_name': self.project_name,
            'use_case_name': self.use_case_name,
            'file_name': self.file_name,
            'uploaded_at': self.uploaded_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'current_version': self.current_version,
            'visibility': self.visibility.value,
            'access_level': self.access_level,
            'template_id': self.template_id,
            'retention_policy': self.retention_policy.value,
            'signature': self.signature,
            'signature_timestamp': self.signature_timestamp.isoformat() if self.signature_timestamp else None,
            'metadata': self.metadata,
            'health_score': self.calculate_health_score(),
            'display_name': self.get_display_name()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Certificate':
        """Create certificate from dictionary."""
        # Convert sqlite3.Row to dict if needed
        if hasattr(data, 'keys'):  # sqlite3.Row object
            data = dict(data)
        
        # Remove database-specific fields that don't exist in the model
        data_copy = data.copy()
        data_copy.pop('id', None)  # Remove database auto-increment ID if present
        
        # Convert string enums back to enum values
        if 'status' in data_copy and isinstance(data_copy['status'], str):
            data_copy['status'] = CertificateStatus(data_copy['status'])
        
        if 'visibility' in data_copy and isinstance(data_copy['visibility'], str):
            data_copy['visibility'] = CertificateVisibility(data_copy['visibility'])
        
        if 'retention_policy' in data_copy and isinstance(data_copy['retention_policy'], str):
            data_copy['retention_policy'] = RetentionPolicy(data_copy['retention_policy'])
        
        # Convert timestamp strings back to datetime
        for field in ['uploaded_at', 'created_at', 'updated_at', 'signature_timestamp']:
            if field in data_copy and data_copy[field] and isinstance(data_copy[field], str):
                data_copy[field] = datetime.fromisoformat(data_copy[field])
        
        # Deserialize JSON fields back to dictionaries
        import json
        if 'metadata' in data_copy and data_copy['metadata'] and isinstance(data_copy['metadata'], str):
            try:
                data_copy['metadata'] = json.loads(data_copy['metadata'])
            except (json.JSONDecodeError, TypeError):
                # Keep as string if JSON parsing fails
                pass
        
        return cls(**data_copy)
    
    def __str__(self) -> str:
        """String representation."""
        return f"Certificate({self.certificate_id}, {self.twin_name}, {self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Certificate(certificate_id='{self.certificate_id}', twin_name='{self.twin_name}', status='{self.status.value}')" 