"""
RAG Technique Manager
Manages and coordinates different RAG techniques
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

logger = logging.getLogger(__name__)

class RAGTechniqueManager:
    """Manager for different RAG techniques"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the RAG technique manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
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
    
    def execute_technique(self, technique_id: str, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific RAG technique
        
        Args:
            technique_id: ID of the technique to execute
            query: User query
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
            
            # Preprocess query
            processed_query = technique.preprocess_query(query)
            
            # Retrieve context
            context_docs = technique.retrieve_context(processed_query, **kwargs)
            
            # Get graph context if available
            graph_context = kwargs.get('graph_context', {})
            
            # Remove graph_context from kwargs to avoid duplicate argument
            technique_kwargs = {k: v for k, v in kwargs.items() if k != 'graph_context'}
            
            # Combine contexts
            combined_context = technique.combine_contexts(context_docs, graph_context=graph_context, **technique_kwargs)
            
            # Generate response
            llm_model = kwargs.get('llm_model', 'gpt-3.5-turbo')
            
            # Remove llm_model from kwargs to avoid duplicate argument
            response_kwargs = {k: v for k, v in technique_kwargs.items() if k != 'llm_model'}
            
            response = technique.generate_response(processed_query, combined_context, llm_model, **response_kwargs)
            
            # Postprocess response
            final_response = technique.postprocess_response(response)
            
            # Add technique metadata
            final_response['technique_id'] = technique_id
            final_response['technique_name'] = technique.name
            
            logger.info(f"✅ Executed {technique_id} technique successfully")
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Technique {technique_id} execution failed: {e}")
            raise
    
    def compare_techniques(self, query: str, technique_ids: List[str], **kwargs) -> Dict[str, Any]:
        """
        Compare multiple RAG techniques on the same query
        
        Args:
            query: User query
            technique_ids: List of technique IDs to compare
            **kwargs: Additional parameters for the techniques
            
        Returns:
            Comparison results
        """
        comparison_results = {
            'query': query,
            'techniques': {},
            'summary': {}
        }
        
        for technique_id in technique_ids:
            try:
                result = self.execute_technique(technique_id, query, **kwargs)
                comparison_results['techniques'][technique_id] = {
                    'success': True,
                    'result': result,
                    'execution_time': result.get('execution_time', 0),
                    'token_usage': result.get('usage', {})
                }
            except Exception as e:
                comparison_results['techniques'][technique_id] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Generate summary
        successful_techniques = [
            tid for tid, data in comparison_results['techniques'].items() 
            if data.get('success', False)
        ]
        
        comparison_results['summary'] = {
            'total_techniques': len(technique_ids),
            'successful_techniques': len(successful_techniques),
            'failed_techniques': len(technique_ids) - len(successful_techniques),
            'best_technique': self._find_best_technique(comparison_results['techniques'])
        }
        
        logger.info(f"✅ Compared {len(technique_ids)} techniques")
        return comparison_results
    
    def _find_best_technique(self, technique_results: Dict[str, Any]) -> Optional[str]:
        """
        Find the best performing technique based on various metrics
        
        Args:
            technique_results: Results from technique comparison
            
        Returns:
            ID of the best technique or None
        """
        best_technique = None
        best_score = 0
        
        for technique_id, data in technique_results.items():
            if not data.get('success', False):
                continue
            
            # Calculate composite score
            result = data.get('result', {})
            usage = result.get('usage', {})
            
            # Score based on token efficiency and response quality
            total_tokens = usage.get('total_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            
            if total_tokens > 0:
                # Higher score for more efficient token usage
                efficiency_score = completion_tokens / total_tokens
                
                # Additional factors could be added here
                # (e.g., response length, confidence scores, etc.)
                
                if efficiency_score > best_score:
                    best_score = efficiency_score
                    best_technique = technique_id
        
        return best_technique
    
    def get_technique_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """
        Get recommendations for which techniques to use based on query characteristics
        
        Args:
            query: User query
            
        Returns:
            List of technique recommendations with reasoning
        """
        recommendations = []
        query_lower = query.lower()
        
        # Basic RAG recommendation
        recommendations.append({
            'technique_id': 'basic',
            'reason': 'Simple queries benefit from straightforward retrieval and generation',
            'confidence': 0.8 if len(query.split()) < 10 else 0.6
        })
        
        # Hybrid RAG recommendation
        if any(word in query_lower for word in ['keyword', 'specific', 'exact']):
            recommendations.append({
                'technique_id': 'hybrid',
                'reason': 'Query contains specific keywords that benefit from hybrid retrieval',
                'confidence': 0.9
            })
        
        # Multi-step RAG recommendation
        if any(word in query_lower for word in ['complex', 'detailed', 'analysis', 'investigate']):
            recommendations.append({
                'technique_id': 'multi_step',
                'reason': 'Complex queries benefit from iterative refinement',
                'confidence': 0.85
            })
        
        # Graph RAG recommendation
        if any(word in query_lower for word in ['relationship', 'connection', 'structure', 'hierarchy']):
            recommendations.append({
                'technique_id': 'graph',
                'reason': 'Query involves relationships and connections',
                'confidence': 0.9
            })
        
        # Advanced RAG recommendation
        if any(word in query_lower for word in ['comprehensive', 'multi', 'advanced', 'sophisticated']):
            recommendations.append({
                'technique_id': 'advanced',
                'reason': 'Query requires sophisticated multi-modal analysis',
                'confidence': 0.8
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
            'technique_details': {}
        }
        
        for technique_id, technique in self.techniques.items():
            info = technique.get_technique_info()
            stats['technique_details'][technique_id] = {
                'name': info['name'],
                'description': info['description'],
                'config_keys': list(info['config'].keys()) if info.get('config') else []
            }
        
        return stats 