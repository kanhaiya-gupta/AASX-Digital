#!/bin/bash

# AASX Digital Twin Analytics Framework - Production Deployment Script
# For www.aasx-digital.de

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="aasx-digital.de"
APP_DIR="/opt/aasx-digital"
BACKUP_DIR="/opt/aasx-digital/backups"
LOG_DIR="/opt/aasx-digital/logs"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as a regular user with sudo privileges."
    fi
}

# Check system requirements
check_system() {
    log "Checking system requirements..."
    
    # Check OS
    if [[ ! -f /etc/os-release ]]; then
        error "Cannot determine operating system"
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
        warn "This script is tested on Ubuntu/Debian. Other distributions may require modifications."
    fi
    
    # Check available memory
    local mem_total=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [[ $mem_total -lt 4096 ]]; then
        error "At least 4GB RAM is required. Available: ${mem_total}MB"
    fi
    
    # Check available disk space
    local disk_space=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
    if [[ $disk_space -lt 20 ]]; then
        error "At least 20GB free disk space is required. Available: ${disk_space}GB"
    fi
    
    log "System requirements check passed"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    sudo apt update
    
    # Install required packages
    sudo apt install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        htop \
        iotop \
        nethogs \
        fail2ban \
        ufw \
        logrotate \
        certbot \
        python3-certbot-nginx
    
    log "System dependencies installed"
}

# Install Docker
install_docker() {
    log "Installing Docker..."
    
    # Remove old versions
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    log "Docker installed successfully"
}

# Install Nginx
install_nginx() {
    log "Installing and configuring Nginx..."
    
    sudo apt install -y nginx
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << 'EOF'
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
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Client max body size for file uploads
    client_max_body_size 100M;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

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

    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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
    sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    sudo nginx -t
    
    # Reload Nginx
    sudo systemctl reload nginx
    sudo systemctl enable nginx
    
    log "Nginx configured successfully"
}

# Setup application directory
setup_app_directory() {
    log "Setting up application directory..."
    
    # Create application directory
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
    
    # Create subdirectories
    mkdir -p $APP_DIR/{data,output,logs,backups,certificates}
    
    # Set permissions
    chmod 755 $APP_DIR
    chmod 755 $APP_DIR/{data,output,logs,backups,certificates}
    
    log "Application directory setup complete"
}

# Clone and setup application
setup_application() {
    log "Setting up application..."
    
    cd $APP_DIR
    
    # Clone repository (replace with your actual repository URL)
    if [[ ! -d ".git" ]]; then
        git clone https://github.com/your-username/aas-data-modeling.git .
    else
        git pull origin main
    fi
    
    # Create production environment file
    if [[ ! -f ".env" ]]; then
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
        
        warn "Please edit .env file with your actual API keys and passwords"
        read -p "Press Enter after editing .env file..."
    fi
    
    log "Application setup complete"
}

# Create production docker-compose file
create_docker_compose() {
    log "Creating production Docker Compose configuration..."
    
    cd $APP_DIR
    
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
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

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
    
    log "Docker Compose configuration created"
}

# Setup SSL certificate
setup_ssl() {
    log "Setting up SSL certificate..."
    
    # Get SSL certificate
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email your-email@example.com
    
    # Test renewal
    sudo certbot renew --dry-run
    
    log "SSL certificate setup complete"
}

# Setup firewall
setup_firewall() {
    log "Setting up firewall..."
    
    # Configure UFW
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    
    log "Firewall configured"
}

# Create monitoring scripts
create_monitoring_scripts() {
    log "Creating monitoring scripts..."
    
    cd $APP_DIR
    
    # Health check script
    cat > health-check.sh << 'EOF'
#!/bin/bash

# AASX Digital Health Check Script

LOG_FILE="/opt/aasx-digital/logs/health-check.log"
EMAIL="your-email@example.com"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Check application health
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "ERROR: Application health check failed"
    echo "AASX Digital Alert: Application health check failed" | mail -s "AASX Digital Alert" $EMAIL
    exit 1
fi

# Check database connectivity
if ! docker-compose -f /opt/aasx-digital/docker-compose.prod.yml exec -T postgres pg_isready -U aasx_user -d aasx_data > /dev/null 2>&1; then
    log "ERROR: Database health check failed"
    echo "AASX Digital Alert: Database health check failed" | mail -s "AASX Digital Alert" $EMAIL
    exit 1
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
if [[ $DISK_USAGE -gt 90 ]]; then
    log "WARNING: Disk usage is ${DISK_USAGE}%"
    echo "AASX Digital Warning: High disk usage (${DISK_USAGE}%)" | mail -s "AASX Digital Warning" $EMAIL
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [[ $MEM_USAGE -gt 90 ]]; then
    log "WARNING: Memory usage is ${MEM_USAGE}%"
    echo "AASX Digital Warning: High memory usage (${MEM_USAGE}%)" | mail -s "AASX Digital Warning" $EMAIL
fi

log "Health check completed successfully"
EOF

    chmod +x health-check.sh
    
    # Backup script
    cat > backup.sh << 'EOF'
#!/bin/bash

# AASX Digital Backup Script

BACKUP_DIR="/opt/aasx-digital/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/opt/aasx-digital/logs/backup.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Create backup directory
mkdir -p $BACKUP_DIR

log "Starting backup process..."

# Database backup
log "Creating database backup..."
docker-compose -f /opt/aasx-digital/docker-compose.prod.yml run --rm backup

# Application data backup
log "Creating application data backup..."
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz \
    /opt/aasx-digital/data \
    /opt/aasx-digital/output \
    /opt/aasx-digital/certificates

# Clean old backups (keep last 7 days)
log "Cleaning old backups..."
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

log "Backup completed: $DATE"
EOF

    chmod +x backup.sh
    
    # Monitoring script
    cat > monitor.sh << 'EOF'
#!/bin/bash

# AASX Digital System Monitoring Script

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
curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "Health check failed"

echo ""
echo "=== Database Status ==="
docker-compose -f /opt/aasx-digital/docker-compose.prod.yml exec -T postgres pg_isready -U aasx_user -d aasx_data

echo ""
echo "=== Recent Logs ==="
tail -n 20 /opt/aasx-digital/logs/*.log 2>/dev/null || echo "No log files found"
EOF

    chmod +x monitor.sh
    
    log "Monitoring scripts created"
}

# Setup cron jobs
setup_cron() {
    log "Setting up automated tasks..."
    
    # Add health check to crontab (every 5 minutes)
    (crontab -l 2>/dev/null; echo "*/5 * * * * /opt/aasx-digital/health-check.sh") | crontab -
    
    # Add backup to crontab (daily at 2 AM)
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/aasx-digital/backup.sh") | crontab -
    
    # Add SSL renewal to crontab (twice daily)
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    
    log "Automated tasks configured"
}

# Build and start application
deploy_application() {
    log "Building and deploying application..."
    
    cd $APP_DIR
    
    # Build images
    log "Building Docker images..."
    docker-compose -f docker-compose.prod.yml build
    
    # Start services
    log "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check service status
    log "Checking service status..."
    docker-compose -f docker-compose.prod.yml ps
    
    log "Application deployment complete"
}

# Final verification
verify_deployment() {
    log "Verifying deployment..."
    
    # Check if application is responding
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ Application is responding"
    else
        error "❌ Application is not responding"
    fi
    
    # Check if Nginx is working
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log "✅ Nginx proxy is working"
    else
        error "❌ Nginx proxy is not working"
    fi
    
    # Check SSL certificate
    if curl -f https://$DOMAIN/health > /dev/null 2>&1; then
        log "✅ SSL certificate is working"
    else
        error "❌ SSL certificate is not working"
    fi
    
    log "🎉 Deployment verification successful!"
    log "Your AASX Digital Twin Analytics Framework is now live at:"
    log "   https://$DOMAIN"
    log "   https://www.$DOMAIN"
}

# Main deployment function
main() {
    log "🚀 Starting AASX Digital Twin Analytics Framework Production Deployment"
    log "Domain: $DOMAIN"
    log "Application Directory: $APP_DIR"
    
    # Check if running as root
    check_root
    
    # System checks
    check_system
    
    # Installation steps
    install_dependencies
    install_docker
    install_nginx
    setup_app_directory
    setup_application
    create_docker_compose
    setup_ssl
    setup_firewall
    create_monitoring_scripts
    setup_cron
    deploy_application
    verify_deployment
    
    log "🎉 Production deployment completed successfully!"
    log ""
    log "📋 Next steps:"
    log "   1. Update DNS records to point to this server"
    log "   2. Test all functionality at https://$DOMAIN"
    log "   3. Monitor logs: tail -f $LOG_DIR/*.log"
    log "   4. Check status: $APP_DIR/monitor.sh"
    log "   5. Set up additional monitoring (optional)"
    log ""
    log "🔧 Useful commands:"
    log "   - View logs: docker-compose -f $APP_DIR/docker-compose.prod.yml logs -f"
    log "   - Restart services: docker-compose -f $APP_DIR/docker-compose.prod.yml restart"
    log "   - Backup: $APP_DIR/backup.sh"
    log "   - Monitor: $APP_DIR/monitor.sh"
    log "   - Health check: $APP_DIR/health-check.sh"
}

# Run main function
main "$@" 