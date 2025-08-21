"""
Export Manager for Certificate Manager

Orchestrates all exporters and provides a unified interface for certificate exports.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .base_exporter import BaseExporter, ExportError
from .html_exporter import HTMLExporter
from .json_exporter import JSONExporter
from .xml_exporter import XMLExporter

logger = logging.getLogger(__name__)


class ExportManager:
    """Manages certificate exports across multiple formats."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ExportManager")
        self.exporters: Dict[str, BaseExporter] = {}
        self._initialize_exporters()
    
    def _initialize_exporters(self):
        """Initialize all available exporters."""
        self.exporters = {
            'html': HTMLExporter(),
            'json': JSONExporter(),
            'xml': XMLExporter()
        }
        self.logger.info(f"Initialized {len(self.exporters)} exporters: {list(self.exporters.keys())}")
    
    def get_available_formats(self) -> List[str]:
        """Get list of available export formats."""
        return list(self.exporters.keys())
    
    def get_exporter(self, format_name: str) -> Optional[BaseExporter]:
        """Get exporter for specific format."""
        return self.exporters.get(format_name.lower())
    
    async def export_certificate(self, certificate_id: str, version: str, 
                                format_name: str, template_id: str = 'default',
                                custom_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export certificate in specified format."""
        try:
            self.logger.info(f"Starting export for certificate {certificate_id} in {format_name} format")
            
            # Get exporter
            exporter = self.get_exporter(format_name)
            if not exporter:
                raise ExportError(f"Unsupported export format: {format_name}")
            
            # Perform export
            export_data = await exporter.export(certificate_id, version, template_id, custom_data)
            
            # Add export manager metadata
            export_data['export_manager'] = {
                'exported_at': datetime.now().isoformat(),
                'format_requested': format_name,
                'template_used': template_id,
                'exporter_version': '1.0'
            }
            
            self.logger.info(f"Export completed for certificate {certificate_id} in {format_name} format")
            return export_data
            
        except Exception as e:
            self.logger.error(f"Export failed for certificate {certificate_id}: {str(e)}")
            raise ExportError(f"Export failed: {str(e)}")
    
    async def export_multiple_formats(self, certificate_id: str, version: str,
                                     formats: List[str], template_id: str = 'default',
                                     custom_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export certificate in multiple formats concurrently."""
        try:
            self.logger.info(f"Starting multi-format export for certificate {certificate_id}")
            
            # Validate formats
            available_formats = self.get_available_formats()
            invalid_formats = [f for f in formats if f.lower() not in available_formats]
            if invalid_formats:
                raise ExportError(f"Unsupported formats: {invalid_formats}")
            
            # Create export tasks
            tasks = []
            for format_name in formats:
                task = self.export_certificate(certificate_id, version, format_name, template_id, custom_data)
                tasks.append(task)
            
            # Execute exports concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            export_results = {}
            for i, result in enumerate(results):
                format_name = formats[i]
                if isinstance(result, Exception):
                    self.logger.error(f"Export failed for {format_name}: {str(result)}")
                    export_results[format_name] = {
                        'error': str(result),
                        'status': 'failed'
                    }
                else:
                    export_results[format_name] = {
                        'data': result,
                        'status': 'success'
                    }
            
            # Create summary
            summary = {
                'certificate_id': certificate_id,
                'version': version,
                'formats_requested': formats,
                'template_used': template_id,
                'exported_at': datetime.now().isoformat(),
                'results': export_results,
                'success_count': sum(1 for r in export_results.values() if r['status'] == 'success'),
                'failure_count': sum(1 for r in export_results.values() if r['status'] == 'failed')
            }
            
            self.logger.info(f"Multi-format export completed for certificate {certificate_id}")
            return summary
            
        except Exception as e:
            self.logger.error(f"Multi-format export failed for certificate {certificate_id}: {str(e)}")
            raise ExportError(f"Multi-format export failed: {str(e)}")
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific export format."""
        exporter = self.get_exporter(format_name)
        if not exporter:
            return None
        
        return {
            'format': format_name,
            'mime_type': exporter.get_mime_type(),
            'file_extension': exporter.get_file_extension(),
            'description': self._get_format_description(format_name),
            'features': self._get_format_features(format_name)
        }
    
    def get_all_format_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available formats."""
        return {
            format_name: self.get_format_info(format_name)
            for format_name in self.get_available_formats()
        }
    
    def _get_format_description(self, format_name: str) -> str:
        """Get description for export format."""
        descriptions = {
            'html': 'Interactive web view with expandable sections and styling',
            'json': 'Machine-readable format with complete certificate data',
            'xml': 'Standards-compliant format for industry integration'
        }
        return descriptions.get(format_name, 'Unknown format')
    
    def _get_format_features(self, format_name: str) -> List[str]:
        """Get features for export format."""
        features = {
            'html': [
                'Interactive sections',
                'Professional styling',
                'Expandable content',
                'Keyboard shortcuts',
                'Print-friendly'
            ],
            'json': [
                'Complete data structure',
                'Machine-readable',
                'API integration',
                'Programmatic access',
                'Schema validation'
            ],
            'xml': [
                'Industry standards',
                'Schema compliance',
                'OPC UA compatible',
                'eCl@ss integration',
                'Validation support'
            ]
        }
        return features.get(format_name, [])
    
    async def validate_export(self, certificate_id: str, version: str, 
                             format_name: str) -> Dict[str, Any]:
        """Validate that a certificate can be exported in the specified format."""
        try:
            # Check if certificate exists
            from src.certificate_manager.core.certificate_manager import CertificateManager
            
            cm = CertificateManager()
            certificate = cm.get_certificate(certificate_id)
            version_data = cm.get_certificate_version(certificate_id, version)
            
            validation_result = {
                'certificate_id': certificate_id,
                'version': version,
                'format': format_name,
                'valid': True,
                'issues': [],
                'warnings': []
            }
            
            # Check certificate existence
            if not certificate:
                validation_result['valid'] = False
                validation_result['issues'].append('Certificate not found')
            
            # Check version existence
            if not version_data:
                validation_result['valid'] = False
                validation_result['issues'].append('Version not found')
            
            # Check format support
            if format_name.lower() not in self.get_available_formats():
                validation_result['valid'] = False
                validation_result['issues'].append(f'Format {format_name} not supported')
            
            # Check content
            if version_data and version_data.is_empty():
                validation_result['warnings'].append('Certificate has no content')
            
            return validation_result
            
        except Exception as e:
            return {
                'certificate_id': certificate_id,
                'version': version,
                'format': format_name,
                'valid': False,
                'issues': [f'Validation error: {str(e)}'],
                'warnings': []
            } 