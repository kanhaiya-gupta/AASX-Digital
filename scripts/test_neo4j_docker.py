#!/usr/bin/env python3
"""
Test script for Neo4j Docker connection and Knowledge Graph service
"""

import os
import sys
from pathlib import Path

# Add webapp to path
sys.path.append(str(Path(__file__).parent.parent / "webapp"))

def test_neo4j_connection():
    """Test Neo4j connection"""
    print("🔍 Testing Neo4j Docker Connection...")
    
    try:
        from kg_neo4j.neo4j_service import get_neo4j_service
        
        # Get service instance
        service = get_neo4j_service()
        
        # Test connection status
        status = service.get_connection_status()
        print(f"✅ Connection Status: {status['status']}")
        print(f"📊 Connected: {status['connected']}")
        
        if status['connected']:
            print("🎉 Neo4j Docker connection successful!")
            
            # Test available files
            try:
                files = service.get_available_files()
                print(f"📁 Available graph files: {files['count']}")
                for file in files['files'][:3]:  # Show first 3 files
                    print(f"   - {file}")
                if len(files['files']) > 3:
                    print(f"   ... and {len(files['files']) - 3} more")
            except Exception as e:
                print(f"⚠️  Error checking files: {e}")
            
            return True
        else:
            print(f"❌ Connection failed: {status.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def test_import_functionality():
    """Test import functionality"""
    print("\n📥 Testing Import Functionality...")
    
    try:
        from kg_neo4j.neo4j_service import get_neo4j_service
        
        service = get_neo4j_service()
        
        # Test dry run import
        print("🔍 Testing dry run import...")
        result = service.import_graph_data("output/etl_results/", dry_run=True)
        
        print(f"📊 Dry run results:")
        print(f"   - Total files found: {result['total_files']}")
        print(f"   - Files that would be imported: {len(result['imported_files'])}")
        print(f"   - Failed files: {len(result['failed_files'])}")
        
        if result['total_files'] > 0:
            print("✅ Import functionality working!")
            return True
        else:
            print("⚠️  No graph files found in ETL output")
            return False
            
    except Exception as e:
        print(f"❌ Error testing import: {e}")
        return False

def test_query_functionality():
    """Test query functionality"""
    print("\n🔍 Testing Query Functionality...")
    
    try:
        from kg_neo4j.neo4j_service import get_neo4j_service
        
        service = get_neo4j_service()
        
        # Test simple query
        print("🔍 Testing simple query...")
        result = service.execute_custom_query("MATCH (n) RETURN count(n) as node_count")
        
        print(f"📊 Query results:")
        print(f"   - Status: {result['status']}")
        print(f"   - Row count: {result['row_count']}")
        
        if result['status'] == 'success':
            print("✅ Query functionality working!")
            return True
        else:
            print("❌ Query failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing query: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Neo4j Docker Connection & Service Test")
    print("=" * 60)
    
    # Test connection
    connection_ok = test_neo4j_connection()
    
    if connection_ok:
        # Test import
        import_ok = test_import_functionality()
        
        # Test query
        query_ok = test_query_functionality()
        
        print("\n" + "=" * 60)
        print("📋 Test Summary:")
        print(f"   - Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
        print(f"   - Import: {'✅ PASS' if import_ok else '❌ FAIL'}")
        print(f"   - Query: {'✅ PASS' if query_ok else '❌ FAIL'}")
        print("=" * 60)
        
        if connection_ok and import_ok and query_ok:
            print("🎉 All tests passed! Knowledge Graph is ready to use.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
    else:
        print("\n❌ Connection test failed. Cannot proceed with other tests.")
        print("💡 Make sure Neo4j Docker container is running and accessible.")

if __name__ == "__main__":
    main() 