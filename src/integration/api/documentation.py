"""
API Documentation Service

This module provides comprehensive API documentation capabilities for the
AAS Data Modeling Engine, including OpenAPI/Swagger generation, interactive
API explorer, and documentation management.

The documentation service handles:
- OpenAPI/Swagger specification generation
- Interactive API documentation
- Endpoint documentation and examples
- Schema documentation
- API changelog and version history
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class DocumentationFormat(str, Enum):
    """Supported documentation formats."""
    OPENAPI_JSON = "openapi_json"
    OPENAPI_YAML = "openapi_yaml"
    SWAGGER_UI = "swagger_ui"
    REDOC = "redoc"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class EndpointInfo:
    """Information about an API endpoint."""
    
    path: str
    method: str
    summary: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    deprecated: bool = False
    version_added: str = "v1"
    version_deprecated: Optional[str] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_openapi(self) -> Dict[str, Any]:
        """Convert to OpenAPI specification format."""
        openapi_spec = {
            "summary": self.summary,
            "description": self.description,
            "tags": self.tags,
            "parameters": self.parameters,
            "responses": self.responses,
            "deprecated": self.deprecated
        }
        
        if self.request_body:
            openapi_spec["requestBody"] = self.request_body
        
        if self.examples:
            openapi_spec["examples"] = self.examples
        
        return openapi_spec


@dataclass
class SchemaInfo:
    """Information about a data schema."""
    
    name: str
    type: str
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    example: Optional[Any] = None
    deprecated: bool = False
    version_added: str = "v1"
    
    def to_openapi(self) -> Dict[str, Any]:
        """Convert to OpenAPI specification format."""
        schema = {
            "type": self.type,
            "description": self.description,
            "properties": self.properties,
            "required": self.required
        }
        
        if self.example is not None:
            schema["example"] = self.example
        
        if self.deprecated:
            schema["deprecated"] = True
        
        return schema


class APIDocumentation:
    """
    Comprehensive API documentation service.
    
    Generates OpenAPI/Swagger specifications, provides interactive
    documentation, and manages API documentation lifecycle.
    """
    
    def __init__(self):
        """Initialize the API documentation service."""
        self.endpoints: Dict[str, EndpointInfo] = {}
        self.schemas: Dict[str, SchemaInfo] = {}
        self.tags: Dict[str, Dict[str, Any]] = {}
        self.info = {
            "title": "AAS Data Modeling Engine API",
            "description": "Enterprise-grade Asset Administration Shell (AAS) data modeling engine with comprehensive workflow orchestration and module management capabilities.",
            "version": "1.0.0",
            "contact": {
                "name": "AAS Data Modeling Team",
                "email": "support@aas-engine.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        }
        self.servers = [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.aas-engine.com",
                "description": "Production server"
            }
        ]
        
        # Initialize default documentation
        self._setup_default_documentation()
        
        logger.info("API Documentation service initialized")
    
    def _setup_default_documentation(self) -> None:
        """Setup default API documentation."""
        # Setup default tags
        self.add_tag("workflows", "Workflow management and orchestration")
        self.add_tag("modules", "External module management and integration")
        self.add_tag("data", "Data processing and management")
        self.add_tag("health", "System health and monitoring")
        self.add_tag("authentication", "Authentication and authorization")
        
        # Setup default schemas
        self._setup_default_schemas()
        
        # Setup default endpoints
        self._setup_default_endpoints()
        
        logger.info("Default API documentation configured")
    
    def _setup_default_schemas(self) -> None:
        """Setup default data schemas."""
        # Workflow Definition Schema
        workflow_def_schema = SchemaInfo(
            name="WorkflowDefinition",
            type="object",
            description="A workflow definition template",
            properties={
                "workflow_id": {"type": "string", "format": "uuid", "description": "Unique workflow identifier"},
                "workflow_name": {"type": "string", "description": "Human-readable workflow name"},
                "workflow_type": {"type": "string", "description": "Type of workflow"},
                "version": {"type": "string", "description": "Workflow version"},
                "tasks": {"type": "array", "items": {"$ref": "#/components/schemas/WorkflowTask"}},
                "dependencies": {"type": "array", "items": {"$ref": "#/components/schemas/TaskDependency"}},
                "is_active": {"type": "boolean", "description": "Whether the workflow is active"}
            },
            required=["workflow_name", "workflow_type", "version"],
            example={
                "workflow_id": "123e4567-e89b-12d3-a456-426614174000",
                "workflow_name": "Data Processing Pipeline",
                "workflow_type": "data_pipeline",
                "version": "1.0.0",
                "is_active": True
            }
        )
        
        # Workflow Task Schema
        workflow_task_schema = SchemaInfo(
            name="WorkflowTask",
            type="object",
            description="A single task within a workflow",
            properties={
                "task_id": {"type": "string", "format": "uuid", "description": "Unique task identifier"},
                "task_name": {"type": "string", "description": "Human-readable task name"},
                "task_type": {"type": "string", "description": "Type of task"},
                "target_module": {"type": "string", "description": "Target module for execution"},
                "parameters": {"type": "object", "description": "Task parameters"}
            },
            required=["task_name", "task_type"],
            example={
                "task_id": "123e4567-e89b-12d3-a456-426614174001",
                "task_name": "Data Validation",
                "task_type": "validation",
                "target_module": "data_processor"
            }
        )
        
        # Task Dependency Schema
        task_dependency_schema = SchemaInfo(
            name="TaskDependency",
            type="object",
            description="Dependency between workflow tasks",
            properties={
                "source_task_id": {"type": "string", "format": "uuid", "description": "Source task identifier"},
                "target_task_id": {"type": "string", "format": "uuid", "description": "Target task identifier"},
                "dependency_type": {"type": "string", "enum": ["required", "optional"], "description": "Type of dependency"}
            },
            required=["source_task_id", "target_task_id"],
            example={
                "source_task_id": "123e4567-e89b-12d3-a456-426614174001",
                "target_task_id": "123e4567-e89b-12d3-a456-426614174002",
                "dependency_type": "required"
            }
        )
        
        # Error Response Schema
        error_response_schema = SchemaInfo(
            name="ErrorResponse",
            type="object",
            description="Standard error response format",
            properties={
                "success": {"type": "boolean", "description": "Always false for errors"},
                "error": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Error message"},
                        "code": {"type": "integer", "description": "HTTP status code"},
                        "timestamp": {"type": "string", "format": "date-time", "description": "Error timestamp"}
                    }
                }
            },
            required=["success", "error"],
            example={
                "success": False,
                "error": {
                    "message": "Resource not found",
                    "code": 404,
                    "timestamp": "2025-08-21T10:00:00Z"
                }
            }
        )
        
        # Add schemas
        self.add_schema(workflow_def_schema)
        self.add_schema(workflow_task_schema)
        self.add_schema(task_dependency_schema)
        self.add_schema(error_response_schema)
    
    def _setup_default_endpoints(self) -> None:
        """Setup default API endpoints documentation."""
        # Health Check Endpoint
        health_endpoint = EndpointInfo(
            path="/health",
            method="GET",
            summary="Health Check",
            description="Check the health status of the API service",
            tags=["health"],
            responses={
                "200": {
                    "description": "Service is healthy",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "healthy"},
                                    "service": {"type": "string", "example": "AAS Data Modeling Engine API"},
                                    "timestamp": {"type": "string", "format": "date-time"}
                                }
                            }
                        }
                    }
                }
            }
        )
        
        # Detailed Health Check Endpoint
        detailed_health_endpoint = EndpointInfo(
            path="/health/detailed",
            method="GET",
            summary="Detailed Health Check",
            description="Get detailed health information about all system components",
            tags=["health"],
            responses={
                "200": {
                    "description": "Detailed health information",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "components": {"type": "object"},
                                    "metrics": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        )
        
        # List Workflows Endpoint
        list_workflows_endpoint = EndpointInfo(
            path="/api/v1/workflows",
            method="GET",
            summary="List Workflows",
            description="Retrieve a list of all available workflow definitions",
            tags=["workflows"],
            parameters=[
                {
                    "name": "workflow_type",
                    "in": "query",
                    "description": "Filter workflows by type",
                    "required": False,
                    "schema": {"type": "string"}
                },
                {
                    "name": "is_active",
                    "in": "query",
                    "description": "Filter by active status",
                    "required": False,
                    "schema": {"type": "boolean"}
                }
            ],
            responses={
                "200": {
                    "description": "List of workflows",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/WorkflowDefinition"}
                            }
                        }
                    }
                },
                "401": {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            }
        )
        
        # Create Workflow Endpoint
        create_workflow_endpoint = EndpointInfo(
            path="/api/v1/workflows",
            method="POST",
            summary="Create Workflow",
            description="Create a new workflow definition",
            tags=["workflows"],
            request_body={
                "description": "Workflow definition data",
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/WorkflowDefinition"}
                    }
                }
            },
            responses={
                "201": {
                    "description": "Workflow created successfully",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/WorkflowDefinition"}
                        }
                    }
                },
                "400": {
                    "description": "Bad request",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                },
                "401": {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    }
                }
            }
        )
        
        # Add endpoints
        self.add_endpoint(health_endpoint)
        self.add_endpoint(detailed_health_endpoint)
        self.add_endpoint(list_workflows_endpoint)
        self.add_endpoint(create_workflow_endpoint)
    
    def add_tag(self, name: str, description: str, **kwargs) -> None:
        """Add a new API tag."""
        self.tags[name] = {
            "name": name,
            "description": description,
            **kwargs
        }
        logger.info(f"API tag added: {name}")
    
    def remove_tag(self, name: str) -> bool:
        """Remove an API tag."""
        if name in self.tags:
            del self.tags[name]
            logger.info(f"API tag removed: {name}")
            return True
        return False
    
    def add_schema(self, schema: SchemaInfo) -> None:
        """Add a new data schema."""
        self.schemas[schema.name] = schema
        logger.info(f"Schema added: {schema.name}")
    
    def remove_schema(self, name: str) -> bool:
        """Remove a data schema."""
        if name in self.schemas:
            del self.schemas[name]
            logger.info(f"Schema removed: {name}")
            return True
        return False
    
    def add_endpoint(self, endpoint: EndpointInfo) -> None:
        """Add a new API endpoint."""
        key = f"{endpoint.method}:{endpoint.path}"
        self.endpoints[key] = endpoint
        logger.info(f"Endpoint added: {endpoint.method} {endpoint.path}")
    
    def remove_endpoint(self, method: str, path: str) -> bool:
        """Remove an API endpoint."""
        key = f"{method}:{path}"
        if key in self.endpoints:
            del self.endpoints[key]
            logger.info(f"Endpoint removed: {method} {path}")
            return True
        return False
    
    def get_endpoint(self, method: str, path: str) -> Optional[EndpointInfo]:
        """Get an API endpoint by method and path."""
        key = f"{method}:{path}"
        return self.endpoints.get(key)
    
    def get_endpoints_by_tag(self, tag: str) -> List[EndpointInfo]:
        """Get all endpoints for a specific tag."""
        return [
            endpoint for endpoint in self.endpoints.values()
            if tag in endpoint.tags
        ]
    
    def generate_openapi_spec(self, version: str = "3.0.3") -> Dict[str, Any]:
        """Generate OpenAPI specification."""
        openapi_spec = {
            "openapi": version,
            "info": self.info,
            "servers": self.servers,
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    },
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "tags": list(self.tags.values()),
            "security": [
                {"ApiKeyAuth": []},
                {"BearerAuth": []}
            ]
        }
        
        # Add paths
        for endpoint in self.endpoints.values():
            if endpoint.path not in openapi_spec["paths"]:
                openapi_spec["paths"][endpoint.path] = {}
            
            openapi_spec["paths"][endpoint.path][endpoint.method.lower()] = endpoint.to_openapi()
        
        # Add schemas
        for schema_name, schema in self.schemas.items():
            openapi_spec["components"]["schemas"][schema_name] = schema.to_openapi()
        
        return openapi_spec
    
    def generate_swagger_ui_html(self, openapi_url: str = "/openapi.json") -> str:
        """Generate Swagger UI HTML page."""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="AAS Data Modeling Engine API Documentation" />
    <title>AAS Data Modeling Engine API</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js" crossorigin></script>
    <script>
        window.onload = () => {{
            window.ui = SwaggerUIBundle({{
                url: '{openapi_url}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                layout: 'StandaloneLayout',
                docExpansion: 'list',
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                displayRequestDuration: true,
                filter: true,
                showExtensions: true,
                showCommonExtensions: true,
                tryItOutEnabled: true
            }});
        }};
    </script>
</body>
</html>
        """
        return html_template
    
    def generate_redoc_html(self, openapi_url: str = "/openapi.json") -> str:
        """Generate ReDoc HTML page."""
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AAS Data Modeling Engine API</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <redoc spec-url="{openapi_url}"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
</body>
</html>
        """
        return html_template
    
    def generate_markdown(self) -> str:
        """Generate Markdown documentation."""
        md_lines = [
            f"# {self.info['title']}",
            f"**Version:** {self.info['version']}",
            "",
            self.info['description'],
            "",
            "## Table of Contents",
            ""
        ]
        
        # Add tag-based sections
        for tag_name, tag_info in self.tags.items():
            md_lines.append(f"- [{tag_info['description']}](#{tag_name})")
        
        md_lines.append("")
        
        # Generate endpoint documentation by tag
        for tag_name, tag_info in self.tags.items():
            md_lines.append(f"## {tag_info['description']}")
            md_lines.append("")
            
            tag_endpoints = self.get_endpoints_by_tag(tag_name)
            for endpoint in tag_endpoints:
                md_lines.append(f"### {endpoint.method} {endpoint.path}")
                md_lines.append("")
                md_lines.append(f"**Summary:** {endpoint.summary}")
                md_lines.append("")
                
                if endpoint.description:
                    md_lines.append(f"**Description:** {endpoint.description}")
                    md_lines.append("")
                
                if endpoint.parameters:
                    md_lines.append("**Parameters:**")
                    md_lines.append("")
                    for param in endpoint.parameters:
                        md_lines.append(f"- `{param['name']}` ({param['in']}) - {param['description']}")
                    md_lines.append("")
                
                if endpoint.request_body:
                    md_lines.append("**Request Body:** Required")
                    md_lines.append("")
                
                if endpoint.responses:
                    md_lines.append("**Responses:**")
                    md_lines.append("")
                    for status_code, response in endpoint.responses.items():
                        md_lines.append(f"- `{status_code}` - {response['description']}")
                    md_lines.append("")
                
                md_lines.append("---")
                md_lines.append("")
        
        return "\n".join(md_lines)
    
    def export_documentation(self, format: DocumentationFormat, **kwargs) -> Union[str, Dict[str, Any]]:
        """Export documentation in the specified format."""
        if format == DocumentationFormat.OPENAPI_JSON:
            return json.dumps(self.generate_openapi_spec(), indent=2)
        elif format == DocumentationFormat.OPENAPI_YAML:
            # This would require PyYAML - for now return JSON
            return json.dumps(self.generate_openapi_spec(), indent=2)
        elif format == DocumentationFormat.SWAGGER_UI:
            openapi_url = kwargs.get("openapi_url", "/openapi.json")
            return self.generate_swagger_ui_html(openapi_url)
        elif format == DocumentationFormat.REDOC:
            openapi_url = kwargs.get("openapi_url", "/openapi.json")
            return self.generate_redoc_html(openapi_url)
        elif format == DocumentationFormat.MARKDOWN:
            return self.generate_markdown()
        elif format == DocumentationFormat.HTML:
            # Generate a simple HTML documentation page
            return self._generate_simple_html()
        else:
            raise ValueError(f"Unsupported documentation format: {format}")
    
    def _generate_simple_html(self) -> str:
        """Generate a simple HTML documentation page."""
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{self.info['title']} - Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .endpoint {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .method {{ font-weight: bold; color: #fff; padding: 5px 10px; border-radius: 3px; }}
        .get {{ background-color: #61affe; }}
        .post {{ background-color: #49cc90; }}
        .put {{ background-color: #fca130; }}
        .delete {{ background-color: #f93e3e; }}
        .path {{ font-family: monospace; font-size: 16px; }}
        .description {{ color: #666; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>{self.info['title']}</h1>
    <p><strong>Version:</strong> {self.info['version']}</p>
    <p>{self.info['description']}</p>
    
    <h2>API Endpoints</h2>
"""
        
        # Group endpoints by tag
        for tag_name, tag_info in self.tags.items():
            html_template += f'    <h3>{tag_info["description"]}</h3>\n'
            
            tag_endpoints = self.get_endpoints_by_tag(tag_name)
            for endpoint in tag_endpoints:
                method_class = endpoint.method.lower()
                html_template += f"""
    <div class="endpoint">
        <span class="method {method_class}">{endpoint.method}</span>
        <span class="path">{endpoint.path}</span>
        <h4>{endpoint.summary}</h4>
        <p class="description">{endpoint.description}</p>
    </div>
"""
        
        html_template += """
</body>
</html>
"""
        return html_template
    
    def get_documentation_stats(self) -> Dict[str, Any]:
        """Get documentation statistics."""
        total_endpoints = len(self.endpoints)
        total_schemas = len(self.schemas)
        total_tags = len(self.tags)
        
        # Count endpoints by method
        methods_count = {}
        for endpoint in self.endpoints.values():
            method = endpoint.method
            methods_count[method] = methods_count.get(method, 0) + 1
        
        # Count endpoints by tag
        tags_count = {}
        for endpoint in self.endpoints.values():
            for tag in endpoint.tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1
        
        return {
            "total_endpoints": total_endpoints,
            "total_schemas": total_schemas,
            "total_tags": total_tags,
            "endpoints_by_method": methods_count,
            "endpoints_by_tag": tags_count,
            "api_info": self.info
        }
    
    def update_api_info(self, **kwargs) -> None:
        """Update API information."""
        for key, value in kwargs.items():
            if key in self.info:
                self.info[key] = value
                logger.info(f"API info updated: {key} = {value}")
    
    def add_server(self, url: str, description: str) -> None:
        """Add a new server to the API documentation."""
        self.servers.append({
            "url": url,
            "description": description
        })
        logger.info(f"Server added: {url}")
    
    def remove_server(self, url: str) -> bool:
        """Remove a server from the API documentation."""
        for i, server in enumerate(self.servers):
            if server["url"] == url:
                del self.servers[i]
                logger.info(f"Server removed: {url}")
                return True
        return False
