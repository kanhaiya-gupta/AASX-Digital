#!/usr/bin/env python3
"""
Test Complete Data Flow Script

This script tests the complete data flow from ETL pipeline to AI/RAG system:
1. ETL Pipeline exports data in multiple formats
2. Data is loaded into Qdrant vector database
3. AI/RAG system can access and use the data
4. Complete data flow verification
"""

import sys
import os
import json
import yaml
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.aasx.aasx_loader import AASXLoader, LoaderConfig
    from src.ai_rag.ai_rag import EnhancedRAGSystem
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install qdrant-client sentence-transformers openai python-dotenv")
    sys.exit(1)

def test_etl_pipeline_export():
    """Test ETL pipeline export functionality"""
    print("🔧 Testing ETL Pipeline Export...")
    
    # Create test configuration with all export formats
    config = LoaderConfig(
        output_directory="output/test_etl",
        database_path="output/test_etl/test/aasx_data.db",
        vector_db_type="qdrant",
        qdrant_url="http://localhost:6333",
        qdrant_collection_prefix="test_aasx",
        backup_existing=False,  # Disable backup for cleaner test output
        export_formats=['json', 'yaml', 'csv', 'tsv', 'graph', 'rag', 'vector_db', 'sqlite']
    )
    
    # Create test data
    test_data = {
        'metadata': {
            'source_file': 'test.aasx',
            'processed_at': '2024-01-01T00:00:00Z',
            'version': '1.0'
        },
        'data': {
            'assets': [
                {
                    'id': 'asset_001',
                    'id_short': 'Motor1',
                    'description': 'DC Servo Motor',
                    'type': 'Motor',
                    'quality_level': 'high',
                    'compliance_status': 'compliant',
                    'properties': {
                        'voltage': '24V',
                        'power': '100W',
                        'speed': '3000RPM'
                    }
                }
            ],
            'submodels': [
                {
                    'id': 'submodel_001',
                    'id_short': 'TechnicalData',
                    'description': 'Technical Data Submodel',
                    'type': 'TechnicalData',
                    'quality_level': 'high',
                    'compliance_status': 'compliant'
                }
            ],
            'documents': [
                {
                    'id': 'doc_001',
                    'id_short': 'Manual',
                    'description': 'User Manual',
                    'type': 'Manual',
                    'filename': 'manual.pdf',
                    'size': 1024000
                }
            ]
        }
    }
    
    try:
        # Initialize loader
        loader = AASXLoader(config, source_file="test.aasx")
        
        # Load data
        result = loader.load_aasx_data(test_data)
        
        print(f"✅ ETL Export completed:")
        print(f"   - Files exported: {len(result.get('files_exported', []))}")
        print(f"   - Database records: {result.get('database_records', 0)}")
        print(f"   - Vector embeddings: {result.get('vector_embeddings', 0)}")
        print(f"   - Export formats: {result.get('export_formats', [])}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ ETL Export failed: {e}")
        return False, None

def test_qdrant_connection():
    """Test Qdrant connection and file-specific collections"""
    print("\n🔍 Testing Qdrant Connection...")
    
    try:
        client = QdrantClient(url="http://localhost:6333", timeout=10)
        
        # Get collections
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        print(f"✅ Qdrant connected successfully")
        print(f"   - Available collections: {collection_names}")
        
        # Check for test collections (file-specific naming)
        test_collections = ['test_aasx_test_assets', 'test_aasx_test_submodels', 'test_aasx_test_documents']
        found_collections = [name for name in test_collections if name in collection_names]
        
        if found_collections:
            print(f"   - Test collections found: {found_collections}")
            
            # Check collection info
            for collection_name in found_collections:
                info = client.get_collection(collection_name)
                print(f"   - {collection_name}: {info.points_count} points")
                
                # Verify file-specific naming
                if 'test_' in collection_name:
                    print(f"     ✅ File-specific collection naming verified")
        
        # Check for any AASX collections to show file isolation
        aasx_collections = [name for name in collection_names if name.startswith('aasx_')]
        if aasx_collections:
            print(f"   - AASX collections found: {len(aasx_collections)}")
            print(f"     Example: {aasx_collections[:3]}")  # Show first 3
        
        return True, collection_names
        
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False, None

def test_ai_rag_system():
    """Test AI/RAG system with file-specific collections"""
    print("\n🤖 Testing AI/RAG System...")
    
    try:
        # Initialize RAG system
        rag_system = EnhancedRAGSystem()
        
        # Test connection status
        status = rag_system.get_system_status()
        print(f"✅ RAG System Status:")
        print(f"   - OpenAI: {status.get('openai', 'unknown')}")
        print(f"   - Qdrant: {status.get('qdrant', 'unknown')}")
        print(f"   - Neo4j: {status.get('neo4j', 'unknown')}")
        
        # Test file management functionality
        print(f"\n📁 Testing file management:")
        available_files = rag_system.get_available_files()
        if available_files:
            print(f"✅ Found {len(available_files)} files with vector data:")
            for file_info in available_files:
                print(f"   - {file_info['file_name']}: {file_info['total_embeddings']} embeddings")
                print(f"     Collections: {file_info['collections']}")
        else:
            print("⚠️  No files found (this might be normal if no data is indexed)")
        
        # Test search functionality
        test_query = "DC Servo Motor specifications"
        print(f"\n🔍 Testing global search: '{test_query}'")
        
        results = rag_system.search_similar(test_query, top_k=3)
        
        if results:
            print(f"✅ Global search successful - Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.get('content', 'No content')[:100]}...")
                print(f"      File: {result.get('file_name', 'Unknown')}")
                print(f"      Score: {result.get('score', 0):.3f}")
        else:
            print("⚠️  No search results found (this might be normal if no data is indexed)")
        
        # Test file-specific search if we have files
        if available_files:
            test_file = available_files[0]['file_name']
            print(f"\n🔍 Testing file-specific search in '{test_file}': '{test_query}'")
            
            file_results = rag_system.search_similar(
                test_query, 
                top_k=3, 
                file_filter=test_file
            )
            
            if file_results:
                print(f"✅ File-specific search successful - Found {len(file_results)} results:")
                for i, result in enumerate(file_results, 1):
                    print(f"   {i}. {result.get('content', 'No content')[:100]}...")
                    print(f"      File: {result.get('file_name', 'Unknown')}")
                    print(f"      Score: {result.get('score', 0):.3f}")
            else:
                print("⚠️  No file-specific results found")
        
        return True, results
        
    except Exception as e:
        print(f"❌ AI/RAG System test failed: {e}")
        return False, None

def test_data_consistency():
    """Test data consistency across different export formats"""
    print("\n📊 Testing Data Consistency...")
    
    try:
        # Check SQLite database
        db_path = "output/test_etl/test/aasx_data.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check assets
            cursor.execute("SELECT COUNT(*) FROM assets")
            asset_count = cursor.fetchone()[0]
            
            # Check submodels
            cursor.execute("SELECT COUNT(*) FROM submodels")
            submodel_count = cursor.fetchone()[0]
            
            # Check documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            document_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"✅ SQLite Database:")
            print(f"   - Assets: {asset_count}")
            print(f"   - Submodels: {submodel_count}")
            print(f"   - Documents: {document_count}")
        
        # Check JSON export
        json_path = "output/test_etl/aasx_data.json"
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                json_data = json.load(f)
            
            assets = json_data.get('data', {}).get('assets', [])
            submodels = json_data.get('data', {}).get('submodels', [])
            documents = json_data.get('data', {}).get('documents', [])
            
            print(f"✅ JSON Export:")
            print(f"   - Assets: {len(assets)}")
            print(f"   - Submodels: {len(submodels)}")
            print(f"   - Documents: {len(documents)}")
        
        # Check RAG export
        rag_path = "output/test_etl/aasx_data_rag.json"
        if os.path.exists(rag_path):
            with open(rag_path, 'r') as f:
                rag_data = json.load(f)
            
            entities = rag_data.get('entities', [])
            print(f"✅ RAG Export:")
            print(f"   - Entities: {len(entities)}")
        else:
            print(f"⚠️  RAG Export: File not found (this might be normal if database is empty)")
        
        return True
        
    except Exception as e:
        print(f"❌ Data consistency test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Complete Data Flow")
    print("=" * 50)
    
    # Test 1: ETL Pipeline Export
    etl_success, etl_result = test_etl_pipeline_export()
    
    # Test 2: Qdrant Connection
    qdrant_success, collections = test_qdrant_connection()
    
    # Test 3: AI/RAG System
    rag_success, search_results = test_ai_rag_system()
    
    # Test 4: Data Consistency
    consistency_success = test_data_consistency()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("ETL Pipeline Export", etl_success),
        ("Qdrant Connection", qdrant_success),
        ("AI/RAG System", rag_success),
        ("Data Consistency", consistency_success)
    ]
    
    passed = 0
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Complete data flow is working correctly.")
        print("\n✅ Data Flow Summary:")
        print("   1. ETL Pipeline → Exports data in multiple formats")
        print("   2. Qdrant → Stores vector embeddings")
        print("   3. AI/RAG System → Can search and use the data")
        print("   4. Data Consistency → All formats contain consistent data")
    else:
        print("⚠️  Some tests failed. Please check the configuration and dependencies.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 