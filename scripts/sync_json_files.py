#!/usr/bin/env python3
"""
Sync JSON Files Script
Synchronizes all JSON files with the current in-memory state of projects and files.
This ensures that the filesystem JSON files match the current state after any operations.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def sync_json_files():
    """Synchronize all JSON files with current in-memory state"""
    
    try:
        # Import the save function from the webapp
        from webapp.aasx.routes import save_all_projects_to_filesystem, PROJECTS_DB, FILES_DB
        
        print("🔄 Starting JSON file synchronization...")
        print(f"📊 Current in-memory state:")
        print(f"   - Projects: {len(PROJECTS_DB)}")
        print(f"   - Files: {len(FILES_DB)}")
        
        # Save all projects and files to filesystem
        success = save_all_projects_to_filesystem()
        
        if success:
            print("✅ Successfully synchronized JSON files!")
            
            # Verify the synchronization
            projects_dir = Path("data/projects")
            summary_file = projects_dir / "projects_summary.json"
            
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
                
                print(f"📄 Updated projects_summary.json:")
                print(f"   - Total projects: {summary.get('total_projects', 0)}")
                print(f"   - Total files: {summary.get('total_files', 0)}")
                print(f"   - Total size: {summary.get('total_size', 0)} bytes")
                print(f"   - Last updated: {summary.get('last_updated', 'N/A')}")
            
            # Show individual project details
            print("\n📁 Individual project details:")
            for project_id, project in PROJECTS_DB.items():
                project_dir = projects_dir / project_id
                project_json = project_dir / "project.json"
                files_json = project_dir / "files.json"
                
                print(f"   📂 {project['name']} ({project_id})")
                print(f"      - Files: {project['file_count']}")
                print(f"      - Size: {project['total_size']} bytes")
                print(f"      - Project JSON: {'✅' if project_json.exists() else '❌'}")
                print(f"      - Files JSON: {'✅' if files_json.exists() else '❌'}")
                
                # Count actual files in directory
                actual_files = list(project_dir.glob("*.aasx"))
                print(f"      - Actual AASX files: {len(actual_files)}")
                
        else:
            print("❌ Failed to synchronize JSON files!")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this script from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error during synchronization: {e}")
        return False

def verify_file_integrity():
    """Verify that all files referenced in JSON actually exist on disk"""
    
    print("\n🔍 Verifying file integrity...")
    
    try:
        projects_dir = Path("data/projects")
        missing_files = []
        orphaned_files = []
        
        # Check all project directories
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
                
            project_id = project_dir.name
            files_json = project_dir / "files.json"
            
            if files_json.exists():
                with open(files_json, 'r') as f:
                    files_data = json.load(f)
                
                # Check if referenced files exist
                for file_info in files_data:
                    file_path = Path(file_info['filepath'])
                    if not file_path.exists():
                        missing_files.append({
                            'project': project_id,
                            'file': file_info['original_filename'],
                            'path': str(file_path)
                        })
            
            # Check for orphaned AASX files (not in JSON)
            json_files = set()
            if files_json.exists():
                with open(files_json, 'r') as f:
                    files_data = json.load(f)
                    json_files = {f['filename'] for f in files_data}
            
            actual_files = {f.name for f in project_dir.glob("*.aasx")}
            orphaned = actual_files - json_files
            
            for orphaned_file in orphaned:
                orphaned_files.append({
                    'project': project_id,
                    'file': orphaned_file,
                    'path': str(project_dir / orphaned_file)
                })
        
        # Report results
        if missing_files:
            print(f"⚠️  Found {len(missing_files)} missing files:")
            for missing in missing_files:
                print(f"   - {missing['project']}/{missing['file']}")
        else:
            print("✅ All referenced files exist on disk")
            
        if orphaned_files:
            print(f"⚠️  Found {len(orphaned_files)} orphaned files:")
            for orphaned in orphaned_files:
                print(f"   - {orphaned['project']}/{orphaned['file']}")
        else:
            print("✅ No orphaned files found")
            
        return len(missing_files) == 0 and len(orphaned_files) == 0
        
    except Exception as e:
        print(f"❌ Error during integrity check: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 AASX JSON File Synchronization Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("data/projects").exists():
        print("❌ Error: data/projects directory not found!")
        print("Please run this script from the project root directory")
        return
    
    # Sync JSON files
    success = sync_json_files()
    
    if success:
        # Verify integrity
        verify_file_integrity()
        
        print("\n🎉 Synchronization completed successfully!")
        print("All JSON files are now up to date with the current in-memory state.")
    else:
        print("\n❌ Synchronization failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main() 