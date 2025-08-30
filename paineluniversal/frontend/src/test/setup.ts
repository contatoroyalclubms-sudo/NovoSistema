import '@testing-library/jest-dom'
import { beforeAll, afterEach, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import { server } from './mocks/server'

// Mock global objects and APIs
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
})

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Mock sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: localStorageMock,
})

// Mock URL.createObjectURL
Object.defineProperty(window, 'URL', {
  value: {
    createObjectURL: () => 'mocked-url',
    revokeObjectURL: () => {},
  },
})

// Mock fetch for tests that don't use MSW
global.fetch = global.fetch || (() => 
  Promise.resolve({
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
    ok: true,
    status: 200,
  })
) as any

// MSW Setup
beforeAll(() => {
  // Start the server before all tests
  server.listen({
    onUnhandledRequest: 'error',
  })
})

afterEach(() => {
  // Clean up after each test
  cleanup()
  
  // Reset handlers between tests
  server.resetHandlers()
  
  // Clear localStorage between tests
  localStorageMock.clear()
})

afterAll(() => {
  // Close server after all tests
  server.close()
})