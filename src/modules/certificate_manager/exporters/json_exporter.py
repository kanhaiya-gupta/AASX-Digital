"""
JSON Exporter for Certificate Manager

Generates JSON data for certificates in a structured format.
This exporter creates JSON data only - no UI rendering or styling.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

from .base_exporter import BaseExporter, ExportFormat, ExportOptions

logger = logging.getLogger(__name__)


class JSONExporter(BaseExporter):
    """
    JSON certificate exporter
    
    Generates structured JSON data for certificates including:
    - Certificate metadata and status
    - Module completion information
    - Quality and compliance metrics
    - Digital trust indicators
    - Export metadata
    """
    
    def __init__(self):
        """Initialize the JSON exporter"""
        super().__init__(ExportFormat.JSON)
        
        logger.info("JSON Exporter initialized successfully")
    
    async def export_certificate(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Export certificate to JSON format
        
        Args:
            certificate_data: Complete certificate data
            options: Export configuration options
            output_path: Optional path to save the JSON file
            
        Returns:
            Dictionary containing JSON data and export metadata
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
                
                # Generate JSON content
                json_content = await self._generate_json_content(prepared_data, options)
                
                # Generate export metadata
                export_metadata = await self._generate_export_metadata(prepared_data, options)
                
                # Create export result
                export_result = {
                    "format": "json",
                    "content": json_content,
                    "metadata": export_metadata,
                    "file_size": len(json_content.encode('utf-8')),
                    "mime_type": "application/json",
                    "file_extension": "json"
                }
                
                # Save to file if output path provided
                if output_path:
                    await self._save_json_file(output_path, json_content)
                    export_result["output_path"] = str(output_path)
                
                # Log successful export
                await self._log_export_operation(certificate_id, options, True)
                
                return export_result
                
            except Exception as e:
                error_msg = f"JSON export failed: {str(e)}"
                await self._log_export_operation(certificate_id, options, False, error_msg)
                raise
    
    async def validate_export_data(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> bool:
        """
        Validate certificate data for JSON export
        
        Args:
            certificate_data: Certificate data to validate
            options: Export options to validate against
            
        Returns:
            True if data is valid for JSON export
        """
        # Check required fields
        missing_fields = await self._validate_required_fields(certificate_data)
        if missing_fields:
            logger.warning(f"Missing required fields for JSON export: {missing_fields}")
            return False
        
        # Validate certificate status
        status = certificate_data.get("status")
        if status not in ["pending", "in_progress", "ready", "archived"]:
            logger.warning(f"Invalid certificate status for JSON export: {status}")
            return False
        
        # Validate completion percentage
        completion = certificate_data.get("completion_percentage", 0)
        if not isinstance(completion, (int, float)) or completion < 0 or completion > 100:
            logger.warning(f"Invalid completion percentage for JSON export: {completion}")
            return False
        
        return True
    
    async def get_export_metadata(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> Dict[str, Any]:
        """
        Get metadata about the JSON export operation
        
        Args:
            certificate_data: Certificate data being exported
            options: Export options being used
            
        Returns:
            Dictionary containing export metadata
        """
        return {
            "exporter_type": "JSONExporter",
            "export_format": "json",
            "mime_type": "application/json",
            "file_extension": "json",
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
    
    async def _generate_json_content(
        self,
        prepared_data: Dict[str, Any],
        options: ExportOptions
    ) -> str:
        """
        Generate JSON content from prepared certificate data
        
        Args:
            prepared_data: Prepared certificate data
            options: Export options
            
        Returns:
            JSON content as string
        """
        certificate_data = prepared_data["certificate_data"]
        
        # Build JSON structure
        json_structure = {
            "certificate": await self._build_certificate_section(certificate_data),
            "export_info": await self._build_export_info_section(prepared_data),
            "timestamp": prepared_data.get("export_timestamp")
        }
        
        # Add optional sections based on options
        if options.include_metrics and "metrics" in prepared_data:
            json_structure["metrics"] = prepared_data["metrics"]
        
        if options.include_versions and "versions" in prepared_data:
            json_structure["versions"] = prepared_data["versions"]
        
        if options.include_lineage and "lineage" in prepared_data:
            json_structure["lineage"] = prepared_data["lineage"]
        
        if options.include_audit_trail and "audit_trail" in prepared_data:
            json_structure["audit_trail"] = prepared_data["audit_trail"]
        
        # Generate JSON with proper formatting
        return json.dumps(json_structure, indent=2, ensure_ascii=False, default=str)
    
    async def _build_certificate_section(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build the main certificate section for JSON export"""
        return {
            "certificate_id": certificate_data.get("certificate_id"),
            "certificate_name": certificate_data.get("certificate_name"),
            "status": certificate_data.get("status"),
            "completion_percentage": certificate_data.get("completion_percentage"),
            "overall_quality_score": certificate_data.get("overall_quality_score"),
            "compliance_status": certificate_data.get("compliance_status"),
            "security_score": certificate_data.get("security_score"),
            "created_at": certificate_data.get("created_at"),
            "updated_at": certificate_data.get("updated_at"),
            "module_status": await self._build_module_status_section(certificate_data),
            "digital_trust": await self._build_digital_trust_section(certificate_data),
            "business_context": await self._build_business_context_section(certificate_data)
        }
    
    async def _build_module_status_section(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build module status section for JSON export"""
        if "module_status" not in certificate_data:
            return {}
        
        module_status = certificate_data["module_status"]
        formatted_status = {}
        
        for module_name, status_info in module_status.items():
            if isinstance(status_info, dict):
                formatted_status[module_name] = {
                    "status": status_info.get("status", "unknown"),
                    "progress": status_info.get("progress", 0),
                    "last_update": status_info.get("last_update"),
                    "error_count": status_info.get("error_count", 0),
                    "health_score": status_info.get("health_score", 0)
                }
            else:
                formatted_status[module_name] = {
                    "status": str(status_info),
                    "progress": 0,
                    "last_update": None,
                    "error_count": 0,
                    "health_score": 0
                }
        
        return formatted_status
    
    async def _build_digital_trust_section(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build digital trust section for JSON export"""
        return {
            "digital_signature": certificate_data.get("digital_signature"),
            "signature_timestamp": certificate_data.get("signature_timestamp"),
            "verification_hash": certificate_data.get("verification_hash"),
            "qr_code_data": certificate_data.get("qr_code_data"),
            "certificate_chain_status": certificate_data.get("certificate_chain_status"),
            "trust_score": certificate_data.get("trust_score", 0)
        }
    
    async def _build_business_context_section(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build business context section for JSON export"""
        return {
            "file_id": certificate_data.get("file_id"),
            "user_id": certificate_data.get("user_id"),
            "org_id": certificate_data.get("org_id"),
            "project_id": certificate_data.get("project_id"),
            "twin_id": certificate_data.get("twin_id"),
            "tags": certificate_data.get("tags", []),
            "custom_attributes": certificate_data.get("custom_attributes", {}),
            "ownership": certificate_data.get("ownership", {}),
            "approval_workflow": certificate_data.get("approval_workflow", {})
        }
    
    async def _build_export_info_section(self, prepared_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build export information section for JSON export"""
        return {
            "export_format": prepared_data.get("export_format"),
            "export_timestamp": prepared_data.get("export_timestamp"),
            "export_options": prepared_data.get("export_options", {}),
            "generator": "Certificate Manager Export System",
            "version": "1.0"
        }
    
    async def _save_json_file(self, output_path: Path, json_content: str) -> None:
        """Save JSON content to file"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json_content, encoding='utf-8')
            logger.info(f"JSON file saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON file: {e}")
            raise 