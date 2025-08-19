"""
Configuration for AASX processing modules.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    import os
    
    # Determine which environment file to load
    node_env = os.getenv('NODE_ENV', 'development')
    is_production = node_env == 'production'
    
    if is_production:
        # Load production environment
        load_dotenv('production.env')
        print(f"✅ Loaded configuration from: {os.path.abspath('production.env')}")
    else:
        # Load local development environment
        load_dotenv('local.env')
        print(f"✅ Loaded configuration from: {os.path.abspath('local.env')}")
        
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables")
    pass

# Path to the aas-processor executable
AAS_PROCESSOR_PATH = Path(__file__).parent.parent.parent / "aas-processor" / "bin" / "Release" / "net8.0" / "AasProcessor.exe"

# Vector Database Configuration
VECTOR_DB_CONFIG = {
    'host': os.getenv('QDRANT_HOST', 'localhost'),  # Default to localhost for local development
    'port': int(os.getenv('QDRANT_PORT', 6333)),
    'collection_name': 'aasx_documents',
    'vector_size': 1536,  # OpenAI embedding dimension
    'distance': 'cosine'
}

# Embedding Models Configuration
EMBEDDING_MODELS_CONFIG = {
    'text': {
        'provider': os.getenv('TEXT_EMBEDDING_PROVIDER', 'openai'),  # openai, sentence_transformers
        'model': os.getenv('TEXT_EMBEDDING_MODEL', 'text-embedding-ada-002'),
        'api_key': os.getenv('OPENAI_API_KEY', None),
        'dimensions': int(os.getenv('TEXT_EMBEDDING_DIMENSIONS', 1536))
    },
    'image': {
        'provider': os.getenv('IMAGE_EMBEDDING_PROVIDER', 'openai'),  # openai, clip, dino
        'model': os.getenv('IMAGE_EMBEDDING_MODEL', 'clip-vit-base-patch32'),
        'api_key': os.getenv('OPENAI_API_KEY', None)
    },
    'multimodal': {
        'provider': os.getenv('MULTIMODAL_EMBEDDING_PROVIDER', 'openai'),
        'model': os.getenv('MULTIMODAL_EMBEDDING_MODEL', 'text-embedding-ada-002')
    }
}

# Processing Configuration
PROCESSING_CONFIG = {
    'batch_size': int(os.getenv('EMBEDDING_BATCH_SIZE', 50)),
    'max_retries': int(os.getenv('EMBEDDING_MAX_RETRIES', 3)),
    'timeout': int(os.getenv('TIMEOUT', 30)),
    'chunk_size': int(os.getenv('TEXT_CHUNK_SIZE', 1000)),
    'max_file_size': int(os.getenv('MAX_FILE_SIZE_MB', 100)) * 1024 * 1024  # Convert MB to bytes
}

# Output Configuration
OUTPUT_CONFIG = {
    'embeddings_dir': 'embeddings',
    'metadata_file': 'embedding_metadata.json',
    'vector_db_export': 'vector_db_export.json'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file': os.getenv('LOG_FILE', 'logs/aasx_processing.log')
}

# Print configuration status
def print_config_status():
    """Print the current configuration status."""
    print("\n🔧 Configuration Status:")
    print(f"  Vector DB Host: {VECTOR_DB_CONFIG['host']}")
    print(f"  Vector DB Port: {VECTOR_DB_CONFIG['port']}")
    print(f"  OpenAI API Key: {'✅ Set' if EMBEDDING_MODELS_CONFIG['text']['api_key'] else '❌ Not Set'}")
    print(f"  Log Level: {LOGGING_CONFIG['level']}")
    print(f"  Environment: {'Production' if os.getenv('NODE_ENV') == 'production' else 'Development'}")

# Auto-print status when module is imported
if __name__ != "__main__":
    print_config_status() 