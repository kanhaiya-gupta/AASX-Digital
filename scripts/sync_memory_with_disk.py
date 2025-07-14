#!/usr/bin/env python3
"""
Sync Memory with Disk Script
Synchronizes the in-memory state with the actual files on disk.
This fixes discrepancies where files exist in memory but not on disk.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def sync_memory_with_disk():
    """Sync in-memory state with actual files on disk"""
    
    try:
        # Import the backend modules
        from webapp.aasx.routes import PROJECTS_DB, FILES_DB, save_project_to_filesystem, save_all_projects_to_filesystem
        
        print("🔄 Synchronizing in-memory state with disk...")
        print(f"📊 Initial state:")
        print(f"   - Projects: {len(PROJECTS_DB)}")
        print(f"   - Files in memory: {len(FILES_DB)}")
        
        projects_dir = Path("data/projects")
        synced_projects = []
        
        # Process each project
        for project_id, project in PROJECTS_DB.items():
            project_dir = projects_dir / project_id
            if not project_dir.exists():
                continue
                
            print(f"\n📁 Processing project: {project['name']} ({project_id})")
            
            # Get files in memory for this project
            memory_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
            print(f"   - Files in memory: {len(memory_files)}")
            
            # Get actual files on disk
            disk_files = list(project_dir.glob("*.aasx"))
            print(f"   - Files on disk: {len(disk_files)}")
            
            # Find files that exist in memory but not on disk
            memory_filenames = {f['filename'] for f in memory_files}
            disk_filenames = {f.name for f in disk_files}
            
            orphaned_memory_files = memory_filenames - disk_filenames
            missing_memory_files = disk_filenames - memory_filenames
            
            if orphaned_memory_files:
                print(f"   ⚠️  Found {len(orphaned_memory_files)} files in memory but not on disk:")
                for filename in orphaned_memory_files:
                    print(f"     - {filename}")
                
                # Remove orphaned files from memory
                files_to_remove = []
                for file_info in memory_files:
                    if file_info['filename'] in orphaned_memory_files:
                        files_to_remove.append(file_info['id'])
                        print(f"     🗑️  Removing from memory: {file_info['original_filename']}")
                
                for file_id in files_to_remove:
                    if file_id in FILES_DB:
                        del FILES_DB[file_id]
            
            if missing_memory_files:
                print(f"   ⚠️  Found {len(missing_memory_files)} files on disk but not in memory:")
                for filename in missing_memory_files:
                    print(f"     - {filename}")
            
            # Update project stats
            updated_memory_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
            project['file_count'] = len(updated_memory_files)
            project['total_size'] = sum(f['size'] for f in updated_memory_files)
            project['updated_at'] = datetime.now().isoformat()
            
            print(f"   📊 Updated project stats: {project['file_count']} files, {project['total_size']} bytes")
            
            # Save project to disk
            save_project_to_filesystem(project_id)
            synced_projects.append(project_id)
        
        # Save all projects to ensure consistency
        print(f"\n🔧 Saving all projects to ensure consistency...")
        save_all_projects_to_filesystem()
        
        print(f"\n📊 Final state:")
        print(f"   - Projects: {len(PROJECTS_DB)}")
        print(f"   - Files in memory: {len(FILES_DB)}")
        print(f"   - Synced projects: {len(synced_projects)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this script from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error during synchronization: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 Sync Memory with Disk Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("data/projects").exists():
        print("❌ Error: data/projects directory not found!")
        print("Please run this script from the project root directory")
        return
    
    # Sync memory with disk
    success = sync_memory_with_disk()
    
    if success:
        print("\n🎉 Synchronization completed successfully!")
        print("The in-memory state now matches the actual files on disk.")
        print("Try refreshing the web interface to see the updated file counts.")
    else:
        print("\n❌ Synchronization failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main() 