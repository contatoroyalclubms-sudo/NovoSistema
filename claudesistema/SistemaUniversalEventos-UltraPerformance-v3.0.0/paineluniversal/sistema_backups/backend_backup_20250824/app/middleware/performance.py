"""
API RESPONSE PERFORMANCE OPTIMIZATION
Sistema Universal de Gestão de Eventos - ULTRA PERFORMANCE

High-performance middleware for:
- Response compression and optimization
- Caching headers and strategies
- Request/Response streaming
- Performance monitoring
- Rate limiting and throttling
"""

import asyncio
import gzip
import json
import time
import logging
from typing import Dict, Any, Optional, Callable
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import StreamingResponse
from starlette.types import ASGIApp
from prometheus_client import Counter, Histogram, Gauge
import hashlib
from datetime import datetime, timedelta

from app.services.redis_cache_performance import ultra_cache

logger = logging.getLogger(__name__)

# Performance Metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
http_response_size = Histogram('http_response_size_bytes', 'HTTP response size')
active_requests = Gauge('http_active_requests', 'Currently active HTTP requests')
cache_usage = Counter('api_cache_usage', 'API cache usage', ['result'])

class UltraPerformanceMiddleware(BaseHTTPMiddleware):
    """
    Ultra-performance middleware with:
    - Intelligent response compression
    - Automatic caching strategies
    - Performance monitoring
    - Request optimization
    """
    
    def __init__(
        self,
        app: ASGIApp,
        compression_threshold: int = 1000,  # Compress responses > 1KB
        cache_ttl: int = 300,  # 5 minutes default cache TTL
        enable_compression: bool = True,
        enable_caching: bool = True,
        enable_etags: bool = True,
    ):
        super().__init__(app)
        self.compression_threshold = compression_threshold
        self.cache_ttl = cache_ttl
        self.enable_compression = enable_compression
        self.enable_caching = enable_caching
        self.enable_etags = enable_etags
        
        # Cache-eligible endpoints (GET requests to these patterns)
        self.cacheable_endpoints = {
            '/api/v1/eventos',
            '/api/v1/eventos/',
            '/api/v1/usuarios',
            '/api/v1/dashboard',
            '/api/v1/analytics',
            '/api/v1/ranking',
            '/health',
            '/metrics'
        }
        
        # Headers for optimal performance
        self.performance_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with performance optimizations"""
        start_time = time.time()
        request_id = self._generate_request_id(request)
        
        # Increment active requests counter
        active_requests.inc()
        
        try:
            # Check if request is cacheable
            if self._is_cacheable(request):
                cached_response = await self._get_cached_response(request)
                if cached_response:
                    cache_usage.labels(result='hit').inc()
                    return await self._create_cached_response(cached_response, request_id)
                else:
                    cache_usage.labels(result='miss').inc()
            
            # Process request
            response = await call_next(request)
            
            # Apply performance optimizations
            response = await self._optimize_response(request, response, request_id)
            
            # Cache response if applicable
            if self._is_cacheable(request) and response.status_code == 200:
                await self._cache_response(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in performance middleware: {e}")
            # Return error response but still apply basic headers
            response = Response(
                content=json.dumps({"error": "Internal server error"}),
                status_code=500,
                media_type="application/json"
            )
            return await self._add_performance_headers(response, request_id)
            
        finally:
            # Decrement active requests and record metrics
            active_requests.dec()
            
            duration = time.time() - start_time
            http_request_duration.observe(duration)
            
            # Record request metrics
            endpoint = self._get_endpoint_pattern(request.url.path)
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=getattr(response, 'status_code', 500)
            ).inc()
    
    def _generate_request_id(self, request: Request) -> str:
        """Generate unique request ID"""
        return hashlib.md5(
            f"{request.method}:{request.url}:{time.time()}".encode()
        ).hexdigest()[:12]
    
    def _is_cacheable(self, request: Request) -> bool:
        """Check if request is cacheable"""
        if not self.enable_caching or request.method != 'GET':
            return False
        
        # Check if endpoint is in cacheable list
        path = request.url.path.rstrip('/')
        
        # Exact match or pattern match
        for pattern in self.cacheable_endpoints:
            if path == pattern.rstrip('/') or path.startswith(pattern.rstrip('/') + '/'):
                return True
        
        return False
    
    async def _get_cached_response(self, request: Request) -> Optional[Dict]:
        """Get cached response if available"""
        try:
            cache_key = self._generate_cache_key(request)
            return await ultra_cache.get(cache_key)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def _cache_response(self, request: Request, response: Response):
        """Cache response for future requests"""
        try:
            # Only cache successful JSON responses
            if (response.status_code == 200 and 
                response.headers.get('content-type', '').startswith('application/json')):
                
                cache_key = self._generate_cache_key(request)
                
                # Extract response body
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                # Cache the response data
                cache_data = {
                    'body': response_body.decode('utf-8'),
                    'headers': dict(response.headers),
                    'status_code': response.status_code,
                    'cached_at': datetime.utcnow().isoformat()
                }
                
                await ultra_cache.set(cache_key, cache_data, self.cache_ttl)
                
                # Recreate response with the body
                response.body_iterator = self._create_body_iterator(response_body)
                
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    def _create_body_iterator(self, body: bytes):
        """Create body iterator from bytes"""
        async def body_iterator():
            yield body
        return body_iterator()
    
    async def _create_cached_response(self, cached_data: Dict, request_id: str) -> Response:
        """Create response from cached data"""
        response = Response(
            content=cached_data['body'],
            status_code=cached_data['status_code'],
            headers=cached_data['headers']
        )
        
        # Add cache headers
        response.headers['X-Cache'] = 'HIT'
        response.headers['X-Cache-Date'] = cached_data['cached_at']
        
        return await self._add_performance_headers(response, request_id)
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        # Include method, path, and query parameters
        key_parts = [
            request.method,
            request.url.path,
            str(sorted(request.query_params.items()))
        ]
        key_string = ':'.join(key_parts)
        return f"api_cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def _optimize_response(self, request: Request, response: Response, request_id: str) -> Response:
        """Apply all response optimizations"""
        # Add performance headers
        response = await self._add_performance_headers(response, request_id)
        
        # Apply compression if enabled and applicable
        if self.enable_compression:
            response = await self._compress_response(request, response)
        
        # Add ETag if enabled
        if self.enable_etags:
            response = await self._add_etag(response)
        
        # Add caching headers
        response = self._add_caching_headers(request, response)
        
        return response
    
    async def _add_performance_headers(self, response: Response, request_id: str) -> Response:
        """Add performance and security headers"""
        # Performance headers
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Response-Time'] = str(int(time.time() * 1000))
        response.headers['X-Powered-By'] = 'FastAPI Ultra Performance'
        
        # Security headers
        for header, value in self.performance_headers.items():
            response.headers[header] = value
        
        return response
    
    async def _compress_response(self, request: Request, response: Response) -> Response:
        """Compress response if beneficial"""
        try:
            # Check if client accepts compression
            accept_encoding = request.headers.get('accept-encoding', '')
            if 'gzip' not in accept_encoding.lower():
                return response
            
            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Only compress if body is larger than threshold
            if len(body) < self.compression_threshold:
                # Recreate response without compression
                response.body_iterator = self._create_body_iterator(body)
                return response
            
            # Compress response
            compressed_body = gzip.compress(body, compresslevel=6)
            
            # Update headers
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = str(len(compressed_body))
            response.headers['Vary'] = 'Accept-Encoding'
            
            # Record compression metrics
            http_response_size.observe(len(compressed_body))
            
            # Create new response with compressed body
            response.body_iterator = self._create_body_iterator(compressed_body)
            
            logger.debug(f"Compressed response: {len(body)} -> {len(compressed_body)} bytes")
            
        except Exception as e:
            logger.warning(f"Compression error: {e}")
            # Fallback to uncompressed response
            response.body_iterator = self._create_body_iterator(body)
        
        return response
    
    async def _add_etag(self, response: Response) -> Response:
        """Add ETag header for caching"""
        try:
            # Get response body for ETag generation
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Generate ETag from content hash
            etag = hashlib.md5(body).hexdigest()
            response.headers['ETag'] = f'"{etag}"'
            
            # Recreate response body iterator
            response.body_iterator = self._create_body_iterator(body)
            
        except Exception as e:
            logger.warning(f"ETag generation error: {e}")
        
        return response
    
    def _add_caching_headers(self, request: Request, response: Response) -> Response:
        """Add appropriate caching headers"""
        if request.method == 'GET' and response.status_code == 200:
            if self._is_cacheable(request):
                # Cache for configured TTL
                response.headers['Cache-Control'] = f'public, max-age={self.cache_ttl}'
                response.headers['X-Cache'] = 'MISS'
            else:
                # Don't cache dynamic content
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        else:
            # Don't cache non-GET requests or error responses
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        return response
    
    def _get_endpoint_pattern(self, path: str) -> str:
        """Get endpoint pattern for metrics"""
        # Remove IDs and replace with placeholders for better grouping
        import re
        
        # Replace UUIDs
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        return path

class ResponseCompressionMiddleware(BaseHTTPMiddleware):
    """Lightweight compression-only middleware"""
    
    def __init__(self, app: ASGIApp, minimum_size: int = 1000):
        super().__init__(app)
        self.minimum_size = minimum_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Check if compression is supported and beneficial
        if (self._should_compress(request, response) and 
            self._supports_gzip(request)):
            return await self._compress_response(response)
        
        return response
    
    def _should_compress(self, request: Request, response: Response) -> bool:
        """Check if response should be compressed"""
        content_type = response.headers.get('content-type', '')
        
        # Only compress text-based content
        compressible_types = [
            'application/json',
            'application/javascript',
            'text/html',
            'text/css',
            'text/plain',
            'text/xml',
            'application/xml'
        ]
        
        return any(content_type.startswith(ct) for ct in compressible_types)
    
    def _supports_gzip(self, request: Request) -> bool:
        """Check if client supports gzip compression"""
        accept_encoding = request.headers.get('accept-encoding', '')
        return 'gzip' in accept_encoding.lower()
    
    async def _compress_response(self, response: Response) -> Response:
        """Compress response with gzip"""
        try:
            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Only compress if above minimum size
            if len(body) >= self.minimum_size:
                compressed_body = gzip.compress(body, compresslevel=6)
                
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = str(len(compressed_body))
                response.headers['Vary'] = 'Accept-Encoding'
                
                # Create new response iterator
                async def compressed_iterator():
                    yield compressed_body
                
                response.body_iterator = compressed_iterator()
            else:
                # Recreate original response
                async def original_iterator():
                    yield body
                
                response.body_iterator = original_iterator()
            
        except Exception as e:
            logger.error(f"Compression error: {e}")
        
        return response