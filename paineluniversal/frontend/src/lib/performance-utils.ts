/**
 * PERFORMANCE UTILITY FUNCTIONS
 * Sistema Universal de Gestão de Eventos - ULTRA PERFORMANCE
 * 
 * Advanced utility functions for:
 * - Function optimization (debounce, throttle, memoization)
 * - Bundle optimization
 * - Image optimization
 * - Memory management
 * - Performance monitoring
 */

/**
 * Advanced debounce with immediate option and cancellation
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate = false
): T & { cancel: () => void } {
  let timeoutId: NodeJS.Timeout | null = null
  let lastArgs: Parameters<T>
  let lastThis: any

  function debounced(this: any, ...args: Parameters<T>): ReturnType<T> | void {
    lastArgs = args
    lastThis = this

    const callNow = immediate && !timeoutId

    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      timeoutId = null
      if (!immediate) {
        func.apply(lastThis, lastArgs)
      }
    }, wait)

    if (callNow) {
      return func.apply(this, args)
    }
  }

  debounced.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  return debounced as T & { cancel: () => void }
}

/**
 * Advanced throttle with leading and trailing options
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number,
  options: { leading?: boolean; trailing?: boolean } = {}
): T & { cancel: () => void } {
  const { leading = true, trailing = true } = options
  let inThrottle: boolean = false
  let lastFunc: NodeJS.Timeout
  let lastRan: number
  let lastArgs: Parameters<T>
  let lastThis: any

  function throttled(this: any, ...args: Parameters<T>): ReturnType<T> | void {
    lastArgs = args
    lastThis = this

    if (!inThrottle) {
      if (leading) {
        func.apply(this, args)
      }
      inThrottle = true
      setTimeout(() => {
        inThrottle = false
        if (trailing && lastRan) {
          func.apply(lastThis, lastArgs)
        }
      }, limit)
      lastRan = Date.now()
    } else {
      clearTimeout(lastFunc)
      lastFunc = setTimeout(() => {
        if (trailing && Date.now() - lastRan >= limit) {
          func.apply(lastThis, lastArgs)
          lastRan = Date.now()
        }
      }, limit - (Date.now() - lastRan))
    }
  }

  throttled.cancel = () => {
    clearTimeout(lastFunc)
    inThrottle = false
  }

  return throttled as T & { cancel: () => void }
}

/**
 * Memoization with LRU cache
 */
export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  maxSize = 10,
  getKey?: (...args: Parameters<T>) => string
): T & { cache: Map<string, ReturnType<T>>; clear: () => void } {
  const cache = new Map<string, ReturnType<T>>()

  function memoized(...args: Parameters<T>): ReturnType<T> {
    const key = getKey ? getKey(...args) : JSON.stringify(args)

    if (cache.has(key)) {
      // Move to end (most recent)
      const value = cache.get(key)!
      cache.delete(key)
      cache.set(key, value)
      return value
    }

    // Remove oldest if at capacity
    if (cache.size >= maxSize) {
      const firstKey = cache.keys().next().value
      cache.delete(firstKey)
    }

    const result = fn.apply(this, args)
    cache.set(key, result)
    return result
  }

  memoized.cache = cache
  memoized.clear = () => cache.clear()

  return memoized as T & { cache: Map<string, ReturnType<T>>; clear: () => void }
}

/**
 * RAF (RequestAnimationFrame) throttle for smooth animations
 */
export function rafThrottle<T extends (...args: any[]) => any>(callback: T): T {
  let rafId: number | null = null
  let lastArgs: Parameters<T>

  function throttled(...args: Parameters<T>) {
    lastArgs = args
    if (rafId === null) {
      rafId = requestAnimationFrame(() => {
        callback.apply(this, lastArgs)
        rafId = null
      })
    }
  }

  return throttled as T
}

/**
 * Dynamic import with preload
 */
export async function dynamicImportWithPreload<T>(
  importFn: () => Promise<T>,
  preloadDelay = 100
): Promise<T> {
  // Preload after a small delay
  setTimeout(() => {
    importFn().catch(() => {
      // Ignore preload errors
    })
  }, preloadDelay)

  return importFn()
}

/**
 * Code splitting helper
 */
export function lazy<T extends React.ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  fallback?: React.ComponentType
): React.LazyExoticComponent<T> {
  return React.lazy(() => {
    return importFn().catch((error) => {
      console.error('Dynamic import failed:', error)
      // Return fallback component or error boundary
      return { 
        default: fallback || (() => React.createElement('div', null, 'Failed to load component')) 
      } as { default: T }
    })
  })
}

/**
 * Image optimization utilities
 */
export const imageUtils = {
  /**
   * Generate responsive image srcSet
   */
  generateSrcSet(baseSrc: string, sizes: number[] = [320, 640, 1024, 1440]): string {
    return sizes
      .map(size => {
        const src = baseSrc.replace(/\.(jpg|jpeg|png|webp)$/i, `_${size}w.$1`)
        return `${src} ${size}w`
      })
      .join(', ')
  },

  /**
   * Create optimized image URL
   */
  optimizeImageUrl(
    src: string, 
    options: {
      width?: number
      height?: number
      quality?: number
      format?: 'webp' | 'avif' | 'jpg' | 'png'
    } = {}
  ): string {
    const { width, height, quality = 80, format } = options
    
    // This would typically use a service like Cloudinary, ImageKit, etc.
    // For now, we'll return the original with query parameters
    const url = new URL(src, window.location.origin)
    
    if (width) url.searchParams.set('w', width.toString())
    if (height) url.searchParams.set('h', height.toString())
    if (quality) url.searchParams.set('q', quality.toString())
    if (format) url.searchParams.set('f', format)
    
    return url.toString()
  },

  /**
   * Preload critical images
   */
  preloadImages(urls: string[]): Promise<void[]> {
    return Promise.all(
      urls.map(url => new Promise<void>((resolve, reject) => {
        const img = new Image()
        img.onload = () => resolve()
        img.onerror = reject
        img.src = url
      }))
    )
  },

  /**
   * Convert image to WebP if supported
   */
  getOptimalImageFormat(): 'webp' | 'jpg' {
    // Simple WebP support detection
    const canvas = document.createElement('canvas')
    canvas.width = 1
    canvas.height = 1
    const supportsWebP = canvas.toDataURL('image/webp').indexOf('image/webp') === 5
    return supportsWebP ? 'webp' : 'jpg'
  }
}

/**
 * Bundle optimization utilities
 */
export const bundleUtils = {
  /**
   * Measure bundle size impact
   */
  measureBundleImpact<T>(moduleName: string, importFn: () => Promise<T>): Promise<T> {
    const startTime = performance.now()
    const startMemory = (performance as any).memory?.usedJSHeapSize || 0

    return importFn().then(module => {
      const endTime = performance.now()
      const endMemory = (performance as any).memory?.usedJSHeapSize || 0

      console.log(`[Bundle] ${moduleName}:`, {
        loadTime: `${(endTime - startTime).toFixed(2)}ms`,
        memoryImpact: `${((endMemory - startMemory) / 1024).toFixed(2)}KB`
      })

      return module
    })
  },

  /**
   * Prefetch modules based on user interaction hints
   */
  prefetchOnHover(moduleImport: () => Promise<any>) {
    let hasStartedFetch = false
    
    return {
      onMouseEnter: () => {
        if (!hasStartedFetch) {
          hasStartedFetch = true
          moduleImport().catch(() => {
            hasStartedFetch = false // Allow retry on actual click
          })
        }
      },
      onClick: moduleImport
    }
  }
}

/**
 * Performance monitoring utilities
 */
export const performanceMonitor = {
  /**
   * Measure function execution time
   */
  measure<T extends (...args: any[]) => any>(name: string, fn: T): T {
    return ((...args: Parameters<T>): ReturnType<T> => {
      const start = performance.now()
      const result = fn.apply(this, args)
      
      // Handle both sync and async functions
      if (result instanceof Promise) {
        return result.then(res => {
          const end = performance.now()
          console.log(`[Performance] ${name}: ${(end - start).toFixed(2)}ms`)
          return res
        }) as ReturnType<T>
      } else {
        const end = performance.now()
        console.log(`[Performance] ${name}: ${(end - start).toFixed(2)}ms`)
        return result
      }
    }) as T
  },

  /**
   * Monitor Core Web Vitals
   */
  async measureWebVitals(): Promise<{
    FCP: number
    LCP: number
    FID: number
    CLS: number
  }> {
    return new Promise((resolve) => {
      const vitals = {
        FCP: 0,
        LCP: 0,
        FID: 0,
        CLS: 0
      }

      // First Contentful Paint
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries()
        const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint')
        if (fcpEntry) {
          vitals.FCP = fcpEntry.startTime
        }
      }).observe({ entryTypes: ['paint'] })

      // Largest Contentful Paint
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries()
        const lcpEntry = entries[entries.length - 1] // Last entry is the latest LCP
        if (lcpEntry) {
          vitals.LCP = lcpEntry.startTime
        }
      }).observe({ entryTypes: ['largest-contentful-paint'] })

      // First Input Delay
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries()
        const fidEntry = entries[0]
        if (fidEntry) {
          vitals.FID = fidEntry.processingStart - fidEntry.startTime
        }
      }).observe({ entryTypes: ['first-input'] })

      // Cumulative Layout Shift
      let clsValue = 0
      new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value
          }
        }
        vitals.CLS = clsValue
      }).observe({ entryTypes: ['layout-shift'] })

      // Resolve after a reasonable time
      setTimeout(() => resolve(vitals), 5000)
    })
  },

  /**
   * Memory usage monitor
   */
  monitorMemoryUsage(interval = 10000) {
    if (!(performance as any).memory) {
      console.warn('Memory monitoring not available in this browser')
      return () => {}
    }

    const intervalId = setInterval(() => {
      const memory = (performance as any).memory
      console.log('[Memory]', {
        used: `${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)}MB`,
        total: `${(memory.totalJSHeapSize / 1024 / 1024).toFixed(2)}MB`,
        limit: `${(memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2)}MB`
      })
    }, interval)

    return () => clearInterval(intervalId)
  }
}

/**
 * Resource loading optimization
 */
export const resourceOptimizer = {
  /**
   * Preload critical resources
   */
  preloadCriticalResources(resources: Array<{
    href: string
    as: 'script' | 'style' | 'image' | 'font'
    type?: string
    crossorigin?: boolean
  }>) {
    resources.forEach(resource => {
      const link = document.createElement('link')
      link.rel = 'preload'
      link.href = resource.href
      link.as = resource.as
      
      if (resource.type) link.type = resource.type
      if (resource.crossorigin) link.crossOrigin = 'anonymous'
      
      document.head.appendChild(link)
    })
  },

  /**
   * Prefetch next page resources
   */
  prefetchPageResources(urls: string[]) {
    urls.forEach(url => {
      const link = document.createElement('link')
      link.rel = 'prefetch'
      link.href = url
      document.head.appendChild(link)
    })
  },

  /**
   * Load scripts with optimal timing
   */
  async loadScript(src: string, async = true, defer = false): Promise<void> {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = src
      script.async = async
      script.defer = defer
      
      script.onload = () => resolve()
      script.onerror = reject
      
      document.head.appendChild(script)
    })
  }
}

/**
 * Service Worker utilities
 */
export const serviceWorkerUtils = {
  /**
   * Register service worker with update handling
   */
  async registerServiceWorker(swUrl: string = '/sw.js') {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register(swUrl)
        
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New content is available
                console.log('New content available, please refresh.')
                
                // You can show a toast notification here
                if (window.dispatchEvent) {
                  window.dispatchEvent(new CustomEvent('sw-update-available'))
                }
              }
            })
          }
        })
        
        return registration
      } catch (error) {
        console.error('SW registration failed:', error)
      }
    }
  },

  /**
   * Update service worker
   */
  async updateServiceWorker() {
    const registration = await navigator.serviceWorker.getRegistration()
    if (registration) {
      await registration.update()
    }
  },

  /**
   * Skip waiting and activate new SW
   */
  skipWaitingAndActivate() {
    navigator.serviceWorker.getRegistration().then(registration => {
      if (registration?.waiting) {
        registration.waiting.postMessage({ type: 'SKIP_WAITING' })
      }
    })
  }
}

// Export React import for lazy function
import * as React from 'react'