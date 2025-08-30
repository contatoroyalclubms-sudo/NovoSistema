import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at?: string;
  last_login?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<boolean>;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface RegisterData {
  username: string;
  email: string;
  full_name: string;
  password: string;
  role?: string;
}

const AuthContext = React.createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('auth_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('auth_token');
      if (savedToken) {
        try {
          const response = await fetch('http://localhost:8005/api/auth/validate', {
            headers: {
              'Authorization': `Bearer ${savedToken}`,
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            const data = await response.json();
            setUser(data.user);
            setToken(savedToken);
          } else {
            localStorage.removeItem('auth_token');
            setToken(null);
          }
        } catch (error) {
          console.error('Erro ao validar token:', error);
          localStorage.removeItem('auth_token');
          setToken(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8005/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setUser(data.user);
        setToken(data.access_token);
        localStorage.setItem('auth_token', data.access_token);
        return true;
      } else {
        console.error('Erro no login:', data.detail || data.message);
        return false;
      }
    } catch (error) {
      console.error('Erro no login:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: RegisterData): Promise<boolean> => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8005/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        return true;
      } else {
        console.error('Erro no registro:', data.detail || data.message);
        return false;
      }
    } catch (error) {
      console.error('Erro no registro:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await fetch('http://localhost:8005/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Erro no logout:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('auth_token');
    }
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    register,
    isAuthenticated: !!user && !!token,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const LoginScreen: React.FC = () => {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    full_name: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);
    setIsLoading(true);

    try {
      if (isLoginMode) {
        // Login
        if (!formData.username || !formData.password) {
          setErrors(['Username e senha são obrigatórios']);
          return;
        }

        const success = await login(formData.username, formData.password);
        if (success) {
          navigate('/dashboard');
        } else {
          setErrors(['Username ou senha inválidos']);
        }
      } else {
        // Registro
        const newErrors: string[] = [];
        
        if (!formData.username) newErrors.push('Username é obrigatório');
        if (!formData.email) newErrors.push('Email é obrigatório');
        if (!formData.full_name) newErrors.push('Nome completo é obrigatório');
        if (!formData.password) newErrors.push('Senha é obrigatória');
        if (formData.password !== formData.confirmPassword) {
          newErrors.push('Senhas não conferem');
        }
        if (formData.password && formData.password.length < 6) {
          newErrors.push('Senha deve ter pelo menos 6 caracteres');
        }

        if (newErrors.length > 0) {
          setErrors(newErrors);
          return;
        }

        const success = await register({
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          password: formData.password,
        });

        if (success) {
          setIsLoginMode(true);
          setFormData({ username: formData.username, password: '', email: '', full_name: '', confirmPassword: '' });
          setErrors(['Conta criada com sucesso! Faça login para continuar.']);
        } else {
          setErrors(['Erro ao criar conta. Tente novamente.']);
        }
      }
    } catch (error) {
      setErrors(['Erro interno. Tente novamente.']);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '16px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
        padding: '32px',
        width: '100%',
        maxWidth: '400px'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: 'bold',
            color: '#1e293b',
            marginBottom: '8px'
          }}>
            Sistema Universal v4.0
          </h1>
          <p style={{
            color: '#64748b',
            fontSize: '14px'
          }}>
            {isLoginMode ? 'Faça login para continuar' : 'Crie sua conta'}
          </p>
        </div>

        {/* Errors */}
        {errors.length > 0 && (
          <div style={{
            backgroundColor: errors[0].includes('sucesso') ? '#dcfce7' : '#fef2f2',
            border: errors[0].includes('sucesso') ? '1px solid #bbf7d0' : '1px solid #fecaca',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '24px'
          }}>
            {errors.map((error, index) => (
              <p key={index} style={{
                color: errors[0].includes('sucesso') ? '#166534' : '#dc2626',
                fontSize: '14px',
                margin: 0
              }}>
                {error}
              </p>
            ))}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {/* Username */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '6px'
            }}>
              Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
              placeholder="Digite seu username"
              required
            />
          </div>

          {/* Email (apenas para registro) */}
          {!isLoginMode && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '6px'
              }}>
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
                placeholder="seu@email.com"
                required
              />
            </div>
          )}

          {/* Nome completo (apenas para registro) */}
          {!isLoginMode && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '6px'
              }}>
                Nome Completo
              </label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
                placeholder="Seu nome completo"
                required
              />
            </div>
          )}

          {/* Password */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '6px'
            }}>
              Senha
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
              placeholder="Digite sua senha"
              required
            />
          </div>

          {/* Confirm Password (apenas para registro) */}
          {!isLoginMode && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '6px'
              }}>
                Confirmar Senha
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
                placeholder="Confirme sua senha"
                required
              />
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              backgroundColor: isLoading ? '#9ca3af' : '#3b82f6',
              color: 'white',
              padding: '12px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s'
            }}
          >
            {isLoading ? 'Carregando...' : (isLoginMode ? 'Entrar' : 'Criar Conta')}
          </button>
        </form>

        {/* Toggle Mode */}
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <p style={{ color: '#64748b', fontSize: '14px', margin: 0 }}>
            {isLoginMode ? 'Não tem uma conta? ' : 'Já tem uma conta? '}
            <button
              type="button"
              onClick={() => {
                setIsLoginMode(!isLoginMode);
                setErrors([]);
                setFormData({ username: '', password: '', email: '', full_name: '', confirmPassword: '' });
              }}
              style={{
                background: 'none',
                border: 'none',
                color: '#3b82f6',
                textDecoration: 'underline',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              {isLoginMode ? 'Criar conta' : 'Fazer login'}
            </button>
          </p>
        </div>

        {/* Demo Credentials */}
        {isLoginMode && (
          <div style={{
            marginTop: '24px',
            padding: '16px',
            backgroundColor: '#f1f5f9',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <p style={{
              fontSize: '12px',
              color: '#64748b',
              margin: '0 0 8px 0',
              fontWeight: '500'
            }}>
              Credenciais de Demonstração:
            </p>
            <p style={{
              fontSize: '12px',
              color: '#475569',
              margin: 0
            }}>
              <strong>Username:</strong> admin<br />
              <strong>Senha:</strong> admin123
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoginScreen;
