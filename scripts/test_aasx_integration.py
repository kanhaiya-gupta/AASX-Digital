#!/usr/bin/env python3
"""
Test script to verify AASX processing integration with .NET processor
"""

import requests
import subprocess
import sys
import os
import time
from pathlib import Path

def test_webapp_health():
    """Test if the webapp is running and healthy"""
    try:
        response = requests.get("http://localhost:80/health", timeout=10)
        if response.status_code == 200:
            print("✅ Webapp health check passed")
            return True
        else:
            print(f"❌ Webapp health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Webapp health check failed: {e}")
        return False

def test_aasx_module():
    """Test if the AASX module is accessible"""
    try:
        response = requests.get("http://localhost:80/aasx/health", timeout=10)
        if response.status_code == 200:
            print("✅ AASX module is accessible")
            return True
        else:
            print(f"❌ AASX module check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AASX module check failed: {e}")
        return False

def test_dotnet_processor_in_container():
    """Test if .NET processor is available in the container"""
    try:
        # Check if processor exists (try both .exe and .dll)
        result = subprocess.run([
            "docker", "exec", "aasx-digital-webapp", 
            "ls", "-la", "/app/aas-processor/bin/Release/net6.0/AasProcessor.dll"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ .NET processor found in container")
            
            # Test processor execution with dotnet
            result = subprocess.run([
                "docker", "exec", "aasx-digital-webapp", 
                "dotnet", "/app/aas-processor/bin/Release/net6.0/AasProcessor.dll", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ .NET processor is executable")
                return True
            else:
                print(f"❌ .NET processor execution failed: {result.stderr}")
                return False
        else:
            print("❌ .NET processor not found in container")
            return False
    except Exception as e:
        print(f"❌ .NET processor test failed: {e}")
        return False

def test_aasx_file_processing():
    """Test AASX file processing functionality"""
    # Look for test AASX files
    test_files = [
        "data/aasx-examples/Example_AAS_ServoDCMotor_21.aasx",
        "data/aasx-examples/additive-manufacturing-3d-printer_converted.aasx",
        "AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
    ]
    
    test_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("⚠️  No test AASX files found, skipping file processing test")
        return True
    
    print(f"📁 Testing with AASX file: {test_file}")
    
    try:
        # Test file upload endpoint
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                "http://localhost:80/aasx/upload",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            print("✅ AASX file upload successful")
            return True
        else:
            print(f"❌ AASX file upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AASX file processing test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing AASX Integration with .NET Processor")
    print("=" * 50)
    
    tests = [
        ("Webapp Health", test_webapp_health),
        ("AASX Module", test_aasx_module),
        (".NET Processor in Container", test_dotnet_processor_in_container),
        ("AASX File Processing", test_aasx_file_processing),
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
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AASX integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the logs and configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 