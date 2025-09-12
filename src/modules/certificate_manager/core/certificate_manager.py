"""
Certificate Manager - Main Orchestration Service

This is the core orchestrator that coordinates all certificate operations
including creation, updates, real-time monitoring, and lifecycle management.
Uses async patterns throughout for non-blocking operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4

from ..models.certificates_registry import (
    CertificateRegistry,
    ModuleStatus,
    CertificateStatus,
    QualityLevel,
    ComplianceStatus,
    SecurityLevel
)
from ..models.certificates_versions import CertificateVersions, VersionType
from ..models.certificates_metrics import CertificateMetrics, MetricCategory
from ..services.certificates_registry_service import CertificatesRegistryService
from ..services.certificates_versions_service import CertificatesVersionsService
from ..services.certificates_metrics_service import CertificatesMetricsService
from ..repositories.certificates_registry_repository import CertificatesRegistryRepository
from ..repositories.certificates_versions_repository import CertificatesVersionsRepository
from ..repositories.certificates_metrics_repository import CertificatesMetricsRepository

logger = logging.getLogger(__name__)


class CertificateManager:
    """
    Main certificate orchestration service
    
    Coordinates all certificate operations including:
    - Certificate lifecycle management
    - Real-time updates and monitoring
    - Module integration and data collection
    - Progress tracking and validation
    - Business intelligence generation
    """
    
    def __init__(self, db_session):
        """Initialize the certificate manager with all required services"""
        try:
            # Initialize repositories
            self.registry_repo = CertificatesRegistryRepository(db_session)
            self.versions_repo = CertificatesVersionsRepository(db_session)
            self.metrics_repo = CertificatesMetricsRepository(db_session)
            
            # Initialize services
            self.registry_service = CertificatesRegistryService(self.registry_repo)
            self.versions_service = CertificatesVersionsService(db_session)
            self.metrics_service = CertificatesMetricsService(db_session)
            
            # Track active certificates
            self.active_certificates: Dict[str, CertificateRegistry] = {}
            self.certificate_locks: Dict[str, asyncio.Lock] = {}
            
            logger.info("Certificate Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Certificate Manager: {e}")
            raise
    
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
        """
        Create a new certificate with initial setup
        
        This is the main entry point for certificate creation.
        Sets up initial state and prepares for real-time updates.
        """
        try:
            logger.info(f"Creating certificate for file: {file_id}")
            
            # Create certificate using registry service
            certificate = await self.registry_service.create_certificate(
                file_id=file_id,
                user_id=user_id,
                org_id=org_id,
                dept_id=dept_id,
                certificate_name=certificate_name,
                project_id=project_id,
                twin_id=twin_id,
                description=description
            )
            
            if not certificate:
                logger.error(f"Failed to create certificate for file: {file_id}")
                return None
            
            # Initialize certificate tracking
            await self._initialize_certificate_tracking(certificate)
            
            # Create initial metrics
            await self._create_initial_metrics(certificate)
            
            # Add to active certificates
            self.active_certificates[certificate.certificate_id] = certificate
            self.certificate_locks[certificate.certificate_id] = asyncio.Lock()
            
            logger.info(f"Certificate created successfully: {certificate.certificate_id}")
            return certificate
            
        except Exception as e:
            logger.error(f"Error creating certificate: {e}")
            return None
    
    async def _initialize_certificate_tracking(self, certificate: CertificateRegistry) -> None:
        """Initialize certificate tracking and monitoring"""
        try:
            # Set initial module statuses to PENDING
            await self.registry_service.update_module_status(
                certificate.certificate_id,
                "aasx_module",
                ModuleStatus.PENDING
            )
            
            # Initialize other module statuses
            module_names = [
                "twin_registry", "ai_rag", "kg_neo4j", 
                "physics_modeling", "federated_learning", "data_governance"
            ]
            
            for module_name in module_names:
                await self.registry_service.update_module_status(
                    certificate.certificate_id,
                    module_name,
                    ModuleStatus.PENDING
                )
            
            logger.info(f"Initialized tracking for certificate: {certificate.certificate_id}")
            
        except Exception as e:
            logger.error(f"Error initializing certificate tracking: {e}")
    
    async def _create_initial_metrics(self, certificate: CertificateRegistry) -> None:
        """Create initial metrics for the certificate"""
        try:
            # Create initial performance metrics
            await self.metrics_service.create_metrics(
                certificate_id=certificate.certificate_id,
                metric_category=MetricCategory.PERFORMANCE,
                metric_name="certificate_creation_time",
                metric_value=0.0,
                metric_unit="seconds"
            )
            
            # Create initial quality metrics
            await self.metrics_service.create_metrics(
                certificate_id=certificate.certificate_id,
                metric_category=MetricCategory.QUALITY,
                metric_name="initial_quality_score",
                metric_value=0.0,
                metric_unit="percentage"
            )
            
            logger.info(f"Created initial metrics for certificate: {certificate.certificate_id}")
            
        except Exception as e:
            logger.error(f"Error creating initial metrics: {e}")
    
    async def update_certificate_progress(
        self,
        certificate_id: str,
        module_name: str,
        progress_data: Dict[str, Any]
    ) -> bool:
        """
        Update certificate progress for a specific module
        
        This is called when modules complete processing and want to
        update the certificate with their results.
        """
        try:
            if certificate_id not in self.active_certificates:
                logger.error(f"Certificate not found: {certificate_id}")
                return False
            
            # Acquire lock for this certificate
            async with self.certificate_locks[certificate_id]:
                # Update module status
                await self._update_module_status(certificate_id, module_name, progress_data)
                
                # Update module summary
                await self._update_module_summary(certificate_id, module_name, progress_data)
                
                # Update overall progress
                await self._update_overall_progress(certificate_id)
                
                # Check if certificate is complete
                await self._check_certificate_completion(certificate_id)
                
                # Update metrics
                await self._update_certificate_metrics(certificate_id, module_name, progress_data)
                
                logger.info(f"Updated progress for certificate {certificate_id}, module {module_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating certificate progress: {e}")
            return False
    
    async def _update_module_status(
        self, 
        certificate_id: str, 
        module_name: str, 
        progress_data: Dict[str, Any]
    ) -> None:
        """Update module status based on progress data"""
        try:
            # Determine status from progress data
            if progress_data.get("status") == "completed":
                status = ModuleStatus.ACTIVE
            elif progress_data.get("status") == "failed":
                status = ModuleStatus.ERROR
            elif progress_data.get("status") == "in_progress":
                status = ModuleStatus.MAINTENANCE
            else:
                status = ModuleStatus.PENDING
            
            # Update module status
            await self.registry_service.update_module_status(
                certificate_id, module_name, status
            )
            
        except Exception as e:
            logger.error(f"Error updating module status: {e}")
    
    async def _update_module_summary(
        self, 
        certificate_id: str, 
        module_name: str, 
        progress_data: Dict[str, Any]
    ) -> None:
        """Update module summary with new data"""
        try:
            # Create module summary from progress data
            from ..models.certificates_registry import ModuleSummary
            
            summary = ModuleSummary(
                module_name=module_name,
                processing_time=progress_data.get("processing_time", 0.0),
                data_quality_score=progress_data.get("quality_score", 0.0),
                records_processed=progress_data.get("records_processed", 0),
                errors_count=progress_data.get("errors_count", 0),
                warnings_count=progress_data.get("warnings_count", 0),
                last_updated=datetime.utcnow()
            )
            
            # Add summary to certificate
            await self.registry_service.add_module_summary(
                certificate_id, module_name, summary
            )
            
        except Exception as e:
            logger.error(f"Error updating module summary: {e}")
    
    async def _update_overall_progress(self, certificate_id: str) -> None:
        """Update overall certificate progress"""
        try:
            # Get current certificate
            certificate = await self.registry_service.get_certificate(certificate_id)
            if not certificate:
                return
            
            # Update health metrics
            await certificate.update_health_metrics()
            
            # Save updated certificate
            await self.registry_service.update_certificate(certificate)
            
        except Exception as e:
            logger.error(f"Error updating overall progress: {e}")
    
    async def _check_certificate_completion(self, certificate_id: str) -> None:
        """Check if certificate is complete and handle completion"""
        try:
            # Get current certificate
            certificate = await self.registry_service.get_certificate(certificate_id)
            if not certificate:
                return
            
            # Check if all modules are completed
            if certificate.module_status.health_score >= 100.0:
                # Mark certificate as complete
                await self.registry_service.mark_certificate_complete(certificate_id)
                
                # Create completion version
                await self._create_completion_version(certificate)
                
                # Generate final business intelligence
                await self._generate_final_business_intelligence(certificate_id)
                
                logger.info(f"Certificate {certificate_id} marked as complete")
                
        except Exception as e:
            logger.error(f"Error checking certificate completion: {e}")
    
    async def _create_completion_version(self, certificate: CertificateRegistry) -> None:
        """Create final version when certificate is complete"""
        try:
            # Create completion version
            version = await self.versions_service.create_version(
                certificate_id=certificate.certificate_id,
                version_number="1.0.0",
                version_type=VersionType.MAJOR,
                change_description="Certificate completion - all modules processed",
                change_impact="HIGH",
                change_category="COMPLETION",
                user_id=certificate.created_by
            )
            
            logger.info(f"Created completion version: {version.version_id}")
            
        except Exception as e:
            logger.error(f"Error creating completion version: {e}")
    
    async def _generate_final_business_intelligence(self, certificate_id: str) -> None:
        """Generate final business intelligence for completed certificate"""
        try:
            # Get final metrics
            metrics = await self.metrics_service.get_certificate_metrics(
                certificate_id, limit=100
            )
            
            # Generate business intelligence summary
            bi_summary = await self._analyze_certificate_data(certificate_id, metrics)
            
            # Store business intelligence
            await self._store_business_intelligence(certificate_id, bi_summary)
            
            logger.info(f"Generated business intelligence for certificate: {certificate_id}")
            
        except Exception as e:
            logger.error(f"Error generating business intelligence: {e}")
    
    async def _analyze_certificate_data(
        self, 
        certificate_id: str, 
        metrics: List[CertificateMetrics]
    ) -> Dict[str, Any]:
        """Analyze certificate data to generate business intelligence"""
        try:
            # Get certificate details
            certificate = await self.registry_service.get_certificate(certificate_id)
            if not certificate:
                return {}
            
            # Analyze performance metrics
            performance_metrics = [m for m in metrics if m.metric_category == MetricCategory.PERFORMANCE]
            avg_processing_time = sum(m.metric_value for m in performance_metrics) / len(performance_metrics) if performance_metrics else 0
            
            # Analyze quality metrics
            quality_metrics = [m for m in metrics if m.metric_category == MetricCategory.QUALITY]
            avg_quality_score = sum(m.metric_value for m in quality_metrics) / len(quality_metrics) if quality_metrics else 0
            
            # Generate insights
            insights = {
                "certificate_id": certificate_id,
                "total_processing_time": avg_processing_time,
                "overall_quality_score": avg_quality_score,
                "modules_completed": certificate.module_status.active_modules,
                "completion_percentage": certificate.module_status.health_score,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing certificate data: {e}")
            return {}
    
    async def _store_business_intelligence(
        self, 
        certificate_id: str, 
        bi_summary: Dict[str, Any]
    ) -> None:
        """Store business intelligence summary"""
        try:
            # Store as metrics
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=MetricCategory.BUSINESS,
                metric_name="business_intelligence_score",
                metric_value=bi_summary.get("overall_quality_score", 0.0),
                metric_unit="percentage"
            )
            
        except Exception as e:
            logger.error(f"Error storing business intelligence: {e}")
    
    async def _update_certificate_metrics(
        self, 
        certificate_id: str, 
        module_name: str, 
        progress_data: Dict[str, Any]
    ) -> None:
        """Update certificate metrics with new data"""
        try:
            # Update performance metrics
            if "processing_time" in progress_data:
                await self.metrics_service.create_metrics(
                    certificate_id=certificate_id,
                    metric_category=MetricCategory.PERFORMANCE,
                    metric_name=f"{module_name}_processing_time",
                    metric_value=progress_data["processing_time"],
                    metric_unit="seconds"
                )
            
            # Update quality metrics
            if "quality_score" in progress_data:
                await self.metrics_service.create_metrics(
                    certificate_id=certificate_id,
                    metric_category=MetricCategory.QUALITY,
                    metric_name=f"{module_name}_quality_score",
                    metric_value=progress_data["quality_score"],
                    metric_unit="percentage"
                )
                
        except Exception as e:
            logger.error(f"Error updating certificate metrics: {e}")
    
    async def get_certificate_status(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive certificate status"""
        try:
            if certificate_id not in self.active_certificates:
                return None
            
            # Get certificate details
            certificate = await self.registry_service.get_certificate(certificate_id)
            if not certificate:
                return None
            
            # Get latest metrics
            metrics = await self.metrics_service.get_certificate_metrics(
                certificate_id, limit=10
            )
            
            # Build status response
            status = {
                "certificate_id": certificate_id,
                "status": certificate.certificate_status.value,
                "completion_percentage": certificate.module_status.health_score,
                "module_status": {
                    "aasx_module": certificate.module_status.aasx_module.value,
                    "twin_registry": certificate.module_status.twin_registry.value,
                    "ai_rag": certificate.module_status.ai_rag.value,
                    "kg_neo4j": certificate.module_status.kg_neo4j.value,
                    "physics_modeling": certificate.module_status.physics_modeling.value,
                    "federated_learning": certificate.module_status.federated_learning.value,
                    "data_governance": certificate.module_status.data_governance.value
                },
                "quality_score": certificate.quality_assessment.overall_quality_score,
                "compliance_status": certificate.compliance_tracking.compliance_status.value,
                "security_score": certificate.security_metrics.security_score,
                "last_updated": certificate.updated_at.isoformat() if certificate.updated_at else None,
                "metrics_count": len(metrics)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting certificate status: {e}")
            return None
    
    async def get_all_certificates_status(self) -> List[Dict[str, Any]]:
        """Get status of all active certificates"""
        try:
            statuses = []
            
            for certificate_id in self.active_certificates:
                status = await self.get_certificate_status(certificate_id)
                if status:
                    statuses.append(status)
            
            return statuses
            
        except Exception as e:
            logger.error(f"Error getting all certificates status: {e}")
            return []
    
    async def cleanup_completed_certificates(self) -> int:
        """Clean up completed certificates from active tracking"""
        try:
            completed_count = 0
            
            for certificate_id in list(self.active_certificates.keys()):
                certificate = self.active_certificates[certificate_id]
                
                if certificate.certificate_status == CertificateStatus.READY:
                    # Remove from active tracking
                    del self.active_certificates[certificate_id]
                    del self.certificate_locks[certificate_id]
                    completed_count += 1
            
            logger.info(f"Cleaned up {completed_count} completed certificates")
            return completed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up completed certificates: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the certificate manager"""
        try:
            health_status = {
                "status": "healthy",
                "active_certificates": len(self.active_certificates),
                "total_locks": len(self.certificate_locks),
                "services": {
                    "registry_service": "healthy",
                    "versions_service": "healthy",
                    "metrics_service": "healthy"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check service health
            try:
                await self.registry_service.health_check()
            except Exception:
                health_status["services"]["registry_service"] = "unhealthy"
                health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 