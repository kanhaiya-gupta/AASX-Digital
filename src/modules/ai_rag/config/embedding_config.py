"""
AI/RAG Configuration for embedding models and vector database.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
try:
    # Determine which environment file to load
    node_env = os.getenv('NODE_ENV', 'development')
    is_production = node_env == 'production'
    
    if is_production:
        # Load production environment
        load_dotenv('production.env')
        print(f"✅ Loaded AI/RAG configuration from: {os.path.abspath('production.env')}")
    else:
        # Load local development environment
        load_dotenv('local.env')
        print(f"✅ Loaded AI/RAG configuration from: {os.path.abspath('local.env')}")
        
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables")
    pass

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
    """Print the current AI/RAG configuration status."""
    print("\n🔧 AI/RAG Configuration Status:")
    print(f"  Vector DB Host: {VECTOR_DB_CONFIG['host']}")
    print(f"  Vector DB Port: {VECTOR_DB_CONFIG['port']}")
    print(f"  OpenAI API Key: {'✅ Set' if EMBEDDING_MODELS_CONFIG['text']['api_key'] else '❌ Not Set'}")
    print(f"  Text Embedding Provider: {EMBEDDING_MODELS_CONFIG['text']['provider']}")
    print(f"  Text Embedding Model: {EMBEDDING_MODELS_CONFIG['text']['model']}")
    print(f"  Log Level: {LOGGING_CONFIG['level']}")
    print(f"  Environment: {'Production' if os.getenv('NODE_ENV') == 'production' else 'Development'}")

# Auto-print status when module is imported
if __name__ != "__main__":
    print_config_status() 