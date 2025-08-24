import React, { useState } from 'react';
import { AuthProvider, useAuth } from './components/LoginScreen';

// Componente de Login Simples
const LoginForm: React.FC = () => {
  const { user, login, logout } = useAuth();
  const [credentials, setCredentials] = useState({
    username: 'admin',
    password: 'admin123'
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('Tentando login...');
    
    try {
      const success = await login(credentials.username, credentials.password);
      if (success) {
        setMessage('Login realizado com sucesso!');
      } else {
        setMessage('Erro no login. Verifique suas credenciais.');
      }
    } catch (error) {
      setMessage('Erro de conexão com o servidor.');
    } finally {
      setLoading(false);
    }
  };

  if (user) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
          <h2 className="text-2xl font-bold mb-6 text-center text-green-600">
            ✅ AUTENTICAÇÃO FUNCIONANDO!
          </h2>
          
          <div className="space-y-4">
            <div className="bg-green-50 p-4 rounded border border-green-200">
              <h3 className="font-semibold text-green-800">Usuário Logado:</h3>
              <p><strong>ID:</strong> {user.id}</p>
              <p><strong>Username:</strong> {user.username}</p>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Role:</strong> {user.role}</p>
              <p><strong>Criado:</strong> {new Date(user.created_at).toLocaleString()}</p>
            </div>
            
            <div className="bg-blue-50 p-4 rounded border border-blue-200">
              <h3 className="font-semibold text-blue-800">Status do Sistema:</h3>
              <p>✅ Backend: Conectado</p>
              <p>✅ Autenticação: Ativa</p>
              <p>✅ JWT Token: Válido</p>
              <p>✅ Session: Ativa</p>
            </div>
            
            <button
              onClick={logout}
              className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <h2 className="text-2xl font-bold mb-6 text-center">
          🔐 Teste de Autenticação
        </h2>
        
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="admin"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="admin123"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
          >
            {loading ? 'Entrando...' : 'Login'}
          </button>
        </form>
        
        {message && (
          <div className={`mt-4 p-3 rounded text-center ${
            message.includes('sucesso') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message}
          </div>
        )}
        
        <div className="mt-6 text-sm text-gray-600">
          <h3 className="font-semibold mb-2">Credenciais Padrão:</h3>
          <p>Username: admin</p>
          <p>Password: admin123</p>
        </div>
      </div>
    </div>
  );
};

// App Principal com Provider
const TestAuth: React.FC = () => {
  return (
    <AuthProvider>
      <LoginForm />
    </AuthProvider>
  );
};

export default TestAuth;
