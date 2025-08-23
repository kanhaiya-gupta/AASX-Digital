"""
Enhanced AI/RAG Services
========================

Enhanced services that integrate with src/shared/ methods to provide
complete reverse engineering capability for AI/RAG system.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import src/shared/ services and repositories
from src.shared.services.file_service import FileService
from src.shared.services.project_service import ProjectService
from src.shared.services.use_case_service import UseCaseService
# Migrated to new twin registry system
from src.twin_registry.core.twin_registry_service import TwinRegistryService as CoreTwinRegistryService
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository
from src.shared.repositories.use_case_repository import UseCaseRepository
from src.twin_registry.core.twin_lifecycle_service import TwinLifecycleService

logger = logging.getLogger(__name__)

class EnhancedQueryService:
    """
    Enhanced query service that integrates with src/shared/ methods
    to provide complete reverse engineering capability.
    """
    
    def __init__(self, db_manager):
        """Initialize enhanced query service with all src/shared/ services."""
        self.db_manager = db_manager
        
        # Initialize repositories
        self.file_repository = FileRepository(db_manager)
        self.project_repository = ProjectRepository(db_manager)
        self.use_case_repository = UseCaseRepository(db_manager)
        # Migrated to new twin registry system
        self.twin_registry_service = CoreTwinRegistryService()
        
        # Initialize services with repositories
        self.file_service = FileService(
            db_manager, 
            self.project_repository, 
            self.digital_twin_repository
        )
        self.project_service = ProjectService(
            db_manager,
            self.use_case_repository,
            self.file_repository
        )
        self.use_case_service = UseCaseService(
            db_manager,
            self.project_repository
        )
        # Migrated to new twin registry system
        self.twin_lifecycle_service = TwinLifecycleService()
        
        logger.info("Enhanced Query Service initialized with all src/shared/ services")
    
    async def get_complete_file_context(self, file_id: str) -> Dict[str, Any]:
        """
        Get complete context for a file using all src/shared/ methods.
        
        Args:
            file_id: The file ID to get context for
            
        Returns:
            Complete file context including trace, project, use case, and twin info
        """
        try:
            logger.info(f"Getting complete context for file: {file_id}")
            
            # Get file trace information
            file_trace = self.file_service.get_file_with_trace(file_id)
            if not file_trace:
                raise ValueError(f"File {file_id} not found")
            
            file_info = file_trace.get("file")
            trace_info = file_trace.get("trace_info", {})
            
            # Get project context
            project_context = None
            if file_info and hasattr(file_info, 'project_id'):
                project_context = self.project_service.get_project_hierarchy_info(file_info.project_id)
            
            # Get use case context
            use_case_context = None
            if project_context and project_context.get("use_cases"):
                primary_use_case = project_context["use_cases"][0]
                use_case_context = self.use_case_service.get_use_case_with_projects(
                    primary_use_case["use_case_id"]
                )
            
            # Get digital twin context
            digital_twin = self.digital_twin_service.get_twin_by_file_id(file_id)
            
            # Get related files
            related_files = []
            if file_info and hasattr(file_info, 'project_id'):
                related_files = self.file_service.get_files_by_project(file_info.project_id)
            
            # Get file statistics
            file_statistics = self.file_service.get_file_statistics(
                file_info.project_id if file_info else None
            )
            
            # Build complete context
            complete_context = {
                "file_trace": {
                    "file_info": file_info.to_dict() if file_info else None,
                    "trace_info": trace_info
                },
                "project_context": project_context,
                "use_case_context": use_case_context,
                "digital_twin": digital_twin.to_dict() if digital_twin else None,
                "related_files": [f.to_dict() for f in related_files] if related_files else [],
                "statistics": file_statistics,
                "complete_trace": {
                    "file_id": file_id,
                    "project_id": file_info.project_id if file_info else None,
                    "use_case_id": primary_use_case["use_case_id"] if project_context and project_context.get("use_cases") else None,
                    "twin_id": digital_twin.twin_id if digital_twin else None
                }
            }
            
            logger.info(f"Complete context retrieved for file: {file_id}")
            return complete_context
            
        except Exception as e:
            logger.error(f"Error getting complete file context for {file_id}: {e}")
            raise
    
    async def get_file_trace(self, file_id: str) -> Dict[str, Any]:
        """Get file trace information using FileService."""
        try:
            file_trace = self.file_service.get_file_with_trace(file_id)
            return file_trace
        except Exception as e:
            logger.error(f"Error getting file trace for {file_id}: {e}")
            raise
    
    async def get_project_context(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get project context for a file."""
        try:
            # First get file info to get project_id
            file_trace = self.file_service.get_file_with_trace(file_id)
            if not file_trace or not file_trace.get("file"):
                return None
            
            file_info = file_trace["file"]
            if not hasattr(file_info, 'project_id'):
                return None
            
            # Get project hierarchy info
            project_context = self.project_service.get_project_hierarchy_info(file_info.project_id)
            return project_context
            
        except Exception as e:
            logger.error(f"Error getting project context for file {file_id}: {e}")
            return None
    
    async def get_use_case_context(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get use case context for a file."""
        try:
            # Get project context first
            project_context = await self.get_project_context(file_id)
            if not project_context or not project_context.get("use_cases"):
                return None
            
            # Get primary use case
            primary_use_case = project_context["use_cases"][0]
            use_case_context = self.use_case_service.get_use_case_with_projects(
                primary_use_case["use_case_id"]
            )
            return use_case_context
            
        except Exception as e:
            logger.error(f"Error getting use case context for file {file_id}: {e}")
            return None
    
    async def get_digital_twin_context(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get digital twin context for a file."""
        try:
            digital_twin = self.digital_twin_service.get_twin_by_file_id(file_id)
            if digital_twin:
                return digital_twin.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting digital twin context for file {file_id}: {e}")
            return None
    
    async def get_related_files(self, file_id: str) -> List[Dict[str, Any]]:
        """Get related files for a file (same project)."""
        try:
            # Get file info to get project_id
            file_trace = self.file_service.get_file_with_trace(file_id)
            if not file_trace or not file_trace.get("file"):
                return []
            
            file_info = file_trace["file"]
            if not hasattr(file_info, 'project_id'):
                return []
            
            # Get all files in the same project
            related_files = self.file_service.get_files_by_project(file_info.project_id)
            return [f.to_dict() for f in related_files] if related_files else []
            
        except Exception as e:
            logger.error(f"Error getting related files for file {file_id}: {e}")
            return []
    
    async def get_file_statistics(self, file_id: str) -> Dict[str, Any]:
        """Get file statistics."""
        try:
            # Get file info to get project_id
            file_trace = self.file_service.get_file_with_trace(file_id)
            if not file_trace or not file_trace.get("file"):
                return {}
            
            file_info = file_trace["file"]
            if not hasattr(file_info, 'project_id'):
                return {}
            
            # Get file statistics for the project
            statistics = self.file_service.get_file_statistics(file_info.project_id)
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting file statistics for file {file_id}: {e}")
            return {}
    
    async def search_files_by_content(self, search_term: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search files by content using FileRepository."""
        try:
            files = self.file_repository.search_files(search_term)
            if project_id:
                # Filter by project if specified
                files = [f for f in files if hasattr(f, 'project_id') and f.project_id == project_id]
            
            return [f.to_dict() for f in files] if files else []
            
        except Exception as e:
            logger.error(f"Error searching files with term '{search_term}': {e}")
            return []
    
    async def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all files in a project."""
        try:
            files = self.file_service.get_files_by_project(project_id)
            return [f.to_dict() for f in files] if files else []
            
        except Exception as e:
            logger.error(f"Error getting project files for project {project_id}: {e}")
            return []
    
    async def get_use_case_projects(self, use_case_id: str) -> List[Dict[str, Any]]:
        """Get all projects in a use case."""
        try:
            projects = self.project_service.get_projects_by_use_case(use_case_id)
            return [p.to_dict() for p in projects] if projects else []
            
        except Exception as e:
            logger.error(f"Error getting use case projects for use case {use_case_id}: {e}")
            return []
    
    async def get_digital_twin_health(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get digital twin health information."""
        try:
            digital_twin = self.digital_twin_service.get_twin_by_file_id(file_id)
            if not digital_twin:
                return None
            
            # Perform health check
            health_result = self.digital_twin_service.perform_health_check(digital_twin.twin_id)
            return health_result
            
        except Exception as e:
            logger.error(f"Error getting digital twin health for file {file_id}: {e}")
            return None 