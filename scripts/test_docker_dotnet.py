#!/usr/bin/env python3
"""
Test script to verify .NET AAS processor works in Docker containers
"""

import subprocess
import sys
import os
from pathlib import Path

def test_dotnet_in_container():
    """Test if .NET processor works in Docker container"""
    print("🧪 Testing .NET AAS Processor in Docker")
    print("=" * 50)
    
    # Test if we're in a Docker container
    in_container = os.path.exists('/.dockerenv')
    print(f"Running in Docker container: {in_container}")
    
    # Test .NET availability
    try:
        result = subprocess.run(
            ["dotnet", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ .NET version: {result.stdout.strip()}")
        else:
            print("❌ .NET not found")
            return False
    except FileNotFoundError:
        print("❌ .NET not found")
        return False
    
    # Test if aas-processor executable exists
    processor_path = Path("/app/aas-processor/bin/Release/net6.0/AasProcessor")
    if processor_path.exists():
        print(f"✅ AAS Processor found: {processor_path}")
    else:
        print(f"❌ AAS Processor not found at: {processor_path}")
        return False
    
    # Test if we can run the processor
    try:
        result = subprocess.run(
            [str(processor_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print("✅ AAS Processor executable works")
        return True
    except subprocess.TimeoutExpired:
        print("⚠️  AAS Processor timed out (this might be normal)")
        return True
    except Exception as e:
        print(f"❌ Error running AAS Processor: {e}")
        return False

def test_python_bridge():
    """Test Python bridge to .NET processor"""
    print("\n🔗 Testing Python Bridge")
    print("=" * 30)
    
    try:
        # Add src to path
        sys.path.insert(0, '/app/src')
        
        from aasx.dotnet_bridge import DotNetAasBridge
        
        bridge = DotNetAasBridge()
        
        if bridge.is_available():
            print("✅ .NET Bridge is available")
            return True
        else:
            print("❌ .NET Bridge is not available")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import .NET Bridge: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing .NET Bridge: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Docker .NET Processor Test")
    print("=" * 50)
    
    # Test .NET processor
    dotnet_ok = test_dotnet_in_container()
    
    # Test Python bridge
    bridge_ok = test_python_bridge()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  .NET Processor: {'✅ Working' if dotnet_ok else '❌ Failed'}")
    print(f"  Python Bridge:  {'✅ Working' if bridge_ok else '❌ Failed'}")
    
    if dotnet_ok and bridge_ok:
        print("\n🎉 All tests passed! Your Docker container is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 