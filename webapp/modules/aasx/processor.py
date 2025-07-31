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
    
    def run_etl_pipeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run ETL pipeline for AASX files"""
        try:
            # Get project ID
            project_id = config.get('project_id')
            if not project_id and config.get('project_name'):
                # Find project by name
                projects = self.project_repo.get_all()
                for project in projects:
                    if project.get('name') == config['project_name']:
                        project_id = project.get('project_id')
                        break
                if not project_id:
                    raise Exception(f"Project '{config['project_name']}' not found")
            
            if not project_id:
                raise Exception("Either project_id or project_name must be provided")
            
            if not self.project_repo.get_by_id(project_id):
                raise Exception("Project not found")
            
            # Get files to process
            file_infos = []
            if config.get('files'):
                # Process specific files
                for filename in config['files']:
                    file_info = self.file_repo.find_by_name_and_project(filename, project_id)
                    if file_info:
                        file_infos.append(file_info)
                    else:
                        print(f"⚠️ File {filename} not found in project {project_id}")
            else:
                # Process all files in project
                file_infos = self.file_repo.get_by_project_id(project_id)
            
            if not file_infos:
                raise Exception("No files to process")
            
            # Setup output directory
            output_dir = Path(config.get('output_dir', f"output/projects/{project_id}"))
            output_dir.mkdir(parents=True, exist_ok=True)
            
            results = {}
            formats = config.get('formats', ['json', 'graph', 'rdf', 'yaml'])
            
            for file_info in file_infos:
                file_path = Path(file_info["filepath"])
                file_output_dir = output_dir / Path(file_info["filename"]).stem
                file_output_dir.mkdir(parents=True, exist_ok=True)
                
                try:
                    # Step 1: ETL Processing
                    result = extract_aasx(file_path, file_output_dir, formats=formats)
                    
                    # Step 2: Register Digital Twin (with ETL results only)
                    file_id = file_info.get('file_id')
                    if file_id:
                        twin_data = {
                            'twin_name': f"Digital Twin - {file_info['filename']}",
                            'twin_type': 'aasx',
                            'metadata': {
                                'etl_results': result,
                                'processing_timestamp': str(Path().cwd()),
                                'output_directory': str(file_output_dir)
                            },
                            'data_points': len(result.get('completed', []))
                        }
                        
                        twin_result = self.twin_repo.create(project_id, file_id, twin_data)
                        result['twin_registration'] = twin_result
                    
                    results[file_info['filename']] = result
                    
                except Exception as e:
                    results[file_info['filename']] = {
                        'status': 'failed',
                        'error': str(e)
                    }
            
            return {
                'status': 'completed',
                'project_id': project_id,
                'files_processed': len(file_infos),
                'results': results
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def process_single_file(self, file_path: Path, output_dir: Path, formats: List[str] = None) -> Dict[str, Any]:
        """Process a single AASX file"""
        try:
            if formats is None:
                formats = ['json', 'graph', 'rdf', 'yaml']
            
            result = extract_aasx(file_path, output_dir, formats=formats)
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