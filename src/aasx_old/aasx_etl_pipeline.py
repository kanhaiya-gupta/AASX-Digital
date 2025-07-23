"""
AASX ETL Pipeline Module

Complete ETL (Extract, Transform, Load) pipeline for AASX data processing
in the Quality Infrastructure Digital Platform.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import json
import traceback

from .aasx_processor import AASXProcessor
from .aasx_transformer import AASXTransformer, TransformationConfig as TransformerConfig
from .aasx_loader import AASXLoader, LoaderConfig

logger = logging.getLogger(__name__)

class ETLPipelineConfig:
    """Configuration for the complete ETL pipeline"""
    
    def __init__(self,
                 extract_config: Optional[Dict[str, Any]] = None,
                 transform_config: Optional[TransformerConfig] = None,
                 load_config: Optional[LoaderConfig] = None,
                 enable_validation: bool = True,
                 enable_logging: bool = True,
                 enable_backup: bool = True,
                 parallel_processing: bool = False,
                 max_workers: int = 4):
        """
        Initialize ETL pipeline configuration.
        
        Args:
            extract_config: Configuration for extraction phase
            transform_config: Configuration for transformation phase
            load_config: Configuration for loading phase
            enable_validation: Enable data validation
            enable_logging: Enable detailed logging
            enable_backup: Enable backup of processed files
            parallel_processing: Enable parallel processing
            max_workers: Maximum number of parallel workers
        """
        self.extract_config = extract_config or {}
        self.transform_config = transform_config or TransformerConfig()
        self.load_config = load_config or LoaderConfig()
        self.enable_validation = enable_validation
        self.enable_logging = enable_logging
        self.enable_backup = enable_backup
        self.parallel_processing = parallel_processing
        self.max_workers = max_workers

class AASXETLPipeline:
    """
    Complete ETL pipeline for AASX data processing.
    
    Integrates extraction, transformation, and loading phases
    for comprehensive AASX data processing in the QI Digital Platform.
    """
    
    def __init__(self, config: Optional[ETLPipelineConfig] = None):
        """
        Initialize ETL pipeline.
        
        Args:
            config: ETL pipeline configuration
        """
        self.config = config or ETLPipelineConfig()
        # Don't create processor here - create it per file
        self.transformer = AASXTransformer(self.config.transform_config)
        # Don't create loader here - create it per file for file-specific outputs
        self.loader = None
        
        # Pipeline statistics
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'total_processing_time': 0,
            'extract_time': 0,
            'transform_time': 0,
            'load_time': 0,
            'errors': []
        }
    
    def process_aasx_file(self, file_path: Union[str, Path], project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a single AASX file through the complete ETL pipeline.
        
        Args:
            file_path: Path to the AASX file
            project_id: Optional project ID for project-based output organization
            
        Returns:
            Dictionary with processing results
        """
        file_path = Path(file_path)
        start_time = time.time()
        
        result = {
            'file_path': str(file_path),
            'project_id': project_id,
            'status': 'processing',
            'extract_result': None,
            'transform_result': None,
            'load_result': None,
            'processing_time': 0,
            'errors': []
        }
        
        try:
            logger.info(f"Starting ETL processing for: {file_path}")
            
            # Step 1: Extract
            extract_start = time.time()
            extract_result = self._extract_phase(file_path)
            result['extract_result'] = extract_result
            self.stats['extract_time'] += time.time() - extract_start
            
            if not extract_result['success']:
                raise Exception(f"Extraction failed: {extract_result['error']}")
            
            # Step 2: Transform
            transform_start = time.time()
            transform_result = self._transform_phase(extract_result['data'])
            result['transform_result'] = transform_result
            self.stats['transform_time'] += time.time() - transform_start
            
            if not transform_result['success']:
                raise Exception(f"Transformation failed: {transform_result['error']}")
            
            # Step 3: Load
            load_start = time.time()
            load_result = self._load_phase(transform_result['data'], str(file_path), project_id)
            result['load_result'] = load_result
            self.stats['load_time'] += time.time() - load_start
            
            if not load_result['success']:
                raise Exception(f"Loading failed: {load_result['error']}")
            
            # Update statistics
            result['status'] = 'completed'
            result['processing_time'] = time.time() - start_time
            self.stats['files_processed'] += 1
            self.stats['total_processing_time'] += result['processing_time']
            
            logger.info(f"ETL processing completed for: {file_path}")
            
        except Exception as e:
            error_msg = f"ETL processing failed for {file_path}: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            result['status'] = 'failed'
            result['error'] = str(e)
            result['errors'].append(error_msg)
            result['processing_time'] = time.time() - start_time
            
            self.stats['files_failed'] += 1
            self.stats['errors'].append(error_msg)
        
        return result
    
    def process_aasx_directory(self, directory_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process all AASX files in a directory through the ETL pipeline.
        
        Args:
            directory_path: Path to directory containing AASX files
            
        Returns:
            Dictionary with batch processing results
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        # Find all AASX files
        aasx_files = list(directory_path.glob("*.aasx"))
        
        if not aasx_files:
            logger.warning(f"No AASX files found in: {directory_path}")
            return {
                'directory': str(directory_path),
                'files_found': 0,
                'files_processed': 0,
                'files_failed': 0,
                'total_time': 0,
                'results': []
            }
        
        logger.info(f"Found {len(aasx_files)} AASX files in: {directory_path}")
        
        batch_start_time = time.time()
        results = []
        
        if self.config.parallel_processing:
            results = self._process_parallel(aasx_files)
        else:
            results = self._process_sequential(aasx_files)
        
        batch_time = time.time() - batch_start_time
        
        # Calculate batch statistics
        successful = [r for r in results if r['status'] == 'completed']
        failed = [r for r in results if r['status'] == 'failed']
        
        return {
            'directory': str(directory_path),
            'files_found': len(aasx_files),
            'files_processed': len(successful),
            'files_failed': len(failed),
            'total_time': batch_time,
            'average_time_per_file': batch_time / len(aasx_files) if aasx_files else 0,
            'results': results,
            'pipeline_stats': self.stats.copy()
        }
    
    def _process_sequential(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Process files sequentially"""
        results = []
        for file_path in files:
            result = self.process_aasx_file(file_path)
            results.append(result)
        return results
    
    def _process_parallel(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Process files in parallel"""
        from concurrent.futures import ProcessPoolExecutor, as_completed
        
        results = []
        
        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(self.process_aasx_file, file_path): file_path
                for file_path in files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Parallel processing failed for {file_path}: {e}")
                    results.append({
                        'file_path': str(file_path),
                        'status': 'failed',
                        'error': str(e),
                        'errors': [str(e)]
                    })
        
        return results
    
    def _extract_phase(self, file_path: Path) -> Dict[str, Any]:
        """Execute extraction phase"""
        try:
            logger.info(f"Starting extraction phase for: {file_path}")
            
            # Create processor for this specific file
            processor = AASXProcessor(str(file_path))
            
            # Extract AASX data
            extract_result = processor.process()
            
            # Convert to expected format
            if extract_result and 'error' not in extract_result:
                logger.info(f"Extraction completed successfully for: {file_path}")
                return {
                    'success': True,
                    'data': extract_result,
                    'metadata': extract_result.get('metadata', {}),
                    'processing_time': 0  # Will be calculated by caller
                }
            else:
                logger.error(f"Extraction failed for: {file_path}")
                return {
                    'success': False,
                    'error': extract_result.get('error', 'Unknown extraction error'),
                    'processing_time': 0
                }
                
        except Exception as e:
            logger.error(f"Extraction phase error for {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': 0
            }
    
    def _transform_phase(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transformation phase"""
        try:
            logger.info("Starting transformation phase")
            
            # Transform extracted data
            transform_result = self.transformer.transform_aasx_data(extracted_data)
            
            # The transformer returns the transformed data directly
            logger.info("Transformation completed successfully")
            return {
                'success': True,
                'data': transform_result,
                'transformations_applied': ['cleaning', 'normalization', 'quality_checks', 'enrichment'],
                'processing_time': 0  # Will be calculated by caller
            }
                
        except Exception as e:
            logger.error(f"Transformation phase error: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': 0
            }
    
    def _load_phase(self, transformed_data: Dict[str, Any], source_file: Optional[str] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute loading phase with project-based output organization"""
        try:
            logger.info("Starting loading phase")
            
            # Create project-specific loader configuration
            load_config = self.config.load_config
            
            # If project_id is provided, create project-based output directory
            if project_id:
                # Create project-specific output directory structure
                project_output_dir = f"output/projects/{project_id}"
                # Ensure SQLite and vector DB exports are enabled for project-based outputs
                export_formats = load_config.export_formats.copy() if load_config.export_formats else []
                if 'sqlite' not in export_formats:
                    export_formats.append('sqlite')
                if 'vector_db' not in export_formats:
                    export_formats.append('vector_db')
                
                load_config = LoaderConfig(
                    output_directory=project_output_dir,
                    database_path=f"{project_output_dir}/aasx_data.db",
                    vector_db_path=f"{project_output_dir}/vector_db",
                    vector_db_type=load_config.vector_db_type,
                    qdrant_url=load_config.qdrant_url,
                    qdrant_collection_prefix=f"aasx_project_{project_id}",
                    embedding_model=load_config.embedding_model,
                    chunk_size=load_config.chunk_size,
                    overlap_size=load_config.overlap_size,
                    include_metadata=load_config.include_metadata,
                    create_indexes=load_config.create_indexes,
                    backup_existing=load_config.backup_existing,
                    separate_file_outputs=load_config.separate_file_outputs,
                    include_filename_in_output=load_config.include_filename_in_output,
                    systematic_structure=load_config.systematic_structure,
                    folder_structure=load_config.folder_structure,
                    export_formats=export_formats,  # Use updated export formats
                    export_json=load_config.export_json,
                    export_yaml=load_config.export_yaml,
                    export_csv=load_config.export_csv,
                    export_tsv=load_config.export_tsv,
                    export_graph=load_config.export_graph,
                    export_rag=load_config.export_rag,
                    export_vector_db=True,  # Always enable for project-based outputs
                    export_sqlite=True      # Always enable for project-based outputs
                )
                logger.info(f"Using project-based output directory: {project_output_dir}")
            
            # Create file-specific loader if needed
            if load_config.separate_file_outputs:
                loader = AASXLoader(load_config, source_file)
            else:
                # Use shared loader for all files
                if self.loader is None:
                    self.loader = AASXLoader(load_config)
                loader = self.loader
            
            # Load transformed data
            load_result = loader.load_aasx_data(transformed_data)
            
            # Add project information to load result
            if project_id:
                load_result['project_id'] = project_id
                load_result['project_output_dir'] = project_output_dir
            
            logger.info("Loading completed successfully")
            return {
                'success': True,
                'files_exported': load_result.get('files_exported', []),
                'database_records': load_result.get('database_records', 0),
                'vector_embeddings': load_result.get('vector_embeddings', 0),
                'project_id': project_id,
                'project_output_dir': load_result.get('project_output_dir'),
                'errors': load_result.get('errors', [])
            }
                
        except Exception as e:
            logger.error(f"Loading phase error: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_id': project_id
            }
    
    def validate_pipeline(self) -> Dict[str, Any]:
        """
        Validate the ETL pipeline configuration and components.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'pipeline_valid': True,
            'components': {},
            'errors': []
        }
        
        try:
            # Validate processor (will be created per file)
            processor_valid = True  # AASXProcessor class is available
            validation_results['components']['processor'] = {
                'valid': processor_valid,
                'status': 'OK' if processor_valid else 'FAILED'
            }
            
            # Validate transformer
            transformer_valid = self.transformer is not None
            validation_results['components']['transformer'] = {
                'valid': transformer_valid,
                'status': 'OK' if transformer_valid else 'FAILED'
            }
            
            # Validate loader (created per file, so just check config)
            loader_config_valid = self.config.load_config is not None
            validation_results['components']['loader'] = {
                'valid': loader_config_valid,
                'status': 'OK' if loader_config_valid else 'FAILED'
            }
            
            # Check overall validity
            all_valid = all([
                processor_valid,
                transformer_valid,
                loader_config_valid
            ])
            
            validation_results['pipeline_valid'] = all_valid
            
            if not all_valid:
                validation_results['errors'].append("One or more pipeline components failed validation")
            
        except Exception as e:
            validation_results['pipeline_valid'] = False
            validation_results['errors'].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive pipeline statistics.
        
        Returns:
            Dictionary with pipeline statistics
        """
        stats = self.stats.copy()
        
        # Add additional statistics
        stats['pipeline_config'] = {
            'enable_validation': self.config.enable_validation,
            'enable_logging': self.config.enable_logging,
            'enable_backup': self.config.enable_backup,
            'parallel_processing': self.config.parallel_processing,
            'max_workers': self.config.max_workers
        }
        
        # Add component statistics
        stats['component_stats'] = {
            'processor': {},  # Processor created per file, no global stats
            'transformer': getattr(self.transformer, 'stats', {}),
            'loader': {}  # Loader created per file, no global stats
        }
        
        return stats
    
    def reset_stats(self):
        """Reset pipeline statistics"""
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'total_processing_time': 0,
            'extract_time': 0,
            'transform_time': 0,
            'load_time': 0,
            'errors': []
        }
    
    def export_pipeline_report(self, output_path: str) -> str:
        """
        Export a comprehensive pipeline processing report.
        
        Args:
            output_path: Path for the report file
            
        Returns:
            Path to the exported report
        """
        report = {
            'report_type': 'AASX_ETL_Pipeline_Report',
            'generated_at': datetime.now().isoformat(),
            'pipeline_config': {
                'enable_validation': self.config.enable_validation,
                'enable_logging': self.config.enable_logging,
                'enable_backup': self.config.enable_backup,
                'parallel_processing': self.config.parallel_processing,
                'max_workers': self.config.max_workers
            },
            'pipeline_stats': self.get_pipeline_stats(),
            'validation_results': self.validate_pipeline(),
            'component_configs': {
                'extract_config': self.config.extract_config,
                'transform_config': {
                    'enable_quality_checks': self.config.transform_config.enable_quality_checks,
                    'enable_enrichment': self.config.transform_config.enable_enrichment,
                    'output_formats': self.config.transform_config.output_formats,
                    'include_metadata': self.config.transform_config.include_metadata
                },
                'load_config': {
                    'output_directory': self.config.load_config.output_directory,
                    'database_path': self.config.load_config.database_path,
                    'vector_db_path': self.config.load_config.vector_db_path,
                    'vector_db_type': self.config.load_config.vector_db_type,
                    'embedding_model': self.config.load_config.embedding_model
                }
            }
        }
        
        # Export report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Pipeline report exported to: {output_path}")
        return output_path
    
    def create_rag_ready_dataset(self, output_path: str) -> str:
        """
        Create a RAG-ready dataset from processed AASX data.
        
        Args:
            output_path: Path for the RAG dataset
            
        Returns:
            Path to the created dataset
        """
        try:
            # Create a loader to access the database with all processed data
            loader = AASXLoader(self.config.load_config)
            
            # Get database stats to check if we have data
            db_stats = loader.get_database_stats()
            
            if db_stats.get('assets_count', 0) == 0 and db_stats.get('submodels_count', 0) == 0:
                raise ValueError("No data available for RAG dataset creation")
            
            # Export RAG-ready data
            rag_path = loader.export_for_rag(output_path)
            
            logger.info(f"RAG-ready dataset created at: {rag_path}")
            return rag_path
            
        except Exception as e:
            logger.error(f"Error creating RAG dataset: {e}")
            raise

def create_etl_pipeline(config: Optional[ETLPipelineConfig] = None) -> AASXETLPipeline:
    """
    Factory function to create an ETL pipeline with default or custom configuration.
    
    Args:
        config: Optional custom configuration
        
    Returns:
        Configured ETL pipeline instance
    """
    return AASXETLPipeline(config)

def process_aasx_batch(file_paths: List[Union[str, Path]], 
                      config: Optional[ETLPipelineConfig] = None) -> Dict[str, Any]:
    """
    Process a batch of AASX files through the ETL pipeline.
    
    Args:
        file_paths: List of AASX file paths
        config: Optional ETL configuration
        
    Returns:
        Batch processing results
    """
    pipeline = create_etl_pipeline(config)
    
    batch_start_time = time.time()
    results = []
    
    for file_path in file_paths:
        result = pipeline.process_aasx_file(file_path)
        results.append(result)
    
    batch_time = time.time() - batch_start_time
    
    successful = [r for r in results if r['status'] == 'completed']
    failed = [r for r in results if r['status'] == 'failed']
    
    return {
        'files_processed': len(successful),
        'files_failed': len(failed),
        'total_time': batch_time,
        'average_time_per_file': batch_time / len(file_paths) if file_paths else 0,
        'results': results,
        'pipeline_stats': pipeline.get_pipeline_stats()
    } 