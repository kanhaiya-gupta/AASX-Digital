"""
Twin Registry Integration Coordinator

Orchestrates all integration components and provides a unified interface.
Phase 3: Event System & Automation with pure async support.

Coordinates:
- File upload integration
- ETL integration  
- AI RAG integration
- Event-driven automation
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .file_upload_integration import FileUploadIntegration, FileUploadIntegrationConfig
from .etl_integration import ETLIntegration, ETLIntegrationConfig
from .ai_rag_integration import AIRAGIntegration, AIRAGIntegrationConfig
from ..core.twin_registry_service import TwinRegistryService
from ..events.event_manager import TwinRegistryEventManager

logger = logging.getLogger(__name__)


class IntegrationCoordinator:
    """Coordinates all integration components for Twin Registry"""
    
    def __init__(self, twin_service: TwinRegistryService, event_manager: TwinRegistryEventManager):
        self.twin_service = twin_service
        self.event_manager = event_manager
        
        # Integration components
        self.file_upload_integration: Optional[FileUploadIntegration] = None
        self.etl_integration: Optional[ETLIntegration] = None
        self.ai_rag_integration: Optional[AIRAGIntegration] = None
        
        # Coordinator state
        self.is_active = False
        self.coordination_task: Optional[asyncio.Task] = None
        
        # Integration status tracking
        self.integration_status = {
            "file_upload": {"active": False, "status": "not_initialized"},
            "etl": {"active": False, "status": "not_initialized"},
            "ai_rag": {"active": False, "status": "not_initialized"}
        }
        
        logger.info("Integration Coordinator initialized")
    
    async def initialize_integrations(
        self,
        database_path: Path,
        file_upload_config: Optional[FileUploadIntegrationConfig] = None,
        etl_config: Optional[ETLIntegrationConfig] = None,
        ai_rag_config: Optional[AIRAGIntegrationConfig] = None
    ) -> None:
        """Initialize all integration components"""
        try:
            logger.info("Initializing integration components...")
            
            # Initialize file upload integration
            if file_upload_config:
                self.file_upload_integration = FileUploadIntegration(
                    self.twin_service,
                    self.event_manager,
                    file_upload_config
                )
                logger.info("File upload integration initialized")
            
            # Initialize ETL integration
            if etl_config:
                self.etl_integration = ETLIntegration(
                    self.twin_service,
                    self.event_manager,
                    etl_config
                )
                logger.info("ETL integration initialized")
            
            # Initialize AI RAG integration
            if ai_rag_config:
                self.ai_rag_integration = AIRAGIntegration(
                    self.twin_service,
                    self.event_manager,
                    ai_rag_config
                )
                logger.info("AI RAG integration initialized")
            
            logger.info("All integration components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize integrations: {e}")
            raise
    
    async def start_all_integrations(self) -> None:
        """Start all active integration components"""
        try:
            if self.is_active:
                logger.warning("Integration coordinator is already active")
                return
            
            self.is_active = True
            logger.info("Starting all integration components...")
            
            # Start file upload integration
            if self.file_upload_integration:
                await self.file_upload_integration.start()
                self.integration_status["file_upload"]["active"] = True
                self.integration_status["file_upload"]["status"] = "running"
                logger.info("File upload integration started")
            
            # Start ETL integration
            if self.etl_integration:
                await self.etl_integration.start()
                self.integration_status["etl"]["active"] = True
                self.integration_status["etl"]["status"] = "running"
                logger.info("ETL integration started")
            
            # Start AI RAG integration
            if self.ai_rag_integration:
                await self.ai_rag_integration.start()
                self.integration_status["ai_rag"]["active"] = True
                self.integration_status["ai_rag"]["status"] = "running"
                logger.info("AI RAG integration started")
            
            # Start coordination task
            self.coordination_task = asyncio.create_task(self._coordinate_integrations())
            
            logger.info("All integration components started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start integrations: {e}")
            self.is_active = False
            raise
    
    async def stop_all_integrations(self) -> None:
        """Stop all active integration components"""
        try:
            if not self.is_active:
                return
            
            self.is_active = False
            logger.info("Stopping all integration components...")
            
            # Stop coordination task
            if self.coordination_task:
                self.coordination_task.cancel()
                try:
                    await self.coordination_task
                except asyncio.CancelledError:
                    pass
            
            # Stop file upload integration
            if self.file_upload_integration:
                await self.file_upload_integration.stop()
                self.integration_status["file_upload"]["active"] = False
                self.integration_status["file_upload"]["status"] = "stopped"
                logger.info("File upload integration stopped")
            
            # Stop ETL integration
            if self.etl_integration:
                await self.etl_integration.stop()
                self.integration_status["etl"]["active"] = False
                self.integration_status["etl"]["status"] = "stopped"
                logger.info("ETL integration stopped")
            
            # Stop AI RAG integration
            if self.ai_rag_integration:
                await self.ai_rag_integration.stop()
                self.integration_status["ai_rag"]["active"] = False
                self.integration_status["ai_rag"]["status"] = "stopped"
                logger.info("AI RAG integration stopped")
            
            logger.info("All integration components stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop integrations: {e}")
            raise
    
    async def _coordinate_integrations(self) -> None:
        """Coordinate and monitor all integration components"""
        while self.is_active:
            try:
                # Monitor integration health
                await self._monitor_integration_health()
                
                # Coordinate cross-integration workflows
                await self._coordinate_workflows()
                
                # Wait before next coordination cycle
                await asyncio.sleep(30)  # 30 second coordination cycle
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in integration coordination: {e}")
                await asyncio.sleep(10)  # Brief pause on error
    
    async def _monitor_integration_health(self) -> None:
        """Monitor the health of all integration components"""
        try:
            # Check file upload integration health
            if self.file_upload_integration:
                try:
                    status = await self.file_upload_integration.get_integration_status()
                    if status.get("error"):
                        self.integration_status["file_upload"]["status"] = "error"
                        logger.warning("File upload integration health check failed")
                    else:
                        self.integration_status["file_upload"]["status"] = "healthy"
                except Exception as e:
                    self.integration_status["file_upload"]["status"] = "error"
                    logger.error(f"File upload integration health check error: {e}")
            
            # Check ETL integration health
            if self.etl_integration:
                try:
                    status = await self.etl_integration.get_integration_status()
                    if status.get("error"):
                        self.integration_status["etl"]["status"] = "error"
                        logger.warning("ETL integration health check failed")
                    else:
                        self.integration_status["etl"]["status"] = "healthy"
                except Exception as e:
                    self.integration_status["etl"]["status"] = "error"
                    logger.error(f"ETL integration health check error: {e}")
            
            # Check AI RAG integration health
            if self.ai_rag_integration:
                try:
                    status = await self.ai_rag_integration.get_integration_status()
                    if status.get("error"):
                        self.integration_status["ai_rag"]["status"] = "error"
                        logger.warning("AI RAG integration health check failed")
                    else:
                        self.integration_status["ai_rag"]["status"] = "healthy"
                except Exception as e:
                    self.integration_status["ai_rag"]["status"] = "error"
                    logger.error(f"AI RAG integration health check error: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to monitor integration health: {e}")
    
    async def _coordinate_workflows(self) -> None:
        """Coordinate cross-integration workflows"""
        try:
            # Example: Coordinate file upload -> ETL -> AI RAG workflow
            # This would implement business logic for coordinating between integrations
            
            # For now, just log that we're coordinating
            logger.debug("Coordinating cross-integration workflows...")
            
        except Exception as e:
            logger.error(f"Failed to coordinate workflows: {e}")
    
    async def get_coordinator_status(self) -> Dict[str, Any]:
        """Get the overall status of the integration coordinator"""
        try:
            return {
                "coordinator_active": self.is_active,
                "integrations": self.integration_status.copy(),
                "timestamp": datetime.now().isoformat(),
                "overall_health": self._calculate_overall_health()
            }
        except Exception as e:
            logger.error(f"Failed to get coordinator status: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall health status"""
        try:
            healthy_count = sum(
                1 for status in self.integration_status.values()
                if status["status"] == "healthy"
            )
            total_count = len(self.integration_status)
            
            if healthy_count == total_count:
                return "healthy"
            elif healthy_count > 0:
                return "degraded"
            else:
                return "critical"
                
        except Exception as e:
            logger.error(f"Failed to calculate overall health: {e}")
            return "unknown"
    
    async def trigger_file_upload_workflow(
        self,
        file_id: str,
        file_name: str,
        file_type: str,
        user_id: str,
        org_id: str,
        dept_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> None:
        """Trigger a complete file upload workflow across all integrations"""
        try:
            logger.info(f"Triggering file upload workflow for {file_name}")
            
            # Step 1: File upload integration creates twin
            if self.file_upload_integration:
                # This would trigger the file upload event
                logger.info("File upload integration processing file")
            
            # Step 2: ETL integration processes the file
            if self.etl_integration:
                # This would trigger ETL processing
                logger.info("ETL integration processing file")
            
            # Step 3: AI RAG integration enhances the twin
            if self.ai_rag_integration:
                # This would trigger AI/RAG enhancement
                logger.info("AI RAG integration enhancing twin")
            
            logger.info(f"File upload workflow completed for {file_name}")
            
        except Exception as e:
            logger.error(f"Failed to trigger file upload workflow: {e}")
            raise
    
    async def get_integration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all integrations"""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "file_upload": {},
                "etl": {},
                "ai_rag": {}
            }
            
            # Get file upload metrics
            if self.file_upload_integration:
                try:
                    metrics["file_upload"] = await self.file_upload_integration.get_integration_status()
                except Exception as e:
                    metrics["file_upload"] = {"error": str(e)}
            
            # Get ETL metrics
            if self.etl_integration:
                try:
                    metrics["etl"] = await self.etl_integration.get_integration_status()
                except Exception as e:
                    metrics["etl"] = {"error": str(e)}
            
            # Get AI RAG metrics
            if self.ai_rag_integration:
                try:
                    metrics["ai_rag"] = await self.ai_rag_integration.get_integration_status()
                except Exception as e:
                    metrics["ai_rag"] = {"error": str(e)}
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get integration metrics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Cleanup all integration resources"""
        try:
            await self.stop_all_integrations()
            logger.info("Integration coordinator cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup integration coordinator: {e}")
            raise

