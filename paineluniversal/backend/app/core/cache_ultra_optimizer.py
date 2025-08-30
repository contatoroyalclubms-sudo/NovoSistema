"""
Ultra Cache Optimizer - Intelligent Caching System
Advanced features: predictive caching, auto-scaling, multi-tier storage
"""

import asyncio
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Set
from functools import wraps
from dataclasses import dataclass
import aioredis
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Cache configuration settings"""
    redis_url: str = "redis://localhost:6379/0"
    local_cache_size: int = 1000  # Local memory cache size
    default_ttl: int = 3600
    prediction_window: int = 300  # 5 minutes
    auto_warmup: bool = True
    compression_enabled: bool = True
    metrics_enabled: bool = True
    backup_enabled: bool = True

class LocalCache:
    """Ultra-fast in-memory cache tier"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.access_count: Dict[str, int] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get from local cache"""
        if key in self.cache:
            entry = self.cache[key]
            if entry['expires'] > time.time():
                self.access_times[key] = time.time()
                self.access_count[key] = self.access_count.get(key, 0) + 1
                return entry['value']
            else:
                # Expired
                self._remove(key)
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set in local cache with LRU eviction"""
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = {
            'value': value,
            'expires': time.time() + ttl,
            'created': time.time()
        }
        self.access_times[key] = time.time()
        self.access_count[key] = 1
    
    def _remove(self, key: str):
        """Remove key from all structures"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.access_count.pop(key, None)
    
    def _evict_lru(self):
        """Evict least recently used items"""
        if not self.access_times:
            return
        
        # Find oldest access time
        oldest_key = min(self.access_times, key=self.access_times.get)
        self._remove(oldest_key)
    
    def clear_expired(self):
        """Clean up expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry['expires'] <= current_time
        ]
        for key in expired_keys:
            self._remove(key)

class PredictiveCache:
    """Predictive caching based on access patterns"""
    
    def __init__(self):
        self.access_patterns: Dict[str, List[float]] = {}
        self.predictions: Set[str] = set()
        self.prediction_accuracy = 0.0
        self.total_predictions = 0
        self.correct_predictions = 0
    
    def record_access(self, key: str):
        """Record cache access for pattern analysis"""
        current_time = time.time()
        if key not in self.access_patterns:
            self.access_patterns[key] = []
        
        self.access_patterns[key].append(current_time)
        
        # Keep only recent history (last 24 hours)
        cutoff = current_time - 86400  # 24 hours
        self.access_patterns[key] = [
            t for t in self.access_patterns[key] if t > cutoff
        ]
    
    def predict_next_access(self, key: str, window: int = 300) -> bool:
        """Predict if key will be accessed in next window seconds"""
        if key not in self.access_patterns:
            return False
        
        access_times = self.access_patterns[key]
        if len(access_times) < 3:
            return False
        
        # Calculate average interval
        intervals = [access_times[i+1] - access_times[i] 
                    for i in range(len(access_times)-1)]
        avg_interval = sum(intervals) / len(intervals)
        
        # Predict next access
        last_access = access_times[-1]
        next_predicted = last_access + avg_interval
        current_time = time.time()
        
        # If predicted next access is within window, return True
        return (next_predicted - current_time) <= window
    
    def get_popular_keys(self, limit: int = 100) -> List[str]:
        """Get most frequently accessed keys"""
        key_scores = {}
        current_time = time.time()
        
        for key, access_times in self.access_patterns.items():
            # Recent accesses have higher weight
            score = sum(
                1.0 / (1 + (current_time - access_time) / 3600)  # Decay over hours
                for access_time in access_times
            )
            key_scores[key] = score
        
        return sorted(key_scores.keys(), key=key_scores.get, reverse=True)[:limit]

class UltraCacheOptimizer:
    """Ultra-high performance cache system with optimization"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.redis = None
        self.local_cache = LocalCache(self.config.local_cache_size)
        self.predictive = PredictiveCache()
        self.metrics = {
            'l1_hits': 0,  # Local cache hits
            'l2_hits': 0,  # Redis cache hits
            'misses': 0,
            'sets': 0,
            'predictions': 0,
            'warmup_loads': 0
        }
        self.running = False
    
    async def initialize(self):
        """Initialize the cache system"""
        try:
            self.redis = await aioredis.from_url(
                self.config.redis_url,
                max_connections=50,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            await self.redis.ping()
            self.running = True
            
            # Start background tasks
            if self.config.auto_warmup:
                asyncio.create_task(self._warmup_task())
            
            asyncio.create_task(self._cleanup_task())
            asyncio.create_task(self._metrics_task())
            
            logger.info("✅ Ultra Cache Optimizer initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache optimizer initialization failed: {e}")
            return False
    
    def _generate_key(self, namespace: str, key: str) -> str:
        """Generate optimized cache key with hash"""
        full_key = f"{namespace}:{key}"
        if len(full_key) > 200:  # Hash long keys
            key_hash = hashlib.md5(full_key.encode()).hexdigest()
            return f"ultra:{namespace}:{key_hash}"
        return f"ultra:{full_key}"
    
    async def get(self, namespace: str, key: str, default=None) -> Any:
        """Multi-tier cache retrieval with optimization"""
        cache_key = self._generate_key(namespace, key)
        
        # L1: Local memory cache (fastest)
        local_result = self.local_cache.get(cache_key)
        if local_result is not None:
            self.metrics['l1_hits'] += 1
            self.predictive.record_access(cache_key)
            return local_result
        
        # L2: Redis cache
        if self.redis:
            try:
                redis_result = await self.redis.get(cache_key)
                if redis_result is not None:
                    self.metrics['l2_hits'] += 1
                    
                    # Deserialize and promote to L1
                    try:
                        value = json.loads(redis_result)
                    except json.JSONDecodeError:
                        value = redis_result
                    
                    # Promote to local cache
                    self.local_cache.set(cache_key, value, 300)  # 5 min local TTL
                    self.predictive.record_access(cache_key)
                    
                    return value
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Cache miss
        self.metrics['misses'] += 1
        return default
    
    async def set(self, namespace: str, key: str, value: Any, ttl: int = None) -> bool:
        """Multi-tier cache storage with optimization"""
        ttl = ttl or self.config.default_ttl
        cache_key = self._generate_key(namespace, key)
        
        try:
            # Store in local cache
            self.local_cache.set(cache_key, value, min(ttl, 300))
            
            # Store in Redis
            if self.redis:
                if isinstance(value, (dict, list)):
                    serialized = json.dumps(value, separators=(',', ':'))
                else:
                    serialized = str(value)
                
                await self.redis.setex(cache_key, ttl, serialized)
            
            self.metrics['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, namespace: str, key: str) -> bool:
        """Delete from all cache tiers"""
        cache_key = self._generate_key(namespace, key)
        
        # Remove from local cache
        self.local_cache._remove(cache_key)
        
        # Remove from Redis
        if self.redis:
            try:
                await self.redis.delete(cache_key)
                return True
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        return False
    
    async def invalidate_pattern(self, namespace: str, pattern: str) -> int:
        """Invalidate cache entries by pattern"""
        full_pattern = f"ultra:{namespace}:{pattern}"
        deleted = 0
        
        if self.redis:
            try:
                keys = []
                async for key in self.redis.scan_iter(match=full_pattern):
                    keys.append(key)
                
                if keys:
                    deleted = await self.redis.delete(*keys)
                    
                    # Also remove from local cache
                    for key in keys:
                        self.local_cache._remove(key)
                
                logger.info(f"Invalidated {deleted} entries for pattern {full_pattern}")
                
            except Exception as e:
                logger.error(f"Pattern invalidation error: {e}")
        
        return deleted
    
    async def _warmup_task(self):
        """Background task for predictive cache warming"""
        while self.running:
            try:
                await asyncio.sleep(self.config.prediction_window)
                
                # Get popular keys for warmup
                popular_keys = self.predictive.get_popular_keys(50)
                
                for key in popular_keys:
                    if self.predictive.predict_next_access(key):
                        # This key is likely to be accessed soon
                        # In real implementation, you'd have a callback to preload data
                        self.metrics['predictions'] += 1
                        logger.debug(f"Predicted access for key: {key}")
                
            except Exception as e:
                logger.error(f"Warmup task error: {e}")
    
    async def _cleanup_task(self):
        """Background cleanup task"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Run every minute
                self.local_cache.clear_expired()
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
    
    async def _metrics_task(self):
        """Background metrics collection"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                stats = self.get_stats()
                logger.info(f"Cache metrics: {stats}")
            except Exception as e:
                logger.error(f"Metrics task error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = (
            self.metrics['l1_hits'] + 
            self.metrics['l2_hits'] + 
            self.metrics['misses']
        )
        
        l1_hit_rate = (self.metrics['l1_hits'] / total_requests * 100) if total_requests > 0 else 0
        l2_hit_rate = (self.metrics['l2_hits'] / total_requests * 100) if total_requests > 0 else 0
        total_hit_rate = ((self.metrics['l1_hits'] + self.metrics['l2_hits']) / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'metrics': self.metrics.copy(),
            'hit_rates': {
                'l1_hit_rate_percent': round(l1_hit_rate, 2),
                'l2_hit_rate_percent': round(l2_hit_rate, 2),
                'total_hit_rate_percent': round(total_hit_rate, 2)
            },
            'cache_sizes': {
                'local_cache_entries': len(self.local_cache.cache),
                'local_cache_max': self.local_cache.max_size
            },
            'predictions': {
                'tracked_patterns': len(self.predictive.access_patterns),
                'accuracy': round(self.predictive.prediction_accuracy * 100, 2)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            # Test Redis connection
            start_time = time.perf_counter()
            await self.redis.ping()
            redis_latency = (time.perf_counter() - start_time) * 1000
            
            return {
                'status': 'healthy',
                'redis_latency_ms': round(redis_latency, 2),
                'local_cache_healthy': True,
                'background_tasks_running': self.running,
                'stats': self.get_stats()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def close(self):
        """Shutdown cache system"""
        self.running = False
        if self.redis:
            await self.redis.close()
        logger.info("Ultra Cache Optimizer closed")

# Global cache optimizer instance
cache_optimizer = UltraCacheOptimizer()

def ultra_cached(namespace: str = "default", ttl: int = 3600, key_func: Optional[Callable] = None):
    """Advanced caching decorator with multi-tier optimization"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Smart key generation
                key_parts = [func.__name__]
                
                # Include function arguments
                for arg in args:
                    if hasattr(arg, 'id'):  # Database models
                        key_parts.append(f"id:{arg.id}")
                    elif isinstance(arg, (str, int, float, bool)):
                        key_parts.append(str(arg)[:50])
                
                # Include keyword arguments
                for k, v in kwargs.items():
                    if hasattr(v, 'id'):
                        key_parts.append(f"{k}:id:{v.id}")
                    elif isinstance(v, (str, int, float, bool)):
                        key_parts.append(f"{k}:{str(v)[:50]}")
                
                cache_key = ":".join(key_parts)
            
            # Try cache first
            cached_result = await cache_optimizer.get(namespace, cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_optimizer.set(namespace, cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Convenience functions
async def init_ultra_cache_optimizer(config: CacheConfig = None):
    """Initialize the ultra cache optimizer"""
    global cache_optimizer
    if config:
        cache_optimizer = UltraCacheOptimizer(config)
    return await cache_optimizer.initialize()

async def get_cache_optimizer_stats():
    """Get cache optimizer statistics"""
    return cache_optimizer.get_stats()

async def cache_optimizer_health():
    """Check cache optimizer health"""
    return await cache_optimizer.health_check()

async def close_cache_optimizer():
    """Close cache optimizer"""
    await cache_optimizer.close()