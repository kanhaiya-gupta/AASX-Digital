"""
Certificate Generator - Certificate Content Generation Service

Handles certificate content generation, formatting, and export.
Generates comprehensive certificates with all required data,
formats them for various output formats, and manages
certificate templates and styling.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from pathlib import Path

from ..models.certificates_registry import (
    CertificateRegistry,
    CertificateStatus,
    QualityLevel,
    ComplianceStatus,
    SecurityLevel
)
from ..models.certificates_versions import CertificateVersion, VersionType
from ..models.certificates_metrics import CertificateMetrics, MetricCategory
from ..services.certificates_registry_service import CertificatesRegistryService
from ..services.certificates_versions_service import CertificatesVersionsService
from ..services.certificates_metrics_service import CertificatesMetricsService

logger = logging.getLogger(__name__)


class OutputFormat(str, Enum):
    """Certificate output formats"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    MARKDOWN = "markdown"


class CertificateTemplate(str, Enum):
    """Certificate template types"""
    STANDARD = "standard"
    PREMIUM = "premium"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"


class CertificateGenerator:
    """
    Certificate content generation service
    
    Handles:
    - Certificate content generation
    - Template management and styling
    - Multi-format export
    - Certificate validation and quality checks
    - Digital signature generation
    - Certificate metadata compilation
    """
    
    def __init__(
        self,
        registry_service: CertificatesRegistryService,
        versions_service: CertificatesVersionsService,
        metrics_service: CertificatesMetricsService
    ):
        """Initialize the certificate generator"""
        self.registry_service = registry_service
        self.versions_service = versions_service
        self.metrics_service = metrics_service
        
        # Template cache
        self.template_cache: Dict[str, Dict[str, Any]] = {}
        
        # Generation locks per certificate
        self.generation_locks: Dict[str, asyncio.Lock] = {}
        
        # Output directory
        self.output_dir = Path("certificates")
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("Certificate Generator initialized successfully")
    
    async def generate_certificate(
        self,
        certificate_id: str,
        output_format: OutputFormat = OutputFormat.PDF,
        template: CertificateTemplate = CertificateTemplate.STANDARD,
        include_metadata: bool = True,
        include_metrics: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a complete certificate
        
        This is the main entry point for certificate generation.
        Generates comprehensive certificate content and exports
        in the specified format.
        """
        try:
            # Acquire generation lock for this certificate
            if certificate_id not in self.generation_locks:
                self.generation_locks[certificate_id] = asyncio.Lock()
            
            async with self.generation_locks[certificate_id]:
                logger.info(f"Generating {output_format.value} certificate for {certificate_id}")
                
                # Get certificate data
                certificate = await self.registry_service.get_certificate(certificate_id)
                if not certificate:
                    logger.error(f"Certificate not found: {certificate_id}")
                    return None
                
                # Validate certificate readiness
                if not await self._validate_certificate_readiness(certificate):
                    logger.error(f"Certificate not ready for generation: {certificate_id}")
                    return None
                
                # Generate certificate content
                certificate_content = await self._generate_certificate_content(
                    certificate, template, include_metadata, include_metrics
                )
                
                # Format for output
                formatted_content = await self._format_certificate_content(
                    certificate_content, output_format
                )
                
                # Save to file
                file_path = await self._save_certificate_file(
                    certificate_id, formatted_content, output_format
                )
                
                # Create new version
                version = await self._create_certificate_version(
                    certificate_id, output_format, template, file_path
                )
                
                # Update generation metrics
                await self._update_generation_metrics(certificate_id, output_format, template)
                
                logger.info(f"Successfully generated {output_format.value} certificate for {certificate_id}")
                
                return {
                    "certificate_id": certificate_id,
                    "output_format": output_format.value,
                    "template": template.value,
                    "file_path": str(file_path),
                    "version_id": version.version_id if version else None,
                    "generated_at": datetime.utcnow().isoformat(),
                    "content_size": len(formatted_content)
                }
                
        except Exception as e:
            logger.error(f"Error generating certificate: {e}")
            return None
    
    async def _validate_certificate_readiness(self, certificate: CertificateRegistry) -> bool:
        """Validate that certificate is ready for generation"""
        try:
            # Check if all required modules are complete
            if certificate.module_status.health_score < 100.0:
                logger.warning(f"Certificate modules not complete: {certificate.module_status.health_score}%")
                return False
            
            # Check quality requirements
            if certificate.quality_assessment.overall_quality_score < 80.0:
                logger.warning(f"Certificate quality below threshold: {certificate.quality_assessment.overall_quality_score}%")
                return False
            
            # Check compliance status
            if certificate.compliance_tracking.compliance_status == ComplianceStatus.NON_COMPLIANT:
                logger.warning("Certificate not compliant")
                return False
            
            # Check security requirements
            if certificate.security_metrics.security_score < 70.0:
                logger.warning(f"Certificate security below threshold: {certificate.security_metrics.security_score}%")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating certificate readiness: {e}")
            return False
    
    async def _generate_certificate_content(
        self,
        certificate: CertificateRegistry,
        template: CertificateTemplate,
        include_metadata: bool,
        include_metrics: bool
    ) -> Dict[str, Any]:
        """Generate comprehensive certificate content"""
        try:
            # Get latest metrics if requested
            metrics = []
            if include_metrics:
                metrics = await self.metrics_service.get_certificate_metrics(
                    certificate.certificate_id, limit=100
                )
            
            # Build certificate content
            content = {
                "certificate_header": await self._generate_certificate_header(certificate, template),
                "module_summaries": await self._generate_module_summaries(certificate),
                "quality_assessment": await self._generate_quality_section(certificate),
                "compliance_tracking": await self._generate_compliance_section(certificate),
                "security_metrics": await self._generate_security_section(certificate),
                "business_context": await self._generate_business_section(certificate),
                "digital_trust": await self._generate_digital_trust_section(certificate)
            }
            
            if include_metadata:
                content["metadata"] = await self._generate_metadata_section(certificate)
            
            if include_metrics:
                content["metrics_summary"] = await self._generate_metrics_summary(metrics)
            
            # Add template-specific styling
            content["styling"] = await self._get_template_styling(template)
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating certificate content: {e}")
            return {}
    
    async def _generate_certificate_header(self, certificate: CertificateRegistry, template: CertificateTemplate) -> Dict[str, Any]:
        """Generate certificate header section"""
        try:
            header = {
                "title": f"Digital Twin Analytics Certificate",
                "subtitle": f"Certificate ID: {certificate.certificate_id}",
                "issue_date": certificate.created_at.isoformat(),
                "expiry_date": (certificate.created_at + timedelta(days=365)).isoformat(),
                "status": certificate.certificate_status.value,
                "template": template.value,
                "version": "1.0"
            }
            
            return header
            
        except Exception as e:
            logger.error(f"Error generating certificate header: {e}")
            return {}
    
    async def _generate_module_summaries(self, certificate: CertificateRegistry) -> Dict[str, Any]:
        """Generate module summaries section"""
        try:
            summaries = {}
            
            # Get module statuses
            module_statuses = {
                "AASX Module": certificate.module_status.aasx_module,
                "Twin Registry": certificate.module_status.twin_registry,
                "AI RAG": certificate.module_status.ai_rag,
                "KG Neo4j": certificate.module_status.kg_neo4j,
                "Physics Modeling": certificate.module_status.physics_modeling,
                "Federated Learning": certificate.module_status.federated_learning,
                "Data Governance": certificate.module_status.data_governance
            }
            
            for module_name, status in module_statuses.items():
                summaries[module_name] = {
                    "status": status.value,
                    "completion_date": certificate.created_at.isoformat() if status.value == "active" else None,
                    "performance_score": certificate.module_status.health_score
                }
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error generating module summaries: {e}")
            return {}
    
    async def _generate_quality_section(self, certificate: CertificateRegistry) -> Dict[str, Any]:
        """Generate quality assessment section"""
        try:
            quality = certificate.quality_assessment
            
            return {
                "overall_score": quality.overall_quality_score,
                "quality_level": quality.quality_level.value,
                "data_completeness": quality.data_completeness_score,
                "validation_rate": quality.validation_rate,
                "coverage_score": quality.coverage_score,
                "assessment_date": quality.last_assessment.isoformat() if quality.last_assessment else None,
                "assessment_notes": quality.assessment_notes
            }
            
        except Exception as e:
            logger.error(f"Error generating quality section: {e}")
            return {}
    
    async def _generate_compliance_section(self, certificate: CertificateRegistry) -> Dict[str, Any]:
        """Generate compliance tracking section"""
        try:
            compliance = certificate.compliance_tracking
            
            return {
                "compliance_status": compliance.compliance_status.value,
                "compliance_score": compliance.compliance_score,
                "regulatory_framework": compliance.regulatory_framework,
                "audit_date": compliance.last_audit.isoformat() if compliance.last_audit else None,
                "next_audit": compliance.next_audit.isoformat() if compliance.next_audit else None,
                "audit_notes": compliance.audit_notes
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance section: {e}")
            return {}
    
    async def _generate_security_section(self, certificate: CertificateRegistry) -> Dict[str, Any]:
        """Generate security metrics section"""
        try:
            security = certificate.security_metrics
            
            return {
                "security_score": security.security_score,
                "security_level": security.security_level.value,
                "threat_level": security.threat_level.value,
                "security_events": len(security.security_events),
                "last_assessment": security.last_security_assessment.isoformat() if security.last_security_assessment else None,
                "security_notes": security.security_notes
            }
            
        except Exception as e:
            logger.error(f"Error generating security section: {e}")
            return {}
    
    async def _generate_business_section(self, certificate: CertificateRegistry) -> Dict[str, Any]:
        """Generate business context section"""
        try:
            business = certificate.business_context
            
            return {
                "tags": business.tags,
                "custom_attributes": business.custom_attributes,
                "ownership": business.ownership,
                "approval_workflow": business.approval_workflow.value,
                "business_unit": business.business_unit,
                "priority": business.priority.value
            }
            
        except Exception as e:
            logger.error(f"Error generating business section: {e}")
            return {}
    
    async def _generate_digital_trust_section(self, certificate: CertificateRegistry) -> Dict[str, Any]:
        """Generate digital trust section"""
        try:
            trust = certificate.digital_trust
            
            return {
                "digital_signature": trust.digital_signature,
                "hash_value": trust.hash_value,
                "qr_code": trust.qr_code,
                "verification_url": trust.verification_url,
                "signature_timestamp": trust.signature_timestamp.isoformat() if trust.signature_timestamp else None,
                "certificate_authority": trust.certificate_authority
            }
            
        except Exception as e:
            logger.error(f"Error generating digital trust section: {e}")
            return {}
    
    async def _generate_metadata_section(self, certificate: CertificateRegistry) -> Dict[str, Any]:
        """Generate metadata section"""
        try:
            return {
                "created_at": certificate.created_at.isoformat(),
                "updated_at": certificate.updated_at.isoformat(),
                "created_by": certificate.created_by,
                "dept_id": certificate.dept_id,
                "certificate_type": certificate.certificate_type,
                "description": certificate.description
            }
            
        except Exception as e:
            logger.error(f"Error generating metadata section: {e}")
            return {}
    
    async def _generate_metrics_summary(self, metrics: List[CertificateMetrics]) -> Dict[str, Any]:
        """Generate metrics summary section"""
        try:
            if not metrics:
                return {}
            
            # Group metrics by category
            metrics_by_category = {}
            for metric in metrics:
                category = metric.metric_category.value
                if category not in metrics_by_category:
                    metrics_by_category[category] = []
                metrics_by_category[category].append({
                    "name": metric.metric_name,
                    "value": metric.metric_value,
                    "unit": metric.metric_unit,
                    "recorded_at": metric.recorded_at.isoformat()
                })
            
            return {
                "total_metrics": len(metrics),
                "categories": metrics_by_category,
                "latest_update": max(m.recorded_at for m in metrics).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating metrics summary: {e}")
            return {}
    
    async def _get_template_styling(self, template: CertificateTemplate) -> Dict[str, Any]:
        """Get template-specific styling"""
        try:
            if template.value not in self.template_cache:
                # Load template styling
                self.template_cache[template.value] = await self._load_template_styling(template)
            
            return self.template_cache[template.value]
            
        except Exception as e:
            logger.error(f"Error getting template styling: {e}")
            return {}
    
    async def _load_template_styling(self, template: CertificateTemplate) -> Dict[str, Any]:
        """Load template styling from configuration"""
        try:
            # This would typically load from a template configuration file
            # For now, return default styling
            base_styling = {
                "font_family": "Arial, sans-serif",
                "primary_color": "#2c3e50",
                "secondary_color": "#3498db",
                "accent_color": "#e74c3c",
                "background_color": "#ffffff",
                "border_style": "solid",
                "border_width": "2px"
            }
            
            # Template-specific customizations
            if template == CertificateTemplate.PREMIUM:
                base_styling.update({
                    "primary_color": "#1a1a1a",
                    "secondary_color": "#d4af37",
                    "border_style": "double"
                })
            elif template == CertificateTemplate.EXECUTIVE:
                base_styling.update({
                    "primary_color": "#2c3e50",
                    "secondary_color": "#34495e",
                    "font_family": "Georgia, serif"
                })
            elif template == CertificateTemplate.TECHNICAL:
                base_styling.update({
                    "primary_color": "#27ae60",
                    "secondary_color": "#2ecc71",
                    "font_family": "Courier New, monospace"
                })
            elif template == CertificateTemplate.COMPLIANCE:
                base_styling.update({
                    "primary_color": "#8e44ad",
                    "secondary_color": "#9b59b6",
                    "accent_color": "#e67e22"
                })
            
            return base_styling
            
        except Exception as e:
            logger.error(f"Error loading template styling: {e}")
            return {}
    
    async def _format_certificate_content(
        self,
        content: Dict[str, Any],
        output_format: OutputFormat
    ) -> str:
        """Format certificate content for output"""
        try:
            if output_format == OutputFormat.JSON:
                return json.dumps(content, indent=2, default=str)
            elif output_format == OutputFormat.HTML:
                return await self._format_as_html(content)
            elif output_format == OutputFormat.MARKDOWN:
                return await self._format_as_markdown(content)
            elif output_format == OutputFormat.XML:
                return await self._format_as_xml(content)
            else:
                # Default to JSON for PDF (would be converted later)
                return json.dumps(content, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error formatting certificate content: {e}")
            return ""
    
    async def _format_as_html(self, content: Dict[str, Any]) -> str:
        """Format certificate content as HTML"""
        try:
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Digital Twin Analytics Certificate</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 20px; }
                    .section { margin: 20px 0; padding: 15px; border: 1px solid #ecf0f1; }
                    .section-title { color: #2c3e50; font-weight: bold; margin-bottom: 10px; }
                    .metric { display: inline-block; margin: 5px 10px; }
                    .status-active { color: #27ae60; }
                    .status-error { color: #e74c3c; }
                    .status-pending { color: #f39c12; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Digital Twin Analytics Certificate</h1>
                    <h2>Certificate ID: {certificate_id}</h2>
                    <p>Issued: {issue_date}</p>
                </div>
            """.format(
                certificate_id=content.get("certificate_header", {}).get("subtitle", "N/A"),
                issue_date=content.get("certificate_header", {}).get("issue_date", "N/A")
            )
            
            # Add sections
            for section_name, section_data in content.items():
                if section_name in ["styling", "certificate_header"]:
                    continue
                
                if section_data:
                    html += f'<div class="section"><div class="section-title">{section_name.replace("_", " ").title()}</div>'
                    
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            if isinstance(value, dict):
                                html += f'<div><strong>{key.replace("_", " ").title()}:</strong></div>'
                                for sub_key, sub_value in value.items():
                                    html += f'<div class="metric">{sub_key.replace("_", " ").title()}: {sub_value}</div>'
                            else:
                                html += f'<div class="metric">{key.replace("_", " ").title()}: {value}</div>'
                    elif isinstance(section_data, list):
                        for item in section_data:
                            html += f'<div class="metric">{item}</div>'
                    else:
                        html += f'<div class="metric">{section_data}</div>'
                    
                    html += '</div>'
            
            html += "</body></html>"
            return html
            
        except Exception as e:
            logger.error(f"Error formatting as HTML: {e}")
            return ""
    
    async def _format_as_markdown(self, content: Dict[str, Any]) -> str:
        """Format certificate content as Markdown"""
        try:
            markdown = "# Digital Twin Analytics Certificate\n\n"
            
            # Add header
            header = content.get("certificate_header", {})
            markdown += f"**Certificate ID:** {header.get('subtitle', 'N/A')}\n"
            markdown += f"**Issue Date:** {header.get('issue_date', 'N/A')}\n"
            markdown += f"**Status:** {header.get('status', 'N/A')}\n\n"
            
            # Add sections
            for section_name, section_data in content.items():
                if section_name in ["styling", "certificate_header"]:
                    continue
                
                if section_data:
                    markdown += f"## {section_name.replace('_', ' ').title()}\n\n"
                    
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            if isinstance(value, dict):
                                markdown += f"### {key.replace('_', ' ').title()}\n"
                                for sub_key, sub_value in value.items():
                                    markdown += f"- **{sub_key.replace('_', ' ').title()}:** {sub_value}\n"
                                markdown += "\n"
                            else:
                                markdown += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                    elif isinstance(section_data, list):
                        for item in section_data:
                            markdown += f"- {item}\n"
                    else:
                        markdown += f"{section_data}\n"
                    
                    markdown += "\n"
            
            return markdown
            
        except Exception as e:
            logger.error(f"Error formatting as Markdown: {e}")
            return ""
    
    async def _format_as_xml(self, content: Dict[str, Any]) -> str:
        """Format certificate content as XML"""
        try:
            xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml += '<certificate xmlns="http://example.com/certificate">\n'
            
            # Add header
            header = content.get("certificate_header", {})
            xml += '  <header>\n'
            xml += f'    <title>{header.get("title", "Digital Twin Analytics Certificate")}</title>\n'
            xml += f'    <certificate_id>{header.get("subtitle", "N/A")}</certificate_id>\n'
            xml += f'    <issue_date>{header.get("issue_date", "N/A")}</issue_date>\n'
            xml += f'    <status>{header.get("status", "N/A")}</status>\n'
            xml += '  </header>\n'
            
            # Add sections
            for section_name, section_data in content.items():
                if section_name in ["styling", "certificate_header"]:
                    continue
                
                if section_data:
                    xml += f'  <{section_name}>\n'
                    
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            if isinstance(value, dict):
                                xml += f'    <{key}>\n'
                                for sub_key, sub_value in value.items():
                                    xml += f'      <{sub_key}>{sub_value}</{sub_key}>\n'
                                xml += f'    </{key}>\n'
                            else:
                                xml += f'    <{key}>{value}</{key}>\n'
                    elif isinstance(section_data, list):
                        for item in section_data:
                            xml += f'    <item>{item}</item>\n'
                    else:
                        xml += f'    <value>{section_data}</value>\n'
                    
                    xml += f'  </{section_name}>\n'
            
            xml += '</certificate>'
            return xml
            
        except Exception as e:
            logger.error(f"Error formatting as XML: {e}")
            return ""
    
    async def _save_certificate_file(
        self,
        certificate_id: str,
        content: str,
        output_format: OutputFormat
    ) -> Path:
        """Save certificate to file"""
        try:
            # Create filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{certificate_id}_{timestamp}.{output_format.value}"
            file_path = self.output_dir / filename
            
            # Save content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved certificate to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving certificate file: {e}")
            raise
    
    async def _create_certificate_version(
        self,
        certificate_id: str,
        output_format: OutputFormat,
        template: CertificateTemplate,
        file_path: Path
    ) -> Optional[CertificateVersion]:
        """Create a new certificate version"""
        try:
            version_data = {
                "certificate_id": certificate_id,
                "version_number": await self.versions_service.get_next_version_number(certificate_id),
                "version_type": VersionType.MINOR,
                "description": f"Generated {output_format.value} certificate using {template.value} template",
                "change_reason": "Certificate generation",
                "output_format": output_format.value,
                "template_used": template.value,
                "file_path": str(file_path)
            }
            
            version = await self.versions_service.create_version(version_data)
            logger.info(f"Created certificate version: {version.version_id}")
            return version
            
        except Exception as e:
            logger.error(f"Error creating certificate version: {e}")
            return None
    
    async def _update_generation_metrics(
        self,
        certificate_id: str,
        output_format: OutputFormat,
        template: CertificateTemplate
    ) -> None:
        """Update generation metrics"""
        try:
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=MetricCategory.PERFORMANCE,
                metric_name="certificate_generation",
                metric_value=1.0,
                metric_unit="count",
                additional_data={
                    "output_format": output_format.value,
                    "template": template.value,
                    "generation_time": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating generation metrics: {e}")
    
    async def get_generation_history(self, certificate_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get certificate generation history"""
        try:
            # Get versions for this certificate
            versions = await self.versions_service.get_certificate_versions(
                certificate_id, limit=limit
            )
            
            history = []
            for version in versions:
                if hasattr(version, 'output_format') and version.output_format:
                    history.append({
                        "version_id": version.version_id,
                        "version_number": version.version_number,
                        "output_format": version.output_format,
                        "template": getattr(version, 'template_used', 'unknown'),
                        "generated_at": version.created_at.isoformat(),
                        "description": version.description
                    })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting generation history: {e}")
            return []
    
    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available certificate templates"""
        try:
            templates = []
            for template in CertificateTemplate:
                styling = await self._get_template_styling(template)
                templates.append({
                    "template_id": template.value,
                    "name": template.value.replace("_", " ").title(),
                    "description": f"{template.value.replace('_', ' ').title()} certificate template",
                    "styling": styling
                })
            
            return templates
            
        except Exception as e:
            logger.error(f"Error getting available templates: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the certificate generator"""
        try:
            health_status = {
                "status": "healthy",
                "active_locks": len(self.generation_locks),
                "template_cache_size": len(self.template_cache),
                "output_directory": str(self.output_dir),
                "output_directory_exists": self.output_dir.exists(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
