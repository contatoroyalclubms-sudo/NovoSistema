"""
Ultra-Performance Async Processing System
Sistema Universal de Gestão de Eventos - Enterprise Scale
Target: Sub-second task processing, 100,000+ tasks/hour, fault-tolerant
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import json
import pickle
import uuid
from functools import wraps
import inspect
import time

from celery import Celery, Task
from celery.result import AsyncResult
from celery.exceptions import Retry, WorkerLostError
import redis.asyncio as redis
from redis.asyncio import Redis
from kombu import Queue, Exchange
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Performance Metrics
TASK_COUNTER = Counter('celery_tasks_total', 'Total Celery tasks', ['task_name', 'status'])
TASK_DURATION = Histogram('celery_task_duration_seconds', 'Task execution duration', ['task_name'])
TASK_QUEUE_SIZE = Gauge('celery_queue_size', 'Queue size', ['queue_name'])
TASK_ACTIVE_WORKERS = Gauge('celery_active_workers', 'Active workers', ['worker_type'])
TASK_RETRIES = Counter('celery_task_retries_total', 'Task retries', ['task_name', 'reason'])

class TaskPriority(Enum):
    """Task priority levels for queue routing"""
    CRITICAL = "critical"      # Real-time operations (< 100ms)
    HIGH = "high"             # User-facing operations (< 1s)
    NORMAL = "normal"         # Background operations (< 10s)
    LOW = "low"              # Batch operations (< 60s)

@dataclass
class TaskConfig:
    """Ultra-performance task configuration"""
    # Redis Configuration
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 1
    redis_password: Optional[str] = None
    
    # Celery Configuration
    broker_pool_limit: int = 100
    result_backend_pool_limit: int = 100
    task_serializer: str = "pickle"  # Faster than JSON for complex objects
    result_serializer: str = "pickle"
    task_compression: str = "gzip"
    result_compression: str = "gzip"
    
    # Performance Settings
    worker_prefetch_multiplier: int = 4  # Optimize for high-throughput
    task_acks_late: bool = True  # Reliability over speed
    worker_max_tasks_per_child: int = 1000  # Prevent memory leaks
    task_soft_time_limit: int = 300  # 5 minutes
    task_time_limit: int = 600  # 10 minutes
    
    # Queue Configuration
    task_routes: Dict[str, str] = None
    queue_priorities: Dict[str, int] = None
    
    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = True

class UltraPerformanceTaskMonitor(Task):
    """Custom Celery task class with ultra-performance monitoring"""
    
    def __call__(self, *args, **kwargs):
        start_time = time.time()
        task_name = self.name
        
        try:
            # Record task start
            if TaskConfig().enable_metrics:
                TASK_COUNTER.labels(task_name=task_name, status='started').inc()
                TASK_ACTIVE_WORKERS.labels(worker_type=self.queue or 'default').inc()
            
            # Execute task
            result = super().__call__(*args, **kwargs)
            
            # Record success
            duration = time.time() - start_time
            if TaskConfig().enable_metrics:
                TASK_COUNTER.labels(task_name=task_name, status='success').inc()
                TASK_DURATION.labels(task_name=task_name).observe(duration)
            
            logger.info(f"✅ Task {task_name} completed in {duration:.3f}s")
            return result
            
        except Exception as e:
            # Record failure
            duration = time.time() - start_time
            if TaskConfig().enable_metrics:
                TASK_COUNTER.labels(task_name=task_name, status='failure').inc()
                TASK_DURATION.labels(task_name=task_name).observe(duration)
            
            logger.error(f"❌ Task {task_name} failed after {duration:.3f}s: {str(e)}")
            raise
        finally:
            if TaskConfig().enable_metrics:
                TASK_ACTIVE_WORKERS.labels(worker_type=self.queue or 'default').dec()

class UltraPerformanceCelery:
    """Ultra-performance Celery configuration for enterprise scale"""
    
    def __init__(self, config: TaskConfig = None):
        self.config = config or TaskConfig()
        self.app: Optional[Celery] = None
        self.redis_client: Optional[Redis] = None
        self._task_registry = {}
        
    def create_celery_app(self, app_name: str = "eventos_ultra_performance") -> Celery:
        """Create optimized Celery application"""
        
        # Redis broker URL
        broker_url = f"redis://:{self.config.redis_password}@{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}" if self.config.redis_password else f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}"
        
        # Create Celery app with ultra-performance settings
        self.app = Celery(
            app_name,
            broker=broker_url,
            backend=broker_url,
            task_cls=UltraPerformanceTaskMonitor
        )
        
        # Ultra-performance configuration
        self.app.conf.update(
            # Message Routing and Serialization
            task_serializer=self.config.task_serializer,
            result_serializer=self.config.result_serializer,
            accept_content=['pickle', 'json'],  # Support both for compatibility
            task_compression=self.config.task_compression,
            result_compression=self.config.result_compression,
            
            # Connection Pool Settings
            broker_pool_limit=self.config.broker_pool_limit,
            broker_connection_retry_on_startup=True,
            broker_connection_retry=True,
            
            # Worker Performance
            worker_prefetch_multiplier=self.config.worker_prefetch_multiplier,
            worker_max_tasks_per_child=self.config.worker_max_tasks_per_child,
            worker_disable_rate_limits=True,  # Remove rate limiting for performance
            
            # Task Execution Settings
            task_acks_late=self.config.task_acks_late,
            task_reject_on_worker_lost=True,
            task_soft_time_limit=self.config.task_soft_time_limit,
            task_time_limit=self.config.task_time_limit,
            
            # Result Backend Settings
            result_expires=3600,  # 1 hour expiration
            result_persistent=True,
            result_backend_transport_options={
                'master_name': 'mymaster',
                'visibility_timeout': 3600,
            },
            
            # Queue Configuration
            task_routes=self._create_task_routes(),
            task_default_queue='normal',
            task_queues=self._create_queues(),
            
            # Optimization Settings
            task_ignore_result=False,  # We want results for monitoring
            task_store_eager_result=True,
            worker_send_task_events=True,  # Enable monitoring
            task_send_sent_event=True,
            
            # Timezone
            timezone='UTC',
            enable_utc=True,
        )
        
        # Setup task autodiscovery
        self.app.autodiscover_tasks([
            'app.tasks.event_tasks',
            'app.tasks.user_tasks', 
            'app.tasks.notification_tasks',
            'app.tasks.payment_tasks',
            'app.tasks.analytics_tasks'
        ])
        
        return self.app
    
    def _create_task_routes(self) -> Dict[str, Dict[str, str]]:
        """Create intelligent task routing based on priority"""
        return {
            # Critical tasks - Real-time operations
            'app.tasks.event_tasks.process_checkin': {'queue': 'critical'},
            'app.tasks.payment_tasks.process_payment': {'queue': 'critical'},
            'app.tasks.notification_tasks.send_real_time_notification': {'queue': 'critical'},
            
            # High priority tasks - User-facing operations
            'app.tasks.user_tasks.send_welcome_email': {'queue': 'high'},
            'app.tasks.event_tasks.generate_qr_code': {'queue': 'high'},
            'app.tasks.notification_tasks.send_email': {'queue': 'high'},
            
            # Normal priority tasks - Background operations
            'app.tasks.analytics_tasks.update_event_stats': {'queue': 'normal'},
            'app.tasks.user_tasks.sync_user_data': {'queue': 'normal'},
            
            # Low priority tasks - Batch operations
            'app.tasks.analytics_tasks.generate_daily_report': {'queue': 'low'},
            'app.tasks.analytics_tasks.cleanup_old_data': {'queue': 'low'},
        }
    
    def _create_queues(self) -> List[Queue]:
        """Create optimized queues with different priorities"""
        default_exchange = Exchange('default', type='direct')
        
        return [
            # Critical queue - Highest priority, dedicated workers
            Queue('critical', 
                  exchange=default_exchange,
                  routing_key='critical',
                  queue_arguments={'x-max-priority': 10}),
            
            # High priority queue
            Queue('high',
                  exchange=default_exchange, 
                  routing_key='high',
                  queue_arguments={'x-max-priority': 7}),
            
            # Normal priority queue (default)
            Queue('normal',
                  exchange=default_exchange,
                  routing_key='normal', 
                  queue_arguments={'x-max-priority': 5}),
            
            # Low priority queue - Batch processing
            Queue('low',
                  exchange=default_exchange,
                  routing_key='low',
                  queue_arguments={'x-max-priority': 1}),
        ]
    
    async def initialize_redis(self):
        """Initialize Redis connection for task monitoring"""
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=False,
            max_connections=50
        )
        
        try:
            await self.redis_client.ping()
            logger.info("✅ Redis connection for async processing initialized")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get detailed queue statistics"""
        if not self.redis_client:
            return {"error": "Redis not initialized"}
        
        stats = {}
        queues = ['critical', 'high', 'normal', 'low']
        
        for queue in queues:
            try:
                # Get queue length
                queue_key = f"celery:{queue}"
                length = await self.redis_client.llen(queue_key)
                
                # Update Prometheus metrics
                if self.config.enable_metrics:
                    TASK_QUEUE_SIZE.labels(queue_name=queue).set(length)
                
                stats[queue] = {
                    "length": length,
                    "priority": self._get_queue_priority(queue)
                }
                
            except Exception as e:
                stats[queue] = {"error": str(e)}
        
        return stats
    
    def _get_queue_priority(self, queue_name: str) -> int:
        """Get queue priority level"""
        priorities = {
            'critical': 10,
            'high': 7,
            'normal': 5,
            'low': 1
        }
        return priorities.get(queue_name, 5)
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for async processing system"""
        try:
            health_status = {
                "celery_app": "unknown",
                "redis_connection": "unknown", 
                "queues": {},
                "workers": {},
                "overall_status": "unknown"
            }
            
            # Check Celery app
            if self.app:
                health_status["celery_app"] = "initialized"
            
            # Check Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis_connection"] = "connected"
            
            # Check queue stats
            health_status["queues"] = await self.get_queue_stats()
            
            # Check active workers (if inspect is available)
            try:
                inspect = self.app.control.inspect()
                active_workers = inspect.active()
                health_status["workers"] = {
                    "total": len(active_workers) if active_workers else 0,
                    "details": active_workers or {}
                }
            except Exception as e:
                health_status["workers"] = {"error": str(e)}
            
            # Determine overall status
            redis_ok = health_status["redis_connection"] == "connected"
            celery_ok = health_status["celery_app"] == "initialized"
            
            if redis_ok and celery_ok:
                health_status["overall_status"] = "healthy"
            else:
                health_status["overall_status"] = "unhealthy"
            
            return health_status
            
        except Exception as e:
            return {
                "overall_status": "error",
                "error": str(e)
            }

# Global ultra-performance Celery instance
ultra_celery = UltraPerformanceCelery()

# Task decorators for different priorities
def critical_task(bind=True, **kwargs):
    """Decorator for critical priority tasks (< 100ms target)"""
    def decorator(func):
        task_name = f"{func.__module__}.{func.__name__}"
        return ultra_celery.app.task(
            bind=bind,
            name=task_name,
            queue='critical',
            priority=10,
            **kwargs
        )(func)
    return decorator

def high_priority_task(bind=True, **kwargs):
    """Decorator for high priority tasks (< 1s target)"""
    def decorator(func):
        task_name = f"{func.__module__}.{func.__name__}"
        return ultra_celery.app.task(
            bind=bind,
            name=task_name,
            queue='high',
            priority=7,
            **kwargs
        )(func)
    return decorator

def normal_task(bind=True, **kwargs):
    """Decorator for normal priority tasks (< 10s target)"""
    def decorator(func):
        task_name = f"{func.__module__}.{func.__name__}"
        return ultra_celery.app.task(
            bind=bind,
            name=task_name,
            queue='normal',
            priority=5,
            **kwargs
        )(func)
    return decorator

def low_priority_task(bind=True, **kwargs):
    """Decorator for low priority tasks (< 60s target)"""
    def decorator(func):
        task_name = f"{func.__module__}.{func.__name__}"
        return ultra_celery.app.task(
            bind=bind,
            name=task_name,
            queue='low',
            priority=1,
            **kwargs
        )(func)
    return decorator

# Task execution utilities
class TaskManager:
    """Manage task execution with ultra-performance features"""
    
    def __init__(self, celery_app: Celery):
        self.app = celery_app
        self.redis_client = ultra_celery.redis_client
    
    async def execute_task_chain(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """Execute a chain of tasks with dependency management"""
        results = []
        
        for task_config in tasks:
            task_name = task_config['task']
            task_args = task_config.get('args', [])
            task_kwargs = task_config.get('kwargs', {})
            depends_on = task_config.get('depends_on', [])
            
            # Wait for dependencies
            if depends_on:
                for dep_idx in depends_on:
                    if dep_idx < len(results):
                        await results[dep_idx].get()
            
            # Execute task
            task = self.app.send_task(task_name, args=task_args, kwargs=task_kwargs)
            results.append(task)
        
        return results
    
    async def execute_parallel_tasks(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """Execute multiple tasks in parallel"""
        task_objects = []
        
        for task_config in tasks:
            task_name = task_config['task']
            task_args = task_config.get('args', [])
            task_kwargs = task_config.get('kwargs', {})
            
            task = self.app.send_task(task_name, args=task_args, kwargs=task_kwargs)
            task_objects.append(task)
        
        # Wait for all tasks to complete
        results = []
        for task in task_objects:
            result = await asyncio.get_event_loop().run_in_executor(
                None, task.get, 30  # 30 second timeout
            )
            results.append(result)
        
        return results
    
    async def schedule_recurring_task(
        self, 
        task_name: str, 
        schedule: str,
        args: List = None,
        kwargs: Dict = None
    ):
        """Schedule recurring task using Celery Beat"""
        # This would integrate with Celery Beat for scheduled tasks
        # Implementation depends on specific scheduling needs
        pass
    
    def get_task_result(self, task_id: str) -> AsyncResult:
        """Get task result by ID"""
        return AsyncResult(task_id, app=self.app)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        try:
            self.app.control.revoke(task_id, terminate=True)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False

# Batch processing utilities
class BatchProcessor:
    """Ultra-performance batch processing for large datasets"""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.app = ultra_celery.app
    
    async def process_in_batches(
        self, 
        data: List[Any],
        task_name: str,
        batch_size: Optional[int] = None
    ) -> List[AsyncResult]:
        """Process large dataset in optimized batches"""
        batch_size = batch_size or self.batch_size
        results = []
        
        # Split data into batches
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            # Submit batch as single task
            task = self.app.send_task(
                task_name,
                args=[batch],
                queue='low'  # Batch processing is usually low priority
            )
            results.append(task)
        
        return results

# Performance monitoring and alerting
class PerformanceMonitor:
    """Monitor async processing performance"""
    
    def __init__(self):
        self.redis_client = ultra_celery.redis_client
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            "queue_stats": await ultra_celery.get_queue_stats(),
            "worker_stats": await self._get_worker_stats(),
            "task_stats": await self._get_task_stats(),
            "system_health": await ultra_celery.health_check()
        }
    
    async def _get_worker_stats(self) -> Dict[str, Any]:
        """Get worker performance statistics"""
        try:
            inspect = ultra_celery.app.control.inspect()
            stats = inspect.stats()
            return stats or {}
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_task_stats(self) -> Dict[str, Any]:
        """Get task execution statistics"""
        # This would aggregate task execution metrics
        # from Prometheus or custom storage
        return {
            "total_tasks_processed": "N/A",  # Would come from metrics
            "average_task_duration": "N/A",
            "task_failure_rate": "N/A"
        }

# Global instances
task_manager = TaskManager(ultra_celery.app) if ultra_celery.app else None
batch_processor = BatchProcessor()
performance_monitor = PerformanceMonitor()

async def init_async_processing():
    """Initialize ultra-performance async processing system"""
    logger.info("🚀 Initializing Ultra-Performance Async Processing System...")
    
    # Create Celery app
    ultra_celery.create_celery_app()
    
    # Initialize Redis
    await ultra_celery.initialize_redis()
    
    # Update global instances
    global task_manager
    task_manager = TaskManager(ultra_celery.app)
    
    logger.info("✅ Ultra-Performance Async Processing System initialized")

async def close_async_processing():
    """Gracefully close async processing connections"""
    if ultra_celery.redis_client:
        await ultra_celery.redis_client.close()
    
    logger.info("🔚 Ultra-Performance Async Processing connections closed")

# Export the Celery app for worker startup
celery_app = ultra_celery.app