// Tipos para o sistema de autenticação
export interface User {
  id: string;
  nome: string;
  email: string;
  tipo: 'admin' | 'organizador' | 'operador' | 'participante';
  empresa_id?: string;
  foto_perfil?: string;
  ativo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface LoginCredentials {
  email: string;
  senha: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
  expires_in?: number;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateUser: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (roles: string[]) => boolean;
}

export interface TokenPayload {
  sub: string;
  email: string;
  tipo: string;
  exp: number;
  iat: number;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface ValidateTokenResponse {
  success: boolean;
  user?: User;
}

export interface APIError {
  detail: string;
  code?: string;
  status_code?: number;
}

// Enum para tipos de usuário
export enum UserType {
  ADMIN = 'admin',
  ORGANIZADOR = 'organizador',
  OPERADOR = 'operador',
  PARTICIPANTE = 'participante'
}

// Interface para permissões
export interface UserPermissions {
  canCreateEvents: boolean;
  canManageUsers: boolean;
  canViewReports: boolean;
  canManagePayments: boolean;
  canManageLists: boolean;
}
