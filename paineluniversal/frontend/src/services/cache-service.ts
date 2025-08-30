/**
 * CacheService - Client-side caching service
 * Sistema Universal de Gestão de Eventos
 */

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class CacheService {
  private cache = new Map<string, CacheItem<any>>();
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes

  set<T>(key: string, data: T, ttl: number = this.DEFAULT_TTL): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) {
      return null;
    }

    // Check if expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  has(key: string): boolean {
    return this.get(key) !== null;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  // Clean expired entries
  cleanup(): void {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(key);
      }
    }
  }

  size(): number {
    return this.cache.size;
  }

  // Get cache statistics
  getStats(): {
    size: number;
    keys: string[];
    oldestEntry?: string;
    newestEntry?: string;
  } {
    const keys = Array.from(this.cache.keys());
    let oldestTime = Infinity;
    let newestTime = 0;
    let oldestKey = '';
    let newestKey = '';

    for (const [key, item] of this.cache.entries()) {
      if (item.timestamp < oldestTime) {
        oldestTime = item.timestamp;
        oldestKey = key;
      }
      if (item.timestamp > newestTime) {
        newestTime = item.timestamp;
        newestKey = key;
      }
    }

    return {
      size: this.cache.size,
      keys,
      oldestEntry: oldestKey || undefined,
      newestEntry: newestKey || undefined
    };
  }
}

// Create singleton instance
const cacheService = new CacheService();

// Cleanup expired entries every 5 minutes
setInterval(() => {
  cacheService.cleanup();
}, 5 * 60 * 1000);

export { cacheService, CacheService };