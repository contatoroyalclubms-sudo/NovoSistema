import { useState, useEffect, createContext, useContext, ReactNode } from 'react'
import { authService } from '../services/auth'

// Tipos locais
interface User {
  id: string
  email: string
  name: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

interface LoginCredentials {
  email: string
  password: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<boolean>
  logout: () => void
  refreshAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true
  })

  // Verificar autenticação ao carregar
  useEffect(() => {
    const initAuth = async () => {
      const token = authService.getToken()
      const user = authService.getCurrentUser()

      if (token && user) {
        // Verificar se o token ainda é válido
        const verifiedUser = await authService.verifyToken()
        if (verifiedUser) {
          setAuthState({
            user: verifiedUser,
            token,
            isAuthenticated: true,
            isLoading: false
          })
        } else {
          setAuthState({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false
          })
        }
      } else {
        setAuthState({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false
        })
      }
    }

    initAuth()
  }, [])

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }))
      
      const authResponse = await authService.login(credentials)
      
      setAuthState({
        user: authResponse.user,
        token: authResponse.access_token,
        isAuthenticated: true,
        isLoading: false
      })
      
      return true
    } catch (error) {
      console.error('Erro no login:', error)
      setAuthState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false
      })
      return false
    }
  }

  const logout = () => {
    authService.logout()
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false
    })
  }

  const refreshAuth = async () => {
    const user = await authService.verifyToken()
    if (user) {
      setAuthState(prev => ({
        ...prev,
        user,
        isAuthenticated: true
      }))
    } else {
      logout()
    }
  }

  const value: AuthContextType = {
    ...authState,
    login,
    logout,
    refreshAuth
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
