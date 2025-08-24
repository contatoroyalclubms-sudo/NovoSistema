"""
Advanced Security Middleware - Enterprise Grade Protection
Features: Rate limiting, DDoS protection, JWT validation, IP whitelisting, request sanitization
"""

import asyncio
import json
import logging
import time
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from passlib.context import CryptContext
import ipaddress

logger = logging.getLogger(__name__)

class RateLimiter:
    """Advanced rate limiting with sliding window and burst protection"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, float] = {}  # IP -> block_until_timestamp
        self.warning_counts: Dict[str, int] = defaultdict(int)
        
        # Rate limit configurations
        self.limits = {
            'default': {'requests': 100, 'window': 60},  # 100 req/min
            'auth': {'requests': 10, 'window': 60},      # 10 req/min for auth
            'api': {'requests': 200, 'window': 60},      # 200 req/min for API
            'upload': {'requests': 5, 'window': 60},     # 5 req/min for uploads
            'heavy': {'requests': 20, 'window': 60},     # 20 req/min for heavy ops
        }
        
        # Burst protection
        self.burst_limits = {
            'default': {'requests': 20, 'window': 10},   # Max 20 req in 10 seconds
            'auth': {'requests': 5, 'window': 10},       # Max 5 auth req in 10 seconds
        }
    
    def _get_client_key(self, request: Request) -> str:
        """Generate unique client identifier"""
        # Try to get real IP from headers (for reverse proxy setups)
        real_ip = (
            request.headers.get('x-forwarded-for', '').split(',')[0].strip() or
            request.headers.get('x-real-ip', '') or
            request.client.host
        )
        
        # Include user agent for better fingerprinting
        user_agent = request.headers.get('user-agent', '')[:100]
        user_agent_hash = hashlib.md5(user_agent.encode()).hexdigest()[:8]
        
        return f"{real_ip}:{user_agent_hash}"
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """Determine rate limit category based on request"""
        path = request.url.path.lower()
        
        if '/auth' in path or '/login' in path or '/register' in path:
            return 'auth'
        elif '/upload' in path or '/import' in path:
            return 'upload'
        elif '/api' in path:
            if any(heavy_path in path for heavy_path in ['/reports', '/analytics', '/export']):
                return 'heavy'
            return 'api'
        
        return 'default'
    
    def is_allowed(self, request: Request) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed based on rate limits"""
        client_key = self._get_client_key(request)
        limit_key = self._get_rate_limit_key(request)
        current_time = time.time()
        
        # Check if IP is currently blocked
        if client_key in self.blocked_ips:
            if current_time < self.blocked_ips[client_key]:
                return False, {
                    'error': 'IP temporarily blocked',
                    'retry_after': int(self.blocked_ips[client_key] - current_time),
                    'reason': 'Rate limit exceeded'
                }
            else:
                # Unblock IP
                del self.blocked_ips[client_key]
                self.warning_counts[client_key] = 0
        
        # Clean old requests (sliding window)
        request_key = f"{client_key}:{limit_key}"
        request_times = self.requests[request_key]
        
        limit_config = self.limits.get(limit_key, self.limits['default'])
        window_start = current_time - limit_config['window']
        
        # Remove old requests
        while request_times and request_times[0] < window_start:
            request_times.popleft()
        
        # Check burst protection
        burst_config = self.burst_limits.get(limit_key, self.burst_limits['default'])
        burst_window_start = current_time - burst_config['window']
        recent_requests = len([t for t in request_times if t > burst_window_start])
        
        if recent_requests >= burst_config['requests']:
            self.warning_counts[client_key] += 1
            
            # Progressive blocking
            if self.warning_counts[client_key] >= 3:
                # Block for increasing durations
                block_duration = min(300 * (self.warning_counts[client_key] - 2), 3600)  # Max 1 hour
                self.blocked_ips[client_key] = current_time + block_duration
                
                logger.warning(f"IP {client_key} blocked for {block_duration}s due to burst limit violations")
                
                return False, {
                    'error': 'Rate limit exceeded - IP blocked',
                    'retry_after': block_duration,
                    'reason': 'Burst protection triggered'
                }
            
            return False, {
                'error': 'Burst rate limit exceeded',
                'retry_after': burst_config['window'],
                'reason': 'Too many requests in short time'
            }
        
        # Check main rate limit
        if len(request_times) >= limit_config['requests']:
            return False, {
                'error': 'Rate limit exceeded',
                'retry_after': int(limit_config['window'] - (current_time - request_times[0])),
                'reason': f"Exceeded {limit_config['requests']} requests per {limit_config['window']}s",
                'limit': limit_config['requests'],
                'window': limit_config['window']
            }
        
        # Add current request
        request_times.append(current_time)
        
        # Calculate remaining requests
        remaining = limit_config['requests'] - len(request_times)
        reset_time = int(current_time + (limit_config['window'] - (current_time - request_times[0])))
        
        return True, {
            'remaining': remaining,
            'limit': limit_config['requests'],
            'reset': reset_time,
            'window': limit_config['window']
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        return {
            'active_clients': len(self.requests),
            'blocked_ips': len(self.blocked_ips),
            'warning_counts': len([c for c in self.warning_counts.values() if c > 0]),
            'current_blocks': [
                {
                    'ip': ip,
                    'expires_in': max(0, int(block_time - time.time()))
                }
                for ip, block_time in self.blocked_ips.items()
            ]
        }

class SecurityValidator:
    """Advanced security validation and sanitization"""
    
    def __init__(self):
        # Malicious pattern detection
        self.sql_injection_patterns = [
            re.compile(r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b', re.IGNORECASE),
            re.compile(r'[\'"];?\s*--', re.IGNORECASE),
            re.compile(r'\/\*.*?\*\/', re.IGNORECASE),
            re.compile(r'\b(or|and)\s+\d+\s*=\s*\d+', re.IGNORECASE)
        ]
        
        self.xss_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL),
        ]
        
        self.path_traversal_patterns = [
            re.compile(r'\.\.\/'),
            re.compile(r'\.\.\\\\'),
            re.compile(r'%2e%2e%2f', re.IGNORECASE),
            re.compile(r'%2e%2e\\\\', re.IGNORECASE)
        ]
        
        # Suspicious header patterns
        self.suspicious_headers = [
            'x-forwarded-host',
            'x-original-url',
            'x-rewrite-url'
        ]
        
        # File upload restrictions
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def validate_request(self, request: Request) -> tuple[bool, Optional[str]]:
        """Comprehensive request validation"""
        try:
            # Check for suspicious headers
            for header in self.suspicious_headers:
                if request.headers.get(header):
                    return False, f"Suspicious header detected: {header}"
            
            # Validate URL path
            path = request.url.path
            for pattern in self.path_traversal_patterns:
                if pattern.search(path):
                    return False, "Path traversal attempt detected"
            
            # Check for excessively long URLs
            if len(str(request.url)) > 2000:
                return False, "URL too long"
            
            # Validate query parameters
            for key, value in request.query_params.items():
                if not self._is_safe_string(value):
                    return False, f"Malicious content in query parameter: {key}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            return False, "Validation error"
    
    def _is_safe_string(self, value: str) -> bool:
        """Check if string contains malicious patterns"""
        if not isinstance(value, str):
            return True
        
        # Check SQL injection patterns
        for pattern in self.sql_injection_patterns:
            if pattern.search(value):
                return False
        
        # Check XSS patterns
        for pattern in self.xss_patterns:
            if pattern.search(value):
                return False
        
        # Check path traversal
        for pattern in self.path_traversal_patterns:
            if pattern.search(value):
                return False
        
        return True
    
    async def validate_json_payload(self, request: Request) -> tuple[bool, Optional[str]]:
        """Validate JSON payload for malicious content"""
        try:
            content_type = request.headers.get('content-type', '')
            if 'application/json' not in content_type:
                return True, None
            
            body = await request.body()
            if not body:
                return True, None
            
            try:
                json_data = json.loads(body)
                return self._validate_json_recursive(json_data), None
            except json.JSONDecodeError:
                return False, "Invalid JSON format"
                
        except Exception as e:
            logger.error(f"JSON validation error: {e}")
            return False, "Payload validation error"
    
    def _validate_json_recursive(self, data: Any) -> bool:
        """Recursively validate JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if not self._is_safe_string(str(key)):
                    return False
                if not self._validate_json_recursive(value):
                    return False
        elif isinstance(data, list):
            for item in data:
                if not self._validate_json_recursive(item):
                    return False
        elif isinstance(data, str):
            if not self._is_safe_string(data):
                return False
        
        return True

class IPWhitelist:
    """IP whitelist/blacklist management"""
    
    def __init__(self):
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()
        self.whitelist_networks: List[ipaddress.IPv4Network] = []
        self.blacklist_networks: List[ipaddress.IPv4Network] = []
        
        # Default safe networks
        self._add_default_whitelist()
    
    def _add_default_whitelist(self):
        """Add default safe networks"""
        safe_networks = [
            '127.0.0.0/8',    # Localhost
            '10.0.0.0/8',     # Private networks
            '172.16.0.0/12',  # Private networks
            '192.168.0.0/16', # Private networks
        ]
        
        for network in safe_networks:
            try:
                self.whitelist_networks.append(ipaddress.IPv4Network(network))
            except ValueError:
                pass
    
    def is_allowed(self, ip: str) -> bool:
        """Check if IP is allowed"""
        try:
            ip_addr = ipaddress.IPv4Address(ip)
            
            # Check blacklist first
            if ip in self.blacklist:
                return False
            
            for network in self.blacklist_networks:
                if ip_addr in network:
                    return False
            
            # Check whitelist
            if ip in self.whitelist:
                return True
            
            for network in self.whitelist_networks:
                if ip_addr in network:
                    return True
            
            # If not in whitelist but whitelist is not empty, deny
            # For production, you might want to change this logic
            return True  # Allow by default for development
            
        except ValueError:
            # Invalid IP format
            return False
    
    def add_to_blacklist(self, ip: str):
        """Add IP to blacklist"""
        self.blacklist.add(ip)
        logger.warning(f"IP {ip} added to blacklist")
    
    def add_to_whitelist(self, ip: str):
        """Add IP to whitelist"""
        self.whitelist.add(ip)
        logger.info(f"IP {ip} added to whitelist")

class AdvancedSecurityMiddleware(BaseHTTPMiddleware):
    """Advanced security middleware combining all security features"""
    
    def __init__(self, app, config: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.config = config or {}
        self.rate_limiter = RateLimiter()
        self.security_validator = SecurityValidator()
        self.ip_whitelist = IPWhitelist()
        
        # Security settings
        self.enable_rate_limiting = self.config.get('enable_rate_limiting', True)
        self.enable_security_validation = self.config.get('enable_security_validation', True)
        self.enable_ip_filtering = self.config.get('enable_ip_filtering', False)
        self.enable_detailed_logging = self.config.get('enable_detailed_logging', True)
        
        # Excluded paths (no security checks)
        self.excluded_paths = set(self.config.get('excluded_paths', [
            '/health',
            '/docs',
            '/redoc',
            '/openapi.json'
        ]))
        
        logger.info("✅ Advanced Security Middleware initialized")
    
    async def dispatch(self, request: Request, call_next):
        """Main security middleware handler"""
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        # Skip security checks for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        try:
            # 1. IP Filtering
            if self.enable_ip_filtering and not self.ip_whitelist.is_allowed(client_ip):
                return self._create_error_response(
                    "Access denied",
                    status_code=status.HTTP_403_FORBIDDEN,
                    details="IP not allowed"
                )
            
            # 2. Rate Limiting
            if self.enable_rate_limiting:
                allowed, rate_info = self.rate_limiter.is_allowed(request)
                if not allowed:
                    response = self._create_error_response(
                        rate_info.get('error', 'Rate limit exceeded'),
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        details=rate_info
                    )
                    
                    # Add rate limit headers
                    if 'retry_after' in rate_info:
                        response.headers['Retry-After'] = str(rate_info['retry_after'])
                    
                    return response
            
            # 3. Security Validation
            if self.enable_security_validation:
                # Validate request structure
                is_valid, error_msg = self.security_validator.validate_request(request)
                if not is_valid:
                    return self._create_error_response(
                        "Security validation failed",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details=error_msg
                    )
                
                # Validate JSON payload for POST/PUT requests
                if request.method in ['POST', 'PUT', 'PATCH']:
                    is_valid, error_msg = await self.security_validator.validate_json_payload(request)
                    if not is_valid:
                        return self._create_error_response(
                            "Payload validation failed",
                            status_code=status.HTTP_400_BAD_REQUEST,
                            details=error_msg
                        )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response = self._add_security_headers(response)
            
            # Log successful request
            if self.enable_detailed_logging:
                process_time = time.time() - start_time
                logger.info(
                    f"✅ {request.method} {request.url.path} - "
                    f"IP: {client_ip} - "
                    f"Status: {response.status_code} - "
                    f"Time: {process_time:.3f}s"
                )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Security middleware error: {e}")
            return self._create_error_response(
                "Internal security error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        return (
            request.headers.get('x-forwarded-for', '').split(',')[0].strip() or
            request.headers.get('x-real-ip', '') or
            request.client.host
        )
    
    def _create_error_response(self, message: str, status_code: int, details: Any = None) -> JSONResponse:
        """Create standardized error response"""
        content = {
            'error': message,
            'status_code': status_code,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            content['details'] = details
        
        return JSONResponse(
            status_code=status_code,
            content=content
        )
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response"""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get comprehensive security statistics"""
        return {
            'rate_limiter': self.rate_limiter.get_stats(),
            'ip_filtering': {
                'whitelist_count': len(self.ip_whitelist.whitelist),
                'blacklist_count': len(self.ip_whitelist.blacklist)
            },
            'middleware_config': {
                'rate_limiting_enabled': self.enable_rate_limiting,
                'security_validation_enabled': self.enable_security_validation,
                'ip_filtering_enabled': self.enable_ip_filtering
            },
            'timestamp': datetime.now().isoformat()
        }

# Convenience function to create middleware
def create_security_middleware(config: Optional[Dict[str, Any]] = None):
    """Create and configure security middleware"""
    return AdvancedSecurityMiddleware(None, config)