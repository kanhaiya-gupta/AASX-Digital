"""
Twin Monitoring Service
======================

Service for twin health and performance monitoring.
Handles real-time status monitoring and health checks.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import asyncio

# Import shared services
from src.shared.services.digital_twin_service import DigitalTwinService
from src.shared.repositories.digital_twin_repository import DigitalTwinRepository

logger = logging.getLogger(__name__)

class TwinMonitoringService:
    """
    Service for monitoring twin health and performance.
    Handles real-time status monitoring and health checks.
    """
    
    def __init__(self, twin_service: DigitalTwinService):
        """Initialize the twin monitoring service."""
        self.twin_service = twin_service
        self.twin_repo = twin_service.get_repository()
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_tasks = {}
        
        logger.info("Twin Monitoring Service initialized")
    
    async def get_twin_health(self, twin_id: str) -> Dict[str, Any]:
        """
        Get comprehensive health status for a twin.
        
        Args:
            twin_id: The twin ID to check
            
        Returns:
            Health status information
        """
        try:
            logger.info(f"Getting health status for twin: {twin_id}")
            
            # Get twin
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            # Extract health information
            health_status = getattr(twin, 'health_status', 'unknown')
            health_score = getattr(twin, 'health_score', 0)
            status = getattr(twin, 'status', 'unknown')
            
            # Perform health checks
            health_checks = await self._perform_health_checks(twin)
            
            # Determine overall health
            overall_health = self._determine_overall_health(health_status, health_score, health_checks)
            
            result = {
                "twin_id": twin_id,
                "overall_health": overall_health,
                "health_status": health_status,
                "health_score": health_score,
                "operational_status": status,
                "health_checks": health_checks,
                "last_check": datetime.now().isoformat(),
                "recommendations": self._generate_health_recommendations(overall_health, health_checks)
            }
            
            logger.info(f"Health status for twin {twin_id}: {overall_health}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get health for twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to get health for twin {twin_id}: {str(e)}")
    
    async def get_twin_performance(self, twin_id: str, 
                                 time_range: str = "24h") -> Dict[str, Any]:
        """
        Get performance metrics for a twin.
        
        Args:
            twin_id: The twin ID to get performance for
            time_range: Time range for metrics ('1h', '24h', '7d', '30d')
            
        Returns:
            Performance metrics
        """
        try:
            logger.info(f"Getting performance metrics for twin: {twin_id}")
            
            # Get twin
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            # Calculate time range
            end_time = datetime.now()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)  # Default to 24h
            
            # Get performance metrics (placeholder implementation)
            performance_metrics = await self._get_performance_metrics(twin_id, start_time, end_time)
            
            result = {
                "twin_id": twin_id,
                "time_range": time_range,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "metrics": performance_metrics,
                "summary": self._generate_performance_summary(performance_metrics)
            }
            
            logger.info(f"Performance metrics retrieved for twin: {twin_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get performance for twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to get performance for twin {twin_id}: {str(e)}")
    
    async def get_twin_events(self, twin_id: str, 
                            event_type: str = None, 
                            limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get event history for a twin.
        
        Args:
            twin_id: The twin ID to get events for
            event_type: Filter by event type
            limit: Maximum number of events
            
        Returns:
            List of events
        """
        try:
            logger.info(f"Getting events for twin: {twin_id}")
            
            # Get twin
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            # Get events (placeholder implementation)
            events = await self._get_twin_events(twin_id, event_type, limit)
            
            logger.info(f"Retrieved {len(events)} events for twin: {twin_id}")
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events for twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to get events for twin {twin_id}: {str(e)}")
    
    async def monitor_twin_status(self, twin_id: str, 
                                callback=None) -> Dict[str, Any]:
        """
        Start real-time monitoring for a twin.
        
        Args:
            twin_id: The twin ID to monitor
            callback: Optional callback function for status updates
            
        Returns:
            Monitoring status
        """
        try:
            logger.info(f"Starting real-time monitoring for twin: {twin_id}")
            
            # Check if already monitoring
            if twin_id in self.monitoring_tasks:
                logger.warning(f"Already monitoring twin: {twin_id}")
                return {
                    "success": True,
                    "message": "Already monitoring this twin",
                    "twin_id": twin_id,
                    "monitoring": True
                }
            
            # Start monitoring task
            monitoring_task = asyncio.create_task(
                self._monitoring_loop(twin_id, callback)
            )
            
            self.monitoring_tasks[twin_id] = {
                "task": monitoring_task,
                "started_at": datetime.now().isoformat(),
                "callback": callback,
                "active": True
            }
            
            result = {
                "success": True,
                "message": f"Started monitoring twin: {twin_id}",
                "twin_id": twin_id,
                "monitoring": True,
                "started_at": datetime.now().isoformat()
            }
            
            logger.info(f"Started monitoring twin: {twin_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to start monitoring for twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to start monitoring for twin {twin_id}: {str(e)}")
    
    async def stop_monitoring(self, twin_id: str) -> Dict[str, Any]:
        """
        Stop real-time monitoring for a twin.
        
        Args:
            twin_id: The twin ID to stop monitoring
            
        Returns:
            Stop monitoring result
        """
        try:
            logger.info(f"Stopping monitoring for twin: {twin_id}")
            
            if twin_id not in self.monitoring_tasks:
                logger.warning(f"Not monitoring twin: {twin_id}")
                return {
                    "success": True,
                    "message": "Not monitoring this twin",
                    "twin_id": twin_id,
                    "monitoring": False
                }
            
            # Cancel monitoring task
            monitoring_info = self.monitoring_tasks[twin_id]
            monitoring_info["task"].cancel()
            monitoring_info["active"] = False
            
            # Remove from monitoring tasks
            del self.monitoring_tasks[twin_id]
            
            result = {
                "success": True,
                "message": f"Stopped monitoring twin: {twin_id}",
                "twin_id": twin_id,
                "monitoring": False,
                "stopped_at": datetime.now().isoformat()
            }
            
            logger.info(f"Stopped monitoring twin: {twin_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring for twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to stop monitoring for twin {twin_id}: {str(e)}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            System health information
        """
        try:
            logger.info("Getting system health status")
            
            # Get all twins
            all_twins = self.twin_repo.get_all()
            
            # Calculate system-wide metrics
            total_twins = len(all_twins)
            active_twins = len([t for t in all_twins if getattr(t, 'status', '') == 'active'])
            healthy_twins = len([t for t in all_twins if getattr(t, 'health_status', '') == 'healthy'])
            warning_twins = len([t for t in all_twins if getattr(t, 'health_status', '') == 'warning'])
            critical_twins = len([t for t in all_twins if getattr(t, 'health_status', '') == 'critical'])
            
            # Calculate overall health score
            if total_twins > 0:
                overall_health_score = (healthy_twins / total_twins) * 100
            else:
                overall_health_score = 100
            
            # Determine overall system status
            if critical_twins > 0:
                system_status = "critical"
            elif warning_twins > 0:
                system_status = "warning"
            else:
                system_status = "healthy"
            
            result = {
                "system_status": system_status,
                "overall_health_score": overall_health_score,
                "total_twins": total_twins,
                "active_twins": active_twins,
                "health_distribution": {
                    "healthy": healthy_twins,
                    "warning": warning_twins,
                    "critical": critical_twins
                },
                "monitoring_status": {
                    "active_monitoring": len(self.monitoring_tasks),
                    "monitoring_tasks": list(self.monitoring_tasks.keys())
                },
                "last_check": datetime.now().isoformat()
            }
            
            logger.info(f"System health: {system_status} (score: {overall_health_score:.1f}%)")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get system health: {str(e)}")
            raise Exception(f"Failed to get system health: {str(e)}")
    
    async def _perform_health_checks(self, twin) -> Dict[str, Any]:
        """
        Perform comprehensive health checks on a twin.
        
        Args:
            twin: Twin object to check
            
        Returns:
            Health check results
        """
        checks = {}
        
        try:
            # Status check
            status = getattr(twin, 'status', 'unknown')
            checks["status"] = {
                "check": "operational_status",
                "status": "pass" if status in ['active', 'inactive'] else "fail",
                "value": status,
                "message": f"Twin status is {status}"
            }
            
            # Health score check
            health_score = getattr(twin, 'health_score', 0)
            checks["health_score"] = {
                "check": "health_score",
                "status": "pass" if health_score >= 80 else "warning" if health_score >= 60 else "fail",
                "value": health_score,
                "message": f"Health score is {health_score}"
            }
            
            # Timestamp check (check if twin is stale)
            updated_at = getattr(twin, 'updated_at', '')
            if updated_at:
                try:
                    last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    time_diff = datetime.now(last_update.tzinfo) - last_update
                    
                    if time_diff.days > 7:
                        status = "warning"
                        message = f"Twin not updated for {time_diff.days} days"
                    elif time_diff.days > 30:
                        status = "fail"
                        message = f"Twin not updated for {time_diff.days} days"
                    else:
                        status = "pass"
                        message = f"Twin updated {time_diff.days} days ago"
                    
                    checks["freshness"] = {
                        "check": "data_freshness",
                        "status": status,
                        "value": f"{time_diff.days} days",
                        "message": message
                    }
                except Exception as e:
                    checks["freshness"] = {
                        "check": "data_freshness",
                        "status": "fail",
                        "value": "unknown",
                        "message": f"Failed to parse timestamp: {str(e)}"
                    }
            
            # Metadata check
            metadata = getattr(twin, 'metadata', {})
            checks["metadata"] = {
                "check": "metadata_completeness",
                "status": "pass" if metadata else "warning",
                "value": len(metadata) if isinstance(metadata, dict) else 0,
                "message": f"Metadata has {len(metadata) if isinstance(metadata, dict) else 0} entries"
            }
            
        except Exception as e:
            logger.error(f"Error performing health checks: {str(e)}")
            checks["error"] = {
                "check": "health_check_error",
                "status": "fail",
                "value": "error",
                "message": f"Health check failed: {str(e)}"
            }
        
        return checks
    
    def _determine_overall_health(self, health_status: str, health_score: int, 
                                health_checks: Dict[str, Any]) -> str:
        """
        Determine overall health based on various factors.
        
        Args:
            health_status: Current health status
            health_score: Health score
            health_checks: Health check results
            
        Returns:
            Overall health status
        """
        # Check for critical failures
        for check_name, check_result in health_checks.items():
            if check_result.get("status") == "fail":
                return "critical"
        
        # Check health score
        if health_score < 60:
            return "critical"
        elif health_score < 80:
            return "warning"
        
        # Check operational status
        if health_status == "critical":
            return "critical"
        elif health_status == "warning":
            return "warning"
        
        return "healthy"
    
    def _generate_health_recommendations(self, overall_health: str, 
                                       health_checks: Dict[str, Any]) -> List[str]:
        """
        Generate health recommendations based on check results.
        
        Args:
            overall_health: Overall health status
            health_checks: Health check results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if overall_health == "critical":
            recommendations.append("Immediate attention required")
        
        for check_name, check_result in health_checks.items():
            if check_result.get("status") == "fail":
                recommendations.append(f"Fix {check_name}: {check_result.get('message', '')}")
            elif check_result.get("status") == "warning":
                recommendations.append(f"Monitor {check_name}: {check_result.get('message', '')}")
        
        return recommendations
    
    async def _get_performance_metrics(self, twin_id: str, start_time: datetime, 
                                     end_time: datetime) -> Dict[str, Any]:
        """
        Get performance metrics for a twin (placeholder implementation).
        
        Args:
            twin_id: Twin ID
            start_time: Start time for metrics
            end_time: End time for metrics
            
        Returns:
            Performance metrics
        """
        # Placeholder implementation - in real system, this would query metrics database
        return {
            "uptime_percentage": 95.5,
            "response_time_avg": 150,
            "response_time_p95": 300,
            "error_rate": 0.02,
            "throughput": 1000,
            "resource_usage": {
                "cpu": 45.2,
                "memory": 67.8,
                "disk": 23.1
            }
        }
    
    def _generate_performance_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate performance summary from metrics.
        
        Args:
            metrics: Performance metrics
            
        Returns:
            Performance summary
        """
        return {
            "overall_performance": "good" if metrics.get("uptime_percentage", 0) > 95 else "poor",
            "key_metrics": {
                "uptime": f"{metrics.get('uptime_percentage', 0):.1f}%",
                "avg_response_time": f"{metrics.get('response_time_avg', 0)}ms",
                "error_rate": f"{metrics.get('error_rate', 0) * 100:.2f}%"
            }
        }
    
    async def _get_twin_events(self, twin_id: str, event_type: str = None, 
                             limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get events for a twin (placeholder implementation).
        
        Args:
            twin_id: Twin ID
            event_type: Event type filter
            limit: Maximum number of events
            
        Returns:
            List of events
        """
        # Placeholder implementation - in real system, this would query events database
        events = [
            {
                "event_id": "evt_001",
                "twin_id": twin_id,
                "event_type": "status_change",
                "message": "Twin status changed to active",
                "severity": "info",
                "timestamp": datetime.now().isoformat(),
                "user": "system"
            }
        ]
        
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]
        
        return events[:limit]
    
    async def _monitoring_loop(self, twin_id: str, callback=None):
        """
        Real-time monitoring loop for a twin.
        
        Args:
            twin_id: Twin ID to monitor
            callback: Optional callback function
        """
        try:
            while twin_id in self.monitoring_tasks and self.monitoring_tasks[twin_id]["active"]:
                # Get current health status
                health_status = await self.get_twin_health(twin_id)
                
                # Call callback if provided
                if callback:
                    try:
                        await callback(twin_id, health_status)
                    except Exception as e:
                        logger.error(f"Callback error for twin {twin_id}: {str(e)}")
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for twin: {twin_id}")
        except Exception as e:
            logger.error(f"Monitoring error for twin {twin_id}: {str(e)}")
        finally:
            if twin_id in self.monitoring_tasks:
                self.monitoring_tasks[twin_id]["active"] = False 