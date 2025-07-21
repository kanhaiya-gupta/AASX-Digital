# SSL/HTTPS Setup Guide for AASX Digital Framework

This guide documents the complete process of setting up HTTP and HTTPS with Let's Encrypt SSL certificates for the AASX Digital Framework.

## Overview

The framework uses Nginx as a reverse proxy to handle both HTTP and HTTPS traffic, with automatic HTTP to HTTPS redirection and proper SSL certificate management.

## Prerequisites

1. **Domain Name**: A registered domain (e.g., `aasx-digital.de`)
2. **DNS Configuration**: A and AAAA records pointing to your server IP
3. **Port 80 Access**: Must be open for Let's Encrypt verification
4. **Docker & Docker Compose**: Installed and configured

## Step-by-Step Setup Process

### 1. Initial Framework Deployment

First, deploy the framework using the deployment script:

```bash
# Run the deployment script
bash scripts/deploy_aasx_digital.sh
```

This will:
- Build and start all containers
- Set up the basic HTTP configuration
- Create necessary directories and files

### 2. DNS Configuration

Configure your domain's DNS records in your domain provider (e.g., GoDaddy):

#### A Records (IPv4)
```
Type: A
Name: @
Value: [YOUR_SERVER_IP]
TTL: 600

Type: A  
Name: www
Value: [YOUR_SERVER_IP]
TTL: 600
```

#### AAAA Records (IPv6) - Optional
```
Type: AAAA
Name: @
Value: [YOUR_SERVER_IPv6]
TTL: 600

Type: AAAA
Name: www
Value: [YOUR_SERVER_IPv6]
TTL: 600
```

### 3. SSL Certificate Generation with Let's Encrypt

#### 3.1 Create SSL Directory Structure
```bash
# Create SSL directories
mkdir -p nginx/ssl
```

#### 3.2 Generate SSL Certificates
```bash
# Run Certbot to generate SSL certificates
docker run --rm -it \
  -v "$PWD/nginx/ssl:/etc/letsencrypt" \
  -v "$PWD:/var/www/html" \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/html \
  -d aasx-digital.de -d www.aasx-digital.de \
  --email admin@aasx-digital.de --agree-tos --non-interactive
```

**Important**: During this process, you need to serve files on port 80 for Let's Encrypt verification:

```bash
# In a separate terminal, serve files on port 80
python -m http.server 80
```

#### 3.3 Verify Certificate Generation
```bash
# Check that certificates were created
ls -la nginx/ssl/live/aasx-digital.de/
```

Expected output:
```
cert.pem -> ../../archive/aasx-digital.de/cert1.pem
chain.pem -> ../../archive/aasx-digital.de/chain1.pem
fullchain.pem -> ../../archive/aasx-digital.de/fullchain1.pem
privkey.pem -> ../../archive/aasx-digital.de/privkey1.pem
```

### 4. Nginx Configuration

#### 4.1 Update Nginx Configuration

The nginx configuration is located at `nginx/nginx.conf`. Key components:

```nginx
# HTTP server block - redirect to HTTPS
server {
    listen 80;
    server_name www.aasx-digital.de aasx-digital.de localhost;
    
    # Redirect all HTTP traffic to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS server block
server {
    listen 443 ssl http2;
    server_name www.aasx-digital.de aasx-digital.de localhost;

    # SSL Configuration - Let's Encrypt certificates
    ssl_certificate /etc/nginx/ssl/live/aasx-digital.de/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/aasx-digital.de/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Upstream for FastAPI application
    upstream fastapi_backend {
        server aasx-digital-webapp:8000;
    }

    # Main application
    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

#### 4.2 Docker Compose Configuration

The docker-compose file (`manifests/framework/docker-compose.aasx-digital.yml`) mounts the SSL certificates:

```yaml
nginx:
  image: nginx:alpine
  container_name: aasx-digital-nginx
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ../../nginx/nginx.conf:/etc/nginx/nginx.conf
    - ../../nginx/ssl:/etc/nginx/ssl
    - ../../logs/nginx:/var/log/nginx
    - ../../webapp/static:/var/www/static
  depends_on:
    - webapp
```

### 5. Restart Services

After updating the configuration:

```bash
# Restart nginx to apply SSL configuration
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml restart nginx

# Or restart all services
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml restart
```

### 6. Verification

#### 6.1 Check Container Status
```bash
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml ps
```

#### 6.2 Test HTTP to HTTPS Redirect
```bash
# Test HTTP redirect
curl -I http://www.aasx-digital.de
# Should return: HTTP/1.1 301 Moved Permanently
```

#### 6.3 Test HTTPS Access
```bash
# Test HTTPS access
curl -I https://www.aasx-digital.de
# Should return: HTTP/1.1 200 OK
```

#### 6.4 Check SSL Certificate
```bash
# Verify SSL certificate
openssl s_client -connect www.aasx-digital.de:443 -servername www.aasx-digital.de
```

## SSL Certificate Renewal

Let's Encrypt certificates expire after 90 days. Set up automatic renewal:

### 1. Create Renewal Script
```bash
# Create renewal script
cat > scripts/renew_ssl.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."

# Stop nginx temporarily
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop nginx

# Renew certificates
docker run --rm -it \
  -v "$PWD/nginx/ssl:/etc/letsencrypt" \
  -v "$PWD:/var/www/html" \
  certbot/certbot renew --webroot \
  --webroot-path=/var/www/html

# Start nginx
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml start nginx
EOF

chmod +x scripts/renew_ssl.sh
```

### 2. Set Up Cron Job
```bash
# Add to crontab (renew every 60 days)
crontab -e

# Add this line:
0 2 */60 * * /path/to/your/project/scripts/renew_ssl.sh >> /var/log/ssl-renewal.log 2>&1
```

## Troubleshooting

### Common Issues

#### 1. Nginx Container Restarting
**Problem**: `nginx: [emerg] host not found in upstream "aasx-digital-webapp:8000"`

**Solution**: Ensure the webapp container is running:
```bash
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml ps webapp
```

#### 2. SSL Certificate Not Found
**Problem**: `nginx: [emerg] cannot load certificate "/etc/nginx/ssl/cert.pem"`

**Solution**: Verify certificate paths and restart nginx:
```bash
ls -la nginx/ssl/live/aasx-digital.de/
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml restart nginx
```

#### 3. Let's Encrypt Verification Failed
**Problem**: Certbot fails with verification errors

**Solution**: Ensure port 80 is accessible and serving files:
```bash
# Check if port 80 is open
netstat -tlnp | grep :80

# Serve files for verification
python -m http.server 80
```

#### 4. DNS Propagation Issues
**Problem**: Domain not resolving

**Solution**: Wait for DNS propagation (up to 48 hours) or check DNS configuration:
```bash
# Check DNS resolution
nslookup www.aasx-digital.de
dig www.aasx-digital.de
```

### Debug Commands

```bash
# Check nginx logs
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs nginx

# Test nginx configuration
docker exec aasx-digital-nginx nginx -t

# Check SSL certificate validity
openssl x509 -in nginx/ssl/live/aasx-digital.de/cert.pem -text -noout

# Test HTTPS connection
curl -v https://www.aasx-digital.de
```

## Security Best Practices

1. **HSTS Header**: Already configured in nginx
2. **Strong Ciphers**: Using modern TLS 1.2/1.3 ciphers
3. **Rate Limiting**: Configured for API endpoints
4. **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.
5. **Certificate Renewal**: Automated renewal process

## File Structure

```
nginx/
├── nginx.conf                    # Main nginx configuration
└── ssl/
    ├── live/
    │   └── aasx-digital.de/
    │       ├── cert.pem          # Certificate
    │       ├── chain.pem         # Certificate chain
    │       ├── fullchain.pem     # Full certificate chain
    │       └── privkey.pem       # Private key
    ├── archive/                  # Certificate archive
    └── renewal/                  # Renewal configuration

manifests/framework/
└── docker-compose.aasx-digital.yml  # Docker compose configuration
```

## Summary

This setup provides:
- ✅ Automatic HTTP to HTTPS redirection
- ✅ Valid SSL certificates from Let's Encrypt
- ✅ Modern TLS configuration (TLS 1.2/1.3)
- ✅ Security headers and best practices
- ✅ Automated certificate renewal
- ✅ Proper reverse proxy configuration for FastAPI

The framework is now ready for production use with secure HTTPS access. 