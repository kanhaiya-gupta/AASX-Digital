#!/usr/bin/env python3
"""
Neo4j Desktop Launcher Script
Handles launching and managing Neo4j Desktop application
"""

import subprocess
import psutil
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

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
        
        self.browser_url = "http://localhost:7474"
        self.bolt_url = "bolt://localhost:7687"
        self.process_name_patterns = [
            "neo4j desktop",
            "neo4j-desktop",
            "Neo4j Desktop",
            "Neo4jDesktop"
        ]

    def find_neo4j_executable(self) -> Optional[str]:
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

    def is_neo4j_running(self) -> Dict[str, Any]:
        """Check if Neo4j Desktop application is running"""
        try:
            # Check if any Neo4j Desktop process is running
            neo4j_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                    
                    # Check if process name matches any pattern
                    is_neo4j = any(pattern.lower() in proc_name for pattern in self.process_name_patterns)
                    
                    if is_neo4j:
                        neo4j_processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'exe': proc_info['exe']
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            is_running = len(neo4j_processes) > 0
            
            return {
                "success": True,
                "running": is_running,
                "processes": neo4j_processes,
                "count": len(neo4j_processes)
            }
            
        except Exception as e:
            logger.error(f"Error checking if Neo4j is running: {e}")
            return {
                "success": False,
                "error": str(e),
                "running": False,
                "processes": []
            }

    def launch_neo4j_desktop(self) -> Dict[str, Any]:
        """Launch Neo4j Desktop application"""
        try:
            # Check if already running
            status = self.is_neo4j_running()
            if status["running"]:
                return {
                    "success": True,
                    "message": "Neo4j Desktop is already running",
                    "processes": status["processes"]
                }
            
            # Find executable
            executable_path = self.find_neo4j_executable()
            if not executable_path:
                return {
                    "success": False,
                    "error": "Neo4j Desktop executable not found. Please install Neo4j Desktop from neo4j.com/desktop"
                }
            
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
                return {
                    "success": True,
                    "message": "Neo4j Desktop launched successfully",
                    "executable_path": executable_path,
                    "pid": process.pid
                }
            else:
                # Process exited immediately
                stdout, stderr = process.communicate()
                return {
                    "success": False,
                    "error": f"Neo4j Desktop failed to start. Exit code: {process.returncode}",
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else ""
                }
                
        except Exception as e:
            logger.error(f"Error launching Neo4j Desktop: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def kill_neo4j_desktop(self) -> Dict[str, Any]:
        """Kill all running Neo4j Desktop processes"""
        try:
            status = self.is_neo4j_running()
            if not status["running"]:
                return {
                    "success": True,
                    "message": "No Neo4j Desktop processes found"
                }
            
            killed_processes = []
            for proc_info in status["processes"]:
                try:
                    process = psutil.Process(proc_info["pid"])
                    process.terminate()
                    killed_processes.append(proc_info["pid"])
                    logger.info(f"Terminated Neo4j Desktop process: {proc_info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.warning(f"Could not terminate process {proc_info['pid']}: {e}")
            
            return {
                "success": True,
                "message": f"Terminated {len(killed_processes)} Neo4j Desktop processes",
                "killed_pids": killed_processes
            }
            
        except Exception as e:
            logger.error(f"Error killing Neo4j Desktop: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_neo4j_info(self) -> Dict[str, Any]:
        """Get comprehensive information about Neo4j Desktop"""
        try:
            executable_path = self.find_neo4j_executable()
            running_status = self.is_neo4j_running()
            
            return {
                "success": True,
                "executable_found": executable_path is not None,
                "executable_path": executable_path,
                "running": running_status.get("running", False),
                "processes": running_status.get("processes", []),
                "browser_url": self.browser_url,
                "bolt_url": self.bolt_url,
                "status": running_status
            }
            
        except Exception as e:
            logger.error(f"Error getting Neo4j info: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Neo4j Desktop Launcher")
    parser.add_argument("action", choices=["launch", "status", "kill", "info"], 
                       help="Action to perform")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    launcher = Neo4jDesktopLauncher()
    
    if args.action == "launch":
        result = launcher.launch_neo4j_desktop()
    elif args.action == "status":
        result = launcher.is_neo4j_running()
    elif args.action == "kill":
        result = launcher.kill_neo4j_desktop()
    elif args.action == "info":
        result = launcher.get_neo4j_info()
    
    print(result)
    return 0 if result.get("success", False) else 1

if __name__ == "__main__":
    sys.exit(main()) 