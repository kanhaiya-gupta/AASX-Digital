#!/usr/bin/env python3
"""
Analyze metadata issues in AASX processing output.
"""

import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_metadata_issues():
    """
    Analyze the metadata issues in the current output.
    """
    # Find the latest JSON output
    json_files = list(Path("aasx-generator/data/samples_json").rglob("*.json"))
    if not json_files:
        logger.error("No JSON files found!")
        return
    
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Analyzing: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print("🔍 METADATA ANALYSIS")
    print("="*80)
    
    # Analyze metadata
    metadata = data.get('metadata', {})
    file_info = metadata.get('file_info', {})
    
    print(f"\n📋 CURRENT METADATA:")
    print(f"  Processing method: {file_info.get('processing_method', 'N/A')}")
    print(f"  Timestamp: {file_info.get('processing_timestamp', 'N/A')}")
    print(f"  Libraries: {file_info.get('libraries_used', [])}")
    
    print(f"\n❌ MISSING METADATA:")
    print(f"  - Original AASX file path")
    print(f"  - Original AASX file size")
    print(f"  - AAS version (should be 2.0)")
    print(f"  - XML namespace information")
    print(f"  - Processing duration")
    print(f"  - Validation status")
    
    # Analyze assets
    assets = data.get('assets', [])
    print(f"\n🏭 ASSET ANALYSIS:")
    print(f"  Total assets: {len(assets)}")
    
    for i, asset in enumerate(assets, 1):
        print(f"  Asset {i}:")
        print(f"    ID: '{asset.get('id', 'N/A')}' (should be: http://customer.com/aas/9175_7013_7091_9168)")
        print(f"    IDShort: {asset.get('idShort', 'N/A')}")
        print(f"    Description: '{asset.get('description', 'N/A')}'")
        print(f"    Kind: '{asset.get('kind', 'N/A')}'")
    
    # Analyze submodels
    submodels = data.get('submodels', [])
    print(f"\n📋 SUBMODEL ANALYSIS:")
    print(f"  Total submodels: {len(submodels)}")
    
    for i, submodel in enumerate(submodels, 1):
        print(f"  Submodel {i}:")
        print(f"    ID: '{submodel.get('id', 'N/A')}' (should have actual ID)")
        print(f"    IDShort: {submodel.get('idShort', 'N/A')}")
        print(f"    Description: '{submodel.get('description', 'N/A')}'")
        print(f"    Kind: '{submodel.get('kind', 'N/A')}'")
    
    # Analyze files
    documents = data.get('documents', [])
    images = data.get('images', [])
    other_files = data.get('other_files', [])
    
    print(f"\n📄 FILE ANALYSIS:")
    print(f"  Documents: {len(documents)}")
    print(f"  Images: {len(images)}")
    print(f"  Other files: {len(other_files)}")
    
    print(f"\n✅ WHAT'S WORKING:")
    print(f"  - File extraction (documents, images, other files)")
    print(f"  - Basic structure preservation")
    print(f"  - File categorization")
    
    print(f"\n❌ WHAT NEEDS FIXING:")
    print(f"  - Asset/Submodel IDs are empty")
    print(f"  - Missing AAS version detection")
    print(f"  - Missing XML namespace information")
    print(f"  - Missing relationship data")
    print(f"  - Incomplete metadata")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    analyze_metadata_issues() 