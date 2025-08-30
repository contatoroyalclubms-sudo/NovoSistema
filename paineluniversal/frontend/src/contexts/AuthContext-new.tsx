import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, AuthContextType, LoginCredentials } from '../types/auth-types';
import authService from '../services/auth-service';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeAuth();
  }, []);

  /**
   * Inicializa o estado de autenticação
   */
  const initializeAuth = async () => {
    setIsLoading(true);
    
    try {
      if (authService.isAuthenticated()) {
        // Primeiro, tentar obter usuário do localStorage
        const cachedUser = authService.getUserFromStorage();
        if (cachedUser) {
          setUser(cachedUser);
        }

        // Verificar se token está expirado
        if (authService.isTokenExpired()) {
          console.log('Token expirado, tentando renovar...');
          await refreshToken();
          return;
        }

        // Validar token atual com o backend
        const isValid = await authService.validateToken();
        
        if (isValid) {
          // Se não tinha usuário em cache, buscar do backend
          if (!cachedUser) {
            const userData = await authService.getCurrentUser();
            setUser(userData);
          }
        } else {
          console.log('Token inválido, fazendo logout...');
          await logout();
        }
      }
    } catch (error) {
      console.error('Erro ao inicializar autenticação:', error);
      await logout();
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Realiza login do usuário
   */
  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      setIsLoading(true);
      const loginResponse = await authService.login(credentials);
      setUser(loginResponse.user);
    } catch (error) {
      setUser(null);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Realiza logout do usuário
   */
  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    } finally {
      setUser(null);
    }
  };

  /**
   * Atualiza o token de acesso
   */
  const refreshToken = async (): Promise<void> => {
    try {
      await authService.refreshToken();
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Erro ao renovar token:', error);
      await logout();
      throw error;
    }
  };

  /**
   * Atualiza dados do usuário
   */
  const updateUser = async (): Promise<void> => {
    try {
      if (authService.isAuthenticated()) {
        const userData = await authService.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      console.error('Erro ao atualizar dados do usuário:', error);
    }
  };

  /**
   * Verifica se usuário tem permissão específica
   */
  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    
    // Implementar lógica de permissões baseada no tipo de usuário
    switch (permission) {
      case 'manage_events':
        return ['admin', 'organizador'].includes(user.tipo);
      case 'manage_users':
        return user.tipo === 'admin';
      case 'view_reports':
        return ['admin', 'organizador'].includes(user.tipo);
      case 'manage_payments':
        return ['admin', 'organizador'].includes(user.tipo);
      case 'manage_lists':
        return ['admin', 'organizador', 'operador'].includes(user.tipo);
      default:
        return false;
    }
  };

  /**
   * Verifica se usuário tem um dos tipos especificados
   */
  const hasRole = (roles: string[]): boolean => {
    if (!user) return false;
    return roles.includes(user.tipo);
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    refreshToken,
    // Funções adicionais que podem ser úteis
    updateUser,
    hasPermission,
    hasRole,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Hook para usar o contexto de autenticação
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};

export default AuthContext;
