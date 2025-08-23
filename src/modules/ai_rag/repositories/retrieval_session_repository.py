"""
Retrieval Session Repository
===========================

Data access layer for retrieval session operations.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any
from src.engine.database.connection_manager import ConnectionManager
from src.modules.ai_rag.models.retrieval_session import RetrievalSession

logger = logging.getLogger(__name__)


class RetrievalSessionRepository:
    """
    Retrieval Session Repository - Pure Async Implementation
    
    Handles all database operations for retrieval sessions.
    Follows the same convention as AASX and Twin Registry modules.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize repository with connection manager"""
        self.connection_manager = connection_manager
        self.table_name = "retrieval_sessions"
    
    async def create(self, session: RetrievalSession) -> bool:
        """Create a new retrieval session"""
        try:
            async with self.connection_manager.get_session() as session_db:
                session_data = session.to_dict()
                
                query = f"""
                INSERT INTO {self.table_name} (
                    session_id, registry_id, user_id, session_name, session_type,
                    session_status, query_text, query_type, query_parameters,
                    retrieval_strategy, max_results, similarity_threshold,
                    retrieved_documents, result_count, retrieval_time_ms,
                    relevance_score, user_satisfaction, feedback_notes,
                    context_history, conversation_flow, created_at, updated_at,
                    started_at, completed_at
                ) VALUES (
                    :session_id, :registry_id, :user_id, :session_name, :session_type,
                    :session_status, :query_text, :query_type, :query_parameters,
                    :retrieval_strategy, :max_results, :similarity_threshold,
                    :retrieved_documents, :result_count, :retrieval_time_ms,
                    :relevance_score, :user_satisfaction, :feedback_notes,
                    :context_history, :conversation_flow, :created_at, :updated_at,
                    :started_at, :completed_at
                )
                """
                
                await session_db.execute(query, session_data)
                await session_db.commit()
                
                logger.info(f"Created retrieval session: {session.session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating retrieval session: {e}")
            return False
    
    async def get_by_id(self, session_id: str) -> Optional[RetrievalSession]:
        """Get retrieval session by ID"""
        try:
            async with self.connection_manager.get_session() as session_db:
                query = f"SELECT * FROM {self.table_name} WHERE session_id = :session_id"
                result = await session_db.execute(query, {"session_id": session_id})
                row = result.fetchone()
                
                if row:
                    return RetrievalSession.from_dict(dict(row))
                return None
                
        except Exception as e:
            logger.error(f"Error getting retrieval session by ID: {e}")
            return None
    
    async def get_by_registry_id(self, registry_id: str) -> List[RetrievalSession]:
        """Get retrieval sessions by registry ID"""
        try:
            async with self.connection_manager.get_session() as session_db:
                query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id ORDER BY created_at DESC"
                result = await session_db.execute(query, {"registry_id": registry_id})
                rows = result.fetchall()
                
                return [RetrievalSession.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting retrieval sessions by registry ID: {e}")
            return []
    
    async def get_by_user_id(self, user_id: str) -> List[RetrievalSession]:
        """Get retrieval sessions by user ID"""
        try:
            async with self.connection_manager.get_session() as session_db:
                query = f"SELECT * FROM {self.table_name} WHERE user_id = :user_id ORDER BY created_at DESC"
                result = await session_db.execute(query, {"user_id": user_id})
                rows = result.fetchall()
                
                return [RetrievalSession.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting retrieval sessions by user ID: {e}")
            return []
    
    async def get_active_sessions(self) -> List[RetrievalSession]:
        """Get active retrieval sessions"""
        try:
            async with self.connection_manager.get_session() as session_db:
                query = f"SELECT * FROM {self.table_name} WHERE session_status = 'active'"
                result = await session_db.execute(query)
                rows = result.fetchall()
                
                return [RetrievalSession.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []
    
    async def update(self, session: RetrievalSession) -> bool:
        """Update existing retrieval session"""
        try:
            async with self.connection_manager.get_session() as session_db:
                session.update_timestamp()
                session_data = session.to_dict()
                
                query = f"""
                UPDATE {self.table_name} SET
                    session_status = :session_status, query_parameters = :query_parameters,
                    retrieved_documents = :retrieved_documents, result_count = :result_count,
                    retrieval_time_ms = :retrieval_time_ms, relevance_score = :relevance_score,
                    user_satisfaction = :user_satisfaction, feedback_notes = :feedback_notes,
                    context_history = :context_history, conversation_flow = :conversation_flow,
                    started_at = :started_at, completed_at = :completed_at, updated_at = :updated_at
                WHERE session_id = :session_id
                """
                
                await session_db.execute(query, session_data)
                await session_db.commit()
                
                logger.info(f"Updated retrieval session: {session.session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating retrieval session: {e}")
            return False
    
    async def delete(self, session_id: str) -> bool:
        """Delete retrieval session"""
        try:
            async with self.connection_manager.get_session() as session_db:
                query = f"DELETE FROM {self.table_name} WHERE session_id = :session_id"
                await session_db.execute(query, {"session_id": session_id})
                await session_db.commit()
                
                logger.info(f"Deleted retrieval session: {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting retrieval session: {e}")
            return False
    
    async def count_by_registry_id(self, registry_id: str) -> int:
        """Count sessions for a registry"""
        try:
            async with self.connection_manager.get_session() as session_db:
                query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE registry_id = :registry_id"
                result = await session_db.execute(query, {"registry_id": registry_id})
                row = result.fetchone()
                
                return row['count'] if row else 0
                
        except Exception as e:
            logger.error(f"Error counting sessions: {e}")
            return 0
