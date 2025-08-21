#!/usr/bin/env python3
"""
Neo4j Docker Management Script
Simple command-line tool to manage Neo4j Docker container
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(cmd, timeout=30):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def check_docker_status():
    """Check if Neo4j Docker container is running"""
    print("🔍 Checking Docker status...")
    
    # Check if Docker is available
    result = run_command(['docker', '--version'])
    if not result['success']:
        print("❌ Docker is not available")
        return False
    
    # Check for Neo4j container
    result = run_command(['docker', 'ps', '--filter', 'name=neo4j', '--format', '{{.Names}}\t{{.Status}}\t{{.ID}}'])
    
    if result['success'] and result['stdout'].strip():
        lines = result['stdout'].strip().split('\n')
        for line in lines:
            if 'neo4j' in line.lower():
                parts = line.split('\t')
                if len(parts) >= 3:
                    print(f"✅ Neo4j container is running")
                    print(f"   Name: {parts[0]}")
                    print(f"   Status: {parts[1]}")
                    print(f"   ID: {parts[2]}")
                    return True
    
    # Check if container exists but is stopped
    result = run_command(['docker', 'ps', '-a', '--filter', 'name=neo4j', '--format', '{{.Names}}\t{{.Status}}\t{{.ID}}'])
    
    if result['success'] and result['stdout'].strip():
        lines = result['stdout'].strip().split('\n')
        for line in lines:
            if 'neo4j' in line.lower():
                parts = line.split('\t')
                if len(parts) >= 3:
                    print(f"⏸️  Neo4j container exists but is stopped")
                    print(f"   Name: {parts[0]}")
                    print(f"   Status: {parts[1]}")
                    print(f"   ID: {parts[2]}")
                    return False
    
    print("❌ Neo4j container not found")
    return False

def start_neo4j():
    """Start Neo4j Docker container"""
    print("🚀 Starting Neo4j...")
    
    # Check if container already exists
    result = run_command(['docker', 'ps', '-a', '--filter', 'name=neo4j', '--format', '{{.ID}}'])
    
    if result['success'] and result['stdout'].strip():
        # Container exists, start it
        container_id = result['stdout'].strip()
        print(f"📦 Starting existing container: {container_id}")
        result = run_command(['docker', 'start', container_id])
    else:
        # Create new container
        print("📦 Creating new Neo4j container...")
        result = run_command([
            'docker', 'run', '-d',
            '--name', 'neo4j',
            '-p', '7474:7474',
            '-p', '7687:7687',
            '-e', 'NEO4J_AUTH=neo4j/password',
            '-e', 'NEO4J_PLUGINS=["apoc"]',
            'neo4j:latest'
        ], timeout=60)
    
    if result['success']:
        print("✅ Neo4j started successfully!")
        print("🌐 Browser URL: http://localhost:7474")
        print("🔗 Bolt URL: neo4j://localhost:7687")
        print("👤 Username: neo4j")
        print("🔑 Password: password")
        return True
    else:
        print(f"❌ Failed to start Neo4j: {result['stderr']}")
        return False

def stop_neo4j():
    """Stop Neo4j Docker container"""
    print("🛑 Stopping Neo4j...")
    
    result = run_command(['docker', 'ps', '--filter', 'name=neo4j', '--format', '{{.ID}}'])
    
    if result['success'] and result['stdout'].strip():
        container_id = result['stdout'].strip()
        print(f"📦 Stopping container: {container_id}")
        result = run_command(['docker', 'stop', container_id])
        
        if result['success']:
            print("✅ Neo4j stopped successfully!")
            return True
        else:
            print(f"❌ Failed to stop Neo4j: {result['stderr']}")
            return False
    else:
        print("❌ No running Neo4j container found")
        return False

def restart_neo4j():
    """Restart Neo4j Docker container"""
    print("🔄 Restarting Neo4j...")
    
    if stop_neo4j():
        time.sleep(2)
        return start_neo4j()
    return False

def remove_neo4j():
    """Remove Neo4j Docker container"""
    print("🗑️ Removing Neo4j container...")
    
    # Stop first
    stop_neo4j()
    
    result = run_command(['docker', 'ps', '-a', '--filter', 'name=neo4j', '--format', '{{.ID}}'])
    
    if result['success'] and result['stdout'].strip():
        container_id = result['stdout'].strip()
        print(f"📦 Removing container: {container_id}")
        result = run_command(['docker', 'rm', container_id])
        
        if result['success']:
            print("✅ Neo4j container removed successfully!")
            return True
        else:
            print(f"❌ Failed to remove Neo4j: {result['stderr']}")
            return False
    else:
        print("❌ No Neo4j container found")
        return False

def show_logs():
    """Show Neo4j container logs"""
    print("📋 Showing Neo4j logs...")
    
    result = run_command(['docker', 'ps', '--filter', 'name=neo4j', '--format', '{{.ID}}'])
    
    if result['success'] and result['stdout'].strip():
        container_id = result['stdout'].strip()
        print(f"📦 Container ID: {container_id}")
        print("=" * 50)
        
        # Show logs with follow
        try:
            subprocess.run(['docker', 'logs', '-f', container_id])
        except KeyboardInterrupt:
            print("\n📋 Logs stopped")
    else:
        print("❌ No running Neo4j container found")

def check_browser():
    """Check if Neo4j Browser is accessible"""
    print("🌐 Checking Neo4j Browser accessibility...")
    
    try:
        import requests
        response = requests.get('http://localhost:7474', timeout=5)
        if response.status_code == 200:
            print("✅ Neo4j Browser is accessible at http://localhost:7474")
            return True
        else:
            print(f"❌ Neo4j Browser returned status code: {response.status_code}")
            return False
    except ImportError:
        print("⚠️  requests library not available, skipping browser check")
        return False
    except Exception as e:
        print(f"❌ Neo4j Browser is not accessible: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Neo4j Docker Management Script")
        print("Usage:")
        print("  python manage_neo4j.py <command>")
        print("")
        print("Commands:")
        print("  status    - Check Neo4j container status")
        print("  start     - Start Neo4j container")
        print("  stop      - Stop Neo4j container")
        print("  restart   - Restart Neo4j container")
        print("  remove    - Remove Neo4j container")
        print("  logs      - Show Neo4j logs")
        print("  browser   - Check browser accessibility")
        print("  help      - Show this help message")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        check_docker_status()
    elif command == 'start':
        start_neo4j()
    elif command == 'stop':
        stop_neo4j()
    elif command == 'restart':
        restart_neo4j()
    elif command == 'remove':
        remove_neo4j()
    elif command == 'logs':
        show_logs()
    elif command == 'browser':
        check_browser()
    elif command == 'help':
        main()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python manage_neo4j.py help' for usage information")

if __name__ == "__main__":
    main() 