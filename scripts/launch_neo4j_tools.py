#!/usr/bin/env python3
"""
Neo4j Tools Launcher
Launches Neo4j Browser, Desktop, and Admin tools from the framework
"""

import os
import sys
import subprocess
import webbrowser
import platform
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jToolsLauncher:
    """Launcher for Neo4j tools"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.neo4j_config = self._load_neo4j_config()
        
    def _load_neo4j_config(self) -> Dict[str, Any]:
        """Load Neo4j configuration"""
        return {
            'uri': os.getenv('NEO4J_URI', 'neo4j://localhost:7688'),
            'user': os.getenv('NEO4J_USER', 'neo4j'),
            'password': os.getenv('NEO4J_PASSWORD', 'Neo4j123'),
            'browser_port': 7474,
            'admin_port': 7688
        }
    
    def launch_neo4j_browser(self) -> bool:
        """Launch Neo4j Browser in web browser"""
        try:
            # Neo4j Browser URL
            browser_url = f"http://localhost:{self.neo4j_config['browser_port']}"
            
            logger.info(f"Launching Neo4j Browser at: {browser_url}")
            
            # Open in default browser
            webbrowser.open(browser_url)
            
            logger.info("✓ Neo4j Browser launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to launch Neo4j Browser: {e}")
            return False
    
    def launch_neo4j_desktop(self) -> bool:
        """Launch Neo4j Desktop application"""
        try:
            desktop_paths = self._find_neo4j_desktop()
            
            if not desktop_paths:
                logger.warning("Neo4j Desktop not found. Please install it first.")
                logger.info("Download from: https://neo4j.com/download/")
                return False
            
            # Try to launch the first found installation
            for path in desktop_paths:
                try:
                    logger.info(f"Attempting to launch Neo4j Desktop from: {path}")
                    
                    if self.system == "windows":
                        subprocess.Popen([path], shell=True)
                    else:
                        subprocess.Popen([path])
                    
                    logger.info("✓ Neo4j Desktop launched successfully")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Failed to launch from {path}: {e}")
                    continue
            
            logger.error("❌ Failed to launch Neo4j Desktop from any location")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to launch Neo4j Desktop: {e}")
            return False
    
    def _find_neo4j_desktop(self) -> list:
        """Find Neo4j Desktop installation paths"""
        paths = []
        
        if self.system == "windows":
            # Windows paths
            possible_paths = [
                r"C:\Program Files\Neo4j\Neo4j Desktop\Neo4j Desktop.exe",
                r"C:\Program Files (x86)\Neo4j\Neo4j Desktop\Neo4j Desktop.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Neo4j Desktop\Neo4j Desktop.exe"),
                os.path.expanduser(r"~\AppData\Roaming\Neo4j Desktop\Neo4j Desktop.exe")
            ]
            
        elif self.system == "darwin":  # macOS
            possible_paths = [
                "/Applications/Neo4j Desktop.app/Contents/MacOS/Neo4j Desktop",
                "/Applications/Neo4j Desktop.app/Contents/Resources/app/bin/neo4j-desktop"
            ]
            
        else:  # Linux
            possible_paths = [
                "/usr/bin/neo4j-desktop",
                "/usr/local/bin/neo4j-desktop",
                os.path.expanduser("~/.local/bin/neo4j-desktop"),
                os.path.expanduser("~/neo4j-desktop/Neo4j Desktop")
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                paths.append(path)
        
        return paths
    
    def open_neo4j_admin(self) -> bool:
        """Open Neo4j Admin interface"""
        try:
            # Neo4j Admin URL (if available)
            admin_url = f"http://localhost:{self.neo4j_config['admin_port']}"
            
            logger.info(f"Opening Neo4j Admin at: {admin_url}")
            
            # Open in default browser
            webbrowser.open(admin_url)
            
            logger.info("✓ Neo4j Admin opened successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to open Neo4j Admin: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get Neo4j connection information"""
        return {
            "uri": self.neo4j_config['uri'],
            "user": self.neo4j_config['user'],
            "browser_url": f"http://localhost:{self.neo4j_config['browser_port']}",
            "admin_url": f"http://localhost:{self.neo4j_config['admin_port']}",
            "system": self.system,
            "desktop_installed": len(self._find_neo4j_desktop()) > 0
        }
    
    def check_neo4j_status(self) -> Dict[str, Any]:
        """Check Neo4j service status"""
        try:
            import requests
            
            # Check if Neo4j Browser is accessible
            browser_url = f"http://localhost:{self.neo4j_config['browser_port']}"
            response = requests.get(browser_url, timeout=5)
            
            return {
                "browser_accessible": response.status_code == 200,
                "browser_url": browser_url,
                "status": "running" if response.status_code == 200 else "not_accessible"
            }
            
        except Exception as e:
            return {
                "browser_accessible": False,
                "browser_url": f"http://localhost:{self.neo4j_config['browser_port']}",
                "status": "error",
                "error": str(e)
            }

    def start_neo4j_docker(self) -> bool:
        """Start Neo4j using Docker Compose"""
        try:
            import subprocess
            from pathlib import Path
            
            # Get the docker-compose file path
            compose_path = Path(__file__).parent.parent / "docker" / "neo4j" / "docker-compose.yml"
            
            if not compose_path.exists():
                logger.error(f"Docker Compose file not found: {compose_path}")
                return False
            
            logger.info(f"Starting Neo4j with Docker Compose: {compose_path}")
            
            # Change to the directory containing docker-compose.yml
            os.chdir(compose_path.parent)
            
            # Start the services
            result = subprocess.run([
                "docker-compose", "up", "-d"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Neo4j Docker container started successfully")
                return True
            else:
                logger.error(f"❌ Failed to start Neo4j Docker: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Neo4j Docker: {e}")
            return False

    def stop_neo4j_docker(self) -> bool:
        """Stop Neo4j Docker container"""
        try:
            import subprocess
            from pathlib import Path
            
            # Get the docker-compose file path
            compose_path = Path(__file__).parent.parent / "docker" / "neo4j" / "docker-compose.yml"
            
            if not compose_path.exists():
                logger.error(f"Docker Compose file not found: {compose_path}")
                return False
            
            logger.info(f"Stopping Neo4j Docker container: {compose_path}")
            
            # Change to the directory containing docker-compose.yml
            os.chdir(compose_path.parent)
            
            # Stop the services
            result = subprocess.run([
                "docker-compose", "down"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Neo4j Docker container stopped successfully")
                return True
            else:
                logger.error(f"❌ Failed to stop Neo4j Docker: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error stopping Neo4j Docker: {e}")
            return False

    def get_docker_status(self) -> Dict[str, Any]:
        """Get Docker container status"""
        try:
            import subprocess
            
            # Check if Docker is running
            result = subprocess.run([
                "docker", "ps", "--filter", "name=aasx-neo4j", "--format", "{{.Names}}:{{.Status}}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n') if result.stdout.strip() else []
                neo4j_running = any('aasx-neo4j' in container for container in containers)
                
                return {
                    "docker_available": True,
                    "neo4j_container_running": neo4j_running,
                    "containers": containers
                }
            else:
                return {
                    "docker_available": False,
                    "neo4j_container_running": False,
                    "error": "Docker not available"
                }
                
        except Exception as e:
            return {
                "docker_available": False,
                "neo4j_container_running": False,
                "error": str(e)
            }

def main():
    """Main function for command line usage"""
    launcher = Neo4jToolsLauncher()
    
    if len(sys.argv) < 2:
        print("Usage: python launch_neo4j_tools.py [browser|desktop|admin|status|info|docker-start|docker-stop|docker-status]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "browser":
        success = launcher.launch_neo4j_browser()
        sys.exit(0 if success else 1)
        
    elif command == "desktop":
        success = launcher.launch_neo4j_desktop()
        sys.exit(0 if success else 1)
        
    elif command == "admin":
        success = launcher.open_neo4j_admin()
        sys.exit(0 if success else 1)
        
    elif command == "status":
        status = launcher.check_neo4j_status()
        print(f"Neo4j Status: {status}")
        
    elif command == "info":
        info = launcher.get_connection_info()
        print(f"Connection Info: {info}")
        
    elif command == "docker-start":
        success = launcher.start_neo4j_docker()
        sys.exit(0 if success else 1)
        
    elif command == "docker-stop":
        success = launcher.stop_neo4j_docker()
        sys.exit(0 if success else 1)
        
    elif command == "docker-status":
        status = launcher.get_docker_status()
        print(f"Docker Status: {status}")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 