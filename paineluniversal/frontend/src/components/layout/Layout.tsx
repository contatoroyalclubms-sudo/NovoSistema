import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Calendar, 
  Users, 
  Building2, 
  BarChart3, 
  FileText, 
  Settings, 
  LogOut,
  Menu,
  X,
  ShoppingCart,
  UserCheck,
  Smartphone,
  DollarSign,
  Trophy
} from 'lucide-react';
import { useState } from 'react';

interface LayoutProps {
  children?: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { icon: BarChart3, label: 'Dashboard', path: '/dashboard', roles: ['admin', 'promoter', 'operador'] },
    { icon: Calendar, label: 'Eventos', path: '/eventos', roles: ['admin', 'promoter'] },
    { icon: ShoppingCart, label: 'Vendas', path: '/vendas', roles: ['admin', 'promoter', 'operador'] },
    { icon: UserCheck, label: 'Check-in Inteligente', path: '/checkin', roles: ['admin', 'promoter', 'operador'] },
    { icon: Smartphone, label: 'Check-in Mobile', path: '/mobile-checkin', roles: ['admin', 'promoter', 'operador'] },
    { icon: ShoppingCart, label: 'PDV', path: '/pdv', roles: ['admin', 'promoter'] },
    { icon: BarChart3, label: 'Dashboard PDV', path: '/pdv/dashboard', roles: ['admin', 'promoter'] },
    { icon: Users, label: 'Listas & Convidados', path: '/listas', roles: ['admin', 'promoter'] },
    { icon: DollarSign, label: 'Caixa & Financeiro', path: '/financeiro', roles: ['admin', 'promoter'] },
    { icon: Trophy, label: 'Ranking & Gamificação', path: '/ranking', roles: ['admin', 'promoter'] },
    { icon: Users, label: 'Usuários', path: '/usuarios', roles: ['admin'] },
    { icon: Building2, label: 'Empresas', path: '/empresas', roles: ['admin'] },
    { icon: FileText, label: 'Relatórios', path: '/relatorios', roles: ['admin', 'promoter'] },
    { icon: Settings, label: 'Configurações', path: '/configuracoes', roles: ['admin'] },
  ];

  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(usuario?.tipo || '')
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:inset-0
      `}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Sistema de Eventos</h1>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {filteredMenuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100 hover:text-gray-900 transition-colors"
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.label}
              </Link>
            ))}
          </div>
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center mb-3">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {usuario?.nome}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {usuario?.email}
              </p>
              <p className="text-xs text-gray-400 capitalize">
                {usuario?.tipo}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-sm font-medium text-red-700 rounded-md hover:bg-red-50 transition-colors"
          >
            <LogOut className="mr-3 h-4 w-4" />
            Sair
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600"
            >
              <Menu className="h-5 w-5" />
            </button>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Empresa: {usuario?.empresa_id}
              </span>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          {children || <Outlet />}
        </main>
      </div>
    </div>
  );
};

export default Layout;
