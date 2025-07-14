#!/usr/bin/env python3
"""
Neo4j Data Import Test

This script tests the data import functionality for Neo4j.
"""

import sys
import os
import json
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

def test_data_import():
    """Test Neo4j data import functionality"""
    print("Testing Neo4j Data Import...")
    print("=" * 50)
    
    try:
        from kg_neo4j import Neo4jManager
        
        # Initialize manager
        uri = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', 'password')
        
        manager = Neo4jManager(uri, user, password)
        
        # Test connection first
        if not manager.test_connection():
            print("FAILED: Cannot test import - Neo4j connection failed")
            return False
        
        print("SUCCESS: Neo4j connection successful")
        
        # Find test graph file
        etl_output_dir = Path("../../output/etl_results")
        if not etl_output_dir.exists():
            print("FAILED: ETL output directory not found")
            print("   Run the ETL pipeline first: python scripts/run_etl.py")
            return False
        
        graph_files = list(etl_output_dir.rglob("*_graph.json"))
        if not graph_files:
            print("FAILED: No graph files found in ETL output")
            return False
        
        # Test importing a single file
        test_file = graph_files[0]
        print(f"Testing import with: {test_file.name}")
        
        # Read and validate graph data
        with open(test_file, 'r') as f:
            graph_data = json.load(f)
        
        if not manager._validate_graph_data(graph_data):
            print("FAILED: Graph data validation failed")
            return False
        
        print("SUCCESS: Graph data validation passed")
        
        # Test import (this will actually import to Neo4j)
        try:
            manager.import_graph_file(test_file)
            print("SUCCESS: Data import successful")
            
            # Get database info
            info = manager.get_database_info()
            print(f"Database info:")
            print(f"   Nodes: {info.get('node_count', 0)}")
            print(f"   Relationships: {info.get('relationship_count', 0)}")
            
            return True
            
        except Exception as e:
            print(f"FAILED: Data import failed: {e}")
            return False
        
    except Exception as e:
        print(f"FAILED: Test error: {e}")
        return False

def test_import_validation():
    """Test import validation without actual import"""
    print("\nTesting Import Validation...")
    print("=" * 40)
    
    try:
        from kg_neo4j import Neo4jManager
        
        # Create manager without connection
        manager = Neo4jManager.__new__(Neo4jManager)
        
        # Test valid graph data
        valid_data = {
            "format": "graph",
            "version": "1.0",
            "nodes": [
                {
                    "id": "test_asset_1",
                    "type": "asset",
                    "properties": {
                        "description": "Test Asset 1",
                        "quality_level": "HIGH"
                    }
                },
                {
                    "id": "test_submodel_1",
                    "type": "submodel",
                    "properties": {
                        "description": "Test Submodel 1",
                        "quality_level": "MEDIUM"
                    }
                }
            ],
            "edges": [
                {
                    "source": "test_asset_1",
                    "target": "test_submodel_1",
                    "type": "has_submodel",
                    "properties": {}
                }
            ]
        }
        
        if manager._validate_graph_data(valid_data):
            print("SUCCESS: Valid graph data validation passed")
        else:
            print("FAILED: Valid graph data validation failed")
            return False
        
        # Test invalid data
        invalid_data = {
            "format": "json",
            "nodes": []
        }
        
        if not manager._validate_graph_data(invalid_data):
            print("SUCCESS: Invalid graph data validation passed")
        else:
            print("FAILED: Invalid graph data validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"FAILED: Validation test error: {e}")
        return False

def main():
    """Run all import tests"""
    print("=" * 60)
    print("Neo4j Data Import Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Validation", test_import_validation),
        ("Data Import", test_data_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"FAILED: {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("SUCCESS: All import tests passed!")
    else:
        print("WARNING: Some import tests failed.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 