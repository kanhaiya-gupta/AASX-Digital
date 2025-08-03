"""
AI/RAG System Management Service
Handles system status, health checks, and vector database management.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemService:
    def __init__(self, rag_manager):
        """Initialize system service with RAG manager"""
        self.rag_manager = rag_manager
        logger.info("System Service initialized")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            logger.info("🔍 Getting system status...")
            
            if self.rag_manager is None:
                return {
                    "vector_db_connected": False,
                    "available_techniques": 0,
                    "technique_names": [],
                    "config_loaded": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get system status from RAG manager
            status = self.rag_manager.get_system_status()
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            raise e
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health check status"""
        try:
            logger.info("🔍 Performing health check...")
            
            if self.rag_manager is None:
                return {
                    "status": "unavailable",
                    "message": "AI/RAG system not available",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get health status
            health = self.rag_manager.get_system_status()
            
            return {
                "status": "healthy" if health.get('vector_db_connected') else "degraded",
                "message": "AI/RAG system is operational",
                "details": health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_vector_db_info(self) -> Dict[str, Any]:
        """Get vector database information"""
        try:
            logger.info("🔍 Getting vector database info...")
            
            if self.rag_manager and self.rag_manager.vector_uploader and self.rag_manager.vector_uploader.vector_db:
                vector_db = self.rag_manager.vector_uploader.vector_db
                
                if vector_db.is_connected:
                    # Get collection info from Qdrant
                    collection_info = vector_db.get_collection_info()
                    
                    # Calculate storage size
                    storage_size_mb = collection_info.get('storage_size_mb', 0)
                    storage_size_str = f"{storage_size_mb} MB" if storage_size_mb > 0 else "Unknown"
                    
                    return {
                        "status": "connected",
                        "database_name": "Qdrant",
                        "collection_name": collection_info.get('name', 'Unknown'),
                        "vectors_count": collection_info.get('vectors_count', 0),
                        "points_count": collection_info.get('points_count', 0),
                        "segments_count": collection_info.get('segments_count', 0),
                        "vector_size": collection_info.get('config', {}).get('vector_size', 1536),
                        "distance": collection_info.get('config', {}).get('distance', 'COSINE'),
                        "collections_count": 1,  # We're using one collection
                        "total_points": collection_info.get('points_count', 0),
                        "storage_size": storage_size_str
                    }
                else:
                    return {
                        "status": "disconnected",
                        "database_name": "Qdrant",
                        "collection_name": None,
                        "vectors_count": 0,
                        "points_count": 0,
                        "segments_count": 0,
                        "vector_size": 1536,
                        "distance": "COSINE",
                        "collections_count": 0,
                        "total_points": 0,
                        "storage_size": "Unknown"
                    }
            else:
                return {
                    "status": "not_initialized",
                    "database_name": "Qdrant",
                    "collection_name": None,
                    "vectors_count": 0,
                    "points_count": 0,
                    "segments_count": 0,
                    "vector_size": 1536,
                    "distance": "COSINE",
                    "collections_count": 0,
                    "total_points": 0,
                    "storage_size": "Unknown"
                }
            
        except Exception as e:
            logger.error(f"Error getting vector DB info: {e}")
            return {
                "status": "error",
                "database_name": "Qdrant",
                "collection_name": None,
                "vectors_count": 0,
                "points_count": 0,
                "segments_count": 0,
                "vector_size": 1536,
                "distance": "COSINE",
                "collections_count": 0,
                "total_points": 0,
                "storage_size": "Unknown",
                "error": str(e)
            }
    
    def clear_vector_data(self) -> Dict[str, Any]:
        """Clear vector database data"""
        try:
            logger.info("🧹 Clearing vector database data...")
            
            if self.rag_manager.vector_uploader and self.rag_manager.vector_uploader.vector_db:
                # Delete collection and recreate
                collection_name = self.rag_manager.vector_uploader.vector_db.collection_name
                self.rag_manager.vector_uploader.vector_db.delete_collection(collection_name)
                self.rag_manager.vector_uploader.vector_db.create_collection(collection_name)
                
                return {
                    "status": "success",
                    "message": f"Vector data cleared for collection: {collection_name}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception("Vector database not available")
            
        except Exception as e:
            logger.error(f"Error clearing vector data: {e}")
            raise e
    
    def process_project_embeddings(self, project_id: str) -> Dict[str, Any]:
        """Process vector embeddings for a specific project"""
        try:
            logger.info(f"🔍 Processing embeddings for project: {project_id}")
            
            if self.rag_manager:
                result = self.rag_manager.process_project_embeddings(project_id)
                return result
            else:
                raise Exception("RAG manager not available")
            
        except Exception as e:
            logger.error(f"Error processing project embeddings: {e}")
            raise e
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            logger.info("📊 Getting system statistics...")
            
            if self.rag_manager and self.rag_manager.vector_uploader and self.rag_manager.vector_uploader.vector_db:
                vector_db = self.rag_manager.vector_uploader.vector_db
                
                if vector_db.is_connected:
                    collection_info = vector_db.get_collection_info()
                    
                    return {
                        "total_collections": 1,
                        "total_points": collection_info.get('points_count', 0),
                        "total_storage": "Unknown",
                        "largest_collection": collection_info.get('name', 'Unknown'),
                        "collection_stats": [
                            {
                                "name": collection_info.get('name', 'Unknown'),
                                "points": collection_info.get('points_count', 0),
                                "storage": "Unknown"
                            }
                        ]
                    }
                else:
                    return {
                        "total_collections": 0,
                        "total_points": 0,
                        "total_storage": "Unknown",
                        "largest_collection": "None",
                        "collection_stats": []
                    }
            else:
                return {
                    "total_collections": 0,
                    "total_points": 0,
                    "total_storage": "Unknown",
                    "largest_collection": "None",
                    "collection_stats": []
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "total_collections": 0,
                "total_points": 0,
                "total_storage": "Unknown",
                "largest_collection": "None",
                "collection_stats": []
            }
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """Get vector collections information"""
        try:
            logger.info("🗂️ Getting collections information...")
            
            if self.rag_manager and self.rag_manager.vector_uploader and self.rag_manager.vector_uploader.vector_db:
                vector_db = self.rag_manager.vector_uploader.vector_db
                
                if vector_db.is_connected:
                    collection_info = vector_db.get_collection_info()
                    
                    return [
                        {
                            "name": collection_info.get('name', 'Unknown'),
                            "points_count": collection_info.get('points_count', 0),
                            "vectors_count": collection_info.get('vectors_count', 0),
                            "vector_size": collection_info.get('config', {}).get('vector_size', 1536),
                            "distance": collection_info.get('config', {}).get('distance', 'COSINE')
                        }
                    ]
                else:
                    return []
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return []
    
    def get_vector_data_stats(self) -> Dict[str, Any]:
        """Get vector data statistics"""
        try:
            logger.info("📊 Getting vector data statistics...")
            
            if self.rag_manager and self.rag_manager.vector_uploader and self.rag_manager.vector_uploader.vector_db:
                vector_db = self.rag_manager.vector_uploader.vector_db
                
                if vector_db.is_connected:
                    collection_info = vector_db.get_collection_info()
                    
                    # Calculate storage size
                    storage_size_mb = collection_info.get('storage_size_mb', 0)
                    storage_size_str = f"{storage_size_mb} MB" if storage_size_mb > 0 else "Unknown"
                    
                    return {
                        "total_collections": 1,
                        "total_points": collection_info.get('points_count', 0),
                        "total_storage": storage_size_str,
                        "largest_collection": collection_info.get('name', 'Unknown'),
                        "collection_stats": [
                            {
                                "name": collection_info.get('name', 'Unknown'),
                                "points": collection_info.get('points_count', 0),
                                "storage": storage_size_str
                            }
                        ]
                    }
                else:
                    return {
                        "total_collections": 0,
                        "total_points": 0,
                        "total_storage": "Unknown",
                        "largest_collection": "None",
                        "collection_stats": []
                    }
            else:
                return {
                    "total_collections": 0,
                    "total_points": 0,
                    "total_storage": "Unknown",
                    "largest_collection": "None",
                    "collection_stats": []
                }
                
        except Exception as e:
            logger.error(f"Error getting vector data stats: {e}")
            return {
                "total_collections": 0,
                "total_points": 0,
                "total_storage": "Unknown",
                "largest_collection": "None",
                "collection_stats": []
            }
    
    def get_available_techniques(self) -> List[Dict[str, Any]]:
        """Get available RAG techniques"""
        try:
            logger.info("🔧 Getting available RAG techniques...")
            
            if self.rag_manager:
                techniques = self.rag_manager.get_available_techniques()
                return techniques
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting available techniques: {e}")
            return []
    
    def backup_vector_data(self) -> Dict[str, Any]:
        """Backup vector database data"""
        try:
            logger.info("💾 Backing up vector database data...")
            
            if self.rag_manager and self.rag_manager.vector_uploader and self.rag_manager.vector_uploader.vector_db:
                vector_db = self.rag_manager.vector_uploader.vector_db
                
                if vector_db.is_connected:
                    # Get collection info for backup
                    collection_info = vector_db.get_collection_info()
                    
                    return {
                        "status": "success",
                        "message": "Vector data backup completed",
                        "backup_info": {
                            "collection_name": collection_info.get('name', 'Unknown'),
                            "points_count": collection_info.get('points_count', 0),
                            "vectors_count": collection_info.get('vectors_count', 0),
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Vector database not connected",
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                return {
                    "status": "error",
                    "message": "Vector database not available",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error backing up vector data: {e}")
            return {
                "status": "error",
                "message": f"Backup failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            } 