"""
AI/RAG ETL Integration Module
Handles AI/RAG processing integration with ETL pipeline without coupling to specific routes.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AIRAGETLIntegration:
    """Handles AI/RAG integration with ETL pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def process_etl_output_with_ai_rag(
        self, 
        project_id: str, 
        file_info: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, Any]:
        """Process ETL output with AI/RAG processors"""
        try:
            from ..processors import ProcessorManager
            from ..embedding_models.text_embeddings import TextEmbeddingManager
            from ..vector_db.qdrant_client import QdrantClient
            from src.shared.database_manager import DatabaseProjectManager
            
            # Get project metadata for human-readable information
            db_manager = DatabaseProjectManager()
            project_metadata = db_manager.get_project_metadata(project_id)
            project_name = project_metadata.get('name', project_id) if project_metadata else project_id
            
            # Initialize AI/RAG components
            text_embedding_manager = TextEmbeddingManager()
            
            # Initialize Qdrant with config
            from ..config import VECTOR_DB_CONFIG
            vector_db_config = {
                'host': VECTOR_DB_CONFIG['host'],
                'port': VECTOR_DB_CONFIG['port'],
                'collection_name': VECTOR_DB_CONFIG['collection_name']
            }
            vector_db = QdrantClient(vector_db_config)
            
            # Connect to Qdrant (required for operations)
            try:
                vector_db.connect()
                self.logger.info(f"Connected to Qdrant at {vector_db_config['host']}:{vector_db_config['port']}")
            except Exception as e:
                self.logger.warning(f"Failed to connect to Qdrant: {e}. Continuing without vector storage.")
                vector_db = None
            
            processor_manager = ProcessorManager(
                text_embedding_manager=text_embedding_manager,
                vector_db=vector_db
            )
            
            # Process all exported files with smart selection
            processed_files = []
            total_files = 0
            successful_files = 0
            
            # Smart file selection to avoid duplicate processing
            selected_files = self._select_files_for_processing(output_dir)
            
            self.logger.info(f"Selected {len(selected_files)} files for AI/RAG processing out of {len(list(output_dir.rglob('*')))} total files")
            
            for file_path in selected_files:
                total_files += 1
                try:
                    # Check if processor can handle this file
                    if processor_manager.can_process_file(file_path):
                        # Process file with AI/RAG
                        file_processing_info = {
                            'file_id': f"ai_rag_{file_path.stem}_{total_files}",
                            'project_id': project_id,
                            'project_name': project_name,  # Add project name for human-readable metadata
                            'source_aasx': file_info['filename']
                        }
                        
                        result = processor_manager.process_file(
                            project_id, 
                            file_processing_info, 
                            file_path
                        )
                        
                        if result.get('status') == 'success':
                            successful_files += 1
                        
                        processed_files.append({
                            'file_path': str(file_path),
                            'file_name': file_path.name,
                            'processor_type': result.get('processor_type'),
                            'status': result.get('status'),
                            'content_preview': result.get('content_preview', '')[:200],
                            'vector_id': result.get('vector_id')
                        })
                        
                        self.logger.info(f"Processed {file_path.name} with {result.get('processor_type', 'unknown')} processor")
                    else:
                        self.logger.warning(f"No processor available for {file_path.name}")
                        
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path.name}: {e}")
                    processed_files.append({
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'status': 'error',
                        'error': str(e)
                    })
            
            # Generate AI/RAG summary
            ai_rag_summary = self._generate_ai_rag_summary(processed_files, file_info['filename'])
            
            return {
                'status': 'completed',
                'total_files_processed': total_files,
                'successful_files': successful_files,
                'processed_files': processed_files,
                'ai_rag_summary': ai_rag_summary,
                'vector_db_collection': vector_db.get_collection_name() if vector_db else None
            }
            
        except Exception as e:
            self.logger.error(f"AI/RAG processing failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'total_files_processed': 0,
                'successful_files': 0
            }
    
    def _generate_ai_rag_summary(self, processed_files: List[Dict], aasx_filename: str) -> Dict[str, Any]:
        """Generate a summary of AI/RAG processing results"""
        try:
            # Count by processor type
            processor_counts = {}
            content_types = {}
            total_content_length = 0
            raw_data_files = []  # 🎯 NEW: Track raw data files
            
            for file_info in processed_files:
                if file_info.get('status') == 'success':
                    processor_type = file_info.get('processor_type', 'unknown')
                    processor_counts[processor_type] = processor_counts.get(processor_type, 0) + 1
                    
                    # Analyze content types
                    file_name = file_info.get('file_name', '').lower()
                    content_type = 'unknown'
                    
                    if any(ext in file_name for ext in ['.pdf', '.docx', '.txt']):
                        content_types['documents'] = content_types.get('documents', 0) + 1
                        content_type = 'document'
                    elif any(ext in file_name for ext in ['.xlsx', '.csv', '.xls']):
                        content_types['spreadsheets'] = content_types.get('spreadsheets', 0) + 1
                        content_type = 'spreadsheet'
                    elif any(ext in file_name for ext in ['.dwg', '.dxf', '.step', '.svg']):
                        content_types['cad_files'] = content_types.get('cad_files', 0) + 1
                        content_type = 'cad_file'
                    elif any(ext in file_name for ext in ['.jpg', '.png', '.gif']):
                        content_types['images'] = content_types.get('images', 0) + 1
                        content_type = 'image'
                    elif any(ext in file_name for ext in ['.py', '.js', '.java', '.cpp']):
                        content_types['code_files'] = content_types.get('code_files', 0) + 1
                        content_type = 'code_file'
                    elif any(ext in file_name for ext in ['.json', '.yaml', '.xml']):
                        content_types['structured_data'] = content_types.get('structured_data', 0) + 1
                        content_type = 'structured_data'
                    
                    # Count content length
                    content_preview = file_info.get('content_preview', '')
                    total_content_length += len(content_preview)
                    
                    # 🎯 NEW: Add raw data file information for physics modeling
                    raw_data_files.append({
                        'file_path': file_info.get('file_path', ''),
                        'file_name': file_info.get('file_name', ''),
                        'content_type': content_type,
                        'processor_type': processor_type,
                        'file_size': self._get_file_size(file_info.get('file_path', '')),
                        'extracted_text_length': len(content_preview),
                        'vector_id': file_info.get('vector_id'),
                        'status': file_info.get('status')
                    })
            
            # Generate insights
            insights = []
            if content_types.get('cad_files', 0) > 0:
                insights.append(f"Contains {content_types['cad_files']} technical drawings/CAD files")
            if content_types.get('spreadsheets', 0) > 0:
                insights.append(f"Contains {content_types['spreadsheets']} spreadsheet files with data")
            if content_types.get('documents', 0) > 0:
                insights.append(f"Contains {content_types['documents']} document files")
            if content_types.get('code_files', 0) > 0:
                insights.append(f"Contains {content_types['code_files']} code/configuration files")
            
            return {
                'aasx_filename': aasx_filename,
                'total_files_processed': len(processed_files),
                'successful_files': len([f for f in processed_files if f.get('status') == 'success']),
                'processor_breakdown': processor_counts,
                'content_type_breakdown': content_types,
                'total_content_length': total_content_length,
                'insights': insights,
                'vector_embeddings_generated': len([f for f in processed_files if f.get('vector_id')]),
                'raw_data_files': raw_data_files  # 🎯 NEW: Raw data paths for physics modeling
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            return {
                'error': f"Failed to generate summary: {str(e)}",
                'aasx_filename': aasx_filename
            }
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        try:
            if file_path and Path(file_path).exists():
                return Path(file_path).stat().st_size
            return 0
        except Exception:
            return 0
    
    def prepare_enhanced_twin_data(
        self, 
        file_info: Dict[str, Any], 
        etl_result: Dict[str, Any], 
        ai_rag_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Prepare enhanced twin data with AI/RAG insights"""
        try:
            # Extract AAS information from ETL result
            aas_id = None
            twin_name = f"Twin for {file_info['filename']}"
            
            if etl_result.get('aas_data'):
                aas_data = etl_result['aas_data']
                if isinstance(aas_data, dict):
                    aas_id = aas_data.get('id') or aas_data.get('aas_id')
                    if aas_data.get('idShort'):
                        twin_name = f"{aas_data['idShort']} Twin"
            
            # Prepare enhanced metadata
            metadata = {
                'original_filename': file_info['filename'],
                'etl_processing': {
                    'status': etl_result.get('status'),
                    'formats_generated': etl_result.get('formats', []),
                    'processing_time': etl_result.get('processing_time', 0)
                },
                'ai_rag_processing': ai_rag_result if ai_rag_result else None,
                'file_metadata': {
                    'file_size': file_info.get('file_size'),
                    'upload_date': file_info.get('upload_date'),
                    'description': file_info.get('description')
                }
            }
            
            # Add AI/RAG insights to metadata
            if ai_rag_result and ai_rag_result.get('status') == 'completed':
                ai_summary = ai_rag_result.get('ai_rag_summary', {})
                metadata['ai_insights'] = {
                    'content_types': ai_summary.get('content_type_breakdown', {}),
                    'key_insights': ai_summary.get('insights', []),
                    'total_content_length': ai_summary.get('total_content_length', 0),
                    'vector_embeddings': ai_summary.get('vector_embeddings_generated', 0),
                    'raw_data_files': ai_summary.get('raw_data_files', [])  # 🎯 NEW: Raw data paths for physics modeling
                }
            
            # Calculate data points (files processed)
            data_points = 0
            if ai_rag_result and ai_rag_result.get('status') == 'completed':
                data_points = ai_rag_result.get('successful_files', 0)
            
            return {
                'aas_id': aas_id,
                'twin_name': twin_name,
                'twin_type': 'aasx_enhanced' if ai_rag_result else 'aasx',
                'metadata': metadata,
                'data_points': data_points
            }
            
        except Exception as e:
            self.logger.error(f"Failed to prepare enhanced twin data: {e}")
            # Fallback to basic twin data
            return {
                'aas_id': None,
                'twin_name': f"Twin for {file_info['filename']}",
                'twin_type': 'aasx',
                'metadata': {
                    'original_filename': file_info['filename'],
                    'error': f"Failed to prepare enhanced data: {str(e)}"
                },
                'data_points': 0
            }

    def _select_files_for_processing(self, output_dir: Path) -> List[Path]:
        """
        Smart file selection to process only the essential data files.
        
        Strategy:
        1. Process {filename}.json (main structured data)
        2. Process {filename}_graph.json (graph representation)
        3. Process all documents in documents/ directory
        4. Skip all other formats to avoid duplicate processing
        
        Args:
            output_dir: ETL output directory
            
        Returns:
            List of files to process
        """
        selected_files = []
        
        # Scan all files in output directory
        all_files = list(output_dir.rglob('*'))
        
        # Get the base filename from the output directory name
        # ETL creates: output/projects/{project_id}/{filename}/
        # So the directory name is the AASX filename without extension
        base_filename = output_dir.name
        
        for file_path in all_files:
            if not file_path.is_file():
                continue
                
            file_name = file_path.name.lower()
            
            # Skip AASX package metadata files
            if self._is_aasx_metadata_file(file_path):
                continue
            
            # Strategy 1: Main structured data (JSON with base filename)
            if file_name == f"{base_filename.lower()}.json":
                selected_files.append(file_path)
                self.logger.info(f"Selected structured data: {file_path.name}")
            
            # Strategy 2: Graph data (graph representation with base filename)
            elif file_name == f"{base_filename.lower()}_graph.json":
                selected_files.append(file_path)
                self.logger.info(f"Selected graph data: {file_path.name}")
            
            # Strategy 3: Documents - Process all extracted documents
            elif file_path.parent.name == 'documents':
                selected_files.append(file_path)
                self.logger.info(f"Selected document: {file_path.name}")
        
        self.logger.info(f"Smart file selection: {len(selected_files)} files selected from {len(all_files)} total files")
        return selected_files
    
    def _is_aasx_metadata_file(self, file_path: Path) -> bool:
        """Check if file is AASX package metadata that should be skipped."""
        file_name = file_path.name.lower()
        
        # Skip AASX package metadata files
        skip_extensions = {'.rels', '.xml.rels', '.rels.xml'}
        if file_path.suffix.lower() in skip_extensions:
            return True
        
        # Skip content types and other package metadata
        skip_filenames = {
            '[content_types].xml',
            'content_types.xml',
            'aasx-origin',
            '.rels',
        }
        
        if file_name in skip_filenames:
            return True
        
        # Skip relationship files
        if file_name.endswith('.rels') or '.rels' in file_name:
            return True
        
        return False


# Global instance for easy access
ai_rag_etl_integration = AIRAGETLIntegration() 