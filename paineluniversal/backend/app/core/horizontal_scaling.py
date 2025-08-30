"""
Ultra-Performance Horizontal Scaling Configuration
Sistema Universal de Gestão de Eventos - Enterprise Scale
Target: Auto-scaling, load balancing, multi-region deployment
"""

import asyncio
import logging
import os
import socket
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import aiohttp
import psutil

from app.core.cache_ultra_performance import ultra_cache
from app.core.performance_monitoring import ultra_metrics

logger = logging.getLogger(__name__)

# ================================
# SCALING CONFIGURATION
# ================================

class LoadBalancerType(Enum):
    """Supported load balancer types"""
    NGINX = "nginx"
    HAProxy = "haproxy"
    AWS_ALB = "aws_alb"
    CLOUDFLARE = "cloudflare"
    TRAEFIK = "traefik"

class ScalingStrategy(Enum):
    """Auto-scaling strategies"""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    REQUEST_BASED = "request_based"
    CUSTOM_METRICS = "custom_metrics"
    PREDICTIVE = "predictive"

@dataclass
class InstanceMetrics:
    """Instance performance metrics for scaling decisions"""
    instance_id: str
    cpu_usage_percent: float
    memory_usage_percent: float
    requests_per_second: float
    response_time_p95_ms: float
    error_rate_percent: float
    websocket_connections: int
    timestamp: datetime = field(default_factory=datetime.now)
    healthy: bool = True

@dataclass
class ScalingConfig:
    """Horizontal scaling configuration"""
    # Instance configuration
    min_instances: int = 2
    max_instances: int = 20
    target_instances: int = 4
    
    # Scaling thresholds
    cpu_scale_up_threshold: float = 70.0
    cpu_scale_down_threshold: float = 30.0
    memory_scale_up_threshold: float = 80.0
    memory_scale_down_threshold: float = 40.0
    response_time_scale_up_threshold: float = 100.0  # ms
    error_rate_scale_up_threshold: float = 2.0  # percent
    
    # Scaling behavior
    scale_up_cooldown_minutes: int = 5
    scale_down_cooldown_minutes: int = 15
    scaling_strategy: ScalingStrategy = ScalingStrategy.CPU_BASED
    
    # Health check configuration
    health_check_interval_seconds: int = 30
    unhealthy_threshold_count: int = 3
    healthy_threshold_count: int = 2
    
    # Load balancer configuration
    load_balancer_type: LoadBalancerType = LoadBalancerType.NGINX
    sticky_sessions: bool = False
    session_affinity_cookie: str = "eventos_session"

@dataclass
class ClusterState:
    """Current cluster state"""
    instances: Dict[str, InstanceMetrics] = field(default_factory=dict)
    total_instances: int = 0
    healthy_instances: int = 0
    last_scale_action: Optional[datetime] = None
    scale_action_type: Optional[str] = None
    target_instance_count: int = 0

# ================================
# SERVICE DISCOVERY
# ================================

class ServiceRegistry:
    """Service discovery and registration system"""
    
    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}
        self.instance_id = self._generate_instance_id()
        self.registration_ttl = 60  # seconds
        self.cleanup_interval = 30  # seconds
    
    def _generate_instance_id(self) -> str:
        """Generate unique instance ID"""
        hostname = socket.gethostname()
        timestamp = int(time.time())
        process_id = os.getpid()
        return f"{hostname}-{process_id}-{timestamp}"
    
    async def register_service(
        self,
        service_name: str,
        host: str,
        port: int,
        metadata: Dict[str, Any] = None
    ):
        """Register service instance"""
        service_key = f"{service_name}:{self.instance_id}"
        
        registration = {
            "instance_id": self.instance_id,
            "service_name": service_name,
            "host": host,
            "port": port,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "healthy": True
        }
        
        # Store in cache with TTL
        await ultra_cache.set(
            f"service_registry:{service_key}",
            registration,
            ttl_seconds=self.registration_ttl,
            namespace="scaling"
        )
        
        logger.info(f"🔗 Service registered: {service_name} at {host}:{port}")
    
    async def heartbeat(self, service_name: str):
        """Send heartbeat for service instance"""
        service_key = f"{service_name}:{self.instance_id}"
        cache_key = f"service_registry:{service_key}"
        
        # Update heartbeat timestamp
        registration = await ultra_cache.get(cache_key, "scaling")
        if registration:
            registration["last_heartbeat"] = datetime.now().isoformat()
            await ultra_cache.set(
                cache_key,
                registration,
                ttl_seconds=self.registration_ttl,
                namespace="scaling"
            )
    
    async def discover_services(self, service_name: str) -> List[Dict[str, Any]]:
        """Discover healthy service instances"""
        # This would typically query Redis or a service mesh
        # For now, return a placeholder implementation
        pattern = f"service_registry:{service_name}:*"
        
        # Get all service instances (simplified)
        services = []
        cutoff_time = datetime.now() - timedelta(seconds=self.registration_ttl * 2)
        
        # In a real implementation, you'd scan Redis for the pattern
        # and filter by heartbeat timestamp
        
        return services
    
    async def deregister_service(self, service_name: str):
        """Deregister service instance"""
        service_key = f"{service_name}:{self.instance_id}"
        await ultra_cache.delete(f"service_registry:{service_key}", "scaling")
        logger.info(f"🔗 Service deregistered: {service_name}")

# ================================
# LOAD BALANCING CONFIGURATION
# ================================

class LoadBalancerConfig:
    """Generate load balancer configurations"""
    
    @staticmethod
    def generate_nginx_config(instances: List[Dict[str, Any]], config: ScalingConfig) -> str:
        """Generate Nginx upstream configuration"""
        
        upstream_servers = []
        for instance in instances:
            if instance.get("healthy", True):
                host = instance["host"]
                port = instance["port"]
                weight = instance.get("weight", 1)
                upstream_servers.append(f"    server {host}:{port} weight={weight};")
        
        session_config = ""
        if config.sticky_sessions:
            session_config = f"    hash $cookie_{config.session_affinity_cookie} consistent;"
        
        nginx_config = f"""
# Ultra-Performance Nginx Load Balancer Configuration
# Generated at {datetime.now().isoformat()}

upstream eventos_backend {{
{session_config}
    # Load balancing method
    least_conn;
    
    # Backend servers
{chr(10).join(upstream_servers)}
    
    # Health check (requires nginx_upstream_check_module)
    # check interval=3000 rise=2 fall=3 timeout=1000;
    
    # Connection keepalive
    keepalive 100;
    keepalive_requests 10000;
    keepalive_timeout 60s;
}}

server {{
    listen 80;
    listen 443 ssl http2;
    server_name eventos.yourdomain.com;
    
    # SSL configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Performance optimizations
    client_max_body_size 100M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    keepalive_timeout 65s;
    send_timeout 60s;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
    limit_req zone=api burst=200 nodelay;
    
    # API endpoints
    location /api/ {{
        proxy_pass http://eventos_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Performance optimizations
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Connection reuse
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }}
    
    # WebSocket endpoints
    location /ws/ {{
        proxy_pass http://eventos_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket specific timeouts
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }}
    
    # Static files (served directly by Nginx)
    location /static/ {{
        root /var/www/eventos;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Compression for static files
        gzip_static on;
        
        # Security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
    }}
    
    # Health check endpoint
    location /health {{
        proxy_pass http://eventos_backend;
        access_log off;
    }}
    
    # Metrics endpoint (restricted)
    location /metrics {{
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;
        deny all;
        
        proxy_pass http://eventos_backend;
    }}
}}
"""
        return nginx_config
    
    @staticmethod
    def generate_haproxy_config(instances: List[Dict[str, Any]], config: ScalingConfig) -> str:
        """Generate HAProxy configuration"""
        
        backend_servers = []
        for i, instance in enumerate(instances):
            if instance.get("healthy", True):
                host = instance["host"]
                port = instance["port"]
                weight = instance.get("weight", 1)
                backend_servers.append(f"    server app{i+1} {host}:{port} weight {weight} check")
        
        balance_method = "leastconn"
        if config.sticky_sessions:
            balance_method = f"source"
        
        haproxy_config = f"""
# Ultra-Performance HAProxy Configuration
# Generated at {datetime.now().isoformat()}

global
    daemon
    maxconn 100000
    
    # Performance tuning
    nbthread 4
    cpu-map auto:1/1-4 0-3
    
    # SSL configuration
    ssl-default-bind-ciphers ECDHE+aRSA+AESGCM:ECDHE+aRSA+SHA384:ECDHE+aRSA+SHA256:ECDHE+aRSA+SHA:ECDHE+aRSA+RC4:DHE+aRSA+AESGCM:DHE+aRSA+SHA256:DHE+aRSA+SHA:!aNULL:!eNULL:!LOW:!3DES:!MD5:!EXP:!PSK:!SRP:!DSS
    ssl-default-bind-options no-sslv3 no-tlsv10 no-tlsv11
    
defaults
    mode http
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    timeout http-keep-alive 2s
    timeout http-request 5s
    
    # Performance options
    option httplog
    option dontlognull
    option http-server-close
    option redispatch
    retries 3
    
    # Compression
    compression algo gzip
    compression type text/plain text/css application/json application/javascript text/xml application/xml application/rss+xml text/javascript

frontend eventos_frontend
    bind *:80
    bind *:443 ssl crt /path/to/ssl/cert.pem
    
    # Redirect HTTP to HTTPS
    redirect scheme https if !{{ ssl_fc }}
    
    # Rate limiting
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request reject if {{ sc_http_req_rate(0) gt 100 }}
    
    # ACLs for routing
    acl is_websocket hdr(Upgrade) -i websocket
    acl is_api path_beg /api/
    acl is_metrics path_beg /metrics
    acl is_health path_beg /health
    
    # Routing
    use_backend eventos_websocket if is_websocket
    use_backend eventos_api if is_api
    use_backend eventos_api if is_health
    use_backend eventos_metrics if is_metrics
    default_backend eventos_api

backend eventos_api
    balance {balance_method}
    
    # Health checks
    option httpchk GET /health
    http-check expect status 200
    
    # Performance options
    option http-server-close
    option httplog
    
    # Backend servers
{chr(10).join(backend_servers)}

backend eventos_websocket
    balance source
    
    # WebSocket specific options
    option http-server-close
    timeout tunnel 3600s
    
    # Backend servers (same as API)
{chr(10).join(backend_servers)}

backend eventos_metrics
    # Restrict metrics access
    acl allowed_ips src 127.0.0.1 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
    http-request deny unless allowed_ips
    
    balance roundrobin
    
    # Backend servers
{chr(10).join(backend_servers)}

# Statistics interface
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE
"""
        return haproxy_config

# ================================
# AUTO-SCALING MANAGER
# ================================

class HorizontalScaler:
    """Intelligent horizontal auto-scaling manager"""
    
    def __init__(self, config: ScalingConfig = None):
        self.config = config or ScalingConfig()
        self.cluster_state = ClusterState()
        self.service_registry = ServiceRegistry()
        self.scaling_active = False
        self.metrics_history: List[InstanceMetrics] = []
        
    async def start_scaling_manager(self):
        """Start the auto-scaling manager"""
        self.scaling_active = True
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._metrics_collection_loop()),
            asyncio.create_task(self._scaling_decision_loop()),
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._service_heartbeat_loop())
        ]
        
        logger.info("🔄 Horizontal scaling manager started")
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("🔄 Scaling manager stopped")
    
    async def stop_scaling_manager(self):
        """Stop the auto-scaling manager"""
        self.scaling_active = False
    
    async def _metrics_collection_loop(self):
        """Collect metrics from all instances"""
        while self.scaling_active:
            try:
                current_metrics = await self._collect_instance_metrics()
                
                # Update cluster state
                self.cluster_state.instances = {
                    metrics.instance_id: metrics
                    for metrics in current_metrics
                }
                
                self.cluster_state.total_instances = len(current_metrics)
                self.cluster_state.healthy_instances = sum(
                    1 for metrics in current_metrics if metrics.healthy
                )
                
                # Store metrics history for trend analysis
                self.metrics_history.extend(current_metrics)
                
                # Keep only last hour of metrics
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                # Update monitoring metrics
                ultra_metrics.system_cpu.set(
                    sum(m.cpu_usage_percent for m in current_metrics) / len(current_metrics)
                    if current_metrics else 0
                )
                
                await asyncio.sleep(self.config.health_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10)
    
    async def _collect_instance_metrics(self) -> List[InstanceMetrics]:
        """Collect metrics from all service instances"""
        # In a real implementation, this would discover service instances
        # and collect metrics from each one via HTTP endpoints or service mesh
        
        # For now, return metrics for the current instance
        current_instance = InstanceMetrics(
            instance_id=self.service_registry.instance_id,
            cpu_usage_percent=psutil.cpu_percent(interval=1),
            memory_usage_percent=psutil.virtual_memory().percent,
            requests_per_second=self._get_current_rps(),
            response_time_p95_ms=self._get_current_p95_response_time(),
            error_rate_percent=self._get_current_error_rate(),
            websocket_connections=self._get_websocket_connections(),
            healthy=True
        )
        
        return [current_instance]
    
    def _get_current_rps(self) -> float:
        """Get current requests per second"""
        # This would typically come from metrics collection
        # For now, return a placeholder
        return 50.0
    
    def _get_current_p95_response_time(self) -> float:
        """Get current P95 response time in milliseconds"""
        # This would typically come from metrics collection
        return 45.0
    
    def _get_current_error_rate(self) -> float:
        """Get current error rate percentage"""
        return 0.1
    
    def _get_websocket_connections(self) -> int:
        """Get current WebSocket connection count"""
        return 100
    
    async def _scaling_decision_loop(self):
        """Make scaling decisions based on metrics"""
        while self.scaling_active:
            try:
                if await self._should_scale_up():
                    await self._scale_up()
                elif await self._should_scale_down():
                    await self._scale_down()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scaling decision error: {e}")
                await asyncio.sleep(30)
    
    async def _should_scale_up(self) -> bool:
        """Determine if we should scale up"""
        if not self.cluster_state.instances:
            return False
        
        # Check cooldown period
        if (self.cluster_state.last_scale_action and 
            datetime.now() - self.cluster_state.last_scale_action < 
            timedelta(minutes=self.config.scale_up_cooldown_minutes)):
            return False
        
        # Check if we're at max capacity
        if self.cluster_state.total_instances >= self.config.max_instances:
            return False
        
        # Get average metrics
        healthy_instances = [m for m in self.cluster_state.instances.values() if m.healthy]
        if not healthy_instances:
            return False
        
        avg_cpu = sum(m.cpu_usage_percent for m in healthy_instances) / len(healthy_instances)
        avg_memory = sum(m.memory_usage_percent for m in healthy_instances) / len(healthy_instances)
        avg_response_time = sum(m.response_time_p95_ms for m in healthy_instances) / len(healthy_instances)
        max_error_rate = max(m.error_rate_percent for m in healthy_instances)
        
        # Scale up conditions
        return (
            avg_cpu > self.config.cpu_scale_up_threshold or
            avg_memory > self.config.memory_scale_up_threshold or
            avg_response_time > self.config.response_time_scale_up_threshold or
            max_error_rate > self.config.error_rate_scale_up_threshold
        )
    
    async def _should_scale_down(self) -> bool:
        """Determine if we should scale down"""
        if not self.cluster_state.instances:
            return False
        
        # Check cooldown period
        if (self.cluster_state.last_scale_action and 
            datetime.now() - self.cluster_state.last_scale_action < 
            timedelta(minutes=self.config.scale_down_cooldown_minutes)):
            return False
        
        # Check if we're at min capacity
        if self.cluster_state.healthy_instances <= self.config.min_instances:
            return False
        
        # Get average metrics
        healthy_instances = [m for m in self.cluster_state.instances.values() if m.healthy]
        if not healthy_instances:
            return False
        
        avg_cpu = sum(m.cpu_usage_percent for m in healthy_instances) / len(healthy_instances)
        avg_memory = sum(m.memory_usage_percent for m in healthy_instances) / len(healthy_instances)
        
        # Scale down conditions (all conditions must be met)
        return (
            avg_cpu < self.config.cpu_scale_down_threshold and
            avg_memory < self.config.memory_scale_down_threshold and
            self.cluster_state.healthy_instances > self.config.min_instances
        )
    
    async def _scale_up(self):
        """Scale up the cluster"""
        logger.info("📈 Scaling up: Adding new instance")
        
        # In a real implementation, this would:
        # 1. Call cloud provider API to launch new instance
        # 2. Wait for instance to be ready
        # 3. Register instance with load balancer
        # 4. Update service discovery
        
        self.cluster_state.last_scale_action = datetime.now()
        self.cluster_state.scale_action_type = "scale_up"
        self.cluster_state.target_instance_count += 1
        
        # Record scaling event in metrics
        ultra_metrics.alert_triggered.labels(
            alert_type='scale_up',
            severity='info'
        ).inc()
    
    async def _scale_down(self):
        """Scale down the cluster"""
        logger.info("📉 Scaling down: Removing instance")
        
        # In a real implementation, this would:
        # 1. Choose least utilized instance
        # 2. Drain connections gracefully
        # 3. Remove from load balancer
        # 4. Terminate instance
        # 5. Update service discovery
        
        self.cluster_state.last_scale_action = datetime.now()
        self.cluster_state.scale_action_type = "scale_down"
        self.cluster_state.target_instance_count = max(
            self.config.min_instances,
            self.cluster_state.target_instance_count - 1
        )
        
        # Record scaling event in metrics
        ultra_metrics.alert_triggered.labels(
            alert_type='scale_down',
            severity='info'
        ).inc()
    
    async def _health_check_loop(self):
        """Monitor instance health"""
        while self.scaling_active:
            try:
                # Check health of all registered instances
                for instance_id, metrics in self.cluster_state.instances.items():
                    healthy = await self._check_instance_health(instance_id, metrics)
                    metrics.healthy = healthy
                
                await asyncio.sleep(self.config.health_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)
    
    async def _check_instance_health(self, instance_id: str, metrics: InstanceMetrics) -> bool:
        """Check if specific instance is healthy"""
        # In a real implementation, this would make HTTP requests
        # to the instance's health check endpoint
        
        # Simple health check based on metrics
        if (metrics.cpu_usage_percent > 95 or 
            metrics.memory_usage_percent > 95 or
            metrics.error_rate_percent > 10):
            return False
        
        return True
    
    async def _service_heartbeat_loop(self):
        """Send periodic heartbeats for service discovery"""
        while self.scaling_active:
            try:
                await self.service_registry.heartbeat("eventos_backend")
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"Service heartbeat error: {e}")
                await asyncio.sleep(10)
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status"""
        healthy_instances = [m for m in self.cluster_state.instances.values() if m.healthy]
        
        if healthy_instances:
            avg_cpu = sum(m.cpu_usage_percent for m in healthy_instances) / len(healthy_instances)
            avg_memory = sum(m.memory_usage_percent for m in healthy_instances) / len(healthy_instances)
            avg_response_time = sum(m.response_time_p95_ms for m in healthy_instances) / len(healthy_instances)
            total_rps = sum(m.requests_per_second for m in healthy_instances)
            max_error_rate = max(m.error_rate_percent for m in healthy_instances) if healthy_instances else 0
        else:
            avg_cpu = avg_memory = avg_response_time = total_rps = max_error_rate = 0
        
        return {
            "cluster_health": "healthy" if self.cluster_state.healthy_instances > 0 else "unhealthy",
            "total_instances": self.cluster_state.total_instances,
            "healthy_instances": self.cluster_state.healthy_instances,
            "target_instances": self.cluster_state.target_instance_count,
            
            "performance_metrics": {
                "avg_cpu_percent": round(avg_cpu, 1),
                "avg_memory_percent": round(avg_memory, 1),
                "avg_response_time_ms": round(avg_response_time, 1),
                "total_requests_per_second": round(total_rps, 1),
                "max_error_rate_percent": round(max_error_rate, 2)
            },
            
            "scaling_info": {
                "last_scale_action": self.cluster_state.last_scale_action.isoformat() if self.cluster_state.last_scale_action else None,
                "last_action_type": self.cluster_state.scale_action_type,
                "min_instances": self.config.min_instances,
                "max_instances": self.config.max_instances,
                "scaling_strategy": self.config.scaling_strategy.value
            },
            
            "instance_details": {
                instance_id: {
                    "healthy": metrics.healthy,
                    "cpu_percent": metrics.cpu_usage_percent,
                    "memory_percent": metrics.memory_usage_percent,
                    "rps": metrics.requests_per_second,
                    "response_time_p95_ms": metrics.response_time_p95_ms,
                    "websocket_connections": metrics.websocket_connections,
                    "last_update": metrics.timestamp.isoformat()
                }
                for instance_id, metrics in self.cluster_state.instances.items()
            }
        }

# ================================
# DEPLOYMENT CONFIGURATION
# ================================

class DeploymentManager:
    """Manage deployment configurations and orchestration"""
    
    @staticmethod
    def generate_docker_compose_config(scaling_config: ScalingConfig) -> str:
        """Generate Docker Compose configuration for scaling"""
        
        return f"""
# Ultra-Performance Docker Compose Configuration
# Generated at {datetime.now().isoformat()}

version: '3.8'

services:
  # Application services
  eventos-app:
    build: .
    image: eventos-backend:latest
    deploy:
      replicas: {scaling_config.target_instances}
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    environment:
      - DATABASE_URL=postgresql://eventos_user:eventos_2024_secure!@postgres:5432/eventos_db
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - eventos-network

  # Load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - eventos-app
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    networks:
      - eventos-network

  # Database
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=eventos_db
      - POSTGRES_USER=eventos_user
      - POSTGRES_PASSWORD=eventos_2024_secure!
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    networks:
      - eventos-network

  # Redis cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    networks:
      - eventos-network

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - eventos-network

volumes:
  postgres_data:
  redis_data:

networks:
  eventos-network:
    driver: overlay
    attachable: true
"""
    
    @staticmethod
    def generate_kubernetes_config(scaling_config: ScalingConfig) -> str:
        """Generate Kubernetes deployment configuration"""
        
        return f"""
# Ultra-Performance Kubernetes Configuration
# Generated at {datetime.now().isoformat()}

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eventos-backend
  labels:
    app: eventos-backend
spec:
  replicas: {scaling_config.target_instances}
  selector:
    matchLabels:
      app: eventos-backend
  template:
    metadata:
      labels:
        app: eventos-backend
    spec:
      containers:
      - name: eventos-backend
        image: eventos-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: eventos-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 2000m
            memory: 2Gi
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

---
apiVersion: v1
kind: Service
metadata:
  name: eventos-backend-service
spec:
  selector:
    app: eventos-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: eventos-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: eventos-backend
  minReplicas: {scaling_config.min_instances}
  maxReplicas: {scaling_config.max_instances}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {int(scaling_config.cpu_scale_up_threshold)}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: {int(scaling_config.memory_scale_up_threshold)}
  behavior:
    scaleUp:
      stabilizationWindowSeconds: {scaling_config.scale_up_cooldown_minutes * 60}
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: {scaling_config.scale_down_cooldown_minutes * 60}
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
"""

# Global scaling manager
horizontal_scaler = HorizontalScaler()
service_registry = ServiceRegistry()

async def init_horizontal_scaling(config: ScalingConfig = None):
    """Initialize horizontal scaling system"""
    global horizontal_scaler
    if config:
        horizontal_scaler = HorizontalScaler(config)
    
    # Register current service
    await service_registry.register_service(
        service_name="eventos_backend",
        host=socket.gethostbyname(socket.gethostname()),
        port=8000,
        metadata={"version": "3.0.0-ultra"}
    )
    
    logger.info("✅ Horizontal scaling system initialized")

# Export main components
__all__ = [
    'horizontal_scaler', 'service_registry', 'ScalingConfig', 'LoadBalancerConfig',
    'DeploymentManager', 'init_horizontal_scaling'
]