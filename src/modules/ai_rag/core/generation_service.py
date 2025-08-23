"""
Generation Service
=================

Business logic layer for generation operations.
Handles AI generation, quality assessment, and feedback management.
Pure async implementation following AASX and Twin Registry convention.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.modules.ai_rag.models.generation_log import GenerationLog
from src.modules.ai_rag.repositories.generation_log_repository import GenerationLogRepository
from src.modules.ai_rag.repositories.retrieval_session_repository import RetrievalSessionRepository
from src.modules.ai_rag.repositories.ai_rag_registry_repository import AIRagRegistryRepository

logger = logging.getLogger(__name__)


class GenerationService:
    """
    Generation Service - Pure Async Implementation
    
    Orchestrates generation operations including:
    - AI content generation and logging
    - Quality assessment and scoring
    - Feedback collection and analysis
    - Generation optimization and retry logic
    """
    
    def __init__(self, generation_repo: GenerationLogRepository,
                 session_repo: RetrievalSessionRepository,
                 registry_repo: AIRagRegistryRepository):
        """Initialize service with required repositories"""
        self.generation_repo = generation_repo
        self.session_repo = session_repo
        self.registry_repo = registry_repo
    
    async def create_generation_log(self, generation_data: Dict[str, Any]) -> Optional[GenerationLog]:
        """Create a new generation log with validation"""
        try:
            logger.info(f"Creating generation log for session: {generation_data.get('session_id', 'Unknown')}")
            
            # Validate generation data
            if not await self._validate_generation_data(generation_data):
                logger.error("Generation data validation failed")
                return None
            
            # Process generation data
            processed_data = await self._process_generation_data(generation_data)
            
            # Create generation log instance
            generation_log = GenerationLog(**processed_data)
            
            # Validate generation log before creation
            if not await self._validate_generation_log(generation_log):
                logger.error("Generation log validation failed")
                return None
            
            # Calculate quality scores
            await self._calculate_generation_quality(generation_log)
            
            # Create in database
            success = await self.generation_repo.create(generation_log)
            if not success:
                logger.error("Failed to create generation log in database")
                return None
            
            logger.info(f"Successfully created generation log: {generation_log.log_id}")
            return generation_log
            
        except Exception as e:
            logger.error(f"Error creating generation log: {e}")
            return None
    
    async def get_generation_log_by_id(self, log_id: str) -> Optional[GenerationLog]:
        """Get generation log by ID with enhanced data"""
        try:
            generation_log = await self.generation_repo.get_by_id(log_id)
            if generation_log:
                # Enhance with additional data
                await self._enhance_generation_data(generation_log)
            
            return generation_log
            
        except Exception as e:
            logger.error(f"Error getting generation log by ID: {e}")
            return None
    
    async def get_generation_logs_by_registry(self, registry_id: str) -> List[GenerationLog]:
        """Get generation logs by registry ID with sorting"""
        try:
            logs = await self.generation_repo.get_by_registry_id(registry_id)
            
            # Sort by creation date (newest first)
            logs.sort(key=lambda x: x.created_at or "", reverse=True)
            
            # Enhance each log
            for log in logs:
                await self._enhance_generation_data(log)
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting generation logs by registry: {e}")
            return []
    
    async def get_generation_logs_by_session(self, session_id: str) -> List[GenerationLog]:
        """Get generation logs by session ID with filtering"""
        try:
            logs = await self.generation_repo.get_by_session_id(session_id)
            
            # Sort by generation time (newest first)
            logs.sort(key=lambda x: x.generated_at or "", reverse=True)
            
            # Enhance each log
            for log in logs:
                await self._enhance_generation_data(log)
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting generation logs by session: {e}")
            return []
    
    async def update_generation_log(self, log_id: str, update_data: Dict[str, Any]) -> bool:
        """Update existing generation log with validation"""
        try:
            logger.info(f"Updating generation log: {log_id}")
            
            # Get existing generation log
            generation_log = await self.generation_repo.get_by_id(log_id)
            if not generation_log:
                logger.error(f"Generation log not found: {log_id}")
                return False
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(generation_log, key):
                    setattr(generation_log, key, value)
            
            # Validate updated generation log
            if not await self._validate_generation_log(generation_log):
                logger.error("Updated generation log validation failed")
                return False
            
            # Update timestamp
            generation_log.update_timestamp()
            
            # Recalculate quality scores if quality-related fields changed
            if any(key in update_data for key in ['quality_score', 'relevance_score', 'coherence_score', 'accuracy_score']):
                await self._calculate_generation_quality(generation_log)
            
            # Save to database
            success = await self.generation_repo.update(generation_log)
            if success:
                logger.info(f"Successfully updated generation log: {log_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating generation log: {e}")
            return False
    
    async def delete_generation_log(self, log_id: str) -> bool:
        """Delete generation log with cleanup"""
        try:
            logger.info(f"Deleting generation log: {log_id}")
            
            # Delete from database
            success = await self.generation_repo.delete(log_id)
            if success:
                logger.info(f"Successfully deleted generation log: {log_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting generation log: {e}")
            return False
    
    async def get_generation_logs_by_type(self, generation_type: str) -> List[GenerationLog]:
        """Get generation logs by type with filtering"""
        try:
            logs = await self.generation_repo.get_by_type(generation_type)
            
            # Filter by quality
            high_quality_logs = [log for log in logs if log.is_high_quality()]
            
            logger.info(f"Found {len(logs)} generation logs for type {generation_type}, {len(high_quality_logs)} high quality")
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting generation logs by type: {e}")
            return []
    
    async def get_successful_generations(self) -> List[GenerationLog]:
        """Get successful generation logs"""
        try:
            return await self.generation_repo.get_successful_generations()
        except Exception as e:
            logger.error(f"Error getting successful generations: {e}")
            return []
    
    async def get_failed_generations(self) -> List[GenerationLog]:
        """Get failed generation logs"""
        try:
            return await self.generation_repo.get_failed_generations()
        except Exception as e:
            logger.error(f"Error getting failed generations: {e}")
            return []
    
    async def retry_generation(self, log_id: str, retry_config: Dict[str, Any] = None) -> Optional[GenerationLog]:
        """Retry a failed generation with new configuration"""
        try:
            logger.info(f"Retrying generation: {log_id}")
            
            # Get original generation log
            original_log = await self.generation_repo.get_by_id(log_id)
            if not original_log:
                logger.error(f"Generation log not found: {log_id}")
                return None
            
            # Check if it's a failed generation
            if not original_log.error_message:
                logger.warning(f"Generation log {log_id} is not failed, cannot retry")
                return None
            
            # Increment retry count
            retry_count = (original_log.retry_count or 0) + 1
            
            # Create new generation log for retry
            retry_data = {
                "registry_id": original_log.registry_id,
                "session_id": original_log.session_id,
                "generation_type": original_log.generation_type,
                "generation_model": retry_config.get("model", original_log.generation_model) if retry_config else original_log.generation_model,
                "generation_prompt": retry_config.get("prompt", original_log.generation_prompt) if retry_config else original_log.generation_prompt,
                "model_parameters": retry_config.get("parameters", original_log.model_parameters) if retry_config else original_log.model_parameters,
                "retry_count": retry_count,
                "flags": ["retry_attempt"]
            }
            
            # Create retry log
            retry_log = await self.create_generation_log(retry_data)
            if retry_log:
                logger.info(f"Successfully created retry generation log: {retry_log.log_id}")
                
                # Update original log with retry information
                await self.update_generation_log(log_id, {"retry_count": retry_count})
            
            return retry_log
            
        except Exception as e:
            logger.error(f"Error retrying generation: {e}")
            return None
    
    async def collect_user_feedback(self, log_id: str, feedback_data: Dict[str, Any]) -> bool:
        """Collect and store user feedback for a generation"""
        try:
            logger.info(f"Collecting user feedback for generation: {log_id}")
            
            # Validate feedback data
            if not await self._validate_feedback_data(feedback_data):
                logger.error("Feedback data validation failed")
                return False
            
            # Update generation log with feedback
            update_data = {
                "user_rating": feedback_data.get("rating"),
                "user_feedback": feedback_data.get("feedback"),
                "feedback_timestamp": datetime.now().isoformat()
            }
            
            success = await self.update_generation_log(log_id, update_data)
            if success:
                logger.info(f"Successfully collected user feedback for generation: {log_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error collecting user feedback: {e}")
            return False
    
    async def analyze_generation_quality(self, log_id: str) -> Dict[str, Any]:
        """Analyze quality metrics for a generation"""
        try:
            logger.info(f"Analyzing generation quality: {log_id}")
            
            generation_log = await self.generation_repo.get_by_id(log_id)
            if not generation_log:
                return {"error": "Generation log not found"}
            
            analysis = {
                "log_id": log_id,
                "generation_type": generation_log.generation_type,
                "generation_model": generation_log.generation_model,
                "quality_metrics": {},
                "recommendations": []
            }
            
            # Analyze quality scores
            if generation_log.quality_score is not None:
                analysis["quality_metrics"]["quality_score"] = generation_log.quality_score
                
                if generation_log.quality_score < 0.7:
                    analysis["recommendations"].append("Quality score is low, consider adjusting generation parameters")
                elif generation_log.quality_score < 0.85:
                    analysis["recommendations"].append("Quality score could be improved with parameter tuning")
            
            # Analyze relevance score
            if generation_log.relevance_score is not None:
                analysis["quality_metrics"]["relevance_score"] = generation_log.relevance_score
                
                if generation_log.relevance_score < 0.8:
                    analysis["recommendations"].append("Relevance score is low, review prompt engineering")
            
            # Analyze coherence score
            if generation_log.coherence_score is not None:
                analysis["quality_metrics"]["coherence_score"] = generation_log.coherence_score
                
                if generation_log.coherence_score < 0.8:
                    analysis["recommendations"].append("Coherence score is low, consider improving context")
            
            # Analyze accuracy score
            if generation_log.accuracy_score is not None:
                analysis["quality_metrics"]["accuracy_score"] = generation_log.accuracy_score
                
                if generation_log.accuracy_score < 0.8:
                    analysis["recommendations"].append("Accuracy score is low, review training data quality")
            
            # Performance analysis
            if generation_log.generation_time_ms:
                analysis["quality_metrics"]["generation_time_ms"] = generation_log.generation_time_ms
                
                if generation_log.generation_time_ms > 10000:
                    analysis["recommendations"].append("Generation time is high, consider model optimization")
            
            # Token usage analysis
            if generation_log.token_count:
                analysis["quality_metrics"]["token_count"] = generation_log.token_count
                
                if generation_log.token_count > 1000:
                    analysis["recommendations"].append("High token usage, consider prompt optimization")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing generation quality: {e}")
            return {"error": str(e)}
    
    async def get_generation_statistics(self, registry_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """Get comprehensive statistics for generations"""
        try:
            if registry_id:
                logs = await self.generation_repo.get_by_registry_id(registry_id)
                scope = f"registry {registry_id}"
            elif session_id:
                logs = await self.generation_repo.get_by_session_id(session_id)
                scope = f"session {session_id}"
            else:
                # Get all logs (this would need a method in repository)
                logs = await self.generation_repo.get_all()
                scope = "all generations"
            
            logger.info(f"Generating generation statistics for {scope}")
            
            stats = {
                "total_generations": len(logs),
                "by_type": {},
                "by_model": {},
                "by_quality": {
                    "excellent": 0,
                    "good": 0,
                    "fair": 0,
                    "poor": 0
                },
                "performance_metrics": {
                    "average_generation_time": 0.0,
                    "average_token_count": 0.0,
                    "average_quality_score": 0.0
                },
                "success_rate": 0.0,
                "error_analysis": {},
                "model_performance": {}
            }
            
            total_generation_time = 0
            total_token_count = 0
            total_quality_score = 0
            generation_time_count = 0
            token_count_count = 0
            quality_count = 0
            successful_count = 0
            
            for log in logs:
                # Count by type
                gen_type = log.generation_type
                stats["by_type"][gen_type] = stats["by_type"].get(gen_type, 0) + 1
                
                # Count by model
                model = log.generation_model
                stats["by_model"][model] = stats["by_model"].get(model, 0) + 1
                
                # Categorize quality scores
                if log.quality_score is not None:
                    total_quality_score += log.quality_score
                    quality_count += 1
                    
                    if log.quality_score >= 0.9:
                        stats["by_quality"]["excellent"] += 1
                    elif log.quality_score >= 0.8:
                        stats["by_quality"]["good"] += 1
                    elif log.quality_score >= 0.7:
                        stats["by_quality"]["fair"] += 1
                    else:
                        stats["by_quality"]["poor"] += 1
                
                # Accumulate performance metrics
                if log.generation_time_ms:
                    total_generation_time += log.generation_time_ms
                    generation_time_count += 1
                
                if log.token_count:
                    total_token_count += log.token_count
                    token_count_count += 1
                
                # Count successful generations
                if log.is_successful():
                    successful_count += 1
                
                # Analyze errors
                if log.error_message:
                    error_type = log.error_code or "unknown"
                    stats["error_analysis"][error_type] = stats["error_analysis"].get(error_type, 0) + 1
            
            # Calculate averages
            if generation_time_count > 0:
                stats["performance_metrics"]["average_generation_time"] = total_generation_time / generation_time_count
            
            if token_count_count > 0:
                stats["performance_metrics"]["average_token_count"] = total_token_count / token_count_count
            
            if quality_count > 0:
                stats["performance_metrics"]["average_quality_score"] = total_quality_score / quality_count
            
            # Calculate success rate
            if logs:
                stats["success_rate"] = (successful_count / len(logs)) * 100
            
            # Calculate model performance
            for model, count in stats["by_model"].items():
                model_logs = [log for log in logs if log.generation_model == model]
                if model_logs:
                    avg_time = sum(log.generation_time_ms or 0 for log in model_logs) / len(model_logs)
                    avg_quality = sum(log.quality_score or 0 for log in model_logs) / len(model_logs)
                    success_count = sum(1 for log in model_logs if log.is_successful())
                    
                    stats["model_performance"][model] = {
                        "count": count,
                        "average_generation_time": avg_time,
                        "average_quality_score": avg_quality,
                        "success_rate": (success_count / len(model_logs)) * 100
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating generation statistics: {e}")
            return {}
    
    # Private helper methods
    
    async def _validate_generation_data(self, generation_data: Dict[str, Any]) -> bool:
        """Validate generation data before processing"""
        try:
            # Check required fields
            if not generation_data.get('registry_id'):
                logger.error("Missing registry_id")
                return False
            
            if not generation_data.get('session_id'):
                logger.error("Missing session_id")
                return False
            
            if not generation_data.get('generation_type'):
                logger.error("Missing generation_type")
                return False
            
            if not generation_data.get('generation_model'):
                logger.error("Missing generation_model")
                return False
            
            # Check generation type
            gen_type = generation_data.get('generation_type')
            if gen_type and gen_type not in ["text", "code", "image", "audio", "video", "multimodal"]:
                logger.error(f"Invalid generation type: {gen_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Generation data validation error: {e}")
            return False
    
    async def _process_generation_data(self, generation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance generation data"""
        try:
            processed_data = generation_data.copy()
            
            # Set default values
            if 'generation_time_ms' not in processed_data:
                processed_data['generation_time_ms'] = 0
            
            if 'token_count' not in processed_data:
                processed_data['token_count'] = 0
            
            if 'cost_credits' not in processed_data:
                processed_data['cost_credits'] = 0.0
            
            if 'quality_score' not in processed_data:
                processed_data['quality_score'] = 0.8  # Default quality
            
            if 'relevance_score' not in processed_data:
                processed_data['relevance_score'] = 0.8  # Default relevance
            
            if 'coherence_score' not in processed_data:
                processed_data['coherence_score'] = 0.8  # Default coherence
            
            if 'accuracy_score' not in processed_data:
                processed_data['accuracy_score'] = 0.8  # Default accuracy
            
            if 'retry_count' not in processed_data:
                processed_data['retry_count'] = 0
            
            # Set generation timestamp if not present
            if 'generated_at' not in processed_data:
                processed_data['generated_at'] = datetime.now().isoformat()
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing generation data: {e}")
            return generation_data
    
    async def _validate_generation_log(self, generation_log: GenerationLog) -> bool:
        """Validate generation log before database operations"""
        try:
            # Check required fields
            if not generation_log.registry_id:
                logger.error("Generation log missing registry_id")
                return False
            
            if not generation_log.session_id:
                logger.error("Generation log missing session_id")
                return False
            
            if not generation_log.generation_type:
                logger.error("Generation log missing generation_type")
                return False
            
            if not generation_log.generation_model:
                logger.error("Generation log missing generation_model")
                return False
            
            # Check value ranges
            if generation_log.quality_score is not None and (generation_log.quality_score < 0 or generation_log.quality_score > 1):
                logger.error("Quality score out of valid range")
                return False
            
            if generation_log.relevance_score is not None and (generation_log.relevance_score < 0 or generation_log.relevance_score > 1):
                logger.error("Relevance score out of valid range")
                return False
            
            if generation_log.coherence_score is not None and (generation_log.coherence_score < 0 or generation_log.coherence_score > 1):
                logger.error("Coherence score out of valid range")
                return False
            
            if generation_log.accuracy_score is not None and (generation_log.accuracy_score < 0 or generation_log.accuracy_score > 1):
                logger.error("Accuracy score out of valid range")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Generation log validation error: {e}")
            return False
    
    async def _calculate_generation_quality(self, generation_log: GenerationLog) -> None:
        """Calculate quality scores for generation"""
        try:
            # Calculate overall quality score if individual scores are available
            if all(score is not None for score in [
                generation_log.quality_score,
                generation_log.relevance_score,
                generation_log.coherence_score,
                generation_log.accuracy_score
            ]):
                overall_score = (
                    generation_log.quality_score * 0.3 +
                    generation_log.relevance_score * 0.3 +
                    generation_log.coherence_score * 0.2 +
                    generation_log.accuracy_score * 0.2
                )
                generation_log.quality_score = overall_score
            
            # Set default tags if not present
            if not generation_log.tags:
                generation_log.tags = ["auto_generated"]
            
            # Set default flags if not present
            if not generation_log.flags:
                generation_log.flags = ["standard"]
                
        except Exception as e:
            logger.warning(f"Error calculating generation quality: {e}")
    
    async def _enhance_generation_data(self, generation_log: GenerationLog) -> None:
        """Enhance generation log with additional computed data"""
        try:
            # Add generation summary if not present
            if not hasattr(generation_log, 'generation_summary') and generation_log.generated_content:
                content = generation_log.generated_content
                if isinstance(content, str):
                    generation_log.generation_summary = content[:100] + "..." if len(content) > 100 else content
                else:
                    generation_log.generation_summary = str(content)[:100] + "..."
            
            # Add prompt summary if not present
            if not hasattr(generation_log, 'prompt_summary') and generation_log.generation_prompt:
                prompt = generation_log.generation_prompt
                generation_log.prompt_summary = prompt[:100] + "..." if len(prompt) > 100 else prompt
                
        except Exception as e:
            logger.warning(f"Error enhancing generation data: {e}")
    
    async def _validate_feedback_data(self, feedback_data: Dict[str, Any]) -> bool:
        """Validate user feedback data"""
        try:
            # Check required fields
            if not feedback_data.get("rating"):
                logger.error("Missing user rating")
                return False
            
            # Check rating range
            rating = feedback_data.get("rating")
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                logger.error("Invalid rating value, must be 1-5")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Feedback data validation error: {e}")
            return False
