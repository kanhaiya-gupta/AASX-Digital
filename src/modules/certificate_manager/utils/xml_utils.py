"""
XML Generation Utilities

This module provides comprehensive XML generation, styling, and management utilities
for certificates and other document types.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class XMLTemplate(Enum):
    """XML template types for different document types"""
    CERTIFICATE = "certificate"
    REPORT = "report"
    CONFIGURATION = "configuration"
    DATA_EXPORT = "data_export"
    API_RESPONSE = "api_response"
    FEED = "feed"
    MANIFEST = "manifest"
    SCHEMA = "schema"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"


class XMLStyle(Enum):
    """XML styling options"""
    COMPACT = "compact"
    READABLE = "readable"
    MINIMAL = "minimal"
    DETAILED = "detailed"
    STANDARD = "standard"
    CUSTOM = "custom"
    SCHEMA_COMPLIANT = "schema_compliant"
    NAMESPACE_AWARE = "namespace_aware"
    ATTRIBUTE_HEAVY = "attribute_heavy"
    ELEMENT_HEAVY = "element_heavy"


@dataclass
class XMLConfig:
    """Configuration for XML generation"""
    encoding: str = "UTF-8"
    indent: int = 2
    declaration: bool = True
    namespaces: Dict[str, str] = None
    schema_location: Optional[str] = None
    dtd_public: Optional[str] = None
    dtd_system: Optional[str] = None
    cdata_sections: bool = False
    attribute_order: List[str] = None
    element_order: List[str] = None


class XMLGenerator:
    """
    XML generation and management utility
    
    Handles:
    - XML generation from various data sources
    - Template-based document creation
    - Custom styling and formatting
    - Batch generation and validation
    - XML metadata management
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the XML generator utility"""
        self.xml_templates = list(XMLTemplate)
        self.xml_styles = list(XMLStyle)
        
        # XML storage and metadata
        self.generated_xml: Dict[str, Dict[str, Any]] = {}
        self.xml_templates_config: Dict[str, Dict[str, Any]] = {}
        self.generation_history: List[Dict[str, Any]] = []
        
        # Generation locks and queues
        self.generation_locks: Dict[str, asyncio.Lock] = {}
        self.generation_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.generation_stats = {
            "total_generated": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0.0,
            "total_size_bytes": 0
        }
        
        # Initialize default templates
        self._initialize_default_templates()
        
        logger.info("XML Generator utility initialized successfully")
    
    async def generate_xml(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: XMLTemplate = XMLTemplate.CERTIFICATE,
        style: XMLStyle = XMLStyle.READABLE,
        config: Optional[XMLConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an XML document with the specified content and configuration
        
        Args:
            content: Content to include in the XML
            template: XML template to use
            style: XML styling to apply
            config: XML configuration
            metadata: Additional metadata for the XML
            
        Returns:
            Dictionary containing XML information and generated data
        """
        start_time = time.time()
        xml_id = f"xml_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_generation_params(content, template, style, config)
            
            # Prepare content for XML generation
            prepared_content = await self._prepare_content_for_xml(content, template)
            
            # Apply configuration and styling
            xml_config = config or self._get_default_config(template, style)
            
            # Generate XML (simulated)
            xml_data = await self._generate_xml_data(prepared_content, xml_config, style)
            
            # Create metadata
            xml_metadata = await self._create_xml_metadata(
                xml_id, content, template, style, xml_config, metadata
            )
            
            # Store generated XML
            xml_info = {
                "id": xml_id,
                "content": prepared_content,
                "template": template.value,
                "style": style.value,
                "config": xml_config.__dict__,
                "metadata": xml_metadata,
                "generated_at": time.time(),
                "size_bytes": len(str(xml_data)),
                "status": "success"
            }
            
            self.generated_xml[xml_id] = xml_info
            self.generation_history.append(xml_info)
            
            # Update statistics
            await self._update_generation_stats(True, time.time() - start_time, len(str(xml_data)))
            
            logger.info(f"XML generated successfully: {xml_id}")
            return xml_info
            
        except Exception as e:
            await self._update_generation_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to generate XML: {str(e)}")
            raise
    
    async def generate_batch_xml(
        self,
        content_list: List[Union[str, Dict[str, Any], List[Dict[str, Any]]]],
        template: XMLTemplate = XMLTemplate.CERTIFICATE,
        style: XMLStyle = XMLStyle.READABLE,
        config: Optional[XMLConfig] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple XML documents in batch
        
        Args:
            content_list: List of content items to convert to XML
            template: XML template to use
            style: XML styling to apply
            config: XML configuration
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of generated XML information
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch XML generation: {batch_id}")
        
        # Create tasks for concurrent generation
        tasks = []
        for i, content in enumerate(content_list):
            task = asyncio.create_task(
                self.generate_xml(content, template, style, config, {
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
                logger.error(f"Failed to generate XML {i} in batch {batch_id}: {str(result)}")
                results.append({
                    "id": f"failed_{batch_id}_{i}",
                    "status": "failed",
                    "error": str(result),
                    "batch_id": batch_id,
                    "batch_index": i
                })
            else:
                results.append(result)
        
        logger.info(f"Batch XML generation completed: {batch_id}, {len(results)} results")
        return results
    
    async def generate_xml_from_template(
        self,
        template_name: str,
        template_data: Dict[str, Any],
        style: XMLStyle = XMLStyle.READABLE,
        config: Optional[XMLConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an XML document using a predefined template
        
        Args:
            template_name: Name of the template to use
            template_data: Data to populate the template
            style: XML styling to apply
            config: XML configuration
            metadata: Additional metadata for the XML
            
        Returns:
            Dictionary containing XML information and generated data
        """
        if template_name not in self.xml_templates_config:
            raise ValueError(f"Template not found: {template_name}")
        
        template_config = self.xml_templates_config[template_name]
        
        # Merge template data with provided data
        merged_data = {**template_config.get("default_data", {}), **template_data}
        
        # Use template's default template type
        template_type = XMLTemplate(template_config.get("template_type", "certificate"))
        
        return await self.generate_xml(
            merged_data, template_type, style, config, metadata
        )
    
    async def validate_xml(self, xml_id: str) -> Dict[str, Any]:
        """
        Validate a generated XML document
        
        Args:
            xml_id: ID of the XML document to validate
            
        Returns:
            Validation result information
        """
        if xml_id not in self.generated_xml:
            raise ValueError(f"XML document not found: {xml_id}")
        
        xml_info = self.generated_xml[xml_id]
        
        # Perform validation checks
        validation_result = await self._perform_validation_checks(xml_info)
        
        return {
            "xml_id": xml_id,
            "validation_result": validation_result,
            "validated_at": time.time(),
            "status": "validated"
        }
    
    async def get_xml_info(self, xml_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a generated XML document
        
        Args:
            xml_id: ID of the XML document
            
        Returns:
            XML document information
        """
        if xml_id not in self.generated_xml:
            raise ValueError(f"XML document not found: {xml_id}")
        
        return self.generated_xml[xml_id]
    
    async def get_xml_history(
        self,
        template: Optional[XMLTemplate] = None,
        style: Optional[XMLStyle] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get XML generation history
        
        Args:
            template: Filter by XML template
            style: Filter by XML style
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of XML history entries
        """
        history = self.generation_history
        
        if template:
            history = [h for h in history if h.get("template") == template.value]
        
        if style:
            history = [h for h in history if h.get("style") == style.value]
        
        # Sort by generation time (newest first)
        history.sort(key=lambda x: x.get("generated_at", 0), reverse=True)
        
        return history[offset:offset + limit]
    
    async def create_xml_template(
        self,
        template_name: str,
        template_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a reusable XML template
        
        Args:
            template_name: Name of the template
            template_config: Template configuration
            
        Returns:
            Template creation result
        """
        if template_name in self.xml_templates_config:
            raise ValueError(f"Template already exists: {template_name}")
        
        self.xml_templates_config[template_name] = template_config
        
        return {
            "template_name": template_name,
            "config": template_config,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Get XML generation statistics
        
        Returns:
            Generation statistics
        """
        return self.generation_stats.copy()
    
    async def cleanup_expired_xml(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired XML documents
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of XML documents cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_xml = []
        for xml_id, xml_info in self.generated_xml.items():
            if current_time - xml_info.get("generated_at", 0) > max_age_seconds:
                expired_xml.append(xml_id)
        
        # Remove expired XML documents
        for xml_id in expired_xml:
            del self.generated_xml[xml_id]
        
        logger.info(f"Cleaned up {len(expired_xml)} expired XML documents")
        return len(expired_xml)
    
    # Private helper methods
    
    def _initialize_default_templates(self):
        """Initialize default XML templates"""
        # Certificate template
        self.xml_templates_config["certificate"] = {
            "template_type": "certificate",
            "default_data": {
                "root_element": "certificate",
                "title": "Certificate of Completion",
                "subtitle": "This is to certify that",
                "signature_line": "Authorized Signature",
                "date_format": "YYYY-MM-DD"
            },
            "structure": ["header", "content", "signature", "footer"],
            "namespaces": {"cert": "http://example.com/certificate"}
        }
        
        # Configuration template
        self.xml_templates_config["configuration"] = {
            "template_type": "configuration",
            "default_data": {
                "root_element": "configuration",
                "version": "1.0",
                "environment": "production",
                "debug": False
            },
            "structure": ["settings", "parameters", "options"],
            "namespaces": {"config": "http://example.com/configuration"}
        }
        
        # Data export template
        self.xml_templates_config["data_export"] = {
            "template_type": "data_export",
            "default_data": {
                "root_element": "data_export",
                "export_date": "YYYY-MM-DD",
                "source": "database",
                "format": "xml"
            },
            "structure": ["metadata", "data", "summary"],
            "namespaces": {"export": "http://example.com/export"}
        }
    
    def _get_default_config(self, template: XMLTemplate, style: XMLStyle) -> XMLConfig:
        """Get default configuration for template and style combination"""
        if template == XMLTemplate.CERTIFICATE:
            return XMLConfig(
                encoding="UTF-8",
                indent=2,
                declaration=True,
                namespaces={"cert": "http://example.com/certificate"},
                cdata_sections=False
            )
        elif template == XMLTemplate.CONFIGURATION:
            return XMLConfig(
                encoding="UTF-8",
                indent=4,
                declaration=True,
                namespaces={"config": "http://example.com/configuration"},
                cdata_sections=False
            )
        else:
            return XMLConfig()
    
    async def _validate_generation_params(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: XMLTemplate,
        style: XMLStyle,
        config: Optional[XMLConfig]
    ):
        """Validate XML generation parameters"""
        if not content:
            raise ValueError("Content cannot be empty")
        
        if not isinstance(template, XMLTemplate):
            raise ValueError("Invalid XML template")
        
        if not isinstance(style, XMLStyle):
            raise ValueError("Invalid XML style")
        
        if config and not isinstance(config, XMLConfig):
            raise ValueError("Invalid configuration object")
    
    async def _prepare_content_for_xml(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: XMLTemplate
    ) -> Dict[str, Any]:
        """Prepare content for XML generation based on template"""
        if isinstance(content, str):
            return {"text_content": content}
        elif isinstance(content, dict):
            return content
        elif isinstance(content, list):
            return {"list_content": content}
        else:
            return {"raw_content": str(content)}
    
    async def _generate_xml_data(
        self,
        content: Dict[str, Any],
        config: XMLConfig,
        style: XMLStyle
    ) -> str:
        """Generate XML data (simulated)"""
        # Simulate XML generation
        root_element = content.get("root_element", "document")
        xml_data = f"<?xml version='1.0' encoding='{config.encoding}'?>\n<{root_element}>{content}</{root_element}>"
        
        # Apply configuration
        if config.indent > 0:
            xml_data = xml_data.replace(">", ">\n" + " " * config.indent)
        
        if config.namespaces:
            for prefix, uri in config.namespaces.items():
                xml_data = xml_data.replace(f"<{root_element}", f"<{root_element} xmlns:{prefix}='{uri}'")
        
        # Apply styling
        if style != XMLStyle.READABLE:
            xml_data += f"<!-- Style: {style.value} -->"
        
        return xml_data
    
    async def _create_xml_metadata(
        self,
        xml_id: str,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: XMLTemplate,
        style: XMLStyle,
        config: XMLConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for the generated XML"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "template": template.value,
            "style": style.value,
            "config_hash": hash(str(config.__dict__)),
            "content_hash": hash(str(content)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _perform_validation_checks(self, xml_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform validation checks on an XML document"""
        checks = {
            "content_integrity": True,
            "template_validity": True,
            "style_validity": True,
            "config_validity": True,
            "metadata_completeness": True,
            "size_appropriateness": True,
            "xml_structure": True,
            "encoding_validity": True
        }
        
        # Check content integrity
        if not xml_info.get("content"):
            checks["content_integrity"] = False
        
        # Check template validity
        if not xml_info.get("template"):
            checks["template_validity"] = False
        
        # Check style validity
        if not xml_info.get("style"):
            checks["style_validity"] = False
        
        # Check config validity
        config = xml_info.get("config", {})
        if not config.get("encoding"):
            checks["config_validity"] = False
        
        # Check metadata completeness
        metadata = xml_info.get("metadata", {})
        required_fields = ["generator", "version", "timestamp"]
        for field in required_fields:
            if field not in metadata:
                checks["metadata_completeness"] = False
                break
        
        # Check size appropriateness
        content_size = len(str(xml_info.get("content", "")))
        if content_size > 1000000:  # 1MB limit
            checks["size_appropriateness"] = False
        
        # Check XML structure
        xml_data = xml_info.get("xml_data", "")
        if not xml_data.startswith("<?xml") or not xml_data.endswith("</"):
            checks["xml_structure"] = False
        
        # Check encoding validity
        if "encoding=" not in xml_data:
            checks["encoding_validity"] = False
        
        return checks
    
    async def _update_generation_stats(self, success: bool, generation_time: float, size_bytes: int):
        """Update generation statistics"""
        self.generation_stats["total_generated"] += 1
        
        if success:
            self.generation_stats["successful"] += 1
            self.generation_stats["total_size_bytes"] += size_bytes
        else:
            self.generation_stats["failed"] += 1
        
        # Update average generation time
        total_successful = self.generation_stats["successful"]
        if total_successful > 0:
            current_avg = self.generation_stats["average_time"]
            self.generation_stats["average_time"] = (
                (current_avg * (total_successful - 1) + generation_time) / total_successful
            )
