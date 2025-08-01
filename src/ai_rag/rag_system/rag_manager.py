"""
Main RAG Manager
Integrates vector embedding system with RAG techniques for complete AI/RAG functionality
"""

import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.shared.utils import setup_logging
from src.ai_rag.config import EMBEDDING_MODELS_CONFIG

from ..vector_embedding_upload import VectorEmbeddingUploader
from .rag_technique_manager import RAGTechniqueManager


class RAGManager:
    """Main RAG manager that coordinates vector embeddings and RAG techniques."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the RAG manager.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = setup_logging("rag_manager")
        self.config = config or {}
        
        # Initialize components
        self.vector_uploader = VectorEmbeddingUploader(config)
        self.technique_manager = RAGTechniqueManager(config)
        
        self.logger.info("✅ RAG Manager initialized successfully")
    
    def process_query(self, query: str, technique_id: str = None, project_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Process a query using the RAG system.
        
        Args:
            query: User query
            technique_id: Specific RAG technique to use (optional)
            project_id: Project to search within (optional)
            **kwargs: Additional parameters
            
        Returns:
            RAG response dictionary
        """
        start_time = time.time()
        self.logger.info(f"🔍 Processing query: {query[:50]}...")
        
        try:
            # Get technique recommendations if not specified
            if not technique_id:
                recommendations = self.technique_manager.get_technique_recommendations(query)
                technique_id = recommendations[0]['technique_id']
                self.logger.info(f"🎯 Auto-selected technique: {technique_id}")
            
            # Validate technique
            if not self.technique_manager.is_technique_available(technique_id):
                raise ValueError(f"Unknown RAG technique: {technique_id}")
            
            # Search for relevant context using vector database
            search_results = self.vector_uploader.search_similar(
                query=query,
                limit=kwargs.get('search_limit', 10),
                project_id=project_id
            )
            
            self.logger.info(f"📚 Found {len(search_results)} relevant documents")
            
            # Execute RAG technique
            result = self.technique_manager.execute_technique(
                technique_id=technique_id,
                query=query,
                vector_db=self.vector_uploader.vector_db,
                search_results=search_results,
                project_id=project_id,
                **kwargs
            )
            
            # Add metadata
            execution_time = time.time() - start_time
            result.update({
                'query': query,
                'technique_id': technique_id,
                'project_id': project_id,
                'execution_time': execution_time,
                'search_results_count': len(search_results),
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"✅ Query processed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Query processing failed: {e}")
            return {
                'error': str(e),
                'query': query,
                'technique_id': technique_id,
                'project_id': project_id,
                'execution_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def compare_techniques(self, query: str, technique_ids: List[str] = None, project_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Compare multiple RAG techniques on the same query.
        
        Args:
            query: User query
            technique_ids: List of techniques to compare (optional)
            project_id: Project to search within (optional)
            **kwargs: Additional parameters
            
        Returns:
            Comparison results
        """
        if not technique_ids:
            technique_ids = self.technique_manager.list_techniques()
        
        self.logger.info(f"🔍 Comparing {len(technique_ids)} techniques for query: {query[:50]}...")
        
        # Search for relevant context once
        search_results = self.vector_uploader.search_similar(
            query=query,
            limit=kwargs.get('search_limit', 10),
            project_id=project_id
        )
        
        # Compare techniques
        comparison_result = self.technique_manager.compare_techniques(
            query=query,
            technique_ids=technique_ids,
            vector_db=self.vector_uploader.vector_db,
            search_results=search_results,
            project_id=project_id,
            **kwargs
        )
        
        # Add metadata
        comparison_result.update({
            'project_id': project_id,
            'search_results_count': len(search_results),
            'timestamp': datetime.now().isoformat()
        })
        
        return comparison_result
    
    def get_available_techniques(self) -> List[Dict[str, Any]]:
        """Get list of available RAG techniques."""
        return self.technique_manager.get_available_techniques()
    
    def get_technique_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """Get technique recommendations for a query."""
        return self.technique_manager.get_technique_recommendations(query)
    
    def process_project_embeddings(self, project_id: str) -> Dict[str, Any]:
        """
        Process vector embeddings for a specific project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Processing results
        """
        self.logger.info(f"🔄 Processing embeddings for project: {project_id}")
        return self.vector_uploader.process_project(project_id)
    
    def search_similar_documents(self, query: str, limit: int = 10, project_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            project_id: Project to search within (optional)
            
        Returns:
            List of similar documents
        """
        return self.vector_uploader.search_similar(query, limit, project_id)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            'vector_db_connected': self.vector_uploader.vector_db.is_connected if self.vector_uploader.vector_db else False,
            'available_techniques': len(self.technique_manager.list_techniques()),
            'technique_names': self.technique_manager.list_techniques(),
            'config_loaded': bool(self.config),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_technique_stats(self) -> Dict[str, Any]:
        """Get statistics about RAG techniques."""
        return self.technique_manager.get_technique_stats()
    
    def close(self):
        """Clean up resources."""
        if self.vector_uploader:
            self.vector_uploader.close()
        self.logger.info("RAG Manager closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG System for AASX Digital Twin Analytics")
    parser.add_argument("--query", required=True, help="Query to process")
    parser.add_argument("--technique", help="RAG technique to use")
    parser.add_argument("--project-id", help="Project ID to search within")
    parser.add_argument("--compare", action="store_true", help="Compare multiple techniques")
    parser.add_argument("--limit", type=int, default=10, help="Search result limit")
    
    args = parser.parse_args()
    
    with RAGManager() as rag_manager:
        if args.compare:
            result = rag_manager.compare_techniques(
                query=args.query,
                project_id=args.project_id,
                search_limit=args.limit
            )
        else:
            result = rag_manager.process_query(
                query=args.query,
                technique_id=args.technique,
                project_id=args.project_id,
                search_limit=args.limit
            )
        
        print(f"Result: {result}")


if __name__ == "__main__":
    main() 