/**
 * REACT PERFORMANCE OPTIMIZATION HOOKS
 * Sistema Universal de Gestão de Eventos - ULTRA PERFORMANCE
 * 
 * Advanced React hooks for:
 * - Component re-render optimization
 * - Memory leak prevention
 * - Virtual scrolling
 * - Image lazy loading
 * - Performance monitoring
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { debounce, throttle } from '../lib/performance-utils'

/**
 * Advanced debouncing hook with cleanup
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

/**
 * Advanced throttling hook for performance-critical operations
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const throttledCallback = useMemo(
    () => throttle(callback, delay),
    [callback, delay]
  )

  useEffect(() => {
    return () => {
      if ('cancel' in throttledCallback) {
        throttledCallback.cancel()
      }
    }
  }, [throttledCallback])

  return throttledCallback
}

/**
 * Virtual scrolling hook for large lists
 */
interface UseVirtualScrollProps {
  itemHeight: number
  containerHeight: number
  itemCount: number
  overscan?: number
}

export function useVirtualScroll({
  itemHeight,
  containerHeight,
  itemCount,
  overscan = 3,
}: UseVirtualScrollProps) {
  const [scrollTop, setScrollTop] = useState(0)
  
  const visibleStart = Math.floor(scrollTop / itemHeight)
  const visibleEnd = Math.min(
    visibleStart + Math.ceil(containerHeight / itemHeight),
    itemCount - 1
  )

  const startIndex = Math.max(0, visibleStart - overscan)
  const endIndex = Math.min(itemCount - 1, visibleEnd + overscan)

  const visibleItems = useMemo(() => {
    const items = []
    for (let i = startIndex; i <= endIndex; i++) {
      items.push({
        index: i,
        offsetTop: i * itemHeight,
      })
    }
    return items
  }, [startIndex, endIndex, itemHeight])

  const totalHeight = itemCount * itemHeight

  const handleScroll = useThrottle((e: Event) => {
    const target = e.target as HTMLElement
    setScrollTop(target.scrollTop)
  }, 16) // 60fps

  return {
    visibleItems,
    totalHeight,
    handleScroll,
    startIndex,
    endIndex,
  }
}

/**
 * Intersection Observer hook for lazy loading
 */
interface UseIntersectionObserverOptions {
  root?: Element | null
  rootMargin?: string
  threshold?: number | number[]
}

export function useIntersectionObserver(
  options: UseIntersectionObserverOptions = {}
) {
  const [isIntersecting, setIsIntersecting] = useState(false)
  const [hasIntersected, setHasIntersected] = useState(false)
  const targetRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const element = targetRef.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        const isVisible = entry.isIntersecting
        setIsIntersecting(isVisible)
        
        if (isVisible && !hasIntersected) {
          setHasIntersected(true)
        }
      },
      {
        root: options.root,
        rootMargin: options.rootMargin || '50px',
        threshold: options.threshold || 0.1,
      }
    )

    observer.observe(element)

    return () => {
      observer.unobserve(element)
    }
  }, [options.root, options.rootMargin, options.threshold, hasIntersected])

  return {
    targetRef,
    isIntersecting,
    hasIntersected,
  }
}

/**
 * Image lazy loading hook with blur-to-clear transition
 */
interface UseImageLazyLoadProps {
  src: string
  placeholder?: string
  blur?: boolean
}

export function useImageLazyLoad({
  src,
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIwIiBoZWlnaHQ9IjI0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8ZyBmaWxsPSIjZTJlOGYwIj4KICAgIDxyZWN0IHdpZHRoPSIzMjAiIGhlaWdodD0iMjQwIi8+CiAgPC9nPgo8L3N2Zz4=',
  blur = true,
}: UseImageLazyLoadProps) {
  const [imageSrc, setImageSrc] = useState(placeholder)
  const [isLoaded, setIsLoaded] = useState(false)
  const [isError, setIsError] = useState(false)
  const { targetRef, hasIntersected } = useIntersectionObserver()

  useEffect(() => {
    if (!hasIntersected) return

    const img = new Image()
    
    img.onload = () => {
      setImageSrc(src)
      setIsLoaded(true)
      setIsError(false)
    }

    img.onerror = () => {
      setIsError(true)
      setIsLoaded(false)
    }

    img.src = src
  }, [src, hasIntersected])

  const imageProps = {
    src: imageSrc,
    ref: targetRef,
    style: {
      filter: blur && !isLoaded ? 'blur(10px)' : 'none',
      transition: 'filter 0.3s ease-out',
    },
    loading: 'lazy' as const,
  }

  return {
    imageProps,
    isLoaded,
    isError,
    hasIntersected,
  }
}

/**
 * Performance monitoring hook
 */
interface PerformanceMetrics {
  renderTime: number
  mountTime: number
  updateCount: number
  memoryUsage?: number
}

export function usePerformanceMonitor(componentName: string) {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    mountTime: 0,
    updateCount: 0,
  })
  
  const mountTimeRef = useRef<number>(0)
  const renderStartRef = useRef<number>(0)
  const updateCountRef = useRef(0)

  // Start render timing
  renderStartRef.current = performance.now()

  useEffect(() => {
    // Component mounted
    mountTimeRef.current = performance.now()
    
    return () => {
      // Component unmounted - log final metrics
      console.log(`[Performance] ${componentName}:`, metrics)
    }
  }, [])

  useEffect(() => {
    // Update metrics after each render
    const renderTime = performance.now() - renderStartRef.current
    updateCountRef.current += 1

    setMetrics(prev => ({
      ...prev,
      renderTime,
      mountTime: mountTimeRef.current > 0 ? mountTimeRef.current - renderStartRef.current : 0,
      updateCount: updateCountRef.current,
      memoryUsage: (performance as any).memory?.usedJSHeapSize || undefined,
    }))
  })

  // Development mode warnings
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      if (metrics.renderTime > 16) {
        console.warn(
          `[Performance Warning] ${componentName} render took ${metrics.renderTime.toFixed(2)}ms (>16ms)`
        )
      }
      
      if (metrics.updateCount > 10) {
        console.warn(
          `[Performance Warning] ${componentName} has re-rendered ${metrics.updateCount} times`
        )
      }
    }
  }, [metrics.renderTime, metrics.updateCount, componentName])

  return metrics
}

/**
 * Optimized state management hook with batching
 */
export function useOptimizedState<T>(
  initialState: T | (() => T)
): [T, (update: T | ((prev: T) => T)) => void] {
  const [state, setState] = useState(initialState)
  const batchedUpdatesRef = useRef<((prev: T) => T)[]>([])
  const timeoutRef = useRef<NodeJS.Timeout>()

  const optimizedSetState = useCallback((update: T | ((prev: T) => T)) => {
    const updater = typeof update === 'function' ? update as (prev: T) => T : () => update

    batchedUpdatesRef.current.push(updater)

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    timeoutRef.current = setTimeout(() => {
      setState(prev => {
        return batchedUpdatesRef.current.reduce((acc, updater) => updater(acc), prev)
      })
      batchedUpdatesRef.current = []
    }, 0)
  }, [])

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return [state, optimizedSetState]
}

/**
 * Memo hook with custom equality function
 */
export function useDeepMemo<T>(
  factory: () => T,
  deps: React.DependencyList,
  isEqual?: (a: T, b: T) => boolean
): T {
  const ref = useRef<{ value: T; deps: React.DependencyList }>()

  const hasChanged = useMemo(() => {
    if (!ref.current) return true

    if (deps.length !== ref.current.deps.length) return true

    return deps.some((dep, index) => {
      const prevDep = ref.current!.deps[index]
      return isEqual ? !isEqual(dep as T, prevDep as T) : dep !== prevDep
    })
  }, deps)

  if (hasChanged || !ref.current) {
    const value = factory()
    ref.current = { value, deps: [...deps] }
  }

  return ref.current.value
}

/**
 * Cleanup hook for preventing memory leaks
 */
export function useCleanup(cleanup: () => void) {
  const cleanupRef = useRef(cleanup)
  cleanupRef.current = cleanup

  useEffect(() => {
    return () => {
      cleanupRef.current()
    }
  }, [])
}

/**
 * Batch API calls hook
 */
export function useBatchedAPI<T, R>(
  apiCall: (items: T[]) => Promise<R>,
  batchSize: number = 10,
  delay: number = 100
) {
  const batchRef = useRef<T[]>([])
  const timeoutRef = useRef<NodeJS.Timeout>()
  const [results, setResults] = useState<R[]>([])
  const [loading, setLoading] = useState(false)

  const addToBatch = useCallback((item: T) => {
    batchRef.current.push(item)

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    if (batchRef.current.length >= batchSize) {
      processBatch()
    } else {
      timeoutRef.current = setTimeout(processBatch, delay)
    }
  }, [batchSize, delay])

  const processBatch = useCallback(async () => {
    if (batchRef.current.length === 0) return

    setLoading(true)
    const batch = [...batchRef.current]
    batchRef.current = []

    try {
      const result = await apiCall(batch)
      setResults(prev => [...prev, result])
    } catch (error) {
      console.error('Batch API call failed:', error)
    } finally {
      setLoading(false)
    }
  }, [apiCall])

  useCleanup(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
  })

  return {
    addToBatch,
    results,
    loading,
  }
}