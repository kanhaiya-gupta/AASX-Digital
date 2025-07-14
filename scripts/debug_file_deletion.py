#!/usr/bin/env python3
"""
Debug File Deletion Script
Checks the current in-memory state and forces a save to fix files.json issues.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_file_deletion():
    """Debug file deletion issues"""
    
    try:
        # Import the backend modules
        from webapp.aasx.routes import PROJECTS_DB, FILES_DB, save_project_to_filesystem, save_all_projects_to_filesystem
        
        print("🔍 Debugging file deletion issue...")
        print(f"📊 Current in-memory state:")
        print(f"   - Projects: {len(PROJECTS_DB)}")
        print(f"   - Files: {len(FILES_DB)}")
        
        # Check specific project
        project_id = "bbeac1aa-1055-4542-8704-7f837bbb3e15"
        if project_id in PROJECTS_DB:
            project = PROJECTS_DB[project_id]
            print(f"\n📁 Project: {project['name']}")
            print(f"   - File count (in memory): {project['file_count']}")
            print(f"   - Total size (in memory): {project['total_size']}")
            
            # Get files for this project
            project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
            print(f"   - Files in memory: {len(project_files)}")
            
            for file_info in project_files:
                print(f"     - {file_info['original_filename']} (ID: {file_info['id']})")
        
        # Check files.json on disk
        projects_dir = Path("data/projects")
        files_json = projects_dir / project_id / "files.json"
        
        if files_json.exists():
            with open(files_json, 'r') as f:
                disk_files = json.load(f)
            
            print(f"\n📄 Files on disk (files.json): {len(disk_files)}")
            for file_info in disk_files:
                print(f"   - {file_info['original_filename']} (ID: {file_info['id']})")
        
        # Check if there's a mismatch
        if len(project_files) != len(disk_files):
            print(f"\n⚠️  MISMATCH DETECTED!")
            print(f"   - In memory: {len(project_files)} files")
            print(f"   - On disk: {len(disk_files)} files")
            
            # Force save to fix the mismatch
            print(f"\n🔧 Forcing save to fix mismatch...")
            success = save_project_to_filesystem(project_id)
            
            if success:
                print(f"✅ Save successful!")
                
                # Check again
                with open(files_json, 'r') as f:
                    updated_disk_files = json.load(f)
                
                print(f"📄 Files on disk after save: {len(updated_disk_files)}")
                for file_info in updated_disk_files:
                    print(f"   - {file_info['original_filename']} (ID: {file_info['id']})")
            else:
                print(f"❌ Save failed!")
        else:
            print(f"\n✅ No mismatch detected. Files in memory match files on disk.")
        
        # Also save all projects to ensure consistency
        print(f"\n🔧 Saving all projects to ensure consistency...")
        save_all_projects_to_filesystem()
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this script from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 Debug File Deletion Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("data/projects").exists():
        print("❌ Error: data/projects directory not found!")
        print("Please run this script from the project root directory")
        return
    
    # Debug file deletion
    success = debug_file_deletion()
    
    if success:
        print("\n🎉 Debugging completed!")
        print("Check the output above to see if the files.json issue was resolved.")
    else:
        print("\n❌ Debugging failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main() 