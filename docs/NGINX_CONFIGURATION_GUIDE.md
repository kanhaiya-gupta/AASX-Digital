# Nginx Configuration Guide

## Overview

This document explains the Nginx configuration setup for the AASX Digital Twin Analytics Framework and how to avoid common configuration mistakes.

## Configuration Files

### 1. `nginx/nginx.conf` - Production Configuration (HTTPS + HTTP Redirect)
- **Purpose**: Full production setup with SSL/HTTPS support
- **Features**:
  - HTTP to HTTPS redirect (301)
  - SSL certificate handling
  - Security headers
  - Domain support: `www.aasx-digital.de`, `aasx-digital.de`, `localhost`
- **Use Case**: Production deployment with SSL certificates

### 2. `nginx/nginx-http.conf` - Development Configuration (HTTP Only)
- **Purpose**: Local development without SSL
- **Features**:
  - HTTP only (no HTTPS redirect)
  - No SSL certificate requirements
  - Domain support: `localhost`, `127.0.0.1`, `www.aasx-digital.de`, `aasx-digital.de`
- **Use Case**: Local development and testing

## Docker Compose Configuration

### Production Setup (Current)
```yaml
nginx:
  volumes:
    - ../../nginx/nginx.conf:/etc/nginx/nginx.conf  # ✅ CORRECT for production
    - ../../nginx/ssl:/etc/nginx/ssl
    - ../../logs/nginx:/var/log/nginx
```

### Development Setup (Alternative)
```yaml
nginx:
  volumes:
    - ../../nginx/nginx-http.conf:/etc/nginx/nginx.conf  # For local development only
    - ../../logs/nginx:/var/log/nginx
```

## Common Mistakes to Avoid

### ❌ Mistake 1: Using HTTP Config in Production
**Problem**: Using `nginx-http.conf` in production deployment
**Symptoms**: 
- Website redirects to external domain instead of localhost
- HTTPS not working
- SSL certificate errors

**Solution**: Always use `nginx.conf` for production deployments

### ❌ Mistake 2: Missing SSL Volume Mount
**Problem**: Not mounting SSL certificates directory
**Symptoms**: 
- Nginx fails to start
- SSL certificate not found errors

**Solution**: Include SSL volume mount in production:
```yaml
- ../../nginx/ssl:/etc/nginx/ssl
```

### ❌ Mistake 3: Wrong Domain Resolution
**Problem**: Domain points to external IP instead of localhost
**Symptoms**: 
- Connection refused errors
- Website not accessible locally

**Solution**: Add hosts file entry for local development:
```
127.0.0.1 www.aasx-digital.de aasx-digital.de
```

## Configuration Differences

| Feature | nginx.conf | nginx-http.conf |
|---------|------------|-----------------|
| HTTPS Redirect | ✅ Yes (301) | ❌ No |
| SSL Support | ✅ Yes | ❌ No |
| Security Headers | ✅ Yes | ❌ No |
| Production Ready | ✅ Yes | ❌ No |
| Local Development | ✅ Yes | ✅ Yes |

## Deployment Checklist

### For Production Deployment:
- [ ] Use `nginx.conf` in Docker Compose
- [ ] Mount SSL certificates: `../../nginx/ssl:/etc/nginx/ssl`
- [ ] Ensure SSL certificates exist in `nginx/ssl/`
- [ ] Verify domain DNS points to server IP
- [ ] Test HTTPS access

### For Local Development:
- [ ] Use `nginx-http.conf` in Docker Compose (if no SSL needed)
- [ ] Add hosts file entry for domain resolution
- [ ] Test HTTP access at `localhost:80`
- [ ] Test domain access at `www.aasx-digital.de`

## Troubleshooting

### Website Redirects to External Domain
**Cause**: Using HTTP config in production or wrong hosts file
**Solution**: 
1. Check Docker Compose uses `nginx.conf`
2. Verify hosts file entry exists
3. Flush DNS cache: `ipconfig /flushdns`

### SSL Certificate Errors
**Cause**: Missing SSL volume mount or certificates
**Solution**:
1. Ensure SSL volume is mounted
2. Check certificates exist in `nginx/ssl/`
3. Verify certificate paths in `nginx.conf`

### Connection Refused
**Cause**: Domain not resolving to localhost
**Solution**:
1. Add hosts file entry
2. Check DNS resolution: `nslookup www.aasx-digital.de`
3. Restart browser after hosts file changes

## Quick Commands

### Check Current Nginx Config
```bash
docker exec aasx-digital-nginx nginx -t
```

### View Nginx Logs
```bash
docker logs aasx-digital-nginx
```

### Test Domain Resolution
```bash
nslookup www.aasx-digital.de
```

### Flush DNS Cache (Windows)
```bash
ipconfig /flushdns
```

## Important Notes

1. **Never use `nginx-http.conf` in production** - it will break HTTPS redirects
2. **Always test both HTTP and HTTPS** after configuration changes
3. **Check hosts file** when working with domains locally
4. **SSL certificates must be present** for production HTTPS to work
5. **Restart containers** after configuration changes

## File Locations

- **Production Config**: `nginx/nginx.conf`
- **Development Config**: `nginx/nginx-http.conf`
- **SSL Certificates**: `nginx/ssl/`
- **Docker Compose**: `manifests/framework/docker-compose.aasx-digital.yml`
- **Hosts File**: `C:\Windows\System32\drivers\etc\hosts` (Windows)

---

**Remember**: The key difference is that `nginx.conf` handles HTTPS redirects and SSL, while `nginx-http.conf` is for HTTP-only development. Always use the appropriate configuration for your deployment scenario. 