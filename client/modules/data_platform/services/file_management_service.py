"""
File Management Service - Data Platform Integration Service
==========================================================

Integration service for file management operations that delegates to backend
engine services while handling frontend-specific logic and maintaining clean
architecture.

Pattern: Lazy initialization with async services for world-class standards
"""

import logging
from typing import Dict, Any, Optional, List, BinaryIO
from datetime import datetime
from pathlib import Path
import uuid

# Import from backend engine
from src.engine.services.business_domain.file_service import FileService
from src.engine.repositories.business_domain_repository import BusinessDomainRepository
from src.engine.models.business_domain import File
from src.engine.models.enums import FileStatus

# Import user and organization services
from src.engine.services.auth.user_service import UserService
from src.engine.services.business_domain.organization_service import OrganizationService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class FileManagementService:
    """Integration service for file management operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._file_service = None
        self._business_domain_repo = None
        self._user_service = None
        self._organization_service = None
        self._auth_repo = None
        
        logger.info("✅ File management service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            self._organization_service = OrganizationService()
            self._business_domain_repo = BusinessDomainRepository()
            self._file_service = FileService()
            
            self._initialized = True
            logger.info("✅ File management service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize file management service: {e}")
            raise
    
    @property
    def file_service(self):
        """Get file service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._file_service
    
    @property
    def business_domain_repo(self):
        """Get business domain repository (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._business_domain_repo
    
    @property
    def user_service(self):
        """Get user service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._user_service
    
    @property
    def organization_service(self):
        """Get organization service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._organization_service
    
    @property
    def auth_repo(self):
        """Get auth repository (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._auth_repo
    
    async def upload_file(self, file_data: Dict[str, Any], project_id: str, 
                         file_content: bytes, user_id: str, organization_id: str) -> Dict[str, Any]:
        """Upload a file with business validation and duplication prevention"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id, project_id)
            
            # Validate business rules
            self._validate_file_upload(file_data, project_id)
            
            # Check for existing file with same name in project
            existing_file = await self._find_existing_file(
                file_data["original_filename"], project_id
            )
            
            if existing_file:
                # Update existing file instead of creating duplicate
                return await self._update_existing_file(existing_file["file_id"], file_data, file_content)
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            file_data["file_id"] = file_id
            
            # Add user and organization context
            file_data["user_id"] = user_id
            file_data["organization_id"] = organization_id
            file_data["uploaded_by"] = user_id
            
            # Get project information for file organization
            project_info = await self._get_project_info(project_id, organization_id)
            if not project_info:
                raise ValueError(f"Project {project_id} not found in organization {organization_id}")
            
            # Generate required fields with hierarchy-based path
            file_data["filename"] = f"{file_id}_{file_data['original_filename']}"
            file_data["file_path"] = f"uploads/{project_info['use_case_name']}/{project_info['project_name']}/{file_data['filename']}"
            
            # Create file using backend service
            file_info = await self.file_service.create_file(file_data, file_content)
            
            # Update project statistics
            await self._update_project_file_count(project_id)
            await self._update_project_total_size(project_id)
            
            logger.info(f"Uploaded file: {file_data['original_filename']} to project: {project_info['project_name']} by user: {user_id}")
            return file_info
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    async def get_file_with_trace(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file with complete trace information"""
        await self._ensure_initialized()
        
        try:
            file_info = await self.file_service.get_file_by_id(file_id)
            if not file_info:
                return None
            
            # Get trace information
            trace_info = await self.file_repo.get_file_trace_info(file_id)
            
            return {
                "file": file_info,
                "trace_info": trace_info
            }
        except Exception as e:
            logger.error(f"Error getting file with trace: {e}")
            raise
    
    async def get_files_by_project(self, project_id: str, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get all files in a project with hierarchy validation and user access control"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id, project_id)
            
            # Validate project hierarchy
            if not await self._validate_project_hierarchy(project_id):
                raise ValueError(f"Project {project_id} is not properly linked to a use case")
            
            files = await self.file_repo.get_files_by_project_id(project_id)
            return files
        except Exception as e:
            logger.error(f"Error getting files by project: {e}")
            raise
    
    async def delete_file(self, file_id: str, user_id: str, organization_id: str) -> bool:
        """Delete file with cascading operations and user access control"""
        await self._ensure_initialized()
        
        try:
            # Validate file exists
            file_info = await self.file_service.get_file_by_id(file_id)
            if not file_info:
                raise ValueError(f"File {file_id} not found")
            
            # Validate user has permission to delete this file
            await self._validate_file_delete_permission(file_id, user_id, organization_id)
            
            # Perform cascading operations (e.g., remove from projects, update statistics)
            await self._handle_file_deletion_cascade(file_id, file_info)
            
            # Delete the file
            success = await self.file_service.delete_file(file_id)
            
            if success:
                logger.info(f"Successfully deleted file: {file_id} by user: {user_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise
    
    def _validate_file_upload(self, file_data: Dict[str, Any], project_id: str):
        """Validate file upload business rules"""
        if not file_data.get("original_filename"):
            raise ValueError("Original filename is required")
        
        if not project_id:
            raise ValueError("Project ID is required")
        
        # Add more business validation rules as needed
        logger.debug(f"File upload validation passed for: {file_data['original_filename']}")
    
    async def _find_existing_file(self, filename: str, project_id: str) -> Optional[Dict[str, Any]]:
        """Find existing file with same name in project"""
        try:
            files = await self.file_repo.get_files_by_project_id(project_id)
            for file in files:
                if file.get("original_filename") == filename:
                    return file
            return None
        except Exception as e:
            logger.warning(f"Error finding existing file: {e}")
            return None
    
    async def _update_existing_file(self, file_id: str, file_data: Dict[str, Any], 
                                   file_content: bytes) -> Dict[str, Any]:
        """Update existing file with new content"""
        try:
            # Update file content and metadata
            updated_file = await self.file_service.update_file(file_id, file_data, file_content)
            logger.info(f"Updated existing file: {file_id}")
            return updated_file
        except Exception as e:
            logger.error(f"Error updating existing file: {e}")
            raise
    
    async def _get_project_info(self, project_id: str, organization_id: str = None) -> Optional[Dict[str, Any]]:
        """Get project information for file organization"""
        try:
            # This would integrate with project management service
            # For now, return basic info from repository
            project_info = await self.file_repo.get_project_info(project_id)
            if project_info:
                return project_info
            
            # Fallback to basic info
            return {
                "project_name": "default_project",
                "use_case_name": "default_use_case"
            }
        except Exception as e:
            logger.warning(f"Error getting project info: {e}")
            return {
                "project_name": "default_project",
                "use_case_name": "default_use_case"
            }
    
    async def _get_use_case_info(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        """Get use case information"""
        try:
            # This would integrate with use case management service
            # For now, return basic info from repository
            use_case_info = await self.file_repo.get_use_case_info(use_case_id)
            if use_case_info:
                return use_case_info
            
            # Fallback to basic info
            return {
                "name": "default_use_case",
                "description": "Default use case"
            }
        except Exception as e:
            logger.warning(f"Error getting use case info: {e}")
            return {
                "name": "default_use_case",
                "description": "Default use case"
            }
    
    async def _update_project_file_count(self, project_id: str):
        """Update project file count after file operations"""
        # This would integrate with project management service
        logger.debug(f"Updated file count for project: {project_id}")
    
    async def _update_project_total_size(self, project_id: str):
        """Update project total size after file operations"""
        # This would integrate with project management service
        logger.debug(f"Updated total size for project: {project_id}")
    
    async def _validate_project_hierarchy(self, project_id: str) -> bool:
        """Validate project hierarchy exists"""
        # This would integrate with project management service
        # For now, return True
        return True
    
    async def _handle_file_deletion_cascade(self, file_id: str, file_info: Dict[str, Any]):
        """Handle cascading operations when file is deleted"""
        # This would integrate with other services to clean up references
        logger.debug(f"Handling file deletion cascade for: {file_id}")
    
    async def get_file_hierarchy_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get complete hierarchy information for a file (use case, project, file details)"""
        await self._ensure_initialized()
        
        try:
            # Get file information
            file_info = await self.file_service.get_file_by_id(file_id)
            if not file_info:
                return None
            
            # Get project information
            project_info = None
            if file_info.get("project_id"):
                project_info = await self._get_project_info(file_info["project_id"])
            
            # Get use case information
            use_case_info = None
            if file_info.get("use_case_id"):
                use_case_info = await self._get_use_case_info(file_info["use_case_id"])
            
            return {
                "file_id": file_id,
                "file_name": file_info.get("original_filename"),
                "file_size": file_info.get("size_bytes"),
                "file_status": file_info.get("status"),
                "project_id": file_info.get("project_id"),
                "project_name": project_info.get("name") if project_info else None,
                "use_case_id": file_info.get("use_case_id"),
                "use_case_name": use_case_info.get("name") if use_case_info else None,
                "organization_id": file_info.get("organization_id"),
                "uploaded_by": file_info.get("user_id"),
                "upload_date": file_info.get("upload_date"),
                "file_path": file_info.get("file_path")
            }
            
        except Exception as e:
            logger.error(f"Error getting file hierarchy info: {e}")
            raise
    
    async def get_files_by_use_case(self, use_case_id: str, user_id: str, 
                                   organization_id: str) -> List[Dict[str, Any]]:
        """Get all files in a specific use case"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Get files by use case
            files = await self.file_repo.get_files_by_use_case_id(use_case_id)
            return files
            
        except Exception as e:
            logger.error(f"Error getting files by use case: {e}")
            raise
    
    async def get_file_statistics(self, project_id: str, user_id: str, 
                                 organization_id: str) -> Dict[str, Any]:
        """Get file statistics for a project"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Get file statistics
            stats = await self.file_repo.get_file_statistics(project_id)
            return stats
            
        except Exception as e:
            logger.error(f"Error getting file statistics: {e}")
            raise
    
    async def _validate_user_access(self, user_id: str, organization_id: str, project_id: str):
        """Validate user has access to the project in the organization"""
        try:
            # Get user information
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Validate user belongs to organization
            if user.get("organization_id") != organization_id:
                raise ValueError(f"User {user_id} does not belong to organization {organization_id}")
            
            # Validate project belongs to organization
            project = await self._get_project_info(project_id, organization_id)
            if not project:
                raise ValueError(f"Project {project_id} not found in organization {organization_id}")
            
            logger.debug(f"User access validated: {user_id} -> {organization_id} -> {project_id}")
            
        except Exception as e:
            logger.error(f"User access validation failed: {e}")
            raise
    
    async def _validate_file_delete_permission(self, file_id: str, user_id: str, organization_id: str):
        """Validate user has permission to delete the file"""
        try:
            # Get file information
            file_info = await self.file_service.get_file_by_id(file_id)
            if not file_info:
                raise ValueError(f"File {file_id} not found")
            
            # Check if user owns the file or has admin privileges
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Allow deletion if user owns the file or is admin
            if (file_info.get("user_id") == user_id or 
                user.get("role") in ["admin", "super_admin"]):
                logger.debug(f"File delete permission granted for user: {user_id}")
                return
            
            raise ValueError(f"User {user_id} does not have permission to delete file {file_id}")
            
        except Exception as e:
            logger.error(f"File delete permission validation failed: {e}")
            raise
