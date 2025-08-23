# API Layer

The API Layer provides the external interface for the AAS Data Modeling Engine, enabling external modules and systems to interact with the engine through RESTful APIs, comprehensive middleware, and enterprise-grade features.

## 🏗️ Architecture Overview

The API Layer is built with a modular, middleware-based architecture that provides:

- **API Gateway**: Central entry point for all external requests
- **Middleware Stack**: Authentication, authorization, rate limiting, and more
- **Rate Limiting**: Multiple algorithms with configurable limits
- **API Versioning**: Comprehensive version management and backward compatibility
- **Documentation**: OpenAPI/Swagger generation and interactive docs
- **Health Monitoring**: Real-time system health and performance monitoring

## 🚀 Core Components

### 1. API Gateway (`gateway.py`)

The main entry point for all external API requests, handling routing, request processing, and response formatting.

**Features:**
- RESTful endpoint routing and dispatching
- Request/response transformation
- Error handling and logging
- Cross-cutting concerns management
- Load balancing and failover support

**Key Methods:**
```python
# Initialize gateway
gateway = APIGateway()

# Add custom routes
gateway.add_route("POST", "/api/v1/custom", custom_handler)

# Process requests
response = await gateway.process_request(
    method="GET",
    path="/health",
    headers={},
    query_params={}
)
```

### 2. API Middleware (`middleware.py`)

Comprehensive middleware components for cross-cutting concerns including authentication, authorization, validation, and more.

**Available Middleware:**

#### Authentication Middleware
- **API Key Authentication**: Simple key-based auth
- **JWT Token Authentication**: JSON Web Token support
- **HMAC Signature Authentication**: Secure signature-based auth

```python
# Initialize with API keys
auth_middleware = AuthenticationMiddleware(
    api_keys={"key123": "user1", "key456": "user2"},
    jwt_secret="your-secret-key"
)

# Add to gateway
gateway.add_middleware(auth_middleware)
```

#### Authorization Middleware
- **Permission-based access control**
- **Role-based authorization**
- **Endpoint-level security**

```python
# Create authorization middleware
authz_middleware = AuthorizationMiddleware()

# Add permission rules
authz_middleware.add_permission_rule("/api/v1/admin", ["admin", "superuser"])

# Add to gateway
gateway.add_middleware(authz_middleware)
```

#### Rate Limiting Middleware
- **Per-user and per-IP rate limiting**
- **Configurable limits and windows**
- **Multiple algorithms support**

```python
# Create rate limiting middleware
rate_limit_middleware = RateLimitingMiddleware(default_limit=100, window_seconds=60)

# Add to gateway
gateway.add_middleware(rate_limit_middleware)
```

#### Logging Middleware
- **Comprehensive request/response logging**
- **Performance monitoring**
- **Debug information capture**

```python
# Create logging middleware
logging_middleware = LoggingMiddleware(log_level="DEBUG")

# Add to gateway
gateway.add_middleware(logging_middleware)
```

#### Validation Middleware
- **Request structure validation**
- **Data type validation**
- **Custom validation rules**

```python
# Create validation middleware
validation_middleware = ValidationMiddleware()

# Add validation rules
validation_middleware.add_validation_rule("/api/v1/workflows", {
    "required_fields": ["name", "type"],
    "data_types": {"name": "string", "type": "string"}
})

# Add to gateway
gateway.add_middleware(validation_middleware)
```

#### CORS Middleware
- **Cross-Origin Resource Sharing support**
- **Configurable origins and methods**
- **Preflight request handling**

```python
# Create CORS middleware
cors_middleware = CORSMiddleware(
    allowed_origins=["https://app.example.com", "http://localhost:3000"],
    allowed_methods=["GET", "POST", "PUT", "DELETE"]
)

# Add to gateway
gateway.add_middleware(cors_middleware)
```

### 3. Rate Limiting (`rate_limiting.py`)

Advanced rate limiting with multiple algorithms and monitoring capabilities.

**Supported Algorithms:**
- **Token Bucket**: Smooth, burst-friendly rate limiting
- **Fixed Window**: Simple, predictable rate limiting
- **Sliding Window**: Accurate, memory-efficient rate limiting

```python
# Initialize rate limiter
rate_limiter = RateLimiter(default_algorithm="token_bucket")

# Create client-specific limiters
rate_limiter.create_limiter(
    client_id="user123",
    algorithm="token_bucket",
    limit=100,
    window_seconds=60,
    max_burst=200
)

# Check rate limits
allowed, details = await rate_limiter.check_rate_limit("user123")
```

### 4. API Versioning (`versioning.py`)

Comprehensive API version management with backward compatibility and migration support.

**Features:**
- **Version detection** from path, headers, and query parameters
- **Status management** (active, deprecated, sunset)
- **Feature flags** per version
- **Migration guides** and breaking change documentation

```python
# Initialize versioning service
versioning = APIVersioning()

# Add new version
v2 = APIVersion(
    version="v2",
    status=VersionStatus.BETA,
    release_date=datetime.utcnow(),
    features=["advanced_workflows", "ai_integration"],
    breaking_changes=["workflow_schema_changes"]
)

versioning.add_version(v2)

# Detect version from request
detected_version, details = versioning.detect_version(
    path="/api/v2/workflows",
    headers={},
    query_params={}
)
```

### 5. API Documentation (`documentation.py`)

OpenAPI/Swagger documentation generation with multiple output formats.

**Supported Formats:**
- **OpenAPI JSON/YAML**: Machine-readable specifications
- **Swagger UI**: Interactive API explorer
- **ReDoc**: Alternative documentation viewer
- **Markdown**: Human-readable documentation
- **HTML**: Custom documentation pages

```python
# Initialize documentation service
doc_service = APIDocumentation()

# Add custom endpoint documentation
endpoint = EndpointInfo(
    path="/api/v1/custom",
    method="POST",
    summary="Custom Operation",
    description="Performs a custom operation",
    tags=["custom"],
    request_body={
        "description": "Custom data",
        "required": True,
        "content": {
            "application/json": {
                "schema": {"type": "object"}
            }
        }
    }
)

doc_service.add_endpoint(endpoint)

# Generate OpenAPI specification
openapi_spec = doc_service.generate_openapi_spec()

# Export in different formats
swagger_html = doc_service.export_documentation(DocumentationFormat.SWAGGER_UI)
markdown_doc = doc_service.export_documentation(DocumentationFormat.MARKDOWN)
```

### 6. Health Check (`health_check.py`)

Real-time system health monitoring with comprehensive metrics and alerting.

**Features:**
- **Component health monitoring**
- **Performance metrics collection**
- **Threshold-based alerting**
- **Health history tracking**

```python
# Initialize health check service
health_service = HealthCheckService()

# Register custom health check function
async def custom_health_check():
    # Your custom health check logic
    return {
        "status": HealthStatus.HEALTHY,
        "message": "Custom component is healthy",
        "details": {"custom_metric": "value"}
    }

health_service.register_health_check("custom_component", custom_health_check)

# Start monitoring
await health_service.start_health_monitoring()

# Get health summary
health_summary = health_service.get_health_summary()
health_metrics = health_service.get_health_metrics()
```

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Authentication
JWT_SECRET=your-secret-key
API_KEYS=key1:user1,key2:user2

# Rate Limiting
DEFAULT_RATE_LIMIT=100
RATE_LIMIT_WINDOW=60

# Health Monitoring
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=5
```

### Configuration File

```yaml
# config/api.yaml
api:
  host: 0.0.0.0
  port: 8000
  debug: false
  
  middleware:
    authentication:
      enabled: true
      methods: ["api_key", "jwt", "hmac"]
    
    rate_limiting:
      enabled: true
      default_limit: 100
      window_seconds: 60
      algorithm: "token_bucket"
    
    cors:
      enabled: true
      allowed_origins: ["*"]
      allowed_methods: ["GET", "POST", "PUT", "DELETE"]
  
  versioning:
    default_version: "v1"
    supported_versions: ["v1", "v2"]
    
  health_check:
    interval_seconds: 30
    timeout_seconds: 5
    thresholds:
      response_time_warning: 1000
      response_time_critical: 5000
```

## 📡 API Endpoints

### Health Endpoints

```
GET  /health              - Basic health check
GET  /health/detailed     - Detailed health information
```

### Workflow Endpoints

```
GET    /api/v1/workflows              - List workflows
POST   /api/v1/workflows              - Create workflow
GET    /api/v1/workflows/{id}         - Get workflow
PUT    /api/v1/workflows/{id}         - Update workflow
DELETE /api/v1/workflows/{id}         - Delete workflow
```

### Module Endpoints

```
GET    /api/v1/modules                - List modules
GET    /api/v1/modules/{id}           - Get module
POST   /api/v1/modules/{id}/connect   - Connect module
DELETE /api/v1/modules/{id}/disconnect - Disconnect module
```

### Data Endpoints

```
GET    /api/v1/data                   - List data sources
POST   /api/v1/data/process           - Process data
GET    /api/v1/data/status/{job_id}   - Get processing status
```

### Documentation Endpoints

```
GET  /docs                    - API documentation
GET  /openapi.json           - OpenAPI specification
GET  /swagger                - Swagger UI
GET  /redoc                  - ReDoc documentation
```

## 🔐 Authentication & Authorization

### API Key Authentication

```bash
# Request with API key
curl -H "X-API-Key: your-api-key" \
     https://api.example.com/health
```

### JWT Authentication

```bash
# Request with JWT token
curl -H "Authorization: Bearer your-jwt-token" \
     https://api.example.com/api/v1/workflows
```

### HMAC Authentication

```bash
# Request with HMAC signature
curl -H "X-HMAC-Signature: signature" \
     -H "X-Timestamp: 2025-08-21T10:00:00Z" \
     https://api.example.com/api/v1/workflows
```

## 📊 Monitoring & Metrics

### Health Metrics

```python
# Get comprehensive health metrics
metrics = health_service.get_health_metrics()

# Monitor specific components
workflow_health = health_service.get_component_health("workflow_engine")

# Get health alerts
alerts = health_service.get_health_alerts()
```

### Rate Limiting Metrics

```python
# Get rate limiting statistics
stats = rate_limiter.get_global_stats()

# Monitor specific client limits
client_status = rate_limiter.get_limiter_status("user123")
```

### API Gateway Metrics

```python
# Get gateway statistics
gateway_status = gateway.get_gateway_status()

# Monitor request processing
total_requests = gateway_status["total_requests"]
error_count = gateway_status["error_count"]
```

## 🚀 Getting Started

### 1. Basic Setup

```python
from integration.api import APIGateway, AuthenticationMiddleware, HealthCheckService

# Initialize services
gateway = APIGateway()
auth_middleware = AuthenticationMiddleware()
health_service = HealthCheckService()

# Add middleware
gateway.add_middleware(auth_middleware)

# Start services
await gateway.start_gateway()
await health_service.start_health_monitoring()
```

### 2. Custom Endpoint

```python
async def custom_workflow_handler(request):
    return {
        "success": True,
        "data": {"message": "Custom workflow created"},
        "status_code": 201
    }

# Add custom route
gateway.add_route("POST", "/api/v1/custom-workflow", custom_workflow_handler)
```

### 3. Custom Health Check

```python
async def database_health_check():
    try:
        # Your database health check logic
        return {
            "status": HealthStatus.HEALTHY,
            "message": "Database connection successful",
            "details": {"connection_pool": "active"}
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": "Database connection failed",
            "error": str(e)
        }

# Register health check
health_service.register_health_check("database", database_health_check)
```

## 🔧 Advanced Configuration

### Custom Middleware

```python
class CustomMiddleware(APIMiddleware):
    async def process_request(self, request):
        # Add custom request processing
        request["custom_field"] = "custom_value"
        return request

# Add custom middleware
gateway.add_middleware(CustomMiddleware("CustomMiddleware"))
```

### Custom Rate Limiting

```python
# Create custom rate limiter
rate_limiter.create_limiter(
    client_id="premium_user",
    algorithm="sliding_window",
    limit=1000,
    window_seconds=60
)

# Update existing limiter
rate_limiter.update_limiter_config(
    client_id="user123",
    limit=200,
    window_seconds=30
)
```

### Version-Specific Features

```python
# Enable feature for specific version
versioning.add_feature_flag("v2", "ai_integration", True)

# Check feature availability
if versioning.get_feature_flag("v2", "ai_integration"):
    # Use AI integration features
    pass
```

## 📈 Performance & Scalability

### Rate Limiting Strategies

- **Token Bucket**: Best for burst traffic and smooth rate limiting
- **Fixed Window**: Simple and predictable, good for basic use cases
- **Sliding Window**: Most accurate, good for strict rate limiting

### Health Check Optimization

- **Configurable intervals**: Adjust based on component criticality
- **Async health checks**: Non-blocking health monitoring
- **Threshold-based alerts**: Prevent alert fatigue

### Middleware Performance

- **Ordered execution**: Optimize middleware chain order
- **Conditional execution**: Skip middleware when not needed
- **Async processing**: Non-blocking middleware execution

## 🛡️ Security Features

### Authentication Methods

- **API Key**: Simple and fast, good for server-to-server communication
- **JWT**: Stateless and scalable, good for user authentication
- **HMAC**: Secure and tamper-proof, good for high-security applications

### Authorization

- **Permission-based**: Fine-grained access control
- **Role-based**: Group-based permissions
- **Endpoint-level**: Granular security per endpoint

### Rate Limiting

- **Per-client limits**: Prevent abuse from individual clients
- **Algorithm variety**: Choose best strategy for your use case
- **Configurable thresholds**: Adjust based on application needs

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check API key format and validity
   - Verify JWT token expiration
   - Ensure HMAC signature calculation

2. **Rate Limiting Issues**
   - Monitor client rate limit status
   - Check rate limiting configuration
   - Verify client identification

3. **Health Check Failures**
   - Review component health status
   - Check health check configuration
   - Monitor performance thresholds

### Debug Mode

```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug middleware
logging_middleware = LoggingMiddleware(log_level="DEBUG")
gateway.add_middleware(logging_middleware)
```

### Health Check Debugging

```python
# Force health check for specific component
health_service.force_health_check("workflow_engine")

# Get detailed component health
component_health = health_service.get_component_health("workflow_engine")
print(f"Component status: {component_health['status']}")
print(f"Last check: {component_health['last_check']}")
print(f"Response time: {component_health['average_response_time']}ms")
```

## 📚 Additional Resources

- **OpenAPI Specification**: [OpenAPI 3.0 Documentation](https://swagger.io/specification/)
- **Swagger UI**: [Interactive API Documentation](https://swagger.io/tools/swagger-ui/)
- **ReDoc**: [Alternative API Documentation](https://github.com/Redocly/redoc)
- **Rate Limiting**: [Rate Limiting Strategies](https://en.wikipedia.org/wiki/Rate_limiting)
- **Health Checks**: [Health Check Patterns](https://microservices.io/patterns/observability/health-check.html)

## 🤝 Contributing

When contributing to the API Layer:

1. **Follow the existing code style** and patterns
2. **Add comprehensive tests** for new functionality
3. **Update documentation** for new features
4. **Consider backward compatibility** when making changes
5. **Follow security best practices** for authentication and authorization

## 📄 License

This API Layer is part of the AAS Data Modeling Engine and is licensed under the MIT License.


