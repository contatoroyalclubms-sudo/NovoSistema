"""
Advanced Monitoring and Alerting System
Enterprise-grade monitoring with real-time metrics, alerts, and performance analysis
"""

import asyncio
import json
import logging
import time
import psutil
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import aiofiles
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class Alert:
    id: str
    level: AlertLevel
    title: str
    message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    tags: Dict[str, str] = None

@dataclass
class MetricPoint:
    timestamp: float
    value: float
    tags: Dict[str, str] = None

@dataclass
class HealthCheck:
    name: str
    status: str  # healthy, unhealthy, unknown
    response_time_ms: float
    message: Optional[str] = None
    timestamp: datetime = None
    metadata: Dict[str, Any] = None

class Metric:
    """Advanced metric with statistical analysis"""
    
    def __init__(self, name: str, metric_type: MetricType, description: str = "", 
                 max_points: int = 1000, tags: Dict[str, str] = None):
        self.name = name
        self.type = metric_type
        self.description = description
        self.max_points = max_points
        self.tags = tags or {}
        self.points = deque(maxlen=max_points)
        self.total_value = 0.0
        self.count = 0
        self.created_at = time.time()
        
    def add_point(self, value: float, timestamp: float = None, tags: Dict[str, str] = None):
        """Add a data point to the metric"""
        timestamp = timestamp or time.time()
        point = MetricPoint(timestamp, value, tags)
        
        self.points.append(point)
        
        if self.type in [MetricType.COUNTER, MetricType.GAUGE]:
            self.total_value += value
            self.count += 1
        elif self.type == MetricType.HISTOGRAM:
            self.total_value += value
            self.count += 1
    
    def get_current_value(self) -> float:
        """Get current metric value"""
        if not self.points:
            return 0.0
        
        if self.type == MetricType.GAUGE:
            return self.points[-1].value
        elif self.type == MetricType.COUNTER:
            return self.total_value
        elif self.type == MetricType.HISTOGRAM:
            return self.total_value / max(self.count, 1)
        else:
            return self.points[-1].value
    
    def get_statistics(self, time_window: Optional[int] = None) -> Dict[str, float]:
        """Get statistical analysis of the metric"""
        if not self.points:
            return {}
        
        # Filter by time window if specified
        if time_window:
            cutoff = time.time() - time_window
            values = [p.value for p in self.points if p.timestamp >= cutoff]
        else:
            values = [p.value for p in self.points]
        
        if not values:
            return {}
        
        try:
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                'p95': statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
                'p99': statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values),
                'current': self.get_current_value(),
                'rate_per_minute': self._calculate_rate(values, 60) if len(values) > 1 else 0
            }
        except Exception as e:
            logger.error(f"Error calculating statistics for {self.name}: {e}")
            return {'current': self.get_current_value()}
    
    def _calculate_rate(self, values: List[float], time_window: int) -> float:
        """Calculate rate of change per time window"""
        if len(values) < 2:
            return 0
        
        recent_points = [p for p in self.points if p.timestamp >= time.time() - time_window]
        if len(recent_points) < 2:
            return 0
        
        time_diff = recent_points[-1].timestamp - recent_points[0].timestamp
        value_diff = sum(p.value for p in recent_points[-10:]) - sum(p.value for p in recent_points[:10])
        
        return (value_diff / max(time_diff, 1)) * 60  # Per minute

class MonitoringSystem:
    """Enterprise-grade monitoring system"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.alerts: List[Alert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.running = False
        
        # System metrics
        self._init_system_metrics()
        
        # Alert thresholds
        self._init_default_alert_rules()
    
    def _init_system_metrics(self):
        """Initialize system performance metrics"""
        self.metrics['cpu_usage'] = Metric('cpu_usage', MetricType.GAUGE, 'CPU usage percentage')
        self.metrics['memory_usage'] = Metric('memory_usage', MetricType.GAUGE, 'Memory usage percentage')  
        self.metrics['disk_usage'] = Metric('disk_usage', MetricType.GAUGE, 'Disk usage percentage')
        self.metrics['network_bytes_sent'] = Metric('network_bytes_sent', MetricType.COUNTER, 'Network bytes sent')
        self.metrics['network_bytes_recv'] = Metric('network_bytes_recv', MetricType.COUNTER, 'Network bytes received')
        
        # Application metrics
        self.metrics['request_count'] = Metric('request_count', MetricType.COUNTER, 'Total HTTP requests')
        self.metrics['request_duration'] = Metric('request_duration', MetricType.HISTOGRAM, 'HTTP request duration')
        self.metrics['error_count'] = Metric('error_count', MetricType.COUNTER, 'Total HTTP errors')
        self.metrics['active_connections'] = Metric('active_connections', MetricType.GAUGE, 'Active connections')
        
        # Database metrics
        self.metrics['db_query_count'] = Metric('db_query_count', MetricType.COUNTER, 'Database queries')
        self.metrics['db_query_duration'] = Metric('db_query_duration', MetricType.HISTOGRAM, 'Database query duration')
        self.metrics['db_connection_pool'] = Metric('db_connection_pool', MetricType.GAUGE, 'Database connections')
        
        # Cache metrics
        self.metrics['cache_hits'] = Metric('cache_hits', MetricType.COUNTER, 'Cache hits')
        self.metrics['cache_misses'] = Metric('cache_misses', MetricType.COUNTER, 'Cache misses')
        self.metrics['cache_size'] = Metric('cache_size', MetricType.GAUGE, 'Cache size in bytes')
    
    def _init_default_alert_rules(self):
        """Initialize default alerting rules"""
        self.alert_rules = {
            'cpu_usage': {
                'threshold': 80,
                'comparison': 'gt',
                'level': AlertLevel.WARNING,
                'message': 'High CPU usage detected'
            },
            'memory_usage': {
                'threshold': 85,
                'comparison': 'gt', 
                'level': AlertLevel.WARNING,
                'message': 'High memory usage detected'
            },
            'disk_usage': {
                'threshold': 90,
                'comparison': 'gt',
                'level': AlertLevel.CRITICAL,
                'message': 'Disk space critically low'
            },
            'request_duration': {
                'threshold': 1000,  # 1 second
                'comparison': 'gt',
                'level': AlertLevel.WARNING,
                'message': 'High request duration detected',
                'metric_function': 'p95'  # Use 95th percentile
            },
            'error_rate': {
                'threshold': 5,  # 5% error rate
                'comparison': 'gt',
                'level': AlertLevel.ERROR,
                'message': 'High error rate detected',
                'custom_calculation': True
            }
        }
    
    async def start(self):
        """Start monitoring system"""
        if self.running:
            return
        
        self.running = True
        logger.info("🔍 Starting monitoring system...")
        
        # Start background tasks
        asyncio.create_task(self._system_metrics_collector())
        asyncio.create_task(self._alert_processor())
        asyncio.create_task(self._health_check_runner())
        asyncio.create_task(self._metrics_cleanup())
        
        logger.info("✅ Monitoring system started")
    
    async def stop(self):
        """Stop monitoring system"""
        self.running = False
        logger.info("🔍 Monitoring system stopped")
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric value"""
        if name not in self.metrics:
            logger.warning(f"Metric {name} not found")
            return
        
        self.metrics[name].add_point(value, tags=tags)
    
    def increment_counter(self, name: str, value: float = 1, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        self.record_metric(name, value, tags)
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric value"""
        self.record_metric(name, value, tags)
    
    def record_timer(self, name: str, duration_ms: float, tags: Dict[str, str] = None):
        """Record a timer metric"""
        self.record_metric(name, duration_ms, tags)
    
    def add_alert_rule(self, metric_name: str, threshold: float, level: AlertLevel,
                      comparison: str = 'gt', message: str = None):
        """Add custom alert rule"""
        self.alert_rules[metric_name] = {
            'threshold': threshold,
            'comparison': comparison,
            'level': level,
            'message': message or f'{metric_name} threshold exceeded'
        }
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add alert handler"""
        self.alert_handlers.append(handler)
    
    async def _system_metrics_collector(self):
        """Collect system performance metrics"""
        while self.running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                self.set_gauge('cpu_usage', cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.set_gauge('memory_usage', memory.percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.set_gauge('disk_usage', disk_percent)
                
                # Network stats
                network = psutil.net_io_counters()
                self.set_gauge('network_bytes_sent', network.bytes_sent)
                self.set_gauge('network_bytes_recv', network.bytes_recv)
                
                await asyncio.sleep(10)  # Collect every 10 seconds
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(30)
    
    async def _alert_processor(self):
        """Process alerts based on metric thresholds"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for metric_name, rule in self.alert_rules.items():
                    await self._check_alert_rule(metric_name, rule)
                    
            except Exception as e:
                logger.error(f"Error processing alerts: {e}")
    
    async def _check_alert_rule(self, metric_name: str, rule: Dict[str, Any]):
        """Check individual alert rule"""
        if metric_name not in self.metrics:
            return
        
        metric = self.metrics[metric_name]
        
        # Custom calculation for error rate
        if rule.get('custom_calculation') and metric_name == 'error_rate':
            current_value = self._calculate_error_rate()
        else:
            # Use specified metric function or current value
            stats = metric.get_statistics(time_window=300)  # Last 5 minutes
            metric_function = rule.get('metric_function', 'current')
            current_value = stats.get(metric_function, metric.get_current_value())
        
        threshold = rule['threshold']
        comparison = rule['comparison']
        
        # Check threshold
        alert_triggered = False
        if comparison == 'gt' and current_value > threshold:
            alert_triggered = True
        elif comparison == 'lt' and current_value < threshold:
            alert_triggered = True
        elif comparison == 'eq' and current_value == threshold:
            alert_triggered = True
        
        if alert_triggered:
            # Check if alert already exists and is not resolved
            existing_alert = next(
                (a for a in self.alerts 
                 if a.metric_name == metric_name and not a.resolved),
                None
            )
            
            if not existing_alert:
                alert = Alert(
                    id=f"{metric_name}_{int(time.time())}",
                    level=rule['level'],
                    title=f"{metric_name.replace('_', ' ').title()} Alert",
                    message=rule['message'],
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold=threshold,
                    timestamp=datetime.utcnow(),
                    tags={'metric': metric_name, 'comparison': comparison}
                )
                
                self.alerts.append(alert)
                await self._handle_alert(alert)
        else:
            # Resolve existing alert if conditions are normal
            existing_alert = next(
                (a for a in self.alerts 
                 if a.metric_name == metric_name and not a.resolved),
                None
            )
            
            if existing_alert:
                existing_alert.resolved = True
                existing_alert.resolved_at = datetime.utcnow()
                logger.info(f"✅ Alert resolved: {existing_alert.title}")
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        request_stats = self.metrics['request_count'].get_statistics(time_window=300)
        error_stats = self.metrics['error_count'].get_statistics(time_window=300)
        
        total_requests = request_stats.get('count', 0)
        total_errors = error_stats.get('count', 0)
        
        if total_requests == 0:
            return 0
        
        return (total_errors / total_requests) * 100
    
    async def _handle_alert(self, alert: Alert):
        """Handle triggered alert"""
        logger.warning(f"🚨 Alert triggered: {alert.title} - {alert.message}")
        
        # Call registered alert handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def register_health_check(self, name: str, check_func: Callable[[], bool], 
                            description: str = ""):
        """Register a health check function"""
        async def run_check():
            try:
                start_time = time.perf_counter()
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                response_time = (time.perf_counter() - start_time) * 1000
                
                self.health_checks[name] = HealthCheck(
                    name=name,
                    status='healthy' if result else 'unhealthy',
                    response_time_ms=round(response_time, 2),
                    timestamp=datetime.utcnow(),
                    metadata={'description': description}
                )
                
            except Exception as e:
                self.health_checks[name] = HealthCheck(
                    name=name,
                    status='unhealthy',
                    response_time_ms=0,
                    message=str(e),
                    timestamp=datetime.utcnow()
                )
        
        # Store the check function for periodic execution
        if not hasattr(self, '_health_check_funcs'):
            self._health_check_funcs = {}
        self._health_check_funcs[name] = run_check
    
    async def _health_check_runner(self):
        """Run health checks periodically"""
        while self.running:
            try:
                if hasattr(self, '_health_check_funcs'):
                    for name, check_func in self._health_check_funcs.items():
                        await check_func()
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Error running health checks: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_cleanup(self):
        """Clean up old metrics data"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff_time = time.time() - (24 * 3600)  # 24 hours ago
                
                for metric in self.metrics.values():
                    # Remove old points
                    while metric.points and metric.points[0].timestamp < cutoff_time:
                        metric.points.popleft()
                
                # Clean up resolved alerts older than 7 days
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                self.alerts = [
                    alert for alert in self.alerts
                    if not alert.resolved or alert.resolved_at > cutoff_date
                ]
                
                logger.debug("🧹 Metrics cleanup completed")
                
            except Exception as e:
                logger.error(f"Error in metrics cleanup: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {}
        
        for name, metric in self.metrics.items():
            stats = metric.get_statistics(time_window=300)  # Last 5 minutes
            summary[name] = {
                'type': metric.type.value,
                'description': metric.description,
                'current_value': metric.get_current_value(),
                'statistics': stats,
                'data_points': len(metric.points)
            }
        
        return summary
    
    def get_alerts_summary(self) -> Dict[str, Any]:
        """Get summary of alerts"""
        active_alerts = [a for a in self.alerts if not a.resolved]
        resolved_alerts = [a for a in self.alerts if a.resolved]
        
        return {
            'active_count': len(active_alerts),
            'resolved_count': len(resolved_alerts),
            'active_alerts': [asdict(alert) for alert in active_alerts[-10:]],  # Last 10
            'alert_levels': {
                'critical': len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
                'error': len([a for a in active_alerts if a.level == AlertLevel.ERROR]),
                'warning': len([a for a in active_alerts if a.level == AlertLevel.WARNING]),
                'info': len([a for a in active_alerts if a.level == AlertLevel.INFO])
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        if not self.health_checks:
            return {'status': 'unknown', 'checks': []}
        
        healthy_checks = [h for h in self.health_checks.values() if h.status == 'healthy']
        unhealthy_checks = [h for h in self.health_checks.values() if h.status == 'unhealthy']
        
        overall_status = 'healthy'
        if unhealthy_checks:
            overall_status = 'unhealthy'
        elif not healthy_checks:
            overall_status = 'unknown'
        
        return {
            'status': overall_status,
            'healthy_count': len(healthy_checks),
            'unhealthy_count': len(unhealthy_checks),
            'checks': [asdict(check) for check in self.health_checks.values()]
        }
    
    async def export_metrics(self, format_type: str = 'json') -> str:
        """Export metrics in various formats"""
        if format_type == 'json':
            return json.dumps({
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': self.get_metrics_summary(),
                'alerts': self.get_alerts_summary(),
                'health': self.get_health_status()
            }, indent=2, default=str)
        
        elif format_type == 'prometheus':
            # Export in Prometheus format
            lines = []
            for name, metric in self.metrics.items():
                current_value = metric.get_current_value()
                lines.append(f'# HELP {name} {metric.description}')
                lines.append(f'# TYPE {name} {metric.type.value}')
                lines.append(f'{name} {current_value}')
            
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")

# Global monitoring instance
monitoring = MonitoringSystem()

# Alert handlers
async def log_alert_handler(alert: Alert):
    """Log alert to file"""
    log_entry = {
        'timestamp': alert.timestamp.isoformat(),
        'level': alert.level.value,
        'title': alert.title,
        'message': alert.message,
        'metric': alert.metric_name,
        'value': alert.current_value,
        'threshold': alert.threshold
    }
    
    try:
        async with aiofiles.open('logs/alerts.json', 'a') as f:
            await f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        logger.error(f"Error logging alert: {e}")

def console_alert_handler(alert: Alert):
    """Print alert to console"""
    level_colors = {
        AlertLevel.INFO: '\033[94m',      # Blue
        AlertLevel.WARNING: '\033[93m',   # Yellow
        AlertLevel.ERROR: '\033[91m',     # Red
        AlertLevel.CRITICAL: '\033[95m'   # Magenta
    }
    
    color = level_colors.get(alert.level, '\033[0m')
    reset = '\033[0m'
    
    print(f"{color}[{alert.level.value.upper()}] {alert.title}: {alert.message}{reset}")
    print(f"  Metric: {alert.metric_name} = {alert.current_value} (threshold: {alert.threshold})")

# Register default alert handlers
monitoring.add_alert_handler(log_alert_handler)
monitoring.add_alert_handler(console_alert_handler)

# Convenience functions
async def init_monitoring():
    """Initialize monitoring system"""
    await monitoring.start()

async def stop_monitoring():
    """Stop monitoring system"""
    await monitoring.stop()

def record_request(duration_ms: float, status_code: int, path: str):
    """Record HTTP request metrics"""
    monitoring.increment_counter('request_count')
    monitoring.record_timer('request_duration', duration_ms)
    
    if status_code >= 400:
        monitoring.increment_counter('error_count')

def record_db_query(duration_ms: float, query_type: str = None):
    """Record database query metrics"""
    monitoring.increment_counter('db_query_count')
    monitoring.record_timer('db_query_duration', duration_ms)

def record_cache_operation(hit: bool, operation: str = 'get'):
    """Record cache operation metrics"""
    if hit:
        monitoring.increment_counter('cache_hits')
    else:
        monitoring.increment_counter('cache_misses')

# Context manager for timing operations
class Timer:
    def __init__(self, metric_name: str, tags: Dict[str, str] = None):
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.perf_counter() - self.start_time) * 1000
            monitoring.record_timer(self.metric_name, duration_ms, self.tags)

# Decorator for timing functions
def timed_operation(metric_name: str, tags: Dict[str, str] = None):
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with Timer(metric_name, tags):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with Timer(metric_name, tags):
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator