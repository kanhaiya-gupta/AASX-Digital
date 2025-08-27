"""
Generation Log Repository
========================

Data access layer for generation log operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any
from src.engine.database.connection_manager import ConnectionManager
from src.modules.ai_rag.models.generation_log import GenerationLog

logger = logging.getLogger(__name__)


class GenerationLogRepository:
    """
    Generation Log Repository - Pure Async Implementation
    
    Handles all database operations for generation logs.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize repository with connection manager"""
        self.connection_manager = connection_manager
        self.table_name = "generation_logs"
    
    async def create(self, log: GenerationLog) -> bool:
        """Create a new generation log"""
        try:
            log_data = log.to_dict()
            
            query = f"""
            INSERT INTO {self.table_name} (
                log_id, registry_id, session_id, generation_type,
                generation_model, generation_prompt, generated_content,
                model_parameters, generation_config, context_documents,
                generation_time_ms, token_count, cost_credits,
                quality_score, relevance_score, coherence_score, accuracy_score,
                user_rating, user_feedback, feedback_timestamp, metadata,
                tags, flags, error_message, error_code, retry_count,
                created_at, updated_at, generated_at
            ) VALUES (
                :log_id, :registry_id, :session_id, :generation_type,
                :generation_model, :generation_prompt, :generated_content,
                :model_parameters, :generation_config, :context_documents,
                :generation_time_ms, :token_count, :cost_credits,
                :quality_score, :relevance_score, :coherence_score, :accuracy_score,
                :user_rating, :user_feedback, :feedback_timestamp, :metadata,
                :tags, :flags, :error_message, :error_code, :retry_count,
                :created_at, :updated_at, :generated_at
            )
            """
            
            await self.connection_manager.execute_update(query, log_data)
            
            logger.info(f"Created generation log: {log.log_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error creating generation log: {e}")
            return False
    
    async def get_by_id(self, log_id: str) -> Optional[GenerationLog]:
        """Get generation log by ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE log_id = :log_id"
                result = await session.execute(query, {"log_id": log_id})
                row = result.fetchone()
                
                if row:
                    return GenerationLog.from_dict(dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Error getting generation log by ID: {e}")
            return None
    
    async def get_by_registry_id(self, registry_id: str) -> List[GenerationLog]:
        """Get generation logs by registry ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id ORDER BY created_at DESC"
                result = await session.execute(query, {"registry_id": registry_id})
                rows = result.fetchall()
                
                return [GenerationLog.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting generation logs by registry ID: {e}")
            return []
    
    async def get_by_session_id(self, session_id: str) -> List[GenerationLog]:
        """Get generation logs by session ID"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE session_id = :session_id ORDER BY created_at DESC"
                result = await session.execute(query, {"session_id": session_id})
                rows = result.fetchall()
                
                return [GenerationLog.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting generation logs by session ID: {e}")
            return []
    
    async def get_by_type(self, generation_type: str) -> List[GenerationLog]:
        """Get generation logs by type"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE generation_type = :generation_type ORDER BY created_at DESC"
                result = await session.execute(query, {"generation_type": generation_type})
                rows = result.fetchall()
                
                return [GenerationLog.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting generation logs by type: {e}")
            return []
    
    async def update(self, log: GenerationLog) -> bool:
        """Update existing generation log"""
        try:
            async with self.connection_manager.get_session() as session:
                log.update_timestamp()
                log_data = log.to_dict()
                
                query = f"""
                UPDATE {self.table_name} SET
                    quality_score = :quality_score, relevance_score = :relevance_score,
                    coherence_score = :coherence_score, accuracy_score = :accuracy_score,
                    user_rating = :user_rating, user_feedback = :user_feedback,
                    feedback_timestamp = :feedback_timestamp, metadata = :metadata,
                    tags = :tags, flags = :flags, error_message = :error_message,
                    error_code = :error_code, retry_count = :retry_count,
                    updated_at = :updated_at
                WHERE log_id = :log_id
                """
                
                await session.execute(query, log_data)
                await session.commit()
                
                logger.info(f"Updated generation log: {log.log_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating generation log: {e}")
            return False
    
    async def delete(self, log_id: str) -> bool:
        """Delete generation log"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"DELETE FROM {self.table_name} WHERE log_id = :log_id"
                await session.execute(query, {"log_id": log_id})
                await session.commit()
                
                logger.info(f"Deleted generation log: {log_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting generation log: {e}")
            return False
    
    async def get_successful_generations(self) -> List[GenerationLog]:
        """Get successful generation logs"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE error_message IS NULL ORDER BY created_at DESC"
                result = await session.execute(query)
                rows = result.fetchall()
                
                return [GenerationLog.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting successful generations: {e}")
            return []
    
    async def get_failed_generations(self) -> List[GenerationLog]:
        """Get failed generation logs"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT * FROM {self.table_name} WHERE error_message IS NOT NULL ORDER BY created_at DESC"
                result = await session.execute(query)
                rows = result.fetchall()
                
                return [GenerationLog.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting failed generations: {e}")
            return []
    
    async def count_by_registry_id(self, registry_id: str) -> int:
        """Count generation logs for a registry"""
        try:
            async with self.connection_manager.get_session() as session:
                query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE registry_id = :registry_id"
                result = await session.execute(query, {"registry_id": registry_id})
                row = result.fetchone()
                
                return row['count'] if row else 0
                
        except Exception as e:
            logger.error(f"Error counting generation logs: {e}")
            return 0
