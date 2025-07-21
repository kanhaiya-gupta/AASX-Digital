#!/usr/bin/env python3
"""
Display enhanced .NET processor output showing all extracted files.
"""

import json
import glob
from pathlib import Path

def show_enhanced_output():
    """
    Display the enhanced .NET processor output.
    """
    # Find the latest analysis file
    analysis_files = glob.glob("analysis_raw_output_*.json")
    if not analysis_files:
        print("No analysis files found!")
        return
    
    latest_file = max(analysis_files)
    print(f"📄 Reading: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print("🎯 ENHANCED AASX PROCESSOR OUTPUT")
    print("="*80)
    
    # Basic info
    print(f"📁 File: {data['file_path']}")
    print(f"📊 Size: {data['file_size']:,} bytes")
    print(f"⏰ Timestamp: {data['processing_timestamp']}")
    print(f"🔧 Method: {data['processing_method']}")
    
    # Assets
    print(f"\n🏭 ASSETS ({len(data['assets'])} items):")
    for i, asset in enumerate(data['assets'], 1):
        print(f"  {i}. {asset.get('idShort', 'N/A')} (ID: {asset.get('id', 'N/A')})")
        print(f"     Description: {asset.get('description', 'N/A')}")
        print(f"     Kind: {asset.get('kind', 'N/A')}")
        print(f"     Source: {asset.get('source', 'N/A')}")
    
    # Submodels
    print(f"\n📋 SUBMODELS ({len(data['submodels'])} items):")
    for i, submodel in enumerate(data['submodels'], 1):
        print(f"  {i}. {submodel.get('idShort', 'N/A')} (ID: {submodel.get('id', 'N/A')})")
        print(f"     Description: {submodel.get('description', 'N/A')}")
        print(f"     Kind: {submodel.get('kind', 'N/A')}")
        print(f"     Source: {submodel.get('source', 'N/A')}")
    
    # Documents
    print(f"\n📄 DOCUMENTS ({len(data['documents'])} items):")
    for i, doc in enumerate(data['documents'], 1):
        print(f"  {i}. {doc.get('filename', 'N/A')}")
        print(f"     Size: {doc.get('size', 0):,} bytes")
        print(f"     Type: {doc.get('type', 'N/A')}")
    
    # Images
    print(f"\n🖼️  IMAGES ({len(data['images'])} items):")
    for i, img in enumerate(data['images'], 1):
        print(f"  {i}. {img.get('filename', 'N/A')}")
        print(f"     Size: {img.get('size', 0):,} bytes")
        print(f"     Type: {img.get('type', 'N/A')}")
    
    # Other files
    if data.get('other_files'):
        print(f"\n📁 OTHER FILES ({len(data['other_files'])} items):")
        for i, file in enumerate(data['other_files'], 1):
            print(f"  {i}. {file.get('filename', 'N/A')}")
            print(f"     Size: {file.get('size', 0):,} bytes")
            print(f"     Type: {file.get('type', 'N/A')}")
    
    # Raw data
    print(f"\n🔍 RAW DATA:")
    print(f"  JSON files: {len(data['raw_data']['json_files'])}")
    print(f"  XML files: {len(data['raw_data']['xml_files'])}")
    for xml_file in data['raw_data']['xml_files']:
        print(f"    - {xml_file}")
    
    print("\n" + "="*80)
    print("✅ ENHANCED PROCESSING COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    show_enhanced_output() 