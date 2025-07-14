#!/usr/bin/env python3
"""
Simple AASX Examples Test

This script demonstrates basic AASX processing with the working example.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_aasx_examples():
    """Test AASX examples processing"""
    print("Simple AASX Examples Test")
    print("=" * 50)
    
    try:
        # Try to import the .NET bridge
        from aasx.dotnet_bridge import DotNetAasBridge
        print("OK: .NET bridge imported successfully")
        
        # Create bridge instance
        bridge = DotNetAasBridge()
        
        # Check if .NET processor is available
        if not bridge.is_available():
            print("ERROR: .NET processor not available")
            return False
        
        # Test with the working AASX file
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print(f"ERROR: AASX file not found: {aasx_file}")
            return False
        
        print(f"OK: Testing with: {aasx_file}")
        
        # Process the AASX file
        result = bridge.process_aasx_file(aasx_file)
        
        if result:
            print("OK: .NET processing successful!")
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
            print("ERROR: .NET processing failed")
            return False
            
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: AASX examples test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_aasx_examples()
    if success:
        print("\nSUCCESS: AASX examples test completed successfully!")
        sys.exit(0)
    else:
        print("\nFAILED: AASX examples test failed!")
        sys.exit(1) 