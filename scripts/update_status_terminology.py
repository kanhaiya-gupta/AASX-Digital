#!/usr/bin/env python3
"""
Script to update file status terminology from "uploaded" to "not_processed"
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.aasx.routes import PROJECTS_DB, FILES_DB, save_project_to_filesystem

def update_status_terminology():
    """Update all 'uploaded' statuses to 'not_processed'"""
    print("🔄 Updating file status terminology...")
    print("=" * 50)
    
    updated_count = 0
    
    # Update in-memory database
    for file_id, file_info in FILES_DB.items():
        if file_info['status'] == 'uploaded':
            print(f"📝 Updating {file_info['original_filename']}: uploaded → not_processed")
            file_info['status'] = 'not_processed'
            FILES_DB[file_id] = file_info
            updated_count += 1
            
            # Save the project to filesystem
            project_id = file_info['project_id']
            save_project_to_filesystem(project_id)
    
    print(f"\n✅ Updated {updated_count} files from 'uploaded' to 'not_processed'")
    
    # Also update any project files.json files directly
    projects_dir = "data/projects"
    if os.path.exists(projects_dir):
        for project_dir in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_dir)
            if os.path.isdir(project_path):
                files_json_path = os.path.join(project_path, "files.json")
                if os.path.exists(files_json_path):
                    try:
                        with open(files_json_path, 'r', encoding='utf-8') as f:
                            files_data = json.load(f)
                        
                        project_updated = False
                        for file_info in files_data:
                            if file_info['status'] == 'uploaded':
                                print(f"📝 Updating {file_info['original_filename']} in {project_dir}: uploaded → not_processed")
                                file_info['status'] = 'not_processed'
                                project_updated = True
                        
                        if project_updated:
                            with open(files_json_path, 'w', encoding='utf-8') as f:
                                json.dump(files_data, f, indent=2, ensure_ascii=False)
                            print(f"✅ Updated files.json for project {project_dir}")
                            
                    except Exception as e:
                        print(f"❌ Error updating {files_json_path}: {e}")
    
    print("\n🎉 Status terminology update completed!")

def list_current_statuses():
    """List all current file statuses"""
    print("\n📋 Current file statuses:")
    print("=" * 50)
    
    status_counts = {}
    for file_id, file_info in FILES_DB.items():
        status = file_info['status']
        status_counts[status] = status_counts.get(status, 0) + 1
        print(f"  {file_info['original_filename']}: {status}")
    
    print(f"\n📊 Status Summary:")
    for status, count in status_counts.items():
        print(f"  {status}: {count} files")

def main():
    """Main function"""
    print("🚀 File Status Terminology Update Script")
    print("=" * 50)
    
    # Show current statuses
    list_current_statuses()
    
    # Update terminology
    update_status_terminology()
    
    # Show updated statuses
    list_current_statuses()

if __name__ == "__main__":
    main() 