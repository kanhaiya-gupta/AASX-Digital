#!/usr/bin/env python3
"""
Simple Neo4j Docker Connection Test
Tests direct connection to Neo4j without src dependencies
"""

import os
import sys
from pathlib import Path

def test_neo4j_connection_direct():
    """Test Neo4j connection directly using neo4j driver"""
    print("🔍 Testing Neo4j Docker Connection Directly...")
    
    try:
        # Try to import neo4j driver
        try:
            from neo4j import GraphDatabase
        except ImportError:
            print("❌ Neo4j driver not installed. Installing...")
            os.system("pip install neo4j")
            from neo4j import GraphDatabase
        
        # Docker Neo4j connection settings
        uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7688')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', 'Neo4j123')
        
        print(f"🔌 Connecting to: {uri}")
        print(f"👤 User: {user}")
        
        # Test connection
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Verify connection
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print("✅ Neo4j Docker connection successful!")
                
                # Test basic queries
                print("\n🔍 Testing basic queries...")
                
                # Get database info
                result = session.run("CALL dbms.components() YIELD name, versions, edition")
                info = result.single()
                if info:
                    print(f"📊 Database: {info['name']}")
                    print(f"📋 Version: {info['versions'][0] if info['versions'] else 'Unknown'}")
                    print(f"🏷️  Edition: {info['edition']}")
                
                # Get node count
                result = session.run("MATCH (n) RETURN count(n) as node_count")
                count = result.single()
                if count:
                    print(f"🔢 Total nodes: {count['node_count']}")
                
                # Get relationship count
                result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                rel_count = result.single()
                if rel_count:
                    print(f"🔗 Total relationships: {rel_count['rel_count']}")
                
                # Get database labels
                result = session.run("CALL db.labels() YIELD label RETURN collect(label) as labels")
                labels = result.single()
                if labels and labels['labels']:
                    print(f"🏷️  Labels: {', '.join(labels['labels'][:5])}{'...' if len(labels['labels']) > 5 else ''}")
                else:
                    print("🏷️  Labels: None (empty database)")
                
                driver.close()
                return True
            else:
                print("❌ Connection test failed")
                driver.close()
                return False
                
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def test_etl_output_files():
    """Test if ETL output files exist"""
    print("\n📁 Testing ETL Output Files...")
    
    etl_output_dir = Path("output/etl_results/")
    
    if not etl_output_dir.exists():
        print(f"❌ ETL output directory not found: {etl_output_dir}")
        return False
    
    # Find graph files
    graph_files = list(etl_output_dir.rglob("*_graph.json"))
    
    print(f"📁 Found {len(graph_files)} graph files:")
    for file in graph_files:
        print(f"   - {file}")
    
    if len(graph_files) > 0:
        print("✅ ETL output files found!")
        return True
    else:
        print("⚠️  No graph files found in ETL output")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Simple Neo4j Docker Connection Test")
    print("=" * 60)
    
    # Test direct connection
    connection_ok = test_neo4j_connection_direct()
    
    # Test ETL files
    files_ok = test_etl_output_files()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   - Neo4j Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"   - ETL Files: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print("=" * 60)
    
    if connection_ok and files_ok:
        print("🎉 All tests passed! Neo4j Docker is working correctly.")
        print("\n💡 Next steps:")
        print("   1. The src modules need to be created/fixed")
        print("   2. Then the Knowledge Graph frontend will work")
        print("   3. You can access the webapp at http://localhost:8000")
    elif connection_ok:
        print("⚠️  Neo4j is working but ETL files are missing.")
        print("💡 Run the ETL pipeline first to generate graph data.")
    else:
        print("❌ Neo4j connection failed.")
        print("💡 Make sure Neo4j Docker container is running:")
        print("   docker ps | grep neo4j")

if __name__ == "__main__":
    main() 