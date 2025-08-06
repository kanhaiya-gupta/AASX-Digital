"""
Test script for Physics Modeling Services
Verifies that all services can be imported and initialized correctly
"""

import sys
import os
import logging

# Add the webapp directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_service_imports():
    """Test that all services can be imported correctly"""
    try:
        from services import PhysicsModelService, SimulationService, ValidationService, UseCaseService
        logger.info("✅ All services imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import services: {e}")
        return False

def test_service_initialization():
    """Test that all services can be initialized"""
    try:
        from services import PhysicsModelService, SimulationService, ValidationService, UseCaseService
        
        # Initialize services
        physics_service = PhysicsModelService()
        simulation_service = SimulationService()
        validation_service = ValidationService()
        use_case_service = UseCaseService()
        
        logger.info("✅ All services initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        return False

def test_use_case_service():
    """Test UseCaseService functionality"""
    try:
        from services import UseCaseService
        
        service = UseCaseService()
        
        # Test getting use cases
        use_cases = service.get_use_cases()
        logger.info(f"✅ Retrieved {len(use_cases)} use cases")
        
        # Test getting use case templates
        templates = service.get_use_case_templates()
        logger.info(f"✅ Retrieved {len(templates)} use case templates")
        
        # Test getting statistics
        stats = service.get_use_case_statistics()
        logger.info(f"✅ Retrieved use case statistics: {stats['total_use_cases']} total use cases")
        
        return True
    except Exception as e:
        logger.error(f"❌ UseCaseService test failed: {e}")
        return False

def test_physics_model_service():
    """Test PhysicsModelService functionality"""
    try:
        from services import PhysicsModelService
        
        service = PhysicsModelService()
        
        # Test getting available twins
        twins = service.get_available_twins()
        logger.info(f"✅ Retrieved {len(twins)} available twins")
        
        # Test listing models (should work even if no models exist)
        models = service.list_models()
        logger.info(f"✅ Retrieved {len(models)} physics models")
        
        return True
    except Exception as e:
        logger.error(f"❌ PhysicsModelService test failed: {e}")
        return False

def test_simulation_service():
    """Test SimulationService functionality"""
    try:
        from services import SimulationService
        
        service = SimulationService()
        
        # Test getting active simulations count
        count = service.get_active_simulations_count()
        logger.info(f"✅ Active simulations count: {count}")
        
        # Test listing simulations
        simulations = service.list_simulations()
        logger.info(f"✅ Retrieved {len(simulations)} simulations")
        
        return True
    except Exception as e:
        logger.error(f"❌ SimulationService test failed: {e}")
        return False

def test_validation_service():
    """Test ValidationService functionality"""
    try:
        from services import ValidationService
        
        service = ValidationService()
        
        # Test listing validations
        validations = service.list_validations()
        logger.info(f"✅ Retrieved {len(validations)} validations")
        
        return True
    except Exception as e:
        logger.error(f"❌ ValidationService test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🧪 Starting Physics Modeling Services Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Service Imports", test_service_imports),
        ("Service Initialization", test_service_initialization),
        ("UseCaseService", test_use_case_service),
        ("PhysicsModelService", test_physics_model_service),
        ("SimulationService", test_simulation_service),
        ("ValidationService", test_validation_service),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                logger.info(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test FAILED with exception: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Service layer is working correctly.")
        return True
    else:
        logger.error("⚠️ Some tests failed. Please check the service layer implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 