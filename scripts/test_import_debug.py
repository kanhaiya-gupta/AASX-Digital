#!/usr/bin/env python3
"""
Debug script to test import paths
"""

import sys
from pathlib import Path

def test_imports():
    """Test different import approaches"""
    print("🔍 Testing Import Paths...")
    
    # Add src to path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.append(str(src_path))
    
    print(f"📁 Backend path: {src_path}")
    print(f"📁 Backend exists: {src_path.exists()}")
    
    # List src contents
    if src_path.exists():
        print("📁 Backend contents:")
        for item in src_path.iterdir():
            print(f"   - {item.name}")
    
    # Test import kg_neo4j
    try:
        print("\n🔍 Testing import kg_neo4j...")
        import kg_neo4j
        print("✅ kg_neo4j imported successfully")
        print(f"📁 kg_neo4j location: {kg_neo4j.__file__}")
        
        # Test import specific modules
        try:
            from kg_neo4j import neo4j_manager
            print("✅ neo4j_manager imported successfully")
        except ImportError as e:
            print(f"❌ neo4j_manager import failed: {e}")
        
        try:
            from kg_neo4j import graph_analyzer
            print("✅ graph_analyzer imported successfully")
        except ImportError as e:
            print(f"❌ graph_analyzer import failed: {e}")
        
        # Test direct import
        try:
            from kg_neo4j.neo4j_manager import Neo4jManager
            print("✅ Neo4jManager class imported successfully")
        except ImportError as e:
            print(f"❌ Neo4jManager import failed: {e}")
        
        try:
            from kg_neo4j.graph_analyzer import AASXGraphAnalyzer
            print("✅ AASXGraphAnalyzer class imported successfully")
        except ImportError as e:
            print(f"❌ AASXGraphAnalyzer import failed: {e}")
        
    except ImportError as e:
        print(f"❌ kg_neo4j import failed: {e}")
    
    # Test sys.path
    print(f"\n📁 Python path:")
    for i, path in enumerate(sys.path[:5]):  # Show first 5 paths
        print(f"   {i}: {path}")

if __name__ == "__main__":
    test_imports() 