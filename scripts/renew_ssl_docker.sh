#!/bin/bash

# Docker-based SSL Certificate Renewal Script
# This script renews SSL certificates using certbot Docker image

set -e

DOMAIN="aasx-digital.de"
EMAIL="admin@aasx-digital.de"

echo "🔄 Renewing SSL certificates for $DOMAIN using Docker..."

# Check if certificates exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    echo "❌ SSL certificates not found. Please run the deployment script first."
    exit 1
fi

# Stop nginx temporarily
echo "🛑 Stopping nginx temporarily..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop nginx

# Renew certificates using Docker
echo "🔑 Renewing SSL certificates using Let's Encrypt..."
if docker run --rm \
    -v $(pwd)/nginx/ssl:/etc/letsencrypt \
    -v $(pwd)/nginx/ssl:/var/lib/letsencrypt \
    -p 80:80 \
    -p 443:443 \
    certbot/certbot renew; then
    
    # Copy renewed certificates
    echo "📁 Copying renewed certificates..."
    cp nginx/ssl/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
    cp nginx/ssl/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
    
    # Set permissions
    chmod 644 nginx/ssl/cert.pem
    chmod 600 nginx/ssl/key.pem
    
    echo "✅ SSL certificates renewed successfully!"
else
    echo "❌ SSL certificate renewal failed!"
    exit 1
fi

# Restart nginx
echo "🔄 Restarting nginx..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml start nginx

# Test HTTPS
echo "🧪 Testing HTTPS..."
sleep 5
if curl -k -s https://$DOMAIN > /dev/null 2>&1; then
    echo "✅ HTTPS is working after renewal!"
else
    echo "⚠️  HTTPS test failed after renewal. Please check nginx logs."
fi

echo "📋 SSL Renewal Summary:"
echo "   - Domain: $DOMAIN"
echo "   - Renewal Date: $(date)"
echo "   - Next Renewal: $(date -d '+60 days')"
echo "   - Certificate: nginx/ssl/cert.pem"
echo "   - Private Key: nginx/ssl/key.pem" 