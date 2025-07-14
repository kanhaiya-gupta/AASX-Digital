#!/usr/bin/env python3
"""
Test different Neo4j ports and connection parameters
"""

import os
import sys
from pathlib import Path

def test_neo4j_port(port, password="password"):
    """Test Neo4j connection on specific port"""
    try:
        from neo4j import GraphDatabase
        
        uri = f"neo4j://localhost:{port}"
        user = "neo4j"
        
        print(f"🔌 Testing {uri} with password '{password}'...")
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print(f"✅ SUCCESS: Port {port} works!")
                driver.close()
                return True
            else:
                print(f"❌ FAILED: Port {port} - Invalid response")
                driver.close()
                return False
                
    except Exception as e:
        print(f"❌ FAILED: Port {port} - {str(e)[:50]}...")
        return False

def main():
    """Test different ports and passwords"""
    print("=" * 60)
    print("🔍 Testing Neo4j Docker Ports and Passwords")
    print("=" * 60)
    
    # Test different ports
    ports_to_test = [7687, 7688, 7474, 7475]
    passwords_to_test = ["Neo4j123", "password", "neo4j", "admin", ""]
    
    working_config = None
    
    for port in ports_to_test:
        for password in passwords_to_test:
            if test_neo4j_port(port, password):
                working_config = {"port": port, "password": password}
                break
        if working_config:
            break
    
    print("\n" + "=" * 60)
    if working_config:
        print(f"🎉 Working configuration found!")
        print(f"   Port: {working_config['port']}")
        print(f"   Password: '{working_config['password']}'")
        print(f"   URI: neo4j://localhost:{working_config['port']}")
        print(f"   User: neo4j")
        
        print("\n💡 Update your environment variables:")
        print(f"   export NEO4J_URI=neo4j://localhost:{working_config['port']}")
        print(f"   export NEO4J_PASSWORD={working_config['password']}")
    else:
        print("❌ No working configuration found")
        print("💡 Check if Neo4j container is running properly")

if __name__ == "__main__":
    main() 