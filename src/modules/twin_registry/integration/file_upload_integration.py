"""
File Upload Integration for Twin Registry Population
Provides hooks and integration points with the file upload system
Phase 3: Event System & Automation with pure async support
"""

import logging
import asyncio
import sqlite3
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass
import hashlib
import mimetypes

from ..events.event_manager import TwinRegistryEventManager, EventType, EventPriority, TwinRegistryEvent
from ..core.twin_registry_service import TwinRegistryService

logger = logging.getLogger(__name__)


@dataclass
class FileUploadInfo:
    """File upload information"""
    upload_id: str
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    upload_time: datetime
    user_id: str
    org_id: str
    dept_id: Optional[str] = None
    project_id: Optional[str] = None
    upload_status: str = "pending"
    processing_status: str = "pending"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FileUploadIntegrationConfig:
    """File upload integration configuration"""
    database_path: Path
    watch_directory: Optional[Path] = None
    file_patterns: List[str] = None
    polling_interval: int = 10  # seconds
    upload_delay: int = 5  # seconds after upload
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    supported_extensions: List[str] = None
    enable_auto_population: bool = True
    population_delay: int = 10  # seconds after upload
    batch_size: int = 20
    cleanup_old_uploads: bool = True
    max_upload_age: int = 86400 * 30  # 30 days in seconds
    
    def __post_init__(self):
        if self.file_patterns is None:
            self.file_patterns = ["*.aasx", "*.xml", "*.json", "*.csv"]
        if self.supported_extensions is None:
            self.supported_extensions = [".aasx", ".xml", ".json", ".csv", ".txt"]


class FileUploadIntegration:
    """File upload system integration for twin registry population - Pure async implementation"""
    
    def __init__(
        self,
        twin_service: TwinRegistryService,
        event_manager: TwinRegistryEventManager,
        config: FileUploadIntegrationConfig
    ):
        self.twin_service = twin_service
        self.event_manager = event_manager
        self.config = config
        self.db_path = config.database_path
        
        # Integration state
        self.is_active = False
        self.polling_task: Optional[asyncio.Task] = None
        self.file_watcher_task: Optional[asyncio.Task] = None
        self.registered_callbacks: List[Callable] = []
        
        # File upload tracking
        self.file_uploads: Dict[str, FileUploadInfo] = {}
        self.pending_uploads: List[str] = []
        self.processed_uploads: List[str] = []
        self.failed_uploads: List[str] = []
        
        # Statistics
        self.stats = {
            "total_uploads_monitored": 0,
            "successful_populations": 0,
            "failed_populations": 0,
            "last_population_time": None,
            "average_population_time": 0.0,
            "total_file_size_processed": 0
        }
    
    async def start(self) -> None:
        """Start file upload integration monitoring"""
        try:
            if self.is_active:
                logger.warning("File upload integration is already active")
                return
            
            self.is_active = True
            
            # Start polling task
            self.polling_task = asyncio.create_task(self._poll_file_uploads())
            
            # Start file watcher if directory is specified
            if self.config.watch_directory:
                self.file_watcher_task = asyncio.create_task(self._watch_directory())
            
            logger.info("File upload integration started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start file upload integration: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop file upload integration monitoring"""
        try:
            if not self.is_active:
                return
            
            self.is_active = False
            
            if self.polling_task:
                self.polling_task.cancel()
                try:
                    await self.polling_task
                except asyncio.CancelledError:
                    pass
            
            if self.file_watcher_task:
                self.file_watcher_task.cancel()
                try:
                    await self.file_watcher_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("File upload integration stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop file upload integration: {e}")
            raise
    
    async def register_file_upload(self, upload_info: FileUploadInfo) -> None:
        """Register a new file upload for monitoring"""
        try:
            self.file_uploads[upload_info.upload_id] = upload_info
            self.pending_uploads.append(upload_info.upload_id)
            self.stats["total_uploads_monitored"] += 1
            
            logger.info(f"Registered file upload: {upload_info.filename}")
            
            # Trigger file upload event for automatic twin creation
            await self._trigger_file_upload_event(upload_info)
            
        except Exception as e:
            logger.error(f"Failed to register file upload {upload_info.upload_id}: {e}")
            raise
    
    async def _trigger_file_upload_event(self, upload_info: FileUploadInfo) -> None:
        """Trigger file upload event for automatic twin creation"""
        try:
            # Determine file type from extension
            file_type = Path(upload_info.filename).suffix.lower().lstrip('.')
            
            # Trigger the event using the event manager
            await self.event_manager.emit_event(
                TwinRegistryEvent(
                    event_type=EventType.FILE_UPLOAD,
                    priority=EventPriority.NORMAL,
                    timestamp=datetime.now(),
                    data={
                        'file_id': upload_info.upload_id,
                        'file_name': upload_info.filename,
                        'file_type': file_type,
                        'project_id': upload_info.project_id,
                        'processed_by': upload_info.user_id,
                        'org_id': upload_info.org_id,
                        'dept_id': upload_info.dept_id,
                        'file_size': upload_info.file_size,
                        'mime_type': upload_info.mime_type
                    },
                    source="file_upload_integration",
                    correlation_id=upload_info.upload_id
                )
            )
            
            logger.info(f"Triggered file upload event for {upload_info.filename}")
            
        except Exception as e:
            logger.error(f"Failed to trigger file upload event for {upload_info.filename}: {e}")
    
    async def update_upload_status(self, upload_id: str, status: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update the status of a file upload"""
        try:
            if upload_id not in self.file_uploads:
                logger.warning(f"File upload {upload_id} not found")
                return
            
            upload = self.file_uploads[upload_id]
            upload.upload_status = status
            
            if status == "completed":
                if upload_id in self.pending_uploads:
                    self.pending_uploads.remove(upload_id)
                self.processed_uploads.append(upload_id)
                
            elif status == "failed":
                if upload_id in self.pending_uploads:
                    self.pending_uploads.remove(upload_id)
                self.failed_uploads.append(upload_id)
            
            if metadata:
                upload.metadata.update(metadata)
            
            logger.info(f"Updated file upload {upload_id} status to: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update file upload {upload_id} status: {e}")
            raise
    
    async def _poll_file_uploads(self) -> None:
        """Poll file uploads for status changes"""
        while self.is_active:
            try:
                # Check for new or updated uploads
                await self._check_upload_statuses()
                
                # Cleanup old uploads if enabled
                if self.config.cleanup_old_uploads:
                    await self._cleanup_old_uploads()
                
                # Wait for next polling interval
                await asyncio.sleep(self.config.polling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in file upload polling: {e}")
                await asyncio.sleep(self.config.polling_interval)
    
    async def _watch_directory(self) -> None:
        """Watch directory for new file uploads"""
        while self.is_active:
            try:
                # This would typically use a file system watcher
                # For now, we'll just log that we're watching
                logger.debug("Watching directory for new file uploads...")
                
                # Wait for next check
                await asyncio.sleep(self.config.polling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in directory watching: {e}")
                await asyncio.sleep(self.config.polling_interval)
    
    async def _check_upload_statuses(self) -> None:
        """Check the status of monitored file uploads"""
        try:
            # This would typically query the file upload system's status
            # For now, we'll just log that we're checking
            logger.debug("Checking file upload statuses...")
            
        except Exception as e:
            logger.error(f"Failed to check file upload statuses: {e}")
    
    async def _cleanup_old_uploads(self) -> None:
        """Clean up old completed/failed uploads"""
        try:
            current_time = datetime.now(timezone.utc)
            uploads_to_remove = []
            
            for upload_id, upload in self.file_uploads.items():
                age = (current_time - upload.upload_time).total_seconds()
                if age > self.config.max_upload_age:
                    uploads_to_remove.append(upload_id)
            
            for upload_id in uploads_to_remove:
                del self.file_uploads[upload_id]
                if upload_id in self.pending_uploads:
                    self.pending_uploads.remove(upload_id)
                if upload_id in self.processed_uploads:
                    self.processed_uploads.remove(upload_id)
                if upload_id in self.failed_uploads:
                    self.failed_uploads.remove(upload_id)
                
                logger.debug(f"Cleaned up old file upload: {upload_id}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old file uploads: {e}")
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get the current status of the file upload integration"""
        try:
            return {
                "is_active": self.is_active,
                "total_uploads_monitored": self.stats["total_uploads_monitored"],
                "pending_uploads": len(self.pending_uploads),
                "processed_uploads": len(self.processed_uploads),
                "failed_uploads": len(self.failed_uploads),
                "last_population_time": self.stats["last_population_time"],
                "average_population_time": self.stats["average_population_time"],
                "total_file_size_processed": self.stats["total_file_size_processed"]
            }
        except Exception as e:
            logger.error(f"Failed to get file upload integration status: {e}")
            return {"error": str(e)}


class FileUploadProcessor:
    """Processes file uploads and triggers events"""
    
    def __init__(self, event_manager: TwinRegistryEventManager):
        self.event_manager = event_manager
    
    async def process_file_upload(self, upload_info: FileUploadInfo) -> None:
        """Process a file upload and trigger the appropriate event"""
        try:
            # Determine file type from extension
            file_type = Path(upload_info.filename).suffix.lower().lstrip('.')
            
            # Trigger file upload event
            await self.event_manager.emit_event(
                TwinRegistryEvent(
                    event_type=EventType.FILE_UPLOAD,
                    priority=EventPriority.NORMAL,
                    timestamp=datetime.now(),
                    data={
                        'file_id': upload_info.upload_id,
                        'file_name': upload_info.filename,
                        'file_type': file_type,
                        'project_id': upload_info.project_id,
                        'processed_by': upload_info.user_id,
                        'org_id': upload_info.org_id,
                        'dept_id': upload_info.dept_id,
                        'file_size': upload_info.file_size,
                        'mime_type': upload_info.mime_type
                    },
                    source="file_upload_processor",
                    correlation_id=upload_info.upload_id
                )
            )
            
            logger.info(f"Processed file upload: {upload_info.filename}")
            
        except Exception as e:
            logger.error(f"Failed to process file upload {upload_info.filename}: {e}")


class FileUploadValidator:
    """Validates file upload data and metadata"""
    
    @staticmethod
    async def validate_upload_info(upload_info: FileUploadInfo) -> bool:
        """Validate file upload information"""
        try:
            if not upload_info.upload_id:
                return False
            
            if not upload_info.filename:
                return False
            
            if not upload_info.file_path:
                return False
            
            if upload_info.file_size <= 0:
                return False
            
            if not upload_info.user_id:
                return False
            
            if not upload_info.org_id:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate file upload info: {e}")
            return False
    
    @staticmethod
    async def validate_file_type(filename: str, supported_extensions: List[str]) -> bool:
        """Validate if file type is supported"""
        try:
            file_extension = Path(filename).suffix.lower()
            return file_extension in supported_extensions
            
        except Exception as e:
            logger.error(f"Failed to validate file type for {filename}: {e}")
            return False
    
    @staticmethod
    async def validate_file_size(file_size: int, max_size: int) -> bool:
        """Validate if file size is within limits"""
        try:
            return file_size <= max_size
            
        except Exception as e:
            logger.error(f"Failed to validate file size: {e}")
            return False
