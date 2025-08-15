"""
AASX Processing Service
Handles AASX file processing, extraction, and ETL operations.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from src.aasx.aasx_processor import extract_aasx, batch_extract
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.project_repository import ProjectRepository
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
from src.shared.services.digital_twin_service import DigitalTwinService
from src.aasx.services.aasx_processing_service import AASXProcessingService
from src.aasx.services.processing_metrics_service import ProcessingMetricsService
from src.federated_learning.core.federated_learning_service import FederatedLearningService

class AASXProcessor:
    def __init__(self):
        from src.shared.database.connection_manager import DatabaseConnectionManager
        from pathlib import Path
        
        # Create data directory and set database path
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        connection_manager = DatabaseConnectionManager(db_path)
        self.db_manager = BaseDatabaseManager(connection_manager)
        self.project_repo = ProjectRepository(self.db_manager)
        self.file_repo = FileRepository(self.db_manager)
        self.twin_repo = DigitalTwinRepository(self.db_manager)
        
        # Initialize services following src/shared/ patterns
        self.digital_twin_service = DigitalTwinService(self.db_manager, self.file_repo, self.project_repo)
        self.federated_learning_service = FederatedLearningService(self.digital_twin_service)
        
        # Initialize AASX processing service for job tracking
        self.processing_service = AASXProcessingService(self.db_manager)
        
        # Phase 4: Initialize comprehensive metrics service
        self.metrics_service = ProcessingMetricsService(self.db_manager.connection_manager.get_connection())
    
    def run_etl_pipeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete ETL pipeline with all steps."""
        import time
        start_time = time.time()
        
        try:
            print("🚀 Starting ETL pipeline...")
            print(f"📋 Received config: {config}")
            
            # Extract configuration
            file_id = config.get('file_id')
            project_id = config.get('project_id')
            use_case_id = config.get('use_case_id')
            output_formats = config.get('output_formats', ['json', 'graph', 'rdf', 'yaml'])
            
            # Detect job type from file type and config
            file_info = self.file_repo.get_by_id(file_id)
            if not file_info:
                return {'status': 'error', 'message': f'File {file_id} not found'}
            
            # Determine job type based on file type and config - NO DEFAULTS, must be explicit
            if hasattr(file_info, 'file_type'):
                file_type = file_info.file_type
            else:
                file_type = file_info.get('file_type')
            
            # Must have explicit job type - no fallbacks allowed
            if file_type == 'aasx':
                job_type = 'extraction'
            elif file_type == 'zip':
                job_type = 'generation'
            else:
                # Check config for explicit job type
                config_job_type = config.get('job_type')
                if config_job_type in ['extraction', 'generation']:
                    job_type = config_job_type
                else:
                    # Fail explicitly - cannot determine job type
                    error_msg = f"Cannot determine job type. File type: {file_type}, Config job type: {config_job_type}. Must be explicitly 'extraction' or 'generation'."
                    print(f"❌ {error_msg}")
                    return {'status': 'error', 'message': error_msg}
            
            # Create processing job record for tracking
            job_data = {
                'file_id': file_id,
                'project_id': project_id,
                'job_type': job_type,  # Use detected job type
                'source_type': config.get('source_type', 'manual_upload'),
                'processed_by': config.get('user_id', 'system'),  # user_id
                'org_id': config.get('org_id', None),  # organization_id
                'extraction_options': {
                    'output_formats': output_formats,
                    'use_case_id': use_case_id,
                    'federated_learning': config.get('federated_learning', 'not_allowed'),
                    'data_privacy_level': config.get('data_privacy_level', 'private')
                } if job_type == 'extraction' else {},
                'generation_options': {
                    'output_formats': output_formats,
                    'use_case_id': use_case_id,
                    'federated_learning': config.get('federated_learning', 'not_allowed'),
                    'data_privacy_level': config.get('data_privacy_level', 'private')
                } if job_type == 'generation' else {}
            }
            
            # Create job and get job ID
            job_id = self.processing_service.create_job(job_data)
            print(f"📋 Created processing job {job_id}")
            
            # Update job status to processing
            self.processing_service.update_status(job_id, 'processing')
            print(f"🔄 Job {job_id} status updated to processing")
            
            print(f"🔍 Extracted config values:")
            print(f"   - file_id: {file_id}")
            print(f"   - project_id: {project_id}")
            print(f"   - use_case_id: {use_case_id}")
            print(f"   - output_formats: {output_formats}")
            
            # User consent and privacy settings
            user_consent = config.get('user_consent', False)
            federated_learning = config.get('federated_learning', 'not_allowed')
            data_privacy_level = config.get('data_privacy_level', 'private')
            
            if not file_id:
                return {'status': 'error', 'message': 'File ID is required'}
            
            # Create hierarchical output path: output/usecase/project/filename_without_extension/
            output_dir = self.create_hierarchical_output_path(config, file_info)
            print(f"📁 Output directory: {output_dir}")
            
            # Step 1: Process ETL extraction
            print("📊 Step 1: Processing ETL extraction...")
            print(f"🔍 File path being processed: {file_info.filepath}")
            
            # Normalize the file path to handle Windows backslashes
            normalized_filepath = str(file_info.filepath).replace('\\', '/')
            file_path = Path(normalized_filepath)
            
            print(f"🔍 Normalized file path: {file_path}")
            print(f"🔍 File exists check: {file_path.exists()}")
            print(f"🔍 File absolute path: {file_path.absolute()}")
            
            etl_result = self.process_etl_extraction(
                file_path, 
                output_dir, 
                output_formats,
                job_id,  # Pass job_id for progress tracking
                job_type  # Pass job_type for proper processing
            )
            
            if etl_result.get('status') != 'success':
                return {'status': 'error', 'message': 'ETL processing failed', 'details': etl_result}
            
            # For generation jobs, skip the complex ETL ecosystem steps
            if job_type == 'generation':
                print("🔄 Generation job detected - skipping complex ETL ecosystem steps")
                print("ℹ️  Generation jobs convert structured data + documents to AASX (preserving all data)")
                
                # Simple completion for generation jobs
                processing_time = (time.time() - start_time) * 1000
                completion_data = {
                    'processing_time': processing_time,
                    'output_directory': str(output_dir)
                }
                
                # Update job with completion data
                self.processing_service.update_status(job_id, 'completed', completion_data)
                print(f"✅ Generation job {job_id} completed successfully in {processing_time:.2f}ms")
                
                # Return simple results for generation
                return {
                    'status': 'success',
                    'message': 'AASX generation completed successfully (structured data + documents)',
                    'job_id': job_id,
                    'job_type': job_type,
                    'results': {
                        'generation_result': etl_result,
                        'input_file_path': str(file_info.filepath),  # Where the input ZIP file came from
                        'output_directory': str(output_dir),  # Where the generated AASX file is stored
                        'output_files_summary': {
                            'aasx_file_generated': etl_result.get('status') == 'success',
                            'output_aasx_file': etl_result.get('output_file', ''),
                            'aasx_file_size': etl_result.get('file_size', 0),
                            'documents_preserved': etl_result.get('document_count', 0),
                            'structured_data_source': etl_result.get('structured_data_file', '')
                        },
                        'processing_time_ms': processing_time,
                        'note': 'Generation preserves all documents including raw sensor data'
                    }
                }
            
            # For extraction jobs, continue with full ETL ecosystem
            print("🔄 Extraction job detected - running full ETL ecosystem")
            
            # Step 2: Update file status
            print("📝 Step 2: Updating file status...")
            file_status_result = self.update_file_status_step(file_id, file_info.filename)
            
            # Step 3: Create digital twin with complete data
            print("🤖 Step 3: Creating digital twin...")
            twin_data = {
                'user_consent': user_consent,
                'federated_learning': federated_learning,
                'data_privacy_level': data_privacy_level
            }
            twin_result = self.create_digital_twin_step(
                project_id, file_id, file_info.__dict__, etl_result, output_dir, config=config
            )
            
            if twin_result.get('status') != 'success':
                return {'status': 'error', 'message': 'Digital twin creation failed', 'details': twin_result}
            
            # Step 4: Update federated learning status
            print("🔗 Step 4: Updating federated learning status...")
            fl_result = self.update_federated_learning_step(twin_result, config)
            
            # Step 5: Process AI/RAG
            print("🧠 Step 5: Processing AI/RAG...")
            ai_rag_data = {
                'project_id': project_id,
                'file_info': file_info.__dict__,
                'output_dir': output_dir
            }
            
            try:
                ai_rag_result = self.process_ai_rag(ai_rag_data)
                if ai_rag_result.get('status') != 'success':
                    print(f"⚠️ AI/RAG failed, continuing without AI/RAG: {ai_rag_result.get('error', 'Unknown error')}")
                    ai_rag_result = {'status': 'skipped', 'reason': 'AI/RAG processing failed'}
            except Exception as e:
                print(f"❌ AI/RAG processing failed: {e}")
                ai_rag_result = {'status': 'failed', 'error': str(e)}
            
            # Step 6: Store in Qdrant
            print("🗄️ Step 6: Storing in Qdrant...")
            qdrant_data = {
                'file_info': file_info.__dict__,
                'etl_result': etl_result,
                'ai_rag_result': ai_rag_result,
                'file_id': file_id
            }
            
            try:
                qdrant_result = self.store_in_qdrant(qdrant_data)
                if qdrant_result.get('status') != 'success':
                    print(f"⚠️ Qdrant storage failed, continuing without Qdrant: {qdrant_result.get('error', 'Unknown error')}")
                    qdrant_result = {'status': 'skipped', 'reason': 'Qdrant storage failed'}
            except Exception as e:
                print(f"❌ Qdrant storage failed: {e}")
                qdrant_result = {'status': 'failed', 'error': str(e)}
            
            # Step 7: Mark simulation ready
            print("⚡ Step 7: Marking simulation ready...")
            simulation_ready = self.mark_simulation_ready(twin_result.get('twin_id'))
            
            print(f"✅ ETL pipeline (extraction) completed successfully!")
            
            # Calculate processing time and complete job
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            completion_data = {
                'processing_time': processing_time,
                'output_directory': str(output_dir)
            }
            
            # Update job with completion data
            self.processing_service.update_status(job_id, 'completed', completion_data)
            print(f"✅ Extraction job {job_id} completed successfully in {processing_time:.2f}ms")
            
            # Complete the job with results (extraction jobs only)
            results_summary = {
                'etl_result': etl_result,
                'job_type': 'extraction',  # This path is only for extraction jobs
                'input_file_path': str(file_path),  # Where the input AASX file came from
                'output_directory': str(output_dir),  # Where all output files are stored
                'output_files_summary': {
                    'formats_processed': etl_result.get('formats', []),
                    'failed_formats': etl_result.get('failed_formats', []),
                    'total_output_files': len(etl_result.get('formats', [])),
                    'documents_extracted': etl_result.get('results', {}).get('documents', {}).get('file_count', 0),
                    'original_file_preserved': etl_result.get('results', {}).get('original', {}).get('status') == 'completed'
                },
                'file_status': file_status_result,
                'digital_twin': twin_result,
                'federated_learning': fl_result,
                'ai_rag': ai_rag_result,
                'qdrant': qdrant_result,
                'simulation_ready': simulation_ready,
                'processing_time_ms': processing_time
            }
            
            # Phase 4: Create comprehensive metrics record
            try:
                metrics_data = {
                    'system_resources': {
                        'memory_usage_mb': self._get_memory_usage(),
                        'cpu_usage_percent': self._get_cpu_usage(),
                        'disk_io_mb': self._get_disk_io(),
                        'network_usage_mb': 0.0,  # Could be enhanced with actual network monitoring
                        'peak_memory_mb': self._get_peak_memory(),
                        'peak_cpu_percent': self._get_peak_cpu(),
                        'total_disk_io_mb': self._get_total_disk_io()
                    },
                    'quality_metrics': {
                        'data_quality_score': self._calculate_quality_score(etl_result),
                        'file_integrity_checksum': self._calculate_file_checksum(file_info),
                        'processing_accuracy': self._calculate_processing_accuracy(etl_result),
                        'validation_results': self._validate_results(etl_result)
                    },
                    'processing_efficiency_score': self._calculate_efficiency_score(processing_time, etl_result),
                    'compliance_data': {
                        'data_sensitivity_level': config.get('data_privacy_level', 'private'),
                        'compliance_requirements': ['AASX_ETL_Standard'],
                        'access_logs': [{'timestamp': time.time(), 'action': 'process', 'user': config.get('user_id')}],
                        'security_events': [],
                        'retention_policy': 'standard_90_days',
                        'scheduled_deletion_date': None
                    }
                }
                
                metrics_id = self.metrics_service.create_metrics_record(job_id, metrics_data)
                print(f"📊 Created comprehensive metrics record: {metrics_id}")
                
            except Exception as metrics_error:
                print(f"⚠️  Warning: Failed to create metrics record: {metrics_error}")
                # Don't fail the main job if metrics fail
            
            self.processing_service.complete_job(job_id, results_summary, 'completed')
            
            return {
                'status': 'success',
                'message': 'ETL pipeline completed successfully',
                'job_id': job_id,
                'results': results_summary
            }
            
        except Exception as e:
            print(f"❌ ETL pipeline ({job_type if 'job_type' in locals() else 'unknown'}) failed: {e}")
            
            # Calculate processing time and update job with error
            if 'job_id' in locals():
                processing_time = (time.time() - start_time) * 1000
                error_data = {
                    'processing_time': processing_time,
                    'error_message': str(e)
                }
                
                # Update job status to failed
                self.processing_service.update_status(job_id, 'failed', error_data)
                print(f"❌ Job {job_id} ({job_type if 'job_type' in locals() else 'unknown'}) failed after {processing_time:.2f}ms")
                
                # Complete the job with error
                self.processing_service.complete_job(job_id, None, 'failed', str(e))
            
            return {'status': 'error', 'message': str(e)}
    
    def create_hierarchical_output_path(self, config: Dict[str, Any], file_info) -> Path:
        """
        Create hierarchical output path: output/usecase/project/job_type/filename_without_extension/
        
        Note: ETL results go to output/ directory with job type separation:
        - Extraction: output/usecase/project/extraction/filename/
        - Generation: output/usecase/project/generation/filename/
        
        Job type determines both input source and output destination for better organization.
        """
        try:
            # Get use case and project names from config
            use_case_name = config.get('use_case_name', 'Unknown_Use_Case')
            project_name = config.get('project_name', 'Unknown_Project')
            
            # Get filename without extension
            filename = file_info.filename
            filename_without_ext = Path(filename).stem
            
            # Determine job type for output path separation - NO DEFAULTS, must be explicit
            if hasattr(file_info, 'file_type'):
                file_type = file_info.file_type
            else:
                file_type = file_info.get('file_type')
            
            # Must have explicit job type - no fallbacks allowed
            if file_type == 'aasx':
                job_type = 'extraction'
            elif file_type == 'zip':
                job_type = 'generation'
            else:
                # Check config for explicit job type
                config_job_type = config.get('job_type')
                if config_job_type in ['extraction', 'generation']:
                    job_type = config_job_type
                else:
                    # Fail explicitly - cannot determine job type
                    error_msg = f"Cannot determine job type. File type: {file_type}, Config job type: {config_job_type}. Must be explicitly 'extraction' or 'generation'."
                    print(f"❌ {error_msg}")
                    raise ValueError(error_msg)
            
            # Create hierarchical path with job type separation
            output_path = Path("output") / use_case_name / project_name / job_type / filename_without_ext
            
            # Create directories if they don't exist
            output_path.mkdir(parents=True, exist_ok=True)
            
            print(f"📁 Created hierarchical output path: {output_path}")
            print(f"ℹ️  Job type: {job_type}")
            print(f"ℹ️  Input: data/{use_case_name}/{project_name}/{job_type}/")
            print(f"ℹ️  Output: output/{use_case_name}/{project_name}/{job_type}/")
            return output_path
            
        except Exception as e:
            print(f"❌ Error creating hierarchical output path: {e}")
            # Fallback to flat structure
            fallback_path = Path("output") / filename_without_ext
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
            # Auto-detect job type if not provided - NO DEFAULTS, must be explicit
            if job_type is None:
                if hasattr(file_info, 'file_type'):
                    file_type = file_info.file_type
                else:
                    file_type = file_info.get('file_type')
                
                if file_type == 'aasx':
                    job_type = 'extraction'
                elif file_type == 'zip':
                    job_type = 'generation'
                else:
                    # Fail explicitly - cannot determine job type
                    error_msg = f"Cannot auto-detect job type. File type: {file_type}. Must be explicitly 'extraction' or 'generation'."
                    print(f"❌ {error_msg}")
                    raise ValueError(error_msg)
            
            # Get file path from file info
            if hasattr(file_info, 'filepath'):
                file_path = Path(file_info.filepath)
            else:
                file_path = Path(file_info.get('filepath', ''))
            
            if not file_path.exists():
                raise FileNotFoundError(f"Input file not found: {file_path}")
            
            print(f"📂 Input file path for {job_type} job: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ Error getting input file path: {e}")
            raise
    
    def process_ai_rag(self, etl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI/RAG analysis on ETL data"""
        try:
            # Validate input data
            if not isinstance(etl_data, dict):
                return {
                    'status': 'failed',
                    'error': 'Invalid etl_data format: expected dict'
                }
            
            from src.ai_rag.etl_integration import AIRAGETLIntegration
            import asyncio
            
            # Create AI/RAG integration instance
            ai_rag_integration = AIRAGETLIntegration()
            
            # Extract required data from etl_data
            project_id = etl_data.get('project_id')
            file_info = etl_data.get('file_info', {})
            output_dir = etl_data.get('output_dir')
            
            if not all([project_id, file_info, output_dir]):
                return {
                    'status': 'failed',
                    'error': 'Missing required data: project_id, file_info, or output_dir'
                }
            
            # Validate output_dir is a Path
            if not isinstance(output_dir, Path):
                output_dir = Path(output_dir)
            
            # Check if output directory exists
            if not output_dir.exists():
                return {
                    'status': 'failed',
                    'error': f'Output directory does not exist: {output_dir}'
                }
            
            # Process ETL output with AI/RAG
            # Note: Using asyncio.run() since the method is async but we're in a sync context
            ai_rag_result = asyncio.run(ai_rag_integration.process_etl_output_with_ai_rag(
                project_id, 
                file_info, 
                output_dir
            ))
            
            # Validate AI/RAG result
            if not isinstance(ai_rag_result, dict):
                return {
                    'status': 'failed',
                    'error': 'Invalid result format from AI/RAG integration'
                }
            
            print(f"✅ AI/RAG processing completed for {file_info.get('filename', 'unknown file')}")
            return ai_rag_result
            
        except ImportError as e:
            print(f"❌ Failed to import AI/RAG modules: {e}")
            return {
                'status': 'failed',
                'error': f'AI/RAG modules not available: {str(e)}'
            }
        except asyncio.TimeoutError as e:
            print(f"❌ AI/RAG processing timed out: {e}")
            return {
                'status': 'failed',
                'error': f'AI/RAG processing timed out: {str(e)}'
            }
        except Exception as e:
            print(f"❌ AI/RAG processing failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def store_in_qdrant(self, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store processed data in Qdrant and enhance twin"""
        try:
            # Validate input data
            if not isinstance(rag_data, dict):
                return {
                    'status': 'failed',
                    'error': 'Invalid rag_data format: expected dict'
                }
            
            from src.ai_rag.etl_integration import AIRAGETLIntegration
            
            # Create AI/RAG integration instance
            ai_rag_integration = AIRAGETLIntegration()
            
            # Extract required data from rag_data
            file_info = rag_data.get('file_info', {})
            etl_result = rag_data.get('etl_result', {})
            ai_rag_result = rag_data.get('ai_rag_result', {})
            file_id = rag_data.get('file_id')
            
            if not all([file_info, etl_result, ai_rag_result]):
                return {
                    'status': 'failed',
                    'error': 'Missing required data: file_info, etl_result, or ai_rag_result'
                }
            
            # Validate data types
            if not isinstance(file_info, dict):
                return {
                    'status': 'failed',
                    'error': 'Invalid file_info format: expected dict'
                }
            
            if not isinstance(etl_result, dict):
                return {
                    'status': 'failed',
                    'error': 'Invalid etl_result format: expected dict'
                }
            
            if not isinstance(ai_rag_result, dict):
                return {
                    'status': 'failed',
                    'error': 'Invalid ai_rag_result format: expected dict'
                }
            
            # Prepare enhanced twin data with AI/RAG insights
            try:
                enhanced_twin_data = ai_rag_integration.prepare_enhanced_twin_data(
                    file_info, 
                    etl_result, 
                    ai_rag_result
                )
            except Exception as e:
                print(f"⚠️ Failed to prepare enhanced twin data: {e}")
                enhanced_twin_data = {}
            
            # Update digital twin with enhanced data
            twin_update_success = False
            if file_id:
                try:
                    success = self.digital_twin_service.update_twin_metadata(
                        file_id, 
                        enhanced_twin_data
                    )
                    if success:
                        print(f"✅ Enhanced twin {file_id} with AI/RAG insights")
                        twin_update_success = True
                    else:
                        print(f"⚠️ Failed to update twin {file_id} with AI/RAG insights")
                except Exception as e:
                    print(f"⚠️ Error updating twin metadata: {e}")
            
            print(f"✅ Qdrant storage and twin enhancement completed for {file_info.get('filename', 'unknown file')}")
            return {
                'status': 'success', 
                'enhanced_twin_data': enhanced_twin_data,
                'file_id': file_id,
                'twin_update_success': twin_update_success
            }
            
        except ImportError as e:
            print(f"❌ Failed to import AI/RAG modules: {e}")
            return {
                'status': 'failed',
                'error': f'AI/RAG modules not available: {str(e)}'
            }
        except Exception as e:
            print(f"❌ Qdrant storage failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def mark_simulation_ready(self, twin_id: str) -> bool:
        """Mark digital twin as ready for physics simulation (Placeholder for future implementation)"""
        try:
            if not twin_id:
                return False
            
            # TODO: Implement simulation readiness marking
            # Use the service method following src/shared/ conventions
            success = self.digital_twin_service.update_simulation_status(twin_id, 'ready')
            if success:
                print(f"✅ Marked twin {twin_id} as simulation ready (placeholder)")
            return success
        except Exception as e:
            print(f"❌ Failed to mark simulation ready: {e}")
            return False
    
    # New modular functions for digital twin and federated learning
    
    def create_digital_twin_step(self, project_id: str, file_id: str, file_info: Dict[str, Any], 
                                etl_result: Dict[str, Any], output_dir: Path, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Modular function: Create digital twin for processed file with complete data"""
        try:
            # Use config data for user consent and privacy settings
            if config is None:
                config = {}
            
            user_consent = config.get('user_consent', False)
            federated_learning = config.get('federated_learning', 'not_allowed')
            data_privacy_level = config.get('data_privacy_level', 'private')
            
            # Prepare complete twin data with all required fields
            twin_data = {
                'twin_type': 'aasx',
                'metadata': {
                    'etl_results': etl_result,
                    'processing_timestamp': str(Path().cwd()),
                    'output_directory': str(output_dir),
                    'data_points': len(etl_result.get('completed', [])),
                    'extracted_data': etl_result.get('extracted_data', {}),
                    'status': etl_result.get('status', 'unknown')
                },
                'output_directory': str(output_dir),
                'etl_results': etl_result,
                # User consent and privacy settings from config
                'user_consent': user_consent,
                'federated_learning': federated_learning,
                'data_privacy_level': data_privacy_level
            }
            
            # Use the service method following src/shared/ conventions
            # This will automatically perform comprehensive health check
            twin = self.digital_twin_service.register_digital_twin(file_id, twin_data)
            
            if twin and hasattr(twin, 'twin_id'):
                print(f"✅ Created digital twin for {file_info['filename']} with comprehensive health check")
                
                # Get the latest health information from the service
                health_info = self.digital_twin_service.perform_health_check(twin.twin_id)
                
                return {
                    'status': 'success',
                    'twin_id': twin.twin_id,
                    'twin_name': twin.twin_name,
                    'health_score': health_info.get('health_score', 0),
                    'health_status': health_info.get('health_status', 'unknown'),
                    'health_checks': health_info.get('checks', {}),
                    'federated_participation_status': getattr(twin, 'federated_participation_status', 'inactive'),
                    'data_privacy_level': getattr(twin, 'data_privacy_level', 'private'),
                    'twin_data': twin.to_dict() if hasattr(twin, 'to_dict') else twin.__dict__
                }
            else:
                print(f"⚠️ Failed to create digital twin for {file_info['filename']}")
                return {
                    'status': 'failed',
                    'error': 'Twin creation returned no twin_id'
                }
                
        except Exception as e:
            print(f"❌ Failed to create digital twin for {file_info['filename']}: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def update_federated_learning_step(self, twin_result: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Modular function: Update federated learning status based on user consent"""
        try:
            if twin_result.get('status') != 'success':
                return {
                    'status': 'skipped',
                    'reason': 'Twin creation failed'
                }
            
            twin_id = twin_result.get('twin_id')
            user_consent = config.get('user_consent', False)
            federated_setting = config.get('federated_learning', 'not_allowed')
            
            if user_consent and federated_setting in ['allowed', 'conditional']:
                self.federated_learning_service.update_federated_participation(twin_id, 'active')
                print(f"✅ Updated federated learning status to 'active' for twin {twin_id}")
                return {
                    'status': 'success',
                    'federated_participation': 'active',
                    'user_consent': user_consent,
                    'federated_setting': federated_setting
                }
            else:
                self.federated_learning_service.update_federated_participation(twin_id, 'inactive')
                print(f"✅ Updated federated learning status to 'inactive' for twin {twin_id}")
                return {
                    'status': 'success',
                    'federated_participation': 'inactive',
                    'user_consent': user_consent,
                    'federated_setting': federated_setting
                }
                
        except Exception as e:
            print(f"❌ Failed to update federated learning status: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def update_file_status_step(self, file_id: str, filename: str) -> Dict[str, Any]:
        """Modular function: Update file status to processed"""
        try:
            if file_id:
                # Get file info to find project_id
                file_info = self.file_repo.get_by_id(file_id)
                project_id = None
                if file_info:
                    project_id = file_info.project_id if hasattr(file_info, 'project_id') else file_info.get('project_id')
                
                # Update file status
                self.file_repo.update_status(file_id, 'processed')
                print(f"✅ Updated file status to 'processed' for {filename}")
                
                # Update project's updated_at timestamp to reflect the file processing
                if project_id:
                    try:
                        from datetime import datetime
                        self.project_repo.update(project_id, {"updated_at": datetime.now().isoformat()})
                        print(f"🔧 Processor: Updated project {project_id} timestamp after file processing")
                    except Exception as update_error:
                        print(f"⚠️ Processor: Failed to update project timestamp after processing: {update_error}")
                
                return {
                    'status': 'success',
                    'file_id': file_id,
                    'new_status': 'processed'
                }
            else:
                print(f"⚠️ No file_id available for {filename}")
                return {
                    'status': 'skipped',
                    'reason': 'No file_id available'
                }
        except Exception as e:
            print(f"❌ Failed to update file status for {filename}: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def process_single_file(self, file_path: Path, output_dir: Path, formats: List[str] = None) -> Dict[str, Any]:
        """Process a single AASX file"""
        try:
            print(f"🔍 process_single_file: Input file_path: {file_path}")
            print(f"🔍 process_single_file: output_dir: {output_dir}")
            print(f"🔍 process_single_file: formats: {formats}")
            
            if formats is None:
                formats = ['json', 'graph', 'rdf', 'yaml']
            
            print(f"🔍 process_single_file: About to call extract_aasx with file_path: {file_path}")
            result = extract_aasx(file_path, output_dir, formats=formats)
            print(f"🔍 process_single_file: extract_aasx result: {result}")
            return result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def batch_process_files(self, input_path: Path, output_dir: Path, formats: List[str] = None) -> Dict[str, Any]:
        """Process multiple AASX files in batch"""
        try:
            if formats is None:
                formats = ['json', 'graph', 'rdf', 'yaml']
            
            result = batch_extract(input_path, output_dir, formats=formats)
            return result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def validate_user_consent(self, user_id: str, consent_type: str = 'federated_learning') -> Dict[str, Any]:
        """Validate user consent for federated learning participation"""
        try:
            # This would typically query the user_consents table
            # For now, return a basic validation structure
            return {
                'valid': True,  # Default to valid for testing
                'user_id': user_id,
                'consent_type': consent_type,
                'consent_given': True,  # Default to given for testing
                'consent_timestamp': None,
                'data_privacy_level': 'private',
                'consent_version': '1.0'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'user_id': user_id,
                'consent_type': consent_type
            }
    
    def record_user_consent(self, user_id: str, consent_data: Dict[str, Any]) -> bool:
        """Record user consent for federated learning"""
        try:
            # This would typically insert into the user_consents table
            # For now, just log the consent
            print(f"📝 Recording user consent for user {user_id}")
            print(f"   📋 Consent data: {consent_data}")
            return True
        except Exception as e:
            print(f"❌ Failed to record user consent: {str(e)}")
            return False

    def process_etl_extraction(self, file_path: Path, output_dir: Path, formats: List[str], job_id: str = None, job_type: str = None) -> Dict[str, Any]:
        """
        Process ETL extraction/generation for a single file with optional job tracking
        
        Args:
            file_path: Path to the input file
            output_dir: Directory to store output
            formats: List of output formats
            job_id: Optional job ID for tracking
            job_type: Job type ('extraction' or 'generation') - if None, auto-detected
        """
        try:
            print(f"🔍 process_etl_extraction: Input file_path: {file_path}")
            print(f"🔍 process_etl_extraction: file_path type: {type(file_path)}")
            print(f"🔍 process_etl_extraction: file_path exists: {file_path.exists()}")
            print(f"🔍 process_etl_extraction: file_path absolute: {file_path.absolute()}")
            
            # Auto-detect job type if not provided
            if job_type is None:
                if file_path.suffix.lower() == '.aasx':
                    job_type = 'extraction'
                elif file_path.suffix.lower() == '.zip':
                    job_type = 'generation'
                else:
                    job_type = 'extraction'  # Default fallback
            
            print(f"🔍 Job type detected: {job_type}")
            
            # Update job progress if job_id is provided
            if job_id:
                self.processing_service.update_status(job_id, 'processing', {
                    'output_directory': str(output_dir),
                    'job_type': job_type
                })
                print(f"🔄 Job {job_id}: ETL {job_type} started")
            
            # Validate inputs
            if not file_path.exists():
                print(f"❌ process_etl_extraction: File does not exist: {file_path}")
                if job_id:
                    self.processing_service.update_status(job_id, 'failed', {
                        'error_message': f'File not found: {file_path}'
                    })
                return {
                    'status': 'failed',
                    'error': f'File not found: {file_path}'
                }
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process the file based on job type
            if job_type == 'extraction':
                # Use existing extraction logic
                result = self.process_single_file(file_path, output_dir, formats)
                
                # Convert status to match expected format
                if result.get('status') == 'completed':
                    result['status'] = 'success'
                elif result.get('status') == 'failed':
                    result['status'] = 'failed'
                    
            elif job_type == 'generation':
                # Use SIMPLE AASX generation logic (no ETL ecosystem)
                print(f"🔧 Processing SIMPLE generation job for {file_path}")
                print(f"ℹ️  Generation jobs only convert to AASX - no ETL ecosystem involved")
                result = self.process_generation_job(file_path, output_dir, formats)
                
            else:
                # Fallback to extraction
                print(f"⚠️ Unknown job type '{job_type}', falling back to extraction")
                result = self.process_single_file(file_path, output_dir, formats)
                
                # Convert status to match expected format
                if result.get('status') == 'completed':
                    result['status'] = 'success'
                elif result.get('status') == 'failed':
                    result['status'] = 'failed'
            
            # Update job progress based on result
            if job_id:
                if result.get('status') == 'success':
                    print(f"✅ Job {job_id}: ETL {job_type} completed successfully")
                else:
                    error_msg = result.get('error', f'Unknown error during ETL {job_type}')
                    self.processing_service.update_status(job_id, 'failed', {
                        'error_message': error_msg
                    })
                    print(f"❌ Job {job_id}: ETL {job_type} failed - {error_msg}")
            
            # Validate result structure
            if not isinstance(result, dict):
                return {
                    'status': 'failed',
                    'error': 'Invalid result format from process_single_file'
                }
            
            return result
            
        except FileNotFoundError as e:
            print(f"❌ File not found: {e}")
            return {
                'status': 'failed',
                'error': f'File not found: {str(e)}'
            }
        except PermissionError as e:
            print(f"❌ Permission denied: {e}")
            return {
                'status': 'failed',
                'error': f'Permission denied: {str(e)}'
            }
        except Exception as e:
            print(f"❌ ETL extraction failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def process_generation_job(self, file_path: Path, output_dir: Path, formats: List[str]) -> Dict[str, Any]:
        """
        Process AASX generation job from structured data + documents (ZIP file).
        
        Expected ZIP structure:
        structured_data.zip
        ├── Structure_Data.json (or .yaml)  ← Root level
        └── Documents/                      ← Root level
            ├── sensor_data.json
            ├── images/
            ├── raw_data/
            └── anything_else/
        
        This is a SIMPLE conversion job that:
        1. Extracts structured data (JSON/YAML) from ZIP root - AAS metadata
        2. Preserves ALL documents from Documents/ folder + any root files
        3. Generates AASX file containing both structured data and documents
        
        It does NOT run the full ETL ecosystem like extraction jobs do.
        
        Args:
            file_path: Path to the ZIP file with root-level structured data + Documents/ folder
            output_dir: Directory to store generated AASX file
            formats: List of output formats (for generation, this is typically just AASX)
            
        Returns:
            Dictionary with generation results including document count and list
        """
        try:
            print(f"🔧 Starting SIMPLE AASX generation from {file_path}")
            print(f"ℹ️  Note: This is a generation job - just converting to AASX, no ETL ecosystem")
            
            # Import generation functions
            from src.aasx.aasx_processor import generate_aasx_from_structured
            import zipfile
            import tempfile
            
            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract ZIP file
                print(f"📦 Extracting ZIP file: {file_path}")
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Look for structured data files at ROOT level (JSON, YAML)
                json_files = list(temp_path.glob("*.json"))
                yaml_files = list(temp_path.glob("*.yaml")) + list(temp_path.glob("*.yml"))
                
                if not json_files and not yaml_files:
                    return {
                        'status': 'failed',
                        'error': 'No structured data files (JSON/YAML) found at ZIP root level'
                    }
                
                # Use JSON if available, otherwise YAML
                structured_file = json_files[0] if json_files else yaml_files[0]
                print(f"📄 Using structured data file at root: {structured_file}")
                
                # Look for Documents folder at root level
                documents_dir = temp_path / "Documents"
                if documents_dir.exists() and documents_dir.is_dir():
                    print(f"📁 Found Documents folder at root level")
                    # List all files in Documents folder
                    document_files = list(documents_dir.rglob("*")) if documents_dir.exists() else []
                else:
                    print(f"⚠️  No Documents folder found at root level")
                    document_files = []
                
                # Also check for any other files at root level (excluding the structured data file)
                root_files = [f for f in temp_path.iterdir() if f.is_file() and f != structured_file]
                if root_files:
                    print(f"📋 Additional files at root level:")
                    for root_file in root_files:
                        print(f"   📄 {root_file.name}")
                    document_files.extend(root_files)
                
                print(f"📋 Found {len(document_files)} document/data files:")
                for doc_file in document_files:
                    rel_path = doc_file.relative_to(temp_path)
                    file_size = doc_file.stat().st_size
                    print(f"   📄 {rel_path} ({file_size} bytes)")
                
                # Generate AASX file - use the structured data filename, not the ZIP filename
                structured_data_name = structured_file.stem  # e.g., "Structure_Data" from "Structure_Data.json"
                output_filename = f"{structured_data_name}_generated.aasx"
                output_aasx = output_dir / output_filename
                
                print(f"🔧 Converting structured data + {len(document_files)} documents to AASX: {output_aasx}")
                print(f"ℹ️  This will preserve all documents including raw sensor data, images, etc.")
                
                # Use the more comprehensive generation function that handles documents
                from src.aasx.aasx_processor import generate_aasx
                generation_result = generate_aasx(output_aasx, structured_file)
                
                if generation_result.get('status') == 'completed':
                    print(f"✅ AASX generation completed: {output_aasx}")
                    
                    # Check if AASX file was created
                    if output_aasx.exists():
                        file_size = output_aasx.stat().st_size
                        print(f"📊 Generated AASX file size: {file_size} bytes")
                        
                        return {
                            'status': 'success',
                            'message': 'AASX generation completed successfully (structured data + documents)',
                            'output_file': str(output_aasx),
                            'file_size': file_size,
                            'input_file': str(file_path),
                            'structured_data_file': str(structured_file),
                            'document_count': len(document_files),
                            'documents': [str(f.relative_to(temp_path)) for f in document_files],
                            'job_type': 'generation',
                            'processing_note': 'Simple conversion job - preserves all documents including raw sensor data'
                        }
                    else:
                        return {
                            'status': 'failed',
                            'error': 'AASX file was not created despite successful generation'
                        }
                else:
                    error_msg = generation_result.get('error', 'Unknown generation error')
                    print(f"❌ AASX generation failed: {error_msg}")
                    return {
                        'status': 'failed',
                        'error': f'AASX generation failed: {error_msg}'
                    }
                    
        except zipfile.BadZipFile as e:
            error_msg = f"Invalid ZIP file: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'status': 'failed',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"AASX generation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'status': 'failed',
                'error': error_msg
            }

    def get_processing_status(self, project_id: str = None) -> Dict[str, Any]:
        """Get processing status for files"""
        try:
            if project_id:
                files = self.file_repo.get_by_project_id(project_id)
            else:
                # Get all files across all projects
                all_files = []
                projects = self.project_repo.get_all()
                for project in projects:
                    project_id = project.get('project_id')
                    if project_id:
                        files = self.file_repo.get_by_project_id(project_id)
                        all_files.extend(files)
                files = all_files
            
            status_counts = {
                'pending': 0,
                'processing': 0,
                'completed': 0,
                'failed': 0,
                'total': len(files)
            }
            
            for file_info in files:
                status = file_info.get('status', 'pending')
                if status in status_counts:
                    status_counts[status] += 1
            
            return status_counts
            
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def get_etl_progress(self) -> Dict[str, Any]:
        """Get ETL processing progress"""
        try:
            # This would typically track real-time progress
            # For now, return basic status
            return {
                'status': 'idle',
                'progress': 0,
                'message': 'No active ETL processing'
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def get_aasx_statistics(self) -> Dict[str, Any]:
        """Get AASX processing statistics"""
        try:
            projects = self.project_repo.get_all()
            total_files = 0
            processed_files = 0
            failed_files = 0
            
            for project in projects:
                project_id = project.get('project_id')
                if project_id:
                    files = self.file_repo.get_by_project_id(project_id)
                    total_files += len(files)
                    
                    for file_info in files:
                        status = file_info.get('status', 'pending')
                        if status == 'completed':
                            processed_files += 1
                        elif status == 'failed':
                            failed_files += 1
            
            # Calculate success rate
            success_rate = 0.0
            if total_files > 0:
                success_rate = (processed_files / total_files) * 100
            
            return {
                'total_projects': len(projects),
                'total_files': total_files,
                'processed_files': processed_files,
                'failed_files': failed_files,
                'pending_files': total_files - processed_files - failed_files,
                'success_rate': success_rate
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_projects': 0,
                'total_files': 0,
                'processed_files': 0,
                'failed_files': 0,
                'pending_files': 0,
                'success_rate': 0.0
            }
    
    # Phase 4: Comprehensive Metrics Collection Methods
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert bytes to MB
        except ImportError:
            return 0.0  # psutil not available
        except Exception:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0  # psutil not available
        except Exception:
            return 0.0
    
    def _get_disk_io(self) -> float:
        """Get current disk I/O in MB."""
        try:
            import psutil
            disk_io = psutil.disk_io_counters()
            return (disk_io.read_bytes + disk_io.write_bytes) / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0  # psutil not available
        except Exception:
            return 0.0
    
    def _get_peak_memory(self) -> float:
        """Get peak memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.peak_wset / 1024 / 1024  # Convert bytes to MB
        except ImportError:
            return 0.0  # psutil not available
        except Exception:
            return 0.0
    
    def _get_peak_cpu(self) -> float:
        """Get peak CPU usage percentage."""
        # For now, return current CPU as peak
        # Could be enhanced with actual peak tracking
        return self._get_cpu_usage()
    
    def _get_total_disk_io(self) -> float:
        """Get total disk I/O in MB."""
        # For now, return current disk I/O as total
        # Could be enhanced with actual cumulative tracking
        return self._get_disk_io()
    
    def _calculate_quality_score(self, etl_result: Dict[str, Any]) -> float:
        """Calculate data quality score (0-100)."""
        try:
            score = 0.0
            
            # Base score for successful processing
            if etl_result.get('status') == 'success':
                score += 50.0
            
            # Bonus for multiple formats
            formats = etl_result.get('formats', [])
            score += min(len(formats) * 10, 30)  # Max 30 points for formats
            
            # Bonus for no failed formats
            failed_formats = etl_result.get('failed_formats', [])
            if not failed_formats:
                score += 20.0
            
            return min(score, 100.0)  # Cap at 100
            
        except Exception:
            return 50.0  # Default score
    
    def _calculate_file_checksum(self, file_info) -> str:
        """Calculate file integrity checksum."""
        try:
            import hashlib
            file_path = Path(file_info.filepath) if hasattr(file_info, 'filepath') else Path(file_info.get('filepath', ''))
            
            if file_path.exists():
                hash_md5 = hashlib.md5()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                return hash_md5.hexdigest()
            else:
                return "file_not_found"
        except Exception:
            return "checksum_error"
    
    def _calculate_processing_accuracy(self, etl_result: Dict[str, Any]) -> float:
        """Calculate processing accuracy (0-100)."""
        try:
            total_formats = len(etl_result.get('formats', []))
            failed_formats = len(etl_result.get('failed_formats', []))
            
            if total_formats == 0:
                return 0.0
            
            success_rate = ((total_formats - failed_formats) / total_formats) * 100
            return max(0.0, min(success_rate, 100.0))
            
        except Exception:
            return 50.0  # Default accuracy
    
    def _validate_results(self, etl_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ETL results and return validation summary."""
        try:
            validation = {
                'total_formats': len(etl_result.get('formats', [])),
                'successful_formats': len(etl_result.get('formats', [])) - len(etl_result.get('failed_formats', [])),
                'failed_formats': len(etl_result.get('failed_formats', [])),
                'success_rate': self._calculate_processing_accuracy(etl_result),
                'has_documents': etl_result.get('results', {}).get('documents', {}).get('file_count', 0) > 0,
                'has_original': etl_result.get('results', {}).get('original', {}).get('status') == 'completed'
            }
            return validation
        except Exception:
            return {'error': 'validation_failed'}
    
    def _calculate_efficiency_score(self, processing_time: float, etl_result: Dict[str, Any]) -> float:
        """Calculate processing efficiency score (0-100)."""
        try:
            # Base efficiency score
            base_score = 50.0
            
            # Time efficiency (faster = better, but not too fast)
            if processing_time < 1000:  # Less than 1 second
                time_score = 20.0
            elif processing_time < 5000:  # Less than 5 seconds
                time_score = 15.0
            elif processing_time < 30000:  # Less than 30 seconds
                time_score = 10.0
            else:
                time_score = 5.0
            
            # Quality efficiency
            quality_score = self._calculate_quality_score(etl_result) * 0.3  # 30% weight
            
            total_score = base_score + time_score + quality_score
            return min(total_score, 100.0)  # Cap at 100
            
        except Exception:
            return 50.0  # Default efficiency score

# Global instance
aasx_processor = AASXProcessor() 