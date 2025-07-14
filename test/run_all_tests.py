#!/usr/bin/env python3
"""
Comprehensive Test Runner for QI Digital Platform

This script runs all tests in the proper order:
1. Unit tests (basic functionality)
2. Data quality tests (data integrity and validation)
3. AASX tests (processing pipeline)
4. Web application tests (routes and endpoints)
5. Performance tests (speed and resource usage)
6. Error handling tests (failure scenarios)
7. Integration tests (cross-module functionality)
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add parent directory to path
sys.path.append('..')

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"TEST: {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n{title}")
    print("-" * 40)

def run_test_file(test_file):
    """Run a single test file and return success status"""
    print(f"  Running: {test_file}")
    
    try:
        # Run the test file from the test directory
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd="."  # Run from current test directory
        )
        
        if result.returncode == 0:
            print(f"  PASSED: {test_file}")
            return True
        else:
            print(f"  FAILED: {test_file}")
            print(f"  Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ERROR: {test_file} - {e}")
        return False

def run_test_category(category_path, category_name):
    """Run all tests in a category"""
    print_section(f"Running {category_name} Tests")
    
    if not os.path.exists(category_path):
        print(f"  WARNING: Category {category_name} not found: {category_path}")
        return 0, 0
    
    test_files = []
    for file in os.listdir(category_path):
        if file.startswith('test_') and file.endswith('.py'):
            test_files.append(os.path.join(category_path, file))
    
    if not test_files:
        print(f"  WARNING: No test files found in {category_name}")
        return 0, 0
    
    # Sort test files for consistent execution order
    test_files.sort()
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
    
    return passed, total

def check_dependencies():
    """Check if required dependencies are available"""
    print_section("Checking Dependencies")
    
    # Check Python version
    python_version = sys.version_info
    print(f"  Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 9):
        print("  WARNING: Python 3.9+ recommended")
    
    # Check .NET processor
    try:
        from src.aasx.dotnet_bridge import DotNetAasBridge
        bridge = DotNetAasBridge()
        if bridge.is_available():
            print("  OK: .NET AAS processor available")
        else:
            print("  WARNING: .NET AAS processor not available")
    except ImportError:
        print("  WARNING: .NET bridge not available")
    
    # Check AASX files
    aasx_dir = Path("../AasxPackageExplorer/content-for-demo")
    if aasx_dir.exists():
        aasx_files = list(aasx_dir.glob("*.aasx"))
        print(f"  OK: Found {len(aasx_files)} AASX files")
    else:
        print("  WARNING: AASX files directory not found")
    
    # Check optional dependencies
    try:
        import psutil
        print("  OK: psutil available for performance tests")
    except ImportError:
        print("  WARNING: psutil not available (performance tests may be limited)")

def main():
    """Main test runner"""
    print_header("QI Digital Platform - Comprehensive Test Suite")
    print(f"Test runner started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check dependencies first
    check_dependencies()
    
    # Define test categories in execution order
    test_categories = [
        ("unit", "Unit"),
        ("data_quality", "Data Quality"),
        ("aasx", "AASX Processing"),
        ("kg_neo4j", "Neo4j Integration"),
        ("webapp", "Web Application"),
        ("performance", "Performance"),
        ("error_handling", "Error Handling"),
        ("integration", "Integration")
    ]
    
    total_passed = 0
    total_tests = 0
    
    # Run tests in order
    for category_path, category_name in test_categories:
        passed, total = run_test_category(category_path, category_name)
        total_passed += passed
        total_tests += total
    
    # Print summary
    print_header("Test Summary")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("EXCELLENT: All critical tests passed!")
        elif success_rate >= 75:
            print("GOOD: Most tests passed.")
        elif success_rate >= 50:
            print("WARNING: Some tests failed.")
        else:
            print("CRITICAL: Many tests failed!")
    
    print(f"\nTest run completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return appropriate exit code
    if total_tests == 0:
        return 0
    elif total_passed == total_tests:
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 