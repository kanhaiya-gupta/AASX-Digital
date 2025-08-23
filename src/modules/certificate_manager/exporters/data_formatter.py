"""
Data Formatter for Certificate Manager

Handles data formatting for exports, including data transformation,
formatting utilities, and export-specific data preparation.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging
import json
from datetime import datetime

from .base_exporter import ExportFormat, ExportOptions

logger = logging.getLogger(__name__)


class DataFormatter:
    """
    Data formatting service for certificate exports
    
    Handles data transformation, formatting, and preparation
    for different export formats and requirements.
    """
    
    def __init__(self):
        """Initialize the data formatter"""
        self.formatting_templates = self._initialize_formatting_templates()
        self.data_transformers: Dict[ExportFormat, Dict[str, Any]] = {}
        
        logger.info("Data Formatter initialized successfully")
    
    def _initialize_formatting_templates(self) -> Dict[str, Any]:
        """Initialize formatting templates for different data types"""
        return {
            "date_formats": {
                "iso": "%Y-%m-%dT%H:%M:%SZ",
                "human": "%B %d, %Y at %I:%M %p",
                "short": "%Y-%m-%d",
                "time_only": "%H:%M:%S"
            },
            "number_formats": {
                "percentage": "{:.1f}%",
                "decimal": "{:.2f}",
                "integer": "{:d}",
                "scientific": "{:.2e}"
            },
            "text_formats": {
                "title_case": lambda x: x.replace("_", " ").title(),
                "sentence_case": lambda x: x.replace("_", " ").capitalize(),
                "camel_case": lambda x: "".join(word.capitalize() for word in x.split("_")),
                "snake_case": lambda x: x.lower().replace(" ", "_")
            }
        }
    
    async def format_certificate_data(
        self,
        certificate_data: Dict[str, Any],
        export_format: ExportFormat,
        options: ExportOptions
    ) -> Dict[str, Any]:
        """
        Format certificate data for export
        
        Args:
            certificate_data: Raw certificate data
            export_format: Target export format
            options: Export configuration options
            
        Returns:
            Formatted certificate data
        """
        try:
            # Create a copy to avoid modifying original data
            formatted_data = certificate_data.copy()
            
            # Apply basic formatting
            formatted_data = await self._apply_basic_formatting(formatted_data)
            
            # Apply format-specific formatting
            formatted_data = await self._apply_format_specific_formatting(
                formatted_data, export_format, options
            )
            
            # Apply custom styling if requested
            if options.custom_styling:
                formatted_data = await self._apply_custom_styling(
                    formatted_data, options.custom_styling, export_format
                )
            
            # Add formatting metadata
            formatted_data["_formatting_metadata"] = {
                "export_format": export_format.value,
                "formatted_at": asyncio.get_event_loop().time(),
                "formatting_options": options.__dict__,
                "formatter_version": "1.0"
            }
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Data formatting failed: {e}")
            raise
    
    async def _apply_basic_formatting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply basic formatting to certificate data"""
        formatted_data = data.copy()
        
        # Format dates
        formatted_data = await self._format_dates(formatted_data)
        
        # Format numbers
        formatted_data = await self._format_numbers(formatted_data)
        
        # Format text fields
        formatted_data = await self._format_text_fields(formatted_data)
        
        # Clean up data structure
        formatted_data = await self._clean_data_structure(formatted_data)
        
        return formatted_data
    
    async def _format_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format date fields in certificate data"""
        date_fields = ["created_at", "updated_at", "signature_timestamp", "last_update"]
        
        for field in date_fields:
            if field in data and data[field]:
                try:
                    # Try to parse and format the date
                    if isinstance(data[field], str):
                        # Assume ISO format and convert to human readable
                        parsed_date = datetime.fromisoformat(data[field].replace("Z", "+00:00"))
                        data[field] = parsed_date.strftime(self.formatting_templates["date_formats"]["human"])
                    elif isinstance(data[field], (int, float)):
                        # Assume timestamp
                        parsed_date = datetime.fromtimestamp(data[field])
                        data[field] = parsed_date.strftime(self.formatting_templates["date_formats"]["human"])
                except Exception as e:
                    logger.warning(f"Failed to format date field {field}: {e}")
                    # Keep original value if formatting fails
        
        return data
    
    async def _format_numbers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format number fields in certificate data"""
        number_fields = {
            "completion_percentage": "percentage",
            "overall_quality_score": "percentage",
            "security_score": "percentage",
            "progress": "percentage",
            "health_score": "percentage"
        }
        
        for field, format_type in number_fields.items():
            if field in data and data[field] is not None:
                try:
                    if isinstance(data[field], (int, float)):
                        template = self.formatting_templates["number_formats"][format_type]
                        data[field] = template.format(data[field])
                except Exception as e:
                    logger.warning(f"Failed to format number field {field}: {e}")
        
        return data
    
    async def _format_text_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format text fields in certificate data"""
        text_fields = {
            "certificate_name": "title_case",
            "status": "sentence_case",
            "compliance_status": "sentence_case"
        }
        
        for field, format_type in text_fields.items():
            if field in data and data[field]:
                try:
                    if isinstance(data[field], str):
                        formatter = self.formatting_templates["text_formats"][format_type]
                        data[field] = formatter(data[field])
                except Exception as e:
                    logger.warning(f"Failed to format text field {field}: {e}")
        
        return data
    
    async def _clean_data_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize data structure"""
        cleaned_data = {}
        
        for key, value in data.items():
            # Skip None values
            if value is None:
                continue
            
            # Clean key names
            clean_key = key.replace(" ", "_").lower()
            
            # Handle different value types
            if isinstance(value, dict):
                cleaned_data[clean_key] = await self._clean_data_structure(value)
            elif isinstance(value, list):
                cleaned_data[clean_key] = [
                    await self._clean_data_structure(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                cleaned_data[clean_key] = value
        
        return cleaned_data
    
    async def _apply_format_specific_formatting(
        self,
        data: Dict[str, Any],
        export_format: ExportFormat,
        options: ExportOptions
    ) -> Dict[str, Any]:
        """Apply format-specific formatting rules"""
        if export_format == ExportFormat.HTML:
            return await self._format_for_html(data, options)
        elif export_format == ExportFormat.PDF:
            return await self._format_for_pdf(data, options)
        elif export_format == ExportFormat.JSON:
            return await self._format_for_json(data, options)
        elif export_format == ExportFormat.XML:
            return await self._format_for_xml(data, options)
        else:
            return data
    
    async def _format_for_html(self, data: Dict[str, Any], options: ExportOptions) -> Dict[str, Any]:
        """Format data specifically for HTML export"""
        html_data = data.copy()
        
        # Add HTML-specific formatting
        if "module_status" in html_data:
            html_data["module_status"] = await self._format_module_status_for_html(
                html_data["module_status"]
            )
        
        # Add CSS classes for styling
        html_data["_css_classes"] = await self._generate_css_classes(html_data)
        
        return html_data
    
    async def _format_for_pdf(self, data: Dict[str, Any], options: ExportOptions) -> Dict[str, Any]:
        """Format data specifically for PDF export"""
        pdf_data = data.copy()
        
        # Ensure text fits within PDF constraints
        if "certificate_name" in pdf_data and len(pdf_data["certificate_name"]) > 100:
            pdf_data["certificate_name"] = pdf_data["certificate_name"][:97] + "..."
        
        # Add PDF-specific metadata
        pdf_data["_pdf_metadata"] = {
            "page_count": 1,
            "orientation": "portrait",
            "margins": {"top": 20, "bottom": 20, "left": 20, "right": 20}
        }
        
        return pdf_data
    
    async def _format_for_json(self, data: Dict[str, Any], options: ExportOptions) -> Dict[str, Any]:
        """Format data specifically for JSON export"""
        json_data = data.copy()
        
        # Ensure JSON serialization compatibility
        json_data = await self._ensure_json_compatibility(json_data)
        
        # Add JSON schema information
        json_data["_json_schema"] = {
            "version": "1.0",
            "type": "object",
            "properties": await self._generate_json_schema(json_data)
        }
        
        return json_data
    
    async def _format_for_xml(self, data: Dict[str, Any], options: ExportOptions) -> Dict[str, Any]:
        """Format data specifically for XML export"""
        xml_data = data.copy()
        
        # Ensure XML compatibility
        xml_data = await self._ensure_xml_compatibility(xml_data)
        
        # Add XML namespace information
        xml_data["_xml_namespaces"] = {
            "default": "http://certificate-manager.org/schema/v1.0",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }
        
        return xml_data
    
    async def _format_module_status_for_html(self, module_status: Dict[str, Any]) -> Dict[str, Any]:
        """Format module status specifically for HTML display"""
        formatted_status = {}
        
        for module_name, status_info in module_status.items():
            if isinstance(status_info, dict):
                formatted_status[module_name] = {
                    "status": status_info.get("status", "unknown"),
                    "progress": status_info.get("progress", 0),
                    "last_update": status_info.get("last_update"),
                    "status_class": self._get_status_css_class(status_info.get("status", "unknown")),
                    "progress_class": self._get_progress_css_class(status_info.get("progress", 0))
                }
            else:
                formatted_status[module_name] = {
                    "status": str(status_info),
                    "progress": 0,
                    "last_update": None,
                    "status_class": "status-unknown",
                    "progress_class": "progress-none"
                }
        
        return formatted_status
    
    async def _generate_css_classes(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate CSS classes for styling"""
        css_classes = {}
        
        # Generate status-based classes
        if "status" in data:
            css_classes["status"] = f"status-{data['status'].lower().replace(' ', '-')}"
        
        # Generate quality-based classes
        if "overall_quality_score" in data:
            quality_score = float(str(data["overall_quality_score"]).replace("%", ""))
            if quality_score >= 90:
                css_classes["quality"] = "quality-excellent"
            elif quality_score >= 80:
                css_classes["quality"] = "quality-good"
            elif quality_score >= 70:
                css_classes["quality"] = "quality-fair"
            else:
                css_classes["quality"] = "quality-poor"
        
        return css_classes
    
    def _get_status_css_class(self, status: str) -> str:
        """Get CSS class for status"""
        status_mapping = {
            "completed": "status-completed",
            "in_progress": "status-in-progress",
            "pending": "status-pending",
            "failed": "status-failed"
        }
        return status_mapping.get(status.lower(), "status-unknown")
    
    def _get_progress_css_class(self, progress: float) -> str:
        """Get CSS class for progress"""
        if progress >= 90:
            return "progress-complete"
        elif progress >= 70:
            return "progress-high"
        elif progress >= 40:
            return "progress-medium"
        elif progress >= 10:
            return "progress-low"
        else:
            return "progress-none"
    
    async def _ensure_json_compatibility(self, data: Any) -> Any:
        """Ensure data is JSON serializable"""
        if isinstance(data, dict):
            return {k: await self._ensure_json_compatibility(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [await self._ensure_json_compatibility(item) for item in data]
        elif isinstance(data, (datetime, datetime)):
            return data.isoformat()
        elif isinstance(data, (int, float, str, bool)) or data is None:
            return data
        else:
            return str(data)
    
    async def _ensure_xml_compatibility(self, data: Any) -> Any:
        """Ensure data is XML compatible"""
        if isinstance(data, dict):
            return {k: await self._ensure_xml_compatibility(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [await self._ensure_xml_compatibility(item) for item in data]
        elif isinstance(data, str):
            # Escape XML special characters
            return data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        else:
            return str(data)
    
    async def _generate_json_schema(self, data: Any) -> Dict[str, Any]:
        """Generate JSON schema for data structure"""
        if isinstance(data, dict):
            properties = {}
            for key, value in data.items():
                if not key.startswith("_"):  # Skip metadata fields
                    properties[key] = await self._generate_json_schema(value)
            return {
                "type": "object",
                "properties": properties
            }
        elif isinstance(data, list):
            if data:
                return {
                    "type": "array",
                    "items": await self._generate_json_schema(data[0])
                }
            else:
                return {"type": "array"}
        elif isinstance(data, bool):
            return {"type": "boolean"}
        elif isinstance(data, int):
            return {"type": "integer"}
        elif isinstance(data, float):
            return {"type": "number"}
        elif isinstance(data, str):
            return {"type": "string"}
        else:
            return {"type": "string"}
    
    async def transform_data_for_export(
        self,
        data: Dict[str, Any],
        transformation_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform data according to specific transformation rules
        
        Args:
            data: Data to transform
            transformation_rules: Rules for transformation
            
        Returns:
            Transformed data
        """
        transformed_data = data.copy()
        
        for field, rule in transformation_rules.items():
            if field in transformed_data:
                try:
                    if rule.get("type") == "format":
                        transformed_data[field] = await self._apply_format_rule(
                            transformed_data[field], rule
                        )
                    elif rule.get("type") == "transform":
                        transformed_data[field] = await self._apply_transform_rule(
                            transformed_data[field], rule
                        )
                    elif rule.get("type") == "calculate":
                        transformed_data[field] = await self._apply_calculation_rule(
                            transformed_data, rule
                        )
                except Exception as e:
                    logger.warning(f"Failed to apply transformation rule for {field}: {e}")
        
        return transformed_data
    
    async def _apply_format_rule(self, value: Any, rule: Dict[str, Any]) -> Any:
        """Apply a formatting rule to a value"""
        format_type = rule.get("format")
        
        if format_type == "date" and rule.get("style"):
            date_style = rule["style"]
            if date_style in self.formatting_templates["date_formats"]:
                if isinstance(value, str):
                    try:
                        parsed_date = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        return parsed_date.strftime(self.formatting_templates["date_formats"][date_style])
                    except:
                        return value
                elif isinstance(value, (int, float)):
                    parsed_date = datetime.fromtimestamp(value)
                    return parsed_date.strftime(self.formatting_templates["date_formats"][date_style])
        
        elif format_type == "number" and rule.get("style"):
            number_style = rule["style"]
            if number_style in self.formatting_templates["number_formats"]:
                if isinstance(value, (int, float)):
                    template = self.formatting_templates["number_formats"][number_style]
                    return template.format(value)
        
        return value
    
    async def _apply_transform_rule(self, value: Any, rule: Dict[str, Any]) -> Any:
        """Apply a transformation rule to a value"""
        transform_type = rule.get("transform")
        
        if transform_type == "text_case" and rule.get("style"):
            text_style = rule["style"]
            if text_style in self.formatting_templates["text_formats"]:
                if isinstance(value, str):
                    formatter = self.formatting_templates["text_formats"][text_style]
                    return formatter(value)
        
        return value
    
    async def _apply_calculation_rule(self, data: Dict[str, Any], rule: Dict[str, Any]) -> Any:
        """Apply a calculation rule to data"""
        calculation_type = rule.get("calculation")
        
        if calculation_type == "sum":
            fields = rule.get("fields", [])
            total = sum(data.get(field, 0) for field in fields if isinstance(data.get(field), (int, float)))
            return total
        
        elif calculation_type == "average":
            fields = rule.get("fields", [])
            values = [data.get(field, 0) for field in fields if isinstance(data.get(field), (int, float))]
            if values:
                return sum(values) / len(values)
            return 0
        
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the data formatter"""
        return {
            "status": "healthy",
            "formatting_templates_count": len(self.formatting_templates),
            "data_transformers_count": len(self.data_transformers),
            "supported_formats": [fmt.value for fmt in ExportFormat],
            "timestamp": asyncio.get_event_loop().time()
        }
