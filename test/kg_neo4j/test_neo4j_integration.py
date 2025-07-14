#!/usr/bin/env python3
"""
Comprehensive Neo4j Integration Test Suite

This test suite validates the complete Neo4j integration functionality
for the AASX Data Modeling Platform.
"""

import sys
import os
import logging
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, will use system environment variables

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from kg_neo4j import Neo4jManager, AASXGraphAnalyzer, CypherQueries
        print("SUCCESS: All modules imported successfully")
        return True
    except ImportError as e:
        print(f"FAILED: Import error: {e}")
        return False

def test_neo4j_connection():
    """Test Neo4j connection (requires Neo4j to be running)"""
    print("\nTesting Neo4j connection...")
    
    try:
        from kg_neo4j import Neo4jManager
        
        # Try to connect to Neo4j using environment variables
        uri = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', 'password')
        
        manager = Neo4jManager(uri, user, password)
        
        # Test connection
        if manager.test_connection():
            print("SUCCESS: Neo4j connection successful")
            manager.close()
            return True
        else:
            print("FAILED: Neo4j connection failed")
            manager.close()
            return False
            
    except Exception as e:
        print(f"FAILED: Neo4j connection error: {e}")
        print("  Note: This test requires Neo4j to be running on localhost:7687")
        return False

def test_graph_file_validation():
    """Test graph file validation logic"""
    print("\nTesting graph file validation...")
    
    try:
        from kg_neo4j import Neo4jManager
        
        # Create a mock manager (without connection)
        manager = Neo4jManager.__new__(Neo4jManager)
        
        # Test valid graph data
        valid_data = {
            "format": "graph",
            "version": "1.0",
            "nodes": [
                {
                    "id": "test_asset",
                    "type": "asset",
                    "properties": {
                        "description": "Test Asset",
                        "quality_level": "HIGH"
                    }
                }
            ],
            "edges": []
        }
        
        if manager._validate_graph_data(valid_data):
            print("SUCCESS: Valid graph data validation passed")
        else:
            print("FAILED: Valid graph data validation failed")
            return False
        
        # Test invalid graph data
        invalid_data = {
            "format": "json",  # Wrong format
            "nodes": []
        }
        
        if not manager._validate_graph_data(invalid_data):
            print("SUCCESS: Invalid graph data validation passed")
        else:
            print("FAILED: Invalid graph data validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"FAILED: Graph validation test error: {e}")
        return False

def test_cypher_queries():
    """Test Cypher queries generation"""
    print("\nTesting Cypher queries...")
    
    try:
        from kg_neo4j import CypherQueries
        
        # Test static queries
        queries = [
            CypherQueries.BASIC_STATS,
            CypherQueries.QUALITY_DISTRIBUTION,
            CypherQueries.COMPLIANCE_SUMMARY,
            CypherQueries.ISOLATED_NODES
        ]
        
        for i, query in enumerate(queries, 1):
            if query and "MATCH" in query:
                print(f"SUCCESS: Query {i} generated successfully")
            else:
                print(f"FAILED: Query {i} generation failed")
                return False
        
        # Test dynamic query generation
        related_query = CypherQueries.find_related_entities("test_asset", 2)
        if "test_asset" in related_query and "1..2" in related_query:
            print("SUCCESS: Dynamic query generation successful")
        else:
            print("FAILED: Dynamic query generation failed")
            return False
        
        quality_query = CypherQueries.get_entities_by_quality("HIGH", "asset")
        if "HIGH" in quality_query and "asset" in quality_query:
            print("SUCCESS: Quality query generation successful")
        else:
            print("FAILED: Quality query generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"FAILED: Cypher queries test error: {e}")
        return False

def test_etl_integration():
    """Test integration with ETL pipeline output"""
    print("\nTesting ETL integration...")
    
    # Check if ETL output exists
    etl_output_dir = Path("../../output/etl_results")
    if not etl_output_dir.exists():
        print("FAILED: ETL output directory not found")
        print("  Run the ETL pipeline first: python scripts/run_etl.py")
        return False
    
    # Find graph files
    graph_files = list(etl_output_dir.rglob("*_graph.json"))
    if not graph_files:
        print("FAILED: No graph files found in ETL output")
        print("  Ensure ETL pipeline generates graph format")
        return False
    
    print(f"SUCCESS: Found {len(graph_files)} graph files in ETL output")
    
    # Test reading a graph file
    try:
        import json
        sample_file = graph_files[0]
        with open(sample_file, 'r') as f:
            graph_data = json.load(f)
        
        if graph_data.get('format') == 'graph' and 'nodes' in graph_data:
            print(f"SUCCESS: Graph file format valid: {sample_file.name}")
            print(f"  Nodes: {len(graph_data['nodes'])}")
            print(f"  Edges: {len(graph_data.get('edges', []))}")
        else:
            print(f"FAILED: Invalid graph file format: {sample_file.name}")
            return False
        
        return True
        
    except Exception as e:
        print(f"FAILED: Graph file reading error: {e}")
        return False

def test_environment_variables():
    """Test environment variable loading"""
    print("\nTesting environment variables...")
    
    try:
        # Test environment variable loading
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER')
        password = os.getenv('NEO4J_PASSWORD')
        
        if uri and user and password:
            print(f"SUCCESS: Environment variables loaded successfully")
            print(f"  URI: {uri}")
            print(f"  User: {user}")
            print(f"  Password: {'*' * len(password)} ({len(password)} chars)")
            return True
        else:
            print("FAILED: Environment variables not found")
            print("  Make sure .env file exists with NEO4J_* variables")
            return False
            
    except Exception as e:
        print(f"FAILED: Environment variable test error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Neo4j Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Module Imports", test_imports),
        ("Graph File Validation", test_graph_file_validation),
        ("Cypher Queries", test_cypher_queries),
        ("ETL Integration", test_etl_integration),
        ("Neo4j Connection", test_neo4j_connection),
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
        print("SUCCESS: All tests passed! Neo4j integration is ready to use.")
        print("\nNext steps:")
        print("1. Start Neo4j database")
        print("2. Run: python scripts/integrate_neo4j.py --import-dir output/etl_results/")
        print("3. Run: python scripts/integrate_neo4j.py --analyze")
    else:
        print("WARNING: Some tests failed. Check the output above for details.")
        print("\nTroubleshooting:")
        print("1. Install dependencies: pip install neo4j pandas python-dotenv")
        print("2. Start Neo4j database")
        print("3. Check .env file configuration")
        print("4. Run ETL pipeline: python scripts/run_etl.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 