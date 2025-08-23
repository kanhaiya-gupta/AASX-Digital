"""
Mock RAG Manager for Testing
Provides a simple mock implementation for testing Phase 1 and Phase 2 functionality
"""

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MockRAGManager:
    """Mock RAG manager for testing purposes"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the mock RAG manager"""
        self.config = config or {}
        self.logger = logger
        self.logger.info("✅ Mock RAG Manager initialized successfully")
    
    def process_query(self, query: str, technique_id: str = None, project_id: str = None, **kwargs) -> Dict[str, Any]:
        """Mock query processing"""
        start_time = time.time()
        self.logger.info(f"🔍 Mock processing query: {query[:50]}...")
        
        # Simulate processing time
        time.sleep(0.1)
        
        execution_time = time.time() - start_time
        
        return {
            'answer': f"This is a mock response to: {query}",
            'technique_id': technique_id or 'mock_technique',
            'technique_name': 'Mock RAG Technique',
            'execution_time': execution_time,
            'search_results_count': 5,
            'query': query,
            'project_id': project_id,
            'timestamp': datetime.now().isoformat(),
            'usage': {'mock': True}
        }
    
    def compare_techniques(self, query: str, technique_ids: List[str] = None, project_id: str = None, **kwargs) -> Dict[str, Any]:
        """Mock technique comparison"""
        return {
            'query': query,
            'techniques_compared': technique_ids or ['mock_technique_1', 'mock_technique_2'],
            'results': {
                'mock_technique_1': {'score': 0.8, 'answer': 'Mock answer 1'},
                'mock_technique_2': {'score': 0.7, 'answer': 'Mock answer 2'}
            },
            'best_technique': 'mock_technique_1',
            'search_results_count': 5,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_available_techniques(self) -> List[Dict[str, Any]]:
        """Mock available techniques"""
        return [
            {
                'technique_id': 'mock_technique_1',
                'name': 'Mock RAG Technique 1',
                'description': 'A mock RAG technique for testing',
                'enabled': True
            },
            {
                'technique_id': 'mock_technique_2',
                'name': 'Mock RAG Technique 2',
                'description': 'Another mock RAG technique for testing',
                'enabled': True
            }
        ]
    
    def get_technique_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """Mock technique recommendations"""
        return [
            {
                'technique_id': 'mock_technique_1',
                'name': 'Mock RAG Technique 1',
                'confidence': 0.8,
                'reason': 'Best match for this query type'
            }
        ]
    
    def search_similar_documents(self, query: str, limit: int = 10, project_id: str = None) -> List[Dict[str, Any]]:
        """Mock document search"""
        return [
            {
                'id': 'mock_doc_1',
                'content': f'Mock document content related to: {query}',
                'score': 0.9,
                'metadata': {'project_id': project_id, 'type': 'mock'}
            }
        ] * min(limit, 3)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Mock system status"""
        return {
            'vector_db_connected': True,
            'available_techniques': 2,
            'technique_names': ['Mock RAG Technique 1', 'Mock RAG Technique 2'],
            'config_loaded': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_technique_stats(self) -> Dict[str, Any]:
        """Mock technique statistics"""
        return {
            'total_queries': 100,
            'successful_queries': 95,
            'average_response_time': 0.5,
            'techniques_used': {
                'mock_technique_1': 60,
                'mock_technique_2': 40
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def close(self):
        """Mock cleanup"""
        self.logger.info("Mock RAG Manager closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 