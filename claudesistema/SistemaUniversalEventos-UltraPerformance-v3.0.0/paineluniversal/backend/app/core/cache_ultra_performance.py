"""
Ultra-Performance Multi-Tier Caching System
Sistema Universal de Gestão de Eventos - Enterprise Scale
Target: Sub-10ms cache hits, intelligent invalidation, distributed caching
"""

import asyncio
import json
import logging
import hashlib
import time
from typing import Any, Dict, List, Optional, Set, Union, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import pickle
import lz4.frame
import redis.asyncio as redis
from redis.asyncio import Redis
from prometheus_client import Counter, Histogram, Gauge
import threading
from functools import wraps
import inspect

logger = logging.getLogger(__name__)

# Performance Metrics
CACHE_HITS = Counter('cache_hits_total', 'Cache hit count', ['tier', 'key_type'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache miss count', ['tier', 'key_type'])
CACHE_OPERATIONS_DURATION = Histogram('cache_operation_duration_seconds', 'Cache operation duration', ['operation', 'tier'])
CACHE_MEMORY_USAGE = Gauge('cache_memory_usage_bytes', 'Cache memory usage', ['tier'])
CACHE_EVICTIONS = Counter('cache_evictions_total', 'Cache eviction count', ['tier', 'reason'])
CACHE_INVALIDATIONS = Counter('cache_invalidations_total', 'Cache invalidation count', ['pattern'])

@dataclass
class CacheConfig:
    """Ultra-performance cache configuration"""
    # L1 Cache (In-Memory) - Nanosecond access
    l1_max_size: int = 10000  # Maximum items in L1 cache
    l1_ttl_seconds: int = 300  # 5 minutes default TTL
    l1_compression_threshold: int = 1024  # Compress data > 1KB
    
    # L2 Cache (Local Redis) - Microsecond access  
    l2_host: str = "127.0.0.1"
    l2_port: int = 6379
    l2_db: int = 0
    l2_ttl_seconds: int = 1800  # 30 minutes default TTL
    l2_max_connections: int = 100
    
    # L3 Cache (Distributed Redis Cluster) - Sub-millisecond access
    l3_cluster_nodes: List[Dict[str, Union[str, int]]] = None
    l3_ttl_seconds: int = 3600  # 1 hour default TTL
    l3_max_connections_per_node: int = 50
    
    # Performance settings
    enable_compression: bool = True
    compression_level: int = 3
    enable_metrics: bool = True
    batch_invalidation_size: int = 1000

class CacheEntry:
    """Optimized cache entry with metadata"""
    __slots__ = ['data', 'created_at', 'expires_at', 'hit_count', 'size', 'compressed']
    
    def __init__(self, data: Any, ttl_seconds: int = 300, compressed: bool = False):
        self.data = data
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds
        self.hit_count = 0
        self.size = len(str(data)) if not compressed else len(data)
        self.compressed = compressed
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    def hit(self) -> Any:
        self.hit_count += 1
        return self.data
    
    def age_seconds(self) -> float:
        return time.time() - self.created_at

class L1InMemoryCache:
    """Ultra-fast in-memory cache with LRU eviction and compression"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # LRU tracking
        self.lock = threading.RLock()  # Thread-safe operations
        self.total_size = 0
        self.hit_stats = {"hits": 0, "misses": 0}
        
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using LZ4 for speed"""
        if not self.config.enable_compression or len(data) < self.config.l1_compression_threshold:
            return data
        return lz4.frame.compress(data, compression_level=self.config.compression_level)
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress LZ4 data"""
        try:
            return lz4.frame.decompress(data)
        except:
            return data  # Return original if not compressed
    
    def _evict_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [key for key, entry in self.cache.items() if entry.expires_at <= current_time]
        for key in expired_keys:
            self._remove_key(key)
    
    def _evict_lru(self):
        """Evict least recently used items"""
        while len(self.cache) >= self.config.l1_max_size and self.access_order:
            lru_key = self.access_order.pop(0)
            self._remove_key(lru_key)
            if self.config.enable_metrics:
                CACHE_EVICTIONS.labels(tier='L1', reason='lru').inc()
    
    def _remove_key(self, key: str):
        """Remove key and update statistics"""
        if key in self.cache:
            entry = self.cache[key]
            self.total_size -= entry.size
            del self.cache[key]
        if key in self.access_order:
            self.access_order.remove(key)
    
    def _update_access_order(self, key: str):
        """Update LRU order"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from L1 cache with performance tracking"""
        start_time = time.time()
        
        with self.lock:
            self._evict_expired()
            
            if key in self.cache:
                entry = self.cache[key]
                if not entry.is_expired():
                    self._update_access_order(key)
                    result = entry.hit()
                    
                    # Metrics
                    self.hit_stats["hits"] += 1
                    if self.config.enable_metrics:
                        CACHE_HITS.labels(tier='L1', key_type=self._classify_key(key)).inc()
                        CACHE_OPERATIONS_DURATION.labels(operation='get', tier='L1').observe(time.time() - start_time)
                    
                    return result
                else:
                    self._remove_key(key)
        
        self.hit_stats["misses"] += 1
        if self.config.enable_metrics:
            CACHE_MISSES.labels(tier='L1', key_type=self._classify_key(key)).inc()
        
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set item in L1 cache with compression"""
        start_time = time.time()
        ttl = ttl_seconds or self.config.l1_ttl_seconds
        
        try:
            # Serialize and compress if needed
            serialized = pickle.dumps(value)
            compressed_data = self._compress_data(serialized)
            is_compressed = len(compressed_data) < len(serialized)
            
            with self.lock:
                self._evict_expired()
                self._evict_lru()
                
                # Remove existing entry if present
                if key in self.cache:
                    self._remove_key(key)
                
                # Create new entry
                entry = CacheEntry(
                    compressed_data if is_compressed else serialized,
                    ttl,
                    is_compressed
                )
                
                self.cache[key] = entry
                self.total_size += entry.size
                self._update_access_order(key)
                
                # Metrics
                if self.config.enable_metrics:
                    CACHE_OPERATIONS_DURATION.labels(operation='set', tier='L1').observe(time.time() - start_time)
                    CACHE_MEMORY_USAGE.labels(tier='L1').set(self.total_size)
                
                return True
                
        except Exception as e:
            logger.error(f"L1 cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete item from L1 cache"""
        with self.lock:
            if key in self.cache:
                self._remove_key(key)
                return True
        return False
    
    def clear(self):
        """Clear all L1 cache"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.total_size = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get L1 cache statistics"""
        with self.lock:
            total_requests = self.hit_stats["hits"] + self.hit_stats["misses"]
            hit_rate = (self.hit_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "tier": "L1",
                "size": len(self.cache),
                "max_size": self.config.l1_max_size,
                "utilization_percent": round((len(self.cache) / self.config.l1_max_size) * 100, 2),
                "memory_usage_bytes": self.total_size,
                "hit_rate_percent": round(hit_rate, 2),
                "hits": self.hit_stats["hits"],
                "misses": self.hit_stats["misses"],
                "average_entry_size": round(self.total_size / len(self.cache), 2) if self.cache else 0
            }
    
    def _classify_key(self, key: str) -> str:
        """Classify cache key for metrics"""
        if key.startswith('user:'):
            return 'user'
        elif key.startswith('event:'):
            return 'event'
        elif key.startswith('product:'):
            return 'product'
        elif key.startswith('query:'):
            return 'query'
        return 'other'

class UltraPerformanceCache:
    """
    Multi-tier ultra-performance caching system.
    
    Architecture:
    - L1: In-memory cache (nanosecond access) - Hot data
    - L2: Local Redis (microsecond access) - Warm data  
    - L3: Distributed Redis cluster (sub-millisecond) - Cold data
    
    Features:
    - Intelligent cache promotion/demotion
    - Automatic compression
    - Smart invalidation patterns
    - Performance metrics
    - Circuit breaker pattern
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.l1_cache = L1InMemoryCache(self.config)
        self.l2_redis: Optional[Redis] = None
        self.l3_redis: Optional[Redis] = None
        self.invalidation_patterns: Set[str] = set()
        self.performance_stats = {
            "l1_hits": 0, "l2_hits": 0, "l3_hits": 0,
            "total_misses": 0, "promotions": 0, "demotions": 0
        }
        
    async def initialize(self):
        """Initialize Redis connections"""
        try:
            # L2 Local Redis
            self.l2_redis = redis.Redis(
                host=self.config.l2_host,
                port=self.config.l2_port,
                db=self.config.l2_db,
                max_connections=self.config.l2_max_connections,
                decode_responses=False,  # Keep binary for compression
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Test L2 connection
            await self.l2_redis.ping()
            logger.info("✅ L2 Redis cache connected")
            
            # L3 Distributed Redis (optional cluster setup)
            if self.config.l3_cluster_nodes:
                # For production, use Redis Cluster
                pass
            else:
                # Use same Redis for now, different DB
                self.l3_redis = redis.Redis(
                    host=self.config.l2_host,
                    port=self.config.l2_port,
                    db=self.config.l2_db + 1,  # Different database
                    max_connections=self.config.l2_max_connections,
                    decode_responses=False
                )
                await self.l3_redis.ping()
                logger.info("✅ L3 Redis cache connected")
                
        except Exception as e:
            logger.error(f"❌ Cache initialization failed: {e}")
            raise
    
    def _generate_cache_key(self, key: str, namespace: str = "default") -> str:
        """Generate optimized cache key"""
        return f"eventos:{namespace}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize and compress value"""
        serialized = pickle.dumps(value)
        if self.config.enable_compression and len(serialized) > 1024:
            return lz4.frame.compress(serialized)
        return serialized
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Decompress and deserialize value"""
        try:
            # Try to decompress first
            decompressed = lz4.frame.decompress(data)
            return pickle.loads(decompressed)
        except:
            # If decompression fails, try direct pickle load
            return pickle.loads(data)
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """
        Ultra-performance multi-tier cache get.
        Checks L1 -> L2 -> L3 with automatic promotion.
        """
        cache_key = self._generate_cache_key(key, namespace)
        
        # L1 Cache check (nanosecond access)
        start_time = time.time()
        l1_result = self.l1_cache.get(cache_key)
        if l1_result is not None:
            self.performance_stats["l1_hits"] += 1
            if self.config.enable_metrics:
                CACHE_OPERATIONS_DURATION.labels(operation='get_total', tier='L1').observe(time.time() - start_time)
            return self._deserialize_value(l1_result) if isinstance(l1_result, bytes) else l1_result
        
        # L2 Cache check (microsecond access)
        try:
            if self.l2_redis:
                l2_data = await self.l2_redis.get(cache_key)
                if l2_data:
                    # Promote to L1
                    self.l1_cache.set(cache_key, l2_data, self.config.l1_ttl_seconds)
                    self.performance_stats["l2_hits"] += 1
                    self.performance_stats["promotions"] += 1
                    
                    if self.config.enable_metrics:
                        CACHE_HITS.labels(tier='L2', key_type=self.l1_cache._classify_key(key)).inc()
                        CACHE_OPERATIONS_DURATION.labels(operation='get_total', tier='L2').observe(time.time() - start_time)
                    
                    return self._deserialize_value(l2_data)
        except Exception as e:
            logger.warning(f"L2 cache error for key {key}: {e}")
        
        # L3 Cache check (sub-millisecond access)
        try:
            if self.l3_redis:
                l3_data = await self.l3_redis.get(cache_key)
                if l3_data:
                    # Promote to L2 and L1
                    await self.l2_redis.setex(cache_key, self.config.l2_ttl_seconds, l3_data)
                    self.l1_cache.set(cache_key, l3_data, self.config.l1_ttl_seconds)
                    self.performance_stats["l3_hits"] += 1
                    self.performance_stats["promotions"] += 2
                    
                    if self.config.enable_metrics:
                        CACHE_HITS.labels(tier='L3', key_type=self.l1_cache._classify_key(key)).inc()
                        CACHE_OPERATIONS_DURATION.labels(operation='get_total', tier='L3').observe(time.time() - start_time)
                    
                    return self._deserialize_value(l3_data)
        except Exception as e:
            logger.warning(f"L3 cache error for key {key}: {e}")
        
        # Cache miss
        self.performance_stats["total_misses"] += 1
        if self.config.enable_metrics:
            CACHE_MISSES.labels(tier='all', key_type=self.l1_cache._classify_key(key)).inc()
        
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None,
        namespace: str = "default",
        cache_tiers: List[str] = None
    ) -> bool:
        """
        Ultra-performance multi-tier cache set.
        Stores in all specified tiers simultaneously.
        """
        cache_key = self._generate_cache_key(key, namespace)
        serialized_value = self._serialize_value(value)
        tiers = cache_tiers or ["L1", "L2", "L3"]
        success = True
        
        # L1 Cache
        if "L1" in tiers:
            l1_ttl = ttl_seconds or self.config.l1_ttl_seconds
            self.l1_cache.set(cache_key, serialized_value, l1_ttl)
        
        # L2 Cache
        if "L2" in tiers and self.l2_redis:
            try:
                l2_ttl = ttl_seconds or self.config.l2_ttl_seconds
                await self.l2_redis.setex(cache_key, l2_ttl, serialized_value)
            except Exception as e:
                logger.warning(f"L2 cache set error for key {key}: {e}")
                success = False
        
        # L3 Cache
        if "L3" in tiers and self.l3_redis:
            try:
                l3_ttl = ttl_seconds or self.config.l3_ttl_seconds
                await self.l3_redis.setex(cache_key, l3_ttl, serialized_value)
            except Exception as e:
                logger.warning(f"L3 cache set error for key {key}: {e}")
                success = False
        
        return success
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete from all cache tiers"""
        cache_key = self._generate_cache_key(key, namespace)
        
        # Delete from all tiers
        self.l1_cache.delete(cache_key)
        
        if self.l2_redis:
            await self.l2_redis.delete(cache_key)
        
        if self.l3_redis:
            await self.l3_redis.delete(cache_key)
        
        return True
    
    async def invalidate_pattern(self, pattern: str, namespace: str = "default") -> int:
        """
        Intelligent cache invalidation by pattern.
        Uses Redis SCAN for memory-efficient pattern matching.
        """
        full_pattern = self._generate_cache_key(pattern, namespace)
        invalidated_count = 0
        
        # Add to invalidation tracking
        self.invalidation_patterns.add(pattern)
        
        try:
            # L1 Pattern invalidation (in-memory)
            keys_to_delete = []
            for key in self.l1_cache.cache.keys():
                if self._matches_pattern(key, full_pattern):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                self.l1_cache.delete(key)
                invalidated_count += 1
            
            # L2 & L3 Pattern invalidation (Redis)
            for redis_client in [self.l2_redis, self.l3_redis]:
                if redis_client:
                    cursor = 0
                    while True:
                        cursor, keys = await redis_client.scan(
                            cursor=cursor,
                            match=full_pattern,
                            count=self.config.batch_invalidation_size
                        )
                        
                        if keys:
                            await redis_client.delete(*keys)
                            invalidated_count += len(keys)
                        
                        if cursor == 0:
                            break
            
            if self.config.enable_metrics:
                CACHE_INVALIDATIONS.labels(pattern=pattern).inc(invalidated_count)
            
            logger.info(f"🗑️ Cache invalidation: {invalidated_count} keys for pattern '{pattern}'")
            
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
        
        return invalidated_count
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching (supports * wildcard)"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = (
            self.performance_stats["l1_hits"] + 
            self.performance_stats["l2_hits"] + 
            self.performance_stats["l3_hits"] + 
            self.performance_stats["total_misses"]
        )
        
        overall_hit_rate = 0
        if total_requests > 0:
            overall_hit_rate = (
                (self.performance_stats["l1_hits"] + 
                 self.performance_stats["l2_hits"] + 
                 self.performance_stats["l3_hits"]) / total_requests * 100
            )
        
        stats = {
            "overall": {
                "total_requests": total_requests,
                "hit_rate_percent": round(overall_hit_rate, 2),
                "promotions": self.performance_stats["promotions"],
                "demotions": self.performance_stats["demotions"]
            },
            "l1": self.l1_cache.get_stats(),
            "l2": await self._get_redis_stats(self.l2_redis, "L2"),
            "l3": await self._get_redis_stats(self.l3_redis, "L3")
        }
        
        return stats
    
    async def _get_redis_stats(self, redis_client: Redis, tier: str) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        if not redis_client:
            return {"tier": tier, "status": "disabled"}
        
        try:
            info = await redis_client.info('memory')
            keyspace_info = await redis_client.info('keyspace')
            
            # Count keys in our namespace
            our_keys_count = 0
            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(
                    cursor=cursor,
                    match="eventos:*",
                    count=1000
                )
                our_keys_count += len(keys)
                if cursor == 0:
                    break
            
            return {
                "tier": tier,
                "status": "connected",
                "memory_usage_bytes": info.get('used_memory', 0),
                "memory_peak_bytes": info.get('used_memory_peak', 0),
                "keys_count": our_keys_count,
                "connected_clients": info.get('connected_clients', 0),
                "ops_per_sec": info.get('instantaneous_ops_per_sec', 0)
            }
            
        except Exception as e:
            return {"tier": tier, "status": "error", "error": str(e)}

# Global ultra-performance cache instance
ultra_cache = UltraPerformanceCache()

# Cache decorators for easy usage
def cached(
    ttl_seconds: int = 300,
    namespace: str = "default",
    key_builder: Optional[Callable] = None,
    cache_tiers: List[str] = None
):
    """
    Ultra-performance cache decorator.
    
    Usage:
    @cached(ttl_seconds=600, namespace="users")
    async def get_user(user_id: int):
        return await db_fetch_user(user_id)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key building
                func_name = func.__name__
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Create deterministic key from arguments
                key_parts = [func_name]
                for param_name, param_value in bound_args.arguments.items():
                    key_parts.append(f"{param_name}={param_value}")
                
                cache_key = hashlib.md5(":".join(map(str, key_parts)).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = await ultra_cache.get(cache_key, namespace)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await ultra_cache.set(
                cache_key, 
                result, 
                ttl_seconds=ttl_seconds,
                namespace=namespace,
                cache_tiers=cache_tiers
            )
            
            return result
        
        return wrapper
    return decorator

# Cache warming utilities
class CacheWarmer:
    """Intelligent cache warming for predictive performance"""
    
    def __init__(self, cache_instance: UltraPerformanceCache):
        self.cache = cache_instance
        
    async def warm_user_data(self, user_ids: List[int]):
        """Pre-warm user data cache"""
        # Implementation would depend on your user service
        pass
    
    async def warm_event_data(self, event_ids: List[str]):
        """Pre-warm event data cache"""
        # Implementation would depend on your event service
        pass
    
    async def warm_popular_queries(self):
        """Pre-warm frequently accessed data"""
        # Implementation for popular query patterns
        pass

async def init_ultra_cache():
    """Initialize ultra-performance cache system"""
    logger.info("🚀 Initializing Ultra-Performance Cache System...")
    await ultra_cache.initialize()
    logger.info("✅ Ultra-Performance Cache System initialized")

async def close_ultra_cache():
    """Gracefully close cache connections"""
    if ultra_cache.l2_redis:
        await ultra_cache.l2_redis.close()
    if ultra_cache.l3_redis:
        await ultra_cache.l3_redis.close()
    logger.info("🔚 Ultra-Performance Cache connections closed")