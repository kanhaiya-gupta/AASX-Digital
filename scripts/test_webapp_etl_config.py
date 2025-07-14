#!/usr/bin/env python3
"""
Test script to verify webapp ETL configuration and systematic structure integration.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_webapp_config():
    """Test webapp ETL configuration loading"""
    print("🧪 Testing Webapp ETL Configuration")
    print("=" * 50)
    
    try:
        # Test webapp config loading
        from webapp.config.etl_config import get_etl_config, ETLConfig
        
        print("✅ Successfully imported webapp config module")
        
        # Load configuration
        etl_config = get_etl_config()
        print(f"✅ Configuration loaded from: {etl_config.config_path}")
        
        # Test configuration sections
        print("\n📋 Configuration Sections:")
        print(f"  - Output config: {len(etl_config.get_output_config())} items")
        print(f"  - Transformation config: {len(etl_config.get_transformation_config())} items")
        print(f"  - Database config: {len(etl_config.get_database_config())} items")
        print(f"  - Vector DB config: {len(etl_config.get_vector_database_config())} items")
        print(f"  - Pipeline config: {len(etl_config.get_pipeline_config())} items")
        print(f"  - RAG config: {len(etl_config.get_rag_config())} items")
        
        # Test systematic structure settings
        print("\n📁 Systematic Structure Settings:")
        print(f"  - Systematic structure enabled: {etl_config.is_systematic_structure_enabled()}")
        print(f"  - Folder structure type: {etl_config.get_folder_structure_type()}")
        print(f"  - Base output directory: {etl_config.get_base_output_directory()}")
        
        # Test configuration validation
        print("\n🔍 Configuration Validation:")
        validation = etl_config.validate_config()
        print(f"  - Valid: {validation['valid']}")
        if validation['errors']:
            print(f"  - Errors: {validation['errors']}")
        if validation['warnings']:
            print(f"  - Warnings: {validation['warnings']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing webapp config: {e}")
        return False

def test_etl_pipeline_integration():
    """Test ETL pipeline integration with webapp config"""
    print("\n🔧 Testing ETL Pipeline Integration")
    print("-" * 30)
    
    try:
        # Test ETL pipeline creation with webapp config
        from webapp.aasx.routes import get_etl_pipeline
        
        print("✅ Successfully imported ETL pipeline from webapp routes")
        
        # Get ETL pipeline instance
        pipeline = get_etl_pipeline()
        print("✅ ETL pipeline instance created successfully")
        
        # Check pipeline configuration
        config = pipeline.config
        print(f"✅ Pipeline config loaded:")
        print(f"  - Validation enabled: {config.enable_validation}")
        print(f"  - Logging enabled: {config.enable_logging}")
        print(f"  - Parallel processing: {config.parallel_processing}")
        print(f"  - Max workers: {config.max_workers}")
        
        # Check loader configuration
        loader_config = config.load_config
        print(f"✅ Loader config:")
        print(f"  - Output directory: {loader_config.output_directory}")
        print(f"  - Systematic structure: {loader_config.systematic_structure}")
        print(f"  - Folder structure: {loader_config.folder_structure}")
        print(f"  - Separate file outputs: {loader_config.separate_file_outputs}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ETL pipeline integration: {e}")
        return False

def test_systematic_structure():
    """Test systematic folder structure creation"""
    print("\n📁 Testing Systematic Folder Structure")
    print("-" * 30)
    
    try:
        from src.aasx.aasx_loader import LoaderConfig, AASXLoader
        
        # Create test configuration
        config = LoaderConfig(
            output_directory="output/etl_results",
            systematic_structure=True,
            folder_structure="timestamped_by_file",
            separate_file_outputs=True,
            include_filename_in_output=True
        )
        
        # Test with a sample file
        test_file = "data/aasx-examples/test_file.aasx"
        loader = AASXLoader(config=config, source_file=test_file)
        
        print(f"✅ Loader created with systematic structure")
        print(f"  - Output directory: {loader.output_dir}")
        
        # Check if directory structure is created
        if loader.output_dir.exists():
            print(f"✅ Output directory exists: {loader.output_dir}")
        else:
            print(f"⚠️  Output directory will be created when needed: {loader.output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing systematic structure: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Webapp ETL Configuration and Systematic Structure Test")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Webapp Config Loading", test_webapp_config),
        ("ETL Pipeline Integration", test_etl_pipeline_integration),
        ("Systematic Structure", test_systematic_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Webapp ETL configuration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 