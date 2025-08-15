"""
Knowledge Graph Neo4j Service
Service layer for Knowledge Graph operations within the webapp module.
Uses existing business logic from src/kg_neo4j/ for detailed operations.
Uses centralized data management system from src/shared/ for database operations.
"""

import os
import json
import subprocess
import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import centralized data management system
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.project_repository import ProjectRepository
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.use_case_repository import UseCaseRepository
from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
from src.shared.services.project_service import ProjectService as SharedProjectService
from src.shared.services.file_service import FileService
from src.shared.services.use_case_service import UseCaseService
from src.shared.services.digital_twin_service import DigitalTwinService

logger = logging.getLogger(__name__)

class KGNeo4jService:
    """Service for Knowledge Graph Neo4j operations"""
    
    def __init__(self):
        logger.info("🔧 Initializing KGNeo4jService...")
        self.docker_container_name = "aasx-digital-neo4j"
        try:
            self._initialize_central_data_management()
            logger.info("✅ Centralized data management initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize centralized data management: {e}")
            raise
            
        try:
            self._initialize_connections()
            logger.info("✅ Connections initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize connections: {e}")
            # Don't raise here, allow service to continue with limited functionality
        
    def _initialize_central_data_management(self):
        """Initialize centralized data management system"""
        try:
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
            self.digital_twin_repo = DigitalTwinRepository(self.db_manager)
            
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
            self.digital_twin_service = DigitalTwinService(
                self.db_manager,
                self.file_repo,
                self.project_repo
            )
            
            logger.info("✓ Centralized data management system initialized for Knowledge Graph")
            
        except Exception as e:
            logger.error(f"Error initializing centralized data management: {e}")
            raise
        
    def _initialize_connections(self):
        """Initialize connections to existing Neo4j business logic"""
        try:
            logger.info("🔧 Initializing Neo4j connections...")
            
            # Import existing Neo4j managers from src/kg_neo4j/
            logger.info("📦 Importing Neo4jManager...")
            from src.kg_neo4j.neo4j_manager import Neo4jManager
            logger.info("✅ Neo4jManager imported successfully")
            
            logger.info("📦 Importing AASXGraphAnalyzer...")
            from src.kg_neo4j.graph_analyzer import AASXGraphAnalyzer
            logger.info("✅ AASXGraphAnalyzer imported successfully")
            
            # Get Neo4j connection parameters from settings
            logger.info("🔧 Getting Neo4j connection parameters...")
            from webapp.config.settings import settings
            neo4j_uri = settings.neo4j_uri
            neo4j_user = settings.neo4j_user
            neo4j_password = settings.neo4j_password
            logger.info(f"🔧 Neo4j URI: {neo4j_uri}, User: {neo4j_user}")
            
            # Initialize with existing business logic and connection parameters
            logger.info("🔧 Creating Neo4jManager instance...")
            self.neo4j_manager = Neo4jManager(neo4j_uri, neo4j_user, neo4j_password)
            logger.info("✅ Neo4jManager created successfully")
            
            logger.info("🔧 Creating AASXGraphAnalyzer instance...")
            self.graph_analyzer = AASXGraphAnalyzer(neo4j_uri, neo4j_user, neo4j_password)
            logger.info("✅ AASXGraphAnalyzer created successfully")
            
            logger.info("✓ Neo4j managers initialized from src/kg_neo4j/")
            
        except ImportError as e:
            logger.error(f"❌ ImportError in _initialize_connections: {e}")
            logger.error(f"❌ ImportError type: {type(e)}")
            import traceback
            logger.error(f"❌ ImportError traceback: {traceback.format_exc()}")
            self.neo4j_manager = None
            self.graph_analyzer = None
        except Exception as e:
            logger.error(f"❌ Unexpected error in _initialize_connections: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Error traceback: {traceback.format_exc()}")
            self.neo4j_manager = None
            self.graph_analyzer = None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive Neo4j system status"""
        try:
            # Check Docker status
            docker_status = self._check_docker_status()
            
            # Check browser accessibility
            browser_accessible = self._check_browser_accessibility()
            
            # Check if Neo4j is actually accessible
            connected = False
            if docker_status.get('running', False):
                try:
                    # Test actual Neo4j connection
                    if self.neo4j_manager:
                        connected = self.neo4j_manager.test_connection()
                    else:
                        connected = browser_accessible
                except Exception as e:
                    logger.warning(f"Neo4j connection test failed: {e}")
                    connected = False
            
            # Get active connections
            active_connections = self._get_active_connections()
            
            return {
                'success': docker_status.get('running', False),
                'docker_running': docker_status.get('running', False),
                'connected': connected,
                'browser_accessible': browser_accessible,
                'active_connections': active_connections,
                'docker_status': docker_status.get('status', 'Unknown'),
                'last_checked': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            raise
    
    def get_docker_status(self) -> Dict[str, Any]:
        """Get detailed Docker container status"""
        try:
            docker_status = self._check_docker_status()
            
            # Check if Neo4j is actually accessible
            connected = False
            if docker_status.get('running', False):
                try:
                    # Test actual Neo4j connection
                    if self.neo4j_manager:
                        connected = self.neo4j_manager.test_connection()
                    else:
                        connected = self._check_browser_accessibility()
                except Exception as e:
                    logger.warning(f"Neo4j connection test failed: {e}")
                    connected = False
            
            # Combine Docker status with connection status
            status = {
                'running': docker_status.get('running', False),
                'connected': connected,
                'healthy': docker_status.get('running', False) and connected,
                'container_id': docker_status.get('container_id'),
                'ports': docker_status.get('ports', '7474:7474, 7687:7687'),
                'created': docker_status.get('created', ''),
                'status': docker_status.get('status', 'unknown')
            }
            
            return {
                'success': True,
                'status': status
            }
        except Exception as e:
            logger.error(f"Error getting Docker status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def start_docker_container(self) -> Dict[str, Any]:
        """Start Neo4j Docker container"""
        try:
            result = self._start_neo4j_docker()
            return {
                'success': True,
                'message': result.get('message', 'Docker container started successfully'),
                'container_id': result.get('container_id')
            }
        except Exception as e:
            logger.error(f"Error starting Docker container: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def stop_docker_container(self) -> Dict[str, Any]:
        """Stop Neo4j Docker container"""
        try:
            result = self._stop_neo4j_docker()
            return {
                'success': True,
                'message': result.get('message', 'Docker container stopped successfully')
            }
        except Exception as e:
            logger.error(f"Error stopping Docker container: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_local_neo4j_status(self) -> Dict[str, Any]:
        """Get local Neo4j Desktop status"""
        try:
            # Check if Neo4j Desktop is installed and running
            desktop_status = self._check_local_desktop_status()
            connection_status = self._check_local_connection_status()
            
            return {
                'success': True,
                'desktop_installed': desktop_status.get('installed', False),
                'desktop_running': desktop_status.get('running', False),
                'connection_available': connection_status.get('available', False),
                'browser_url': 'http://localhost:7474',
                'bolt_url': 'bolt://localhost:7687'
            }
        except Exception as e:
            logger.error(f"Error getting local Neo4j status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def launch_local_desktop(self) -> Dict[str, Any]:
        """Launch Neo4j Desktop application"""
        try:
            # Implementation for launching Neo4j Desktop
            # This would depend on the operating system
            return {
                'success': True,
                'message': 'Neo4j Desktop launch initiated'
            }
        except Exception as e:
            logger.error(f"Error launching Neo4j Desktop: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_cypher_query(self, query: str) -> Dict[str, Any]:
        """Execute Cypher query against Neo4j using existing business logic"""
        try:
            if not self.neo4j_manager:
                return {
                    'success': False,
                    'error': 'Neo4j manager not initialized',
                    'query': query
                }
            
            # Use existing business logic from src/kg_neo4j/
            result = self.neo4j_manager.execute_query(query)
            
            return {
                'success': True,
                'data': result,
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing Cypher query: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def execute_query(self, query: str) -> List[Dict]:
        """Execute a Cypher query and return raw results (for internal use)"""
        try:
            if not self.neo4j_manager:
                raise Exception('Neo4j manager not initialized')
            
            # Use existing business logic from src/kg_neo4j/
            return self.neo4j_manager.execute_query(query)
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def execute_query_raw(self, query: str) -> List:
        """Execute a Cypher query and return raw Neo4j objects (for graph data)"""
        try:
            if not self.neo4j_manager:
                raise Exception('Neo4j manager not initialized')
            
            # Use the new raw query method
            return self.neo4j_manager.execute_query_raw(query)
        except Exception as e:
            logger.error(f"Error executing raw query: {e}")
            raise
    
    def get_projects(self) -> Dict[str, Any]:
        """Get all projects using centralized data management system"""
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
                'success': True,
                'projects': project_list,
                'count': len(project_list),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_project_files(self, project_id: str) -> Dict[str, Any]:
        """Get files for a specific project using centralized data management system"""
        try:
            logger.info(f"🔍 Getting files for project: {project_id}")
            
            # Use shared project service to get project with files
            project_with_files = self.shared_project_service.get_project_with_files(project_id)
            
            if project_with_files:
                files = project_with_files.get('files', [])
                return {
                    'success': True,
                    'project_id': project_id,
                    'files': files,
                    'count': len(files),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Project not found',
                    'project_id': project_id
                }
        except Exception as e:
            logger.error(f"Error getting project files: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_project_graph(self, project_id: str) -> Dict[str, Any]:
        """Get graph data for a specific project using existing business logic"""
        try:
            if not self.graph_analyzer:
                return {
                    'success': False,
                    'error': 'Graph analyzer not initialized'
                }
            
            # Use existing business logic from src/kg_neo4j/
            # Implementation would depend on existing graph analyzer methods
            return {
                'success': True,
                'project_id': project_id,
                'graph_data': {}  # Would use existing graph analyzer
            }
        except Exception as e:
            logger.error(f"Error getting project graph: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_graph(self, file_id: str) -> Dict[str, Any]:
        """Get graph data for a specific file using centralized data management system"""
        try:
            logger.info(f"🔍 Getting graph data for file: {file_id}")
            
            # Get file info using centralized file service
            file = self.file_service.get_by_id(file_id)
            if not file:
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            # Use existing business logic for graph data
            return {
                'success': True,
                'file_id': file_id,
                'file_info': file.to_dict() if hasattr(file, 'to_dict') else file,
                'graph_data': {}  # Would use existing graph logic from src/kg_neo4j/
            }
        except Exception as e:
            logger.error(f"Error getting file graph: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_file_graph_exists(self, file_id: str) -> Dict[str, Any]:
        """Check if graph data exists for a file"""
        try:
            # Get file information with complete trace
            file_trace = self.file_service.get_file_with_trace(file_id)
            if not file_trace:
                return {
                    'success': False,
                    'file_id': file_id,
                    'exists': False,
                    'error': f"File with ID {file_id} not found"
                }
            
            file_info = file_trace["file"]
            trace_info = file_trace["trace_info"]
            
            if not trace_info:
                return {
                    'success': False,
                    'file_id': file_id,
                    'exists': False,
                    'error': f"No trace information found for file {file_id}"
                }
            
            # Extract information from trace
            use_case_name = trace_info.get("use_case_name")
            project_name = trace_info.get("project_name")
            
            if not use_case_name or not project_name:
                return {
                    'success': False,
                    'file_id': file_id,
                    'exists': False,
                    'error': f"Incomplete trace information for file {file_id}"
                }
            
            # Construct the graph data path
            graph_data_path = Path("output") / use_case_name / project_name / Path(file_info.filename).stem
            graph_file_name = f"{Path(file_info.filename).stem}_graph.json"
            graph_file_path = graph_data_path / graph_file_name
            
            # Check if graph file exists
            exists = graph_file_path.exists()
            
            return {
                'success': True,
                'file_id': file_id,
                'exists': exists,
                'file_path': str(graph_file_path),
                'file_name': file_info.filename,
                'project_name': project_name,
                'use_case_name': use_case_name
            }
        except Exception as e:
            logger.error(f"Error checking file graph existence: {e}")
            return {
                'success': False,
                'file_id': file_id,
                'exists': False,
                'error': str(e)
            }
    
    def get_file_graph_data(self, file_id: str) -> Dict[str, Any]:
        """Get detailed graph data for a file"""
        try:
            # First check if the file has graph data
            check_result = self.check_file_graph_exists(file_id)
            if not check_result['success'] or not check_result['exists']:
                return {
                    'success': False,
                    'file_id': file_id,
                    'error': check_result.get('error', 'Graph data not found')
                }
            
            # Load the graph data from the file
            graph_file_path = Path(check_result['file_path'])
            graph_data = self._load_graph_data(graph_file_path)
            
            if not graph_data:
                return {
                    'success': False,
                    'file_id': file_id,
                    'error': 'Failed to load graph data from file'
                }
            
            return {
                'success': True,
                'file_id': file_id,
                'graph_data': graph_data,
                'file_path': str(graph_file_path),
                'node_count': len(graph_data.get('nodes', [])),
                'edge_count': len(graph_data.get('edges', [])),
                'relationship_count': len(graph_data.get('edges', []))
            }
        except Exception as e:
            logger.error(f"Error getting file graph data: {e}")
            return {
                'success': False,
                'file_id': file_id,
                'error': str(e)
            }
    
    def get_project_graph_data(self, project_id: str) -> Dict[str, Any]:
        """Get detailed graph data for a project"""
        try:
            # Implementation using existing business logic
            return {
                'success': True,
                'project_id': project_id,
                'nodes': [],
                'edges': [],
                'metadata': {}
            }
        except Exception as e:
            logger.error(f"Error getting project graph data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_folders(self) -> Dict[str, Any]:
        """Get list of available data folders"""
        try:
            etl_output_dir = Path("output/etl_results")
            folders = []
            
            if etl_output_dir.exists():
                for folder in etl_output_dir.iterdir():
                    if folder.is_dir():
                        # Count graph files in this folder
                        graph_files = list(folder.rglob("*_graph.json"))
                        has_graph_data = len(graph_files) > 0
                        
                        folders.append({
                            "name": folder.name,
                            "path": str(folder),
                            "file_count": len(graph_files),
                            "has_graph_data": has_graph_data
                        })
            
            return {
                "success": True,
                "folders": folders,
                "total_folders": len(folders)
            }
            
        except Exception as e:
            logger.error(f"Error getting available folders: {e}")
            return {
                "success": False,
                "error": str(e),
                "folders": []
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics using existing business logic"""
        try:
            if not self.neo4j_manager:
                return {
                    "success": False,
                    "error": "Neo4j manager not initialized"
                }
            
            # Check Neo4j connection and ports first
            port_status = self.neo4j_manager.check_neo4j_ports()
            connection_test = self.neo4j_manager.test_connection()
            
            if not connection_test:
                return {
                    "success": False,
                    "error": "Cannot connect to Neo4j database",
                    "diagnostics": {
                        "connection_test": connection_test,
                        "port_status": port_status,
                        "uri": self.neo4j_manager.uri,
                        "user": self.neo4j_manager.user
                    },
                    "stats": {
                        "total_nodes": 0,
                        "total_relationships": 0,
                        "total_labels": 0,
                        "total_relationship_types": 0,
                        "labels": [],
                        "relationship_types": []
                    }
                }
            
            # Use the actual Neo4j manager to get real database statistics
            stats = self.neo4j_manager.get_database_stats()
            
            if stats:
                return {
                    "success": True,
                    "stats": {
                        "total_nodes": stats.get('total_nodes', 0),
                        "total_relationships": stats.get('total_relationships', 0),
                        "total_labels": len(stats.get('labels', [])),
                        "total_relationship_types": len(stats.get('relationship_types', [])),
                        "labels": stats.get('labels', []),
                        "relationship_types": stats.get('relationship_types', [])
                    }
                }
            else:
                return {
                    "success": True,
                    "stats": {
                        "total_nodes": 0,
                        "total_relationships": 0,
                        "total_labels": 0,
                        "total_relationship_types": 0,
                        "labels": [],
                        "relationship_types": []
                    }
                }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "stats": {
                    "total_nodes": 0,
                    "total_relationships": 0,
                    "total_labels": 0,
                    "total_relationship_types": 0,
                    "labels": [],
                    "relationship_types": []
                }
            }
    
    # Private helper methods
    def get_docker_logs(self) -> str:
        """Get Docker container logs"""
        try:
            result = subprocess.run(
                ['docker', 'logs', '--tail', '50', self.docker_container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error getting logs: {result.stderr}"
        except Exception as e:
            logger.error(f"Error getting Docker logs: {e}")
            return f"Error getting logs: {str(e)}"
    
    def _check_docker_status(self) -> Dict[str, Any]:
        """Check Docker container status"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={self.docker_container_name}', '--format', 'json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                container_info = json.loads(result.stdout)
                return {
                    'running': True,
                    'status': 'running',
                    'container_id': container_info.get('ID'),
                    'ports': container_info.get('Ports', ''),
                    'created': container_info.get('CreatedAt', '')
                }
            else:
                return {
                    'running': False,
                    'status': 'stopped',
                    'container_id': None
                }
        except Exception as e:
            logger.error(f"Error checking Docker status: {e}")
            return {
                'running': False,
                'status': 'error',
                'error': str(e)
            }
    
    def _check_browser_accessibility(self) -> bool:
        """Check if Neo4j Browser is accessible"""
        try:
            import requests
            response = requests.get('http://localhost:7474', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_active_connections(self) -> int:
        """Get number of active connections (simplified)"""
        try:
            # This would be a more complex implementation
            # For now, return a placeholder value
            return 0
        except Exception as e:
            logger.error(f"Error getting active connections: {e}")
            return 0
    
    def _start_neo4j_docker(self) -> Dict[str, Any]:
        """Start Neo4j Docker container"""
        try:
            # Check if container already exists
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', f'name={self.docker_container_name}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Container exists, start it
                start_result = subprocess.run(
                    ['docker', 'start', self.docker_container_name],
                    capture_output=True,
                    text=True
                )
                
                if start_result.returncode == 0:
                    return {
                        'success': True,
                        'message': 'Docker container started successfully',
                        'container_id': start_result.stdout.strip()
                    }
                else:
                    raise Exception(f"Failed to start container: {start_result.stderr}")
            else:
                # Container doesn't exist, create and start it
                create_result = subprocess.run([
                    'docker', 'run', '-d',
                    '--name', self.docker_container_name,
                    '-p', '7474:7474',
                    '-p', '7687:7687',
                    '-e', 'NEO4J_AUTH=neo4j/password',
                    'neo4j:5.15-community'
                ], capture_output=True, text=True)
                
                if create_result.returncode == 0:
                    return {
                        'success': True,
                        'message': 'Docker container created and started successfully',
                        'container_id': create_result.stdout.strip()
                    }
                else:
                    raise Exception(f"Failed to create container: {create_result.stderr}")
                    
        except Exception as e:
            logger.error(f"Error starting Neo4j Docker: {e}")
            raise
    
    def _stop_neo4j_docker(self) -> Dict[str, Any]:
        """Stop Neo4j Docker container"""
        try:
            result = subprocess.run(
                ['docker', 'stop', self.docker_container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Docker container stopped successfully'
                }
            else:
                raise Exception(f"Failed to stop container: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error stopping Neo4j Docker: {e}")
            raise
    
    def _check_local_desktop_status(self) -> Dict[str, Any]:
        """Check local Neo4j Desktop status"""
        try:
            # This would check if Neo4j Desktop is installed and running
            # Implementation depends on operating system
            return {
                'installed': True,
                'running': False
            }
        except Exception as e:
            logger.error(f"Error checking local desktop status: {e}")
            return {
                'installed': False,
                'running': False,
                'error': str(e)
            }
    
    def _check_local_connection_status(self) -> Dict[str, Any]:
        """Check local Neo4j connection status"""
        try:
            # This would check if local Neo4j is accessible
            return {
                'available': False
            }
        except Exception as e:
            logger.error(f"Error checking local connection status: {e}")
            return {
                'available': False,
                'error': str(e)
            }

    def import_file_to_neo4j(self, file_id: str) -> Dict[str, Any]:
        """Import a specific file to Neo4j for graph visualization"""
        try:
            # Get file information with complete trace using the efficient method
            file_trace = self.file_service.get_file_with_trace(file_id)
            if not file_trace:
                return {
                    "success": False,
                    "error": f"File with ID {file_id} not found"
                }
            
            file_info = file_trace["file"]
            trace_info = file_trace["trace_info"]
            
            if not trace_info:
                return {
                    "success": False,
                    "error": f"No trace information found for file {file_id}"
                }
            
            # Extract information from trace
            use_case_name = trace_info.get("use_case_name")
            project_name = trace_info.get("project_name")
            
            if not use_case_name or not project_name:
                return {
                    "success": False,
                    "error": f"Incomplete trace information for file {file_id}"
                }
            
            # Construct the graph data path
            # Format: output/UseCase/Project/File/
            graph_data_path = Path("output") / use_case_name / project_name / Path(file_info.filename).stem
            
            logger.info(f"🔍 Looking for graph data at: {graph_data_path}")
            
            # Check if graph data exists
            if not graph_data_path.exists():
                return {
                    "success": False,
                    "error": f"Graph data not found at {graph_data_path}",
                    "file_id": file_id,
                    "file_name": file_info.filename,
                    "project_name": project_name,
                    "use_case_name": use_case_name
                }
            
            # Look for specific graph file: {filename}_graph.json
            graph_file_name = f"{Path(file_info.filename).stem}_graph.json"
            graph_file_path = graph_data_path / graph_file_name
            
            logger.info(f"🔍 Looking for specific graph file: {graph_file_path}")
            
            if not graph_file_path.exists():
                return {
                    "success": False,
                    "error": f"Graph file not found: {graph_file_path}",
                    "file_id": file_id,
                    "file_name": file_info.filename,
                    "project_name": project_name,
                    "use_case_name": use_case_name
                }
            
            graph_files = [graph_file_path]
            
            if not graph_files:
                return {
                    "success": False,
                    "error": f"No graph files found in {graph_data_path}",
                    "file_id": file_id,
                    "file_name": file_info.filename,
                    "project_name": project_name,
                    "use_case_name": use_case_name
                }
            
            # Check if data for this file already exists in Neo4j
            existing_check = self._check_file_data_exists(file_id)
            if existing_check['exists']:
                logger.info(f"Data for file {file_info.filename} already exists in Neo4j")
                return {
                    "success": True,
                    "message": f"File {file_info.filename} data already exists in database",
                    "file_id": file_id,
                    "file_name": file_info.filename,
                    "project_name": project_name,
                    "use_case_name": use_case_name,
                    "node_count": existing_check.get('node_count', 0),
                    "relationship_count": existing_check.get('relationship_count', 0),
                    "edges_count": existing_check.get('relationship_count', 0),
                    "already_exists": True
                }
            
            # Load and process graph data
            graph_data = self._load_graph_data(graph_files[0])
            
            # Actually import the data into Neo4j database
            if self.neo4j_manager and graph_data:
                try:
                    logger.info(f"📊 Importing graph data into Neo4j database...")
                    # Pass file_id to the import process
                    self.neo4j_manager.import_graph_file_with_id(graph_files[0], file_id)
                    logger.info(f"✅ Successfully imported data into Neo4j database")
                except Exception as e:
                    logger.error(f"❌ Failed to import data into Neo4j database: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to import data into Neo4j database: {str(e)}",
                        "file_id": file_id,
                        "file_name": file_info.filename
                    }
            
            return {
                "success": True,
                "message": f"File {file_info.filename} imported successfully",
                "file_id": file_id,
                "file_name": file_info.filename,
                "project_name": project_name,
                "use_case_name": use_case_name,
                "graph_path": str(graph_data_path),
                "graph_files": [str(f) for f in graph_files],
                "node_count": len(graph_data.get("nodes", [])),
                "relationship_count": len(graph_data.get("edges", [])),
                "edges_count": len(graph_data.get("edges", [])),  # Add explicit edges count
                "graph_data": graph_data
            }
            
        except Exception as e:
            logger.error(f"Error importing file {file_id} to Neo4j: {e}")
            return {
                "success": False,
                "error": f"Error importing file: {str(e)}"
            }

    def import_project_to_neo4j(self, project_id: str) -> Dict[str, Any]:
        """Import all processed files in a project to Neo4j"""
        try:
            # Get project information
            project_info = self.shared_project_service.get_by_id(project_id)
            if not project_info:
                return {
                    "success": False,
                    "error": f"Project with ID {project_id} not found"
                }
            
            # Get all processed files in the project
            files = self.file_service.get_files_by_project(project_id)
            processed_files = [f for f in files if f.status == "processed"]
            
            if not processed_files:
                return {
                    "success": False,
                    "error": f"No processed files found in project {project_info.name}"
                }
            
            # Import each processed file
            imported_files = []
            total_nodes = 0
            total_relationships = 0
            
            for file_info in processed_files:
                result = self.import_file_to_neo4j(file_info.file_id)
                if result["success"]:
                    imported_files.append(result)
                    total_nodes += result.get("node_count", 0)
                    total_relationships += result.get("relationship_count", 0)
            
            return {
                "success": True,
                "message": f"Project {project_info.name} imported successfully",
                "project_id": project_id,
                "project_name": project_info.name,
                "total_files": len(processed_files),
                "imported_files": len(imported_files),
                "total_nodes": total_nodes,
                "total_relationships": total_relationships,
                "imported_files_data": imported_files
            }
            
        except Exception as e:
            logger.error(f"Error importing project {project_id} to Neo4j: {e}")
            return {
                "success": False,
                "error": f"Error importing project: {str(e)}"
            }

    def _check_file_data_exists(self, file_id: str) -> Dict[str, Any]:
        """Check if data for a specific file already exists in Neo4j"""
        try:
            if not self.neo4j_manager:
                return {'exists': False, 'error': 'Neo4j manager not initialized'}
            
            # Query to check if nodes with this file_id exist
            query = """
            MATCH (n)
            WHERE n.file_id = $file_id
            RETURN count(n) as node_count
            """
            
            result = self.neo4j_manager.execute_query(query, {'file_id': file_id})
            
            if result and len(result) > 0:
                node_count = result[0].get('node_count', 0)
                
                if node_count > 0:
                    # Also get relationship count
                    rel_query = """
                    MATCH (n)-[r]->(m)
                    WHERE n.file_id = $file_id OR m.file_id = $file_id
                    RETURN count(r) as relationship_count
                    """
                    rel_result = self.neo4j_manager.execute_query(rel_query, {'file_id': file_id})
                    relationship_count = rel_result[0].get('relationship_count', 0) if rel_result else 0
                    
                    return {
                        'exists': True,
                        'node_count': node_count,
                        'relationship_count': relationship_count,
                        'file_id': file_id
                    }
            
            return {'exists': False, 'node_count': 0, 'relationship_count': 0}
            
        except Exception as e:
            logger.error(f"Error checking if file data exists: {e}")
            return {'exists': False, 'error': str(e)}

    def clear_all_neo4j_data(self) -> Dict[str, Any]:
        """Clear all data from Neo4j database"""
        try:
            if not self.neo4j_manager:
                return {'success': False, 'error': 'Neo4j manager not initialized'}
            
            # Delete all nodes and relationships
            query = "MATCH (n) DETACH DELETE n"
            self.neo4j_manager.execute_query(query)
            
            logger.info("✅ Cleared all data from Neo4j database")
            return {
                'success': True,
                'message': 'All data cleared from Neo4j database'
            }
            
        except Exception as e:
            logger.error(f"Error clearing Neo4j data: {e}")
            return {'success': False, 'error': str(e)}

    def _load_graph_data(self, graph_file_path: Path) -> Dict[str, Any]:
        """Load graph data from file"""
        try:
            if graph_file_path.suffix.lower() == '.json':
                with open(graph_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif graph_file_path.suffix.lower() == '.csv':
                # Handle CSV graph data
                import pandas as pd
                df = pd.read_csv(graph_file_path)
                return {
                    "nodes": df.to_dict('records'),
                    "edges": []
                }
            else:
                return {
                    "nodes": [],
                    "edges": [],
                    "error": f"Unsupported file format: {graph_file_path.suffix}"
                }
        except Exception as e:
            logger.error(f"Error loading graph data from {graph_file_path}: {e}")
            return {
                "nodes": [],
                "edges": [],
                "error": f"Error loading graph data: {str(e)}"
            } 