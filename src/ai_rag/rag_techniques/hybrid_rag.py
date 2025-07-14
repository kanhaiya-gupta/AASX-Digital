"""
Hybrid RAG Technique
Dense + sparse retrieval approach
"""

from typing import Dict, List, Any
import openai
from datetime import datetime
import re
from .base_technique import BaseRAGTechnique

class HybridRAGTechnique(BaseRAGTechnique):
    """Hybrid RAG technique combining dense and sparse retrieval"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="Hybrid RAG",
            description="Dense + sparse retrieval approach using vector search and keyword matching",
            config=config
        )
    
    def retrieve_context(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve context using hybrid approach (dense + sparse)
        
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
            # Dense retrieval (vector search)
            dense_docs = vector_search_func(query, top_k=top_k)
            
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
    
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict, **kwargs) -> str:
        """
        Combine contexts with hybrid approach emphasis
        
        Args:
            vector_docs: Documents from vector search (now hybrid)
            graph_context: Context from knowledge graph
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
    
    def generate_response(self, query: str, context: str, llm_model: str, **kwargs) -> Dict[str, Any]:
        """
        Generate response with hybrid approach emphasis
        
        Args:
            query: User query
            context: Combined context
            llm_model: LLM model to use
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        try:
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
            raise
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate hybrid RAG parameters"""
        required_params = ['vector_search_func']
        for param in required_params:
            if param not in kwargs:
                self.logger.error(f"Missing required parameter: {param}")
                return False
        return True 