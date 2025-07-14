#!/usr/bin/env python3
"""
Neo4j Desktop Launcher Script
Launches Neo4j Desktop application for the AASX Digital Twin Analytics Framework
"""

import subprocess
import sys
import os
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jDesktopLauncher:
    def __init__(self):
        self.neo4j_paths = [
            # Windows paths
            r"C:\Users\kanha\AppData\Local\Programs\neo4j-desktop\Neo4j Desktop 2.exe",
            r"C:\Program Files\Neo4j Desktop\Neo4j Desktop.exe",
            r"C:\Users\{}\AppData\Local\Programs\neo4j-desktop\Neo4j Desktop.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\AppData\Local\Programs\neo4j-desktop\Neo4j Desktop 2.exe".format(os.getenv('USERNAME', '')),
            # Add more common paths
            r"C:\Program Files (x86)\Neo4j Desktop\Neo4j Desktop.exe",
            r"C:\Users\{}\AppData\Local\Programs\Neo4j Desktop\Neo4j Desktop.exe".format(os.getenv('USERNAME', '')),
        ]

    def find_neo4j_executable(self):
        """Find the Neo4j Desktop executable path"""
        for path in self.neo4j_paths:
            if os.path.exists(path):
                logger.info(f"Found Neo4j Desktop at: {path}")
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(
                ["where", "neo4j-desktop"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                logger.info(f"Found Neo4j Desktop in PATH: {path}")
                return path
        except:
            pass
        
        logger.warning("Neo4j Desktop executable not found")
        return None

    def is_neo4j_running(self):
        """Check if Neo4j Desktop is currently running"""
        try:
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                    
                    # Check if process name matches Neo4j Desktop patterns
                    if 'neo4j' in proc_name and 'desktop' in proc_name:
                        logger.info(f"Neo4j Desktop is already running (PID: {proc_info['pid']})")
                        return True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.info("Neo4j Desktop is not running")
            return False
            
        except ImportError:
            logger.warning("psutil not available, cannot check if Neo4j Desktop is running")
            return False
        except Exception as e:
            logger.error(f"Error checking if Neo4j is running: {e}")
            return False

    def launch_neo4j_desktop(self):
        """Launch Neo4j Desktop application"""
        try:
            # Check if already running
            if self.is_neo4j_running():
                logger.info("Neo4j Desktop is already running")
                return True
            
            # Find executable
            executable_path = self.find_neo4j_executable()
            if not executable_path:
                logger.error("Neo4j Desktop executable not found. Please install Neo4j Desktop from neo4j.com/desktop")
                return False
            
            # Launch the application
            logger.info(f"Launching Neo4j Desktop: {executable_path}")
            
            # Use subprocess.Popen to launch in background
            process = subprocess.Popen(
                [executable_path],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait a moment for the process to start
            time.sleep(2)
            
            # Check if process started successfully
            if process.poll() is None:  # Process is still running
                logger.info("Neo4j Desktop launched successfully")
                return True
            else:
                # Process exited immediately
                stdout, stderr = process.communicate()
                logger.error(f"Neo4j Desktop failed to start. Exit code: {process.returncode}")
                if stderr:
                    logger.error(f"Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error launching Neo4j Desktop: {e}")
            return False

def main():
    """Main function"""
    print("🚀 Neo4j Desktop Launcher")
    print("=" * 50)
    
    launcher = Neo4jDesktopLauncher()
    
    # Check if Neo4j Desktop is already running
    if launcher.is_neo4j_running():
        print("✅ Neo4j Desktop is already running")
        print("\n📋 Connection Information:")
        print("   • Browser URL: http://localhost:7474")
        print("   • Bolt URL: bolt://localhost:7687")
        print("   • Username: neo4j")
        print("   • Password: (set in Desktop)")
        return 0
    
    # Launch Neo4j Desktop
    print("🖥️ Launching Neo4j Desktop...")
    success = launcher.launch_neo4j_desktop()
    
    if success:
        print("✅ Neo4j Desktop launched successfully!")
        print("\n📋 Next Steps:")
        print("   1. Wait for Neo4j Desktop to fully load")
        print("   2. Create a new project or open existing one")
        print("   3. Add a database connection:")
        print("      • URI: bolt://localhost:7688 (for Docker Neo4j)")
        print("      • URI: bolt://localhost:7687 (for local Neo4j)")
        print("      • Username: neo4j")
        print("      • Password: password (for Docker) or your set password")
        print("\n🌐 You can also access Neo4j Browser at:")
        print("   • Docker: http://localhost:7475")
        print("   • Local: http://localhost:7474")
        return 0
    else:
        print("❌ Failed to launch Neo4j Desktop")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Neo4j Desktop is installed")
        print("   2. Download from: https://neo4j.com/desktop")
        print("   3. Check if the executable path is correct")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 