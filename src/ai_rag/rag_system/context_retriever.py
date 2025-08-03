"""
Context Retriever for RAG System
Retrieves relevant context from vector databases and other sources.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np


class ContextRetriever:
    """Retrieves relevant context for RAG queries."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the context retriever.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Retrieval settings
        self.max_results = self.config.get('max_results', 10)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.include_metadata = self.config.get('include_metadata', True)
        self.retrieval_strategy = self.config.get('retrieval_strategy', 'semantic')
        
        # Vector database reference (will be set by RAG manager)
        self.vector_db = None
        
        self.logger.info("✅ Context Retriever initialized")
    
    def set_vector_db(self, vector_db):
        """Set the vector database reference."""
        self.vector_db = vector_db
        self.logger.info("Vector database reference set")
    
    def retrieve_context(
        self, 
        query: str, 
        limit: int = None,
        filter_dict: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            limit: Maximum number of results
            filter_dict: Filter criteria
            **kwargs: Additional parameters
            
        Returns:
            Retrieved context and metadata
        """
        try:
            self.logger.info(f"Retrieving context for query: {query[:50]}...")
            
            if not self.vector_db:
                return self._create_error_response("Vector database not available")
            
            # Determine retrieval strategy
            if self.retrieval_strategy == 'semantic':
                results = self._semantic_retrieval(query, limit, filter_dict, **kwargs)
            elif self.retrieval_strategy == 'hybrid':
                results = self._hybrid_retrieval(query, limit, filter_dict, **kwargs)
            elif self.retrieval_strategy == 'keyword':
                results = self._keyword_retrieval(query, limit, filter_dict, **kwargs)
            else:
                results = self._semantic_retrieval(query, limit, filter_dict, **kwargs)
            
            # Filter results by similarity threshold
            filtered_results = self._filter_by_similarity(results)
            
            # Prepare context documents
            context_documents = self._prepare_context_documents(filtered_results)
            
            return {
                'status': 'success',
                'context_documents': context_documents,
                'total_retrieved': len(results),
                'total_filtered': len(filtered_results),
                'query': query,
                'retrieval_strategy': self.retrieval_strategy,
                'retrieved_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Context retrieval failed: {e}")
            return self._create_error_response(str(e))
    
    def _semantic_retrieval(
        self, 
        query: str, 
        limit: int = None,
        filter_dict: Dict[str, Any] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Perform semantic retrieval using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = self._generate_query_embedding(query)
            if not query_embedding:
                return []
            
            # Search vector database
            limit = limit or self.max_results
            search_results = self.vector_db.search_vectors(
                query_vector=query_embedding,
                limit=limit,
                filter_dict=filter_dict
            )
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Semantic retrieval failed: {e}")
            return []
    
    def _hybrid_retrieval(
        self, 
        query: str, 
        limit: int = None,
        filter_dict: Dict[str, Any] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Perform hybrid retrieval combining semantic and keyword search."""
        try:
            # Get semantic results
            semantic_results = self._semantic_retrieval(query, limit, filter_dict, **kwargs)
            
            # Get keyword results
            keyword_results = self._keyword_retrieval(query, limit, filter_dict, **kwargs)
            
            # Combine and rank results
            combined_results = self._combine_results(semantic_results, keyword_results, limit)
            
            return combined_results
            
        except Exception as e:
            self.logger.error(f"Hybrid retrieval failed: {e}")
            return []
    
    def _keyword_retrieval(
        self, 
        query: str, 
        limit: int = None,
        filter_dict: Dict[str, Any] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based retrieval."""
        try:
            # Extract keywords from query
            keywords = self._extract_keywords(query)
            
            # Search using keyword matching
            # This is a simplified implementation - can be enhanced with proper keyword search
            results = []
            
            # For now, return empty results for keyword search
            # In a real implementation, this would search metadata and content for keywords
            self.logger.info(f"Keyword retrieval not fully implemented for keywords: {keywords}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Keyword retrieval failed: {e}")
            return []
    
    def _generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """Generate embedding for the query."""
        try:
            # Use the text embedding manager from the AI/RAG system
            from src.ai_rag.embedding_models.text_embeddings import TextEmbeddingManager
            
            embedding_manager = TextEmbeddingManager()
            embedding = embedding_manager.get_model().embed_text(query)
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Failed to generate query embedding: {e}")
            return None
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        # Simple keyword extraction (can be enhanced with NLP)
        import re
        
        # Remove common stop words and extract meaningful words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _combine_results(
        self, 
        semantic_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Combine and rank results from different retrieval methods."""
        try:
            # Create a combined list with scores
            combined = []
            
            # Add semantic results with semantic score
            for result in semantic_results:
                combined.append({
                    'result': result,
                    'semantic_score': result.get('score', 0),
                    'keyword_score': 0,
                    'combined_score': result.get('score', 0)
                })
            
            # Add keyword results with keyword score
            for result in keyword_results:
                # Check if result already exists
                existing = next((item for item in combined if item['result'].get('id') == result.get('id')), None)
                
                if existing:
                    existing['keyword_score'] = result.get('score', 0)
                    existing['combined_score'] = (existing['semantic_score'] + existing['keyword_score']) / 2
                else:
                    combined.append({
                        'result': result,
                        'semantic_score': 0,
                        'keyword_score': result.get('score', 0),
                        'combined_score': result.get('score', 0)
                    })
            
            # Sort by combined score and return top results
            combined.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Return the top results
            top_results = combined[:limit]
            return [item['result'] for item in top_results]
            
        except Exception as e:
            self.logger.error(f"Failed to combine results: {e}")
            return semantic_results  # Fallback to semantic results
    
    def _filter_by_similarity(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter results by similarity threshold."""
        try:
            filtered = []
            
            for result in results:
                score = result.get('score', 0)
                if score >= self.similarity_threshold:
                    filtered.append(result)
            
            return filtered
            
        except Exception as e:
            self.logger.error(f"Failed to filter by similarity: {e}")
            return results
    
    def _prepare_context_documents(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare context documents from search results."""
        try:
            context_documents = []
            
            for result in results:
                document = {
                    'content': result.get('payload', {}).get('content', ''),
                    'source': result.get('payload', {}).get('source', 'Unknown'),
                    'score': result.get('score', 0),
                    'id': result.get('id', ''),
                }
                
                # Add metadata if requested
                if self.include_metadata:
                    document['metadata'] = {
                        'file_type': result.get('payload', {}).get('file_type', ''),
                        'project_id': result.get('payload', {}).get('project_id', ''),
                        'created_at': result.get('payload', {}).get('created_at', ''),
                        'file_size': result.get('payload', {}).get('file_size', 0)
                    }
                
                context_documents.append(document)
            
            return context_documents
            
        except Exception as e:
            self.logger.error(f"Failed to prepare context documents: {e}")
            return []
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            'status': 'error',
            'error': error_message,
            'context_documents': [],
            'total_retrieved': 0,
            'total_filtered': 0,
            'retrieved_at': datetime.now().isoformat()
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update context retriever configuration."""
        self.config.update(new_config)
        
        # Update instance variables
        self.max_results = self.config.get('max_results', 10)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.include_metadata = self.config.get('include_metadata', True)
        self.retrieval_strategy = self.config.get('retrieval_strategy', 'semantic')
        
        self.logger.info("Context retriever configuration updated")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
    
    def test_retrieval(self, test_query: str = "test query") -> Dict[str, Any]:
        """Test the context retrieval functionality."""
        try:
            if not self.vector_db:
                return {'status': 'error', 'message': 'Vector database not available'}
            
            # Perform a test retrieval
            test_results = self.retrieve_context(test_query, limit=5)
            
            if test_results.get('status') == 'success':
                return {
                    'status': 'success', 
                    'message': 'Retrieval test passed',
                    'results_count': test_results.get('total_filtered', 0)
                }
            else:
                return {'status': 'error', 'message': 'Retrieval test failed'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Retrieval test failed: {str(e)}'}





