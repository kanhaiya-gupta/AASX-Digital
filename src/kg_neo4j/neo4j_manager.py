"""
Neo4j Manager for AASX Knowledge Graph
Handles Neo4j database operations for importing and managing graph data
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from neo4j import GraphDatabase, Driver, Session
import subprocess
import psutil
import requests
import time
import os

logger = logging.getLogger(__name__)

class Neo4jManager:
    """Manages Neo4j database operations for AASX graph data"""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """Initialize Neo4j connection"""
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Driver] = None
        
        # Only connect if credentials are provided
        if uri and user and password:
            self._connect()
        
        # Management properties
        self.docker_container_name = "neo4j-aasx"
        self.local_neo4j_paths = [
            r"C:\Users\kanha\AppData\Local\Programs\neo4j-desktop\Neo4j Desktop 2.exe",
            r"C:\Program Files\Neo4j Desktop\Neo4j Desktop.exe",
            r"C:\Users\{}\AppData\Local\Programs\neo4j-desktop\Neo4j Desktop.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\AppData\Local\Programs\neo4j-desktop\Neo4j Desktop 2.exe".format(os.getenv('USERNAME', ''))
        ]
        self.local_browser_url = "http://localhost:7474"
        self.local_bolt_url = "bolt://localhost:7687"
    
    def _connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test if connection is working"""
        try:
            if not self.driver:
                logger.error("Neo4j driver not initialized")
                return False
                
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                success = record and record["test"] == 1
                if success:
                    logger.info("✅ Neo4j connection test successful")
                return success
        except Exception as e:
            logger.error(f"❌ Neo4j connection test failed: {e}")
            logger.error(f"   URI: {self.uri}")
            logger.error(f"   User: {self.user}")
            logger.error(f"   Please check if Neo4j is running and accessible")
            return False
    
    def import_graph_file(self, file_path: Path):
        """Import graph data from a JSON file using Python Neo4j driver and Bolt protocol"""
        try:
            logger.info(f"Importing graph file: {file_path}")
            
            # Check if driver is connected
            if not self.driver:
                raise Exception("Neo4j driver not initialized. Please check connection settings.")
            
            # Test connection before importing
            if not self.test_connection():
                raise Exception("Cannot connect to Neo4j database. Please check if Neo4j is running.")
            
            # Read the graph file
            with open(file_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            logger.info(f"📊 Loaded JSON data: {len(graph_data.get('nodes', []))} nodes, {len(graph_data.get('edges', []))} edges")
            
            # Extract filename for metadata
            filename = file_path.stem
            
            with self.driver.session() as session:
                # Import nodes
                if 'nodes' in graph_data:
                    logger.info(f"📥 Importing {len(graph_data['nodes'])} nodes...")
                    self._import_nodes(session, graph_data['nodes'], filename)
                
                # Import relationships (handle both 'edges' and 'relationships' keys)
                edge_data = graph_data.get('relationships', graph_data.get('edges', []))
                if edge_data:
                    logger.info(f"🔗 Importing {len(edge_data)} relationships...")
                    self._import_relationships(session, edge_data, filename)
                
                # Import metadata
                if 'metadata' in graph_data:
                    logger.info("📋 Importing metadata...")
                    self._import_metadata(session, graph_data['metadata'], filename)
            
            logger.info(f"✅ Successfully imported {file_path.name} into Neo4j")
            
        except Exception as e:
            logger.error(f"❌ Failed to import {file_path}: {e}")
            raise

    def import_graph_file_with_id(self, file_path: Path, file_id: str):
        """Import graph data from a JSON file with file_id tracking"""
        try:
            logger.info(f"Importing graph file: {file_path} with file_id: {file_id}")
            
            # Check if driver is connected
            if not self.driver:
                raise Exception("Neo4j driver not initialized. Please check connection settings.")
            
            # Test connection before importing
            if not self.test_connection():
                raise Exception("Cannot connect to Neo4j database. Please check if Neo4j is running.")
            
            # Read the graph file
            with open(file_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            logger.info(f"📊 Loaded JSON data: {len(graph_data.get('nodes', []))} nodes, {len(graph_data.get('edges', []))} edges")
            
            # Extract filename for metadata
            filename = file_path.stem
            
            with self.driver.session() as session:
                # Import nodes
                if 'nodes' in graph_data:
                    logger.info(f"📥 Importing {len(graph_data['nodes'])} nodes...")
                    self._import_nodes_with_id(session, graph_data['nodes'], filename, file_id)
                
                # Import relationships (handle both 'edges' and 'relationships' keys)
                edge_data = graph_data.get('relationships', graph_data.get('edges', []))
                if edge_data:
                    logger.info(f"🔗 Importing {len(edge_data)} relationships...")
                    self._import_relationships_with_id(session, edge_data, filename, file_id)
                
                # Import metadata
                if 'metadata' in graph_data:
                    logger.info("📋 Importing metadata...")
                    self._import_metadata_with_id(session, graph_data['metadata'], filename, file_id)
            
            logger.info(f"✅ Successfully imported {file_path.name} into Neo4j with file_id: {file_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to import {file_path}: {e}")
            raise
    
    def _clean_properties(self, properties: Dict) -> Dict:
        """Clean properties to ensure they are Neo4j-compatible"""
        cleaned = {}
        for key, value in properties.items():
            if isinstance(value, (str, int, float, bool, list)):
                # These types are directly compatible with Neo4j
                cleaned[key] = value
            elif isinstance(value, dict):
                # Convert dict to JSON string
                cleaned[key] = json.dumps(value)
            elif value is None:
                # Skip None values
                continue
            else:
                # Convert other types to string
                cleaned[key] = str(value)
        return cleaned

    def _import_nodes(self, session: Session, nodes: List[Dict], source_file: str):
        """Import nodes into Neo4j using Cypher MERGE statements"""
        imported_count = 0
        failed_count = 0
        
        for node in nodes:
            try:
                # Extract node properties
                node_id = node.get('id', node.get('id_short', f"node_{hash(str(node))}"))
                node_type = node.get('type', 'Node')
                properties = {k: v for k, v in node.items() if k not in ['id', 'id_short', 'type']}
                
                # Clean properties for Neo4j compatibility
                properties = self._clean_properties(properties)
                
                # Add source file metadata
                properties['source_file'] = source_file
                properties['imported_at'] = datetime.now().isoformat()
                
                # Create Cypher query with proper escaping
                query = f"""
                MERGE (n:{node_type} {{id: $node_id}})
                SET n += $properties
                RETURN n
                """
                
                result = session.run(query, node_id=node_id, properties=properties)
                imported_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to import node {node.get('id', 'unknown')}: {e}")
                failed_count += 1
        
        logger.info(f"📥 Nodes imported: {imported_count} successful, {failed_count} failed")
    
    def _import_nodes_with_id(self, session: Session, nodes: List[Dict], source_file: str, file_id: str):
        """Import nodes into Neo4j with file_id tracking"""
        imported_count = 0
        failed_count = 0
        
        for node in nodes:
            try:
                # Extract node properties
                node_id = node.get('id', node.get('id_short', f"node_{hash(str(node))}"))
                node_type = node.get('type', 'Node')
                properties = {k: v for k, v in node.items() if k not in ['id', 'id_short', 'type']}
                
                # Clean properties for Neo4j compatibility
                properties = self._clean_properties(properties)
                
                # Add source file metadata and file_id
                properties['source_file'] = source_file
                properties['file_id'] = file_id
                properties['imported_at'] = datetime.now().isoformat()
                
                # Create Cypher query with proper escaping
                query = f"""
                MERGE (n:{node_type} {{id: $node_id}})
                SET n += $properties
                RETURN n
                """
                
                result = session.run(query, node_id=node_id, properties=properties)
                imported_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to import node {node.get('id', 'unknown')}: {e}")
                failed_count += 1
        
        logger.info(f"📥 Nodes imported with file_id: {imported_count} successful, {failed_count} failed")
    
    def _import_relationships(self, session: Session, relationships: List[Dict], source_file: str):
        """Import relationships into Neo4j using Cypher MATCH/MERGE statements"""
        imported_count = 0
        failed_count = 0
        
        for rel in relationships:
            try:
                # Extract relationship properties
                source_id = rel.get('source_id', rel.get('from', rel.get('source')))
                target_id = rel.get('target_id', rel.get('to', rel.get('target')))
                rel_type = rel.get('type', rel.get('relationship_type', 'RELATES_TO'))
                properties = {k: v for k, v in rel.items() if k not in ['source_id', 'target_id', 'type', 'from', 'to', 'source', 'target', 'relationship_type']}
                
                # Clean properties for Neo4j compatibility
                properties = self._clean_properties(properties)
                
                # Add source file metadata
                properties['source_file'] = source_file
                properties['imported_at'] = datetime.now().isoformat()
                
                # Create Cypher query that matches by both id and idShort
                query = f"""
                MATCH (a), (b)
                WHERE (a.id = $source_id OR a.idShort = $source_id) 
                  AND (b.id = $target_id OR b.idShort = $target_id)
                MERGE (a)-[r:{rel_type}]->(b)
                SET r += $properties
                RETURN r
                """
                
                result = session.run(query, source_id=source_id, target_id=target_id, properties=properties)
                imported_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to import relationship {rel.get('type', 'unknown')}: {e}")
                failed_count += 1
        
        logger.info(f"🔗 Relationships imported: {imported_count} successful, {failed_count} failed")
    
    def _import_relationships_with_id(self, session: Session, relationships: List[Dict], source_file: str, file_id: str):
        """Import relationships into Neo4j with file_id tracking"""
        imported_count = 0
        failed_count = 0
        
        for rel in relationships:
            try:
                # Extract relationship properties
                source_id = rel.get('source_id', rel.get('from', rel.get('source')))
                target_id = rel.get('target_id', rel.get('to', rel.get('target')))
                rel_type = rel.get('type', rel.get('relationship_type', 'RELATES_TO'))
                properties = {k: v for k, v in rel.items() if k not in ['source_id', 'target_id', 'type', 'from', 'to', 'source', 'target', 'relationship_type']}
                
                # Clean properties for Neo4j compatibility
                properties = self._clean_properties(properties)
                
                # Add source file metadata and file_id
                properties['source_file'] = source_file
                properties['file_id'] = file_id
                properties['imported_at'] = datetime.now().isoformat()
                
                # Create Cypher query that matches by both id and idShort
                query = f"""
                MATCH (a), (b)
                WHERE (a.id = $source_id OR a.idShort = $source_id) 
                  AND (b.id = $target_id OR b.idShort = $target_id)
                MERGE (a)-[r:{rel_type}]->(b)
                SET r += $properties
                RETURN r
                """
                
                result = session.run(query, source_id=source_id, target_id=target_id, properties=properties)
                imported_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to import relationship {rel.get('type', 'unknown')}: {e}")
                failed_count += 1
        
        logger.info(f"🔗 Relationships imported with file_id: {imported_count} successful, {failed_count} failed")
    
    def _import_metadata(self, session: Session, metadata: Dict, source_file: str):
        """Import metadata as a metadata node"""
        try:
            # Create metadata node
            query = """
            MERGE (m:Metadata {source_file: $source_file})
            SET m += $metadata
            RETURN m
            """
            
            session.run(query, source_file=source_file, metadata=metadata)
            
        except Exception as e:
            logger.warning(f"Failed to import metadata for {source_file}: {e}")
    
    def _import_metadata_with_id(self, session: Session, metadata: Dict, source_file: str, file_id: str):
        """Import metadata as a metadata node with file_id tracking"""
        try:
            # Create metadata node with file_id
            query = """
            MERGE (m:Metadata {source_file: $source_file, file_id: $file_id})
            SET m += $metadata
            RETURN m
            """
            
            session.run(query, source_file=source_file, file_id=file_id, metadata=metadata)
            
        except Exception as e:
            logger.warning(f"Failed to import metadata for {source_file} with file_id {file_id}: {e}")
    
    def execute_query(self, query: str) -> List[Dict]:
        """Execute a Cypher query and return results"""
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_query_raw(self, query: str) -> List:
        """Execute a Cypher query and return raw Neo4j objects (not converted to dict)"""
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return list(result)  # Return raw records with Neo4j objects
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def clear_database(self):
        """Clear all data from the database"""
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Database cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.driver.session() as session:
                stats = {}
                
                # Node count
                result = session.run("MATCH (n) RETURN count(n) as node_count")
                stats['total_nodes'] = result.single()['node_count']
                
                # Relationship count
                result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                stats['total_relationships'] = result.single()['rel_count']
                
                # Label counts
                result = session.run("CALL db.labels() YIELD label RETURN collect(label) as labels")
                labels = result.single()['labels']
                stats['labels'] = labels
                
                # Relationship types
                result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types")
                types = result.single()['types']
                stats['relationship_types'] = types
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def check_neo4j_ports(self) -> Dict[str, Any]:
        """Check if Neo4j ports are accessible"""
        try:
            import socket
            
            # Check Bolt port (7687 or 7688)
            bolt_port = 7687 if "7687" in self.uri else 7688
            http_port = 7474
            
            results = {}
            
            # Test Bolt port
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(('localhost', bolt_port))
                sock.close()
                results['bolt_port'] = {
                    'port': bolt_port,
                    'accessible': result == 0,
                    'status': 'open' if result == 0 else 'closed'
                }
            except Exception as e:
                results['bolt_port'] = {
                    'port': bolt_port,
                    'accessible': False,
                    'status': 'error',
                    'error': str(e)
                }
            
            # Test HTTP port
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(('localhost', http_port))
                sock.close()
                results['http_port'] = {
                    'port': http_port,
                    'accessible': result == 0,
                    'status': 'open' if result == 0 else 'closed'
                }
            except Exception as e:
                results['http_port'] = {
                    'port': http_port,
                    'accessible': False,
                    'status': 'error',
                    'error': str(e)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error checking Neo4j ports: {e}")
            return {
                'error': str(e)
            } 

    def check_docker_status(self) -> Dict[str, Any]:
        """Check if Docker Neo4j container is running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.docker_container_name}", "--format", "{{.Names}}"],
                capture_output=True, text=True, timeout=10
            )
            
            is_running = self.docker_container_name in result.stdout.strip()
            
            return {
                "success": True,
                "running": is_running,
                "container_name": self.docker_container_name,
                "status": "running" if is_running else "stopped"
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Docker command timeout"}
        except FileNotFoundError:
            return {"success": False, "error": "Docker not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_docker_connection(self) -> Dict[str, Any]:
        """Check if Docker Neo4j is accessible"""
        try:
            # Check if container is running
            docker_status = self.check_docker_status()
            if not docker_status["success"] or not docker_status["running"]:
                return {
                    "success": False,
                    "docker_running": False,
                    "browser_accessible": False,
                    "error": "Docker container not running"
                }

            # Check browser accessibility
            browser_accessible = False
            try:
                response = requests.get("http://localhost:7475", timeout=5)
                browser_accessible = response.status_code == 200
            except:
                pass

            return {
                "success": True,
                "docker_running": True,
                "browser_accessible": browser_accessible,
                "browser_url": "http://localhost:7475",
                "bolt_url": "bolt://localhost:7688"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def start_docker_neo4j(self) -> Dict[str, Any]:
        """Start Docker Neo4j container"""
        try:
            # Check if container already exists
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={self.docker_container_name}", "--format", "{{.Names}}"],
                capture_output=True, text=True, timeout=10
            )
            
            container_exists = self.docker_container_name in result.stdout.strip()
            
            if container_exists:
                # Start existing container
                result = subprocess.run(
                    ["docker", "start", self.docker_container_name],
                    capture_output=True, text=True, timeout=30
                )
            else:
                # Create and start new container
                result = subprocess.run([
                    "docker", "run", "-d",
                    "--name", self.docker_container_name,
                    "-p", "7475:7474",
                    "-p", "7688:7687",
                    "-e", "NEO4J_AUTH=neo4j/password",
                    "-e", "NEO4J_PLUGINS='[\"apoc\"]'",
                    "neo4j:5.15"
                ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Wait for container to be ready
                time.sleep(5)
                return {"success": True, "message": "Docker Neo4j started successfully"}
            else:
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Docker command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_docker_neo4j(self) -> Dict[str, Any]:
        """Stop Docker Neo4j container"""
        try:
            result = subprocess.run(
                ["docker", "stop", self.docker_container_name],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                return {"success": True, "message": "Docker Neo4j stopped successfully"}
            else:
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Docker command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_local_neo4j_desktop(self) -> Dict[str, Any]:
        """Check if Neo4j Desktop application is running"""
        try:
            from .neo4j_launcher import Neo4jDesktopLauncher
            launcher = Neo4jDesktopLauncher()
            return launcher.is_neo4j_running()
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_local_neo4j_connection(self) -> Dict[str, Any]:
        """Check if local Neo4j Desktop is accessible"""
        try:
            # Check if application is running
            desktop_status = self.check_local_neo4j_desktop()
            if not desktop_status["success"]:
                return {
                    "success": False,
                    "application_running": False,
                    "connection_available": False,
                    "error": "Failed to check application status"
                }

            application_running = desktop_status["running"]
            
            # Check browser accessibility
            connection_available = False
            try:
                response = requests.get(self.local_browser_url, timeout=5)
                connection_available = response.status_code == 200
            except:
                pass

            return {
                "success": True,
                "application_running": application_running,
                "connection_available": connection_available,
                "browser_url": self.local_browser_url,
                "bolt_url": self.local_bolt_url,
                "processes": desktop_status.get("processes", [])
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def launch_local_neo4j_desktop(self) -> Dict[str, Any]:
        """Launch Neo4j Desktop application"""
        try:
            from .neo4j_launcher import Neo4jDesktopLauncher
            launcher = Neo4jDesktopLauncher()
            return launcher.launch_neo4j_desktop()
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_local_neo4j_info(self) -> Dict[str, Any]:
        """Get comprehensive information about local Neo4j Desktop"""
        try:
            desktop_status = self.check_local_neo4j_desktop()
            connection_status = self.check_local_neo4j_connection()
            
            # Find executable path
            executable_path = None
            for path in self.local_neo4j_paths:
                if os.path.exists(path):
                    executable_path = path
                    break
            
            return {
                "success": True,
                "application_running": desktop_status.get("running", False),
                "connection_available": connection_status.get("connection_available", False),
                "executable_path": executable_path,
                "browser_url": self.local_browser_url,
                "bolt_url": self.local_bolt_url,
                "processes": desktop_status.get("processes", []),
                "status": {
                    "desktop": desktop_status,
                    "connection": connection_status
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_query_docker(self, query: str) -> List[Dict]:
        """Execute Cypher query using Docker Neo4j connection"""
        try:
            # Try to connect to Docker Neo4j
            docker_uri = "bolt://localhost:7688"
            docker_user = "neo4j"
            docker_password = "password"
            
            driver = GraphDatabase.driver(docker_uri, auth=(docker_user, docker_password))
            
            with driver.session() as session:
                result = session.run(query)
                records = []
                for record in result:
                    # Convert Neo4j record to dict
                    record_dict = {}
                    for key, value in record.items():
                        record_dict[key] = value
                    records.append(record_dict)
                
                driver.close()
                return records
                
        except Exception as e:
            logger.error(f"Docker query execution failed: {e}")
            raise

    def execute_query_local(self, query: str) -> List[Dict]:
        """Execute Cypher query using Local Neo4j connection"""
        try:
            # Try to connect to Local Neo4j
            local_uri = "bolt://localhost:7687"
            local_user = "neo4j"
            local_password = "password"  # This should be configurable
            
            driver = GraphDatabase.driver(local_uri, auth=(local_user, local_password))
            
            with driver.session() as session:
                result = session.run(query)
                records = []
                for record in result:
                    # Convert Neo4j record to dict
                    record_dict = {}
                    for key, value in record.items():
                        record_dict[key] = value
                    records.append(record_dict)
                
                driver.close()
                return records
                
        except Exception as e:
            logger.error(f"Local query execution failed: {e}")
            raise

# Global instance for management operations (no database connection)
neo4j_manager = Neo4jManager()

# Function to create database-connected instance
def create_neo4j_manager(uri: str, user: str, password: str) -> Neo4jManager:
    """Create a Neo4jManager instance with database connection"""
    return Neo4jManager(uri, user, password) 