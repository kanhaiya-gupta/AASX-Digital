"""
Retrieval Service
================

Business logic layer for retrieval operations.
Handles RAG query sessions, retrieval strategies, and result management.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from src.modules.ai_rag.models.retrieval_session import RetrievalSession
from src.modules.ai_rag.repositories.retrieval_session_repository import RetrievalSessionRepository
from src.modules.ai_rag.repositories.ai_rag_registry_repository import AIRagRegistryRepository
from src.modules.ai_rag.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Retrieval Service - Pure Async Implementation
    
    Orchestrates retrieval operations including:
    - RAG query session management
    - Retrieval strategy execution
    - Result ranking and filtering
    - Session analytics and optimization
    """
    
    def __init__(self, session_repo: RetrievalSessionRepository,
                 registry_repo: AIRagRegistryRepository,
                 document_repo: DocumentRepository):
        """Initialize service with required repositories"""
        self.session_repo = session_repo
        self.registry_repo = registry_repo
        self.document_repo = document_repo
    
    async def create_session(self, session_data: Dict[str, Any]) -> Optional[RetrievalSession]:
        """Create a new retrieval session with validation"""
        try:
            logger.info(f"Creating retrieval session: {session_data.get('session_name', 'Unknown')}")
            
            # Validate session data
            if not await self._validate_session_data(session_data):
                logger.error("Session data validation failed")
                return None
            
            # Process session data
            processed_data = await self._process_session_data(session_data)
            
            # Create session instance
            session = RetrievalSession(**processed_data)
            
            # Validate session before creation
            if not await self._validate_session(session):
                logger.error("Session validation failed")
                return None
            
            # Create in database
            success = await self.session_repo.create(session)
            if not success:
                logger.error("Failed to create session in database")
                return None
            
            logger.info(f"Successfully created retrieval session: {session.session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating retrieval session: {e}")
            return None
    
    async def get_session_by_id(self, session_id: str) -> Optional[RetrievalSession]:
        """Get retrieval session by ID with enhanced data"""
        try:
            session = await self.session_repo.get_by_id(session_id)
            if session:
                # Enhance with additional data
                await self._enhance_session_data(session)
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting session by ID: {e}")
            return None
    
    async def get_sessions_by_registry(self, registry_id: str) -> List[RetrievalSession]:
        """Get retrieval sessions by registry ID with sorting"""
        try:
            sessions = await self.session_repo.get_by_registry_id(registry_id)
            
            # Sort by creation date (newest first)
            sessions.sort(key=lambda x: x.created_at or "", reverse=True)
            
            # Enhance each session
            for session in sessions:
                await self._enhance_session_data(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting sessions by registry: {e}")
            return []
    
    async def get_sessions_by_user(self, user_id: str) -> List[RetrievalSession]:
        """Get retrieval sessions by user ID with filtering"""
        try:
            sessions = await self.session_repo.get_by_user_id(user_id)
            
            # Filter active sessions first
            active_sessions = [s for s in sessions if s.is_active()]
            completed_sessions = [s for s in sessions if s.is_completed()]
            
            # Combine with active sessions first
            sorted_sessions = active_sessions + completed_sessions
            
            # Enhance each session
            for session in sorted_sessions:
                await self._enhance_session_data(session)
            
            return sorted_sessions
            
        except Exception as e:
            logger.error(f"Error getting sessions by user: {e}")
            return []
    
    async def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update existing retrieval session with validation"""
        try:
            logger.info(f"Updating retrieval session: {session_id}")
            
            # Get existing session
            session = await self.session_repo.get_by_id(session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return False
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            # Validate updated session
            if not await self._validate_session(session):
                logger.error("Updated session validation failed")
                return False
            
            # Update timestamp
            session.update_timestamp()
            
            # Save to database
            success = await self.session_repo.update(session)
            if success:
                logger.info(f"Successfully updated session: {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete retrieval session with cleanup"""
        try:
            logger.info(f"Deleting retrieval session: {session_id}")
            
            # Delete from database
            success = await self.session_repo.delete(session_id)
            if success:
                logger.info(f"Successfully deleted session: {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    async def start_session(self, session_id: str) -> bool:
        """Start a retrieval session"""
        try:
            logger.info(f"Starting retrieval session: {session_id}")
            
            update_data = {
                "session_status": "active",
                "started_at": datetime.now().isoformat()
            }
            
            success = await self.update_session(session_id, update_data)
            if success:
                logger.info(f"Successfully started session: {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return False
    
    async def complete_session(self, session_id: str, results: List[Dict[str, Any]] = None) -> bool:
        """Complete a retrieval session with results"""
        try:
            logger.info(f"Completing retrieval session: {session_id}")
            
            # Get session to calculate duration
            session = await self.session_repo.get_by_id(session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return False
            
            # Calculate session duration
            duration_ms = None
            if session.started_at:
                try:
                    start_time = datetime.fromisoformat(session.started_at.replace('Z', '+00:00'))
                    end_time = datetime.now()
                    duration_ms = int((end_time - start_time).total_seconds() * 1000)
                except:
                    duration_ms = 0
            
            update_data = {
                "session_status": "completed",
                "completed_at": datetime.now().isoformat(),
                "retrieved_documents": results or [],
                "result_count": len(results) if results else 0
            }
            
            if duration_ms is not None:
                update_data["retrieval_time_ms"] = duration_ms
            
            success = await self.update_session(session_id, update_data)
            if success:
                logger.info(f"Successfully completed session: {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error completing session: {e}")
            return False
    
    async def get_active_sessions(self) -> List[RetrievalSession]:
        """Get all active retrieval sessions"""
        try:
            sessions = await self.session_repo.get_active_sessions()
            
            # Enhance each session
            for session in sessions:
                await self._enhance_session_data(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []
    
    async def execute_retrieval_strategy(self, session_id: str, strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific retrieval strategy for a session"""
        try:
            logger.info(f"Executing retrieval strategy for session: {session_id}")
            
            # Get session
            session = await self.session_repo.get_by_id(session_id)
            if not session:
                return {"error": "Session not found"}
            
            # Execute strategy based on type
            strategy_type = strategy_config.get("type", session.retrieval_strategy)
            
            if strategy_type == "semantic":
                results = await self._execute_semantic_strategy(session, strategy_config)
            elif strategy_type == "keyword":
                results = await self._execute_keyword_strategy(session, strategy_config)
            elif strategy_type == "hybrid":
                results = await self._execute_hybrid_strategy(session, strategy_config)
            else:
                results = await self._execute_default_strategy(session, strategy_config)
            
            # Update session with results
            await self.complete_session(session_id, results)
            
            return {
                "session_id": session_id,
                "strategy_type": strategy_type,
                "results": results,
                "result_count": len(results),
                "execution_time_ms": strategy_config.get("execution_time", 0)
            }
            
        except Exception as e:
            logger.error(f"Error executing retrieval strategy: {e}")
            return {"error": str(e)}
    
    async def analyze_session_performance(self, session_id: str) -> Dict[str, Any]:
        """Analyze performance metrics for a session"""
        try:
            logger.info(f"Analyzing session performance: {session_id}")
            
            session = await self.session_repo.get_by_id(session_id)
            if not session:
                return {"error": "Session not found"}
            
            analysis = {
                "session_id": session_id,
                "session_name": session.session_name,
                "session_type": session.session_type,
                "performance_metrics": {},
                "recommendations": []
            }
            
            # Calculate performance metrics
            if session.retrieval_time_ms:
                analysis["performance_metrics"]["retrieval_time_ms"] = session.retrieval_time_ms
                
                # Categorize performance
                if session.retrieval_time_ms < 100:
                    analysis["performance_metrics"]["performance_level"] = "excellent"
                elif session.retrieval_time_ms < 500:
                    analysis["performance_metrics"]["performance_level"] = "good"
                elif session.retrieval_time_ms < 1000:
                    analysis["performance_metrics"]["performance_level"] = "fair"
                else:
                    analysis["performance_metrics"]["performance_level"] = "poor"
            
            # Result quality analysis
            if session.result_count:
                analysis["performance_metrics"]["result_count"] = session.result_count
                
                if session.result_count < 5:
                    analysis["recommendations"].append("Consider increasing max_results for better coverage")
                elif session.result_count > 20:
                    analysis["recommendations"].append("Consider reducing max_results for faster retrieval")
            
            # Relevance analysis
            if session.relevance_score:
                analysis["performance_metrics"]["relevance_score"] = session.relevance_score
                
                if session.relevance_score < 0.7:
                    analysis["recommendations"].append("Consider adjusting similarity threshold for better relevance")
            
            # Strategy optimization
            if session.retrieval_strategy:
                analysis["performance_metrics"]["strategy"] = session.retrieval_strategy
                
                if session.retrieval_strategy == "semantic" and session.retrieval_time_ms and session.retrieval_time_ms > 1000:
                    analysis["recommendations"].append("Consider using hybrid strategy for better performance")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing session performance: {e}")
            return {"error": str(e)}
    
    async def get_session_statistics(self, registry_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """Get comprehensive statistics for retrieval sessions"""
        try:
            if registry_id:
                sessions = await self.session_repo.get_by_registry_id(registry_id)
                scope = f"registry {registry_id}"
            elif user_id:
                sessions = await self.session_repo.get_by_user_id(user_id)
                scope = f"user {user_id}"
            else:
                # Get all sessions (this would need a method in repository)
                sessions = await self.session_repo.get_all()
                scope = "all sessions"
            
            logger.info(f"Generating session statistics for {scope}")
            
            stats = {
                "total_sessions": len(sessions),
                "by_status": {},
                "by_type": {},
                "by_strategy": {},
                "performance_metrics": {
                    "average_retrieval_time": 0.0,
                    "average_result_count": 0.0,
                    "average_relevance_score": 0.0
                },
                "user_activity": {},
                "strategy_effectiveness": {}
            }
            
            total_retrieval_time = 0
            total_result_count = 0
            total_relevance_score = 0
            retrieval_time_count = 0
            result_count_count = 0
            relevance_count = 0
            
            for session in sessions:
                # Count by status
                status = session.session_status
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Count by type
                session_type = session.session_type
                stats["by_type"][session_type] = stats["by_type"].get(session_type, 0) + 1
                
                # Count by strategy
                strategy = session.retrieval_strategy
                stats["by_strategy"][strategy] = stats["by_strategy"].get(strategy, 0) + 1
                
                # Accumulate performance metrics
                if session.retrieval_time_ms:
                    total_retrieval_time += session.retrieval_time_ms
                    retrieval_time_count += 1
                
                if session.result_count:
                    total_result_count += session.result_count
                    result_count_count += 1
                
                if session.relevance_score:
                    total_relevance_score += session.relevance_score
                    relevance_count += 1
                
                # Track user activity
                if session.user_id:
                    user = session.user_id
                    if user not in stats["user_activity"]:
                        stats["user_activity"][user] = 0
                    stats["user_activity"][user] += 1
            
            # Calculate averages
            if retrieval_time_count > 0:
                stats["performance_metrics"]["average_retrieval_time"] = total_retrieval_time / retrieval_time_count
            
            if result_count_count > 0:
                stats["performance_metrics"]["average_result_count"] = total_result_count / result_count_count
            
            if relevance_count > 0:
                stats["performance_metrics"]["average_relevance_score"] = total_relevance_score / relevance_count
            
            # Calculate strategy effectiveness
            for strategy, count in stats["by_strategy"].items():
                strategy_sessions = [s for s in sessions if s.retrieval_strategy == strategy]
                if strategy_sessions:
                    avg_time = sum(s.retrieval_time_ms or 0 for s in strategy_sessions) / len(strategy_sessions)
                    avg_relevance = sum(s.relevance_score or 0 for s in strategy_sessions) / len(strategy_sessions)
                    
                    stats["strategy_effectiveness"][strategy] = {
                        "count": count,
                        "average_retrieval_time": avg_time,
                        "average_relevance_score": avg_relevance
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating session statistics: {e}")
            return {}
    
    # Private helper methods
    
    async def _validate_session_data(self, session_data: Dict[str, Any]) -> bool:
        """Validate session data before processing"""
        try:
            # Check required fields
            if not session_data.get('registry_id'):
                logger.error("Missing registry_id")
                return False
            
            if not session_data.get('user_id'):
                logger.error("Missing user_id")
                return False
            
            if not session_data.get('query_text'):
                logger.error("Missing query_text")
                return False
            
            # Check session type
            session_type = session_data.get('session_type')
            if session_type and session_type not in ["query", "conversation", "batch", "streaming"]:
                logger.error(f"Invalid session type: {session_type}")
                return False
            
            # Check retrieval strategy
            strategy = session_data.get('retrieval_strategy')
            if strategy and strategy not in ["semantic", "keyword", "hybrid", "vector", "rule_based"]:
                logger.error(f"Invalid retrieval strategy: {strategy}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Session data validation error: {e}")
            return False
    
    async def _process_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance session data"""
        try:
            processed_data = session_data.copy()
            
            # Set default values
            if 'session_status' not in processed_data:
                processed_data['session_status'] = 'pending'
            
            if 'session_type' not in processed_data:
                processed_data['session_type'] = 'query'
            
            if 'retrieval_strategy' not in processed_data:
                processed_data['retrieval_strategy'] = 'semantic'
            
            if 'max_results' not in processed_data:
                processed_data['max_results'] = 10
            
            if 'similarity_threshold' not in processed_data:
                processed_data['similarity_threshold'] = 0.7
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing session data: {e}")
            return session_data
    
    async def _validate_session(self, session: RetrievalSession) -> bool:
        """Validate session before database operations"""
        try:
            # Check required fields
            if not session.registry_id:
                logger.error("Session missing registry_id")
                return False
            
            if not session.user_id:
                logger.error("Session missing user_id")
                return False
            
            if not session.query_text:
                logger.error("Session missing query_text")
                return False
            
            # Check session status
            if session.session_status and session.session_status not in ["pending", "active", "completed", "failed", "cancelled"]:
                logger.error(f"Invalid session status: {session.session_status}")
                return False
            
            # Check session type
            if session.session_type and session.session_type not in ["query", "conversation", "batch", "streaming"]:
                logger.error(f"Invalid session type: {session.session_type}")
                return False
            
            # Check retrieval strategy
            if session.retrieval_strategy and session.retrieval_strategy not in ["semantic", "keyword", "hybrid", "vector", "rule_based"]:
                logger.error(f"Invalid retrieval strategy: {session.retrieval_strategy}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False
    
    async def _enhance_session_data(self, session: RetrievalSession) -> None:
        """Enhance session with additional computed data"""
        try:
            # Add session duration if started and completed
            if session.started_at and session.completed_at:
                try:
                    start_time = datetime.fromisoformat(session.started_at.replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(session.completed_at.replace('Z', '+00:00'))
                    duration_ms = int((end_time - start_time).total_seconds() * 1000)
                    session.retrieval_time_ms = duration_ms
                except:
                    pass
            
            # Add query summary if not present
            if not hasattr(session, 'query_summary') and session.query_text:
                session.query_summary = session.query_text[:100] + "..." if len(session.query_text) > 100 else session.query_text
                
        except Exception as e:
            logger.warning(f"Error enhancing session data: {e}")
    
    async def _execute_semantic_strategy(self, session: RetrievalSession, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute semantic retrieval strategy"""
        try:
            logger.info(f"Executing semantic strategy for session: {session.session_id}")
            
            # Simulate semantic search results
            results = [
                {
                    "document_id": "doc_123",
                    "title": "Semantic Search Result 1",
                    "content": "This is a semantic search result based on meaning and context.",
                    "relevance_score": 0.92,
                    "retrieval_method": "semantic"
                },
                {
                    "document_id": "doc_456",
                    "title": "Semantic Search Result 2",
                    "content": "Another semantic result with high relevance to the query.",
                    "relevance_score": 0.87,
                    "retrieval_method": "semantic"
                }
            ]
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing semantic strategy: {e}")
            return []
    
    async def _execute_keyword_strategy(self, session: RetrievalSession, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute keyword-based retrieval strategy"""
        try:
            logger.info(f"Executing keyword strategy for session: {session.session_id}")
            
            # Simulate keyword search results
            results = [
                {
                    "document_id": "doc_789",
                    "title": "Keyword Search Result 1",
                    "content": "This result matches specific keywords in the query.",
                    "relevance_score": 0.85,
                    "retrieval_method": "keyword"
                }
            ]
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing keyword strategy: {e}")
            return []
    
    async def _execute_hybrid_strategy(self, session: RetrievalSession, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute hybrid retrieval strategy"""
        try:
            logger.info(f"Executing hybrid strategy for session: {session.session_id}")
            
            # Combine semantic and keyword results
            semantic_results = await self._execute_semantic_strategy(session, config)
            keyword_results = await self._execute_keyword_strategy(session, config)
            
            # Merge and rank results
            all_results = semantic_results + keyword_results
            all_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return all_results[:session.max_results]
            
        except Exception as e:
            logger.error(f"Error executing hybrid strategy: {e}")
            return []
    
    async def _execute_default_strategy(self, session: RetrievalSession, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute default retrieval strategy"""
        try:
            logger.info(f"Executing default strategy for session: {session.session_id}")
            
            # Default to semantic strategy
            return await self._execute_semantic_strategy(session, config)
            
        except Exception as e:
            logger.error(f"Error executing default strategy: {e}")
            return []
