"""
Test script for vector embedding implementation.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_rag.vector_embedding_upload import VectorEmbeddingUploader
from src.shared.utils import setup_logging


def test_vector_embedding():
    """Test the vector embedding functionality."""
    logger = setup_logging("test_vector_embedding")
    
    logger.info("Starting vector embedding test")
    
    try:
        # Initialize the uploader
        uploader = VectorEmbeddingUploader()
        logger.info("✅ Vector embedding uploader initialized successfully")
        
        # Test with a specific project
        project_id = "fb35fa1d-5fbe-45a5-a5a9-fbaa1a6ce026"  # Use actual project ID from output/projects
        
        logger.info(f"Testing with project: {project_id}")
        
        # Process the project
        result = uploader.process_project(project_id)
        
        logger.info(f"Processing result: {result}")
        
        if result.get('status') == 'completed':
            logger.info("✅ Project processing completed successfully")
            logger.info(f"Files processed: {result.get('files_processed', 0)}")
            logger.info(f"Embeddings created: {result.get('embeddings_created', 0)}")
            
            # Test search functionality
            logger.info("Testing search functionality...")
            search_results = uploader.search_similar("motor", limit=5)
            
            if search_results:
                logger.info("✅ Search functionality working")
                logger.info(f"Found {len(search_results)} similar documents")
                
                for i, result in enumerate(search_results[:3], 1):
                    logger.info(f"Result {i}: Score {result['score']:.3f} - {result['payload'].get('source_file', 'Unknown')}")
            else:
                logger.warning("⚠️ No search results found")
        
        else:
            logger.error(f"❌ Project processing failed: {result.get('error', 'Unknown error')}")
        
        # Clean up
        uploader.close()
        logger.info("✅ Test completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    logger = setup_logging("test_configuration")
    
    try:
        from src.shared.config import VECTOR_DB_CONFIG, EMBEDDING_MODELS_CONFIG
        
        logger.info("Testing configuration...")
        logger.info(f"Vector DB config: {VECTOR_DB_CONFIG}")
        logger.info(f"Embedding models config: {EMBEDDING_MODELS_CONFIG}")
        
        # Check if required environment variables are set
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"⚠️ Missing environment variables: {missing_vars}")
            logger.info("Please set these environment variables to test OpenAI embeddings")
        else:
            logger.info("✅ All required environment variables are set")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False


def test_project_structure():
    """Test project structure and file discovery."""
    logger = setup_logging("test_project_structure")
    
    try:
        from src.shared.management import ProjectManager
        
        logger.info("Testing project structure...")
        
        # Initialize project manager
        project_manager = ProjectManager()
        
        # List projects
        projects = project_manager.list_projects()
        logger.info(f"Found {len(projects)} projects")
        
        if projects:
            # Test with first project
            project = projects[0]
            project_id = project.get('project_id')
            
            if project_id:
                logger.info(f"Testing with project: {project_id}")
                
                # List project files
                files = project_manager.list_project_files(project_id)
                logger.info(f"Found {len(files)} files in project")
                
                for file_info in files[:3]:  # Show first 3 files
                    logger.info(f"  - {file_info.get('filename', 'Unknown')} (ID: {file_info.get('file_id', 'Unknown')})")
                
                return True
            else:
                logger.error("❌ No project ID found")
                return False
        else:
            logger.warning("⚠️ No projects found")
            return False
        
    except Exception as e:
        logger.error(f"❌ Project structure test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Vector Embedding Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Project Structure", test_project_structure),
        ("Vector Embedding", test_vector_embedding)
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
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Vector embedding system is ready.")
    else:
        print("⚠️ Some tests failed. Please check the configuration and setup.")


if __name__ == "__main__":
    main() 