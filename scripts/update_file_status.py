#!/usr/bin/env python3
"""
Script to update file status for processed files
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.aasx.routes import PROJECTS_DB, FILES_DB, save_project_to_filesystem

def update_file_status(filename, new_status="completed"):
    """Update the status of a specific file"""
    print(f"🔍 Looking for file: {filename}")
    
    # Find the file in FILES_DB
    file_id = None
    for fid, file_info in FILES_DB.items():
        if file_info['filename'] == filename or file_info['original_filename'] == filename:
            file_id = fid
            print(f"✅ Found file with ID: {file_id}")
            print(f"   Current status: {file_info['status']}")
            print(f"   Project ID: {file_info['project_id']}")
            break
    
    if file_id:
        # Update the file status
        file_info = FILES_DB[file_id]
        old_status = file_info['status']
        file_info['status'] = new_status
        
        # Add a processing result if it doesn't exist
        if not file_info.get('processing_result'):
            file_info['processing_result'] = {
                'status': new_status,
                'processing_time': 0,
                'timestamp': datetime.now().isoformat(),
                'message': 'Status updated manually'
            }
        
        FILES_DB[file_id] = file_info
        
        # Save the project to filesystem
        project_id = file_info['project_id']
        save_project_to_filesystem(project_id)
        
        print(f"✅ Updated file status from '{old_status}' to '{new_status}'")
        print(f"✅ Saved project {project_id} to filesystem")
        return True
    else:
        print(f"❌ File '{filename}' not found in FILES_DB")
        return False

def list_all_files():
    """List all files with their current status"""
    print("📋 Current files in database:")
    print("-" * 80)
    
    for fid, file_info in FILES_DB.items():
        print(f"ID: {fid}")
        print(f"  Filename: {file_info['filename']}")
        print(f"  Original: {file_info['original_filename']}")
        print(f"  Project: {file_info['project_id']}")
        print(f"  Status: {file_info['status']}")
        print(f"  Size: {file_info['size']} bytes")
        print("-" * 80)

def main():
    """Main function"""
    print("🚀 File Status Update Script")
    print("=" * 50)
    
    # List current files
    list_all_files()
    
    # Update specific files that were processed
    files_to_update = [
        "Example_AAS_Additive_Manufacturing.aasx"
    ]
    
    print("\n🔄 Updating file statuses...")
    for filename in files_to_update:
        update_file_status(filename, "completed")
    
    print("\n✅ File status update completed!")
    print("\n📋 Updated file list:")
    list_all_files()

if __name__ == "__main__":
    main() 