"""
Advanced RAG Technique
Sophisticated multi-modal analysis approach for the new modular system
"""

from typing import Dict, List, Any
import openai
from datetime import datetime
from .base_technique import BaseRAGTechnique
from ...embedding_models.text_embeddings import TextEmbeddingManager


class AdvancedRAGTechnique(BaseRAGTechnique):
    """Advanced RAG technique with sophisticated multi-modal analysis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Advanced RAG",
            description="Sophisticated multi-modal analysis approach with advanced reasoning",
            config=config
        )
    
    def execute(self, query: str, vector_db=None, search_results: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the advanced RAG technique.
        
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
            
            # Advanced reasoning and analysis
            enhanced_context = self._advanced_reasoning(processed_query, search_results)
            
            # Combine contexts
            combined_context = self.combine_contexts(search_results, enhanced_context=enhanced_context, **kwargs)
            
            # Generate response
            llm_model = kwargs.get('llm_model', 'gpt-4')
            response = self.generate_response(processed_query, combined_context, **kwargs)
            
            # Postprocess response
            final_response = self.postprocess_response(response)
            
            # Add metadata
            execution_time = (datetime.now() - start_time).total_seconds()
            final_response.update({
                'technique_id': 'advanced',
                'technique_name': self.name,
                'execution_time': execution_time,
                'advanced_features': ['reasoning', 'multi_modal', 'sophisticated_analysis']
            })
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error in advanced RAG execution: {e}")
            raise
    
    def retrieve_context(self, query: str, vector_db=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve context using advanced approach
        
        Args:
            query: User query
            vector_db: Vector database client (optional)
            **kwargs: Additional parameters
            
        Returns:
            List of context documents
        """
        top_k = kwargs.get('top_k', 10)  # More documents for advanced analysis
        
        if not vector_db:
            self.logger.warning("Vector database not provided")
            return []
        
        try:
            # Multiple retrieval strategies
            strategies = [
                self._semantic_search,
                self._keyword_search,
                self._concept_search
            ]
            
            all_docs = []
            for strategy in strategies:
                try:
                    docs = strategy(query, vector_db, top_k)
                    all_docs.extend(docs)
                except Exception as e:
                    self.logger.warning(f"Strategy {strategy.__name__} failed: {e}")
            
            # Deduplicate and rank
            unique_docs = self._deduplicate_and_rank(all_docs)
            
            self.logger.info(f"Retrieved {len(unique_docs)} documents using advanced RAG strategies")
            return unique_docs[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error in advanced RAG retrieval: {e}")
            return []
    
    def _semantic_search(self, query: str, vector_db, top_k: int) -> List[Dict]:
        """Semantic search using vector similarity"""
        try:
            results = vector_db.search_vectors(
                query_vector=self._get_query_embedding(query),
                limit=top_k
            )
            
            docs = []
            for result in results:
                docs.append({
                    'content': result.get('payload', {}).get('content_preview', ''),
                    'score': result.get('score', 0),
                    'metadata': result.get('payload', {}),
                    'id': result.get('id', ''),
                    'strategy': 'semantic'
                })
            return docs
        except Exception as e:
            self.logger.warning(f"Semantic search failed: {e}")
            return []
    
    def _keyword_search(self, query: str, vector_db, top_k: int) -> List[Dict]:
        """Keyword-based search"""
        try:
            # Extract keywords from query
            keywords = self._extract_keywords(query)
            
            # Search with keyword variations
            all_docs = []
            for keyword in keywords[:3]:  # Top 3 keywords
                try:
                    results = vector_db.search_vectors(
                        query_vector=self._get_query_embedding(keyword),
                        limit=top_k // 2
                    )
                    
                    for result in results:
                        all_docs.append({
                            'content': result.get('payload', {}).get('content_preview', ''),
                            'score': result.get('score', 0) * 0.8,  # Lower weight for keyword search
                            'metadata': result.get('payload', {}),
                            'id': result.get('id', ''),
                            'strategy': 'keyword',
                            'keyword': keyword
                        })
                except Exception as e:
                    continue
            
            return all_docs
        except Exception as e:
            self.logger.warning(f"Keyword search failed: {e}")
            return []
    
    def _concept_search(self, query: str, vector_db, top_k: int) -> List[Dict]:
        """Concept-based search using query expansion"""
        try:
            # Expand query with related concepts
            expanded_queries = self._expand_query_with_concepts(query)
            
            all_docs = []
            for expanded_query in expanded_queries:
                try:
                    results = vector_db.search_vectors(
                        query_vector=self._get_query_embedding(expanded_query),
                        limit=top_k // 3
                    )
                    
                    for result in results:
                        all_docs.append({
                            'content': result.get('payload', {}).get('content_preview', ''),
                            'score': result.get('score', 0) * 0.9,  # Slightly lower weight
                            'metadata': result.get('payload', {}),
                            'id': result.get('id', ''),
                            'strategy': 'concept',
                            'concept_query': expanded_query
                        })
                except Exception as e:
                    continue
            
            return all_docs
        except Exception as e:
            self.logger.warning(f"Concept search failed: {e}")
            return []
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        # Simple keyword extraction - in production, use NLP libraries
        words = query.lower().split()
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def _expand_query_with_concepts(self, query: str) -> List[str]:
        """Expand query with related concepts"""
        # Simple concept expansion - in production, use knowledge graphs or concept hierarchies
        concepts = {
            'motor': ['motor', 'motor system', 'motor specifications', 'motor control'],
            'sensor': ['sensor', 'sensor data', 'sensor readings', 'sensor calibration'],
            'system': ['system', 'system architecture', 'system components', 'system integration'],
            'data': ['data', 'data analysis', 'data processing', 'data visualization']
        }
        
        expanded = [query]
        query_lower = query.lower()
        
        for concept, related in concepts.items():
            if concept in query_lower:
                expanded.extend(related)
        
        return expanded[:3]  # Limit to 3 expansions
    
    def _deduplicate_and_rank(self, docs: List[Dict]) -> List[Dict]:
        """Deduplicate documents and rank by multiple criteria"""
        # Group by content hash
        content_groups = {}
        for doc in docs:
            content_hash = hash(doc.get('content', ''))
            if content_hash not in content_groups:
                content_groups[content_hash] = []
            content_groups[content_hash].append(doc)
        
        # Merge duplicates and calculate combined score
        unique_docs = []
        for content_hash, group in content_groups.items():
            if len(group) == 1:
                unique_docs.append(group[0])
            else:
                # Merge multiple versions of same content
                merged_doc = group[0].copy()
                strategies = [doc.get('strategy', 'unknown') for doc in group]
                scores = [doc.get('score', 0) for doc in group]
                
                merged_doc['strategies'] = strategies
                merged_doc['combined_score'] = max(scores) * 1.1  # Boost for multiple strategies
                unique_docs.append(merged_doc)
        
        # Sort by combined score
        unique_docs.sort(key=lambda x: x.get('combined_score', x.get('score', 0)), reverse=True)
        return unique_docs
    
    def _advanced_reasoning(self, query: str, docs: List[Dict]) -> Dict[str, Any]:
        """Perform advanced reasoning on retrieved documents"""
        try:
            # Extract key insights from documents
            insights = self._extract_insights(docs)
            
            # Identify relationships between documents
            relationships = self._identify_relationships(docs)
            
            # Generate reasoning summary
            reasoning_summary = self._generate_reasoning_summary(query, insights, relationships)
            
            return {
                'insights': insights,
                'relationships': relationships,
                'reasoning_summary': reasoning_summary
            }
        except Exception as e:
            self.logger.warning(f"Advanced reasoning failed: {e}")
            return {}
    
    def _extract_insights(self, docs: List[Dict]) -> List[str]:
        """Extract key insights from documents"""
        insights = []
        for doc in docs[:5]:  # Top 5 documents
            content = doc.get('content', '')
            if content:
                # Simple insight extraction - in production, use more sophisticated NLP
                sentences = content.split('.')
                for sentence in sentences[:2]:  # First 2 sentences
                    if len(sentence.strip()) > 20:
                        insights.append(sentence.strip())
        return insights[:10]  # Limit to 10 insights
    
    def _identify_relationships(self, docs: List[Dict]) -> List[Dict]:
        """Identify relationships between documents"""
        relationships = []
        # Simple relationship identification - in production, use graph analysis
        for i, doc1 in enumerate(docs[:3]):
            for j, doc2 in enumerate(docs[i+1:4], i+1):
                # Check for common terms
                content1 = doc1.get('content', '').lower()
                content2 = doc2.get('content', '').lower()
                
                words1 = set(content1.split())
                words2 = set(content2.split())
                common_words = words1.intersection(words2)
                
                if len(common_words) >= 2:
                    relationships.append({
                        'doc1_id': doc1.get('id', f'doc_{i}'),
                        'doc2_id': doc2.get('id', f'doc_{j}'),
                        'relationship_type': 'shared_terms',
                        'common_terms': list(common_words)[:3]
                    })
        
        return relationships
    
    def _generate_reasoning_summary(self, query: str, insights: List[str], relationships: List[Dict]) -> str:
        """Generate reasoning summary"""
        summary_parts = []
        
        if insights:
            summary_parts.append("Key Insights:")
            for i, insight in enumerate(insights[:5], 1):
                summary_parts.append(f"{i}. {insight}")
        
        if relationships:
            summary_parts.append("\nDocument Relationships:")
            for rel in relationships[:3]:
                summary_parts.append(f"• {rel['doc1_id']} ↔ {rel['doc2_id']}: {rel['relationship_type']}")
        
        return "\n".join(summary_parts) if summary_parts else "No advanced reasoning available"
    
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict = None, enhanced_context: Dict = None, **kwargs) -> str:
        """
        Combine contexts with advanced analysis emphasis
        
        Args:
            vector_docs: Documents from vector search
            graph_context: Context from knowledge graph (optional)
            enhanced_context: Enhanced context from advanced reasoning (optional)
            **kwargs: Additional parameters
            
        Returns:
            Combined context string
        """
        combined = []
        
        # Add advanced reasoning summary
        if enhanced_context and enhanced_context.get('reasoning_summary'):
            combined.append("=== Advanced Reasoning Analysis ===")
            combined.append(enhanced_context['reasoning_summary'])
        
        # Add multi-strategy retrieval results
        if vector_docs:
            combined.append("\n=== Multi-Strategy Retrieval Results ===")
            
            # Group by strategy
            strategies = {}
            for doc in vector_docs:
                strategy = doc.get('strategy', 'unknown')
                if strategy not in strategies:
                    strategies[strategy] = []
                strategies[strategy].append(doc)
            
            for strategy, docs in strategies.items():
                combined.append(f"\n--- {strategy.title()} Search Results ---")
                for i, doc in enumerate(docs[:3], 1):  # Top 3 per strategy
                    content = doc.get('content', '')
                    score = doc.get('combined_score', doc.get('score', 0))
                    combined.append(f"{i}. {content}")
                    combined.append(f"   Score: {score:.3f} | Strategy: {strategy}")
        
        # Add graph context if available
        if graph_context and graph_context.get('graph_data'):
            combined.append("\n=== Knowledge Graph Context ===")
            for record in graph_context['graph_data']:
                combined.append(f"• {record.get('type', 'Unknown')}: {record.get('id', 'Unknown')}")
        
        return "\n".join(combined) if combined else "No context available"
    
    def generate_response(self, query: str, context: str, llm_model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generate response with advanced analysis emphasis
        
        Args:
            query: User query
            context: Combined context
            llm_model: LLM model to use (optional)
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        try:
            # Use GPT-4 for advanced analysis if available
            if not llm_model:
                llm_model = 'gpt-4'
            
            # Build system prompt for advanced approach
            system_prompt = self.config.get('system_prompt', 
                "You are an advanced AI assistant analyzing digital twin data using sophisticated multi-modal analysis. "
                "Provide deep insights, identify patterns, and offer comprehensive analysis.")
            
            # Build user prompt
            user_prompt = f"""
Question: {query}

Context from advanced multi-modal analysis:
{context}

Please provide a sophisticated analysis that includes:
1. Deep insights from the multi-strategy retrieval
2. Pattern recognition and trend analysis
3. Comprehensive understanding of relationships and connections
4. Actionable recommendations based on the analysis

Provide a detailed, well-structured response that demonstrates advanced reasoning capabilities.
"""
            
            # Query OpenAI
            response = openai.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 1500)
            )
            
            # Format response
            result = {
                'answer': response.choices[0].message.content,
                'model': llm_model,
                'technique': self.name,
                'advanced_analysis': True,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Generated advanced RAG response using {llm_model}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating advanced RAG response: {e}")
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
        """Validate advanced RAG parameters"""
        # Advanced RAG doesn't have strict parameter requirements
        return True 