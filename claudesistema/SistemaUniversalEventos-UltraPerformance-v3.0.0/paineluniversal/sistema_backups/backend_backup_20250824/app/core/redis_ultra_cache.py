"""
Ultra-High Performance Redis Caching System
Enterprise-grade multi-tier caching with connection pooling
Target: 99.9% hit ratio, sub-millisecond access times
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional, Union
import redis
import aioredis
from redis.connection import ConnectionPool

logger = logging.getLogger(__name__)

class UltraRedisCache:
    """Enterprise Redis cache with advanced features"""
    
    def __init__(self):
        self.redis_client = None
        self.async_redis = None
        self.connection_pool = None
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        
    async def init_cache(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize Redis connection with pooling"""
        try:
            # Connection pool for high performance
            self.connection_pool = ConnectionPool.from_url(
                redis_url,
                max_connections=100,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Sync Redis client
            self.redis_client = redis.Redis(
                connection_pool=self.connection_pool,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Async Redis client
            self.async_redis = await aioredis.from_url(
                redis_url,
                max_connections=50,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connections
            await self.async_redis.ping()
            self.redis_client.ping()
            
            logger.info("✅ Ultra Redis Cache initialized with connection pooling")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis cache initialization failed: {e}")
            return False
    
    def _get_cache_key(self, namespace: str, key: str) -> str:
        """Generate optimized cache key"""
        return f"ultra:{namespace}:{key}"
    
    async def get(self, namespace: str, key: str, default=None) -> Any:
        """Ultra-fast cache retrieval"""
        cache_key = self._get_cache_key(namespace, key)
        
        try:
            start_time = time.perf_counter()
            
            if self.async_redis:
                value = await self.async_redis.get(cache_key)
            else:
                value = self.redis_client.get(cache_key) if self.redis_client else None
                
            if value is not None:
                self.stats['hits'] += 1
                access_time = (time.perf_counter() - start_time) * 1000
                
                if access_time > 1.0:  # Log slow access
                    logger.warning(f"Slow cache access: {access_time:.2f}ms for {cache_key}")
                
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            else:
                self.stats['misses'] += 1
                return default
                
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache get error for {cache_key}: {e}")
            return default
    
    async def set(self, namespace: str, key: str, value: Any, ttl: int = 3600) -> bool:
        """Ultra-fast cache storage"""
        cache_key = self._get_cache_key(namespace, key)
        
        try:
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, separators=(',', ':'))
            else:
                serialized_value = str(value)
            
            if self.async_redis:
                await self.async_redis.setex(cache_key, ttl, serialized_value)
            elif self.redis_client:
                self.redis_client.setex(cache_key, ttl, serialized_value)
            else:
                return False
                
            self.stats['sets'] += 1
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache set error for {cache_key}: {e}")
            return False
    
    async def delete(self, namespace: str, key: str) -> bool:
        """Delete cache entry"""
        cache_key = self._get_cache_key(namespace, key)
        
        try:
            if self.async_redis:
                result = await self.async_redis.delete(cache_key)
            elif self.redis_client:
                result = self.redis_client.delete(cache_key)
            else:
                return False
                
            self.stats['deletes'] += 1
            return bool(result)
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache delete error for {cache_key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries by pattern"""
        try:
            if self.async_redis:
                keys = []
                async for key in self.async_redis.scan_iter(match=f"ultra:{pattern}"):
                    keys.append(key)
                
                if keys:
                    deleted = await self.async_redis.delete(*keys)
                    logger.info(f"Invalidated {deleted} cache entries matching {pattern}")
                    return deleted
                    
            return 0
            
        except Exception as e:
            logger.error(f"Pattern invalidation error for {pattern}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_ratio = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_ratio_percent': round(hit_ratio, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive cache health check"""
        try:
            start_time = time.perf_counter()
            
            # Test async connection
            if self.async_redis:
                await self.async_redis.ping()
                async_latency = (time.perf_counter() - start_time) * 1000
            else:
                async_latency = None
            
            # Test sync connection
            start_time = time.perf_counter()
            if self.redis_client:
                self.redis_client.ping()
                sync_latency = (time.perf_counter() - start_time) * 1000
            else:
                sync_latency = None
            
            return {
                'status': 'healthy',
                'async_latency_ms': round(async_latency, 2) if async_latency else None,
                'sync_latency_ms': round(sync_latency, 2) if sync_latency else None,
                'connection_pool_size': self.connection_pool.connection_kwargs if self.connection_pool else None,
                'stats': self.get_stats()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def close(self):
        """Close all connections"""
        try:
            if self.async_redis:
                await self.async_redis.close()
            if self.connection_pool:
                self.connection_pool.disconnect()
            logger.info("Redis cache connections closed")
        except Exception as e:
            logger.error(f"Error closing Redis connections: {e}")

# Global cache instance
ultra_cache = UltraRedisCache()

def cached(namespace: str = "default", ttl: int = 3600, key_func=None):
    """Ultra-performance caching decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Simple key generation
                key_parts = [func.__name__]
                if args:
                    key_parts.extend([str(arg)[:50] for arg in args])
                if kwargs:
                    key_parts.extend([f"{k}:{str(v)[:50]}" for k, v in kwargs.items()])
                cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = await ultra_cache.get(namespace, cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await ultra_cache.set(namespace, cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Convenience functions
async def init_ultra_cache(redis_url: str = "redis://localhost:6379/0"):
    """Initialize ultra cache system"""
    return await ultra_cache.init_cache(redis_url)

async def get_cache_stats():
    """Get cache performance statistics"""
    return ultra_cache.get_stats()

async def cache_health_check():
    """Check cache system health"""
    return await ultra_cache.health_check()

async def close_ultra_cache():
    """Close cache connections"""
    await ultra_cache.close()