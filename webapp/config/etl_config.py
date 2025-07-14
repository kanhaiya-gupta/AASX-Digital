"""
ETL Configuration Management
Handles ETL pipeline configuration loading and management within the webapp.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ETLConfig:
    """ETL Configuration container"""
    config_path: str
    config_data: Dict[str, Any]
    
    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> 'ETLConfig':
        """Load ETL configuration from YAML file"""
        if config_path is None:
            # Default to webapp/config/config_etl.yaml
            config_path = os.path.join(os.getcwd(), "webapp", "config", "config_etl.yaml")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"ETL configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return cls(config_path=config_path, config_data=config_data)
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration section"""
        return self.config_data.get('output', {})
    
    def get_transformation_config(self) -> Dict[str, Any]:
        """Get transformation configuration section"""
        return self.config_data.get('transformation', {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration section"""
        return self.config_data.get('database', {})
    
    def get_vector_database_config(self) -> Dict[str, Any]:
        """Get vector database configuration section"""
        return self.config_data.get('vector_database', {})
    
    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get pipeline configuration section"""
        return self.config_data.get('pipeline', {})
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG configuration section"""
        return self.config_data.get('rag', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration section"""
        return self.config_data.get('logging', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration section"""
        return self.config_data.get('performance', {})
    
    def get_error_handling_config(self) -> Dict[str, Any]:
        """Get error handling configuration section"""
        return self.config_data.get('error_handling', {})
    
    def is_systematic_structure_enabled(self) -> bool:
        """Check if systematic folder structure is enabled"""
        output_config = self.get_output_config()
        return output_config.get('systematic_structure', True)
    
    def get_folder_structure_type(self) -> str:
        """Get the folder structure type"""
        output_config = self.get_output_config()
        return output_config.get('folder_structure', 'timestamped_by_file')
    
    def get_base_output_directory(self) -> str:
        """Get the base output directory"""
        output_config = self.get_output_config()
        return output_config.get('base_directory', 'output/etl_results')
    
    def save_config(self, config_path: Optional[str] = None) -> None:
        """Save configuration to file"""
        if config_path is None:
            config_path = self.config_path
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in self.config_data:
                self.config_data[key].update(value)
            else:
                self.config_data[key] = value
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required sections
        required_sections = ['output', 'transformation', 'pipeline']
        for section in required_sections:
            if section not in self.config_data:
                validation_results['errors'].append(f"Missing required section: {section}")
                validation_results['valid'] = False
        
        # Validate output configuration
        output_config = self.get_output_config()
        if output_config.get('systematic_structure', True):
            folder_structure = output_config.get('folder_structure', 'timestamped_by_file')
            valid_structures = ['timestamped_by_file', 'by_type', 'flat']
            if folder_structure not in valid_structures:
                validation_results['errors'].append(f"Invalid folder structure: {folder_structure}")
                validation_results['valid'] = False
        
        # Validate transformation configuration
        transform_config = self.get_transformation_config()
        output_formats = transform_config.get('output_formats', [])
        valid_formats = ['json', 'yaml', 'csv', 'graph', 'rag', 'vector_db', 'sqlite']
        for format_type in output_formats:
            if format_type not in valid_formats:
                validation_results['warnings'].append(f"Unknown output format: {format_type}")
        
        # Validate quality threshold
        quality_threshold = transform_config.get('quality_threshold', 0.8)
        if not 0.0 <= quality_threshold <= 1.0:
            validation_results['errors'].append(f"Quality threshold must be between 0.0 and 1.0: {quality_threshold}")
            validation_results['valid'] = False
        
        return validation_results

def create_default_config() -> ETLConfig:
    """Create a default ETL configuration"""
    default_config = {
        'pipeline': {
            'enable_validation': True,
            'enable_logging': True,
            'enable_backup': True,
            'parallel_processing': False,
            'max_workers': 4
        },
        'input': {
            'source_directory': 'data/aasx-examples',
            'file_pattern': '*.aasx',
            'specific_files': [],
            'recursive': False
        },
        'output': {
            'base_directory': 'output/etl_results',
            'timestamped_output': True,
            'clean_output': False,
            'separate_file_outputs': True,
            'include_filename_in_output': True,
            'systematic_structure': True,
            'folder_structure': 'timestamped_by_file'
        },
        'transformation': {
            'enable_quality_checks': True,
            'enable_enrichment': True,
            'output_formats': ['json', 'yaml', 'csv', 'graph', 'rag', 'vector_db', 'sqlite'],
            'include_metadata': True,
            'quality_threshold': 0.8,
            'normalize_ids': True,
            'add_timestamps': True
        },
        'database': {
            'sqlite_path': 'aasx_data.db',
            'create_indexes': True,
            'backup_existing': True
        },
        'vector_database': {
            'enabled': True,
            'type': 'chromadb',
            'path': 'output/vector_db',
            'embedding_model': 'all-MiniLM-L6-v2',
            'chunk_size': 512,
            'overlap_size': 50,
            'include_metadata': True
        },
        'rag': {
            'enabled': True,
            'output_path': 'output/rag_dataset.json',
            'entity_types': ['asset', 'submodel', 'document'],
            'min_quality_score': 0.7
        },
        'logging': {
            'level': 'INFO',
            'file_path': 'logs/etl_pipeline.log',
            'console_output': True,
            'include_timestamps': True
        },
        'performance': {
            'memory_limit': 0,
            'batch_processing': False,
            'batch_size': 10,
            'file_timeout': 300
        },
        'error_handling': {
            'continue_on_error': True,
            'max_consecutive_errors': 5,
            'retry_failed': False,
            'max_retries': 3
        }
    }
    
    return ETLConfig(config_path='', config_data=default_config)

def get_etl_config() -> ETLConfig:
    """Get ETL configuration, creating default if not exists"""
    try:
        return ETLConfig.load_from_file()
    except FileNotFoundError:
        # Create default configuration
        default_config = create_default_config()
        config_path = os.path.join(os.getcwd(), "webapp", "config", "config_etl.yaml")
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Save default configuration
        default_config.config_path = config_path
        default_config.save_config()
        
        print(f"Created default ETL configuration at: {config_path}")
        return default_config 