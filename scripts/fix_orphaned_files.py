#!/usr/bin/env python3
"""
Fix Orphaned Files Script
Scans actual files on disk and updates JSON files to include orphaned files.
This fixes the issue where uploaded files exist on disk but are not in JSON.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path

def fix_orphaned_files():
    """Fix orphaned files by updating JSON files with actual files on disk"""
    
    print("🔧 Fixing orphaned files...")
    
    projects_dir = Path("data/projects")
    fixed_files = []
    
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
        
        # Load current project and files data
        with open(project_json, 'r') as f:
            project_data = json.load(f)
            
        with open(files_json, 'r') as f:
            files_data = json.load(f)
        
        # Get existing file IDs from JSON
        existing_files = {f['filename'] for f in files_data}
        
        # Scan actual AASX files on disk
        actual_files = list(project_dir.glob("*.aasx"))
        orphaned_files = []
        
        for file_path in actual_files:
            if file_path.name not in existing_files:
                orphaned_files.append(file_path)
                print(f"   🔍 Found orphaned file: {file_path.name}")
        
        # Add orphaned files to JSON
        for file_path in orphaned_files:
            file_size = file_path.stat().st_size
            
            # Create file record
            file_info = {
                "id": str(uuid.uuid4()),
                "filename": file_path.name,
                "original_filename": file_path.name,  # We don't know the original name
                "project_id": project_id,
                "filepath": str(file_path),
                "size": file_size,
                "upload_date": datetime.now().isoformat(),
                "description": f"Recovered file: {file_path.name}",
                "status": "uploaded",
                "processing_result": None
            }
            
            files_data.append(file_info)
            fixed_files.append({
                'project': project_data['name'],
                'file': file_path.name,
                'size': file_size
            })
            
            print(f"   ✅ Added to JSON: {file_path.name} ({file_size} bytes)")
        
        # Update project stats
        if orphaned_files:
            project_data['file_count'] = len(files_data)
            project_data['total_size'] = sum(f['size'] for f in files_data)
            project_data['updated_at'] = datetime.now().isoformat()
            
            # Save updated files.json
            with open(files_json, 'w') as f:
                json.dump(files_data, f, indent=2)
            
            # Save updated project.json
            with open(project_json, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            print(f"   📊 Updated project stats: {project_data['file_count']} files, {project_data['total_size']} bytes")
    
    # Update projects_summary.json
    if fixed_files:
        update_projects_summary()
    
    return fixed_files

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
    
    print("🚀 Fix Orphaned Files Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("data/projects").exists():
        print("❌ Error: data/projects directory not found!")
        print("Please run this script from the project root directory")
        return
    
    # Fix orphaned files
    fixed_files = fix_orphaned_files()
    
    if fixed_files:
        print(f"\n🎉 Successfully fixed {len(fixed_files)} orphaned files!")
        print("\n📋 Fixed files:")
        for file_info in fixed_files:
            print(f"   - {file_info['project']}: {file_info['file']} ({file_info['size']} bytes)")
        
        print(f"\n✅ All JSON files have been updated to reflect the actual files on disk.")
        print("The projects should now show the correct file counts in the web interface.")
    else:
        print("\n✅ No orphaned files found. All files are properly recorded in JSON.")

if __name__ == "__main__":
    main() 