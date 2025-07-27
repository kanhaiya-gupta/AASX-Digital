"""
Base RAG Technique
Abstract base class for all RAG techniques in the new modular system
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import time

from src.shared.utils import setup_logging


class BaseRAGTechnique(ABC):
    """Base class for all RAG techniques"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
        """
        Initialize the RAG technique
        
        Args:
            name: Name of the technique
            description: Description of the technique
            config: Configuration dictionary
        """
        self.name = name
        self.description = description
        self.config = config or {}
        self.logger = setup_logging(f"rag_technique.{name.lower()}")
    
    @abstractmethod
    def execute(self, query: str, vector_db=None, search_results: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the RAG technique.
        
        Args:
            query: User query
            vector_db: Vector database client (optional)
            search_results: Pre-retrieved search results (optional)
            **kwargs: Additional parameters
            
        Returns:
            RAG response dictionary
        """
        pass
    
    @abstractmethod
    def retrieve_context(self, query: str, vector_db=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for the query
        
        Args:
            query: User query
            vector_db: Vector database client (optional)
            **kwargs: Additional parameters
            
        Returns:
            List of context documents
        """
        pass
    
    @abstractmethod
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict = None, **kwargs) -> str:
        """
        Combine different types of context
        
        Args:
            vector_docs: Documents from vector search
            graph_context: Context from knowledge graph (optional)
            **kwargs: Additional parameters
            
        Returns:
            Combined context string
        """
        pass
    
    @abstractmethod
    def generate_response(self, query: str, context: str, llm_model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generate AI response using the combined context
        
        Args:
            query: User query
            context: Combined context
            llm_model: LLM model to use (optional)
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
        return query.strip()
    
    def postprocess_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess the response if needed
        
        Args:
            response: Original response
            
        Returns:
            Postprocessed response
        """
        return response
    
    def _extract_text_from_search_results(self, search_results: List[Dict]) -> List[str]:
        """
        Extract text content from search results.
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            List of text content
        """
        texts = []
        for result in search_results:
            payload = result.get('payload', {})
            text = payload.get('content_preview', '')
            if text:
                texts.append(text)
        return texts
    
    def _format_context_for_llm(self, texts: List[str], max_length: int = 4000) -> str:
        """
        Format context texts for LLM input.
        
        Args:
            texts: List of text content
            max_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        if not texts:
            return ""
        
        # Join texts with separators
        context = "\n\n---\n\n".join(texts)
        
        # Truncate if too long
        if len(context) > max_length:
            context = context[:max_length] + "..."
        
        return context
    
    def _create_prompt(self, query: str, context: str) -> str:
        """
        Create a prompt for the LLM.
        
        Args:
            query: User query
            context: Context information
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Based on the following context, please answer the user's question.

Context:
{context}

Question: {query}

Answer:"""
        return prompt 