"""
AI RAG Metrics Repository
=========================

Data access layer for AI RAG metrics operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any
from src.engine.database.connection_manager import ConnectionManager
from src.modules.ai_rag.models.ai_rag_metrics import AIRagMetrics

logger = logging.getLogger(__name__)


class AIRagMetricsRepository:
    """
    AI RAG Metrics Repository - Pure Async Implementation
    
    Handles all database operations for AI RAG metrics.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize repository with connection manager"""
        self.connection_manager = connection_manager
        self.table_name = "ai_rag_metrics"
    
    async def create(self, metrics: AIRagMetrics) -> bool:
        """Create new AI RAG metrics"""
        try:
            metrics_data = metrics.to_dict()
            
            query = f"""
            INSERT INTO {self.table_name} (
                registry_id, timestamp, health_score, response_time_ms,
                uptime_percentage, error_rate, embedding_generation_speed_sec,
                vector_db_query_response_time_ms, rag_response_generation_time_ms,
                context_retrieval_accuracy, rag_technique_performance,
                document_processing_stats, performance_trends,
                resource_utilization_trends, user_activity, query_patterns,
                compliance_status, security_events, user_interaction_count,
                query_execution_count, successful_rag_operations,
                failed_rag_operations, data_freshness_score,
                data_completeness_score, data_consistency_score,
                data_accuracy_score, cpu_usage_percent, memory_usage_percent,
                network_throughput_mbps, storage_usage_percent,
                rag_analytics, technique_effectiveness, model_performance,
                file_type_processing_efficiency, created_at, updated_at
            ) VALUES (
                :registry_id, :timestamp, :health_score, :response_time_ms,
                :uptime_percentage, :error_rate, :embedding_generation_speed_sec,
                :vector_db_query_response_time_ms, :rag_response_generation_time_ms,
                :context_retrieval_accuracy, :rag_technique_performance,
                :document_processing_stats, :performance_trends,
                :resource_utilization_trends, :user_activity, :query_patterns,
                :compliance_status, :security_events, :user_interaction_count,
                :query_execution_count, :successful_rag_operations,
                :failed_rag_operations, :data_freshness_score,
                :data_completeness_score, :data_consistency_score,
                :data_accuracy_score, :cpu_usage_percent, :memory_usage_percent,
                :network_throughput_mbps, :storage_usage_percent,
                :rag_analytics, :technique_effectiveness, :model_performance,
                :file_type_processing_efficiency, :created_at, :updated_at
            )
            """
            
            await self.connection_manager.execute_update(query, metrics_data)
            
            logger.info(f"Created AI RAG metrics for registry: {metrics.registry_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error creating AI RAG metrics: {e}")
            return False
    
    async def get_by_id(self, metric_id: int) -> Optional[AIRagMetrics]:
        """Get AI RAG metrics by ID"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE metric_id = :metric_id"
            result = await self.connection_manager.execute_query(query, {"metric_id": metric_id})
            
            if result and len(result) > 0:
                return AIRagMetrics(**result[0])
            return None
                
        except Exception as e:
            logger.error(f"Error getting AI RAG metrics by ID: {e}")
            return None
    
    async def get_by_registry_id(self, registry_id: str) -> List[AIRagMetrics]:
        """Get AI RAG metrics by registry ID"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id ORDER BY timestamp DESC"
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            return [AIRagMetrics(**row) for row in result]
                
        except Exception as e:
            logger.error(f"Error getting AI RAG metrics by registry ID: {e}")
            return []
    
    async def get_latest_by_registry_id(self, registry_id: str) -> Optional[AIRagMetrics]:
        """Get latest AI RAG metrics by registry ID"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id ORDER BY timestamp DESC LIMIT 1"
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                return AIRagMetrics(**result[0])
            return None
                
        except Exception as e:
            logger.error(f"Error getting latest AI RAG metrics: {e}")
            return None
    
    async def update(self, metrics: AIRagMetrics) -> bool:
        """Update existing AI RAG metrics"""
        try:
            metrics.update_timestamp()
            metrics_data = metrics.to_dict()
            
            query = f"""
            UPDATE {self.table_name} SET
                health_score = :health_score, response_time_ms = :response_time_ms,
                uptime_percentage = :uptime_percentage, error_rate = :error_rate,
                embedding_generation_speed_sec = :embedding_generation_speed_sec,
                vector_db_query_response_time_ms = :vector_db_query_response_time_ms,
                rag_response_generation_time_ms = :rag_response_generation_time_ms,
                context_retrieval_accuracy = :context_retrieval_accuracy,
                updated_at = :updated_at
            WHERE metric_id = :metric_id
            """
            
            await self.connection_manager.execute_update(query, metrics_data)
            
            logger.info(f"Updated AI RAG metrics: {metrics.metric_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error updating AI RAG metrics: {e}")
            return False
    
    async def delete(self, metric_id: int) -> bool:
        """Delete AI RAG metrics"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE metric_id = :metric_id"
            await self.connection_manager.execute_update(query, {"metric_id": metric_id})
            
            logger.info(f"Deleted AI RAG metrics: {metric_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error deleting AI RAG metrics: {e}")
            return False
    
    async def get_health_metrics(self, registry_id: str, limit: int = 100) -> List[AIRagMetrics]:
        """Get health metrics for a registry"""
        try:
            query = f"""
            SELECT * FROM {self.table_name} 
            WHERE registry_id = :registry_id 
            AND health_score IS NOT NULL
            ORDER BY timestamp DESC 
            LIMIT :limit
            """
            
            result = await self.connection_manager.execute_query(query, {
                "registry_id": registry_id,
                "limit": limit
            })
            
            return [AIRagMetrics(**row) for row in result]
                
        except Exception as e:
            logger.error(f"Error getting health metrics: {e}")
            return []
    
    async def get_performance_metrics(self, registry_id: str, limit: int = 100) -> List[AIRagMetrics]:
        """Get performance metrics for a registry"""
        try:
            query = f"""
            SELECT * FROM {self.table_name} 
            WHERE registry_id = :registry_id 
            AND response_time_ms IS NOT NULL
            ORDER BY timestamp DESC 
            LIMIT :limit
            """
            
            result = await self.connection_manager.execute_query(query, {
                "registry_id": registry_id,
                "limit": limit
            })
            
            return [AIRagMetrics(**row) for row in result]
                
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return []
    
    async def count_by_registry_id(self, registry_id: str) -> int:
        """Count metrics for a registry"""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE registry_id = :registry_id"
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            return result[0]['count'] if result and len(result) > 0 else 0
                
        except Exception as e:
            logger.error(f"Error counting metrics: {e}")
            return 0
