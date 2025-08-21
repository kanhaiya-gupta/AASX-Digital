"""
XML Exporter for Certificate Manager

Generates standards-compliant XML format for certificates with industry standards.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base_exporter import BaseExporter, ExportError


class XMLExporter(BaseExporter):
    """XML export implementation for standards compliance."""
    
    def __init__(self):
        super().__init__('xml')
    
    async def export(self, certificate_id: str, version: str, 
                    template_id: str = 'default', 
                    custom_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export certificate as XML."""
        try:
            self.logger.info(f"Starting XML export for certificate {certificate_id} v{version}")
            
            # Get certificate data
            certificate_data = await self._get_certificate_data(certificate_id, version)
            
            # Generate XML content
            xml_content = self._generate_xml_content(certificate_data, template_id, custom_data)
            
            # Compress if needed
            if self._should_compress(xml_content):
                xml_content = await self._compress_content(xml_content)
            
            # Create export data
            export_data = {
                'content': xml_content,
                'file_size': len(xml_content.encode('utf-8')),
                'mime_type': self.get_mime_type(),
                'file_extension': self.get_file_extension(),
                'filename': self._generate_filename(certificate_id, version)
            }
            
            # Add metadata
            export_data = self._add_export_metadata(export_data, certificate_id, version, template_id)
            
            # Validate export data
            self._validate_export_data(export_data)
            
            self.logger.info(f"XML export completed for certificate {certificate_id}")
            return export_data
            
        except Exception as e:
            self.logger.error(f"XML export failed for certificate {certificate_id}: {str(e)}")
            raise ExportError(f"XML export failed: {str(e)}")
    
    def get_mime_type(self) -> str:
        return 'application/xml'
    
    def get_file_extension(self) -> str:
        return 'xml'
    
    def _generate_xml_content(self, certificate_data: Dict[str, Any], 
                             template_id: str, custom_data: Optional[Dict[str, Any]]) -> str:
        """Generate XML content from certificate data."""
        certificate = certificate_data['certificate']
        version = certificate_data['version']
        sections = certificate_data['sections']
        summary_data = certificate_data.get('summary_data')
        reference_links = certificate_data.get('reference_links')
        
        # Create XML structure
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<certificate xmlns="http://aas-data-modeling.com/certificate/1.0"',
            '             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
            '             xsi:schemaLocation="http://aas-data-modeling.com/certificate/1.0 certificate.xsd">',
            '',
            '  <metadata>',
            f'    <export_timestamp>{datetime.now().isoformat()}</export_timestamp>',
            f'    <template_id>{template_id}</template_id>',
            f'    <format>xml</format>',
            f'    <schema_version>1.0</schema_version>',
            '  </metadata>',
            '',
            '  <certificate_info>',
            f'    <id>{self._escape_xml(certificate.get("certificate_id", ""))}</id>',
            f'    <twin_name>{self._escape_xml(certificate.get("twin_name", ""))}</twin_name>',
            f'    <project_name>{self._escape_xml(certificate.get("project_name", ""))}</project_name>',
            f'    <use_case_name>{self._escape_xml(certificate.get("use_case_name", ""))}</use_case_name>',
            f'    <file_name>{self._escape_xml(certificate.get("file_name", ""))}</file_name>',
            f'    <status>{self._escape_xml(str(certificate.get("status", "")))}</status>',
            f'    <visibility>{self._escape_xml(str(certificate.get("visibility", "")))}</visibility>',
            f'    <retention_policy>{self._escape_xml(str(certificate.get("retention_policy", "")))}</retention_policy>',
            f'    <created_at>{self._escape_xml(certificate.get("created_at", ""))}</created_at>',
            f'    <updated_at>{self._escape_xml(certificate.get("updated_at", ""))}</updated_at>',
            f'    <uploaded_at>{self._escape_xml(certificate.get("uploaded_at", ""))}</uploaded_at>',
            f'    <signature_timestamp>{self._escape_xml(certificate.get("signature_timestamp", ""))}</signature_timestamp>',
            '  </certificate_info>',
            '',
            '  <version_info>',
            f'    <version>{self._escape_xml(version.get("version", ""))}</version>',
            f'    <content_hash>{self._escape_xml(version.get("content_hash", ""))}</content_hash>',
            f'    <created_at>{self._escape_xml(version.get("created_at", ""))}</created_at>',
            f'    <created_by>{self._escape_xml(version.get("created_by", ""))}</created_by>',
            f'    <sections_count>{version.get("sections_count", 0)}</sections_count>',
            f'    <content_size>{version.get("content_size", 0)}</content_size>',
            f'    <is_empty>{str(version.get("is_empty", True)).lower()}</is_empty>',
            '  </version_info>',
            '',
            '  <sections>'
        ]
        
        # Add sections
        if sections:
            for section_name, section_data in sections.items():
                xml_lines.extend(self._generate_section_xml(section_name, section_data))
        else:
            xml_lines.append('    <no_sections>No sections available</no_sections>')
        
        xml_lines.append('  </sections>')
        
        # Add summary data
        if summary_data:
            xml_lines.extend([
                '',
                '  <summary_data>',
                self._dict_to_xml(summary_data, indent=4),
                '  </summary_data>'
            ])
        
        # Add reference links
        if reference_links:
            xml_lines.extend([
                '',
                '  <reference_links>',
                self._dict_to_xml(reference_links, indent=4),
                '  </reference_links>'
            ])
        
        # Add custom data
        if custom_data:
            xml_lines.extend([
                '',
                '  <custom_data>',
                self._dict_to_xml(custom_data, indent=4),
                '  </custom_data>'
            ])
        
        # Close XML
        xml_lines.extend([
            '',
            '</certificate>'
        ])
        
        return '\n'.join(xml_lines)
    
    def _generate_section_xml(self, section_name: str, section_data: Any) -> list:
        """Generate XML for a section."""
        lines = [f'    <section name="{self._escape_xml(section_name)}">']
        
        if isinstance(section_data, dict):
            lines.append(self._dict_to_xml(section_data, indent=6))
        elif isinstance(section_data, list):
            lines.append(self._list_to_xml(section_data, indent=6))
        else:
            lines.append(f'      <value>{self._escape_xml(str(section_data))}</value>')
        
        lines.append('    </section>')
        return lines
    
    def _dict_to_xml(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Convert dictionary to XML format."""
        if not data:
            return ' ' * indent + '<empty/>'
        
        lines = []
        for key, value in data.items():
            safe_key = self._make_xml_safe(key)
            indent_str = ' ' * indent
            
            if isinstance(value, dict):
                lines.append(f'{indent_str}<{safe_key}>')
                lines.append(self._dict_to_xml(value, indent + 2))
                lines.append(f'{indent_str}</{safe_key}>')
            elif isinstance(value, list):
                lines.append(f'{indent_str}<{safe_key}>')
                lines.append(self._list_to_xml(value, indent + 2))
                lines.append(f'{indent_str}</{safe_key}>')
            else:
                lines.append(f'{indent_str}<{safe_key}>{self._escape_xml(str(value))}</{safe_key}>')
        
        return '\n'.join(lines)
    
    def _list_to_xml(self, data: list, indent: int = 0) -> str:
        """Convert list to XML format."""
        if not data:
            return ' ' * indent + '<empty/>'
        
        lines = []
        for i, item in enumerate(data):
            indent_str = ' ' * indent
            
            if isinstance(item, dict):
                lines.append(f'{indent_str}<item_{i}>')
                lines.append(self._dict_to_xml(item, indent + 2))
                lines.append(f'{indent_str}</item_{i}>')
            elif isinstance(item, list):
                lines.append(f'{indent_str}<item_{i}>')
                lines.append(self._list_to_xml(item, indent + 2))
                lines.append(f'{indent_str}</item_{i}>')
            else:
                lines.append(f'{indent_str}<item_{i}>{self._escape_xml(str(item))}</item_{i}>')
        
        return '\n'.join(lines)
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        if not text:
            return ""
        
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))
    
    def _make_xml_safe(self, name: str) -> str:
        """Make a string safe for XML element names."""
        # Remove or replace invalid characters
        safe_name = ''.join(c for c in name if c.isalnum() or c in '_-')
        
        # Ensure it starts with a letter or underscore
        if safe_name and not (safe_name[0].isalpha() or safe_name[0] == '_'):
            safe_name = 'item_' + safe_name
        
        # Ensure it's not empty
        if not safe_name:
            safe_name = 'item'
        
        return safe_name
    
    async def _compress_content(self, content: str) -> str:
        """Compress XML content."""
        # For XML, we can use gzip compression
        import gzip
        compressed = gzip.compress(content.encode('utf-8'))
        return compressed.decode('latin-1')  # Return as string for storage 