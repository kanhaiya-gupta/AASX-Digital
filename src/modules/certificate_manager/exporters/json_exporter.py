"""
JSON Exporter for Certificate Manager

Generates machine-readable JSON format for certificates with complete data.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base_exporter import BaseExporter, ExportError


class JSONExporter(BaseExporter):
    """JSON export implementation for machine-readable format."""
    
    def __init__(self):
        super().__init__('json')
    
    async def export(self, certificate_id: str, version: str, 
                    template_id: str = 'default', 
                    custom_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export certificate as JSON."""
        try:
            self.logger.info(f"Starting JSON export for certificate {certificate_id} v{version}")
            
            # Get certificate data
            certificate_data = await self._get_certificate_data(certificate_id, version)
            
            # Generate JSON content
            json_content = self._generate_json_content(certificate_data, template_id, custom_data)
            
            # Compress if needed
            if self._should_compress(json_content):
                json_content = await self._compress_content(json_content)
            
            # Create export data
            export_data = {
                'content': json_content,
                'file_size': len(json_content.encode('utf-8')),
                'mime_type': self.get_mime_type(),
                'file_extension': self.get_file_extension(),
                'filename': self._generate_filename(certificate_id, version)
            }
            
            # Add metadata
            export_data = self._add_export_metadata(export_data, certificate_id, version, template_id)
            
            # Validate export data
            self._validate_export_data(export_data)
            
            self.logger.info(f"JSON export completed for certificate {certificate_id}")
            return export_data
            
        except Exception as e:
            self.logger.error(f"JSON export failed for certificate {certificate_id}: {str(e)}")
            raise ExportError(f"JSON export failed: {str(e)}")
    
    def get_mime_type(self) -> str:
        return 'application/json'
    
    def get_file_extension(self) -> str:
        return 'json'
    
    def _generate_json_content(self, certificate_data: Dict[str, Any], 
                              template_id: str, custom_data: Optional[Dict[str, Any]]) -> str:
        """Generate JSON content from certificate data."""
        certificate = certificate_data['certificate']
        version = certificate_data['version']
        sections = certificate_data['sections']
        summary_data = certificate_data.get('summary_data')
        reference_links = certificate_data.get('reference_links')
        
        # Create complete JSON structure
        json_data = {
            'certificate': {
                'id': certificate.get('certificate_id'),
                'twin_name': certificate.get('twin_name'),
                'project_name': certificate.get('project_name'),
                'use_case_name': certificate.get('use_case_name'),
                'file_name': certificate.get('file_name'),
                'status': certificate.get('status'),
                'visibility': certificate.get('visibility'),
                'retention_policy': certificate.get('retention_policy'),
                'created_at': certificate.get('created_at'),
                'updated_at': certificate.get('updated_at'),
                'uploaded_at': certificate.get('uploaded_at'),
                'signature_timestamp': certificate.get('signature_timestamp'),
                'metadata': certificate.get('metadata', {})
            },
            'version': {
                'version': version.get('version'),
                'content_hash': version.get('content_hash'),
                'created_at': version.get('created_at'),
                'created_by': version.get('created_by'),
                'sections_count': version.get('sections_count'),
                'content_size': version.get('content_size'),
                'is_empty': version.get('is_empty')
            },
            'sections': sections,
            'summary_data': summary_data,
            'reference_links': reference_links,
            'export_metadata': {
                'format': 'json',
                'template_id': template_id,
                'export_timestamp': datetime.now().isoformat(),
                'custom_data': custom_data or {},
                'schema_version': '1.0'
            }
        }
        
        # Convert to JSON string with proper formatting
        return json.dumps(json_data, indent=2, default=self._json_serializer)
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    async def _compress_content(self, content: str) -> str:
        """Compress JSON content."""
        # For JSON, we can use gzip compression
        import gzip
        compressed = gzip.compress(content.encode('utf-8'))
        return compressed.decode('latin-1')  # Return as string for storage 