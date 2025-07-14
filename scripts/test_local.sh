#!/bin/bash

# AASX Digital Twin Analytics Framework - Local Testing Script
# Tests the framework with the new src folder structure

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if we're in the right directory
check_directory() {
    log "Checking project structure..."
    
    if [[ ! -d "src" ]]; then
        error "src directory not found! Make sure you're in the project root."
    fi
    
    if [[ ! -d "webapp" ]]; then
        error "webapp directory not found! Make sure you're in the project root."
    fi
    
    if [[ ! -f "main.py" ]]; then
        error "main.py not found! Make sure you're in the project root."
    fi
    
    log "✅ Project structure looks good"
}

# Check Python environment
check_python() {
    log "Checking Python environment..."
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log "Python version: $python_version"
    
    # Check if virtual environment is active
    if [[ -z "$VIRTUAL_ENV" ]]; then
        warn "No virtual environment detected. Consider creating one:"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate  # Linux/Mac"
        echo "  venv\\Scripts\\activate     # Windows"
    else
        log "✅ Virtual environment active: $VIRTUAL_ENV"
    fi
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    # Check if requirements.txt exists
    if [[ ! -f "requirements.txt" ]]; then
        error "requirements.txt not found!"
    fi
    
    # Check key packages
    packages=("fastapi" "uvicorn" "neo4j" "qdrant-client" "openai")
    
    for package in "${packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            log "✅ $package is installed"
        else
            warn "$package is not installed"
        fi
    done
}

# Check Docker
check_docker() {
    log "Checking Docker..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running. Please start Docker Desktop."
    fi
    
    log "✅ Docker is running"
}

# Start databases
start_databases() {
    log "Starting databases..."
    
    # Check if databases are already running
    if docker-compose ps | grep -q "Up"; then
        log "Databases are already running"
        return
    fi
    
    # Start databases
    docker-compose up -d
    
    # Wait for databases to be ready
    log "Waiting for databases to be ready..."
    sleep 30
    
    # Check database status
    if docker-compose ps | grep -q "Up"; then
        log "✅ Databases are running"
    else
        error "Failed to start databases"
    fi
}

# Test imports
test_imports() {
    log "Testing Python imports..."
    
    # Test main imports
    python3 -c "
import sys
sys.path.append('.')
try:
    from src.aasx.aasx_etl_pipeline import AasxEtlPipeline
    print('✅ AASX ETL Pipeline import successful')
except ImportError as e:
    print(f'❌ AASX ETL Pipeline import failed: {e}')

try:
    from src.kg_neo4j.graph_analyzer import GraphAnalyzer
    print('✅ Knowledge Graph import successful')
except ImportError as e:
    print(f'❌ Knowledge Graph import failed: {e}')

try:
    from src.ai_rag.ai_rag import AIRagSystem
    print('✅ AI/RAG System import successful')
except ImportError as e:
    print(f'❌ AI/RAG System import failed: {e}')

try:
    from webapp.app import app
    print('✅ Webapp import successful')
except ImportError as e:
    print(f'❌ Webapp import failed: {e}')
"
}

# Test database connections
test_databases() {
    log "Testing database connections..."
    
    # Test Neo4j
    if curl -s http://localhost:7474 > /dev/null; then
        log "✅ Neo4j is accessible"
    else
        warn "Neo4j is not accessible"
    fi
    
    # Test Qdrant
    if curl -s http://localhost:6333/health > /dev/null; then
        log "✅ Qdrant is accessible"
    else
        warn "Qdrant is not accessible"
    fi
}

# Test application startup
test_application() {
    log "Testing application startup..."
    
    # Start application in background
    python3 main.py start &
    APP_PID=$!
    
    # Wait for application to start
    sleep 10
    
    # Test health endpoint
    if curl -s http://localhost:8000/health > /dev/null; then
        log "✅ Application is running and responding"
    else
        warn "Application is not responding"
    fi
    
    # Stop application
    kill $APP_PID 2>/dev/null || true
    wait $APP_PID 2>/dev/null || true
}

# Main test function
main() {
    log "🧪 Starting AASX Digital Twin Analytics Framework Local Tests"
    log "Testing with new src folder structure..."
    
    # Run all checks
    check_directory
    check_python
    check_dependencies
    check_docker
    start_databases
    test_imports
    test_databases
    test_application
    
    log ""
    log "🎉 All tests completed!"
    log ""
    log "📋 Next steps:"
    log "   1. Start the application: python main.py start"
    log "   2. Open browser: http://localhost:8000"
    log "   3. Test the ETL pipeline with sample AASX files"
    log "   4. Explore the knowledge graph"
    log "   5. Try the AI/RAG system"
    log ""
    log "🔧 Useful commands:"
    log "   - View logs: tail -f logs/*.log"
    log "   - Check status: docker-compose ps"
    log "   - Restart services: docker-compose restart"
    log "   - Stop everything: docker-compose down"
}

# Run main function
main "$@" 