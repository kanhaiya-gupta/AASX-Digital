#!/usr/bin/env python3
"""
Test script to demonstrate the systematic folder structure for ETL results.
"""

import sys
from pathlib import Path
import yaml
import json
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.aasx.aasx_loader import LoaderConfig, AASXLoader

def test_systematic_structure():
    """Test the systematic folder structure"""
    print("🧪 Testing Systematic Folder Structure")
    print("=" * 50)
    
    # Test data
    test_data = {
        "format": "json",
        "version": "1.0",
        "data": {
            "assets": [
                {
                    "id": "asset_001",
                    "id_short": "TestAsset",
                    "description": "Test Asset for Systematic Structure",
                    "type": "asset",
                    "qi_metadata": {
                        "quality_level": "high",
                        "compliance_status": "compliant"
                    }
                }
            ],
            "submodels": [
                {
                    "id": "submodel_001",
                    "id_short": "TestSubmodel",
                    "description": "Test Submodel",
                    "type": "submodel",
                    "qi_metadata": {
                        "quality_level": "medium",
                        "compliance_status": "pending"
                    }
                }
            ],
            "relationships": [
                {
                    "source_id": "asset_001",
                    "target_id": "submodel_001",
                    "type": "contains",
                    "metadata": {"relationship_type": "composition"}
                }
            ]
        },
        "quality_metrics": {
            "total_assets": 1,
            "total_submodels": 1,
            "quality_score": 0.9
        },
        "metadata": {
            "transformation_timestamp": datetime.now().isoformat(),
            "transformer_version": "1.0.0"
        }
    }
    
    # Test different folder structures
    test_cases = [
        {
            "name": "Timestamped by File",
            "config": LoaderConfig(
                output_directory="output/etl_results",
                systematic_structure=True,
                folder_structure="timestamped_by_file",
                separate_file_outputs=True,
                include_filename_in_output=True
            ),
            "source_file": "data/aasx-examples/test_file.aasx"
        },
        {
            "name": "By Type",
            "config": LoaderConfig(
                output_directory="output/etl_results",
                systematic_structure=True,
                folder_structure="by_type",
                separate_file_outputs=True,
                include_filename_in_output=True
            ),
            "source_file": "data/aasx-examples/test_file.aasx"
        },
        {
            "name": "Flat Structure",
            "config": LoaderConfig(
                output_directory="output/etl_results",
                systematic_structure=True,
                folder_structure="flat",
                separate_file_outputs=True,
                include_filename_in_output=True
            ),
            "source_file": "data/aasx-examples/test_file.aasx"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📁 Testing: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Create loader with test configuration
            loader = AASXLoader(
                config=test_case['config'],
                source_file=test_case['source_file']
            )
            
            print(f"Output directory: {loader.output_dir}")
            
            # Export test data
            exported_files = loader._export_to_files(test_data)
            
            print(f"Exported files:")
            for file_path in exported_files:
                print(f"  ✅ {file_path}")
            
            # Check if files exist
            for file_path in exported_files:
                if Path(file_path).exists():
                    print(f"  ✓ File exists: {file_path}")
                else:
                    print(f"  ✗ File missing: {file_path}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Systematic structure test completed!")
    print("\n📋 Expected folder structure:")
    print("output/etl_results/")
    print("├── etl_run_YYYYMMDD_HHMMSS/")
    print("│   ├── test_file/")
    print("│   │   ├── aasx_data.json")
    print("│   │   ├── aasx_data.yaml")
    print("│   │   ├── aasx_data.csv")
    print("│   │   └── aasx_data_graph.json")
    print("│   └── another_file/")
    print("│       └── ...")
    print("└── ...")

if __name__ == "__main__":
    test_systematic_structure() 