"""
Graph RAG Technique
Knowledge graph integration approach for the new modular system
"""

from typing import Dict, List, Any
import openai
from datetime import datetime
import json
from .base_technique import BaseRAGTechnique
from src.ai_rag.embedding_models.text_embeddings import TextEmbeddingManager


class GraphRAGTechnique(BaseRAGTechnique):
    """Graph RAG technique with knowledge graph integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Graph RAG",
            description="Knowledge graph integration approach using graph queries and relationships",
            config=config
        )
    
    def execute(self, query: str, vector_db=None, search_results: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the graph RAG technique.
        
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
                'technique_id': 'graph',
                'technique_name': self.name,
                'execution_time': execution_time
            })
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error in graph RAG execution: {e}")
            raise
    
    def retrieve_context(self, query: str, vector_db=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve context using graph-enhanced approach
        
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
            # Vector search for initial context
            vector_results = vector_db.search_vectors(
                query_vector=self._get_query_embedding(query),
                limit=top_k
            )
            
            # Convert to standard format
            vector_docs = []
            for result in vector_results:
                vector_docs.append({
                    'content': result.get('payload', {}).get('content_preview', ''),
                    'score': result.get('score', 0),
                    'metadata': result.get('payload', {}),
                    'id': result.get('id', ''),
                    'source': 'vector'
                })
            
            # Graph-based retrieval if available
            graph_docs = []
            graph_query_func = kwargs.get('graph_query_func')
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
    
    def combine_contexts(self, vector_docs: List[Dict], graph_context: Dict = None, **kwargs) -> str:
        """
        Combine contexts with graph emphasis
        
        Args:
            vector_docs: Documents from vector search (graph-enhanced)
            graph_context: Context from knowledge graph (optional)
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
    
    def generate_response(self, query: str, context: str, llm_model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generate response with graph integration emphasis
        
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
        """Validate graph RAG parameters"""
        # Graph RAG doesn't have strict parameter requirements
        return True 