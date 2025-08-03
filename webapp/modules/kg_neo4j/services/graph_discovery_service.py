"""
Graph Discovery Service
======================

Service for discovering graph data files using existing digital twin information.
Uses the centralized database and digital twin extracted_data_path to find graph files.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository
from src.shared.repositories.use_case_repository import UseCaseRepository
from src.shared.services.digital_twin_service import DigitalTwinService
from src.shared.services.file_service import FileService
from src.shared.services.use_case_service import UseCaseService
from src.shared.services.project_service import ProjectService


class GraphDiscoveryService:
    """Service for discovering graph data files using existing database hierarchy."""
    
    def __init__(self):
        from src.shared.database.connection_manager import DatabaseConnectionManager
        
        # Initialize database connection
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        
        # Initialize repositories
        self.twin_repo = DigitalTwinRepository(self.db_manager)
        self.file_repo = FileRepository(self.db_manager)
        self.project_repo = ProjectRepository(self.db_manager)
        self.use_case_repo = UseCaseRepository(self.db_manager)
        
        # Initialize services
        self.digital_twin_service = DigitalTwinService(self.db_manager, self.file_repo, self.project_repo)
        self.file_service = FileService(self.db_manager, self.project_repo, self.twin_repo)
        self.use_case_service = UseCaseService(self.db_manager, self.project_repo)
        self.project_service = ProjectService(self.db_manager, self.use_case_repo, self.file_repo)
    
    def discover_use_cases_with_graphs(self) -> List[Dict[str, Any]]:
        """Discover all use cases that have graph data files."""
        try:
            use_cases = self.use_case_service.get_all()
            use_cases_with_graphs = []
            
            for use_case in use_cases:
                # Get projects for this use case
                projects = self.project_service.get_projects_by_use_case(use_case.use_case_id)
                
                # Check if any project has graph files
                has_graphs = False
                graph_count = 0
                
                for project in projects:
                    project_graphs = self.discover_projects_with_graphs(use_case.use_case_id)
                    if project_graphs:
                        has_graphs = True
                        graph_count += len(project_graphs)
                
                if has_graphs:
                    use_cases_with_graphs.append({
                        "use_case_id": use_case.use_case_id,
                        "use_case_name": use_case.name,
                        "category": use_case.category,
                        "graph_count": graph_count,
                        "project_count": len(projects)
                    })
            
            return use_cases_with_graphs
            
        except Exception as e:
            print(f"❌ Error discovering use cases with graphs: {e}")
            return []
    
    def get_all_use_cases(self) -> List[Dict[str, Any]]:
        """Get all use cases regardless of graph data availability."""
        try:
            print("🔍 Starting get_all_use_cases...")
            # Get use cases from database (same approach as AASX module)
            use_cases = self.use_case_repo.get_all()
            print(f"📊 Found {len(use_cases)} use cases from repository")
            
            # Transform to API format
            api_use_cases = []
            for i, use_case in enumerate(use_cases):
                print(f"🔍 Processing use case {i+1}/{len(use_cases)}: {use_case.use_case_id} - {use_case.name}")
                
                # Get projects for this use case
                projects = self.project_service.get_projects_by_use_case(use_case.use_case_id)
                print(f"📁 Found {len(projects)} projects for use case {use_case.use_case_id}")
                
                # Check if any project has graph files
                has_graphs = False
                graph_count = 0
                
                for project in projects:
                    # Get files for this project
                    files = self.file_service.get_files_by_project(project.project_id)
                    
                    # Check if any file has graph data
                    for file in files:
                        graph_status = self.get_graph_file_status(file.file_id)
                        if graph_status["import_status"] == "imported":
                            has_graphs = True
                            graph_count += 1
                
                # Get category icon based on category (same as AASX module)
                category_icons = {
                    'thermal': 'fas fa-fire',
                    'structural': 'fas fa-cube', 
                    'fluid_dynamics': 'fas fa-water',
                    'multi_physics': 'fas fa-atom',
                    'industrial': 'fas fa-industry',
                    'general': 'fas fa-chart-line'
                }
                
                # Extract metadata if it exists
                metadata = {}
                if hasattr(use_case, 'metadata') and use_case.metadata:
                    if isinstance(use_case.metadata, str):
                        import json
                        try:
                            metadata = json.loads(use_case.metadata)
                        except:
                            metadata = {}
                    elif isinstance(use_case.metadata, dict):
                        metadata = use_case.metadata
                
                api_use_case = {
                    "use_case_id": use_case.use_case_id,
                    "use_case_name": use_case.name,
                    "description": use_case.description,
                    "category": use_case.category,
                    "icon": category_icons.get(use_case.category, 'fas fa-cog'),
                    "industry": metadata.get('industry'),
                    "complexity": metadata.get('complexity'),
                    "expected_duration": metadata.get('expected_duration'),
                    "data_points": metadata.get('data_points'),
                    "physics_type": metadata.get('physics_type'),
                    "tags": metadata.get('tags', []),
                    "famous_examples": metadata.get('famous_examples', []),
                    "optimization_targets": metadata.get('optimization_targets', []),
                    "materials": metadata.get('materials', []),
                    "graph_count": graph_count,
                    "project_count": len(projects),
                    "has_graphs": has_graphs
                }
                print(f"✅ Added use case: {api_use_case['use_case_name']}")
                api_use_cases.append(api_use_case)
            
            print(f"🎯 Returning {len(api_use_cases)} use cases")
            return api_use_cases
            
        except Exception as e:
            print(f"❌ Error getting all use cases: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def discover_projects_with_graphs(self, use_case_id: str) -> List[Dict[str, Any]]:
        """Discover all projects in a use case that have graph data files."""
        try:
            projects = self.project_service.get_projects_by_use_case(use_case_id)
            projects_with_graphs = []
            
            for project in projects:
                # Get files for this project
                files = self.file_service.get_files_by_project(project.project_id)
                
                # Check if any file has graph data
                has_graphs = False
                graph_files = []
                
                for file in files:
                    graph_status = self.get_graph_file_status(file.file_id)
                    if graph_status["import_status"] == "imported":
                        has_graphs = True
                        graph_files.append({
                            "file_id": file.file_id,
                            "filename": file.filename,
                            "original_filename": file.original_filename,
                            "graph_path": graph_status["graph_file_path"]
                        })
                
                if has_graphs:
                    projects_with_graphs.append({
                        "project_id": project.project_id,
                        "project_name": project.name,
                        "use_case_id": use_case_id,
                        "graph_count": len(graph_files),
                        "graph_files": graph_files
                    })
            
            return projects_with_graphs
            
        except Exception as e:
            print(f"❌ Error discovering projects with graphs: {e}")
            return []

    def get_all_projects_for_use_case(self, use_case_id: str) -> List[Dict[str, Any]]:
        """Get all projects for a use case regardless of graph data availability."""
        try:
            print(f"🔍 Getting all projects for use case: {use_case_id}")
            projects = self.project_service.get_projects_by_use_case(use_case_id)
            print(f"📊 Found {len(projects)} projects from repository")
            
            api_projects = []
            for project in projects:
                # Get files for this project
                files = self.file_service.get_files_by_project(project.project_id)
                
                # Check if any file has graph data
                has_graphs = False
                graph_count = 0
                
                for file in files:
                    graph_status = self.get_graph_file_status(file.file_id)
                    if graph_status["import_status"] == "imported":
                        has_graphs = True
                        graph_count += 1
                
                api_project = {
                    "project_id": project.project_id,
                    "project_name": project.name,
                    "use_case_id": use_case_id,
                    "file_count": len(files),
                    "graph_count": graph_count,
                    "has_graphs": has_graphs
                }
                print(f"✅ Added project: {api_project['project_name']}")
                api_projects.append(api_project)
            
            print(f"🎯 Returning {len(api_projects)} projects")
            return api_projects
            
        except Exception as e:
            print(f"❌ Error getting all projects for use case {use_case_id}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def discover_files_with_graphs(self, project_id: str) -> List[Dict[str, Any]]:
        """Discover all files in a project that have graph data files."""
        try:
            files = self.file_service.get_files_by_project(project_id)
            files_with_graphs = []
            
            for file in files:
                graph_status = self.get_graph_file_status(file.file_id)
                if graph_status["import_status"] == "imported":
                    files_with_graphs.append({
                        "file_id": file.file_id,
                        "filename": file.filename,
                        "original_filename": file.original_filename,
                        "graph_path": graph_status["graph_file_path"],
                        "graph_stats": graph_status["graph_stats"],
                        "import_date": graph_status["import_date"]
                    })
            
            return files_with_graphs
            
        except Exception as e:
            print(f"❌ Error discovering files with graphs: {e}")
            return []

    def get_all_files_for_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all processed files for a project (files with status 'processed')."""
        try:
            print(f"🔍 Getting processed files for project: {project_id}")
            files = self.file_service.get_files_by_project(project_id)
            print(f"📊 Found {len(files)} files from repository")
            
            api_files = []
            for file in files:
                # Check if file status is 'processed' in database
                if file.status == "processed":
                    # Remove file extension for display
                    filename_without_ext = Path(file.filename).stem
                    
                    api_file = {
                        "file_id": file.file_id,
                        "filename": filename_without_ext,  # Display name without extension
                        "original_filename": file.original_filename,
                        "full_filename": file.filename,  # Keep full filename for reference
                        "has_graph": True,
                        "import_date": file.upload_date
                    }
                    print(f"✅ Added processed file: {api_file['filename']}")
                    api_files.append(api_file)
                else:
                    print(f"⏭️ Skipping unprocessed file: {file.filename} (status: {file.status})")
            
            print(f"🎯 Returning {len(api_files)} processed files")
            return api_files
            
        except Exception as e:
            print(f"❌ Error getting all files for project {project_id}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_graph_file_status(self, file_id: str) -> Dict[str, Any]:
        """Get graph file status for a specific file using digital twin data."""
        try:
            # Get digital twin for this file
            twin = self.digital_twin_service.get_twin_by_file_id(file_id)
            
            if not twin or not twin.extracted_data_path:
                return {
                    "file_id": file_id,
                    "import_status": "not_imported",
                    "graph_file_path": None,
                    "graph_stats": {"nodes": 0, "relationships": 0},
                    "import_date": None
                }
            
            # Build graph file path from extracted_data_path
            extracted_path = Path(twin.extracted_data_path)
            filename_without_ext = Path(twin.extracted_data_path).name
            graph_file_path = extracted_path / f"{filename_without_ext}_graph.json"
            
            # Check if graph file exists
            if graph_file_path.exists():
                # Read graph statistics
                try:
                    with open(graph_file_path, 'r') as f:
                        graph_data = json.load(f)
                        graph_stats = {
                            "nodes": len(graph_data.get("nodes", [])),
                            "relationships": len(graph_data.get("edges", []))
                        }
                except Exception:
                    graph_stats = {"nodes": 0, "relationships": 0}
                
                return {
                    "file_id": file_id,
                    "import_status": "imported",
                    "graph_file_path": str(graph_file_path),
                    "graph_stats": graph_stats,
                    "import_date": twin.last_health_check
                }
            else:
                return {
                    "file_id": file_id,
                    "import_status": "not_imported",
                    "graph_file_path": str(graph_file_path),
                    "graph_stats": {"nodes": 0, "relationships": 0},
                    "import_date": None
                }
                
        except Exception as e:
            print(f"❌ Error getting graph file status for {file_id}: {e}")
            return {
                "file_id": file_id,
                "import_status": "error",
                "graph_file_path": None,
                "graph_stats": {"nodes": 0, "relationships": 0},
                "import_date": None,
                "error": str(e)
            }
    
    def validate_graph_file(self, file_id: str) -> bool:
        """Validate if a graph file exists and has correct format."""
        try:
            graph_status = self.get_graph_file_status(file_id)
            
            if graph_status["import_status"] != "imported":
                return False
            
            graph_path = Path(graph_status["graph_file_path"])
            if not graph_path.exists():
                return False
            
            # Validate JSON format
            try:
                with open(graph_path, 'r') as f:
                    graph_data = json.load(f)
                
                # Check for required fields
                if not isinstance(graph_data, dict):
                    return False
                
                # Check if it has nodes or edges (basic graph structure)
                if not (graph_data.get("nodes") or graph_data.get("edges")):
                    return False
                
                return True
                
            except (json.JSONDecodeError, IOError):
                return False
                
        except Exception as e:
            print(f"❌ Error validating graph file for {file_id}: {e}")
            return False
    
    def get_hierarchical_availability_status(self) -> Dict[str, Any]:
        """Get overall availability status for all graph data."""
        try:
            # Get all use cases (for total count)
            all_use_cases = self.get_all_use_cases()
            total_use_cases = len(all_use_cases)
            
            # Get use cases with graphs (for graph-specific info)
            use_cases_with_graphs = self.discover_use_cases_with_graphs()
            total_graph_files = sum(uc["graph_count"] for uc in use_cases_with_graphs)
            
            return {
                "total_use_cases": total_use_cases,
                "total_graph_files": total_graph_files,
                "use_cases_with_graphs": use_cases_with_graphs,
                "status": "available" if total_graph_files > 0 else "no_graphs"
            }
            
        except Exception as e:
            print(f"❌ Error getting hierarchical availability status: {e}")
            return {
                "total_use_cases": 0,
                "total_graph_files": 0,
                "use_cases_with_graphs": [],
                "status": "error",
                "error": str(e)
            }
    
    def get_graph_file_path(self, file_id: str) -> Optional[Path]:
        """Get the graph file path for a specific file."""
        try:
            graph_status = self.get_graph_file_status(file_id)
            
            if graph_status["import_status"] == "imported" and graph_status["graph_file_path"]:
                return Path(graph_status["graph_file_path"])
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting graph file path for {file_id}: {e}")
            return None 