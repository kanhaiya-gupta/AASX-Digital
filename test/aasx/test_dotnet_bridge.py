#!/usr/bin/env python3
"""
Test .NET AAS Bridge Integration

This script tests the .NET bridge for AASX processing.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_dotnet_bridge():
    """Test .NET bridge functionality"""
    print("Testing .NET AAS Bridge Integration")
    print("=" * 50)
    
    try:
        # Try to import the .NET bridge
        from aasx.dotnet_bridge import DotNetAasBridge
        print("OK: .NET bridge imported successfully")
        
        # Create bridge instance
        bridge = DotNetAasBridge()
        print("OK: .NET bridge instance created")
        
        # Check if .NET processor is available
        if bridge.is_available():
            print("OK: .NET processor is available")
            
            # Test with a sample AASX file
            aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
            
            if os.path.exists(aasx_file):
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
            else:
                print(f"ERROR: AASX file not found: {aasx_file}")
                return False
        else:
            print("ERROR: .NET processor not available")
            return False
            
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: .NET bridge test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_dotnet_bridge()
    if success:
        print("\nSUCCESS: .NET bridge test completed successfully!")
        sys.exit(0)
    else:
        print("\nFAILED: .NET bridge test failed!")
        sys.exit(1) 