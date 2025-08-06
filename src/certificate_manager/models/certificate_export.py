"""
Certificate Export Model

Export tracking and management for certificate downloads.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import hashlib

from src.shared.models.base_model import BaseModel


class ExportFormat(str, Enum):
    """Supported export formats."""
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    XML = "xml"


class ExportStatus(str, Enum):
    """Export processing status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class CertificateExport(BaseModel):
    """Certificate export data model."""
    
    # Core identification - make these optional with defaults
    certificate_id: str = field(default="")
    version: str = field(default="1.0.0")
    format: ExportFormat = ExportFormat.HTML
    
    # File information
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    
    # Timestamps
    generated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Processing status
    status: ExportStatus = ExportStatus.PENDING
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization setup."""
        super().__post_init__()
        
        # Set default expiration (7 days from generation)
        if not self.expires_at:
            self.expires_at = datetime.now().replace(
                hour=23, minute=59, second=59, microsecond=999999
            ) + datetime.timedelta(days=7)
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate hash of exported file content."""
        return hashlib.sha256(file_content).hexdigest()
    
    def update_file_info(self, file_path: str, file_content: bytes) -> None:
        """Update file information after generation."""
        self.file_path = file_path
        self.file_hash = self.calculate_file_hash(file_content)
        self.file_size = len(file_content)
        self.status = ExportStatus.COMPLETED
        self.generated_at = datetime.now()
    
    def mark_generating(self) -> None:
        """Mark export as generating."""
        self.status = ExportStatus.GENERATING
    
    def mark_completed(self) -> None:
        """Mark export as completed."""
        self.status = ExportStatus.COMPLETED
        self.generated_at = datetime.now()
    
    def mark_failed(self) -> None:
        """Mark export as failed."""
        self.status = ExportStatus.FAILED
    
    def mark_expired(self) -> None:
        """Mark export as expired."""
        self.status = ExportStatus.EXPIRED
    
    def is_expired(self) -> bool:
        """Check if export has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def is_available(self) -> bool:
        """Check if export is available for download."""
        return (
            self.status == ExportStatus.COMPLETED and
            not self.is_expired() and
            self.file_path is not None
        )
    
    def get_download_url(self, base_url: str = "") -> Optional[str]:
        """Get download URL for the export."""
        if not self.is_available():
            return None
        
        return f"{base_url}/api/certificates/{self.certificate_id}/exports/{self.format.value}/download"
    
    def get_filename(self) -> str:
        """Get suggested filename for download."""
        return f"certificate_{self.certificate_id}_{self.version}.{self.format.value}"
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the export."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def get_remaining_days(self) -> Optional[int]:
        """Get remaining days until expiration."""
        if not self.expires_at:
            return None
        
        remaining = self.expires_at - datetime.now()
        return max(0, remaining.days)
    
    def extend_expiration(self, days: int) -> None:
        """Extend expiration by specified days."""
        if self.expires_at:
            self.expires_at = self.expires_at + datetime.timedelta(days=days)
        else:
            self.expires_at = datetime.now() + datetime.timedelta(days=days)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert export to dictionary."""
        return {
            'certificate_id': self.certificate_id,
            'version': self.version,
            'format': self.format.value,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'generated_at': self.generated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'status': self.status.value,
            'metadata': self.metadata,
            'is_expired': self.is_expired(),
            'is_available': self.is_available(),
            'filename': self.get_filename(),
            'remaining_days': self.get_remaining_days()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CertificateExport':
        """Create export from dictionary."""
        # Convert string enums back to enum values
        if 'format' in data and isinstance(data['format'], str):
            data['format'] = ExportFormat(data['format'])
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = ExportStatus(data['status'])
        
        # Convert timestamp strings back to datetime
        for field in ['generated_at', 'expires_at']:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation."""
        return f"CertificateExport({self.certificate_id}, {self.format.value}, {self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"CertificateExport(certificate_id='{self.certificate_id}', format='{self.format.value}', status='{self.status.value}')" 