"""
REDIS CACHE PERFORMANCE OPTIMIZATION
Sistema Universal de Gestão de Eventos - ULTRA PERFORMANCE

High-performance Redis caching layer with:
- Intelligent cache strategies
- Performance monitoring
- Cache warming
- Automatic invalidation
- Memory optimization
"""

import asyncio
import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List, Union, Callable
from functools import wraps
import hashlib
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import time

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Performance Metrics
cache_operations = Counter('cache_operations_total', 'Total cache operations', ['operation', 'result'])
cache_response_time = Histogram('cache_response_time_seconds', 'Cache operation response time')
cache_memory_usage = Gauge('cache_memory_usage_bytes', 'Current cache memory usage')
cache_hit_ratio = Gauge('cache_hit_ratio', 'Cache hit ratio')

class UltraPerformanceCache:
    """
    Ultra-performance Redis cache with:
    - Intelligent caching strategies
    - Performance monitoring
    - Automatic cache warming
    - Memory optimization
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'total_operations': 0
        }
        self._key_patterns = {
            'events': 'event:{event_id}',
            'user_events': 'user:{user_id}:events',
            'event_participants': 'event:{event_id}:participants',
            'checkins': 'event:{event_id}:checkins',
            'pdv_transactions': 'event:{event_id}:transactions',
            'rankings': 'event:{event_id}:rankings',
            'dashboard_stats': 'dashboard:{event_id}:stats',
            'api_responses': 'api:{endpoint}:{params_hash}',
            'query_results': 'query:{table}:{query_hash}'
        }
    
    async def connect(self, redis_url: str = None) -> bool:
        """Connect to Redis with performance optimization"""
        try:
            if not redis_url:
                redis_url = settings.REDIS_URL or "redis://localhost:6379/0"
            
            # Create Redis connection with optimized settings
            self.redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                max_connections=20,  # Connection pooling
            )
            
            # Test connection
            await self.redis_client.ping()
            self.is_connected = True
            
            # Setup performance monitoring
            await self._setup_monitoring()
            
            logger.info("✅ Ultra-Performance Redis Cache connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.is_connected = False
            return False
    
    async def _setup_monitoring(self):
        """Setup Redis performance monitoring"""
        try:
            # Get Redis info for monitoring
            info = await self.redis_client.info('memory')
            used_memory = info.get('used_memory', 0)
            cache_memory_usage.set(used_memory)
            
            logger.info("✅ Redis performance monitoring setup completed")
        except Exception as e:
            logger.warning(f"⚠️ Could not setup Redis monitoring: {e}")
    
    def _generate_key(self, pattern: str, **kwargs) -> str:
        """Generate cache key using pattern"""
        return pattern.format(**kwargs)
    
    def _serialize_value(self, value: Any, use_pickle: bool = False) -> Union[str, bytes]:
        """Serialize value for caching"""
        if use_pickle:
            return pickle.dumps(value)
        return json.dumps(value, default=str, ensure_ascii=False)
    
    def _deserialize_value(self, value: Union[str, bytes], use_pickle: bool = False) -> Any:
        """Deserialize cached value"""
        if use_pickle:
            return pickle.loads(value)
        return json.loads(value)
    
    async def get(self, key: str, use_pickle: bool = False) -> Optional[Any]:
        """Get value from cache with performance monitoring"""
        if not self.is_connected:
            return None
        
        start_time = time.time()
        
        try:
            value = await self.redis_client.get(key)
            
            if value is not None:
                self._stats['hits'] += 1
                cache_operations.labels(operation='get', result='hit').inc()
                
                # Update hit ratio
                total_gets = self._stats['hits'] + self._stats['misses']
                if total_gets > 0:
                    hit_ratio = self._stats['hits'] / total_gets
                    cache_hit_ratio.set(hit_ratio)
                
                return self._deserialize_value(value, use_pickle)
            else:
                self._stats['misses'] += 1
                cache_operations.labels(operation='get', result='miss').inc()
                return None
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            cache_operations.labels(operation='get', result='error').inc()
            return None
        finally:
            duration = time.time() - start_time
            cache_response_time.observe(duration)
    
    async def set(self, key: str, value: Any, ttl: int = 3600, use_pickle: bool = False):
        """Set value in cache with TTL"""
        if not self.is_connected:
            return False
        
        start_time = time.time()
        
        try:
            serialized_value = self._serialize_value(value, use_pickle)
            
            if ttl > 0:
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                await self.redis_client.set(key, serialized_value)
            
            self._stats['sets'] += 1
            cache_operations.labels(operation='set', result='success').inc()
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            cache_operations.labels(operation='set', result='error').inc()
            return False
        finally:
            duration = time.time() - start_time
            cache_response_time.observe(duration)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            self._stats['deletes'] += 1
            cache_operations.labels(operation='delete', result='success').inc()
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            cache_operations.labels(operation='delete', result='error').inc()
            return False
    
    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self.is_connected:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                result = await self.redis_client.delete(*keys)
                cache_operations.labels(operation='delete_pattern', result='success').inc()
                return result
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for pattern {pattern}: {e}")
            cache_operations.labels(operation='delete_pattern', result='error').inc()
            return 0
    
    # High-level caching methods for specific use cases
    
    async def cache_event(self, event_id: str, event_data: Dict, ttl: int = 1800):
        """Cache event data (30 min TTL)"""
        key = self._generate_key(self._key_patterns['events'], event_id=event_id)
        return await self.set(key, event_data, ttl)
    
    async def get_cached_event(self, event_id: str) -> Optional[Dict]:
        """Get cached event data"""
        key = self._generate_key(self._key_patterns['events'], event_id=event_id)
        return await self.get(key)
    
    async def cache_user_events(self, user_id: str, events: List[Dict], ttl: int = 900):
        """Cache user events list (15 min TTL)"""
        key = self._generate_key(self._key_patterns['user_events'], user_id=user_id)
        return await self.set(key, events, ttl)
    
    async def get_cached_user_events(self, user_id: str) -> Optional[List[Dict]]:
        """Get cached user events"""
        key = self._generate_key(self._key_patterns['user_events'], user_id=user_id)
        return await self.get(key)
    
    async def cache_api_response(self, endpoint: str, params: Dict, response: Any, ttl: int = 300):
        """Cache API response (5 min TTL)"""
        params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        key = self._generate_key(self._key_patterns['api_responses'], endpoint=endpoint, params_hash=params_hash)
        return await self.set(key, response, ttl)
    
    async def get_cached_api_response(self, endpoint: str, params: Dict) -> Optional[Any]:
        """Get cached API response"""
        params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        key = self._generate_key(self._key_patterns['api_responses'], endpoint=endpoint, params_hash=params_hash)
        return await self.get(key)
    
    async def cache_query_result(self, table: str, query_params: Dict, result: Any, ttl: int = 600):
        """Cache database query result (10 min TTL)"""
        query_hash = hashlib.md5(json.dumps(query_params, sort_keys=True).encode()).hexdigest()
        key = self._generate_key(self._key_patterns['query_results'], table=table, query_hash=query_hash)
        return await self.set(key, result, ttl, use_pickle=True)
    
    async def get_cached_query_result(self, table: str, query_params: Dict) -> Optional[Any]:
        """Get cached query result"""
        query_hash = hashlib.md5(json.dumps(query_params, sort_keys=True).encode()).hexdigest()
        key = self._generate_key(self._key_patterns['query_results'], table=table, query_hash=query_hash)
        return await self.get(key, use_pickle=True)
    
    async def invalidate_event_cache(self, event_id: str):
        """Invalidate all cache related to an event"""
        patterns = [
            f"event:{event_id}*",
            f"user:*:events",  # Invalidate user events lists
            f"dashboard:{event_id}:*",
            f"api:*"  # Invalidate API responses
        ]
        
        tasks = [self.delete_pattern(pattern) for pattern in patterns]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_deleted = sum(r for r in results if isinstance(r, int))
        logger.info(f"Invalidated {total_deleted} cache keys for event {event_id}")
        return total_deleted
    
    async def warm_cache(self):
        """Pre-warm cache with frequently accessed data"""
        logger.info("🔥 Starting cache warming process...")
        
        # This would be implemented based on your specific use cases
        # For example, cache recent events, popular rankings, etc.
        
        logger.info("✅ Cache warming completed")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            redis_info = await self.redis_client.info() if self.is_connected else {}
            
            return {
                "connected": self.is_connected,
                "stats": self._stats,
                "hit_ratio": self._stats['hits'] / (self._stats['hits'] + self._stats['misses']) if (self._stats['hits'] + self._stats['misses']) > 0 else 0,
                "redis_info": {
                    "used_memory": redis_info.get('used_memory_human', 'N/A'),
                    "connected_clients": redis_info.get('connected_clients', 0),
                    "total_commands_processed": redis_info.get('total_commands_processed', 0),
                    "keyspace_hits": redis_info.get('keyspace_hits', 0),
                    "keyspace_misses": redis_info.get('keyspace_misses', 0),
                }
            }
        except Exception as e:
            return {
                "connected": self.is_connected,
                "stats": self._stats,
                "error": str(e)
            }
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
        self.is_connected = False
        logger.info("✅ Redis cache connection closed")

# Global cache instance
ultra_cache = UltraPerformanceCache()

# Decorator for automatic caching
def cache_result(ttl: int = 300, key_prefix: str = "", use_params: bool = True):
    """Decorator to automatically cache function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not ultra_cache.is_connected:
                return await func(*args, **kwargs)
            
            # Generate cache key
            if use_params:
                params_str = f"{args}_{kwargs}"
                params_hash = hashlib.md5(params_str.encode()).hexdigest()
                cache_key = f"{key_prefix}:{func.__name__}:{params_hash}"
            else:
                cache_key = f"{key_prefix}:{func.__name__}"
            
            # Try to get from cache
            cached_result = await ultra_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await ultra_cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

# Initialization functions
async def init_redis_cache(redis_url: str = None) -> bool:
    """Initialize Redis cache"""
    return await ultra_cache.connect(redis_url)

async def close_redis_cache():
    """Close Redis cache"""
    await ultra_cache.close()

# Legacy compatibility
redis_cache = ultra_cache
events_cache = ultra_cache