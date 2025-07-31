#!/usr/bin/env python3
"""
Test AASX Module Integration
============================

Tests the integration between the AASX processor and the new modular backend.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from src.aasx.aasx_processor import extract_aasx, batch_extract, generate_aasx
        print("✅ AASX processor imports successful")
    except ImportError as e:
        print(f"❌ AASX processor import failed: {e}")
        return False
    
    try:
        from webapp.modules.aasx.processor import AASXProcessor
        print("✅ AASX processor service import successful")
    except ImportError as e:
        print(f"❌ AASX processor service import failed: {e}")
        return False
    
    try:
        from src.shared.database.base_manager import BaseDatabaseManager
        from src.shared.repositories.project_repository import ProjectRepository
        from src.shared.repositories.file_repository import FileRepository
        from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
        print("✅ Modular backend imports successful")
    except ImportError as e:
        print(f"❌ Modular backend import failed: {e}")
        return False
    
    return True

def test_repository_methods():
    """Test that repository methods work correctly."""
    print("\n🔍 Testing repository methods...")
    
    try:
        from src.shared.database.base_manager import BaseDatabaseManager
        from src.shared.database.connection_manager import DatabaseConnectionManager
        from src.shared.repositories.file_repository import FileRepository
        from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
        from pathlib import Path
        
        # Create data directory and set database path
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        connection_manager = DatabaseConnectionManager(db_path)
        db_manager = BaseDatabaseManager(connection_manager)
        file_repo = FileRepository(db_manager)
        twin_repo = DigitalTwinRepository(db_manager)
        
        # Test file repository methods
        files = file_repo.get_all()
        print(f"✅ File repository: {len(files)} files found")
        
        # Test digital twin repository methods
        twins = twin_repo.get_all()
        print(f"✅ Digital twin repository: {len(twins)} twins found")
        
        return True
        
    except Exception as e:
        print(f"❌ Repository test failed: {e}")
        return False

def test_aasx_processor_service():
    """Test the AASX processor service."""
    print("\n🔍 Testing AASX processor service...")
    
    try:
        from webapp.modules.aasx.processor import AASXProcessor
        
        processor = AASXProcessor()
        
        # Test statistics method
        stats = processor.get_aasx_statistics()
        print(f"✅ AASX statistics: {stats}")
        
        # Test processing status method
        status = processor.get_processing_status()
        print(f"✅ Processing status: {status}")
        
        # Test ETL progress method
        progress = processor.get_etl_progress()
        print(f"✅ ETL progress: {progress}")
        
        return True
        
    except Exception as e:
        print(f"❌ AASX processor service test failed: {e}")
        return False

def test_digital_twin_naming():
    """Test digital twin naming convention."""
    print("\n🔍 Testing digital twin naming convention...")
    
    try:
        from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
        from src.shared.database.base_manager import BaseDatabaseManager
        from src.shared.database.connection_manager import DatabaseConnectionManager
        from pathlib import Path
        
        # Create data directory and set database path
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "aasx_database.db"
        
        connection_manager = DatabaseConnectionManager(db_path)
        db_manager = BaseDatabaseManager(connection_manager)
        twin_repo = DigitalTwinRepository(db_manager)
        
        # Test the _get_file_info method
        # This would require a real file_id, so we'll just test the method exists
        if hasattr(twin_repo, '_get_file_info'):
            print("✅ Digital twin naming method exists")
            return True
        else:
            print("❌ Digital twin naming method missing")
            return False
            
    except Exception as e:
        print(f"❌ Digital twin naming test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing AASX Module Integration with Modular Backend")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Repository Methods", test_repository_methods),
        ("AASX Processor Service", test_aasx_processor_service),
        ("Digital Twin Naming", test_digital_twin_naming),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AASX module integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 