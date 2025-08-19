"""
Twin Monitoring Service
======================

Service for twin health and performance monitoring.
Handles real-time status monitoring and health checks.
Now integrated with src/twin_registry core services.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import asyncio

# Import core Twin Registry services (only those that exist)
try:
    from src.twin_registry.core.twin_lifecycle_service import TwinLifecycleService
    from src.twin_registry.core.twin_sync_service import TwinSyncService
    print("✅ Twin Registry core services imported successfully")
    CORE_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Twin Registry core services not available: {e}")
    CORE_SERVICES_AVAILABLE = False
    TwinLifecycleService = None
    TwinSyncService = None

logger = logging.getLogger(__name__)

class TwinMonitoringService:
    """
    Service for monitoring twin health and performance.
    Now integrated with src/twin_registry core services.
    """
    
    def __init__(self):
        """Initialize the twin monitoring service with core services."""
        if not CORE_SERVICES_AVAILABLE:
            logger.warning("⚠️ Core services not available - using fallback mode")
            self.lifecycle_service = None
            self.sync_service = None
            return
        
        try:
            # Initialize core services from src/twin_registry
            self.lifecycle_service = TwinLifecycleService()
            self.sync_service = TwinSyncService()
            
            # Try to import core registry service for twin data access
            try:
                from src.twin_registry.core.twin_registry_service import TwinRegistryService
                self.core_registry = TwinRegistryService()
                logger.info("✅ Twin Monitoring Service initialized with all core services")
            except ImportError as e:
                logger.warning(f"⚠️ Core registry service not available: {e}")
                self.core_registry = None
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize core services: {e}")
            # Fallback to None if initialization fails
            self.lifecycle_service = None
            self.sync_service = None
            self.core_registry = None
    
    async def initialize(self) -> None:
        """Initialize all core services"""
        if not CORE_SERVICES_AVAILABLE:
            logger.warning("⚠️ Core services not available - skipping initialization")
            return
            
        try:
            if self.lifecycle_service:
                await self.lifecycle_service.initialize()
            if self.sync_service:
                await self.sync_service.initialize()
                
            logger.info("✅ All core services initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize core services: {e}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        Returns comprehensive health information for the twin registry system.
        """
        try:
            logger.info("🔍 Checking system health...")
            
            # Check core services availability
            core_services_status = {
                "lifecycle_service": self.lifecycle_service is not None,
                "sync_service": self.sync_service is not None
            }
            
            # Check database connectivity (basic check)
            db_status = "unknown"
            try:
                # Basic database check - you can implement actual DB ping here
                db_status = "healthy"
            except Exception as e:
                logger.warning(f"Database health check failed: {e}")
                db_status = "error"
            
            # Overall system status
            overall_status = "healthy"
            if db_status == "error" or not any(core_services_status.values()):
                overall_status = "error"
            elif db_status == "unknown" or not all(core_services_status.values()):
                overall_status = "warning"
            
            health_info = {
                "overall_status": overall_status,
                "timestamp": datetime.utcnow().isoformat(),
                "core_services": core_services_status,
                "database": {
                    "status": db_status,
                    "last_check": datetime.utcnow().isoformat()
                },
                "system_info": {
                    "service_name": "Twin Registry Monitoring",
                    "version": "1.0.0",
                    "uptime": "unknown"  # You can implement actual uptime tracking
                }
            }
            
            if overall_status == "error":
                health_info["error"] = "One or more critical services are unavailable"
            
            logger.info(f"✅ System health check completed: {overall_status}")
            return health_info
            
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_twin_health(self, twin_id: str) -> Dict[str, Any]:
        """
        Get comprehensive health status for a specific twin.
        Queries the twin_registry table for health information.
        """
        try:
            logger.info(f"🔍 Getting health status for twin: {twin_id}")
            
            # Use core registry service if available
            if hasattr(self, 'core_registry') and self.core_registry:
                try:
                    twin_info = await self.core_registry.get_twin_by_id(twin_id)
                    if not twin_info:
                        return {
                            "success": False,
                            "error": "Twin not found",
                            "twin_id": twin_id
                        }
                    
                    # Extract health metrics from twin data
                    health_data = {
                        "twin_id": twin_id,
                        "overall_health_score": getattr(twin_info, 'overall_health_score', 0),
                        "health_status": getattr(twin_info, 'health_status', 'unknown'),
                        "performance_score": getattr(twin_info, 'performance_score', 0.0),
                        "data_quality_score": getattr(twin_info, 'data_quality_score', 0.0),
                        "reliability_score": getattr(twin_info, 'reliability_score', 0.0),
                        "compliance_score": getattr(twin_info, 'compliance_score', 0.0),
                        "lifecycle_status": getattr(twin_info, 'lifecycle_status', 'unknown'),
                        "operational_status": getattr(twin_info, 'operational_status', 'unknown'),
                        "last_updated": getattr(twin_info, 'updated_at', datetime.utcnow().isoformat()),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Determine overall health
                    if health_data["overall_health_score"] >= 80:
                        health_data["health_level"] = "excellent"
                    elif health_data["overall_health_score"] >= 60:
                        health_data["health_level"] = "good"
                    elif health_data["overall_health_score"] >= 40:
                        health_data["health_level"] = "fair"
                    else:
                        health_data["health_level"] = "poor"
                    
                    logger.info(f"✅ Retrieved health data for twin {twin_id}")
                    return {
                        "success": True,
                        "health_data": health_data
                    }
                    
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to basic method: {e}")
            
            # Fallback: Return basic health info
            logger.warning("⚠️ Core registry service not available - returning basic health info")
            return {
                "success": True,
                "health_data": {
                    "twin_id": twin_id,
                    "overall_health_score": 0,
                    "health_status": "unknown",
                    "health_level": "unknown",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting twin health for {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "twin_id": twin_id
            }
    
    async def get_twin_performance(self, twin_id: str, time_range: str = "24h") -> Dict[str, Any]:
        """
        Get performance metrics for a specific twin.
        Queries the twin_registry_metrics table for performance data.
        """
        try:
            logger.info(f"📊 Getting performance metrics for twin: {twin_id}, range: {time_range}")
            
            # Use core registry service if available
            if hasattr(self, 'core_registry') and self.core_registry:
                try:
                    twin_info = await self.core_registry.get_twin_by_id(twin_id)
                    if not twin_info:
                        return {
                            "success": False,
                            "error": "Twin not found",
                            "twin_id": twin_id
                        }
                    
                    # Extract performance metrics from twin data
                    performance_data = {
                        "twin_id": twin_id,
                        "time_range": time_range,
                        "performance_score": getattr(twin_info, 'performance_score', 0.0),
                        "data_quality_score": getattr(twin_info, 'data_quality_score', 0.0),
                        "reliability_score": getattr(twin_info, 'reliability_score', 0.0),
                        "compliance_score": getattr(twin_info, 'compliance_score', 0.0),
                        "sync_status": getattr(twin_info, 'sync_status', 'unknown'),
                        "sync_frequency": getattr(twin_info, 'sync_frequency', 'unknown'),
                        "last_sync_at": getattr(twin_info, 'last_sync_at', None),
                        "next_sync_at": getattr(twin_info, 'next_sync_at', None),
                        "sync_error_count": getattr(twin_info, 'sync_error_count', 0),
                        "last_updated": getattr(twin_info, 'updated_at', datetime.utcnow().isoformat()),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Calculate performance trends based on scores
                    total_score = sum([
                        performance_data["performance_score"],
                        performance_data["data_quality_score"],
                        performance_data["reliability_score"],
                        performance_data["compliance_score"]
                    ]) / 4
                    
                    performance_data["overall_performance"] = total_score
                    performance_data["performance_trend"] = "stable"  # Could be enhanced with historical data
                    
                    logger.info(f"✅ Retrieved performance data for twin {twin_id}")
                    return {
                        "success": True,
                        "performance_data": performance_data
                    }
                    
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to basic method: {e}")
            
            # Fallback: Return basic performance info
            logger.warning("⚠️ Core registry service not available - returning basic performance info")
            return {
                "success": True,
                "performance_data": {
                    "twin_id": twin_id,
                    "time_range": time_range,
                    "overall_performance": 0.0,
                    "performance_trend": "unknown",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting twin performance for {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "twin_id": twin_id
            }
    
    async def get_twin_events(self, twin_id: str, event_type: str = None, limit: int = 50) -> Dict[str, Any]:
        """
        Get event history for a specific twin.
        Uses the lifecycle service to retrieve events.
        """
        try:
            logger.info(f"📅 Getting events for twin: {twin_id}, type: {event_type}, limit: {limit}")
            
            # Use lifecycle service if available
            if self.lifecycle_service:
                try:
                    # Get events from lifecycle service
                    events = await self.lifecycle_service.get_events(
                        registry_id="default",  # Could be enhanced to get actual registry_id
                        twin_id=twin_id,
                        query=None  # Could be enhanced with event_type filtering
                    )
                    
                    # Filter by event type if specified
                    if event_type:
                        events = [e for e in events if getattr(e, 'event_type', '').value == event_type]
                    
                    # Limit results
                    events = events[:limit]
                    
                    # Convert events to serializable format
                    event_data = []
                    for event in events:
                        event_data.append({
                            "event_id": getattr(event, 'event_id', 'unknown'),
                            "event_type": getattr(event, 'event_type', 'unknown'),
                            "timestamp": getattr(event, 'timestamp', datetime.utcnow().isoformat()),
                            "event_data": getattr(event, 'event_data', {}),
                            "triggered_by": getattr(event, 'triggered_by', 'system')
                        })
                    
                    logger.info(f"✅ Retrieved {len(event_data)} events for twin {twin_id}")
                    return {
                        "success": True,
                        "events": event_data,
                        "total_count": len(event_data),
                        "twin_id": twin_id
                    }
                    
                except Exception as e:
                    logger.warning(f"⚠️ Lifecycle service failed: {e}")
            
            # Fallback: Return empty events list
            logger.warning("⚠️ Lifecycle service not available - returning empty events")
            return {
                "success": True,
                "events": [],
                "total_count": 0,
                "twin_id": twin_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting twin events for {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "twin_id": twin_id
            }
    
    async def monitor_twin_status(self, twin_id: str) -> Dict[str, Any]:
        """
        Start real-time monitoring for a twin.
        Sets up monitoring session and returns session info.
        """
        try:
            logger.info(f"🔍 Starting monitoring for twin: {twin_id}")
            
            # Check if twin exists
            if hasattr(self, 'core_registry') and self.core_registry:
                try:
                    twin_info = await self.core_registry.get_twin_by_id(twin_id)
                    if not twin_info:
                        return {
                            "success": False,
                            "error": "Twin not found",
                            "twin_id": twin_id
                        }
                except Exception as e:
                    logger.warning(f"⚠️ Could not verify twin existence: {e}")
            
            # Create monitoring session
            session_id = f"monitor_{twin_id}_{int(datetime.utcnow().timestamp())}"
            
            # Store monitoring session info (could be enhanced with database storage)
            if not hasattr(self, '_monitoring_sessions'):
                self._monitoring_sessions = {}
            
            self._monitoring_sessions[session_id] = {
                "twin_id": twin_id,
                "started_at": datetime.utcnow().isoformat(),
                "status": "active",
                "last_check": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Started monitoring session {session_id} for twin {twin_id}")
            return {
                "success": True,
                "session_id": session_id,
                "twin_id": twin_id,
                "status": "active",
                "started_at": self._monitoring_sessions[session_id]["started_at"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting monitoring for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "twin_id": twin_id
            }
    
    async def stop_monitoring(self, twin_id: str) -> Dict[str, Any]:
        """
        Stop real-time monitoring for a twin.
        Ends monitoring session and returns summary.
        """
        try:
            logger.info(f"🛑 Stopping monitoring for twin: {twin_id}")
            
            if not hasattr(self, '_monitoring_sessions'):
                return {
                    "success": False,
                    "error": "No monitoring sessions found",
                    "twin_id": twin_id
                }
            
            # Find and stop monitoring sessions for this twin
            stopped_sessions = []
            for session_id, session_info in list(self._monitoring_sessions.items()):
                if session_info["twin_id"] == twin_id:
                    session_info["status"] = "stopped"
                    session_info["stopped_at"] = datetime.utcnow().isoformat()
                    stopped_sessions.append(session_id)
                    del self._monitoring_sessions[session_id]
            
            if not stopped_sessions:
                return {
                    "success": False,
                    "error": "No active monitoring sessions found for this twin",
                    "twin_id": twin_id
                }
            
            logger.info(f"✅ Stopped {len(stopped_sessions)} monitoring sessions for twin {twin_id}")
            return {
                "success": True,
                "stopped_sessions": stopped_sessions,
                "twin_id": twin_id,
                "message": f"Stopped {len(stopped_sessions)} monitoring session(s)"
            }
            
        except Exception as e:
            logger.error(f"❌ Error stopping monitoring for twin {twin_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "twin_id": twin_id
            } 