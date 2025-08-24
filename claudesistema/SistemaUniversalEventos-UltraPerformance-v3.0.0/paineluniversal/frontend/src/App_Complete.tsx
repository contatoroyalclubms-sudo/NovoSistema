import React, { useState, useEffect } from 'react';
import './index.css';

// Tipos
interface Event {
  id: number;
  name: string;
  date: string;
  participants: number;
  revenue: number;
  status: 'active' | 'completed' | 'upcoming';
}

interface Sale {
  id: number;
  product: string;
  quantity: number;
  value: number;
  time: string;
}

function AppComplete() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('dashboard');
  const [notifications, setNotifications] = useState<string[]>([]);
  
  // Estados para dados dinâmicos
  const [events, setEvents] = useState<Event[]>([
    { id: 1, name: 'Festival de Verão', date: '2025-09-15', participants: 450, revenue: 67500, status: 'upcoming' },
    { id: 2, name: 'Tech Conference', date: '2025-08-30', participants: 200, revenue: 45000, status: 'active' },
    { id: 3, name: 'Rock in Rio', date: '2025-07-20', participants: 1500, revenue: 225000, status: 'completed' },
  ]);
  
  const [recentSales, setRecentSales] = useState<Sale[]>([
    { id: 1, product: 'Ingresso VIP', quantity: 2, value: 300, time: '14:23' },
    { id: 2, product: 'Cerveja', quantity: 5, value: 50, time: '14:21' },
    { id: 3, product: 'Camiseta', quantity: 1, value: 80, time: '14:19' },
  ]);

  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    if (isLoggedIn) {
      // Animação de entrada
      const timer = setInterval(() => {
        setAnimatedValue(prev => {
          if (prev >= 100) {
            clearInterval(timer);
            return 100;
          }
          return prev + 5;
        });
      }, 30);

      // Notificação de boas-vindas
      setTimeout(() => {
        addNotification('🎉 Bem-vindo ao Sistema de Eventos!');
      }, 500);

      // Simular atualizações em tempo real
      const salesTimer = setInterval(() => {
        const newSale: Sale = {
          id: Date.now(),
          product: ['Ingresso', 'Bebida', 'Comida', 'Merchandise'][Math.floor(Math.random() * 4)],
          quantity: Math.floor(Math.random() * 5) + 1,
          value: Math.floor(Math.random() * 200) + 20,
          time: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
        };
        setRecentSales(prev => [newSale, ...prev.slice(0, 4)]);
        addNotification(`💰 Nova venda: ${newSale.product} - R$ ${newSale.value}`);
      }, 15000);

      return () => {
        clearInterval(salesTimer);
      };
    }
  }, [isLoggedIn]);

  const addNotification = (message: string) => {
    setNotifications(prev => [...prev, message]);
    setTimeout(() => {
      setNotifications(prev => prev.slice(1));
    }, 5000);
  };

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
    setCurrentView('dashboard');
    setAnimatedValue(0);
  };

  const createEvent = () => {
    const newEvent: Event = {
      id: Date.now(),
      name: `Novo Evento ${events.length + 1}`,
      date: new Date(Date.now() + Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      participants: Math.floor(Math.random() * 500) + 100,
      revenue: Math.floor(Math.random() * 100000) + 10000,
      status: 'upcoming'
    };
    setEvents([...events, newEvent]);
    addNotification(`✅ Evento "${newEvent.name}" criado com sucesso!`);
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Métricas animadas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-lg text-white transform hover:scale-105 transition-all">
          <h3 className="text-lg font-semibold mb-2">📅 Eventos Ativos</h3>
          <p className="text-3xl font-bold">{events.filter(e => e.status === 'active').length}</p>
          <div className="mt-2 bg-white/20 rounded-full h-2">
            <div 
              className="bg-white rounded-full h-2 transition-all duration-1000"
              style={{ width: `${animatedValue}%` }}
            />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-lg text-white transform hover:scale-105 transition-all">
          <h3 className="text-lg font-semibold mb-2">👥 Total Participantes</h3>
          <p className="text-3xl font-bold">
            {events.reduce((sum, e) => sum + e.participants, 0).toLocaleString('pt-BR')}
          </p>
        </div>
        
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-lg text-white transform hover:scale-105 transition-all">
          <h3 className="text-lg font-semibold mb-2">💰 Receita Total</h3>
          <p className="text-3xl font-bold">
            R$ {events.reduce((sum, e) => sum + e.revenue, 0).toLocaleString('pt-BR')}
          </p>
        </div>
        
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-6 rounded-lg text-white transform hover:scale-105 transition-all">
          <h3 className="text-lg font-semibold mb-2">📈 Taxa de Ocupação</h3>
          <p className="text-3xl font-bold">87%</p>
        </div>
      </div>

      {/* Vendas Recentes */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">💳 Vendas em Tempo Real</h2>
        <div className="space-y-3">
          {recentSales.map((sale, index) => (
            <div 
              key={sale.id} 
              className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
              style={{
                animation: index === 0 ? 'slideIn 0.5s ease-out' : 'none'
              }}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🛒</span>
                <div>
                  <p className="font-semibold">{sale.product}</p>
                  <p className="text-sm text-gray-600">Qtd: {sale.quantity} • {sale.time}</p>
                </div>
              </div>
              <span className="text-lg font-bold text-green-600">
                R$ {sale.value.toLocaleString('pt-BR')}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderEvents = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">🎪 Gestão de Eventos</h2>
        <button 
          onClick={createEvent}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          + Criar Novo Evento
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {events.map(event => (
          <div key={event.id} className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-bold text-gray-800">{event.name}</h3>
              <span className={`px-2 py-1 rounded text-xs font-semibold ${
                event.status === 'active' ? 'bg-green-100 text-green-800' :
                event.status === 'upcoming' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {event.status === 'active' ? 'Ativo' : 
                 event.status === 'upcoming' ? 'Próximo' : 'Concluído'}
              </span>
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <p>📅 {new Date(event.date).toLocaleDateString('pt-BR')}</p>
              <p>👥 {event.participants} participantes</p>
              <p>💰 R$ {event.revenue.toLocaleString('pt-BR')}</p>
            </div>
            <div className="mt-4 flex space-x-2">
              <button className="flex-1 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">
                Editar
              </button>
              <button className="flex-1 px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600">
                QR Code
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (isLoggedIn) {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Header */}
        <header className="bg-white shadow-md">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <h1 className="text-2xl font-bold text-gray-800">
                  🎉 Sistema Universal de Eventos
                </h1>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                  Online
                </span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-gray-600">👤 {email}</span>
                <button 
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition"
                >
                  Sair
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Navegação */}
        <nav className="bg-indigo-600 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8 py-3">
              {['dashboard', 'eventos', 'checkin', 'pdv', 'relatorios'].map(item => (
                <button
                  key={item}
                  onClick={() => setCurrentView(item)}
                  className={`px-3 py-1 rounded transition ${
                    currentView === item ? 'bg-indigo-700' : 'hover:bg-indigo-500'
                  }`}
                >
                  {item.charAt(0).toUpperCase() + item.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* Notificações */}
        <div className="fixed top-20 right-4 z-50 space-y-2">
          {notifications.map((notif, index) => (
            <div 
              key={index}
              className="bg-white shadow-lg rounded-lg p-4 min-w-[250px] animate-slideIn"
            >
              {notif}
            </div>
          ))}
        </div>

        {/* Conteúdo Principal */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {currentView === 'dashboard' && renderDashboard()}
          {currentView === 'eventos' && renderEvents()}
          {currentView === 'checkin' && (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <h2 className="text-2xl font-bold mb-4">✅ Sistema de Check-in</h2>
              <p className="text-gray-600 mb-6">Escaneie QR Codes ou busque por CPF</p>
              <div className="space-y-4 max-w-md mx-auto">
                <button className="w-full p-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
                  📷 Escanear QR Code
                </button>
                <button className="w-full p-4 bg-green-500 text-white rounded-lg hover:bg-green-600">
                  🔍 Buscar por CPF
                </button>
              </div>
            </div>
          )}
          {currentView === 'pdv' && (
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-4">🛒 Ponto de Venda</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {['Ingresso', 'Bebida', 'Comida', 'Merchandise'].map(item => (
                  <button 
                    key={item}
                    className="p-6 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          )}
          {currentView === 'relatorios' && (
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-4">📊 Relatórios</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button className="p-4 border-2 border-gray-300 rounded-lg hover:border-blue-500">
                  📈 Relatório de Vendas
                </button>
                <button className="p-4 border-2 border-gray-300 rounded-lg hover:border-blue-500">
                  👥 Relatório de Participantes
                </button>
                <button className="p-4 border-2 border-gray-300 rounded-lg hover:border-blue-500">
                  💰 Relatório Financeiro
                </button>
                <button className="p-4 border-2 border-gray-300 rounded-lg hover:border-blue-500">
                  🏆 Relatório de Performance
                </button>
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="bg-gray-800 text-white py-4 mt-12">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p>🏰 Powered by Torre Suprema - Sistema 100% Autônomo</p>
            <p className="text-sm mt-1">v3.0.0 Ultra Performance Edition</p>
          </div>
        </footer>
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

export default AppComplete;