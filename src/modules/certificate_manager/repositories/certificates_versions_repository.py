"""
Certificate Versions Repository
Database access layer for certificates_versions table with all component operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, text, select, update, delete
from sqlalchemy.orm import selectinload

from ..models.certificates_versions import (
    CertificateVersion,
    VersionType,
    ApprovalStatus,
    ChangeImpact,
    ChangeCategory,
    ReviewStatus,
    PublicationStatus
)

logger = logging.getLogger(__name__)


class CertificatesVersionsRepository:
    """
    Repository for certificates_versions table
    Handles all CRUD operations and component-specific operations
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    # ========================================================================
    # VERSION MANAGEMENT
    # ========================================================================
    
    async def create(self, version: CertificateVersion) -> CertificateVersion:
        """Create a new version"""
        try:
            self.db_session.add(version)
            await self.db_session.commit()
            await self.db_session.refresh(version)
            logger.info(f"Created version {version.version_id}")
            return version
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error creating version: {e}")
            raise
    
    async def get_by_id(self, version_id: str) -> Optional[CertificateVersion]:
        """Get version by ID"""
        try:
            result = await self.db_session.execute(
                select(CertificateVersion)
                .where(CertificateVersion.version_id == version_id)
                .where(CertificateVersion.is_deleted == False)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error retrieving version {version_id}: {e}")
            raise
    
    async def get_by_certificate_id(
        self,
        certificate_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[CertificateVersion]:
        """Get all versions for a specific certificate"""
        try:
            result = await self.db_session.execute(
                select(CertificateVersion)
                .where(CertificateVersion.certificate_id == certificate_id)
                .where(CertificateVersion.is_deleted == False)
                .order_by(CertificateVersion.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error retrieving versions for certificate {certificate_id}: {e}")
            raise
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CertificateVersion]:
        """Get all versions with optional filtering"""
        try:
            query = select(CertificateVersion).where(CertificateVersion.is_deleted == False)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(CertificateVersion, key) and value is not None:
                        query = query.where(getattr(CertificateVersion, key) == value)
            
            query = query.order_by(CertificateVersion.created_at.desc()).limit(limit).offset(offset)
            result = await self.db_session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error retrieving versions: {e}")
            raise
    
    async def update(self, version_id: str, update_data: Dict[str, Any]) -> Optional[CertificateVersion]:
        """Update version"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.db_session.execute(
                update(CertificateVersion)
                .where(CertificateVersion.version_id == version_id)
                .values(**update_data)
                .returning(CertificateVersion)
            )
            
            await self.db_session.commit()
            updated_version = result.scalar_one_or_none()
            
            if updated_version:
                logger.info(f"Updated version {version_id}")
            
            return updated_version
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating version {version_id}: {e}")
            raise
    
    async def delete(self, version_id: str) -> bool:
        """Soft delete version"""
        try:
            result = await self.db_session.execute(
                update(CertificateVersion)
                .where(CertificateVersion.version_id == version_id)
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow()
                )
            )
            
            await self.db_session.commit()
            success = result.rowcount > 0
            
            if success:
                logger.info(f"Deleted version {version_id}")
            
            return success
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error deleting version {version_id}: {e}")
            raise
    
    # ========================================================================
    # SNAPSHOT OPERATIONS
    # ========================================================================
    
    async def update_data_snapshots(
        self,
        version_id: str,
        module_name: str,
        snapshot_data: Dict[str, Any]
    ) -> bool:
        """Update data snapshot for a specific module"""
        try:
            version = await self.get_by_id(version_id)
            if not version:
                return False
            
            # Update specific module snapshot
            if hasattr(version.data_snapshots, f"{module_name}_snapshot"):
                module_snapshot_attr = f"{module_name}_snapshot"
                current_snapshot = getattr(version.data_snapshots, module_snapshot_attr)
                current_snapshot.update(snapshot_data)
            
            # Update snapshot metadata
            version.data_snapshots.snapshot_timestamp = datetime.utcnow()
            version.data_snapshots.data_records_count += 1
            
            # Update total data size (estimate)
            if "size_bytes" in snapshot_data:
                version.data_snapshots.total_data_size_bytes += snapshot_data["size_bytes"]
            
            await self.db_session.commit()
            logger.info(f"Updated data snapshot for {module_name} in version {version_id}")
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating data snapshot: {e}")
            raise
    
    async def get_snapshot_by_module(
        self,
        version_id: str,
        module_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get snapshot data for a specific module"""
        try:
            version = await self.get_by_id(version_id)
            if not version:
                return None
            
            if hasattr(version.data_snapshots, f"{module_name}_snapshot"):
                module_snapshot_attr = f"{module_name}_snapshot"
                return getattr(version.data_snapshots, module_snapshot_attr)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting snapshot for module {module_name}: {e}")
            raise
    
    async def get_snapshots_by_date_range(
        self,
        certificate_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[CertificateVersion]:
        """Get versions with snapshots within a date range"""
        try:
            result = await self.db_session.execute(
                select(CertificateVersion)
                .where(CertificateVersion.certificate_id == certificate_id)
                .where(CertificateVersion.created_at >= start_date)
                .where(CertificateVersion.created_at <= end_date)
                .where(CertificateVersion.is_deleted == False)
                .order_by(CertificateVersion.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting snapshots by date range: {e}")
            raise
    
    async def get_snapshot_statistics(self, certificate_id: str) -> Dict[str, Any]:
        """Get snapshot statistics for a certificate"""
        try:
            versions = await self.get_by_certificate_id(certificate_id, limit=1000)
            
            total_snapshots = len(versions)
            total_data_size = 0
            total_compressed_size = 0
            module_coverage = {}
            
            for version in versions:
                total_data_size += version.data_snapshots.total_data_size_bytes
                total_compressed_size += version.data_snapshots.compressed_size_bytes
                
                # Count module coverage
                for module_name, snapshot in version.data_snapshots.all_module_snapshots.items():
                    if module_name not in module_coverage:
                        module_coverage[module_name] = 0
                    if snapshot:
                        module_coverage[module_name] += 1
            
            return {
                "total_snapshots": total_snapshots,
                "total_data_size_bytes": total_data_size,
                "total_compressed_size_bytes": total_compressed_size,
                "average_compression_ratio": (
                    (1 - (total_compressed_size / total_data_size)) * 100
                ) if total_data_size > 0 else 0,
                "module_coverage": module_coverage,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting snapshot statistics: {e}")
            raise
    
    # ========================================================================
    # CHANGE TRACKING OPERATIONS
    # ========================================================================
    
    async def update_change_tracking(
        self,
        version_id: str,
        change_data: Dict[str, Any]
    ) -> bool:
        """Update change tracking data"""
        try:
            version = await self.get_by_id(version_id)
            if not version:
                return False
            
            # Update change tracking fields
            for key, value in change_data.items():
                if hasattr(version.change_tracking, key):
                    setattr(version.change_tracking, key, value)
            
            # Recalculate total lines changed
            version.change_tracking.total_lines_changed = (
                version.change_tracking.lines_added +
                version.change_tracking.lines_removed +
                version.change_tracking.lines_modified
            )
            
            # Update change complexity
            total_changes = version.change_tracking.total_lines_changed
            if total_changes > 1000:
                version.change_tracking.change_complexity = "very_high"
            elif total_changes > 500:
                version.change_tracking.change_complexity = "high"
            elif total_changes > 100:
                version.change_tracking.change_complexity = "medium"
            elif total_changes > 50:
                version.change_tracking.change_complexity = "low"
            else:
                version.change_tracking.change_complexity = "very_low"
            
            await self.db_session.commit()
            logger.info(f"Updated change tracking for version {version_id}")
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating change tracking: {e}")
            raise
    
    async def get_versions_by_change_impact(
        self,
        change_impact: ChangeImpact,
        limit: int = 100
    ) -> List[CertificateVersion]:
        """Get versions by change impact level"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            filtered_versions = []
            for version in all_versions:
                if version.change_tracking.change_impact == change_impact:
                    filtered_versions.append(version)
                    if len(filtered_versions) >= limit:
                        break
            
            return filtered_versions
            
        except Exception as e:
            logger.error(f"Error getting versions by change impact: {e}")
            raise
    
    async def get_versions_by_change_category(
        self,
        change_category: ChangeCategory,
        limit: int = 100
    ) -> List[CertificateVersion]:
        """Get versions by change category"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            filtered_versions = []
            for version in all_versions:
                if version.change_tracking.change_category == change_category:
                    filtered_versions.append(version)
                    if len(filtered_versions) >= limit:
                        break
            
            return filtered_versions
            
        except Exception as e:
            logger.error(f"Error getting versions by change category: {e}")
            raise
    
    async def get_breaking_changes(self, limit: int = 100) -> List[CertificateVersion]:
        """Get versions with breaking changes"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            breaking_versions = []
            for version in all_versions:
                if version.change_tracking.is_breaking_change:
                    breaking_versions.append(version)
                    if len(breaking_versions) >= limit:
                        break
            
            return breaking_versions
            
        except Exception as e:
            logger.error(f"Error getting breaking changes: {e}")
            raise
    
    # ========================================================================
    # APPROVAL WORKFLOW OPERATIONS
    # ========================================================================
    
    async def update_approval_workflow(
        self,
        version_id: str,
        workflow_data: Dict[str, Any]
    ) -> bool:
        """Update approval workflow data"""
        try:
            version = await self.get_by_id(version_id)
            if not version:
                return False
            
            # Update workflow fields
            for key, value in workflow_data.items():
                if hasattr(version.approval_workflow, key):
                    setattr(version.approval_workflow, key, value)
            
            # Recalculate workflow progress
            total_steps = 4  # submitted, review, approval, publication
            completed_steps = 0
            
            if version.approval_workflow.review_status == ReviewStatus.COMPLETED:
                completed_steps += 1
            
            if version.approval_workflow.workflow_status == ApprovalStatus.APPROVED:
                completed_steps += 1
            
            if hasattr(version, 'digital_verification') and version.digital_verification.verification_status == "completed":
                completed_steps += 1
            
            if version.approval_workflow.publication_status == PublicationStatus.PUBLISHED:
                completed_steps += 1
            
            version.approval_workflow.workflow_progress = (completed_steps / total_steps) * 100
            
            # Update workflow status if complete
            if version.approval_workflow.workflow_progress == 100:
                version.approval_workflow.workflow_status = ApprovalStatus.APPROVED
                version.approval_workflow.workflow_completed_at = datetime.utcnow()
            
            await self.db_session.commit()
            logger.info(f"Updated approval workflow for version {version_id}")
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating approval workflow: {e}")
            raise
    
    async def get_pending_approvals(
        self,
        org_id: Optional[str] = None,
        limit: int = 50
    ) -> List[CertificateVersion]:
        """Get versions pending approval"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            pending_versions = []
            for version in all_versions:
                if version.approval_workflow.workflow_status in [ApprovalStatus.PENDING, ApprovalStatus.IN_REVIEW]:
                    pending_versions.append(version)
                    if len(pending_versions) >= limit:
                        break
            
            return pending_versions
            
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            raise
    
    async def get_versions_by_review_status(
        self,
        review_status: ReviewStatus,
        limit: int = 100
    ) -> List[CertificateVersion]:
        """Get versions by review status"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            filtered_versions = []
            for version in all_versions:
                if version.approval_workflow.review_status == review_status:
                    filtered_versions.append(version)
                    if len(filtered_versions) >= limit:
                        break
            
            return filtered_versions
            
        except Exception as e:
            logger.error(f"Error getting versions by review status: {e}")
            raise
    
    async def get_approval_statistics(
        self,
        org_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get approval workflow statistics"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            # Filter by date range if provided
            if start_date and end_date:
                all_versions = [
                    v for v in all_versions
                    if start_date <= v.created_at <= end_date
                ]
            
            total_versions = len(all_versions)
            workflow_status_counts = {status: 0 for status in ApprovalStatus}
            review_status_counts = {status: 0 for status in ReviewStatus}
            publication_status_counts = {status: 0 for status in PublicationStatus}
            
            total_workflow_duration = 0
            completed_workflows = 0
            
            for version in all_versions:
                workflow_status_counts[version.approval_workflow.workflow_status] += 1
                review_status_counts[version.approval_workflow.review_status] += 1
                publication_status_counts[version.approval_workflow.publication_status] += 1
                
                if version.approval_workflow.workflow_completed_at:
                    duration = version.approval_workflow.workflow_duration_hours
                    if duration:
                        total_workflow_duration += duration
                        completed_workflows += 1
            
            return {
                "total_versions": total_versions,
                "workflow_status_distribution": workflow_status_counts,
                "review_status_distribution": review_status_counts,
                "publication_status_distribution": publication_status_counts,
                "average_workflow_duration_hours": (
                    total_workflow_duration / completed_workflows
                ) if completed_workflows > 0 else 0,
                "completed_workflows": completed_workflows,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting approval statistics: {e}")
            raise
    
    # ========================================================================
    # VERIFICATION OPERATIONS
    # ========================================================================
    
    async def update_digital_verification(
        self,
        version_id: str,
        verification_data: Dict[str, Any]
    ) -> bool:
        """Update digital verification data"""
        try:
            version = await self.get_by_id(version_id)
            if not version:
                return False
            
            # Update verification fields
            for key, value in verification_data.items():
                if hasattr(version.digital_verification, key):
                    setattr(version.digital_verification, key, value)
            
            # Recalculate trust score if not provided
            if "trust_score" not in verification_data:
                scores = []
                
                # Digital signature score
                if version.digital_verification.is_digitally_signed:
                    scores.append(100)
                else:
                    scores.append(0)
                
                # Hash verification score
                if version.digital_verification.is_hash_verified:
                    scores.append(100)
                else:
                    scores.append(0)
                
                # Integrity check score
                if version.digital_verification.is_integrity_verified:
                    scores.append(100)
                else:
                    scores.append(0)
                
                # Blockchain integration score
                if version.digital_verification.blockchain_hash:
                    scores.append(100)
                else:
                    scores.append(50)
                
                if scores:
                    version.digital_verification.trust_score = sum(scores) / len(scores)
                
                # Update trust level based on score
                if version.digital_verification.trust_score >= 90:
                    version.digital_verification.trust_level = "high"
                elif version.digital_verification.trust_score >= 70:
                    version.digital_verification.trust_level = "medium"
                elif version.digital_verification.trust_score >= 50:
                    version.digital_verification.trust_level = "low"
                else:
                    version.digital_verification.trust_level = "untrusted"
            
            await self.db_session.commit()
            logger.info(f"Updated digital verification for version {version_id}")
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating digital verification: {e}")
            raise
    
    async def get_versions_by_verification_status(
        self,
        verification_status: str,
        limit: int = 100
    ) -> List[CertificateVersion]:
        """Get versions by verification status"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            filtered_versions = []
            for version in all_versions:
                if version.digital_verification.verification_status == verification_status:
                    filtered_versions.append(version)
                    if len(filtered_versions) >= limit:
                        break
            
            return filtered_versions
            
        except Exception as e:
            logger.error(f"Error getting versions by verification status: {e}")
            raise
    
    async def get_versions_by_trust_level(
        self,
        trust_level: str,
        limit: int = 100
    ) -> List[CertificateVersion]:
        """Get versions by trust level"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            filtered_versions = []
            for version in all_versions:
                if version.digital_verification.trust_level == trust_level:
                    filtered_versions.append(version)
                    if len(filtered_versions) >= limit:
                        break
            
            return filtered_versions
            
        except Exception as e:
            logger.error(f"Error getting versions by trust level: {e}")
            raise
    
    async def get_verification_statistics(self) -> Dict[str, Any]:
        """Get digital verification statistics"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            total_versions = len(all_versions)
            verification_status_counts = {}
            trust_level_counts = {"high": 0, "medium": 0, "low": 0, "untrusted": 0}
            
            digitally_signed_count = 0
            hash_verified_count = 0
            integrity_verified_count = 0
            blockchain_integrated_count = 0
            total_trust_score = 0
            
            for version in all_versions:
                # Count verification statuses
                status = version.digital_verification.verification_status
                verification_status_counts[status] = verification_status_counts.get(status, 0) + 1
                
                # Count trust levels
                trust_level_counts[version.digital_verification.trust_level] += 1
                
                # Count verification features
                if version.digital_verification.is_digitally_signed:
                    digitally_signed_count += 1
                if version.digital_verification.is_hash_verified:
                    hash_verified_count += 1
                if version.digital_verification.is_integrity_verified:
                    integrity_verified_count += 1
                if version.digital_verification.blockchain_hash:
                    blockchain_integrated_count += 1
                
                total_trust_score += version.digital_verification.trust_score
            
            return {
                "total_versions": total_versions,
                "verification_status_distribution": verification_status_counts,
                "trust_level_distribution": trust_level_counts,
                "digitally_signed_percentage": (digitally_signed_count / total_versions * 100) if total_versions > 0 else 0,
                "hash_verified_percentage": (hash_verified_count / total_versions * 100) if total_versions > 0 else 0,
                "integrity_verified_percentage": (integrity_verified_count / total_versions * 100) if total_versions > 0 else 0,
                "blockchain_integrated_percentage": (blockchain_integrated_count / total_versions * 100) if total_versions > 0 else 0,
                "average_trust_score": total_trust_score / total_versions if total_versions > 0 else 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting verification statistics: {e}")
            raise
    
    # ========================================================================
    # BUSINESS INTELLIGENCE OPERATIONS
    # ========================================================================
    
    async def update_business_intelligence(
        self,
        version_id: str,
        business_data: Dict[str, Any]
    ) -> bool:
        """Update business intelligence data"""
        try:
            version = await self.get_by_id(version_id)
            if not version:
                return False
            
            # Update business intelligence fields
            for key, value in business_data.items():
                if hasattr(version.business_intelligence, key):
                    setattr(version.business_intelligence, key, value)
            
            # Recalculate overall business score
            scores = [
                version.business_intelligence.business_value_score,
                version.business_intelligence.stakeholder_satisfaction,
                version.business_intelligence.market_relevance,
                version.business_intelligence.strategic_alignment
            ]
            version.business_intelligence.overall_business_score = sum(scores) / len(scores)
            
            # Update risk assessment level
            risk_factors_count = len(version.business_intelligence.risk_factors)
            if risk_factors_count > 5:
                version.business_intelligence.business_risk_level = "high"
            elif risk_factors_count > 2:
                version.business_intelligence.business_risk_level = "medium"
            else:
                version.business_intelligence.business_risk_level = "low"
            
            await self.db_session.commit()
            logger.info(f"Updated business intelligence for version {version_id}")
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating business intelligence: {e}")
            raise
    
    async def get_versions_by_business_priority(
        self,
        business_priority: str,
        limit: int = 100
    ) -> List[CertificateVersion]:
        """Get versions by business priority"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            filtered_versions = []
            for version in all_versions:
                if version.business_intelligence.business_priority == business_priority:
                    filtered_versions.append(version)
                    if len(filtered_versions) >= limit:
                        break
            
            return filtered_versions
            
        except Exception as e:
            logger.error(f"Error getting versions by business priority: {e}")
            raise
    
    async def get_versions_by_risk_level(
        self,
        risk_level: str,
        limit: int = 100
    ) -> List[CertificateVersion]:
        """Get versions by business risk level"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            filtered_versions = []
            for version in all_versions:
                if version.business_intelligence.business_risk_level == risk_level:
                    filtered_versions.append(version)
                    if len(filtered_versions) >= limit:
                        break
            
            return filtered_versions
            
        except Exception as e:
            logger.error(f"Error getting versions by risk level: {e}")
            raise
    
    async def get_business_intelligence_statistics(self) -> Dict[str, Any]:
        """Get business intelligence statistics"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            total_versions = len(all_versions)
            business_priority_counts = {}
            risk_level_counts = {"low": 0, "medium": 0, "high": 0}
            
            total_business_score = 0
            total_stakeholder_satisfaction = 0
            total_market_relevance = 0
            total_strategic_alignment = 0
            total_roi = 0
            roi_count = 0
            
            for version in all_versions:
                # Count business priorities
                priority = version.business_intelligence.business_priority
                business_priority_counts[priority] = business_priority_counts.get(priority, 0) + 1
                
                # Count risk levels
                risk_level_counts[version.business_intelligence.business_risk_level] += 1
                
                # Accumulate scores
                total_business_score += version.business_intelligence.overall_business_score
                total_stakeholder_satisfaction += version.business_intelligence.stakeholder_satisfaction
                total_market_relevance += version.business_intelligence.market_relevance
                total_strategic_alignment += version.business_intelligence.strategic_alignment
                
                # Accumulate ROI
                if version.business_intelligence.roi_estimate:
                    total_roi += version.business_intelligence.roi_estimate
                    roi_count += 1
            
            return {
                "total_versions": total_versions,
                "business_priority_distribution": business_priority_counts,
                "risk_level_distribution": risk_level_counts,
                "average_business_score": total_business_score / total_versions if total_versions > 0 else 0,
                "average_stakeholder_satisfaction": total_stakeholder_satisfaction / total_versions if total_versions > 0 else 0,
                "average_market_relevance": total_market_relevance / total_versions if total_versions > 0 else 0,
                "average_strategic_alignment": total_strategic_alignment / total_versions if total_versions > 0 else 0,
                "average_roi": total_roi / roi_count if roi_count > 0 else 0,
                "versions_with_roi": roi_count,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting business intelligence statistics: {e}")
            raise
    
    # ========================================================================
    # ADVANCED QUERY OPERATIONS
    # ========================================================================
    
    async def get_latest_approved_version(self, certificate_id: str) -> Optional[CertificateVersion]:
        """Get the latest approved version of a certificate"""
        try:
            result = await self.db_session.execute(
                select(CertificateVersion)
                .where(CertificateVersion.certificate_id == certificate_id)
                .where(CertificateVersion.approval_status == ApprovalStatus.APPROVED)
                .where(CertificateVersion.is_deleted == False)
                .order_by(CertificateVersion.created_at.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting latest approved version: {e}")
            raise
    
    async def get_version_history(
        self,
        certificate_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CertificateVersion]:
        """Get version history within a date range"""
        try:
            query = select(CertificateVersion).where(
                CertificateVersion.certificate_id == certificate_id
            ).where(CertificateVersion.is_deleted == False)
            
            if start_date:
                query = query.where(CertificateVersion.created_at >= start_date)
            if end_date:
                query = query.where(CertificateVersion.created_at <= end_date)
            
            query = query.order_by(CertificateVersion.created_at.desc())
            result = await self.db_session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting version history: {e}")
            raise
    
    async def get_versions_by_type(
        self,
        version_type: VersionType,
        limit: int = 100
    ) -> List[CertificateVersion]:
        """Get versions by version type"""
        try:
            result = await self.db_session.execute(
                select(CertificateVersion)
                .where(CertificateVersion.version_type == version_type)
                .where(CertificateVersion.is_deleted == False)
                .order_by(CertificateVersion.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting versions by type: {e}")
            raise
    
    async def get_versions_by_approval_status(
        self,
        approval_status: ApprovalStatus,
        limit: int = 100
    ) -> List[CertificateVersion]:
        """Get versions by approval status"""
        try:
            result = await self.db_session.execute(
                select(CertificateVersion)
                .where(CertificateVersion.approval_status == approval_status)
                .where(CertificateVersion.is_deleted == False)
                .order_by(CertificateVersion.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting versions by approval status: {e}")
            raise
    
    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================
    
    async def bulk_update_versions(
        self,
        version_ids: List[str],
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Bulk update multiple versions"""
        try:
            results = {
                "successful": [],
                "failed": [],
                "total_processed": len(version_ids)
            }
            
            for version_id in version_ids:
                try:
                    success = await self.update(version_id, update_data)
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
    
    async def bulk_delete_versions(
        self,
        version_ids: List[str]
    ) -> Dict[str, Any]:
        """Bulk delete multiple versions"""
        try:
            results = {
                "successful": [],
                "failed": [],
                "total_processed": len(version_ids)
            }
            
            for version_id in version_ids:
                try:
                    success = await self.delete(version_id)
                    if success:
                        results["successful"].append(version_id)
                    else:
                        results["failed"].append(version_id)
                except Exception as e:
                    logger.error(f"Error deleting version {version_id}: {e}")
                    results["failed"].append(version_id)
            
            logger.info(f"Bulk delete completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk delete: {e}")
            raise
    
    # ========================================================================
    # STATISTICS AND ANALYTICS OPERATIONS
    # ========================================================================
    
    async def get_version_analytics(
        self,
        org_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive version analytics"""
        try:
            all_versions = await self.get_all(limit=1000)
            
            # Filter by date range if provided
            if start_date and end_date:
                all_versions = [
                    v for v in all_versions
                    if start_date <= v.created_at <= end_date
                ]
            
            total_versions = len(all_versions)
            version_type_counts = {vt: 0 for vt in VersionType}
            approval_status_counts = {as_: 0 for as_ in ApprovalStatus}
            change_impact_counts = {ci: 0 for ci in ChangeImpact}
            change_category_counts = {cc: 0 for cc in ChangeCategory}
            
            total_workflow_duration = 0
            completed_workflows = 0
            total_quality_score = 0
            total_business_score = 0
            total_trust_score = 0
            
            for version in all_versions:
                # Count by various categories
                version_type_counts[version.version_type] += 1
                approval_status_counts[version.approval_status] += 1
                change_impact_counts[version.change_tracking.change_impact] += 1
                change_category_counts[version.change_tracking.change_category] += 1
                
                # Accumulate scores
                total_quality_score += version.overall_quality_score
                total_business_score += version.business_intelligence.overall_business_score
                total_trust_score += version.digital_verification.trust_score
                
                # Accumulate workflow duration
                if version.approval_workflow.workflow_completed_at:
                    duration = version.approval_workflow.workflow_duration_hours
                    if duration:
                        total_workflow_duration += duration
                        completed_workflows += 1
            
            return {
                "total_versions": total_versions,
                "version_type_distribution": version_type_counts,
                "approval_status_distribution": approval_status_counts,
                "change_impact_distribution": change_impact_counts,
                "change_category_distribution": change_category_counts,
                "average_quality_score": total_quality_score / total_versions if total_versions > 0 else 0,
                "average_business_score": total_business_score / total_versions if total_versions > 0 else 0,
                "average_trust_score": total_trust_score / total_versions if total_versions > 0 else 0,
                "average_workflow_duration_hours": (
                    total_workflow_duration / completed_workflows
                ) if completed_workflows > 0 else 0,
                "completed_workflows": completed_workflows,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting version analytics: {e}")
            raise
    
    # ========================================================================
    # EXPORT OPERATIONS
    # ========================================================================
    
    async def export_version_data(
        self,
        version_ids: List[str],
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export version data in specified format"""
        try:
            versions = []
            for version_id in version_ids:
                version = await self.get_by_id(version_id)
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
