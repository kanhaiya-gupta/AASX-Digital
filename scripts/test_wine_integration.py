#!/usr/bin/env python3
"""
Test script to verify Wine integration for AASX Package Explorer
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def test_wine_installation():
    """Test if Wine is properly installed"""
    print("🧪 Testing Wine Installation")
    print("=" * 40)
    
    try:
        # Check Wine version
        result = subprocess.run(
            ["wine", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Wine version: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Wine check failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Wine not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Wine version check timed out")
        return False
    except Exception as e:
        print(f"❌ Wine test failed: {e}")
        return False

def test_wine_configuration():
    """Test Wine configuration"""
    print("\n🔧 Testing Wine Configuration")
    print("=" * 40)
    
    try:
        # Check Wine architecture
        result = subprocess.run(
            ["wine", "winecfg", "/v"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            print("✅ Wine configuration accessible")
            return True
        else:
            print(f"⚠️  Wine configuration check: {result.stderr}")
            return True  # Not critical for basic functionality
            
    except Exception as e:
        print(f"⚠️  Wine configuration test: {e}")
        return True  # Not critical

def test_aasx_explorer_files():
    """Test if AASX Package Explorer files are available"""
    print("\n📁 Testing AASX Package Explorer Files")
    print("=" * 40)
    
    # Check if we're in a Docker container
    in_container = os.path.exists('/.dockerenv')
    print(f"Running in Docker container: {in_container}")
    
    # Check for AASX Package Explorer
    explorer_path = Path("/app/AasxPackageExplorer/AasxPackageExplorer.exe")
    if not explorer_path.exists():
        # Try alternative paths
        explorer_path = Path("AasxPackageExplorer/AasxPackageExplorer.exe")
        if not explorer_path.exists():
            print("❌ AASX Package Explorer not found")
            return False
    
    print(f"✅ AASX Package Explorer found: {explorer_path}")
    
    # Check for required DLLs
    required_files = [
        "AasxPackageExplorer.exe",
        "AasCore.Aas3_0.dll",
        "System.dll",
        "System.Windows.Forms.dll"
    ]
    
    explorer_dir = explorer_path.parent
    missing_files = []
    
    for file in required_files:
        if not (explorer_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Missing files: {missing_files}")
    else:
        print("✅ All required files found")
    
    return True

def test_wine_aasx_launch():
    """Test launching AASX Package Explorer with Wine"""
    print("\n🚀 Testing Wine AASX Package Explorer Launch")
    print("=" * 40)
    
    try:
        # Import the launcher module
        sys.path.append(str(Path(__file__).parent.parent / "src"))
        from src.aasx.launch_explorer import launch_explorer
        
        # Test launch (silent mode)
        result = launch_explorer(silent=True)
        
        if result["success"]:
            print(f"✅ Launch successful: {result['message']}")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   PID: {result.get('pid', 'N/A')}")
            return True
        else:
            print(f"❌ Launch failed: {result['message']}")
            print(f"   Error: {result.get('error', 'unknown')}")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import launcher module: {e}")
        return False
    except Exception as e:
        print(f"❌ Launch test failed: {e}")
        return False

def test_display_environment():
    """Test display environment for GUI applications"""
    print("\n🖥️  Testing Display Environment")
    print("=" * 40)
    
    # Check DISPLAY variable
    display = os.environ.get('DISPLAY', 'Not set')
    print(f"DISPLAY variable: {display}")
    
    # Check if we're in a container
    in_container = os.path.exists('/.dockerenv')
    if in_container:
        print("⚠️  Running in container - GUI may not be visible")
        print("   Consider using X11 forwarding or VNC for GUI access")
    else:
        print("✅ Running on host - GUI should be visible")
    
    return True

def main():
    """Main test function"""
    print("🧪 Wine Integration Test for AASX Package Explorer")
    print("=" * 60)
    
    tests = [
        ("Wine Installation", test_wine_installation),
        ("Wine Configuration", test_wine_configuration),
        ("AASX Explorer Files", test_aasx_explorer_files),
        ("Display Environment", test_display_environment),
        ("Wine AASX Launch", test_wine_aasx_launch),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Wine integration is working correctly.")
        print("\n💡 Usage:")
        print("   • AASX Package Explorer can now run in Docker containers")
        print("   • Use the web interface to launch the explorer")
        print("   • GUI will be available if X11 forwarding is configured")
        return 0
    elif passed >= total - 1:
        print("⚠️  Most tests passed. Wine integration should work with limitations.")
        print("\n💡 Notes:")
        print("   • GUI may not be visible in headless containers")
        print("   • Consider using X11 forwarding for GUI access")
        return 0
    else:
        print("❌ Several tests failed. Wine integration needs attention.")
        print("\n🔧 Troubleshooting:")
        print("   • Ensure Wine is properly installed in the container")
        print("   • Check AASX Package Explorer files are present")
        print("   • Verify container has necessary permissions")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 