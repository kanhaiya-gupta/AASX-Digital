"""
Basic RAG Technique
Simple retrieval + generation approach
"""

from typing import Dict, List, Any
import openai
from datetime import datetime
from .base_technique import BaseRAGTechnique

class BasicRAGTechnique(BaseRAGTechnique):
    """Basic RAG technique with simple retrieval and generation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="Basic RAG",
            description="Simple retrieval + generation approach using vector search and LLM",
            config=config
        )
    
    def retrieve_context(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve context using simple vector search
        
        Args:
            query: User query
            **kwargs: Additional parameters including vector_search_func
            
        Returns:
            List of context documents
        """
        vector_search_func = kwargs.get('vector_search_func')
        top_k = kwargs.get('top_k', 5)
        
        if not vector_search_func:
            self.logger.warning("Vector search function not provided")
            return []
        
        try:
            # Simple vector search
            context_docs = vector_search_func(query, top_k=top_k)
            self.logger.info(f"Retrieved {len(context_docs)} documents for basic RAG")
            return context_docs
        except Exception as e:
            self.logger.error(f"Error in basic RAG retrieval: {e}")
            return []
    
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict, **kwargs) -> str:
        """
        Combine contexts using simple concatenation
        
        Args:
            vector_docs: Documents from vector search
            graph_context: Context from knowledge graph
            **kwargs: Additional parameters
            
        Returns:
            Combined context string
        """
        combined = []
        
        # Add vector search results
        if vector_docs:
            combined.append("=== Vector Search Results ===")
            for i, doc in enumerate(vector_docs, 1):
                content = doc.get('content', '')
                score = doc.get('score', 0)
                combined.append(f"{i}. {content} (Score: {score:.3f})")
        
        # Add graph context if available
        if graph_context and graph_context.get('graph_data'):
            combined.append("\n=== Knowledge Graph Context ===")
            for record in graph_context['graph_data']:
                combined.append(f"• {record.get('type', 'Unknown')}: {record.get('id', 'Unknown')}")
        
        return "\n".join(combined) if combined else "No context available"
    
    def generate_response(self, query: str, context: str, llm_model: str, **kwargs) -> Dict[str, Any]:
        """
        Generate response using simple prompt engineering
        
        Args:
            query: User query
            context: Combined context
            llm_model: LLM model to use
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        try:
            # Build system prompt
            system_prompt = self.config.get('system_prompt', 
                "You are an AI assistant analyzing digital twin data. Provide clear, accurate responses based on the provided context.")
            
            # Build user prompt
            user_prompt = f"""
Question: {query}

Context from digital twin data:
{context}

Please provide a comprehensive analysis based on the available digital twin data.
"""
            
            # Query OpenAI
            response = openai.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 1000)
            )
            
            # Format response
            result = {
                'answer': response.choices[0].message.content,
                'model': llm_model,
                'technique': self.name,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Generated basic RAG response using {llm_model}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating basic RAG response: {e}")
            raise
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate basic RAG parameters"""
        required_params = ['vector_search_func']
        for param in required_params:
            if param not in kwargs:
                self.logger.error(f"Missing required parameter: {param}")
                return False
        return True 