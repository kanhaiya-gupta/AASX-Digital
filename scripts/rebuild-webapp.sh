#!/bin/bash

# AASX Digital Twin Analytics Framework - Webapp Rebuild Script
# For domain: www.aasx-digital.de
# Framework: FastAPI with .NET AAS Processor and Blazor Web Viewer
# Docker Compose: manifests/framework/docker-compose.aasx-digital.yml

set -e

echo "🔄 Starting AASX Webapp Rebuild..."
echo "🌐 Domain: www.aasx-digital.de"
echo "⚡ Framework: FastAPI with .NET AAS Processor and Blazor Web Viewer"
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

# Stop webapp container only
print_header "Stopping webapp container..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop webapp

# Remove webapp container
print_header "Removing webapp container..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml rm -f webapp

# Build webapp only
print_header "Building webapp with latest code changes..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml build --no-cache webapp

# Start webapp only
print_header "Starting webapp container..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml up -d webapp

# Wait for webapp to be ready
print_status "Waiting for webapp to be ready..."
sleep 15

# Check webapp status
print_header "Checking webapp status..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml ps webapp

# Test webapp health
print_header "Testing webapp health..."
if curl -f http://localhost:80/health > /dev/null 2>&1; then
    print_status "✅ Webapp is healthy and responding!"
else
    print_warning "⚠️  Webapp health check failed. Check logs with: docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs webapp"
fi

print_status "🎉 Webapp rebuild complete!"
print_status "📝 You can check logs with: docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs webapp"
print_status "🌐 Access the application at: https://www.aasx-digital.de" 