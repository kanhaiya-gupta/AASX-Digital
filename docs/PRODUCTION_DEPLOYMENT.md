# Production Deployment Guide for www.aasx-digital.de

## 🚀 Overview

This guide covers deploying the AASX Digital Twin Analytics Framework to production at `www.aasx-digital.de` with multiple hosting options.

## 🎯 Deployment Options

### Option 1: VPS/Cloud Server (Recommended)
- **Providers**: DigitalOcean, Hetzner, AWS EC2, Google Cloud, Azure
- **Cost**: €20-50/month
- **Control**: Full control over infrastructure
- **Best for**: Production use, custom configurations

### Option 2: Managed Kubernetes
- **Providers**: Google GKE, AWS EKS, Azure AKS, DigitalOcean Kubernetes
- **Cost**: €50-150/month
- **Control**: High scalability, managed infrastructure
- **Best for**: Enterprise, high traffic, auto-scaling

### Option 3: Container Platforms
- **Providers**: Railway, Render, Fly.io, DigitalOcean App Platform
- **Cost**: €20-80/month
- **Control**: Managed containers, easy deployment
- **Best for**: Quick deployment, managed scaling

### Option 4: Traditional Hosting
- **Providers**: Netlify, Vercel (frontend) + Backend services
- **Cost**: €10-30/month
- **Control**: Limited, but very easy
- **Best for**: Simple deployments, static content

## 🏗️ Recommended Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Domain DNS    │    │   Load Balancer │    │   SSL/TLS       │
│ aasx-digital.de │───▶│   (Nginx/Traefik)│───▶│   (Let's Encrypt)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Web App       │   AI/RAG        │   Backend Services          │
│   (Port 8000)   │   (Port 8001)   │   (Ports 8002-8004)        │
└─────────────────┴─────────────────┴─────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                   │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   PostgreSQL    │   Neo4j         │   Qdrant Vector DB          │
│   (Port 5432)   │   (Port 7474)   │   (Port 6333)               │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

## 🚀 Option 1: VPS Deployment (Step-by-Step)

### 1. Server Setup

#### Choose a VPS Provider
- **Hetzner Cloud** (Germany): €20-30/month
- **DigitalOcean**: $20-40/month
- **AWS EC2**: $20-50/month

#### Server Specifications
- **CPU**: 4-8 cores
- **RAM**: 8-16 GB
- **Storage**: 100-200 GB SSD
- **OS**: Ubuntu 22.04 LTS

### 2. Domain Configuration

#### DNS Setup
```bash
# Add these DNS records to your domain provider
A     @           YOUR_SERVER_IP
A     www         YOUR_SERVER_IP
CNAME api         www.aasx-digital.de
CNAME admin       www.aasx-digital.de
```

#### SSL Certificate
```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d aasx-digital.de -d www.aasx-digital.de
```

### 3. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y
```

### 4. Application Deployment

#### Clone Repository
```bash
# Create application directory
sudo mkdir -p /opt/aasx-digital
sudo chown $USER:$USER /opt/aasx-digital
cd /opt/aasx-digital

# Clone your repository
git clone https://github.com/your-username/aas-data-modeling.git .
```

#### Environment Configuration
```bash
# Create production environment file
cat > .env << 'EOF'
# Production Environment Variables
NODE_ENV=production
FLASK_ENV=production

# Database Configuration
DATABASE_URL=postgresql://aasx_user:aasx_password@postgres:5432/aasx_data
REDIS_URL=redis://redis:6379

# Neo4j Configuration
NEO4J_URI=neo4j://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_neo4j_password

# Qdrant Configuration
QDRANT_URL=http://qdrant:6333

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Security
SECRET_KEY=your_very_secure_secret_key_here
JWT_SECRET=your_jwt_secret_key_here

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false

# Domain
DOMAIN=aasx-digital.de
ALLOWED_HOSTS=["aasx-digital.de", "www.aasx-digital.de"]
EOF
```

#### Nginx Configuration
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/aasx-digital.de << 'EOF'
server {
    listen 80;
    server_name aasx-digital.de www.aasx-digital.de;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aasx-digital.de www.aasx-digital.de;

    # SSL Configuration (will be managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/aasx-digital.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aasx-digital.de/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Client max body size for file uploads
    client_max_body_size 100M;

    # Main application
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static/ {
        alias /opt/aasx-digital/webapp/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    # API documentation
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/aasx-digital.de /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Docker Compose Production
```bash
# Create production docker-compose file
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  # Main Web Application
  webapp:
    build:
      context: .
      dockerfile: docker/Dockerfile.webapp
    container_name: aasx-webapp-prod
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - FLASK_ENV=production
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./logs:/app/logs
      - ./certificates:/app/certificates
    depends_on:
      - postgres
      - redis
      - neo4j
      - qdrant
    networks:
      - aasx-network

  # AI/RAG System
  ai-rag:
    build:
      context: .
      dockerfile: docker/Dockerfile.ai-rag
    container_name: aasx-ai-rag-prod
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
      - neo4j
      - qdrant
    networks:
      - aasx-network

  # Digital Twin Registry
  twin-registry:
    build:
      context: .
      dockerfile: docker/Dockerfile.twin-registry
    container_name: aasx-twin-registry-prod
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
      - neo4j
    networks:
      - aasx-network

  # Certificate Manager
  certificate-manager:
    build:
      context: .
      dockerfile: docker/Dockerfile.certificate-manager
    container_name: aasx-cert-manager-prod
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./certificates:/app/certificates
      - ./logs:/app/logs
    depends_on:
      - postgres
    networks:
      - aasx-network

  # Quality Infrastructure Analytics
  qi-analytics:
    build:
      context: .
      dockerfile: docker/Dockerfile.qi-analytics
    container_name: aasx-qi-analytics-prod
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    depends_on:
      - postgres
      - ai-rag
    networks:
      - aasx-network

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: aasx-postgres-prod
    restart: unless-stopped
    environment:
      POSTGRES_DB: aasx_data
      POSTGRES_USER: aasx_user
      POSTGRES_PASSWORD: aasx_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - aasx-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aasx_user -d aasx_data"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: aasx-redis-prod
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - aasx-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Neo4j Graph Database
  neo4j:
    image: neo4j:5.15-community
    container_name: aasx-neo4j-prod
    restart: unless-stopped
    environment:
      NEO4J_AUTH: neo4j/your_secure_neo4j_password
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
      NEO4J_dbms_security_procedures_unrestricted: apoc.*,gds.*
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins
    networks:
      - aasx-network
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "your_secure_neo4j_password", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: aasx-qdrant-prod
    restart: unless-stopped
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - aasx-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backup Service
  backup:
    image: postgres:15-alpine
    container_name: aasx-backup-prod
    restart: "no"
    environment:
      POSTGRES_PASSWORD: aasx_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - aasx-network
    command: >
      sh -c "
        echo 'Creating backup...' &&
        pg_dump -h postgres -U aasx_user -d aasx_data > /backups/backup_$$(date +%Y%m%d_%H%M%S).sql &&
        echo 'Backup completed'
      "

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  neo4j_plugins:
  qdrant_data:

networks:
  aasx-network:
    driver: bridge
EOF
```

### 5. Deployment Commands

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Create initial backup
docker-compose -f docker-compose.prod.yml run --rm backup
```

### 6. Monitoring and Maintenance

#### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Create monitoring script
cat > /opt/aasx-digital/monitor.sh << 'EOF'
#!/bin/bash
echo "=== AASX Digital System Status ==="
echo "Date: $(date)"
echo ""

echo "=== Docker Containers ==="
docker-compose -f /opt/aasx-digital/docker-compose.prod.yml ps

echo ""
echo "=== System Resources ==="
df -h
free -h

echo ""
echo "=== Application Health ==="
curl -s http://localhost:8000/health | jq .

echo ""
echo "=== Database Status ==="
docker-compose -f /opt/aasx-digital/docker-compose.prod.yml exec -T postgres pg_isready -U aasx_user -d aasx_data
EOF

chmod +x /opt/aasx-digital/monitor.sh
```

#### Automated Backups
```bash
# Create backup script
cat > /opt/aasx-digital/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/aasx-digital/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker-compose -f /opt/aasx-digital/docker-compose.prod.yml run --rm backup

# Application data backup
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz \
    /opt/aasx-digital/data \
    /opt/aasx-digital/output \
    /opt/aasx-digital/certificates

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/aasx-digital/backup.sh

# Add to crontab (daily backup at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/aasx-digital/backup.sh") | crontab -
```

## 🚀 Option 2: Managed Kubernetes Deployment

### 1. Cluster Setup (Google GKE Example)

```bash
# Create GKE cluster
gcloud container clusters create aasx-cluster \
    --zone=europe-west1-b \
    --num-nodes=3 \
    --machine-type=e2-standard-4 \
    --disk-size=100 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10

# Get credentials
gcloud container clusters get-credentials aasx-cluster --zone=europe-west1-b
```

### 2. Kubernetes Manifests

#### Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: aasx-digital
```

#### ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aasx-config
  namespace: aasx-digital
data:
  NODE_ENV: "production"
  FLASK_ENV: "production"
  APP_HOST: "0.0.0.0"
  APP_PORT: "8000"
  DEBUG: "false"
  DOMAIN: "aasx-digital.de"
```

#### Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: aasx-secrets
  namespace: aasx-digital
type: Opaque
data:
  # Base64 encoded values
  OPENAI_API_KEY: <base64-encoded-key>
  NEO4J_PASSWORD: <base64-encoded-password>
  SECRET_KEY: <base64-encoded-secret>
  JWT_SECRET: <base64-encoded-jwt-secret>
```

#### Persistent Volumes
```yaml
# k8s/storage.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: aasx-digital
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: neo4j-pvc
  namespace: aasx-digital
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qdrant-pvc
  namespace: aasx-digital
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

#### Deployments
```yaml
# k8s/deployments.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aasx-webapp
  namespace: aasx-digital
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aasx-webapp
  template:
    metadata:
      labels:
        app: aasx-webapp
    spec:
      containers:
      - name: webapp
        image: your-registry/aasx-webapp:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: aasx-config
        - secretRef:
            name: aasx-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Services
```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: aasx-webapp-service
  namespace: aasx-digital
spec:
  selector:
    app: aasx-webapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

#### Ingress
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: aasx-ingress
  namespace: aasx-digital
  annotations:
    kubernetes.io/ingress.class: "gce"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - aasx-digital.de
    - www.aasx-digital.de
    secretName: aasx-tls
  rules:
  - host: aasx-digital.de
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: aasx-webapp-service
            port:
              number: 80
  - host: www.aasx-digital.de
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: aasx-webapp-service
            port:
              number: 80
```

### 3. Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/storage.yaml
kubectl apply -f k8s/deployments.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods -n aasx-digital
kubectl get services -n aasx-digital
kubectl get ingress -n aasx-digital
```

## 🚀 Option 3: Container Platform Deployment

### Railway Deployment

1. **Connect Repository**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Select the repository

2. **Environment Variables**
   ```env
   NODE_ENV=production
   FLASK_ENV=production
   OPENAI_API_KEY=your_openai_key
   NEO4J_URI=your_neo4j_uri
   QDRANT_URL=your_qdrant_url
   SECRET_KEY=your_secret_key
   ```

3. **Deploy**
   - Railway will automatically detect the Dockerfile
   - Deploy with one click
   - Get a public URL

4. **Custom Domain**
   - Add custom domain: `aasx-digital.de`
   - Configure DNS records
   - SSL certificate automatically provisioned

### Render Deployment

1. **Create Service**
   - Go to [Render.com](https://render.com)
   - Create new Web Service
   - Connect GitHub repository

2. **Configuration**
   ```yaml
   # render.yaml
   services:
     - type: web
       name: aasx-digital
       env: docker
       plan: starter
       dockerfilePath: ./docker/Dockerfile.webapp
       envVars:
         - key: NODE_ENV
           value: production
         - key: FLASK_ENV
           value: production
         - key: OPENAI_API_KEY
           sync: false
   ```

3. **Deploy**
   - Render builds and deploys automatically
   - Automatic SSL certificates
   - Custom domain support

## 🔧 Post-Deployment Configuration

### 1. SSL Certificate Renewal

```bash
# Add to crontab for automatic renewal
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
```

### 2. Monitoring Setup

#### Prometheus + Grafana
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'aasx-digital'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

#### Log Management
```bash
# Install logrotate
sudo apt install logrotate

# Configure log rotation
sudo tee /etc/logrotate.d/aasx-digital << 'EOF'
/opt/aasx-digital/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
EOF
```

### 3. Performance Optimization

#### Nginx Optimization
```nginx
# Add to nginx configuration
worker_processes auto;
worker_connections 1024;

# Enable gzip
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

# Cache static files
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

#### Database Optimization
```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

## 🔒 Security Hardening

### 1. Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Security Headers
```nginx
# Add security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 3. Rate Limiting
```nginx
# Add rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://localhost:8000;
}

location /login {
    limit_req zone=login burst=5 nodelay;
    proxy_pass http://localhost:8000;
}
```

## 📊 Monitoring and Alerting

### 1. Health Checks
```bash
# Create health check script
cat > /opt/aasx-digital/health-check.sh << 'EOF'
#!/bin/bash

# Check application health
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Application health check failed"
    exit 1
fi

# Check database connectivity
if ! docker-compose -f /opt/aasx-digital/docker-compose.prod.yml exec -T postgres pg_isready -U aasx_user -d aasx_data > /dev/null 2>&1; then
    echo "Database health check failed"
    exit 1
fi

echo "All health checks passed"
EOF

chmod +x /opt/aasx-digital/health-check.sh
```

### 2. Automated Alerts
```bash
# Install monitoring tools
sudo apt install mailutils -y

# Create alert script
cat > /opt/aasx-digital/alert.sh << 'EOF'
#!/bin/bash
if [ $1 -ne 0 ]; then
    echo "AASX Digital Alert: Service failure detected" | mail -s "AASX Digital Alert" your-email@example.com
fi
EOF

chmod +x /opt/aasx-digital/alert.sh

# Add to crontab (check every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/aasx-digital/health-check.sh; /opt/aasx-digital/alert.sh \$?") | crontab -
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Domain DNS configured
- [ ] SSL certificates obtained
- [ ] Environment variables set
- [ ] Database backups configured
- [ ] Monitoring tools installed
- [ ] Security measures implemented

### Deployment
- [ ] Application deployed successfully
- [ ] All services running
- [ ] Health checks passing
- [ ] SSL certificates working
- [ ] Custom domain accessible
- [ ] Performance monitoring active

### Post-Deployment
- [ ] Automated backups working
- [ ] Log rotation configured
- [ ] Alert system tested
- [ ] Performance optimized
- [ ] Security audit completed
- [ ] Documentation updated

## 🆘 Troubleshooting

### Common Issues

#### Application Not Starting
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs webapp

# Check environment variables
docker-compose -f docker-compose.prod.yml exec webapp env

# Check port availability
sudo netstat -tlnp | grep :8000
```

#### Database Connection Issues
```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U aasx_user -d aasx_data

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U aasx_user -d aasx_data -c "SELECT 1;"
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates manually
sudo certbot renew --dry-run

# Check Nginx configuration
sudo nginx -t
```

## 📞 Support

For deployment support:
- Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
- Monitor system: `/opt/aasx-digital/monitor.sh`
- Health check: `curl http://localhost:8000/health`
- Backup status: `ls -la /opt/aasx-digital/backups/`

## 🎯 Next Steps

1. **Choose your deployment option** based on budget and requirements
2. **Set up the server/infrastructure** following the guide
3. **Deploy the application** using the provided scripts
4. **Configure monitoring and alerts** for production reliability
5. **Test thoroughly** before going live
6. **Monitor performance** and optimize as needed

Your AASX Digital Twin Analytics Framework will be live at `www.aasx-digital.de`! 🚀 