"""
AASX Processing Service

Manages AASX extraction and generation job tracking using the new architecture.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import uuid

from ..models.aasx_processing import AasxProcessing, create_aasx_processing_job
from ..repositories.aasx_processing_repository import AasxProcessingRepository
from src.engine.database.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class AASXProcessingService:
    """Service for managing AASX processing jobs using the new architecture."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize the service with connection manager.
        
        Args:
            connection_manager: Engine connection manager instance
        """
        self.connection_manager = connection_manager
        self.repository = AasxProcessingRepository(connection_manager)
        logger.info("AASXProcessingService initialized with new architecture")
    
    async def create_job(self, job_data: Dict[str, Any]) -> str:
        """
        Create a new processing job using the new architecture.
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            str: Created job ID
        """
        try:
            # Create Pydantic model instance
            job = create_aasx_processing_job(**job_data)
            
            # Save to database via repository
            job_id = await self.repository.create(job)
            
            logger.info(f"Created processing job {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create processing job: {e}")
            raise
    
    async def create_job_from_file_upload(self, file_id: str, file_path: str, 
                                        priority: str = "normal", project_id: str = "default_project",
                                        processed_by: str = "system", org_id: str = "default_org",
                                        dept_id: Optional[str] = None) -> str:
        """
        Automatically create a processing job when a file is uploaded.
        
        Args:
            file_id: ID of the uploaded file
            file_path: Path to the uploaded file
            priority: Processing priority (low, normal, high, critical)
            project_id: Project ID (required by schema)
            processed_by: User ID who processed the job (required by schema)
            org_id: Organization ID (required by schema)
            dept_id: Department ID for complete traceability
            
        Returns:
            str: Created job ID
        """
        try:
            # Prepare job data for automatic creation with ALL required columns
            job_data = {
                # Primary Identification (REQUIRED)
                "job_id": f"job_{uuid.uuid4().hex[:8]}",
                "file_id": file_id,
                "project_id": project_id,
                
                # Job Classification & Metadata (REQUIRED)
                "job_type": "extraction",  # Default to extraction for file uploads
                "source_type": "manual_upload",  # Default source type
                "processing_status": "pending",  # Correct column name from schema
                "processing_priority": priority,
                "job_version": "1.0.0",
                
                # Workflow Classification
                "workflow_type": "standard",
                "processing_mode": "asynchronous",
                
                # Module Integration References
                "twin_registry_id": None,
                "kg_neo4j_id": None,
                "ai_rag_id": None,
                "physics_modeling_id": None,
                "federated_learning_id": None,
                "certificate_manager_id": None,
                
                # Integration Status & Health
                "integration_status": "pending",
                "overall_health_score": 0,
                "health_status": "unknown",
                
                # Lifecycle Management
                "lifecycle_status": "created",
                "lifecycle_phase": "development",
                
                # Operational Status
                "operational_status": "stopped",
                "availability_status": "offline",
                
                # AASX-Specific Processing Status
                "extraction_status": "pending",
                "generation_status": "pending",
                "validation_status": "pending",
                "last_extraction_at": None,
                "last_generation_at": None,
                "last_validation_at": None,
                
                # Processing Configuration (JSON)
                "extraction_options": {},
                "generation_options": {},
                "validation_options": {},
                
                # Processing Results (JSON)
                "extraction_results": {},
                "generation_results": {},
                "validation_results": {},
                
                # Performance & Quality Metrics
                "processing_time": 0.0,
                "extraction_time": 0.0,
                "generation_time": 0.0,
                "validation_time": 0.0,
                "data_quality_score": 0.0,
                "processing_accuracy": 0.0,
                "file_integrity_checksum": None,
                
                # Security & Access Control
                "security_level": "standard",
                "access_control_level": "user",
                "encryption_enabled": False,
                "audit_logging_enabled": True,
                
                # User Management & Ownership (REQUIRED)
                "processed_by": processed_by,
                "org_id": org_id,
                "dept_id": dept_id,
                "owner_team": None,
                "steward_user_id": None,
                
                # Timestamps & Audit (REQUIRED)
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "activated_at": None,
                "last_accessed_at": None,
                "last_modified_at": None,
                "timestamp": datetime.utcnow().isoformat(),
                
                # Output & Storage
                "output_directory": str(file_path),  # Use file_path as output directory
                
                # Error Handling
                "error_message": None,
                "error_code": None,
                "retry_count": 0,
                "max_retries": 3,
                
                # Federated Learning & Consent
                "federated_learning": "not_allowed",
                "user_consent_timestamp": None,
                "consent_terms_version": "1.0",
                "federated_participation_status": "inactive",
                
                # Configuration & Metadata (JSON)
                "processing_config": {
                    "source": "file_upload_trigger",
                    "file_path": str(file_path),
                    "auto_created": True
                },
                "processing_metadata": {
                    "upload_timestamp": datetime.utcnow().isoformat(),
                    "trigger_type": "file_upload",
                    "batch_eligible": True
                },
                "custom_attributes": {},
                "tags_config": {
                    "tags": ["aasx", "auto_created", "file_upload"],
                    "categories": ["data_processing", "automation"]
                },
                
                # Relationships & Dependencies (JSON)
                "relationships_config": {},
                "dependencies_config": {},
                "processing_instances_config": {}
            }
            
            # Create the job
            job_id = await self.create_job(job_data)
            
            logger.info(f"Auto-created processing job {job_id} for file {file_id} with all required columns")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to auto-create job for file {file_id}: {e}")
            raise
    
    async def create_batch_job(self, files: List[str], 
                              batch_metadata: Optional[Dict[str, Any]] = None,
                              project_id: str = "default_project",
                              processed_by: str = "system", 
                              org_id: str = "default_org",
                              dept_id: Optional[str] = None) -> str:
        """
        Create a batch processing job for multiple files.
        
        Args:
            files: List of file IDs to process in batch
            batch_metadata: Additional metadata for the batch
            project_id: Project ID (required by schema)
            processed_by: User ID who processed the job (required by schema)
            org_id: Organization ID (required by schema)
            dept_id: Department ID for complete traceability
            
        Returns:
            str: Created batch job ID
        """
        try:
            # Prepare batch job data with ALL required columns
            batch_data = {
                # Primary Identification (REQUIRED)
                "job_id": f"batch_{uuid.uuid4().hex[:8]}",
                "file_id": files[0],  # Primary file ID for the batch
                "project_id": project_id,
                
                # Job Classification & Metadata (REQUIRED)
                "job_type": "extraction",  # Default to extraction for batch jobs
                "source_type": "batch_upload",  # Batch source type
                "processing_status": "pending",  # Correct column name from schema
                "processing_priority": "normal",
                "job_version": "1.0.0",
                
                # Workflow Classification
                "workflow_type": "batch",
                "processing_mode": "batch",
                
                # Module Integration References
                "twin_registry_id": None,
                "kg_neo4j_id": None,
                "ai_rag_id": None,
                "physics_modeling_id": None,
                "federated_learning_id": None,
                "certificate_manager_id": None,
                
                # Integration Status & Health
                "integration_status": "pending",
                "overall_health_score": 0,
                "health_status": "unknown",
                
                # Lifecycle Management
                "lifecycle_status": "created",
                "lifecycle_phase": "development",
                
                # Operational Status
                "operational_status": "stopped",
                "availability_status": "offline",
                
                # AASX-Specific Processing Status
                "extraction_status": "pending",
                "generation_status": "pending",
                "validation_status": "pending",
                "last_extraction_at": None,
                "last_generation_at": None,
                "last_validation_at": None,
                
                # Processing Configuration (JSON)
                "extraction_options": {
                    "batch_mode": True,
                    "batch_size": len(files),
                    "parallel_processing": True
                },
                "generation_options": {},
                "validation_options": {},
                
                # Processing Results (JSON)
                "extraction_results": {},
                "generation_results": {},
                "validation_results": {},
                
                # Performance & Quality Metrics
                "processing_time": 0.0,
                "extraction_time": 0.0,
                "generation_time": 0.0,
                "validation_time": 0.0,
                "data_quality_score": 0.0,
                "processing_accuracy": 0.0,
                "file_integrity_checksum": None,
                
                # Security & Access Control
                "security_level": "standard",
                "access_control_level": "user",
                "encryption_enabled": False,
                "audit_logging_enabled": True,
                
                # User Management & Ownership (REQUIRED)
                "processed_by": processed_by,
                "org_id": org_id,
                "dept_id": dept_id,
                "owner_team": None,
                "steward_user_id": None,
                
                # Timestamps & Audit (REQUIRED)
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "activated_at": None,
                "last_accessed_at": None,
                "last_modified_at": None,
                "timestamp": datetime.utcnow().isoformat(),
                
                # Output & Storage
                "output_directory": f"batch_processing_{len(files)}_files",
                
                # Error Handling
                "error_message": None,
                "error_code": None,
                "retry_count": 0,
                "max_retries": 3,
                
                # Federated Learning & Consent
                "federated_learning": "not_allowed",
                "user_consent_timestamp": None,
                "consent_terms_version": "1.0",
                "federated_participation_status": "inactive",
                
                # Configuration & Metadata (JSON)
                "processing_config": {
                    "source": "batch_detection_trigger",
                    "batch_size": len(files),
                    "auto_created": True,
                    "batch_metadata": batch_metadata or {}
                },
                "processing_metadata": {
                    "batch_creation_timestamp": datetime.utcnow().isoformat(),
                    "trigger_type": "batch_detection",
                    "file_count": len(files),
                    "file_ids": files
                },
                "custom_attributes": {
                    "batch_processing": True,
                    "estimated_processing_time": len(files) * 5.0  # 5 seconds per file estimate
                },
                "tags_config": {
                    "tags": ["aasx", "batch", "auto_created", "batch_processing"],
                    "categories": ["data_processing", "automation", "batch"],
                    "keywords": ["extraction", "batch", "efficiency"]
                },
                
                # Relationships & Dependencies (JSON)
                "relationships_config": {
                    "batch_files": files,
                    "batch_relationships": "sequential_processing"
                },
                "dependencies_config": {
                    "required_modules": ["file_processor", "aasx_validator"],
                    "batch_dependencies": "all_files_available"
                },
                "processing_instances_config": {
                    "batch_instance": True,
                    "instance_count": 1
                }
            }
            
            # Create the batch job
            job_id = await self.create_job(batch_data)
            
            logger.info(f"Created batch job {job_id} for {len(files)} files with all required columns")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create batch job: {e}")
            raise
    
    async def get_job_by_id(self, job_id: str) -> Optional[AasxProcessing]:
        """
        Get a processing job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Optional[AasxProcessing]: Job instance or None
        """
        try:
            return await self.repository.get_by_id(job_id)
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    async def update_job_status(self, job_id: str, status: str, 
                               additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update job status and additional data.
        
        Args:
            job_id: Job identifier
            status: New status
            additional_data: Additional data to update
            
        Returns:
            bool: True if update successful
        """
        try:
            # Get current job
            job = await self.repository.get_by_id(job_id)
            if not job:
                logger.warning(f"Job {job_id} not found for status update")
                return False
            
            # Update job data
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if additional_data:
                update_data.update(additional_data)
            
            # Update via repository
            await self.repository.update(job_id, update_data)
            
            logger.info(f"Updated job {job_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {e}")
            return False
    
    async def start_processing(self, job_id: str) -> bool:
        """
        Start processing a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: True if processing started successfully
        """
        try:
            # Update status to processing
            update_data = {
                "status": "processing",
                "processing_started_at": datetime.utcnow()
            }
            
            success = await self.update_job_status(job_id, "processing", update_data)
            
            if success:
                logger.info(f"Started processing job {job_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to start processing job {job_id}: {e}")
            return False
    
    async def complete_processing(self, job_id: str, results: Dict[str, Any]) -> bool:
        """
        Mark job as completed with results.
        
        Args:
            job_id: Job identifier
            results: Processing results
            
        Returns:
            bool: True if completion recorded successfully
        """
        try:
            # Update status to completed
            update_data = {
                "status": "completed",
                "processing_completed_at": datetime.utcnow(),
                "results": results,
                "completion_status": "success"
            }
            
            success = await self.update_job_status(job_id, "completed", update_data)
            
            if success:
                logger.info(f"Completed processing job {job_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
            return False
    
    async def fail_processing(self, job_id: str, error: str, 
                             error_details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Mark job as failed with error information.
        
        Args:
            job_id: Job identifier
            error: Error message
            error_details: Additional error details
            
        Returns:
            bool: True if failure recorded successfully
        """
        try:
            # Update status to failed
            update_data = {
                "status": "failed",
                "processing_completed_at": datetime.utcnow(),
                "error_message": error,
                "error_details": error_details or {},
                "completion_status": "failure"
            }
            
            success = await self.update_job_status(job_id, "failed", update_data)
            
            if success:
                logger.info(f"Marked job {job_id} as failed: {error}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to mark job {job_id} as failed: {e}")
            return False
    
    async def get_pending_jobs(self, limit: int = 100) -> List[AasxProcessing]:
        """
        Get pending jobs for processing.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List[AasxProcessing]: List of pending jobs
        """
        try:
            return await self.repository.get_by_status("pending", limit=limit)
        except Exception as e:
            logger.error(f"Failed to get pending jobs: {e}")
            return []
    
    async def get_jobs_by_status(self, status: str, limit: int = 100) -> List[AasxProcessing]:
        """
        Get jobs by status.
        
        Args:
            status: Job status to filter by
            limit: Maximum number of jobs to return
            
        Returns:
            List[AasxProcessing]: List of jobs with specified status
        """
        try:
            return await self.repository.get_by_status(status, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get jobs by status {status}: {e}")
            return []
    
    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a processing job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: True if deletion successful
        """
        try:
            await self.repository.delete(job_id)
            logger.info(f"Deleted processing job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    async def get_job_statistics(self) -> Dict[str, Any]:
        """
        Get processing job statistics.
        
        Returns:
            Dict[str, Any]: Job statistics
        """
        try:
            stats = await self.repository.get_statistics()
            return stats
        except Exception as e:
            logger.error(f"Failed to get job statistics: {e}")
            return {}
    
    async def cleanup_old_jobs(self, days_old: int = 30) -> int:
        """
        Clean up old completed/failed jobs.
        
        Args:
            days_old: Age threshold in days
            
        Returns:
            int: Number of jobs cleaned up
        """
        try:
            count = await self.repository.cleanup_old_jobs(days_old)
            logger.info(f"Cleaned up {count} old jobs")
            return count
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
            return 0
