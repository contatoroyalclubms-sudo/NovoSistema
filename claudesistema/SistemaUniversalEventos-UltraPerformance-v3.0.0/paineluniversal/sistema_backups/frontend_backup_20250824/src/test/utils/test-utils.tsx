import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthContext } from '@/contexts/AuthContext'
import { User } from '@/types/auth'

// Mock user data for tests
export const mockAdminUser: User = {
  id: '1',
  email: 'admin@test.com',
  nome: 'Admin Test',
  tipo: 'ADMIN',
  ativo: true,
  verificado: true
}

export const mockPromoterUser: User = {
  id: '2',
  email: 'promoter@test.com',
  nome: 'Promoter Test',
  tipo: 'PROMOTER',
  ativo: true,
  verificado: true
}

export const mockOperadorUser: User = {
  id: '3',
  email: 'operador@test.com',
  nome: 'Operador Test',
  tipo: 'OPERADOR',
  ativo: true,
  verificado: true
}

// Mock auth context value
export const createMockAuthContext = (user: User | null = null, loading = false) => ({
  user,
  isLoading: loading,
  isAuthenticated: !!user,
  login: vi.fn().mockResolvedValue({ success: true }),
  logout: vi.fn(),
  register: vi.fn().mockResolvedValue({ success: true }),
  refreshToken: vi.fn().mockResolvedValue({ success: true })
})

// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string
  user?: User | null
  authLoading?: boolean
}

export function renderWithProviders(
  ui: ReactElement,
  {
    route = '/',
    user = null,
    authLoading = false,
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  // Create a new QueryClient for each test
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  })

  const mockAuthValue = createMockAuthContext(user, authLoading)

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <AuthContext.Provider value={mockAuthValue}>
          <MemoryRouter initialEntries={[route]}>
            {children}
          </MemoryRouter>
        </AuthContext.Provider>
      </QueryClientProvider>
    )
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
    mockAuthValue
  }
}

// Utility function to wait for loading states
export const waitForLoadingToFinish = () => 
  new Promise(resolve => setTimeout(resolve, 0))

// Mock implementations for common hooks
export const mockUseNavigate = vi.fn()
export const mockUseLocation = vi.fn(() => ({ pathname: '/', search: '', hash: '', state: null }))

// Mock WebSocket
export const mockWebSocket = {
  connect: vi.fn(),
  disconnect: vi.fn(),
  subscribe: vi.fn(),
  unsubscribe: vi.fn(),
  send: vi.fn(),
  isConnected: false
}

// Mock file upload
export const createMockFile = (name = 'test.jpg', type = 'image/jpeg', size = 1024) => {
  const file = new File(['test content'], name, { type })
  Object.defineProperty(file, 'size', { value: size })
  return file
}

// Mock API responses
export const mockApiResponse = <T>(data: T, status = 200) => ({
  data,
  status,
  statusText: 'OK',
  headers: {},
  config: {},
  request: {}
})

// Mock error response
export const mockApiError = (message = 'API Error', status = 500) => ({
  response: {
    data: { detail: message },
    status,
    statusText: 'Internal Server Error',
    headers: {},
    config: {},
    request: {}
  },
  request: {},
  config: {},
  message
})

// Wait for async operations
export const waitFor = (callback: () => void, timeout = 1000) =>
  new Promise<void>((resolve, reject) => {
    let elapsed = 0
    const interval = 10
    
    const check = () => {
      try {
        callback()
        resolve()
      } catch (error) {
        elapsed += interval
        if (elapsed >= timeout) {
          reject(error)
        } else {
          setTimeout(check, interval)
        }
      }
    }
    
    check()
  })

// Helper to simulate user interactions
export const userInteraction = {
  click: async (element: HTMLElement) => {
    const { userEvent } = await import('@testing-library/user-event')
    const user = userEvent.setup()
    await user.click(element)
  },
  
  type: async (element: HTMLElement, text: string) => {
    const { userEvent } = await import('@testing-library/user-event')
    const user = userEvent.setup()
    await user.type(element, text)
  },
  
  clear: async (element: HTMLElement) => {
    const { userEvent } = await import('@testing-library/user-event')
    const user = userEvent.setup()
    await user.clear(element)
  },
  
  selectOption: async (element: HTMLElement, option: string | string[]) => {
    const { userEvent } = await import('@testing-library/user-event')
    const user = userEvent.setup()
    await user.selectOptions(element, option)
  },
  
  upload: async (element: HTMLElement, file: File | File[]) => {
    const { userEvent } = await import('@testing-library/user-event')
    const user = userEvent.setup()
    await user.upload(element, file)
  }
}

// Mock data generators
export const generateMockEvent = (overrides = {}) => ({
  id: '1',
  nome: 'Evento Test',
  descricao: 'Descrição do evento teste',
  data_inicio: '2024-12-25T20:00:00Z',
  data_fim: '2024-12-26T02:00:00Z',
  local: 'Centro de Convenções',
  endereco: 'Av. Principal, 1000',
  capacidade_maxima: 500,
  status: 'ATIVO',
  preco_ingresso: 50.00,
  ...overrides
})

export const generateMockProduct = (overrides = {}) => ({
  id: '1',
  nome: 'Produto Test',
  descricao: 'Descrição do produto teste',
  preco: 25.50,
  categoria: 'Categoria Test',
  ativo: true,
  estoque: 100,
  ...overrides
})

export const generateMockSale = (overrides = {}) => ({
  id: '1',
  cliente_nome: 'Cliente Test',
  total: 50.00,
  forma_pagamento: 'DINHEIRO',
  status: 'CONCLUIDA',
  itens: [
    {
      produto_id: '1',
      produto_nome: 'Produto Test',
      quantidade: 2,
      preco_unitario: 25.00
    }
  ],
  created_at: new Date().toISOString(),
  ...overrides
})

// Assert helpers
export const expectElementToBeVisible = (element: HTMLElement | null) => {
  expect(element).toBeInTheDocument()
  expect(element).toBeVisible()
}

export const expectElementToHaveText = (element: HTMLElement | null, text: string) => {
  expect(element).toBeInTheDocument()
  expect(element).toHaveTextContent(text)
}

export const expectElementToBeDisabled = (element: HTMLElement | null) => {
  expect(element).toBeInTheDocument()
  expect(element).toBeDisabled()
}

export const expectElementToBeEnabled = (element: HTMLElement | null) => {
  expect(element).toBeInTheDocument()
  expect(element).toBeEnabled()
}

// Re-export testing library utilities
export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'