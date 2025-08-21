"""
File Service - Business Domain Service
=====================================

Manages files, documents, and file-related operations.
This service provides comprehensive file management capabilities.

Features:
- File upload, download, and storage management
- Document versioning and metadata management
- File access control and permissions
- File categorization and tagging
- File lifecycle management
"""

import logging
import asyncio
import hashlib
import mimetypes
import os
from typing import Dict, Any, List, Optional, Set, BinaryIO
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from ..base import BaseService
from ...models.base_model import BaseModel
from ...repositories.base_repository import BaseRepository
from ...models.enums import EventType, SystemCategory, SecurityLevel

logger = logging.getLogger(__name__)


class FileType(Enum):
    """File type categories."""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    DATA = "data"
    CODE = "code"
    OTHER = "other"


class FileStatus(Enum):
    """File status values."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ARCHIVED = "archived"
    DELETED = "deleted"
    CORRUPTED = "corrupted"


class FilePermission(Enum):
    """File permission levels."""
    PRIVATE = "private"
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"


@dataclass
class FileInfo:
    """File information structure."""
    file_id: str
    filename: str
    original_filename: str
    file_type: FileType
    mime_type: str
    size_bytes: int
    status: FileStatus
    checksum: str
    file_path: str
    org_id: str
    dept_id: Optional[str]
    project_id: Optional[str]
    uploaded_by: str
    permissions: FilePermission
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    accessed_at: Optional[datetime]


@dataclass
class FileVersion:
    """File version information."""
    version_id: str
    file_id: str
    version_number: int
    filename: str
    file_path: str
    size_bytes: int
    checksum: str
    changes_description: str
    created_by: str
    created_at: datetime


@dataclass
class FileAccessLog:
    """File access log entry."""
    log_id: str
    file_id: str
    user_id: str
    action: str
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Dict[str, Any]


class FileService(BaseService[BaseModel, BaseRepository]):
    """
    Business domain service for file management.
    
    Provides:
    - File CRUD operations
    - File versioning and metadata management
    - Access control and permissions
    - File categorization and search
    - File lifecycle management
    """

    def __init__(self, repository: Optional[BaseRepository] = None):
        super().__init__(repository, "FileService")
        
        # File storage
        self._files: Dict[str, FileInfo] = {}
        self._file_versions: Dict[str, List[FileVersion]] = {}  # file_id -> versions
        self._file_access_logs: Dict[str, List[FileAccessLog]] = {}  # file_id -> logs
        
        # File organization
        self._org_files: Dict[str, Set[str]] = {}  # org_id -> files
        self._dept_files: Dict[str, Set[str]] = {}  # dept_id -> files
        self._project_files: Dict[str, Set[str]] = {}  # project_id -> files
        self._user_files: Dict[str, Set[str]] = {}  # user_id -> files
        
        # File type indexing
        self._file_type_index: Dict[FileType, Set[str]] = {}  # file_type -> files
        self._tag_index: Dict[str, Set[str]] = {}  # tag -> files
        
        # Storage configuration
        self._storage_config = {
            'base_path': '/tmp/file_storage',
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'allowed_extensions': {'.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                                 '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.zip'},
            'max_versions_per_file': 10
        }
        
        logger.info("File service initialized")

    async def _initialize_service_resources(self) -> None:
        """Initialize file service resources."""
        # Create storage directory
        await self._ensure_storage_directory()
        
        # Load existing files from repository
        await self._load_files()
        
        # Build indexes
        await self._build_file_indexes()
        
        logger.info("File service resources initialized")

    async def _cleanup_service_resources(self) -> None:
        """Cleanup file service resources."""
        # Save files to repository
        await self._save_files()
        
        # Clear in-memory data
        self._files.clear()
        self._file_versions.clear()
        self._file_access_logs.clear()
        self._org_files.clear()
        self._dept_files.clear()
        self._project_files.clear()
        self._user_files.clear()
        self._file_type_index.clear()
        self._tag_index.clear()
        
        logger.info("File service resources cleaned up")

    async def get_service_info(self) -> Dict[str, Any]:
        """Get file service information."""
        return {
            'service_name': self.service_name,
            'total_files': len(self._files),
            'total_versions': sum(len(versions) for versions in self._file_versions.values()),
            'file_types': [t.value for t in FileType],
            'storage_path': self._storage_config['base_path'],
            'max_file_size': self._storage_config['max_file_size'],
            'health_status': self.health_status,
            'uptime': str(self.get_uptime()),
            'last_health_check': self.last_health_check.isoformat()
        }

    # File Management

    async def upload_file(self, file_data: BinaryIO, filename: str, org_id: str,
                         uploaded_by: str, project_id: str = None, dept_id: str = None,
                         file_type: FileType = None, tags: List[str] = None,
                         permissions: FilePermission = FilePermission.READ_ONLY,
                         metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Upload a new file.
        
        Args:
            file_data: File data stream
            filename: Original filename
            org_id: Organization ID
            uploaded_by: User ID who uploaded the file
            project_id: Associated project ID
            file_type: File type category
            tags: File tags
            permissions: File permissions
            metadata: Additional file metadata
            
        Returns:
            File ID if successful, None otherwise
        """
        try:
            # Validate file data
            if not await self._validate_file_upload(filename, file_data):
                return None
            
            # Determine file type if not provided
            if file_type is None:
                file_type = await self._detect_file_type(filename)
            
            # Generate file ID and path
            file_id = f"file_{filename.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            file_path = await self._generate_file_path(file_id, filename)
            
            # Calculate file size and checksum
            file_size, checksum = await self._calculate_file_properties(file_data)
            
            # Save file to storage
            if not await self._save_file_to_storage(file_data, file_path):
                logger.error(f"Failed to save file {filename} to storage")
                return None
            
            # Create file info
            file_info = FileInfo(
                file_id=file_id,
                filename=os.path.basename(file_path),
                original_filename=filename,
                file_type=file_type,
                mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                size_bytes=file_size,
                status=FileStatus.READY,
                checksum=checksum,
                file_path=file_path,
                org_id=org_id,
                dept_id=dept_id,
                project_id=project_id,
                uploaded_by=uploaded_by,
                permissions=permissions,
                tags=tags or [],
                metadata=metadata or {},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                accessed_at=None
            )
            
            # Store file info
            self._files[file_id] = file_info
            
            # Update indexes
            await self._update_file_indexes(file_id, file_info)
            
            # Log access
            await self._log_file_access(file_id, uploaded_by, 'upload', {'filename': filename})
            
            # Log audit event
            await self.log_audit_event(
                EventType.FILE_UPLOADED,
                SystemCategory.APPLICATION,
                f"File uploaded: {filename}",
                {'file_id': file_id, 'org_id': org_id, 'size_bytes': file_size},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"File uploaded: {file_id} ({filename})")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to upload file {filename}: {e}")
            return None

    async def get_file(self, file_id: str) -> Optional[FileInfo]:
        """Get file information by ID."""
        try:
            return self._files.get(file_id)
        except Exception as e:
            logger.error(f"Failed to get file {file_id}: {e}")
            return None

    async def download_file(self, file_id: str, user_id: str) -> Optional[BinaryIO]:
        """Download a file."""
        try:
            if file_id not in self._files:
                logger.warning(f"File {file_id} not found")
                return None
            
            file_info = self._files[file_id]
            
            # Check permissions
            if not await self._check_file_access(file_id, user_id, 'read'):
                logger.warning(f"User {user_id} does not have read access to file {file_id}")
                return None
            
            # Check if file exists on disk
            if not os.path.exists(file_info.file_path):
                logger.error(f"File {file_id} not found on disk: {file_info.file_path}")
                return None
            
            # Update access time
            file_info.accessed_at = datetime.now()
            file_info.updated_at = datetime.now()
            
            # Log access
            await self._log_file_access(file_id, user_id, 'download')
            
            # Return file stream
            return open(file_info.file_path, 'rb')
            
        except Exception as e:
            logger.error(f"Failed to download file {file_id}: {e}")
            return None

    async def update_file(self, file_id: str, user_id: str, **kwargs) -> bool:
        """Update file information."""
        try:
            if file_id not in self._files:
                logger.warning(f"File {file_id} not found")
                return False
            
            file_info = self._files[file_id]
            
            # Check permissions
            if not await self._check_file_access(file_id, user_id, 'write'):
                logger.warning(f"User {user_id} does not have write access to file {file_id}")
                return False
            
            # Update allowed fields
            allowed_fields = {
                'tags', 'metadata', 'permissions', 'project_id'
            }
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(file_info, field):
                    setattr(file_info, field, value)
            
            file_info.updated_at = datetime.now()
            
            # Update indexes if needed
            if 'tags' in kwargs:
                await self._update_tag_indexes(file_id, file_info)
            
            # Log access
            await self._log_file_access(file_id, user_id, 'update', {'updated_fields': list(kwargs.keys())})
            
            # Log audit event
            await self.log_audit_event(
                EventType.FILE_STATUS_CHANGED,
                SystemCategory.APPLICATION,
                f"File updated: {file_id}",
                {'file_id': file_id, 'updated_fields': list(kwargs.keys())},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"File updated: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update file {file_id}: {e}")
            return False

    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete a file."""
        try:
            if file_id not in self._files:
                logger.warning(f"File {file_id} not found")
                return False
            
            file_info = self._files[file_id]
            
            # Check permissions
            if not await self._check_file_access(file_id, user_id, 'admin'):
                logger.warning(f"User {user_id} does not have admin access to file {file_id}")
                return False
            
            # Remove file from disk
            if os.path.exists(file_info.file_path):
                os.remove(file_info.file_path)
            
            # Remove file versions
            if file_id in self._file_versions:
                for version in self._file_versions[file_id]:
                    if os.path.exists(version.file_path):
                        os.remove(version.file_path)
                del self._file_versions[file_id]
            
            # Remove from indexes
            await self._remove_file_from_indexes(file_id, file_info)
            
            # Log access
            await self._log_file_access(file_id, user_id, 'delete')
            
            # Log audit event
            await self.log_audit_event(
                EventType.FILE_DELETED,
                SystemCategory.APPLICATION,
                f"File deleted: {file_id}",
                {'file_id': file_id, 'filename': file_info.original_filename},
                SecurityLevel.INTERNAL
            )
            
            # Delete file info
            del self._files[file_id]
            
            logger.info(f"File deleted: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return False

    # File Versioning

    async def create_file_version(self, file_id: str, user_id: str, new_file_data: BinaryIO,
                                changes_description: str) -> Optional[str]:
        """
        Create a new version of a file.
        
        Args:
            file_id: Original file ID
            user_id: User creating the version
            new_file_data: New file data
            changes_description: Description of changes
            
        Returns:
            Version ID if successful, None otherwise
        """
        try:
            if file_id not in self._files:
                logger.warning(f"File {file_id} not found")
                return None
            
            file_info = self._files[file_id]
            
            # Check permissions
            if not await self._check_file_access(file_id, user_id, 'write'):
                logger.warning(f"User {user_id} does not have write access to file {file_id}")
                return None
            
            # Check version limit
            current_versions = self._file_versions.get(file_id, [])
            if len(current_versions) >= self._storage_config['max_versions_per_file']:
                logger.warning(f"Maximum versions per file exceeded for {file_id}")
                return None
            
            # Generate version info
            version_number = len(current_versions) + 1
            version_id = f"ver_{file_id}_{version_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            version_filename = f"{file_info.original_filename}_v{version_number}"
            version_path = await self._generate_file_path(version_id, version_filename)
            
            # Save new version to storage
            if not await self._save_file_to_storage(new_file_data, version_path):
                logger.error(f"Failed to save version {version_id} to storage")
                return None
            
            # Calculate new version properties
            file_size, checksum = await self._calculate_file_properties(new_file_data)
            
            # Create version info
            version_info = FileVersion(
                version_id=version_id,
                file_id=file_id,
                version_number=version_number,
                filename=version_filename,
                file_path=version_path,
                size_bytes=file_size,
                checksum=checksum,
                changes_description=changes_description,
                created_by=user_id,
                created_at=datetime.now()
            )
            
            # Store version
            if file_id not in self._file_versions:
                self._file_versions[file_id] = []
            self._file_versions[file_id].append(version_info)
            
            # Update file info
            file_info.updated_at = datetime.now()
            
            # Log access
            await self._log_file_access(file_id, user_id, 'version_created', 
                                      {'version_id': version_id, 'version_number': version_number})
            
            logger.info(f"File version created: {version_id} for file {file_id}")
            return version_id
            
        except Exception as e:
            logger.error(f"Failed to create file version for {file_id}: {e}")
            return None

    async def get_file_versions(self, file_id: str) -> List[FileVersion]:
        """Get all versions of a file."""
        try:
            return self._file_versions.get(file_id, [])
        except Exception as e:
            logger.error(f"Failed to get versions for file {file_id}: {e}")
            return []

    # File Search and Organization

    async def search_files(self, org_id: str = None, project_id: str = None,
                          file_type: FileType = None, tags: List[str] = None,
                          filename_pattern: str = None, user_id: str = None) -> List[FileInfo]:
        """
        Search for files based on criteria.
        
        Args:
            org_id: Organization ID filter
            project_id: Project ID filter
            file_type: File type filter
            tags: Tags filter
            filename_pattern: Filename pattern filter
            user_id: User ID filter
            
        Returns:
            List of matching files
        """
        try:
            matching_files = []
            
            for file_id, file_info in self._files.items():
                # Apply filters
                if org_id and file_info.org_id != org_id:
                    continue
                
                if project_id and file_info.project_id != project_id:
                    continue
                
                if file_type and file_info.file_type != file_type:
                    continue
                
                if tags:
                    if not any(tag in file_info.tags for tag in tags):
                        continue
                
                if filename_pattern:
                    if filename_pattern.lower() not in file_info.original_filename.lower():
                        continue
                
                if user_id:
                    if not await self._check_file_access(file_id, user_id, 'read'):
                        continue
                
                matching_files.append(file_info)
            
            # Sort by creation date (newest first)
            matching_files.sort(key=lambda x: x.created_at, reverse=True)
            
            return matching_files
            
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return []

    async def get_organization_files(self, org_id: str) -> List[FileInfo]:
        """Get all files for an organization."""
        try:
            if org_id not in self._org_files:
                return []
            
            return [self._files[file_id] for file_id in self._org_files[org_id] 
                   if file_id in self._files]
        except Exception as e:
            logger.error(f"Failed to get files for organization {org_id}: {e}")
            return []

    async def get_department_files(self, dept_id: str) -> List[FileInfo]:
        """Get all files for a department."""
        try:
            if dept_id not in self._dept_files:
                return []
            
            return [self._files[file_id] for file_id in self._dept_files[dept_id] 
                   if file_id in self._files]
        except Exception as e:
            logger.error(f"Failed to get files for department {dept_id}: {e}")
            return []

    async def get_project_files(self, project_id: str) -> List[FileInfo]:
        """Get all files for a project."""
        try:
            if project_id not in self._project_files:
                return []
            
            return [self._files[file_id] for file_id in self._project_files[project_id] 
                   if file_id in self._files]
        except Exception as e:
            logger.error(f"Failed to get files for project {project_id}: {e}")
            return []

    # File Access Control

    async def _check_file_access(self, file_id: str, user_id: str, action: str) -> bool:
        """Check if user has access to perform action on file."""
        try:
            if file_id not in self._files:
                return False
            
            file_info = self._files[file_id]
            
            # File owner has full access
            if file_info.uploaded_by == user_id:
                return True
            
            # Check permissions based on action
            if action == 'read':
                return file_info.permissions in [FilePermission.READ_ONLY, FilePermission.READ_WRITE, FilePermission.ADMIN]
            elif action == 'write':
                return file_info.permissions in [FilePermission.READ_WRITE, FilePermission.ADMIN]
            elif action == 'admin':
                return file_info.permissions == FilePermission.ADMIN
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check file access: {e}")
            return False

    # File Storage Management

    async def _ensure_storage_directory(self) -> None:
        """Ensure storage directory exists."""
        try:
            os.makedirs(self._storage_config['base_path'], exist_ok=True)
            logger.info(f"Storage directory ensured: {self._storage_config['base_path']}")
        except Exception as e:
            logger.error(f"Failed to ensure storage directory: {e}")

    async def _generate_file_path(self, file_id: str, filename: str) -> str:
        """Generate file path for storage."""
        try:
            # Create subdirectories based on file_id
            subdir = file_id[:2]
            file_dir = os.path.join(self._storage_config['base_path'], subdir)
            os.makedirs(file_dir, exist_ok=True)
            
            return os.path.join(file_dir, f"{file_id}_{filename}")
        except Exception as e:
            logger.error(f"Failed to generate file path: {e}")
            return os.path.join(self._storage_config['base_path'], f"{file_id}_{filename}")

    async def _save_file_to_storage(self, file_data: BinaryIO, file_path: str) -> bool:
        """Save file data to storage."""
        try:
            with open(file_path, 'wb') as f:
                # Reset file pointer to beginning
                file_data.seek(0)
                f.write(file_data.read())
            return True
        except Exception as e:
            logger.error(f"Failed to save file to storage {file_path}: {e}")
            return False

    async def _calculate_file_properties(self, file_data: BinaryIO) -> tuple[int, str]:
        """Calculate file size and checksum."""
        try:
            # Reset file pointer
            file_data.seek(0)
            data = file_data.read()
            
            size = len(data)
            checksum = hashlib.md5(data).hexdigest()
            
            return size, checksum
        except Exception as e:
            logger.error(f"Failed to calculate file properties: {e}")
            return 0, ""

    # File Type Detection

    async def _detect_file_type(self, filename: str) -> FileType:
        """Detect file type based on filename extension."""
        try:
            ext = Path(filename).suffix.lower()
            
            # Document types
            if ext in {'.txt', '.pdf', '.doc', '.docx', '.rtf'}:
                return FileType.DOCUMENT
            
            # Image types
            elif ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}:
                return FileType.IMAGE
            
            # Video types
            elif ext in {'.mp4', '.avi', '.mov', '.wmv', '.flv'}:
                return FileType.VIDEO
            
            # Audio types
            elif ext in {'.mp3', '.wav', '.flac', '.aac', '.ogg'}:
                return FileType.AUDIO
            
            # Archive types
            elif ext in {'.zip', '.rar', '.7z', '.tar', '.gz'}:
                return FileType.ARCHIVE
            
            # Code types
            elif ext in {'.py', '.js', '.java', '.cpp', '.c', '.html', '.css'}:
                return FileType.CODE
            
            # Data types
            elif ext in {'.csv', '.json', '.xml', '.sql', '.db'}:
                return FileType.DATA
            
            else:
                return FileType.OTHER
                
        except Exception as e:
            logger.error(f"Failed to detect file type for {filename}: {e}")
            return FileType.OTHER

    # Validation Methods

    async def _validate_file_upload(self, filename: str, file_data: BinaryIO) -> bool:
        """Validate file upload data."""
        try:
            # Check file extension
            ext = Path(filename).suffix.lower()
            if ext not in self._storage_config['allowed_extensions']:
                logger.warning(f"File extension {ext} not allowed")
                return False
            
            # Check file size
            file_data.seek(0, 2)  # Seek to end
            size = file_data.tell()
            if size > self._storage_config['max_file_size']:
                logger.warning(f"File size {size} exceeds maximum allowed")
                return False
            
            file_data.seek(0)  # Reset to beginning
            return True
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False

    # Index Management

    async def _update_file_indexes(self, file_id: str, file_info: FileInfo) -> None:
        """Update all file indexes."""
        try:
            # Organization index
            if file_info.org_id not in self._org_files:
                self._org_files[file_info.org_id] = set()
            self._org_files[file_info.org_id].add(file_id)
            
            # Department index
            if file_info.dept_id:
                if file_info.dept_id not in self._dept_files:
                    self._dept_files[file_info.dept_id] = set()
                self._dept_files[file_info.dept_id].add(file_id)
            
            # Project index
            if file_info.project_id:
                if file_info.project_id not in self._project_files:
                    self._project_files[file_info.project_id] = set()
                self._project_files[file_info.project_id].add(file_id)
            
            # User index
            if file_info.uploaded_by not in self._user_files:
                self._user_files[file_info.uploaded_by] = set()
            self._user_files[file_info.uploaded_by].add(file_id)
            
            # File type index
            if file_info.file_type not in self._file_type_index:
                self._file_type_index[file_info.file_type] = set()
            self._file_type_index[file_info.file_type].add(file_id)
            
            # Tag index
            await self._update_tag_indexes(file_id, file_info)
            
        except Exception as e:
            logger.error(f"Failed to update file indexes: {e}")

    async def _update_tag_indexes(self, file_id: str, file_info: FileInfo) -> None:
        """Update tag indexes."""
        try:
            for tag in file_info.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(file_id)
        except Exception as e:
            logger.error(f"Failed to update tag indexes: {e}")

    async def _remove_file_from_indexes(self, file_id: str, file_info: FileInfo) -> None:
        """Remove file from all indexes."""
        try:
            # Organization index
            if file_info.org_id in self._org_files:
                self._org_files[file_info.org_id].discard(file_id)
            
            # Department index
            if file_info.dept_id and file_info.dept_id in self._dept_files:
                self._dept_files[file_info.dept_id].discard(file_id)
            
            # Project index
            if file_info.project_id and file_info.project_id in self._project_files:
                self._project_files[file_info.project_id].discard(file_id)
            
            # User index
            if file_info.uploaded_by in self._user_files:
                self._user_files[file_info.uploaded_by].discard(file_id)
            
            # File type index
            if file_info.file_type in self._file_type_index:
                self._file_type_index[file_info.file_type].discard(file_id)
            
            # Tag index
            for tag in file_info.tags:
                if tag in self._tag_index:
                    self._tag_index[tag].discard(file_id)
            
        except Exception as e:
            logger.error(f"Failed to remove file from indexes: {e}")

    # Access Logging

    async def _log_file_access(self, file_id: str, user_id: str, action: str, 
                              details: Dict[str, Any] = None) -> None:
        """Log file access."""
        try:
            log_entry = FileAccessLog(
                log_id=f"log_{file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                file_id=file_id,
                user_id=user_id,
                action=action,
                timestamp=datetime.now(),
                ip_address=None,  # Would be set by web framework
                user_agent=None,  # Would be set by web framework
                details=details or {}
            )
            
            if file_id not in self._file_access_logs:
                self._file_access_logs[file_id] = []
            self._file_access_logs[file_id].append(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to log file access: {e}")

    # Data Loading and Saving

    async def _load_files(self) -> None:
        """Load files from repository."""
        try:
            # This would typically load from a database or file
            logger.info("Loading files from repository")
            
        except Exception as e:
            logger.error(f"Failed to load files: {e}")

    async def _save_files(self) -> None:
        """Save files to repository."""
        try:
            # This would typically save to a database or file
            logger.info("Saving files to repository")
            
        except Exception as e:
            logger.error(f"Failed to save files: {e}")

    async def _build_file_indexes(self) -> None:
        """Build file indexes from loaded data."""
        try:
            # Build all indexes from loaded files
            for file_id, file_info in self._files.items():
                await self._update_file_indexes(file_id, file_info)
            
            logger.info("File indexes built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build file indexes: {e}")

    # Business Intelligence

    async def get_file_statistics(self) -> Dict[str, Any]:
        """Get comprehensive file statistics."""
        try:
            stats = {
                'total_files': len(self._files),
                'total_versions': sum(len(versions) for versions in self._file_versions.values()),
                'file_type_distribution': {},
                'file_status_distribution': {},
                'permission_distribution': {},
                'size_distribution': {},
                'tag_distribution': {},
                'storage_usage': {}
            }
            
            # Count by file type
            for file_info in self._files.values():
                file_type = file_info.file_type.value
                stats['file_type_distribution'][file_type] = stats['file_type_distribution'].get(file_type, 0) + 1
            
            # Count by status
            for file_info in self._files.values():
                status = file_info.status.value
                stats['file_status_distribution'][status] = stats['file_status_distribution'].get(status, 0) + 1
            
            # Count by permissions
            for file_info in self._files.values():
                permission = file_info.permissions.value
                stats['permission_distribution'][permission] = stats['permission_distribution'].get(permission, 0) + 1
            
            # Size distribution
            size_ranges = [(0, 1024), (1024, 10240), (10240, 102400), (102400, 1048576), (1048576, float('inf'))]
            for file_info in self._files.values():
                for start, end in size_ranges:
                    if start <= file_info.size_bytes < end:
                        range_key = f"{start}-{end if end != float('inf') else '∞'} bytes"
                        stats['size_distribution'][range_key] = stats['size_distribution'].get(range_key, 0) + 1
                        break
            
            # Tag distribution
            for file_info in self._files.values():
                for tag in file_info.tags:
                    stats['tag_distribution'][tag] = stats['tag_distribution'].get(tag, 0) + 1
            
            # Storage usage
            total_size = sum(f.size_bytes for f in self._files.values())
            stats['storage_usage'] = {
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'total_size_gb': total_size / (1024 * 1024 * 1024)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get file statistics: {e}")
            return {'error': str(e)}
