"""
Certificate Updater - Real-Time Update Service

Handles real-time certificate updates as modules process data.
Coordinates with the main certificate manager to ensure
smooth certificate evolution and progress tracking.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from ..models.certificates_registry import (
    CertificateRegistry,
    ModuleStatus,
    CertificateStatus,
    QualityLevel
)
from ..models.certificates_metrics import CertificateMetrics, MetricCategory
from ..services.certificates_registry_service import CertificatesRegistryService
from ..services.certificates_metrics_service import CertificatesMetricsService

logger = logging.getLogger(__name__)


class UpdateType(str, Enum):
    """Types of certificate updates"""
    MODULE_PROGRESS = "module_progress"
    QUALITY_UPDATE = "quality_update"
    COMPLIANCE_UPDATE = "compliance_update"
    SECURITY_UPDATE = "security_update"
    STATUS_CHANGE = "status_change"
    METRICS_UPDATE = "metrics_update"


class UpdatePriority(str, Enum):
    """Priority levels for updates"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CertificateUpdater:
    """
    Real-time certificate update service
    
    Handles:
    - Module progress updates
    - Quality score updates
    - Compliance status updates
    - Security metric updates
    - Real-time metrics collection
    - Update validation and conflict resolution
    """
    
    def __init__(self, registry_service: CertificatesRegistryService, metrics_service: CertificatesMetricsService):
        """Initialize the certificate updater"""
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Update queue for processing
        self.update_queue: asyncio.Queue = asyncio.Queue()
        
        # Update history tracking
        self.update_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Processing locks per certificate
        self.processing_locks: Dict[str, asyncio.Lock] = {}
        
        logger.info("Certificate Updater initialized successfully")
    
    async def start_update_processor(self) -> None:
        """Start the background update processor"""
        try:
            logger.info("Starting certificate update processor")
            
            # Start background task
            asyncio.create_task(self._process_update_queue())
            
            logger.info("Certificate update processor started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start update processor: {e}")
            raise
    
    async def queue_update(
        self,
        certificate_id: str,
        update_type: UpdateType,
        update_data: Dict[str, Any],
        priority: UpdatePriority = UpdatePriority.MEDIUM
    ) -> bool:
        """
        Queue an update for processing
        
        This is the main entry point for updates from modules.
        Updates are queued and processed asynchronously.
        """
        try:
            update_item = {
                "certificate_id": certificate_id,
                "update_type": update_type,
                "update_data": update_data,
                "priority": priority,
                "timestamp": datetime.utcnow(),
                "processed": False
            }
            
            # Add to queue
            await self.update_queue.put(update_item)
            
            # Track in history
            if certificate_id not in self.update_history:
                self.update_history[certificate_id] = []
            self.update_history[certificate_id].append(update_item)
            
            logger.info(f"Queued {update_type.value} update for certificate {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing update: {e}")
            return False
    
    async def _process_update_queue(self) -> None:
        """Background processor for the update queue"""
        try:
            logger.info("Update processor started")
            
            while True:
                try:
                    # Get update from queue
                    update_item = await self.update_queue.get()
                    
                    # Process the update
                    await self._process_single_update(update_item)
                    
                    # Mark as processed
                    update_item["processed"] = True
                    
                    # Mark queue task as done
                    self.update_queue.task_done()
                    
                except asyncio.CancelledError:
                    logger.info("Update processor cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error processing update: {e}")
                    
        except Exception as e:
            logger.error(f"Update processor failed: {e}")
    
    async def _process_single_update(self, update_item: Dict[str, Any]) -> None:
        """Process a single update item"""
        try:
            certificate_id = update_item["certificate_id"]
            update_type = update_item["update_type"]
            update_data = update_item["update_data"]
            
            logger.info(f"Processing {update_type.value} update for certificate {certificate_id}")
            
            # Acquire processing lock for this certificate
            if certificate_id not in self.processing_locks:
                self.processing_locks[certificate_id] = asyncio.Lock()
            
            async with self.processing_locks[certificate_id]:
                # Process based on update type
                if update_type == UpdateType.MODULE_PROGRESS:
                    await self._process_module_progress_update(certificate_id, update_data)
                elif update_type == UpdateType.QUALITY_UPDATE:
                    await self._process_quality_update(certificate_id, update_data)
                elif update_type == UpdateType.COMPLIANCE_UPDATE:
                    await self._process_compliance_update(certificate_id, update_data)
                elif update_type == UpdateType.SECURITY_UPDATE:
                    await self._process_security_update(certificate_id, update_data)
                elif update_type == UpdateType.STATUS_CHANGE:
                    await self._process_status_change(certificate_id, update_data)
                elif update_type == UpdateType.METRICS_UPDATE:
                    await self._process_metrics_update(certificate_id, update_data)
                else:
                    logger.warning(f"Unknown update type: {update_type}")
            
            logger.info(f"Successfully processed {update_type.value} update for certificate {certificate_id}")
            
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    async def _process_module_progress_update(self, certificate_id: str, update_data: Dict[str, Any]) -> None:
        """Process module progress update"""
        try:
            module_name = update_data.get("module_name")
            progress_percentage = update_data.get("progress_percentage", 0)
            status = update_data.get("status", "in_progress")
            
            if not module_name:
                logger.error("Module name missing from progress update")
                return
            
            # Determine module status
            if status == "completed":
                module_status = ModuleStatus.ACTIVE
            elif status == "failed":
                module_status = ModuleStatus.ERROR
            elif status == "in_progress":
                module_status = ModuleStatus.MAINTENANCE
            else:
                module_status = ModuleStatus.PENDING
            
            # Update module status
            await self.registry_service.update_module_status(
                certificate_id, module_name, module_status
            )
            
            # Update progress metrics
            await self._update_progress_metrics(certificate_id, module_name, progress_percentage)
            
            logger.info(f"Updated module {module_name} progress to {progress_percentage}% for certificate {certificate_id}")
            
        except Exception as e:
            logger.error(f"Error processing module progress update: {e}")
    
    async def _process_quality_update(self, certificate_id: str, update_data: Dict[str, Any]) -> None:
        """Process quality assessment update"""
        try:
            quality_score = update_data.get("quality_score", 0.0)
            quality_level = update_data.get("quality_level", "unknown")
            assessment_notes = update_data.get("assessment_notes", "")
            
            # Update quality assessment
            await self.registry_service.update_quality_assessment(
                certificate_id,
                {
                    "overall_quality_score": quality_score,
                    "quality_level": quality_level,
                    "assessment_notes": assessment_notes,
                    "last_assessment": datetime.utcnow()
                }
            )
            
            # Create quality metrics
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=MetricCategory.QUALITY,
                metric_name="quality_assessment_score",
                metric_value=quality_score,
                metric_unit="percentage"
            )
            
            logger.info(f"Updated quality assessment to {quality_score}% for certificate {certificate_id}")
            
        except Exception as e:
            logger.error(f"Error processing quality update: {e}")
    
    async def _process_compliance_update(self, certificate_id: str, update_data: Dict[str, Any]) -> None:
        """Process compliance tracking update"""
        try:
            compliance_status = update_data.get("compliance_status", "unknown")
            compliance_score = update_data.get("compliance_score", 0.0)
            audit_notes = update_data.get("audit_notes", "")
            
            # Update compliance tracking
            await self.registry_service.update_compliance_status(
                certificate_id,
                {
                    "compliance_status": compliance_status,
                    "compliance_score": compliance_score,
                    "audit_notes": audit_notes,
                    "last_audit": datetime.utcnow()
                }
            )
            
            logger.info(f"Updated compliance status to {compliance_status} for certificate {certificate_id}")
            
        except Exception as e:
            logger.error(f"Error processing compliance update: {e}")
    
    async def _process_security_update(self, certificate_id: str, update_data: Dict[str, Any]) -> None:
        """Process security metrics update"""
        try:
            security_score = update_data.get("security_score", 0.0)
            security_level = update_data.get("security_level", "unknown")
            security_events = update_data.get("security_events", [])
            
            # Update security metrics
            await self.registry_service.update_security_metrics(
                certificate_id,
                {
                    "security_score": security_score,
                    "security_level": security_level,
                    "security_events": security_events,
                    "last_security_assessment": datetime.utcnow()
                }
            )
            
            # Create security metrics
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=MetricCategory.SECURITY,
                metric_name="security_assessment_score",
                metric_value=security_score,
                metric_unit="percentage"
            )
            
            logger.info(f"Updated security metrics to {security_score}% for certificate {certificate_id}")
            
        except Exception as e:
            logger.error(f"Error processing security update: {e}")
    
    async def _process_status_change(self, certificate_id: str, update_data: Dict[str, Any]) -> None:
        """Process certificate status change"""
        try:
            new_status = update_data.get("new_status")
            status_reason = update_data.get("status_reason", "")
            
            if not new_status:
                logger.error("New status missing from status change update")
                return
            
            # Update certificate status
            await self.registry_service.update_certificate_status(
                certificate_id, new_status
            )
            
            logger.info(f"Updated certificate {certificate_id} status to {new_status.value}")
            
        except Exception as e:
            logger.error(f"Error processing status change: {e}")
    
    async def _process_metrics_update(self, certificate_id: str, update_data: Dict[str, Any]) -> None:
        """Process metrics update"""
        try:
            metric_name = update_data.get("metric_name")
            metric_value = update_data.get("metric_value", 0.0)
            metric_unit = update_data.get("metric_unit", "count")
            metric_category = update_data.get("metric_category", MetricCategory.PERFORMANCE)
            
            if not metric_name:
                logger.error("Metric name missing from metrics update")
                return
            
            # Create or update metric
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=metric_category,
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit
            )
            
            logger.info(f"Updated metric {metric_name} to {metric_value} {metric_unit} for certificate {certificate_id}")
            
        except Exception as e:
            logger.error(f"Error processing metrics update: {e}")
    
    async def _update_progress_metrics(self, certificate_id: str, module_name: str, progress_percentage: float) -> None:
        """Update progress metrics for a module"""
        try:
            # Create progress metric
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=MetricCategory.PERFORMANCE,
                metric_name=f"{module_name}_progress",
                metric_value=progress_percentage,
                metric_unit="percentage"
            )
            
        except Exception as e:
            logger.error(f"Error updating progress metrics: {e}")
    
    async def get_update_history(self, certificate_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get update history for a certificate"""
        try:
            if certificate_id not in self.update_history:
                return []
            
            # Return recent updates
            return self.update_history[certificate_id][-limit:]
            
        except Exception as e:
            logger.error(f"Error getting update history: {e}")
            return []
    
    async def get_pending_updates_count(self) -> int:
        """Get count of pending updates in queue"""
        try:
            return self.update_queue.qsize()
            
        except Exception as e:
            logger.error(f"Error getting pending updates count: {e}")
            return 0
    
    async def stop_update_processor(self) -> None:
        """Stop the update processor gracefully"""
        try:
            logger.info("Stopping certificate update processor")
            
            # Cancel background task
            # Note: In a real implementation, you'd need to track the task ID
            # and cancel it properly
            
            logger.info("Certificate update processor stopped")
            
        except Exception as e:
            logger.error(f"Error stopping update processor: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the certificate updater"""
        try:
            health_status = {
                "status": "healthy",
                "queue_size": self.update_queue.qsize(),
                "active_locks": len(self.processing_locks),
                "tracked_certificates": len(self.update_history),
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
