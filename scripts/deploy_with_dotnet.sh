#!/bin/bash

# Deploy AASX Digital Twin Analytics Framework with .NET Processor
# This script ensures the .NET AAS processor is built and available

set -e  # Exit on any error

echo "🚀 Deploying AASX Digital Twin Analytics Framework with .NET Processor"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Build .NET processor locally first (for testing)
build_dotnet_locally() {
    print_status "Building .NET AAS processor locally..."
    
    if [ ! -d "aas-processor" ]; then
        print_error "aas-processor directory not found!"
        exit 1
    fi
    
    cd aas-processor
    
    # Check if .NET is available
    if ! command -v dotnet &> /dev/null; then
        print_warning ".NET 6.0 SDK not found locally. This is okay for Docker deployment."
        cd ..
        return 0
    fi
    
    # Build the processor
    print_status "Restoring .NET packages..."
    dotnet restore
    
    print_status "Building .NET project..."
    dotnet build --configuration Release
    
    # Check if build was successful
    if [ -f "bin/Release/net6.0/AasProcessor" ] || [ -f "bin/Release/net6.0/AasProcessor.exe" ]; then
        print_success ".NET AAS processor built successfully"
    else
        print_error ".NET AAS processor build failed"
        exit 1
    fi
    
    cd ..
}

# Build Docker images
build_docker_images() {
    print_status "Building Docker images with .NET processor..."
    
    # Build all services
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    print_success "Docker images built successfully"
}

# Test .NET processor in container
test_dotnet_in_container() {
    print_status "Testing .NET processor in container..."
    
    # Run the test script in a temporary container
    docker run --rm \
        -v "$(pwd)/scripts:/app/scripts" \
        -v "$(pwd)/src:/app/src" \
        aasx-webapp \
        python3 /app/scripts/test_docker_dotnet.py
    
    if [ $? -eq 0 ]; then
        print_success ".NET processor test passed"
    else
        print_error ".NET processor test failed"
        exit 1
    fi
}

# Start the framework
start_framework() {
    print_status "Starting AASX Digital Twin Analytics Framework..."
    
    # Stop any existing containers
    docker-compose -f docker-compose.prod.yml down
    
    # Start the framework
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Framework started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for webapp
    print_status "Waiting for webapp..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Webapp is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_warning "Webapp health check timed out, but continuing..."
    fi
    
    # Wait for Neo4j
    print_status "Waiting for Neo4j..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:7474 > /dev/null 2>&1; then
            print_success "Neo4j is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_warning "Neo4j health check timed out, but continuing..."
    fi
}

# Show deployment summary
show_summary() {
    echo ""
    echo "🎉 Deployment Complete!"
    echo "======================"
    echo ""
    echo "🌐 Access your framework:"
    echo "   Main Dashboard: http://localhost:8000"
    echo "   AASX ETL Pipeline: http://localhost:8000/aasx"
    echo "   Knowledge Graph: http://localhost:8000/kg-neo4j"
    echo "   AI/RAG System: http://localhost:8000/ai-rag"
    echo "   Twin Registry: http://localhost:8000/twin-registry"
    echo ""
    echo "🗄️  Database Access:"
    echo "   Neo4j Browser: http://localhost:7474"
    echo "   Qdrant: http://localhost:6333"
    echo ""
    echo "📊 Monitor your deployment:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f"
    echo ""
    echo "🛑 Stop the framework:"
    echo "   docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo "✅ Your framework now has full .NET AAS processor support!"
}

# Main deployment function
main() {
    echo "Starting deployment at $(date)"
    echo ""
    
    # Run deployment steps
    check_docker
    build_dotnet_locally
    build_docker_images
    test_dotnet_in_container
    start_framework
    wait_for_services
    show_summary
    
    echo ""
    print_success "Deployment completed successfully at $(date)"
}

# Run main function
main "$@" 