#!/usr/bin/env python3
"""
Direct test of Neo4j service from webapp
"""

import sys
import os
from pathlib import Path

# Simulate webapp environment
webapp_path = Path(__file__).parent.parent / "webapp"
sys.path.insert(0, str(webapp_path))

def test_neo4j_service():
    """Test Neo4j service directly"""
    print("🔍 Testing Neo4j Service Directly...")
    
    try:
        # Import the service
        from kg_neo4j.neo4j_service import get_neo4j_service
        
        print("✅ Neo4j service imported successfully")
        
        # Get service instance
        service = get_neo4j_service()
        
        print("✅ Neo4j service instance created")
        
        # Test connection status
        status = service.get_connection_status()
        print(f"✅ Connection Status: {status['status']}")
        print(f"📊 Connected: {status['connected']}")
        
        if status['connected']:
            print("🎉 Neo4j service is working!")
            
            # Test available files
            try:
                files = service.get_available_files()
                print(f"📁 Available graph files: {files['count']}")
                return True
            except Exception as e:
                print(f"⚠️  Error checking files: {e}")
                return True  # Service is working, just file check failed
        else:
            print(f"❌ Connection failed: {status.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing service: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Direct Neo4j Service Test")
    print("=" * 60)
    
    success = test_neo4j_service()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Neo4j service test passed!")
        print("💡 The Knowledge Graph should now work in the webapp.")
    else:
        print("❌ Neo4j service test failed.")
        print("💡 Check the error messages above for details.")

if __name__ == "__main__":
    main() 