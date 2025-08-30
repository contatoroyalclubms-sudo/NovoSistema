"""
Ultra-High Performance Async Task Processor
Enterprise-grade background task processing with Celery and Redis
Target: Sub-100ms critical tasks, fault tolerance, intelligent routing
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

from celery import Celery
from celery.result import AsyncResult
from kombu import Queue
import redis

logger = logging.getLogger(__name__)

class TaskPriority(str, Enum):
    CRITICAL = "critical"    # <100ms target
    HIGH = "high"           # <1s target
    NORMAL = "normal"       # <5s target
    LOW = "low"            # <30s target

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"

@dataclass
class UltraTask:
    """High-performance task wrapper"""
    id: str
    name: str
    priority: TaskPriority
    payload: Dict[str, Any]
    created_at: datetime
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 300     # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UltraTask':
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['priority'] = TaskPriority(data['priority'])
        return cls(**data)

class UltraAsyncProcessor:
    """Enterprise async task processor"""
    
    def __init__(self):
        self.celery_app = None
        self.redis_client = None
        self.task_registry: Dict[str, Callable] = {}
        self.stats = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'tasks_retried': 0,
            'average_processing_time': 0,
            'critical_tasks_processed': 0,
            'start_time': datetime.now()
        }
        
    def init_processor(self, redis_url: str = "redis://localhost:6379/1"):
        """Initialize ultra async processor"""
        try:
            # Configure Celery with optimized settings
            self.celery_app = Celery(
                'ultra_events_processor',
                broker=redis_url,
                backend=redis_url,
                include=['app.tasks.ultra_async_processor']
            )
            
            # Ultra performance configuration
            self.celery_app.conf.update(
                # Task routing by priority
                task_routes={
                    'ultra_critical_task': {'queue': 'critical'},
                    'ultra_high_task': {'queue': 'high'},
                    'ultra_normal_task': {'queue': 'normal'},
                    'ultra_low_task': {'queue': 'low'}
                },
                
                # Queue configuration with priority
                task_queues=(
                    Queue('critical', priority=10),
                    Queue('high', priority=7),
                    Queue('normal', priority=5),
                    Queue('low', priority=1),
                ),
                
                # Performance optimizations
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                
                # Connection settings
                broker_transport_options={
                    'priority_steps': list(range(10)),
                    'sep': ':',
                    'queue_order_strategy': 'priority',
                },
                
                # Task execution settings
                task_always_eager=False,
                task_eager_propagates=True,
                task_ignore_result=False,
                task_store_errors_even_if_ignored=True,
                
                # Worker settings
                worker_prefetch_multiplier=1,
                worker_max_tasks_per_child=1000,
                worker_disable_rate_limits=True,
                
                # Result backend settings
                result_expires=3600,  # 1 hour
                result_backend_transport_options={
                    'retry_policy': {'timeout': 5.0}
                }
            )
            
            # Redis client for direct operations
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            
            # Register task handlers
            self._register_default_tasks()
            
            logger.info("✅ Ultra Async Processor initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Async processor initialization failed: {e}")
            return False
    
    def _register_default_tasks(self):
        """Register default high-performance task handlers"""
        
        @self.celery_app.task(name='ultra_critical_task', bind=True)
        def ultra_critical_task(self, task_data: Dict[str, Any]):
            """Handle critical priority tasks (<100ms target)"""
            return self._execute_task_with_monitoring(self, task_data, TaskPriority.CRITICAL)
        
        @self.celery_app.task(name='ultra_high_task', bind=True)
        def ultra_high_task(self, task_data: Dict[str, Any]):
            """Handle high priority tasks (<1s target)"""
            return self._execute_task_with_monitoring(self, task_data, TaskPriority.HIGH)
        
        @self.celery_app.task(name='ultra_normal_task', bind=True)
        def ultra_normal_task(self, task_data: Dict[str, Any]):
            """Handle normal priority tasks (<5s target)"""
            return self._execute_task_with_monitoring(self, task_data, TaskPriority.NORMAL)
        
        @self.celery_app.task(name='ultra_low_task', bind=True)
        def ultra_low_task(self, task_data: Dict[str, Any]):
            """Handle low priority tasks (<30s target)"""
            return self._execute_task_with_monitoring(self, task_data, TaskPriority.LOW)
    
    def _execute_task_with_monitoring(self, celery_task, task_data: Dict[str, Any], priority: TaskPriority):
        """Execute task with comprehensive monitoring"""
        start_time = time.perf_counter()
        task_id = celery_task.request.id
        
        try:
            # Parse task data
            ultra_task = UltraTask.from_dict(task_data)
            
            # Find and execute task handler
            if ultra_task.name in self.task_registry:
                handler = self.task_registry[ultra_task.name]
                result = handler(ultra_task.payload)
                
                # Update statistics
                processing_time = (time.perf_counter() - start_time) * 1000
                self._update_task_stats(priority, processing_time, success=True)
                
                # Log performance for critical tasks
                if priority == TaskPriority.CRITICAL and processing_time > 100:
                    logger.warning(f"Critical task exceeded target: {processing_time:.2f}ms")
                
                return {
                    'status': 'success',
                    'result': result,
                    'processing_time_ms': processing_time,
                    'task_id': task_id
                }
                
            else:
                raise ValueError(f"Task handler not found: {ultra_task.name}")
                
        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            self._update_task_stats(priority, processing_time, success=False)
            
            logger.error(f"Task execution failed: {e}")
            
            # Retry logic
            if celery_task.request.retries < ultra_task.max_retries:
                self.stats['tasks_retried'] += 1
                raise celery_task.retry(countdown=ultra_task.retry_delay, exc=e)
            
            return {
                'status': 'failure',
                'error': str(e),
                'processing_time_ms': processing_time,
                'task_id': task_id
            }
    
    def register_task_handler(self, task_name: str, handler: Callable):
        """Register custom task handler"""
        self.task_registry[task_name] = handler
        logger.info(f"Task handler registered: {task_name}")
    
    async def submit_task(self, task_name: str, payload: Dict[str, Any], 
                         priority: TaskPriority = TaskPriority.NORMAL,
                         max_retries: int = 3, timeout: int = 300) -> str:
        """Submit task for async processing"""
        if not self.celery_app:
            raise RuntimeError("Async processor not initialized")
        
        # Create ultra task
        ultra_task = UltraTask(
            id=str(uuid.uuid4()),
            name=task_name,
            priority=priority,
            payload=payload,
            created_at=datetime.now(),
            max_retries=max_retries,
            timeout=timeout
        )
        
        # Select appropriate Celery task based on priority
        task_mapping = {
            TaskPriority.CRITICAL: 'ultra_critical_task',
            TaskPriority.HIGH: 'ultra_high_task',
            TaskPriority.NORMAL: 'ultra_normal_task',
            TaskPriority.LOW: 'ultra_low_task'
        }
        
        celery_task_name = task_mapping[priority]
        
        # Submit to Celery
        celery_result = self.celery_app.send_task(
            celery_task_name,
            args=[ultra_task.to_dict()],
            task_id=ultra_task.id,
            countdown=0,
            expires=timeout
        )
        
        self.stats['tasks_submitted'] += 1
        
        # Store task metadata in Redis for fast lookups
        await self._store_task_metadata(ultra_task)
        
        logger.info(f"Task submitted: {ultra_task.id} ({priority}) - {task_name}")
        return ultra_task.id
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task execution result"""
        if not self.celery_app:
            return None
        
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            
            return {
                'id': task_id,
                'status': result.status,
                'result': result.result,
                'ready': result.ready(),
                'successful': result.successful() if result.ready() else None,
                'failed': result.failed() if result.ready() else None,
                'traceback': result.traceback if result.failed() else None
            }
            
        except Exception as e:
            logger.error(f"Error getting task result {task_id}: {e}")
            return None
    
    async def get_task_status(self, task_id: str) -> Optional[str]:
        """Get task execution status"""
        if not self.celery_app:
            return None
        
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            return result.status
        except Exception as e:
            logger.error(f"Error getting task status {task_id}: {e}")
            return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel pending task"""
        if not self.celery_app:
            return False
        
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            result.revoke(terminate=True)
            logger.info(f"Task cancelled: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {e}")
            return False
    
    async def _store_task_metadata(self, task: UltraTask):
        """Store task metadata in Redis for fast access"""
        try:
            if self.redis_client:
                metadata = {
                    'name': task.name,
                    'priority': task.priority.value,
                    'created_at': task.created_at.isoformat(),
                    'timeout': task.timeout
                }
                
                key = f"task_metadata:{task.id}"
                self.redis_client.hset(key, mapping=metadata)
                self.redis_client.expire(key, 3600)  # 1 hour TTL
                
        except Exception as e:
            logger.error(f"Error storing task metadata: {e}")
    
    def _update_task_stats(self, priority: TaskPriority, processing_time_ms: float, success: bool):
        """Update task processing statistics"""
        if success:
            self.stats['tasks_completed'] += 1
            
            if priority == TaskPriority.CRITICAL:
                self.stats['critical_tasks_processed'] += 1
            
            # Update average processing time
            total_completed = self.stats['tasks_completed']
            current_avg = self.stats['average_processing_time']
            self.stats['average_processing_time'] = (
                (current_avg * (total_completed - 1) + processing_time_ms) / total_completed
            )
        else:
            self.stats['tasks_failed'] += 1
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        if not self.celery_app:
            return {}
        
        try:
            inspect = self.celery_app.control.inspect()
            
            # Get active tasks
            active_tasks = inspect.active()
            
            # Get queue lengths
            queue_stats = {}
            if self.redis_client:
                for queue in ['critical', 'high', 'normal', 'low']:
                    queue_key = f"celery:queue:{queue}"
                    queue_length = self.redis_client.llen(queue_key)
                    queue_stats[queue] = queue_length
            
            return {
                'active_tasks': active_tasks,
                'queue_lengths': queue_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return {'error': str(e)}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            **self.stats,
            'uptime_seconds': uptime,
            'tasks_per_second': self.stats['tasks_completed'] / max(uptime, 1),
            'success_rate_percent': (
                self.stats['tasks_completed'] / 
                max(self.stats['tasks_submitted'], 1) * 100
            ),
            'failure_rate_percent': (
                self.stats['tasks_failed'] / 
                max(self.stats['tasks_submitted'], 1) * 100
            ),
            'queue_stats': self.get_queue_stats()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            health_status = {
                'celery_app': 'healthy' if self.celery_app else 'unhealthy',
                'redis_connection': 'unknown',
                'worker_status': 'unknown',
                'queue_accessibility': 'unknown'
            }
            
            # Test Redis connection
            if self.redis_client:
                try:
                    self.redis_client.ping()
                    health_status['redis_connection'] = 'healthy'
                except:
                    health_status['redis_connection'] = 'unhealthy'
            
            # Test Celery workers
            if self.celery_app:
                try:
                    inspect = self.celery_app.control.inspect()
                    stats = inspect.stats()
                    health_status['worker_status'] = 'healthy' if stats else 'no_workers'
                except:
                    health_status['worker_status'] = 'unhealthy'
            
            # Overall health
            health_status['overall'] = (
                'healthy' if all(
                    status in ['healthy', 'unknown'] 
                    for status in health_status.values()
                ) else 'unhealthy'
            )
            
            return health_status
            
        except Exception as e:
            return {
                'overall': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Global async processor instance
ultra_async_processor = UltraAsyncProcessor()

# Example task handlers for common operations
def handle_event_notification(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle event notification task"""
    logger.info(f"Processing event notification: {payload}")
    
    # Simulate notification processing
    time.sleep(0.05)  # 50ms simulation
    
    return {
        'notification_sent': True,
        'recipients': payload.get('recipients', []),
        'event_id': payload.get('event_id')
    }

def handle_checkin_processing(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle check-in processing task"""
    logger.info(f"Processing check-in: {payload}")
    
    # Simulate check-in processing
    time.sleep(0.02)  # 20ms simulation
    
    return {
        'checkin_processed': True,
        'participant_id': payload.get('participant_id'),
        'event_id': payload.get('event_id'),
        'timestamp': datetime.now().isoformat()
    }

def handle_sales_analytics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle sales analytics calculation"""
    logger.info(f"Processing sales analytics: {payload}")
    
    # Simulate analytics processing
    time.sleep(0.1)  # 100ms simulation
    
    return {
        'analytics_updated': True,
        'metrics_calculated': ['revenue', 'units_sold', 'conversion_rate'],
        'period': payload.get('period', 'daily')
    }

# Convenience functions
def init_async_processor(redis_url: str = "redis://localhost:6379/1"):
    """Initialize ultra async processor"""
    success = ultra_async_processor.init_processor(redis_url)
    
    if success:
        # Register default task handlers
        ultra_async_processor.register_task_handler('event_notification', handle_event_notification)
        ultra_async_processor.register_task_handler('checkin_processing', handle_checkin_processing)
        ultra_async_processor.register_task_handler('sales_analytics', handle_sales_analytics)
    
    return success

async def submit_async_task(task_name: str, payload: Dict[str, Any], 
                           priority: TaskPriority = TaskPriority.NORMAL) -> str:
    """Submit task for async processing"""
    return await ultra_async_processor.submit_task(task_name, payload, priority)

async def get_async_task_result(task_id: str):
    """Get async task result"""
    return await ultra_async_processor.get_task_result(task_id)

async def get_async_processor_stats():
    """Get async processor statistics"""
    return ultra_async_processor.get_performance_stats()

async def async_processor_health_check():
    """Check async processor health"""
    return await ultra_async_processor.health_check()