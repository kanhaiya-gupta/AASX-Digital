"""
Comprehensive test script for the complete RAG system with all techniques.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_rag.rag_system import RAGManager
from ai_rag.rag_system.rag_techniques import (
    BasicRAGTechnique,
    HybridRAGTechnique,
    MultiStepRAGTechnique,
    GraphRAGTechnique,
    AdvancedRAGTechnique
)
from src.shared.utils import setup_logging


def test_rag_techniques_import():
    """Test that all RAG techniques can be imported and initialized."""
    logger = setup_logging("test_rag_techniques")
    
    logger.info("🧪 Testing RAG Techniques Import")
    print("=" * 50)
    
    techniques = [
        ("Basic RAG", BasicRAGTechnique),
        ("Hybrid RAG", HybridRAGTechnique),
        ("Multi-Step RAG", MultiStepRAGTechnique),
        ("Graph RAG", GraphRAGTechnique),
        ("Advanced RAG", AdvancedRAGTechnique)
    ]
    
    results = {}
    
    for technique_name, technique_class in techniques:
        try:
            # Initialize technique
            technique = technique_class()
            
            # Test basic properties
            assert hasattr(technique, 'name'), f"{technique_name} missing 'name' attribute"
            assert hasattr(technique, 'description'), f"{technique_name} missing 'description' attribute"
            assert hasattr(technique, 'execute'), f"{technique_name} missing 'execute' method"
            
            # Test technique info
            info = technique.get_technique_info()
            assert 'name' in info, f"{technique_name} info missing 'name'"
            assert 'description' in info, f"{technique_name} info missing 'description'"
            
            results[technique_name] = True
            print(f"✅ {technique_name}: {info['name']} - {info['description']}")
            
        except Exception as e:
            results[technique_name] = False
            print(f"❌ {technique_name}: {e}")
    
    return results


def test_rag_manager_integration():
    """Test RAG manager integration with all techniques."""
    logger = setup_logging("test_rag_manager")
    
    logger.info("🧪 Testing RAG Manager Integration")
    print("=" * 50)
    
    try:
        # Initialize RAG manager
        rag_manager = RAGManager()
        
        # Test system status
        status = rag_manager.get_system_status()
        print(f"✅ RAG Manager initialized successfully")
        print(f"  Vector DB Connected: {status['vector_db_connected']}")
        print(f"  Available Techniques: {status['available_techniques']}")
        print(f"  Technique Names: {status['technique_names']}")
        
        # Test available techniques
        techniques = rag_manager.get_available_techniques()
        print(f"\n🔧 Available Techniques:")
        for technique in techniques:
            print(f"  - {technique['name']}: {technique['description']}")
        
        # Test technique recommendations
        test_query = "What are the motor specifications and how do they relate to the system?"
        recommendations = rag_manager.get_technique_recommendations(test_query)
        print(f"\n🎯 Technique Recommendations for: '{test_query}'")
        for rec in recommendations:
            print(f"  - {rec['technique_id']}: {rec['reason']} (confidence: {rec['confidence']})")
        
        rag_manager.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG Manager integration test failed: {e}")
        return False


def test_individual_techniques():
    """Test individual RAG techniques with mock data."""
    logger = setup_logging("test_individual_techniques")
    
    logger.info("🧪 Testing Individual RAG Techniques")
    print("=" * 50)
    
    # Mock search results for testing
    mock_search_results = [
        {
            'id': 'doc_1',
            'score': 0.95,
            'payload': {
                'content_preview': 'Motor specifications: 12V DC motor with 1000 RPM max speed',
                'source_file': 'motor_specs.json',
                'project_id': 'test_project'
            }
        },
        {
            'id': 'doc_2', 
            'score': 0.87,
            'payload': {
                'content_preview': 'System integration details for motor control system',
                'source_file': 'system_integration.json',
                'project_id': 'test_project'
            }
        }
    ]
    
    techniques = [
        ("Basic RAG", BasicRAGTechnique),
        ("Hybrid RAG", HybridRAGTechnique),
        ("Multi-Step RAG", MultiStepRAGTechnique),
        ("Graph RAG", GraphRAGTechnique),
        ("Advanced RAG", AdvancedRAGTechnique)
    ]
    
    test_query = "What are the motor specifications?"
    results = {}
    
    for technique_name, technique_class in techniques:
        try:
            # Initialize technique
            technique = technique_class()
            
            # Test technique execution with mock data
            # Note: This won't actually call OpenAI, just test the structure
            technique_info = technique.get_technique_info()
            
            # Test context combination
            combined_context = technique.combine_contexts(mock_search_results)
            assert isinstance(combined_context, str), f"{technique_name} combine_contexts should return string"
            
            # Test parameter validation
            is_valid = technique.validate_parameters()
            assert isinstance(is_valid, bool), f"{technique_name} validate_parameters should return boolean"
            
            results[technique_name] = True
            print(f"✅ {technique_name}: {technique_info['name']}")
            print(f"   Description: {technique_info['description']}")
            print(f"   Context length: {len(combined_context)} characters")
            
        except Exception as e:
            results[technique_name] = False
            print(f"❌ {technique_name}: {e}")
    
    return results


def test_technique_comparison():
    """Test technique comparison functionality."""
    logger = setup_logging("test_technique_comparison")
    
    logger.info("🧪 Testing Technique Comparison")
    print("=" * 50)
    
    try:
        with RAGManager() as rag_manager:
            test_query = "Explain the motor system and its specifications"
            project_id = "fb35fa1d-5fbe-45a5-a5a9-fbaa1a6ce026"
            
            print(f"🔍 Comparing techniques for: '{test_query}'")
            
            # Test with a subset of techniques to avoid API costs
            comparison = rag_manager.compare_techniques(
                query=test_query,
                technique_ids=['basic', 'hybrid'],  # Test with 2 techniques
                project_id=project_id,
                search_limit=3
            )
            
            print(f"\n📊 Comparison Results:")
            print(f"  Techniques Compared: {comparison['techniques_compared']}")
            print(f"  Search Results: {comparison['search_results_count']}")
            
            results = comparison.get('results', {})
            for technique_id, result in results.items():
                status = result.get('status', 'unknown')
                if status == 'success':
                    exec_time = result.get('result', {}).get('execution_time', 0)
                    print(f"  ✅ {technique_id}: {exec_time:.2f}s")
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"  ❌ {technique_id}: {error}")
            
            best_technique = comparison.get('best_technique')
            if best_technique:
                print(f"  🏆 Best Technique: {best_technique}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Technique comparison test failed: {e}")
        return False


def test_configuration_loading():
    """Test that configuration is properly loaded."""
    logger = setup_logging("test_configuration")
    
    logger.info("🧪 Testing Configuration Loading")
    print("=" * 50)
    
    try:
        from src.shared.config import (
            VECTOR_DB_CONFIG, 
            EMBEDDING_MODELS_CONFIG, 
            PROCESSING_CONFIG,
            LOGGING_CONFIG
        )
        
        print("✅ Configuration loaded successfully!")
        print(f"  Qdrant Host: {VECTOR_DB_CONFIG['host']}")
        print(f"  Qdrant Port: {VECTOR_DB_CONFIG['port']}")
        print(f"  OpenAI API Key: {'✅ Present' if EMBEDDING_MODELS_CONFIG['text']['api_key'] else '❌ Missing'}")
        print(f"  Log Level: {LOGGING_CONFIG['level']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration loading failed: {e}")
        return False


def main():
    """Run all comprehensive tests."""
    print("🧪 Complete RAG System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("RAG Techniques Import", test_rag_techniques_import),
        ("Individual Techniques", test_individual_techniques),
        ("RAG Manager Integration", test_rag_manager_integration),
        ("Technique Comparison", test_technique_comparison)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} {test_name} test")
        except Exception as e:
            results[test_name] = False
            print(f"❌ FAILED {test_name} test: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All RAG system tests passed! The system is ready for production use.")
        print("\n🚀 Next Steps:")
        print("  1. Process your AASX projects to create embeddings")
        print("  2. Test different RAG techniques on your data")
        print("  3. Integrate with your web application")
        print("  4. Monitor and optimize performance")
    else:
        print("⚠️ Some tests failed. Please check the configuration and setup.")
        print("\n🔧 Troubleshooting:")
        print("  1. Ensure production.env is properly configured")
        print("  2. Check that Qdrant is running")
        print("  3. Verify OpenAI API key is set")
        print("  4. Install all required dependencies")


if __name__ == "__main__":
    main() 