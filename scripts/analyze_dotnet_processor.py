#!/usr/bin/env python3
"""
Detailed Analysis of .NET AAS Processor Output
==============================================

This script analyzes the raw output from the .NET AAS processor to understand:
1. What data structure is returned
2. What field names are used
3. Why validation is filtering out data
4. How to properly handle the output
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from aasx.aasx_processor import AASXProcessor
from aasx.dotnet_bridge import DotNetAasBridge

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_dotnet_output(aasx_file_path: str):
    """
    Analyze the raw output from the .NET processor for a single AASX file.
    """
    logger.info(f"Analyzing .NET processor output for: {aasx_file_path}")
    
    # Initialize the .NET bridge
    bridge = DotNetAasBridge()
    
    if not bridge.is_available():
        logger.error(".NET processor not available")
        return
    
    # Get raw output from .NET processor
    logger.info("Getting raw output from .NET processor...")
    raw_result = bridge.process_aasx_file(aasx_file_path)
    
    if not raw_result:
        logger.error("No result returned from .NET processor")
        return
    
    # Analyze the structure
    logger.info("=== RAW .NET PROCESSOR OUTPUT ANALYSIS ===")
    logger.info(f"Result type: {type(raw_result)}")
    logger.info(f"Result keys: {list(raw_result.keys()) if isinstance(raw_result, dict) else 'Not a dict'}")
    
    # Save raw output for inspection
    raw_output_file = f"analysis_raw_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(raw_output_file, 'w', encoding='utf-8') as f:
        json.dump(raw_result, f, indent=2, ensure_ascii=False, default=str)
    logger.info(f"Raw output saved to: {raw_output_file}")
    
    # Detailed analysis
    if isinstance(raw_result, dict):
        analyze_dict_structure(raw_result, "root")
    
    # Now analyze with our processor
    logger.info("\n=== PROCESSOR ANALYSIS ===")
    processor = AASXProcessor(aasx_file_path)
    processed_result = processor.process()
    
    if processed_result:
        logger.info(f"Processed result keys: {list(processed_result.keys())}")
        
        # Save processed output
        processed_output_file = f"analysis_processed_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(processed_output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_result, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Processed output saved to: {processed_output_file}")
        
        # Analyze validation results
        if 'validation' in processed_result:
            validation = processed_result['validation']
            logger.info(f"Validation summary: {validation}")
            
            if 'validation_errors' in validation:
                logger.info(f"Validation errors: {validation['validation_errors']}")

def analyze_dict_structure(data: dict, path: str, max_depth: int = 3, current_depth: int = 0):
    """
    Recursively analyze dictionary structure.
    """
    if current_depth >= max_depth:
        logger.info(f"{'  ' * current_depth}{path}: [MAX DEPTH REACHED]")
        return
    
    for key, value in data.items():
        current_path = f"{path}.{key}" if path != "root" else key
        
        if isinstance(value, dict):
            logger.info(f"{'  ' * current_depth}{current_path}: dict with keys: {list(value.keys())}")
            if current_depth < max_depth - 1:
                analyze_dict_structure(value, current_path, max_depth, current_depth + 1)
        elif isinstance(value, list):
            logger.info(f"{'  ' * current_depth}{current_path}: list with {len(value)} items")
            if value and current_depth < max_depth - 1:
                # Show first item structure
                first_item = value[0]
                if isinstance(first_item, dict):
                    logger.info(f"{'  ' * (current_depth + 1)}{current_path}[0]: dict with keys: {list(first_item.keys())}")
                else:
                    logger.info(f"{'  ' * (current_depth + 1)}{current_path}[0]: {type(first_item)} = {first_item}")
        else:
            logger.info(f"{'  ' * current_depth}{current_path}: {type(value)} = {value}")

def analyze_validation_logic():
    """
    Analyze why validation is filtering out data.
    """
    logger.info("\n=== VALIDATION LOGIC ANALYSIS ===")
    
    # Test with sample data that matches .NET processor output
    test_assets = [
        {"id": "test_id", "idShort": "test_short"},  # Should pass
        {"id": None, "idShort": "test_short"},       # Should fail (None id)
        {"id": "test_id", "idShort": None},          # Should fail (None idShort)
        {"id": "", "idShort": "test_short"},         # Should fail (empty id)
        {"id": "test_id", "idShort": ""},            # Should fail (empty idShort)
        {"id": None, "idShort": None},               # Should fail (both None)
        {"id": "http://valid.url", "idShort": "test"}, # Should pass
        {"id": "http.//invalid.url", "idShort": "test"}, # Should fail (malformed URL)
    ]
    
    # Create a minimal processor instance for testing
    class TestProcessor:
        def __init__(self):
            self.validation_errors = []
        
        def _is_valid_asset(self, asset):
            if not asset:
                return False
            
            id_value = asset.get('id')
            id_short = asset.get('idShort')
            
            if id_value is None or id_short is None:
                self.validation_errors.append(f"Asset missing required ID or ID_Short: {asset}")
                return False
            
            if not str(id_value).strip() or not str(id_short).strip():
                self.validation_errors.append(f"Asset has empty ID or ID_Short: {asset}")
                return False
            
            return True
    
    processor = TestProcessor()
    
    for i, asset in enumerate(test_assets):
        is_valid = processor._is_valid_asset(asset)
        logger.info(f"Test asset {i+1}: {asset} -> Valid: {is_valid}")
    
    logger.info(f"Total validation errors: {len(processor.validation_errors)}")
    for error in processor.validation_errors:
        logger.info(f"  - {error}")

def main():
    """
    Main analysis function.
    """
    # Find AASX files
    aasx_dir = Path("aasx-generator/data/samples_aasx/servodcmotor")
    if not aasx_dir.exists():
        logger.error(f"AASX directory not found: {aasx_dir}")
        return
    
    aasx_files = list(aasx_dir.rglob("*.aasx"))
    if not aasx_files:
        logger.error("No AASX files found")
        return
    
    logger.info(f"Found {len(aasx_files)} AASX files")
    
    # Analyze first file in detail
    first_file = aasx_files[0]
    logger.info(f"Analyzing first file: {first_file}")
    
    analyze_dotnet_output(str(first_file))
    
    # Analyze validation logic
    analyze_validation_logic()
    
    logger.info("\n=== ANALYSIS COMPLETE ===")
    logger.info("Check the generated JSON files for detailed output structure")

if __name__ == "__main__":
    main() 