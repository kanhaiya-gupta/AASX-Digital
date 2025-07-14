"""
Graph RAG Technique
Knowledge graph integration approach
"""

from typing import Dict, List, Any
import openai
from datetime import datetime
import json
from .base_technique import BaseRAGTechnique

class GraphRAGTechnique(BaseRAGTechnique):
    """Graph RAG technique with knowledge graph integration"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="Graph RAG",
            description="Knowledge graph integration approach using graph queries and relationships",
            config=config
        )
    
    def retrieve_context(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve context using graph-enhanced approach
        
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
            # Vector search for initial context
            vector_docs = vector_search_func(query, top_k=top_k)
            
            # Graph-based retrieval if available
            graph_docs = []
            if graph_query_func:
                graph_docs = self._graph_based_retrieval(query, graph_query_func, top_k)
            
            # Combine vector and graph results
            combined_docs = self._combine_vector_and_graph(vector_docs, graph_docs)
            
            self.logger.info(f"Retrieved {len(combined_docs)} documents for graph RAG (vector: {len(vector_docs)}, graph: {len(graph_docs)})")
            return combined_docs
            
        except Exception as e:
            self.logger.error(f"Error in graph RAG retrieval: {e}")
            return []
    
    def _graph_based_retrieval(self, query: str, graph_query_func, top_k: int) -> List[Dict[str, Any]]:
        """
        Perform graph-based retrieval using knowledge graph
        
        Args:
            query: Search query
            graph_query_func: Function to query the knowledge graph
            top_k: Number of results to return
            
        Returns:
            List of graph-based documents
        """
        try:
            # Generate graph query based on user query
            graph_query = self._generate_graph_query(query)
            
            # Execute graph query
            graph_results = graph_query_func(graph_query)
            
            # Convert graph results to document format
            graph_docs = []
            for result in graph_results:
                doc = {
                    'content': self._format_graph_result(result),
                    'source': 'graph',
                    'graph_data': result,
                    'score': 1.0,  # Graph results get default score
                    'metadata': {
                        'query_type': 'graph',
                        'graph_query': graph_query
                    }
                }
                graph_docs.append(doc)
            
            return graph_docs[:top_k]
            
        except Exception as e:
            self.logger.warning(f"Graph-based retrieval failed: {e}")
            return []
    
    def _generate_graph_query(self, query: str) -> str:
        """
        Generate Cypher query based on user query
        
        Args:
            query: User query
            
        Returns:
            Cypher query string
        """
        # Simple keyword-based query generation
        query_lower = query.lower()
        
        if 'asset' in query_lower or 'device' in query_lower:
            return """
            MATCH (n:Asset)
            RETURN n.id as id, labels(n)[0] as type, n.properties as properties
            LIMIT 10
            """
        elif 'submodel' in query_lower or 'model' in query_lower:
            return """
            MATCH (n:Submodel)
            RETURN n.id as id, labels(n)[0] as type, n.properties as properties
            LIMIT 10
            """
        elif 'relationship' in query_lower or 'connection' in query_lower:
            return """
            MATCH (a)-[r]->(b)
            RETURN a.id as source_id, type(r) as relationship, b.id as target_id
            LIMIT 10
            """
        else:
            # Default query for any node
            return """
            MATCH (n)
            RETURN n.id as id, labels(n)[0] as type, n.properties as properties
            LIMIT 10
            """
    
    def _format_graph_result(self, result: Dict) -> str:
        """
        Format graph result as readable text
        
        Args:
            result: Graph query result
            
        Returns:
            Formatted text
        """
        if 'source_id' in result and 'target_id' in result:
            # Relationship result
            return f"Graph Relationship: {result['source_id']} --[{result.get('relationship', 'RELATES_TO')}]--> {result['target_id']}"
        else:
            # Node result
            node_type = result.get('type', 'Unknown')
            node_id = result.get('id', 'Unknown')
            properties = result.get('properties', {})
            
            if properties:
                props_str = ", ".join([f"{k}: {v}" for k, v in properties.items() if v])
                return f"Graph Node ({node_type}): {node_id} - Properties: {props_str}"
            else:
                return f"Graph Node ({node_type}): {node_id}"
    
    def _combine_vector_and_graph(self, vector_docs: List[Dict], graph_docs: List[Dict]) -> List[Dict]:
        """
        Combine vector and graph retrieval results
        
        Args:
            vector_docs: Documents from vector search
            graph_docs: Documents from graph search
            
        Returns:
            Combined documents
        """
        combined = []
        
        # Add vector results with graph enhancement flag
        for doc in vector_docs:
            doc['enhanced_with_graph'] = len(graph_docs) > 0
            combined.append(doc)
        
        # Add graph results
        for doc in graph_docs:
            combined.append(doc)
        
        # Sort by score (vector docs first, then graph docs)
        combined.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return combined
    
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict, **kwargs) -> str:
        """
        Combine contexts with graph emphasis
        
        Args:
            vector_docs: Documents from vector search (graph-enhanced)
            graph_context: Context from knowledge graph
            **kwargs: Additional parameters
            
        Returns:
            Combined context string
        """
        combined = []
        
        # Start with graph context
        if graph_context and graph_context.get('graph_data'):
            combined.append("=== Knowledge Graph Context ===")
            for record in graph_context['graph_data']:
                combined.append(f"• {record.get('type', 'Unknown')}: {record.get('id', 'Unknown')}")
                if record.get('properties'):
                    props_str = ", ".join([f"{k}: {v}" for k, v in record['properties'].items() if v])
                    combined.append(f"  Properties: {props_str}")
        
        # Add vector results as supporting evidence
        if vector_docs:
            combined.append("\n=== Supporting Vector Evidence ===")
            for i, doc in enumerate(vector_docs, 1):
                content = doc.get('content', '')
                score = doc.get('score', 0)
                source = doc.get('source', 'vector')
                enhanced = doc.get('enhanced_with_graph', False)
                
                combined.append(f"{i}. {content}")
                combined.append(f"   Score: {score:.3f} | Source: {source}")
                if enhanced:
                    combined.append(f"   Enhanced with graph context")
        
        # Add graph-specific documents
        graph_docs = [doc for doc in vector_docs if doc.get('source') == 'graph']
        if graph_docs:
            combined.append("\n=== Graph-Based Retrieval Results ===")
            for i, doc in enumerate(graph_docs, 1):
                combined.append(f"{i}. {doc.get('content', '')}")
        
        return "\n".join(combined) if combined else "No context available"
    
    def generate_response(self, query: str, context: str, llm_model: str, **kwargs) -> Dict[str, Any]:
        """
        Generate response with graph integration emphasis
        
        Args:
            query: User query
            context: Combined context
            llm_model: LLM model to use
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        try:
            # Build system prompt for graph approach
            system_prompt = self.config.get('system_prompt', 
                "You are an AI assistant analyzing digital twin data using knowledge graph integration. "
                "Consider the relationships and connections between entities in your analysis.")
            
            # Build user prompt
            user_prompt = f"""
Question: {query}

Context from knowledge graph integration:
{context}

Please provide a comprehensive analysis that considers:
1. The relationships and connections between digital twin entities
2. How the knowledge graph enhances understanding of the data
3. The structural insights provided by graph-based retrieval

Provide a clear, structured response that leverages both vector similarity and graph relationships.
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
                'graph_integration': True,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Generated graph RAG response using {llm_model}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating graph RAG response: {e}")
            raise
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate graph RAG parameters"""
        required_params = ['vector_search_func']
        for param in required_params:
            if param not in kwargs:
                self.logger.error(f"Missing required parameter: {param}")
                return False
        return True 