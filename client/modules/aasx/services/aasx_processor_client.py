"""
AASX Processor Client - Thin Client Wrapper
==========================================

Thin client wrapper around src.modules.aasx.services.aasx_processing_service
Provides client-specific interface for AASX processing operations.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Import from engine services
try:
    from src.modules.aasx.services import AASXProcessingService
    from src.modules.aasx.core.aasx_population_orchestrator import create_aasx_population_orchestrator
    from src.modules.aasx.core.aasx_processor import extract_aasx, generate_aasx_from_structured
except ImportError as e:
    # Log the import error but don't fail immediately
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Some AASX engine services could not be imported: {e}")
    # Set to None - will be handled in __init__ if needed
    AASXProcessingService = None
    create_aasx_population_orchestrator = None
    extract_aasx = None
    generate_aasx_from_structured = None
from .aasx_file_client import AASXFileClient

logger = logging.getLogger(__name__)

class AASXProcessorClient:
    """Thin client wrapper for AASX processing operations."""
    
    def __init__(self, connection_manager=None):
        """Initialize the AASX processor client."""
        # Initialize with engine services
        self.aasx_processing_service = AASXProcessingService(connection_manager)
        self.population_orchestrator = create_aasx_population_orchestrator(connection_manager)
        self.file_client = AASXFileClient(connection_manager)
        
        logger.info("AASX Processor Client initialized with file client integration")
    
    async def run_etl_pipeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete ETL pipeline with all steps."""
        try:
            # 1. Run ETL processing (light orchestration)
            etl_result = await self._run_etl_processing(config)
            
            # 2. Trigger heavy population (delegate to engine orchestrator)
            population_result = await self.population_orchestrator.populate_aasx_dependent_modules(etl_result)
            
            # 3. Combine results and return
            return {
                'etl_status': 'success',
                'etl_result': etl_result,
                'population_status': population_result.get('overall_status'),
                'population_result': population_result,
                'timestamp': etl_result.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            return {
                'etl_status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _run_etl_processing(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the ETL processing step for both extraction and generation."""
        try:
            # Extract configuration
            file_id = config.get('file_id')
            project_id = config.get('project_id')
            use_case_id = config.get('use_case_id')
            output_formats = config.get('output_formats', ['json', 'graph', 'rdf', 'yaml'])
            
            # Detect job type from config or file type
            job_type = self._detect_job_type(config)
            
            # Create processing job
            job_data = {
                'file_id': file_id,
                'project_id': project_id,
                'use_case_id': use_case_id,
                'output_formats': output_formats,
                'job_type': job_type,
                'source_type': config.get('source_type', 'manual_upload'),
                'processed_by': config.get('user_id', 'system'),
                'org_id': config.get('org_id', 'default_org')
            }
            
            # Create job and get job ID
            job_id = await self.aasx_processing_service.create_job(job_data)
            
            # Update job status to processing
            await self.aasx_processing_service.update_status(job_id, 'processing')
            
            # Run actual ETL processing based on job type
            if job_type == 'extraction':
                etl_result = await self._run_extraction_job(config, job_id)
            elif job_type == 'generation':
                etl_result = await self._run_generation_job(config, job_id)
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            # Update job status to completed
            await self.aasx_processing_service.update_status(job_id, 'completed')
            
            return etl_result
            
        except Exception as e:
            # Update job status to failed
            if 'job_id' in locals():
                await self.aasx_processing_service.update_status(job_id, 'failed', {'error': str(e)})
            raise
    
    def _detect_job_type(self, config: Dict[str, Any]) -> str:
        """Detect job type from config only."""
        # Get job type from config
        job_type = config.get('job_type')
        
        # Validate job type
        if job_type not in ['extraction', 'generation']:
            raise ValueError(f"Invalid job type: {job_type}. Must be 'extraction' or 'generation'")
        
        return job_type
    
    async def _run_extraction_job(self, config: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        """Run AASX extraction job with hierarchical path construction."""
        try:
            # Import AASX extraction functions
            from src.modules.aasx.core.aasx_processor import extract_aasx
            
            # Get file information to construct proper paths
            file_id = config.get('file_id')
            if not file_id:
                raise ValueError("file_id is required for extraction job")
            
            # Get file paths using file client
            file_paths = await self.file_client.get_file_paths(file_id)
            if file_paths.get('status') != 'success':
                raise ValueError(f"Failed to get file paths: {file_paths.get('error')}")
            
            # Use the hierarchical output path from file client
            output_dir = Path(file_paths['output_path'])
            logger.info(f"Using hierarchical output path for extraction: {output_dir}")
            
            # Get input file path
            file_info = await self.file_client.file_service.get_file(file_id)
            if not file_info:
                raise ValueError(f"File not found: {file_id}")
            
            # Construct input file path using file client
            input_file_path = self.file_client.get_input_file_path(file_info, 'extraction')
            
            # Run AASX extraction with proper paths
            extraction_result = extract_aasx(
                input_file_path, 
                output_dir, 
                formats=config.get('output_formats', ['json', 'graph', 'rdf', 'yaml'])
            )
            
            # Convert result to standard format
            etl_result = {
                'job_id': job_id,
                'file_id': config.get('file_id'),
                'project_id': config.get('project_id'),
                'use_case_id': config.get('use_case_id'),
                'job_type': 'extraction',
                'status': 'completed',
                'output_formats': config.get('output_formats', ['json', 'graph', 'rdf', 'yaml']),
                'input_path': str(input_file_path),
                'output_path': str(output_dir),
                'extracted_content': {
                    'aas_models': extraction_result.get('aas_models', []),
                    'content_size': extraction_result.get('content_size', '0MB'),
                    'processing_time': extraction_result.get('processing_time', '0s'),
                    'documents': extraction_result.get('documents', {}),
                    'original': extraction_result.get('original', {})
                },
                'metrics': {
                    'quality_score': extraction_result.get('quality_score', 0.0),
                    'processing_accuracy': extraction_result.get('accuracy', 0.0),
                    'file_integrity': 'verified'
                },
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Extraction job completed successfully. Output stored at: {output_dir}")
            return etl_result
            
        except Exception as e:
            logger.error(f"Extraction job failed: {e}")
            raise
    
    async def _run_generation_job(self, config: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        """Run AASX generation job with hierarchical path construction."""
        try:
            # Import AASX generation functions
            from src.modules.aasx.core.aasx_processor import generate_aasx_from_structured
            
            # Get file information to construct proper paths
            file_id = config.get('file_id')
            if not file_id:
                raise ValueError("file_id is required for generation job")
            
            # Get file paths using file client
            file_paths = await self.file_client.get_file_paths(file_id)
            if file_paths.get('status') != 'success':
                raise ValueError(f"Failed to get file paths: {file_paths.get('error')}")
            
            # Use the hierarchical output path from file client
            output_dir = Path(file_paths['output_path'])
            logger.info(f"Using hierarchical output path for generation: {output_dir}")
            
            # Get input file path
            file_info = await self.file_client.file_service.get_file(file_id)
            if not file_info:
                raise ValueError(f"File not found: {file_id}")
            
            # Construct input file path using file client
            input_file_path = self.file_client.get_input_file_path(file_info, 'generation')
            
            # Run AASX generation with proper paths
            generation_result = generate_aasx_from_structured(
                input_file_path, 
                output_dir, 
                formats=config.get('output_formats', ['aasx'])
            )
            
            # Convert result to standard format
            etl_result = {
                'job_id': job_id,
                'file_id': config.get('file_id'),
                'project_id': config.get('project_id'),
                'use_case_id': config.get('use_case_id'),
                'job_type': 'generation',
                'status': 'completed',
                'output_formats': config.get('output_formats', ['aasx']),
                'input_path': str(input_file_path),
                'output_path': str(output_dir),
                'extracted_content': {
                    'aas_models': generation_result.get('aas_models', []),
                    'content_size': generation_result.get('file_size', '0MB'),
                    'processing_time': generation_result.get('processing_time', '0s'),
                    'documents': generation_result.get('documents', {}),
                    'structured_data': generation_result.get('structured_data', {})
                },
                'metrics': {
                    'quality_score': generation_result.get('quality_score', 0.0),
                    'processing_accuracy': generation_result.get('accuracy', 0.0),
                    'file_integrity': 'verified'
                },
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Generation job completed successfully. Output stored at: {output_dir}")
            return etl_result
            
        except Exception as e:
            logger.error(f"Generation job failed: {e}")
            raise
    
    async def get_job_file_paths(self, job_id: str) -> Dict[str, Any]:
        """
        Get the hierarchical file paths for a specific job.
        
        Args:
            job_id: Job ID to get paths for
            
        Returns:
            Dict[str, Any]: File paths information including input and output paths
        """
        try:
            # Get job information
            job_info = await self.aasx_processing_service.get_job(job_id)
            if not job_info:
                return {'error': 'Job not found'}
            
            file_id = job_info.file_id if hasattr(job_info, 'file_id') else job_info.get('file_id')
            if not file_id:
                return {'error': 'Job has no associated file'}
            
            # Get file paths using file client
            file_paths = await self.file_client.get_file_paths(file_id)
            if file_paths.get('status') != 'success':
                return {'error': f"Failed to get file paths: {file_paths.get('error')}"}
            
            # Add job-specific information
            result = {
                'status': 'success',
                'job_id': job_id,
                'file_id': file_id,
                'job_type': job_info.job_type if hasattr(job_info, 'job_type') else job_info.get('job_type'),
                'file_paths': file_paths
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get job file paths: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'job_id': job_id
            }
    
    async def process_etl_extraction(self, file_path: Path, output_dir: Path, 
                                   formats: list, job_id: str = None, 
                                   job_type: str = None) -> Dict[str, Any]:
        """Process ETL extraction for a single file."""
        # Delegate to engine service
        return await self.aasx_processing_service.process_extraction(
            file_path, output_dir, formats, job_id, job_type
        )
    
    async def process_generation_job(self, file_path: Path, output_dir: Path, 
                                   formats: list) -> Dict[str, Any]:
        """Process AASX generation job from structured data."""
        # Delegate to engine service
        return await self.aasx_processing_service.process_generation(
            file_path, output_dir, formats
        )
    
    async def get_processing_status(self, project_id: str = None) -> Dict[str, Any]:
        """Get processing status for projects."""
        # Delegate to engine service
        return await self.aasx_processing_service.get_processing_status(project_id)
    
    async def get_etl_progress(self) -> Dict[str, Any]:
        """Get ETL processing progress."""
        # Delegate to engine service
        return await self.aasx_processing_service.get_etl_progress()
    
    async def get_aasx_statistics(self) -> Dict[str, Any]:
        """Get AASX processing statistics."""
        # Delegate to engine service
        return await self.aasx_processing_service.get_aasx_statistics()
