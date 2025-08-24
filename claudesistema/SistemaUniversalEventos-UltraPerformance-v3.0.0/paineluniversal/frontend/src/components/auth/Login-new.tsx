import React, { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth-new';

const Login: React.FC = () => {
  const { login, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  
  const [credentials, setCredentials] = useState({
    email: '',
    senha: ''
  });
  const [loginLoading, setLoginLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirecionar se já estiver autenticado
  if (isAuthenticated) {
    const from = (location.state as any)?.from?.pathname || '/dashboard';
    return <Navigate to={from} replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoginLoading(true);

    try {
      await login(credentials);
    } catch (error: any) {
      setError(error.message || 'Erro ao fazer login');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <div className="text-center text-white">
          <div className="w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
      <div className="w-full max-w-md bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">
            Sistema de Eventos
          </h1>
          <p className="text-gray-300">Entre com suas credenciais</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 text-red-100 p-3 rounded-lg">
              {error}
            </div>
          )}
          
          <div className="space-y-2">
            <label htmlFor="email" className="block text-white text-sm font-medium">
              Email
            </label>
            <div className="relative">
              <input
                id="email"
                name="email"
                type="email"
                placeholder="seu@email.com"
                value={credentials.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 pl-10 bg-white/10 border border-white/20 text-white placeholder-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <div className="absolute left-3 top-3 w-4 h-4 text-gray-400">
                📧
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <label htmlFor="senha" className="block text-white text-sm font-medium">
              Senha
            </label>
            <div className="relative">
              <input
                id="senha"
                name="senha"
                type="password"
                placeholder="••••••••"
                value={credentials.senha}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 pl-10 bg-white/10 border border-white/20 text-white placeholder-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <div className="absolute left-3 top-3 w-4 h-4 text-gray-400">
                🔒
              </div>
            </div>
          </div>
          
          <button
            type="submit"
            disabled={loginLoading}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition-all duration-300 transform hover:scale-105"
          >
            {loginLoading ? (
              <div className="flex items-center justify-center">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Entrando...
              </div>
            ) : (
              'Entrar'
            )}
          </button>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-gray-400 text-sm">
            Esqueceu a senha? 
            <button className="text-purple-300 hover:text-purple-200 ml-1">
              Clique aqui
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
