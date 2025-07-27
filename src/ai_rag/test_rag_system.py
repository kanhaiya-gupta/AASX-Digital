"""
Test script for the complete RAG system integration.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_rag.rag_system import RAGManager
from src.shared.utils import setup_logging


def test_rag_system():
    """Test the complete RAG system."""
    logger = setup_logging("test_rag_system")
    
    logger.info("🧪 Testing Complete RAG System")
    print("=" * 60)
    
    try:
        # Initialize RAG manager
        rag_manager = RAGManager()
        logger.info("✅ RAG Manager initialized successfully")
        
        # Test system status
        status = rag_manager.get_system_status()
        print(f"\n📊 System Status:")
        print(f"  Vector DB Connected: {status['vector_db_connected']}")
        print(f"  Available Techniques: {status['available_techniques']}")
        print(f"  Technique Names: {status['technique_names']}")
        
        # Test available techniques
        techniques = rag_manager.get_available_techniques()
        print(f"\n🔧 Available RAG Techniques:")
        for technique in techniques:
            print(f"  - {technique['name']}: {technique['description']}")
        
        # Test with a simple query
        test_query = "What are the motor specifications?"
        project_id = "fb35fa1d-5fbe-45a5-a5a9-fbaa1a6ce026"
        
        print(f"\n🔍 Testing Query: '{test_query}'")
        print(f"📁 Project ID: {project_id}")
        
        # Get technique recommendations
        recommendations = rag_manager.get_technique_recommendations(test_query)
        print(f"\n🎯 Technique Recommendations:")
        for rec in recommendations[:3]:
            print(f"  - {rec['technique_id']}: {rec['reason']} (confidence: {rec['confidence']})")
        
        # Test basic search
        print(f"\n🔍 Testing Vector Search...")
        search_results = rag_manager.search_similar_documents(
            query=test_query,
            limit=5,
            project_id=project_id
        )
        
        if search_results:
            print(f"✅ Found {len(search_results)} similar documents")
            for i, result in enumerate(search_results[:2], 1):
                score = result.get('score', 0)
                source = result.get('payload', {}).get('source_file', 'Unknown')
                print(f"  {i}. Score: {score:.3f} - File: {source}")
        else:
            print("⚠️ No search results found")
        
        # Test RAG processing (if embeddings exist)
        if search_results:
            print(f"\n🤖 Testing RAG Processing...")
            try:
                result = rag_manager.process_query(
                    query=test_query,
                    project_id=project_id,
                    search_limit=5
                )
                
                if 'error' not in result:
                    print(f"✅ RAG processing successful!")
                    print(f"  Technique Used: {result.get('technique_id', 'Unknown')}")
                    print(f"  Execution Time: {result.get('execution_time', 0):.2f}s")
                    print(f"  Search Results: {result.get('search_results_count', 0)}")
                else:
                    print(f"❌ RAG processing failed: {result['error']}")
                    
            except Exception as e:
                print(f"❌ RAG processing error: {e}")
        
        # Clean up
        rag_manager.close()
        logger.info("✅ RAG system test completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG system test failed: {e}")
        return False


def test_technique_comparison():
    """Test technique comparison functionality."""
    logger = setup_logging("test_technique_comparison")
    
    logger.info("🧪 Testing Technique Comparison")
    print("=" * 50)
    
    try:
        with RAGManager() as rag_manager:
            test_query = "Explain the motor system"
            project_id = "fb35fa1d-5fbe-45a5-a5a9-fbaa1a6ce026"
            
            print(f"🔍 Comparing techniques for: '{test_query}'")
            
            # Compare basic and hybrid techniques
            comparison = rag_manager.compare_techniques(
                query=test_query,
                technique_ids=['basic', 'hybrid'],
                project_id=project_id,
                search_limit=5
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


def main():
    """Run all RAG system tests."""
    print("🧪 Complete RAG System Test Suite")
    print("=" * 60)
    
    tests = [
        ("RAG System", test_rag_system),
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
        print("🎉 All RAG system tests passed! The system is ready for use.")
    else:
        print("⚠️ Some tests failed. Please check the configuration and setup.")


if __name__ == "__main__":
    main() 