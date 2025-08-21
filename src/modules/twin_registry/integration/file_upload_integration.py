"""
File Upload Integration for Twin Registry Population
Provides hooks and integration points with the file upload system
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

from ..events.event_types import Event, create_file_upload_event
from ..events.event_bus import EventBus

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
    upload_status: str
    processing_status: str
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
    """File upload system integration for twin registry population"""
    
    def __init__(
        self,
        event_bus: EventBus,
        config: FileUploadIntegrationConfig
    ):
        self.event_bus = event_bus
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
            if self.config.watch_directory and self.config.watch_directory.exists():
                self.file_watcher_task = asyncio.create_task(self._watch_directory())
            
            logger.info("File upload integration started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start file upload integration: {e}")
            self.is_active = False
            raise
    
    async def stop(self) -> None:
        """Stop file upload integration monitoring"""
        try:
            if not self.is_active:
                logger.warning("File upload integration is not active")
                return
            
            self.is_active = False
            
            # Cancel tasks
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
    
    async def _poll_file_uploads(self) -> None:
        """Poll file uploads for status changes"""
        while self.is_active:
            try:
                await self._check_file_uploads()
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
                await self._scan_directory_for_new_files()
                await asyncio.sleep(self.config.polling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in directory watching: {e}")
                await asyncio.sleep(self.config.polling_interval)
    
    async def _scan_directory_for_new_files(self) -> None:
        """Scan directory for new files"""
        try:
            if not self.config.watch_directory or not self.config.watch_directory.exists():
                return
            
            # Get list of files in directory
            for file_path in self.config.watch_directory.rglob("*"):
                if file_path.is_file() and self._is_supported_file(file_path):
                    await self._process_new_file(file_path)
                    
        except Exception as e:
            logger.error(f"Failed to scan directory: {e}")
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """Check if file is supported"""
        # Check file extension
        if file_path.suffix.lower() not in self.config.supported_extensions:
            return False
        
        # Check file patterns
        for pattern in self.config.file_patterns:
            if file_path.match(pattern):
                return True
        
        return False
    
    async def _process_new_file(self, file_path: Path) -> None:
        """Process a new file in the watch directory"""
        try:
            # Generate upload ID
            upload_id = self._generate_upload_id(file_path)
            
            # Check if already processed
            if upload_id in self.file_uploads:
                return
            
            # Get file information
            file_info = await self._get_file_info(file_path)
            
            # Create file upload info
            upload_info = FileUploadInfo(
                upload_id=upload_id,
                filename=file_path.name,
                file_path=str(file_path),
                file_size=file_info["size"],
                mime_type=file_info["mime_type"],
                upload_time=datetime.now(timezone.utc),
                user_id="system",  # Default user for watched files
                org_id="system",   # Default org for watched files
                upload_status="detected",
                processing_status="pending",
                metadata=file_info["metadata"]
            )
            
            # Add to tracking
            self.file_uploads[upload_id] = upload_info
            self.pending_uploads.append(upload_id)
            self.stats["total_uploads_monitored"] += 1
            
            logger.info(f"New file detected: {file_path.name} (ID: {upload_id})")
            
            # Trigger population after delay
            if self.config.enable_auto_population:
                await asyncio.sleep(self.config.upload_delay)
                await self._trigger_registry_population(upload_info)
            
        except Exception as e:
            logger.error(f"Failed to process new file {file_path}: {e}")
    
    async def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information"""
        try:
            stat = file_path.stat()
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Calculate file hash
            file_hash = await self._calculate_file_hash(file_path)
            
            return {
                "size": stat.st_size,
                "mime_type": mime_type,
                "created_time": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
                "modified_time": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                "file_hash": file_hash,
                "metadata": {
                    "file_hash": file_hash,
                    "detection_method": "directory_watch",
                    "file_permissions": oct(stat.st_mode)[-3:]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return {
                "size": 0,
                "mime_type": "application/octet-stream",
                "created_time": datetime.now(timezone.utc),
                "modified_time": datetime.now(timezone.utc),
                "file_hash": "",
                "metadata": {"error": str(e)}
            }
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            return ""
    
    def _generate_upload_id(self, file_path: Path) -> str:
        """Generate unique upload ID for file"""
        # Use file path and modification time to generate ID
        stat = file_path.stat()
        unique_string = f"{file_path.absolute()}_{stat.st_mtime}_{stat.st_size}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    async def _check_file_uploads(self) -> None:
        """Check file uploads for status changes"""
        try:
            # Get current file uploads from database
            current_uploads = await self._get_file_uploads_from_db()
            
            # Check for new or updated uploads
            for upload_info in current_uploads:
                await self._process_file_upload(upload_info)
            
            # Cleanup old uploads if enabled
            if self.config.cleanup_old_uploads:
                await self._cleanup_old_uploads()
                
        except Exception as e:
            logger.error(f"Failed to check file uploads: {e}")
    
    async def _get_file_uploads_from_db(self) -> List[FileUploadInfo]:
        """Get file uploads from database"""
        uploads = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Query file uploads table (adjust table name as needed)
                cursor.execute("""
                    SELECT 
                        upload_id, filename, file_path, file_size, mime_type,
                        upload_time, user_id, org_id, upload_status, processing_status,
                        metadata
                    FROM file_uploads 
                    WHERE upload_status IN ('completed', 'failed', 'processing')
                    ORDER BY upload_time DESC
                    LIMIT ?
                """, (self.config.batch_size,))
                
                rows = cursor.fetchall()
                
                for row in rows:
                    try:
                        # Parse datetime fields
                        upload_time = datetime.fromisoformat(row[5]) if row[5] else datetime.now(timezone.utc)
                        
                        # Parse metadata
                        metadata = {}
                        if row[10]:
                            try:
                                import json
                                metadata = json.loads(row[10])
                            except:
                                pass
                        
                        upload_info = FileUploadInfo(
                            upload_id=row[0],
                            filename=row[1],
                            file_path=row[2],
                            file_size=row[3],
                            mime_type=row[4],
                            upload_time=upload_time,
                            user_id=row[6],
                            org_id=row[7],
                            upload_status=row[8],
                            processing_status=row[9],
                            metadata=metadata
                        )
                        
                        uploads.append(upload_info)
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse file upload row: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to get file uploads from database: {e}")
        
        return uploads
    
    async def _process_file_upload(self, upload_info: FileUploadInfo) -> None:
        """Process a file upload for population triggers"""
        try:
            upload_id = upload_info.upload_id
            
            # Check if this is a new upload
            if upload_id not in self.file_uploads:
                self.file_uploads[upload_id] = upload_info
                self.stats["total_uploads_monitored"] += 1
                self.stats["total_file_size_processed"] += upload_info.file_size
                logger.info(f"New file upload detected: {upload_info.filename}")
            
            # Check for status changes
            current_upload = self.file_uploads[upload_id]
            if current_upload.upload_status != upload_info.upload_status:
                current_upload.upload_status = upload_info.upload_status
                current_upload.processing_status = upload_info.processing_status
                
                logger.info(f"File upload {upload_id} status changed to: {upload_info.upload_status}")
                
                # Handle status change
                await self._handle_upload_status_change(upload_info)
            
            # Update upload info
            self.file_uploads[upload_id] = upload_info
            
        except Exception as e:
            logger.error(f"Failed to process file upload {upload_info.upload_id}: {e}")
    
    async def _handle_upload_status_change(self, upload_info: FileUploadInfo) -> None:
        """Handle file upload status changes"""
        try:
            if upload_info.upload_status == "completed":
                await self._handle_upload_completion(upload_info)
            elif upload_info.upload_status == "failed":
                await self._handle_upload_failure(upload_info)
            elif upload_info.upload_status == "processing":
                await self._handle_upload_processing(upload_info)
                
        except Exception as e:
            logger.error(f"Failed to handle upload status change: {e}")
    
    async def _handle_upload_completion(self, upload_info: FileUploadInfo) -> None:
        """Handle file upload completion"""
        try:
            upload_id = upload_info.upload_id
            
            # Add to processed uploads
            if upload_id not in self.processed_uploads:
                self.processed_uploads.append(upload_id)
            
            # Remove from pending and failed uploads
            if upload_id in self.pending_uploads:
                self.pending_uploads.remove(upload_id)
            if upload_id in self.failed_uploads:
                self.failed_uploads.remove(upload_id)
            
            logger.info(f"File upload completed: {upload_info.filename}")
            
            # Trigger population after delay
            if self.config.enable_auto_population:
                await asyncio.sleep(self.config.population_delay)
                await self._trigger_registry_population(upload_info)
            
            # Execute registered callbacks
            await self._execute_callbacks("upload_completion", upload_info)
            
        except Exception as e:
            logger.error(f"Failed to handle upload completion: {e}")
    
    async def _handle_upload_failure(self, upload_info: FileUploadInfo) -> None:
        """Handle file upload failure"""
        try:
            upload_id = upload_info.upload_id
            
            # Add to failed uploads
            if upload_id not in self.failed_uploads:
                self.failed_uploads.append(upload_id)
            
            # Remove from pending and processed uploads
            if upload_id in self.pending_uploads:
                self.pending_uploads.remove(upload_id)
            if upload_id in self.processed_uploads:
                self.processed_uploads.remove(upload_id)
            
            logger.warning(f"File upload failed: {upload_info.filename}")
            
            # Execute registered callbacks
            await self._execute_callbacks("upload_failure", upload_info)
            
        except Exception as e:
            logger.error(f"Failed to handle upload failure: {e}")
    
    async def _handle_upload_processing(self, upload_info: FileUploadInfo) -> None:
        """Handle file upload processing"""
        try:
            upload_id = upload_info.upload_id
            logger.debug(f"File upload processing: {upload_info.filename}")
            
            # Execute registered callbacks
            await self._execute_callbacks("upload_processing", upload_info)
            
        except Exception as e:
            logger.error(f"Failed to handle upload processing: {e}")
    
    async def _trigger_registry_population(self, upload_info: FileUploadInfo) -> None:
        """Trigger twin registry population for completed file upload"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Create file upload event
            event = create_file_upload_event(
                source="file_upload_integration",
                filename=upload_info.filename,
                file_path=upload_info.file_path,
                file_size=upload_info.file_size,
                mime_type=upload_info.mime_type,
                user_id=upload_info.user_id,
                org_id=upload_info.org_id,
                upload_time=upload_info.upload_time,
                metadata=upload_info.metadata
            )
            
            # Publish event
            await self.event_bus.publish(event)
            
            # Update statistics
            population_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.stats["successful_populations"] += 1
            self.stats["last_population_time"] = start_time
            
            # Update average population time
            total_time = self.stats["average_population_time"] * (self.stats["successful_populations"] - 1) + population_time
            self.stats["average_population_time"] = total_time / self.stats["successful_populations"]
            
            logger.info(f"Registry population triggered for file upload: {upload_info.filename}")
            
        except Exception as e:
            logger.error(f"Failed to trigger registry population: {e}")
            self.stats["failed_populations"] += 1
    
    async def _execute_callbacks(self, event_type: str, upload_info: FileUploadInfo) -> None:
        """Execute registered callbacks"""
        try:
            for callback in self.registered_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_type, upload_info)
                    else:
                        callback(event_type, upload_info)
                except Exception as e:
                    logger.error(f"Callback execution failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to execute callbacks: {e}")
    
    async def _cleanup_old_uploads(self) -> None:
        """Cleanup old file uploads"""
        try:
            current_time = datetime.now(timezone.utc)
            cutoff_time = current_time.timestamp() - self.config.max_upload_age
            
            # Cleanup old uploads from tracking
            old_uploads = [
                upload_id for upload_id, upload_info in self.file_uploads.items()
                if upload_info.upload_time.timestamp() < cutoff_time
            ]
            
            for upload_id in old_uploads:
                upload_info = self.file_uploads[upload_id]
                del self.file_uploads[upload_id]
                if upload_id in self.pending_uploads:
                    self.pending_uploads.remove(upload_id)
                if upload_id in self.processed_uploads:
                    self.processed_uploads.remove(upload_id)
                if upload_id in self.failed_uploads:
                    self.failed_uploads.remove(upload_id)
            
            if old_uploads:
                logger.info(f"Cleaned up {len(old_uploads)} old file uploads")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old uploads: {e}")
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for file upload events"""
        if callback not in self.registered_callbacks:
            self.registered_callbacks.append(callback)
            logger.info("File upload integration callback registered")
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback"""
        if callback in self.registered_callbacks:
            self.registered_callbacks.remove(callback)
            logger.info("File upload integration callback unregistered")
    
    async def get_upload_status(self, upload_id: str) -> Optional[FileUploadInfo]:
        """Get status of a specific file upload"""
        return self.file_uploads.get(upload_id)
    
    def get_uploads_summary(self) -> Dict[str, Any]:
        """Get summary of file uploads"""
        return {
            "total_uploads": len(self.file_uploads),
            "pending_uploads": len(self.pending_uploads),
            "processed_uploads": len(self.processed_uploads),
            "failed_uploads": len(self.failed_uploads),
            "stats": self.stats.copy()
        }
    
    async def manually_trigger_population(self, upload_id: str) -> bool:
        """Manually trigger population for a specific file upload"""
        try:
            upload_info = self.file_uploads.get(upload_id)
            if not upload_info:
                logger.warning(f"File upload not found: {upload_id}")
                return False
            
            if upload_info.upload_status != "completed":
                logger.warning(f"File upload {upload_id} is not completed (status: {upload_info.upload_status})")
                return False
            
            await self._trigger_registry_population(upload_info)
            return True
            
        except Exception as e:
            logger.error(f"Failed to manually trigger population: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of file upload integration"""
        health_status = {
            "active": self.is_active,
            "polling_task_running": self.polling_task and not self.polling_task.done(),
            "file_watcher_running": self.file_watcher_task and not self.file_watcher_task.done(),
            "total_uploads_monitored": self.stats["total_uploads_monitored"],
            "recent_populations": self.stats["successful_populations"],
            "failed_populations": self.stats["failed_populations"],
            "last_population": self.stats["last_population_time"].isoformat() if self.stats["last_population_time"] else None,
            "average_population_time": round(self.stats["average_population_time"], 3),
            "total_file_size_processed": self.stats["total_file_size_processed"],
            "registered_callbacks": len(self.registered_callbacks),
            "watch_directory": str(self.config.watch_directory) if self.config.watch_directory else None
        }
        
        # Check database connectivity
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM file_uploads")
                count = cursor.fetchone()[0]
                health_status["database_accessible"] = True
                health_status["total_uploads_in_db"] = count
        except Exception as e:
            health_status["database_accessible"] = False
            health_status["database_error"] = str(e)
        
        return health_status
    
    async def cleanup(self) -> None:
        """Cleanup file upload integration resources"""
        try:
            await self.stop()
            
            # Clear tracking data
            self.file_uploads.clear()
            self.pending_uploads.clear()
            self.processed_uploads.clear()
            self.failed_uploads.clear()
            self.registered_callbacks.clear()
            
            logger.info("File upload integration cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during file upload integration cleanup: {e}")
            raise
