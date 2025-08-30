/**
 * LAZY COMPONENT LOADER - ULTRA PERFORMANCE
 * Sistema Universal de Gestão de Eventos
 * 
 * Advanced lazy loading system with:
 * - Intelligent preloading
 * - Error boundaries
 * - Loading states
 * - Performance monitoring
 */

import React, { Suspense, useState, useEffect, useCallback } from 'react'
import { performanceMonitor } from '../../lib/performance-utils'

interface LazyComponentLoaderProps {
  /**
   * Component import function
   */
  importFn: () => Promise<{ default: React.ComponentType<any> }>
  
  /**
   * Component name for debugging
   */
  componentName: string
  
  /**
   * Props to pass to the lazy component
   */
  componentProps?: Record<string, any>
  
  /**
   * Custom loading component
   */
  loadingComponent?: React.ComponentType
  
  /**
   * Custom error component
   */
  errorComponent?: React.ComponentType<{ error: Error; retry: () => void }>
  
  /**
   * Preload the component on hover
   */
  preloadOnHover?: boolean
  
  /**
   * Preload delay in ms (default: 100ms)
   */
  preloadDelay?: number
  
  /**
   * Retry attempts on failure
   */
  maxRetries?: number
  
  /**
   * Enable performance monitoring
   */
  monitorPerformance?: boolean
}

interface LazyComponentState {
  component: React.ComponentType<any> | null
  loading: boolean
  error: Error | null
  retryCount: number
}

const DefaultLoadingComponent: React.FC = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    <span className="ml-3 text-gray-600">Carregando componente...</span>
  </div>
)

const DefaultErrorComponent: React.FC<{ error: Error; retry: () => void }> = ({ 
  error, 
  retry 
}) => (
  <div className="flex flex-col items-center justify-center p-8 border border-red-200 rounded-lg bg-red-50">
    <div className="text-red-500 text-xl mb-2">⚠️</div>
    <h3 className="text-red-700 font-medium mb-2">Erro ao carregar componente</h3>
    <p className="text-red-600 text-sm text-center mb-4">{error.message}</p>
    <button
      onClick={retry}
      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
    >
      Tentar Novamente
    </button>
  </div>
)

export const LazyComponentLoader: React.FC<LazyComponentLoaderProps> = ({
  importFn,
  componentName,
  componentProps = {},
  loadingComponent: LoadingComponent = DefaultLoadingComponent,
  errorComponent: ErrorComponent = DefaultErrorComponent,
  preloadOnHover = false,
  preloadDelay = 100,
  maxRetries = 3,
  monitorPerformance = true,
}) => {
  const [state, setState] = useState<LazyComponentState>({
    component: null,
    loading: false,
    error: null,
    retryCount: 0,
  })

  const loadComponent = useCallback(async () => {
    if (state.loading || (state.component && !state.error)) {
      return
    }

    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const startTime = performance.now()
      
      const module = await importFn()
      const component = module.default

      if (monitorPerformance) {
        const loadTime = performance.now() - startTime
        console.log(`[LazyComponent] ${componentName} loaded in ${loadTime.toFixed(2)}ms`)
      }

      setState(prev => ({
        ...prev,
        component,
        loading: false,
        error: null,
      }))

    } catch (error) {
      console.error(`[LazyComponent] Failed to load ${componentName}:`, error)
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: error as Error,
        retryCount: prev.retryCount + 1,
      }))
    }
  }, [importFn, componentName, state.loading, state.component, state.error, monitorPerformance])

  const handleRetry = useCallback(() => {
    if (state.retryCount < maxRetries) {
      loadComponent()
    }
  }, [loadComponent, state.retryCount, maxRetries])

  const handlePreload = useCallback(() => {
    if (!state.component && !state.loading) {
      setTimeout(() => {
        loadComponent()
      }, preloadDelay)
    }
  }, [loadComponent, state.component, state.loading, preloadDelay])

  // Load component immediately on mount
  useEffect(() => {
    loadComponent()
  }, [loadComponent])

  // Render loading state
  if (state.loading) {
    return <LoadingComponent />
  }

  // Render error state
  if (state.error) {
    if (state.retryCount >= maxRetries) {
      return (
        <ErrorComponent 
          error={new Error(`Falha após ${maxRetries} tentativas: ${state.error.message}`)} 
          retry={() => setState(prev => ({ ...prev, retryCount: 0 }))} 
        />
      )
    }
    return <ErrorComponent error={state.error} retry={handleRetry} />
  }

  // Render component
  if (state.component) {
    const Component = state.component
    
    const wrapperProps = preloadOnHover 
      ? { onMouseEnter: handlePreload }
      : {}

    return (
      <div {...wrapperProps}>
        <Component {...componentProps} />
      </div>
    )
  }

  // Fallback loading state
  return <LoadingComponent />
}

/**
 * HOC for creating lazy components with built-in error handling
 */
export function withLazyLoading<P extends object>(
  importFn: () => Promise<{ default: React.ComponentType<P> }>,
  options: {
    componentName: string
    loadingComponent?: React.ComponentType
    errorComponent?: React.ComponentType<{ error: Error; retry: () => void }>
    preloadOnHover?: boolean
    monitorPerformance?: boolean
  }
) {
  return function LazyComponent(props: P) {
    return (
      <LazyComponentLoader
        importFn={importFn}
        componentProps={props}
        {...options}
      />
    )
  }
}

/**
 * Route-based lazy loading component
 */
interface LazyRouteProps {
  importFn: () => Promise<{ default: React.ComponentType<any> }>
  routeName: string
  fallback?: React.ComponentType
}

export const LazyRoute: React.FC<LazyRouteProps> = ({
  importFn,
  routeName,
  fallback,
}) => {
  // Create lazy component with React.lazy for better integration with Suspense
  const LazyComponent = React.lazy(() => {
    const startTime = performance.now()
    
    return importFn().then(module => {
      const loadTime = performance.now() - startTime
      console.log(`[LazyRoute] ${routeName} loaded in ${loadTime.toFixed(2)}ms`)
      return module
    }).catch(error => {
      console.error(`[LazyRoute] Failed to load ${routeName}:`, error)
      // Return a fallback component wrapped in the expected format
      return {
        default: fallback || (() => (
          <div className="p-8 text-center">
            <h2 className="text-xl text-red-600 mb-2">Falha ao carregar página</h2>
            <p className="text-gray-600">{error.message}</p>
          </div>
        ))
      }
    })
  })

  return (
    <Suspense fallback={<DefaultLoadingComponent />}>
      <LazyComponent />
    </Suspense>
  )
}

/**
 * Preloader for critical components
 */
export class ComponentPreloader {
  private static cache = new Map<string, Promise<any>>()

  static preload(
    componentName: string,
    importFn: () => Promise<{ default: React.ComponentType<any> }>
  ): Promise<void> {
    if (this.cache.has(componentName)) {
      return this.cache.get(componentName)!.then(() => {})
    }

    console.log(`[Preloader] Preloading ${componentName}...`)
    
    const promise = importFn()
      .then(module => {
        console.log(`[Preloader] ${componentName} preloaded successfully`)
        return module
      })
      .catch(error => {
        console.error(`[Preloader] Failed to preload ${componentName}:`, error)
        // Remove from cache so it can be retried
        this.cache.delete(componentName)
        throw error
      })

    this.cache.set(componentName, promise)
    return promise.then(() => {})
  }

  static preloadMultiple(components: Array<{
    name: string
    importFn: () => Promise<{ default: React.ComponentType<any> }>
  }>): Promise<void[]> {
    return Promise.all(
      components.map(({ name, importFn }) => this.preload(name, importFn))
    )
  }

  static clearCache(): void {
    this.cache.clear()
  }

  static getCacheStatus(): Record<string, 'loading' | 'loaded' | 'error'> {
    const status: Record<string, 'loading' | 'loaded' | 'error'> = {}
    
    this.cache.forEach((promise, name) => {
      status[name] = 'loading' // We could enhance this to track actual status
    })
    
    return status
  }
}

/**
 * Hook for component preloading
 */
export function useComponentPreloader() {
  const [preloadedComponents, setPreloadedComponents] = useState<Set<string>>(new Set())

  const preloadComponent = useCallback(async (
    componentName: string,
    importFn: () => Promise<{ default: React.ComponentType<any> }>
  ) => {
    try {
      await ComponentPreloader.preload(componentName, importFn)
      setPreloadedComponents(prev => new Set(prev).add(componentName))
    } catch (error) {
      console.error(`Failed to preload ${componentName}:`, error)
    }
  }, [])

  const preloadMultiple = useCallback(async (components: Array<{
    name: string
    importFn: () => Promise<{ default: React.ComponentType<any> }>
  }>) => {
    try {
      await ComponentPreloader.preloadMultiple(components)
      const names = components.map(c => c.name)
      setPreloadedComponents(prev => {
        const newSet = new Set(prev)
        names.forEach(name => newSet.add(name))
        return newSet
      })
    } catch (error) {
      console.error('Failed to preload multiple components:', error)
    }
  }, [])

  const isPreloaded = useCallback((componentName: string) => {
    return preloadedComponents.has(componentName)
  }, [preloadedComponents])

  return {
    preloadComponent,
    preloadMultiple,
    isPreloaded,
    preloadedComponents: Array.from(preloadedComponents),
  }
}