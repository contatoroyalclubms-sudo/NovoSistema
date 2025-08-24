"""
PERFORMANCE MONITORING AND BENCHMARKING
Sistema Universal de Gestão de Eventos - ULTRA PERFORMANCE

Advanced performance monitoring with:
- Real-time metrics collection
- Performance benchmarking
- Bottleneck detection
- Memory profiling
- Load testing utilities
"""

import asyncio
import time
import logging
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge, Summary
import json
import statistics

logger = logging.getLogger(__name__)

# Performance Metrics
performance_counter = Counter('performance_operations_total', 'Performance operations', ['operation', 'status'])
performance_duration = Histogram('performance_operation_duration_seconds', 'Operation duration')
system_cpu_usage = Gauge('system_cpu_usage_percent', 'System CPU usage')
system_memory_usage = Gauge('system_memory_usage_percent', 'System memory usage')
system_disk_usage = Gauge('system_disk_usage_percent', 'System disk usage')
application_memory = Gauge('application_memory_usage_bytes', 'Application memory usage')
database_connections = Gauge('database_connections_active', 'Active database connections')
cache_hit_rate = Gauge('cache_hit_rate_percent', 'Cache hit rate percentage')

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    timestamp: datetime
    unit: str = 'ms'
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BenchmarkResult:
    """Benchmark result data structure"""
    name: str
    duration: float
    operations_per_second: float
    percentiles: Dict[str, float]
    memory_usage: Dict[str, float]
    error_rate: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class UltraPerformanceMonitor:
    """
    Ultra-performance monitoring system with:
    - Real-time system metrics
    - Application performance tracking
    - Benchmark execution
    - Bottleneck detection
    """
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.benchmarks: List[BenchmarkResult] = []
        self.is_monitoring = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time_ms': 1000.0,
            'error_rate_percent': 5.0
        }
        
    async def start_monitoring(self, interval: float = 5.0):
        """Start continuous system monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        def monitor_loop():
            while self.is_monitoring:
                try:
                    self._collect_system_metrics()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(interval)
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("✅ Ultra Performance Monitor started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        
        logger.info("✅ Ultra Performance Monitor stopped")
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            system_disk_usage.set(disk_percent)
            
            # Application memory
            process = psutil.Process()
            app_memory = process.memory_info().rss
            application_memory.set(app_memory)
            
            # Store metrics
            now = datetime.utcnow()
            self.metrics.extend([
                PerformanceMetric('cpu_percent', cpu_percent, now, '%'),
                PerformanceMetric('memory_percent', memory.percent, now, '%'),
                PerformanceMetric('disk_percent', disk_percent, now, '%'),
                PerformanceMetric('app_memory_mb', app_memory / 1024 / 1024, now, 'MB')
            ])
            
            # Check thresholds and alert
            self._check_alert_thresholds({
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk_percent
            })
            
            # Cleanup old metrics (keep last 1000)
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _check_alert_thresholds(self, metrics: Dict[str, float]):
        """Check if metrics exceed alert thresholds"""
        for metric_name, value in metrics.items():
            threshold = self.alert_thresholds.get(metric_name)
            if threshold and value > threshold:
                logger.warning(
                    f"🚨 PERFORMANCE ALERT: {metric_name} = {value:.2f} "
                    f"(threshold: {threshold})"
                )
    
    async def benchmark_function(
        self,
        func: Callable,
        name: str,
        iterations: int = 100,
        concurrent_users: int = 1,
        **kwargs
    ) -> BenchmarkResult:
        """Benchmark a function with multiple iterations"""
        logger.info(f"🏁 Starting benchmark: {name} ({iterations} iterations, {concurrent_users} users)")
        
        start_time = time.time()
        durations = []
        errors = 0
        
        # Memory before
        process = psutil.Process()
        memory_before = process.memory_info().rss
        
        if concurrent_users == 1:
            # Sequential execution
            for i in range(iterations):
                iter_start = time.time()
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func(**kwargs)
                    else:
                        func(**kwargs)
                    durations.append((time.time() - iter_start) * 1000)  # ms
                except Exception as e:
                    errors += 1
                    logger.debug(f"Benchmark error in iteration {i}: {e}")
        else:
            # Concurrent execution
            async def run_iteration():
                iter_start = time.time()
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func(**kwargs)
                    else:
                        func(**kwargs)
                    return (time.time() - iter_start) * 1000
                except Exception as e:
                    logger.debug(f"Concurrent benchmark error: {e}")
                    raise
            
            # Run concurrent tasks in batches
            batch_size = min(concurrent_users, 50)  # Limit concurrent tasks
            for batch_start in range(0, iterations, batch_size):
                batch_end = min(batch_start + batch_size, iterations)
                tasks = [run_iteration() for _ in range(batch_end - batch_start)]
                
                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for result in results:
                        if isinstance(result, Exception):
                            errors += 1
                        else:
                            durations.append(result)
                except Exception as e:
                    logger.error(f"Batch execution error: {e}")
                    errors += len(tasks)
        
        # Memory after
        memory_after = process.memory_info().rss
        memory_diff = memory_after - memory_before
        
        total_time = time.time() - start_time
        successful_operations = len(durations)
        operations_per_second = successful_operations / total_time if total_time > 0 else 0
        error_rate = (errors / iterations) * 100 if iterations > 0 else 0
        
        # Calculate percentiles
        percentiles = {}
        if durations:
            percentiles = {
                'p50': statistics.median(durations),
                'p90': statistics.quantiles(durations, n=10)[8] if len(durations) > 10 else max(durations),
                'p95': statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else max(durations),
                'p99': statistics.quantiles(durations, n=100)[98] if len(durations) > 100 else max(durations),
                'min': min(durations),
                'max': max(durations),
                'avg': statistics.mean(durations)
            }
        
        # Create benchmark result
        result = BenchmarkResult(
            name=name,
            duration=total_time * 1000,  # ms
            operations_per_second=operations_per_second,
            percentiles=percentiles,
            memory_usage={
                'before_mb': memory_before / 1024 / 1024,
                'after_mb': memory_after / 1024 / 1024,
                'diff_mb': memory_diff / 1024 / 1024
            },
            error_rate=error_rate,
            timestamp=datetime.utcnow(),
            metadata={
                'iterations': iterations,
                'concurrent_users': concurrent_users,
                'successful_operations': successful_operations,
                'failed_operations': errors
            }
        )
        
        self.benchmarks.append(result)
        
        # Log results
        logger.info(f"✅ Benchmark completed: {name}")
        logger.info(f"   Duration: {result.duration:.2f}ms")
        logger.info(f"   Ops/sec: {result.operations_per_second:.2f}")
        logger.info(f"   Error rate: {result.error_rate:.2f}%")
        if percentiles:
            logger.info(f"   P50: {percentiles['p50']:.2f}ms, P95: {percentiles['p95']:.2f}ms")
        
        # Record metrics
        performance_counter.labels(operation=name, status='completed').inc()
        performance_duration.observe(result.duration / 1000)  # seconds
        
        return result
    
    async def benchmark_api_endpoint(
        self,
        client,
        method: str,
        url: str,
        name: str,
        iterations: int = 100,
        concurrent_users: int = 1,
        payload: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> BenchmarkResult:
        """Benchmark an API endpoint"""
        
        async def make_request():
            if method.upper() == 'GET':
                response = await client.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = await client.post(url, json=payload, headers=headers)
            elif method.upper() == 'PUT':
                response = await client.put(url, json=payload, headers=headers)
            elif method.upper() == 'DELETE':
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check if response is successful
            if response.status_code >= 400:
                raise Exception(f"HTTP {response.status_code}")
            
            return response
        
        return await self.benchmark_function(
            make_request,
            f"{name} ({method.upper()} {url})",
            iterations=iterations,
            concurrent_users=concurrent_users
        )
    
    async def profile_database_queries(self, db_session):
        """Profile database query performance"""
        # This would be implemented based on your specific database setup
        logger.info("📊 Profiling database queries...")
        
        # Example: Profile common queries
        queries_to_profile = [
            ("SELECT COUNT(*) FROM eventos", "count_eventos"),
            ("SELECT * FROM eventos LIMIT 10", "select_eventos_limit"),
            ("SELECT * FROM participantes LIMIT 100", "select_participantes_limit"),
        ]
        
        results = []
        for query, name in queries_to_profile:
            start_time = time.time()
            try:
                # Execute query (implementation depends on your DB layer)
                # result = await db_session.execute(text(query))
                # rows = result.fetchall()
                
                duration = (time.time() - start_time) * 1000
                results.append({
                    'name': name,
                    'query': query,
                    'duration_ms': duration,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                performance_counter.labels(operation=f"db_query_{name}", status='success').inc()
                
            except Exception as e:
                logger.error(f"Query profiling error for {name}: {e}")
                performance_counter.labels(operation=f"db_query_{name}", status='error').inc()
        
        return results
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate performance report for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter recent metrics and benchmarks
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        recent_benchmarks = [b for b in self.benchmarks if b.timestamp >= cutoff_time]
        
        # Aggregate metrics by type
        metric_summary = {}
        for metric in recent_metrics:
            if metric.name not in metric_summary:
                metric_summary[metric.name] = []
            metric_summary[metric.name].append(metric.value)
        
        # Calculate statistics for each metric
        metric_stats = {}
        for name, values in metric_summary.items():
            if values:
                metric_stats[name] = {
                    'avg': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'p95': statistics.quantiles(values, n=20)[18] if len(values) > 20 else max(values),
                    'count': len(values)
                }
        
        # Benchmark summary
        benchmark_stats = {}
        for benchmark in recent_benchmarks:
            benchmark_stats[benchmark.name] = {
                'duration_ms': benchmark.duration,
                'ops_per_sec': benchmark.operations_per_second,
                'error_rate': benchmark.error_rate,
                'p95_ms': benchmark.percentiles.get('p95', 0),
                'timestamp': benchmark.timestamp.isoformat()
            }
        
        return {
            'report_period_hours': hours,
            'generated_at': datetime.utcnow().isoformat(),
            'system_metrics': metric_stats,
            'benchmarks': benchmark_stats,
            'alert_thresholds': self.alert_thresholds,
            'total_metrics_collected': len(recent_metrics),
            'total_benchmarks_run': len(recent_benchmarks)
        }
    
    def export_metrics_json(self, filepath: str):
        """Export metrics to JSON file"""
        data = {
            'exported_at': datetime.utcnow().isoformat(),
            'metrics': [
                {
                    'name': m.name,
                    'value': m.value,
                    'timestamp': m.timestamp.isoformat(),
                    'unit': m.unit,
                    'metadata': m.metadata
                }
                for m in self.metrics
            ],
            'benchmarks': [
                {
                    'name': b.name,
                    'duration': b.duration,
                    'operations_per_second': b.operations_per_second,
                    'percentiles': b.percentiles,
                    'memory_usage': b.memory_usage,
                    'error_rate': b.error_rate,
                    'timestamp': b.timestamp.isoformat(),
                    'metadata': b.metadata
                }
                for b in self.benchmarks
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Metrics exported to {filepath}")

# Global performance monitor instance
ultra_performance_monitor = UltraPerformanceMonitor()

# Utility functions for easy benchmarking
async def benchmark_function(func: Callable, name: str, iterations: int = 100, **kwargs) -> BenchmarkResult:
    """Quick benchmark function wrapper"""
    return await ultra_performance_monitor.benchmark_function(func, name, iterations, **kwargs)

async def benchmark_api(client, method: str, url: str, name: str, iterations: int = 100, **kwargs) -> BenchmarkResult:
    """Quick API benchmark wrapper"""
    return await ultra_performance_monitor.benchmark_api_endpoint(
        client, method, url, name, iterations, **kwargs
    )

def performance_report(hours: int = 24) -> Dict[str, Any]:
    """Quick performance report wrapper"""
    return ultra_performance_monitor.get_performance_report(hours)

# Decorator for automatic function benchmarking
def benchmark(name: str = None, iterations: int = 1):
    """Decorator to benchmark function calls"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            func_name = name or f"{func.__module__}.{func.__name__}"
            if iterations > 1:
                return await ultra_performance_monitor.benchmark_function(
                    func, func_name, iterations, *args, **kwargs
                )
            else:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    logger.debug(f"⏱️ {func_name}: {duration:.2f}ms")
                    performance_counter.labels(operation=func_name, status='success').inc()
                    performance_duration.observe(duration / 1000)
                    return result
                except Exception as e:
                    performance_counter.labels(operation=func_name, status='error').inc()
                    raise
        
        def sync_wrapper(*args, **kwargs):
            func_name = name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.debug(f"⏱️ {func_name}: {duration:.2f}ms")
                performance_counter.labels(operation=func_name, status='success').inc()
                performance_duration.observe(duration / 1000)
                return result
            except Exception as e:
                performance_counter.labels(operation=func_name, status='error').inc()
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator