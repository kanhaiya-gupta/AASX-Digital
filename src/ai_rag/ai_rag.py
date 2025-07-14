"""
AASX Digital Twin Analytics Framework - AI/RAG System
Provides AI-powered analysis and insights for digital twin data
"""

import os
import json
import logging
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from neo4j import GraphDatabase
import uuid

# Import data migration module
try:
    from .data_migration import DataMigrationManager
    MIGRATION_AVAILABLE = True
except ImportError:
    MIGRATION_AVAILABLE = False
    logging.warning("Data migration module not available")

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AASXDigitalTwinRAG:
    """AI/RAG system for AASX Digital Twin Analytics Framework"""
    
    def __init__(self, config_path: str = "src/config/config_enhanced_rag.yaml"):
        """Initialize the RAG system"""
        self.config = self._load_config(config_path)
        self._setup_clients()
        self._setup_collection()
        
        # Initialize data migration manager
        if MIGRATION_AVAILABLE:
            self.migration_manager = DataMigrationManager(
                chromadb_path="output/vector_db",
                qdrant_url=self.config['qdrant']['url'],
                embedding_model=self.config['embeddings']['model']
            )
        else:
            self.migration_manager = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"✅ Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            raise
    
    def _setup_clients(self):
        """Setup database and AI clients"""
        # OpenAI client
        api_key = os.getenv('OPENAI_API_KEY') or self.config['openai'].get('api_key')
        if not api_key:
            logger.warning("⚠️  OpenAI API key not found")
        else:
            openai.api_key = api_key
            logger.info("✅ OpenAI client configured")
        
        # Qdrant client
        try:
            qdrant_url = os.getenv('QDRANT_URL') or self.config['qdrant'].get('url')
            qdrant_port = int(qdrant_url.split(":")[-1]) if qdrant_url and ":" in qdrant_url else self.config['qdrant'].get('port', 6333)
            self.qdrant_client = QdrantClient(
                host=qdrant_url.replace('http://','').replace('https://','').split(":")[0],
                port=qdrant_port
            )
            logger.info("✅ Qdrant client connected")
        except Exception as e:
            logger.error(f"❌ Qdrant connection failed: {e}")
            raise
        
        # Neo4j client
        try:
            neo4j_uri = os.getenv('NEO4J_URI') or self.config['neo4j']['uri']
            neo4j_user = os.getenv('NEO4J_USER') or self.config['neo4j'].get('user') or self.config['neo4j'].get('username')
            neo4j_password = os.getenv('NEO4J_PASSWORD') or self.config['neo4j'].get('password')
            self.neo4j_driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(neo4j_user, neo4j_password)
            )
            logger.info("✅ Neo4j client connected")
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            raise
    
    def _setup_collection(self):
        """Setup Qdrant collection for vector storage"""
        collection_name = self.config['qdrant']['collection_name']
        
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if collection_name not in collection_names:
                # Create collection
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.config['qdrant']['vector_size'],
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created Qdrant collection: {collection_name}")
            else:
                logger.info(f"✅ Using existing Qdrant collection: {collection_name}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to setup Qdrant collection: {e}")
            raise
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add a document to the vector database"""
        try:
            # Generate embedding
            embedding = self._get_embedding(content)
            
            # Create point
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Add to collection
            self.qdrant_client.upsert(
                collection_name=self.config['qdrant']['collection_name'],
                points=[point]
            )
            
            logger.info(f"✅ Added document with ID: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add document: {e}")
            raise
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI or local model"""
        try:
            # Check if we should use local embeddings
            use_local = self.config.get('embeddings', {}).get('use_local', False)
            
            if use_local:
                return self._get_local_embedding(text)
            else:
                response = openai.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
        except Exception as e:
            logger.error(f"❌ Failed to get embedding: {e}")
            raise
    
    def _get_local_embedding(self, text: str) -> List[float]:
        """Get embedding using local sentence-transformers model"""
        try:
            # Import sentence-transformers (install if needed)
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                logger.error("❌ sentence-transformers not installed. Install with: pip install sentence-transformers")
                raise ImportError("sentence-transformers not installed")
            
            # Get model name from config
            model_name = self.config.get('embeddings', {}).get('model', 'all-MiniLM-L6-v2')
            
            # Load model (will download on first use)
            if not hasattr(self, '_local_model'):
                logger.info(f"🔧 Loading local embedding model: {model_name}")
                self._local_model = SentenceTransformer(model_name)
            
            # Generate embedding
            embedding = self._local_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"❌ Failed to get local embedding: {e}")
            raise
    
    def search_similar(self, query: str, top_k: int = 5, file_filter: str = None) -> List[Dict[str, Any]]:
        """
        Search for similar entities across all file-specific collections
        
        Args:
            query: Search query
            top_k: Number of results to return
            file_filter: Optional file name to filter results (e.g., "Example_AAS_ServoDCMotor_21")
            
        Returns:
            List of similar entities with file context
        """
        if not self.qdrant_client:
            logger.warning("Qdrant client not available")
            return []
        
        try:
            # Generate query embedding
            if self.use_local_embeddings:
                query_embedding = self.local_embedding_model.encode(query).tolist()
            else:
                response = self.openai_client.embeddings.create(
                    input=query,
                    model="text-embedding-3-small"
                )
                query_embedding = response.data[0].embedding
            
            # Get all collections
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            # Filter collections based on file_filter
            if file_filter:
                # Search only in collections for the specific file
                target_collections = [name for name in collection_names 
                                    if file_filter.lower() in name.lower()]
            else:
                # Search in all AASX collections
                collection_prefix = self.config['qdrant'].get('collection_prefix', 'aasx')
                target_collections = [name for name in collection_names 
                                    if name.startswith(collection_prefix)]
            
            if not target_collections:
                logger.warning(f"No collections found for search")
                return []
            
            all_results = []
            
            # Search in each collection
            for collection_name in target_collections:
                try:
                    # Search in this collection
                    search_results = self.qdrant_client.search(
                        collection_name=collection_name,
                        query_vector=query_embedding,
                        limit=top_k,
                        with_payload=True,
                        with_vectors=False
                    )
                    
                    # Add collection context to results
                    for result in search_results:
                        payload = result.payload
                        all_results.append({
                            'id': result.id,
                            'score': result.score,
                            'content': payload.get('content', ''),
                            'entity_type': payload.get('entity_type', ''),
                            'source_file': payload.get('source_file', ''),
                            'file_name': payload.get('file_name', ''),
                            'collection_name': collection_name,
                            'metadata': payload.get('metadata', {}),
                            'timestamp': payload.get('timestamp', '')
                        })
                        
                except Exception as e:
                    logger.error(f"Error searching collection {collection_name}: {e}")
                    continue
            
            # Sort by score and return top_k results
            all_results.sort(key=lambda x: x['score'], reverse=True)
            return all_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, str]:
        """
        Get system status for all components
        
        Returns:
            Dictionary with status of each component
        """
        status = {}
        
        # Check OpenAI
        try:
            if self.openai_client:
                # Simple test call
                status['openai'] = 'connected'
            else:
                status['openai'] = 'not_configured'
        except Exception as e:
            status['openai'] = f'error: {str(e)}'
        
        # Check Qdrant
        try:
            if self.qdrant_client:
                collections = self.qdrant_client.get_collections()
                status['qdrant'] = f'connected ({len(collections.collections)} collections)'
            else:
                status['qdrant'] = 'not_connected'
        except Exception as e:
            status['qdrant'] = f'error: {str(e)}'
        
        # Check Neo4j
        try:
            if hasattr(self, 'neo4j_manager') and self.neo4j_manager:
                status['neo4j'] = 'connected'
            else:
                status['neo4j'] = 'not_configured'
        except Exception as e:
            status['neo4j'] = f'error: {str(e)}'
        
        return status

    def get_available_files(self) -> List[Dict[str, Any]]:
        """
        Get list of available AASX files with their collection information
        
        Returns:
            List of file information with collection counts
        """
        if not self.qdrant_client:
            return []
        
        try:
            collections = self.qdrant_client.get_collections()
            file_info = {}
            
            for collection in collections.collections:
                collection_name = collection.name
                
                # Parse collection name to extract file name
                collection_prefix = self.config['qdrant'].get('collection_prefix', 'aasx')
                if collection_name.startswith(collection_prefix):
                    parts = collection_name.split('_')
                    if len(parts) >= 3:
                        file_name = parts[1]  # Extract file name from collection
                        entity_type = parts[2].rstrip('s')  # Remove 's' from end
                        
                        if file_name not in file_info:
                            file_info[file_name] = {
                                'file_name': file_name,
                                'collections': {},
                                'total_embeddings': 0
                            }
                        
                        # Get collection info
                        info = self.qdrant_client.get_collection(collection_name)
                        embedding_count = info.points_count
                        
                        file_info[file_name]['collections'][entity_type] = embedding_count
                        file_info[file_name]['total_embeddings'] += embedding_count
            
            return list(file_info.values())
            
        except Exception as e:
            logger.error(f"Error getting available files: {e}")
            return []
    
    def delete_file_data(self, file_name: str) -> bool:
        """
        Delete all vector data for a specific file
        
        Args:
            file_name: Name of the file to delete (without extension)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.qdrant_client:
            return False
        
        try:
            collections = self.qdrant_client.get_collections()
            deleted_collections = []
            
            for collection in collections.collections:
                collection_name = collection.name
                
                # Check if this collection belongs to the specified file
                collection_prefix = self.config['qdrant'].get('collection_prefix', 'aasx')
                if (collection_name.startswith(collection_prefix) and 
                    file_name.lower() in collection_name.lower()):
                    
                    try:
                        self.qdrant_client.delete_collection(collection_name)
                        deleted_collections.append(collection_name)
                        logger.info(f"Deleted collection: {collection_name}")
                    except Exception as e:
                        logger.error(f"Error deleting collection {collection_name}: {e}")
            
            if deleted_collections:
                logger.info(f"Deleted {len(deleted_collections)} collections for file: {file_name}")
                return True
            else:
                logger.warning(f"No collections found for file: {file_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file data: {e}")
            return False
    
    def query_ai(self, question: str, context_docs: List[Dict] = None) -> Dict:
        """Query AI with context from vector search"""
        try:
            # Get relevant context
            if not context_docs:
                context_docs = self.search_similar(question)
            
            # Build enhanced context with metadata
            context_parts = []
            for i, doc in enumerate(context_docs, 1):
                content = doc.get('content', '')
                entity_type = doc.get('entity_type', '')
                source_file = doc.get('source_file', '')
                collection_name = doc.get('collection_name', '')
                
                context_part = f"Source {i} ({entity_type} from {source_file}):\n{content}"
                context_parts.append(context_part)
            
            context = "\n\n".join(context_parts)
            
            # Build prompt
            system_prompt = self.config['rag']['system_prompt']
            user_prompt = f"""
Question: {question}

Context from digital twin data:
{context}

Please provide a comprehensive analysis based on the available digital twin data.
"""
            
            # Query OpenAI
            response = openai.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config['openai']['temperature'],
                max_tokens=self.config['openai']['max_tokens']
            )
            
            # Format response
            result = {
                'answer': response.choices[0].message.content,
                'model': self.config['openai']['model'],
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'sources': [doc['metadata'] for doc in context_docs],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ AI query completed using {result['model']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ AI query failed: {e}")
            raise
    
    def analyze_category(self, category: str, query: str) -> Dict:
        """Analyze data for a specific category"""
        try:
            # Get category info
            categories = self.config['analysis_categories']
            if category not in categories:
                raise ValueError(f"Unknown category: {category}")
            
            category_info = categories[category]
            
            # Build category-specific query
            enhanced_query = f"{category_info['description']}: {query}"
            
            # Get AI response
            result = self.query_ai(enhanced_query)
            
            # Add category metadata
            result['category'] = category
            result['category_name'] = category_info['name']
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Category analysis failed: {e}")
            raise
    
    def get_graph_insights(self, query: str) -> Dict:
        """Get insights from Neo4j knowledge graph"""
        try:
            with self.neo4j_driver.session() as session:
                # Run Cypher query
                result = session.run(query)
                
                # Process results
                records = []
                for record in result:
                    records.append(dict(record))
                
                # Get AI analysis of graph data
                graph_context = f"Knowledge Graph Query Results: {json.dumps(records, indent=2)}"
                ai_result = self.query_ai(f"Analyze this knowledge graph data: {graph_context}")
            
            return {
                    'graph_data': records,
                    'ai_analysis': ai_result,
                    'query': query
            }
            
        except Exception as e:
            logger.error(f"❌ Graph insights failed: {e}")
            raise
    
    def health_check(self) -> Dict:
        """Check system health"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        # Check OpenAI
        try:
            if openai.api_key:
                health_status['services']['openai'] = 'connected'
            else:
                health_status['services']['openai'] = 'not_configured'
        except:
            health_status['services']['openai'] = 'error'
        
        # Check Qdrant
        try:
            self.qdrant_client.get_collections()
            health_status['services']['qdrant'] = 'connected'
        except:
            health_status['services']['qdrant'] = 'error'
        
        # Check Neo4j
        try:
            with self.neo4j_driver.session() as session:
                session.run("RETURN 1")
            health_status['services']['neo4j'] = 'connected'
        except:
            health_status['services']['neo4j'] = 'error'
        
        # Overall status
        if 'error' in health_status['services'].values():
            health_status['status'] = 'degraded'
        
        return health_status
    
    def close(self):
        """Close connections"""
        try:
            self.neo4j_driver.close()
            logger.info("✅ Connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing connections: {e}")

# Global RAG system instance
_rag_system_instance = None

def get_rag_system(config_path: str = "src/config/config_enhanced_rag.yaml") -> "EnhancedRAGSystem":
    """Get or create a singleton instance of the RAG system"""
    global _rag_system_instance
    if _rag_system_instance is None:
        _rag_system_instance = EnhancedRAGSystem(config_path)
        logger.info("✅ Enhanced RAG system initialized")
    return _rag_system_instance

class EnhancedRAGSystem(AASXDigitalTwinRAG):
    """Enhanced RAG system with additional features for web interface"""
    
    def __init__(self, config_path: str = "src/config/config_enhanced_rag.yaml"):
        """Initialize the enhanced RAG system"""
        super().__init__(config_path)
        
        # Initialize additional attributes
        self.openai_client = openai
        self.use_local_embeddings = self.config.get('embeddings', {}).get('use_local', False)
        
        # Initialize local embedding model if needed
        if self.use_local_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                model_name = self.config.get('embeddings', {}).get('model', 'all-MiniLM-L6-v2')
                self.local_embedding_model = SentenceTransformer(model_name)
                logger.info(f"✅ Local embedding model loaded: {model_name}")
            except ImportError:
                logger.warning("⚠️  sentence-transformers not available, falling back to OpenAI")
                self.use_local_embeddings = False
                self.local_embedding_model = None
        
        self._setup_enhanced_features()
    
    def _setup_enhanced_features(self):
        """Setup enhanced features"""
        logger.info("🔧 Setting up enhanced RAG features")
    
    async def generate_rag_response(self, query: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Generate a comprehensive RAG response for web interface"""
        try:
            # Get relevant context from vector search
            context_docs = self.search_similar(query)
            
            # Get additional context from Neo4j if available
            graph_context = await self._get_graph_context(query)
            
            # Combine contexts
            combined_context = self._combine_contexts(context_docs, graph_context)
            
            # Generate AI response
            ai_response = self.query_ai(query, context_docs)
            
            # Enhance response with analysis type
            enhanced_response = {
                'analysis': ai_response['answer'],
                'context': [doc['content'] for doc in context_docs],
                'sources': [doc['metadata'] for doc in context_docs],
                'confidence': self._calculate_confidence(context_docs),
                'analysis_type': analysis_type,
                'graph_context': graph_context,
                'model': ai_response['model'],
                'usage': ai_response['usage'],
                'timestamp': ai_response['timestamp']
            }
            
            logger.info(f"✅ Generated enhanced RAG response for '{analysis_type}' analysis")
            return enhanced_response
            
        except Exception as e:
            logger.error(f"❌ Enhanced RAG response generation failed: {e}")
            raise
    
    async def _get_graph_context(self, query: str) -> Dict[str, Any]:
        """Get relevant context from Neo4j knowledge graph"""
        try:
            # Simple graph query to get asset information
            graph_query = """
            MATCH (n)
            WHERE n.type = "asset" OR n.type = "submodel"
            RETURN n.id as id, n.type as type, n.properties as properties
            LIMIT 10
            """
            
            with self.neo4j_driver.session() as session:
                result = session.run(graph_query)
                records = [dict(record) for record in result]
            
            return {
                'graph_data': records,
                'query': graph_query,
                'count': len(records)
            }
            
        except Exception as e:
            logger.warning(f"⚠️  Graph context retrieval failed: {e}")
            return {'graph_data': [], 'query': '', 'count': 0}
    
    def _combine_contexts(self, vector_docs: List[Dict], graph_context: Dict) -> str:
        """Combine vector search and graph context"""
        combined = []
        
        # Add vector search results
        for doc in vector_docs:
            combined.append(f"Vector Result: {doc['content']}")
        
        # Add graph context
        if graph_context.get('graph_data'):
            combined.append("Knowledge Graph Data:")
            for record in graph_context['graph_data']:
                combined.append(f"- {record['type']}: {record['id']}")
        
        return "\n\n".join(combined)
    
    def _calculate_confidence(self, context_docs: List[Dict]) -> float:
        """Calculate confidence score based on context relevance"""
        if not context_docs:
            return 0.0
        
        # Average similarity scores
        scores = [doc['score'] for doc in context_docs]
        avg_score = sum(scores) / len(scores)
        
        # Normalize to 0-1 range
        confidence = min(1.0, avg_score * 2)  # Assuming scores are typically 0-0.5
        
        return round(confidence, 3)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            stats = {
                'collections_count': 0,
                'total_points': 0,
                'assets_count': 0,
                'submodels_count': 0,
                'last_indexed': None,
                'neo4j_status': 'unknown',
                'qdrant_status': 'unknown',
                'openai_status': 'unknown'
            }
            
            # Get Qdrant stats
            try:
                collections = self.qdrant_client.get_collections()
                stats['collections_count'] = len(collections.collections)
                
                # Get points count for main collection
                collection_name = self.config['qdrant']['collection_name']
                collection_info = self.qdrant_client.get_collection(collection_name)
                stats['total_points'] = collection_info.points_count
                stats['qdrant_status'] = 'connected'
            except Exception as e:
                logger.warning(f"⚠️  Qdrant stats failed: {e}")
                stats['qdrant_status'] = 'error'
            
            # Get Neo4j stats
            try:
                with self.neo4j_driver.session() as session:
                    # Count assets
                    result = session.run("MATCH (n) WHERE n.type = 'asset' RETURN count(n) as count")
                    stats['assets_count'] = result.single()['count']
                    
                    # Count submodels
                    result = session.run("MATCH (n) WHERE n.type = 'submodel' RETURN count(n) as count")
                    stats['submodels_count'] = result.single()['count']
                    
                stats['neo4j_status'] = 'connected'
            except Exception as e:
                logger.warning(f"⚠️  Neo4j stats failed: {e}")
                stats['neo4j_status'] = 'error'
            
            # Check OpenAI
            try:
                if openai.api_key:
                    stats['openai_status'] = 'configured'
                else:
                    stats['openai_status'] = 'not_configured'
            except:
                stats['openai_status'] = 'error'
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ System stats failed: {e}")
            raise
    
    def get_collections_info(self) -> List[Dict[str, Any]]:
        """Get information about available collections"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_info = []
            
            for collection in collections.collections:
                info = {
                    'name': collection.name,
                    'points_count': collection.points_count,
                    'description': f"Collection with {collection.points_count} points"
                }
                collection_info.append(info)
            
            return collection_info
            
        except Exception as e:
            logger.error(f"❌ Collections info failed: {e}")
            return []
    
    async def index_etl_data(self, data_path: str = "output/etl_results") -> Dict[str, Any]:
        """Index ETL data into the vector database by migrating from ChromaDB"""
        try:
            if not self.migration_manager:
                raise ValueError("Data migration manager not available")
            
            # Check migration status
            migration_status = self.migration_manager.get_migration_status()
            
            if not migration_status.get('migration_needed', False):
                logger.info("✅ No migration needed - data already synchronized")
                return {
                    'status': 'success',
                    'message': 'Data already synchronized',
                    'migration_needed': False,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Perform migration
            logger.info("🔄 Starting data migration from ETL pipeline to AI/RAG system")
            migration_result = self.migration_manager.migrate_all_collections()
            
            if migration_result['status'] == 'completed':
                logger.info(f"✅ Data migration completed: {migration_result['migrated_collections']} collections")
                return {
                    'status': 'success',
                    'message': 'Data migration completed successfully',
                    'migration_result': migration_result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Data migration failed: {migration_result.get('error', 'Unknown error')}")
                return {
                    'status': 'failed',
                    'message': 'Data migration failed',
                    'migration_result': migration_result,
                    'timestamp': datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"❌ ETL data indexing failed: {e}")
            raise
    
    async def search_aasx_data(self, query: str, collection: str = "aasx_assets", limit: int = 5) -> List[Dict[str, Any]]:
        """Search AASX data using vector similarity"""
        try:
            # Get embedding for query
            query_embedding = self._get_embedding(query)
            
            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=collection,
                query_vector=query_embedding,
                limit=limit
            )
            
            # Format results
            results = []
            for point in search_result:
                results.append({
                    'id': point.id,
                    'score': point.score,
                    'payload': point.payload
                })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Vector search failed: {e}")
            return []
    
    async def sync_etl_data(self) -> Dict[str, Any]:
        """Synchronize data from ETL pipeline to AI/RAG system"""
        try:
            if not self.migration_manager:
                return {
                    'status': 'error',
                    'message': 'Data migration manager not available',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check current status
            status = self.migration_manager.get_migration_status()
            
            if not status.get('migration_needed', False):
                return {
                    'status': 'success',
                    'message': 'Data already synchronized',
                    'details': status,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Perform migration
            result = self.migration_manager.migrate_all_collections()
            
            return {
                'status': 'success' if result['status'] == 'completed' else 'failed',
                'message': f"Migration {result['status']}",
                'details': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Data synchronization failed: {e}")
            return {
                'status': 'error',
                'message': f'Data synchronization failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_data_status(self) -> Dict[str, Any]:
        """Get status of data in both ETL pipeline and AI/RAG system"""
        try:
            if not self.migration_manager:
                return {
                    'status': 'error',
                    'message': 'Data migration manager not available',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Get migration status
            migration_status = self.migration_manager.get_migration_status()
            
            # Get collection details
            chroma_collections = self.migration_manager.get_chromadb_collections()
            qdrant_collections = self.migration_manager.get_qdrant_collections()
            
            return {
                'status': 'success',
                'etl_pipeline': {
                    'collections': chroma_collections,
                    'collection_count': len(chroma_collections)
                },
                'ai_rag_system': {
                    'collections': qdrant_collections,
                    'collection_count': len(qdrant_collections)
                },
                'migration': migration_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get data status: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get data status: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

# Example usage
if __name__ == "__main__":
    # Initialize RAG system
    rag = AASXDigitalTwinRAG()
    
    # Example queries
    queries = [
        "What are the quality metrics for the additive manufacturing facility?",
        "What are the main risks in the hydrogen filling station?",
        "How can we optimize the performance of the 3D printer?",
        "Provide a general overview of the digital twin assets"
    ]
    
    # Run queries
    for query in queries:
        print(f"\n🔍 Query: {query}")
        try:
            result = rag.query_ai(query)
            print(f"🤖 Answer: {result['answer'][:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Health check
    health = rag.health_check()
    print(f"\n🏥 Health Status: {health}")
    
    rag.close() 