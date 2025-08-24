"""
Advanced API Documentation Generator
Auto-generates comprehensive OpenAPI/Swagger documentation with examples
"""

import json
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from pydantic import BaseModel
import os

class APIDocumentationGenerator:
    """Advanced API documentation generator with enhanced features"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.examples = {}
        self.tags_metadata = []
        self.custom_responses = {}
        
    def add_tag_metadata(self, name: str, description: str, external_docs: Optional[Dict] = None):
        """Add metadata for API tags"""
        tag_data = {
            "name": name,
            "description": description
        }
        if external_docs:
            tag_data["externalDocs"] = external_docs
            
        self.tags_metadata.append(tag_data)
    
    def add_example(self, path: str, method: str, example_name: str, example_data: Dict):
        """Add examples for API endpoints"""
        key = f"{method.upper()}:{path}"
        if key not in self.examples:
            self.examples[key] = {}
        self.examples[key][example_name] = example_data
    
    def add_custom_response(self, status_code: int, description: str, content_type: str = "application/json"):
        """Add custom response definitions"""
        self.custom_responses[status_code] = {
            "description": description,
            "content": {
                content_type: {
                    "schema": {}
                }
            }
        }
    
    def generate_enhanced_openapi(self) -> Dict[str, Any]:
        """Generate enhanced OpenAPI specification"""
        
        # Initialize tag metadata
        self._init_tag_metadata()
        
        # Generate base OpenAPI spec
        openapi_spec = get_openapi(
            title=self.app.title,
            version=self.app.version,
            description=self.app.description,
            routes=self.app.routes,
            tags=self.tags_metadata
        )
        
        # Enhance with additional information
        openapi_spec["info"].update({
            "termsOfService": "https://your-domain.com/terms",
            "contact": {
                "name": "Sistema Universal API Support",
                "url": "https://your-domain.com/support",
                "email": "support@your-domain.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            },
            "x-logo": {
                "url": "https://your-domain.com/logo.png",
                "altText": "Sistema Universal Logo"
            }
        })
        
        # Add servers
        openapi_spec["servers"] = [
            {
                "url": "http://localhost:8000",
                "description": "Development Server"
            },
            {
                "url": "https://api-staging.your-domain.com",
                "description": "Staging Server"
            },
            {
                "url": "https://api.your-domain.com",
                "description": "Production Server"
            }
        ]
        
        # Add security schemes
        openapi_spec["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token authentication"
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key authentication"
            }
        }
        
        # Add global security
        openapi_spec["security"] = [
            {"BearerAuth": []},
            {"ApiKeyAuth": []}
        ]
        
        # Add examples to paths
        self._add_examples_to_paths(openapi_spec)
        
        # Add custom responses
        self._add_custom_responses(openapi_spec)
        
        # Add performance information
        self._add_performance_info(openapi_spec)
        
        return openapi_spec
    
    def _init_tag_metadata(self):
        """Initialize comprehensive tag metadata"""
        tags_data = [
            {
                "name": "Authentication",
                "description": "User authentication and authorization endpoints",
                "externalDocs": {
                    "description": "Auth Documentation",
                    "url": "https://docs.your-domain.com/auth"
                }
            },
            {
                "name": "Events",
                "description": "Event management operations",
                "externalDocs": {
                    "description": "Events Guide",
                    "url": "https://docs.your-domain.com/events"
                }
            },
            {
                "name": "Check-in",
                "description": "Event check-in system operations",
                "externalDocs": {
                    "description": "Check-in Guide",
                    "url": "https://docs.your-domain.com/checkin"
                }
            },
            {
                "name": "Point of Sale",
                "description": "POS and sales management operations"
            },
            {
                "name": "Analytics",
                "description": "Analytics and reporting endpoints"
            },
            {
                "name": "Users",
                "description": "User management operations"
            },
            {
                "name": "Lists",
                "description": "Guest list management operations"
            },
            {
                "name": "Financial",
                "description": "Financial and payment operations"
            },
            {
                "name": "Gamification",
                "description": "Gamification and ranking system"
            },
            {
                "name": "WebSocket",
                "description": "Real-time WebSocket connections"
            },
            {
                "name": "Monitoring",
                "description": "System monitoring and health endpoints"
            }
        ]
        
        self.tags_metadata.extend(tags_data)
    
    def _add_examples_to_paths(self, openapi_spec: Dict):
        """Add examples to API paths"""
        if "paths" not in openapi_spec:
            return
            
        # Add common request/response examples
        common_examples = {
            "GET:/api/v1/eventos": {
                "success_response": {
                    "summary": "Successful response",
                    "value": {
                        "success": True,
                        "data": [
                            {
                                "id": 1,
                                "name": "Tech Conference 2024",
                                "description": "Annual technology conference",
                                "start_date": "2024-06-01T09:00:00Z",
                                "end_date": "2024-06-03T18:00:00Z",
                                "location": "Convention Center",
                                "capacity": 1000,
                                "status": "active"
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "page_size": 10
                    }
                }
            },
            "POST:/api/v1/auth/login": {
                "login_request": {
                    "summary": "Login request",
                    "value": {
                        "email": "user@example.com",
                        "password": "securepassword123"
                    }
                },
                "login_success": {
                    "summary": "Login successful",
                    "value": {
                        "success": True,
                        "data": {
                            "access_token": "eyJhbGciOiJIUzI1NiIs...",
                            "token_type": "bearer",
                            "expires_in": 3600,
                            "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "name": "John Doe",
                                "role": "organizer"
                            }
                        }
                    }
                }
            }
        }
        
        # Merge with custom examples
        all_examples = {**common_examples, **self.examples}
        
        for path, methods in openapi_spec["paths"].items():
            for method, details in methods.items():
                key = f"{method.upper()}:{path}"
                if key in all_examples:
                    # Add request examples
                    if "requestBody" in details:
                        if "content" in details["requestBody"]:
                            for content_type, content in details["requestBody"]["content"].items():
                                content["examples"] = all_examples[key]
                    
                    # Add response examples
                    if "responses" in details:
                        for status_code, response in details["responses"].items():
                            if "content" in response:
                                for content_type, content in response["content"].items():
                                    content["examples"] = all_examples[key]
    
    def _add_custom_responses(self, openapi_spec: Dict):
        """Add custom response definitions"""
        if not openapi_spec.get("components"):
            openapi_spec["components"] = {}
        
        if not openapi_spec["components"].get("responses"):
            openapi_spec["components"]["responses"] = {}
        
        # Add common response schemas
        common_responses = {
            "ValidationError": {
                "description": "Validation error",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": False},
                                "error": {"type": "string", "example": "Validation failed"},
                                "details": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "field": {"type": "string", "example": "email"},
                                            "message": {"type": "string", "example": "Invalid email format"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "Unauthorized": {
                "description": "Authentication required",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": False},
                                "error": {"type": "string", "example": "Authentication required"},
                                "code": {"type": "string", "example": "UNAUTHORIZED"}
                            }
                        }
                    }
                }
            },
            "RateLimited": {
                "description": "Rate limit exceeded",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": False},
                                "error": {"type": "string", "example": "Rate limit exceeded"},
                                "retry_after": {"type": "integer", "example": 60}
                            }
                        }
                    }
                }
            }
        }
        
        openapi_spec["components"]["responses"].update(common_responses)
    
    def _add_performance_info(self, openapi_spec: Dict):
        """Add performance information to the API spec"""
        if "info" not in openapi_spec:
            openapi_spec["info"] = {}
        
        # Add performance metadata
        openapi_spec["info"]["x-performance"] = {
            "target_response_time": "< 200ms",
            "rate_limits": {
                "default": "100 requests/minute",
                "authenticated": "1000 requests/minute",
                "premium": "10000 requests/minute"
            },
            "caching": {
                "enabled": True,
                "ttl": "300 seconds",
                "redis_backend": True
            },
            "monitoring": {
                "health_endpoint": "/health",
                "metrics_endpoint": "/metrics",
                "uptime_target": "99.9%"
            }
        }
        
        # Add versioning information
        openapi_spec["info"]["x-versioning"] = {
            "strategy": "URL versioning",
            "current_version": "v1",
            "supported_versions": ["v1"],
            "deprecation_policy": "6 months notice"
        }

class DocumentationServer:
    """Custom documentation server with enhanced UI"""
    
    def __init__(self, app: FastAPI, doc_generator: APIDocumentationGenerator):
        self.app = app
        self.doc_generator = doc_generator
        self.setup_custom_docs()
    
    def setup_custom_docs(self):
        """Setup custom documentation endpoints"""
        
        @self.app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url="/openapi.json",
                title=f"{self.app.title} - Interactive API Documentation",
                swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
                swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
                swagger_ui_parameters={
                    "defaultModelsExpandDepth": -1,
                    "displayRequestDuration": True,
                    "filter": True,
                    "showExtensions": True,
                    "showCommonExtensions": True,
                    "tryItOutEnabled": True
                }
            )
        
        @self.app.get("/redoc", include_in_schema=False)
        async def custom_redoc_html():
            return get_redoc_html(
                openapi_url="/openapi.json",
                title=f"{self.app.title} - API Documentation",
                redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
                with_google_fonts=True
            )
        
        @self.app.get("/api-docs/postman", include_in_schema=False)
        async def download_postman_collection():
            """Download Postman collection"""
            openapi_spec = self.doc_generator.generate_enhanced_openapi()
            
            # Convert OpenAPI to Postman collection format
            postman_collection = self._convert_to_postman(openapi_spec)
            
            return {
                "collection": postman_collection,
                "download_url": "/api-docs/postman/download"
            }
        
        @self.app.get("/api-docs/changelog", include_in_schema=False)
        async def api_changelog():
            """API changelog and versioning information"""
            return {
                "changelog": [
                    {
                        "version": "3.0.0",
                        "date": "2024-01-15",
                        "changes": [
                            "Added ultra-performance optimizations",
                            "Implemented advanced caching system",
                            "Added comprehensive monitoring",
                            "Enhanced security middleware"
                        ]
                    },
                    {
                        "version": "2.1.0", 
                        "date": "2023-12-01",
                        "changes": [
                            "Added WebSocket support",
                            "Improved error handling",
                            "Added rate limiting"
                        ]
                    }
                ],
                "breaking_changes": [],
                "deprecations": []
            }
        
        # Override the default openapi endpoint
        @self.app.get("/openapi.json", include_in_schema=False)
        async def get_enhanced_openapi():
            return self.doc_generator.generate_enhanced_openapi()
    
    def _convert_to_postman(self, openapi_spec: Dict) -> Dict:
        """Convert OpenAPI specification to Postman collection format"""
        postman_collection = {
            "info": {
                "name": openapi_spec["info"]["title"],
                "description": openapi_spec["info"]["description"],
                "version": openapi_spec["info"]["version"],
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [],
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{access_token}}",
                        "type": "string"
                    }
                ]
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": "http://localhost:8000",
                    "type": "string"
                },
                {
                    "key": "access_token",
                    "value": "",
                    "type": "string"
                }
            ]
        }
        
        # Convert paths to Postman requests
        for path, methods in openapi_spec.get("paths", {}).items():
            folder = {
                "name": path.split("/")[2] if len(path.split("/")) > 2 else "API",
                "item": []
            }
            
            for method, details in methods.items():
                request = {
                    "name": details.get("summary", f"{method.upper()} {path}"),
                    "request": {
                        "method": method.upper(),
                        "url": {
                            "raw": "{{base_url}}" + path,
                            "host": ["{{base_url}}"],
                            "path": path.strip("/").split("/")
                        }
                    }
                }
                
                # Add request body if present
                if "requestBody" in details:
                    request["request"]["body"] = {
                        "mode": "raw",
                        "raw": "{}",
                        "options": {
                            "raw": {
                                "language": "json"
                            }
                        }
                    }
                
                folder["item"].append(request)
            
            if folder["item"]:
                postman_collection["item"].append(folder)
        
        return postman_collection

def setup_enhanced_documentation(app: FastAPI) -> APIDocumentationGenerator:
    """Setup enhanced API documentation for the FastAPI app"""
    
    # Create documentation generator
    doc_generator = APIDocumentationGenerator(app)
    
    # Add comprehensive examples
    doc_generator.add_example(
        "/api/v1/eventos", "GET",
        "list_events",
        {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "name": "Annual Tech Conference",
                    "description": "The biggest tech event of the year",
                    "start_date": "2024-06-01T09:00:00Z",
                    "end_date": "2024-06-03T18:00:00Z",
                    "location": "Tech Convention Center",
                    "capacity": 2000,
                    "registered_count": 1500,
                    "status": "active",
                    "tags": ["technology", "conference", "networking"]
                }
            ],
            "pagination": {
                "total": 1,
                "page": 1,
                "page_size": 10,
                "total_pages": 1
            }
        }
    )
    
    # Setup custom documentation server
    doc_server = DocumentationServer(app, doc_generator)
    
    return doc_generator

def generate_static_documentation(openapi_spec: Dict, output_dir: str = "docs"):
    """Generate static documentation files"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save OpenAPI spec
    with open(f"{output_dir}/openapi.json", "w") as f:
        json.dump(openapi_spec, f, indent=2)
    
    # Generate markdown documentation
    markdown_doc = _generate_markdown_docs(openapi_spec)
    with open(f"{output_dir}/API.md", "w") as f:
        f.write(markdown_doc)
    
    # Generate HTML documentation
    html_doc = _generate_html_docs(openapi_spec)
    with open(f"{output_dir}/index.html", "w") as f:
        f.write(html_doc)
    
    print(f"📚 Documentation generated in {output_dir}/")

def _generate_markdown_docs(openapi_spec: Dict) -> str:
    """Generate markdown documentation from OpenAPI spec"""
    
    md_content = f"""# {openapi_spec['info']['title']}

{openapi_spec['info']['description']}

**Version:** {openapi_spec['info']['version']}  
**Generated:** {datetime.now().isoformat()}

## Base URLs

"""
    
    for server in openapi_spec.get("servers", []):
        md_content += f"- **{server['description']}:** `{server['url']}`\n"
    
    md_content += "\n## Authentication\n\n"
    md_content += "This API uses Bearer token authentication. Include your JWT token in the Authorization header:\n\n"
    md_content += "```\nAuthorization: Bearer your-jwt-token\n```\n\n"
    
    # Add endpoints documentation
    md_content += "## Endpoints\n\n"
    
    for path, methods in openapi_spec.get("paths", {}).items():
        md_content += f"### {path}\n\n"
        
        for method, details in methods.items():
            md_content += f"#### {method.upper()}\n\n"
            md_content += f"{details.get('description', details.get('summary', 'No description'))}\n\n"
            
            # Add parameters if present
            if "parameters" in details:
                md_content += "**Parameters:**\n\n"
                for param in details["parameters"]:
                    md_content += f"- `{param['name']}` ({param['in']}) - {param.get('description', 'No description')}\n"
                md_content += "\n"
            
            # Add responses
            if "responses" in details:
                md_content += "**Responses:**\n\n"
                for status_code, response in details["responses"].items():
                    md_content += f"- `{status_code}` - {response.get('description', 'No description')}\n"
                md_content += "\n"
    
    return md_content

def _generate_html_docs(openapi_spec: Dict) -> str:
    """Generate simple HTML documentation"""
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{openapi_spec['info']['title']} - API Documentation</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #2563eb; }}
        code {{ background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }}
        pre {{ background: #1f2937; color: #f9fafb; padding: 16px; border-radius: 8px; overflow-x: auto; }}
        .endpoint {{ border: 1px solid #e5e7eb; margin: 20px 0; padding: 16px; border-radius: 8px; }}
        .method {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; color: white; }}
        .get {{ background: #10b981; }}
        .post {{ background: #3b82f6; }}
        .put {{ background: #f59e0b; }}
        .delete {{ background: #ef4444; }}
    </style>
</head>
<body>
    <h1>{openapi_spec['info']['title']}</h1>
    <p>{openapi_spec['info']['description']}</p>
    
    <h2>Base URLs</h2>
    <ul>
"""
    
    for server in openapi_spec.get("servers", []):
        html_content += f"<li><strong>{server['description']}:</strong> <code>{server['url']}</code></li>"
    
    html_content += "</ul><h2>Endpoints</h2>"
    
    for path, methods in openapi_spec.get("paths", {}).items():
        html_content += f'<div class="endpoint">'
        html_content += f'<h3>{path}</h3>'
        
        for method, details in methods.items():
            html_content += f'<span class="method {method.lower()}">{method.upper()}</span> '
            html_content += f'<strong>{details.get("summary", "No summary")}</strong><br>'
            html_content += f'<p>{details.get("description", "No description")}</p>'
        
        html_content += '</div>'
    
    html_content += "</body></html>"
    
    return html_content