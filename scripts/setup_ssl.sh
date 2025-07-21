#!/bin/bash

# SSL Certificate Setup Script for AASX Digital Twin Framework
# This script sets up SSL certificates using Let's Encrypt

set -e

DOMAIN="aasx-digital.de"
EMAIL="admin@aasx-digital.de"  # Change this to your email

echo "🔐 Setting up SSL certificates for $DOMAIN..."

# Create SSL directory
mkdir -p nginx/ssl

# Check if certbot is available
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y certbot
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y certbot
    elif command -v brew &> /dev/null; then
        # macOS
        brew install certbot
    else
        echo "❌ Could not install certbot automatically. Please install it manually."
        exit 1
    fi
fi

# Stop nginx temporarily to free port 80
echo "🛑 Stopping nginx temporarily..."
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop nginx

# Obtain SSL certificate
echo "🔑 Obtaining SSL certificate from Let's Encrypt..."
sudo certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN,www.$DOMAIN

# Copy certificates to nginx directory
echo "📁 Copying certificates to nginx directory..."
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem

# Set proper permissions
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem

# Create renewal script
echo "🔄 Creating certificate renewal script..."
cat > scripts/renew_ssl.sh << 'EOF'
#!/bin/bash
# Certificate renewal script

DOMAIN="aasx-digital.de"

echo "🔄 Renewing SSL certificates..."

# Stop nginx
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop nginx

# Renew certificates
sudo certbot renew

# Copy renewed certificates
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem

# Set permissions
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem

# Restart nginx
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml start nginx

echo "✅ SSL certificates renewed successfully!"
EOF

chmod +x scripts/renew_ssl.sh

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
    echo "   0 12 * * * $(pwd)/scripts/renew_ssl.sh"
else
    echo "⚠️  SSL setup completed, but HTTPS test failed. Please check nginx logs."
fi

echo "📋 SSL Setup Summary:"
echo "   - Domain: $DOMAIN"
echo "   - SSL Certificate: nginx/ssl/cert.pem"
echo "   - Private Key: nginx/ssl/key.pem"
echo "   - Renewal Script: scripts/renew_ssl.sh"
echo "   - HTTPS URL: https://$DOMAIN" 