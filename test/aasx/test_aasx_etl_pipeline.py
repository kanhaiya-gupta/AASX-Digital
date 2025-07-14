"""
Tests for AASX ETL Pipeline Module

Tests the complete ETL (Extract, Transform, Load) pipeline functionality
including batch processing, validation, and reporting.
"""

import unittest
import tempfile
import shutil
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from aasx.aasx_etl_pipeline import AASXETLPipeline, ETLPipelineConfig, create_etl_pipeline, process_aasx_batch

class TestAASXETLPipeline(unittest.TestCase):
    """Test cases for AASXETLPipeline class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config = ETLPipelineConfig(
            enable_validation=True,
            enable_logging=True,
            enable_backup=False,
            parallel_processing=False,
            max_workers=2
        )
        
        # Create sample AASX file for testing
        self.sample_aasx_file = Path(self.test_dir) / "test_sample.aasx"
        self._create_sample_aasx_file()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_sample_aasx_file(self):
        """Create a sample AASX file for testing"""
        # This is a minimal AASX file structure for testing
        import zipfile
        
        with zipfile.ZipFile(self.sample_aasx_file, 'w') as zf:
            # Add AASX manifest
            manifest = {
                "aasx": {
                    "fileVersion": "1.0",
                    "aasxOrigin": {
                        "aas": {
                            "assetAdministrationShells": [
                                {
                                    "id": "asset_001",
                                    "idShort": "TestAsset",
                                    "description": [
                                        {
                                            "language": "en",
                                            "text": "Test Asset for ETL Pipeline"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
            
            zf.writestr('AASX-Origin', json.dumps(manifest, indent=2))
            
            # Add sample submodel
            submodel = {
                "id": "submodel_001",
                "idShort": "TechnicalData",
                "description": [
                    {
                        "language": "en",
                        "text": "Technical specifications"
                    }
                ]
            }
            
            zf.writestr('aasx/smc/TechnicalData.json', json.dumps(submodel, indent=2))
    
    def test_pipeline_initialization(self):
        """Test ETL pipeline initialization"""
        pipeline = AASXETLPipeline(self.config)
        
        self.assertIsNotNone(pipeline)
        self.assertIsNotNone(pipeline.processor)
        self.assertIsNotNone(pipeline.transformer)
        self.assertIsNotNone(pipeline.loader)
        self.assertEqual(pipeline.config.enable_validation, True)
        self.assertEqual(pipeline.config.parallel_processing, False)
    
    @patch('aasx.aasx_processor.AASXProcessor.process_aasx_file')
    @patch('aasx.aasx_transformer.AASXTransformer.transform_aasx_data')
    @patch('aasx.aasx_loader.AASXLoader.load_aasx_data')
    def test_single_file_processing(self, mock_load, mock_transform, mock_extract):
        """Test processing of a single AASX file"""
        # Mock successful extraction
        mock_extract.return_value = {
            'success': True,
            'data': {
                'assets': [{'id': 'asset_001', 'description': 'Test Asset'}],
                'submodels': [{'id': 'submodel_001', 'description': 'Test Submodel'}]
            },
            'metadata': {'source_file': 'test.aasx'},
            'processing_time': 0.1
        }
        
        # Mock successful transformation
        mock_transform.return_value = {
            'success': True,
            'data': {
                'data': {
                    'assets': [{'id': 'asset_001', 'description': 'Test Asset', 'qi_metadata': {'quality_level': 'high'}}],
                    'submodels': [{'id': 'submodel_001', 'description': 'Test Submodel', 'qi_metadata': {'quality_level': 'medium'}}]
                }
            },
            'transformations_applied': ['quality_enrichment'],
            'processing_time': 0.2
        }
        
        # Mock successful loading
        mock_load.return_value = {
            'files_exported': ['output.json', 'output.yaml'],
            'database_records': 2,
            'vector_embeddings': 2,
            'errors': []
        }
        
        pipeline = AASXETLPipeline(self.config)
        result = pipeline.process_aasx_file(self.sample_aasx_file)
        
        # Verify result structure
        self.assertEqual(result['status'], 'completed')
        self.assertIn('extract_result', result)
        self.assertIn('transform_result', result)
        self.assertIn('load_result', result)
        self.assertGreater(result['processing_time'], 0)
        
        # Verify pipeline statistics
        self.assertEqual(pipeline.stats['files_processed'], 1)
        self.assertEqual(pipeline.stats['files_failed'], 0)
        self.assertGreater(pipeline.stats['total_processing_time'], 0)
    
    @patch('aasx.aasx_processor.AASXProcessor.process_aasx_file')
    def test_extraction_failure_handling(self, mock_extract):
        """Test handling of extraction failures"""
        # Mock failed extraction
        mock_extract.return_value = {
            'success': False,
            'error': 'Invalid AASX file format',
            'processing_time': 0.1
        }
        
        pipeline = AASXETLPipeline(self.config)
        result = pipeline.process_aasx_file(self.sample_aasx_file)
        
        # Verify failure handling
        self.assertEqual(result['status'], 'failed')
        self.assertIn('error', result)
        self.assertEqual(pipeline.stats['files_failed'], 1)
        self.assertEqual(pipeline.stats['files_processed'], 0)
    
    @patch('aasx.aasx_processor.AASXProcessor.process_aasx_file')
    @patch('aasx.aasx_transformer.AASXTransformer.transform_aasx_data')
    def test_transformation_failure_handling(self, mock_transform, mock_extract):
        """Test handling of transformation failures"""
        # Mock successful extraction
        mock_extract.return_value = {
            'success': True,
            'data': {'assets': [], 'submodels': []},
            'processing_time': 0.1
        }
        
        # Mock failed transformation
        mock_transform.return_value = {
            'success': False,
            'error': 'Transformation error',
            'processing_time': 0.2
        }
        
        pipeline = AASXETLPipeline(self.config)
        result = pipeline.process_aasx_file(self.sample_aasx_file)
        
        # Verify failure handling
        self.assertEqual(result['status'], 'failed')
        self.assertIn('error', result)
        self.assertEqual(pipeline.stats['files_failed'], 1)
    
    def test_directory_processing(self):
        """Test processing of a directory containing AASX files"""
        # Create multiple sample files
        test_files = []
        for i in range(3):
            file_path = Path(self.test_dir) / f"test_{i}.aasx"
            shutil.copy(self.sample_aasx_file, file_path)
            test_files.append(file_path)
        
        with patch('aasx.aasx_processor.AASXProcessor.process_aasx_file') as mock_extract, \
             patch('aasx.aasx_transformer.AASXTransformer.transform_aasx_data') as mock_transform, \
             patch('aasx.aasx_loader.AASXLoader.load_aasx_data') as mock_load:
            
            # Mock successful processing for all files
            mock_extract.return_value = {
                'success': True,
                'data': {'assets': [], 'submodels': []},
                'processing_time': 0.1
            }
            
            mock_transform.return_value = {
                'success': True,
                'data': {'data': {'assets': [], 'submodels': []}},
                'processing_time': 0.2
            }
            
            mock_load.return_value = {
                'files_exported': [],
                'database_records': 0,
                'vector_embeddings': 0,
                'errors': []
            }
            
            pipeline = AASXETLPipeline(self.config)
            result = pipeline.process_aasx_directory(self.test_dir)
            
            # Verify batch processing results
            self.assertEqual(result['files_found'], 3)
            self.assertEqual(result['files_processed'], 3)
            self.assertEqual(result['files_failed'], 0)
            self.assertGreater(result['total_time'], 0)
            self.assertIn('results', result)
            self.assertEqual(len(result['results']), 3)
    
    def test_parallel_processing_config(self):
        """Test parallel processing configuration"""
        parallel_config = ETLPipelineConfig(
            parallel_processing=True,
            max_workers=2
        )
        
        pipeline = AASXETLPipeline(parallel_config)
        
        self.assertTrue(pipeline.config.parallel_processing)
        self.assertEqual(pipeline.config.max_workers, 2)
    
    def test_pipeline_validation(self):
        """Test pipeline validation functionality"""
        pipeline = AASXETLPipeline(self.config)
        
        validation_result = pipeline.validate_pipeline()
        
        # Verify validation structure
        self.assertIn('pipeline_valid', validation_result)
        self.assertIn('components', validation_result)
        self.assertIn('errors', validation_result)
        
        # Verify component validation
        components = validation_result['components']
        self.assertIn('processor', components)
        self.assertIn('transformer', components)
        self.assertIn('loader', components)
        
        # All components should be valid
        for component_name, component_result in components.items():
            self.assertTrue(component_result['valid'])
            self.assertEqual(component_result['status'], 'OK')
    
    def test_pipeline_statistics(self):
        """Test pipeline statistics collection"""
        pipeline = AASXETLPipeline(self.config)
        
        # Get initial stats
        initial_stats = pipeline.get_pipeline_stats()
        
        self.assertIn('files_processed', initial_stats)
        self.assertIn('files_failed', initial_stats)
        self.assertIn('total_processing_time', initial_stats)
        self.assertIn('pipeline_config', initial_stats)
        self.assertIn('component_stats', initial_stats)
        
        # Verify initial values
        self.assertEqual(initial_stats['files_processed'], 0)
        self.assertEqual(initial_stats['files_failed'], 0)
        self.assertEqual(initial_stats['total_processing_time'], 0)
    
    def test_statistics_reset(self):
        """Test pipeline statistics reset"""
        pipeline = AASXETLPipeline(self.config)
        
        # Modify some stats
        pipeline.stats['files_processed'] = 5
        pipeline.stats['files_failed'] = 2
        
        # Reset stats
        pipeline.reset_stats()
        
        # Verify reset
        self.assertEqual(pipeline.stats['files_processed'], 0)
        self.assertEqual(pipeline.stats['files_failed'], 0)
        self.assertEqual(pipeline.stats['total_processing_time'], 0)
    
    def test_pipeline_report_export(self):
        """Test pipeline report export functionality"""
        pipeline = AASXETLPipeline(self.config)
        
        report_path = os.path.join(self.test_dir, "pipeline_report.json")
        exported_path = pipeline.export_pipeline_report(report_path)
        
        # Verify report was created
        self.assertEqual(exported_path, report_path)
        self.assertTrue(Path(report_path).exists())
        
        # Verify report content
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        self.assertEqual(report['report_type'], 'AASX_ETL_Pipeline_Report')
        self.assertIn('generated_at', report)
        self.assertIn('pipeline_config', report)
        self.assertIn('pipeline_stats', report)
        self.assertIn('validation_results', report)
        self.assertIn('component_configs', report)
    
    @patch('aasx.aasx_loader.AASXLoader.get_database_stats')
    @patch('aasx.aasx_loader.AASXLoader.export_for_rag')
    def test_rag_dataset_creation(self, mock_export_rag, mock_db_stats):
        """Test RAG dataset creation"""
        # Mock database stats
        mock_db_stats.return_value = {
            'assets_count': 2,
            'submodels_count': 1,
            'documents_count': 0,
            'relationships_count': 1
        }
        
        # Mock RAG export
        mock_export_rag.return_value = "rag_dataset.json"
        
        pipeline = AASXETLPipeline(self.config)
        rag_path = os.path.join(self.test_dir, "rag_dataset.json")
        
        exported_path = pipeline.create_rag_ready_dataset(rag_path)
        
        # Verify RAG dataset was created
        self.assertEqual(exported_path, "rag_dataset.json")
        mock_export_rag.assert_called_once_with(rag_path)
    
    @patch('aasx.aasx_loader.AASXLoader.get_database_stats')
    def test_rag_dataset_creation_no_data(self, mock_db_stats):
        """Test RAG dataset creation with no data"""
        # Mock empty database
        mock_db_stats.return_value = {
            'assets_count': 0,
            'submodels_count': 0,
            'documents_count': 0,
            'relationships_count': 0
        }
        
        pipeline = AASXETLPipeline(self.config)
        rag_path = os.path.join(self.test_dir, "rag_dataset.json")
        
        # Should raise error for no data
        with self.assertRaises(ValueError):
            pipeline.create_rag_ready_dataset(rag_path)

class TestETLPipelineConfig(unittest.TestCase):
    """Test cases for ETLPipelineConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ETLPipelineConfig()
        
        self.assertEqual(config.extract_config, {})
        self.assertIsNotNone(config.transform_config)
        self.assertIsNotNone(config.load_config)
        self.assertTrue(config.enable_validation)
        self.assertTrue(config.enable_logging)
        self.assertTrue(config.enable_backup)
        self.assertFalse(config.parallel_processing)
        self.assertEqual(config.max_workers, 4)
    
    def test_custom_config(self):
        """Test custom configuration values"""
        custom_config = ETLPipelineConfig(
            extract_config={'custom_param': 'value'},
            enable_validation=False,
            enable_logging=False,
            enable_backup=False,
            parallel_processing=True,
            max_workers=8
        )
        
        self.assertEqual(custom_config.extract_config['custom_param'], 'value')
        self.assertFalse(custom_config.enable_validation)
        self.assertFalse(custom_config.enable_logging)
        self.assertFalse(custom_config.enable_backup)
        self.assertTrue(custom_config.parallel_processing)
        self.assertEqual(custom_config.max_workers, 8)

class TestETLPipelineFactory(unittest.TestCase):
    """Test cases for ETL pipeline factory functions"""
    
    def test_create_etl_pipeline(self):
        """Test ETL pipeline factory function"""
        pipeline = create_etl_pipeline()
        
        self.assertIsInstance(pipeline, AASXETLPipeline)
        self.assertIsNotNone(pipeline.processor)
        self.assertIsNotNone(pipeline.transformer)
        self.assertIsNotNone(pipeline.loader)
    
    def test_create_etl_pipeline_with_config(self):
        """Test ETL pipeline factory function with custom config"""
        config = ETLPipelineConfig(
            enable_validation=False,
            parallel_processing=True
        )
        
        pipeline = create_etl_pipeline(config)
        
        self.assertIsInstance(pipeline, AASXETLPipeline)
        self.assertFalse(pipeline.config.enable_validation)
        self.assertTrue(pipeline.config.parallel_processing)
    
    @patch('aasx.aasx_processor.AASXProcessor.process_aasx_file')
    @patch('aasx.aasx_transformer.AASXTransformer.transform_aasx_data')
    @patch('aasx.aasx_loader.AASXLoader.load_aasx_data')
    def test_process_aasx_batch(self, mock_load, mock_transform, mock_extract):
        """Test batch processing function"""
        # Mock successful processing
        mock_extract.return_value = {
            'success': True,
            'data': {'assets': [], 'submodels': []},
            'processing_time': 0.1
        }
        
        mock_transform.return_value = {
            'success': True,
            'data': {'data': {'assets': [], 'submodels': []}},
            'processing_time': 0.2
        }
        
        mock_load.return_value = {
            'files_exported': [],
            'database_records': 0,
            'vector_embeddings': 0,
            'errors': []
        }
        
        # Create test files
        test_files = [
            Path(tempfile.mkdtemp()) / "test1.aasx",
            Path(tempfile.mkdtemp()) / "test2.aasx"
        ]
        
        for file_path in test_files:
            file_path.parent.mkdir(exist_ok=True)
            file_path.touch()
        
        try:
            result = process_aasx_batch(test_files)
            
            # Verify batch processing results
            self.assertEqual(result['files_processed'], 2)
            self.assertEqual(result['files_failed'], 0)
            self.assertGreater(result['total_time'], 0)
            self.assertIn('results', result)
            self.assertEqual(len(result['results']), 2)
            self.assertIn('pipeline_stats', result)
            
        finally:
            # Clean up test files
            for file_path in test_files:
                shutil.rmtree(file_path.parent, ignore_errors=True)

if __name__ == '__main__':
    unittest.main() 