"""
HTML Exporter for Certificate Manager

Generates HTML data for certificates in a structured format.
This exporter creates HTML data only - no UI rendering or styling.
"""

import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

from .base_exporter import BaseExporter, ExportFormat, ExportOptions

logger = logging.getLogger(__name__)


class HTMLExporter(BaseExporter):
    """
    HTML certificate exporter
    
    Generates structured HTML data for certificates including:
    - Certificate metadata and status
    - Module completion information
    - Quality and compliance metrics
    - Digital trust indicators
    - Export metadata
    """
    
    def __init__(self):
        """Initialize the HTML exporter"""
        super().__init__(ExportFormat.HTML)
        self.html_templates = self._initialize_html_templates()
        
        logger.info("HTML Exporter initialized successfully")
    
    def _initialize_html_templates(self) -> Dict[str, str]:
        """Initialize HTML template structures"""
        return {
            "certificate_header": """
                <div class="certificate-header">
                    <h1 class="certificate-title">{certificate_name}</h1>
                    <div class="certificate-meta">
                        <span class="certificate-id">ID: {certificate_id}</span>
                        <span class="status status-{status_class}">{status}</span>
                        <span class="completion">Completion: {completion_percentage}%</span>
                    </div>
                </div>
            """,
            
            "module_status": """
                <div class="module-status-section">
                    <h2>Module Status</h2>
                    <div class="module-grid">
                        {module_status_items}
                    </div>
                </div>
            """,
            
            "module_status_item": """
                <div class="module-item status-{status_class}">
                    <h3>{module_name}</h3>
                    <div class="module-details">
                        <span class="status">{status}</span>
                        <span class="progress">{progress}%</span>
                        <span class="last-update">{last_update}</span>
                    </div>
                </div>
            """,
            
            "quality_metrics": """
                <div class="quality-metrics-section">
                    <h2>Quality Assessment</h2>
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <span class="metric-label">Overall Quality Score</span>
                            <span class="metric-value quality-{quality_class}">{quality_score}%</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Compliance Status</span>
                            <span class="metric-value compliance-{compliance_class}">{compliance_status}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Security Score</span>
                            <span class="metric-value security-{security_class}">{security_score}%</span>
                        </div>
                    </div>
                </div>
            """,
            
            "digital_trust": """
                <div class="digital-trust-section">
                    <h2>Digital Trust & Verification</h2>
                    <div class="trust-indicators">
                        <div class="trust-item">
                            <span class="trust-label">Digital Signature</span>
                            <span class="trust-value">{signature_status}</span>
                        </div>
                        <div class="trust-item">
                            <span class="trust-label">Verification Hash</span>
                            <span class="trust-value">{verification_hash}</span>
                        </div>
                        <div class="trust-item">
                            <span class="trust-label">QR Code</span>
                            <span class="trust-value">{qr_code_data}</span>
                        </div>
                    </div>
                </div>
            """,
            
            "export_metadata": """
                <div class="export-metadata">
                    <h3>Export Information</h3>
                    <div class="export-details">
                        <p><strong>Format:</strong> {format}</p>
                        <p><strong>Generated:</strong> {timestamp}</p>
                        <p><strong>Certificate ID:</strong> {certificate_id}</p>
                        <p><strong>Version:</strong> {version}</p>
                    </div>
                </div>
            """
        }
    
    async def export_certificate(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Export certificate to HTML format
        
        Args:
            certificate_data: Complete certificate data
            options: Export configuration options
            output_path: Optional path to save the HTML file
            
        Returns:
            Dictionary containing HTML data and export metadata
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
                
                # Generate HTML content
                html_content = await self._generate_html_content(prepared_data, options)
                
                # Generate export metadata
                export_metadata = await self._generate_export_metadata(prepared_data, options)
                
                # Create export result
                export_result = {
                    "format": "html",
                    "content": html_content,
                    "metadata": export_metadata,
                    "file_size": len(html_content.encode('utf-8')),
                    "mime_type": "text/html",
                    "file_extension": "html"
                }
                
                # Save to file if output path provided
                if output_path:
                    await self._save_html_file(output_path, html_content)
                    export_result["output_path"] = str(output_path)
                
                # Log successful export
                await self._log_export_operation(certificate_id, options, True)
                
                return export_result
                
            except Exception as e:
                error_msg = f"HTML export failed: {str(e)}"
                await self._log_export_operation(certificate_id, options, False, error_msg)
                raise
    
    async def validate_export_data(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> bool:
        """
        Validate certificate data for HTML export
        
        Args:
            certificate_data: Certificate data to validate
            options: Export options to validate against
            
        Returns:
            True if data is valid for HTML export
        """
        # Check required fields
        missing_fields = await self._validate_required_fields(certificate_data)
        if missing_fields:
            logger.warning(f"Missing required fields for HTML export: {missing_fields}")
            return False
        
        # Validate certificate status
        status = certificate_data.get("status")
        if status not in ["pending", "in_progress", "ready", "archived"]:
            logger.warning(f"Invalid certificate status for HTML export: {status}")
            return False
        
        # Validate completion percentage
        completion = certificate_data.get("completion_percentage", 0)
        if not isinstance(completion, (int, float)) or completion < 0 or completion > 100:
            logger.warning(f"Invalid completion percentage for HTML export: {completion}")
            return False
        
        return True
    
    async def get_export_metadata(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> Dict[str, Any]:
        """
        Get metadata about the HTML export operation
        
        Args:
            certificate_data: Certificate data being exported
            options: Export options being used
            
        Returns:
            Dictionary containing export metadata
        """
        return {
            "exporter_type": "HTMLExporter",
            "export_format": "html",
            "mime_type": "text/html",
            "file_extension": "html",
            "supports_styling": True,
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
    
    async def _generate_html_content(
        self,
        prepared_data: Dict[str, Any],
        options: ExportOptions
    ) -> str:
        """
        Generate HTML content from prepared certificate data
        
        Args:
            prepared_data: Prepared certificate data
            options: Export options
            
        Returns:
            Complete HTML content as string
        """
        certificate_data = prepared_data["certificate_data"]
        
        # Generate HTML sections
        header_html = await self._generate_header_html(certificate_data)
        module_status_html = await self._generate_module_status_html(certificate_data)
        quality_metrics_html = await self._generate_quality_metrics_html(certificate_data)
        digital_trust_html = await self._generate_digital_trust_html(certificate_data)
        export_metadata_html = await self._generate_export_metadata_html(prepared_data)
        
        # Combine all sections
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Certificate - {certificate_data.get('certificate_name', 'Unknown')}</title>
            <meta name="description" content="Digital Certificate Export">
            <meta name="generator" content="Certificate Manager Export System">
        </head>
        <body>
            <div class="certificate-container">
                {header_html}
                {module_status_html}
                {quality_metrics_html}
                {digital_trust_html}
                {export_metadata_html}
            </div>
        </body>
        </html>
        """
        
        return html_content.strip()
    
    async def _generate_header_html(self, certificate_data: Dict[str, Any]) -> str:
        """Generate HTML for certificate header section"""
        template = self.html_templates["certificate_header"]
        
        # Determine status class for styling
        status = certificate_data.get("status", "unknown")
        status_class = self._get_status_class(status)
        
        return template.format(
            certificate_name=certificate_data.get("certificate_name", "Unknown Certificate"),
            certificate_id=certificate_data.get("certificate_id", "Unknown"),
            status=status.title().replace("_", " "),
            status_class=status_class,
            completion_percentage=certificate_data.get("completion_percentage", 0)
        )
    
    async def _generate_module_status_html(self, certificate_data: Dict[str, Any]) -> str:
        """Generate HTML for module status section"""
        if "module_status" not in certificate_data:
            return ""
        
        module_status = certificate_data["module_status"]
        module_items = []
        
        for module_name, status_info in module_status.items():
            if isinstance(status_info, dict):
                status = status_info.get("status", "unknown")
                progress = status_info.get("progress", 0)
                last_update = status_info.get("last_update", "Unknown")
            else:
                status = str(status_info)
                progress = 0
                last_update = "Unknown"
            
            status_class = self._get_status_class(status)
            
            module_item = self.html_templates["module_status_item"].format(
                module_name=module_name.replace("_", " ").title(),
                status=status.title().replace("_", " "),
                status_class=status_class,
                progress=progress,
                last_update=last_update
            )
            module_items.append(module_item)
        
        if not module_items:
            return ""
        
        return self.html_templates["module_status"].format(
            module_status_items="\n".join(module_items)
        )
    
    async def _generate_quality_metrics_html(self, certificate_data: Dict[str, Any]) -> str:
        """Generate HTML for quality metrics section"""
        template = self.html_templates["quality_metrics"]
        
        quality_score = certificate_data.get("overall_quality_score", 0)
        compliance_status = certificate_data.get("compliance_status", "unknown")
        security_score = certificate_data.get("security_score", 0)
        
        # Determine CSS classes for styling
        quality_class = self._get_quality_class(quality_score)
        compliance_class = self._get_compliance_class(compliance_status)
        security_class = self._get_security_class(security_score)
        
        return template.format(
            quality_score=quality_score,
            quality_class=quality_class,
            compliance_status=compliance_status.title().replace("_", " "),
            compliance_class=compliance_class,
            security_score=security_score,
            security_class=security_class
        )
    
    async def _generate_digital_trust_html(self, certificate_data: Dict[str, Any]) -> str:
        """Generate HTML for digital trust section"""
        template = self.html_templates["digital_trust"]
        
        # Extract digital trust information
        digital_signature = certificate_data.get("digital_signature", "")
        verification_hash = certificate_data.get("verification_hash", "")
        qr_code_data = certificate_data.get("qr_code_data", "")
        
        return template.format(
            signature_status="✓ Valid" if digital_signature else "✗ Not Available",
            verification_hash=verification_hash[:16] + "..." if verification_hash else "Not Available",
            qr_code_data=qr_code_data[:20] + "..." if qr_code_data else "Not Available"
        )
    
    async def _generate_export_metadata_html(self, prepared_data: Dict[str, Any]) -> str:
        """Generate HTML for export metadata section"""
        template = self.html_templates["export_metadata"]
        
        return template.format(
            format=prepared_data.get("export_format", "html"),
            timestamp=prepared_data.get("export_timestamp", "Unknown"),
            certificate_id=prepared_data.get("certificate_id", "Unknown"),
            version="1.0"  # Default version
        )
    
    async def _save_html_file(self, output_path: Path, html_content: str) -> None:
        """Save HTML content to file"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html_content, encoding='utf-8')
            logger.info(f"HTML file saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save HTML file: {e}")
            raise
    
    def _get_status_class(self, status: str) -> str:
        """Get CSS class for status styling"""
        status_mapping = {
            "completed": "success",
            "ready": "success",
            "in_progress": "warning",
            "pending": "info",
            "failed": "error",
            "archived": "secondary"
        }
        return status_mapping.get(status.lower(), "default")
    
    def _get_quality_class(self, quality_score: float) -> str:
        """Get CSS class for quality score styling"""
        if quality_score >= 90:
            return "excellent"
        elif quality_score >= 80:
            return "good"
        elif quality_score >= 70:
            return "fair"
        elif quality_score >= 60:
            return "poor"
        else:
            return "critical"
    
    def _get_compliance_class(self, compliance_status: str) -> str:
        """Get CSS class for compliance status styling"""
        status_mapping = {
            "compliant": "success",
            "pending": "warning",
            "non_compliant": "error",
            "under_review": "info"
        }
        return status_mapping.get(compliance_status.lower(), "default")
    
    def _get_security_class(self, security_score: float) -> str:
        """Get CSS class for security score styling"""
        if security_score >= 90:
            return "excellent"
        elif security_score >= 80:
            return "good"
        elif security_score >= 70:
            return "fair"
        elif security_score >= 60:
            return "poor"
        else:
            return "critical" 