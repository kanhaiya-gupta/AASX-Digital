"""
XML Exporter for Certificate Manager

Generates XML data for certificates in a structured format.
This exporter creates XML data only - no UI rendering or styling.
"""

import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

from .base_exporter import BaseExporter, ExportFormat, ExportOptions

logger = logging.getLogger(__name__)


class XMLExporter(BaseExporter):
    """
    XML certificate exporter
    
    Generates structured XML data for certificates including:
    - Certificate metadata and status
    - Module completion information
    - Quality and compliance metrics
    - Digital trust indicators
    - Export metadata
    """
    
    def __init__(self):
        """Initialize the XML exporter"""
        super().__init__(ExportFormat.XML)
        
        logger.info("XML Exporter initialized successfully")
    
    async def export_certificate(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Export certificate to XML format
        
        Args:
            certificate_data: Complete certificate data
            options: Export configuration options
            output_path: Optional path to save the XML file
            
        Returns:
            Dictionary containing XML data and export metadata
        """
        certificate_id = certificate_data.get("certificate_id", "unknown")
        
        # Acquire export lock
        async with await self._acquire_export_lock(certificate_id):
            try:
                # Validate export data
                if not await self.validate_export_data(certificate_data, options):
                    raise ValueError("Certificate data validation failed")
                
                # Prepare data for export
                prepared_data = await self._prepare_certificate_data(certificate_data, options)
                
                # Generate XML content
                xml_content = await self._generate_xml_content(prepared_data, options)
                
                # Generate export metadata
                export_metadata = await self._generate_export_metadata(prepared_data, options)
                
                # Create export result
                export_result = {
                    "format": "xml",
                    "content": xml_content,
                    "metadata": export_metadata,
                    "file_size": len(xml_content.encode('utf-8')),
                    "mime_type": "application/xml",
                    "file_extension": "xml"
                }
                
                # Save to file if output path provided
                if output_path:
                    await self._save_xml_file(output_path, xml_content)
                    export_result["output_path"] = str(output_path)
                
                # Log successful export
                await self._log_export_operation(certificate_id, options, True)
                
                return export_result
                
            except Exception as e:
                error_msg = f"XML export failed: {str(e)}"
                await self._log_export_operation(certificate_id, options, False, error_msg)
                raise
    
    async def validate_export_data(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> bool:
        """
        Validate certificate data for XML export
        
        Args:
            certificate_data: Certificate data to validate
            options: Export options to validate against
            
        Returns:
            True if data is valid for XML export
        """
        # Check required fields
        missing_fields = await self._validate_required_fields(certificate_data)
        if missing_fields:
            logger.warning(f"Missing required fields for XML export: {missing_fields}")
            return False
        
        # Validate certificate status
        status = certificate_data.get("status")
        if status not in ["pending", "in_progress", "ready", "archived"]:
            logger.warning(f"Invalid certificate status for XML export: {status}")
            return False
        
        # Validate completion percentage
        completion = certificate_data.get("completion_percentage", 0)
        if not isinstance(completion, (int, float)) or completion < 0 or completion > 100:
            logger.warning(f"Invalid completion percentage for XML export: {completion}")
            return False
        
        return True
    
    async def get_export_metadata(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> Dict[str, Any]:
        """
        Get metadata about the XML export operation
        
        Args:
            certificate_data: Certificate data being exported
            options: Export options being used
            
        Returns:
            Dictionary containing export metadata
        """
        return {
            "exporter_type": "XMLExporter",
            "export_format": "xml",
            "mime_type": "application/xml",
            "file_extension": "xml",
            "supports_styling": False,
            "supports_metadata": True,
            "supports_metrics": True,
            "supports_versions": options.include_versions,
            "supports_lineage": options.include_lineage,
            "supports_audit_trail": options.include_audit_trail,
            "compression_support": True,
            "encryption_support": options.encryption_enabled,
            "digital_signature_support": options.digital_signature,
            "qr_code_support": options.qr_code
        }
    
    async def _generate_xml_content(
        self,
        prepared_data: Dict[str, Any],
        options: ExportOptions
    ) -> str:
        """
        Generate XML content from prepared certificate data
        
        Args:
            prepared_data: Prepared certificate data
            options: Export options
            
        Returns:
            XML content as string
        """
        certificate_data = prepared_data["certificate_data"]
        
        # Build XML structure
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<certificate xmlns="http://certificate-manager.org/schema/v1.0">
    {await self._build_certificate_section_xml(certificate_data)}
    {await self._build_export_info_section_xml(prepared_data)}
    {await self._build_optional_sections_xml(prepared_data, options)}
</certificate>"""
        
        return xml_content
    
    async def _build_certificate_section_xml(self, certificate_data: Dict[str, Any]) -> str:
        """Build the main certificate section for XML export"""
        return f"""    <certificate_info>
        <certificate_id>{self._escape_xml(certificate_data.get('certificate_id', ''))}</certificate_id>
        <certificate_name>{self._escape_xml(certificate_data.get('certificate_name', ''))}</certificate_name>
        <status>{self._escape_xml(certificate_data.get('status', ''))}</status>
        <completion_percentage>{certificate_data.get('completion_percentage', 0)}</completion_percentage>
        <overall_quality_score>{certificate_data.get('overall_quality_score', 0)}</overall_quality_score>
        <compliance_status>{self._escape_xml(certificate_data.get('compliance_status', ''))}</compliance_status>
        <security_score>{certificate_data.get('security_score', 0)}</security_score>
        <created_at>{self._escape_xml(str(certificate_data.get('created_at', '')))}</created_at>
        <updated_at>{self._escape_xml(str(certificate_data.get('updated_at', '')))}</updated_at>
        {await self._build_module_status_xml(certificate_data)}
        {await self._build_digital_trust_xml(certificate_data)}
        {await self._build_business_context_xml(certificate_data)}
    </certificate_info>"""
    
    async def _build_module_status_xml(self, certificate_data: Dict[str, Any]) -> str:
        """Build module status section for XML export"""
        if "module_status" not in certificate_data:
            return "        <module_status />"
        
        module_status = certificate_data["module_status"]
        xml_lines = ["        <module_status>"]
        
        for module_name, status_info in module_status.items():
            if isinstance(status_info, dict):
                xml_lines.append(f"""            <module name="{self._escape_xml(module_name)}">
                <status>{self._escape_xml(status_info.get('status', 'unknown'))}</status>
                <progress>{status_info.get('progress', 0)}</progress>
                <last_update>{self._escape_xml(str(status_info.get('last_update', '')))}</last_update>
                <error_count>{status_info.get('error_count', 0)}</error_count>
                <health_score>{status_info.get('health_score', 0)}</health_score>
            </module>""")
            else:
                xml_lines.append(f"""            <module name="{self._escape_xml(module_name)}">
                <status>{self._escape_xml(str(status_info))}</status>
                <progress>0</progress>
                <last_update />
                <error_count>0</error_count>
                <health_score>0</health_score>
            </module>""")
        
        xml_lines.append("        </module_status>")
        return "\n".join(xml_lines)
    
    async def _build_digital_trust_xml(self, certificate_data: Dict[str, Any]) -> str:
        """Build digital trust section for XML export"""
        return f"""        <digital_trust>
            <digital_signature>{self._escape_xml(str(certificate_data.get('digital_signature', '')))}</digital_signature>
            <signature_timestamp>{self._escape_xml(str(certificate_data.get('signature_timestamp', '')))}</signature_timestamp>
            <verification_hash>{self._escape_xml(str(certificate_data.get('verification_hash', '')))}</verification_hash>
            <qr_code_data>{self._escape_xml(str(certificate_data.get('qr_code_data', '')))}</qr_code_data>
            <certificate_chain_status>{self._escape_xml(str(certificate_data.get('certificate_chain_status', '')))}</certificate_chain_status>
            <trust_score>{certificate_data.get('trust_score', 0)}</trust_score>
        </digital_trust>"""
    
    async def _build_business_context_xml(self, certificate_data: Dict[str, Any]) -> str:
        """Build business context section for XML export"""
        return f"""        <business_context>
            <file_id>{self._escape_xml(str(certificate_data.get('file_id', '')))}</file_id>
            <user_id>{self._escape_xml(str(certificate_data.get('user_id', '')))}</user_id>
            <org_id>{self._escape_xml(str(certificate_data.get('org_id', '')))}</org_id>
            <project_id>{self._escape_xml(str(certificate_data.get('project_id', '')))}</project_id>
            <twin_id>{self._escape_xml(str(certificate_data.get('twin_id', '')))}</twin_id>
            <tags>{await self._build_tags_xml(certificate_data.get('tags', []))}</tags>
            <custom_attributes>{await self._build_custom_attributes_xml(certificate_data.get('custom_attributes', {}))}</custom_attributes>
        </business_context>"""
    
    async def _build_tags_xml(self, tags: List[str]) -> str:
        """Build tags section for XML export"""
        if not tags:
            return "<tag />"
        
        xml_lines = []
        for tag in tags:
            xml_lines.append(f"            <tag>{self._escape_xml(str(tag))}</tag>")
        return "\n".join(xml_lines)
    
    async def _build_custom_attributes_xml(self, attributes: Dict[str, Any]) -> str:
        """Build custom attributes section for XML export"""
        if not attributes:
            return "<attribute />"
        
        xml_lines = []
        for key, value in attributes.items():
            xml_lines.append(f"""            <attribute name="{self._escape_xml(str(key))}">{self._escape_xml(str(value))}</attribute>""")
        return "\n".join(xml_lines)
    
    async def _build_export_info_section_xml(self, prepared_data: Dict[str, Any]) -> str:
        """Build export information section for XML export"""
        return f"""    <export_info>
        <export_format>{self._escape_xml(prepared_data.get('export_format', ''))}</export_format>
        <export_timestamp>{prepared_data.get('export_timestamp', '')}</export_timestamp>
        <generator>{self._escape_xml('Certificate Manager Export System')}</generator>
        <version>1.0</version>
    </export_info>"""
    
    async def _build_optional_sections_xml(self, prepared_data: Dict[str, Any], options: ExportOptions) -> str:
        """Build optional sections for XML export based on options"""
        xml_sections = []
        
        if options.include_metrics and "metrics" in prepared_data:
            xml_sections.append(await self._build_metrics_xml(prepared_data["metrics"]))
        
        if options.include_versions and "versions" in prepared_data:
            xml_sections.append(await self._build_versions_xml(prepared_data["versions"]))
        
        if options.include_lineage and "lineage" in prepared_data:
            xml_sections.append(await self._build_lineage_xml(prepared_data["lineage"]))
        
        if options.include_audit_trail and "audit_trail" in prepared_data:
            xml_sections.append(await self._build_audit_trail_xml(prepared_data["audit_trail"]))
        
        return "\n".join(xml_sections)
    
    async def _build_metrics_xml(self, metrics: Dict[str, Any]) -> str:
        """Build metrics section for XML export"""
        if not metrics:
            return "    <metrics />"
        
        xml_lines = ["    <metrics>"]
        for key, value in metrics.items():
            xml_lines.append(f"        <metric name=\"{self._escape_xml(str(key))}\">{self._escape_xml(str(value))}</metric>")
        xml_lines.append("    </metrics>")
        return "\n".join(xml_lines)
    
    async def _build_versions_xml(self, versions: List[Dict[str, Any]]) -> str:
        """Build versions section for XML export"""
        if not versions:
            return "    <versions />"
        
        xml_lines = ["    <versions>"]
        for version in versions:
            xml_lines.append(f"""        <version>
            <version_id>{self._escape_xml(str(version.get('version_id', '')))}</version_id>
            <version_number>{self._escape_xml(str(version.get('version_number', '')))}</version_number>
            <created_at>{self._escape_xml(str(version.get('created_at', '')))}</created_at>
        </version>""")
        xml_lines.append("    </versions>")
        return "\n".join(xml_lines)
    
    async def _build_lineage_xml(self, lineage: Dict[str, Any]) -> str:
        """Build lineage section for XML export"""
        if not lineage:
            return "    <lineage />"
        
        return f"""    <lineage>
        <data_sources>{self._escape_xml(str(lineage.get('data_sources', '')))}</data_sources>
        <dependencies>{self._escape_xml(str(lineage.get('dependencies', '')))}</dependencies>
        <provenance_level>{self._escape_xml(str(lineage.get('provenance_level', '')))}</provenance_level>
    </lineage>"""
    
    async def _build_audit_trail_xml(self, audit_trail: List[Dict[str, Any]]) -> str:
        """Build audit trail section for XML export"""
        if not audit_trail:
            return "    <audit_trail />"
        
        xml_lines = ["    <audit_trail>"]
        for audit_entry in audit_trail:
            xml_lines.append(f"""        <audit_entry>
            <action>{self._escape_xml(str(audit_entry.get('action', '')))}</action>
            <timestamp>{self._escape_xml(str(audit_entry.get('timestamp', '')))}</timestamp>
            <user_id>{self._escape_xml(str(audit_entry.get('user_id', '')))}</user_id>
        </audit_entry>""")
        xml_lines.append("    </audit_trail>")
        return "\n".join(xml_lines)
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        if not text:
            return ""
        
        text = str(text)
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        return text
    
    async def _save_xml_file(self, output_path: Path, xml_content: str) -> None:
        """Save XML content to file"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(xml_content, encoding='utf-8')
            logger.info(f"XML file saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save XML file: {e}")
            raise 