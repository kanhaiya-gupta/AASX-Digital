"""
PDF Exporter for Certificate Manager

Generates PDF data for certificates in a structured format.
This exporter creates PDF data only - no UI rendering or styling.
"""

import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

from .base_exporter import BaseExporter, ExportFormat, ExportOptions

logger = logging.getLogger(__name__)


class PDFExporter(BaseExporter):
    """
    PDF certificate exporter
    
    Generates structured PDF data for certificates including:
    - Certificate metadata and status
    - Module completion information
    - Quality and compliance metrics
    - Digital trust indicators
    - Export metadata
    """
    
    def __init__(self):
        """Initialize the PDF exporter"""
        super().__init__(ExportFormat.PDF)
        self.pdf_templates = self._initialize_pdf_templates()
        
        logger.info("PDF Exporter initialized successfully")
    
    def _initialize_pdf_templates(self) -> Dict[str, str]:
        """Initialize PDF template structures"""
        return {
            "document_header": """
                %PDF-1.7
                %âãÏÓ
                1 0 obj
                <<
                /Type /Catalog
                /Pages 2 0 R
                /Metadata 3 0 R
                >>
                endobj
                
                2 0 obj
                <<
                /Type /Pages
                /Kids [4 0 R]
                /Count 1
                >>
                endobj
                
                3 0 obj
                <<
                /Type /Metadata
                /Subtype /XML
                /Length {metadata_length}
                >>
                stream
                {metadata_content}
                endstream
                endobj
            """,
            
            "page_content": """
                4 0 obj
                <<
                /Type /Page
                /Parent 2 0 R
                /MediaBox [0 0 612 792]
                /Contents 5 0 R
                /Resources 6 0 R
                >>
                endobj
                
                5 0 obj
                <<
                /Length {content_length}
                >>
                stream
                {content_stream}
                endstream
                endobj
            """,
            
            "resources": """
                6 0 obj
                <<
                /Font <<
                /F1 7 0 R
                /F2 8 0 R
                >>
                >>
                endobj
                
                7 0 obj
                <<
                /Type /Font
                /Subtype /Type1
                /BaseFont /Helvetica
                >>
                endobj
                
                8 0 obj
                <<
                /Type /Font
                /Subtype /Type1
                /BaseFont /Helvetica-Bold
                >>
                endobj
            """,
            
            "content_stream_template": """
                BT
                /F1 24 Tf
                50 750 Td
                (Certificate: {certificate_name}) Tj
                ET
                
                BT
                /F2 12 Tf
                50 720 Td
                (Certificate ID: {certificate_id}) Tj
                ET
                
                BT
                /F2 12 Tf
                50 700 Td
                (Status: {status}) Tj
                ET
                
                BT
                /F2 12 Tf
                50 680 Td
                (Completion: {completion_percentage}%) Tj
                ET
                
                BT
                /F1 18 Tf
                50 640 Td
                (Quality Metrics) Tj
                ET
                
                BT
                /F2 12 Tf
                50 620 Td
                (Overall Quality Score: {quality_score}%) Tj
                ET
                
                BT
                /F2 12 Tf
                50 600 Td
                (Compliance Status: {compliance_status}) Tj
                ET
                
                BT
                /F2 12 Tf
                50 580 Td
                (Security Score: {security_score}%) Tj
                ET
                
                BT
                /F1 18 Tf
                50 540 Td
                (Module Status) Tj
                ET
                {module_status_content}
                
                BT
                /F1 18 Tf
                50 300 Td
                (Digital Trust) Tj
                ET
                
                BT
                /F2 12 Tf
                50 280 Td
                (Digital Signature: {signature_status}) Tj
                ET
                
                BT
                /F2 12 Tf
                50 260 Td
                (Verification Hash: {verification_hash}) Tj
                ET
                
                BT
                /F2 12 Tf
                50 240 Td
                (QR Code: {qr_code_data}) Tj
                ET
                
                BT
                /F1 14 Tf
                50 200 Td
                (Generated: {timestamp}) Tj
                ET
            """
        }
    
    async def export_certificate(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Export certificate to PDF format
        
        Args:
            certificate_data: Complete certificate data
            options: Export configuration options
            output_path: Optional path to save the PDF file
            
        Returns:
            Dictionary containing PDF data and export metadata
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
                
                # Generate PDF content
                pdf_content = await self._generate_pdf_content(prepared_data, options)
                
                # Generate export metadata
                export_metadata = await self._generate_export_metadata(prepared_data, options)
                
                # Create export result
                export_result = {
                    "format": "pdf",
                    "content": pdf_content,
                    "metadata": export_metadata,
                    "file_size": len(pdf_content),
                    "mime_type": "application/pdf",
                    "file_extension": "pdf"
                }
                
                # Save to file if output path provided
                if output_path:
                    await self._save_pdf_file(output_path, pdf_content)
                    export_result["output_path"] = str(output_path)
                
                # Log successful export
                await self._log_export_operation(certificate_id, options, True)
                
                return export_result
                
            except Exception as e:
                error_msg = f"PDF export failed: {str(e)}"
                await self._log_export_operation(certificate_id, options, False, error_msg)
                raise
    
    async def validate_export_data(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> bool:
        """
        Validate certificate data for PDF export
        
        Args:
            certificate_data: Certificate data to validate
            options: Export options to validate against
            
        Returns:
            True if data is valid for PDF export
        """
        # Check required fields
        missing_fields = await self._validate_required_fields(certificate_data)
        if missing_fields:
            logger.warning(f"Missing required fields for PDF export: {missing_fields}")
            return False
        
        # Validate certificate status
        status = certificate_data.get("status")
        if status not in ["pending", "in_progress", "ready", "archived"]:
            logger.warning(f"Invalid certificate status for PDF export: {status}")
            return False
        
        # Validate completion percentage
        completion = certificate_data.get("completion_percentage", 0)
        if not isinstance(completion, (int, float)) or completion < 0 or completion > 100:
            logger.warning(f"Invalid completion percentage for PDF export: {completion}")
            return False
        
        return True
    
    async def get_export_metadata(
        self,
        certificate_data: Dict[str, Any],
        options: ExportOptions
    ) -> Dict[str, Any]:
        """
        Get metadata about the PDF export operation
        
        Args:
            certificate_data: Certificate data being exported
            options: Export options being used
            
        Returns:
            Dictionary containing export metadata
        """
        return {
            "exporter_type": "PDFExporter",
            "export_format": "pdf",
            "mime_type": "application/pdf",
            "file_extension": "pdf",
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
    
    async def _generate_pdf_content(
        self,
        prepared_data: Dict[str, Any],
        options: ExportOptions
    ) -> bytes:
        """
        Generate PDF content from prepared certificate data
        
        Args:
            prepared_data: Prepared certificate data
            options: Export options
            
        Returns:
            PDF content as bytes
        """
        certificate_data = prepared_data["certificate_data"]
        
        # Generate content stream
        content_stream = await self._generate_content_stream(certificate_data)
        
        # Generate metadata
        metadata_content = await self._generate_metadata_content(prepared_data)
        
        # Build PDF structure
        pdf_content = await self._build_pdf_structure(content_stream, metadata_content)
        
        return pdf_content
    
    async def _generate_content_stream(self, certificate_data: Dict[str, Any]) -> str:
        """Generate PDF content stream"""
        template = self.pdf_templates["content_stream_template"]
        
        # Generate module status content
        module_status_content = await self._generate_module_status_content(certificate_data)
        
        # Extract values for template
        quality_score = certificate_data.get("overall_quality_score", 0)
        compliance_status = certificate_data.get("compliance_status", "unknown")
        security_score = certificate_data.get("security_score", 0)
        digital_signature = certificate_data.get("digital_signature", "")
        verification_hash = certificate_data.get("verification_hash", "")
        qr_code_data = certificate_data.get("qr_code_data", "")
        
        return template.format(
            certificate_name=certificate_data.get("certificate_name", "Unknown Certificate"),
            certificate_id=certificate_data.get("certificate_id", "Unknown"),
            status=certificate_data.get("status", "unknown").title().replace("_", " "),
            completion_percentage=certificate_data.get("completion_percentage", 0),
            quality_score=quality_score,
            compliance_status=compliance_status.title().replace("_", " "),
            security_score=security_score,
            module_status_content=module_status_content,
            signature_status="Valid" if digital_signature else "Not Available",
            verification_hash=verification_hash[:16] + "..." if verification_hash else "Not Available",
            qr_code_data=qr_code_data[:20] + "..." if qr_code_data else "Not Available",
            timestamp=asyncio.get_event_loop().time()
        )
    
    async def _generate_module_status_content(self, certificate_data: Dict[str, Any]) -> str:
        """Generate PDF content for module status section"""
        if "module_status" not in certificate_data:
            return ""
        
        module_status = certificate_data["module_status"]
        content_lines = []
        y_position = 520
        
        for module_name, status_info in module_status.items():
            if isinstance(status_info, dict):
                status = status_info.get("status", "unknown")
                progress = status_info.get("progress", 0)
            else:
                status = str(status_info)
                progress = 0
            
            module_line = f"""
                BT
                /F2 12 Tf
                50 {y_position} Td
                ({module_name.replace('_', ' ').title()}: {status.title().replace('_', ' ')} - {progress}%) Tj
                ET
            """
            content_lines.append(module_line)
            y_position -= 20
            
            if y_position < 100:  # Prevent content from going off page
                break
        
        return "\n".join(content_lines)
    
    async def _generate_metadata_content(self, prepared_data: Dict[str, Any]) -> str:
        """Generate PDF metadata content"""
        metadata = {
            "title": f"Certificate - {prepared_data.get('certificate_id', 'Unknown')}",
            "author": "Certificate Manager Export System",
            "subject": "Digital Certificate Export",
            "creator": "Certificate Manager",
            "producer": "PDF Exporter",
            "creation_date": prepared_data.get("export_timestamp", ""),
            "export_format": prepared_data.get("export_format", "pdf"),
            "certificate_id": prepared_data.get("certificate_id", "Unknown")
        }
        
        # Convert to XML format for PDF metadata
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:dc="http://purl.org/dc/elements/1.1/"
                 xmlns:pdf="http://ns.adobe.com/pdf/1.3/">
            <rdf:Description rdf:about="">
                <dc:title>{metadata['title']}</dc:title>
                <dc:creator>{metadata['author']}</dc:creator>
                <dc:subject>{metadata['subject']}</dc:subject>
                <dc:description>Digital Certificate Export</dc:description>
                <pdf:Producer>{metadata['producer']}</pdf:Producer>
                <pdf:Creator>{metadata['creator']}</pdf:Creator>
                <dc:date>{metadata['creation_date']}</dc:date>
            </rdf:Description>
        </rdf:RDF>"""
        
        return xml_content
    
    async def _build_pdf_structure(
        self,
        content_stream: str,
        metadata_content: str
    ) -> bytes:
        """Build complete PDF structure"""
        # Get template parts
        header_template = self.pdf_templates["document_header"]
        page_template = self.pdf_templates["page_content"]
        resources_template = self.pdf_templates["resources"]
        
        # Calculate lengths
        content_length = len(content_stream)
        metadata_length = len(metadata_content.encode('utf-8'))
        
        # Build PDF content
        pdf_content = header_template.format(
            metadata_length=metadata_length,
            metadata_content=metadata_content
        )
        
        pdf_content += page_template.format(
            content_length=content_length,
            content_stream=content_stream
        )
        
        pdf_content += resources_template
        
        # Add cross-reference table and trailer
        pdf_content += self._generate_xref_and_trailer()
        
        return pdf_content.encode('utf-8')
    
    def _generate_xref_and_trailer(self) -> str:
        """Generate PDF cross-reference table and trailer"""
        return """
        xref
        0 9
        0000000000 65535 f 
        0000000009 00000 n 
        0000000058 00000 n 
        0000000117 00000 n 
        0000000176 00000 n 
        0000000235 00000 n 
        0000000294 00000 n 
        0000000353 00000 n 
        0000000412 00000 n 
        
        trailer
        <<
        /Size 9
        /Root 1 0 R
        >>
        startxref
        0000000471
        %%EOF
        """
    
    async def _save_pdf_file(self, output_path: Path, pdf_content: bytes) -> None:
        """Save PDF content to file"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(pdf_content)
            logger.info(f"PDF file saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save PDF file: {e}")
            raise
