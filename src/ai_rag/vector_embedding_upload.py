"""
Main vector embedding and upload module for AASX ETL pipeline.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.shared.management import ProjectManager
from src.shared.config import VECTOR_DB_CONFIG, EMBEDDING_MODELS_CONFIG, PROCESSING_CONFIG, OUTPUT_CONFIG
from src.shared.utils import setup_logging, ensure_dir

from .vector_db.qdrant_client import QdrantClient
from .embedding_models.text_embeddings import TextEmbeddingModel, TextEmbeddingManager
from .processors import ProcessorManager


class VectorEmbeddingUploader:
    """Main class for vector embedding and upload operations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize vector embedding uploader.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = setup_logging("vector_embedding_uploader")
        self.config = config or {}
        
        # Initialize components
        self.project_manager = ProjectManager()
        self.vector_db = None
        self.text_embedding_manager = TextEmbeddingManager()
        self.processor_manager = None
        
        # Initialize vector database
        self._initialize_vector_db()
        
        # Initialize processor manager
        self.processor_manager = ProcessorManager(
            text_embedding_manager=self.text_embedding_manager,
            vector_db=self.vector_db
        )
    
    def _initialize_vector_db(self):
        """Initialize vector database client."""
        try:
            # Use Qdrant as default
            self.vector_db = QdrantClient(VECTOR_DB_CONFIG)
            self.vector_db.connect()
            self.logger.info("Connected to Qdrant vector database")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize vector database: {e}")
            raise
    
    def process_project(self, project_id: str) -> Dict[str, Any]:
        """
        Process a single project for vector embedding.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dictionary containing processing results
        """
        self.logger.info(f"Starting vector embedding for project: {project_id}")
        
        try:
            # Get project files
            files = self.project_manager.list_project_files(project_id)
            if not files:
                self.logger.warning(f"No files found for project: {project_id}")
                return {'status': 'no_files', 'project_id': project_id}
            
            # Process each file
            results = {
                'project_id': project_id,
                'status': 'processing',
                'files_processed': 0,
                'embeddings_created': 0,
                'errors': [],
                'start_time': datetime.now().isoformat(),
                'file_results': []
            }
            
            for file_info in files:
                file_result = self._process_file_and_graph(project_id, file_info)
                results['file_results'].append(file_result)
                
                if file_result['status'] == 'success':
                    results['files_processed'] += 1
                    results['embeddings_created'] += file_result.get('embeddings_created', 0)
                else:
                    results['errors'].append(file_result.get('error', 'Unknown error'))
            
            results['status'] = 'completed'
            results['end_time'] = datetime.now().isoformat()
            
            # Save results
            self._save_project_results(project_id, results)
            
            self.logger.info(f"Completed vector embedding for project {project_id}: "
                           f"{results['files_processed']} files, {results['embeddings_created']} embeddings")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to process project {project_id}: {e}")
            return {
                'project_id': project_id,
                'status': 'error',
                'error': str(e),
                'end_time': datetime.now().isoformat()
            }
    
    def _process_file_and_graph(self, project_id: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single file and its associated graph data for vector embedding.
        
        Args:
            project_id: Project identifier
            file_info: File information from project manager
            
        Returns:
            Dictionary containing file processing results
        """
        file_id = file_info.get('file_id')
        filename = file_info.get('filename', '')
        
        self.logger.info(f"Processing file and graph: {filename} (ID: {file_id})")
        
        try:
            # Get file path from output directory
            output_dir = Path("output/projects") / project_id
            file_path = self._find_file_in_output(output_dir, filename)
            
            if not file_path:
                return {
                    'file_id': file_id,
                    'filename': filename,
                    'status': 'error',
                    'error': 'File not found in output directory'
                }
            
            # Process the main file
            file_result = self.processor_manager.process_file(project_id, file_info, file_path)
            
            # Also process graph data if available
            base_name = Path(filename).stem
            graph_file_path = self._find_graph_file(output_dir, base_name)
            
            if graph_file_path:
                self.logger.info(f"Found graph file for {filename}, processing graph data")
                graph_result = self.processor_manager.process_file(project_id, file_info, graph_file_path)
                
                # Combine results
                combined_result = {
                    'file_id': file_id,
                    'filename': filename,
                    'status': 'success' if file_result['status'] == 'success' or graph_result['status'] == 'success' else 'error',
                    'embeddings_created': (file_result.get('embeddings_created', 0) + graph_result.get('embeddings_created', 0)),
                    'file_processing': file_result,
                    'graph_processing': graph_result
                }
                
                if file_result['status'] != 'success' and graph_result['status'] != 'success':
                    combined_result['status'] = 'error'
                    combined_result['error'] = f"File processing: {file_result.get('error', 'Unknown')}, Graph processing: {graph_result.get('error', 'Unknown')}"
                
                return combined_result
            else:
                # No graph file found, return just file result
                return file_result
                
        except Exception as e:
            self.logger.error(f"Failed to process file and graph {filename}: {e}")
            return {
                'file_id': file_id,
                'filename': filename,
                'status': 'error',
                'error': str(e)
            }
    
    def _find_file_in_output(self, output_dir: Path, filename: str) -> Optional[Path]:
        """Find a file in the output directory structure."""
        if not output_dir.exists():
            return None
        
        # Extract the base name without extension (e.g., "Example_AAS_ServoDCMotor_21" from "Example_AAS_ServoDCMotor_21.aasx")
        base_name = Path(filename).stem
        
        # Look for extracted files in the project directory
        for file_path in output_dir.rglob(f"{base_name}.*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.json', '.yaml', '.yml', '.ttl', '.txt']:
                self.logger.info(f"Found extracted file: {file_path}")
                return file_path
        
        # If no extracted files found, look for the original file
        for file_path in output_dir.rglob(filename):
            if file_path.is_file():
                self.logger.info(f"Found original file: {file_path}")
                return file_path
        
        self.logger.warning(f"No files found for {filename} in {output_dir}")
        return None
    
    def _find_graph_file(self, output_dir: Path, base_filename: str) -> Optional[Path]:
        """Find graph file for a given base filename."""
        if not output_dir.exists():
            return None
        
        # Look for graph file
        graph_file = output_dir / f"{base_filename}_graph.json"
        if graph_file.exists():
            self.logger.info(f"Found graph file: {graph_file}")
            return graph_file
        
        # Also check in subdirectories
        for file_path in output_dir.rglob(f"{base_filename}_graph.json"):
            if file_path.is_file():
                self.logger.info(f"Found graph file: {file_path}")
                return file_path
        
        return None
    
    def _save_project_results(self, project_id: str, results: Dict[str, Any]):
        """Save project processing results."""
        try:
            output_dir = Path("output/projects") / project_id
            output_dir.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
            
            results_file = output_dir / "embedding_results.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save project results: {e}")
    
    def process_all_projects(self) -> Dict[str, Any]:
        """Process all projects for vector embedding."""
        self.logger.info("Starting vector embedding for all projects")
        
        try:
            projects = self.project_manager.list_projects()
            results = {
                'total_projects': len(projects),
                'processed_projects': 0,
                'total_embeddings': 0,
                'errors': [],
                'project_results': [],
                'start_time': datetime.now().isoformat()
            }
            
            for project in projects:
                project_id = project.get('project_id')
                if project_id:
                    project_result = self.process_project(project_id)
                    results['project_results'].append(project_result)
                    
                    if project_result.get('status') == 'completed':
                        results['processed_projects'] += 1
                        results['total_embeddings'] += project_result.get('embeddings_created', 0)
                    else:
                        results['errors'].append(f"Project {project_id}: {project_result.get('error', 'Unknown error')}")
            
            results['end_time'] = datetime.now().isoformat()
            
            self.logger.info(f"Completed vector embedding for all projects: "
                           f"{results['processed_projects']}/{results['total_projects']} projects, "
                           f"{results['total_embeddings']} embeddings")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to process all projects: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'end_time': datetime.now().isoformat()
            }
    
    def search_similar(self, query: str, limit: int = 10, project_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for similar content using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            project_id: Optional project filter
            
        Returns:
            List of similar documents
        """
        try:
            # Generate query embedding
            text_model = self.text_embedding_manager.get_model()
            query_embedding = text_model.embed_text(query)
            
            if not query_embedding:
                self.logger.error("Failed to generate query embedding")
                return []
            
            # Prepare filter
            filter_dict = None
            if project_id:
                filter_dict = {'project_id': project_id}
            
            # Search vector database
            results = self.vector_db.search_vectors(
                query_vector=query_embedding,
                limit=limit,
                filter_dict=filter_dict
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def close(self):
        """Clean up resources."""
        if self.vector_db:
            self.vector_db.disconnect()
        
        self.text_embedding_manager.close()
        self.logger.info("Vector embedding uploader closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vector embedding and upload for AASX files")
    parser.add_argument("--project-id", help="Process specific project ID")
    parser.add_argument("--all-projects", action="store_true", help="Process all projects")
    parser.add_argument("--search", help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Search result limit")
    
    args = parser.parse_args()
    
    with VectorEmbeddingUploader() as uploader:
        if args.search:
            results = uploader.search_similar(args.search, args.limit)
            print(f"Search results for '{args.search}':")
            for i, result in enumerate(results, 1):
                print(f"{i}. Score: {result['score']:.3f}")
                print(f"   File: {result['payload'].get('source_file', 'Unknown')}")
                print(f"   Preview: {result['payload'].get('content_preview', 'No preview')}")
                print()
        elif args.project_id:
            result = uploader.process_project(args.project_id)
            print(f"Project processing result: {result}")
        elif args.all_projects:
            result = uploader.process_all_projects()
            print(f"All projects processing result: {result}")
        else:
            print("Please specify --project-id, --all-projects, or --search")


if __name__ == "__main__":
    main()
