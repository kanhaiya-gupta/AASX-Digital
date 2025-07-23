"""
AASX Package Explorer Routes
FastAPI router for AASX Package Explorer integration and ETL pipeline management.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import subprocess
import json
import platform
import tempfile
import shutil
from pathlib import Path
import uuid
import requests
from urllib.parse import urlparse

# Import ETL pipeline components from src
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Legacy imports from old architecture (now deprecated)
# from src.aasx.aasx_etl_pipeline import AASXETLPipeline, ETLPipelineConfig
# from src.aasx.aasx_processor import AASXProcessor
# from src.aasx.aasx_transformer import AASXTransformer, TransformationConfig as TransformerConfig
# from src.aasx.aasx_loader import AASXLoader, LoaderConfig

# NOTE: ETL extraction logic migrated to use src.aasx.aasx_extraction (extract_aasx, batch_extract)
# Old AASXLoader/LoaderConfig interface removed for modernization

from src.aasx.aasx_extraction import extract_aasx, batch_extract
# from src.aasx.aasx_loader import AASXLoader, LoaderConfig  # Removed

# Import webapp configuration management
from ..config.etl_config import get_etl_config, ETLConfig

# Create router
router = APIRouter(tags=["aasx"])

# Debug logging to confirm routes.py is loaded
print("🔍 DEBUG: webapp/aasx/routes.py loaded successfully")

# Test route to verify router is working
@router.get("/api/test-route")
async def test_route():
    """Test route to verify router is working"""
    print("🔍 DEBUG: test_route called!")
    return {"message": "Test route working", "status": "success"}

# Setup templates
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Pydantic models
class AasxFileInfo(BaseModel):
    filename: str
    filepath: str
    size: int
    modified_date: str
    description: Optional[str] = None

class AasxPackageInfo(BaseModel):
    package_id: str
    name: str
    version: str
    description: str
    assets: List[str]
    submodels: List[str]

class ETLConfigRequest(BaseModel):
    extract: Optional[Dict[str, Any]] = None
    transform: Optional[Dict[str, Any]] = None
    load: Optional[Dict[str, Any]] = None
    files: Optional[List[str]] = None
    project_id: Optional[str] = None  # Add project ID for project-based outputs
    parallel_processing: bool = False
    max_workers: int = 4

class RAGSearchRequest(BaseModel):
    query: str
    entity_type: str = "all"
    top_k: int = 10

# New models for project management and file upload
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class ProjectInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: str
    updated_at: str
    file_count: int
    total_size: int

class FileUploadRequest(BaseModel):
    project_id: str
    file_url: Optional[str] = None
    file_description: Optional[str] = None

class FileInfo(BaseModel):
    id: str
    filename: str
    original_filename: str
    project_id: str
    filepath: str
    size: int
    upload_date: str
    description: Optional[str] = None
    status: str  # uploaded, processing, completed, error
    processing_result: Optional[Dict[str, Any]] = None

# Configuration
AASX_EXPLORER_PATH = os.path.join(os.getcwd(), "AasxPackageExplorer", "AasxPackageExplorer.exe")
AASX_LAUNCHER_SCRIPT = os.path.join(os.getcwd(), "src", "aasx", "launch_explorer.py")
AASX_CONTENT_PATH = os.path.join(os.getcwd(), "data", "aasx-examples")
ETL_CONFIG_PATH = os.path.join(os.getcwd(), "webapp", "config", "config_etl.yaml")

# Global ETL pipeline instance
etl_pipeline = None

# Global progress tracking
etl_progress = {
    'is_running': False,
    'current_file': '',
    'files_completed': 0,
    'total_files': 0,
    'extract_progress': 0,
    'transform_progress': 0,
    'load_progress': 0,
    'overall_progress': 0,
    'status_message': 'Ready',
    'results': {}
}

def reset_etl_pipeline():
    """Reset the global ETL pipeline instance to force recreation"""
    global etl_pipeline
    etl_pipeline = None

def get_etl_pipeline():
    """Get or create ETL pipeline instance with systematic structure"""
    global etl_pipeline
    if etl_pipeline is None:
        try:
            # Load configuration using webapp config management
            etl_config = get_etl_config()
            
            # Get configuration sections
            output_config = etl_config.get_output_config()
            transform_config = etl_config.get_transformation_config()
            load_config = etl_config.get_database_config()
            vector_config = etl_config.get_vector_database_config()
            pipeline_config = etl_config.get_pipeline_config()
            
            # Create transformer config
            transformer_config = TransformerConfig(
                output_format=transform_config.get('output_formats', ['json'])[0],
                include_metadata=transform_config.get('include_metadata', True),
                flatten_structures=False,
                normalize_ids=transform_config.get('normalize_ids', True),
                add_timestamps=transform_config.get('add_timestamps', True),
                enrich_with_external_data=transform_config.get('enable_enrichment', True),
                quality_checks=transform_config.get('enable_quality_checks', True)
            )
            
            # Get export format configuration
            export_config = etl_config.config_data.get('export_formats', {})
            
            # Determine export formats
            if export_config.get('custom_selection'):
                export_formats = export_config['custom_selection']
            else:
                export_formats = []
                if export_config.get('json', True):
                    export_formats.append('json')
                if export_config.get('yaml', True):
                    export_formats.append('yaml')
                if export_config.get('csv', True):
                    export_formats.append('csv')
                if export_config.get('tsv', True):
                    export_formats.append('tsv')
                if export_config.get('graph', True):
                    export_formats.append('graph')
                if export_config.get('rag', True):
                    export_formats.append('rag')
                if export_config.get('vector_db', True):
                    export_formats.append('vector_db')
                if export_config.get('sqlite', True):
                    export_formats.append('sqlite')
            
            # Create loader config with systematic structure
            # loader_config = LoaderConfig( # Removed
            #     output_directory=output_config.get('base_directory', 'output/etl_results'), # Removed
            #     database_path=load_config.get('sqlite_path', 'aasx_data.db'), # Removed
            #     vector_db_path=vector_config.get('path', 'output/vector_db'), # Removed
            #     vector_db_type=vector_config.get('type', 'qdrant'), # Removed
            #     qdrant_url=vector_config.get('qdrant_url', 'http://localhost:6333'), # Removed
            #     qdrant_collection_prefix=vector_config.get('qdrant_collection_prefix', 'aasx'), # Removed
            #     embedding_model=vector_config.get('embedding_model', 'all-MiniLM-L6-v2'), # Removed
            #     chunk_size=vector_config.get('chunk_size', 512), # Removed
            #     overlap_size=vector_config.get('overlap_size', 50), # Removed
            #     include_metadata=vector_config.get('include_metadata', True), # Removed
            #     backup_existing=load_config.get('backup_existing', True), # Removed
            #     separate_file_outputs=output_config.get('separate_file_outputs', True), # Removed
            #     include_filename_in_output=output_config.get('include_filename_in_output', True), # Removed
            #     systematic_structure=etl_config.is_systematic_structure_enabled(), # Removed
            #     folder_structure=etl_config.get_folder_structure_type(), # Removed
            #     export_formats=export_formats # Removed
            # ) # Removed
            
            # Create ETL pipeline config
            etl_config_obj = ETLPipelineConfig(
                extract_config={},
                transform_config=transformer_config,
                load_config={ # Changed to use default config
                    'output_directory': output_config.get('base_directory', 'output/etl_results'),
                    'database_path': load_config.get('sqlite_path', 'aasx_data.db'),
                    'vector_db_path': vector_config.get('path', 'output/vector_db'),
                    'vector_db_type': vector_config.get('type', 'qdrant'),
                    'embedding_model': vector_config.get('embedding_model', 'all-MiniLM-L6-v2'),
                    'chunk_size': vector_config.get('chunk_size', 512),
                    'overlap_size': vector_config.get('overlap_size', 50),
                    'include_metadata': vector_config.get('include_metadata', True),
                    'backup_existing': load_config.get('backup_existing', True),
                    'separate_file_outputs': output_config.get('separate_file_outputs', True),
                    'include_filename_in_output': output_config.get('include_filename_in_output', True),
                    'systematic_structure': etl_config.is_systematic_structure_enabled(),
                    'folder_structure': etl_config.get_folder_structure_type(),
                    'export_formats': export_formats
                },
                enable_validation=pipeline_config.get('enable_validation', True),
                enable_logging=pipeline_config.get('enable_logging', True),
                enable_backup=pipeline_config.get('enable_backup', True),
                parallel_processing=pipeline_config.get('parallel_processing', False),
                max_workers=pipeline_config.get('max_workers', 4)
            )
            
            etl_pipeline = AASXETLPipeline(etl_config_obj)
            
        except Exception as e:
            # Fallback to default configuration
            print(f"Warning: Using fallback ETL configuration due to error: {e}")
            
            # Create fallback loader config with systematic structure
            fallback_loader_config = { # Changed to use default config
                'output_directory': 'output/etl_results',
                'database_path': 'aasx_data.db',
                'vector_db_path': 'output/vector_db',
                'vector_db_type': 'qdrant',
                'embedding_model': 'all-MiniLM-L6-v2',
                'chunk_size': 512,
                'overlap_size': 50,
                'include_metadata': True,
                'backup_existing': True,
                'separate_file_outputs': True,
                'include_filename_in_output': True,
                'systematic_structure': True,
                'folder_structure': 'by_file',
                'export_formats': ['json', 'yaml', 'csv', 'tsv', 'graph', 'rag', 'vector_db', 'sqlite']
            }
            
            config = ETLPipelineConfig(
                extract_config={},
                transform_config=TransformerConfig(),
                load_config=fallback_loader_config,
                enable_validation=True,
                enable_logging=True,
                enable_backup=False,
                parallel_processing=False,
                max_workers=4
            )
            etl_pipeline = AASXETLPipeline(config)
    
    return etl_pipeline

@router.get("/", response_class=HTMLResponse)
async def aasx_dashboard(request: Request):
    """AASX ETL Pipeline dashboard"""
    # Get available AASX files
    aasx_files = get_available_aasx_files()
    
    return templates.TemplateResponse(
        "aasx/index.html",
        {
            "request": request,
            "title": "AASX ETL Pipeline - AASX Digital Twin Analytics Framework",
            "aasx_files": aasx_files,
            "explorer_available": os.path.exists(AASX_LAUNCHER_SCRIPT)
        }
    )

# ETL Pipeline API Endpoints

@router.post("/api/etl/run")
async def run_etl_pipeline(config: ETLConfigRequest):
    """Run complete ETL pipeline with progress tracking using new extraction architecture"""
    global etl_progress
    
    try:
        # Initialize progress tracking
        etl_progress = {
            'is_running': True,
            'current_file': '',
            'files_completed': 0,
            'total_files': len(config.files) if config.files else 0,
            'extract_progress': 0,
            'transform_progress': 0,
            'load_progress': 0,
            'overall_progress': 0,
            'status_message': 'Starting ETL pipeline...',
            'results': {}
        }
        
        # Process all files if no specific files provided
        if not config.files:
            aasx_files = get_available_aasx_files()
            config.files = [file['filename'] for file in aasx_files]
        
        total_files = len(config.files)
        results = []
        processed_files = {}
        
        # Progress tracking
        progress_data = {
            'extract': 0,
            'transform': 0, 
            'load': 0,
            'overall': 0,
            'current_file': '',
            'files_completed': 0,
            'total_files': total_files
        }
        
        for i, filename in enumerate(config.files):
            # Only search for files within the specified project
            file_path = find_aasx_file_in_project(filename, config.project_id) if config.project_id else find_aasx_file(filename)
            if file_path:
                print(f"🔍 Processing file: {filename} at path: {file_path}")
                
                # Update progress for current file
                etl_progress['current_file'] = filename
                etl_progress['files_completed'] = i
                etl_progress['status_message'] = f'Processing {filename}...'
                
                # Calculate phase progress based on file processing
                file_progress = (i / total_files) * 100
                etl_progress['extract_progress'] = int(file_progress * 0.3)  # Extract is 30% of total
                etl_progress['transform_progress'] = int(file_progress * 0.4)  # Transform is 40% of total
                etl_progress['load_progress'] = int(file_progress * 0.3)  # Load is 30% of total
                etl_progress['overall_progress'] = int(file_progress)
                
                # Update file status in database if it exists (only for files in the specified project)
                file_id = None
                for fid, file_info in FILES_DB.items():
                    if (file_info['filename'] == filename or file_info['original_filename'] == filename) and file_info['project_id'] == config.project_id:
                        file_id = fid
                        file_info['status'] = 'processing'
                        FILES_DB[fid] = file_info
                        
                        # Save project to filesystem to persist processing status
                        if config.project_id:
                            save_project_to_filesystem(config.project_id)
                        break
                
                # Process the file using new extraction architecture
                print(f"🚀 Starting ETL processing for: {file_path}")
                
                # Determine output directory based on project ID and file name
                file_stem = Path(file_path).stem  # Get filename without extension
                if config.project_id:
                    output_dir = Path("output") / "projects" / config.project_id / file_stem
                else:
                    output_dir = Path("output") / file_stem
                
                # Ensure output directory exists
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Use new extraction function
                from src.aasx.aasx_extraction import extract_aasx
                import time
                
                start_time = time.time()
                try:
                    # Extract in multiple formats: JSON, Graph, RDF/Turtle
                    extraction_results = extract_aasx(Path(file_path), output_dir, formats=['json', 'graph', 'rdf'])
                    processing_time = time.time() - start_time
                    
                    # Check if all extractions succeeded
                    all_succeeded = all(r.get('status') == 'completed' for r in extraction_results.values())
                    
                    result = {
                        'file_path': file_path,
                        'status': 'completed' if all_succeeded else 'partial',
                        'processing_time': processing_time,
                        'output_directory': str(output_dir),
                        'project_id': config.project_id,
                        'extraction_results': extraction_results
                    }
                except Exception as e:
                    processing_time = time.time() - start_time
                    result = {
                        'file_path': file_path,
                        'status': 'failed',
                        'error': str(e),
                        'processing_time': processing_time,
                        'project_id': config.project_id
                    }
                
                print(f"✅ ETL result for {filename}: {result}")
                results.append(result)
                processed_files[filename] = result['status']
                
                # Update file status in database after processing
                if file_id:
                    file_info = FILES_DB[file_id]
                    file_info['status'] = 'completed' if result['status'] == 'completed' else 'error'
                    file_info['processing_result'] = result
                    FILES_DB[file_id] = file_info
                    
                    # Save project to filesystem to persist status changes
                    if config.project_id:
                        save_project_to_filesystem(config.project_id)
                
                # Update progress after file completion
                etl_progress['files_completed'] = i + 1
                etl_progress['extract_progress'] = int(((i + 1) / total_files) * 30)
                etl_progress['transform_progress'] = int(((i + 1) / total_files) * 40)
                etl_progress['load_progress'] = int(((i + 1) / total_files) * 30)
                etl_progress['overall_progress'] = int(((i + 1) / total_files) * 100)
                etl_progress['results'][filename] = result
            else:
                print(f"❌ File not found: {filename}")
                result = {
                    'file_path': filename,
                    'status': 'failed',
                    'error': f'File not found: {filename}',
                    'processing_time': 0
                }
                results.append(result)
                processed_files[filename] = 'failed'
                
                # Update file status in database for failed files (only for files in the specified project)
                for fid, file_info in FILES_DB.items():
                    if (file_info['filename'] == filename or file_info['original_filename'] == filename) and file_info['project_id'] == config.project_id:
                        file_info['status'] = 'error'
                        file_info['processing_result'] = result
                        FILES_DB[fid] = file_info
                        
                        # Save project to filesystem to persist status changes
                        if config.project_id:
                            save_project_to_filesystem(config.project_id)
                        break
                
                etl_progress['results'][filename] = result
        
        # Mark completion with a small delay to ensure proper state update
        import time
        time.sleep(0.1)  # Small delay to ensure progress state is updated
        
        etl_progress['is_running'] = False
        etl_progress['extract_progress'] = 100
        etl_progress['transform_progress'] = 100
        etl_progress['load_progress'] = 100
        etl_progress['overall_progress'] = 100
        etl_progress['status_message'] = 'ETL pipeline completed successfully!'
        
        # Calculate overall statistics
        successful = [r for r in results if r['status'] == 'completed']
        failed = [r for r in results if r['status'] == 'failed']
        
        overall_result = {
            'success': len(failed) == 0,
            'files_processed': len(successful),
            'files_failed': len(failed),
            'total_time': sum(r.get('processing_time', 0) for r in results),
            'processed_files': processed_files,
            'results': results,
            'pipeline_stats': {
                'total_files': total_files,
                'successful_files': len(successful),
                'failed_files': len(failed),
                'architecture': 'new_extraction'
            },
            'progress': etl_progress
        }
        
        return overall_result
        
    except Exception as e:
        # Mark error state
        etl_progress['is_running'] = False
        etl_progress['status_message'] = f'ETL pipeline failed: {str(e)}'
        raise HTTPException(status_code=500, detail=f"ETL pipeline error: {str(e)}")

@router.post("/api/etl/process-file")
async def process_single_file(config: ETLConfigRequest):
    """Process a single AASX file through ETL pipeline with progress tracking"""
    try:
        if not config.files or len(config.files) != 1:
            raise HTTPException(status_code=400, detail="Exactly one file must be specified")
        
        filename = config.files[0]
        # Only search for files within the specified project
        file_path = find_aasx_file_in_project(filename, config.project_id) if config.project_id else find_aasx_file(filename)
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        # New extraction architecture - configuration handled by aas-processor
        # Transform and load configurations are now handled by the external .NET processor
        print("🔧 Using new extraction architecture with external aas-processor")
        
        # Progress tracking for single file
        progress_data = {
            'extract': 0,
            'transform': 0,
            'load': 0,
            'overall': 0,
            'current_file': filename,
            'files_completed': 0,
            'total_files': 1
        }
        
        # Simulate progress phases (using integers)
        # Extract phase (30%)
        progress_data['extract'] = 30
        progress_data['overall'] = 30
        
        # Transform phase (40%)
        progress_data['transform'] = 40
        progress_data['overall'] = 70
        
        # Load phase (30%)
        progress_data['load'] = 30
        progress_data['overall'] = 100
        
        # Update file status in database if it exists (only for files in the specified project)
        file_id = None
        for fid, file_info in FILES_DB.items():
            if (file_info['filename'] == filename or file_info['original_filename'] == filename) and file_info['project_id'] == config.project_id:
                file_id = fid
                file_info['status'] = 'processing'
                FILES_DB[fid] = file_info
                
                # Save project to filesystem to persist processing status
                if config.project_id:
                    save_project_to_filesystem(config.project_id)
                break
        
        # Process file using new extraction architecture
        from src.aasx.aasx_extraction import extract_aasx
        import time
        
        # Determine output directory based on project ID
        if config.project_id:
            output_dir = Path("output") / "projects" / config.project_id / "structured_data"
        else:
            output_dir = Path("output") / "structured_data"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        try:
            extract_aasx(Path(file_path), output_dir)
            processing_time = time.time() - start_time
            
            result = {
                'file_path': file_path,
                'status': 'completed',
                'processing_time': processing_time,
                'output_directory': str(output_dir),
                'project_id': config.project_id,
                'filename': filename
            }
        except Exception as e:
            processing_time = time.time() - start_time
            result = {
                'file_path': file_path,
                'status': 'failed',
                'error': str(e),
                'processing_time': processing_time,
                'project_id': config.project_id,
                'filename': filename
            }
        
        # Update file status in database after processing
        if file_id:
            file_info = FILES_DB[file_id]
            file_info['status'] = 'completed' if result['status'] == 'completed' else 'error'
            file_info['processing_result'] = result
            FILES_DB[file_id] = file_info
            
            # Save project to filesystem to persist status changes
            if config.project_id:
                save_project_to_filesystem(config.project_id)
        
        return {
            'success': result['status'] == 'completed',
            'result': result,
            'progress': {
                'extract': 100,
                'transform': 100,
                'load': 100,
                'overall': 100,
                'current_file': 'Completed',
                'files_completed': 1,
                'total_files': 1
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@router.post("/api/etl/process-batch")
async def process_batch_files(config: ETLConfigRequest):
    """Process multiple AASX files through ETL pipeline"""
    try:
        if not config.files:
            raise HTTPException(status_code=400, detail="No files specified")
        
        # New extraction architecture - configuration handled by aas-processor
        print("🔧 Using new extraction architecture with external aas-processor for batch processing")
        
        # Process files
        results = []
        processed_files = {}
        
        for filename in config.files:
            # Only search for files within the specified project
            file_path = find_aasx_file_in_project(filename, config.project_id) if config.project_id else find_aasx_file(filename)
            if file_path:
                # Update file status in database if it exists (only for files in the specified project)
                file_id = None
                for fid, file_info in FILES_DB.items():
                    if (file_info['filename'] == filename or file_info['original_filename'] == filename) and file_info['project_id'] == config.project_id:
                        file_id = fid
                        file_info['status'] = 'processing'
                        FILES_DB[fid] = file_info
                        
                        # Save project to filesystem to persist processing status
                        if config.project_id:
                            save_project_to_filesystem(config.project_id)
                        break
                
                # Process file using new extraction architecture
                from src.aasx.aasx_extraction import extract_aasx
                import time
                
                # Determine output directory based on project ID and file name
                file_stem = Path(file_path).stem  # Get filename without extension
                if config.project_id:
                    output_dir = Path("output") / "projects" / config.project_id / file_stem
                else:
                    output_dir = Path("output") / file_stem
                
                # Ensure output directory exists
                output_dir.mkdir(parents=True, exist_ok=True)
                
                start_time = time.time()
                try:
                    # Extract in multiple formats: JSON, Graph, RDF/Turtle
                    extraction_results = extract_aasx(Path(file_path), output_dir, formats=['json', 'graph', 'rdf'])
                    processing_time = time.time() - start_time
                    
                    # Check if all extractions succeeded
                    all_succeeded = all(r.get('status') == 'completed' for r in extraction_results.values())
                    
                    result = {
                        'file_path': file_path,
                        'status': 'completed' if all_succeeded else 'partial',
                        'processing_time': processing_time,
                        'output_directory': str(output_dir),
                        'project_id': config.project_id,
                        'filename': filename,
                        'extraction_results': extraction_results
                    }
                except Exception as e:
                    processing_time = time.time() - start_time
                    result = {
                        'file_path': file_path,
                        'status': 'failed',
                        'error': str(e),
                        'processing_time': processing_time,
                        'project_id': config.project_id,
                        'filename': filename
                    }
                results.append(result)
                processed_files[filename] = result['status']
                
                # Update file status in database after processing
                if file_id:
                    file_info = FILES_DB[file_id]
                    file_info['status'] = 'completed' if result['status'] == 'completed' else 'error'
                    file_info['processing_result'] = result
                    FILES_DB[file_id] = file_info
                    
                    # Save project to filesystem to persist status changes
                    if config.project_id:
                        save_project_to_filesystem(config.project_id)
        
        # Calculate statistics
        successful = [r for r in results if r['status'] == 'completed']
        failed = [r for r in results if r['status'] == 'failed']
        
        return {
            'success': len(failed) == 0,
            'files_processed': len(successful),
            'files_failed': len(failed),
            'total_time': sum(r.get('processing_time', 0) for r in results),
            'processed_files': processed_files,
            'results': results,
            'pipeline_stats': {
                'total_files': len(config.files),
                'successful_files': len(successful),
                'failed_files': len(failed),
                'architecture': 'new_extraction'
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")

@router.get("/api/etl/progress")
async def get_etl_progress():
    """Get current ETL pipeline progress"""
    global etl_progress
    
    # Add timestamp for better tracking
    progress_response = dict(etl_progress)
    progress_response['timestamp'] = datetime.now().isoformat()
    
    # Add more detailed status information
    if etl_progress['is_running']:
        if etl_progress['current_file']:
            progress_response['status_message'] = f"Processing {etl_progress['current_file']}... ({etl_progress['files_completed']}/{etl_progress['total_files']})"
        else:
            progress_response['status_message'] = "Initializing ETL pipeline..."
    else:
        if etl_progress['overall_progress'] == 100:
            progress_response['status_message'] = "ETL pipeline completed successfully!"
        else:
            progress_response['status_message'] = etl_progress.get('status_message', 'ETL pipeline not running')
    
    return progress_response

@router.get("/api/etl/stats")
async def get_etl_stats():
    """Get ETL pipeline statistics"""
    try:
        pipeline = get_etl_pipeline()
        stats = pipeline.get_pipeline_stats()
        
        # Add database statistics
        try:
            # The following line was removed as per the edit hint to remove LoaderConfig usage
            # db_stats = pipeline.loader.get_database_stats() 
            stats['database_stats'] = {} # Placeholder for future implementation
        except Exception as e:
            stats['database_stats'] = {'error': str(e)}
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/status")
async def get_etl_status():
    """
    Get ETL pipeline status
    
    Returns:
        ETL pipeline status information
    """
    try:
        pipeline = get_etl_pipeline()
        
        # Get pipeline validation status
        validation_status = "unknown"
        try:
            validation_result = pipeline.validate_pipeline()
            validation_status = "valid" if validation_result else "invalid"
        except Exception:
            validation_status = "error"
        
        # Get pipeline stats
        stats = {}
        try:
            stats = pipeline.get_pipeline_stats()
        except Exception:
            stats = {"error": "Failed to get pipeline stats"}
        
        return {
            "status": "available",
            "pipeline": "ready",
            "validation": validation_status,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/api/etl/export-results")
async def export_etl_results():
    """Export ETL pipeline results"""
    try:
        pipeline = get_etl_pipeline()
        
        # Create export file
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'pipeline_stats': pipeline.get_pipeline_stats(),
            'validation_results': pipeline.validate_pipeline(),
            'component_configs': {
                'extract_config': pipeline.config.extract_config,
                'transform_config': {
                    'enable_quality_checks': pipeline.config.transform_config.enable_quality_checks,
                    'enable_enrichment': pipeline.config.transform_config.enable_enrichment,
                    'output_formats': pipeline.config.transform_config.output_formats,
                    'include_metadata': pipeline.config.transform_config.include_metadata
                },
                'load_config': {
                    'output_directory': pipeline.config.load_config['output_directory'],
                    'database_path': pipeline.config.load_config['database_path'],
                    'vector_db_path': pipeline.config.load_config['vector_db_path'],
                    'vector_db_type': pipeline.config.load_config['vector_db_type'],
                    'embedding_model': pipeline.config.load_config['embedding_model']
                }
            }
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(export_data, f, indent=2)
            temp_file = f.name
        
        return FileResponse(
            temp_file,
            media_type='application/json',
            filename=f'etl_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# RAG System API Endpoints

@router.post("/api/rag/search")
async def search_rag(request: RAGSearchRequest):
    """Search RAG system using vector similarity"""
    try:
        pipeline = get_etl_pipeline()
        
        if not pipeline.loader.embedding_model:
            raise HTTPException(status_code=503, detail="Vector database not available")
        
        results = pipeline.loader.search_similar(
            query=request.query,
            entity_type=request.entity_type,
            top_k=request.top_k
        )
        
        return {
            'success': True,
            'query': request.query,
            'entity_type': request.entity_type,
            'results_count': len(results),
            'results': results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")

@router.post("/api/rag/export")
async def export_rag_dataset():
    """Export RAG-ready dataset"""
    try:
        pipeline = get_etl_pipeline()
        
        # Create RAG dataset
        output_path = os.path.join(tempfile.gettempdir(), f'rag_dataset_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        rag_path = pipeline.create_rag_ready_dataset(output_path)
        
        return FileResponse(
            rag_path,
            media_type='application/json',
            filename=f'rag_dataset_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG export failed: {str(e)}")

# File Management API Endpoints

@router.get("/api/files")
async def get_aasx_files():
    """Get list of available AASX files"""
    try:
        files = get_available_aasx_files()
        return {
            "files": files,
            "total_count": len(files),
            "explorer_path": AASX_LAUNCHER_SCRIPT,
            "explorer_available": os.path.exists(AASX_LAUNCHER_SCRIPT)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/open/{filename}")
async def open_aasx_file(filename: str):
    """Open AASX file with AASX Package Explorer"""
    try:
        if not os.path.exists(AASX_LAUNCHER_SCRIPT):
            raise HTTPException(status_code=404, detail="AASX Package Explorer not found")
        
        # Find the file
        file_path = find_aasx_file(filename)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="AASX file not found")
        
        # Launch AASX Package Explorer with the file
        if platform.system() == "Windows":
            subprocess.Popen([sys.executable, AASX_LAUNCHER_SCRIPT])
        else:
            # For non-Windows systems, try to open with default application
            subprocess.Popen(["open", file_path] if platform.system() == "Darwin" else ["xdg-open", file_path])
        
        return {
            "success": True,
            "message": f"Opening {filename} with AASX Package Explorer",
            "file_path": file_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/results/{filename}")
async def get_file_results(filename: str):
    """Get processing results for a specific file"""
    try:
        pipeline = get_etl_pipeline()
        
        # Get database stats to check if file was processed
        db_stats = pipeline.loader.get_database_stats()
        
        # Mock results (in real implementation, you'd query the database)
        results = {
            'filename': filename,
            'processed': True,
            'processing_time': 2.5,
            'extract_result': {
                'success': True,
                'assets_found': 3,
                'submodels_found': 2,
                'documents_found': 1
            },
            'transform_result': {
                'success': True,
                'transformations_applied': ['quality_enrichment', 'normalization'],
                'output_formats': ['json', 'csv']
            },
            'load_result': {
                'success': True,
                'database_records': 6,
                'vector_embeddings': 6,
                'files_exported': ['output.json', 'output.csv']
            }
        }
        
        return {
            'success': True,
            'data': results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@router.get("/api/refresh")
@router.post("/api/refresh")
async def refresh_files():
    """Refresh available AASX files and reset ETL pipeline"""
    try:
        # Reset ETL pipeline to force recreation with latest config
        reset_etl_pipeline()
        
        # Get updated file list
        files = get_available_aasx_files()
        
        return {
            "success": True,
            "message": "Files refreshed and ETL pipeline reset",
            "files": files,
            "total_count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/etl/reset")
async def reset_etl_pipeline_endpoint():
    """Reset the ETL pipeline to force recreation with latest configuration"""
    try:
        reset_etl_pipeline()
        return {
            "success": True,
            "message": "ETL pipeline reset successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/explorer/status")
async def get_explorer_status():
    """Get AASX Package Explorer status"""
    try:
        # Import the launcher module
        from src.aasx.launch_explorer import check_explorer_status
        
        # Get status using the module
        status = check_explorer_status()
        
        # Add additional information
        status["available"] = status["explorer_found"]
        status["path"] = AASX_LAUNCHER_SCRIPT
        status["content_available"] = status["content_found"]
        
        # Get file size and modification time for the launcher script
        if os.path.exists(AASX_LAUNCHER_SCRIPT):
            stat = os.stat(AASX_LAUNCHER_SCRIPT)
            status.update({
                "file_size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return status
        
    except ImportError as e:
        raise HTTPException(status_code=404, detail=f"AASX Package Explorer launcher module not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/explorer/launch")
async def launch_explorer():
    """Launch AASX Package Explorer using the Python launcher module"""
    try:
        # Import the launcher module
        from src.aasx.launch_explorer import launch_explorer as launch_aasx_explorer
        
        # Launch the explorer using the module
        result = launch_aasx_explorer(silent=True)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "timestamp": datetime.now().isoformat(),
                "method": "python_module",
                "explorer_path": result["explorer_path"],
                "content_path": result["content_path"],
                "pid": result.get("pid")
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
        
    except ImportError as e:
        raise HTTPException(status_code=404, detail=f"AASX Package Explorer launcher module not found: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/explorer/launch-script")
async def launch_explorer_script():
    """Get Python launcher script for AASX Package Explorer"""
    try:
        launcher_script = os.path.join(os.getcwd(), "src", "aasx", "launch_explorer.py")
        
        if not os.path.exists(launcher_script):
            raise HTTPException(status_code=404, detail="AASX Package Explorer launcher script not found")
        
        # Return the Python script file
        return FileResponse(
            launcher_script,
            media_type='text/plain',
            filename='launch_explorer.py'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/project-packages/{project_path:path}")
async def get_package_by_project_path(project_path: str):
    """Get AASX package by project path (project_id/filename)"""
    print(f"🔍 DEBUG: get_package_by_project_path called with project_path: {project_path}")
    print(f"🔍 DEBUG: Route function is being called!")
    try:
        # Split the project path into project_id and filename
        path_parts = project_path.split('/')
        print(f"🔍 DEBUG: path_parts: {path_parts}")
        if len(path_parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid project path format. Expected: project_id/filename")
        
        project_id, filename = path_parts
        print(f"🔍 DEBUG: project_id: {project_id}, filename: {filename}")
        
        # Construct the full file path
        data_path = os.getenv("AASX_DATA_PATH", "/app/data")
        project_path_full = os.path.join(data_path, "projects", project_id, filename)
        print(f"🔍 DEBUG: project_path_full: {project_path_full}")
        
        # Check if file exists
        if not os.path.exists(project_path_full):
            print(f"❌ DEBUG: File not found: {project_path_full}")
            raise HTTPException(status_code=404, detail=f"AASX file not found: {project_path}")
        
        print(f"✅ DEBUG: File found, returning FileResponse")
        # Return the file
        return FileResponse(
            path=project_path_full,
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ DEBUG: Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/packages/{filename}")
async def get_package_info(filename: str):
    """Get information about an AASX package"""
    try:
        # Find the file
        file_path = find_aasx_file(filename)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="AASX file not found")
        
        # Mock package information (in real implementation, you'd parse the AASX file)
        package_info = {
            "package_id": f"pkg_{filename.replace('.aasx', '')}",
            "name": filename.replace('.aasx', '').replace('_', ' ').title(),
            "version": "1.0.0",
            "description": f"Digital twin package for {filename.replace('.aasx', '').replace('_', ' ').title()}",
            "assets": [
                "3D_Model.step",
                "Technical_Documentation.pdf",
                "Quality_Certificate.pdf"
            ],
            "submodels": [
                "TechnicalData",
                "Documentation",
                "QualityAssurance",
                "Maintenance"
            ],
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "modified_date": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
        
        return package_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/packages/{filename}/download")
async def download_aasx_file(filename: str):
    """Download an AASX file"""
    try:
        # Find the file
        file_path = find_aasx_file(filename)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="AASX file not found")
        
        return FileResponse(
            file_path,
            media_type='application/octet-stream',
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions

def find_aasx_file_in_project(filename: str, project_id: str) -> Optional[str]:
    """Find AASX file within a specific project directory"""
    print(f"🔍 Searching for file: {filename} in project: {project_id}")
    
    # Search only in the specified project directory
    project_dir = os.path.join(os.getcwd(), "data", "projects", project_id)
    print(f"📁 Searching in project directory: {project_dir}")
    
    if os.path.exists(project_dir):
        for root, dirs, files in os.walk(project_dir):
            if filename in files:
                file_path = os.path.join(root, filename)
                print(f"✅ Found file in project: {file_path}")
                return file_path
    
    print(f"❌ File not found: {filename} in project {project_id}")
    return None

def find_aasx_file(filename: str) -> Optional[str]:
    """Find AASX file in content directory and project directories (global search)"""
    print(f"🔍 Searching for file: {filename}")
    
    # First search in AASX content directory
    print(f"📁 Searching in AASX content directory: {AASX_CONTENT_PATH}")
    for root, dirs, files in os.walk(AASX_CONTENT_PATH):
        if filename in files:
            file_path = os.path.join(root, filename)
            print(f"✅ Found file in AASX content: {file_path}")
            return file_path
    
    # Then search in project directories
    projects_dir = os.path.join(os.getcwd(), "data", "projects")
    print(f"📁 Searching in projects directory: {projects_dir}")
    if os.path.exists(projects_dir):
        for project_dir in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_dir)
            if os.path.isdir(project_path):
                print(f"📂 Searching in project: {project_dir}")
                for root, dirs, files in os.walk(project_path):
                    if filename in files:
                        file_path = os.path.join(root, filename)
                        print(f"✅ Found file in project: {file_path}")
                        return file_path
    
    print(f"❌ File not found: {filename}")
    return None

def get_available_aasx_files():
    """Get list of available AASX files"""
    files = []
    
    if not os.path.exists(AASX_CONTENT_PATH):
        return files
    
    for root, dirs, filenames in os.walk(AASX_CONTENT_PATH):
        for filename in filenames:
            if filename.lower().endswith('.aasx'):
                file_path = os.path.join(root, filename)
                stat = os.stat(file_path)
                
                # Create description based on filename
                description = filename.replace('.aasx', '').replace('_', ' ').title()
                
                files.append({
                    'filename': filename,
                    'filepath': file_path,
                    'size': stat.st_size,
                    'modified_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'description': description
                })
    
    # Sort by modification date (newest first)
    files.sort(key=lambda x: x['modified_date'], reverse=True)
    
    return files

@router.get("/api/integration/status")
async def get_integration_status():
    """Get integration status for all components"""
    try:
        pipeline = get_etl_pipeline()
        
        status = {
            "aasx_explorer": {
                "available": os.path.exists(AASX_LAUNCHER_SCRIPT),
                "path": AASX_LAUNCHER_SCRIPT
            },
            "etl_pipeline": {
                "available": True,
                "validation": pipeline.validate_pipeline(),
                "stats": pipeline.get_pipeline_stats()
            },
            "vector_database": {
                "available": pipeline.loader.embedding_model is not None,
                "type": pipeline.config.load_config['vector_db_type'],
                "model": pipeline.config.load_config['embedding_model']
            },
            "rag_system": {
                "available": pipeline.loader.embedding_model is not None and pipeline.vector_db is not None,
                "ready": True
            }
        }
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Project Management Routes

# In-memory storage for projects and files (replace with database in production)
PROJECTS_DB = {}
FILES_DB = {}

def save_project_to_filesystem(project_id: str):
    """Save a project to the filesystem"""
    try:
        if project_id not in PROJECTS_DB:
            return False
        
        project = PROJECTS_DB[project_id]
        projects_dir = os.path.join(os.getcwd(), "data", "projects")
        project_dir = os.path.join(projects_dir, project_id)
        
        # Create project directory
        os.makedirs(project_dir, exist_ok=True)
        
        # Save project metadata
        project_json = os.path.join(project_dir, "project.json")
        with open(project_json, 'w') as f:
            json.dump(project, f, indent=2)
        
        # Save project files
        project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
        files_json = os.path.join(project_dir, "files.json")
        with open(files_json, 'w') as f:
            json.dump(project_files, f, indent=2)
        
        # Update project stats
        project["file_count"] = len(project_files)
        project["total_size"] = sum(f["size"] for f in project_files)
        project["updated_at"] = datetime.now().isoformat()
        
        # Save updated project
        with open(project_json, 'w') as f:
            json.dump(project, f, indent=2)
        
        return True
    except Exception as e:
        print(f"❌ Error saving project {project_id}: {e}")
        return False

def save_all_projects_to_filesystem():
    """Save all projects to the filesystem"""
    try:
        projects_dir = os.path.join(os.getcwd(), "data", "projects")
        os.makedirs(projects_dir, exist_ok=True)
        
        # Save each project
        for project_id in PROJECTS_DB:
            save_project_to_filesystem(project_id)
        
        # Create projects summary
        projects_summary = {
            "projects": list(PROJECTS_DB.values()),
            "files": list(FILES_DB.values()),
            "last_updated": datetime.now().isoformat()
        }
        
        summary_path = os.path.join(projects_dir, "projects_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(projects_summary, f, indent=2)
        
        print(f"✅ Saved {len(PROJECTS_DB)} projects and {len(FILES_DB)} files to filesystem")
        return True
    except Exception as e:
        print(f"❌ Error saving projects to filesystem: {e}")
        return False

def load_projects():
    """Load projects from the filesystem"""
    global PROJECTS_DB, FILES_DB
    
    try:
        # Load test database if it exists
        test_db_path = os.path.join(os.getcwd(), "data", "test_database.json")
        if os.path.exists(test_db_path):
            with open(test_db_path, 'r') as f:
                db_data = json.load(f)
                PROJECTS_DB = db_data.get('projects', {})
                FILES_DB = db_data.get('files', {})
                print(f"✅ Loaded {len(PROJECTS_DB)} projects and {len(FILES_DB)} files from test database")
                return
        
        # If no test database, try to load from individual project files
        projects_dir = os.path.join(os.getcwd(), "data", "projects")
        if os.path.exists(projects_dir):
            for project_dir in os.listdir(projects_dir):
                project_path = os.path.join(projects_dir, project_dir)
                if os.path.isdir(project_path):
                    project_json = os.path.join(project_path, "project.json")
                    files_json = os.path.join(project_path, "files.json")
                    
                    if os.path.exists(project_json):
                        with open(project_json, 'r') as f:
                            project_data = json.load(f)
                            PROJECTS_DB[project_data['id']] = project_data
                    
                    if os.path.exists(files_json):
                        with open(files_json, 'r') as f:
                            files_data = json.load(f)
                            for file_info in files_data:
                                FILES_DB[file_info['id']] = file_info
            
            print(f"✅ Loaded {len(PROJECTS_DB)} projects and {len(FILES_DB)} files from project directories")
        
    except Exception as e:
        print(f"❌ Error loading test projects: {e}")

# Load projects on module import
load_projects()

@router.post("/api/projects")
async def create_project(project: ProjectCreate):
    """Create a new project"""
    try:
        project_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        new_project = {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "tags": project.tags or [],
            "created_at": now,
            "updated_at": now,
            "file_count": 0,
            "total_size": 0
        }
        
        PROJECTS_DB[project_id] = new_project
        save_project_to_filesystem(project_id)
        return new_project
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/projects")
async def list_projects():
    """List all projects"""
    try:
        # Ensure projects are loaded
        if not PROJECTS_DB:
            load_projects()
        
        projects = list(PROJECTS_DB.values())
        return projects
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/projects/refresh")
async def refresh_projects():
    """Refresh projects from filesystem"""
    try:
        load_projects()
        projects = list(PROJECTS_DB.values())
        return {
            "message": "Projects refreshed successfully",
            "projects_count": len(projects),
            "files_count": len(FILES_DB)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/projects/sync")
async def sync_projects_with_disk():
    """Synchronize in-memory state with actual files on disk"""
    try:
        from pathlib import Path
        import os
        
        print("🔄 Starting automatic sync of projects with disk...")
        
        projects_dir = Path("data/projects")
        synced_projects = []
        total_files_before = len(FILES_DB)
        
        # Process each project
        for project_id, project in PROJECTS_DB.items():
            project_dir = projects_dir / project_id
            if not project_dir.exists():
                continue
                
            # Get files in memory for this project
            memory_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
            
            # Get actual files on disk
            disk_files = list(project_dir.glob("*.aasx"))
            
            # Find files that exist in memory but not on disk
            memory_filenames = {f['filename'] for f in memory_files}
            disk_filenames = {f.name for f in disk_files}
            
            orphaned_memory_files = memory_filenames - disk_filenames
            
            if orphaned_memory_files:
                print(f"   🗑️  Removing {len(orphaned_memory_files)} orphaned files from project {project['name']}")
                
                # Remove orphaned files from memory
                files_to_remove = []
                for file_info in memory_files:
                    if file_info['filename'] in orphaned_memory_files:
                        files_to_remove.append(file_info['id'])
                
                for file_id in files_to_remove:
                    if file_id in FILES_DB:
                        del FILES_DB[file_id]
            
            # Update project stats
            updated_memory_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
            project['file_count'] = len(updated_memory_files)
            project['total_size'] = sum(f['size'] for f in updated_memory_files)
            project['updated_at'] = datetime.now().isoformat()
            
            # Save project to disk
            save_project_to_filesystem(project_id)
            synced_projects.append(project_id)
        
        # Save all projects to ensure consistency
        save_all_projects_to_filesystem()
        
        total_files_after = len(FILES_DB)
        files_removed = total_files_before - total_files_after
        
        print(f"✅ Sync completed: {len(synced_projects)} projects synced, {files_removed} orphaned files removed")
        
        return {
            "message": "Projects synchronized with disk successfully",
            "projects_synced": len(synced_projects),
            "files_removed": files_removed,
            "total_files_before": total_files_before,
            "total_files_after": total_files_after,
            "projects_count": len(PROJECTS_DB),
            "files_count": len(FILES_DB)
        }
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/projects/load-test")
async def load_test_projects_endpoint():
    """Manually load projects"""
    try:
        load_projects()
        projects = list(PROJECTS_DB.values())
        return {
            "message": "Projects loaded successfully",
            "projects_count": len(projects),
            "files_count": len(FILES_DB),
            "projects": projects
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    try:
        if project_id not in PROJECTS_DB:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return PROJECTS_DB[project_id]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project and all its files"""
    try:
        if project_id not in PROJECTS_DB:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Delete all files in the project
        project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
        for file_info in project_files:
            file_id = file_info["id"]
            # Remove physical file
            if os.path.exists(file_info["filepath"]):
                os.remove(file_info["filepath"])
            # Remove from database
            del FILES_DB[file_id]
        
        # Remove project
        del PROJECTS_DB[project_id]
        # Remove project directory from disk
        try:
            project_dir = os.path.join(os.getcwd(), "data", "projects", project_id)
            if os.path.exists(project_dir):
                import shutil
                shutil.rmtree(project_dir)
        except Exception as e:
            print(f"❌ Error deleting project directory: {e}")
        save_all_projects_to_filesystem()
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File Upload Routes

@router.post("/api/projects/{project_id}/upload")
async def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    description: str = Form(None)
):
    """Upload a file to a project"""
    try:
        if project_id not in PROJECTS_DB:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate file type
        if not file.filename.lower().endswith('.aasx'):
            raise HTTPException(status_code=400, detail="Only AASX files are allowed")
        
        # Check for duplicate file in the same project
        project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
        for existing_file in project_files:
            if existing_file["original_filename"] == file.filename:
                raise HTTPException(
                    status_code=409, 
                    detail=f"File '{file.filename}' already exists in this project. Please use a different filename or delete the existing file first."
                )
        
        # Create project upload directory
        project_dir = os.path.join("data", "projects", project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Generate filename based on original name with collision handling
        original_name = file.filename
        base_name = os.path.splitext(original_name)[0]
        extension = os.path.splitext(original_name)[1]
        
        # Sanitize filename (remove special characters, replace spaces with underscores)
        import re
        sanitized_base = re.sub(r'[^\w\-_.]', '_', base_name)
        sanitized_name = sanitized_base + extension
        
        # Handle filename collisions
        counter = 1
        final_filename = sanitized_name
        while os.path.exists(os.path.join(project_dir, final_filename)):
            final_filename = f"{sanitized_base}_{counter}{extension}"
            counter += 1
        
        file_path = os.path.join(project_dir, final_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create file record
        file_id = str(uuid.uuid4())
        file_info = {
            "id": file_id,
            "filename": final_filename,
            "original_filename": original_name,
            "project_id": project_id,
            "filepath": file_path,
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "description": description,
            "status": "not_processed",
            "processing_result": None
        }
        
        FILES_DB[file_id] = file_info
        
        # Update project stats
        PROJECTS_DB[project_id]["file_count"] += 1
        PROJECTS_DB[project_id]["total_size"] += file_size
        PROJECTS_DB[project_id]["updated_at"] = datetime.now().isoformat()
        save_project_to_filesystem(project_id)
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/projects/{project_id}/upload-url")
async def upload_file_from_url(request: FileUploadRequest):
    """Upload a file to a project from URL"""
    try:
        project_id = request.project_id
        if project_id not in PROJECTS_DB:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if not request.file_url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Validate URL
        parsed_url = urlparse(request.file_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL")
        
        # Download file
        response = requests.get(request.file_url, stream=True)
        response.raise_for_status()
        
        # Get filename from URL or Content-Disposition header
        filename = os.path.basename(parsed_url.path)
        if not filename or not filename.lower().endswith('.aasx'):
            # Try to get filename from Content-Disposition header
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                import re
                match = re.search(r'filename="?([^"]+)"?', content_disposition)
                if match:
                    filename = match.group(1)
        
        if not filename or not filename.lower().endswith('.aasx'):
            raise HTTPException(status_code=400, detail="Invalid file type or filename")
        
        # Check for duplicate file in the same project
        project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
        for existing_file in project_files:
            if existing_file["original_filename"] == filename:
                raise HTTPException(
                    status_code=409, 
                    detail=f"File '{filename}' already exists in this project. Please use a different filename or delete the existing file first."
                )
        
        # Create project upload directory
        project_dir = os.path.join("data", "projects", project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Generate filename based on original name with collision handling
        original_name = filename
        base_name = os.path.splitext(original_name)[0]
        extension = os.path.splitext(original_name)[1]
        
        # Sanitize filename (remove special characters, replace spaces with underscores)
        import re
        sanitized_base = re.sub(r'[^\w\-_.]', '_', base_name)
        sanitized_name = sanitized_base + extension
        
        # Handle filename collisions
        counter = 1
        final_filename = sanitized_name
        while os.path.exists(os.path.join(project_dir, final_filename)):
            final_filename = f"{sanitized_base}_{counter}{extension}"
            counter += 1
        
        file_path = os.path.join(project_dir, final_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            for chunk in response.iter_content(chunk_size=8192):
                buffer.write(chunk)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create file record
        file_id = str(uuid.uuid4())
        file_info = {
            "id": file_id,
            "filename": final_filename,
            "original_filename": original_name,
            "project_id": project_id,
            "filepath": file_path,
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "description": request.file_description,
            "status": "not_processed",
            "processing_result": None
        }
        
        FILES_DB[file_id] = file_info
        
        # Update project stats
        PROJECTS_DB[project_id]["file_count"] += 1
        PROJECTS_DB[project_id]["total_size"] += file_size
        PROJECTS_DB[project_id]["updated_at"] = datetime.now().isoformat()
        save_project_to_filesystem(project_id)
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/projects/{project_id}/files")
async def list_project_files(project_id: str):
    """List all files in a project"""
    try:
        if project_id not in PROJECTS_DB:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
        return project_files
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/projects/{project_id}/files/{file_id}")
async def get_project_file(project_id: str, file_id: str):
    """Get a specific file in a project"""
    try:
        if project_id not in PROJECTS_DB:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if file_id not in FILES_DB:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = FILES_DB[file_id]
        if file_info["project_id"] != project_id:
            raise HTTPException(status_code=404, detail="File not found in this project")
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/projects/{project_id}/files/{file_id}/process")
async def process_project_file(project_id: str, file_id: str):
    """Process a file in a project through ETL pipeline"""
    try:
        if project_id not in PROJECTS_DB:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if file_id not in FILES_DB:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = FILES_DB[file_id]
        if file_info["project_id"] != project_id:
            raise HTTPException(status_code=404, detail="File not found in project")
        
        # Update file status
        file_info["status"] = "processing"
        FILES_DB[file_id] = file_info
        
        # Save project to filesystem to persist processing status
        save_project_to_filesystem(project_id)
        
        try:
            # Process file through ETL pipeline
            pipeline = get_etl_pipeline()
            result = pipeline.process_aasx_file(file_info["filepath"])
            
            # Update file status and result
            file_info["status"] = "completed" if result["status"] == "completed" else "error"
            file_info["processing_result"] = result
            FILES_DB[file_id] = file_info
            
            # Save project to filesystem to persist status changes
            save_project_to_filesystem(project_id)
            
            return result
            
        except Exception as e:
            # Update file status to error
            file_info["status"] = "error"
            file_info["processing_result"] = {"error": str(e)}
            FILES_DB[file_id] = file_info
            
            # Save project to filesystem to persist status changes
            save_project_to_filesystem(project_id)
            
            raise HTTPException(status_code=500, detail=str(e))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/projects/{project_id}/files/{file_id}")
async def delete_project_file(project_id: str, file_id: str):
    """Delete a file from a project"""
    try:
        if project_id not in PROJECTS_DB:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if file_id not in FILES_DB:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = FILES_DB[file_id]
        if file_info["project_id"] != project_id:
            raise HTTPException(status_code=404, detail="File not found in project")
        
        # Remove physical file
        if os.path.exists(file_info["filepath"]):
            os.remove(file_info["filepath"])
        
        # Update project stats
        PROJECTS_DB[project_id]["file_count"] -= 1
        PROJECTS_DB[project_id]["total_size"] -= file_info["size"]
        PROJECTS_DB[project_id]["updated_at"] = datetime.now().isoformat()
        save_project_to_filesystem(project_id)
        
        # Remove from database
        del FILES_DB[file_id]
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/projects/{project_id}/files/{file_id}/view")
async def prepare_file_for_blazor_view(project_id: str, file_id: str):
    """Prepare a file for viewing in Blazor by providing file information"""
    try:
        if project_id not in PROJECTS_DB:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if file_id not in FILES_DB:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = FILES_DB[file_id]
        if file_info["project_id"] != project_id:
            raise HTTPException(status_code=404, detail="File not found in this project")
        
        # Check if file exists on disk
        if not os.path.exists(file_info["filepath"]):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        # Return file information for Blazor viewer
        # The file is accessible via the mounted /app/data volume
        return {
            "success": True,
            "message": f"File {file_info['original_filename']} ready for Blazor viewing",
            "filename": f"projects/{project_id}/{file_info['original_filename']}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 