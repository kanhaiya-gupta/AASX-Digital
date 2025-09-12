"""
Certificate Versions Service
Business logic for certificate version management operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func

from ..models.certificates_versions import (
    CertificateVersions,
    VersionType,
    ApprovalStatus,
    ChangeImpact,
    ChangeCategory,
    DigitalVerification,
    BusinessIntelligence
)
from ..repositories.certificates_versions_repository import CertificatesVersionsRepository
from ..models.certificates_registry import CertificateRegistry

logger = logging.getLogger(__name__)


class CertificatesVersionsService:
    """
    Business logic service for certificate version management
    Coordinates version operations using models and repositories
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repository = CertificatesVersionsRepository(db_session)
    
    async def create_version(
        self,
        certificate_id: str,
        version_number: str,
        version_type: VersionType,
        change_description: str,
        change_impact: ChangeImpact,
        change_category: ChangeCategory,
        user_id: str,
        **kwargs
    ) -> CertificateVersions:
        """
        Create a new certificate version
        """
        try:
            # Generate version ID
            version_id = str(uuid4())
            
            # Create version data
            version_data = {
                "version_id": version_id,
                "certificate_id": certificate_id,
                "version_number": version_number,
                "version_type": version_type,
                "change_description": change_description,
                "change_impact": change_impact,
                "change_category": change_category,
                "created_by": user_id,
                "created_at": datetime.utcnow(),
                "approval_status": ApprovalStatus.PENDING,
                **kwargs
            }
            
            # Create version instance
            version = CertificateVersions(**version_data)
            
            # Save to database
            created_version = await self.repository.create(version)
            
            logger.info(f"Created version {version_number} for certificate {certificate_id}")
            return created_version
            
        except Exception as e:
            logger.error(f"Error creating version: {e}")
            raise
    
    async def get_version(self, version_id: str) -> Optional[CertificateVersions]:
        """
        Retrieve a specific version by ID
        """
        try:
            return await self.repository.get_by_id(version_id)
        except Exception as e:
            logger.error(f"Error retrieving version {version_id}: {e}")
            raise
    
    async def get_certificate_versions(
        self,
        certificate_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[CertificateVersions]:
        """
        Get all versions for a specific certificate
        """
        try:
            return await self.repository.get_by_certificate_id(
                certificate_id, limit, offset
            )
        except Exception as e:
            logger.error(f"Error retrieving versions for certificate {certificate_id}: {e}")
            raise
    
    async def update_version(
        self,
        version_id: str,
        update_data: Dict[str, Any],
        user_id: str
    ) -> Optional[CertificateVersions]:
        """
        Update an existing version
        """
        try:
            # Add audit fields
            update_data.update({
                "updated_by": user_id,
                "updated_at": datetime.utcnow()
            })
            
            updated_version = await self.repository.update(version_id, update_data)
            
            if updated_version:
                logger.info(f"Updated version {version_id}")
            
            return updated_version
            
        except Exception as e:
            logger.error(f"Error updating version {version_id}: {e}")
            raise
    
    async def delete_version(self, version_id: str, user_id: str) -> bool:
        """
        Delete a version (soft delete)
        """
        try:
            # Soft delete by marking as deleted
            delete_data = {
                "deleted_by": user_id,
                "deleted_at": datetime.utcnow(),
                "is_deleted": True
            }
            
            success = await self.repository.update(version_id, delete_data)
            
            if success:
                logger.info(f"Deleted version {version_id}")
            
            return bool(success)
            
        except Exception as e:
            logger.error(f"Error deleting version {version_id}: {e}")
            raise
    
    async def approve_version(
        self,
        version_id: str,
        approver_id: str,
        approval_notes: Optional[str] = None
    ) -> Optional[CertificateVersions]:
        """
        Approve a version
        """
        try:
            approval_data = {
                "approval_status": ApprovalStatus.APPROVED,
                "approved_by": approver_id,
                "approved_at": datetime.utcnow(),
                "approval_notes": approval_notes
            }
            
            approved_version = await self.repository.update(version_id, approval_data)
            
            if approved_version:
                logger.info(f"Version {version_id} approved by {approver_id}")
            
            return approved_version
            
        except Exception as e:
            logger.error(f"Error approving version {version_id}: {e}")
            raise
    
    async def reject_version(
        self,
        version_id: str,
        rejector_id: str,
        rejection_reason: str
    ) -> Optional[CertificateVersions]:
        """
        Reject a version
        """
        try:
            rejection_data = {
                "approval_status": ApprovalStatus.REJECTED,
                "rejected_by": rejector_id,
                "rejected_at": datetime.utcnow(),
                "rejection_reason": rejection_reason
            }
            
            rejected_version = await self.repository.update(version_id, rejection_data)
            
            if rejected_version:
                logger.info(f"Version {version_id} rejected by {rejector_id}")
            
            return rejected_version
            
        except Exception as e:
            logger.error(f"Error rejecting version {version_id}: {e}")
            raise
    
    async def get_latest_version(self, certificate_id: str) -> Optional[CertificateVersions]:
        """
        Get the latest approved version of a certificate
        """
        try:
            return await self.repository.get_latest_approved_version(certificate_id)
        except Exception as e:
            logger.error(f"Error getting latest version for certificate {certificate_id}: {e}")
            raise
    
    async def get_version_history(
        self,
        certificate_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CertificateVersions]:
        """
        Get version history within a date range
        """
        try:
            return await self.repository.get_version_history(
                certificate_id, start_date, end_date
            )
        except Exception as e:
            logger.error(f"Error getting version history for certificate {certificate_id}: {e}")
            raise
    
    async def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two versions and highlight differences
        """
        try:
            version_1 = await self.repository.get_by_id(version_id_1)
            version_2 = await self.repository.get_by_id(version_id_2)
            
            if not version_1 or not version_2:
                raise ValueError("One or both versions not found")
            
            # Compare key fields
            comparison = {
                "version_1": {
                    "version_number": version_1.version_number,
                    "version_type": version_1.version_type,
                    "change_description": version_1.change_description,
                    "change_impact": version_1.change_impact,
                    "change_category": version_1.change_category,
                    "created_at": version_1.created_at
                },
                "version_2": {
                    "version_number": version_2.version_number,
                    "version_type": version_2.version_type,
                    "change_description": version_2.change_description,
                    "change_impact": version_2.change_impact,
                    "change_category": version_2.change_category,
                    "created_at": version_2.created_at
                },
                "differences": []
            }
            
            # Identify differences
            if version_1.version_type != version_2.version_type:
                comparison["differences"].append("version_type")
            if version_1.change_impact != version_2.change_impact:
                comparison["differences"].append("change_impact")
            if version_1.change_category != version_2.change_category:
                comparison["differences"].append("change_category")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            raise
    
    async def get_pending_approvals(
        self,
        org_id: Optional[str] = None,
        limit: int = 50
    ) -> List[CertificateVersions]:
        """
        Get all versions pending approval
        """
        try:
            return await self.repository.get_pending_approvals(org_id, limit)
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            raise
    
    async def get_approval_statistics(
        self,
        org_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get approval statistics and metrics
        """
        try:
            return await self.repository.get_approval_statistics(
                org_id, start_date, end_date
            )
        except Exception as e:
            logger.error(f"Error getting approval statistics: {e}")
            raise
    
    async def bulk_update_approval_status(
        self,
        version_ids: List[str],
        new_status: ApprovalStatus,
        user_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk update approval status for multiple versions
        """
        try:
            results = {
                "successful": [],
                "failed": [],
                "total_processed": len(version_ids)
            }
            
            for version_id in version_ids:
                try:
                    update_data = {
                        "approval_status": new_status,
                        "updated_by": user_id,
                        "updated_at": datetime.utcnow()
                    }
                    
                    if new_status == ApprovalStatus.APPROVED:
                        update_data["approved_by"] = user_id
                        update_data["approved_at"] = datetime.utcnow()
                        update_data["approval_notes"] = notes
                    elif new_status == ApprovalStatus.REJECTED:
                        update_data["rejected_by"] = user_id
                        update_data["rejected_at"] = datetime.utcnow()
                        update_data["rejection_reason"] = notes
                    
                    success = await self.repository.update(version_id, update_data)
                    
                    if success:
                        results["successful"].append(version_id)
                    else:
                        results["failed"].append(version_id)
                        
                except Exception as e:
                    logger.error(f"Error updating version {version_id}: {e}")
                    results["failed"].append(version_id)
            
            logger.info(f"Bulk update completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            raise
    
    async def get_version_analytics(
        self,
        org_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive version analytics
        """
        try:
            analytics = await self.repository.get_version_analytics(
                org_id, start_date, end_date
            )
            
            # Add computed metrics
            if analytics.get("total_versions", 0) > 0:
                analytics["approval_rate"] = (
                    analytics.get("approved_versions", 0) / analytics["total_versions"]
                ) * 100
                analytics["rejection_rate"] = (
                    analytics.get("rejected_versions", 0) / analytics["total_versions"]
                ) * 100
                analytics["pending_rate"] = (
                    analytics.get("pending_versions", 0) / analytics["total_versions"]
                ) * 100
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting version analytics: {e}")
            raise
    
    async def validate_version_integrity(self, version_id: str) -> bool:
        """
        Validate version data integrity
        """
        try:
            version = await self.repository.get_by_id(version_id)
            if not version:
                return False
            
            # Validate required fields
            required_fields = [
                version.version_id,
                version.certificate_id,
                version.version_number,
                version.version_type,
                version.change_description,
                version.change_impact,
                version.change_category
            ]
            
            if not all(required_fields):
                return False
            
            # Validate version number format (basic check)
            if not version.version_number or len(version.version_number.strip()) == 0:
                return False
            
            # Validate change description
            if not version.change_description or len(version.change_description.strip()) == 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating version integrity: {e}")
            return False
    
    async def get_version_health_status(self, version_id: str) -> Dict[str, Any]:
        """
        Get version health and status information
        """
        try:
            version = await self.repository.get_by_id(version_id)
            if not version:
                return {"status": "not_found", "health": "unknown"}
            
            health_indicators = {
                "data_completeness": 0,
                "approval_status": "unknown",
                "age_days": 0,
                "issues": []
            }
            
            # Check data completeness
            required_fields = [
                "version_number", "version_type", "change_description",
                "change_impact", "change_category", "created_by"
            ]
            
            complete_fields = sum(
                1 for field in required_fields 
                if getattr(version, field) is not None
            )
            health_indicators["data_completeness"] = (complete_fields / len(required_fields)) * 100
            
            # Check approval status
            health_indicators["approval_status"] = version.approval_status.value
            
            # Calculate age
            if version.created_at:
                age = datetime.utcnow() - version.created_at
                health_indicators["age_days"] = age.days
            
            # Identify issues
            if health_indicators["data_completeness"] < 100:
                health_indicators["issues"].append("incomplete_data")
            
            if version.approval_status == ApprovalStatus.PENDING:
                if health_indicators["age_days"] > 30:
                    health_indicators["issues"].append("stale_pending_approval")
            
            # Determine overall health
            if health_indicators["data_completeness"] == 100 and not health_indicators["issues"]:
                health_indicators["health"] = "healthy"
            elif health_indicators["data_completeness"] >= 80 and len(health_indicators["issues"]) <= 1:
                health_indicators["health"] = "warning"
            else:
                health_indicators["health"] = "critical"
            
            return health_indicators
            
        except Exception as e:
            logger.error(f"Error getting version health status: {e}")
            return {"status": "error", "health": "unknown", "error": str(e)}
    
    async def export_version_data(
        self,
        version_ids: List[str],
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export version data in specified format
        """
        try:
            versions = []
            for version_id in version_ids:
                version = await self.repository.get_by_id(version_id)
                if version:
                    versions.append(version.model_dump())
            
            export_data = {
                "export_info": {
                    "format": format,
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_versions": len(versions)
                },
                "versions": versions
            }
            
            logger.info(f"Exported {len(versions)} versions in {format} format")
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting version data: {e}")
            raise
    
    async def cleanup_old_versions(
        self,
        certificate_id: str,
        keep_versions: int = 10,
        older_than_days: int = 365
    ) -> Dict[str, Any]:
        """
        Clean up old versions, keeping only the most recent ones
        """
        try:
            # Get all versions for the certificate
            all_versions = await self.repository.get_by_certificate_id(
                certificate_id, limit=1000, offset=0
            )
            
            if len(all_versions) <= keep_versions:
                return {
                    "message": "No cleanup needed",
                    "total_versions": len(all_versions),
                    "versions_kept": len(all_versions),
                    "versions_removed": 0
                }
            
            # Sort by creation date (newest first)
            sorted_versions = sorted(
                all_versions,
                key=lambda v: v.created_at or datetime.min,
                reverse=True
            )
            
            # Keep the most recent versions
            versions_to_keep = sorted_versions[:keep_versions]
            versions_to_remove = sorted_versions[keep_versions:]
            
            # Filter out versions older than specified days
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            versions_to_remove = [
                v for v in versions_to_remove
                if v.created_at and v.created_at < cutoff_date
            ]
            
            # Soft delete old versions
            removed_count = 0
            for version in versions_to_remove:
                try:
                    success = await self.repository.update(
                        version.version_id,
                        {
                            "is_deleted": True,
                            "deleted_at": datetime.utcnow(),
                            "deleted_by": "system_cleanup"
                        }
                    )
                    if success:
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove version {version.version_id}: {e}")
            
            return {
                "message": "Cleanup completed",
                "total_versions": len(all_versions),
                "versions_kept": len(versions_to_keep),
                "versions_removed": removed_count,
                "cleanup_criteria": {
                    "keep_versions": keep_versions,
                    "older_than_days": older_than_days
                }
            }
            
        except Exception as e:
            logger.error(f"Error during version cleanup: {e}")
            raise
