"""
Certificate Registry Repository
Database access layer for certificates_registry table with all component operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4

from src.engine.database.connection_manager import ConnectionManager
from ..models.certificates_registry import (
    CertificateRegistry,
    ModuleStatus,
    CertificateStatus,
    QualityLevel,
    ComplianceStatus,
    SecurityLevel
)

logger = logging.getLogger(__name__)


class CertificatesRegistryRepository:
    """
    Repository for certificates_registry table
    Handles all CRUD operations and component-specific operations
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize with connection manager for raw SQL operations."""
        self.connection_manager = connection_manager
        self.table_name = "certificates_registry"
        logger.info("Certificate Registry Repository initialized with ConnectionManager")
    
    # ========================================================================
    # CORE CERTIFICATE OPERATIONS
    # ========================================================================
    
    async def create(self, certificate: CertificateRegistry) -> CertificateRegistry:
        """Create a new certificate using raw SQL"""
        try:
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(certificate)
            
            # Build INSERT query dynamically
            columns = list(db_data.keys())
            placeholders = [f":{col}" for col in columns]
            
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            # Execute raw SQL
            await self.execute_query(query, db_data)
            
            logger.info(f"Created certificate {certificate.certificate_id}")
            return certificate
        except Exception as e:
            logger.error(f"Error creating certificate: {e}")
            raise
    
    async def get_by_id(self, certificate_id: str) -> Optional[CertificateRegistry]:
        """Get certificate by ID using raw SQL"""
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE certificate_id = :certificate_id AND is_deleted = :is_deleted
            """
            
            result = await self.fetch_one(query, {"certificate_id": certificate_id, "is_deleted": False})
            
            if result:
                return self._dict_to_model(result)
            return None
        except Exception as e:
            logger.error(f"Error retrieving certificate {certificate_id}: {e}")
            raise
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CertificateRegistry]:
        """Get all certificates with optional filtering using raw SQL"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE is_deleted = :is_deleted"
            params = {"is_deleted": False}
            
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query += f" AND {key} = :{key}"
                        params[key] = value
            
            query += " LIMIT :limit OFFSET :offset"
            params["limit"] = limit
            params["offset"] = offset
            
            result = await self.execute_query(query, params)
            return [self._dict_to_model(row) for row in result]
        except Exception as e:
            logger.error(f"Error retrieving certificates: {e}")
            raise
    
    async def update(self, certificate_id: str, update_data: Dict[str, Any]) -> Optional[CertificateRegistry]:
        """Update certificate using raw SQL"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in update_data.keys()]
            query = f"""
                UPDATE {self.table_name} 
                SET {', '.join(set_clauses)}
                WHERE certificate_id = :certificate_id
                RETURNING *
            """
            
            # Add certificate_id to params
            params = {**update_data, "certificate_id": certificate_id}
            
            result = await self.fetch_one(query, params)
            
            if result:
                return self._dict_to_model(result)
            return None
        except Exception as e:
            logger.error(f"Error updating certificate: {e}")
            raise
    
    async def delete(self, certificate_id: str, user_id: str) -> bool:
        """Soft delete certificate using raw SQL"""
        try:
            query = f"""
                UPDATE {self.table_name}
                SET is_deleted = :is_deleted, deleted_at = :deleted_at, deleted_by = :deleted_by
                WHERE certificate_id = :certificate_id
            """
            params = {
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
                "deleted_by": user_id,
                "certificate_id": certificate_id
            }
            
            await self.execute_query(query, params)
            return True # Raw SQL execute_query doesn't return rowcount directly, assume success if no error
        except Exception as e:
            logger.error(f"Error deleting certificate {certificate_id}: {e}")
            raise
    
    # ========================================================================
    # MODULE STATUS MANAGEMENT
    # ========================================================================
    
    async def update_module_status(
        self,
        certificate_id: str,
        module_name: str,
        status: ModuleStatus,
        health_score: Optional[float] = None
    ) -> bool:
        """Update status of a specific module using raw SQL"""
        try:
            # Get current certificate
            certificate = await self.get_by_id(certificate_id)
            if not certificate:
                return False
            
            # Update module status
            if hasattr(certificate.module_status, module_name):
                setattr(certificate.module_status, module_name, status)
            
            # Update health score if provided
            if health_score is not None:
                certificate.module_status.health_score = health_score
            
            # Update last updated timestamp
            certificate.module_status.last_updated = datetime.utcnow()
            
            # Recalculate active modules count
            active_modules = sum(
                1 for module in [
                    certificate.module_status.aasx_module,
                    certificate.module_status.certificate_manager,
                    certificate.module_status.data_processor,
                    certificate.module_status.analytics_engine,
                    certificate.module_status.workflow_engine,
                    certificate.module_status.integration_layer,
                    certificate.module_status.security_module
                ] if module == ModuleStatus.ACTIVE
            )
            certificate.module_status.active_modules = active_modules
            
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(certificate)
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in db_data.keys() if key != "certificate_id"] # Exclude certificate_id for update
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE certificate_id = :certificate_id
            """
            
            # Add certificate_id to params
            params = {**db_data, "certificate_id": certificate_id}
            
            await self.execute_query(query, params)
            logger.info(f"Updated module {module_name} status to {status} for certificate {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating module status: {e}")
            raise
    
    async def get_certificates_by_module_status(
        self,
        module_name: str,
        status: ModuleStatus,
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by specific module status using raw SQL"""
        try:
            # This would require a more complex query to filter by nested JSON data
            # For now, we'll get all certificates and filter in Python
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                if hasattr(cert.module_status, module_name):
                    module_status = getattr(cert.module_status, module_name)
                    if module_status == status:
                        filtered_certificates.append(cert)
                        if len(filtered_certificates) >= limit:
                            break
            
            return filtered_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates by module status: {e}")
            raise
    
    async def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary across all certificates using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            total_certificates = len(all_certificates)
            healthy_certificates = 0
            warning_certificates = 0
            critical_certificates = 0
            
            total_health_score = 0
            module_status_counts = {status: 0 for status in ModuleStatus}
            
            for cert in all_certificates:
                health_score = cert.module_status.health_score
                total_health_score += health_score
                
                if health_score >= 80:
                    healthy_certificates += 1
                elif health_score >= 60:
                    warning_certificates += 1
                else:
                    critical_certificates += 1
                
                # Count module statuses
                for module in [
                    cert.module_status.aasx_module,
                    cert.module_status.certificate_manager,
                    cert.module_status.data_processor,
                    cert.module_status.analytics_engine,
                    cert.module_status.workflow_engine,
                    cert.module_status.integration_layer,
                    cert.module_status.security_module
                ]:
                    module_status_counts[module] += 1
            
            return {
                "total_certificates": total_certificates,
                "healthy_certificates": healthy_certificates,
                "warning_certificates": warning_certificates,
                "critical_certificates": critical_certificates,
                "average_health_score": total_health_score / total_certificates if total_certificates > 0 else 0,
                "module_status_distribution": module_status_counts,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health summary: {e}")
            raise
    
    # ========================================================================
    # QUALITY SCORE OPERATIONS
    # ========================================================================
    
    async def update_quality_assessment(
        self,
        certificate_id: str,
        quality_data: Dict[str, Any]
    ) -> bool:
        """Update quality assessment data using raw SQL"""
        try:
            certificate = await self.get_by_id(certificate_id)
            if not certificate:
                return False
            
            # Update quality assessment fields
            for key, value in quality_data.items():
                if hasattr(certificate.quality_assessment, key):
                    setattr(certificate.quality_assessment, key, value)
            
            # Recalculate overall quality score
            scores = [
                certificate.quality_assessment.data_completeness,
                certificate.quality_assessment.data_accuracy,
                certificate.quality_assessment.data_consistency,
                certificate.quality_assessment.data_timeliness,
                certificate.quality_assessment.data_relevance
            ]
            certificate.quality_assessment.overall_quality_score = sum(scores) / len(scores)
            
            # Update quality level based on score
            if certificate.quality_assessment.overall_quality_score >= 90:
                certificate.quality_assessment.quality_level = QualityLevel.EXCELLENT
            elif certificate.quality_assessment.overall_quality_score >= 80:
                certificate.quality_assessment.quality_level = QualityLevel.GOOD
            elif certificate.quality_assessment.overall_quality_score >= 70:
                certificate.quality_assessment.quality_level = QualityLevel.FAIR
            elif certificate.quality_assessment.overall_quality_score >= 60:
                certificate.quality_assessment.quality_level = QualityLevel.POOR
            else:
                certificate.quality_assessment.quality_level = QualityLevel.CRITICAL
            
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(certificate)
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in db_data.keys() if key != "certificate_id"] # Exclude certificate_id for update
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE certificate_id = :certificate_id
            """
            
            # Add certificate_id to params
            params = {**db_data, "certificate_id": certificate_id}
            
            await self.execute_query(query, params)
            logger.info(f"Updated quality assessment for certificate {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating quality assessment: {e}")
            raise
    
    async def get_certificates_by_quality_level(
        self,
        quality_level: QualityLevel,
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by quality level using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                if cert.quality_assessment.quality_level == quality_level:
                    filtered_certificates.append(cert)
                    if len(filtered_certificates) >= limit:
                        break
            
            return filtered_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates by quality level: {e}")
            raise
    
    async def get_quality_statistics(self) -> Dict[str, Any]:
        """Get quality statistics across all certificates using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            quality_distribution = {level: 0 for level in QualityLevel}
            total_quality_score = 0
            total_completeness = 0
            total_accuracy = 0
            total_consistency = 0
            
            for cert in all_certificates:
                quality_distribution[cert.quality_assessment.quality_level] += 1
                total_quality_score += cert.quality_assessment.overall_quality_score
                total_completeness += cert.quality_assessment.data_completeness
                total_accuracy += cert.quality_assessment.data_accuracy
                total_consistency += cert.quality_assessment.data_consistency
            
            total_certificates = len(all_certificates)
            
            return {
                "total_certificates": total_certificates,
                "quality_distribution": quality_distribution,
                "average_quality_score": total_quality_score / total_certificates if total_certificates > 0 else 0,
                "average_completeness": total_completeness / total_certificates if total_certificates > 0 else 0,
                "average_accuracy": total_accuracy / total_certificates if total_certificates > 0 else 0,
                "average_consistency": total_consistency / total_certificates if total_certificates > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting quality statistics: {e}")
            raise
    
    # ========================================================================
    # COMPLIANCE MANAGEMENT
    # ========================================================================
    
    async def update_compliance_tracking(
        self,
        certificate_id: str,
        compliance_data: Dict[str, Any]
    ) -> bool:
        """Update compliance tracking data using raw SQL"""
        try:
            certificate = await self.get_by_id(certificate_id)
            if not certificate:
                return False
            
            # Update compliance fields
            for key, value in compliance_data.items():
                if hasattr(certificate.compliance_tracking, key):
                    setattr(certificate.compliance_tracking, key, value)
            
            # Recalculate compliance score if not provided
            if "compliance_score" not in compliance_data:
                # Calculate based on checks passed vs total
                if certificate.compliance_tracking.compliance_checks_total > 0:
                    certificate.compliance_tracking.compliance_score = (
                        certificate.compliance_tracking.compliance_checks_passed /
                        certificate.compliance_tracking.compliance_checks_total
                    ) * 100
                
                # Update compliance status based on score
                if certificate.compliance_tracking.compliance_score >= 90:
                    certificate.compliance_tracking.compliance_status = ComplianceStatus.COMPLIANT
                elif certificate.compliance_tracking.compliance_score >= 70:
                    certificate.compliance_tracking.compliance_status = ComplianceStatus.PARTIALLY_COMPLIANT
                else:
                    certificate.compliance_tracking.compliance_status = ComplianceStatus.NON_COMPLIANT
            
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(certificate)
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in db_data.keys() if key != "certificate_id"] # Exclude certificate_id for update
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE certificate_id = :certificate_id
            """
            
            # Add certificate_id to params
            params = {**db_data, "certificate_id": certificate_id}
            
            await self.execute_query(query, params)
            logger.info(f"Updated compliance tracking for certificate {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating compliance tracking: {e}")
            raise
    
    async def get_certificates_by_compliance_status(
        self,
        compliance_status: ComplianceStatus,
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by compliance status using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                if cert.compliance_tracking.compliance_status == compliance_status:
                    filtered_certificates.append(cert)
                    if len(filtered_certificates) >= limit:
                        break
            
            return filtered_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates by compliance status: {e}")
            raise
    
    async def get_compliance_statistics(self) -> Dict[str, Any]:
        """Get compliance statistics across all certificates using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            compliance_distribution = {status: 0 for status in ComplianceStatus}
            total_compliance_score = 0
            total_checks_passed = 0
            total_checks_total = 0
            
            for cert in all_certificates:
                compliance_distribution[cert.compliance_tracking.compliance_status] += 1
                total_compliance_score += cert.compliance_tracking.compliance_score
                total_checks_passed += cert.compliance_tracking.compliance_checks_passed
                total_checks_total += cert.compliance_tracking.compliance_checks_total
            
            total_certificates = len(all_certificates)
            
            return {
                "total_certificates": total_certificates,
                "compliance_distribution": compliance_distribution,
                "average_compliance_score": total_compliance_score / total_certificates if total_certificates > 0 else 0,
                "total_checks_passed": total_checks_passed,
                "total_checks_total": total_checks_total,
                "overall_compliance_rate": (total_checks_passed / total_checks_total * 100) if total_checks_total > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance statistics: {e}")
            raise
    
    # ========================================================================
    # SECURITY OPERATIONS
    # ========================================================================
    
    async def update_security_metrics(
        self,
        certificate_id: str,
        security_data: Dict[str, Any]
    ) -> bool:
        """Update security metrics data using raw SQL"""
        try:
            certificate = await self.get_by_id(certificate_id)
            if not certificate:
                return False
            
            # Update security fields
            for key, value in security_data.items():
                if hasattr(certificate.security_metrics, key):
                    setattr(certificate.security_metrics, key, value)
            
            # Recalculate security score if not provided
            if "security_score" not in security_data:
                # Calculate based on various security factors
                scores = []
                
                # Controls effectiveness
                if certificate.security_metrics.security_controls_total > 0:
                    control_score = (certificate.security_metrics.security_controls_effective /
                                   certificate.security_metrics.security_controls_total) * 100
                    scores.append(control_score)
                
                # Incident response time (lower is better)
                if certificate.security_metrics.incident_response_time_minutes > 0:
                    response_score = max(0, 100 - (certificate.security_metrics.incident_response_time_minutes / 60))
                    scores.append(response_score)
                
                # Error rate (lower is better)
                error_score = max(0, 100 - certificate.security_metrics.authentication_failures)
                scores.append(error_score)
                
                if scores:
                    certificate.security_metrics.security_score = sum(scores) / len(scores)
                
                # Update security level based on score
                if certificate.security_metrics.security_score >= 90:
                    certificate.security_metrics.security_level = SecurityLevel.LOW
                elif certificate.security_metrics.security_score >= 70:
                    certificate.security_metrics.security_level = SecurityLevel.MEDIUM
                elif certificate.security_metrics.security_score >= 50:
                    certificate.security_metrics.security_level = SecurityLevel.HIGH
                else:
                    certificate.security_metrics.security_level = SecurityLevel.CRITICAL
            
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(certificate)
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in db_data.keys() if key != "certificate_id"] # Exclude certificate_id for update
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE certificate_id = :certificate_id
            """
            
            # Add certificate_id to params
            params = {**db_data, "certificate_id": certificate_id}
            
            await self.execute_query(query, params)
            logger.info(f"Updated security metrics for certificate {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating security metrics: {e}")
            raise
    
    async def get_certificates_by_security_level(
        self,
        security_level: SecurityLevel,
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by security level using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                if cert.security_metrics.security_level == security_level:
                    filtered_certificates.append(cert)
                    if len(filtered_certificates) >= limit:
                        break
            
            return filtered_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates by security level: {e}")
            raise
    
    async def get_security_statistics(self) -> Dict[str, Any]:
        """Get security statistics across all certificates using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            security_distribution = {level: 0 for level in SecurityLevel}
            total_security_score = 0
            total_active_threats = 0
            total_security_events = 0
            
            for cert in all_certificates:
                security_distribution[cert.security_metrics.security_level] += 1
                total_security_score += cert.security_metrics.security_score
                total_active_threats += cert.security_metrics.active_threats
                total_security_events += cert.security_metrics.security_events_total
            
            total_certificates = len(all_certificates)
            
            return {
                "total_certificates": total_certificates,
                "security_distribution": security_distribution,
                "average_security_score": total_security_score / total_certificates if total_certificates > 0 else 0,
                "total_active_threats": total_active_threats,
                "total_security_events": total_security_events,
                "average_threats_per_certificate": total_active_threats / total_certificates if total_certificates > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting security statistics: {e}")
            raise
    
    # ========================================================================
    # BUSINESS CONTEXT OPERATIONS
    # ========================================================================
    
    async def update_business_context(
        self,
        certificate_id: str,
        business_data: Dict[str, Any]
    ) -> bool:
        """Update business context data using raw SQL"""
        try:
            certificate = await self.get_by_id(certificate_id)
            if not certificate:
                return False
            
            # Update business context fields
            for key, value in business_data.items():
                if hasattr(certificate.business_context, key):
                    setattr(certificate.business_context, key, value)
            
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(certificate)
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in db_data.keys() if key != "certificate_id"] # Exclude certificate_id for update
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE certificate_id = :certificate_id
            """
            
            # Add certificate_id to params
            params = {**db_data, "certificate_id": certificate_id}
            
            await self.execute_query(query, params)
            logger.info(f"Updated business context for certificate {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating business context: {e}")
            raise
    
    async def get_certificates_by_business_tag(
        self,
        business_tag: str,
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by business tag using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                if business_tag in cert.business_context.business_tags:
                    filtered_certificates.append(cert)
                    if len(filtered_certificates) >= limit:
                        break
            
            return filtered_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates by business tag: {e}")
            raise
    
    async def get_certificates_by_owner(
        self,
        business_owner: str,
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by business owner using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                if cert.business_context.business_owner == business_owner:
                    filtered_certificates.append(cert)
                    if len(filtered_certificates) >= limit:
                        break
            
            return filtered_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates by owner: {e}")
            raise
    
    # ========================================================================
    # MODULE SUMMARY OPERATIONS
    # ========================================================================
    
    async def update_module_summaries(
        self,
        certificate_id: str,
        module_name: str,
        summary_data: Dict[str, Any]
    ) -> bool:
        """Update module summary data using raw SQL"""
        try:
            certificate = await self.get_by_id(certificate_id)
            if not certificate:
                return False
            
            # Update specific module summary
            if hasattr(certificate.module_summaries, f"{module_name}_summary"):
                module_summary_attr = f"{module_name}_summary"
                current_summary = getattr(certificate.module_summaries, module_summary_attr)
                current_summary.update(summary_data)
            
            # Update summary metadata
            certificate.module_summaries.summary_generated_at = datetime.utcnow()
            certificate.module_summaries.modules_with_data += 1
            
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(certificate)
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in db_data.keys() if key != "certificate_id"] # Exclude certificate_id for update
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE certificate_id = :certificate_id
            """
            
            # Add certificate_id to params
            params = {**db_data, "certificate_id": certificate_id}
            
            await self.execute_query(query, params)
            logger.info(f"Updated module summary for {module_name} in certificate {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating module summary: {e}")
            raise
    
    async def get_certificates_by_module_data_coverage(
        self,
        min_coverage_percentage: float,
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by module data coverage using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                coverage = cert.module_summaries.data_coverage_percentage
                if coverage >= min_coverage_percentage:
                    filtered_certificates.append(cert)
                    if len(filtered_certificates) >= limit:
                        break
            
            return filtered_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates by module data coverage: {e}")
            raise
    
    # ========================================================================
    # DIGITAL TRUST OPERATIONS
    # ========================================================================
    
    async def update_digital_trust(
        self,
        certificate_id: str,
        trust_data: Dict[str, Any]
    ) -> bool:
        """Update digital trust data using raw SQL"""
        try:
            certificate = await self.get_by_id(certificate_id)
            if not certificate:
                return False
            
            # Update digital trust fields
            for key, value in trust_data.items():
                if hasattr(certificate.digital_trust, key):
                    setattr(certificate.digital_trust, key, value)
            
            # Recalculate trust score if not provided
            if "trust_score" not in trust_data:
                # Calculate based on various trust factors
                scores = []
                
                # Digital signature score
                if certificate.digital_trust.is_digitally_signed:
                    scores.append(100)
                else:
                    scores.append(0)
                
                # Hash verification score
                if certificate.digital_trust.is_hash_verified:
                    scores.append(100)
                else:
                    scores.append(0)
                
                # Blockchain integration score
                if certificate.digital_trust.blockchain_hash:
                    scores.append(100)
                else:
                    scores.append(50)
                
                if scores:
                    certificate.digital_trust.trust_score = sum(scores) / len(scores)
                
                # Update trust level based on score
                if certificate.digital_trust.trust_score >= 90:
                    certificate.digital_trust.trust_level = "high"
                elif certificate.digital_trust.trust_score >= 70:
                    certificate.digital_trust.trust_level = "medium"
                elif certificate.digital_trust.trust_score >= 50:
                    certificate.digital_trust.trust_level = "low"
                else:
                    certificate.digital_trust.trust_level = "untrusted"
            
            # Convert Pydantic model to database dict
            db_data = self._model_to_dict(certificate)
            
            # Build UPDATE query dynamically
            set_clauses = [f"{key} = :{key}" for key in db_data.keys() if key != "certificate_id"] # Exclude certificate_id for update
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE certificate_id = :certificate_id
            """
            
            # Add certificate_id to params
            params = {**db_data, "certificate_id": certificate_id}
            
            await self.execute_query(query, params)
            logger.info(f"Updated digital trust for certificate {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating digital trust: {e}")
            raise
    
    async def get_certificates_by_trust_level(
        self,
        trust_level: str,
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by trust level using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                if cert.digital_trust.trust_level == trust_level:
                    filtered_certificates.append(cert)
                    if len(filtered_certificates) >= limit:
                        break
            
            return filtered_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates by trust level: {e}")
            raise
    
    async def get_digital_trust_statistics(self) -> Dict[str, Any]:
        """Get digital trust statistics across all certificates using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            trust_distribution = {"high": 0, "medium": 0, "low": 0, "untrusted": 0}
            total_trust_score = 0
            digitally_signed_count = 0
            hash_verified_count = 0
            blockchain_integrated_count = 0
            
            for cert in all_certificates:
                trust_distribution[cert.digital_trust.trust_level] += 1
                total_trust_score += cert.digital_trust.trust_score
                
                if cert.digital_trust.is_digitally_signed:
                    digitally_signed_count += 1
                if cert.digital_trust.is_hash_verified:
                    hash_verified_count += 1
                if cert.digital_trust.blockchain_hash:
                    blockchain_integrated_count += 1
            
            total_certificates = len(all_certificates)
            
            return {
                "total_certificates": total_certificates,
                "trust_distribution": trust_distribution,
                "average_trust_score": total_trust_score / total_certificates if total_certificates > 0 else 0,
                "digitally_signed_percentage": (digitally_signed_count / total_certificates * 100) if total_certificates > 0 else 0,
                "hash_verified_percentage": (hash_verified_count / total_certificates * 100) if total_certificates > 0 else 0,
                "blockchain_integrated_percentage": (blockchain_integrated_count / total_certificates * 100) if total_certificates > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting digital trust statistics: {e}")
            raise
    
    # ========================================================================
    # SEARCH AND FILTERING OPERATIONS
    # ========================================================================
    
    async def search_certificates(
        self,
        search_term: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CertificateRegistry]:
        """Search certificates with advanced filtering using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                # Basic search in certificate name and description
                if (search_term.lower() in cert.certificate_name.lower() or
                    (cert.description and search_term.lower() in cert.description.lower())):
                    
                    # Apply additional filters
                    if filters:
                        matches_filters = True
                        for key, value in filters.items():
                            if hasattr(cert, key):
                                if getattr(cert, key) != value:
                                    matches_filters = False
                                    break
                        
                        if not matches_filters:
                            continue
                    
                    filtered_certificates.append(cert)
                    if len(filtered_certificates) >= limit:
                        break
            
            return filtered_certificates[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error searching certificates: {e}")
            raise
    
    async def get_certificates_by_status(
        self,
        status: CertificateStatus,
        limit: int = 100
    ) -> List[CertificateRegistry]:
        """Get certificates by status using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            filtered_certificates = []
            for cert in all_certificates:
                if cert.certificate_status == status:
                    filtered_certificates.append(cert)
                    if len(filtered_certificates) >= limit:
                        break
            
            return filtered_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates by status: {e}")
            raise
    
    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================
    
    async def bulk_update_certificates(
        self,
        certificate_ids: List[str],
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Bulk update multiple certificates using raw SQL"""
        try:
            results = {
                "successful": [],
                "failed": [],
                "total_processed": len(certificate_ids)
            }
            
            for certificate_id in certificate_ids:
                try:
                    success = await self.update(certificate_id, update_data)
                    if success:
                        results["successful"].append(certificate_id)
                    else:
                        results["failed"].append(certificate_id)
                except Exception as e:
                    logger.error(f"Error updating certificate {certificate_id}: {e}")
                    results["failed"].append(certificate_id)
            
            logger.info(f"Bulk update completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            raise
    
    async def bulk_delete_certificates(
        self,
        certificate_ids: List[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Bulk delete multiple certificates using raw SQL"""
        try:
            results = {
                "successful": [],
                "failed": [],
                "total_processed": len(certificate_ids)
            }
            
            for certificate_id in certificate_ids:
                try:
                    success = await self.delete(certificate_id, user_id)
                    if success:
                        results["successful"].append(certificate_id)
                    else:
                        results["failed"].append(certificate_id)
                except Exception as e:
                    logger.error(f"Error deleting certificate {certificate_id}: {e}")
                    results["failed"].append(certificate_id)
            
            logger.info(f"Bulk delete completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk delete: {e}")
            raise
    
    # ========================================================================
    # STATISTICS AND ANALYTICS OPERATIONS
    # ========================================================================
    
    async def get_certificate_statistics(self) -> Dict[str, Any]:
        """Get comprehensive certificate statistics using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            total_certificates = len(all_certificates)
            status_distribution = {status: 0 for status in CertificateStatus}
            total_health_score = 0
            total_quality_score = 0
            total_compliance_score = 0
            total_security_score = 0
            total_trust_score = 0
            
            for cert in all_certificates:
                status_distribution[cert.certificate_status] += 1
                total_health_score += cert.overall_health_score
                total_quality_score += cert.quality_assessment.overall_quality_score
                total_compliance_score += cert.compliance_tracking.compliance_score
                total_security_score += cert.security_metrics.security_score
                total_trust_score += cert.digital_trust.trust_score
            
            return {
                "total_certificates": total_certificates,
                "status_distribution": status_distribution,
                "average_health_score": total_health_score / total_certificates if total_certificates > 0 else 0,
                "average_quality_score": total_quality_score / total_certificates if total_certificates > 0 else 0,
                "average_compliance_score": total_compliance_score / total_certificates if total_certificates > 0 else 0,
                "average_security_score": total_security_score / total_certificates if total_certificates > 0 else 0,
                "average_trust_score": total_trust_score / total_certificates if total_certificates > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting certificate statistics: {e}")
            raise
    
    async def get_certificates_requiring_attention(self, limit: int = 100) -> List[CertificateRegistry]:
        """Get certificates that require attention using raw SQL"""
        try:
            all_certificates = await self.get_all(limit=1000)
            
            attention_certificates = []
            for cert in all_certificates:
                if cert.requires_attention:
                    attention_certificates.append(cert)
                    if len(attention_certificates) >= limit:
                        break
            
            return attention_certificates
            
        except Exception as e:
            logger.error(f"Error getting certificates requiring attention: {e}")
            raise
    
    # ========================================================================
    # HEALTH CHECK OPERATIONS
    # ========================================================================
    
    async def get_certificate_health_status(self, certificate_id: str) -> Dict[str, Any]:
        """Get comprehensive health status for a certificate using raw SQL"""
        try:
            certificate = await self.get_by_id(certificate_id)
            if not certificate:
                return {"status": "not_found", "health": "unknown"}
            
            # Calculate health indicators
            health_indicators = {
                "overall_health_score": certificate.overall_health_score,
                "module_status_health": certificate.module_status.health_score,
                "quality_health": certificate.quality_assessment.overall_quality_score,
                "compliance_health": certificate.compliance_tracking.compliance_score,
                "security_health": certificate.security_metrics.security_score,
                "digital_trust_health": certificate.digital_trust.trust_score,
                "requires_attention": certificate.requires_attention,
                "age_days": certificate.age_days,
                "is_expired": certificate.is_expired,
                "days_until_expiry": certificate.days_until_expiry
            }
            
            # Determine overall health
            if health_indicators["overall_health_score"] >= 80:
                health_indicators["health"] = "healthy"
            elif health_indicators["overall_health_score"] >= 60:
                health_indicators["health"] = "warning"
            else:
                health_indicators["health"] = "critical"
            
            return health_indicators
            
        except Exception as e:
            logger.error(f"Error getting certificate health status: {e}")
            return {"status": "error", "health": "unknown", "error": str(e)}
    
    # ========================================================================
    # EXPORT OPERATIONS
    # ========================================================================
    
    async def export_certificate_data(
        self,
        certificate_ids: List[str],
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export certificate data in specified format using raw SQL"""
        try:
            certificates = []
            for certificate_id in certificate_ids:
                certificate = await self.get_by_id(certificate_id)
                if certificate:
                    certificates.append(certificate.model_dump())
            
            export_data = {
                "export_info": {
                    "format": format,
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_certificates": len(certificates)
                },
                "certificates": certificates
            }
            
            logger.info(f"Exported {len(certificates)} certificates in {format} format")
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting certificate data: {e}")
            raise
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _model_to_dict(self, certificate: CertificateRegistry) -> Dict[str, Any]:
        """Convert Pydantic model to database dictionary."""
        return certificate.model_dump()
    
    def _dict_to_model(self, data: Dict[str, Any]) -> CertificateRegistry:
        """Convert database dictionary to Pydantic model."""
        return CertificateRegistry(**data)
    
    # ========================================================================
    # CONNECTION MANAGER METHODS
    # ========================================================================
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a query using the connection manager."""
        try:
            if query.strip().upper().startswith('SELECT'):
                return await self.connection_manager.execute_query(query, params or {})
            else:
                await self.connection_manager.execute_update(query, params or {})
                return []
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise
    
    async def fetch_one(self, query: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row using the connection manager."""
        try:
            result = await self.connection_manager.execute_query(query, params or {})
            return result[0] if result and len(result) > 0 else None
        except Exception as e:
            logger.error(f"Failed to fetch one: {e}")
            return None
