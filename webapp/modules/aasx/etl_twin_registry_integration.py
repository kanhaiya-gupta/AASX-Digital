"""
ETL Twin Registry Integration
Automatically populates the twin registry when ETL jobs complete
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone
import json

from src.twin_registry.populator.twin_registry_populator import TwinRegistryPopulator
from src.twin_registry.events.event_bus import EventBus
from src.twin_registry.events.event_types import create_etl_completion_event
from src.twin_registry.integration.etl_integration import ETLIntegration, ETLIntegrationConfig

logger = logging.getLogger(__name__)

class ETLTwinRegistryIntegration:
    """Integration between ETL pipeline and Twin Registry Population"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("data/aasx_database.db")
        self.populator = TwinRegistryPopulator(self.db_path)
        self.event_bus = EventBus()
        self.etl_integration = ETLIntegration(
            self.event_bus,
            ETLIntegrationConfig(
                database_path=self.db_path,
                polling_interval=5.0,
                max_polling_attempts=100
            )
        )
        self.is_active = False
        
    async def start(self):
        """Start the ETL integration monitoring"""
        try:
            logger.info("🚀 Starting ETL Twin Registry Integration...")
            
            # Start the event bus
            await self.event_bus.start()
            
            # Start ETL integration monitoring
            await self.etl_integration.start()
            
            # Register event handlers
            self._register_event_handlers()
            
            self.is_active = True
            logger.info("✅ ETL Twin Registry Integration started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start ETL Twin Registry Integration: {e}")
            raise
    
    async def stop(self):
        """Stop the ETL integration monitoring"""
        try:
            logger.info("🛑 Stopping ETL Twin Registry Integration...")
            
            self.is_active = False
            
            # Stop ETL integration
            await self.etl_integration.stop()
            
            # Stop event bus
            await self.event_bus.stop()
            
            logger.info("✅ ETL Twin Registry Integration stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping ETL Twin Registry Integration: {e}")
    
    def _register_event_handlers(self):
        """Register event handlers for ETL events"""
        try:
            # Register ETL completion handler
            self.event_bus.subscribe(
                "etl_completion_event",
                self._handle_etl_completion
            )
            
            # Register ETL failure handler
            self.event_bus.subscribe(
                "etl_failure_event", 
                self._handle_etl_failure
            )
            
            logger.info("✅ Event handlers registered successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to register event handlers: {e}")
    
    async def _handle_etl_completion(self, event_data: Dict[str, Any]):
        """Handle ETL completion events"""
        try:
            logger.info(f"🎯 Processing ETL completion event: {event_data.get('job_id', 'unknown')}")
            
            job_id = event_data.get('job_id')
            if not job_id:
                logger.warning("⚠️ ETL completion event missing job_id")
                return
            
            # Extract ETL data from event
            etl_data = {
                'job_id': job_id,
                'status': 'completed',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'input_files': event_data.get('input_files', []),
                'output_files': event_data.get('output_files', []),
                'processing_time': event_data.get('processing_time'),
                'job_type': event_data.get('job_type', 'extraction'),
                'user_id': event_data.get('user_id'),
                'org_id': event_data.get('org_id'),
                'project_id': event_data.get('project_id'),
                'use_case_id': event_data.get('use_case_id'),
                'output_directory': event_data.get('output_directory'),
                'formats_processed': event_data.get('formats_processed', []),
                'failed_formats': event_data.get('failed_formats', []),
                'documents_extracted': event_data.get('documents_extracted', 0),
                'quality_score': event_data.get('quality_score', 0.0)
            }
            
            # Trigger twin registry population
            population_result = await self.populator.populate_from_etl(etl_data)
            
            if population_result.get('status') == 'success':
                logger.info(f"✅ Twin registry populated successfully for ETL job {job_id}")
            else:
                logger.warning(f"⚠️ Twin registry population failed for ETL job {job_id}: {population_result.get('error')}")
            
        except Exception as e:
            logger.error(f"❌ Error handling ETL completion event: {e}")
    
    async def _handle_etl_failure(self, event_data: Dict[str, Any]):
        """Handle ETL failure events"""
        try:
            logger.info(f"⚠️ Processing ETL failure event: {event_data.get('job_id', 'unknown')}")
            
            job_id = event_data.get('job_id')
            if not job_id:
                logger.warning("⚠️ ETL failure event missing job_id")
                return
            
            # Extract ETL failure data
            etl_data = {
                'job_id': job_id,
                'status': 'failed',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error_message': event_data.get('error_message', 'Unknown error'),
                'input_files': event_data.get('input_files', []),
                'job_type': event_data.get('job_type', 'extraction'),
                'user_id': event_data.get('user_id'),
                'org_id': event_data.get('org_id'),
                'project_id': event_data.get('project_id'),
                'use_case_id': event_data.get('use_case_id')
            }
            
            # Update twin registry with failure status
            await self.populator.update_etl_status(job_id, 'failed', etl_data)
            
            logger.info(f"✅ Twin registry updated with failure status for ETL job {job_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling ETL failure event: {e}")
    
    async def manually_trigger_population(self, job_id: str) -> Dict[str, Any]:
        """Manually trigger twin registry population for a specific ETL job"""
        try:
            logger.info(f"🔧 Manually triggering twin registry population for ETL job {job_id}")
            
            # Get ETL job data from the database
            etl_data = await self._get_etl_job_data(job_id)
            
            if not etl_data:
                return {
                    'status': 'error',
                    'message': f'ETL job {job_id} not found'
                }
            
            # Trigger population
            result = await self.populator.populate_from_etl(etl_data)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error manually triggering population: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def _get_etl_job_data(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get ETL job data from the database"""
        try:
            # This would query the aasx_processing table to get job details
            # For now, return a basic structure - you can enhance this based on your actual database schema
            
            # Import the processing service to get job data
            from src.aasx.services.aasx_processing_service import AASXProcessingService
            from src.shared.database.connection_manager import DatabaseConnectionManager
            from src.shared.database.base_manager import BaseDatabaseManager
            
            connection_manager = DatabaseConnectionManager(self.db_path)
            db_manager = BaseDatabaseManager(connection_manager)
            processing_service = AASXProcessingService(db_manager)
            
            # Get job details
            job_info = processing_service.get_job_by_id(job_id)
            
            if not job_info:
                return None
            
            # Convert to the format expected by the populator
            etl_data = {
                'job_id': job_id,
                'status': job_info.get('status', 'unknown'),
                'timestamp': job_info.get('created_at'),
                'input_files': job_info.get('input_files', []),
                'output_files': job_info.get('output_files', []),
                'processing_time': job_info.get('processing_time'),
                'job_type': job_info.get('job_type', 'extraction'),
                'user_id': job_info.get('processed_by'),
                'org_id': job_info.get('org_id'),
                'project_id': job_info.get('project_id'),
                'use_case_id': job_info.get('use_case_id'),
                'output_directory': job_info.get('output_directory'),
                'formats_processed': job_info.get('formats_processed', []),
                'failed_formats': job_info.get('failed_formats', []),
                'documents_extracted': job_info.get('documents_extracted', 0),
                'quality_score': job_info.get('quality_score', 0.0)
            }
            
            return etl_data
            
        except Exception as e:
            logger.error(f"❌ Error getting ETL job data: {e}")
            return None
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get the current status of the ETL integration"""
        return {
            'is_active': self.is_active,
            'event_bus_status': self.event_bus.get_stats(),
            'etl_integration_status': self.etl_integration.health_check(),
            'populator_status': 'active' if self.populator else 'inactive',
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the integration"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'components': {}
            }
            
            # Check event bus health
            try:
                event_bus_stats = self.event_bus.get_stats()
                health_status['components']['event_bus'] = {
                    'status': 'healthy',
                    'subscription_count': event_bus_stats.get('subscription_count', 0),
                    'event_count': event_bus_stats.get('event_count', 0)
                }
            except Exception as e:
                health_status['components']['event_bus'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'unhealthy'
            
            # Check ETL integration health
            try:
                etl_health = await self.etl_integration.health_check()
                health_status['components']['etl_integration'] = {
                    'status': 'healthy' if etl_health.get('is_active') else 'unhealthy',
                    'details': etl_health
                }
                if not etl_health.get('is_active'):
                    health_status['status'] = 'unhealthy'
            except Exception as e:
                health_status['components']['etl_integration'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'unhealthy'
            
            # Check populator health
            try:
                if self.populator:
                    health_status['components']['populator'] = {
                        'status': 'healthy',
                        'version': getattr(self.populator, '__version__', 'unknown')
                    }
                else:
                    health_status['components']['populator'] = {
                        'status': 'unhealthy',
                        'error': 'Populator not initialized'
                    }
                    health_status['status'] = 'unhealthy'
            except Exception as e:
                health_status['components']['populator'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'unhealthy'
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

# Global instance for easy access
etl_twin_registry_integration = ETLTwinRegistryIntegration()

async def start_etl_integration():
    """Start the ETL twin registry integration"""
    await etl_twin_registry_integration.start()

async def stop_etl_integration():
    """Stop the ETL twin registry integration"""
    await etl_twin_registry_integration.stop()

def get_etl_integration():
    """Get the global ETL twin registry integration instance"""
    return etl_twin_registry_integration
