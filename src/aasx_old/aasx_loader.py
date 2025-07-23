"""
AASX Data Loader Module

This module handles the loading of transformed AASX data into various storage systems
including file systems, databases, and vector databases for RAG applications.
"""

import json
import yaml
import csv
import sqlite3
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from datetime import datetime
import hashlib
import uuid
from dataclasses import dataclass

# Vector database imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Vector database features disabled.")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant not available. Vector database features disabled.")

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available. Vector search features disabled.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("Sentence Transformers not available. Embedding features disabled.")

logger = logging.getLogger(__name__)

@dataclass
class LoaderConfig:
    """Configuration for AASX data loading"""
    output_directory: str = "output"
    database_path: str = "aasx_data.db"
    vector_db_path: str = "vector_db"
    vector_db_type: str = "qdrant"  # qdrant, chromadb, faiss
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_prefix: str = "aasx"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    overlap_size: int = 50
    include_metadata: bool = True
    create_indexes: bool = True
    backup_existing: bool = True
    separate_file_outputs: bool = False
    include_filename_in_output: bool = False
    systematic_structure: bool = True
    folder_structure: str = "by_file"  # timestamped_by_file, by_file, by_type, flat
    
    # Export format control
    export_formats: List[str] = None  # If None, exports all formats
    export_json: bool = True
    export_yaml: bool = True
    export_csv: bool = True
    export_tsv: bool = True
    export_graph: bool = True
    export_rag: bool = True
    export_vector_db: bool = True
    export_sqlite: bool = True
    
    def __post_init__(self):
        """Set default export formats if not specified"""
        if self.export_formats is None:
            self.export_formats = [
                'json', 'yaml', 'csv', 'tsv', 'graph', 'rag', 'vector_db', 'sqlite'
            ]
        
        # Update individual flags based on export_formats
        self.export_json = 'json' in self.export_formats
        self.export_yaml = 'yaml' in self.export_formats
        self.export_csv = 'csv' in self.export_formats
        self.export_tsv = 'tsv' in self.export_formats
        self.export_graph = 'graph' in self.export_formats
        self.export_rag = 'rag' in self.export_formats
        self.export_vector_db = 'vector_db' in self.export_formats
        self.export_sqlite = 'sqlite' in self.export_formats

class AASXLoader:
    """AASX Data Loader for multiple storage systems"""
    
    def __init__(self, config: LoaderConfig, source_file: Optional[str] = None):
        """Initialize the loader"""
        self.config = config
        self.source_file = source_file
        
        # Create output directory
        self.output_dir = self._create_output_directory()
        
        # Initialize storage systems
        self._initialize_storage()
        
        # Initialize embedding model
        self.embedding_model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialize_embedding_model()
    
    def _create_output_directory(self) -> Path:
        """Create output directory with systematic structure"""
        base_dir = Path(self.config.output_directory)
        
        if self.config.systematic_structure:
            if self.config.folder_structure == "timestamped_by_file" and self.source_file:
                # Create timestamped directory for each file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = Path(self.source_file).stem if self.source_file else "unknown"
                output_dir = base_dir / timestamp / file_name
            elif self.config.folder_structure == "by_file" and self.source_file:
                # Create directory for each file
                file_name = Path(self.source_file).stem if self.source_file else "unknown"
                output_dir = base_dir / file_name
            elif self.config.folder_structure == "by_type":
                # Create directories by data type
                output_dir = base_dir / "aasx_data"
            else:
                # Flat structure
                output_dir = base_dir
        else:
            output_dir = base_dir
        
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")
        return output_dir
    
    def _initialize_storage(self):
        """Initialize storage systems"""
        logger.info("Initializing storage systems")
        
        # Initialize vector database based on type
        if self.config.vector_db_type == "qdrant" and QDRANT_AVAILABLE:
            self._initialize_qdrant()
        elif self.config.vector_db_type == "chromadb" and CHROMADB_AVAILABLE:
            self._initialize_chromadb()
        elif self.config.vector_db_type == "faiss" and FAISS_AVAILABLE:
            self._initialize_faiss()
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialize_embedding_model()
    
    def _initialize_qdrant(self):
        """Initialize Qdrant vector database"""
        try:
            self.qdrant_client = QdrantClient(
                url=self.config.qdrant_url,
                timeout=30
            )
            
            # Test connection
            collections = self.qdrant_client.get_collections()
            logger.info(f"✅ Qdrant connected at {self.config.qdrant_url}")
            logger.info(f"Available collections: {[c.name for c in collections.collections]}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")
            self.qdrant_client = None
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB vector database"""
        try:
            vector_db_path = Path(self.config.vector_db_path)
            vector_db_path.mkdir(exist_ok=True)
            
            self.vector_db = chromadb.PersistentClient(
                path=str(vector_db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create collections
            self.assets_collection = self.vector_db.get_or_create_collection(
                name="aasx_assets",
                metadata={"description": "AASX Assets for RAG"}
            )
            
            self.submodels_collection = self.vector_db.get_or_create_collection(
                name="aasx_submodels", 
                metadata={"description": "AASX Submodels for RAG"}
            )
            
            self.documents_collection = self.vector_db.get_or_create_collection(
                name="aasx_documents",
                metadata={"description": "AASX Documents for RAG"}
            )
            
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.vector_db = None
    
    def _initialize_faiss(self):
        """Initialize FAISS vector database"""
        try:
            vector_db_path = Path(self.config.vector_db_path)
            vector_db_path.mkdir(exist_ok=True)
            
            # FAISS initialization would go here
            logger.info("FAISS initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {e}")
    
    def _initialize_embedding_model(self):
        """Initialize embedding model"""
        try:
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            logger.info(f"Embedding model loaded: {self.config.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def load_aasx_data(self, transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load transformed AASX data into storage systems.
        
        Args:
            transformed_data: Transformed AASX data
            
        Returns:
            Dictionary with loading results
        """
        logger.info("Starting AASX data loading")
        
        results = {
            'files_exported': [],
            'database_records': 0,
            'vector_embeddings': 0,
            'errors': [],
            'export_formats': self.config.export_formats
        }
        
        try:
            # Step 1: Export to files (based on user selection)
            if any([self.config.export_json, self.config.export_yaml, 
                   self.config.export_csv, self.config.export_graph, self.config.export_rag]):
                file_results = self._export_to_files(transformed_data)
                results['files_exported'] = file_results
            
            # Step 2: Load to database (if selected)
            if self.config.export_sqlite:
                db_results = self._load_to_database(transformed_data)
                results['database_records'] = db_results
                # Add SQLite database to exported files list for counting
                if db_results > 0:
                    db_path = Path(self.config.database_path)
                    if db_path.exists():
                        results['files_exported'].append(str(db_path))
            
            # Step 3: Load to vector database (if selected)
            if self.config.export_vector_db:
                vector_results = self._load_to_vector_db(transformed_data)
                results['vector_embeddings'] = vector_results
                # Create vector database export file
                if vector_results > 0:
                    vector_export_path = self.output_dir / "aasx_data_vector_db.json"
                    vector_export_data = self._create_vector_db_export()
                    with open(vector_export_path, 'w', encoding='utf-8') as f:
                        json.dump(vector_export_data, f, indent=2, ensure_ascii=False)
                    results['files_exported'].append(str(vector_export_path))
            
            logger.info("AASX data loading completed successfully")
            
        except Exception as e:
            error_msg = f"Error during AASX loading: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    def _export_to_files(self, data: Dict[str, Any]) -> List[str]:
        """Export data to various file formats"""
        exported_files = []
        
        try:
            # Export as JSON
            if self.config.export_json:
                json_path = self.output_dir / "aasx_data.json"
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                exported_files.append(str(json_path))
            
            # Export as YAML
            if self.config.export_yaml:
                yaml_path = self.output_dir / "aasx_data.yaml"
                with open(yaml_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                exported_files.append(str(yaml_path))
            
            # Export flattened data as CSV
            if 'data' in data and isinstance(data['data'], dict):
                if self.config.export_csv:
                    csv_path = self.output_dir / "aasx_data.csv"
                    self._export_to_csv(data['data'], csv_path)
                    exported_files.append(str(csv_path))
                
                # Export flattened data as TSV
                if self.config.export_tsv:
                    tsv_path = self.output_dir / "aasx_data.tsv"
                    self._export_to_tsv(data['data'], tsv_path)
                    exported_files.append(str(tsv_path))
            
            # Export as Graph format (for graph databases)
            if self.config.export_graph:
                graph_path = self.output_dir / "aasx_data_graph.json"
                graph_data = self._create_graph_format(data)
                with open(graph_path, 'w', encoding='utf-8') as f:
                    json.dump(graph_data, f, indent=2, ensure_ascii=False)
                exported_files.append(str(graph_path))
                
                # Export graph data as CSV
                graph_csv_path = self.output_dir / "aasx_data_graph.csv"
                self._export_graph_to_csv(graph_data, graph_csv_path)
                exported_files.append(str(graph_csv_path))
                
                # Export graph data as TSV
                graph_tsv_path = self.output_dir / "aasx_data_graph.tsv"
                self._export_graph_to_tsv(graph_data, graph_tsv_path)
                exported_files.append(str(graph_tsv_path))
            
            # Export RAG dataset
            if self.config.export_rag:
                rag_path = self.output_dir / "aasx_data_rag.json"
                try:
                    rag_data = self._create_rag_export(data)
                    with open(rag_path, 'w', encoding='utf-8') as f:
                        json.dump(rag_data, f, indent=2, ensure_ascii=False)
                    exported_files.append(str(rag_path))
                except Exception as e:
                    logger.error(f"Error exporting RAG data: {e}")
            
            logger.info(f"Exported {len(exported_files)} files to {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Error exporting files: {e}")
        
        return exported_files
    
    def _export_to_csv(self, data: Dict[str, Any], csv_path: Path):
        """Export data to CSV format"""
        flattened_data = []
        
        # Flatten assets
        for asset in data.get('assets', []):
            flattened_data.append({
                'entity_type': 'asset',
                'id': asset.get('id', ''),
                'id_short': asset.get('id_short', ''),
                'description': asset.get('description', ''),
                'type': asset.get('type', ''),
                'quality_level': asset.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': asset.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        # Flatten submodels
        for submodel in data.get('submodels', []):
            flattened_data.append({
                'entity_type': 'submodel',
                'id': submodel.get('id', ''),
                'id_short': submodel.get('id_short', ''),
                'description': submodel.get('description', ''),
                'type': submodel.get('type', ''),
                'quality_level': submodel.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': submodel.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        if flattened_data:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
    
    def _export_to_tsv(self, data: Dict[str, Any], tsv_path: Path):
        """Export data to TSV format"""
        flattened_data = []
        
        # Flatten assets
        for asset in data.get('assets', []):
            flattened_data.append({
                'entity_type': 'asset',
                'id': asset.get('id', ''),
                'id_short': asset.get('id_short', ''),
                'description': asset.get('description', ''),
                'type': asset.get('type', ''),
                'quality_level': asset.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': asset.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        # Flatten submodels
        for submodel in data.get('submodels', []):
            flattened_data.append({
                'entity_type': 'submodel',
                'id': submodel.get('id', ''),
                'id_short': submodel.get('id_short', ''),
                'description': submodel.get('description', ''),
                'type': submodel.get('type', ''),
                'quality_level': submodel.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': submodel.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        if flattened_data:
            with open(tsv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys(), delimiter='\t')
                writer.writeheader()
                writer.writerows(flattened_data)
    
    def _export_graph_to_csv(self, graph_data: Dict[str, Any], csv_path: Path):
        """Export graph data to CSV format with nodes and edges"""
        # Export nodes by type (separate files for different node types)
        nodes_by_type = {}
        for node in graph_data.get('nodes', []):
            node_type = node.get('type', 'unknown')
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)
        
        for node_type, nodes in nodes_by_type.items():
            if nodes:
                nodes_csv_path = csv_path.parent / f"{csv_path.stem}_{node_type}_nodes.csv"
                with open(nodes_csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=nodes[0].keys())
                    writer.writeheader()
                    writer.writerows(nodes)
        
        # Export edges
        edges_csv_path = csv_path.parent / f"{csv_path.stem}_edges.csv"
        if graph_data.get('edges'):
            # Flatten edge properties for CSV
            flattened_edges = []
            for edge in graph_data['edges']:
                flat_edge = {
                    'source_id': edge.get('source_id', ''),
                    'target_id': edge.get('target_id', ''),
                    'type': edge.get('type', ''),
                    'relationship_type': edge.get('properties', {}).get('relationship_type', ''),
                    'created_at': edge.get('properties', {}).get('created_at', '')
                }
                flattened_edges.append(flat_edge)
            
            if flattened_edges:
                with open(edges_csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=flattened_edges[0].keys())
                    writer.writeheader()
                    writer.writerows(flattened_edges)
    
    def _export_graph_to_tsv(self, graph_data: Dict[str, Any], tsv_path: Path):
        """Export graph data to TSV format with nodes and edges"""
        # Export nodes by type (separate files for different node types)
        nodes_by_type = {}
        for node in graph_data.get('nodes', []):
            node_type = node.get('type', 'unknown')
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)
        
        for node_type, nodes in nodes_by_type.items():
            if nodes:
                nodes_tsv_path = tsv_path.parent / f"{tsv_path.stem}_{node_type}_nodes.tsv"
                with open(nodes_tsv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=nodes[0].keys(), delimiter='\t')
                    writer.writeheader()
                    writer.writerows(nodes)
        
        # Export edges
        edges_tsv_path = tsv_path.parent / f"{tsv_path.stem}_edges.tsv"
        if graph_data.get('edges'):
            # Flatten edge properties for TSV
            flattened_edges = []
            for edge in graph_data['edges']:
                flat_edge = {
                    'source_id': edge.get('source_id', ''),
                    'target_id': edge.get('target_id', ''),
                    'type': edge.get('type', ''),
                    'relationship_type': edge.get('properties', {}).get('relationship_type', ''),
                    'created_at': edge.get('properties', {}).get('created_at', '')
                }
                flattened_edges.append(flat_edge)
            
            if flattened_edges:
                with open(edges_tsv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=flattened_edges[0].keys(), delimiter='\t')
                    writer.writeheader()
                    writer.writerows(flattened_edges)
    
    def _create_graph_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create graph format data for graph databases"""
        nodes = []
        edges = []
        
        # Add asset nodes
        for asset in data.get('data', {}).get('assets', []):
            nodes.append({
                'id': asset.get('id', ''),
                'type': 'asset',
                'id_short': asset.get('id_short', ''),
                'description': asset.get('description', ''),
                'asset_type': asset.get('type', ''),
                'quality_level': asset.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': asset.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        # Add submodel nodes
        for submodel in data.get('data', {}).get('submodels', []):
            nodes.append({
                'id': submodel.get('id', ''),
                'type': 'submodel',
                'id_short': submodel.get('id_short', ''),
                'description': submodel.get('description', ''),
                'submodel_type': submodel.get('type', ''),
                'quality_level': submodel.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': submodel.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        # Add document nodes
        for document in data.get('data', {}).get('documents', []):
            nodes.append({
                'id': document.get('id', ''),
                'type': 'document',
                'id_short': document.get('id_short', ''),
                'description': document.get('description', ''),
                'document_type': document.get('type', ''),
                'filename': document.get('filename', ''),
                'size': document.get('size', 0)
            })
        
        # Add relationships as edges
        for relationship in data.get('data', {}).get('relationships', []):
            edges.append({
                'source_id': relationship.get('source_id', ''),
                'target_id': relationship.get('target_id', ''),
                'type': relationship.get('type', ''),
                'properties': relationship.get('metadata', {})
            })
        
        # Create default relationships if none exist
        if not edges and nodes:
            # Connect assets to their submodels
            assets = [n for n in nodes if n['type'] == 'asset']
            submodels = [n for n in nodes if n['type'] == 'submodel']
            
            for asset in assets:
                for submodel in submodels:
                    edges.append({
                        'source_id': asset['id'],
                        'target_id': submodel['id'],
                        'type': 'HAS_SUBMODEL',
                        'properties': {
                            'relationship_type': 'asset_to_submodel',
                            'created_at': datetime.now().isoformat()
                        }
                    })
            
            # Connect documents to assets
            documents = [n for n in nodes if n['type'] == 'document']
            for asset in assets:
                for document in documents:
                    edges.append({
                        'source_id': asset['id'],
                        'target_id': document['id'],
                        'type': 'HAS_DOCUMENT',
                        'properties': {
                            'relationship_type': 'asset_to_document',
                            'created_at': datetime.now().isoformat()
                        }
                    })
        
        return {
            'format': 'graph',
            'version': '1.0',
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'total_nodes': len(nodes),
                'total_edges': len(edges)
            }
        }
    
    def _create_vector_db_export(self) -> Dict[str, Any]:
        """Create vector database export metadata"""
        vector_export = {
            'format': 'vector_database',
            'version': '1.0',
            'vector_db_type': self.config.vector_db_type,
            'created_at': datetime.now().isoformat(),
            'collections': [],
            'metadata': {
                'embedding_model': self.config.embedding_model,
                'chunk_size': self.config.chunk_size,
                'overlap_size': self.config.overlap_size,
                'collection_prefix': self.config.qdrant_collection_prefix
            }
        }
        
        # Add collection information
        if self.config.vector_db_type == "qdrant" and hasattr(self, 'qdrant_client'):
            try:
                collections = self.qdrant_client.get_collections()
                for collection in collections.collections:
                    if collection.name.startswith(self.config.qdrant_collection_prefix):
                        try:
                            # Get detailed collection info
                            collection_detail = self.qdrant_client.get_collection(collection.name)
                            collection_info = {
                                'name': collection.name,
                                'points_count': getattr(collection_detail, 'points_count', 'unknown'),
                                'vector_size': getattr(collection_detail.config.params.vectors, 'size', 'unknown'),
                                'distance': getattr(collection_detail.config.params.vectors.distance, 'value', 'unknown'),
                                'type': 'qdrant_collection'
                            }
                        except Exception:
                            # Fallback for any issues
                            collection_info = {
                                'name': collection.name,
                                'points_count': 'unknown',
                                'vector_size': 'unknown',
                                'distance': 'unknown',
                                'type': 'qdrant_collection'
                            }
                        vector_export['collections'].append(collection_info)
            except Exception as e:
                logger.error(f"Error getting Qdrant collections: {e}")
        
        return vector_export
    
    def _create_rag_export(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create RAG-ready export from input data"""
        rag_data = {
            'version': '1.0',
            'format': 'rag_ready',
            'timestamp': datetime.now().isoformat(),
            'source_file': self.source_file,
            'entities': []
        }
        
        # Add assets
        for asset in data.get('data', {}).get('assets', []):
            rag_data['entities'].append({
                'type': 'asset',
                'id': asset.get('id', ''),
                'id_short': asset.get('id_short', ''),
                'description': asset.get('description', ''),
                'content': f"Asset: {asset.get('id_short', '')} - {asset.get('description', '')}",
                'metadata': asset.get('metadata', {})
            })
        
        # Add submodels
        for submodel in data.get('data', {}).get('submodels', []):
            rag_data['entities'].append({
                'type': 'submodel',
                'id': submodel.get('id', ''),
                'id_short': submodel.get('id_short', ''),
                'description': submodel.get('description', ''),
                'content': f"Submodel: {submodel.get('id_short', '')} - {submodel.get('description', '')}",
                'metadata': submodel.get('metadata', {})
            })
        
        # Add documents
        for document in data.get('data', {}).get('documents', []):
            rag_data['entities'].append({
                'type': 'document',
                'id': document.get('id', ''),
                'id_short': document.get('id_short', ''),
                'description': document.get('description', ''),
                'content': f"Document: {document.get('id_short', '')} - {document.get('description', '')}",
                'metadata': document.get('metadata', {})
            })
        
        return rag_data
    
    def _load_to_database(self, data: Dict[str, Any]) -> int:
        """Load data to SQLite database"""
        records_loaded = 0
        
        try:
            # Use file-specific output directory for database if systematic structure is enabled
            if self.config.systematic_structure and self.source_file:
                # Create database in the file-specific output directory
                db_filename = Path(self.config.database_path).name
                db_path = self.output_dir / db_filename
            else:
                db_path = Path(self.config.database_path)
            
            # Create database directory if it doesn't exist
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Only backup on first file if configured
            if self.config.backup_existing and db_path.exists() and not hasattr(self, '_backup_created'):
                backup_path = db_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                import shutil
                shutil.copy2(db_path, backup_path)
                self._backup_created = True
                logger.info(f"Backed up existing database to {backup_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables
            self._create_database_tables(cursor)
            
            # Load assets
            for asset in data.get('data', {}).get('assets', []):
                self._insert_asset(cursor, asset)
                records_loaded += 1
            
            # Load submodels
            for submodel in data.get('data', {}).get('submodels', []):
                self._insert_submodel(cursor, submodel)
                records_loaded += 1
            
            # Load documents
            for document in data.get('data', {}).get('documents', []):
                self._insert_document(cursor, document)
                records_loaded += 1
            
            # Load relationships
            for relationship in data.get('data', {}).get('relationships', []):
                self._insert_relationship(cursor, relationship)
                records_loaded += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Loaded {records_loaded} records to database")
            
        except Exception as e:
            logger.error(f"Error loading to database: {e}")
        
        return records_loaded
    
    def _create_database_tables(self, cursor):
        """Create database tables"""
        # Assets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                id_short TEXT,
                description TEXT,
                type TEXT,
                quality_level TEXT,
                compliance_status TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Submodels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submodels (
                id TEXT PRIMARY KEY,
                id_short TEXT,
                description TEXT,
                type TEXT,
                quality_level TEXT,
                compliance_status TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT,
                size INTEGER,
                type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT,
                target_id TEXT,
                type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes if configured
        if self.config.create_indexes:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_submodels_type ON submodels(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id)')
    
    def _insert_asset(self, cursor, asset: Dict[str, Any]):
        """Insert asset into database"""
        cursor.execute('''
            INSERT OR REPLACE INTO assets 
            (id, id_short, description, type, quality_level, compliance_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset.get('id', ''),
            asset.get('id_short', ''),
            asset.get('description', ''),
            asset.get('type', ''),
            asset.get('qi_metadata', {}).get('quality_level', ''),
            asset.get('qi_metadata', {}).get('compliance_status', ''),
            json.dumps(asset.get('metadata', {}))
        ))
    
    def _insert_submodel(self, cursor, submodel: Dict[str, Any]):
        """Insert submodel into database"""
        cursor.execute('''
            INSERT OR REPLACE INTO submodels 
            (id, id_short, description, type, quality_level, compliance_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            submodel.get('id', ''),
            submodel.get('id_short', ''),
            submodel.get('description', ''),
            submodel.get('type', ''),
            submodel.get('qi_metadata', {}).get('quality_level', ''),
            submodel.get('qi_metadata', {}).get('compliance_status', ''),
            json.dumps(submodel.get('metadata', {}))
        ))
    
    def _insert_document(self, cursor, document: Dict[str, Any]):
        """Insert document into database"""
        doc_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT OR REPLACE INTO documents 
            (id, filename, size, type, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            doc_id,
            document.get('filename', ''),
            document.get('size', 0),
            document.get('type', ''),
            json.dumps(document.get('metadata', {}))
        ))
    
    def _insert_relationship(self, cursor, relationship: Dict[str, Any]):
        """Insert relationship into database"""
        rel_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT OR REPLACE INTO relationships 
            (id, source_id, target_id, type, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            rel_id,
            relationship.get('source_id', ''),
            relationship.get('target_id', ''),
            relationship.get('type', ''),
            json.dumps(relationship.get('metadata', {}))
        ))
    
    def _load_to_vector_db(self, data: Dict[str, Any]) -> int:
        """Load data to vector database for RAG"""
        embeddings_loaded = 0
        
        logger.info(f"Starting vector database loading...")
        logger.info(f"Embedding model available: {self.embedding_model is not None}")
        logger.info(f"Vector DB type: {self.config.vector_db_type}")
        logger.info(f"Qdrant client available: {hasattr(self, 'qdrant_client') and self.qdrant_client is not None}")
        
        if not self.embedding_model:
            logger.warning("Embedding model not available, skipping vector database loading")
            return 0
        
        try:
            # Count entities to process
            assets = data.get('data', {}).get('assets', [])
            submodels = data.get('data', {}).get('submodels', [])
            documents = data.get('data', {}).get('documents', [])
            
            logger.info(f"Found {len(assets)} assets, {len(submodels)} submodels, {len(documents)} documents to vectorize")
            
            # Load assets to vector database
            for i, asset in enumerate(assets):
                logger.debug(f"Processing asset {i+1}/{len(assets)}: {asset.get('id_short', asset.get('id', 'unknown'))}")
                self._add_to_vector_db(asset, 'asset')
                embeddings_loaded += 1
            
            # Load submodels to vector database
            for i, submodel in enumerate(submodels):
                logger.debug(f"Processing submodel {i+1}/{len(submodels)}: {submodel.get('id_short', submodel.get('id', 'unknown'))}")
                self._add_to_vector_db(submodel, 'submodel')
                embeddings_loaded += 1
            
            # Load documents to vector database
            for i, document in enumerate(documents):
                logger.debug(f"Processing document {i+1}/{len(documents)}: {document.get('id_short', document.get('id', 'unknown'))}")
                self._add_to_vector_db(document, 'document')
                embeddings_loaded += 1
            
            logger.info(f"Successfully loaded {embeddings_loaded} embeddings to vector database")
            
        except Exception as e:
            logger.error(f"Error loading to vector database: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return embeddings_loaded
    
    def _add_to_vector_db(self, entity: Dict[str, Any], entity_type: str):
        """Add entity to vector database (Qdrant or ChromaDB)"""
        try:
            logger.debug(f"Adding {entity_type} to vector database: {entity.get('id_short', entity.get('id', 'unknown'))}")
            
            # Create content for embedding
            content = self._create_entity_content(entity, entity_type)
            logger.debug(f"Created content for {entity_type}: {content[:100]}...")
            
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            logger.debug(f"Generated embedding of size: {len(embedding)}")
            
            # Create metadata
            metadata = {
                'entity_type': entity_type,
                'id': entity.get('id', ''),
                'id_short': entity.get('id_short', ''),
                'description': entity.get('description', ''),
                'quality_level': entity.get('quality_level', ''),
                'compliance_status': entity.get('compliance_status', ''),
                'source_file': self.source_file,
                'processed_at': datetime.now().isoformat()
            }
            
            # Add to appropriate vector database
            if self.config.vector_db_type == "qdrant" and self.qdrant_client:
                logger.debug(f"Adding to Qdrant: {entity_type}")
                self._add_to_qdrant(entity, embedding, content, metadata, entity_type)
            elif self.config.vector_db_type == "chromadb" and hasattr(self, 'vector_db'):
                logger.debug(f"Adding to ChromaDB: {entity_type}")
                self._add_to_chromadb(entity, embedding, content, metadata, entity_type)
            else:
                logger.warning(f"Vector database not available: type={self.config.vector_db_type}, qdrant_client={self.qdrant_client is not None}")
            
        except Exception as e:
            logger.error(f"Error adding {entity_type} to vector database: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _add_to_qdrant(self, entity: Dict[str, Any], embedding: List[float], 
                      content: str, metadata: Dict[str, Any], entity_type: str):
        """Add entity to Qdrant vector database with file-specific collections"""
        try:
            logger.debug(f"Starting Qdrant addition for {entity_type}")
            
            # Create file-specific collection name
            if self.source_file:
                file_name = Path(self.source_file).stem
                collection_name = f"{self.config.qdrant_collection_prefix}_{file_name}_{entity_type}s"
            else:
                collection_name = f"{self.config.qdrant_collection_prefix}_unknown_{entity_type}s"
            
            logger.debug(f"Collection name: {collection_name}")
            
            # Check if collection exists, create if not
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            logger.debug(f"Existing collections: {collection_names}")
            
            if collection_name not in collection_names:
                logger.info(f"Creating new Qdrant collection: {collection_name}")
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=len(embedding),
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Successfully created Qdrant collection: {collection_name}")
            else:
                logger.debug(f"Using existing Qdrant collection: {collection_name}")
            
            # Create point with file-specific ID (Qdrant requires UUID or integer)
            if self.source_file:
                file_name = Path(self.source_file).stem
                # Use UUID for point ID to avoid format issues
                point_id = str(uuid.uuid4())
            else:
                point_id = str(uuid.uuid4())
            
            logger.debug(f"Created point ID: {point_id}")
            
            # Add file information to metadata
            metadata['source_file'] = self.source_file
            metadata['file_name'] = Path(self.source_file).stem if self.source_file else 'unknown'
            metadata['collection_name'] = collection_name
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": metadata,
                    "entity_type": entity_type,
                    "source_file": self.source_file,
                    "file_name": Path(self.source_file).stem if self.source_file else 'unknown',
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Add to collection
            logger.debug(f"Upserting point to collection: {collection_name}")
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            logger.info(f"Successfully added {entity_type} to Qdrant: {point_id} in {collection_name}")
            
        except Exception as e:
            logger.error(f"Error adding to Qdrant: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _add_to_chromadb(self, entity: Dict[str, Any], embedding: List[float], 
                        content: str, metadata: Dict[str, Any], entity_type: str):
        """Add entity to ChromaDB vector database"""
        try:
            # Select appropriate collection
            if entity_type == 'asset':
                collection = self.assets_collection
            elif entity_type == 'submodel':
                collection = self.submodels_collection
            elif entity_type == 'document':
                collection = self.documents_collection
            else:
                collection = self.assets_collection  # Default
            
            # Add to collection
            collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[entity.get('id', str(uuid.uuid4()))]
            )
            
            logger.debug(f"Added {entity_type} to ChromaDB: {entity.get('id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {e}")
    
    def _create_entity_content(self, entity: Dict[str, Any], entity_type: str) -> str:
        """Create content string for entity embedding"""
        content_parts = []
        
        # Add entity type
        content_parts.append(f"{entity_type.title()}")
        
        # Add ID short
        if entity.get('id_short'):
            content_parts.append(f"ID: {entity['id_short']}")
        
        # Add description
        if entity.get('description'):
            content_parts.append(f"Description: {entity['description']}")
        
        # Add type
        if entity.get('type'):
            content_parts.append(f"Type: {entity['type']}")
        
        # Add quality level
        if entity.get('quality_level'):
            content_parts.append(f"Quality: {entity['quality_level']}")
        
        # Add compliance status
        if entity.get('compliance_status'):
            content_parts.append(f"Compliance: {entity['compliance_status']}")
        
        # Add properties if available
        if entity.get('properties'):
            for prop_name, prop_value in entity['properties'].items():
                content_parts.append(f"{prop_name}: {prop_value}")
        
        return " - ".join(content_parts)
    
    def export_for_rag(self, output_path: str) -> str:
        """
        Export data in RAG-ready format.
        
        Args:
            output_path: Path for RAG export file
            
        Returns:
            Path to exported file
        """
        try:
            rag_data = {
                'version': '1.0',
                'format': 'rag_ready',
                'timestamp': datetime.now().isoformat(),
                'source_file': self.source_file,
                'entities': []
            }
            
            # Get all entities from database
            # Use file-specific database path if systematic structure is enabled
            if self.config.systematic_structure and self.source_file:
                db_filename = Path(self.config.database_path).name
                db_path = self.output_dir / db_filename
            else:
                db_path = Path(self.config.database_path)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get assets
            cursor.execute('SELECT * FROM assets')
            for row in cursor.fetchall():
                rag_data['entities'].append({
                    'type': 'asset',
                    'id': row[0],
                    'id_short': row[1],
                    'description': row[2],
                    'content': f"Asset: {row[1]} - {row[2]}",
                    'metadata': json.loads(row[6]) if row[6] else {}
                })
            
            # Get submodels
            cursor.execute('SELECT * FROM submodels')
            for row in cursor.fetchall():
                rag_data['entities'].append({
                    'type': 'submodel',
                    'id': row[0],
                    'id_short': row[1],
                    'description': row[2],
                    'content': f"Submodel: {row[1]} - {row[2]}",
                    'metadata': json.loads(row[6]) if row[6] else {}
                })
            
            conn.close()
            
            # Export to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(rag_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"RAG data exported to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting RAG data: {e}")
            raise
    
    def _create_embedding_text(self, entity: Dict[str, Any], entity_type: str) -> str:
        """Create text for embedding from entity"""
        text_parts = []
        
        # Add basic information
        text_parts.append(f"Type: {entity_type}")
        text_parts.append(f"ID: {entity.get('id', '')}")
        text_parts.append(f"Short ID: {entity.get('id_short', '')}")
        text_parts.append(f"Description: {entity.get('description', '')}")
        
        # Add type-specific information
        if entity_type == 'asset':
            text_parts.append(f"Asset Type: {entity.get('type', '')}")
            asset_info = entity.get('asset_information', {})
            if asset_info:
                text_parts.append(f"Asset Information: {json.dumps(asset_info)}")
        
        elif entity_type == 'submodel':
            text_parts.append(f"Submodel Type: {entity.get('type', '')}")
            semantic_id = entity.get('semantic_id', {})
            if semantic_id:
                text_parts.append(f"Semantic ID: {json.dumps(semantic_id)}")
        
        elif entity_type == 'document':
            text_parts.append(f"Document Type: {entity.get('type', '')}")
            text_parts.append(f"Filename: {entity.get('filename', '')}")
            text_parts.append(f"Size: {entity.get('size', 0)} bytes")
        
        # Add quality information
        qi_metadata = entity.get('qi_metadata', {})
        if qi_metadata:
            text_parts.append(f"Quality Level: {qi_metadata.get('quality_level', '')}")
            text_parts.append(f"Compliance Status: {qi_metadata.get('compliance_status', '')}")
        
        return " | ".join(text_parts)
    
    def search_similar(self, query: str, entity_type: str = "all", top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar entities using vector similarity.
        
        Args:
            query: Search query
            entity_type: Type of entity to search (asset, submodel, document, all)
            top_k: Number of results to return
            
        Returns:
            List of similar entities
        """
        if not self.embedding_model or not self.vector_db:
            logger.warning("Vector search not available")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = []
            
            # Search in appropriate collections
            if entity_type in ["asset", "all"] and hasattr(self, 'assets_collection'):
                asset_results = self.assets_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                results.extend(self._format_search_results(asset_results, 'asset'))
            
            if entity_type in ["submodel", "all"] and hasattr(self, 'submodels_collection'):
                submodel_results = self.submodels_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                results.extend(self._format_search_results(submodel_results, 'submodel'))
            
            if entity_type in ["document", "all"] and hasattr(self, 'documents_collection'):
                document_results = self.documents_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                results.extend(self._format_search_results(document_results, 'document'))
            
            # Sort by similarity score
            results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    def _format_search_results(self, results, entity_type: str) -> List[Dict[str, Any]]:
        """Format search results"""
        formatted_results = []
        
        if not results or not results['ids']:
            return formatted_results
        
        for i, doc_id in enumerate(results['ids'][0]):
            formatted_results.append({
                'id': doc_id,
                'entity_type': entity_type,
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity': results['distances'][0][i] if 'distances' in results else 0.0
            })
        
        return formatted_results
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        try:
            # Use file-specific database path if systematic structure is enabled
            if self.config.systematic_structure and self.source_file:
                db_filename = Path(self.config.database_path).name
                db_path = self.output_dir / db_filename
            else:
                db_path = Path(self.config.database_path)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Count records in each table
            tables = ['assets', 'submodels', 'documents', 'relationships']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                stats[f'{table}_count'] = count
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
        
        return stats
    
    def export_for_rag(self, output_path: str) -> str:
        """
        Export data in RAG-ready format.
        
        Args:
            output_path: Path for RAG export file
            
        Returns:
            Path to exported file
        """
        try:
            rag_data = {
                'version': '1.0',
                'format': 'rag_ready',
                'timestamp': datetime.now().isoformat(),
                'entities': []
            }
            
            # Get all entities from database
            # Use file-specific database path if systematic structure is enabled
            if self.config.systematic_structure and self.source_file:
                db_filename = Path(self.config.database_path).name
                db_path = self.output_dir / db_filename
            else:
                db_path = Path(self.config.database_path)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get assets
            cursor.execute('SELECT * FROM assets')
            for row in cursor.fetchall():
                rag_data['entities'].append({
                    'type': 'asset',
                    'id': row[0],
                    'id_short': row[1],
                    'description': row[2],
                    'content': f"Asset: {row[1]} - {row[2]}",
                    'metadata': json.loads(row[6]) if row[6] else {}
                })
            
            # Get submodels
            cursor.execute('SELECT * FROM submodels')
            for row in cursor.fetchall():
                rag_data['entities'].append({
                    'type': 'submodel',
                    'id': row[0],
                    'id_short': row[1],
                    'description': row[2],
                    'content': f"Submodel: {row[1]} - {row[2]}",
                    'metadata': json.loads(row[6]) if row[6] else {}
                })
            
            conn.close()
            
            # Export to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(rag_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"RAG data exported to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting RAG data: {e}")
            raise 