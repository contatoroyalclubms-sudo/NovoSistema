"""
Ultra-Performance Monitoring System with OpenTelemetry
Sistema Universal de Gestão de Eventos - Enterprise Scale
Target: Sub-microsecond tracing, comprehensive observability, predictive analytics
"""

import asyncio
import logging
import time
import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from contextlib import asynccontextmanager
import threading
import json

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.semantic_conventions.trace import SpanAttributes

# Prometheus and custom metrics
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)

logger = logging.getLogger(__name__)

# ================================
# PERFORMANCE METRICS COLLECTION
# ================================

class UltraPerformanceMetrics:
    """Comprehensive performance metrics collection"""
    
    def __init__(self):
        # Custom registry for ultra-performance metrics
        self.registry = CollectorRegistry()
        
        # API Performance Metrics
        self.api_requests = Counter(
            'ultra_api_requests_total',
            'Total API requests with ultra-performance tracking',
            ['method', 'endpoint', 'status_code', 'user_type'],
            registry=self.registry
        )
        
        self.api_duration = Histogram(
            'ultra_api_duration_seconds',
            'API request duration with ultra-precision',
            ['method', 'endpoint'],
            buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )
        
        self.api_response_size = Histogram(
            'ultra_api_response_size_bytes',
            'API response size distribution',
            ['endpoint'],
            registry=self.registry
        )
        
        # Database Performance Metrics
        self.db_queries = Counter(
            'ultra_db_queries_total',
            'Database queries with performance classification',
            ['operation', 'table', 'performance_tier'],
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'ultra_db_query_duration_seconds',
            'Database query execution time with ultra-precision',
            ['operation', 'table'],
            buckets=[0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
            registry=self.registry
        )
        
        self.db_connection_pool = Gauge(
            'ultra_db_connection_pool_usage',
            'Database connection pool usage metrics',
            ['pool_name', 'metric_type'],
            registry=self.registry
        )
        
        # Cache Performance Metrics
        self.cache_operations = Counter(
            'ultra_cache_operations_total',
            'Cache operations with tier tracking',
            ['tier', 'operation', 'hit_miss'],
            registry=self.registry
        )
        
        self.cache_latency = Histogram(
            'ultra_cache_latency_seconds',
            'Cache operation latency by tier',
            ['tier', 'operation'],
            buckets=[0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05],
            registry=self.registry
        )
        
        self.cache_memory_usage = Gauge(
            'ultra_cache_memory_bytes',
            'Cache memory usage by tier',
            ['tier'],
            registry=self.registry
        )
        
        # WebSocket Performance Metrics
        self.websocket_connections = Gauge(
            'ultra_websocket_connections',
            'Active WebSocket connections',
            ['connection_type', 'event_id'],
            registry=self.registry
        )
        
        self.websocket_messages = Counter(
            'ultra_websocket_messages_total',
            'WebSocket messages processed',
            ['direction', 'message_type', 'latency_tier'],
            registry=self.registry
        )
        
        # System Resource Metrics
        self.system_cpu = Gauge(
            'ultra_system_cpu_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory = Gauge(
            'ultra_system_memory_bytes',
            'System memory usage',
            ['memory_type'],
            registry=self.registry
        )
        
        self.system_disk_io = Counter(
            'ultra_system_disk_io_bytes',
            'System disk I/O',
            ['direction'],
            registry=self.registry
        )
        
        # Business Metrics
        self.business_events = Counter(
            'ultra_business_events_total',
            'Business events processed',
            ['event_type', 'status', 'processing_tier'],
            registry=self.registry
        )
        
        self.revenue_processing = Counter(
            'ultra_revenue_processing_total',
            'Revenue processing metrics',
            ['payment_method', 'status', 'amount_tier'],
            registry=self.registry
        )
        
        # Error and Alert Metrics
        self.error_rate = Counter(
            'ultra_errors_total',
            'Error count by category and severity',
            ['category', 'severity', 'component'],
            registry=self.registry
        )
        
        self.alert_triggered = Counter(
            'ultra_alerts_triggered_total',
            'Alerts triggered by type and severity',
            ['alert_type', 'severity'],
            registry=self.registry
        )

# Global metrics instance
ultra_metrics = UltraPerformanceMetrics()

# ================================
# OPENTELEMETRY CONFIGURATION
# ================================

@dataclass
class TracingConfig:
    """OpenTelemetry tracing configuration"""
    service_name: str = "eventos-ultra-performance"
    service_version: str = "3.0.0"
    environment: str = "production"
    otlp_endpoint: str = "http://localhost:4317"
    enable_console_export: bool = False
    enable_prometheus_export: bool = True
    sample_rate: float = 1.0  # 100% sampling for ultra-performance monitoring

class UltraPerformanceTracing:
    """Ultra-performance distributed tracing system"""
    
    def __init__(self, config: TracingConfig = None):
        self.config = config or TracingConfig()
        self.tracer_provider = None
        self.meter_provider = None
        self.tracer = None
        self.meter = None
        
    def initialize(self):
        """Initialize OpenTelemetry tracing with ultra-performance configuration"""
        
        # Configure resource with service information
        resource = Resource.create({
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
            "environment": self.config.environment,
            "deployment.environment": self.config.environment
        })
        
        # Configure tracing
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)
        
        # Add OTLP span exporter for distributed tracing
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.config.otlp_endpoint,
            insecure=True  # Use TLS in production
        )
        
        span_processor = BatchSpanProcessor(
            otlp_exporter,
            max_queue_size=2048,  # High-throughput queue
            export_timeout=30000,  # 30 second timeout
            max_export_batch_size=512  # Batch size optimization
        )
        
        self.tracer_provider.add_span_processor(span_processor)
        
        # Configure metrics
        prometheus_reader = PrometheusMetricReader(registry=ultra_metrics.registry)
        self.meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[prometheus_reader]
        )
        metrics.set_meter_provider(self.meter_provider)
        
        # Get tracer and meter instances
        self.tracer = trace.get_tracer(self.config.service_name, self.config.service_version)
        self.meter = metrics.get_meter(self.config.service_name, self.config.service_version)
        
        # Set up propagation
        set_global_textmap(B3MultiFormat())
        
        logger.info("✅ Ultra-Performance OpenTelemetry initialized")
    
    def instrument_frameworks(self):
        """Instrument frameworks with OpenTelemetry"""
        try:
            # FastAPI instrumentation
            FastAPIInstrumentor().instrument()
            
            # Database instrumentation
            SQLAlchemyInstrumentor().instrument(
                enable_commenter=True,
                commenter_options={
                    "db_driver": True,
                    "db_framework": True,
                    "opentelemetry_values": True
                }
            )
            
            # Redis instrumentation
            RedisInstrumentor().instrument()
            
            # Celery instrumentation
            CeleryInstrumentor().instrument()
            
            logger.info("✅ Framework instrumentation completed")
            
        except Exception as e:
            logger.error(f"❌ Framework instrumentation failed: {e}")
    
    @asynccontextmanager
    async def trace_operation(
        self, 
        operation_name: str,
        attributes: Optional[Dict[str, Any]] = None,
        record_exception: bool = True
    ):
        """Context manager for tracing operations with ultra-performance"""
        
        with self.tracer.start_as_current_span(operation_name) as span:
            start_time = time.perf_counter()
            
            # Set span attributes
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            try:
                yield span
                
                # Record success metrics
                duration = time.perf_counter() - start_time
                span.set_attribute("operation.duration_ms", duration * 1000)
                span.set_attribute("operation.success", True)
                
            except Exception as e:
                # Record error metrics
                duration = time.perf_counter() - start_time
                span.set_attribute("operation.duration_ms", duration * 1000)
                span.set_attribute("operation.success", False)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                
                if record_exception:
                    span.record_exception(e)
                
                # Update error metrics
                ultra_metrics.error_rate.labels(
                    category="operation",
                    severity="error",
                    component=operation_name
                ).inc()
                
                raise

# Global tracing instance
ultra_tracing = UltraPerformanceTracing()

# ================================
# SYSTEM PERFORMANCE MONITORING
# ================================

class SystemMonitor:
    """Real-time system performance monitoring"""
    
    def __init__(self):
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage_percent": 90.0,
            "response_time_ms": 100.0,
            "error_rate_percent": 1.0
        }
        
    async def start_monitoring(self, interval_seconds: float = 5.0):
        """Start continuous system monitoring"""
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval_seconds))
        logger.info("🔍 System monitoring started")
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("🔍 System monitoring stopped")
    
    async def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        last_disk_io = psutil.disk_io_counters()
        
        while self.monitoring_active:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                ultra_metrics.system_cpu.set(cpu_percent)
                
                # Memory metrics
                memory = psutil.virtual_memory()
                ultra_metrics.system_memory.labels(memory_type='used').set(memory.used)
                ultra_metrics.system_memory.labels(memory_type='available').set(memory.available)
                ultra_metrics.system_memory.labels(memory_type='total').set(memory.total)
                
                # Disk I/O metrics
                current_disk_io = psutil.disk_io_counters()
                if last_disk_io:
                    read_bytes = current_disk_io.read_bytes - last_disk_io.read_bytes
                    write_bytes = current_disk_io.write_bytes - last_disk_io.write_bytes
                    
                    ultra_metrics.system_disk_io.labels(direction='read').inc(read_bytes)
                    ultra_metrics.system_disk_io.labels(direction='write').inc(write_bytes)
                
                last_disk_io = current_disk_io
                
                # Check alert thresholds
                await self._check_alerts(cpu_percent, memory.percent)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _check_alerts(self, cpu_percent: float, memory_percent: float):
        """Check system metrics against alert thresholds"""
        
        # CPU alert
        if cpu_percent > self.alert_thresholds["cpu_percent"]:
            ultra_metrics.alert_triggered.labels(
                alert_type='high_cpu',
                severity='warning'
            ).inc()
            logger.warning(f"🚨 High CPU usage: {cpu_percent:.1f}%")
        
        # Memory alert
        if memory_percent > self.alert_thresholds["memory_percent"]:
            ultra_metrics.alert_triggered.labels(
                alert_type='high_memory',
                severity='warning'
            ).inc()
            logger.warning(f"🚨 High memory usage: {memory_percent:.1f}%")

# Global system monitor
system_monitor = SystemMonitor()

# ================================
# PERFORMANCE ANALYTICS
# ================================

class PerformanceAnalytics:
    """Advanced performance analytics and predictions"""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.performance_baselines = {}
        self.anomaly_thresholds = {}
        
    def record_performance_snapshot(self, metrics: Dict[str, Any]):
        """Record performance snapshot for analysis"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        self.metrics_history.append(snapshot)
        
        # Keep only last 1000 snapshots for memory efficiency
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect performance anomalies using statistical analysis"""
        anomalies = []
        
        if len(self.metrics_history) < 10:
            return anomalies  # Not enough data
        
        # Simple anomaly detection based on standard deviation
        recent_metrics = self.metrics_history[-10:]
        
        for metric_name in ["response_time", "cpu_usage", "memory_usage"]:
            values = [m["metrics"].get(metric_name, 0) for m in recent_metrics]
            if not values:
                continue
            
            avg = sum(values) / len(values)
            variance = sum((x - avg) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            # Check if latest value is beyond 2 standard deviations
            latest_value = values[-1]
            if abs(latest_value - avg) > (2 * std_dev):
                anomalies.append({
                    "metric": metric_name,
                    "value": latest_value,
                    "baseline": avg,
                    "deviation": abs(latest_value - avg) / std_dev if std_dev > 0 else 0,
                    "severity": "high" if abs(latest_value - avg) > (3 * std_dev) else "medium"
                })
        
        return anomalies
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.metrics_history:
            return {"error": "No performance data available"}
        
        recent_data = self.metrics_history[-100:] if len(self.metrics_history) >= 100 else self.metrics_history
        
        # Calculate averages and trends
        summary = {
            "data_points": len(recent_data),
            "time_range": {
                "start": recent_data[0]["timestamp"] if recent_data else None,
                "end": recent_data[-1]["timestamp"] if recent_data else None
            },
            "metrics": {},
            "anomalies": self.detect_anomalies(),
            "performance_grade": self._calculate_performance_grade()
        }
        
        return summary
    
    def _calculate_performance_grade(self) -> str:
        """Calculate overall performance grade"""
        if not self.metrics_history:
            return "N/A"
        
        recent = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        
        # Simple grading based on response times and error rates
        avg_response_time = sum(m["metrics"].get("response_time", 0) for m in recent) / len(recent)
        avg_error_rate = sum(m["metrics"].get("error_rate", 0) for m in recent) / len(recent)
        
        if avg_response_time < 50 and avg_error_rate < 0.1:
            return "A+"
        elif avg_response_time < 100 and avg_error_rate < 0.5:
            return "A"
        elif avg_response_time < 200 and avg_error_rate < 1.0:
            return "B"
        elif avg_response_time < 500 and avg_error_rate < 2.0:
            return "C"
        else:
            return "F"

# Global performance analytics
performance_analytics = PerformanceAnalytics()

# ================================
# INITIALIZATION AND UTILITIES
# ================================

async def init_ultra_monitoring():
    """Initialize ultra-performance monitoring system"""
    logger.info("🚀 Initializing Ultra-Performance Monitoring System...")
    
    try:
        # Initialize OpenTelemetry tracing
        ultra_tracing.initialize()
        ultra_tracing.instrument_frameworks()
        
        # Start system monitoring
        await system_monitor.start_monitoring()
        
        logger.info("✅ Ultra-Performance Monitoring System initialized")
        
    except Exception as e:
        logger.error(f"❌ Monitoring initialization failed: {e}")
        raise

async def shutdown_ultra_monitoring():
    """Gracefully shutdown monitoring system"""
    logger.info("🛑 Shutting down Ultra-Performance Monitoring System...")
    
    try:
        # Stop system monitoring
        await system_monitor.stop_monitoring()
        
        logger.info("✅ Ultra-Performance Monitoring System shutdown completed")
        
    except Exception as e:
        logger.error(f"❌ Monitoring shutdown error: {e}")

def get_prometheus_metrics() -> str:
    """Get Prometheus metrics in text format"""
    return generate_latest(ultra_metrics.registry)

# Performance decorators for easy integration
def monitor_performance(operation_name: str, record_metrics: bool = True):
    """Decorator for monitoring function performance"""
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            async with ultra_tracing.trace_operation(
                operation_name,
                attributes={"function": func.__name__}
            ) as span:
                start_time = time.perf_counter()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    if record_metrics:
                        duration = time.perf_counter() - start_time
                        ultra_metrics.business_events.labels(
                            event_type=operation_name,
                            status='success',
                            processing_tier='normal' if duration < 0.1 else 'slow'
                        ).inc()
                    
                    return result
                    
                except Exception as e:
                    if record_metrics:
                        ultra_metrics.business_events.labels(
                            event_type=operation_name,
                            status='error',
                            processing_tier='failed'
                        ).inc()
                    raise
        
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions, create a simplified version
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                
                if record_metrics:
                    duration = time.perf_counter() - start_time
                    ultra_metrics.business_events.labels(
                        event_type=operation_name,
                        status='success',
                        processing_tier='normal' if duration < 0.1 else 'slow'
                    ).inc()
                
                return result
                
            except Exception as e:
                if record_metrics:
                    ultra_metrics.business_events.labels(
                        event_type=operation_name,
                        status='error',
                        processing_tier='failed'
                    ).inc()
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

# Export main components
__all__ = [
    'ultra_metrics', 'ultra_tracing', 'system_monitor', 'performance_analytics',
    'init_ultra_monitoring', 'shutdown_ultra_monitoring', 'get_prometheus_metrics',
    'monitor_performance'
]