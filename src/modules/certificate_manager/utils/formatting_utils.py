"""
Formatting Utilities

This module provides comprehensive formatting utilities for data formatting, styling,
and format management.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class FormatType(Enum):
    """Format types for different data formats"""
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    CSV = "csv"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TABLE = "table"
    LIST = "list"
    CUSTOM = "custom"


class FormatStyle(Enum):
    """Format styling options"""
    PLAIN = "plain"
    PRETTY = "pretty"
    COMPACT = "compact"
    DETAILED = "detailed"
    STANDARD = "standard"
    CUSTOM = "custom"
    COLORED = "colored"
    STRUCTURED = "structured"
    MINIMAL = "minimal"
    VERBOSE = "verbose"


@dataclass
class FormatConfig:
    """Configuration for data formatting"""
    format_type: FormatType = FormatType.TEXT
    style: FormatStyle = FormatStyle.STANDARD
    indent: int = 2
    sort_keys: bool = False
    include_metadata: bool = True
    max_line_length: int = 80
    encoding: str = "UTF-8"
    line_ending: str = "\n"
    custom_template: Optional[str] = None


class FormattingUtils:
    """
    Formatting utilities and management service
    
    Handles:
    - Data formatting using various formats and styles
    - Custom format template creation
    - Format result management
    - Batch formatting operations
    - Format configuration storage
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the formatting utilities service"""
        self.format_types = list(FormatType)
        self.format_styles = list(FormatStyle)
        
        # Formatting storage and metadata
        self.format_templates: Dict[str, Dict[str, Any]] = {}
        self.formatting_history: List[Dict[str, Any]] = []
        self.custom_formatters: Dict[str, callable] = {}
        
        # Formatting locks and queues
        self.formatting_locks: Dict[str, asyncio.Lock] = {}
        self.formatting_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.formatting_stats = {
            "total_formatted": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0.0,
            "total_data_size": 0
        }
        
        # Initialize default format templates
        self._initialize_default_templates()
        
        logger.info("Formatting utilities service initialized successfully")
    
    async def format_data(
        self,
        data: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        format_type: FormatType = FormatType.TEXT,
        style: FormatStyle = FormatStyle.STANDARD,
        config: Optional[FormatConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format data using the specified format type and style
        
        Args:
            data: Data to format
            format_type: Format type to use
            style: Format style to apply
            config: Format configuration
            metadata: Additional metadata for the formatting
            
        Returns:
            Dictionary containing formatted data and metadata
        """
        start_time = time.time()
        format_id = f"format_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_formatting_params(data, format_type, style, config)
            
            # Prepare data for formatting
            prepared_data = await self._prepare_data_for_formatting(data, format_type)
            
            # Apply configuration and styling
            format_config = config or self._get_default_config(format_type, style)
            
            # Format data
            formatted_data = await self._format_data(prepared_data, format_config, style)
            
            # Create metadata
            format_metadata = await self._create_format_metadata(
                format_id, data, format_type, style, format_config, metadata
            )
            
            # Store formatting results
            format_info = {
                "id": format_id,
                "original_data": prepared_data,
                "formatted_data": formatted_data,
                "format_type": format_type.value,
                "style": style.value,
                "config": format_config.__dict__,
                "metadata": format_metadata,
                "formatted_at": time.time(),
                "size_bytes": len(str(formatted_data)),
                "status": "success"
            }
            
            self.formatting_history.append(format_info)
            
            # Update statistics
            await self._update_formatting_stats(True, time.time() - start_time, len(str(formatted_data)))
            
            logger.info(f"Data formatting completed successfully: {format_id}")
            return format_info
            
        except Exception as e:
            await self._update_formatting_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to format data: {str(e)}")
            raise
    
    async def format_batch_data(
        self,
        data_list: List[Union[str, Dict[str, Any], List[Dict[str, Any]]]],
        format_type: FormatType = FormatType.TEXT,
        style: FormatStyle = FormatStyle.STANDARD,
        config: Optional[FormatConfig] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Format multiple data items in batch
        
        Args:
            data_list: List of data items to format
            format_type: Format type to use
            style: Format style to apply
            config: Format configuration
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of formatting results
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch data formatting: {batch_id}")
        
        # Create tasks for concurrent formatting
        tasks = []
        for i, data in enumerate(data_list):
            task = asyncio.create_task(
                self.format_data(data, format_type, style, config, {
                    "batch_id": batch_id,
                    "batch_index": i,
                    **(batch_metadata or {})
                })
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to format data {i} in batch {batch_id}: {str(result)}")
                results.append({
                    "id": f"failed_{batch_id}_{i}",
                    "status": "failed",
                    "error": str(result),
                    "batch_id": batch_id,
                    "batch_index": i
                })
            else:
                results.append(result)
        
        logger.info(f"Batch data formatting completed: {batch_id}, {len(results)} results")
        return results
    
    async def format_data_from_template(
        self,
        template_name: str,
        template_data: Dict[str, Any],
        style: FormatStyle = FormatStyle.STANDARD,
        config: Optional[FormatConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format data using a predefined template
        
        Args:
            template_name: Name of the template to use
            template_data: Data to populate the template
            style: Format style to apply
            config: Format configuration
            metadata: Additional metadata for the formatting
            
        Returns:
            Dictionary containing formatting results and metadata
        """
        if template_name not in self.format_templates:
            raise ValueError(f"Template not found: {template_name}")
        
        template_config = self.format_templates[template_name]
        
        # Merge template data with provided data
        merged_data = {**template_config.get("default_data", {}), **template_data}
        
        # Use template's default format type
        format_type = FormatType(template_config.get("format_type", "text"))
        
        return await self.format_data(
            merged_data, format_type, style, config, metadata
        )
    
    async def create_format_template(
        self,
        template_name: str,
        template_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a reusable format template
        
        Args:
            template_name: Name of the template
            template_config: Template configuration
            
        Returns:
            Template creation result
        """
        if template_name in self.format_templates:
            raise ValueError(f"Template already exists: {template_name}")
        
        self.format_templates[template_name] = template_config
        
        return {
            "template_name": template_name,
            "config": template_config,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def add_custom_formatter(
        self,
        formatter_name: str,
        formatter_func: callable
    ) -> Dict[str, Any]:
        """
        Add a custom formatter function
        
        Args:
            formatter_name: Name of the custom formatter
            formatter_func: Formatter function
            
        Returns:
            Formatter addition result
        """
        if formatter_name in self.custom_formatters:
            raise ValueError(f"Custom formatter already exists: {formatter_name}")
        
        self.custom_formatters[formatter_name] = formatter_func
        
        return {
            "formatter_name": formatter_name,
            "added_at": time.time(),
            "status": "added"
        }
    
    async def get_format_info(self, format_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a formatting operation
        
        Args:
            format_id: ID of the formatting operation
            
        Returns:
            Formatting operation information
        """
        for format_info in self.formatting_history:
            if format_info.get("id") == format_id:
                return format_info
        
        raise ValueError(f"Formatting operation not found: {format_id}")
    
    async def get_format_history(
        self,
        format_type: Optional[FormatType] = None,
        style: Optional[FormatStyle] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get formatting operation history
        
        Args:
            format_type: Filter by format type
            style: Filter by format style
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of formatting operation history entries
        """
        history = self.formatting_history
        
        if format_type:
            history = [h for h in history if h.get("format_type") == format_type.value]
        
        if style:
            history = [h for h in history if h.get("style") == style.value]
        
        # Sort by formatting time (newest first)
        history.sort(key=lambda x: x.get("formatted_at", 0), reverse=True)
        
        return history[offset:offset + limit]
    
    async def get_format_statistics(self) -> Dict[str, Any]:
        """
        Get formatting operation statistics
        
        Returns:
            Formatting operation statistics
        """
        return self.formatting_stats.copy()
    
    async def cleanup_expired_formats(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired formatting operations
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of formatting operations cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_formats = []
        for format_info in self.formatting_history:
            if current_time - format_info.get("formatted_at", 0) > max_age_seconds:
                expired_formats.append(format_info.get("id"))
        
        # Remove expired formatting operations
        self.formatting_history = [
            f for f in self.formatting_history
            if f.get("id") not in expired_formats
        ]
        
        logger.info(f"Cleaned up {len(expired_formats)} expired formatting operations")
        return len(expired_formats)
    
    # Private helper methods
    
    def _initialize_default_templates(self):
        """Initialize default format templates"""
        # Text template
        self.format_templates["text"] = {
            "format_type": "text",
            "default_data": {
                "title": "Document",
                "content": "Content goes here",
                "author": "Unknown",
                "date": "Unknown"
            },
            "structure": ["title", "content", "author", "date"],
            "separator": "\n\n"
        }
        
        # JSON template
        self.format_templates["json"] = {
            "format_type": "json",
            "default_data": {
                "id": "template_id",
                "name": "Template Name",
                "description": "Template Description",
                "version": "1.0"
            },
            "structure": ["id", "name", "description", "version"],
            "indent": 2
        }
        
        # Table template
        self.format_templates["table"] = {
            "format_type": "table",
            "default_data": {
                "headers": ["Column 1", "Column 2", "Column 3"],
                "rows": [["Data 1", "Data 2", "Data 3"]]
            },
            "structure": ["headers", "rows"],
            "separator": "|"
        }
    
    def _get_default_config(self, format_type: FormatType, style: FormatStyle) -> FormatConfig:
        """Get default configuration for format type and style combination"""
        if format_type == FormatType.JSON:
            return FormatConfig(
                format_type=format_type,
                style=style,
                indent=2,
                sort_keys=True,
                include_metadata=True
            )
        elif format_type == FormatType.TABLE:
            return FormatConfig(
                format_type=format_type,
                style=style,
                indent=0,
                sort_keys=False,
                include_metadata=False
            )
        else:
            return FormatConfig(
                format_type=format_type,
                style=style,
                indent=2,
                sort_keys=False,
                include_metadata=True
            )
    
    async def _validate_formatting_params(
        self,
        data: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        format_type: FormatType,
        style: FormatStyle,
        config: Optional[FormatConfig]
    ):
        """Validate formatting parameters"""
        if not data:
            raise ValueError("Data cannot be empty")
        
        if not isinstance(format_type, FormatType):
            raise ValueError("Invalid format type")
        
        if not isinstance(style, FormatStyle):
            raise ValueError("Invalid format style")
        
        if config and not isinstance(config, FormatConfig):
            raise ValueError("Invalid configuration object")
    
    async def _prepare_data_for_formatting(
        self,
        data: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        format_type: FormatType
    ) -> Dict[str, Any]:
        """Prepare data for formatting based on format type"""
        if isinstance(data, str):
            return {"text_content": data}
        elif isinstance(data, dict):
            return data
        elif isinstance(data, list):
            return {"list_content": data}
        else:
            return {"raw_data": str(data)}
    
    async def _format_data(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data using the specified configuration and style"""
        try:
            if config.format_type == FormatType.JSON:
                return await self._format_as_json(data, config, style)
            elif config.format_type == FormatType.TEXT:
                return await self._format_as_text(data, config, style)
            elif config.format_type == FormatType.TABLE:
                return await self._format_as_table(data, config, style)
            elif config.format_type == FormatType.XML:
                return await self._format_as_xml(data, config, style)
            elif config.format_type == FormatType.HTML:
                return await self._format_as_html(data, config, style)
            elif config.format_type == FormatType.CSV:
                return await self._format_as_csv(data, config, style)
            elif config.format_type == FormatType.YAML:
                return await self._format_as_yaml(data, config, style)
            elif config.format_type == FormatType.MARKDOWN:
                return await self._format_as_markdown(data, config, style)
            else:
                return await self._format_as_custom(data, config, style)
        
        except Exception as e:
            logger.error(f"Error formatting data: {str(e)}")
            return f"FORMATTING_ERROR: {str(e)}"
    
    async def _format_as_json(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data as JSON"""
        try:
            if style == FormatStyle.PRETTY:
                return json.dumps(data, indent=config.indent, sort_keys=config.sort_keys, ensure_ascii=False)
            elif style == FormatStyle.COMPACT:
                return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            else:
                return json.dumps(data, ensure_ascii=False)
        except Exception as e:
            return f"JSON_FORMATTING_ERROR: {str(e)}"
    
    async def _format_as_text(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data as text"""
        try:
            if style == FormatStyle.PRETTY:
                lines = []
                for key, value in data.items():
                    lines.append(f"{key}: {value}")
                return config.line_ending.join(lines)
            elif style == FormatStyle.COMPACT:
                return " ".join(f"{k}:{v}" for k, v in data.items())
            else:
                return str(data)
        except Exception as e:
            return f"TEXT_FORMATTING_ERROR: {str(e)}"
    
    async def _format_as_table(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data as table"""
        try:
            if "headers" in data and "rows" in data:
                headers = data["headers"]
                rows = data["rows"]
                
                if style == FormatStyle.PRETTY:
                    # Create a pretty table
                    separator = "+" + "+".join("-" * (len(h) + 2) for h in headers) + "+"
                    header_line = "|" + "|".join(f" {h} " for h in headers) + "|"
                    
                    lines = [separator, header_line, separator]
                    for row in rows:
                        row_line = "|" + "|".join(f" {str(cell)} " for cell in row) + "|"
                        lines.append(row_line)
                    lines.append(separator)
                    
                    return config.line_ending.join(lines)
                else:
                    # Create a simple table
                    lines = [config.separator.join(headers)]
                    for row in rows:
                        lines.append(config.separator.join(str(cell) for cell in row))
                    return config.line_ending.join(lines)
            else:
                return str(data)
        except Exception as e:
            return f"TABLE_FORMATTING_ERROR: {str(e)}"
    
    async def _format_as_xml(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data as XML"""
        try:
            if style == FormatStyle.PRETTY:
                xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<root>']
                for key, value in data.items():
                    xml_lines.append(f"{' ' * config.indent}<{key}>{value}</{key}>")
                xml_lines.append('</root>')
                return config.line_ending.join(xml_lines)
            else:
                xml_content = '<root>'
                for key, value in data.items():
                    xml_content += f"<{key}>{value}</{key}>"
                xml_content += '</root>'
                return xml_content
        except Exception as e:
            return f"XML_FORMATTING_ERROR: {str(e)}"
    
    async def _format_as_html(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data as HTML"""
        try:
            if style == FormatStyle.PRETTY:
                html_lines = [
                    '<!DOCTYPE html>',
                    '<html>',
                    '<head>',
                    f'{config.indent * " "}<title>Formatted Data</title>',
                    '</head>',
                    '<body>',
                    f'{config.indent * " "}<h1>Data</h1>',
                    f'{config.indent * " "}<ul>'
                ]
                for key, value in data.items():
                    html_lines.append(f'{config.indent * 2 * " "}<li><strong>{key}:</strong> {value}</li>')
                html_lines.extend([
                    f'{config.indent * " "}</ul>',
                    '</body>',
                    '</html>'
                ])
                return config.line_ending.join(html_lines)
            else:
                html_content = '<ul>'
                for key, value in data.items():
                    html_content += f'<li><strong>{key}:</strong> {value}</li>'
                html_content += '</ul>'
                return html_content
        except Exception as e:
            return f"HTML_FORMATTING_ERROR: {str(e)}"
    
    async def _format_as_csv(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data as CSV"""
        try:
            if style == FormatStyle.STRUCTURED:
                # Create structured CSV with headers
                headers = list(data.keys())
                values = list(data.values())
                return f"{','.join(headers)}{config.line_ending}{','.join(str(v) for v in values)}"
            else:
                # Create simple CSV
                return ','.join(f"{k},{v}" for k, v in data.items())
        except Exception as e:
            return f"CSV_FORMATTING_ERROR: {str(e)}"
    
    async def _format_as_yaml(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data as YAML"""
        try:
            if style == FormatStyle.PRETTY:
                yaml_lines = []
                for key, value in data.items():
                    yaml_lines.append(f"{key}: {value}")
                return config.line_ending.join(yaml_lines)
            else:
                return str(data).replace("'", "").replace("{", "").replace("}", "")
        except Exception as e:
            return f"YAML_FORMATTING_ERROR: {str(e)}"
    
    async def _format_as_markdown(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data as Markdown"""
        try:
            if style == FormatStyle.PRETTY:
                markdown_lines = ['# Data', '']
                for key, value in data.items():
                    markdown_lines.append(f"**{key}:** {value}")
                    markdown_lines.append('')
                return config.line_ending.join(markdown_lines)
            else:
                markdown_content = '# Data\n\n'
                for key, value in data.items():
                    markdown_content += f"**{key}:** {value}\n"
                return markdown_content
        except Exception as e:
            return f"MARKDOWN_FORMATTING_ERROR: {str(e)}"
    
    async def _format_as_custom(
        self,
        data: Dict[str, Any],
        config: FormatConfig,
        style: FormatStyle
    ) -> str:
        """Format data using custom formatter"""
        try:
            if config.custom_template:
                # Use custom template
                template = config.custom_template
                for key, value in data.items():
                    template = template.replace(f"{{{key}}}", str(value))
                return template
            else:
                # Use default custom formatting
                return f"CUSTOM_FORMAT: {data}"
        except Exception as e:
            return f"CUSTOM_FORMATTING_ERROR: {str(e)}"
    
    async def _create_format_metadata(
        self,
        format_id: str,
        data: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        format_type: FormatType,
        style: FormatStyle,
        config: FormatConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for formatting operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "format_type": format_type.value,
            "style": style.value,
            "config_hash": hash(str(config.__dict__)),
            "data_hash": hash(str(data)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _update_formatting_stats(self, success: bool, formatting_time: float, data_size: int):
        """Update formatting statistics"""
        self.formatting_stats["total_formatted"] += 1
        
        if success:
            self.formatting_stats["successful"] += 1
            self.formatting_stats["total_data_size"] += data_size
        else:
            self.formatting_stats["failed"] += 1
        
        # Update average formatting time
        total_successful = self.formatting_stats["successful"]
        if total_successful > 0:
            current_avg = self.formatting_stats["average_time"]
            self.formatting_stats["average_time"] = (
                (current_avg * (total_successful - 1) + formatting_time) / total_successful
            )
