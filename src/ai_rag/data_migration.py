"""
Data Migration Module for AI/RAG System
Transfers data from ETL pipeline's ChromaDB to AI/RAG system's Qdrant
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Vector database imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Migration features disabled.")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant not available. Migration features disabled.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("Sentence Transformers not available. Migration features disabled.")

logger = logging.getLogger(__name__)

class DataMigrationManager:
    """Manages data migration from ETL pipeline to AI/RAG system"""
    
    def __init__(self, 
                 chromadb_path: str = "output/vector_db",
                 qdrant_url: str = "http://localhost:6333",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize the migration manager"""
        self.chromadb_path = Path(chromadb_path)
        self.qdrant_url = qdrant_url
        self.embedding_model_name = embedding_model
        
        # Initialize clients
        self.chromadb_client = None
        self.qdrant_client = None
        self.embedding_model = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize ChromaDB and Qdrant clients"""
        try:
            # Initialize ChromaDB client
            if CHROMADB_AVAILABLE and self.chromadb_path.exists():
                self.chromadb_client = chromadb.PersistentClient(
                    path=str(self.chromadb_path),
                    settings=Settings(anonymized_telemetry=False)
                )
                logger.info(f"✅ ChromaDB client initialized from {self.chromadb_path}")
            else:
                logger.info(f"ℹ️  ChromaDB path not found: {self.chromadb_path} (this is normal for new installations)")
            
            # Initialize Qdrant client
            if QDRANT_AVAILABLE:
                self.qdrant_client = QdrantClient(
                    url=self.qdrant_url,
                    timeout=30
                )
                logger.info(f"✅ Qdrant client initialized at {self.qdrant_url}")
            else:
                logger.warning("❌ Qdrant not available")
            
            # Initialize embedding model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                logger.info(f"✅ Embedding model loaded: {self.embedding_model_name}")
            else:
                logger.warning("❌ Sentence Transformers not available")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize clients: {e}")
            raise
    
    def get_chromadb_collections(self) -> List[str]:
        """Get list of available ChromaDB collections"""
        if not self.chromadb_client:
            return []
        
        try:
            collections = self.chromadb_client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"❌ Failed to get ChromaDB collections: {e}")
            return []
    
    def get_qdrant_collections(self) -> List[str]:
        """Get list of available Qdrant collections"""
        if not self.qdrant_client:
            return []
        
        try:
            collections = self.qdrant_client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"❌ Failed to get Qdrant collections: {e}")
            return []
    
    def migrate_collection(self, collection_name: str, 
                          vector_size: int = 384,
                          distance: Distance = Distance.COSINE) -> Dict[str, Any]:
        """Migrate a single collection from ChromaDB to Qdrant"""
        if not self.chromadb_client or not self.qdrant_client:
            raise ValueError("Both ChromaDB and Qdrant clients must be available")
        
        try:
            logger.info(f"🔄 Starting migration of collection: {collection_name}")
            
            # Get ChromaDB collection
            chroma_collection = self.chromadb_client.get_collection(collection_name)
            
            # Get all data from ChromaDB
            chroma_data = chroma_collection.get()
            
            if not chroma_data['ids']:
                logger.warning(f"⚠️ Collection {collection_name} is empty")
                return {
                    'collection': collection_name,
                    'status': 'empty',
                    'migrated_points': 0,
                    'errors': []
                }
            
            # Create Qdrant collection if it doesn't exist
            qdrant_collections = self.qdrant_client.get_collections()
            qdrant_collection_names = [c.name for c in qdrant_collections.collections]
            
            if collection_name not in qdrant_collection_names:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=distance
                    )
                )
                logger.info(f"✅ Created Qdrant collection: {collection_name}")
            
            # Prepare points for Qdrant
            points = []
            errors = []
            
            for i, (doc_id, embedding, document, metadata) in enumerate(zip(
                chroma_data['ids'],
                chroma_data['embeddings'],
                chroma_data['documents'],
                chroma_data['metadatas']
            )):
                try:
                    # Ensure embedding is the right size
                    if len(embedding) != vector_size:
                        if self.embedding_model and document:
                            # Re-generate embedding if size mismatch
                            embedding = self.embedding_model.encode(document).tolist()
                        else:
                            # Pad or truncate embedding
                            if len(embedding) > vector_size:
                                embedding = embedding[:vector_size]
                            else:
                                embedding.extend([0.0] * (vector_size - len(embedding)))
                    
                    point = PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload={
                            "content": document,
                            "metadata": metadata or {},
                            "migrated_at": datetime.now().isoformat(),
                            "source": "chromadb_migration"
                        }
                    )
                    points.append(point)
                    
                except Exception as e:
                    error_msg = f"Error processing document {doc_id}: {e}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
            
            # Upload points to Qdrant
            if points:
                self.qdrant_client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                logger.info(f"✅ Uploaded {len(points)} points to Qdrant collection: {collection_name}")
            
            return {
                'collection': collection_name,
                'status': 'completed',
                'migrated_points': len(points),
                'total_points': len(chroma_data['ids']),
                'errors': errors,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate collection {collection_name}: {e}")
            return {
                'collection': collection_name,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def migrate_all_collections(self, vector_size: int = 384) -> Dict[str, Any]:
        """Migrate all available ChromaDB collections to Qdrant"""
        if not self.chromadb_client or not self.qdrant_client:
            raise ValueError("Both ChromaDB and Qdrant clients must be available")
        
        try:
            logger.info("🔄 Starting migration of all collections")
            
            # Get all ChromaDB collections
            chroma_collections = self.get_chromadb_collections()
            
            if not chroma_collections:
                logger.warning("⚠️ No ChromaDB collections found")
                return {
                    'status': 'no_collections',
                    'migrated_collections': 0,
                    'total_collections': 0,
                    'results': []
                }
            
            # Migrate each collection
            results = []
            successful_migrations = 0
            
            for collection_name in chroma_collections:
                result = self.migrate_collection(collection_name, vector_size)
                results.append(result)
                
                if result['status'] == 'completed':
                    successful_migrations += 1
            
            logger.info(f"✅ Migration completed: {successful_migrations}/{len(chroma_collections)} collections")
            
            return {
                'status': 'completed',
                'migrated_collections': successful_migrations,
                'total_collections': len(chroma_collections),
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate collections: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def verify_migration(self, collection_name: str) -> Dict[str, Any]:
        """Verify that migration was successful by comparing collection stats"""
        try:
            # Get ChromaDB stats
            chroma_stats = {
                'points_count': 0,
                'available': False
            }
            
            if self.chromadb_client:
                try:
                    chroma_collection = self.chromadb_client.get_collection(collection_name)
                    chroma_data = chroma_collection.get()
                    chroma_stats['points_count'] = len(chroma_data['ids'])
                    chroma_stats['available'] = True
                except Exception as e:
                    logger.warning(f"Could not get ChromaDB stats for {collection_name}: {e}")
            
            # Get Qdrant stats
            qdrant_stats = {
                'points_count': 0,
                'available': False
            }
            
            if self.qdrant_client:
                try:
                    qdrant_collection = self.qdrant_client.get_collection(collection_name)
                    qdrant_stats['points_count'] = qdrant_collection.points_count
                    qdrant_stats['available'] = True
                except Exception as e:
                    logger.warning(f"Could not get Qdrant stats for {collection_name}: {e}")
            
            # Compare stats
            migration_successful = (
                chroma_stats['available'] and 
                qdrant_stats['available'] and
                chroma_stats['points_count'] == qdrant_stats['points_count']
            )
            
            return {
                'collection': collection_name,
                'migration_successful': migration_successful,
                'chromadb_stats': chroma_stats,
                'qdrant_stats': qdrant_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to verify migration for {collection_name}: {e}")
            return {
                'collection': collection_name,
                'migration_successful': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get overall migration status"""
        try:
            chroma_collections = self.get_chromadb_collections()
            qdrant_collections = self.get_qdrant_collections()
            
            # Find collections that exist in ChromaDB but not in Qdrant
            pending_migrations = [col for col in chroma_collections if col not in qdrant_collections]
            
            return {
                'chromadb_collections': chroma_collections,
                'qdrant_collections': qdrant_collections,
                'pending_migrations': pending_migrations,
                'migration_needed': len(pending_migrations) > 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get migration status: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            } 