"""
Neo4j Service Layer
Handles all Neo4j operations and business logic for the Knowledge Graph
"""

import logging
import os
from pathlib import Path
import sys
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path for imports
import sys
from pathlib import Path

# Get the project root directory (3 levels up from this file)
current_file = Path(__file__)
project_root = current_file.parent.parent.parent
src_path = project_root / "src"

# Add both project root and src to path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

try:
    # Import directly from the src module with specific path
    from src.kg_neo4j.neo4j_manager import Neo4jManager
    from src.kg_neo4j.graph_analyzer import AASXGraphAnalyzer
    logging.info("Successfully imported Neo4j modules")
except ImportError as e:
    logging.warning(f"Could not import Neo4j modules: {e}")
    logging.warning(f"Src path: {src_path}")
    logging.warning(f"Src exists: {src_path.exists()}")
    
    # Try alternative import paths
    try:
        from kg_neo4j.neo4j_manager import Neo4jManager
        from kg_neo4j.graph_analyzer import AASXGraphAnalyzer
        logging.info("Successfully imported Neo4j modules using alternative path")
    except ImportError as e2:
        logging.error(f"Alternative import also failed: {e2}")
        Neo4jManager = None
        AASXGraphAnalyzer = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jService:
    """Service class for Neo4j operations"""
    
    def __init__(self):
        self.neo4j_manager = None
        self.graph_analyzer = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize Neo4j connections"""
        try:
            # Docker Neo4j connection settings
            # The container is running on port 7688 (mapped from 7687)
            uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7688')
            user = os.getenv('NEO4J_USER', 'neo4j')
            password = os.getenv('NEO4J_PASSWORD', 'Neo4j123')
            
            logger.info(f"Connecting to Neo4j at {uri}")
            
            self.neo4j_manager = Neo4jManager(uri, user, password)
            self.graph_analyzer = AASXGraphAnalyzer(uri, user, password)
            
            # Test connection
            if not self.neo4j_manager.test_connection():
                logger.warning("Neo4j connection test failed, but continuing...")
                # Don't raise exception, just log warning
                
            logger.info("✓ Neo4j managers initialized")
            
        except Exception as e:
            logger.warning(f"Error initializing Neo4j connections: {e}")
            logger.warning("Neo4j service will be available but may not work until connection is established")
            self.neo4j_manager = None
            self.graph_analyzer = None
            # Don't raise exception, just set to None
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get Neo4j connection status"""
        try:
            if not self.neo4j_manager:
                return {
                    "status": "error",
                    "connected": False,
                    "neo4j_status": "disconnected",
                    "error": "Neo4j manager not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            is_connected = self.neo4j_manager.test_connection()
            
            return {
                "status": "connected" if is_connected else "disconnected",
                "connected": is_connected,
                "neo4j_status": "connected" if is_connected else "disconnected",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "connected": False,
                "neo4j_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def find_graph_files(self, directory: Path) -> List[Path]:
        """Find all graph files in the directory"""
        graph_files = []
        
        if directory.exists():
            # Find all *_graph.json files recursively
            graph_files = list(directory.rglob("*_graph.json"))
            logger.info(f"Found {len(graph_files)} graph files in {directory}")
        else:
            logger.error(f"Directory does not exist: {directory}")
        
        return graph_files
    
    def import_graph_data(self, directory: str, dry_run: bool = False) -> Dict[str, Any]:
        """Import graph data from ETL output directory"""
        try:
            if not self.neo4j_manager:
                raise Exception("Neo4j manager not initialized")
            
            import_dir = Path(directory)
            graph_files = self.find_graph_files(import_dir)
            
            if not graph_files:
                raise Exception(f"No graph files found in {import_dir}")
            
            results = {
                "total_files": len(graph_files),
                "imported_files": [],
                "failed_files": [],
                "dry_run": dry_run
            }
            
            for i, graph_file in enumerate(graph_files, 1):
                logger.info(f"Processing {i}/{len(graph_files)}: {graph_file.name}")
                
                if dry_run:
                    results["imported_files"].append({
                        "file": str(graph_file),
                        "status": "dry_run",
                        "message": "Would import"
                    })
                    continue
                
                try:
                    self.neo4j_manager.import_graph_file(graph_file)
                    results["imported_files"].append({
                        "file": str(graph_file),
                        "status": "success",
                        "message": "Successfully imported"
                    })
                except Exception as e:
                    results["failed_files"].append({
                        "file": str(graph_file),
                        "status": "error",
                        "message": str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error importing graph data: {e}")
            raise
    
    def import_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Import a single graph file"""
        try:
            if not self.neo4j_manager:
                raise Exception("Neo4j manager not initialized")
            
            if not file_path.exists():
                raise Exception(f"File not found: {file_path}")
            
            self.neo4j_manager.import_graph_file(file_path)
            
            return {
                "status": "success",
                "file": file_path.name,
                "message": "Successfully imported"
            }
            
        except Exception as e:
            logger.error(f"Error importing single file: {e}")
            raise
    
    def run_graph_analysis(self, export_file: Optional[str] = None) -> Dict[str, Any]:
        """Run comprehensive graph analysis"""
        try:
            if not self.graph_analyzer:
                raise Exception("Graph analyzer not initialized")
            
            results = {}
            
            # 1. Network Statistics
            try:
                stats = self.graph_analyzer.get_network_statistics()
                results['network_statistics'] = stats.to_dict('records') if not stats.empty else []
            except Exception as e:
                results['network_statistics'] = {"error": str(e)}
            
            # 2. Quality Distribution
            try:
                quality_dist = self.graph_analyzer.get_quality_distribution()
                results['quality_distribution'] = quality_dist.to_dict('records') if not quality_dist.empty else []
            except Exception as e:
                results['quality_distribution'] = {"error": str(e)}
            
            # 3. Compliance Analysis
            try:
                compliance = self.graph_analyzer.analyze_compliance_network()
                results['compliance_analysis'] = compliance.to_dict('records') if not compliance.empty else []
            except Exception as e:
                results['compliance_analysis'] = {"error": str(e)}
            
            # 4. Entity Type Distribution
            try:
                entity_dist = self.graph_analyzer.get_entity_type_distribution()
                results['entity_distribution'] = entity_dist.to_dict('records') if not entity_dist.empty else []
            except Exception as e:
                results['entity_distribution'] = {"error": str(e)}
            
            # 5. Relationship Analysis
            try:
                rel_analysis = self.graph_analyzer.analyze_relationships()
                results['relationship_analysis'] = rel_analysis.to_dict('records') if not rel_analysis.empty else []
            except Exception as e:
                results['relationship_analysis'] = {"error": str(e)}
            
            # Export to Excel if requested
            if export_file:
                try:
                    export_path = f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                        for analysis_name, data in results.items():
                            if isinstance(data, list) and data:
                                df = pd.DataFrame(data)
                                df.to_excel(writer, sheet_name=analysis_name[:31], index=False)
                    
                    results['export_file'] = export_path
                except Exception as e:
                    results['export_error'] = str(e)
            
            return results
            
        except Exception as e:
            logger.error(f"Error running graph analysis: {e}")
            raise
    
    def execute_custom_query(self, query: str) -> Dict[str, Any]:
        """Execute a custom Cypher query"""
        try:
            if not self.neo4j_manager:
                raise Exception("Neo4j manager not initialized")
            
            result = self.neo4j_manager.execute_query(query)
            
            if result:
                if isinstance(result, list) and result:
                    # Convert to DataFrame for better display
                    df = pd.DataFrame(result)
                    return {
                        "status": "success",
                        "results": df.to_dict('records'),
                        "columns": df.columns.tolist(),
                        "row_count": len(df)
                    }
                else:
                    return {
                        "status": "success",
                        "results": result,
                        "row_count": 1
                    }
            else:
                return {
                    "status": "success",
                    "results": [],
                    "row_count": 0,
                    "message": "No results returned"
                }
                
        except Exception as e:
            logger.error(f"Error executing custom query: {e}")
            raise
    
    def get_available_files(self) -> Dict[str, Any]:
        """Get list of available graph files in ETL output"""
        try:
            etl_output_dir = Path("output/etl_results/")
            graph_files = self.find_graph_files(etl_output_dir)
            
            return {
                "directory": str(etl_output_dir),
                "files": [str(f) for f in graph_files],
                "count": len(graph_files)
            }
        except Exception as e:
            logger.error(f"Error getting available files: {e}")
            raise
    
    def clear_graph_data(self) -> Dict[str, Any]:
        """Clear all data from Neo4j database"""
        try:
            if not self.neo4j_manager:
                raise Exception("Neo4j manager not initialized")
            
            self.neo4j_manager.clear_database()
            
            return {
                "status": "success",
                "message": "All graph data cleared successfully"
            }
        except Exception as e:
            logger.error(f"Error clearing graph data: {e}")
            raise

    def get_graph_data(self) -> Dict[str, Any]:
        """Get graph data for visualization"""
        try:
            if not self.neo4j_manager:
                raise Exception("Neo4j manager not initialized")
            
            logger.info("Fetching graph data from Neo4j...")
            
            # Get all nodes
            nodes_query = "MATCH (n) RETURN n"
            nodes_result = self.neo4j_manager.execute_query(nodes_query)
            logger.info(f"Found {len(nodes_result)} nodes")
            
            # Get all relationships
            relationships_query = "MATCH (n)-[r]->(m) RETURN n, r, m"
            relationships_result = self.neo4j_manager.execute_query(relationships_query)
            logger.info(f"Found {len(relationships_result)} relationships")
            
            # Process nodes
            nodes = []
            for record in nodes_result:
                try:
                    node_data = record['n']
                    # Handle different Neo4j node formats
                    if hasattr(node_data, 'identity'):
                        node_id = str(node_data.identity)
                    elif hasattr(node_data, 'id'):
                        node_id = node_data.id
                    else:
                        node_id = str(hash(node_data))
                    
                    # Get node type
                    node_type = 'unknown'
                    if hasattr(node_data, 'type'):
                        node_type = node_data.type
                    elif hasattr(node_data, 'labels') and node_data.labels:
                        node_type = list(node_data.labels)[0]
                    
                    # Get properties
                    properties = {}
                    if hasattr(node_data, '__iter__'):
                        properties = dict(node_data)
                    
                    node = {
                        'id': node_id,
                        'type': node_type,
                        'labels': list(node_data.labels) if hasattr(node_data, 'labels') else [],
                        'properties': properties
                    }
                    nodes.append(node)
                except Exception as e:
                    logger.warning(f"Error processing node: {e}")
                    continue
            
            # Process relationships
            relationships = []
            for record in relationships_result:
                try:
                    source = record['n']
                    target = record['m']
                    rel = record['r']
                    
                    # Get source and target IDs
                    source_id = str(source.identity) if hasattr(source, 'identity') else str(hash(source))
                    target_id = str(target.identity) if hasattr(target, 'identity') else str(hash(target))
                    
                    # Get relationship type
                    rel_type = type(rel).__name__ if hasattr(rel, '__class__') else 'RELATES_TO'
                    
                    relationship = {
                        'source': source_id,
                        'target': target_id,
                        'type': rel_type,
                        'properties': dict(rel) if hasattr(rel, '__iter__') else {}
                    }
                    relationships.append(relationship)
                except Exception as e:
                    logger.warning(f"Error processing relationship: {e}")
                    continue
            
            logger.info(f"Processed {len(nodes)} nodes and {len(relationships)} relationships")
            
            return {
                "success": True,
                "graph": {
                    "nodes": nodes,
                    "relationships": relationships
                },
                "node_count": len(nodes),
                "relationship_count": len(relationships)
            }
            
        except Exception as e:
            logger.error(f"Error getting graph data: {e}")
            return {
                "success": False,
                "error": str(e)
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
        """Get database statistics"""
        try:
            if not self.neo4j_manager:
                raise Exception("Neo4j manager not initialized")
            
            # Get total nodes
            nodes_query = "MATCH (n) RETURN count(n) as node_count"
            nodes_result = self.neo4j_manager.execute_query(nodes_query)
            node_count = nodes_result[0]['node_count'] if nodes_result else 0
            
            # Get total relationships
            rels_query = "MATCH ()-[r]->() RETURN count(r) as rel_count"
            rels_result = self.neo4j_manager.execute_query(rels_query)
            rel_count = rels_result[0]['rel_count'] if rels_result else 0
            
            # Get node types
            types_query = "MATCH (n) RETURN DISTINCT n.type as node_type"
            types_result = self.neo4j_manager.execute_query(types_query)
            node_types = [record['node_type'] for record in types_result if record['node_type']]
            
            # Get asset count
            assets_query = "MATCH (n) WHERE n.type = 'asset' RETURN count(n) as asset_count"
            assets_result = self.neo4j_manager.execute_query(assets_query)
            asset_count = assets_result[0]['asset_count'] if assets_result else 0
            
            # Get submodel count
            submodels_query = "MATCH (n) WHERE n.type = 'submodel' RETURN count(n) as submodel_count"
            submodels_result = self.neo4j_manager.execute_query(submodels_query)
            submodel_count = submodels_result[0]['submodel_count'] if submodels_result else 0
            
            return {
                "success": True,
                "stats": {
                    "total_nodes": node_count,
                    "total_relationships": rel_count,
                    "node_types": len(node_types),
                    "assets": asset_count,
                    "submodels": submodel_count,
                    "types": node_types
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
                    "node_types": 0,
                    "assets": 0,
                    "submodels": 0,
                    "types": []
                }
            }

    def debug_database(self) -> Dict[str, Any]:
        """Debug method to check database contents"""
        try:
            if not self.neo4j_manager:
                raise Exception("Neo4j manager not initialized")
            
            debug_info = {}
            
            # Check total nodes
            try:
                result = self.neo4j_manager.execute_query("MATCH (n) RETURN count(n) as count")
                debug_info['total_nodes'] = result[0]['count'] if result else 0
            except Exception as e:
                debug_info['total_nodes_error'] = str(e)
            
            # Check total relationships
            try:
                result = self.neo4j_manager.execute_query("MATCH ()-[r]->() RETURN count(r) as count")
                debug_info['total_relationships'] = result[0]['count'] if result else 0
            except Exception as e:
                debug_info['total_relationships_error'] = str(e)
            
            # Check node labels
            try:
                result = self.neo4j_manager.execute_query("CALL db.labels() YIELD label RETURN label")
                debug_info['labels'] = [record['label'] for record in result]
            except Exception as e:
                debug_info['labels_error'] = str(e)
            
            # Check relationship types
            try:
                result = self.neo4j_manager.execute_query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
                debug_info['relationship_types'] = [record['relationshipType'] for record in result]
            except Exception as e:
                debug_info['relationship_types_error'] = str(e)
            
            # Check sample nodes
            try:
                result = self.neo4j_manager.execute_query("MATCH (n) RETURN n LIMIT 3")
                debug_info['sample_nodes'] = []
                for record in result:
                    node = record['n']
                    debug_info['sample_nodes'].append({
                        'identity': str(node.identity) if hasattr(node, 'identity') else 'unknown',
                        'labels': list(node.labels) if hasattr(node, 'labels') else [],
                        'properties': dict(node) if hasattr(node, '__iter__') else {}
                    })
            except Exception as e:
                debug_info['sample_nodes_error'] = str(e)
            
            return {
                "success": True,
                "debug_info": debug_info
            }
            
        except Exception as e:
            logger.error(f"Error debugging database: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close Neo4j connections"""
        try:
            if self.neo4j_manager:
                self.neo4j_manager.close()
            if self.graph_analyzer:
                self.graph_analyzer.close()
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

# Global service instance
neo4j_service = None

def get_neo4j_service() -> Neo4jService:
    """Get or create Neo4j service instance"""
    global neo4j_service
    
    if neo4j_service is None:
        neo4j_service = Neo4jService()
    
    return neo4j_service 

def get_available_data_folders():
    """Get list of available data folders in the ETL output directory"""
    try:
        etl_output_path = Path("output/etl_results")
        if not etl_output_path.exists():
            return []
        
        folders = []
        for folder in etl_output_path.iterdir():
            if folder.is_dir():
                # Check if folder contains graph data
                graph_file = folder / "aasx_data_graph.json"
                if graph_file.exists():
                    folders.append({
                        "name": folder.name,
                        "path": str(folder),
                        "has_graph_data": True,
                        "file_count": len(list(folder.glob("*.json")))
                    })
                else:
                    folders.append({
                        "name": folder.name,
                        "path": str(folder),
                        "has_graph_data": False,
                        "file_count": len(list(folder.glob("*.json")))
                    })
        
        return sorted(folders, key=lambda x: x["name"])
    except Exception as e:
        print(f"Error discovering data folders: {e}")
        return [] 

def get_graph_stats():
    """Get basic graph statistics"""
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            # Get total nodes
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()["node_count"]
            
            # Get total relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = result.single()["rel_count"]
            
            # Get node types
            result = session.run("MATCH (n) RETURN DISTINCT n.type as node_type")
            node_types = [record["node_type"] for record in result if record["node_type"]]
            
            # Get asset count
            result = session.run("MATCH (n) WHERE n.type = 'asset' RETURN count(n) as asset_count")
            asset_count = result.single()["asset_count"]
            
            # Get submodel count
            result = session.run("MATCH (n) WHERE n.type = 'submodel' RETURN count(n) as submodel_count")
            submodel_count = result.single()["submodel_count"]
            
            return {
                "nodes": node_count,
                "relationships": rel_count,
                "labels": len(node_types),
                "assets": asset_count,
                "submodels": submodel_count
            }
    except Exception as e:
        print(f"Error getting graph stats: {e}")
        return {
            "nodes": 0,
            "relationships": 0,
            "labels": 0,
            "assets": 0,
            "submodels": 0
        } 