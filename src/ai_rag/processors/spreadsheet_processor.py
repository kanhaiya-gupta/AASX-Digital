"""
Spreadsheet processor for Excel, CSV, and other spreadsheet files.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from .base_processor import BaseDataProcessor


class SpreadsheetProcessor(BaseDataProcessor):
    """Processor for spreadsheet files (Excel, CSV, etc.) with semantic analysis."""
    
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the given file."""
        return file_path.suffix.lower() in ['.xlsx', '.xls', '.csv', '.tsv', '.ods', '.xlsm', '.xlsb']
    
    def process(self, project_id: str, file_info: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Process spreadsheet file."""
        try:
            self.logger.info(f"Processing spreadsheet file: {file_path}")
            
            # Extract and analyze spreadsheet content
            spreadsheet_data = self._extract_spreadsheet_content(file_path)
            
            if not spreadsheet_data:
                return self._create_skipped_result(file_info, file_path, "No content extracted from spreadsheet")
            
            # Generate semantic analysis
            semantic_content = self._generate_semantic_analysis(spreadsheet_data, file_path)
            
            if not semantic_content:
                return self._create_skipped_result(file_info, file_path, "No meaningful semantic content generated")
            
            self.logger.info(f"Generated semantic content: {semantic_content[:100]}...")
            
            # Generate embedding
            embedding = self._generate_embedding(semantic_content, file_path)
            if not embedding:
                return self._create_error_result(file_info, file_path, "Failed to generate embedding for spreadsheet")
            
            # Get spreadsheet metadata
            spreadsheet_metadata = self._get_spreadsheet_metadata(file_path, spreadsheet_data)
            
            # Prepare metadata
            metadata = {
                'project_id': project_id,
                'file_id': file_info.get('file_id'),
                'source_file': file_path.name,
                'content_type': 'spreadsheet',
                'content_preview': semantic_content[:200] + "..." if len(semantic_content) > 200 else semantic_content,
                'file_path': str(file_path),
                'embedding_model': self.text_embedding_manager.get_model().get_model_info() if self.text_embedding_manager else None,
                'spreadsheet_type': file_path.suffix.lower(),
                'text_length': len(semantic_content),
                'spreadsheet_metadata': spreadsheet_metadata
            }
            
            # Upload to vector database
            success = self._upload_to_vector_db(embedding, metadata, file_path)
            if not success:
                return self._create_error_result(file_info, file_path, "Failed to upload spreadsheet to vector database")
            
            # Save embedding locally
            vector_data = {
                'id': file_info.get('file_id'),  # Use file_id directly for deterministic mapping
                'vector': embedding,
                'payload': metadata
            }
            self._save_embedding_locally(project_id, file_path, vector_data)
            
            return self._create_success_result(file_info, file_path, vector_data['id'])
            
        except Exception as e:
            self.logger.error(f"Exception processing spreadsheet {file_path}: {e}")
            return self._create_error_result(file_info, file_path, str(e))
    
    def _extract_spreadsheet_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from spreadsheet based on its type."""
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension in ['.xlsx', '.xls', '.xlsm', '.xlsb']:
                return self._extract_excel_content(file_path)
            elif file_extension == '.csv':
                return self._extract_csv_content(file_path)
            elif file_extension == '.tsv':
                return self._extract_tsv_content(file_path)
            elif file_extension == '.ods':
                return self._extract_ods_content(file_path)
            else:
                self.logger.error(f"Unsupported spreadsheet type: {file_extension}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to extract content from {file_path}: {e}")
            return None
    
    def _extract_excel_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from Excel files."""
        try:
            import pandas as pd
            
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            sheets_data = {}
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    sheets_data[sheet_name] = {
                        'data': df.to_dict('records'),
                        'columns': df.columns.tolist(),
                        'shape': df.shape,
                        'dtypes': df.dtypes.to_dict()
                    }
                except Exception as e:
                    self.logger.warning(f"Failed to read sheet {sheet_name}: {e}")
                    continue
            
            return {
                'type': 'excel',
                'sheets': sheets_data,
                'sheet_names': excel_file.sheet_names,
                'total_sheets': len(excel_file.sheet_names)
            }
            
        except ImportError:
            self.logger.error("pandas library not available for Excel extraction")
            return None
        except Exception as e:
            self.logger.error(f"Excel extraction failed for {file_path}: {e}")
            return None
    
    def _extract_csv_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from CSV files."""
        try:
            import pandas as pd
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                self.logger.error(f"Failed to read CSV with any encoding: {file_path}")
                return None
            
            return {
                'type': 'csv',
                'data': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'shape': df.shape,
                'dtypes': df.dtypes.to_dict()
            }
            
        except ImportError:
            self.logger.error("pandas library not available for CSV extraction")
            return None
        except Exception as e:
            self.logger.error(f"CSV extraction failed for {file_path}: {e}")
            return None
    
    def _extract_tsv_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from TSV files."""
        try:
            import pandas as pd
            
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
            
            return {
                'type': 'tsv',
                'data': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'shape': df.shape,
                'dtypes': df.dtypes.to_dict()
            }
            
        except ImportError:
            self.logger.error("pandas library not available for TSV extraction")
            return None
        except Exception as e:
            self.logger.error(f"TSV extraction failed for {file_path}: {e}")
            return None
    
    def _extract_ods_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract content from ODS files."""
        try:
            import pandas as pd
            
            # Read all sheets
            ods_file = pd.ExcelFile(file_path, engine='odf')
            sheets_data = {}
            
            for sheet_name in ods_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='odf')
                    sheets_data[sheet_name] = {
                        'data': df.to_dict('records'),
                        'columns': df.columns.tolist(),
                        'shape': df.shape,
                        'dtypes': df.dtypes.to_dict()
                    }
                except Exception as e:
                    self.logger.warning(f"Failed to read ODS sheet {sheet_name}: {e}")
                    continue
            
            return {
                'type': 'ods',
                'sheets': sheets_data,
                'sheet_names': ods_file.sheet_names,
                'total_sheets': len(ods_file.sheet_names)
            }
            
        except ImportError:
            self.logger.error("pandas library not available for ODS extraction")
            return None
        except Exception as e:
            self.logger.error(f"ODS extraction failed for {file_path}: {e}")
            return None
    
    def _generate_semantic_analysis(self, spreadsheet_data: Dict[str, Any], file_path: Path) -> Optional[str]:
        """Generate semantic analysis of spreadsheet content."""
        try:
            analysis_parts = []
            
            if spreadsheet_data['type'] in ['xlsx', 'xls', 'xlsm', 'xlsb', 'ods']:
                # Multi-sheet analysis
                analysis_parts.append(f"Spreadsheet contains {spreadsheet_data['total_sheets']} sheets: {', '.join(spreadsheet_data['sheet_names'])}")
                
                for sheet_name, sheet_data in spreadsheet_data['sheets'].items():
                    sheet_analysis = self._analyze_sheet(sheet_name, sheet_data)
                    if sheet_analysis:
                        analysis_parts.append(sheet_analysis)
                        
            else:
                # Single sheet analysis
                sheet_analysis = self._analyze_sheet("Main", spreadsheet_data)
                if sheet_analysis:
                    analysis_parts.append(sheet_analysis)
            
            return "\n".join(analysis_parts) if analysis_parts else None
            
        except Exception as e:
            self.logger.error(f"Semantic analysis failed for {file_path}: {e}")
            return None
    
    def _analyze_sheet(self, sheet_name: str, sheet_data: Dict[str, Any]) -> Optional[str]:
        """Analyze a single sheet for semantic content."""
        try:
            import pandas as pd
            analysis_parts = []
            
            # Basic sheet info
            rows, cols = sheet_data['shape']
            analysis_parts.append(f"Sheet '{sheet_name}': {rows} rows, {cols} columns")
            
            # Column analysis
            columns = sheet_data['columns']
            analysis_parts.append(f"Columns: {', '.join(columns)}")
            
            # Data analysis
            data = sheet_data['data']
            if data:
                # Sample data analysis
                sample_rows = min(5, len(data))
                analysis_parts.append(f"Sample data from first {sample_rows} rows:")
                
                for i, row in enumerate(data[:sample_rows]):
                    row_text = []
                    for col, value in row.items():
                        if pd.notna(value) and str(value).strip():
                            row_text.append(f"{col}: {value}")
                    if row_text:
                        analysis_parts.append(f"  Row {i+1}: {'; '.join(row_text)}")
                
                # Statistical analysis
                numeric_columns = []
                text_columns = []
                date_columns = []
                
                for col, dtype in sheet_data['dtypes'].items():
                    if 'int' in str(dtype) or 'float' in str(dtype):
                        numeric_columns.append(col)
                    elif 'datetime' in str(dtype):
                        date_columns.append(col)
                    else:
                        text_columns.append(col)
                
                if numeric_columns:
                    analysis_parts.append(f"Numeric columns: {', '.join(numeric_columns)}")
                if date_columns:
                    analysis_parts.append(f"Date columns: {', '.join(date_columns)}")
                if text_columns:
                    analysis_parts.append(f"Text columns: {', '.join(text_columns)}")
                
                # Content patterns
                content_patterns = self._detect_content_patterns(data, columns)
                if content_patterns:
                    analysis_parts.append(f"Content patterns: {content_patterns}")
            
            return "\n".join(analysis_parts)
            
        except Exception as e:
            self.logger.error(f"Sheet analysis failed for {sheet_name}: {e}")
            return None
    
    def _detect_content_patterns(self, data: List[Dict], columns: List[str]) -> Optional[str]:
        """Detect patterns in spreadsheet content."""
        try:
            patterns = []
            
            if not data:
                return None
            
            # Check for technical specifications
            tech_keywords = ['specification', 'parameter', 'dimension', 'tolerance', 'material', 'weight', 'power', 'voltage', 'current', 'frequency', 'temperature', 'pressure', 'flow', 'speed', 'rpm', 'torque', 'efficiency']
            
            tech_columns = []
            for col in columns:
                if any(keyword in col.lower() for keyword in tech_keywords):
                    tech_columns.append(col)
            
            if tech_columns:
                patterns.append(f"Technical specifications detected in columns: {', '.join(tech_columns)}")
            
            # Check for asset information
            asset_keywords = ['asset', 'equipment', 'device', 'component', 'part', 'model', 'serial', 'manufacturer', 'vendor', 'location', 'status', 'condition']
            
            asset_columns = []
            for col in columns:
                if any(keyword in col.lower() for keyword in asset_keywords):
                    asset_columns.append(col)
            
            if asset_columns:
                patterns.append(f"Asset information detected in columns: {', '.join(asset_columns)}")
            
            # Check for measurement data
            measurement_keywords = ['measurement', 'reading', 'value', 'unit', 'timestamp', 'date', 'time', 'sensor', 'monitor']
            
            measurement_columns = []
            for col in columns:
                if any(keyword in col.lower() for keyword in measurement_keywords):
                    measurement_columns.append(col)
            
            if measurement_columns:
                patterns.append(f"Measurement data detected in columns: {', '.join(measurement_columns)}")
            
            return "; ".join(patterns) if patterns else None
            
        except Exception as e:
            self.logger.error(f"Pattern detection failed: {e}")
            return None
    
    def _get_spreadsheet_metadata(self, file_path: Path, spreadsheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata about the spreadsheet."""
        try:
            metadata = {
                'file_size': file_path.stat().st_size,
                'spreadsheet_type': spreadsheet_data['type'],
                'total_rows': 0,
                'total_columns': 0,
                'total_sheets': 1
            }
            
            if spreadsheet_data['type'] in ['xlsx', 'xls', 'xlsm', 'xlsb', 'ods']:
                metadata['total_sheets'] = spreadsheet_data['total_sheets']
                metadata['sheet_names'] = spreadsheet_data['sheet_names']
                
                # Calculate totals across all sheets
                for sheet_data in spreadsheet_data['sheets'].values():
                    rows, cols = sheet_data['shape']
                    metadata['total_rows'] += rows
                    metadata['total_columns'] = max(metadata['total_columns'], cols)
            else:
                rows, cols = spreadsheet_data['shape']
                metadata['total_rows'] = rows
                metadata['total_columns'] = cols
                metadata['columns'] = spreadsheet_data['columns']
            
            return metadata
            
        except Exception as e:
            self.logger.warning(f"Failed to get spreadsheet metadata for {file_path}: {e}")
            return {
                'spreadsheet_type': spreadsheet_data.get('type', 'unknown'),
                'error': str(e)
            } 