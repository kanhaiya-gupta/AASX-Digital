"""
Twin Operations Service
======================

Service for twin lifecycle operations (start, stop, restart, configure).
Handles twin operational state management.
Now integrated with src/twin_registry core services.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import core Twin Registry services
try:
    from src.modules.twin_registry.core.twin_lifecycle_service import TwinLifecycleService
from src.modules.twin_registry.core.twin_sync_service import TwinSyncService
    print("✅ Twin Registry core services imported successfully")
    CORE_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Twin Registry core services not available: {e}")
    CORE_SERVICES_AVAILABLE = False
    TwinLifecycleService = None
    TwinSyncService = None

logger = logging.getLogger(__name__)

class TwinOperationsService:
    """
    Service for managing twin lifecycle operations.
    Now integrated with src/twin_registry core services.
    Note: Start/stop operations are handled by AASX-ETL integration.
    """
    
    def __init__(self):
        """Initialize the twin operations service with core services."""
        if not CORE_SERVICES_AVAILABLE:
            logger.warning("⚠️ Core services not available - using fallback mode")
            self.lifecycle_service = None
            self.sync_service = None
            return
        
        try:
            # Initialize core services from src/twin_registry
            self.lifecycle_service = TwinLifecycleService()
            self.sync_service = TwinSyncService()
            
            logger.info("✅ Twin Operations Service initialized with core services")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize core services: {e}")
            # Fallback to None if initialization fails
            self.lifecycle_service = None
            self.sync_service = None
    
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
    
    # ==================== DEPRECATED METHODS (Moved to AASX-ETL) ====================
    
    # Note: All twin start/stop/restart operations are now handled by AASX-ETL module
    # These methods have been completely removed to avoid confusion
    
    async def configure_twin(self, twin_id: str, config_data: Dict[str, Any], 
                           user: str = "system") -> Dict[str, Any]:
        """
        DEPRECATED: Twin configuration operations are now handled by AASX-ETL module.
        This method is kept for backward compatibility but will be removed.
        """
        logger.warning("⚠️ configure_twin is deprecated - use AASX-ETL module instead")
        return {
            "success": False,
            "message": "Twin configuration operations are now handled by AASX-ETL module. Use the AASX-ETL page for twin operations.",
            "deprecated": True,
            "redirect_to": "aasx-etl"
        }
    
    async def bulk_operations(self, twin_ids: List[str], operation: str, 
                            user: str = "system") -> Dict[str, Any]:
        """
        DEPRECATED: Bulk twin operations are now handled by AASX-ETL module.
        This method is kept for backward compatibility but will be removed.
        """
        logger.warning("⚠️ bulk_operations is deprecated - use AASX-ETL module instead")
        return {
            "success": False,
            "message": "Bulk twin operations are now handled by AASX-ETL module. Use the AASX-ETL page for twin operations.",
            "deprecated": True,
            "redirect_to": "aasx-etl"
        }
    
    async def get_twin_operations_history(self, twin_id: str, 
                                        limit: int = 50) -> List[Dict[str, Any]]:
        """
        DEPRECATED: Twin operations history is now handled by AASX-ETL module.
        This method is kept for backward compatibility but will be removed.
        """
        logger.warning("⚠️ get_twin_operations_history is deprecated - use AASX-ETL module instead")
        return []
    
    def _log_operation(self, twin_id: str, operation: str, user: str, 
                      status: str, error_message: str = None):
        """
        DEPRECATED: Operation logging is now handled by AASX-ETL module.
        This method is kept for backward compatibility but will be removed.
        """
        logger.warning("⚠️ _log_operation is deprecated - use AASX-ETL module instead")
        pass 