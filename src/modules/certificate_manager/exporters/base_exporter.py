"""
Base Exporter for Certificate Manager

Abstract base class for certificate exporters with common functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, BinaryIO
from pathlib import Path
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Exception raised for export-related errors."""
    pass


class BaseExporter(ABC):
    """Base class for certificate exporters."""
    
    def __init__(self, format_name: str):
        self.format_name = format_name
        self.logger = logging.getLogger(f"{__name__}.{format_name}")
    
    @abstractmethod
    async def export(self, certificate_id: str, version: str, 
                    template_id: str = 'default', 
                    custom_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export certificate to specific format."""
        pass
    
    @abstractmethod
    def get_mime_type(self) -> str:
        """Get MIME type for the export format."""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension for the export format."""
        pass
    
    async def _get_certificate_data(self, certificate_id: str, version: str) -> Dict[str, Any]:
        """Get certificate and version data for export."""
        try:
            from src.certificate_manager.core.certificate_manager import CertificateManager
            
            cm = CertificateManager()
            certificate = cm.get_certificate(certificate_id)
            version_data = cm.get_certificate_version(certificate_id, version)
            
            if not certificate:
                raise ExportError(f"Certificate {certificate_id} not found")
            
            if not version_data:
                raise ExportError(f"Version {version} not found for certificate {certificate_id}")
            
            return {
                'certificate': certificate.to_dict(),
                'version': version_data.to_dict(),
                'sections': version_data.sections,
                'summary_data': version_data.summary_data,
                'reference_links': version_data.reference_links
            }
            
        except Exception as e:
            raise ExportError(f"Failed to get certificate data: {str(e)}")
    
    def _generate_filename(self, certificate_id: str, version: str) -> str:
        """Generate filename for export."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"certificate_{certificate_id}_v{version}_{timestamp}.{self.get_file_extension()}"
    
    def _add_export_metadata(self, export_data: Dict[str, Any], 
                            certificate_id: str, version: str, 
                            template_id: str) -> Dict[str, Any]:
        """Add metadata to export data."""
        export_data.update({
            'export_metadata': {
                'format': self.format_name,
                'certificate_id': certificate_id,
                'version': version,
                'template_id': template_id,
                'generated_at': datetime.now().isoformat(),
                'mime_type': self.get_mime_type(),
                'file_extension': self.get_file_extension()
            }
        })
        return export_data
    
    def _validate_export_data(self, export_data: Dict[str, Any]) -> bool:
        """Validate export data structure."""
        required_fields = ['content', 'file_size', 'mime_type', 'file_extension']
        
        for field in required_fields:
            if field not in export_data:
                raise ExportError(f"Missing required field: {field}")
        
        if not isinstance(export_data['content'], (str, bytes)):
            raise ExportError("Content must be string or bytes")
        
        if not isinstance(export_data['file_size'], int):
            raise ExportError("File size must be integer")
        
        return True
    
    async def _compress_content(self, content: str) -> str:
        """Compress content if needed."""
        # Simple compression for now - can be enhanced later
        return content
    
    def _should_compress(self, content: str) -> bool:
        """Determine if content should be compressed."""
        # Compress if content is larger than 1MB
        return len(content.encode('utf-8')) > 1024 * 1024 