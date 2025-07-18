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
from pathlib import Path
from typing import Optional, Dict, Any

def get_project_root() -> Path:
    """Get the project root directory"""
    # Start from the current file location
    current_file = Path(__file__)
    
    # Navigate up to find the project root (where we have data/, scripts/, etc.)
    # src/aasx/launch_explorer.py -> src/aasx/ -> src/ -> project_root
    project_root = current_file.parent.parent.parent
    
    # Verify this is the project root by checking for key directories
    if not (project_root / "data").exists() or not (project_root / "scripts").exists():
        # Try alternative path calculation
        # If we're running from webapp, we need to go up one more level
        project_root = current_file.parent.parent.parent.parent
        if not (project_root / "data").exists():
            # Fallback: use current working directory
            project_root = Path.cwd()
    
    return project_root

def get_explorer_path() -> Path:
    """Get the path to the AASX Package Explorer executable"""
    project_root = get_project_root()
    return project_root / "AasxPackageExplorer" / "AasxPackageExplorer.exe"

def get_content_path() -> Path:
    """Get the path to the AASX content directory"""
    project_root = get_project_root()
    return project_root / "data" / "aasx-examples"

def check_explorer_status() -> Dict[str, Any]:
    """Check the status of the AASX Package Explorer installation"""
    explorer_path = get_explorer_path()
    content_path = get_content_path()
    
    status = {
        "explorer_found": explorer_path.exists(),
        "explorer_path": str(explorer_path),
        "content_found": content_path.exists(),
        "content_path": str(content_path),
        "platform": platform.system(),
        "is_windows": platform.system() == "Windows"
    }
    
    # Check for sample files
    if content_path.exists():
        sample_files = list(content_path.glob("*.aasx"))
        status["sample_files_count"] = len(sample_files)
        status["sample_files"] = [f.name for f in sample_files[:10]]  # First 10 files
    else:
        status["sample_files_count"] = 0
        status["sample_files"] = []
    
    return status

def launch_explorer(silent: bool = False) -> Dict[str, Any]:
    """
    Launch the AASX Package Explorer
    
    Args:
        silent: If True, don't print status messages (for webapp use)
    
    Returns:
        Dict with launch result information
    """
    result = {
        "success": False,
        "message": "",
        "explorer_path": "",
        "content_path": "",
        "error": None
    }
    
    # Get paths
    explorer_path = get_explorer_path()
    content_path = get_content_path()
    
    result["explorer_path"] = str(explorer_path)
    result["content_path"] = str(content_path)
    
    if not silent:
        print("🚀 AASX Package Explorer Launcher")
        print("=" * 60)
        print()
        print("📋 What is AASX Package Explorer?")
        print("   The AASX Package Explorer is a desktop application for creating")
        print("   and editing AASX (Asset Administration Shell Exchange) files.")
        print("   It provides a visual interface for building digital twin data.")
        print()
        print("🔧 Key Features:")
        print("   • Create new AASX files from scratch")
        print("   • Edit existing AASX files with visual tools")
        print("   • Add assets, submodels, and properties")
        print("   • Import/export AASX files")
        print("   • Validate files against AAS specification")
        print("   • Preview and test AASX packages")
        print()
        print(f"📁 Project root: {get_project_root()}")
        print(f"🔍 Explorer path: {explorer_path}")
        print(f"📂 Content path: {content_path}")
        print()
    
    # Check if explorer exists
    if not explorer_path.exists():
        error_msg = f"AASX Package Explorer not found at {explorer_path}"
        result["message"] = error_msg
        result["error"] = "explorer_not_found"
        
        if not silent:
            print("❌ Error: AASX Package Explorer not found!")
            print(f"   Expected location: {explorer_path}")
            print()
            print("💡 Please ensure:")
            print("   1. The AasxPackageExplorer folder exists in the project root")
            print("   2. AasxPackageExplorer.exe is present in the folder")
            print("   3. Windows Desktop Runtime 3.1 is installed")
            print()
            print("🔗 Download AASX Package Explorer:")
            print("   https://github.com/admin-shell-io/aasx-package-explorer")
        
        return result
    
    if not silent:
        print("✅ AASX Package Explorer found!")
    
    # Check content directory
    if content_path.exists():
        if not silent:
            print("✅ Sample content directory found!")
        sample_files = list(content_path.glob("*.aasx"))
        if sample_files:
            if not silent:
                print(f"📄 Found {len(sample_files)} sample AASX files:")
                for file in sample_files[:5]:  # Show first 5
                    print(f"   • {file.name}")
                if len(sample_files) > 5:
                    print(f"   • ... and {len(sample_files) - 5} more")
        else:
            if not silent:
                print("📄 No sample AASX files found in content directory")
    else:
        if not silent:
            print("⚠️  Sample content directory not found")
    
    if not silent:
        print()
    
    # Check platform
    if platform.system() != "Windows":
        error_msg = "AASX Package Explorer is a Windows application only"
        result["message"] = error_msg
        result["error"] = "platform_not_supported"
        
        if not silent:
            print("⚠️  Warning: This launcher is designed for Windows")
            print("   The AASX Package Explorer is a Windows application")
            print("   For other platforms, please use the web-based version")
        
        return result
    
    # Launch the explorer
    try:
        if not silent:
            print("🚀 Launching AASX Package Explorer...")
        
        process = subprocess.Popen([str(explorer_path)])
        
        success_msg = "AASX Package Explorer launched successfully!"
        result["success"] = True
        result["message"] = success_msg
        result["pid"] = process.pid
        
        if not silent:
            print("✅ AASX Package Explorer launched successfully!")
            print()
            print("💡 How to use AASX Package Explorer:")
            print("   1. File > Open: Load existing AASX files")
            print("   2. File > New: Create new AASX packages")
            print("   3. Add assets, submodels, and properties")
            print("   4. Save your work as .aasx files")
            print("   5. Use the files in the AASX Digital Twin Analytics Framework")
            print()
            print("📂 Sample files location:")
            print(f"   {content_path}")
            print()
            print("🔄 Integration with Framework:")
            print("   • Place your AASX files in the data/aasx-examples directory")
            print("   • Use the web interface at http://localhost:8000/aasx")
            print("   • Process files through the ETL pipeline")
            print("   • Analyze data in the Knowledge Graph")
            print()
            print("⏹️  Press Ctrl+C to close this launcher")
        
        return result
        
    except Exception as e:
        error_msg = f"Error launching explorer: {e}"
        result["message"] = error_msg
        result["error"] = "launch_failed"
        result["exception"] = str(e)
        
        if not silent:
            print(f"❌ Error launching explorer: {e}")
            print()
            print("💡 Troubleshooting:")
            print("   1. Ensure Windows Desktop Runtime 3.1 is installed")
            print("   2. Try running as administrator")
            print("   3. Check Windows Defender/antivirus settings")
            print("   4. Verify the executable file is not corrupted")
            print()
            print("🔗 Download Windows Desktop Runtime:")
            print("   https://dotnet.microsoft.com/download/dotnet/3.1")
        
        return result

def main():
    """Main launcher function for command-line use"""
    result = launch_explorer(silent=False)
    return 0 if result["success"] else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        if exit_code == 0:
            # Keep the script running to show the help information
            try:
                input("\nPress Enter to close this launcher...")
            except KeyboardInterrupt:
                pass
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Launcher closed by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 