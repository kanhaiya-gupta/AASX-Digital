#!/usr/bin/env python3
"""
AASX Transformation Test

This script tests the AASX data transformation capabilities.
"""

import sys, os
import json
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_transformation_imports():
    """Test that transformation modules can be imported"""
    print("Testing Transformation Module Imports")
    print("=" * 40)
    
    try:
        from aasx.aasx_transformer import AASXTransformer, TransformationConfig
        print("OK: AASXTransformer imported successfully")
        print("OK: TransformationConfig imported successfully")
        return True
        
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        return False

def test_basic_transformation():
    """Test basic AASX data transformation"""
    print("\nTesting Basic Transformation")
    print("=" * 40)
    
    try:
        from aasx.aasx_transformer import AASXTransformer, TransformationConfig
        from aasx.aasx_processor import AASXProcessor
        
        # Get sample AASX data
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("ERROR: AASX file not found")
            return False
        
        # Process AASX file
        processor = AASXProcessor(aasx_file)
        raw_data = processor.process()
        
        if not raw_data:
            print("ERROR: Failed to process AASX file")
            return False
        
        print(f"OK: Raw data extracted - {len(raw_data.get('assets', []))} assets, {len(raw_data.get('submodels', []))} submodels")
        
        # Transform data
        config = TransformationConfig(
            output_format="json",
            include_metadata=True,
            normalize_ids=True,
            quality_checks=True
        )
        
        transformer = AASXTransformer(config)
        transformed_data = transformer.transform_aasx_data(raw_data)
        
        if transformed_data:
            print("OK: Data transformation successful")
            print(f"   Format: {transformed_data.get('format', 'unknown')}")
            print(f"   Version: {transformed_data.get('version', 'unknown')}")
            
            # Check quality metrics
            quality_metrics = transformed_data.get('quality_metrics', {})
            if quality_metrics:
                print(f"   Quality score: {quality_metrics.get('quality_score', 0):.2f}")
                print(f"   Total assets: {quality_metrics.get('total_assets', 0)}")
                print(f"   Total submodels: {quality_metrics.get('total_submodels', 0)}")
            
            return True
        else:
            print("ERROR: Transformation failed")
            return False
        
    except Exception as e:
        print(f"ERROR: Basic transformation test failed: {e}")
        return False

def test_multiple_formats():
    """Test transformation to multiple output formats"""
    print("\nTesting Multiple Output Formats")
    print("=" * 40)
    
    try:
        from aasx.aasx_transformer import AASXTransformer, TransformationConfig
        from aasx.aasx_processor import AASXProcessor
        
        # Get sample data
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("ERROR: AASX file not found")
            return False
        
        processor = AASXProcessor(aasx_file)
        raw_data = processor.process()
        
        if not raw_data:
            print("ERROR: Failed to process AASX file")
            return False
        
        # Test different formats
        formats = ['json', 'xml', 'csv', 'yaml', 'graph', 'flattened']
        
        for format_type in formats:
            try:
                config = TransformationConfig(
                    output_format=format_type,
                    include_metadata=True,
                    normalize_ids=True
                )
                
                transformer = AASXTransformer(config)
                transformed_data = transformer.transform_aasx_data(raw_data)
                
                if transformed_data:
                    print(f"OK: {format_type.upper()} format transformation successful")
                    print(f"   Format: {transformed_data.get('format', 'unknown')}")
                else:
                    print(f"ERROR: {format_type.upper()} format transformation failed")
                    return False
                    
            except Exception as e:
                print(f"ERROR: {format_type.upper()} format test failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: Multiple formats test failed: {e}")
        return False

def test_quality_checks():
    """Test quality checking functionality"""
    print("\nTesting Quality Checks")
    print("=" * 40)
    
    try:
        from aasx.aasx_transformer import AASXTransformer, TransformationConfig
        from aasx.aasx_processor import AASXProcessor
        
        # Get sample data
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("ERROR: AASX file not found")
            return False
        
        processor = AASXProcessor(aasx_file)
        raw_data = processor.process()
        
        if not raw_data:
            print("ERROR: Failed to process AASX file")
            return False
        
        # Test with quality checks enabled
        config = TransformationConfig(
            output_format="json",
            quality_checks=True,
            enrich_with_external_data=True
        )
        
        transformer = AASXTransformer(config)
        transformed_data = transformer.transform_aasx_data(raw_data)
        
        if transformed_data:
            # Get quality report
            quality_report = transformer.get_quality_report()
            
            if quality_report:
                print("OK: Quality report generated")
                metrics = quality_report.get('quality_metrics', {})
                print(f"   Quality score: {metrics.get('quality_score', 0):.2f}")
                print(f"   Assets with IDs: {metrics.get('assets_with_ids', 0)}")
                print(f"   Submodels with IDs: {metrics.get('submodels_with_ids', 0)}")
                print(f"   Assets with descriptions: {metrics.get('assets_with_descriptions', 0)}")
                print(f"   Submodels with descriptions: {metrics.get('submodels_with_descriptions', 0)}")
                
                return True
            else:
                print("ERROR: Quality report not generated")
                return False
        else:
            print("ERROR: Transformation failed")
            return False
        
    except Exception as e:
        print(f"ERROR: Quality checks test failed: {e}")
        return False

def test_data_export():
    """Test data export functionality"""
    print("\nTesting Data Export")
    print("=" * 40)
    
    try:
        from aasx.aasx_transformer import AASXTransformer, TransformationConfig
        from aasx.aasx_processor import AASXProcessor
        
        # Get sample data
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("ERROR: AASX file not found")
            return False
        
        processor = AASXProcessor(aasx_file)
        raw_data = processor.process()
        
        if not raw_data:
            print("ERROR: Failed to process AASX file")
            return False
        
        # Test JSON export
        config = TransformationConfig(output_format="json")
        transformer = AASXTransformer(config)
        transformer.transform_aasx_data(raw_data)
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            export_path = transformer.export_transformed_data(temp_file.name)
            
            if os.path.exists(export_path):
                print("OK: JSON export successful")
                
                # Check file content
                with open(export_path, 'r') as f:
                    exported_data = json.load(f)
                
                if exported_data.get('format') == 'json':
                    print("OK: Exported data format correct")
                else:
                    print("ERROR: Exported data format incorrect")
                    return False
                
                # Clean up
                os.unlink(export_path)
            else:
                print("ERROR: JSON export failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: Data export test failed: {e}")
        return False

def main():
    """Run all transformation tests"""
    print("="*60)
    print("AASX Transformation Test Suite")
    print("="*60)
    
    tests = [
        ("Module Imports", test_transformation_imports),
        ("Basic Transformation", test_basic_transformation),
        ("Multiple Formats", test_multiple_formats),
        ("Quality Checks", test_quality_checks),
        ("Data Export", test_data_export)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 30)
        
        if test_func():
            print(f"PASSED: {test_name}")
            passed += 1
        else:
            print(f"FAILED: {test_name}")
    
    print("\n" + "="*60)
    print(f"Transformation Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("SUCCESS: All transformation tests passed!")
        return 0
    else:
        print("WARNING: Some transformation tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 