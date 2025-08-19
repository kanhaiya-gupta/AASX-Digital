"""
AASX Processing Service
Manages AASX extraction and generation job tracking.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from ...shared.database.base_manager import BaseDatabaseManager

logger = logging.getLogger(__name__)

class AASXProcessingService:
    """Service for managing AASX processing jobs."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        self.db_manager = db_manager
    
    def create_job(self, job_data: Dict[str, Any]) -> str:
        """
        Create a new processing job.
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            str: The created job ID (UUID)
            
        Raises:
            Exception: If job creation fails
        """
        try:
            # Validate required fields
            required_fields = ['file_id', 'project_id', 'job_type', 'source_type', 'processed_by']
            for field in required_fields:
                if field not in job_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate UUID for job_id
            import uuid
            job_id = str(uuid.uuid4())
            
            # Set default values
            job_data.setdefault('processing_status', 'pending')
            job_data.setdefault('extraction_options', '{}')
            job_data.setdefault('generation_options', '{}')
            job_data.setdefault('timestamp', datetime.now().isoformat())
            
            # Convert options to JSON strings if they aren't already
            if isinstance(job_data['extraction_options'], dict):
                job_data['extraction_options'] = json.dumps(job_data['extraction_options'])
            if isinstance(job_data['generation_options'], dict):
                job_data['generation_options'] = json.dumps(job_data['generation_options'])
            
            # Insert job record with UUID job_id
            query = """
                INSERT INTO aasx_processing (
                    job_id, file_id, project_id, processing_status, job_type, source_type,
                    processed_by, org_id, federated_learning, user_consent_timestamp,
                    consent_terms_version, federated_participation_status,
                    extraction_options, generation_options, timestamp, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            current_time = datetime.now().isoformat()
            params = (
                job_id,  # Include the generated UUID job_id
                job_data['file_id'],
                job_data['project_id'],
                job_data['processing_status'],
                job_data['job_type'],
                job_data['source_type'],
                job_data['processed_by'],
                job_data.get('org_id'),
                job_data.get('federated_learning', 'not_allowed'),
                job_data.get('user_consent_timestamp'),
                job_data.get('consent_terms_version', '1.0'),
                job_data.get('federated_participation_status', 'inactive'),
                job_data['extraction_options'],
                job_data['generation_options'],
                job_data['timestamp'],
                current_time,
                current_time
            )
            
            self.db_manager.execute_update(query, params)
            
            logger.info(f"Created AASX processing job {job_id} for file {job_data['file_id']}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create AASX processing job: {e}")
            raise
    
    def update_status(self, job_id: str, status: str, additional_data: Dict[str, Any] = None) -> bool:
        """
        Update job status and optional additional data.
        
        Args:
            job_id: The job ID to update
            status: New status (pending, processing, completed, failed)
            additional_data: Optional additional data to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            update_fields = ["processing_status = ?"]
            params = [status]
            
            if additional_data:
                for key, value in additional_data.items():
                    if key in ['processing_time', 'output_directory', 'error_message']:
                        update_fields.append(f"{key} = ?")
                        params.append(value)
            
            # Add timestamp update
            update_fields.append("timestamp = ?")
            params.append(datetime.now().isoformat())
            
            # Add job_id to params
            params.append(job_id)
            
            query = f"""
                UPDATE aasx_processing 
                SET {', '.join(update_fields)}
                WHERE job_id = ?
            """
            
            self.db_manager.execute_update(query, params)
            
            logger.info(f"Updated job {job_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job information by job_id.
        
        Args:
            job_id: The job ID to retrieve
            
        Returns:
            Dict containing job information or None if not found
        """
        try:
            query = "SELECT * FROM aasx_processing WHERE job_id = ?"
            results = self.db_manager.execute_query(query, (job_id,))
            
            if results:
                return dict(results[0])  # Convert sqlite3.Row to dict
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    def complete_job(self, job_id: str, results: Dict[str, Any], 
                    status: str = 'completed', error_message: str = None,
                    federated_learning_update: Dict[str, Any] = None) -> bool:
        """
        Mark job as completed with results and optional federated learning updates.
        
        Args:
            job_id: The job ID to complete
            results: Results data (extraction_results or generation_results)
            status: Final status (completed or failed)
            error_message: Error message if status is failed
            federated_learning_update: Optional federated learning consent updates
            
        Returns:
            bool: True if completion successful, False otherwise
        """
        try:
            # Get job type to determine which results field to update
            job_info = self.get_job(job_id)
            if not job_info:
                logger.error(f"Job {job_id} not found")
                return False
            
            job_type = job_info['job_type']
            
            # Prepare update data
            update_data = {
                'processing_status': status,
                'timestamp': datetime.now().isoformat()
            }
            
            if error_message:
                update_data['error_message'] = error_message
            
            # Add results to appropriate field
            if job_type == 'extraction':
                update_data['extraction_results'] = json.dumps(results) if isinstance(results, dict) else results
            elif job_type == 'generation':
                update_data['generation_results'] = json.dumps(results) if isinstance(results, dict) else results
            
            # Update the job status and results
            success = self.update_status(job_id, status, update_data)
            
            # If successful and federated learning update is provided, update consent
            if success and federated_learning_update and status == 'completed':
                try:
                    consent_success = self.update_federated_learning_consent(job_id, federated_learning_update)
                    if consent_success:
                        logger.info(f"Updated federated learning consent for completed job {job_id}")
                    else:
                        logger.warning(f"Failed to update federated learning consent for job {job_id}")
                except Exception as consent_error:
                    logger.error(f"Error updating federated learning consent for job {job_id}: {consent_error}")
                    # Don't fail the job completion if consent update fails
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job details by ID.
        
        Args:
            job_id: The job ID to retrieve
            
        Returns:
            Dict: Job data or None if not found
        """
        try:
            query = "SELECT * FROM aasx_processing WHERE id = ?"
            result = self.db_manager.execute_query(query, (job_id,))
            
            if result:
                job_data = result[0]
                # Parse JSON fields
                if job_data['extraction_options']:
                    try:
                        job_data['extraction_options'] = json.loads(job_data['extraction_options'])
                    except json.JSONDecodeError:
                        pass
                
                if job_data['generation_options']:
                    try:
                        job_data['generation_options'] = json.loads(job_data['generation_options'])
                    except json.JSONDecodeError:
                        pass
                
                if job_data['extraction_results']:
                    try:
                        job_data['extraction_results'] = json.loads(job_data['extraction_results'])
                    except json.JSONDecodeError:
                        pass
                
                if job_data['generation_results']:
                    try:
                        job_data['generation_results'] = json.loads(job_data['generation_results'])
                    except json.JSONDecodeError:
                        pass
                
                return job_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    def get_job_history(self, user_id: str = None, project_id: str = None, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get processing job history.
        
        Args:
            user_id: Filter by user ID
            project_id: Filter by project ID
            limit: Maximum number of jobs to return
            
        Returns:
            List: List of job records
        """
        try:
            query = "SELECT * FROM aasx_processing WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND processed_by = ?"
                params.append(user_id)
            
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            results = self.db_manager.execute_query(query, params)
            
            # Parse JSON fields for all results
            for job in results:
                for field in ['extraction_options', 'generation_options', 'extraction_results', 'generation_results']:
                    if job[field]:
                        try:
                            job[field] = json.loads(job[field])
                        except json.JSONDecodeError:
                            pass
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get job history: {e}")
            return []
    
    def get_jobs_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get jobs by processing status.
        
        Args:
            status: Status to filter by
            limit: Maximum number of jobs to return
            
        Returns:
            List: List of jobs with specified status
        """
        try:
            query = """
                SELECT * FROM aasx_processing 
                WHERE processing_status = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            
            results = self.db_manager.execute_query(query, (status, limit))
            
            # Parse JSON fields
            for job in results:
                for field in ['extraction_options', 'generation_options', 'extraction_results', 'generation_results']:
                    if job[field]:
                        try:
                            job[field] = json.loads(job[field])
                        except json.JSONDecodeError:
                            pass
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get jobs by status {status}: {e}")
            return []
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific job by ID.
        
        Args:
            job_id: The job ID to retrieve
            
        Returns:
            Dict: Job data or None if not found
        """
        try:
            query = """
                SELECT * FROM aasx_processing 
                WHERE id = ?
            """
            
            results = self.db_manager.execute_query(query, (job_id,))
            
            if not results:
                return None
            
            job = results[0]
            
            # Parse JSON fields
            for field in ['extraction_options', 'generation_options', 'extraction_results', 'generation_results']:
                if job[field]:
                    try:
                        job[field] = json.loads(job[field])
                    except json.JSONDecodeError:
                        pass
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job record.
        
        Args:
            job_id: The job ID to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            query = "DELETE FROM aasx_processing WHERE id = ?"
            self.db_manager.execute_update(query, (job_id,))
            
            logger.info(f"Deleted job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    def get_job_statistics(self, user_id: str = None, project_id: str = None) -> Dict[str, Any]:
        """
        Get job processing statistics.
        
        Args:
            user_id: Filter by user ID
            project_id: Filter by project ID
            
        Returns:
            Dict: Statistics summary
        """
        try:
            where_clause = "WHERE 1=1"
            params = []
            
            if user_id:
                where_clause += " AND processed_by = ?"
                params.append(user_id)
            
            if project_id:
                where_clause += " AND project_id = ?"
                params.append(project_id)
            
            # Get counts by status
            status_query = f"""
                SELECT processing_status, COUNT(*) as count 
                FROM aasx_processing 
                {where_clause}
                GROUP BY processing_status
            """
            
            status_results = self.db_manager.execute_query(status_query, params)
            
            # Get counts by job type
            type_query = f"""
                SELECT job_type, COUNT(*) as count 
                FROM aasx_processing 
                {where_clause}
                GROUP BY job_type
            """
            
            type_results = self.db_manager.execute_query(type_query, params)
            
            # Get average processing time
            time_query = f"""
                SELECT AVG(processing_time) as avg_time 
                FROM aasx_processing 
                {where_clause} AND processing_time IS NOT NULL
            """
            
            time_result = self.db_manager.execute_query(time_query, params)
            avg_time = time_result[0]['avg_time'] if time_result and time_result[0]['avg_time'] else 0
            
            # Build statistics
            stats = {
                'total_jobs': sum(r['count'] for r in status_results),
                'by_status': {r['processing_status']: r['count'] for r in status_results},
                'by_type': {r['job_type']: r['count'] for r in type_results},
                'average_processing_time': avg_time
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get job statistics: {e}")
            return {}
    
    def update_federated_learning_consent(self, job_id: str, consent_data: Dict[str, Any]) -> bool:
        """
        Update federated learning consent for a processing job.
        
        Args:
            job_id: The job ID to update
            consent_data: Dictionary containing consent information
                - federated_learning: 'allowed', 'not_allowed', or 'conditional'
                - user_consent_timestamp: ISO timestamp when consent was given
                - consent_terms_version: Version of consent terms
                - federated_participation_status: 'active' or 'inactive'
                
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Validate consent data
            if 'federated_learning' in consent_data:
                valid_values = ['allowed', 'not_allowed', 'conditional']
                if consent_data['federated_learning'] not in valid_values:
                    raise ValueError(f"Invalid federated_learning value. Must be one of: {valid_values}")
            
            if 'federated_participation_status' in consent_data:
                valid_statuses = ['active', 'inactive']
                if consent_data['federated_participation_status'] not in valid_statuses:
                    raise ValueError(f"Invalid federated_participation_status. Must be one of: {valid_statuses}")
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            for field in ['federated_learning', 'user_consent_timestamp', 'consent_terms_version', 'federated_participation_status']:
                if field in consent_data:
                    update_fields.append(f"{field} = ?")
                    params.append(consent_data[field])
            
            if not update_fields:
                raise ValueError("No valid fields to update")
            
            # Add timestamp and job_id
            update_fields.append("updated_at = datetime('now')")
            params.append(job_id)
            
            query = f"""
                UPDATE aasx_processing 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """
            
            affected_rows = self.db_manager.execute_update(query, params)
            
            if affected_rows > 0:
                logger.info(f"Updated federated learning consent for job {job_id}")
                return True
            else:
                logger.warning(f"No rows updated for job {job_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update federated learning consent for job {job_id}: {e}")
            return False
    
    def get_federated_learning_stats(self, user_id: str = None, project_id: str = None) -> Dict[str, Any]:
        """
        Get federated learning consent statistics.
        
        Args:
            user_id: Filter by user ID
            project_id: Filter by project ID
            
        Returns:
            Dict: Federated learning statistics
        """
        try:
            where_clause = "WHERE 1=1"
            params = []
            
            if user_id:
                where_clause += " AND processed_by = ?"
                params.append(user_id)
            
            if project_id:
                where_clause += " AND project_id = ?"
                params.append(project_id)
            
            # Get counts by federated learning status
            fl_query = f"""
                SELECT federated_learning, COUNT(*) as count 
                FROM aasx_processing 
                {where_clause}
                GROUP BY federated_learning
            """
            
            fl_results = self.db_manager.execute_query(fl_query, params)
            
            # Get counts by participation status
            participation_query = f"""
                SELECT federated_participation_status, COUNT(*) as count 
                FROM aasx_processing 
                {where_clause}
                GROUP BY federated_participation_status
            """
            
            participation_results = self.db_manager.execute_query(participation_query, params)
            
            # Build statistics
            stats = {
                'total_jobs': sum(r['count'] for r in fl_results),
                'by_federated_learning': {r['federated_learning']: r['count'] for r in fl_results},
                'by_participation_status': {r['federated_participation_status']: r['count'] for r in participation_results}
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get federated learning statistics: {e}")
            return {}
    
    def determine_federated_learning_consent(self, job_id: str, etl_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically determine federated learning consent based on ETL processing results.
        This method analyzes the results and suggests appropriate consent levels.
        
        Args:
            job_id: The job ID to analyze
            etl_results: Results from ETL processing
            
        Returns:
            Dict: Suggested federated learning consent settings
        """
        try:
            # Get the original job info
            job_info = self.get_job(job_id)
            if not job_info:
                logger.error(f"Job {job_id} not found for consent determination")
                return {}
            
            # Default consent settings
            consent_settings = {
                'federated_learning': 'not_allowed',
                'federated_participation_status': 'inactive',
                'user_consent_timestamp': None,
                'consent_terms_version': '1.0'
            }
            
            # Analyze ETL results to determine consent level
            if etl_results:
                # Check data sensitivity based on content
                data_sensitivity = self._analyze_data_sensitivity(etl_results)
                
                # Check data quality and completeness
                data_quality = self._analyze_data_quality(etl_results)
                
                # Determine consent level based on analysis
                if data_sensitivity == 'low' and data_quality == 'high':
                    consent_settings['federated_learning'] = 'allowed'
                    consent_settings['federated_participation_status'] = 'active'
                elif data_sensitivity == 'medium' and data_quality == 'high':
                    consent_settings['federated_learning'] = 'conditional'
                    consent_settings['federated_participation_status'] = 'inactive'
                else:
                    consent_settings['federated_learning'] = 'not_allowed'
                    consent_settings['federated_participation_status'] = 'inactive'
                
                # Set consent timestamp if consent is allowed
                if consent_settings['federated_learning'] in ['allowed', 'conditional']:
                    consent_settings['user_consent_timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Determined federated learning consent for job {job_id}: {consent_settings['federated_learning']}")
            return consent_settings
            
        except Exception as e:
            logger.error(f"Failed to determine federated learning consent for job {job_id}: {e}")
            return {}
    
    def _analyze_data_sensitivity(self, etl_results: Dict[str, Any]) -> str:
        """
        Analyze data sensitivity from ETL results.
        
        Args:
            etl_results: Results from ETL processing
            
        Returns:
            str: Sensitivity level ('low', 'medium', 'high')
        """
        try:
            # This is a simplified analysis - in production, you'd want more sophisticated logic
            sensitivity_score = 0
            
            # Check for sensitive keywords in results
            sensitive_keywords = ['password', 'token', 'key', 'secret', 'private', 'confidential']
            results_text = str(etl_results).lower()
            
            for keyword in sensitive_keywords:
                if keyword in results_text:
                    sensitivity_score += 2
            
            # Check data size (larger datasets might be more sensitive)
            if 'size' in etl_results and etl_results['size'] > 1000000:  # 1MB
                sensitivity_score += 1
            
            # Determine sensitivity level
            if sensitivity_score == 0:
                return 'low'
            elif sensitivity_score <= 3:
                return 'medium'
            else:
                return 'high'
                
        except Exception as e:
            logger.error(f"Error analyzing data sensitivity: {e}")
            return 'high'  # Default to high sensitivity on error
    
    def _analyze_data_quality(self, etl_results: Dict[str, Any]) -> str:
        """
        Analyze data quality from ETL results.
        
        Args:
            etl_results: Results from ETL processing
            
        Returns:
            str: Quality level ('low', 'medium', 'high')
        """
        try:
            # This is a simplified analysis - in production, you'd want more sophisticated logic
            quality_score = 0
            
            # Check if results contain expected fields
            if 'status' in etl_results and etl_results['status'] == 'success':
                quality_score += 2
            
            # Check for completeness indicators
            if 'completeness' in etl_results:
                quality_score += 1
            
            # Check for validation results
            if 'validation' in etl_results and etl_results['validation']:
                quality_score += 1
            
            # Determine quality level
            if quality_score >= 3:
                return 'high'
            elif quality_score >= 1:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error analyzing data quality: {e}")
            return 'low'  # Default to low quality on error
    
    def complete_job_with_auto_consent(self, job_id: str, results: Dict[str, Any], 
                                      status: str = 'completed', error_message: str = None) -> bool:
        """
        Complete a job and automatically determine federated learning consent based on results.
        This is a convenience method that combines job completion with consent determination.
        
        Args:
            job_id: The job ID to complete
            results: Results data from ETL processing
            status: Final status (completed or failed)
            error_message: Error message if status is failed
            
        Returns:
            bool: True if completion successful, False otherwise
        """
        try:
            # Only determine consent for successful completions
            if status == 'completed' and not error_message:
                # Automatically determine consent based on ETL results
                consent_settings = self.determine_federated_learning_consent(job_id, results)
                
                # Complete the job with the determined consent settings
                return self.complete_job(job_id, results, status, error_message, consent_settings)
            else:
                # For failed jobs, just complete without consent updates
                return self.complete_job(job_id, results, status, error_message)
                
        except Exception as e:
            logger.error(f"Failed to complete job {job_id} with auto consent: {e}")
            return False
