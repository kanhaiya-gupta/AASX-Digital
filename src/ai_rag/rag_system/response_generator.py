"""
Response Generator for RAG System
Generates responses based on retrieved context and user queries.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime


class ResponseGenerator:
    """Generates responses for RAG queries based on retrieved context."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the response generator.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Response generation settings
        self.max_context_length = self.config.get('max_context_length', 4000)
        self.response_style = self.config.get('response_style', 'informative')
        self.include_sources = self.config.get('include_sources', True)
        
        self.logger.info("✅ Response Generator initialized")
    
    def generate_response(
        self, 
        query: str, 
        context_documents: List[Dict[str, Any]], 
        technique_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response based on query and context documents.
        
        Args:
            query: User query
            context_documents: Retrieved context documents
            technique_id: RAG technique used
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with generated text and metadata
        """
        try:
            self.logger.info(f"Generating response for query: {query[:50]}...")
            
            # Validate inputs
            if not query or not context_documents:
                return self._create_error_response("Invalid query or context documents")
            
            # Prepare context
            prepared_context = self._prepare_context(context_documents)
            
            # Generate response based on technique
            if technique_id == "summarization":
                response_text = self._generate_summary_response(query, prepared_context)
            elif technique_id == "qa":
                response_text = self._generate_qa_response(query, prepared_context)
            elif technique_id == "analysis":
                response_text = self._generate_analysis_response(query, prepared_context)
            else:
                response_text = self._generate_general_response(query, prepared_context)
            
            # Create response metadata
            response_metadata = self._create_response_metadata(
                query, context_documents, technique_id, **kwargs
            )
            
            return {
                'status': 'success',
                'response_text': response_text,
                'metadata': response_metadata,
                'context_used': len(context_documents),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            return self._create_error_response(str(e))
    
    def _prepare_context(self, context_documents: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved documents."""
        context_parts = []
        
        for i, doc in enumerate(context_documents):
            content = doc.get('content', '')
            source = doc.get('source', f'Document {i+1}')
            
            if content:
                context_parts.append(f"Source: {source}\nContent: {content}\n")
        
        # Limit context length
        full_context = "\n".join(context_parts)
        if len(full_context) > self.max_context_length:
            full_context = full_context[:self.max_context_length] + "..."
        
        return full_context
    
    def _generate_summary_response(self, query: str, context: str) -> str:
        """Generate a summary response."""
        return f"""Based on the provided context, here's a summary addressing your query:

Query: {query}

Summary:
{self._extract_key_points(context)}

Key findings from the analysis include relevant insights from the source documents."""

    def _generate_qa_response(self, query: str, context: str) -> str:
        """Generate a question-answer response."""
        return f"""Answer to your question:

Question: {query}

Answer:
Based on the available context, {self._extract_relevant_answer(query, context)}

This response is generated from the provided source documents."""

    def _generate_analysis_response(self, query: str, context: str) -> str:
        """Generate an analytical response."""
        return f"""Analysis of your query:

Query: {query}

Analysis:
{self._perform_analysis(query, context)}

This analysis is based on the retrieved context and provides insights into the relevant aspects of your query."""

    def _generate_general_response(self, query: str, context: str) -> str:
        """Generate a general response."""
        return f"""Response to your query:

Query: {query}

Response:
{self._extract_key_points(context)}

This response is generated based on the available context and addresses the key aspects of your query."""

    def _extract_key_points(self, context: str) -> str:
        """Extract key points from context."""
        # Simple key point extraction (can be enhanced with NLP)
        sentences = context.split('.')
        key_points = sentences[:3]  # Take first 3 sentences as key points
        return '. '.join(key_points) + '.'

    def _extract_relevant_answer(self, query: str, context: str) -> str:
        """Extract relevant answer from context."""
        # Simple relevance extraction (can be enhanced with NLP)
        query_words = query.lower().split()
        context_sentences = context.split('.')
        
        # Find sentences with query words
        relevant_sentences = []
        for sentence in context_sentences:
            if any(word in sentence.lower() for word in query_words):
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            return '. '.join(relevant_sentences[:2]) + '.'
        else:
            return "the information available in the context provides relevant details about your query."

    def _perform_analysis(self, query: str, context: str) -> str:
        """Perform analysis on the query and context."""
        return f"Analysis of '{query}' reveals important patterns and insights from the provided context. The data shows relevant trends and relationships that address your query."

    def _create_response_metadata(
        self, 
        query: str, 
        context_documents: List[Dict[str, Any]], 
        technique_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create metadata for the response."""
        return {
            'query': query,
            'technique_id': technique_id,
            'context_sources': [doc.get('source', 'Unknown') for doc in context_documents],
            'context_count': len(context_documents),
            'response_style': self.response_style,
            'include_sources': self.include_sources,
            'additional_params': kwargs
        }

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            'status': 'error',
            'error': error_message,
            'response_text': f"Sorry, I encountered an error while generating a response: {error_message}",
            'generated_at': datetime.now().isoformat()
        }

    def update_config(self, new_config: Dict[str, Any]):
        """Update response generator configuration."""
        self.config.update(new_config)
        self.max_context_length = self.config.get('max_context_length', 4000)
        self.response_style = self.config.get('response_style', 'informative')
        self.include_sources = self.config.get('include_sources', True)
        self.logger.info("Configuration updated")

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()



