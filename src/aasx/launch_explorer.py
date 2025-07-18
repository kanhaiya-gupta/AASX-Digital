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

Supports both native Windows and Wine (Linux/macOS) environments.
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

def check_wine_availability() -> bool:
    """Check if Wine is available for running Windows applications"""
    try:
        result = subprocess.run(["wine", "--version"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_x11_setup() -> Dict[str, Any]:
    """Check X11 setup for GUI applications on Windows"""
    x11_status = {
        "vcxsrv_installed": False,
        "vcxsrv_running": False,
        "display_set": False,
        "xauthority_set": False,
        "setup_needed": True
    }
    
    # Check if VcXsrv is installed
    vcxsrv_path = Path("C:/Program Files/VcXsrv/vcxsrv.exe")
    x11_status["vcxsrv_installed"] = vcxsrv_path.exists()
    
    # Check if VcXsrv is running
    try:
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq vcxsrv.exe"], 
                              capture_output=True, text=True, timeout=10)
        x11_status["vcxsrv_running"] = "vcxsrv.exe" in result.stdout
    except:
        x11_status["vcxsrv_running"] = False
    
    # Check environment variables
    x11_status["display_set"] = bool(os.environ.get('DISPLAY'))
    x11_status["xauthority_set"] = bool(os.environ.get('XAUTHORITY'))
    
    # Determine if setup is needed
    x11_status["setup_needed"] = not (x11_status["vcxsrv_installed"] and 
                                     x11_status["vcxsrv_running"] and 
                                     x11_status["display_set"])
    
    return x11_status

def setup_x11_windows() -> Dict[str, Any]:
    """Set up X11 forwarding for Windows GUI applications"""
    setup_result = {
        "success": False,
        "message": "",
        "vcxsrv_started": False,
        "environment_set": False
    }
    
    # Check if VcXsrv is installed
    vcxsrv_path = Path("C:/Program Files/VcXsrv/vcxsrv.exe")
    if not vcxsrv_path.exists():
        setup_result["message"] = "VcXsrv not installed. Please install from https://sourceforge.net/projects/vcxsrv/"
        return setup_result
    
    # Set environment variables
    os.environ['DISPLAY'] = 'localhost:0.0'
    os.environ['XAUTHORITY'] = str(Path.home() / '.Xauthority')
    setup_result["environment_set"] = True
    
    # Create .Xauthority file if it doesn't exist
    xauthority_path = Path.home() / '.Xauthority'
    if not xauthority_path.exists():
        xauthority_path.touch()
    
    # Start VcXsrv if not running
    try:
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq vcxsrv.exe"], 
                              capture_output=True, text=True, timeout=10)
        if "vcxsrv.exe" not in result.stdout:
            subprocess.Popen([str(vcxsrv_path), ":0", "-multiwindow", "-clipboard", "-wgl", "-ac"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            setup_result["vcxsrv_started"] = True
        else:
            setup_result["vcxsrv_started"] = True  # Already running
    except Exception as e:
        setup_result["message"] = f"Failed to start VcXsrv: {e}"
        return setup_result
    
    setup_result["success"] = True
    setup_result["message"] = "X11 setup completed successfully"
    return setup_result

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
        "is_windows": platform.system() == "Windows",
        "wine_available": check_wine_availability()
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
        "error": None,
        "method": None
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
            print("   3. Windows Desktop Runtime 3.1 is installed (for Windows)")
            print("   4. Wine is installed (for Linux/macOS)")
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
    
    # Determine launch method based on platform
    current_platform = platform.system()
    
    if current_platform == "Windows":
        # Native Windows launch
        result["method"] = "native_windows"
        return launch_native_windows(explorer_path, silent, result)
    else:
        # Linux/macOS with Wine
        result["method"] = "wine"
        return launch_with_wine(explorer_path, silent, result)

def launch_native_windows(explorer_path: Path, silent: bool, result: Dict[str, Any]) -> Dict[str, Any]:
    """Launch AASX Package Explorer natively on Windows"""
    try:
        if not silent:
            print("🚀 Launching AASX Package Explorer (Native Windows)...")
        
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
            print(f"   {get_content_path()}")
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

def launch_with_wine(explorer_path: Path, silent: bool, result: Dict[str, Any]) -> Dict[str, Any]:
    """Launch AASX Package Explorer using Wine on Linux/macOS or Windows with X11"""
    
    # Check if Wine is available
    if not check_wine_availability():
        error_msg = "Wine is not available for running Windows applications"
        result["message"] = error_msg
        result["error"] = "wine_not_available"
        
        if not silent:
            print("❌ Error: Wine is not available!")
            print()
            print("💡 To run AASX Package Explorer on Linux/macOS:")
            print("   1. Install Wine: sudo apt-get install wine64 (Ubuntu/Debian)")
            print("   2. Install Wine: brew install wine (macOS)")
            print("   3. Or use the Docker container with Wine pre-installed")
            print()
            print("🔗 Alternative: Use the web-based AASX processing interface")
            print("   Available at: http://localhost:8000/aasx")
        
        return result
    
    # Check if we're on Windows and need X11 setup
    if platform.system() == "Windows":
        x11_status = check_x11_setup()
        if x11_status["setup_needed"]:
            if not silent:
                print("🔧 Setting up X11 forwarding for GUI...")
            
            setup_result = setup_x11_windows()
            if not setup_result["success"]:
                result["message"] = f"X11 setup failed: {setup_result['message']}"
                result["error"] = "x11_setup_failed"
                return result
            
            if not silent:
                print("✅ X11 setup completed!")
    
    try:
        if not silent:
            print("🚀 Launching AASX Package Explorer (Wine)...")
            print("   This may take a moment to initialize Wine...")
        
        # Set Wine environment variables
        env = os.environ.copy()
        env['WINEARCH'] = 'win64'
        env['WINEPREFIX'] = str(get_project_root() / '.wine')
        
        # Use proper display for X11 forwarding
        if platform.system() == "Windows":
            env['DISPLAY'] = 'localhost:0.0'
            env['XAUTHORITY'] = str(Path.home() / '.Xauthority')
        else:
            env['DISPLAY'] = ':99'
        
        # Launch with Wine
        process = subprocess.Popen(
            ["wine", str(explorer_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        success_msg = "AASX Package Explorer launched successfully with Wine!"
        result["success"] = True
        result["message"] = success_msg
        result["pid"] = process.pid
        
        if not silent:
            print("✅ AASX Package Explorer launched successfully with Wine!")
            print()
            print("💡 Wine Integration Notes:")
            print("   • First launch may take longer as Wine initializes")
            print("   • GUI may appear in a separate window")
            print("   • Performance may be slower than native Windows")
            print("   • Some advanced features may have limitations")
            print()
            print("💡 How to use AASX Package Explorer:")
            print("   1. File > Open: Load existing AASX files")
            print("   2. File > New: Create new AASX packages")
            print("   3. Add assets, submodels, and properties")
            print("   4. Save your work as .aasx files")
            print("   5. Use the files in the AASX Digital Twin Analytics Framework")
            print()
            print("📂 Sample files location:")
            print(f"   {get_content_path()}")
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
        error_msg = f"Error launching explorer with Wine: {e}"
        result["message"] = error_msg
        result["error"] = "wine_launch_failed"
        result["exception"] = str(e)
        
        if not silent:
            print(f"❌ Error launching explorer with Wine: {e}")
            print()
            print("💡 Troubleshooting Wine:")
            print("   1. Ensure Wine is properly installed")
            print("   2. Check Wine configuration: winecfg")
            print("   3. Verify Wine can run other Windows applications")
            print("   4. Check system display settings")
            print("   5. Try running with: WINEDEBUG=+all wine AasxPackageExplorer.exe")
            print()
            print("🔗 Alternative: Use the web-based AASX processing interface")
            print("   Available at: http://localhost:8000/aasx")
        
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
                input("\nPress Enter to exit...")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0) 