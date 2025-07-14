"""
Base RAG Technique
Abstract base class for all RAG techniques
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseRAGTechnique(ABC):
    """Base class for all RAG techniques"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any]):
        """
        Initialize the RAG technique
        
        Args:
            name: Name of the technique
            description: Description of the technique
            config: Configuration dictionary
        """
        self.name = name
        self.description = description
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def retrieve_context(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for the query
        
        Args:
            query: User query
            **kwargs: Additional parameters
            
        Returns:
            List of context documents
        """
        pass
    
    @abstractmethod
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict, **kwargs) -> str:
        """
        Combine different types of context
        
        Args:
            vector_docs: Documents from vector search
            graph_context: Context from knowledge graph
            **kwargs: Additional parameters
            
        Returns:
            Combined context string
        """
        pass
    
    @abstractmethod
    def generate_response(self, query: str, context: str, llm_model: str, **kwargs) -> Dict[str, Any]:
        """
        Generate AI response using the combined context
        
        Args:
            query: User query
            context: Combined context
            llm_model: LLM model to use
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        pass
    
    def get_technique_info(self) -> Dict[str, Any]:
        """Get information about this technique"""
        return {
            'name': self.name,
            'description': self.description,
            'config': self.config
        }
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate technique-specific parameters
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            True if parameters are valid
        """
        return True
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess the query if needed
        
        Args:
            query: Original query
            
        Returns:
            Preprocessed query
        """
        return query
    
    def postprocess_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess the response if needed
        
        Args:
            response: Original response
            
        Returns:
            Postprocessed response
        """
        return response 