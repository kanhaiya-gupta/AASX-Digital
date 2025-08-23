"""
AI RAG Integration
==================

Integration with AI Retrieval-Augmented Generation for federated learning.
Handles document processing, vector embeddings, semantic search, and AI-powered insights.
"""

import asyncio
import json
import hashlib
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class AIRAGConfig:
    """Configuration for AI RAG integration"""
    # Integration settings
    auto_processing_enabled: bool = True
    embedding_generation_enabled: bool = True
    semantic_search_enabled: bool = True
    ai_generation_enabled: bool = True
    
    # Document processing settings
    supported_formats: List[str] = None
    max_document_size_mb: int = 50
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_chunks_per_document: int = 100
    
    # Embedding settings
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimensions: int = 1536
    batch_size: int = 32
    similarity_threshold: float = 0.7
    
    # Vector database settings
    vector_db_type: str = "in_memory"  # in_memory, pinecone, weaviate, etc.
    index_type: str = "hnsw"  # hnsw, ivf, flat
    max_results: int = 10
    
    # AI generation settings
    generation_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 0.9
    
    # Caching settings
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    max_cache_size: int = 1000
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.txt', '.md', '.pdf', '.docx', '.json', '.xml']


@dataclass
class AIRAGMetrics:
    """Metrics for AI RAG integration"""
    # Document processing metrics
    documents_processed: int = 0
    documents_failed: int = 0
    chunks_created: int = 0
    processing_time: float = 0.0
    
    # Embedding metrics
    embeddings_generated: int = 0
    embedding_generation_time: float = 0.0
    embedding_errors: int = 0
    
    # Search metrics
    searches_performed: int = 0
    search_time: float = 0.0
    average_results_per_search: float = 0.0
    
    # AI generation metrics
    generations_created: int = 0
    generation_time: float = 0.0
    generation_errors: int = 0
    
    # Vector database metrics
    vectors_stored: int = 0
    index_size_mb: float = 0.0
    query_cache_hits: int = 0
    query_cache_misses: int = 0
    
    # Performance metrics
    average_processing_time: float = 0.0
    memory_usage_mb: float = 0.0


class AIRAGIntegration:
    """Integration with AI Retrieval-Augmented Generation for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[AIRAGConfig] = None
    ):
        """Initialize AI RAG Integration"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or AIRAGConfig()
        
        # Integration state
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.chunks: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        self.vector_index: Dict[str, Any] = {}
        
        # Processing state
        self.processing_active = False
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task = None
        
        # AI models state
        self.embedding_model_loaded = False
        self.generation_model_loaded = False
        
        # Query cache
        self.query_cache: Dict[str, Dict[str, Any]] = {}
        
        # Metrics tracking
        self.metrics = AIRAGMetrics()
        
        # Background tasks
        self.cleanup_task = None
        self.cleanup_active = False
    
    async def start_integration(self):
        """Start the AI RAG integration"""
        try:
            print("🚀 Starting AI RAG Integration...")
            
            # Initialize AI models
            await self._initialize_ai_models()
            
            # Initialize vector database
            await self._initialize_vector_database()
            
            # Start document processing if enabled
            if self.config.auto_processing_enabled:
                await self.start_document_processing()
            
            # Start cleanup task
            await self._start_cleanup_task()
            
            print("✅ AI RAG Integration started successfully")
            
        except Exception as e:
            print(f"❌ Failed to start AI RAG Integration: {e}")
            raise
    
    async def stop_integration(self):
        """Stop the AI RAG integration"""
        try:
            print("🛑 Stopping AI RAG Integration...")
            
            # Stop document processing
            if self.processing_active:
                await self.stop_document_processing()
            
            # Stop cleanup task
            if self.cleanup_active:
                await self._stop_cleanup_task()
            
            print("✅ AI RAG Integration stopped successfully")
            
        except Exception as e:
            print(f"❌ Failed to stop AI RAG Integration: {e}")
            raise
    
    async def _initialize_ai_models(self):
        """Initialize AI models for embeddings and generation"""
        try:
            print("🤖 Initializing AI models...")
            
            # Simulate model loading
            await asyncio.sleep(0.5)  # Simulate model loading time
            
            # Mock model initialization
            self.embedding_model_loaded = True
            self.generation_model_loaded = True
            
            print("✅ AI models initialized successfully")
            
        except Exception as e:
            print(f"❌ AI model initialization failed: {e}")
            raise
    
    async def _initialize_vector_database(self):
        """Initialize vector database for embeddings"""
        try:
            print(f"🗄️  Initializing vector database: {self.config.vector_db_type}")
            
            # Simulate vector database initialization
            await asyncio.sleep(0.3)  # Simulate initialization time
            
            # Create in-memory vector index
            self.vector_index = {
                'type': self.config.vector_db_type,
                'index_type': self.config.index_type,
                'dimensions': self.config.embedding_dimensions,
                'vectors': {},
                'metadata': {},
                'created_at': datetime.now().isoformat()
            }
            
            print("✅ Vector database initialized successfully")
            
        except Exception as e:
            print(f"❌ Vector database initialization failed: {e}")
            raise
    
    async def start_document_processing(self):
        """Start automatic document processing"""
        try:
            if self.processing_active:
                print("⚠️  Document processing already active")
                return
            
            self.processing_active = True
            self.processing_task = asyncio.create_task(self._document_processing_loop())
            print("📄 Document processing started")
            
        except Exception as e:
            print(f"❌ Failed to start document processing: {e}")
            self.processing_active = False
    
    async def stop_document_processing(self):
        """Stop automatic document processing"""
        try:
            if not self.processing_active:
                return
            
            self.processing_active = False
            
            if self.processing_task and not self.processing_task.done():
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            print("📄 Document processing stopped")
            
        except Exception as e:
            print(f"❌ Failed to stop document processing: {e}")
    
    async def _document_processing_loop(self):
        """Main document processing loop"""
        try:
            while self.processing_active:
                try:
                    # Process documents from queue
                    while not self.processing_queue.empty():
                        document_data = await asyncio.wait_for(
                            self.processing_queue.get(), 
                            timeout=1.0
                        )
                        await self._process_document(document_data)
                        self.processing_queue.task_done()
                    
                    await asyncio.sleep(1)  # Small delay to prevent busy waiting
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Document processing loop error: {e}")
                    
        except asyncio.CancelledError:
            print("📄 Document processing loop cancelled")
        except Exception as e:
            print(f"❌ Document processing loop error: {e}")
            self.processing_active = False
    
    async def _start_cleanup_task(self):
        """Start background cleanup task"""
        try:
            if self.cleanup_active:
                return
            
            self.cleanup_active = True
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            print("🧹 AI RAG cleanup task started")
            
        except Exception as e:
            print(f"❌ Failed to start cleanup task: {e}")
            self.cleanup_active = False
    
    async def _stop_cleanup_task(self):
        """Stop background cleanup task"""
        try:
            if not self.cleanup_active:
                return
            
            self.cleanup_active = False
            
            if self.cleanup_task and not self.cleanup_task.done():
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            print("🧹 AI RAG cleanup task stopped")
            
        except Exception as e:
            print(f"❌ Failed to stop cleanup task: {e}")
    
    async def _cleanup_loop(self):
        """Main cleanup loop"""
        try:
            while self.cleanup_active:
                await self._perform_cleanup()
                await asyncio.sleep(3600)  # Run every hour
                
        except asyncio.CancelledError:
            print("🧹 Cleanup loop cancelled")
        except Exception as e:
            print(f"❌ Cleanup loop error: {e}")
            self.cleanup_active = False
    
    async def _perform_cleanup(self):
        """Perform AI RAG cleanup"""
        try:
            print("🧹 Performing AI RAG cleanup...")
            
            # Clean up expired query cache
            await self._cleanup_query_cache()
            
            # Update metrics
            await self._update_metrics()
            
            print("✅ AI RAG cleanup completed")
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
    
    async def _cleanup_query_cache(self):
        """Clean up expired query cache entries"""
        try:
            if not self.config.cache_enabled:
                return
            
            current_time = datetime.now()
            expired_keys = []
            
            for key, entry in self.query_cache.items():
                if current_time > entry['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.query_cache[key]
            
            print(f"🗑️  Cleaned up {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            print(f"⚠️  Query cache cleanup failed: {e}")
    
    async def _update_metrics(self):
        """Update integration metrics"""
        try:
            # Update vector database metrics
            self.metrics.vectors_stored = len(self.embeddings)
            self.metrics.index_size_mb = len(self.vector_index) * 0.001  # Rough estimate
            
        except Exception as e:
            print(f"⚠️  Metrics update failed: {e}")
    
    async def add_document(self, document_path: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the AI RAG system"""
        try:
            print(f"📄 Adding document: {document_path}")
            
            # Generate document ID
            document_id = hashlib.md5(document_path.encode()).hexdigest()
            
            # Prepare document data
            document_data = {
                'id': document_id,
                'path': document_path,
                'metadata': metadata or {},
                'status': 'pending',
                'added_at': datetime.now().isoformat()
            }
            
            # Add to processing queue
            await self.processing_queue.put(document_data)
            
            # Store document metadata
            self.documents[document_id] = document_data
            
            print(f"✅ Document {document_id} added to processing queue")
            return document_id
            
        except Exception as e:
            print(f"❌ Failed to add document: {e}")
            raise
    
    async def _process_document(self, document_data: Dict[str, Any]):
        """Process a single document"""
        try:
            start_time = datetime.now()
            document_id = document_data['id']
            
            print(f"🔄 Processing document: {document_id}")
            
            # Update document status
            self.documents[document_id]['status'] = 'processing'
            
            # Read and chunk document
            chunks = await self._chunk_document(document_data)
            if not chunks:
                self.documents[document_id]['status'] = 'failed'
                self.metrics.documents_failed += 1
                return
            
            # Generate embeddings for chunks
            if self.config.embedding_generation_enabled:
                await self._generate_chunk_embeddings(document_id, chunks)
            
            # Update document status
            self.documents[document_id]['status'] = 'completed'
            self.documents[document_id]['chunks_count'] = len(chunks)
            self.documents[document_id]['processed_at'] = datetime.now().isoformat()
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics.processing_time = processing_time
            self.metrics.documents_processed += 1
            self.metrics.chunks_created += len(chunks)
            
            # Update average processing time
            total_docs = self.metrics.documents_processed
            current_avg = self.metrics.average_processing_time
            self.metrics.average_processing_time = ((current_avg * (total_docs - 1)) + processing_time) / total_docs
            
            print(f"✅ Document {document_id} processed successfully in {processing_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Failed to process document {document_data.get('id', 'unknown')}: {e}")
            self.documents[document_data.get('id', 'unknown')]['status'] = 'failed'
            self.metrics.documents_failed += 1
    
    async def _chunk_document(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk document into smaller pieces"""
        try:
            document_path = document_data['path']
            document_id = document_data['id']
            
            # Simulate document reading and chunking
            # In practice, this would read the actual file and split it
            
            await asyncio.sleep(0.2)  # Simulate processing time
            
            # Generate mock chunks
            chunks = []
            for i in range(3):  # Generate 3 mock chunks
                chunk_id = f"{document_id}_chunk_{i}"
                chunk = {
                    'id': chunk_id,
                    'document_id': document_id,
                    'content': f"This is mock chunk {i} content for document {document_id}",
                    'chunk_index': i,
                    'start_position': i * self.config.chunk_size,
                    'end_position': (i + 1) * self.config.chunk_size,
                    'created_at': datetime.now().isoformat()
                }
                chunks.append(chunk)
                
                # Store chunk
                self.chunks[chunk_id] = chunk
            
            return chunks
            
        except Exception as e:
            print(f"❌ Document chunking failed: {e}")
            return []
    
    async def _generate_chunk_embeddings(self, document_id: str, chunks: List[Dict[str, Any]]):
        """Generate embeddings for document chunks"""
        try:
            print(f"🧠 Generating embeddings for {len(chunks)} chunks")
            
            start_time = datetime.now()
            
            # Simulate embedding generation
            # In practice, this would use the actual embedding model
            
            for chunk in chunks:
                chunk_id = chunk['id']
                
                # Generate mock embedding vector
                embedding_vector = np.random.randn(self.config.embedding_dimensions)
                embedding_vector = embedding_vector / np.linalg.norm(embedding_vector)  # Normalize
                
                # Store embedding
                self.embeddings[chunk_id] = embedding_vector
                
                # Add to vector index
                self.vector_index['vectors'][chunk_id] = {
                    'vector': embedding_vector.tolist(),
                    'metadata': {
                        'document_id': document_id,
                        'chunk_id': chunk_id,
                        'chunk_index': chunk['chunk_index']
                    }
                }
            
            # Update metrics
            embedding_time = (datetime.now() - start_time).total_seconds()
            self.metrics.embedding_generation_time = embedding_time
            self.metrics.embeddings_generated += len(chunks)
            
            print(f"✅ Generated {len(chunks)} embeddings in {embedding_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            self.metrics.embedding_errors += 1
    
    async def semantic_search(
        self, 
        query: str, 
        max_results: int = None,
        similarity_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search using embeddings"""
        try:
            if max_results is None:
                max_results = self.config.max_results
            if similarity_threshold is None:
                similarity_threshold = self.config.similarity_threshold
            
            start_time = datetime.now()
            
            print(f"🔍 Performing semantic search: '{query}' (max results: {max_results})")
            
            # Check cache first
            if self.config.cache_enabled:
                cache_key = f"search_{hash(query)}_{max_results}_{similarity_threshold}"
                if cache_key in self.query_cache:
                    cache_entry = self.query_cache[cache_key]
                    if datetime.now() < cache_entry['expires_at']:
                        self.metrics.query_cache_hits += 1
                        print("✅ Search result retrieved from cache")
                        return cache_entry['result']
            
            # Generate query embedding
            query_embedding = await self._generate_query_embedding(query)
            
            # Perform similarity search
            search_results = await self._perform_similarity_search(
                query_embedding, max_results, similarity_threshold
            )
            
            # Cache result if caching is enabled
            if self.config.cache_enabled:
                cache_key = f"search_{hash(query)}_{max_results}_{similarity_threshold}"
                self.query_cache[cache_key] = {
                    'result': search_results,
                    'cached_at': datetime.now(),
                    'expires_at': datetime.now() + timedelta(hours=self.config.cache_ttl_hours)
                }
            
            # Update metrics
            search_time = (datetime.now() - start_time).total_seconds()
            self.metrics.search_time = search_time
            self.metrics.searches_performed += 1
            self.metrics.query_cache_misses += 1
            
            # Update average results per search
            if search_results:
                total_results = sum(len(result.get('chunks', [])) for result in search_results)
                self.metrics.average_results_per_search = total_results / len(search_results)
            
            print(f"✅ Semantic search completed in {search_time:.2f}s")
            return search_results
            
        except Exception as e:
            print(f"❌ Semantic search failed: {e}")
            return []
    
    async def _generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for search query"""
        try:
            # Simulate query embedding generation
            # In practice, this would use the actual embedding model
            
            await asyncio.sleep(0.1)  # Simulate embedding time
            
            # Generate mock embedding vector
            embedding_vector = np.random.randn(self.config.embedding_dimensions)
            embedding_vector = embedding_vector / np.linalg.norm(embedding_vector)  # Normalize
            
            return embedding_vector
            
        except Exception as e:
            print(f"❌ Query embedding generation failed: {e}")
            raise
    
    async def _perform_similarity_search(
        self, 
        query_embedding: np.ndarray, 
        max_results: int, 
        similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """Perform similarity search in vector database"""
        try:
            # Simulate similarity search
            # In practice, this would use vector similarity algorithms
            
            await asyncio.sleep(0.2)  # Simulate search time
            
            # Calculate similarities with all stored embeddings
            similarities = []
            for chunk_id, embedding in self.embeddings.items():
                similarity = np.dot(query_embedding, embedding)
                if similarity >= similarity_threshold:
                    similarities.append((chunk_id, similarity))
            
            # Sort by similarity and take top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_similarities = similarities[:max_results]
            
            # Format results
            search_results = []
            for chunk_id, similarity in top_similarities:
                chunk = self.chunks.get(chunk_id, {})
                document = self.documents.get(chunk.get('document_id', ''), {})
                
                result = {
                    'chunk_id': chunk_id,
                    'document_id': chunk.get('document_id'),
                    'similarity_score': float(similarity),
                    'content': chunk.get('content', ''),
                    'metadata': {
                        'document_path': document.get('path', ''),
                        'chunk_index': chunk.get('chunk_index', 0),
                        'document_metadata': document.get('metadata', {})
                    }
                }
                search_results.append(result)
            
            return search_results
            
        except Exception as e:
            print(f"❌ Similarity search failed: {e}")
            return []
    
    async def generate_ai_response(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]] = None,
        max_tokens: int = None
    ) -> Optional[str]:
        """Generate AI response using RAG"""
        try:
            if max_tokens is None:
                max_tokens = self.config.max_tokens
            
            start_time = datetime.now()
            
            print(f"🤖 Generating AI response for query: '{query[:50]}...'")
            
            # If no context provided, perform semantic search
            if context_chunks is None:
                context_chunks = await self.semantic_search(query, max_results=5)
                if not context_chunks:
                    print("⚠️  No relevant context found for AI generation")
                    return None
            
            # Prepare context for AI model
            context_text = self._prepare_context_for_ai(context_chunks)
            
            # Generate AI response
            ai_response = await self._call_ai_generation_model(query, context_text, max_tokens)
            
            # Update metrics
            generation_time = (datetime.now() - start_time).total_seconds()
            self.metrics.generation_time = generation_time
            self.metrics.generations_created += 1
            
            print(f"✅ AI response generated in {generation_time:.2f}s")
            return ai_response
            
        except Exception as e:
            print(f"❌ AI response generation failed: {e}")
            self.metrics.generation_errors += 1
            return None
    
    def _prepare_context_for_ai(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context chunks for AI model input"""
        try:
            context_parts = []
            
            for chunk in context_chunks:
                content = chunk.get('content', '')
                metadata = chunk.get('metadata', {})
                
                # Add chunk with metadata
                chunk_text = f"[Document: {metadata.get('document_path', 'Unknown')}]\n{content}\n"
                context_parts.append(chunk_text)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"⚠️  Context preparation failed: {e}")
            return ""
    
    async def _call_ai_generation_model(
        self, 
        query: str, 
        context: str, 
        max_tokens: int
    ) -> str:
        """Call AI generation model with query and context"""
        try:
            # Simulate AI model call
            # In practice, this would use the actual AI model API
            
            await asyncio.sleep(0.5)  # Simulate AI generation time
            
            # Generate mock AI response
            prompt = f"Query: {query}\n\nContext:\n{context}\n\nResponse:"
            
            # Mock response based on query type
            if 'federated' in query.lower():
                response = "Based on the federated learning context, here's a comprehensive response..."
            elif 'algorithm' in query.lower():
                response = "The algorithm analysis shows optimal performance with the following parameters..."
            elif 'performance' in query.lower():
                response = "Performance metrics indicate the following improvements can be made..."
            else:
                response = "Based on the provided context, here's a detailed analysis and response..."
            
            return response
            
        except Exception as e:
            print(f"❌ AI model call failed: {e}")
            raise
    
    async def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific document"""
        try:
            return self.documents.get(document_id)
            
        except Exception as e:
            print(f"❌ Failed to get document info: {e}")
            return None
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the system"""
        try:
            return list(self.documents.values())
            
        except Exception as e:
            print(f"❌ Failed to get all documents: {e}")
            return []
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            return [
                chunk for chunk in self.chunks.values()
                if chunk.get('document_id') == document_id
            ]
            
        except Exception as e:
            print(f"❌ Failed to get document chunks: {e}")
            return []
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status and metrics"""
        try:
            return {
                'ai_models_loaded': {
                    'embedding_model': self.embedding_model_loaded,
                    'generation_model': self.generation_model_loaded
                },
                'vector_database': {
                    'type': self.vector_index.get('type'),
                    'vectors_stored': len(self.embeddings),
                    'index_size_mb': self.metrics.index_size_mb
                },
                'processing_active': self.processing_active,
                'queue_size': self.processing_queue.qsize(),
                'documents_count': len(self.documents),
                'chunks_count': len(self.chunks),
                'cache_size': len(self.query_cache),
                'metrics': self.metrics.__dict__
            }
            
        except Exception as e:
            print(f"❌ Failed to get integration status: {e}")
            return {'error': str(e)}
    
    async def clear_cache(self):
        """Clear the query cache"""
        try:
            self.query_cache.clear()
            print("🗑️  Query cache cleared")
            
        except Exception as e:
            print(f"❌ Failed to clear cache: {e}")
    
    async def reset_metrics(self):
        """Reset integration metrics"""
        try:
            self.metrics = AIRAGMetrics()
            print("🔄 Integration metrics reset")
            
        except Exception as e:
            print(f"❌ Failed to reset metrics: {e}")

