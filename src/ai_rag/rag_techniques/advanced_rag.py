"""
Advanced RAG Technique
Multi-modal + reasoning approach
"""

from typing import Dict, List, Any
import openai
from datetime import datetime
import json
from .base_technique import BaseRAGTechnique

class AdvancedRAGTechnique(BaseRAGTechnique):
    """Advanced RAG technique with multi-modal and reasoning capabilities"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="Advanced RAG",
            description="Multi-modal + reasoning approach with advanced context processing",
            config=config
        )
    
    def retrieve_context(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve context using advanced multi-modal approach
        
        Args:
            query: User query
            **kwargs: Additional parameters including vector_search_func and graph_query_func
            
        Returns:
            List of context documents
        """
        vector_search_func = kwargs.get('vector_search_func')
        graph_query_func = kwargs.get('graph_query_func')
        top_k = kwargs.get('top_k', 5)
        
        if not vector_search_func:
            self.logger.warning("Vector search function not provided")
            return []
        
        try:
            # Multi-modal retrieval
            vector_docs = vector_search_func(query, top_k=top_k)
            graph_docs = []
            
            if graph_query_func:
                graph_docs = self._advanced_graph_retrieval(query, graph_query_func, top_k)
            
            # Apply advanced filtering and reranking
            filtered_docs = self._apply_advanced_filtering(vector_docs, query)
            reranked_docs = self._apply_advanced_reranking(filtered_docs, query)
            
            # Combine all sources
            combined_docs = self._combine_advanced_sources(reranked_docs, graph_docs)
            
            self.logger.info(f"Retrieved {len(combined_docs)} documents for advanced RAG")
            return combined_docs
            
        except Exception as e:
            self.logger.error(f"Error in advanced RAG retrieval: {e}")
            return []
    
    def _advanced_graph_retrieval(self, query: str, graph_query_func, top_k: int) -> List[Dict[str, Any]]:
        """
        Perform advanced graph-based retrieval with reasoning
        
        Args:
            query: Search query
            graph_query_func: Function to query the knowledge graph
            top_k: Number of results to return
            
        Returns:
            List of advanced graph-based documents
        """
        try:
            # Generate multiple graph queries for different aspects
            graph_queries = self._generate_advanced_graph_queries(query)
            
            all_graph_results = []
            for query_type, cypher_query in graph_queries.items():
                try:
                    results = graph_query_func(cypher_query)
                    for result in results:
                        result['query_type'] = query_type
                        all_graph_results.append(result)
                except Exception as e:
                    self.logger.warning(f"Graph query {query_type} failed: {e}")
            
            # Convert to document format with reasoning
            graph_docs = []
            for result in all_graph_results:
                doc = {
                    'content': self._format_advanced_graph_result(result),
                    'source': 'advanced_graph',
                    'graph_data': result,
                    'reasoning_type': result.get('query_type', 'general'),
                    'score': 1.0,
                    'metadata': {
                        'query_type': 'advanced_graph',
                        'reasoning_type': result.get('query_type', 'general')
                    }
                }
                graph_docs.append(doc)
            
            return graph_docs[:top_k]
            
        except Exception as e:
            self.logger.warning(f"Advanced graph retrieval failed: {e}")
            return []
    
    def _generate_advanced_graph_queries(self, query: str) -> Dict[str, str]:
        """
        Generate multiple graph queries for different reasoning aspects
        
        Args:
            query: User query
            
        Returns:
            Dictionary of query types and Cypher queries
        """
        query_lower = query.lower()
        queries = {}
        
        # Entity-focused queries
        if any(word in query_lower for word in ['asset', 'device', 'component']):
            queries['entity_analysis'] = """
            MATCH (n:Asset)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n.id as id, labels(n)[0] as type, n.properties as properties, 
                   type(r) as relationship, m.id as related_id
            LIMIT 15
            """
        
        # Relationship-focused queries
        if any(word in query_lower for word in ['relationship', 'connection', 'dependency']):
            queries['relationship_analysis'] = """
            MATCH (a)-[r]->(b)
            RETURN a.id as source_id, type(r) as relationship, b.id as target_id,
                   a.properties as source_props, b.properties as target_props
            LIMIT 15
            """
        
        # Hierarchical queries
        if any(word in query_lower for word in ['hierarchy', 'structure', 'organization']):
            queries['hierarchical_analysis'] = """
            MATCH path = (n)-[:CONTAINS*]->(m)
            RETURN n.id as root_id, m.id as child_id, length(path) as depth
            ORDER BY depth
            LIMIT 15
            """
        
        # Default comprehensive query
        if not queries:
            queries['comprehensive_analysis'] = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n.id as id, labels(n)[0] as type, n.properties as properties,
                   type(r) as relationship, m.id as related_id
            LIMIT 20
            """
        
        return queries
    
    def _format_advanced_graph_result(self, result: Dict) -> str:
        """
        Format advanced graph result with reasoning context
        
        Args:
            result: Graph query result
            
        Returns:
            Formatted text with reasoning
        """
        query_type = result.get('query_type', 'general')
        
        if query_type == 'entity_analysis':
            return f"Entity Analysis: {result.get('type', 'Unknown')} - {result.get('id', 'Unknown')} " \
                   f"(Related to: {result.get('related_id', 'None')} via {result.get('relationship', 'None')})"
        
        elif query_type == 'relationship_analysis':
            return f"Relationship Analysis: {result.get('source_id', 'Unknown')} --[{result.get('relationship', 'RELATES_TO')}]--> {result.get('target_id', 'Unknown')}"
        
        elif query_type == 'hierarchical_analysis':
            return f"Hierarchical Analysis: {result.get('root_id', 'Unknown')} -> {result.get('child_id', 'Unknown')} (Depth: {result.get('depth', 0)})"
        
        else:
            # Default formatting
            return f"Graph Node: {result.get('id', 'Unknown')} - Type: {result.get('type', 'Unknown')}"
    
    def _apply_advanced_filtering(self, docs: List[Dict], query: str) -> List[Dict]:
        """
        Apply advanced filtering based on multiple criteria
        
        Args:
            docs: Documents to filter
            query: Original query
            
        Returns:
            Filtered documents
        """
        filtered = []
        query_keywords = set(query.lower().split())
        
        for doc in docs:
            content = doc.get('content', '').lower()
            metadata = str(doc.get('metadata', {})).lower()
            
            # Calculate relevance score
            content_relevance = sum(1 for keyword in query_keywords if keyword in content)
            metadata_relevance = sum(1 for keyword in query_keywords if keyword in metadata)
            
            # Apply filters
            if content_relevance > 0 or metadata_relevance > 0:
                doc['advanced_score'] = content_relevance + metadata_relevance * 0.5
                filtered.append(doc)
        
        return filtered
    
    def _apply_advanced_reranking(self, docs: List[Dict], query: str) -> List[Dict]:
        """
        Apply advanced reranking with reasoning
        
        Args:
            docs: Documents to rerank
            query: Original query
            
        Returns:
            Reranked documents
        """
        for doc in docs:
            # Combine multiple scoring factors
            base_score = doc.get('score', 0)
            advanced_score = doc.get('advanced_score', 0)
            
            # Weighted combination
            final_score = 0.6 * base_score + 0.4 * advanced_score
            
            # Bonus for graph-enhanced documents
            if doc.get('source') == 'advanced_graph':
                final_score *= 1.2
            
            doc['final_score'] = final_score
        
        # Sort by final score
        docs.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        return docs
    
    def _combine_advanced_sources(self, vector_docs: List[Dict], graph_docs: List[Dict]) -> List[Dict]:
        """
        Combine vector and graph sources with advanced logic
        
        Args:
            vector_docs: Documents from vector search
            graph_docs: Documents from graph search
            
        Returns:
            Combined documents
        """
        combined = []
        
        # Add vector results
        for doc in vector_docs:
            doc['source_type'] = 'vector'
            combined.append(doc)
        
        # Add graph results
        for doc in graph_docs:
            doc['source_type'] = 'graph'
            combined.append(doc)
        
        # Sort by final score
        combined.sort(key=lambda x: x.get('final_score', x.get('score', 0)), reverse=True)
        
        return combined
    
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict, **kwargs) -> str:
        """
        Combine contexts with advanced multi-modal approach
        
        Args:
            vector_docs: Documents from vector search (advanced)
            graph_context: Context from knowledge graph
            **kwargs: Additional parameters
            
        Returns:
            Combined context string
        """
        combined = []
        
        # Add advanced retrieval results
        if vector_docs:
            combined.append("=== Advanced Multi-Modal Retrieval Results ===")
            
            # Group by source type
            vector_results = [doc for doc in vector_docs if doc.get('source_type') == 'vector']
            graph_results = [doc for doc in vector_docs if doc.get('source_type') == 'graph']
            
            if vector_results:
                combined.append("\n--- Vector Search Results ---")
                for i, doc in enumerate(vector_results, 1):
                    content = doc.get('content', '')
                    final_score = doc.get('final_score', doc.get('score', 0))
                    combined.append(f"{i}. {content}")
                    combined.append(f"   Final Score: {final_score:.3f}")
            
            if graph_results:
                combined.append("\n--- Advanced Graph Results ---")
                for i, doc in enumerate(graph_results, 1):
                    content = doc.get('content', '')
                    reasoning_type = doc.get('reasoning_type', 'general')
                    combined.append(f"{i}. {content}")
                    combined.append(f"   Reasoning Type: {reasoning_type}")
        
        # Add additional graph context
        if graph_context and graph_context.get('graph_data'):
            combined.append("\n=== Additional Knowledge Graph Context ===")
            for record in graph_context['graph_data']:
                combined.append(f"• {record.get('type', 'Unknown')}: {record.get('id', 'Unknown')}")
        
        # Add metadata analysis
        combined.append("\n=== Metadata Analysis ===")
        metadata_summary = self._analyze_advanced_metadata(vector_docs)
        combined.append(metadata_summary)
        
        return "\n".join(combined) if combined else "No context available"
    
    def _analyze_advanced_metadata(self, docs: List[Dict]) -> str:
        """
        Analyze metadata with advanced insights
        
        Args:
            docs: Documents to analyze
            
        Returns:
            Metadata analysis summary
        """
        if not docs:
            return "No metadata available"
        
        analysis = []
        source_types = set()
        reasoning_types = set()
        file_types = set()
        
        for doc in docs:
            source_types.add(doc.get('source_type', 'unknown'))
            reasoning_types.add(doc.get('reasoning_type', 'none'))
            
            metadata = doc.get('metadata', {})
            if isinstance(metadata, dict):
                file_types.add(metadata.get('file_type', 'unknown'))
        
        if source_types:
            analysis.append(f"Source Types: {', '.join(source_types)}")
        if reasoning_types and 'none' not in reasoning_types:
            analysis.append(f"Reasoning Types: {', '.join(reasoning_types)}")
        if file_types:
            analysis.append(f"File Types: {', '.join(file_types)}")
        
        return " | ".join(analysis) if analysis else "Standard metadata"
    
    def generate_response(self, query: str, context: str, llm_model: str, **kwargs) -> Dict[str, Any]:
        """
        Generate response with advanced reasoning
        
        Args:
            query: User query
            context: Combined context
            llm_model: LLM model to use
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        try:
            # Build system prompt for advanced approach
            system_prompt = self.config.get('system_prompt', 
                "You are an AI assistant analyzing digital twin data using advanced multi-modal retrieval and reasoning. "
                "Consider multiple data sources, relationships, and apply sophisticated analysis techniques.")
            
            # Build user prompt
            user_prompt = f"""
Question: {query}

Context from advanced multi-modal retrieval and reasoning:
{context}

Please provide a comprehensive analysis that demonstrates:
1. Multi-modal understanding (vector similarity + graph relationships)
2. Advanced reasoning about entity relationships and dependencies
3. Sophisticated insights from the combined data sources
4. Clear recommendations based on the analysis

Provide a structured, insightful response that leverages all available data modalities.
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
                'advanced_features': True,
                'multi_modal': True,
                'reasoning_applied': True,
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
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate advanced RAG parameters"""
        required_params = ['vector_search_func']
        for param in required_params:
            if param not in kwargs:
                self.logger.error(f"Missing required parameter: {param}")
                return False
        return True 