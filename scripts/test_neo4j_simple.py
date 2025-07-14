#!/usr/bin/env python3
"""
Simple test script for Neo4j Docker connection
"""

import os
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent / "webapp"))
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_neo4j_connection():
    """Test Neo4j connection directly"""
    print("🔍 Testing Neo4j Docker Connection...")
    
    try:
        # Import the service directly
        import sys
        sys.path.append(str(Path(__file__).parent.parent / "webapp/kg_neo4j"))
        from neo4j_service import get_neo4j_service
        
        # Get service instance
        service = get_neo4j_service()
        
        # Test connection status
        status = service.get_connection_status()
        print(f"✅ Connection Status: {status['status']}")
        print(f"📊 Connected: {status['connected']}")
        
        if status['connected']:
            print("🎉 Neo4j Docker connection successful!")
            return True
        else:
            print(f"❌ Connection failed: {status.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_available_files():
    """Test file discovery"""
    print("\n📁 Testing File Discovery...")
    
    try:
        import sys
        sys.path.append(str(Path(__file__).parent.parent / "webapp/kg_neo4j"))
        from neo4j_service import get_neo4j_service
        
        service = get_neo4j_service()
        
        # Test available files
        files = service.get_available_files()
        print(f"📁 Available graph files: {files['count']}")
        for file in files['files'][:3]:  # Show first 3 files
            print(f"   - {file}")
        if len(files['files']) > 3:
            print(f"   ... and {len(files['files']) - 3} more")
        
        return True
            
    except Exception as e:
        print(f"❌ Error checking files: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Simple Neo4j Docker Connection Test")
    print("=" * 60)
    
    # Test connection
    connection_ok = test_neo4j_connection()
    
    if connection_ok:
        # Test file discovery
        files_ok = test_available_files()
        
        print("\n" + "=" * 60)
        print("📋 Test Summary:")
        print(f"   - Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
        print(f"   - File Discovery: {'✅ PASS' if files_ok else '❌ FAIL'}")
        print("=" * 60)
        
        if connection_ok and files_ok:
            print("🎉 All tests passed! Knowledge Graph is ready to use.")
            print("\n💡 You can now:")
            print("   1. Open http://localhost:8000/kg-neo4j in your browser")
            print("   2. Import graph data from ETL output")
            print("   3. Run analysis and queries")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
    else:
        print("\n❌ Connection test failed. Cannot proceed with other tests.")
        print("💡 Make sure Neo4j Docker container is running and accessible.")

if __name__ == "__main__":
    main() 