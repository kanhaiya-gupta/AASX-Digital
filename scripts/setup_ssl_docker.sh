#!/bin/bash

# Docker-based SSL Certificate Setup Script
# This script uses certbot Docker image to generate SSL certificates

set -e

DOMAIN="aasx-digital.de"
EMAIL="admin@aasx-digital.de"  # Change this to your email

echo "🔐 Setting up SSL certificates for $DOMAIN using Docker..."

# Create SSL directory
mkdir -p nginx/ssl

# Stop nginx temporarily to free port 80
echo "🛑 Stopping nginx temporarily..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop nginx

# Generate SSL certificate using certbot Docker image
echo "🔑 Generating SSL certificate using certbot Docker..."
docker run --rm \
    -v $(pwd)/nginx/ssl:/etc/letsencrypt \
    -v $(pwd)/nginx/ssl:/var/lib/letsencrypt \
    -p 80:80 \
    -p 443:443 \
    certbot/certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN,www.$DOMAIN

# Copy certificates to the correct location
echo "📁 Copying certificates..."
cp nginx/ssl/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
cp nginx/ssl/live/$DOMAIN/privkey.pem nginx/ssl/key.pem

# Set proper permissions
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

# Create renewal script
echo "🔄 Creating certificate renewal script..."
cat > scripts/renew_ssl_docker.sh << 'EOF'
#!/bin/bash
# Docker-based certificate renewal script

DOMAIN="aasx-digital.de"
EMAIL="admin@aasx-digital.de"

echo "🔄 Renewing SSL certificates using Docker..."

# Stop nginx
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop nginx

# Renew certificates using Docker
docker run --rm \
    -v $(pwd)/nginx/ssl:/etc/letsencrypt \
    -v $(pwd)/nginx/ssl:/var/lib/letsencrypt \
    -p 80:80 \
    -p 443:443 \
    certbot/certbot renew

# Copy renewed certificates
cp nginx/ssl/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
cp nginx/ssl/live/$DOMAIN/privkey.pem nginx/ssl/key.pem

# Set permissions
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

# Restart nginx
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml start nginx

echo "✅ SSL certificates renewed successfully!"
EOF

chmod +x scripts/renew_ssl_docker.sh

# Rebuild and restart nginx with SSL
echo "🔧 Rebuilding nginx with SSL support..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml build nginx
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml up -d nginx

# Test SSL configuration
echo "🧪 Testing SSL configuration..."
sleep 5
if curl -k -s https://$DOMAIN > /dev/null; then
    echo "✅ SSL setup completed successfully!"
    echo "🌐 Your site is now available at: https://$DOMAIN"
    echo "🔄 To renew certificates automatically, add to crontab:"
    echo "   0 12 * * * $(pwd)/scripts/renew_ssl_docker.sh"
else
    echo "⚠️  SSL setup completed, but HTTPS test failed. Please check nginx logs."
fi

echo "📋 SSL Setup Summary:"
echo "   - Domain: $DOMAIN"
echo "   - SSL Certificate: nginx/ssl/cert.pem"
echo "   - Private Key: nginx/ssl/key.pem"
echo "   - Renewal Script: scripts/renew_ssl_docker.sh"
echo "   - HTTPS URL: https://$DOMAIN" 