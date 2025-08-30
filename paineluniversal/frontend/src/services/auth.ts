import { apiRequest, PaginatedResponse } from './api-client'

// Tipos para autenticação
export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginResponse {
  user: User
  tokens: AuthTokens
}

// Serviços de autenticação
export const authService = {
  // Login
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await apiRequest.post('/auth/login', credentials)
    const data = response.data
    
    // Extrair tokens e user da resposta
    const tokens = {
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      token_type: data.token_type
    }
    const user = data.user
    
    // Salvar tokens no localStorage
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    localStorage.setItem('user', JSON.stringify(user))
    
    return { user, tokens }
  },

  // Registro
  async register(data: RegisterData): Promise<User> {
    const response = await apiRequest.post<User>('/auth/register', data)
    return response.data
  },

  // Logout
  async logout(): Promise<void> {
    try {
      await apiRequest.post('/auth/logout')
    } finally {
      // Limpar dados locais independentemente da resposta
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  },

  // Refresh token
  async refreshToken(): Promise<AuthTokens> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('Refresh token não encontrado')
    }

    const response = await apiRequest.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken
    })

    const tokens = response.data
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)

    return tokens
  },

  // Verificar token atual
  async verifyToken(): Promise<User> {
    const response = await apiRequest.get<User>('/auth/me')
    const user = response.data
    localStorage.setItem('user', JSON.stringify(user))
    return user
  },

  // Obter usuário atual do localStorage
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  // Verificar se está autenticado
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  },

  // Alterar senha
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiRequest.put('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  },

  // Solicitar reset de senha
  async requestPasswordReset(email: string): Promise<void> {
    await apiRequest.post('/auth/request-password-reset', { email })
  },

  // Reset de senha
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiRequest.post('/auth/reset-password', {
      token,
      new_password: newPassword
    })
  }
}

export default authService
