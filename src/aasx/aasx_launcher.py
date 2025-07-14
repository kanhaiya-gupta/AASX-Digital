#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AASX Package Explorer Launcher
Launches the AASX Package Explorer application for creating and editing AASX files.

The AASX Package Explorer is a desktop application that allows you to:
- Create new AASX (Asset Administration Shell Exchange) files
- Edit existing AASX files with a visual interface
- Add assets, submodels, and properties
- Export AASX files for use in digital twin applications
- Validate AASX files against the AAS specification

This launcher provides an easy way to start the AASX Package Explorer
and access sample files for learning and development.
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AASXExplorerLauncher:
    def __init__(self):
        # Get the project root directory
        self.project_root = Path(__file__).parent.parent.parent
        self.explorer_path = self.project_root / "AasxPackageExplorer" / "AasxPackageExplorer.exe"
        self.content_path = self.project_root / "data" / "aasx-examples"

    def find_explorer_executable(self) -> Optional[str]:
        """Find the AASX Package Explorer executable"""
        if self.explorer_path.exists():
            logger.info(f"Found AASX Package Explorer at: {self.explorer_path}")
            return str(self.explorer_path)
        
        # Try alternative paths
        alternative_paths = [
            self.project_root / "AasxPackageExplorer" / "AasxPackageExplorer",
            Path("C:/Program Files/AASX Package Explorer/AasxPackageExplorer.exe"),
            Path("C:/Program Files (x86)/AASX Package Explorer/AasxPackageExplorer.exe"),
        ]
        
        for path in alternative_paths:
            if path.exists():
                logger.info(f"Found AASX Package Explorer at: {path}")
                return str(path)
        
        logger.warning("AASX Package Explorer executable not found")
        return None

    def is_explorer_running(self) -> Dict[str, Any]:
        """Check if AASX Package Explorer is currently running"""
        try:
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                    
                    # Check if process name matches AASX Explorer patterns
                    if 'aasx' in proc_name and 'explorer' in proc_name:
                        logger.info(f"AASX Package Explorer is already running (PID: {proc_info['pid']})")
                        return {
                            "success": True,
                            "running": True,
                            "pid": proc_info['pid'],
                            "name": proc_info['name']
                        }
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.info("AASX Package Explorer is not running")
            return {
                "success": True,
                "running": False,
                "pid": None,
                "name": None
            }
            
        except ImportError:
            logger.warning("psutil not available, cannot check if AASX Explorer is running")
            return {
                "success": False,
                "running": False,
                "error": "psutil not available"
            }
        except Exception as e:
            logger.error(f"Error checking if AASX Explorer is running: {e}")
            return {
                "success": False,
                "running": False,
                "error": str(e)
            }

    def launch_explorer(self) -> Dict[str, Any]:
        """Launch AASX Package Explorer application"""
        try:
            # Check if already running
            status = self.is_explorer_running()
            if status.get("running", False):
                return {
                    "success": True,
                    "message": "AASX Package Explorer is already running",
                    "pid": status.get("pid")
                }
            
            # Check platform
            if platform.system() != "Windows":
                return {
                    "success": False,
                    "error": "AASX Package Explorer is a Windows application only"
                }
            
            # Find executable
            executable_path = self.find_explorer_executable()
            if not executable_path:
                return {
                    "success": False,
                    "error": "AASX Package Explorer not found. Please ensure it's installed in the AasxPackageExplorer folder."
                }
            
            # Launch the application
            logger.info(f"Launching AASX Package Explorer: {executable_path}")
            
            process = subprocess.Popen(
                [executable_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for the process to start
            import time
            time.sleep(2)
            
            # Check if process started successfully
            if process.poll() is None:  # Process is still running
                return {
                    "success": True,
                    "message": "AASX Package Explorer launched successfully",
                    "executable_path": executable_path,
                    "pid": process.pid
                }
            else:
                # Process exited immediately
                stdout, stderr = process.communicate()
                return {
                    "success": False,
                    "error": f"AASX Package Explorer failed to start. Exit code: {process.returncode}",
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else ""
                }
                
        except Exception as e:
            logger.error(f"Error launching AASX Package Explorer: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_explorer_info(self) -> Dict[str, Any]:
        """Get comprehensive information about AASX Package Explorer"""
        try:
            executable_path = self.find_explorer_executable()
            running_status = self.is_explorer_running()
            
            # Check content directory
            content_info = {
                "exists": self.content_path.exists(),
                "path": str(self.content_path)
            }
            
            if self.content_path.exists():
                sample_files = list(self.content_path.glob("*.aasx"))
                content_info["sample_files"] = [f.name for f in sample_files]
                content_info["sample_count"] = len(sample_files)
            
            return {
                "success": True,
                "executable_found": executable_path is not None,
                "executable_path": executable_path,
                "running": running_status.get("running", False),
                "content_directory": content_info,
                "platform": platform.system(),
                "status": running_status
            }
            
        except Exception as e:
            logger.error(f"Error getting AASX Explorer info: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AASX Package Explorer Launcher")
    parser.add_argument("action", choices=["launch", "status", "info"], 
                       help="Action to perform")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    launcher = AASXExplorerLauncher()
    
    if args.action == "launch":
        result = launcher.launch_explorer()
    elif args.action == "status":
        result = launcher.is_explorer_running()
    elif args.action == "info":
        result = launcher.get_explorer_info()
    
    print(result)
    return 0 if result.get("success", False) else 1

if __name__ == "__main__":
    sys.exit(main()) 