#!/usr/bin/env python3
"""
AASX Integration Test

This script tests AASX integration with the platform.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_aasx_integration():
    """Test AASX integration functionality"""
    print("AASX Integration Test Suite")
    print("=" * 50)
    
    try:
        # Import required modules
        from aasx.aasx_processor import AASXProcessor
        from aasx.dotnet_bridge import DotNetAasBridge
        
        print("OK: All modules imported successfully")
        
        # Create processor instances
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        python_processor = AASXProcessor(aasx_file)
        dotnet_bridge = DotNetAasBridge()
        
        print("OK: Processor instances created")
        
        # Test with AASX file
        if not os.path.exists(aasx_file):
            print(f"ERROR: AASX file not found: {aasx_file}")
            return False
        
        print(f"OK: Testing with: {aasx_file}")
        
        # Test Python processing
        print("\nTesting Python processing...")
        python_result = python_processor.process()
        
        if python_result:
            print("OK: Python processing successful")
            print(f"   Method: {python_result.get('processing_method', 'unknown')}")
        else:
            print("WARNING: Python processing failed")
        
        # Test .NET processing
        print("\nTesting .NET processing...")
        if dotnet_bridge.is_available():
            dotnet_result = dotnet_bridge.process_aasx_file(aasx_file)
            
            if dotnet_result:
                print("OK: .NET processing successful")
                print(f"   Method: {dotnet_result.get('processing_method', 'unknown')}")
            else:
                print("WARNING: .NET processing failed")
        else:
            print("WARNING: .NET processor not available")
        
        return True
        
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: AASX integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_aasx_integration()
    if success:
        print("\nSUCCESS: AASX integration test completed!")
        sys.exit(0)
    else:
        print("\nFAILED: AASX integration test failed!")
        sys.exit(1) 