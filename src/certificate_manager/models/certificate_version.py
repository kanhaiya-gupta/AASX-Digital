"""
Certificate Version Model

Version management for certificates with content tracking and validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import json

from src.shared.models.base_model import BaseModel


@dataclass
class CertificateVersion(BaseModel):
    """Certificate version data model."""
    
    # Core identification - make these optional with defaults
    certificate_id: str = field(default="")
    version: str = field(default="1.0.0")
    
    # Content and data
    content_hash: str = field(default="")
    sections: Dict[str, Any] = field(default_factory=dict)
    
    # Summary and reference data
    summary_data: Optional[Dict[str, Any]] = None
    reference_links: Optional[Dict[str, Any]] = None
    
    # Export and cache data
    export_cache: Optional[Dict[str, Any]] = None
    
    # Signature metadata
    signature_metadata: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def __post_init__(self):
        """Post-initialization setup."""
        super().__post_init__()
        
        # Generate content hash if not provided
        if not self.content_hash:
            self.content_hash = self._calculate_content_hash()
    
    def _calculate_content_hash(self) -> str:
        """Calculate hash of certificate content."""
        content_string = json.dumps(self.sections, sort_keys=True, default=str)
        return hashlib.sha256(content_string.encode()).hexdigest()
    
    def validate_version_format(self) -> bool:
        """Validate semantic versioning format."""
        try:
            parts = self.version.split('.')
            if len(parts) != 3:
                return False
            
            major, minor, patch = parts
            int(major)
            int(minor)
            int(patch)
            return True
        except (ValueError, AttributeError):
            return False
    
    def increment_version(self, increment_type: str = "patch") -> str:
        """Increment version number."""
        if not self.validate_version_format():
            return "1.0.0"
        
        major, minor, patch = map(int, self.version.split('.'))
        
        if increment_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def add_section(self, section_name: str, section_data: Dict[str, Any]) -> None:
        """Add or update a section in the certificate."""
        self.sections[section_name] = section_data
        self.content_hash = self._calculate_content_hash()
    
    def get_section(self, section_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific section."""
        return self.sections.get(section_name)
    
    def remove_section(self, section_name: str) -> bool:
        """Remove a section."""
        if section_name in self.sections:
            del self.sections[section_name]
            self.content_hash = self._calculate_content_hash()
            return True
        return False
    
    def update_summary_data(self, summary_data: Dict[str, Any]) -> None:
        """Update summary data."""
        self.summary_data = summary_data
    
    def update_reference_links(self, reference_links: Dict[str, Any]) -> None:
        """Update reference links."""
        self.reference_links = reference_links
    
    def add_export_cache(self, format_type: str, cache_data: Dict[str, Any]) -> None:
        """Add export cache data."""
        if self.export_cache is None:
            self.export_cache = {}
        
        self.export_cache[format_type] = {
            'data': cache_data,
            'created_at': datetime.now().isoformat()
        }
    
    def get_export_cache(self, format_type: str) -> Optional[Dict[str, Any]]:
        """Get export cache data."""
        if self.export_cache and format_type in self.export_cache:
            return self.export_cache[format_type]
        return None
    
    def update_signature_metadata(self, signature_data: Dict[str, Any]) -> None:
        """Update signature metadata."""
        self.signature_metadata = signature_data
    
    def get_sections_count(self) -> int:
        """Get the number of sections."""
        return len(self.sections)
    
    def get_total_content_size(self) -> int:
        """Get approximate content size in bytes."""
        return len(json.dumps(self.sections, default=str))
    
    def is_empty(self) -> bool:
        """Check if version has any content."""
        return len(self.sections) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary."""
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'version': self.version,
            'content_hash': self.content_hash,
            'sections': self.sections,
            'summary_data': self.summary_data,
            'reference_links': self.reference_links,
            'export_cache': self.export_cache,
            'signature_metadata': self.signature_metadata,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'sections_count': self.get_sections_count(),
            'content_size': self.get_total_content_size(),
            'is_empty': self.is_empty()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CertificateVersion':
        """Create version from dictionary."""
        # Convert sqlite3.Row to dict if needed
        if hasattr(data, 'keys'):  # sqlite3.Row object
            data = dict(data)
        
        # Remove database-specific fields that don't exist in the model
        data_copy = data.copy()
        data_copy.pop('id', None)  # Remove database auto-increment ID
        
        # Convert timestamp string back to datetime
        if 'created_at' in data_copy and data_copy['created_at'] and isinstance(data_copy['created_at'], str):
            data_copy['created_at'] = datetime.fromisoformat(data_copy['created_at'])
        
        # Deserialize JSON fields back to dictionaries
        import json
        for field in ['sections', 'summary_data', 'reference_links', 'export_cache', 'signature_metadata']:
            if field in data_copy and data_copy[field] and isinstance(data_copy[field], str):
                try:
                    data_copy[field] = json.loads(data_copy[field])
                except (json.JSONDecodeError, TypeError):
                    # Keep as string if JSON parsing fails
                    pass
        
        return cls(**data_copy)
    
    def __str__(self) -> str:
        """String representation."""
        return f"CertificateVersion({self.certificate_id}, {self.version})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"CertificateVersion(certificate_id='{self.certificate_id}', version='{self.version}', sections_count={self.get_sections_count()})" 