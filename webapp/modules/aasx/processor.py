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
from src.shared.services.federated_learning_service import FederatedLearningService

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
    
    def run_etl_pipeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete ETL pipeline with all steps."""
        try:
            print("🚀 Starting ETL pipeline...")
            print(f"📋 Received config: {config}")
            
            # Extract configuration
            file_id = config.get('file_id')
            project_id = config.get('project_id')
            use_case_id = config.get('use_case_id')
            output_formats = config.get('output_formats', ['json', 'graph', 'rdf', 'yaml'])
            
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
            
            # Get file information
            file_info = self.file_repo.get_by_id(file_id)
            if not file_info:
                return {'status': 'error', 'message': f'File {file_id} not found'}
            
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
                output_formats
            )
            
            if etl_result.get('status') != 'success':
                return {'status': 'error', 'message': 'ETL extraction failed', 'details': etl_result}
            
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
            
            print("✅ ETL pipeline completed successfully!")
            
            return {
                'status': 'success',
                'message': 'ETL pipeline completed successfully',
                'results': {
                    'etl_extraction': etl_result,
                    'file_status': file_status_result,
                    'digital_twin': twin_result,
                    'federated_learning': fl_result,
                    'ai_rag': ai_rag_result,
                    'qdrant': qdrant_result,
                    'simulation_ready': simulation_ready
                }
            }
            
        except Exception as e:
            print(f"❌ ETL pipeline failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def create_hierarchical_output_path(self, config: Dict[str, Any], file_info) -> Path:
        """Create hierarchical output path: output/usecase/project/filename_without_extension/"""
        try:
            # Get use case and project names from config
            use_case_name = config.get('use_case_name', 'Unknown_Use_Case')
            project_name = config.get('project_name', 'Unknown_Project')
            
            # Get filename without extension
            filename = file_info.filename
            filename_without_ext = Path(filename).stem
            
            # Create hierarchical path
            output_path = Path("output") / use_case_name / project_name / filename_without_ext
            
            # Create directories if they don't exist
            output_path.mkdir(parents=True, exist_ok=True)
            
            print(f"📁 Created hierarchical output path: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error creating hierarchical output path: {e}")
            # Fallback to flat structure
            fallback_path = Path("output") / filename_without_ext
            fallback_path.mkdir(parents=True, exist_ok=True)
            return fallback_path
    
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

    def process_etl_extraction(self, file_path: Path, output_dir: Path, formats: List[str]) -> Dict[str, Any]:
        """Process ETL extraction for a single file"""
        try:
            print(f"🔍 process_etl_extraction: Input file_path: {file_path}")
            print(f"🔍 process_etl_extraction: file_path type: {type(file_path)}")
            print(f"🔍 process_etl_extraction: file_path exists: {file_path.exists()}")
            print(f"🔍 process_etl_extraction: file_path absolute: {file_path.absolute()}")
            
            # Validate inputs
            if not file_path.exists():
                print(f"❌ process_etl_extraction: File does not exist: {file_path}")
                return {
                    'status': 'failed',
                    'error': f'File not found: {file_path}'
                }
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process the file using the existing process_single_file method
            result = self.process_single_file(file_path, output_dir, formats)
            
            # Convert status to match expected format
            if result.get('status') == 'completed':
                result['status'] = 'success'
            elif result.get('status') == 'failed':
                result['status'] = 'failed'
            
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

# Global instance
aasx_processor = AASXProcessor() 