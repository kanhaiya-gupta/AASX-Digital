# 🔐 SSL/HTTPS Setup Guide for AASX Digital Twin Framework

## 📋 Overview
This guide will help you set up SSL certificates for your domain `aasx-digital.de` to enable HTTPS access.

## 🎯 Prerequisites
- Domain pointing to your server IP
- Docker and Docker Compose installed
- Root/sudo access on your server
- Port 80 and 443 open on your firewall

## 🚀 Quick Setup (Recommended)

### Step 1: Install Certbot
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y certbot

# CentOS/RHEL
sudo yum install -y certbot

# macOS
brew install certbot
```

### Step 2: Stop Nginx Temporarily
```bash
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml stop nginx
```

### Step 3: Generate SSL Certificate
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate certificate
sudo certbot certonly --standalone \
    --email admin@aasx-digital.de \
    --agree-tos \
    --no-eff-email \
    --domains aasx-digital.de,www.aasx-digital.de
```

### Step 4: Copy Certificates
```bash
# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/aasx-digital.de/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/aasx-digital.de/privkey.pem nginx/ssl/key.pem

# Set proper permissions
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem
```

### Step 5: Rebuild and Start Nginx
```bash
# Rebuild nginx with SSL support
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml build nginx

# Start nginx
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml up -d nginx
```

### Step 6: Test HTTPS
```bash
# Test your site
curl -I https://aasx-digital.de
```

## 🔄 Certificate Renewal

### Automatic Renewal Script
Create a renewal script:
```bash
cat > scripts/renew_ssl.sh << 'EOF'
#!/bin/bash
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
```

### Set Up Automatic Renewal
```bash
# Add to crontab (runs daily at 12:00 PM)
crontab -e

# Add this line:
0 12 * * * /path/to/your/project/scripts/renew_ssl.sh
```

## 🔧 Manual Setup (Alternative)

### Step 1: Create Self-Signed Certificate (Testing)
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=DE/ST=State/L=City/O=Organization/CN=aasx-digital.de"
```

### Step 2: Update Nginx Configuration
The nginx configuration is already set up for SSL. It includes:
- HTTP to HTTPS redirect
- SSL security settings
- Security headers
- Rate limiting

### Step 3: Rebuild and Restart
```bash
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml build nginx
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml restart nginx
```

## 🧪 Testing

### Test HTTPS Access
```bash
# Test main domain
curl -I https://aasx-digital.de

# Test www subdomain
curl -I https://www.aasx-digital.de

# Test HTTP redirect
curl -I http://aasx-digital.de
```

### Test SSL Configuration
```bash
# Check SSL certificate
openssl s_client -connect aasx-digital.de:443 -servername aasx-digital.de

# Test with SSL Labs (online)
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=aasx-digital.de
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Certificate Not Found
```bash
# Check if certificates exist
ls -la nginx/ssl/

# Regenerate if missing
sudo certbot certonly --standalone --domains aasx-digital.de,www.aasx-digital.de
```

#### 2. Permission Issues
```bash
# Fix permissions
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/cert.pem
sudo chown $USER:$USER nginx/ssl/key.pem
```

#### 3. Nginx Won't Start
```bash
# Check nginx logs
docker-compose -f manifests/framework/docker-compose.aasx-digital.yml logs nginx

# Test nginx configuration
docker exec aasx-digital-nginx nginx -t
```

#### 4. Port 80/443 Already in Use
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Stop conflicting services
sudo systemctl stop apache2  # if Apache is running
sudo systemctl stop nginx    # if system nginx is running
```

### SSL Configuration Issues

#### 1. Mixed Content Warnings
- Ensure all resources (CSS, JS, images) use HTTPS
- Update any hardcoded HTTP URLs in your application

#### 2. HSTS Issues
- The nginx config includes HSTS headers
- Clear browser cache if you see HSTS errors

#### 3. Certificate Expiry
```bash
# Check certificate expiry
openssl x509 -in nginx/ssl/cert.pem -text -noout | grep "Not After"

# Renew manually if needed
sudo certbot renew
```

## 📊 SSL Security Features

The nginx configuration includes:

### Security Headers
- `Strict-Transport-Security`: Forces HTTPS
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME sniffing
- `X-XSS-Protection`: XSS protection
- `Referrer-Policy`: Controls referrer information

### SSL Configuration
- TLS 1.2 and 1.3 only
- Strong cipher suites
- SSL session caching
- OCSP stapling (when available)

### Rate Limiting
- API endpoints rate limited
- Protection against DDoS attacks

## 🎯 Final Checklist

- [ ] SSL certificates generated and installed
- [ ] Nginx configuration updated
- [ ] HTTPS redirect working
- [ ] All resources loading over HTTPS
- [ ] Automatic renewal configured
- [ ] Security headers in place
- [ ] SSL Labs test passed
- [ ] Browser shows secure connection

## 📞 Support

If you encounter issues:

1. **Check logs**: `docker-compose logs nginx`
2. **Test connectivity**: `curl -I https://aasx-digital.de`
3. **Verify DNS**: `nslookup aasx-digital.de`
4. **Check firewall**: Ensure ports 80 and 443 are open

---

*Last updated: July 2024*
*Framework Version: 1.0* 