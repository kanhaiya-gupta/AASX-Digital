#!/usr/bin/env python3
"""
AASX Examples Test

This script tests various AASX examples.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Add parent directory to path
sys.path.append('..')

def test_aasx_examples():
    """Test AASX examples processing"""
    print("AASX Examples Test")
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