import React, { useState } from 'react';
import './index.css';

function AppSimple() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (email === 'admin@teste.com' && password === 'admin123') {
      setIsLoggedIn(true);
      setError('');
    } else {
      setError('Email ou senha incorretos!');
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setEmail('');
    setPassword('');
  };

  if (isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-3xl font-bold text-gray-800">
                🎉 Sistema Universal de Eventos
              </h1>
              <button 
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Sair
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-lg text-white">
                <h2 className="text-xl font-semibold mb-2">📅 Eventos</h2>
                <p className="text-3xl font-bold">12</p>
                <p className="text-sm opacity-90">Eventos ativos</p>
              </div>
              
              <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-lg text-white">
                <h2 className="text-xl font-semibold mb-2">👥 Participantes</h2>
                <p className="text-3xl font-bold">1,234</p>
                <p className="text-sm opacity-90">Total confirmados</p>
              </div>
              
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-lg text-white">
                <h2 className="text-xl font-semibold mb-2">💰 Vendas</h2>
                <p className="text-3xl font-bold">R$ 45.678</p>
                <p className="text-sm opacity-90">Vendas do mês</p>
              </div>
            </div>
            
            <div className="mt-8 p-6 bg-gray-50 rounded-lg">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">✨ Funcionalidades</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button className="p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
                  <span className="text-2xl">🎪</span>
                  <p className="mt-2 text-sm">Eventos</p>
                </button>
                <button className="p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
                  <span className="text-2xl">✅</span>
                  <p className="mt-2 text-sm">Check-in</p>
                </button>
                <button className="p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
                  <span className="text-2xl">🛒</span>
                  <p className="mt-2 text-sm">PDV</p>
                </button>
                <button className="p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
                  <span className="text-2xl">🏆</span>
                  <p className="mt-2 text-sm">Ranking</p>
                </button>
                <button className="p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
                  <span className="text-2xl">📊</span>
                  <p className="mt-2 text-sm">Relatórios</p>
                </button>
                <button className="p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
                  <span className="text-2xl">💳</span>
                  <p className="mt-2 text-sm">Financeiro</p>
                </button>
                <button className="p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
                  <span className="text-2xl">🎮</span>
                  <p className="mt-2 text-sm">Gamificação</p>
                </button>
                <button className="p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
                  <span className="text-2xl">⚙️</span>
                  <p className="mt-2 text-sm">Configurações</p>
                </button>
              </div>
            </div>

            <div className="mt-8 text-center text-gray-600">
              <p>🏰 Powered by Torre Suprema - Sistema 100% Autônomo</p>
              <p className="text-sm mt-2">Versão 3.0.0 - Ultra Performance Edition</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🎉 Sistema de Eventos
          </h1>
          <p className="text-gray-600">Faça login para continuar</p>
        </div>
        
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="admin@teste.com"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Senha
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="admin123"
              required
            />
          </div>
          
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
              {error}
            </div>
          )}
          
          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition duration-200 font-semibold"
          >
            Entrar
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Credenciais de teste:</p>
          <p className="font-mono mt-1">admin@teste.com / admin123</p>
        </div>
      </div>
    </div>
  );
}

export default AppSimple;