"""
AI/RAG Project Management Service
Handles project and file management operations using the central data management system.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from pathlib import Path

# Import central data management system
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.project_repository import ProjectRepository
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.use_case_repository import UseCaseRepository
# Migrated to new twin registry system
from src.modules.twin_registry.core.twin_registry_service import TwinRegistryService as CoreTwinRegistryService
from src.shared.services.project_service import ProjectService as SharedProjectService
from src.shared.services.file_service import FileService
from src.shared.services.use_case_service import UseCaseService
from src.modules.twin_registry.core.twin_lifecycle_service import TwinLifecycleService

logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self):
        """Initialize project service using central data management system"""
        # Create data directory and set database path
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        # Initialize central database connection
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        
        # Initialize repositories
        self.project_repo = ProjectRepository(self.db_manager)
        self.file_repo = FileRepository(self.db_manager)
        self.use_case_repo = UseCaseRepository(self.db_manager)
        # Migrated to new twin registry system
        self.twin_registry_service = CoreTwinRegistryService()
        
        # Initialize shared services
        self.shared_project_service = SharedProjectService(
            self.db_manager, 
            self.use_case_repo, 
            self.file_repo
        )
        self.file_service = FileService(
            self.db_manager,
            self.project_repo,
            self.digital_twin_repo
        )
        self.use_case_service = UseCaseService(
            self.db_manager,
            self.project_repo
        )
        # Migrated to new twin registry system
        self.twin_lifecycle_service = TwinLifecycleService()
        
        logger.info("AI/RAG Project Service initialized with complete central data management system")
    
    def get_projects(self) -> Dict[str, Any]:
        """Get list of available projects using central system"""
        try:
            logger.info("🔍 Getting available projects from central system...")
            
            # Use shared project service to get all projects
            projects = self.shared_project_service.get_all()
            
            # Convert to list of dictionaries
            project_list = []
            for project in projects:
                project_dict = project.to_dict() if hasattr(project, 'to_dict') else project
                project_list.append(project_dict)
            
            return {
                "projects": project_list,
                "count": len(project_list),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            raise e
    
    def get_project_files(self, project_id: str) -> Dict[str, Any]:
        """Get files for a specific project using central system"""
        try:
            logger.info(f"🔍 Getting files for project: {project_id}")
            
            # Use shared project service to get project with files
            project_with_files = self.shared_project_service.get_project_with_files(project_id)
            
            if project_with_files:
                return {
                    "project_id": project_id,
                    "files": project_with_files.get("files", []),
                    "count": project_with_files.get("file_count", 0),
                    "total_size": project_with_files.get("total_size", 0),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "project_id": project_id,
                    "files": [],
                    "count": 0,
                    "total_size": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error getting project files: {e}")
            raise e
    
    def get_project_details(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific project"""
        try:
            logger.info(f"🔍 Getting project details for: {project_id}")
            
            # Use shared project service to get project with hierarchy info
            project_hierarchy = self.shared_project_service.get_project_hierarchy_info(project_id)
            
            if project_hierarchy:
                return project_hierarchy
            else:
                return None
            
        except Exception as e:
            logger.error(f"Error getting project details: {e}")
            raise e
    
    def create_project(self, project_data: Dict[str, Any], use_case_id: str) -> str:
        """Create a new project using central system"""
        try:
            logger.info(f"🔧 Creating new project: {project_data.get('name', 'Unknown')}")
            
            # Use shared project service to create project
            project = self.shared_project_service.create_project(project_data, use_case_id)
            
            return project.project_id
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise e
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing project using central system"""
        try:
            logger.info(f"🔧 Updating project: {project_id}")
            
            # Use shared project service to update project
            success = self.shared_project_service.update(project_id, updates)
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            raise e
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project using central system"""
        try:
            logger.info(f"🗑️ Deleting project: {project_id}")
            
            # Use shared project service to delete project
            success = self.shared_project_service.delete(project_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            raise e
    
    def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a specific project"""
        try:
            logger.info(f"📊 Getting statistics for project: {project_id}")
            
            # Use shared project service to get project with files
            project_with_files = self.shared_project_service.get_project_with_files(project_id)
            
            if project_with_files:
                return {
                    "project_id": project_id,
                    "file_count": project_with_files.get("file_count", 0),
                    "total_size": project_with_files.get("total_size", 0),
                    "last_updated": datetime.now().isoformat(),
                    "status": "available"
                }
            else:
                return {
                    "project_id": project_id,
                    "file_count": 0,
                    "total_size": 0,
                    "last_updated": None,
                    "status": "not_found"
                }
            
        except Exception as e:
            logger.error(f"Error getting project statistics: {e}")
            raise e
    
    def validate_project(self, project_id: str) -> Dict[str, Any]:
        """Validate project structure and files using central system"""
        try:
            logger.info(f"🔍 Validating project: {project_id}")
            
            # Use shared project service to validate project hierarchy
            is_valid = self.shared_project_service.validate_project_hierarchy(project_id)
            
            if is_valid:
                return {
                    "project_id": project_id,
                    "valid": True,
                    "errors": [],
                    "warnings": []
                }
            else:
                return {
                    "project_id": project_id,
                    "valid": False,
                    "errors": ["Project hierarchy validation failed"],
                    "warnings": []
                }
            
        except Exception as e:
            logger.error(f"Error validating project: {e}")
            return {
                "project_id": project_id,
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            } 

    def get_file_with_complete_context(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete context for a file using all src/shared/ methods.
        This is the core method for reverse engineering capability.
        """
        try:
            logger.info(f"🔍 Getting complete context for file: {file_id}")
            
            # Get file trace information
            file_trace = self.file_service.get_file_with_trace(file_id)
            if not file_trace:
                logger.warning(f"File {file_id} not found")
                return None
            
            file_info = file_trace.get("file")
            trace_info = file_trace.get("trace_info", {})
            
            # Get project context
            project_context = None
            if file_info and hasattr(file_info, 'project_id'):
                project_context = self.shared_project_service.get_project_hierarchy_info(file_info.project_id)
            
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
            
            logger.info(f"✅ Complete context retrieved for file: {file_id}")
            return complete_context
            
        except Exception as e:
            logger.error(f"Error getting complete file context for {file_id}: {e}")
            return None

    def get_file_trace(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file trace information using FileService."""
        try:
            file_trace = self.file_service.get_file_with_trace(file_id)
            return file_trace
        except Exception as e:
            logger.error(f"Error getting file trace for {file_id}: {e}")
            return None

    def get_project_context_for_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get project context for a specific file."""
        try:
            # First get file info to get project_id
            file_trace = self.file_service.get_file_with_trace(file_id)
            if not file_trace or not file_trace.get("file"):
                return None
            
            file_info = file_trace["file"]
            if not hasattr(file_info, 'project_id'):
                return None
            
            # Get project hierarchy info
            project_context = self.shared_project_service.get_project_hierarchy_info(file_info.project_id)
            return project_context
            
        except Exception as e:
            logger.error(f"Error getting project context for file {file_id}: {e}")
            return None

    def get_use_case_context_for_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get use case context for a specific file."""
        try:
            # Get project context first
            project_context = self.get_project_context_for_file(file_id)
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

    def get_digital_twin_context_for_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get digital twin context for a specific file."""
        try:
            digital_twin = self.digital_twin_service.get_twin_by_file_id(file_id)
            if digital_twin:
                return digital_twin.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting digital twin context for file {file_id}: {e}")
            return None

    def get_related_files_for_file(self, file_id: str) -> List[Dict[str, Any]]:
        """Get related files for a specific file (same project)."""
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

    def search_files_by_content(self, search_term: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search files by content using FileRepository."""
        try:
            files = self.file_repo.search_files(search_term)
            if project_id:
                # Filter by project if specified
                files = [f for f in files if hasattr(f, 'project_id') and f.project_id == project_id]
            
            return [f.to_dict() for f in files] if files else []
            
        except Exception as e:
            logger.error(f"Error searching files with term '{search_term}': {e}")
            return []

    def get_digital_twin_health_for_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get digital twin health information for a file."""
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

    def get_use_case_projects(self, use_case_id: str) -> List[Dict[str, Any]]:
        """Get all projects in a use case."""
        try:
            projects = self.shared_project_service.get_projects_by_use_case(use_case_id)
            return [p.to_dict() for p in projects] if projects else []
            
        except Exception as e:
            logger.error(f"Error getting use case projects for use case {use_case_id}: {e}")
            return [] 