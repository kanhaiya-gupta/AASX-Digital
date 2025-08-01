"""
Multi-Step RAG Technique
Iterative refinement approach for the new modular system
"""

from typing import Dict, List, Any
import openai
from datetime import datetime
from .base_technique import BaseRAGTechnique
from src.ai_rag.embedding_models.text_embeddings import TextEmbeddingManager


class MultiStepRAGTechnique(BaseRAGTechnique):
    """Multi-Step RAG technique with iterative refinement"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Multi-Step RAG",
            description="Iterative refinement approach with multiple retrieval and generation steps",
            config=config
        )
        self.max_steps = config.get('max_steps', 3) if config else 3
    
    def execute(self, query: str, vector_db=None, search_results: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the multi-step RAG technique.
        
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
            response = self.generate_response(processed_query, combined_context, llm_model, **kwargs)
            
            # Postprocess response
            final_response = self.postprocess_response(response)
            
            # Add metadata
            execution_time = (datetime.now() - start_time).total_seconds()
            final_response.update({
                'technique_id': 'multi_step',
                'technique_name': self.name,
                'execution_time': execution_time
            })
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error in multi-step RAG execution: {e}")
            raise
    
    def retrieve_context(self, query: str, vector_db=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve context using multi-step approach
        
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
            all_docs = []
            refined_query = query
            
            # Multi-step retrieval
            for step in range(self.max_steps):
                self.logger.info(f"Multi-step RAG: Step {step + 1}")
                
                # Retrieve documents for current query
                step_results = vector_db.search_vectors(
                    query_vector=self._get_query_embedding(refined_query),
                    limit=top_k
                )
                
                # Convert to standard format
                step_docs = []
                for result in step_results:
                    step_docs.append({
                        'content': result.get('payload', {}).get('content_preview', ''),
                        'score': result.get('score', 0),
                        'metadata': result.get('payload', {}),
                        'id': result.get('id', ''),
                        'retrieval_step': step + 1,
                        'query_used': refined_query
                    })
                
                all_docs.extend(step_docs)
                
                # Refine query for next step if not the last step
                if step < self.max_steps - 1 and step_docs:
                    refined_query = self._refine_query(query, step_docs, step + 1)
                    self.logger.info(f"Refined query for step {step + 2}: {refined_query}")
            
            # Remove duplicates and sort by step and score
            unique_docs = self._deduplicate_docs(all_docs)
            unique_docs.sort(key=lambda x: (x.get('retrieval_step', 0), x.get('score', 0)), reverse=True)
            
            self.logger.info(f"Retrieved {len(unique_docs)} documents across {self.max_steps} steps")
            return unique_docs
            
        except Exception as e:
            self.logger.error(f"Error in multi-step RAG retrieval: {e}")
            return []
    
    def _refine_query(self, original_query: str, docs: List[Dict], step: int) -> str:
        """
        Refine query based on retrieved documents
        
        Args:
            original_query: Original user query
            docs: Retrieved documents from current step
            step: Current step number
            
        Returns:
            Refined query
        """
        try:
            # Extract key information from documents
            doc_contents = [doc.get('content', '') for doc in docs[:3]]  # Top 3 docs
            context_summary = "\n".join(doc_contents)
            
            # Build refinement prompt
            refinement_prompt = f"""
Original Query: {original_query}

Retrieved Context (Step {step}):
{context_summary}

Based on the retrieved context, generate a refined query that:
1. Maintains the original intent
2. Incorporates relevant terms and concepts found in the context
3. Is more specific and targeted for the next retrieval step

Refined Query:"""
            
            # Get refined query from LLM
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a query refinement assistant. Generate concise, focused queries."},
                    {"role": "user", "content": refinement_prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            refined_query = response.choices[0].message.content.strip()
            
            # Fallback to original query if refinement fails
            if not refined_query or len(refined_query) < 5:
                refined_query = original_query
            
            return refined_query
            
        except Exception as e:
            self.logger.warning(f"Query refinement failed for step {step}: {e}")
            return original_query
    
    def _deduplicate_docs(self, docs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate documents while preserving step information
        
        Args:
            docs: List of documents with potential duplicates
            
        Returns:
            Deduplicated documents
        """
        seen = set()
        unique_docs = []
        
        for doc in docs:
            # Create unique identifier based on content
            content_hash = hash(doc.get('content', ''))
            
            if content_hash not in seen:
                seen.add(content_hash)
                unique_docs.append(doc)
            else:
                # Update existing document with additional step info
                for existing_doc in unique_docs:
                    if hash(existing_doc.get('content', '')) == content_hash:
                        existing_doc['retrieval_steps'] = existing_doc.get('retrieval_steps', []) + [doc.get('retrieval_step', 0)]
                        break
        
        return unique_docs
    
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict = None, **kwargs) -> str:
        """
        Combine contexts with multi-step approach emphasis
        
        Args:
            vector_docs: Documents from vector search (multi-step)
            graph_context: Context from knowledge graph (optional)
            **kwargs: Additional parameters
            
        Returns:
            Combined context string
        """
        combined = []
        
        # Add multi-step retrieval results
        if vector_docs:
            combined.append("=== Multi-Step Retrieval Results ===")
            
            # Group by step
            steps = {}
            for doc in vector_docs:
                step = doc.get('retrieval_step', 1)
                if step not in steps:
                    steps[step] = []
                steps[step].append(doc)
            
            # Present results by step
            for step in sorted(steps.keys()):
                combined.append(f"\n--- Step {step} Results ---")
                step_docs = steps[step]
                for i, doc in enumerate(step_docs, 1):
                    content = doc.get('content', '')
                    score = doc.get('score', 0)
                    query_used = doc.get('query_used', 'Unknown')
                    combined.append(f"{i}. {content}")
                    combined.append(f"   Score: {score:.3f} | Query: {query_used}")
        
        # Add graph context if available
        if graph_context and graph_context.get('graph_data'):
            combined.append("\n=== Knowledge Graph Context ===")
            for record in graph_context['graph_data']:
                combined.append(f"• {record.get('type', 'Unknown')}: {record.get('id', 'Unknown')}")
        
        return "\n".join(combined) if combined else "No context available"
    
    def generate_response(self, query: str, context: str, llm_model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generate response with multi-step approach emphasis
        
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
            
            # Build system prompt for multi-step approach
            system_prompt = self.config.get('system_prompt', 
                "You are an AI assistant analyzing digital twin data using multi-step retrieval. "
                "Consider the iterative refinement process and how each step contributed to the final analysis.")
            
            # Build user prompt
            user_prompt = f"""
Question: {query}

Context from multi-step retrieval (iterative refinement):
{context}

Please provide a comprehensive analysis that considers:
1. How the multi-step retrieval process refined the search
2. The relevance of documents from each step
3. The overall insights from the iterative approach

Provide a clear, structured response based on the available digital twin data.
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
                'steps_used': self.max_steps,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Generated multi-step RAG response using {llm_model} with {self.max_steps} steps")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating multi-step RAG response: {e}")
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
        """Validate multi-step RAG parameters"""
        # Multi-step RAG doesn't have strict parameter requirements
        return True 