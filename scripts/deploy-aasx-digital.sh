#!/bin/bash

# AASX Digital Twin Analytics Framework - Production Deployment Script
# For domain: www.aasx-digital.de
# Framework: FastAPI with .NET AAS Processor
# Docker Compose: manifests/framework/docker-compose.aasx-digital.yml

set -e

echo "🚀 Starting AASX Digital Twin Analytics Framework Deployment..."
echo "🌐 Domain: www.aasx-digital.de"
echo "⚡ Framework: FastAPI with .NET AAS Processor"
echo "🐳 Docker Compose: manifests/framework/docker-compose.aasx-digital.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check prerequisites
print_header "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Prerequisites check passed!"

# .NET AAS Processor Setup
print_header "Setting up .NET AAS Processor..."

# Check if .NET SDK is available locally for testing
if command -v dotnet &> /dev/null; then
    print_status "Local .NET SDK found. Testing .NET processor build..."
    
    # Check if aas-processor directory exists
    if [ -d "aas-processor" ]; then
        print_status "Building .NET AAS Processor locally for validation..."
        cd aas-processor
        
        # Restore packages
        if dotnet restore; then
            print_status "✅ .NET packages restored successfully"
        else
            print_error "❌ Failed to restore .NET packages"
            exit 1
        fi
        
        # Build the processor
        if dotnet build -c Release; then
            print_status "✅ .NET AAS Processor built successfully"
        else
            print_error "❌ Failed to build .NET AAS Processor"
            exit 1
        fi
        
        # Test the processor
        if [ -f "bin/Release/net6.0/AasProcessor.exe" ]; then
            print_status "✅ .NET AAS Processor executable found"
        else
            print_error "❌ .NET AAS Processor executable not found"
            exit 1
        fi
        
        cd ..
    else
        print_error "❌ aas-processor directory not found"
        exit 1
    fi
else
    print_warning "Local .NET SDK not found. .NET processor will be built in Docker."
fi

# Create necessary directories
print_header "Creating necessary directories..."
mkdir -p nginx/ssl
mkdir -p logs/nginx
mkdir -p data
mkdir -p output
mkdir -p certificates
mkdir -p backups

# SSL Certificate Setup
print_header "Setting up SSL certificates..."

# Check if SSL certificates exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    print_warning "SSL certificates not found. Setting up automatic SSL certificate generation..."
    
    # Check if domain is accessible
    if curl -s http://aasx-digital.de > /dev/null 2>&1; then
        print_status "Domain is accessible. Proceeding with SSL certificate generation..."
        
        # Stop nginx temporarily to free port 80
        print_status "Stopping nginx temporarily for certificate generation..."
        docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop nginx 2>/dev/null || true
        
        # Generate SSL certificate using certbot Docker
        print_status "Generating SSL certificate using Let's Encrypt..."
        if docker run --rm \
            -v $(pwd)/nginx/ssl:/etc/letsencrypt \
            -v $(pwd)/nginx/ssl:/var/lib/letsencrypt \
            -p 80:80 \
            -p 443:443 \
            certbot/certbot certonly \
            --standalone \
            --email admin@aasx-digital.de \
            --agree-tos \
            --no-eff-email \
            --domains aasx-digital.de,www.aasx-digital.de; then
            
            # Copy certificates to the correct location
            print_status "Copying certificates..."
            cp nginx/ssl/live/aasx-digital.de/fullchain.pem nginx/ssl/cert.pem
            cp nginx/ssl/live/aasx-digital.de/privkey.pem nginx/ssl/key.pem
            
            # Set proper permissions
            chmod 644 nginx/ssl/cert.pem
            chmod 600 nginx/ssl/key.pem
            
            print_status "✅ SSL certificates generated successfully!"
        else
            print_warning "SSL certificate generation failed. Continuing without SSL..."
            print_warning "You can manually set up SSL certificates later."
        fi
    else
        print_warning "Domain is not accessible. Skipping SSL certificate generation."
        print_warning "Please ensure your domain DNS is properly configured."
    fi
else
    print_status "✅ SSL certificates found!"
fi

# Load environment variables
if [ -f "production.env" ]; then
    print_status "Loading production environment variables..."
    # More robust way to load environment variables for Windows/Git Bash
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "$line" ]]; then
            # Check if line contains = sign
            if [[ "$line" == *"="* ]]; then
                export "$line"
            fi
        fi
    done < "production.env"
else
    print_warning "production.env not found. Using default values."
fi

# Stop existing containers
print_header "Stopping existing containers..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml down --remove-orphans

# Build and start services
print_header "Building and starting FastAPI services with .NET AAS Processor..."
print_status "Building Docker images (this may take several minutes for .NET build)..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml up -d --build

# Wait for services to be ready
print_status "Waiting for FastAPI services to be ready..."
sleep 30

# Test .NET processor in container
print_header "Testing .NET AAS Processor in container..."
if docker exec aasx-digital-webapp ls -la /app/aas-processor/AasProcessor.exe > /dev/null 2>&1; then
    print_status "✅ .NET AAS Processor found in container"
    
    # Test processor execution
    if docker exec aasx-digital-webapp /app/aas-processor/AasProcessor.exe --help > /dev/null 2>&1; then
        print_status "✅ .NET AAS Processor is executable"
    else
        print_warning "⚠️  .NET AAS Processor executable test failed"
    fi
else
    print_error "❌ .NET AAS Processor not found in container"
    docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs webapp
    exit 1
fi

# Test Wine integration for AASX Package Explorer
print_header "Testing Wine integration for AASX Package Explorer..."
if docker exec aasx-digital-webapp wine --version > /dev/null 2>&1; then
    print_status "✅ Wine is available in container"
    
    # Test AASX Package Explorer files
    if docker exec aasx-digital-webapp ls -la /app/AasxPackageExplorer/AasxPackageExplorer.exe > /dev/null 2>&1; then
        print_status "✅ AASX Package Explorer found in container"
        
        # Test Wine integration
        if docker exec aasx-digital-webapp python scripts/test_wine_integration.py > /dev/null 2>&1; then
            print_status "✅ Wine integration test passed"
        else
            print_warning "⚠️  Wine integration test failed (GUI may not be visible in container)"
        fi
    else
        print_warning "⚠️  AASX Package Explorer not found in container"
    fi
else
    print_warning "⚠️  Wine not available in container"
fi

# Check service health
print_header "Checking service health..."

# Check FastAPI webapp
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ FastAPI webapp is healthy"
else
    print_error "❌ FastAPI webapp health check failed"
    docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs webapp
    exit 1
fi

# Check Neo4j
if curl -f http://localhost:7474 > /dev/null 2>&1; then
    print_status "✅ Neo4j is healthy"
else
    print_error "❌ Neo4j health check failed"
    docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs neo4j
    exit 1
fi

# Check Qdrant
if curl -f http://localhost:6333/health > /dev/null 2>&1; then
    print_status "✅ Qdrant is healthy"
else
    print_error "❌ Qdrant health check failed"
    docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs qdrant
    exit 1
fi

# Check Redis
if docker exec aasx-digital-redis redis-cli ping > /dev/null 2>&1; then
    print_status "✅ Redis is healthy"
else
    print_error "❌ Redis health check failed"
    docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs redis
    exit 1
fi

print_status "🎉 All FastAPI services are healthy!"

# Test AASX processing functionality
print_header "Testing AASX processing functionality..."
if curl -f http://localhost:8000/aasx/health > /dev/null 2>&1; then
    print_status "✅ AASX processing module is accessible"
else
    print_warning "⚠️  AASX processing module health check failed"
fi

# Run integration tests
print_header "Running AASX integration tests..."
if python scripts/test_aasx_integration.py; then
    print_status "✅ All AASX integration tests passed"
else
    print_warning "⚠️  Some AASX integration tests failed"
fi

# Test HTTPS if SSL certificates exist
if [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
    print_header "Testing HTTPS access..."
    sleep 10  # Wait for nginx to fully start
    
    if curl -k -s https://aasx-digital.de > /dev/null 2>&1; then
        print_status "✅ HTTPS is working! Your site is available at: https://aasx-digital.de"
    else
        print_warning "⚠️  HTTPS test failed. Please check nginx logs."
    fi
fi

# Display deployment information
echo ""
echo "🌐 AASX Digital Twin Analytics Framework"
echo "========================================"
echo "Framework: FastAPI with .NET AAS Processor"
if [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
    echo "Domain: https://www.aasx-digital.de (SSL Enabled)"
else
    echo "Domain: http://www.aasx-digital.de (SSL Not Configured)"
fi
echo "Main Application: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "ReDoc Documentation: http://localhost:8000/redoc"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "📊 Available Services:"
echo "  • AASX ETL Pipeline: /aasx (with .NET Processor)"
echo "  • Knowledge Graph: /kg-neo4j"
echo "  • AI/RAG System: /ai-rag"
echo "  • Twin Registry: /twin-registry"
echo "  • Certificate Manager: /certificates"
echo "  • Analytics Dashboard: /analytics"
echo "  • Federated Learning: /federated-learning"
echo ""
echo "🔧 Management Commands:"
echo "  • View logs: docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs -f"
echo "  • Stop services: docker-compose -f manifests/framework/docker-compose.aasx-digital.yml down"
echo "  • Restart services: docker-compose -f manifests/framework/docker-compose.aasx-digital.yml restart"
echo "  • Update services: ./scripts/deploy-aasx-digital.sh"
echo "  • Backup data: docker-compose -f manifests/framework/docker-compose.aasx-digital.yml run backup"
echo "  • Renew SSL: ./scripts/renew_ssl_docker.sh"
echo "  • Test .NET processor: docker exec aasx-digital-webapp /app/aas-processor/AasProcessor.exe --help"
echo ""
echo "📝 Next Steps:"
echo "  1. Configure your domain DNS to point to this server"
echo "  2. Set up SSL certificates if not already done"
echo "  3. Configure backup schedules"
echo "  4. Set up monitoring and alerts"
echo "  5. Upload AASX files to test the processing pipeline"
echo ""

print_status "FastAPI deployment with .NET AAS Processor completed successfully! 🚀" 