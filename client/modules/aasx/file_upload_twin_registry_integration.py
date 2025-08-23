"""
File Upload Twin Registry Integration
Automatically populates the twin registry when files are uploaded
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone
import json

from src.twin_registry.populator.twin_registry_populator import TwinRegistryPopulator
from src.twin_registry.events.event_bus import EventBus
from src.twin_registry.events.event_types import create_file_upload_event
from src.twin_registry.integration.file_upload_integration import FileUploadIntegration, FileUploadIntegrationConfig

logger = logging.getLogger(__name__)

class FileUploadTwinRegistryIntegration:
    """Integration between file upload system and Twin Registry Population"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("data/aasx_database.db")
        self.populator = TwinRegistryPopulator(self.db_path)
        self.event_bus = EventBus()
        self.file_upload_integration = FileUploadIntegration(
            self.event_bus,
            FileUploadIntegrationConfig(
                database_path=self.db_path,
                watch_directory=Path("uploads"),  # Directory to watch for new files
                polling_interval=2.0,
                max_polling_attempts=100,
                supported_extensions=['.aasx', '.zip', '.json', '.yaml', '.xml', '.csv']
            )
        )
        self.is_active = False
        
    async def start(self):
        """Start the file upload integration monitoring"""
        try:
            logger.info("🚀 Starting File Upload Twin Registry Integration...")
            
            # Start the event bus
            await self.event_bus.start()
            
            # Start file upload integration monitoring
            await self.file_upload_integration.start()
            
            # Register event handlers
            self._register_event_handlers()
            
            self.is_active = True
            logger.info("✅ File Upload Twin Registry Integration started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start File Upload Twin Registry Integration: {e}")
            raise
    
    async def stop(self):
        """Stop the file upload integration monitoring"""
        try:
            logger.info("🛑 Stopping File Upload Twin Registry Integration...")
            
            self.is_active = False
            
            # Stop file upload integration
            await self.file_upload_integration.stop()
            
            # Stop event bus
            await self.event_bus.stop()
            
            logger.info("✅ File Upload Twin Registry Integration stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping File Upload Twin Registry Integration: {e}")
    
    def _register_event_handlers(self):
        """Register event handlers for file upload events"""
        try:
            # Register file upload handler
            self.event_bus.subscribe(
                "file_upload_event",
                self._handle_file_upload
            )
            
            # Register file processing handler
            self.event_bus.subscribe(
                "file_processing_event", 
                self._handle_file_processing
            )
            
            logger.info("✅ File upload event handlers registered successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to register file upload event handlers: {e}")
    
    async def _handle_file_upload(self, event_data: Dict[str, Any]):
        """Handle file upload events - Phase 1: Basic twin registry entry"""
        try:
            logger.info(f"🎯 Processing file upload event: {event_data.get('upload_id', 'unknown')}")
            
            upload_id = event_data.get('upload_id')
            if not upload_id:
                logger.warning("⚠️ File upload event missing upload_id")
                return
            
            # Extract file upload data
            file_data = {
                'upload_id': upload_id,
                'file_path': event_data.get('file_path', ''),
                'file_name': event_data.get('file_name', ''),
                'file_size': event_data.get('file_size', 0),
                'file_type': event_data.get('file_type', 'unknown'),
                'upload_timestamp': event_data.get('timestamp'),
                'user_id': event_data.get('user_id', 'system'),
                'org_id': event_data.get('org_id'),
                'project_id': event_data.get('project_id'),
                'use_case_id': event_data.get('use_case_id'),
                'upload_status': 'completed',
                'file_hash': event_data.get('file_hash', ''),
                'mime_type': event_data.get('mime_type', ''),
                'upload_source': event_data.get('upload_source', 'manual')
            }
            
            # Trigger Phase 1: Basic twin registry population
            population_result = await self.populator.create_basic_registry_from_upload(file_data)
            
            if population_result.get('status') == 'success':
                logger.info(f"✅ Phase 1: Basic twin registry populated successfully for upload {upload_id}")
            else:
                logger.warning(f"⚠️ Phase 1: Basic twin registry population failed for upload {upload_id}: {population_result.get('error')}")
            
        except Exception as e:
            logger.error(f"❌ Error handling file upload event: {e}")
    
    async def _handle_file_processing(self, event_data: Dict[str, Any]):
        """Handle file processing events - Update twin registry with processing status"""
        try:
            logger.info(f"🔄 Processing file processing event: {event_data.get('upload_id', 'unknown')}")
            
            upload_id = event_data.get('upload_id')
            if not upload_id:
                logger.warning("⚠️ File processing event missing upload_id")
                return
            
            # Extract file processing data
            processing_data = {
                'upload_id': upload_id,
                'processing_status': event_data.get('processing_status', 'unknown'),
                'processing_timestamp': event_data.get('timestamp'),
                'processing_result': event_data.get('processing_result', {}),
                'error_message': event_data.get('error_message'),
                'processing_time': event_data.get('processing_time'),
                'output_files': event_data.get('output_files', []),
                'metadata_extracted': event_data.get('metadata_extracted', {})
            }
            
            # Update twin registry with processing status
            await self.populator.update_upload_status(upload_id, processing_data)
            
            logger.info(f"✅ Twin registry updated with processing status for upload {upload_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling file processing event: {e}")
    
    async def manually_trigger_upload_population(self, upload_id: str) -> Dict[str, Any]:
        """Manually trigger twin registry population for a specific file upload"""
        try:
            logger.info(f"🔧 Manually triggering twin registry population for upload {upload_id}")
            
            # Get file upload data from the database
            upload_data = await self._get_file_upload_data(upload_id)
            
            if not upload_data:
                return {
                    'status': 'error',
                    'message': f'File upload {upload_id} not found'
                }
            
            # Trigger Phase 1 population
            result = await self.populator.create_basic_registry_from_upload(upload_data)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error manually triggering upload population: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def _get_file_upload_data(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Get file upload data from the database"""
        try:
            # Import the file repository to get upload details
            from src.shared.repositories.file_repository import FileRepository
            from src.shared.database.connection_manager import DatabaseConnectionManager
            from src.shared.database.base_manager import BaseDatabaseManager
            
            connection_manager = DatabaseConnectionManager(self.db_path)
            db_manager = BaseDatabaseManager(connection_manager)
            file_repo = FileRepository(db_manager)
            
            # Get file info by upload ID (you may need to adjust this based on your schema)
            file_info = file_repo.get_by_id(upload_id)
            
            if not file_info:
                return None
            
            # Convert to the format expected by the populator
            upload_data = {
                'upload_id': upload_id,
                'file_path': str(file_info.filepath) if hasattr(file_info, 'filepath') else '',
                'file_name': file_info.filename if hasattr(file_info, 'filename') else '',
                'file_size': getattr(file_info, 'file_size', 0),
                'file_type': file_info.file_type if hasattr(file_info, 'file_type') else 'unknown',
                'upload_timestamp': getattr(file_info, 'created_at', datetime.now(timezone.utc).isoformat()),
                'user_id': getattr(file_info, 'user_id', 'system'),
                'org_id': getattr(file_info, 'org_id'),
                'project_id': getattr(file_info, 'project_id'),
                'use_case_id': getattr(file_info, 'use_case_id'),
                'upload_status': 'completed',
                'file_hash': getattr(file_info, 'file_hash', ''),
                'mime_type': getattr(file_info, 'mime_type', ''),
                'upload_source': 'manual'
            }
            
            return upload_data
            
        except Exception as e:
            logger.error(f"❌ Error getting file upload data: {e}")
            return None
    
    async def process_existing_uploads(self) -> Dict[str, Any]:
        """Process all existing file uploads that haven't been registered in twin registry"""
        try:
            logger.info("🔄 Processing existing file uploads for twin registry population...")
            
            # Import repositories
            from src.shared.repositories.file_repository import FileRepository
            from src.shared.database.connection_manager import DatabaseConnectionManager
            from src.shared.database.base_manager import BaseDatabaseManager
            
            connection_manager = DatabaseConnectionManager(self.db_path)
            db_manager = BaseDatabaseManager(connection_manager)
            file_repo = FileRepository(db_manager)
            
            # Get all files (you may need to adjust this query based on your schema)
            all_files = file_repo.get_all()
            
            processed_count = 0
            error_count = 0
            
            for file_info in all_files:
                try:
                    # Check if this file is already in twin registry
                    # This is a simplified check - you may need to implement proper duplicate detection
                    
                    # Create upload data
                    upload_data = {
                        'upload_id': str(file_info.id),
                        'file_path': str(file_info.filepath) if hasattr(file_info, 'filepath') else '',
                        'file_name': file_info.filename if hasattr(file_info, 'filename') else '',
                        'file_size': getattr(file_info, 'file_size', 0),
                        'file_type': file_info.file_type if hasattr(file_info, 'file_type') else 'unknown',
                        'upload_timestamp': getattr(file_info, 'created_at', datetime.now(timezone.utc).isoformat()),
                        'user_id': getattr(file_info, 'user_id', 'system'),
                        'org_id': getattr(file_info, 'org_id'),
                        'project_id': getattr(file_info, 'project_id'),
                        'use_case_id': getattr(file_info, 'use_case_id'),
                        'upload_status': 'completed',
                        'file_hash': getattr(file_info, 'file_hash', ''),
                        'mime_type': getattr(file_info, 'mime_type', ''),
                        'upload_source': 'manual'
                    }
                    
                    # Trigger Phase 1 population
                    result = await self.populator.create_basic_registry_from_upload(upload_data)
                    
                    if result.get('status') == 'success':
                        processed_count += 1
                        logger.info(f"✅ Processed existing upload: {file_info.filename}")
                    else:
                        error_count += 1
                        logger.warning(f"⚠️ Failed to process existing upload: {file_info.filename}")
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Error processing existing upload {getattr(file_info, 'filename', 'unknown')}: {e}")
            
            return {
                'status': 'success',
                'processed_count': processed_count,
                'error_count': error_count,
                'total_files': len(all_files)
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing existing uploads: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get the current status of the file upload integration"""
        return {
            'is_active': self.is_active,
            'event_bus_status': self.event_bus.get_stats(),
            'file_upload_integration_status': self.file_upload_integration.health_check(),
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
            
            # Check file upload integration health
            try:
                upload_health = await self.file_upload_integration.health_check()
                health_status['components']['file_upload_integration'] = {
                    'status': 'healthy' if upload_health.get('is_active') else 'unhealthy',
                    'details': upload_health
                }
                if not upload_health.get('is_active'):
                    health_status['status'] = 'unhealthy'
            except Exception as e:
                health_status['components']['file_upload_integration'] = {
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
file_upload_twin_registry_integration = FileUploadTwinRegistryIntegration()

async def start_file_upload_integration():
    """Start the file upload twin registry integration"""
    await file_upload_twin_registry_integration.start()

async def stop_file_upload_integration():
    """Stop the file upload twin registry integration"""
    await file_upload_twin_registry_integration.stop()

def get_file_upload_integration():
    """Get the global file upload twin registry integration instance"""
    return file_upload_twin_registry_integration
