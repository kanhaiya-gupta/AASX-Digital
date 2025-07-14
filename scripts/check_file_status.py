#!/usr/bin/env python3
"""
Script to check current file status
"""

import sys
import os
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.aasx.routes import PROJECTS_DB, FILES_DB

def check_file_status():
    """Check the current status of all files"""
    print("🔍 Checking current file status...")
    print("=" * 80)
    
    for fid, file_info in FILES_DB.items():
        print(f"File: {file_info['original_filename']}")
        print(f"  ID: {fid}")
        print(f"  Status: {file_info['status']}")
        print(f"  Project: {file_info['project_id']}")
        if file_info.get('processing_result'):
            print(f"  Processing Result: {file_info['processing_result'].get('status', 'N/A')}")
        print("-" * 80)

def check_specific_file(filename):
    """Check the status of a specific file"""
    print(f"🔍 Checking status for: {filename}")
    print("=" * 50)
    
    for fid, file_info in FILES_DB.items():
        if file_info['filename'] == filename or file_info['original_filename'] == filename:
            print(f"Found file with ID: {fid}")
            print(f"Current status: {file_info['status']}")
            print(f"Project ID: {file_info['project_id']}")
            if file_info.get('processing_result'):
                print(f"Processing result: {file_info['processing_result']}")
            return file_info
    
    print(f"❌ File '{filename}' not found in FILES_DB")
    return None

def main():
    """Main function"""
    print("🚀 File Status Check Script")
    print("=" * 50)
    
    # Check all files
    check_file_status()
    
    # Check specific file
    print("\n🔍 Checking specific file:")
    check_specific_file("Example_AAS_Additive_Manufacturing.aasx")

if __name__ == "__main__":
    main() 