"""
Certificate Registry Service - Business Logic Layer

This service provides business logic for certificate management operations.
It coordinates between models and repositories to implement high-level
certificate operations including module status management, quality assessment,
compliance tracking, security metrics, business context, and digital trust.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json
import asyncio
from uuid import uuid4

from ..models.certificates_registry import (
    CertificateRegistry,
    ModuleStatus,
    CertificateStatus,
    ComplianceStatus,
    SecurityLevel,
    QualityLevel,
    ModuleSummary
)
from ..repositories.certificates_registry_repository import CertificatesRegistryRepository


logger = logging.getLogger(__name__)


class CertificatesRegistryService:
    """Service for certificate registry business logic"""
    
    def __init__(self, repository: CertificatesRegistryRepository):
        self.repository = repository
    
    # Certificate Lifecycle Management
    async def create_certificate(
        self,
        file_id: str,
        user_id: str,
        org_id: str,
        dept_id: str,
        certificate_name: str,
        project_id: Optional[str] = None,
        twin_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[CertificateRegistry]:
        """Create a new certificate with initial setup"""
        try:
            # Generate unique certificate ID
            certificate_id = f"cert_{uuid4().hex[:16]}"
            
            # Create certificate instance
            certificate = CertificateRegistry(
                certificate_id=certificate_id,
                file_id=file_id,
                user_id=user_id,
                org_id=org_id,
                dept_id=dept_id,
                project_id=project_id,
                twin_id=twin_id,
                certificate_name=certificate_name,
                description=description
            )
            
            # Validate integrity before saving
            if not await certificate.validate_integrity():
                logger.error(f"Certificate integrity validation failed for {certificate_id}")
                return None
            
            # Save to database
            if await self.repository.create_certificate(certificate):
                logger.info(f"Created certificate: {certificate_id}")
                return certificate
            else:
                logger.error(f"Failed to save certificate to database: {certificate_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating certificate: {e}")
            return None
    
    async def get_certificate(self, certificate_id: str) -> Optional[CertificateRegistry]:
        """Retrieve a certificate by ID"""
        try:
            return await self.repository.get_certificate_by_id(certificate_id)
        except Exception as e:
            logger.error(f"Error retrieving certificate {certificate_id}: {e}")
            return None
    
    async def get_certificates_by_org(self, org_id: str, limit: int = 100) -> List[CertificateRegistry]:
        """Get all certificates for an organization"""
        try:
            return await self.repository.get_certificates_by_org(org_id, limit)
        except Exception as e:
            logger.error(f"Error retrieving certificates for org {org_id}: {e}")
            return []
    
    async def get_certificates_by_dept(self, dept_id: str, limit: int = 100) -> List[CertificateRegistry]:
        """Get all certificates for a department"""
        try:
            return await self.repository.get_certificates_by_dept(dept_id, limit)
        except Exception as e:
            logger.error(f"Error retrieving certificates for dept {dept_id}: {e}")
            return []
    
    async def get_certificates_by_user(self, user_id: str, limit: int = 100) -> List[CertificateRegistry]:
        """Get all certificates for a user"""
        try:
            return await self.repository.get_certificates_by_user(user_id, limit)
        except Exception as e:
            logger.error(f"Error retrieving certificates for user {user_id}: {e}")
            return []
    
    async def update_certificate(self, certificate: CertificateRegistry) -> bool:
        """Update an existing certificate"""
        try:
            # Validate integrity before updating
            if not await certificate.validate_integrity():
                logger.error(f"Certificate integrity validation failed for {certificate.certificate_id}")
                return False
            
            # Update timestamp
            certificate.updated_at = datetime.utcnow()
            
            # Save to database
            return await self.repository.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error updating certificate {certificate.certificate_id}: {e}")
            return False
    
    async def delete_certificate(self, certificate_id: str) -> bool:
        """Delete a certificate by ID"""
        try:
            return await self.repository.delete_certificate(certificate_id)
        except Exception as e:
            logger.error(f"Error deleting certificate {certificate_id}: {e}")
            return False
    
    # Module Status Management
    async def update_module_status(
        self, 
        certificate_id: str, 
        module_name: str, 
        status: ModuleStatus
    ) -> bool:
        """Update status for a specific module"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Update module status in the component model
            if hasattr(certificate.module_status, f"{module_name}_status"):
                setattr(certificate.module_status, f"{module_name}_status", status)
            
            # Update overall status based on individual module statuses
            await self._update_overall_module_status(certificate)
            
            # Update health metrics
            await certificate.update_health_metrics()
            
            # Save to database
            return await self.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error updating module status for certificate {certificate_id}: {e}")
            return False
    
    async def _update_overall_module_status(self, certificate: CertificateRegistry) -> None:
        """Update overall module status based on individual module statuses"""
        try:
            # Count active and error modules
            active_count = 0
            error_count = 0
            total_modules = 0
            
            # Check each module status
            for attr_name in dir(certificate.module_status):
                if attr_name.endswith('_status') and not attr_name.startswith('_'):
                    total_modules += 1
                    status = getattr(certificate.module_status, attr_name)
                    if status == ModuleStatus.ACTIVE:
                        active_count += 1
                    elif status == ModuleStatus.ERROR:
                        error_count += 1
            
            # Update overall status
            if error_count > 0:
                certificate.module_status.overall_status = ModuleStatus.ERROR
            elif active_count == total_modules:
                certificate.module_status.overall_status = ModuleStatus.ACTIVE
            elif active_count > 0:
                certificate.module_status.overall_status = ModuleStatus.PARTIAL
            else:
                certificate.module_status.overall_status = ModuleStatus.INACTIVE
            
            # Update counts
            certificate.module_status.active_modules = active_count
            certificate.module_status.error_count = error_count
            certificate.module_status.total_modules = total_modules
            
            # Calculate health score
            if total_modules > 0:
                certificate.module_status.health_score = (active_count / total_modules) * 100
            else:
                certificate.module_status.health_score = 0
                
        except Exception as e:
            logger.error(f"Error updating overall module status: {e}")
    
    async def get_module_status(self, certificate_id: str, module_name: str) -> Optional[ModuleStatus]:
        """Get current status for a specific module"""
        try:
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                return None
            
            if hasattr(certificate.module_status, f"{module_name}_status"):
                return getattr(certificate.module_status, f"{module_name}_status")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting module status for certificate {certificate_id}: {e}")
            return None
    
    async def get_overall_completion(self, certificate_id: str) -> float:
        """Get overall completion percentage for a certificate"""
        try:
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                return 0.0
            
            # Calculate completion based on module status health score
            return certificate.module_status.health_score
            
        except Exception as e:
            logger.error(f"Error getting completion percentage for certificate {certificate_id}: {e}")
            return 0.0
    
    # Module Summary Management
    async def add_module_summary(
        self, 
        certificate_id: str, 
        module_name: str, 
        summary: ModuleSummary
    ) -> bool:
        """Add or update module summary for a certificate"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Add module summary to the component model
            if hasattr(certificate.module_summaries, f"{module_name}_summary"):
                setattr(certificate.module_summaries, f"{module_name}_summary", summary)
            
            # Update summary metadata
            certificate.module_summaries.last_updated = datetime.utcnow()
            certificate.module_summaries.total_summaries += 1
            
            # Update quality assessment based on summary data
            await self._update_quality_from_summaries(certificate)
            
            # Update health metrics
            await certificate.update_health_metrics()
            
            # Save to database
            return await self.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error adding module summary for certificate {certificate_id}: {e}")
            return False
    
    async def _update_quality_from_summaries(self, certificate: CertificateRegistry) -> None:
        """Update quality assessment based on module summaries"""
        try:
            total_quality = 0
            summary_count = 0
            
            # Calculate average quality from all module summaries
            for attr_name in dir(certificate.module_summaries):
                if attr_name.endswith('_summary') and not attr_name.startswith('_'):
                    summary = getattr(certificate.module_summaries, attr_name)
                    if summary and hasattr(summary, 'quality_score'):
                        total_quality += summary.quality_score
                        summary_count += 1
            
            # Update overall quality score
            if summary_count > 0:
                certificate.quality_assessment.overall_quality_score = total_quality / summary_count
                
                # Update quality level based on score
                if certificate.quality_assessment.overall_quality_score >= 90:
                    certificate.quality_assessment.quality_level = QualityLevel.EXCELLENT
                elif certificate.quality_assessment.overall_quality_score >= 80:
                    certificate.quality_assessment.quality_level = QualityLevel.GOOD
                elif certificate.quality_assessment.overall_quality_score >= 70:
                    certificate.quality_assessment.quality_level = QualityLevel.FAIR
                elif certificate.quality_assessment.overall_quality_score >= 50:
                    certificate.quality_assessment.quality_level = QualityLevel.POOR
                else:
                    certificate.quality_assessment.quality_level = QualityLevel.CRITICAL
                    
        except Exception as e:
            logger.error(f"Error updating quality from summaries: {e}")
    
    async def get_module_summary(self, certificate_id: str, module_name: str) -> Optional[ModuleSummary]:
        """Get module summary for a specific module"""
        try:
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                return None
            
            if hasattr(certificate.module_summaries, f"{module_name}_summary"):
                return getattr(certificate.module_summaries, f"{module_name}_summary")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting module summary for certificate {certificate_id}: {e}")
            return None
    
    # Quality Assessment Management
    async def update_quality_assessment(
        self, 
        certificate_id: str, 
        quality_data: Dict[str, Any]
    ) -> bool:
        """Update quality assessment for a certificate"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Update quality assessment fields
            for key, value in quality_data.items():
                if hasattr(certificate.quality_assessment, key):
                    setattr(certificate.quality_assessment, key, value)
            
            # Update timestamp
            certificate.quality_assessment.last_assessment = datetime.utcnow()
            
            # Save to database
            return await self.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error updating quality assessment for certificate {certificate_id}: {e}")
            return False
    
    async def get_quality_score(self, certificate_id: str) -> float:
        """Get overall quality score for a certificate"""
        try:
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                return 0.0
            
            return certificate.quality_assessment.overall_quality_score
            
        except Exception as e:
            logger.error(f"Error getting quality score for certificate {certificate_id}: {e}")
            return 0.0
    
    # Compliance Tracking Management
    async def update_compliance_status(
        self, 
        certificate_id: str, 
        compliance_data: Dict[str, Any]
    ) -> bool:
        """Update compliance tracking for a certificate"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Update compliance tracking fields
            for key, value in compliance_data.items():
                if hasattr(certificate.compliance_tracking, key):
                    setattr(certificate.compliance_tracking, key, value)
            
            # Save to database
            return await self.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error updating compliance status for certificate {certificate_id}: {e}")
            return False
    
    async def get_compliance_status(self, certificate_id: str) -> str:
        """Get compliance status for a certificate"""
        try:
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                return "unknown"
            
            return certificate.compliance_tracking.compliance_status.value
            
        except Exception as e:
            logger.error(f"Error getting compliance status for certificate {certificate_id}: {e}")
            return "unknown"
    
    # Security Metrics Management
    async def update_security_metrics(
        self, 
        certificate_id: str, 
        security_data: Dict[str, Any]
    ) -> bool:
        """Update security metrics for a certificate"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Update security metrics fields
            for key, value in security_data.items():
                if hasattr(certificate.security_metrics, key):
                    setattr(certificate.security_metrics, key, value)
            
            # Save to database
            return await self.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error updating security metrics for certificate {certificate_id}: {e}")
            return False
    
    async def get_security_score(self, certificate_id: str) -> float:
        """Get security score for a certificate"""
        try:
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                return 0.0
            
            return certificate.security_metrics.security_score
            
        except Exception as e:
            logger.error(f"Error getting security score for certificate {certificate_id}: {e}")
            return 0.0
    
    # Business Context Management
    async def update_business_context(
        self, 
        certificate_id: str, 
        business_data: Dict[str, Any]
    ) -> bool:
        """Update business context for a certificate"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Update business context fields
            for key, value in business_data.items():
                if hasattr(certificate.business_context, key):
                    setattr(certificate.business_context, key, value)
            
            # Save to database
            return await self.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error updating business context for certificate {certificate_id}: {e}")
            return False
    
    # Digital Trust Management
    async def update_digital_trust(
        self, 
        certificate_id: str, 
        trust_data: Dict[str, Any]
    ) -> bool:
        """Update digital trust information for a certificate"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Update digital trust fields
            for key, value in trust_data.items():
                if hasattr(certificate.digital_trust, key):
                    setattr(certificate.digital_trust, key, value)
            
            # Save to database
            return await self.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error updating digital trust for certificate {certificate_id}: {e}")
            return False
    
    async def verify_certificate(self, certificate_id: str, verification_hash: str) -> bool:
        """Verify a certificate digitally"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Update verification status
            certificate.digital_trust.verification_hash = verification_hash
            certificate.digital_trust.verification_status = "verified"
            certificate.digital_trust.last_verification = datetime.utcnow()
            
            # Save to database
            return await self.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error verifying certificate {certificate_id}: {e}")
            return False
    
    # Certificate Status Management
    async def update_certificate_status(
        self, 
        certificate_id: str, 
        status: CertificateStatus
    ) -> bool:
        """Update overall certificate status"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Update status
            certificate.status = status
            
            # Save to database
            return await self.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error updating certificate status for {certificate_id}: {e}")
            return False
    
    async def mark_certificate_complete(self, certificate_id: str) -> bool:
        """Mark a certificate as complete"""
        try:
            # Get current certificate
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Check if all modules are completed based on health score
            if certificate.module_status.health_score >= 100.0:
                certificate.certificate_status = CertificateStatus.READY
                return await self.update_certificate(certificate)
            else:
                logger.warning(f"Certificate {certificate_id} not ready for completion: {certificate.module_status.health_score}%")
                return False
                
        except Exception as e:
            logger.error(f"Error marking certificate complete {certificate_id}: {e}")
            return False
    
    # Search and Filter Operations
    async def search_certificates(
        self, 
        search_criteria: Dict[str, Any], 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Search certificates based on multiple criteria"""
        try:
            return await self.repository.search_certificates(search_criteria, limit)
        except Exception as e:
            logger.error(f"Error searching certificates: {e}")
            return []
    
    async def get_certificates_by_status(
        self, 
        status: CertificateStatus, 
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by status"""
        try:
            return await self.repository.get_certificates_by_status(status, limit)
        except Exception as e:
            logger.error(f"Error getting certificates by status {status}: {e}")
            return []
    
    # Bulk Operations
    async def bulk_update_module_statuses(
        self, 
        updates: List[Tuple[str, str, ModuleStatus]]
    ) -> bool:
        """Bulk update module statuses for multiple certificates"""
        try:
            return await self.repository.bulk_update_module_statuses(updates)
        except Exception as e:
            logger.error(f"Error in bulk update module statuses: {e}")
            return False
    
    # Statistics and Analytics
    async def get_certificate_stats(
        self, 
        org_id: Optional[str] = None, 
        dept_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get certificate statistics and analytics"""
        try:
            return await self.repository.get_certificate_stats(org_id, dept_id)
        except Exception as e:
            logger.error(f"Error getting certificate stats: {e}")
            return {}
    
    # Health Check
    async def health_check(self) -> bool:
        """Check service health"""
        try:
            return await self.repository.health_check()
        except Exception as e:
            logger.error(f"Service health check failed: {e}")
            return False
    
    # Certificate Export
    async def export_certificate(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Export certificate data for external use"""
        try:
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                return None
            
            return await certificate.export_data()
            
        except Exception as e:
            logger.error(f"Error exporting certificate {certificate_id}: {e}")
            return None
    
    # Certificate Validation
    async def validate_certificate_integrity(self, certificate_id: str) -> bool:
        """Validate certificate data integrity"""
        try:
            certificate = await self.get_certificate(certificate_id)
            if not certificate:
                return False
            
            return await certificate.validate_integrity()
            
        except Exception as e:
            logger.error(f"Error validating certificate integrity {certificate_id}: {e}")
            return False
