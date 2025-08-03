"""
Hybrid RAG Technique
Dense + sparse retrieval approach for the new modular system
"""

from typing import Dict, List, Any
import openai
from datetime import datetime
import re
from .base_technique import BaseRAGTechnique
from src.ai_rag.embedding_models.text_embeddings import TextEmbeddingManager


class HybridRAGTechnique(BaseRAGTechnique):
    """Hybrid RAG technique combining dense and sparse retrieval"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Hybrid RAG",
            description="Dense + sparse retrieval approach using vector search and keyword matching",
            config=config
        )
    
    def execute(self, query: str, vector_db=None, search_results: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the hybrid RAG technique.
        
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
                try:
                    search_results = self.retrieve_context(processed_query, vector_db=vector_db, **kwargs)
                except Exception as e:
                    self.logger.warning(f"Context retrieval failed, using fallback: {e}")
                    search_results = []
            
            # Combine contexts
            combined_context = self.combine_contexts(search_results, **kwargs)
            
            # Generate response
            response = self.generate_response(processed_query, combined_context, **kwargs)
            
            # Postprocess response
            final_response = self.postprocess_response(response)
            
            # Add metadata
            execution_time = (datetime.now() - start_time).total_seconds()
            final_response.update({
                'technique_id': 'hybrid',
                'technique_name': self.name,
                'execution_time': execution_time
            })
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error in hybrid RAG execution: {e}")
            # Return a fallback response instead of raising
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                'answer': f"I encountered an issue processing your query with the Hybrid RAG technique. Please try again or use a different technique. Error: {str(e)}",
                'technique_id': 'hybrid',
                'technique_name': self.name,
                'execution_time': execution_time,
                'error': str(e),
                'query': query
            }
    
    def retrieve_context(self, query: str, vector_db=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve context using hybrid approach (dense + sparse)
        
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
            # Get query embedding with fallback
            try:
                query_embedding = self._get_query_embedding(query)
            except Exception as e:
                self.logger.warning(f"Embedding generation failed, using fallback: {e}")
                query_embedding = [0.0] * 1536  # Fallback embedding
            
            # Dense retrieval (vector search)
            try:
                dense_results = vector_db.search_vectors(
                    query_vector=query_embedding,
                    limit=top_k
                )
            except Exception as e:
                self.logger.warning(f"Vector search failed, using empty results: {e}")
                dense_results = []
            
            # Convert to standard format
            dense_docs = []
            for result in dense_results:
                dense_docs.append({
                    'content': result.get('payload', {}).get('content_preview', ''),
                    'score': result.get('score', 0),
                    'metadata': result.get('payload', {}),
                    'id': result.get('id', '')
                })
            
            # Sparse retrieval (keyword-based)
            sparse_docs = self._keyword_search(query, dense_docs, top_k=top_k)
            
            # Combine and deduplicate
            combined_docs = self._combine_retrieval_results(dense_docs, sparse_docs)
            
            self.logger.info(f"Retrieved {len(combined_docs)} documents for hybrid RAG (dense: {len(dense_docs)}, sparse: {len(sparse_docs)})")
            return combined_docs
            
        except Exception as e:
            self.logger.error(f"Error in hybrid RAG retrieval: {e}")
            return []
    
    def _keyword_search(self, query: str, existing_docs: List[Dict], top_k: int) -> List[Dict]:
        """
        Perform keyword-based search on existing documents
        
        Args:
            query: Search query
            existing_docs: Existing documents to search through
            top_k: Number of results to return
            
        Returns:
            List of keyword-matched documents
        """
        query_keywords = set(re.findall(r'\b\w+\b', query.lower()))
        keyword_matches = []
        
        for doc in existing_docs:
            content = doc.get('content', '').lower()
            metadata_text = str(doc.get('metadata', {})).lower()
            
            # Calculate keyword match score
            content_matches = sum(1 for keyword in query_keywords if keyword in content)
            metadata_matches = sum(1 for keyword in query_keywords if keyword in metadata_text)
            
            total_score = content_matches + metadata_matches * 0.5  # Metadata gets lower weight
            
            if total_score > 0:
                doc_copy = doc.copy()
                doc_copy['keyword_score'] = total_score
                keyword_matches.append(doc_copy)
        
        # Sort by keyword score and return top_k
        keyword_matches.sort(key=lambda x: x.get('keyword_score', 0), reverse=True)
        return keyword_matches[:top_k]
    
    def _combine_retrieval_results(self, dense_docs: List[Dict], sparse_docs: List[Dict]) -> List[Dict]:
        """
        Combine dense and sparse retrieval results
        
        Args:
            dense_docs: Documents from dense retrieval
            sparse_docs: Documents from sparse retrieval
            
        Returns:
            Combined and deduplicated documents
        """
        combined = {}
        
        # Add dense results
        for doc in dense_docs:
            doc_id = doc.get('id', str(hash(doc.get('content', ''))))
            combined[doc_id] = {
                **doc,
                'dense_score': doc.get('score', 0),
                'sparse_score': 0
            }
        
        # Add sparse results
        for doc in sparse_docs:
            doc_id = doc.get('id', str(hash(doc.get('content', ''))))
            if doc_id in combined:
                # Update existing document with sparse score
                combined[doc_id]['sparse_score'] = doc.get('keyword_score', 0)
            else:
                # Add new document
                combined[doc_id] = {
                    **doc,
                    'dense_score': 0,
                    'sparse_score': doc.get('keyword_score', 0)
                }
        
        # Calculate hybrid scores
        for doc in combined.values():
            dense_score = doc.get('dense_score', 0)
            sparse_score = doc.get('sparse_score', 0)
            # Weighted combination (configurable weights)
            doc['hybrid_score'] = 0.7 * dense_score + 0.3 * sparse_score
        
        # Sort by hybrid score
        result = list(combined.values())
        result.sort(key=lambda x: x.get('hybrid_score', 0), reverse=True)
        
        return result
    
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict = None, **kwargs) -> str:
        """
        Combine contexts with hybrid approach emphasis
        
        Args:
            vector_docs: Documents from vector search (now hybrid)
            graph_context: Context from knowledge graph (optional)
            **kwargs: Additional parameters
            
        Returns:
            Combined context string
        """
        combined = []
        
        # Add hybrid retrieval results
        if vector_docs:
            combined.append("=== Hybrid Retrieval Results ===")
            combined.append("Dense + Sparse Search Results:")
            for i, doc in enumerate(vector_docs, 1):
                content = doc.get('content', '')
                dense_score = doc.get('dense_score', 0)
                sparse_score = doc.get('sparse_score', 0)
                hybrid_score = doc.get('hybrid_score', 0)
                combined.append(f"{i}. {content}")
                combined.append(f"   Scores - Dense: {dense_score:.3f}, Sparse: {sparse_score:.3f}, Hybrid: {hybrid_score:.3f}")
        
        # Add graph context if available
        if graph_context and graph_context.get('graph_data'):
            combined.append("\n=== Knowledge Graph Context ===")
            for record in graph_context['graph_data']:
                combined.append(f"• {record.get('type', 'Unknown')}: {record.get('id', 'Unknown')}")
        
        return "\n".join(combined) if combined else "No context available"
    
    def generate_response(self, query: str, context: str, llm_model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generate response with hybrid approach emphasis
        
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
            
            # Build system prompt for hybrid approach
            system_prompt = self.config.get('system_prompt', 
                "You are an AI assistant analyzing digital twin data using hybrid retrieval (dense + sparse). "
                "Consider both semantic similarity and keyword relevance in your analysis.")
            
            # Build user prompt
            user_prompt = f"""
Question: {query}

Context from hybrid retrieval (dense + sparse search):
{context}

Please provide a comprehensive analysis considering both semantic and keyword-based relevance from the digital twin data.
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
            
            self.logger.info(f"Generated hybrid RAG response using {llm_model}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating hybrid RAG response: {e}")
            # Return a fallback response instead of raising
            return {
                'answer': f"I'm using the Hybrid RAG technique to analyze your query: '{query}'. While I encountered some technical issues with the hybrid retrieval, I can still provide a response based on available information. Please try again or consider using a different technique if the issue persists.",
                'model': llm_model or 'gpt-3.5-turbo',
                'technique': self.name,
                'usage': {
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0
                },
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
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
                # Return a fallback embedding (zeros) instead of raising
                return [0.0] * 1536  # Default embedding size
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            # Return a fallback embedding (zeros) instead of raising
            return [0.0] * 1536  # Default embedding size
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate hybrid RAG parameters"""
        # Hybrid RAG doesn't have strict parameter requirements
        return True
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess the query for hybrid RAG
        
        Args:
            query: Original query
            
        Returns:
            Preprocessed query
        """
        # Basic preprocessing for hybrid RAG
        return query.strip()
    
    def postprocess_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess the response for hybrid RAG
        
        Args:
            response: Original response
            
        Returns:
            Postprocessed response
        """
        # Basic postprocessing for hybrid RAG
        return response 