"""
HTML Generation Utilities

This module provides comprehensive HTML generation, styling, and management utilities
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


class HTMLTemplate(Enum):
    """HTML template types for different document types"""
    CERTIFICATE = "certificate"
    REPORT = "report"
    DASHBOARD = "dashboard"
    FORM = "form"
    PRESENTATION = "presentation"
    ARTICLE = "article"
    LANDING_PAGE = "landing_page"
    EMAIL = "email"
    DOCUMENTATION = "documentation"
    PORTFOLIO = "portfolio"


class HTMLStyle(Enum):
    """HTML styling options"""
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    CORPORATE = "corporate"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    ELEGANT = "elegant"
    RESPONSIVE = "responsive"
    DARK = "dark"
    LIGHT = "light"


@dataclass
class HTMLConfig:
    """Configuration for HTML generation"""
    doctype: str = "html5"
    charset: str = "UTF-8"
    viewport: str = "width=device-width, initial-scale=1.0"
    css_framework: str = "bootstrap"
    theme: str = "default"
    responsive: bool = True
    seo_optimized: bool = True
    accessibility: bool = True
    minify: bool = False
    inline_css: bool = False


class HTMLGenerator:
    """
    HTML generation and management utility
    
    Handles:
    - HTML generation from various data sources
    - Template-based document creation
    - Custom styling and branding
    - Batch generation and optimization
    - HTML metadata management
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the HTML generator utility"""
        self.html_templates = list(HTMLTemplate)
        self.html_styles = list(HTMLStyle)
        
        # HTML storage and metadata
        self.generated_html: Dict[str, Dict[str, Any]] = {}
        self.html_templates_config: Dict[str, Dict[str, Any]] = {}
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
        
        logger.info("HTML Generator utility initialized successfully")
    
    async def generate_html(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: HTMLTemplate = HTMLTemplate.CERTIFICATE,
        style: HTMLStyle = HTMLStyle.MODERN,
        config: Optional[HTMLConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an HTML document with the specified content and configuration
        
        Args:
            content: Content to include in the HTML
            template: HTML template to use
            style: HTML styling to apply
            config: HTML configuration
            metadata: Additional metadata for the HTML
            
        Returns:
            Dictionary containing HTML information and generated data
        """
        start_time = time.time()
        html_id = f"html_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_generation_params(content, template, style, config)
            
            # Prepare content for HTML generation
            prepared_content = await self._prepare_content_for_html(content, template)
            
            # Apply configuration and styling
            html_config = config or self._get_default_config(template, style)
            
            # Generate HTML (simulated)
            html_data = await self._generate_html_data(prepared_content, html_config, style)
            
            # Create metadata
            html_metadata = await self._create_html_metadata(
                html_id, content, template, style, html_config, metadata
            )
            
            # Store generated HTML
            html_info = {
                "id": html_id,
                "content": prepared_content,
                "template": template.value,
                "style": style.value,
                "config": html_config.__dict__,
                "metadata": html_metadata,
                "generated_at": time.time(),
                "size_bytes": len(str(html_data)),
                "status": "success"
            }
            
            self.generated_html[html_id] = html_info
            self.generation_history.append(html_info)
            
            # Update statistics
            await self._update_generation_stats(True, time.time() - start_time, len(str(html_data)))
            
            logger.info(f"HTML generated successfully: {html_id}")
            return html_info
            
        except Exception as e:
            await self._update_generation_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to generate HTML: {str(e)}")
            raise
    
    async def generate_batch_html(
        self,
        content_list: List[Union[str, Dict[str, Any], List[Dict[str, Any]]]],
        template: HTMLTemplate = HTMLTemplate.CERTIFICATE,
        style: HTMLStyle = HTMLStyle.MODERN,
        config: Optional[HTMLConfig] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple HTML documents in batch
        
        Args:
            content_list: List of content items to convert to HTML
            template: HTML template to use
            style: HTML styling to apply
            config: HTML configuration
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of generated HTML information
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch HTML generation: {batch_id}")
        
        # Create tasks for concurrent generation
        tasks = []
        for i, content in enumerate(content_list):
            task = asyncio.create_task(
                self.generate_html(content, template, style, config, {
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
                logger.error(f"Failed to generate HTML {i} in batch {batch_id}: {str(result)}")
                results.append({
                    "id": f"failed_{batch_id}_{i}",
                    "status": "failed",
                    "error": str(result),
                    "batch_id": batch_id,
                    "batch_index": i
                })
            else:
                results.append(result)
        
        logger.info(f"Batch HTML generation completed: {batch_id}, {len(results)} results")
        return results
    
    async def generate_html_from_template(
        self,
        template_name: str,
        template_data: Dict[str, Any],
        style: HTMLStyle = HTMLStyle.MODERN,
        config: Optional[HTMLConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an HTML document using a predefined template
        
        Args:
            template_name: Name of the template to use
            template_data: Data to populate the template
            style: HTML styling to apply
            config: HTML configuration
            metadata: Additional metadata for the HTML
            
        Returns:
            Dictionary containing HTML information and generated data
        """
        if template_name not in self.html_templates_config:
            raise ValueError(f"Template not found: {template_name}")
        
        template_config = self.html_templates_config[template_name]
        
        # Merge template data with provided data
        merged_data = {**template_config.get("default_data", {}), **template_data}
        
        # Use template's default template type
        template_type = HTMLTemplate(template_config.get("template_type", "certificate"))
        
        return await self.generate_html(
            merged_data, template_type, style, config, metadata
        )
    
    async def validate_html(self, html_id: str) -> Dict[str, Any]:
        """
        Validate a generated HTML document
        
        Args:
            html_id: ID of the HTML document to validate
            
        Returns:
            Validation result information
        """
        if html_id not in self.generated_html:
            raise ValueError(f"HTML document not found: {html_id}")
        
        html_info = self.generated_html[html_id]
        
        # Perform validation checks
        validation_result = await self._perform_validation_checks(html_info)
        
        return {
            "html_id": html_id,
            "validation_result": validation_result,
            "validated_at": time.time(),
            "status": "validated"
        }
    
    async def get_html_info(self, html_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a generated HTML document
        
        Args:
            html_id: ID of the HTML document
            
        Returns:
            HTML document information
        """
        if html_id not in self.generated_html:
            raise ValueError(f"HTML document not found: {html_id}")
        
        return self.generated_html[html_id]
    
    async def get_html_history(
        self,
        template: Optional[HTMLTemplate] = None,
        style: Optional[HTMLStyle] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get HTML generation history
        
        Args:
            template: Filter by HTML template
            style: Filter by HTML style
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of HTML history entries
        """
        history = self.generation_history
        
        if template:
            history = [h for h in history if h.get("template") == template.value]
        
        if style:
            history = [h for h in history if h.get("style") == style.value]
        
        # Sort by generation time (newest first)
        history.sort(key=lambda x: x.get("generated_at", 0), reverse=True)
        
        return history[offset:offset + limit]
    
    async def create_html_template(
        self,
        template_name: str,
        template_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a reusable HTML template
        
        Args:
            template_name: Name of the template
            template_config: Template configuration
            
        Returns:
            Template creation result
        """
        if template_name in self.html_templates_config:
            raise ValueError(f"Template already exists: {template_name}")
        
        self.html_templates_config[template_name] = template_config
        
        return {
            "template_name": template_name,
            "config": template_config,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Get HTML generation statistics
        
        Returns:
            Generation statistics
        """
        return self.generation_stats.copy()
    
    async def cleanup_expired_html(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired HTML documents
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of HTML documents cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_html = []
        for html_id, html_info in self.generated_html.items():
            if current_time - html_info.get("generated_at", 0) > max_age_seconds:
                expired_html.append(html_id)
        
        # Remove expired HTML documents
        for html_id in expired_html:
            del self.generated_html[html_id]
        
        logger.info(f"Cleaned up {len(expired_html)} expired HTML documents")
        return len(expired_html)
    
    # Private helper methods
    
    def _initialize_default_templates(self):
        """Initialize default HTML templates"""
        # Certificate template
        self.html_templates_config["certificate"] = {
            "template_type": "certificate",
            "default_data": {
                "title": "Certificate of Completion",
                "subtitle": "This is to certify that",
                "signature_line": "Authorized Signature",
                "date_format": "MMMM DD, YYYY",
                "logo_url": "/static/images/logo.png"
            },
            "sections": ["header", "content", "signature", "footer"],
            "css_classes": ["certificate", "elegant", "print-friendly"]
        }
        
        # Dashboard template
        self.html_templates_config["dashboard"] = {
            "template_type": "dashboard",
            "default_data": {
                "title": "Dashboard",
                "subtitle": "Analytics Overview",
                "charts_enabled": True,
                "responsive": True
            },
            "sections": ["header", "sidebar", "main_content", "footer"],
            "css_classes": ["dashboard", "responsive", "modern"]
        }
        
        # Report template
        self.html_templates_config["report"] = {
            "template_type": "report",
            "default_data": {
                "title": "Report",
                "subtitle": "Generated Report",
                "table_of_contents": True,
                "page_numbers": True
            },
            "sections": ["cover", "toc", "content", "appendix", "footer"],
            "css_classes": ["report", "professional", "print-friendly"]
        }
    
    def _get_default_config(self, template: HTMLTemplate, style: HTMLStyle) -> HTMLConfig:
        """Get default configuration for template and style combination"""
        if template == HTMLTemplate.CERTIFICATE:
            return HTMLConfig(
                doctype="html5",
                charset="UTF-8",
                css_framework="bootstrap",
                theme="elegant",
                responsive=True,
                seo_optimized=True,
                accessibility=True
            )
        elif template == HTMLTemplate.DASHBOARD:
            return HTMLConfig(
                doctype="html5",
                charset="UTF-8",
                css_framework="bootstrap",
                theme="modern",
                responsive=True,
                seo_optimized=False,
                accessibility=True
            )
        else:
            return HTMLConfig()
    
    async def _validate_generation_params(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: HTMLTemplate,
        style: HTMLStyle,
        config: Optional[HTMLConfig]
    ):
        """Validate HTML generation parameters"""
        if not content:
            raise ValueError("Content cannot be empty")
        
        if not isinstance(template, HTMLTemplate):
            raise ValueError("Invalid HTML template")
        
        if not isinstance(style, HTMLStyle):
            raise ValueError("Invalid HTML style")
        
        if config and not isinstance(config, HTMLConfig):
            raise ValueError("Invalid configuration object")
    
    async def _prepare_content_for_html(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: HTMLTemplate
    ) -> Dict[str, Any]:
        """Prepare content for HTML generation based on template"""
        if isinstance(content, str):
            return {"text_content": content}
        elif isinstance(content, dict):
            return content
        elif isinstance(content, list):
            return {"list_content": content}
        else:
            return {"raw_content": str(content)}
    
    async def _generate_html_data(
        self,
        content: Dict[str, Any],
        config: HTMLConfig,
        style: HTMLStyle
    ) -> str:
        """Generate HTML data (simulated)"""
        # Simulate HTML generation
        html_data = f"<html><head><title>{content.get('title', 'Document')}</title></head><body>{content}</body></html>"
        
        # Apply configuration
        if config.doctype != "html5":
            html_data = f"<!DOCTYPE {config.doctype}>\n{html_data}"
        
        if config.charset != "UTF-8":
            html_data = html_data.replace("UTF-8", config.charset)
        
        # Apply styling
        if style != HTMLStyle.MODERN:
            html_data += f"<!-- Style: {style.value} -->"
        
        return html_data
    
    async def _create_html_metadata(
        self,
        html_id: str,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: HTMLTemplate,
        style: HTMLStyle,
        config: HTMLConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for the generated HTML"""
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
    
    async def _perform_validation_checks(self, html_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform validation checks on an HTML document"""
        checks = {
            "content_integrity": True,
            "template_validity": True,
            "style_validity": True,
            "config_validity": True,
            "metadata_completeness": True,
            "size_appropriateness": True,
            "html_structure": True
        }
        
        # Check content integrity
        if not html_info.get("content"):
            checks["content_integrity"] = False
        
        # Check template validity
        if not html_info.get("template"):
            checks["template_validity"] = False
        
        # Check style validity
        if not html_info.get("style"):
            checks["style_validity"] = False
        
        # Check config validity
        config = html_info.get("config", {})
        if not config.get("doctype"):
            checks["config_validity"] = False
        
        # Check metadata completeness
        metadata = html_info.get("metadata", {})
        required_fields = ["generator", "version", "timestamp"]
        for field in required_fields:
            if field not in metadata:
                checks["metadata_completeness"] = False
                break
        
        # Check size appropriateness
        content_size = len(str(html_info.get("content", "")))
        if content_size > 1000000:  # 1MB limit
            checks["size_appropriateness"] = False
        
        # Check HTML structure
        html_data = html_info.get("html_data", "")
        if not html_data.startswith("<html") or not html_data.endswith("</html>"):
            checks["html_structure"] = False
        
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
