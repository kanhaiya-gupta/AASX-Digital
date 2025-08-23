"""
Knowledge Graph Neo4j Service
Service layer for Knowledge Graph operations within the webapp module.
Uses new backend services from src/kg_neo4j/ for detailed operations.
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
from src.shared.database.async_base_manager import AsyncBaseDatabaseManager
from src.shared.repositories.project_repository import ProjectRepository
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.use_case_repository import UseCaseRepository

# Import new backend services from src/kg_neo4j/
from src.kg_neo4j.services import KGGraphOperationsService
from src.kg_neo4j.core import KGGraphService, KGMetricsService, KGNeo4jIntegrationService
from src.kg_neo4j.neo4j import Neo4jManager, AASXGraphAnalyzer
from src.kg_neo4j.utils import docker_manager

# Migrated to new twin registry system
from src.twin_registry.core.twin_registry_service import TwinRegistryService as CoreTwinRegistryService
from src.shared.services.project_service import ProjectService as SharedProjectService
from src.shared.services.file_service import FileService
from src.shared.services.use_case_service import UseCaseService
from src.twin_registry.core.twin_lifecycle_service import TwinLifecycleService

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
            self._initialize_new_backend_services()
            logger.info("✅ New backend services initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize new backend services: {e}")
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
            self.async_db_manager = AsyncBaseDatabaseManager(connection_manager)
            
            # Initialize repositories
            self.project_repo = ProjectRepository(self.async_db_manager)
            self.file_repo = FileRepository(self.async_db_manager)
            self.use_case_repo = UseCaseRepository(self.async_db_manager)
            # Migrated to new twin registry system
            self.twin_registry_service = CoreTwinRegistryService()
            
            # Initialize shared services
            self.shared_project_service = SharedProjectService(
                self.async_db_manager, 
                self.use_case_repo, 
                self.file_repo
            )
            self.file_service = FileService(
                self.async_db_manager,
                self.project_repo,
                None  # Remove digital_twin_repo reference
            )
            self.use_case_service = UseCaseService(
                self.async_db_manager,
                self.project_repo
            )
            # Migrated to new twin registry system
            self.twin_lifecycle_service = TwinLifecycleService()
            
            logger.info("✓ Centralized data management system initialized for Knowledge Graph")
            
        except Exception as e:
            logger.error(f"Error initializing centralized data management: {e}")
            raise
        
    def _initialize_new_backend_services(self):
        """Initialize new backend services from src/kg_neo4j/"""
        try:
            logger.info("🔧 Initializing new backend services...")
            
            # Initialize new backend services with async database manager
            logger.info("📦 Initializing KGGraphOperationsService...")
            self.operations_service = KGGraphOperationsService(self.async_db_manager)
            logger.info("✅ KGGraphOperationsService initialized")
            
            logger.info("📦 Initializing KGGraphService...")
            self.graph_service = KGGraphService(self.async_db_manager)
            logger.info("✅ KGGraphService initialized")
            
            logger.info("📦 Initializing KGMetricsService...")
            self.metrics_service = KGMetricsService(self.async_db_manager)
            logger.info("✅ KGMetricsService initialized")
            
            logger.info("📦 Initializing KGNeo4jIntegrationService...")
            self.neo4j_integration_service = KGNeo4jIntegrationService(self.async_db_manager)
            logger.info("✅ KGNeo4jIntegrationService initialized")
            
            # Get Neo4j connection parameters from settings
            logger.info("🔧 Getting Neo4j connection parameters...")
            from webapp.config.settings import settings
            neo4j_uri = settings.neo4j_uri
            neo4j_user = settings.neo4j_user
            neo4j_password = settings.neo4j_password
            logger.info(f"🔧 Neo4j URI: {neo4j_uri}, User: {neo4j_user}")
            
            # Initialize legacy Neo4j managers for backward compatibility
            logger.info("📦 Initializing legacy Neo4jManager...")
            self.neo4j_manager = Neo4jManager(neo4j_uri, neo4j_user, neo4j_password)
            logger.info("✅ Legacy Neo4jManager initialized")
            
            logger.info("📦 Initializing legacy AASXGraphAnalyzer...")
            self.graph_analyzer = AASXGraphAnalyzer(neo4j_uri, neo4j_user, neo4j_password)
            logger.info("✅ Legacy AASXGraphAnalyzer initialized")
            
            logger.info("✓ New backend services initialized successfully")
            
        except ImportError as e:
            logger.error(f"❌ ImportError in _initialize_new_backend_services: {e}")
            logger.error(f"❌ ImportError type: {type(e)}")
            import traceback
            logger.error(f"❌ ImportError traceback: {traceback.format_exc()}")
            self.operations_service = None
            self.graph_service = None
            self.metrics_service = None
            self.neo4j_integration_service = None
            self.neo4j_manager = None
            self.graph_analyzer = None
        except Exception as e:
            logger.error(f"❌ Unexpected error in _initialize_new_backend_services: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Error traceback: {traceback.format_exc()}")
            self.operations_service = None
            self.graph_service = None
            self.metrics_service = None
            self.neo4j_integration_service = None
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

    # ============================================================================
    # PHASE 1: NEW BACKEND INTEGRATION METHODS
    # ============================================================================

    async def create_knowledge_graph(self, file_id: str, user_id: str, org_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new knowledge graph using the new backend services"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Creating knowledge graph for file {file_id}")
            
            # Use the new operations service to create graph from AASX file
            result = await self.operations_service.create_graph_from_aasx_file(
                file_id=file_id,
                user_id=user_id,
                org_id=org_id,
                graph_config=config
            )
            
            logger.info(f"✅ Knowledge graph created successfully: {result.get('graph_id', 'unknown')}")
            return {
                "success": True,
                "data": result,
                "message": "Knowledge graph created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating knowledge graph: {e}")
            return {
                "success": False,
                "error": f"Failed to create knowledge graph: {str(e)}"
            }

    async def get_graph_registry(self, graph_id: str) -> Dict[str, Any]:
        """Get knowledge graph registry information"""
        try:
            if not self.graph_service:
                return {"success": False, "error": "Graph service not initialized"}
            
            logger.info(f"🔧 Getting graph registry for {graph_id}")
            
            # Use the new graph service to get graph by ID
            result = await self.graph_service.get_graph_by_id(graph_id)
            
            if result:
                logger.info(f"✅ Graph registry retrieved successfully")
                return {
                    "success": True,
                    "data": result,
                    "message": "Graph registry retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Graph not found"
                }
            
        except Exception as e:
            logger.error(f"❌ Error getting graph registry: {e}")
            return {
                "success": False,
                "error": f"Failed to get graph registry: {str(e)}"
            }

    async def list_graph_registries(self, user_id: str, org_id: str) -> Dict[str, Any]:
        """List all knowledge graph registries for a user/organization"""
        try:
            if not self.graph_service:
                return {"success": False, "error": "Graph service not initialized"}
            
            logger.info(f"🔧 Listing graph registries for user {user_id}, org {org_id}")
            
            # Use the new graph service to get graphs by user ID
            result = await self.graph_service.get_graphs_by_user_id(user_id)
            
            # Filter by organization if needed
            if org_id:
                result = [graph for graph in result if graph.get('org_id') == org_id]
            
            logger.info(f"✅ Found {len(result)} graph registries")
            return {
                "success": True,
                "data": result,
                "count": len(result),
                "message": f"Found {len(result)} graph registries"
            }
            
        except Exception as e:
            logger.error(f"❌ Error listing graph registries: {e}")
            return {
                "success": False,
                "error": f"Failed to list graph registries: {str(e)}"
            }

    async def update_graph_status(self, graph_id: str, status_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update knowledge graph status"""
        try:
            if not self.graph_service:
                return {"success": False, "error": "Graph service not initialized"}
            
            logger.info(f"🔧 Updating graph status for {graph_id}: {status_updates}")
            
            # Use the new graph service to update graph status
            result = await self.graph_service.update_graph_status(graph_id, status_updates)
            
            logger.info(f"✅ Graph status updated successfully")
            return {
                "success": True,
                "data": result,
                "message": "Graph status updated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating graph status: {e}")
            return {
                "success": False,
                "error": f"Failed to update graph status: {str(e)}"
            }

    async def delete_graph_registry(self, graph_id: str) -> Dict[str, Any]:
        """Delete a knowledge graph registry"""
        try:
            if not self.graph_service:
                return {"success": False, "error": "Graph service not initialized"}
            
            logger.info(f"🔧 Deleting graph registry {graph_id}")
            
            # First get the graph to ensure it exists
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return {
                    "success": False,
                    "error": "Graph not found"
                }
            
            # Use the new graph service to delete graph
            # Note: This would need to be implemented in the graph service
            # For now, we'll return a placeholder
            logger.info(f"✅ Graph registry deletion requested")
            return {
                "success": True,
                "message": "Graph registry deletion requested",
                "graph_id": graph_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error deleting graph registry: {e}")
            return {
                "success": False,
                "error": f"Failed to delete graph registry: {str(e)}"
            }

    async def get_graph_performance_summary(self, graph_id: str) -> Dict[str, Any]:
        """Get performance summary for a knowledge graph"""
        try:
            if not self.metrics_service:
                return {"success": False, "error": "Metrics service not initialized"}
            
            logger.info(f"🔧 Getting performance summary for graph {graph_id}")
            
            # Use the new metrics service to get performance summary
            result = await self.metrics_service.get_comprehensive_metrics_summary(graph_id)
            
            logger.info(f"✅ Performance summary retrieved successfully")
            return {
                "success": True,
                "data": result,
                "message": "Performance summary retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting performance summary: {e}")
            return {
                "success": False,
                "error": f"Failed to get performance summary: {str(e)}"
            }

    async def test_neo4j_connection(self) -> Dict[str, Any]:
        """Test Neo4j connection using the new integration service"""
        try:
            if not self.neo4j_integration_service:
                return {"success": False, "error": "Neo4j integration service not initialized"}
            
            logger.info("🔧 Testing Neo4j connection with new integration service")
            
            # Use the new integration service to test connection
            result = await self.neo4j_integration_service.test_neo4j_connection()
            
            logger.info(f"✅ Neo4j connection test completed")
            return {
                "success": True,
                "data": result,
                "message": "Neo4j connection test completed"
            }
            
        except Exception as e:
            logger.error(f"❌ Error testing Neo4j connection: {e}")
            return {
                "success": False,
                "error": f"Failed to test Neo4j connection: {str(e)}"
            }

    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health using new backend services"""
        try:
            logger.info("🔧 Getting comprehensive system health")
            
            health_status = {
                "backend_services": {},
                "database": {},
                "neo4j": {},
                "overall_status": "unknown"
            }
            
            # Check backend services
            if self.operations_service:
                health_status["backend_services"]["operations_service"] = "available"
            else:
                health_status["backend_services"]["operations_service"] = "unavailable"
                
            if self.graph_service:
                health_status["backend_services"]["graph_service"] = "available"
            else:
                health_status["backend_services"]["graph_service"] = "unavailable"
                
            if self.metrics_service:
                health_status["backend_services"]["metrics_service"] = "available"
            else:
                health_status["backend_services"]["metrics_service"] = "unavailable"
                
            if self.neo4j_integration_service:
                health_status["backend_services"]["neo4j_integration_service"] = "available"
            else:
                health_status["backend_services"]["neo4j_integration_service"] = "unavailable"
            
            # Check database
            if self.async_db_manager:
                health_status["database"]["async_manager"] = "available"
            else:
                health_status["database"]["async_manager"] = "unavailable"
            
            # Check Neo4j
            if self.neo4j_manager:
                health_status["neo4j"]["legacy_manager"] = "available"
            else:
                health_status["neo4j"]["legacy_manager"] = "unavailable"
            
            # Determine overall status
            available_services = sum(1 for service in health_status["backend_services"].values() if service == "available")
            total_services = len(health_status["backend_services"])
            
            if available_services == total_services:
                health_status["overall_status"] = "healthy"
            elif available_services > 0:
                health_status["overall_status"] = "degraded"
            else:
                health_status["overall_status"] = "unhealthy"
            
            logger.info(f"✅ System health check completed: {health_status['overall_status']}")
            return {
                "success": True,
                "data": health_status,
                "message": f"System health: {health_status['overall_status']}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system health: {e}")
            return {
                "success": False,
                "error": f"Failed to get system health: {str(e)}"
            }

    # ============================================================================
    # PHASE 2: AI/RAG INTEGRATION METHODS
    # ============================================================================

    async def import_ai_insights(self, graph_id: str, ai_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Import AI insights into a knowledge graph"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Importing AI insights for graph {graph_id}")
            
            # Use the operations service to import AI insights
            result = await self.operations_service.enhance_existing_graph_with_ai(
                graph_id=graph_id,
                ai_data=ai_data,
                user_id=user_id
            )
            
            logger.info(f"✅ AI insights imported successfully for graph {graph_id}")
            return {
                "success": True,
                "data": result,
                "message": "AI insights imported successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error importing AI insights: {e}")
            return {
                "success": False,
                "error": f"Failed to import AI insights: {str(e)}"
            }

    async def get_ai_insights(self, graph_id: str) -> Dict[str, Any]:
        """Get AI insights for a knowledge graph"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Getting AI insights for graph {graph_id}")
            
            # Use the operations service to get AI insights
            result = await self.operations_service.get_graph_ai_insights_summary(graph_id)
            
            logger.info(f"✅ AI insights retrieved successfully for graph {graph_id}")
            return {
                "success": True,
                "data": result,
                "message": "AI insights retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting AI insights: {e}")
            return {
                "success": False,
                "error": f"Failed to get AI insights: {str(e)}"
            }

    async def merge_ai_insights(self, graph_id: str, ai_graph_id: str) -> Dict[str, Any]:
        """Merge AI insights with existing knowledge graph"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Merging AI insights for graph {graph_id} with AI graph {ai_graph_id}")
            
            # Use the operations service to merge AI insights
            result = await self.operations_service.merge_graphs(
                source_graph_id=ai_graph_id,
                target_graph_id=graph_id,
                config={"merge_type": "ai_insights", "preserve_existing": True}
            )
            
            logger.info(f"✅ AI insights merged successfully")
            return {
                "success": True,
                "data": result,
                "message": "AI insights merged successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error merging AI insights: {e}")
            return {
                "success": False,
                "error": f"Failed to merge AI insights: {str(e)}"
            }

    async def create_graph_with_ai_insights(self, file_id: str, ai_data: Dict[str, Any], user_id: str, org_id: str) -> Dict[str, Any]:
        """Create a new knowledge graph with AI insights"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Creating knowledge graph with AI insights for file {file_id}")
            
            # Use the operations service to create graph with AI insights
            result = await self.operations_service.create_graph_with_ai_insights(
                file_id=file_id,
                ai_data=ai_data,
                user_id=user_id,
                org_id=org_id
            )
            
            logger.info(f"✅ Knowledge graph with AI insights created successfully")
            return {
                "success": True,
                "data": result,
                "message": "Knowledge graph with AI insights created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating graph with AI insights: {e}")
            return {
                "success": False,
                "error": f"Failed to create graph with AI insights: {str(e)}"
            }

    async def enhance_graph_with_ai(self, graph_id: str, ai_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Enhance existing graph with AI insights"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Enhancing graph {graph_id} with AI insights")
            
            # Use the operations service to enhance graph with AI
            result = await self.operations_service.enhance_existing_graph_with_ai(
                graph_id=graph_id,
                ai_data=ai_data,
                user_id=user_id
            )
            
            logger.info(f"✅ Graph enhanced with AI insights successfully")
            return {
                "success": True,
                "data": result,
                "message": "Graph enhanced with AI insights successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error enhancing graph with AI: {e}")
            return {
                "success": False,
                "error": f"Failed to enhance graph with AI: {str(e)}"
            }

    # ============================================================================
    # PHASE 2: CROSS-MODULE INTEGRATION METHODS
    # ============================================================================

    async def link_graph_to_twin(self, graph_id: str, twin_id: str) -> Dict[str, Any]:
        """Link a knowledge graph to a digital twin"""
        try:
            if not self.graph_service:
                return {"success": False, "error": "Graph service not initialized"}
            
            logger.info(f"🔧 Linking graph {graph_id} to twin {twin_id}")
            
            # Use the graph service to link graph to twin
            result = await self.graph_service.link_graph_to_twin(graph_id, twin_id)
            
            logger.info(f"✅ Graph linked to twin successfully")
            return {
                "success": True,
                "data": result,
                "message": "Graph linked to twin successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error linking graph to twin: {e}")
            return {
                "success": False,
                "error": f"Failed to link graph to twin: {str(e)}"
            }

    async def get_linked_twins(self, graph_id: str) -> Dict[str, Any]:
        """Get all digital twins linked to a knowledge graph"""
        try:
            if not self.graph_service:
                return {"success": False, "error": "Graph service not initialized"}
            
            logger.info(f"🔧 Getting linked twins for graph {graph_id}")
            
            # Get the graph registry to find linked twins
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return {
                    "success": False,
                    "error": "Graph not found"
                }
            
            # Extract linked twin information
            linked_twins = []
            if graph.get('twin_registry_id'):
                linked_twins.append({
                    "twin_id": graph['twin_registry_id'],
                    "link_type": "primary",
                    "linked_at": graph.get('updated_at')
                })
            
            logger.info(f"✅ Found {len(linked_twins)} linked twins")
            return {
                "success": True,
                "data": {
                    "graph_id": graph_id,
                    "linked_twins": linked_twins,
                    "count": len(linked_twins)
                },
                "message": f"Found {len(linked_twins)} linked twins"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting linked twins: {e}")
            return {
                "success": False,
                "error": f"Failed to get linked twins: {str(e)}"
            }

    async def get_linked_aasx_files(self, graph_id: str) -> Dict[str, Any]:
        """Get all AASX files linked to a knowledge graph"""
        try:
            if not self.graph_service:
                return {"success": False, "error": "Graph service not initialized"}
            
            logger.info(f"🔧 Getting linked AASX files for graph {graph_id}")
            
            # Get the graph registry to find linked AASX files
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return {
                    "success": False,
                    "error": "Graph not found"
                }
            
            # Extract linked AASX file information
            linked_files = []
            if graph.get('file_id'):
                linked_files.append({
                    "file_id": graph['file_id'],
                    "link_type": "source",
                    "linked_at": graph.get('created_at')
                })
            
            if graph.get('aasx_integration_id'):
                linked_files.append({
                    "file_id": graph['aasx_integration_id'],
                    "link_type": "integration",
                    "linked_at": graph.get('updated_at')
                })
            
            logger.info(f"✅ Found {len(linked_files)} linked AASX files")
            return {
                "success": True,
                "data": {
                    "graph_id": graph_id,
                    "linked_files": linked_files,
                    "count": len(linked_files)
                },
                "message": f"Found {len(linked_files)} linked AASX files"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting linked AASX files: {e}")
            return {
                "success": False,
                "error": f"Failed to get linked AASX files: {str(e)}"
            }

    async def get_cross_module_analytics(self, graph_id: str) -> Dict[str, Any]:
        """Get cross-module analytics for a knowledge graph"""
        try:
            if not self.graph_service or not self.metrics_service:
                return {"success": False, "error": "Required services not initialized"}
            
            logger.info(f"🔧 Getting cross-module analytics for graph {graph_id}")
            
            # Get graph information
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return {
                    "success": False,
                    "error": "Graph not found"
                }
            
            # Get performance metrics
            performance = await self.metrics_service.get_comprehensive_metrics_summary(graph_id)
            
            # Build cross-module analytics
            analytics = {
                "graph_id": graph_id,
                "graph_name": graph.get('graph_name'),
                "integration_status": graph.get('integration_status'),
                "linked_modules": {
                    "twin_registry": bool(graph.get('twin_registry_id')),
                    "aasx_processing": bool(graph.get('aasx_integration_id')),
                    "physics_modeling": bool(graph.get('physics_modeling_id')),
                    "federated_learning": bool(graph.get('federated_learning_id')),
                    "certificate_manager": bool(graph.get('certificate_manager_id'))
                },
                "performance_metrics": performance.get('data', {}),
                "cross_module_health": {
                    "overall_score": graph.get('overall_health_score', 0),
                    "integration_score": graph.get('integration_status') == 'active' and 100 or 0,
                    "data_quality_score": graph.get('data_quality_score', 0)
                }
            }
            
            logger.info(f"✅ Cross-module analytics retrieved successfully")
            return {
                "success": True,
                "data": analytics,
                "message": "Cross-module analytics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting cross-module analytics: {e}")
            return {
                "success": False,
                "error": f"Failed to get cross-module analytics: {str(e)}"
            } 

    # ============================================================================
    # PHASE 2: ADVANCED ANALYTICS METHODS
    # ============================================================================

    async def get_graph_analytics(self, graph_id: str, period: str = "30d") -> Dict[str, Any]:
        """Get comprehensive analytics for a knowledge graph"""
        try:
            if not self.metrics_service:
                return {"success": False, "error": "Metrics service not initialized"}
            
            logger.info(f"🔧 Getting graph analytics for {graph_id} over {period}")
            
            # Get comprehensive metrics summary
            metrics = await self.metrics_service.get_comprehensive_metrics_summary(graph_id)
            
            # Get performance trends
            trends = await self.metrics_service.get_performance_trends(graph_id, days=30)
            
            # Get health score trend
            health_trend = await self.metrics_service.get_health_score_trend(graph_id, days=30)
            
            analytics = {
                "graph_id": graph_id,
                "period": period,
                "metrics_summary": metrics.get('data', {}),
                "performance_trends": trends.get('data', {}),
                "health_trends": health_trend.get('data', {}),
                "analytics_timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"✅ Graph analytics retrieved successfully")
            return {
                "success": True,
                "data": analytics,
                "message": "Graph analytics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting graph analytics: {e}")
            return {
                "success": False,
                "error": f"Failed to get graph analytics: {str(e)}"
            }

    async def get_performance_analytics(self, graph_id: str, days: str = "30") -> Dict[str, Any]:
        """Get performance analytics for a knowledge graph"""
        try:
            if not self.metrics_service:
                return {"success": False, "error": "Metrics service not initialized"}
            
            logger.info(f"🔧 Getting performance analytics for {graph_id} over {days} days")
            
            # Get performance trends
            trends = await self.metrics_service.get_performance_trends(graph_id, days=int(days))
            
            # Get comprehensive metrics
            metrics = await self.metrics_service.get_comprehensive_metrics_summary(graph_id)
            
            performance_analytics = {
                "graph_id": graph_id,
                "period_days": days,
                "performance_trends": trends.get('data', {}),
                "current_metrics": metrics.get('data', {}),
                "performance_summary": {
                    "avg_response_time": metrics.get('data', {}).get('avg_response_time_ms', 0),
                    "avg_health_score": metrics.get('data', {}).get('avg_health_score', 0),
                    "total_operations": metrics.get('data', {}).get('total_operations', 0)
                }
            }
            
            logger.info(f"✅ Performance analytics retrieved successfully")
            return {
                "success": True,
                "data": performance_analytics,
                "message": "Performance analytics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting performance analytics: {e}")
            return {
                "success": False,
                "error": f"Failed to get performance analytics: {str(e)}"
            }

    async def get_user_activity_analytics(self, graph_id: str, days: str = "30") -> Dict[str, Any]:
        """Get user activity analytics for a knowledge graph"""
        try:
            if not self.metrics_service:
                return {"success": False, "error": "Metrics service not initialized"}
            
            logger.info(f"🔧 Getting user activity analytics for {graph_id} over {days} days")
            
            # Get user activity metrics
            user_activity = await self.metrics_service.get_user_activity_metrics_by_graph_id(graph_id, days=int(days))
            
            # Get comprehensive metrics for user interaction data
            metrics = await self.metrics_service.get_comprehensive_metrics_summary(graph_id)
            
            activity_analytics = {
                "graph_id": graph_id,
                "period_days": days,
                "user_activity": user_activity.get('data', {}),
                "interaction_summary": {
                    "total_interactions": metrics.get('data', {}).get('user_interaction_count', 0),
                    "query_executions": metrics.get('data', {}).get('query_execution_count', 0),
                    "visualization_views": metrics.get('data', {}).get('visualization_view_count', 0),
                    "export_operations": metrics.get('data', {}).get('export_operation_count', 0)
                }
            }
            
            logger.info(f"✅ User activity analytics retrieved successfully")
            return {
                "success": True,
                "data": activity_analytics,
                "message": "User activity analytics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user activity analytics: {e}")
            return {
                "success": False,
                "error": f"Failed to get user activity analytics: {str(e)}"
            }

    async def get_data_quality_analytics(self, graph_id: str, days: str = "30") -> Dict[str, Any]:
        """Get data quality analytics for a knowledge graph"""
        try:
            if not self.metrics_service:
                return {"success": False, "error": "Metrics service not initialized"}
            
            logger.info(f"🔧 Getting data quality analytics for {graph_id} over {days} days")
            
            # Get data quality metrics
            data_quality = await self.metrics_service.get_data_quality_metrics_by_graph_id(graph_id, days=int(days))
            
            # Get comprehensive metrics
            metrics = await self.metrics_service.get_comprehensive_metrics_summary(graph_id)
            
            quality_analytics = {
                "graph_id": graph_id,
                "period_days": days,
                "data_quality_metrics": data_quality.get('data', {}),
                "quality_summary": {
                    "freshness_score": metrics.get('data', {}).get('data_freshness_score', 0),
                    "completeness_score": metrics.get('data', {}).get('data_completeness_score', 0),
                    "consistency_score": metrics.get('data', {}).get('data_consistency_score', 0),
                    "accuracy_score": metrics.get('data', {}).get('data_accuracy_score', 0)
                }
            }
            
            logger.info(f"✅ Data quality analytics retrieved successfully")
            return {
                "success": True,
                "data": quality_analytics,
                "message": "Data quality analytics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting data quality analytics: {e}")
            return {
                "success": False,
                "error": f"Failed to get data quality analytics: {str(e)}"
            }

    async def get_business_intelligence_report(self, graph_id: str) -> Dict[str, Any]:
        """Get comprehensive business intelligence report for a knowledge graph"""
        try:
            if not self.metrics_service or not self.graph_service:
                return {"success": False, "error": "Required services not initialized"}
            
            logger.info(f"🔧 Getting business intelligence report for {graph_id}")
            
            # Get graph information
            graph = await self.graph_service.get_graph_by_id(graph_id)
            if not graph:
                return {
                    "success": False,
                    "error": "Graph not found"
                }
            
            # Get comprehensive metrics
            metrics = await self.metrics_service.get_comprehensive_metrics_summary(graph_id)
            
            # Get performance trends
            trends = await self.metrics_service.get_performance_trends(graph_id, days=30)
            
            # Build business intelligence report
            bi_report = {
                "graph_id": graph_id,
                "graph_name": graph.get('graph_name'),
                "report_generated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "executive_summary": {
                    "overall_health": graph.get('overall_health_score', 0),
                    "performance_score": graph.get('performance_score', 0),
                    "data_quality_score": graph.get('data_quality_score', 0),
                    "reliability_score": graph.get('reliability_score', 0),
                    "compliance_score": graph.get('compliance_score', 0)
                },
                "operational_metrics": metrics.get('data', {}),
                "performance_trends": trends.get('data', {}),
                "business_insights": {
                    "integration_status": graph.get('integration_status'),
                    "lifecycle_status": graph.get('lifecycle_status'),
                    "operational_status": graph.get('operational_status'),
                    "total_nodes": graph.get('total_nodes', 0),
                    "total_relationships": graph.get('total_relationships', 0)
                },
                "recommendations": [
                    "Monitor performance trends for optimization opportunities",
                    "Review data quality scores for improvement areas",
                    "Check integration status for cross-module connectivity"
                ]
            }
            
            logger.info(f"✅ Business intelligence report generated successfully")
            return {
                "success": True,
                "data": bi_report,
                "message": "Business intelligence report generated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting business intelligence report: {e}")
            return {
                "success": False,
                "error": f"Failed to get business intelligence report: {str(e)}"
            } 

    # ============================================================================
    # PHASE 2: GRAPH OPERATIONS METHODS
    # ============================================================================

    async def transform_graph_structure(self, graph_id: str, transformations: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the structure of a knowledge graph"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Transforming graph structure for {graph_id}")
            
            # Use the operations service to transform graph structure
            result = await self.operations_service.transform_graph_structure(
                graph_id=graph_id,
                transformations=transformations
            )
            
            logger.info(f"✅ Graph structure transformed successfully")
            return {
                "success": True,
                "data": result,
                "message": "Graph structure transformed successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error transforming graph structure: {e}")
            return {
                "success": False,
                "error": f"Failed to transform graph structure: {str(e)}"
            }

    async def merge_graphs(self, source_graph_id: str, target_graph_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two knowledge graphs"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Merging graphs {source_graph_id} into {target_graph_id}")
            
            # Use the operations service to merge graphs
            result = await self.operations_service.merge_graphs(
                source_graph_id=source_graph_id,
                target_graph_id=target_graph_id,
                config=config
            )
            
            logger.info(f"✅ Graphs merged successfully")
            return {
                "success": True,
                "data": result,
                "message": "Graphs merged successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error merging graphs: {e}")
            return {
                "success": False,
                "error": f"Failed to merge graphs: {str(e)}"
            }

    async def export_graph_workflow(self, graph_id: str, format: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Export a knowledge graph workflow"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Exporting graph workflow for {graph_id} in {format} format")
            
            # Use the operations service to export graph workflow
            result = await self.operations_service.export_graph_workflow(
                graph_id=graph_id,
                format=format,
                config=config
            )
            
            logger.info(f"✅ Graph workflow exported successfully")
            return {
                "success": True,
                "data": result,
                "message": "Graph workflow exported successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error exporting graph workflow: {e}")
            return {
                "success": False,
                "error": f"Failed to export graph workflow: {str(e)}"
            }

    async def get_graph_ai_insights_summary(self, graph_id: str) -> Dict[str, Any]:
        """Get AI insights summary for a knowledge graph"""
        try:
            if not self.operations_service:
                return {"success": False, "error": "Operations service not initialized"}
            
            logger.info(f"🔧 Getting AI insights summary for {graph_id}")
            
            # Use the operations service to get AI insights summary
            result = await self.operations_service.get_graph_ai_insights_summary(graph_id)
            
            logger.info(f"✅ AI insights summary retrieved successfully")
            return {
                "success": True,
                "data": result,
                "message": "AI insights summary retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting AI insights summary: {e}")
            return {
                "success": False,
                "error": f"Failed to get AI insights summary: {str(e)}"
            } 