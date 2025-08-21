"""
RAG Technique Manager
Manages and coordinates different RAG techniques for the new modular AI/RAG system
"""

from typing import Dict, List, Any, Optional
import logging
from .rag_techniques import (
    BasicRAGTechnique,
    HybridRAGTechnique,
    MultiStepRAGTechnique,
    GraphRAGTechnique,
    AdvancedRAGTechnique
)

from src.shared.utils import setup_logging

logger = setup_logging("rag_technique_manager")

class RAGTechniqueManager:
    """Manager for different RAG techniques"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the RAG technique manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.techniques = {}
        self._initialize_techniques()
    
    def _initialize_techniques(self):
        """Initialize all available RAG techniques"""
        try:
            # Initialize each technique with configuration
            self.techniques['basic'] = BasicRAGTechnique(self.config)
            self.techniques['hybrid'] = HybridRAGTechnique(self.config)
            self.techniques['multi_step'] = MultiStepRAGTechnique(self.config)
            self.techniques['graph'] = GraphRAGTechnique(self.config)
            self.techniques['advanced'] = AdvancedRAGTechnique(self.config)
            
            logger.info(f"✅ Initialized {len(self.techniques)} RAG techniques")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG techniques: {e}")
            raise
    
    def get_available_techniques(self) -> List[Dict[str, Any]]:
        """
        Get list of available techniques with their information
        
        Returns:
            List of technique information dictionaries
        """
        techniques_info = []
        
        for technique_id, technique in self.techniques.items():
            info = technique.get_technique_info()
            info['id'] = technique_id
            techniques_info.append(info)
        
        return techniques_info
    
    def get_technique(self, technique_id: str) -> Optional[Any]:
        """
        Get a specific RAG technique
        
        Args:
            technique_id: ID of the technique to get
            
        Returns:
            RAG technique instance or None if not found
        """
        return self.techniques.get(technique_id)
    
    def execute_technique(self, technique_id: str, query: str, vector_db=None, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific RAG technique
        
        Args:
            technique_id: ID of the technique to execute
            query: User query
            vector_db: Vector database client (optional)
            **kwargs: Additional parameters for the technique
            
        Returns:
            Result from the technique execution
        """
        logger.info(f"🔍 Technique manager executing technique: {technique_id}")
        logger.info(f"🔍 Available techniques: {list(self.techniques.keys())}")
        
        technique = self.get_technique(technique_id)
        if not technique:
            raise ValueError(f"Unknown technique: {technique_id}")
        
        logger.info(f"✅ Found technique: {technique.name}")
        
        try:
            # Validate parameters
            if not technique.validate_parameters(**kwargs):
                raise ValueError(f"Invalid parameters for technique: {technique_id}")
            
            # Execute the technique
            result = technique.execute(query, vector_db=vector_db, **kwargs)
            
            logger.info(f"✅ Technique {technique_id} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Technique {technique_id} execution failed: {e}")
            raise
    
    def compare_techniques(self, query: str, technique_ids: List[str], vector_db=None, **kwargs) -> Dict[str, Any]:
        """
        Compare multiple RAG techniques on the same query
        
        Args:
            query: User query
            technique_ids: List of technique IDs to compare
            vector_db: Vector database client (optional)
            **kwargs: Additional parameters
            
        Returns:
            Comparison results
        """
        logger.info(f"🔍 Comparing {len(technique_ids)} techniques for query: {query[:50]}...")
        
        results = {}
        
        for technique_id in technique_ids:
            try:
                result = self.execute_technique(technique_id, query, vector_db=vector_db, **kwargs)
                results[technique_id] = {
                    'status': 'success',
                    'result': result,
                    'execution_time': result.get('execution_time', 0)
                }
            except Exception as e:
                results[technique_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Find best technique
        best_technique = self._find_best_technique(results)
        
        comparison_result = {
            'query': query,
            'techniques_compared': technique_ids,
            'results': results,
            'best_technique': best_technique,
            'summary': {
                'total_techniques': len(technique_ids),
                'successful_techniques': len([r for r in results.values() if r['status'] == 'success']),
                'failed_techniques': len([r for r in results.values() if r['status'] == 'error'])
            }
        }
        
        logger.info(f"✅ Technique comparison completed. Best: {best_technique}")
        return comparison_result
    
    def _find_best_technique(self, technique_results: Dict[str, Any]) -> Optional[str]:
        """
        Find the best performing technique based on results
        
        Args:
            technique_results: Results from technique comparison
            
        Returns:
            ID of the best technique or None
        """
        successful_results = {
            k: v for k, v in technique_results.items() 
            if v['status'] == 'success'
        }
        
        if not successful_results:
            return None
        
        # Simple heuristic: prefer faster execution time
        best_technique = min(
            successful_results.items(),
            key=lambda x: x[1].get('execution_time', float('inf'))
        )[0]
        
        return best_technique
    
    def get_technique_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """
        Get recommendations for which techniques to use for a query
        
        Args:
            query: User query
            
        Returns:
            List of technique recommendations
        """
        recommendations = []
        
        # Simple keyword-based recommendations
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['graph', 'relationship', 'connection']):
            recommendations.append({
                'technique_id': 'graph',
                'reason': 'Query mentions graph-related concepts',
                'confidence': 0.8
            })
        
        if any(word in query_lower for word in ['complex', 'multi', 'step', 'detailed']):
            recommendations.append({
                'technique_id': 'multi_step',
                'reason': 'Query suggests complex multi-step reasoning',
                'confidence': 0.7
            })
        
        if any(word in query_lower for word in ['hybrid', 'combine', 'both']):
            recommendations.append({
                'technique_id': 'hybrid',
                'reason': 'Query suggests hybrid approach',
                'confidence': 0.6
            })
        
        # Default recommendation
        recommendations.append({
            'technique_id': 'basic',
            'reason': 'Good general-purpose technique',
            'confidence': 0.5
        })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations
    
    def get_technique_stats(self) -> Dict[str, Any]:
        """
        Get statistics about available techniques
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_techniques': len(self.techniques),
            'technique_names': list(self.techniques.keys()),
            'technique_details': {}
        }
        
        for technique_id, technique in self.techniques.items():
            info = technique.get_technique_info()
            stats['technique_details'][technique_id] = {
                'name': info['name'],
                'description': info['description']
            }
        
        return stats
    
    def list_techniques(self) -> List[str]:
        """Get list of available technique IDs"""
        return list(self.techniques.keys())
    
    def is_technique_available(self, technique_id: str) -> bool:
        """
        Check if a technique is available
        
        Args:
            technique_id: ID of the technique
            
        Returns:
            True if technique is available
        """
        return technique_id in self.techniques 