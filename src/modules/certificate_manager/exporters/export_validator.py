"""
Export Validator for Certificate Manager

Validates export formats and ensures data integrity for certificate exports.
Provides comprehensive validation for all export operations.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging

from .base_exporter import ExportFormat, ExportOptions

logger = logging.getLogger(__name__)


class ExportValidator:
    """
    Export validation service
    
    Validates export formats, data integrity, and export options
    to ensure successful certificate exports.
    """
    
    def __init__(self):
        """Initialize the export validator"""
        self.validation_rules = self._initialize_validation_rules()
        self.format_validators: Dict[ExportFormat, Dict[str, Any]] = {}
        
        logger.info("Export Validator initialized successfully")
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for different export aspects"""
        return {
            "certificate_data": {
                "required_fields": [
                    "certificate_id",
                    "certificate_name",
                    "status",
                    "created_at"
                ],
                "status_values": ["pending", "in_progress", "ready", "archived"],
                "completion_range": (0, 100),
                "quality_score_range": (0, 100),
                "security_score_range": (0, 100)
            },
            "export_options": {
                "compression_range": (0, 9),
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "supported_encryption": ["AES-256", "AES-128"],
                "max_custom_attributes": 100
            },
            "format_specific": {
                ExportFormat.HTML: {
                    "max_content_length": 10 * 1024 * 1024,  # 10MB
                    "allowed_tags": ["div", "span", "h1", "h2", "h3", "p", "table", "ul", "li"],
                    "max_nesting_depth": 10
                },
                ExportFormat.PDF: {
                    "max_page_count": 100,
                    "max_image_size": 5 * 1024 * 1024,  # 5MB
                    "supported_fonts": ["Helvetica", "Times", "Courier"]
                },
                ExportFormat.JSON: {
                    "max_depth": 20,
                    "max_array_length": 10000,
                    "max_string_length": 1024 * 1024  # 1MB
                },
                ExportFormat.XML: {
                    "max_element_depth": 20,
                    "max_attribute_count": 100,
                    "max_text_length": 1024 * 1024  # 1MB
                }
            }
        }
    
    async def validate_export_request(
        self,
        certificate_data: Dict[str, Any],
        export_format: ExportFormat,
        options: ExportOptions
    ) -> Dict[str, Any]:
        """
        Validate a complete export request
        
        Args:
            certificate_data: Certificate data to validate
            export_format: Export format to validate
            options: Export options to validate
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "format": export_format.value,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Validate certificate data
        data_validation = await self._validate_certificate_data(certificate_data)
        validation_result["errors"].extend(data_validation["errors"])
        validation_result["warnings"].extend(data_validation["warnings"])
        
        # Validate export options
        options_validation = await self._validate_export_options(options)
        validation_result["errors"].extend(options_validation["errors"])
        validation_result["warnings"].extend(options_validation["warnings"])
        
        # Validate format-specific requirements
        format_validation = await self._validate_format_specific(certificate_data, export_format, options)
        validation_result["errors"].extend(format_validation["errors"])
        validation_result["warnings"].extend(format_validation["warnings"])
        
        # Determine overall validity
        validation_result["valid"] = len(validation_result["errors"]) == 0
        
        # Add validation metadata
        validation_result["validation_summary"] = {
            "total_checks": len(data_validation["errors"]) + len(options_validation["errors"]) + len(format_validation["errors"]),
            "error_count": len(validation_result["errors"]),
            "warning_count": len(validation_result["warnings"]),
            "data_valid": len(data_validation["errors"]) == 0,
            "options_valid": len(options_validation["errors"]) == 0,
            "format_valid": len(format_validation["errors"]) == 0
        }
        
        return validation_result
    
    async def validate_certificate_data(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate certificate data structure and content
        
        Args:
            certificate_data: Certificate data to validate
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        rules = self.validation_rules["certificate_data"]
        
        # Check required fields
        missing_fields = []
        for field in rules["required_fields"]:
            if field not in certificate_data or certificate_data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing required fields: {missing_fields}")
        
        # Validate status values
        status = certificate_data.get("status")
        if status and status not in rules["status_values"]:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Invalid status value: {status}")
        
        # Validate completion percentage
        completion = certificate_data.get("completion_percentage")
        if completion is not None:
            if not isinstance(completion, (int, float)):
                validation_result["valid"] = False
                validation_result["errors"].append("Completion percentage must be numeric")
            elif not (rules["completion_range"][0] <= completion <= rules["completion_range"][1]):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Completion percentage must be between {rules['completion_range'][0]} and {rules['completion_range'][1]}")
        
        # Validate quality score
        quality_score = certificate_data.get("overall_quality_score")
        if quality_score is not None:
            if not isinstance(quality_score, (int, float)):
                validation_result["valid"] = False
                validation_result["errors"].append("Quality score must be numeric")
            elif not (rules["quality_score_range"][0] <= quality_score <= rules["quality_score_range"][1]):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Quality score must be between {rules['quality_score_range'][0]} and {rules['quality_score_range'][1]}")
        
        # Validate security score
        security_score = certificate_data.get("security_score")
        if security_score is not None:
            if not isinstance(security_score, (int, float)):
                validation_result["valid"] = False
                validation_result["errors"].append("Security score must be numeric")
            elif not (rules["security_score_range"][0] <= security_score <= rules["security_score_range"][1]):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Security score must be between {rules['security_score_range'][0]} and {rules['security_score_range'][1]}")
        
        # Validate module status structure
        if "module_status" in certificate_data:
            module_validation = await self._validate_module_status(certificate_data["module_status"])
            validation_result["errors"].extend(module_validation["errors"])
            validation_result["warnings"].extend(module_validation["warnings"])
        
        return validation_result
    
    async def validate_export_options(self, options: ExportOptions) -> Dict[str, Any]:
        """
        Validate export configuration options
        
        Args:
            options: Export options to validate
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        rules = self.validation_rules["export_options"]
        
        # Validate compression level
        if options.compression_level < rules["compression_range"][0] or options.compression_level > rules["compression_range"][1]:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Compression level must be between {rules['compression_range'][0]} and {rules['compression_range'][1]}")
        
        # Validate custom styling
        if options.custom_styling:
            styling_validation = await self._validate_custom_styling(options.custom_styling)
            validation_result["errors"].extend(styling_validation["errors"])
            validation_result["warnings"].extend(styling_validation["warnings"])
        
        # Validate custom attributes count
        if options.custom_styling and len(options.custom_styling) > rules["max_custom_attributes"]:
            validation_result["warnings"].append(f"Too many custom attributes: {len(options.custom_styling)} > {rules['max_custom_attributes']}")
        
        return validation_result
    
    async def validate_format_specific(
        self,
        certificate_data: Dict[str, Any],
        export_format: ExportFormat,
        options: ExportOptions
    ) -> Dict[str, Any]:
        """
        Validate format-specific requirements
        
        Args:
            certificate_data: Certificate data to validate
            export_format: Export format to validate
            options: Export options to validate
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if export_format not in self.validation_rules["format_specific"]:
            validation_result["warnings"].append(f"No specific validation rules for format: {export_format.value}")
            return validation_result
        
        rules = self.validation_rules["format_specific"][export_format]
        
        # Format-specific validations
        if export_format == ExportFormat.HTML:
            html_validation = await self._validate_html_specific(certificate_data, rules)
            validation_result["errors"].extend(html_validation["errors"])
            validation_result["warnings"].extend(html_validation["warnings"])
        
        elif export_format == ExportFormat.PDF:
            pdf_validation = await self._validate_pdf_specific(certificate_data, rules)
            validation_result["errors"].extend(pdf_validation["errors"])
            validation_result["warnings"].extend(pdf_validation["warnings"])
        
        elif export_format == ExportFormat.JSON:
            json_validation = await self._validate_json_specific(certificate_data, rules)
            validation_result["errors"].extend(json_validation["errors"])
            validation_result["warnings"].extend(json_validation["warnings"])
        
        elif export_format == ExportFormat.XML:
            xml_validation = await self._validate_xml_specific(certificate_data, rules)
            validation_result["errors"].extend(xml_validation["errors"])
            validation_result["warnings"].extend(xml_validation["warnings"])
        
        # Determine validity
        validation_result["valid"] = len(validation_result["errors"]) == 0
        
        return validation_result
    
    async def _validate_module_status(self, module_status: Dict[str, Any]) -> Dict[str, Any]:
        """Validate module status structure"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        for module_name, status_info in module_status.items():
            if isinstance(status_info, dict):
                # Validate status info structure
                if "status" in status_info:
                    status = status_info["status"]
                    if status not in ["pending", "in_progress", "completed", "failed"]:
                        validation_result["warnings"].append(f"Invalid module status for {module_name}: {status}")
                
                if "progress" in status_info:
                    progress = status_info["progress"]
                    if not isinstance(progress, (int, float)) or progress < 0 or progress > 100:
                        validation_result["errors"].append(f"Invalid progress value for {module_name}: {progress}")
        
        return validation_result
    
    async def _validate_custom_styling(self, custom_styling: Dict[str, Any]) -> Dict[str, Any]:
        """Validate custom styling options"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for invalid CSS properties
        invalid_properties = []
        for key in custom_styling.keys():
            if not self._is_valid_css_property(key):
                invalid_properties.append(key)
        
        if invalid_properties:
            validation_result["warnings"].append(f"Invalid CSS properties: {invalid_properties}")
        
        return validation_result
    
    async def _validate_html_specific(self, certificate_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate HTML-specific requirements"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check content length
        estimated_content_length = len(str(certificate_data)) * 10  # Rough estimate
        if estimated_content_length > rules["max_content_length"]:
            validation_result["warnings"].append(f"Estimated HTML content may exceed size limit: {estimated_content_length} > {rules['max_content_length']}")
        
        return validation_result
    
    async def _validate_pdf_specific(self, certificate_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PDF-specific requirements"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for large images or content
        if "module_data_snapshot" in certificate_data:
            snapshot_size = len(str(certificate_data["module_data_snapshot"]))
            if snapshot_size > rules["max_image_size"]:
                validation_result["warnings"].append(f"Module data snapshot may be too large for PDF: {snapshot_size} > {rules['max_image_size']}")
        
        return validation_result
    
    async def _validate_json_specific(self, certificate_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JSON-specific requirements"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check data depth
        max_depth = self._calculate_data_depth(certificate_data)
        if max_depth > rules["max_depth"]:
            validation_result["warnings"].append(f"Data structure may be too deep for JSON: {max_depth} > {rules['max_depth']}")
        
        return validation_result
    
    async def _validate_xml_specific(self, certificate_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate XML-specific requirements"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for special characters that might cause XML issues
        special_chars = self._find_xml_special_chars(certificate_data)
        if special_chars:
            validation_result["warnings"].append(f"Found XML special characters: {special_chars}")
        
        return validation_result
    
    def _is_valid_css_property(self, property_name: str) -> bool:
        """Check if a CSS property name is valid"""
        valid_properties = {
            "color", "background-color", "font-size", "font-family", "margin", "padding",
            "border", "border-radius", "text-align", "display", "position", "width", "height"
        }
        return property_name.lower() in valid_properties
    
    def _calculate_data_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate the maximum depth of nested data structures"""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._calculate_data_depth(value, current_depth + 1) for value in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._calculate_data_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth
    
    def _find_xml_special_chars(self, data: Any) -> List[str]:
        """Find XML special characters in data"""
        special_chars = []
        xml_chars = ["&", "<", ">", '"', "'"]
        
        def check_value(value):
            if isinstance(value, str):
                for char in xml_chars:
                    if char in value:
                        special_chars.append(char)
            elif isinstance(value, dict):
                for v in value.values():
                    check_value(v)
            elif isinstance(value, list):
                for item in value:
                    check_value(item)
        
        check_value(data)
        return list(set(special_chars))  # Remove duplicates
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the export validator"""
        return {
            "status": "healthy",
            "validation_rules_count": len(self.validation_rules),
            "format_validators_count": len(self.format_validators),
            "supported_formats": [fmt.value for fmt in ExportFormat],
            "timestamp": asyncio.get_event_loop().time()
        }
