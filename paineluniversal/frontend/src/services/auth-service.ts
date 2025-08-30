import api, { handleApiError, clearTokens, saveTokens } from '../lib/api';
import { LoginCredentials, LoginResponse, User, ValidateTokenResponse } from '../types/auth-types';

class AuthService {
  /**
   * Realiza login do usuário
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await api.post('/api/v1/auth/login', {
        email: credentials.email,
        senha: credentials.senha // Backend espera 'senha'
      });
      
      const data = response.data;
      
      // Salvar tokens no localStorage
      saveTokens(data.access_token, data.refresh_token);
      
      // Salvar dados do usuário
      localStorage.setItem('user', JSON.stringify(data.user));
      
      return data;
    } catch (error: any) {
      const errorMessage = handleApiError(error);
      throw new Error(errorMessage);
    }
  }

  /**
   * Realiza logout do usuário
   */
  async logout(): Promise<void> {
    try {
      // Tentar fazer logout no backend
      await api.post('/api/v1/auth/logout');
    } catch (error) {
      console.error('Erro ao fazer logout no backend:', error);
      // Não propagar erro, sempre limpar tokens localmente
    } finally {
      // Sempre limpar tokens localmente
      clearTokens();
    }
  }

  /**
   * Atualiza o access token usando refresh token
   */
  async refreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('Refresh token não encontrado');
    }

    try {
      const response = await api.post('/api/v1/auth/refresh', {
        refresh_token: refreshToken
      });
      
      const { access_token, refresh_token: newRefreshToken } = response.data;
      
      // Salvar novos tokens
      saveTokens(access_token, newRefreshToken);
      
      return access_token;
    } catch (error) {
      // Se refresh falhar, limpar tokens
      clearTokens();
      throw new Error('Sessão expirada. Faça login novamente.');
    }
  }

  /**
   * Obtém dados do usuário atual
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get('/api/v1/auth/me');
      
      // Estrutura da resposta do backend: { success: true, data: user }
      const userData = response.data.data || response.data.user || response.data;
      
      // Salvar dados atualizados do usuário
      localStorage.setItem('user', JSON.stringify(userData));
      
      return userData;
    } catch (error: any) {
      const errorMessage = handleApiError(error);
      throw new Error(errorMessage);
    }
  }

  /**
   * Valida se o token atual é válido
   */
  async validateToken(): Promise<boolean> {
    try {
      const response = await api.post('/api/v1/auth/validate');
      const data: ValidateTokenResponse = response.data;
      
      return data.success;
    } catch (error) {
      console.error('Erro ao validar token:', error);
      return false;
    }
  }

  /**
   * Verifica se o usuário está autenticado (tem token)
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  /**
   * Obtém dados do usuário do localStorage
   */
  getUserFromStorage(): User | null {
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        return JSON.parse(userStr);
      }
    } catch (error) {
      console.error('Erro ao obter usuário do localStorage:', error);
    }
    return null;
  }

  /**
   * Verifica se o token está expirado (básico)
   */
  isTokenExpired(): boolean {
    const token = localStorage.getItem('access_token');
    
    if (!token) return true;
    
    try {
      // Decodificar JWT básico (apenas para verificar expiração)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      
      return payload.exp < currentTime;
    } catch (error) {
      console.error('Erro ao verificar expiração do token:', error);
      return true;
    }
  }

  /**
   * Força atualização dos dados do usuário
   */
  async refreshUserData(): Promise<User> {
    try {
      return await this.getCurrentUser();
    } catch (error) {
      throw new Error('Erro ao atualizar dados do usuário');
    }
  }
}

// Instância singleton do serviço
export const authService = new AuthService();
export default authService;
