#!/usr/bin/env python3
"""
AASX Processing Module Test

This script tests the AASX processing module functionality.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Add parent directory to path
sys.path.append('..')

def test_aasx_processing():
    """Test AASX processing functionality"""
    print("AASX Processing Module Test Suite")
    print("=" * 50)
    
    try:
        # Import the AASX processor
        from aasx.aasx_processor import AASXProcessor
        
        print("OK: AASX processor imported successfully")
        
        # Test with AASX file
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print(f"ERROR: AASX file not found: {aasx_file}")
            return False
        
        print(f"OK: Testing with: {aasx_file}")
        
        # Create processor instance
        processor = AASXProcessor(aasx_file)
        print("OK: AASX processor instance created")
        
        # Process the AASX file
        result = processor.process()
        
        if result:
            print("OK: AASX processing successful!")
            print(f"   Processing method: {result.get('processing_method', 'unknown')}")
            print(f"   Assets found: {len(result.get('assets', []))}")
            print(f"   Submodels found: {len(result.get('submodels', []))}")
            print(f"   Documents found: {len(result.get('documents', []))}")
            
            # Show some details
            assets = result.get('assets', [])
            if assets:
                print(f"\n   Asset details:")
                for i, asset in enumerate(assets[:3]):  # Show first 3
                    print(f"     {i+1}. {asset.get('id', 'Unknown ID')} - {asset.get('type', 'Unknown Type')}")
            
            submodels = result.get('submodels', [])
            if submodels:
                print(f"\n   Submodel details:")
                for i, submodel in enumerate(submodels[:3]):  # Show first 3
                    print(f"     {i+1}. {submodel.get('id', 'Unknown ID')} - {submodel.get('type', 'Unknown Type')}")
            
            return True
        else:
            print("ERROR: AASX processing failed")
            return False
            
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: AASX processing test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_aasx_processing()
    if success:
        print("\nSUCCESS: AASX processing test completed successfully!")
        sys.exit(0)
    else:
        print("\nFAILED: AASX processing test failed!")
        sys.exit(1) 