#!/usr/bin/env python3
"""
Migrate File Names Script
Migrates existing files from UUID-based names to original filename-based names.
This script will rename files on disk and update JSON records accordingly.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

def migrate_file_names():
    """Migrate files from UUID names to original filename-based names"""
    
    print("🔄 Migrating file names from UUID to original names...")
    
    projects_dir = Path("data/projects")
    migrated_files = []
    
    # Scan each project directory
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
            
        project_id = project_dir.name
        project_json = project_dir / "project.json"
        files_json = project_dir / "files.json"
        
        if not project_json.exists() or not files_json.exists():
            continue
            
        print(f"\n📁 Processing project: {project_id}")
        
        # Load current files data
        with open(files_json, 'r') as f:
            files_data = json.load(f)
        
        # Process each file
        for file_info in files_data:
            old_filename = file_info['filename']
            original_filename = file_info['original_filename']
            
            # Skip if already using original name
            if old_filename == original_filename:
                continue
                
            old_path = project_dir / old_filename
            if not old_path.exists():
                print(f"   ⚠️  File not found: {old_filename}")
                continue
            
            # Generate new filename with collision handling
            base_name = os.path.splitext(original_filename)[0]
            extension = os.path.splitext(original_filename)[1]
            
            # Sanitize filename
            import re
            sanitized_base = re.sub(r'[^\w\-_.]', '_', base_name)
            sanitized_name = sanitized_base + extension
            
            # Handle filename collisions
            counter = 1
            new_filename = sanitized_name
            while (project_dir / new_filename).exists():
                new_filename = f"{sanitized_base}_{counter}{extension}"
                counter += 1
            
            new_path = project_dir / new_filename
            
            try:
                # Rename file on disk
                shutil.move(str(old_path), str(new_path))
                
                # Update file info
                file_info['filename'] = new_filename
                file_info['filepath'] = str(new_path)
                
                migrated_files.append({
                    'project': project_id,
                    'old_name': old_filename,
                    'new_name': new_filename,
                    'original_name': original_filename
                })
                
                print(f"   ✅ Renamed: {old_filename} → {new_filename}")
                
            except Exception as e:
                print(f"   ❌ Error renaming {old_filename}: {e}")
        
        # Save updated files.json
        with open(files_json, 'w') as f:
            json.dump(files_data, f, indent=2)
        
        print(f"   📄 Updated files.json for project {project_id}")
    
    # Update projects_summary.json
    if migrated_files:
        update_projects_summary()
    
    return migrated_files

def update_projects_summary():
    """Update the projects_summary.json file with current state"""
    
    print("\n📄 Updating projects_summary.json...")
    
    projects_dir = Path("data/projects")
    projects = []
    all_files = []
    total_size = 0
    
    # Scan all projects
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
            
        project_json = project_dir / "project.json"
        files_json = project_dir / "files.json"
        
        if project_json.exists() and files_json.exists():
            with open(project_json, 'r') as f:
                project_data = json.load(f)
            
            with open(files_json, 'r') as f:
                files_data = json.load(f)
            
            projects.append(project_data)
            all_files.extend(files_data)
            total_size += project_data['total_size']
    
    # Create summary
    summary = {
        "projects": projects,
        "files": all_files,
        "last_updated": datetime.now().isoformat()
    }
    
    # Save summary
    summary_path = projects_dir / "projects_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"   ✅ Updated summary: {len(projects)} projects, {len(all_files)} files, {total_size} bytes")

def main():
    """Main function"""
    
    print("🚀 Migrate File Names Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("data/projects").exists():
        print("❌ Error: data/projects directory not found!")
        print("Please run this script from the project root directory")
        return
    
    # Confirm before proceeding
    print("⚠️  This script will rename files on disk and update JSON records.")
    print("Make sure you have a backup before proceeding.")
    
    response = input("Do you want to continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Migrate file names
    migrated_files = migrate_file_names()
    
    if migrated_files:
        print(f"\n🎉 Successfully migrated {len(migrated_files)} files!")
        print("\n📋 Migrated files:")
        for file_info in migrated_files:
            print(f"   - {file_info['project']}: {file_info['old_name']} → {file_info['new_name']}")
        
        print(f"\n✅ All files now use their original names with proper collision handling.")
        print("Duplicate file detection is now active for future uploads.")
    else:
        print("\n✅ No files needed migration. All files already use original names.")

if __name__ == "__main__":
    main() 