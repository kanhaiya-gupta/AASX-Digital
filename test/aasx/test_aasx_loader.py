"""
Tests for AASX Data Loader Module

Tests the loading functionality including file export, database storage,
and vector database integration for RAG applications.
"""

import unittest
import tempfile
import shutil
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from aasx.aasx_loader import AASXLoader, LoaderConfig

class TestAASXLoader(unittest.TestCase):
    """Test cases for AASXLoader class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config = LoaderConfig(
            output_directory=os.path.join(self.test_dir, "output"),
            database_path=os.path.join(self.test_dir, "test_aasx.db"),
            vector_db_path=os.path.join(self.test_dir, "vector_db"),
            backup_existing=False
        )
        
        # Sample transformed data
        self.sample_data = {
            'metadata': {
                'source_file': 'test.aasx',
                'processed_at': '2024-01-01T00:00:00Z',
                'version': '1.0'
            },
            'data': {
                'assets': [
                    {
                        'id': 'asset_001',
                        'id_short': 'Motor_001',
                        'description': 'DC Servo Motor for Quality Control',
                        'type': 'Motor',
                        'qi_metadata': {
                            'quality_level': 'high',
                            'compliance_status': 'certified'
                        },
                        'asset_information': {
                            'manufacturer': 'TestCorp',
                            'model': 'DC-1000'
                        },
                        'metadata': {
                            'location': 'Production Line A',
                            'installation_date': '2023-01-01'
                        }
                    }
                ],
                'submodels': [
                    {
                        'id': 'submodel_001',
                        'id_short': 'TechnicalData_001',
                        'description': 'Technical specifications and parameters',
                        'type': 'TechnicalData',
                        'qi_metadata': {
                            'quality_level': 'medium',
                            'compliance_status': 'pending'
                        },
                        'semantic_id': {
                            'type': 'IRI',
                            'value': 'https://example.com/tech-data'
                        },
                        'metadata': {
                            'version': '1.2',
                            'last_updated': '2023-12-01'
                        }
                    }
                ],
                'documents': [
                    {
                        'filename': 'technical_spec.pdf',
                        'size': 1024000,
                        'type': 'application/pdf',
                        'metadata': {
                            'title': 'Technical Specifications',
                            'author': 'Engineering Team'
                        }
                    }
                ],
                'relationships': [
                    {
                        'source_id': 'asset_001',
                        'target_id': 'submodel_001',
                        'type': 'has_submodel',
                        'metadata': {
                            'relationship_type': 'composition'
                        }
                    }
                ]
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_loader_initialization(self):
        """Test AASXLoader initialization"""
        loader = AASXLoader(self.config)
        
        self.assertIsNotNone(loader)
        self.assertEqual(loader.config.output_directory, self.config.output_directory)
        self.assertTrue(Path(loader.config.output_directory).exists())
    
    def test_export_to_files(self):
        """Test file export functionality"""
        loader = AASXLoader(self.config)
        
        # Test file export
        exported_files = loader._export_to_files(self.sample_data)
        
        self.assertIsInstance(exported_files, list)
        self.assertGreater(len(exported_files), 0)
        
        # Check that files were created
        for file_path in exported_files:
            self.assertTrue(Path(file_path).exists())
        
        # Check JSON file content
        json_files = [f for f in exported_files if f.endswith('.json')]
        if json_files:
            with open(json_files[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertEqual(data['metadata']['source_file'], 'test.aasx')
        
        # Check YAML file content
        yaml_files = [f for f in exported_files if f.endswith('.yaml')]
        if yaml_files:
            import yaml
            with open(yaml_files[0], 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.assertEqual(data['metadata']['source_file'], 'test.aasx')
        
        # Check CSV file content
        csv_files = [f for f in exported_files if f.endswith('.csv')]
        if csv_files:
            import csv
            with open(csv_files[0], 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertGreater(len(rows), 0)
                # Check that we have both assets and submodels
                entity_types = [row['entity_type'] for row in rows]
                self.assertIn('asset', entity_types)
                self.assertIn('submodel', entity_types)
    
    def test_database_loading(self):
        """Test database loading functionality"""
        loader = AASXLoader(self.config)
        
        # Load data to database
        records_loaded = loader._load_to_database(self.sample_data)
        
        self.assertGreater(records_loaded, 0)
        
        # Verify database was created
        self.assertTrue(Path(self.config.database_path).exists())
        
        # Check database content
        conn = sqlite3.connect(self.config.database_path)
        cursor = conn.cursor()
        
        # Check assets table
        cursor.execute('SELECT COUNT(*) FROM assets')
        asset_count = cursor.fetchone()[0]
        self.assertEqual(asset_count, 1)
        
        # Check submodels table
        cursor.execute('SELECT COUNT(*) FROM submodels')
        submodel_count = cursor.fetchone()[0]
        self.assertEqual(submodel_count, 1)
        
        # Check documents table
        cursor.execute('SELECT COUNT(*) FROM documents')
        document_count = cursor.fetchone()[0]
        self.assertEqual(document_count, 1)
        
        # Check relationships table
        cursor.execute('SELECT COUNT(*) FROM relationships')
        relationship_count = cursor.fetchone()[0]
        self.assertEqual(relationship_count, 1)
        
        # Check specific asset data
        cursor.execute('SELECT id_short, description, type FROM assets WHERE id = ?', ('asset_001',))
        asset_data = cursor.fetchone()
        self.assertIsNotNone(asset_data)
        self.assertEqual(asset_data[0], 'Motor_001')
        self.assertEqual(asset_data[1], 'DC Servo Motor for Quality Control')
        self.assertEqual(asset_data[2], 'Motor')
        
        conn.close()
    
    def test_database_stats(self):
        """Test database statistics functionality"""
        loader = AASXLoader(self.config)
        
        # Load some data first
        loader._load_to_database(self.sample_data)
        
        # Get stats
        stats = loader.get_database_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['assets_count'], 1)
        self.assertEqual(stats['submodels_count'], 1)
        self.assertEqual(stats['documents_count'], 1)
        self.assertEqual(stats['relationships_count'], 1)
    
    @patch('aasx.aasx_loader.CHROMADB_AVAILABLE', True)
    @patch('aasx.aasx_loader.SENTENCE_TRANSFORMERS_AVAILABLE', True)
    def test_vector_database_initialization(self):
        """Test vector database initialization"""
        with patch('chromadb.PersistentClient') as mock_client:
            mock_collection = Mock()
            mock_client.return_value.get_or_create_collection.return_value = mock_collection
            
            loader = AASXLoader(self.config)
            
            # Verify ChromaDB was initialized
            mock_client.assert_called_once()
    
    @patch('aasx.aasx_loader.CHROMADB_AVAILABLE', True)
    @patch('aasx.aasx_loader.SENTENCE_TRANSFORMERS_AVAILABLE', True)
    def test_vector_database_loading(self):
        """Test vector database loading functionality"""
        with patch('chromadb.PersistentClient') as mock_client, \
             patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            
            # Mock the embedding model
            mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 20  # 100-dimensional vector
            mock_transformer.return_value.encode.return_value = mock_embedding
            
            # Mock collections
            mock_collection = Mock()
            mock_client.return_value.get_or_create_collection.return_value = mock_collection
            
            loader = AASXLoader(self.config)
            
            # Load to vector database
            embeddings_loaded = loader._load_to_vector_db(self.sample_data)
            
            # Verify embeddings were created
            self.assertGreater(embeddings_loaded, 0)
            
            # Verify add was called on collections
            self.assertGreater(mock_collection.add.call_count, 0)
    
    @patch('aasx.aasx_loader.CHROMADB_AVAILABLE', True)
    @patch('aasx.aasx_loader.SENTENCE_TRANSFORMERS_AVAILABLE', True)
    def test_vector_search(self):
        """Test vector search functionality"""
        with patch('chromadb.PersistentClient') as mock_client, \
             patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            
            # Mock the embedding model
            mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 20
            mock_transformer.return_value.encode.return_value = mock_embedding
            
            # Mock search results
            mock_search_results = {
                'ids': [['asset_001']],
                'documents': [['Asset: Motor_001 - DC Servo Motor for Quality Control']],
                'metadatas': [[{'entity_type': 'asset', 'entity_id': 'asset_001'}]],
                'distances': [[0.1]]
            }
            
            mock_collection = Mock()
            mock_collection.query.return_value = mock_search_results
            mock_client.return_value.get_or_create_collection.return_value = mock_collection
            
            loader = AASXLoader(self.config)
            
            # Test search
            results = loader.search_similar("motor quality control", top_k=5)
            
            # Verify search was performed
            self.assertIsInstance(results, list)
            if results:  # If vector DB is available
                self.assertGreater(len(results), 0)
                self.assertIn('id', results[0])
                self.assertIn('entity_type', results[0])
    
    def test_create_embedding_text(self):
        """Test embedding text creation"""
        loader = AASXLoader(self.config)
        
        # Test asset text creation
        asset = self.sample_data['data']['assets'][0]
        text = loader._create_embedding_text(asset, 'asset')
        
        self.assertIsInstance(text, str)
        self.assertIn('Type: asset', text)
        self.assertIn('ID: asset_001', text)
        self.assertIn('Asset Type: Motor', text)
        self.assertIn('Quality Level: high', text)
        
        # Test submodel text creation
        submodel = self.sample_data['data']['submodels'][0]
        text = loader._create_embedding_text(submodel, 'submodel')
        
        self.assertIsInstance(text, str)
        self.assertIn('Type: submodel', text)
        self.assertIn('ID: submodel_001', text)
        self.assertIn('Submodel Type: TechnicalData', text)
    
    def test_rag_export(self):
        """Test RAG-ready export functionality"""
        loader = AASXLoader(self.config)
        
        # Load data first
        loader._load_to_database(self.sample_data)
        
        # Export for RAG
        rag_file = os.path.join(self.test_dir, "rag_export.json")
        exported_path = loader.export_for_rag(rag_file)
        
        self.assertEqual(exported_path, rag_file)
        self.assertTrue(Path(rag_file).exists())
        
        # Check RAG file content
        with open(rag_file, 'r', encoding='utf-8') as f:
            rag_data = json.load(f)
            
        self.assertEqual(rag_data['version'], '1.0')
        self.assertEqual(rag_data['format'], 'rag_ready')
        self.assertIn('entities', rag_data)
        self.assertGreater(len(rag_data['entities']), 0)
        
        # Check entity structure
        entity = rag_data['entities'][0]
        self.assertIn('type', entity)
        self.assertIn('id', entity)
        self.assertIn('content', entity)
        self.assertIn('metadata', entity)
    
    def test_complete_loading_pipeline(self):
        """Test complete loading pipeline"""
        loader = AASXLoader(self.config)
        
        # Run complete loading
        results = loader.load_aasx_data(self.sample_data)
        
        # Verify results structure
        self.assertIn('files_exported', results)
        self.assertIn('database_records', results)
        self.assertIn('vector_embeddings', results)
        self.assertIn('errors', results)
        
        # Verify files were exported
        self.assertGreater(len(results['files_exported']), 0)
        
        # Verify database records were created
        self.assertGreater(results['database_records'], 0)
        
        # Verify no errors
        self.assertEqual(len(results['errors']), 0)
    
    def test_error_handling(self):
        """Test error handling in loader"""
        loader = AASXLoader(self.config)
        
        # Test with invalid data
        invalid_data = {'invalid': 'data'}
        
        results = loader.load_aasx_data(invalid_data)
        
        # Should handle gracefully
        self.assertIn('errors', results)
        # May have some errors but shouldn't crash
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test with custom config
        custom_config = LoaderConfig(
            output_directory="/custom/path",
            database_path="/custom/db.sqlite",
            vector_db_path="/custom/vector",
            embedding_model="custom-model"
        )
        
        loader = AASXLoader(custom_config)
        
        self.assertEqual(loader.config.output_directory, "/custom/path")
        self.assertEqual(loader.config.database_path, "/custom/db.sqlite")
        self.assertEqual(loader.config.vector_db_path, "/custom/vector")
        self.assertEqual(loader.config.embedding_model, "custom-model")

class TestLoaderConfig(unittest.TestCase):
    """Test cases for LoaderConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = LoaderConfig()
        
        self.assertEqual(config.output_directory, "output")
        self.assertEqual(config.database_path, "aasx_data.db")
        self.assertEqual(config.vector_db_path, "vector_db")
        self.assertEqual(config.vector_db_type, "chromadb")
        self.assertEqual(config.embedding_model, "all-MiniLM-L6-v2")
        self.assertEqual(config.chunk_size, 512)
        self.assertEqual(config.overlap_size, 50)
        self.assertTrue(config.include_metadata)
        self.assertTrue(config.create_indexes)
        self.assertTrue(config.backup_existing)
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = LoaderConfig(
            output_directory="custom_output",
            database_path="custom.db",
            vector_db_path="custom_vector",
            vector_db_type="faiss",
            embedding_model="custom-embedding",
            chunk_size=1024,
            overlap_size=100,
            include_metadata=False,
            create_indexes=False,
            backup_existing=False
        )
        
        self.assertEqual(config.output_directory, "custom_output")
        self.assertEqual(config.database_path, "custom.db")
        self.assertEqual(config.vector_db_path, "custom_vector")
        self.assertEqual(config.vector_db_type, "faiss")
        self.assertEqual(config.embedding_model, "custom-embedding")
        self.assertEqual(config.chunk_size, 1024)
        self.assertEqual(config.overlap_size, 100)
        self.assertFalse(config.include_metadata)
        self.assertFalse(config.create_indexes)
        self.assertFalse(config.backup_existing)

if __name__ == '__main__':
    unittest.main() 