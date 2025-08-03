"""
Basic RAG Technique
Simple retrieval + generation approach for the new modular system
"""

from typing import Dict, List, Any
import openai
from datetime import datetime
from .base_technique import BaseRAGTechnique
from src.ai_rag.embedding_models.text_embeddings import TextEmbeddingManager


class BasicRAGTechnique(BaseRAGTechnique):
    """Basic RAG technique with simple retrieval and generation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Basic RAG",
            description="Simple retrieval + generation approach using vector search and LLM",
            config=config
        )
    
    def execute(self, query: str, vector_db=None, search_results: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the basic RAG technique.
        
        Args:
            query: User query
            vector_db: Vector database client (optional)
            search_results: Pre-retrieved search results (optional)
            **kwargs: Additional parameters
            
        Returns:
            RAG response dictionary
        """
        start_time = datetime.now()
        
        try:
            # Preprocess query
            processed_query = self.preprocess_query(query)
            
            # Retrieve context if not provided
            if not search_results:
                search_results = self.retrieve_context(processed_query, vector_db=vector_db, **kwargs)
            
            # Combine contexts
            combined_context = self.combine_contexts(search_results, **kwargs)
            
            # Generate response
            llm_model = kwargs.get('llm_model', 'gpt-3.5-turbo')
            # Remove llm_model from kwargs to avoid duplicate parameter error
            kwargs_without_llm = {k: v for k, v in kwargs.items() if k != 'llm_model'}
            response = self.generate_response(processed_query, combined_context, llm_model=llm_model, **kwargs_without_llm)
            
            # Postprocess response
            final_response = self.postprocess_response(response)
            
            # Add metadata
            execution_time = (datetime.now() - start_time).total_seconds()
            final_response.update({
                'technique_id': 'basic',
                'technique_name': self.name,
                'execution_time': execution_time
            })
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error in basic RAG execution: {e}")
            raise
    
    def retrieve_context(self, query: str, vector_db=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve context using simple vector search
        
        Args:
            query: User query
            vector_db: Vector database client (optional)
            **kwargs: Additional parameters
            
        Returns:
            List of context documents
        """
        top_k = kwargs.get('top_k', 5)
        
        if not vector_db:
            self.logger.warning("Vector database not provided")
            return []
        
        try:
            # Simple vector search
            search_results = vector_db.search_vectors(
                query_vector=self._get_query_embedding(query),
                limit=top_k
            )
            
            # Convert to standard format
            context_docs = []
            for result in search_results:
                context_docs.append({
                    'content': result.get('payload', {}).get('content_preview', ''),
                    'score': result.get('score', 0),
                    'metadata': result.get('payload', {}),
                    'id': result.get('id', '')
                })
            
            self.logger.info(f"Retrieved {len(context_docs)} documents for basic RAG")
            return context_docs
            
        except Exception as e:
            self.logger.error(f"Error in basic RAG retrieval: {e}")
            return []
    
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict = None, **kwargs) -> str:
        """
        Combine contexts using simple concatenation
        
        Args:
            vector_docs: Documents from vector search
            graph_context: Context from knowledge graph (optional)
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
    
    def generate_response(self, query: str, context: str, llm_model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generate response using simple prompt engineering
        
        Args:
            query: User query
            context: Combined context
            llm_model: LLM model to use (optional)
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        try:
            # Use default model if not specified
            if not llm_model:
                llm_model = 'gpt-3.5-turbo'
            
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
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """
        Get embedding for the query using secure TextEmbeddingManager.
        
        Args:
            query: Query text
            
        Returns:
            Query embedding vector
        """
        try:
            embedding_manager = TextEmbeddingManager()
            embedding = embedding_manager.get_model().embed_text(query)
            if embedding:
                return embedding
            else:
                self.logger.error("Failed to generate embedding")
                raise ValueError("Embedding generation failed")
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise ValueError(f"Embedding generation failed: {e}")
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate basic RAG parameters"""
        # Basic RAG doesn't have strict parameter requirements
        return True 