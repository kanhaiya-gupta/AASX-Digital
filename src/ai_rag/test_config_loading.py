"""
Test script to verify configuration loading from production.env
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_config_loading():
    """Test that configuration is properly loaded from production.env"""
    print("🧪 Testing Configuration Loading")
    print("=" * 50)
    
    try:
        # Import config to trigger loading
        from src.shared.config import (
            VECTOR_DB_CONFIG, 
            EMBEDDING_MODELS_CONFIG, 
            PROCESSING_CONFIG,
            LOGGING_CONFIG
        )
        
        print("\n✅ Configuration loaded successfully!")
        
        # Test specific values from production.env
        print("\n📋 Configuration Values:")
        print(f"  Qdrant Host: {VECTOR_DB_CONFIG['host']}")
        print(f"  Qdrant Port: {VECTOR_DB_CONFIG['port']}")
        print(f"  OpenAI API Key: {'✅ Present' if EMBEDDING_MODELS_CONFIG['text']['api_key'] else '❌ Missing'}")
        print(f"  Log Level: {LOGGING_CONFIG['level']}")
        print(f"  Timeout: {PROCESSING_CONFIG['timeout']} seconds")
        
        # Test OpenAI API key specifically
        openai_key = EMBEDDING_MODELS_CONFIG['text']['api_key']
        if openai_key:
            print(f"  OpenAI Key Preview: {openai_key[:20]}...")
            print("✅ OpenAI API key loaded from production.env")
        else:
            print("❌ OpenAI API key not found in production.env")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_environment_file():
    """Test that production.env file exists and is readable"""
    print("\n📁 Testing Environment File")
    print("=" * 30)
    
    env_file = Path(__file__).parent.parent.parent / "production.env"
    
    if env_file.exists():
        print(f"✅ Environment file found: {env_file}")
        
        # Read and display some key values
        with open(env_file, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        key_vars = ['OPENAI_API_KEY', 'QDRANT_HOST', 'QDRANT_PORT', 'LOG_LEVEL']
        
        print("\n🔑 Key Environment Variables:")
        for line in lines:
            for var in key_vars:
                if line.startswith(var + '='):
                    if 'API_KEY' in var:
                        value = line.split('=', 1)[1]
                        print(f"  {var}: {value[:20]}..." if len(value) > 20 else f"  {var}: {value}")
                    else:
                        print(f"  {line}")
        
        return True
    else:
        print(f"❌ Environment file not found: {env_file}")
        return False

def main():
    """Run all configuration tests"""
    print("🔧 Configuration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment File", test_environment_file),
        ("Configuration Loading", test_config_loading)
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
        print("🎉 All configuration tests passed! Ready to proceed with vector embedding.")
    else:
        print("⚠️ Some configuration tests failed. Please check your production.env file.")

if __name__ == "__main__":
    main() 