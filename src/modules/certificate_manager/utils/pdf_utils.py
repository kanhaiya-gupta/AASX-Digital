"""
PDF Generation Utilities

This module provides comprehensive PDF generation, styling, and management utilities
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


class PDFTemplate(Enum):
    """PDF template types for different document types"""
    CERTIFICATE = "certificate"
    REPORT = "report"
    INVOICE = "invoice"
    LETTER = "letter"
    FORM = "form"
    PRESENTATION = "presentation"
    MANUAL = "manual"
    CONTRACT = "contract"
    PROPOSAL = "proposal"
    SUMMARY = "summary"


class PDFStyle(Enum):
    """PDF styling options"""
    PROFESSIONAL = "professional"
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    COLORFUL = "colorful"
    CORPORATE = "corporate"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    ELEGANT = "elegant"
    CASUAL = "casual"


@dataclass
class PDFConfig:
    """Configuration for PDF generation"""
    page_size: str = "A4"
    orientation: str = "portrait"
    margins: Dict[str, float] = None
    font_family: str = "Helvetica"
    font_size: int = 12
    line_spacing: float = 1.2
    header_enabled: bool = True
    footer_enabled: bool = True
    watermark: Optional[str] = None
    password_protected: bool = False
    compression: bool = True


class PDFGenerator:
    """
    PDF generation and management utility
    
    Handles:
    - PDF generation from various data sources
    - Template-based document creation
    - Custom styling and branding
    - Batch generation and optimization
    - PDF metadata management
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the PDF generator utility"""
        self.pdf_templates = list(PDFTemplate)
        self.pdf_styles = list(PDFStyle)
        
        # PDF storage and metadata
        self.generated_pdfs: Dict[str, Dict[str, Any]] = {}
        self.pdf_templates_config: Dict[str, Dict[str, Any]] = {}
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
        
        logger.info("PDF Generator utility initialized successfully")
    
    async def generate_pdf(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: PDFTemplate = PDFTemplate.CERTIFICATE,
        style: PDFStyle = PDFStyle.PROFESSIONAL,
        config: Optional[PDFConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a PDF document with the specified content and configuration
        
        Args:
            content: Content to include in the PDF
            template: PDF template to use
            style: PDF styling to apply
            config: PDF configuration
            metadata: Additional metadata for the PDF
            
        Returns:
            Dictionary containing PDF information and generated data
        """
        start_time = time.time()
        pdf_id = f"pdf_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_generation_params(content, template, style, config)
            
            # Prepare content for PDF generation
            prepared_content = await self._prepare_content_for_pdf(content, template)
            
            # Apply configuration and styling
            pdf_config = config or self._get_default_config(template, style)
            
            # Generate PDF (simulated)
            pdf_data = await self._generate_pdf_data(prepared_content, pdf_config, style)
            
            # Create metadata
            pdf_metadata = await self._create_pdf_metadata(
                pdf_id, content, template, style, pdf_config, metadata
            )
            
            # Store generated PDF
            pdf_info = {
                "id": pdf_id,
                "content": prepared_content,
                "template": template.value,
                "style": style.value,
                "config": pdf_config.__dict__,
                "metadata": pdf_metadata,
                "generated_at": time.time(),
                "size_bytes": len(str(pdf_data)),
                "status": "success"
            }
            
            self.generated_pdfs[pdf_id] = pdf_info
            self.generation_history.append(pdf_info)
            
            # Update statistics
            await self._update_generation_stats(True, time.time() - start_time, len(str(pdf_data)))
            
            logger.info(f"PDF generated successfully: {pdf_id}")
            return pdf_info
            
        except Exception as e:
            await self._update_generation_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to generate PDF: {str(e)}")
            raise
    
    async def generate_batch_pdfs(
        self,
        content_list: List[Union[str, Dict[str, Any], List[Dict[str, Any]]]],
        template: PDFTemplate = PDFTemplate.CERTIFICATE,
        style: PDFStyle = PDFStyle.PROFESSIONAL,
        config: Optional[PDFConfig] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple PDFs in batch
        
        Args:
            content_list: List of content items to convert to PDFs
            template: PDF template to use
            style: PDF styling to apply
            config: PDF configuration
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of generated PDF information
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch PDF generation: {batch_id}")
        
        # Create tasks for concurrent generation
        tasks = []
        for i, content in enumerate(content_list):
            task = asyncio.create_task(
                self.generate_pdf(content, template, style, config, {
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
                logger.error(f"Failed to generate PDF {i} in batch {batch_id}: {str(result)}")
                results.append({
                    "id": f"failed_{batch_id}_{i}",
                    "status": "failed",
                    "error": str(result),
                    "batch_id": batch_id,
                    "batch_index": i
                })
            else:
                results.append(result)
        
        logger.info(f"Batch PDF generation completed: {batch_id}, {len(results)} results")
        return results
    
    async def generate_pdf_from_template(
        self,
        template_name: str,
        template_data: Dict[str, Any],
        style: PDFStyle = PDFStyle.PROFESSIONAL,
        config: Optional[PDFConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a PDF using a predefined template
        
        Args:
            template_name: Name of the template to use
            template_data: Data to populate the template
            style: PDF styling to apply
            config: PDF configuration
            metadata: Additional metadata for the PDF
            
        Returns:
            Dictionary containing PDF information and generated data
        """
        if template_name not in self.pdf_templates_config:
            raise ValueError(f"Template not found: {template_name}")
        
        template_config = self.pdf_templates_config[template_name]
        
        # Merge template data with provided data
        merged_data = {**template_config.get("default_data", {}), **template_data}
        
        # Use template's default template type
        template_type = PDFTemplate(template_config.get("template_type", "certificate"))
        
        return await self.generate_pdf(
            merged_data, template_type, style, config, metadata
        )
    
    async def validate_pdf(self, pdf_id: str) -> Dict[str, Any]:
        """
        Validate a generated PDF
        
        Args:
            pdf_id: ID of the PDF to validate
            
        Returns:
            Validation result information
        """
        if pdf_id not in self.generated_pdfs:
            raise ValueError(f"PDF not found: {pdf_id}")
        
        pdf_info = self.generated_pdfs[pdf_id]
        
        # Perform validation checks
        validation_result = await self._perform_validation_checks(pdf_info)
        
        return {
            "pdf_id": pdf_id,
            "validation_result": validation_result,
            "validated_at": time.time(),
            "status": "validated"
        }
    
    async def get_pdf_info(self, pdf_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a generated PDF
        
        Args:
            pdf_id: ID of the PDF
            
        Returns:
            PDF information
        """
        if pdf_id not in self.generated_pdfs:
            raise ValueError(f"PDF not found: {pdf_id}")
        
        return self.generated_pdfs[pdf_id]
    
    async def get_pdf_history(
        self,
        template: Optional[PDFTemplate] = None,
        style: Optional[PDFStyle] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get PDF generation history
        
        Args:
            template: Filter by PDF template
            style: Filter by PDF style
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of PDF history entries
        """
        history = self.generation_history
        
        if template:
            history = [h for h in history if h.get("template") == template.value]
        
        if style:
            history = [h for h in history if h.get("style") == style.value]
        
        # Sort by generation time (newest first)
        history.sort(key=lambda x: x.get("generated_at", 0), reverse=True)
        
        return history[offset:offset + limit]
    
    async def create_pdf_template(
        self,
        template_name: str,
        template_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a reusable PDF template
        
        Args:
            template_name: Name of the template
            template_config: Template configuration
            
        Returns:
            Template creation result
        """
        if template_name in self.pdf_templates_config:
            raise ValueError(f"Template already exists: {template_name}")
        
        self.pdf_templates_config[template_name] = template_config
        
        return {
            "template_name": template_name,
            "config": template_config,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Get PDF generation statistics
        
        Returns:
            Generation statistics
        """
        return self.generation_stats.copy()
    
    async def cleanup_expired_pdfs(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired PDFs
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of PDFs cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_pdfs = []
        for pdf_id, pdf_info in self.generated_pdfs.items():
            if current_time - pdf_info.get("generated_at", 0) > max_age_seconds:
                expired_pdfs.append(pdf_id)
        
        # Remove expired PDFs
        for pdf_id in expired_pdfs:
            del self.generated_pdfs[pdf_id]
        
        logger.info(f"Cleaned up {len(expired_pdfs)} expired PDFs")
        return len(expired_pdfs)
    
    # Private helper methods
    
    def _initialize_default_templates(self):
        """Initialize default PDF templates"""
        # Certificate template
        self.pdf_templates_config["certificate"] = {
            "template_type": "certificate",
            "default_data": {
                "title": "Certificate of Completion",
                "subtitle": "This is to certify that",
                "signature_line": "Authorized Signature",
                "date_format": "MMMM DD, YYYY"
            },
            "sections": ["header", "content", "signature", "footer"],
            "page_count": 1
        }
        
        # Report template
        self.pdf_templates_config["report"] = {
            "template_type": "report",
            "default_data": {
                "title": "Report",
                "subtitle": "Generated Report",
                "table_of_contents": True,
                "page_numbers": True
            },
            "sections": ["cover", "toc", "content", "appendix", "footer"],
            "page_count": 1
        }
        
        # Invoice template
        self.pdf_templates_config["invoice"] = {
            "template_type": "invoice",
            "default_data": {
                "title": "Invoice",
                "subtitle": "Payment Due",
                "due_date_format": "MM/DD/YYYY",
                "currency_symbol": "$"
            },
            "sections": ["header", "billing_info", "items", "totals", "footer"],
            "page_count": 1
        }
    
    def _get_default_config(self, template: PDFTemplate, style: PDFStyle) -> PDFConfig:
        """Get default configuration for template and style combination"""
        if template == PDFTemplate.CERTIFICATE:
            return PDFConfig(
                page_size="A4",
                orientation="landscape",
                margins={"top": 0.5, "bottom": 0.5, "left": 0.5, "right": 0.5},
                font_family="Times-Roman",
                font_size=14,
                header_enabled=True,
                footer_enabled=True
            )
        elif template == PDFTemplate.REPORT:
            return PDFConfig(
                page_size="A4",
                orientation="portrait",
                margins={"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
                font_family="Helvetica",
                font_size=11,
                line_spacing=1.5,
                header_enabled=True,
                footer_enabled=True
            )
        else:
            return PDFConfig()
    
    async def _validate_generation_params(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: PDFTemplate,
        style: PDFStyle,
        config: Optional[PDFConfig]
    ):
        """Validate PDF generation parameters"""
        if not content:
            raise ValueError("Content cannot be empty")
        
        if not isinstance(template, PDFTemplate):
            raise ValueError("Invalid PDF template")
        
        if not isinstance(style, PDFStyle):
            raise ValueError("Invalid PDF style")
        
        if config and not isinstance(config, PDFConfig):
            raise ValueError("Invalid configuration object")
    
    async def _prepare_content_for_pdf(
        self,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: PDFTemplate
    ) -> Dict[str, Any]:
        """Prepare content for PDF generation based on template"""
        if isinstance(content, str):
            return {"text_content": content}
        elif isinstance(content, dict):
            return content
        elif isinstance(content, list):
            return {"list_content": content}
        else:
            return {"raw_content": str(content)}
    
    async def _generate_pdf_data(
        self,
        content: Dict[str, Any],
        config: PDFConfig,
        style: PDFStyle
    ) -> str:
        """Generate PDF data (simulated)"""
        # Simulate PDF generation
        pdf_data = f"PDF_DATA:{content}"
        
        # Apply configuration
        if config.page_size != "A4":
            pdf_data += f"_SIZE_{config.page_size}"
        
        if config.orientation != "portrait":
            pdf_data += f"_ORIENT_{config.orientation}"
        
        # Apply styling
        if style != PDFStyle.PROFESSIONAL:
            pdf_data += f"_STYLE_{style.value}"
        
        return pdf_data
    
    async def _create_pdf_metadata(
        self,
        pdf_id: str,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        template: PDFTemplate,
        style: PDFStyle,
        config: PDFConfig,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for the generated PDF"""
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
    
    async def _perform_validation_checks(self, pdf_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform validation checks on a PDF"""
        checks = {
            "content_integrity": True,
            "template_validity": True,
            "style_validity": True,
            "config_validity": True,
            "metadata_completeness": True,
            "size_appropriateness": True
        }
        
        # Check content integrity
        if not pdf_info.get("content"):
            checks["content_integrity"] = False
        
        # Check template validity
        if not pdf_info.get("template"):
            checks["template_validity"] = False
        
        # Check style validity
        if not pdf_info.get("style"):
            checks["style_validity"] = False
        
        # Check config validity
        config = pdf_info.get("config", {})
        if not config.get("page_size"):
            checks["config_validity"] = False
        
        # Check metadata completeness
        metadata = pdf_info.get("metadata", {})
        required_fields = ["generator", "version", "timestamp"]
        for field in required_fields:
            if field not in metadata:
                checks["metadata_completeness"] = False
                break
        
        # Check size appropriateness
        content_size = len(str(pdf_info.get("content", "")))
        if content_size > 1000000:  # 1MB limit
            checks["size_appropriateness"] = False
        
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
