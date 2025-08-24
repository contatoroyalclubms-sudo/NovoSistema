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
  image: string;
}

interface Sale {
  id: number;
  product: string;
  quantity: number;
  value: number;
  time: string;
  icon: string;
}

function AppUltraDesign() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('dashboard');
  const [notifications, setNotifications] = useState<string[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  
  // Estados para dados dinâmicos
  const [events, setEvents] = useState<Event[]>([
    { 
      id: 1, 
      name: 'Festival de Verão 2025', 
      date: '2025-09-15', 
      participants: 450, 
      revenue: 67500, 
      status: 'upcoming',
      image: '🎸'
    },
    { 
      id: 2, 
      name: 'Tech Conference SP', 
      date: '2025-08-30', 
      participants: 200, 
      revenue: 45000, 
      status: 'active',
      image: '💻'
    },
    { 
      id: 3, 
      name: 'Rock in Rio Experience', 
      date: '2025-07-20', 
      participants: 1500, 
      revenue: 225000, 
      status: 'completed',
      image: '🎪'
    },
  ]);
  
  const [recentSales, setRecentSales] = useState<Sale[]>([
    { id: 1, product: 'Ingresso VIP Gold', quantity: 2, value: 300, time: '14:23', icon: '🎫' },
    { id: 2, product: 'Cerveja Premium', quantity: 5, value: 50, time: '14:21', icon: '🍺' },
    { id: 3, product: 'Camiseta Oficial', quantity: 1, value: 80, time: '14:19', icon: '👕' },
  ]);

  const [animatedValues, setAnimatedValues] = useState({
    events: 0,
    participants: 0,
    revenue: 0,
    rate: 0
  });

  useEffect(() => {
    if (isLoggedIn) {
      // Animações de entrada com valores incrementais
      const animateValue = (key: string, target: number, duration: number) => {
        const step = target / (duration / 16);
        let current = 0;
        const timer = setInterval(() => {
          current = Math.min(current + step, target);
          setAnimatedValues(prev => ({ ...prev, [key]: Math.floor(current) }));
          if (current >= target) clearInterval(timer);
        }, 16);
      };

      animateValue('events', events.filter(e => e.status === 'active').length, 1000);
      animateValue('participants', events.reduce((sum, e) => sum + e.participants, 0), 1500);
      animateValue('revenue', events.reduce((sum, e) => sum + e.revenue, 0), 2000);
      animateValue('rate', 87, 1200);

      // Notificação de boas-vindas
      setTimeout(() => {
        addNotification('🎉 Bem-vindo ao Sistema Ultra Performance!');
      }, 500);

      // Simular atualizações em tempo real
      const salesTimer = setInterval(() => {
        const products = [
          { name: 'Ingresso Premium', icon: '🎫' },
          { name: 'Bebida Especial', icon: '🥤' },
          { name: 'Combo Gourmet', icon: '🍔' },
          { name: 'Kit Merchandise', icon: '🎁' }
        ];
        const selectedProduct = products[Math.floor(Math.random() * products.length)];
        
        const newSale: Sale = {
          id: Date.now(),
          product: selectedProduct.name,
          icon: selectedProduct.icon,
          quantity: Math.floor(Math.random() * 5) + 1,
          value: Math.floor(Math.random() * 200) + 20,
          time: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
        };
        
        setRecentSales(prev => [newSale, ...prev.slice(0, 4)]);
        addNotification(`💰 Nova venda: ${newSale.product} - R$ ${newSale.value}`);
      }, 10000);

      return () => clearInterval(salesTimer);
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
  };

  const createEvent = () => {
    const eventNames = [
      'Summer Festival', 'Music Experience', 'Tech Summit', 
      'Food & Wine', 'Sports Championship', 'Art Exhibition'
    ];
    const icons = ['🎵', '🎭', '🎨', '🏆', '🎪', '🎸'];
    
    const newEvent: Event = {
      id: Date.now(),
      name: eventNames[Math.floor(Math.random() * eventNames.length)] + ' ' + new Date().getFullYear(),
      date: new Date(Date.now() + Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      participants: Math.floor(Math.random() * 1000) + 200,
      revenue: Math.floor(Math.random() * 150000) + 25000,
      status: 'upcoming',
      image: icons[Math.floor(Math.random() * icons.length)]
    };
    
    setEvents([...events, newEvent]);
    addNotification(`✅ Evento "${newEvent.name}" criado com sucesso!`);
  };

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊', color: 'from-blue-500 to-blue-600' },
    { id: 'eventos', label: 'Eventos', icon: '🎪', color: 'from-purple-500 to-purple-600' },
    { id: 'checkin', label: 'Check-in', icon: '✅', color: 'from-green-500 to-green-600' },
    { id: 'pdv', label: 'PDV', icon: '🛒', color: 'from-orange-500 to-orange-600' },
    { id: 'financeiro', label: 'Financeiro', icon: '💰', color: 'from-yellow-500 to-yellow-600' },
    { id: 'relatorios', label: 'Relatórios', icon: '📈', color: 'from-indigo-500 to-indigo-600' },
    { id: 'config', label: 'Configurações', icon: '⚙️', color: 'from-gray-500 to-gray-600' },
  ];

  const renderDashboard = () => (
    <div className="space-y-8">
      {/* Header Stats com Glassmorphism */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-pink-600 to-purple-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative bg-white dark:bg-gray-900 p-6 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-4xl">📅</span>
              <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-xs font-bold">
                +12%
              </span>
            </div>
            <h3 className="text-gray-600 dark:text-gray-400 text-sm font-medium">Eventos Ativos</h3>
            <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {animatedValues.events}
            </p>
            <div className="mt-4 bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-1500 ease-out"
                style={{ width: `${(animatedValues.events / 5) * 100}%` }}
              />
            </div>
          </div>
        </div>

        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-green-600 to-teal-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative bg-white dark:bg-gray-900 p-6 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-4xl">👥</span>
              <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-xs font-bold">
                +23%
              </span>
            </div>
            <h3 className="text-gray-600 dark:text-gray-400 text-sm font-medium">Total Participantes</h3>
            <p className="text-3xl font-bold bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent">
              {animatedValues.participants.toLocaleString('pt-BR')}
            </p>
            <div className="mt-4 flex space-x-1">
              {[1,2,3,4,5].map(i => (
                <div 
                  key={i}
                  className="flex-1 h-8 bg-gradient-to-t from-green-500 to-teal-400 rounded"
                  style={{ 
                    height: `${Math.random() * 20 + 10}px`,
                    opacity: 0.6 + (i * 0.08)
                  }}
                />
              ))}
            </div>
          </div>
        </div>

        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative bg-white dark:bg-gray-900 p-6 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-4xl">💰</span>
              <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full text-xs font-bold">
                +45%
              </span>
            </div>
            <h3 className="text-gray-600 dark:text-gray-400 text-sm font-medium">Receita Total</h3>
            <p className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              R$ {animatedValues.revenue.toLocaleString('pt-BR')}
            </p>
            <div className="mt-4 relative h-16">
              <svg className="w-full h-full">
                <polyline
                  fill="none"
                  stroke="url(#gradient)"
                  strokeWidth="3"
                  points="0,40 20,30 40,35 60,20 80,25 100,10 120,15 140,5"
                />
                <defs>
                  <linearGradient id="gradient">
                    <stop offset="0%" stopColor="#9333ea" />
                    <stop offset="100%" stopColor="#ec4899" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>
        </div>

        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-600 to-red-600 rounded-2xl blur opacity-50 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative bg-white dark:bg-gray-900 p-6 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <span className="text-4xl">📈</span>
              <span className="px-3 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded-full text-xs font-bold">
                TOP
              </span>
            </div>
            <h3 className="text-gray-600 dark:text-gray-400 text-sm font-medium">Taxa de Ocupação</h3>
            <p className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
              {animatedValues.rate}%
            </p>
            <div className="mt-4 relative">
              <div className="flex items-center justify-center">
                <div className="relative w-20 h-20">
                  <svg className="transform -rotate-90 w-20 h-20">
                    <circle
                      cx="40"
                      cy="40"
                      r="36"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      className="text-gray-200 dark:text-gray-700"
                    />
                    <circle
                      cx="40"
                      cy="40"
                      r="36"
                      stroke="url(#gradient2)"
                      strokeWidth="8"
                      fill="none"
                      strokeDasharray={`${animatedValues.rate * 2.26} 226`}
                      className="transition-all duration-1500 ease-out"
                    />
                    <defs>
                      <linearGradient id="gradient2">
                        <stop offset="0%" stopColor="#ea580c" />
                        <stop offset="100%" stopColor="#dc2626" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Vendas em Tempo Real - Ultra Design */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                💳 Vendas em Tempo Real
              </h2>
              <div className="flex items-center space-x-2">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400">Live</span>
              </div>
            </div>
            
            <div className="space-y-4">
              {recentSales.map((sale, index) => (
                <div 
                  key={sale.id}
                  className="group relative overflow-hidden bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-5 transition-all duration-300 hover:shadow-lg hover:scale-[1.02]"
                  style={{
                    animation: index === 0 ? 'slideInRight 0.5s ease-out' : 'none'
                  }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  
                  <div className="relative flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-4xl animate-bounce">{sale.icon}</div>
                      <div>
                        <p className="font-bold text-gray-800 dark:text-gray-200 text-lg">{sale.product}</p>
                        <div className="flex items-center space-x-3 mt-1">
                          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-lg text-xs font-medium">
                            Qtd: {sale.quantity}
                          </span>
                          <span className="text-gray-500 dark:text-gray-400 text-sm">
                            {sale.time}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-2xl font-bold bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent">
                        R$ {sale.value.toLocaleString('pt-BR')}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        +2.5% tax
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions - Ultra Modern */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-purple-600 to-pink-600 rounded-3xl p-8 text-white">
            <h3 className="text-xl font-bold mb-4">⚡ Ações Rápidas</h3>
            <div className="space-y-3">
              <button className="w-full bg-white/20 backdrop-blur hover:bg-white/30 transition-all duration-300 rounded-xl p-4 text-left group">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Novo Evento</span>
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </button>
              <button className="w-full bg-white/20 backdrop-blur hover:bg-white/30 transition-all duration-300 rounded-xl p-4 text-left group">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Gerar QR Code</span>
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </button>
              <button className="w-full bg-white/20 backdrop-blur hover:bg-white/30 transition-all duration-300 rounded-xl p-4 text-left group">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Relatório Rápido</span>
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </button>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-white dark:bg-gray-900 rounded-3xl p-6 shadow-xl">
            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4">🚀 Performance</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 dark:text-gray-400">CPU</span>
                  <span className="font-medium">23%</span>
                </div>
                <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full" style={{ width: '23%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 dark:text-gray-400">Memory</span>
                  <span className="font-medium">45%</span>
                </div>
                <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-yellow-500 to-yellow-600 h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 dark:text-gray-400">Storage</span>
                  <span className="font-medium">67%</span>
                </div>
                <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-orange-500 to-orange-600 h-2 rounded-full" style={{ width: '67%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderEvents = () => (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            🎪 Gestão de Eventos
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Gerencie todos os seus eventos em um só lugar</p>
        </div>
        <button 
          onClick={createEvent}
          className="group relative px-6 py-3 font-bold text-white rounded-xl overflow-hidden"
        >
          <span className="absolute inset-0 w-full h-full bg-gradient-to-br from-purple-600 to-pink-600"></span>
          <span className="absolute inset-0 w-full h-full bg-gradient-to-br from-purple-600 to-pink-600 blur opacity-50 group-hover:opacity-75 transition duration-300"></span>
          <span className="relative flex items-center space-x-2">
            <span>+ Criar Novo Evento</span>
            <span className="group-hover:translate-x-1 transition-transform">✨</span>
          </span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {events.map((event, index) => (
          <div 
            key={event.id} 
            className="group relative"
            style={{
              animation: `fadeInUp 0.5s ease-out ${index * 0.1}s both`
            }}
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl blur opacity-30 group-hover:opacity-60 transition duration-300"></div>
            <div className="relative bg-white dark:bg-gray-900 rounded-3xl overflow-hidden shadow-xl">
              {/* Header do Card */}
              <div className="h-32 bg-gradient-to-br from-purple-600 to-pink-600 p-6 relative overflow-hidden">
                <div className="absolute top-4 right-4 text-6xl opacity-20">{event.image}</div>
                <div className="relative z-10">
                  <h3 className="text-xl font-bold text-white mb-2">{event.name}</h3>
                  <span className={`inline-flex px-3 py-1 rounded-full text-xs font-bold ${
                    event.status === 'active' 
                      ? 'bg-green-400/30 text-green-100 border border-green-400/50' 
                      : event.status === 'upcoming' 
                      ? 'bg-blue-400/30 text-blue-100 border border-blue-400/50'
                      : 'bg-gray-400/30 text-gray-100 border border-gray-400/50'
                  }`}>
                    <span className="mr-1">
                      {event.status === 'active' ? '🟢' : event.status === 'upcoming' ? '🔵' : '⚪'}
                    </span>
                    {event.status === 'active' ? 'Ativo' : event.status === 'upcoming' ? 'Próximo' : 'Concluído'}
                  </span>
                </div>
              </div>
              
              {/* Body do Card */}
              <div className="p-6">
                <div className="space-y-3 mb-6">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400 text-sm">📅 Data</span>
                    <span className="font-semibold">{new Date(event.date).toLocaleDateString('pt-BR')}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400 text-sm">👥 Participantes</span>
                    <span className="font-semibold">{event.participants.toLocaleString('pt-BR')}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400 text-sm">💰 Receita</span>
                    <span className="font-bold text-green-600">R$ {event.revenue.toLocaleString('pt-BR')}</span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button className="flex-1 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-300">
                    Editar
                  </button>
                  <button className="flex-1 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-300">
                    QR Code
                  </button>
                  <button className="p-2 bg-gray-100 dark:bg-gray-800 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
                    ⋮
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (isLoggedIn) {
    return (
      <div className={`min-h-screen ${darkMode ? 'dark bg-gray-950' : 'bg-gray-50'} transition-colors duration-300`}>
        {/* Sidebar Ultra Modern */}
        <aside className={`fixed top-0 left-0 h-full bg-white dark:bg-gray-900 shadow-2xl transition-all duration-300 z-40 ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}>
          <div className="p-6">
            <div className="flex items-center justify-between mb-8">
              <h1 className={`font-bold text-xl bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent transition-all duration-300 ${
                sidebarOpen ? 'opacity-100' : 'opacity-0 w-0'
              }`}>
                Torre Suprema
              </h1>
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                {sidebarOpen ? '←' : '→'}
              </button>
            </div>
            
            <nav className="space-y-2">
              {menuItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group ${
                    currentView === item.id 
                      ? 'bg-gradient-to-r ' + item.color + ' text-white shadow-lg scale-105'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <span className="text-2xl">{item.icon}</span>
                  <span className={`font-medium transition-all duration-300 ${
                    sidebarOpen ? 'opacity-100' : 'opacity-0 w-0'
                  }`}>
                    {item.label}
                  </span>
                </button>
              ))}
            </nav>
          </div>

          {/* User Section */}
          <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-gray-200 dark:border-gray-800">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white font-bold">
                A
              </div>
              <div className={`transition-all duration-300 ${sidebarOpen ? 'opacity-100' : 'opacity-0 w-0'}`}>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Admin</p>
                <p className="text-xs text-gray-500 dark:text-gray-500">{email}</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <div className={`transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
          {/* Top Bar */}
          <header className="bg-white dark:bg-gray-900 shadow-lg">
            <div className="px-8 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                    {menuItems.find(item => item.id === currentView)?.icon} {menuItems.find(item => item.id === currentView)?.label}
                  </h2>
                  <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-xs font-bold flex items-center space-x-1">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                    </span>
                    <span>Online</span>
                  </span>
                </div>
                
                <div className="flex items-center space-x-4">
                  {/* Dark Mode Toggle */}
                  <button
                    onClick={() => setDarkMode(!darkMode)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                  >
                    {darkMode ? '☀️' : '🌙'}
                  </button>
                  
                  {/* Notifications */}
                  <button className="relative p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
                    <span>🔔</span>
                    {notifications.length > 0 && (
                      <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
                    )}
                  </button>
                  
                  {/* Logout */}
                  <button 
                    onClick={handleLogout}
                    className="px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-300"
                  >
                    Sair
                  </button>
                </div>
              </div>
            </div>
          </header>

          {/* Notifications Toast */}
          <div className="fixed top-20 right-8 z-50 space-y-3">
            {notifications.map((notif, index) => (
              <div 
                key={index}
                className="bg-white dark:bg-gray-900 shadow-2xl rounded-2xl p-5 min-w-[300px] border-l-4 border-purple-600"
                style={{
                  animation: 'slideInRight 0.3s ease-out'
                }}
              >
                <p className="text-gray-800 dark:text-gray-200 font-medium">{notif}</p>
              </div>
            ))}
          </div>

          {/* Page Content */}
          <main className="p-8">
            {currentView === 'dashboard' && renderDashboard()}
            {currentView === 'eventos' && renderEvents()}
            {currentView === 'checkin' && (
              <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl p-10">
                <h2 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent mb-8">
                  ✅ Sistema de Check-in Inteligente
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                  <button className="group relative p-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl text-white overflow-hidden hover:scale-105 transition-transform duration-300">
                    <span className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></span>
                    <span className="relative">
                      <span className="text-5xl mb-4 block">📷</span>
                      <span className="text-xl font-bold">Escanear QR Code</span>
                    </span>
                  </button>
                  <button className="group relative p-8 bg-gradient-to-br from-green-500 to-green-600 rounded-3xl text-white overflow-hidden hover:scale-105 transition-transform duration-300">
                    <span className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></span>
                    <span className="relative">
                      <span className="text-5xl mb-4 block">🔍</span>
                      <span className="text-xl font-bold">Buscar por CPF</span>
                    </span>
                  </button>
                </div>
              </div>
            )}
            {currentView === 'pdv' && (
              <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl p-10">
                <h2 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-8">
                  🛒 Ponto de Venda Ultra Rápido
                </h2>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                  {[
                    { name: 'Ingressos', icon: '🎫', color: 'from-purple-500 to-purple-600' },
                    { name: 'Bebidas', icon: '🥤', color: 'from-blue-500 to-blue-600' },
                    { name: 'Comidas', icon: '🍔', color: 'from-green-500 to-green-600' },
                    { name: 'Merchandise', icon: '🎁', color: 'from-orange-500 to-orange-600' },
                  ].map(item => (
                    <button 
                      key={item.name}
                      className={`group relative p-8 bg-gradient-to-br ${item.color} rounded-3xl text-white overflow-hidden hover:scale-105 transition-all duration-300`}
                    >
                      <span className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></span>
                      <span className="relative">
                        <span className="text-5xl mb-4 block group-hover:animate-bounce">{item.icon}</span>
                        <span className="text-xl font-bold">{item.name}</span>
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </main>

          {/* Footer */}
          <footer className="mt-auto p-8 text-center text-gray-600 dark:text-gray-400">
            <p className="font-medium">🏰 Powered by Torre Suprema - Sistema 100% Autônomo</p>
            <p className="text-sm mt-1">v3.0.0 Ultra Performance Edition | Design Ultra Supremo</p>
          </footer>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-pink-600 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500 rounded-full filter blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-pink-500 rounded-full filter blur-3xl opacity-30 animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-500 rounded-full filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Login Card */}
      <div className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
        <div className="relative bg-white dark:bg-gray-900 rounded-3xl shadow-2xl p-10 max-w-md w-full">
          <div className="text-center mb-8">
            <div className="inline-block p-4 bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl mb-4">
              <span className="text-5xl">🎉</span>
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
              Sistema de Eventos
            </h1>
            <p className="text-gray-600 dark:text-gray-400">Ultra Performance Edition</p>
          </div>
          
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-600/20 focus:border-purple-600 transition-all duration-300"
                placeholder="admin@teste.com"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Senha
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-600/20 focus:border-purple-600 transition-all duration-300"
                placeholder="admin123"
                required
              />
            </div>
            
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-xl text-sm font-medium">
                {error}
              </div>
            )}
            
            <button
              type="submit"
              className="relative w-full py-4 px-6 font-bold text-white rounded-xl overflow-hidden group"
            >
              <span className="absolute inset-0 w-full h-full bg-gradient-to-br from-purple-600 to-pink-600"></span>
              <span className="absolute inset-0 w-full h-full bg-gradient-to-br from-purple-600 to-pink-600 blur opacity-50 group-hover:opacity-75 transition duration-300"></span>
              <span className="relative">Entrar no Sistema</span>
            </button>
          </form>
          
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">Credenciais de teste:</p>
            <p className="font-mono text-sm mt-1 text-purple-600 dark:text-purple-400">admin@teste.com / admin123</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Add CSS animations
const style = document.createElement('style');
style.innerHTML = `
  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes fadeInUp {
    from {
      transform: translateY(20px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
`;
document.head.appendChild(style);

export default AppUltraDesign;