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

def main():
    """Main launcher function"""
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
    
    # Get the project root directory (parent of scripts folder)
    project_root = Path(__file__).parent.parent
    explorer_path = project_root / "AasxPackageExplorer" / "AasxPackageExplorer.exe"
    content_path = project_root / "data" / "aasx-examples"
    
    print(f"📁 Project root: {project_root}")
    print(f"🔍 Explorer path: {explorer_path}")
    print(f"📂 Content path: {content_path}")
    print()
    
    # Check if explorer exists
    if not explorer_path.exists():
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
        return 1
    
    print("✅ AASX Package Explorer found!")
    
    # Check content directory
    if content_path.exists():
        print("✅ Sample content directory found!")
        sample_files = list(content_path.glob("*.aasx"))
        if sample_files:
            print(f"📄 Found {len(sample_files)} sample AASX files:")
            for file in sample_files[:5]:  # Show first 5
                print(f"   • {file.name}")
            if len(sample_files) > 5:
                print(f"   • ... and {len(sample_files) - 5} more")
        else:
            print("📄 No sample AASX files found in content directory")
    else:
        print("⚠️  Sample content directory not found")
    
    print()
    
    # Check platform
    if platform.system() != "Windows":
        print("⚠️  Warning: This launcher is designed for Windows")
        print("   The AASX Package Explorer is a Windows application")
        print("   For other platforms, please use the web-based version")
        return 1
    
    # Launch the explorer
    try:
        print("🚀 Launching AASX Package Explorer...")
        subprocess.Popen([str(explorer_path)])
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
        return 0
        
    except Exception as e:
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
        return 1

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