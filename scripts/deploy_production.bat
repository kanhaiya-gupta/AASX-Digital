@echo off
REM AASX Digital Twin Analytics Framework - Production Deployment Script (Windows)
REM For www.aasx-digital.de

setlocal enabledelayedexpansion

REM Configuration
set DOMAIN=aasx-digital.de
set APP_DIR=C:\aasx-digital
set BACKUP_DIR=C:\aasx-digital\backups
set LOG_DIR=C:\aasx-digital\logs

REM Colors for output (Windows 10+)
set GREEN=[92m
set YELLOW=[93m
set RED=[91m
set NC=[0m

REM Logging function
:log
echo %GREEN%[%date% %time%] %~1%NC%
goto :eof

:warn
echo %YELLOW%[%date% %time%] WARNING: %~1%NC%
goto :eof

:error
echo %RED%[%date% %time%] ERROR: %~1%NC%
exit /b 1

REM Check if running as administrator
:check_admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    call :error "This script must be run as Administrator"
    pause
    exit /b 1
)
call :log "Running as Administrator"
goto :eof

REM Check system requirements
:check_system
call :log "Checking system requirements..."

REM Check Windows version
ver | findstr /i "10\.0\|11\.0" >nul
if %errorLevel% neq 0 (
    call :warn "This script is tested on Windows 10/11. Other versions may require modifications."
)

REM Check available memory (minimum 4GB)
for /f "tokens=2" %%i in ('wmic computersystem get TotalPhysicalMemory /value ^| find "="') do set TOTAL_MEM=%%i
set /a TOTAL_MEM_GB=%TOTAL_MEM:~0,-1%/1024/1024/1024
if %TOTAL_MEM_GB% LSS 4 (
    call :error "At least 4GB RAM is required. Available: %TOTAL_MEM_GB%GB"
)

REM Check available disk space (minimum 20GB)
for /f "tokens=3" %%i in ('dir C:\ ^| find "bytes free"') do set FREE_SPACE=%%i
set FREE_SPACE=%FREE_SPACE:,=%
set /a FREE_SPACE_GB=%FREE_SPACE%/1024/1024/1024
if %FREE_SPACE_GB% LSS 20 (
    call :error "At least 20GB free disk space is required. Available: %FREE_SPACE_GB%GB"
)

call :log "System requirements check passed"
goto :eof

REM Install Chocolatey (Windows package manager)
:install_chocolatey
call :log "Installing Chocolatey package manager..."
if not exist "C:\ProgramData\chocolatey\bin\choco.exe" (
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    if %errorLevel% neq 0 (
        call :error "Failed to install Chocolatey"
    )
)
call :log "Chocolatey installed successfully"
goto :eof

REM Install Docker Desktop
:install_docker
call :log "Installing Docker Desktop..."
choco install docker-desktop -y
if %errorLevel% neq 0 (
    call :error "Failed to install Docker Desktop"
)

REM Start Docker Desktop
call :log "Starting Docker Desktop..."
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

REM Wait for Docker to start
call :log "Waiting for Docker to start..."
:wait_docker
docker version >nul 2>&1
if %errorLevel% neq 0 (
    timeout /t 5 /nobreak >nul
    goto :wait_docker
)

call :log "Docker Desktop installed and started"
goto :eof

REM Install Git
:install_git
call :log "Installing Git..."
choco install git -y
if %errorLevel% neq 0 (
    call :error "Failed to install Git"
)
call :log "Git installed successfully"
goto :eof

REM Setup application directory
:setup_app_directory
call :log "Setting up application directory..."

REM Create application directory
if not exist "%APP_DIR%" mkdir "%APP_DIR%"

REM Create subdirectories
if not exist "%APP_DIR%\data" mkdir "%APP_DIR%\data"
if not exist "%APP_DIR%\output" mkdir "%APP_DIR%\output"
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"
if not exist "%APP_DIR%\backups" mkdir "%APP_DIR%\backups"
if not exist "%APP_DIR%\certificates" mkdir "%APP_DIR%\certificates"

call :log "Application directory setup complete"
goto :eof

REM Clone and setup application
:setup_application
call :log "Setting up application..."

cd /d "%APP_DIR%"

REM Clone repository (replace with your actual repository URL)
if not exist ".git" (
    git clone https://github.com/your-username/aas-data-modeling.git .
    if %errorLevel% neq 0 (
        call :error "Failed to clone repository"
    )
) else (
    git pull origin main
    if %errorLevel% neq 0 (
        call :warn "Failed to pull latest changes"
    )
)

REM Create production environment file
if not exist ".env" (
    call :log "Creating .env file..."
    (
        echo # Production Environment Variables
        echo NODE_ENV=production
        echo FLASK_ENV=production
        echo.
        echo # Database Configuration
        echo DATABASE_URL=postgresql://aasx_user:aasx_password@postgres:5432/aasx_data
        echo REDIS_URL=redis://redis:6379
        echo.
        echo # Neo4j Configuration
        echo NEO4J_URI=neo4j://neo4j:7687
        echo NEO4J_USER=neo4j
        echo NEO4J_PASSWORD=your_secure_neo4j_password
        echo.
        echo # Qdrant Configuration
        echo QDRANT_URL=http://qdrant:6333
        echo.
        echo # AI Services
        echo OPENAI_API_KEY=your_openai_api_key
        echo ANTHROPIC_API_KEY=your_anthropic_api_key
        echo.
        echo # Security
        echo SECRET_KEY=your_very_secure_secret_key_here
        echo JWT_SECRET=your_jwt_secret_key_here
        echo.
        echo # Application
        echo APP_HOST=0.0.0.0
        echo APP_PORT=8000
        echo DEBUG=false
        echo.
        echo # Domain
        echo DOMAIN=aasx-digital.de
        echo ALLOWED_HOSTS=["aasx-digital.de", "www.aasx-digital.de"]
    ) > .env
    
    call :warn "Please edit .env file with your actual API keys and passwords"
    pause
)

call :log "Application setup complete"
goto :eof

REM Create production docker-compose file
:create_docker_compose
call :log "Creating production Docker Compose configuration..."

cd /d "%APP_DIR%"

(
    echo version: '3.8'
    echo.
    echo services:
    echo   # Main Web Application
    echo   webapp:
    echo     build:
    echo       context: .
    echo       dockerfile: docker/Dockerfile.webapp
    echo     container_name: aasx-webapp-prod
    echo     restart: unless-stopped
    echo     environment:
    echo       - NODE_ENV=production
    echo       - FLASK_ENV=production
    echo     env_file:
    echo       - .env
    echo     volumes:
    echo       - ./data:/app/data
    echo       - ./output:/app/output
    echo       - ./logs:/app/logs
    echo       - ./certificates:/app/certificates
    echo     ports:
    echo       - "8000:8000"
    echo     depends_on:
    echo       - postgres
    echo       - redis
    echo       - neo4j
    echo       - qdrant
    echo     networks:
    echo       - aasx-network
    echo     healthcheck:
    echo       test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    echo       interval: 30s
    echo       timeout: 10s
    echo       retries: 3
    echo.
    echo   # AI/RAG System
    echo   ai-rag:
    echo     build:
    echo       context: .
    echo       dockerfile: docker/Dockerfile.ai-rag
    echo     container_name: aasx-ai-rag-prod
    echo     restart: unless-stopped
    echo     env_file:
    echo       - .env
    echo     volumes:
    echo       - ./data:/app/data
    echo       - ./output:/app/output
    echo       - ./logs:/app/logs
    echo     depends_on:
    echo       - postgres
    echo       - redis
    echo       - neo4j
    echo       - qdrant
    echo     networks:
    echo       - aasx-network
    echo.
    echo   # Digital Twin Registry
    echo   twin-registry:
    echo     build:
    echo       context: .
    echo       dockerfile: docker/Dockerfile.twin-registry
    echo     container_name: aasx-twin-registry-prod
    echo     restart: unless-stopped
    echo     env_file:
    echo       - .env
    echo     volumes:
    echo       - ./data:/app/data
    echo       - ./logs:/app/logs
    echo     depends_on:
    echo       - postgres
    echo       - neo4j
    echo     networks:
    echo       - aasx-network
    echo.
    echo   # Certificate Manager
    echo   certificate-manager:
    echo     build:
    echo       context: .
    echo       dockerfile: docker/Dockerfile.certificate-manager
    echo     container_name: aasx-cert-manager-prod
    echo     restart: unless-stopped
    echo     env_file:
    echo       - .env
    echo     volumes:
    echo       - ./certificates:/app/certificates
    echo       - ./logs:/app/logs
    echo     depends_on:
    echo       - postgres
    echo     networks:
    echo       - aasx-network
    echo.
    echo   # Quality Infrastructure Analytics
    echo   qi-analytics:
    echo     build:
    echo       context: .
    echo       dockerfile: docker/Dockerfile.qi-analytics
    echo     container_name: aasx-qi-analytics-prod
    echo     restart: unless-stopped
    echo     env_file:
    echo       - .env
    echo     volumes:
    echo       - ./output:/app/output
    echo       - ./logs:/app/logs
    echo     depends_on:
    echo       - postgres
    echo       - ai-rag
    echo     networks:
    echo       - aasx-network
    echo.
    echo   # PostgreSQL Database
    echo   postgres:
    echo     image: postgres:15-alpine
    echo     container_name: aasx-postgres-prod
    echo     restart: unless-stopped
    echo     environment:
    echo       POSTGRES_DB: aasx_data
    echo       POSTGRES_USER: aasx_user
    echo       POSTGRES_PASSWORD: aasx_password
    echo     volumes:
    echo       - postgres_data:/var/lib/postgresql/data
    echo       - ./backups:/backups
    echo     networks:
    echo       - aasx-network
    echo     healthcheck:
    echo       test: ["CMD-SHELL", "pg_isready -U aasx_user -d aasx_data"]
    echo       interval: 30s
    echo       timeout: 10s
    echo       retries: 3
    echo.
    echo   # Redis Cache
    echo   redis:
    echo     image: redis:7-alpine
    echo     container_name: aasx-redis-prod
    echo     restart: unless-stopped
    echo     volumes:
    echo       - redis_data:/data
    echo     networks:
    echo       - aasx-network
    echo     healthcheck:
    echo       test: ["CMD", "redis-cli", "ping"]
    echo       interval: 30s
    echo       timeout: 10s
    echo       retries: 3
    echo.
    echo   # Neo4j Graph Database
    echo   neo4j:
    echo     image: neo4j:5.15-community
    echo     container_name: aasx-neo4j-prod
    echo     restart: unless-stopped
    echo     environment:
    echo       NEO4J_AUTH: neo4j/your_secure_neo4j_password
    echo       NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
    echo       NEO4J_dbms_security_procedures_unrestricted: apoc.*,gds.*
    echo     volumes:
    echo       - neo4j_data:/data
    echo       - neo4j_logs:/logs
    echo       - neo4j_import:/var/lib/neo4j/import
    echo       - neo4j_plugins:/plugins
    echo     ports:
    echo       - "7474:7474"
    echo       - "7687:7687"
    echo     networks:
    echo       - aasx-network
    echo     healthcheck:
    echo       test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "your_secure_neo4j_password", "RETURN 1"]
    echo       interval: 30s
    echo       timeout: 10s
    echo       retries: 3
    echo.
    echo   # Qdrant Vector Database
    echo   qdrant:
    echo     image: qdrant/qdrant:latest
    echo     container_name: aasx-qdrant-prod
    echo     restart: unless-stopped
    echo     volumes:
    echo       - qdrant_data:/qdrant/storage
    echo     ports:
    echo       - "6333:6333"
    echo       - "6334:6334"
    echo     networks:
    echo       - aasx-network
    echo     healthcheck:
    echo       test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
    echo       interval: 30s
    echo       timeout: 10s
    echo       retries: 3
    echo.
    echo volumes:
    echo   postgres_data:
    echo   redis_data:
    echo   neo4j_data:
    echo   neo4j_logs:
    echo   neo4j_import:
    echo   neo4j_plugins:
    echo   qdrant_data:
    echo.
    echo networks:
    echo   aasx-network:
    echo     driver: bridge
) > docker-compose.prod.yml

call :log "Docker Compose configuration created"
goto :eof

REM Create monitoring scripts
:create_monitoring_scripts
call :log "Creating monitoring scripts..."

cd /d "%APP_DIR%"

REM Health check script
(
    echo @echo off
    echo REM AASX Digital Health Check Script
    echo.
    echo set LOG_FILE=%LOG_DIR%\health-check.log
    echo set EMAIL=your-email@example.com
    echo.
    echo echo [%date% %time%] Starting health check ^>^> "%LOG_FILE%"
    echo.
    echo REM Check application health
    echo curl -f http://localhost:8000/health ^>nul 2^>^&1
    echo if %%errorLevel%% neq 0 ^(
    echo     echo [%date% %time%] ERROR: Application health check failed ^>^> "%LOG_FILE%"
    echo     echo AASX Digital Alert: Application health check failed ^| mail -s "AASX Digital Alert" %%EMAIL%%
    echo     exit /b 1
    echo ^)
    echo.
    echo REM Check database connectivity
    echo docker-compose -f "%APP_DIR%\docker-compose.prod.yml" exec -T postgres pg_isready -U aasx_user -d aasx_data ^>nul 2^>^&1
    echo if %%errorLevel%% neq 0 ^(
    echo     echo [%date% %time%] ERROR: Database health check failed ^>^> "%LOG_FILE%"
    echo     echo AASX Digital Alert: Database health check failed ^| mail -s "AASX Digital Alert" %%EMAIL%%
    echo     exit /b 1
    echo ^)
    echo.
    echo echo [%date% %time%] Health check completed successfully ^>^> "%LOG_FILE%"
) > health-check.bat

REM Backup script
(
    echo @echo off
    echo REM AASX Digital Backup Script
    echo.
    echo set BACKUP_DIR=%BACKUP_DIR%
    echo set DATE=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    echo set LOG_FILE=%LOG_DIR%\backup.log
    echo.
    echo echo [%date% %time%] Starting backup process... ^>^> "%LOG_FILE%"
    echo.
    echo REM Create backup directory
    echo if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
    echo.
    echo REM Database backup
    echo echo [%date% %time%] Creating database backup... ^>^> "%LOG_FILE%"
    echo docker-compose -f "%APP_DIR%\docker-compose.prod.yml" run --rm backup
    echo.
    echo REM Application data backup
    echo echo [%date% %time%] Creating application data backup... ^>^> "%LOG_FILE%"
    echo powershell -Command "Compress-Archive -Path '%APP_DIR%\data', '%APP_DIR%\output', '%APP_DIR%\certificates' -DestinationPath '%BACKUP_DIR%\app_data_%DATE%.zip' -Force"
    echo.
    echo REM Clean old backups ^(keep last 7 days^)
    echo echo [%date% %time%] Cleaning old backups... ^>^> "%LOG_FILE%"
    echo forfiles /p "%BACKUP_DIR%" /s /m *.sql /d -7 /c "cmd /c del @path" 2^>nul
    echo forfiles /p "%BACKUP_DIR%" /s /m *.zip /d -7 /c "cmd /c del @path" 2^>nul
    echo.
    echo echo [%date% %time%] Backup completed: %DATE% ^>^> "%LOG_FILE%"
) > backup.bat

REM Monitoring script
(
    echo @echo off
    echo REM AASX Digital System Monitoring Script
    echo.
    echo echo === AASX Digital System Status ===
    echo echo Date: %date% %time%
    echo echo.
    echo.
    echo echo === Docker Containers ===
    echo docker-compose -f "%APP_DIR%\docker-compose.prod.yml" ps
    echo.
    echo echo.
    echo echo === System Resources ===
    echo wmic logicaldisk get size,freespace,caption
    echo wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value
    echo.
    echo echo.
    echo echo === Application Health ===
    echo curl -s http://localhost:8000/health
    echo.
    echo echo.
    echo echo === Database Status ===
    echo docker-compose -f "%APP_DIR%\docker-compose.prod.yml" exec -T postgres pg_isready -U aasx_user -d aasx_data
    echo.
    echo echo.
    echo echo === Recent Logs ===
    echo if exist "%LOG_DIR%\*.log" ^(
    echo     for /f "delims=" %%i in ^('dir /b "%LOG_DIR%\*.log"'^) do ^(
    echo         echo --- %%i ---
    echo         powershell -Command "Get-Content '%LOG_DIR%\%%i' -Tail 10"
    echo         echo.
    echo     ^)
    echo ^) else ^(
    echo     echo No log files found
    echo ^)
) > monitor.bat

call :log "Monitoring scripts created"
goto :eof

REM Build and start application
:deploy_application
call :log "Building and deploying application..."

cd /d "%APP_DIR%"

REM Build images
call :log "Building Docker images..."
docker-compose -f docker-compose.prod.yml build
if %errorLevel% neq 0 (
    call :error "Failed to build Docker images"
)

REM Start services
call :log "Starting services..."
docker-compose -f docker-compose.prod.yml up -d
if %errorLevel% neq 0 (
    call :error "Failed to start services"
)

REM Wait for services to be ready
call :log "Waiting for services to be ready..."
timeout /t 30 /nobreak >nul

REM Check service status
call :log "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

call :log "Application deployment complete"
goto :eof

REM Final verification
:verify_deployment
call :log "Verifying deployment..."

REM Check if application is responding
curl -f http://localhost:8000/health >nul 2>&1
if %errorLevel% equ 0 (
    call :log "✅ Application is responding"
) else (
    call :error "❌ Application is not responding"
)

call :log "🎉 Deployment verification successful!"
call :log "Your AASX Digital Twin Analytics Framework is now running at:"
call :log "   http://localhost:8000"
call :log "   http://%DOMAIN% (after DNS configuration)"
goto :eof

REM Main deployment function
:main
call :log "🚀 Starting AASX Digital Twin Analytics Framework Production Deployment"
call :log "Domain: %DOMAIN%"
call :log "Application Directory: %APP_DIR%"

REM Check if running as administrator
call :check_admin

REM System checks
call :check_system

REM Installation steps
call :install_chocolatey
call :install_docker
call :install_git
call :setup_app_directory
call :setup_application
call :create_docker_compose
call :create_monitoring_scripts
call :deploy_application
call :verify_deployment

call :log "🎉 Production deployment completed successfully!"
call :log ""
call :log "📋 Next steps:"
call :log "   1. Update DNS records to point to this server"
call :log "   2. Test all functionality at http://localhost:8000"
call :log "   3. Monitor logs: type %LOG_DIR%\*.log"
call :log "   4. Check status: %APP_DIR%\monitor.bat"
call :log "   5. Set up additional monitoring (optional)"
call :log ""
call :log "🔧 Useful commands:"
call :log "   - View logs: docker-compose -f %APP_DIR%\docker-compose.prod.yml logs -f"
call :log "   - Restart services: docker-compose -f %APP_DIR%\docker-compose.prod.yml restart"
call :log "   - Backup: %APP_DIR%\backup.bat"
call :log "   - Monitor: %APP_DIR%\monitor.bat"
call :log "   - Health check: %APP_DIR%\health-check.bat"
call :log ""
pause
goto :eof

REM Run main function
call :main 