"""
Progress Tracker - Certificate Progress Monitoring Service

Monitors certificate progress across all modules and tracks
completion status. Provides real-time progress updates and
completion validation for certificates.
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


class ProgressStatus(str, Enum):
    """Progress status levels"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    NEAR_COMPLETION = "near_completion"
    COMPLETED = "completed"
    STALLED = "stalled"
    ERROR = "error"


class ProgressThreshold(str, Enum):
    """Progress threshold levels"""
    LOW = "low"           # 0-25%
    MEDIUM = "medium"     # 26-50%
    HIGH = "high"         # 51-75%
    CRITICAL = "critical" # 76-100%


class ProgressTracker:
    """
    Certificate progress tracking service
    
    Handles:
    - Real-time progress monitoring
    - Module completion tracking
    - Progress threshold alerts
    - Completion validation
    - Progress analytics and reporting
    """
    
    def __init__(
        self, 
        registry_service: CertificatesRegistryService,
        metrics_service: CertificatesMetricsService
    ):
        """Initialize the progress tracker"""
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Progress tracking data
        self.progress_cache: Dict[str, Dict[str, Any]] = {}
        
        # Progress thresholds and alerts
        self.progress_thresholds = {
            ProgressThreshold.LOW: 25.0,
            ProgressThreshold.MEDIUM: 50.0,
            ProgressThreshold.HIGH: 75.0,
            ProgressThreshold.CRITICAL: 100.0
        }
        
        # Progress monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Progress event callbacks
        self.progress_callbacks: List[callable] = []
        
        logger.info("Progress Tracker initialized successfully")
    
    async def start_progress_monitoring(self, certificate_id: str) -> bool:
        """Start monitoring progress for a specific certificate"""
        try:
            if certificate_id in self.monitoring_tasks:
                logger.warning(f"Progress monitoring already active for certificate: {certificate_id}")
                return True
            
            # Create monitoring task
            monitoring_task = asyncio.create_task(
                self._monitor_certificate_progress(certificate_id)
            )
            
            self.monitoring_tasks[certificate_id] = monitoring_task
            
            logger.info(f"Started progress monitoring for certificate: {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting progress monitoring: {e}")
            return False
    
    async def stop_progress_monitoring(self, certificate_id: str) -> bool:
        """Stop monitoring progress for a specific certificate"""
        try:
            if certificate_id not in self.monitoring_tasks:
                return True
            
            # Cancel monitoring task
            task = self.monitoring_tasks[certificate_id]
            task.cancel()
            
            # Wait for task to complete
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Remove from tracking
            del self.monitoring_tasks[certificate_id]
            
            if certificate_id in self.progress_cache:
                del self.progress_cache[certificate_id]
            
            logger.info(f"Stopped progress monitoring for certificate: {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping progress monitoring: {e}")
            return False
    
    async def _monitor_certificate_progress(self, certificate_id: str) -> None:
        """Background task to monitor certificate progress"""
        try:
            logger.info(f"Progress monitoring started for certificate: {certificate_id}")
            
            while True:
                try:
                    # Get current progress
                    progress_data = await self.get_certificate_progress(certificate_id)
                    
                    if not progress_data:
                        logger.warning(f"No progress data for certificate: {certificate_id}")
                        await asyncio.sleep(30)  # Wait 30 seconds before retry
                        continue
                    
                    # Check for progress changes
                    await self._check_progress_changes(certificate_id, progress_data)
                    
                    # Check for threshold crossings
                    await self._check_threshold_crossings(certificate_id, progress_data)
                    
                    # Check for stalled progress
                    await self._check_stalled_progress(certificate_id, progress_data)
                    
                    # Update progress cache
                    self.progress_cache[certificate_id] = progress_data
                    
                    # Wait before next check
                    await asyncio.sleep(10)  # Check every 10 seconds
                    
                except asyncio.CancelledError:
                    logger.info(f"Progress monitoring cancelled for certificate: {certificate_id}")
                    break
                except Exception as e:
                    logger.error(f"Error in progress monitoring: {e}")
                    await asyncio.sleep(30)  # Wait before retry
                    
        except Exception as e:
            logger.error(f"Progress monitoring failed for certificate {certificate_id}: {e}")
    
    async def get_certificate_progress(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive progress data for a certificate"""
        try:
            # Get certificate details
            certificate = await self.registry_service.get_certificate(certificate_id)
            if not certificate:
                return None
            
            # Get latest metrics
            metrics = await self.metrics_service.get_certificate_metrics(
                certificate_id, limit=50
            )
            
            # Calculate progress breakdown
            progress_breakdown = await self._calculate_progress_breakdown(certificate, metrics)
            
            # Build progress data
            progress_data = {
                "certificate_id": certificate_id,
                "overall_progress": certificate.module_status.health_score,
                "progress_status": self._determine_progress_status(certificate.module_status.health_score),
                "module_progress": progress_breakdown,
                "quality_score": certificate.quality_assessment.overall_quality_score,
                "compliance_status": certificate.compliance_tracking.compliance_status.value,
                "security_score": certificate.security_metrics.security_score,
                "estimated_completion": await self._estimate_completion_time(certificate_id),
                "last_updated": datetime.utcnow().isoformat(),
                "metrics_count": len(metrics)
            }
            
            return progress_data
            
        except Exception as e:
            logger.error(f"Error getting certificate progress: {e}")
            return None
    
    async def _calculate_progress_breakdown(
        self, 
        certificate: CertificateRegistry, 
        metrics: List[CertificateMetrics]
    ) -> Dict[str, Any]:
        """Calculate detailed progress breakdown by module"""
        try:
            breakdown = {}
            
            # Get module statuses
            module_statuses = {
                "aasx_module": certificate.module_status.aasx_module,
                "twin_registry": certificate.module_status.twin_registry,
                "ai_rag": certificate.module_status.ai_rag,
                "kg_neo4j": certificate.module_status.kg_neo4j,
                "physics_modeling": certificate.module_status.physics_modeling,
                "federated_learning": certificate.module_status.federated_learning,
                "data_governance": certificate.module_status.data_governance
            }
            
            # Calculate progress for each module
            for module_name, status in module_statuses.items():
                if status == ModuleStatus.ACTIVE:
                    progress = 100.0
                elif status == ModuleStatus.ERROR:
                    progress = 0.0
                elif status == ModuleStatus.MAINTENANCE:
                    # Get progress from metrics
                    progress = await self._get_module_progress_from_metrics(
                        certificate.certificate_id, module_name, metrics
                    )
                else:
                    progress = 0.0
                
                breakdown[module_name] = {
                    "status": status.value,
                    "progress": progress,
                    "completed": status == ModuleStatus.ACTIVE,
                    "has_errors": status == ModuleStatus.ERROR
                }
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error calculating progress breakdown: {e}")
            return {}
    
    async def _get_module_progress_from_metrics(
        self, 
        certificate_id: str, 
        module_name: str, 
        metrics: List[CertificateMetrics]
    ) -> float:
        """Get module progress from metrics data"""
        try:
            # Look for progress metrics for this module
            progress_metrics = [
                m for m in metrics 
                if m.metric_name == f"{module_name}_progress" and 
                m.metric_category == MetricCategory.PERFORMANCE
            ]
            
            if progress_metrics:
                # Return the latest progress value
                latest_metric = max(progress_metrics, key=lambda m: m.recorded_at)
                return latest_metric.metric_value
            
            # Default progress based on module status
            return 50.0  # Assume 50% if no specific metrics
            
        except Exception as e:
            logger.error(f"Error getting module progress from metrics: {e}")
            return 0.0
    
    def _determine_progress_status(self, progress_percentage: float) -> ProgressStatus:
        """Determine progress status based on percentage"""
        if progress_percentage == 0:
            return ProgressStatus.NOT_STARTED
        elif progress_percentage < 25:
            return ProgressStatus.IN_PROGRESS
        elif progress_percentage < 75:
            return ProgressStatus.IN_PROGRESS
        elif progress_percentage < 100:
            return ProgressStatus.NEAR_COMPLETION
        else:
            return ProgressStatus.COMPLETED
    
    async def _estimate_completion_time(self, certificate_id: str) -> Optional[str]:
        """Estimate completion time based on current progress"""
        try:
            # Get progress history
            progress_history = await self._get_progress_history(certificate_id)
            
            if len(progress_history) < 2:
                return None
            
            # Calculate progress rate
            recent_progress = progress_history[-5:]  # Last 5 progress points
            if len(recent_progress) < 2:
                return None
            
            # Calculate average progress rate per hour
            total_time = (recent_progress[-1]["timestamp"] - recent_progress[0]["timestamp"]).total_seconds() / 3600
            total_progress = recent_progress[-1]["progress"] - recent_progress[0]["progress"]
            
            if total_progress <= 0 or total_time <= 0:
                return None
            
            progress_rate_per_hour = total_progress / total_time
            
            # Get current progress
            current_progress = await self.get_certificate_progress(certificate_id)
            if not current_progress:
                return None
            
            remaining_progress = 100.0 - current_progress["overall_progress"]
            
            if progress_rate_per_hour <= 0:
                return None
            
            # Estimate remaining time
            remaining_hours = remaining_progress / progress_rate_per_hour
            estimated_completion = datetime.utcnow() + timedelta(hours=remaining_hours)
            
            return estimated_completion.isoformat()
            
        except Exception as e:
            logger.error(f"Error estimating completion time: {e}")
            return None
    
    async def _get_progress_history(self, certificate_id: str) -> List[Dict[str, Any]]:
        """Get progress history for a certificate"""
        try:
            # This would typically come from a progress history table
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting progress history: {e}")
            return []
    
    async def _check_progress_changes(self, certificate_id: str, current_progress: Dict[str, Any]) -> None:
        """Check for significant progress changes"""
        try:
            if certificate_id not in self.progress_cache:
                return
            
            previous_progress = self.progress_cache[certificate_id]
            previous_overall = previous_progress.get("overall_progress", 0)
            current_overall = current_progress.get("overall_progress", 0)
            
            # Check for significant changes (more than 5%)
            if abs(current_overall - previous_overall) >= 5.0:
                await self._notify_progress_change(
                    certificate_id, 
                    previous_overall, 
                    current_overall
                )
                
        except Exception as e:
            logger.error(f"Error checking progress changes: {e}")
    
    async def _check_threshold_crossings(self, certificate_id: str, progress_data: Dict[str, Any]) -> None:
        """Check for progress threshold crossings"""
        try:
            overall_progress = progress_data.get("overall_progress", 0)
            
            for threshold_name, threshold_value in self.progress_thresholds.items():
                # Check if we've crossed this threshold
                if overall_progress >= threshold_value:
                    await self._notify_threshold_crossing(
                        certificate_id, 
                        threshold_name, 
                        threshold_value, 
                        overall_progress
                    )
                    
        except Exception as e:
            logger.error(f"Error checking threshold crossings: {e}")
    
    async def _check_stalled_progress(self, certificate_id: str, progress_data: Dict[str, Any]) -> None:
        """Check for stalled progress"""
        try:
            # This would check if progress hasn't changed for a significant time
            # For now, just log the check
            pass
            
        except Exception as e:
            logger.error(f"Error checking stalled progress: {e}")
    
    async def _notify_progress_change(
        self, 
        certificate_id: str, 
        previous_progress: float, 
        current_progress: float
    ) -> None:
        """Notify about significant progress changes"""
        try:
            change_message = f"Certificate {certificate_id} progress changed from {previous_progress:.1f}% to {current_progress:.1f}%"
            logger.info(change_message)
            
            # Notify callbacks
            for callback in self.progress_callbacks:
                try:
                    await callback("progress_change", {
                        "certificate_id": certificate_id,
                        "previous_progress": previous_progress,
                        "current_progress": current_progress,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error notifying progress change: {e}")
    
    async def _notify_threshold_crossing(
        self, 
        certificate_id: str, 
        threshold_name: str, 
        threshold_value: float, 
        current_progress: float
    ) -> None:
        """Notify about threshold crossings"""
        try:
            threshold_message = f"Certificate {certificate_id} crossed {threshold_name} threshold ({threshold_value}%) - Current: {current_progress:.1f}%"
            logger.info(threshold_message)
            
            # Notify callbacks
            for callback in self.progress_callbacks:
                try:
                    await callback("threshold_crossing", {
                        "certificate_id": certificate_id,
                        "threshold_name": threshold_name,
                        "threshold_value": threshold_value,
                        "current_progress": current_progress,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error in threshold callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error notifying threshold crossing: {e}")
    
    def add_progress_callback(self, callback: callable) -> None:
        """Add a callback for progress events"""
        try:
            self.progress_callbacks.append(callback)
            logger.info("Added progress callback")
            
        except Exception as e:
            logger.error(f"Error adding progress callback: {e}")
    
    def remove_progress_callback(self, callback: callable) -> None:
        """Remove a progress callback"""
        try:
            if callback in self.progress_callbacks:
                self.progress_callbacks.remove(callback)
                logger.info("Removed progress callback")
                
        except Exception as e:
            logger.error(f"Error removing progress callback: {e}")
    
    async def get_all_certificates_progress(self) -> List[Dict[str, Any]]:
        """Get progress for all monitored certificates"""
        try:
            progress_list = []
            
            for certificate_id in self.monitoring_tasks.keys():
                progress_data = await self.get_certificate_progress(certificate_id)
                if progress_data:
                    progress_list.append(progress_data)
            
            return progress_list
            
        except Exception as e:
            logger.error(f"Error getting all certificates progress: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the progress tracker"""
        try:
            health_status = {
                "status": "healthy",
                "monitored_certificates": len(self.monitoring_tasks),
                "progress_cache_size": len(self.progress_cache),
                "active_callbacks": len(self.progress_callbacks),
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
