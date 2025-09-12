"""
AASX File Client - Thin Client Wrapper
=====================================

Thin client wrapper around engine FileService + AASX-specific logic
Provides client-specific interface for AASX file operations.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from fastapi import UploadFile
from datetime import datetime

# Import from engine services
from src.engine.services.business_domain.file_service import FileService
from src.engine.services.business_domain.project_service import ProjectService
from src.engine.services.business_domain.use_case_service import UseCaseService
from src.engine.database.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class AASXFileClient:
    """Thin client wrapper for AASX file operations."""
    
    def __init__(self, connection_manager: ConnectionManager = None):
        """
        Initialize the AASX file client.
        
        Args:
            connection_manager: Engine connection manager instance
        """
        self.connection_manager = connection_manager
        
        # Initialize engine services
        if connection_manager:
            self.file_service = FileService(connection_manager)
            self.project_service = ProjectService(connection_manager)
            self.use_case_service = UseCaseService(connection_manager)
        else:
            self.file_service = None
            self.project_service = None
            self.use_case_service = None
            
        # Create data and output directories
        self._setup_directories()
        logger.info("AASX File Client initialized")
    
    def _setup_directories(self):
        """Create data and output directories for AASX processing."""
        try:
            # Create data directory for uploaded files
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Create output directory for processed files
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            logger.info(f"✅ Created directories: {data_dir}, {output_dir}")
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
    
    async def create_hierarchical_output_path(self, config: Dict[str, Any], file_info) -> Path:
        """
        Create hierarchical output path: output/usecase/project/job_type/filename_without_extension/
        
        Note: ETL results go to output/ directory with job type separation:
        - Extraction: output/usecase/project/extraction/filename/
        - Generation: output/usecase/project/generation/filename/
        
        Job type determines both input source and output destination for better organization.
        """
        try:
            # Get use case and project IDs from config and look up names
            use_case_id = config.get('use_case_id')
            project_id = config.get('project_id')
            
            if not use_case_id or not project_id:
                logger.error("Missing use_case_id or project_id in config")
                raise ValueError("use_case_id and project_id are required")
            
            # Look up names from database using IDs
            use_case_info = await self.use_case_service.get_use_case_by_id(use_case_id)
            project_info = await self.project_service.get_project(project_id)
            
            if not use_case_info:
                raise ValueError(f"Use case not found for ID: {use_case_id}")
            if not project_info:
                raise ValueError(f"Project not found for ID: {project_id}")
            
            # Extract names and make them filesystem-safe
            use_case_name = use_case_info.name.replace(" ", "_").replace("/", "_").replace("&", "and").replace(":", "_")
            project_name = project_info.name.replace(" ", "_").replace("/", "_").replace("&", "and").replace(":", "_")
            
            logger.info(f"Creating output path with: {use_case_name} / {project_name}")
            
            # Get filename without extension
            filename = file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename')
            filename_without_ext = Path(filename).stem
            
            # Determine job type for output path separation - NO DEFAULTS, must be explicit
            job_type = config.get('job_type')
            if job_type not in ['extraction', 'generation']:
                raise ValueError(f"Invalid job type: {job_type}. Must be 'extraction' or 'generation'")
            
            # Create hierarchical path with job type separation
            output_path = Path("output") / use_case_name / project_name / job_type / filename_without_ext
            
            # Create directories if they don't exist
            output_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Created hierarchical output path: {output_path}")
            logger.info(f"Job type: {job_type}")
            logger.info(f"Input: data/{use_case_name}/{project_name}/{job_type}/")
            logger.info(f"Output: output/{use_case_name}/{project_name}/{job_type}/")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating hierarchical output path: {e}")
            # Fallback to flat structure
            filename = file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename')
            filename_without_ext = Path(filename).stem
            fallback_path = Path("output") / filename_without_ext
            fallback_path.mkdir(parents=True, exist_ok=True)
            return fallback_path
    
    async def create_hierarchical_data_path(self, config: Dict[str, Any], file_info) -> Path:
        """
        Create hierarchical data path: data/usecase/project/job_type/filename_without_extension/
        
        This is where uploaded files are stored before processing.
        """
        try:
            # Get use case and project IDs from config and look up names
            use_case_id = config.get('use_case_id')
            project_id = config.get('project_id')
            
            if not use_case_id or not project_id:
                logger.error("Missing use_case_id or project_id in config")
                raise ValueError("use_case_id and project_id are required")
            
            # Look up names from database using IDs
            use_case_info = await self.use_case_service.get_use_case_by_id(use_case_id)
            project_info = await self.project_service.get_project(project_id)
            
            if not use_case_info:
                raise ValueError(f"Use case not found for ID: {use_case_id}")
            if not project_info:
                raise ValueError(f"Project not found for ID: {project_id}")
            
            # Extract names and make them filesystem-safe
            use_case_name = use_case_info.name.replace(" ", "_").replace("/", "_").replace("&", "and").replace(":", "_")
            project_name = project_info.name.replace(" ", "_").replace("/", "_").replace("&", "and").replace(":", "_")
            
            logger.info(f"Creating data path with: {use_case_name} / {project_name}")
            
            # Get filename without extension
            filename = file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename')
            filename_without_ext = Path(filename).stem
            
            # Determine job type for data path separation
            job_type = config.get('job_type')
            if job_type not in ['extraction', 'generation']:
                raise ValueError(f"Invalid job type: {job_type}. Must be 'extraction' or 'generation'")
            
            # Create hierarchical path with job type separation
            data_path = Path("data") / use_case_name / project_name / job_type / filename_without_ext
            
            # Create directories if they don't exist
            data_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Created hierarchical data path: {data_path}")
            return data_path
            
        except Exception as e:
            logger.error(f"Error creating hierarchical data path: {e}")
            # Fallback to flat structure
            filename = file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename')
            filename_without_ext = Path(filename).stem
            fallback_path = Path("data") / filename_without_ext
            fallback_path.mkdir(parents=True, exist_ok=True)
            return fallback_path
    
    def get_input_file_path(self, file_info, job_type: str = None) -> Path:
        """
        Get the input file path based on job type and file info.
        
        Args:
            file_info: File information object
            job_type: Job type ('extraction' or 'generation') - if None, auto-detected
            
        Returns:
            Path: Full path to the input file
        """
        try:
            # Auto-detect job type if not provided
            if job_type is None:
                file_type = file_info.file_type if hasattr(file_info, 'file_type') else file_info.get('file_type')
                
                if file_type == 'aasx':
                    job_type = 'extraction'
                elif file_type == 'zip':
                    job_type = 'generation'
                else:
                    raise ValueError(f"Cannot auto-detect job type. File type: {file_type}. Must be explicitly 'extraction' or 'generation'.")
            
            # Get file path from file info
            file_path = Path(file_info.filepath if hasattr(file_info, 'filepath') else file_info.get('filepath', ''))
            
            if not file_path.exists():
                raise FileNotFoundError(f"Input file not found: {file_path}")
            
            logger.info(f"Input file path for {job_type} job: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error getting input file path: {e}")
            raise
    
    async def upload_aasx_file(self, project_id: str, file: UploadFile, 
                              job_type: str, description: str = None, 
                              user_id: str = None, org_id: str = None, 
                              source_type: str = 'manual_upload') -> Dict[str, Any]:
        """
        Upload an AASX file to a project with hierarchy validation.
        
        Args:
            project_id: Project ID to upload to
            file: AASX file to upload
            job_type: Job type ('extraction' or 'generation')
            description: Optional file description
            user_id: User ID uploading the file
            org_id: Organization ID
            source_type: Source type ('manual_upload', 'url_upload', etc.)
            
        Returns:
            Dict[str, Any]: Upload result with file details
        """
        try:
            if not self.file_service:
                return {'error': 'File service not initialized'}
            
            # Validate job type
            if job_type not in ['extraction', 'generation']:
                raise ValueError("Job type must be 'extraction' or 'generation'")
            
            # Validate file type based on job type
            if job_type == 'extraction' and not file.filename.lower().endswith('.aasx'):
                raise ValueError("Extraction jobs require AASX files (.aasx)")
            elif job_type == 'generation' and not file.filename.lower().endswith('.zip'):
                raise ValueError("Generation jobs require structured data files (.zip)")
            
            # Validate project hierarchy
            hierarchy_validation = await self.validate_project_hierarchy(project_id)
            if not hierarchy_validation.get('valid', False):
                raise ValueError(f"Project hierarchy validation failed: {hierarchy_validation.get('error')}")
            
            # Create hierarchical paths for organized storage
            config = {
                'project_id': project_id,
                'use_case_id': hierarchy_validation.get('use_case_id'),
                'job_type': job_type
            }
            
            # Create file info object for path construction
            file_info = type('FileInfo', (), {
                'filename': file.filename,
                'file_type': 'aasx' if job_type == 'extraction' else 'zip'
            })()
            
            # Create hierarchical data and output paths
            data_path = await self.create_hierarchical_data_path(config, file_info)
            output_path = await self.create_hierarchical_output_path(config, file_info)
            
            # Store file in the hierarchical data path
            file_destination = data_path / file.filename
            with open(file_destination, 'wb') as f:
                content = await file.read()
                f.write(content)
            
            # Prepare file data for upload
            file_data = {
                'project_id': project_id,
                'filename': file.filename,
                'description': description or f"{job_type.title()} job for {file.filename}",
                'file_type': 'aasx' if job_type == 'extraction' else 'zip',
                'job_type': job_type,
                'source_type': source_type,
                'user_id': user_id,
                'org_id': org_id,
                'tags': [job_type, 'aasx_processing'],
                'metadata': {
                    'job_type': job_type,
                    'source_type': source_type,
                    'upload_timestamp': datetime.now().isoformat(),
                    'file_size_bytes': len(content),
                    'mime_type': file.content_type or 'application/octet-stream',
                    'data_path': str(data_path),
                    'output_path': str(output_path),
                    'hierarchy_path': hierarchy_validation.get('hierarchy_path')
                }
            }
            
            # Upload file using engine service
            upload_result = await self.file_service.upload_file(
                file_data=file.file,
                filename=file.filename,
                org_id=org_id,
                project_id=project_id,
                user_id=user_id,
                description=file_data['description'],
                tags=file_data['tags'],
                metadata=file_data['metadata']
            )
            
            # Add AASX-specific information with paths
            result = {
                'status': 'success',
                'file_id': upload_result.file_id if hasattr(upload_result, 'file_id') else upload_result.get('file_id'),
                'filename': file.filename,
                'project_id': project_id,
                'job_type': job_type,
                'source_type': source_type,
                'upload_timestamp': datetime.now().isoformat(),
                'hierarchy_path': hierarchy_validation.get('hierarchy_path'),
                'file_type': file_data['file_type'],
                'description': file_data['description'],
                'data_path': str(data_path),
                'output_path': str(output_path),
                'file_size_bytes': len(content)
            }
            
            logger.info(f"Successfully uploaded AASX file {file.filename} to project {project_id}")
            logger.info(f"File stored at: {data_path}")
            logger.info(f"Output will be at: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload AASX file: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'filename': file.filename if file else 'unknown',
                'project_id': project_id
            }
    
    async def get_file_paths(self, file_id: str) -> Dict[str, Any]:
        """
        Get the hierarchical data and output paths for an existing file.
        
        Args:
            file_id: File ID to get paths for
            
        Returns:
            Dict[str, Any]: File paths information
        """
        try:
            if not self.file_service:
                return {'error': 'File service not initialized'}
            
            file_info = await self.file_service.get_file(file_id)
            if not file_info:
                return {'error': 'File not found'}
            
            project_id = file_info.project_id if hasattr(file_info, 'project_id') else file_info.get('project_id')
            if not project_id:
                return {'error': 'File has no associated project'}
            
            hierarchy_validation = await self.validate_project_hierarchy(project_id)
            if not hierarchy_validation.get('valid', False):
                return {'error': f"Project hierarchy validation failed: {hierarchy_validation.get('error')}"}
            
            # Create config for path construction
            config = {
                'project_id': project_id,
                'use_case_id': hierarchy_validation.get('use_case_id'),
                'job_type': file_info.job_type if hasattr(file_info, 'job_type') else file_info.get('job_type', 'extraction')
            }
            
            # Create file info object for path construction
            file_info_obj = type('FileInfo', (), {
                'filename': file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename'),
                'file_type': file_info.file_type if hasattr(file_info, 'file_type') else file_info.get('file_type')
            })()
            
            # Get paths
            data_path = await self.create_hierarchical_data_path(config, file_info_obj)
            output_path = await self.create_hierarchical_output_path(config, file_info_obj)
            
            return {
                'status': 'success',
                'file_id': file_id,
                'filename': file_info_obj.filename,
                'data_path': str(data_path),
                'output_path': str(output_path),
                'hierarchy_path': hierarchy_validation.get('hierarchy_path'),
                'project_id': project_id,
                'use_case_id': hierarchy_validation.get('use_case_id'),
                'job_type': config['job_type']
            }
            
        except Exception as e:
            logger.error(f"Failed to get file paths: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'file_id': file_id
            }
    
    async def upload_structured_data(self, project_id: str, file: UploadFile,
                                   description: str = None, user_id: str = None,
                                   org_id: str = None) -> Dict[str, Any]:
        """
        Upload structured data for AASX generation.
        
        Args:
            project_id: Project ID to upload to
            file: Structured data file (ZIP, JSON, etc.)
            description: Optional file description
            user_id: User ID uploading the file
            org_id: Organization ID
            
        Returns:
            Dict[str, Any]: Upload result with file details
        """
        try:
            if not self.file_service:
                return {'error': 'File service not initialized'}
            
            # Validate project hierarchy
            hierarchy_validation = await self.validate_project_hierarchy(project_id)
            if not hierarchy_validation.get('valid', False):
                raise ValueError(f"Project hierarchy validation failed: {hierarchy_validation.get('error')}")
            
            # Create hierarchical paths for organized storage
            config = {
                'project_id': project_id,
                'use_case_id': hierarchy_validation.get('use_case_id'),
                'job_type': 'generation'
            }
            
            # Create file info object for path construction
            file_info = type('FileInfo', (), {
                'filename': file.filename,
                'file_type': 'zip'  # Structured data for generation
            })()
            
            # Create hierarchical data and output paths
            data_path = await self.create_hierarchical_data_path(config, file_info)
            output_path = await self.create_hierarchical_output_path(config, file_info)
            
            # Store file in the hierarchical data path
            file_destination = data_path / file.filename
            with open(file_destination, 'wb') as f:
                content = await file.read()
                f.write(content)
            
            # Prepare file data for structured data upload
            file_data = {
                'project_id': project_id,
                'filename': file.filename,
                'description': description or f"Structured data for AASX generation: {file.filename}",
                'file_type': 'structured_data',
                'job_type': 'generation',
                'source_type': 'manual_upload',
                'user_id': user_id,
                'org_id': org_id,
                'tags': ['generation', 'structured_data', 'aasx_processing'],
                'metadata': {
                    'job_type': 'generation',
                    'source_type': 'manual_upload',
                    'upload_timestamp': datetime.now().isoformat(),
                    'file_size_bytes': len(content),
                    'mime_type': file.content_type or 'application/octet-stream',
                    'data_format': self._detect_data_format(file.filename),
                    'data_path': str(data_path),
                    'output_path': str(output_path),
                    'hierarchy_path': hierarchy_validation.get('hierarchy_path')
                }
            }
            
            # Upload file using engine service
            upload_result = await self.file_service.upload_file(
                file_data=file.file,
                filename=file.filename,
                org_id=org_id,
                project_id=project_id,
                user_id=user_id,
                description=file_data['description'],
                tags=file_data['tags'],
                metadata=file_data['metadata']
            )
            
            result = {
                'status': 'success',
                'file_id': upload_result.file_id if hasattr(upload_result, 'file_id') else upload_result.get('file_id'),
                'filename': file.filename,
                'project_id': project_id,
                'job_type': 'generation',
                'file_type': 'structured_data',
                'upload_timestamp': datetime.now().isoformat(),
                'hierarchy_path': hierarchy_validation.get('hierarchy_path'),
                'description': file_data['description'],
                'data_path': str(data_path),
                'output_path': str(output_path),
                'file_size_bytes': len(content)
            }
            
            logger.info(f"Successfully uploaded structured data {file.filename} to project {project_id}")
            logger.info(f"File stored at: {data_path}")
            logger.info(f"Output will be at: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload structured data: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'filename': file.filename if file else 'unknown',
                'project_id': project_id
            }
    
    async def get_file_hierarchy_path(self, file_id: str) -> Dict[str, Any]:
        """
        Get the logical hierarchy path for a file (usecase/project/filename).
        
        Args:
            file_id: File ID to get hierarchy for
            
        Returns:
            Dict[str, Any]: Hierarchy path information
        """
        try:
            if not self.file_service:
                return {'error': 'File service not initialized'}
            
            # Get file information
            file_info = await self.file_service.get_file(file_id)
            if not file_info:
                return {'error': 'File not found'}
            
            # Get project information
            project_id = file_info.project_id if hasattr(file_info, 'project_id') else file_info.get('project_id')
            if not project_id:
                return {'error': 'File has no associated project'}
            
            # Get project details
            project_info = await self.project_service.get_project(project_id)
            if not project_info:
                return {'error': 'Project not found'}
            
            # Get use case information
            use_case_id = project_info.use_case_id if hasattr(project_info, 'use_case_id') else project_info.get('use_case_id')
            if not use_case_id:
                return {'error': 'Project has no associated use case'}
            
            use_case_info = await self.use_case_service.get_use_case_by_id(use_case_id)
            if not use_case_info:
                return {'error': 'Use case not found'}
            
            # Build hierarchy path
            hierarchy_path = {
                'file_id': file_id,
                'filename': file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename'),
                'project': {
                    'id': project_id,
                    'name': project_info.name if hasattr(project_info, 'name') else project_info.get('name'),
                    'description': project_info.description if hasattr(project_info, 'description') else project_info.get('description')
                },
                'use_case': {
                    'id': use_case_id,
                    'name': use_case_info.name if hasattr(use_case_info, 'name') else use_case_info.get('name'),
                    'description': use_case_info.description if hasattr(use_case_info, 'description') else use_case_info.get('description')
                },
                'full_path': f"{use_case_info.name}/{project_info.name}/{file_info.filename}",
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'status': 'success',
                'hierarchy_path': hierarchy_path
            }
            
        except Exception as e:
            logger.error(f"Failed to get file hierarchy path: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'file_id': file_id
            }
    
    async def validate_project_hierarchy(self, project_id: str) -> Dict[str, Any]:
        """
        Validate that project is in proper Use Case → Project hierarchy.
        
        Args:
            project_id: Project ID to validate
            
        Returns:
            Dict[str, Any]: Validation result with hierarchy information
        """
        try:
            if not self.project_service:
                return {'error': 'Project service not initialized'}
            
            # Get project information
            project_info = await self.project_service.get_project(project_id)
            if not project_info:
                return {
                    'valid': False,
                    'error': 'Project not found',
                    'project_id': project_id
                }
            
            # Get use case information
            use_case_id = project_info.use_case_id if hasattr(project_info, 'use_case_id') else project_info.get('use_case_id')
            if not use_case_id:
                return {
                    'valid': False,
                    'error': 'Project has no associated use case',
                    'project_id': project_id
                }
            
            use_case_info = await self.use_case_service.get_use_case_by_id(use_case_id)
            if not use_case_info:
                return {
                    'valid': False,
                    'error': 'Use case not found',
                    'project_id': project_id,
                    'use_case_id': use_case_id
                }
            
            # Validate hierarchy is complete
            hierarchy_path = f"{use_case_info.name}/{project_info.name}"
            
            return {
                'valid': True,
                'project_id': project_id,
                'use_case_id': use_case_id,
                'hierarchy_path': hierarchy_path,
                'project': {
                    'id': project_id,
                    'name': project_info.name if hasattr(project_info, 'name') else project_info.get('name'),
                    'description': project_info.description if hasattr(project_info, 'description') else project_info.get('description')
                },
                'use_case': {
                    'id': use_case_id,
                    'name': use_case_info.name if hasattr(use_case_info, 'name') else use_case_info.get('name'),
                    'description': use_case_info.description if hasattr(use_case_info, 'description') else use_case_info.get('description')
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to validate project hierarchy: {e}")
            return {
                'valid': False,
                'error': str(e),
                'project_id': project_id
            }
    
    async def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all files for a specific project.
        
        Args:
            project_id: Project ID to get files for
            
        Returns:
            List[Dict[str, Any]]: List of file information
        """
        try:
            if not self.file_service:
                return [{'error': 'File service not initialized'}]
            
            # Validate project hierarchy first
            hierarchy_validation = await self.validate_project_hierarchy(project_id)
            if not hierarchy_validation.get('valid', False):
                return [{'error': f"Project hierarchy validation failed: {hierarchy_validation.get('error')}"}]
            
            # Get project files using engine service
            files = await self.file_service.get_project_files(project_id)
            
            # Convert to list of dictionaries
            file_list = []
            for file_info in files:
                file_dict = {
                    'file_id': file_info.file_id if hasattr(file_info, 'file_id') else file_info.get('file_id'),
                    'filename': file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename'),
                    'description': file_info.description if hasattr(file_info, 'description') else file_info.get('description'),
                    'file_type': file_info.file_type if hasattr(file_info, 'file_type') else file_info.get('file_type'),
                    'upload_date': file_info.upload_date if hasattr(file_info, 'upload_date') else file_info.get('upload_date'),
                    'file_size': file_info.file_size if hasattr(file_info, 'file_size') else file_info.get('file_size'),
                    'tags': file_info.tags if hasattr(file_info, 'tags') else file_info.get('tags', []),
                    'metadata': file_info.metadata if hasattr(file_info, 'metadata') else file_info.get('metadata', {})
                }
                file_list.append(file_dict)
            
            return file_list
            
        except Exception as e:
            logger.error(f"Failed to get project files: {e}")
            return [{'error': str(e), 'project_id': project_id}]
    
    async def get_use_case_files(self, use_case_id: str) -> List[Dict[str, Any]]:
        """
        Get all files for a specific use case.
        
        Args:
            use_case_id: Use case ID to get files for
            
        Returns:
            List[Dict[str, Any]]: List of file information
        """
        try:
            if not self.use_case_service:
                return [{'error': 'Use case service not initialized'}]
            
            # Get use case with projects
            use_case_with_projects = await self.use_case_service.get_use_case_with_projects(use_case_id)
            if not use_case_with_projects:
                return [{'error': 'Use case not found'}]
            
            # Collect all files from all projects in the use case
            all_files = []
            projects = use_case_with_projects.get('projects', [])
            
            for project in projects:
                project_id = project.get('project_id')
                if project_id:
                    project_files = await self.get_project_files(project_id)
                    # Filter out error responses
                    valid_files = [f for f in project_files if 'error' not in f]
                    all_files.extend(valid_files)
            
            return all_files
            
        except Exception as e:
            logger.error(f"Failed to get use case files: {e}")
            return [{'error': str(e), 'use_case_id': use_case_id}]
    
    async def delete_aasx_file(self, file_id: str, user_id: str = None) -> Dict[str, Any]:
        """
        Delete an AASX file with proper cleanup.
        
        Args:
            file_id: File ID to delete
            user_id: User ID performing the deletion
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        try:
            if not self.file_service:
                return {'error': 'File service not initialized'}
            
            # Get file information before deletion
            file_info = await self.file_service.get_file(file_id)
            if not file_info:
                return {'error': 'File not found'}
            
            # Delete file using engine service
            success = await self.file_service.delete_file(file_id, user_id)
            
            if success:
                return {
                    'status': 'success',
                    'message': 'File deleted successfully',
                    'file_id': file_id,
                    'filename': file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename'),
                    'deletion_timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'error': 'Failed to delete file',
                    'file_id': file_id
                }
                
        except Exception as e:
            logger.error(f"Failed to delete AASX file: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'file_id': file_id
            }
    
    async def update_file_status(self, file_id: str, status: str, 
                               metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update file status and metadata.
        
        Args:
            file_id: File ID to update
            status: New status
            metadata: Additional metadata to update
            
        Returns:
            Dict[str, Any]: Update result
        """
        try:
            if not self.file_service:
                return {'error': 'File service not initialized'}
            
            # Prepare update data
            update_data = {'status': status}
            if metadata:
                update_data.update(metadata)
            
            # Update file using engine service
            success = await self.file_service.update_file(file_id, user_id=None, **update_data)
            
            if success:
                return {
                    'status': 'success',
                    'message': 'File updated successfully',
                    'file_id': file_id,
                    'updated_fields': list(update_data.keys()),
                    'update_timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'error': 'Failed to update file',
                    'file_id': file_id
                }
                
        except Exception as e:
            logger.error(f"Failed to update file status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'file_id': file_id
            }
    
    async def search_files(self, search_term: str, project_id: str = None, 
                          use_case_id: str = None, file_type: str = None,
                          tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for files with various filters.
        
        Args:
            search_term: Search term for filename/description
            project_id: Optional project filter
            use_case_id: Optional use case filter
            file_type: Optional file type filter
            tags: Optional tags filter
            
        Returns:
            List[Dict[str, Any]]: List of matching files
        """
        try:
            if not self.file_service:
                return [{'error': 'File service not initialized'}]
            
            # Build search filters
            filters = {}
            if project_id:
                filters['project_id'] = project_id
            if file_type:
                filters['file_type'] = file_type
            if tags:
                filters['tags'] = tags
            
            # Search files using engine service
            files = await self.file_service.search_files(
                org_id=None,  # Will be handled by service
                project_id=project_id,
                search_term=search_term,
                **filters
            )
            
            # Convert to list of dictionaries
            file_list = []
            for file_info in files:
                file_dict = {
                    'file_id': file_info.file_id if hasattr(file_info, 'file_id') else file_info.get('file_id'),
                    'filename': file_info.filename if hasattr(file_info, 'filename') else file_info.get('filename'),
                    'description': file_info.description if hasattr(file_info, 'description') else file_info.get('description'),
                    'file_type': file_info.file_type if hasattr(file_info, 'file_type') else file_info.get('file_type'),
                    'project_id': file_info.project_id if hasattr(file_info, 'project_id') else file_info.get('project_id'),
                    'upload_date': file_info.upload_date if hasattr(file_info, 'upload_date') else file_info.get('upload_date'),
                    'tags': file_info.tags if hasattr(file_info, 'tags') else file_info.get('tags', [])
                }
                file_list.append(file_dict)
            
            return file_list
            
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return [{'error': str(e), 'search_term': search_term}]
    
    def _detect_data_format(self, filename: str) -> str:
        """Detect data format from filename extension."""
        if filename.lower().endswith('.zip'):
            return 'zip'
        elif filename.lower().endswith('.json'):
            return 'json'
        elif filename.lower().endswith('.xml'):
            return 'xml'
        elif filename.lower().endswith('.csv'):
            return 'csv'
        elif filename.lower().endswith('.yaml') or filename.lower().endswith('.yml'):
            return 'yaml'
        else:
            return 'unknown'
