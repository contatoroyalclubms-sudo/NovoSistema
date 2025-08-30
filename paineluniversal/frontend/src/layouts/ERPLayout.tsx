import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { ERPNavigation } from '@/components/erp/ERPNavigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  Bell, 
  Search, 
  Menu, 
  X, 
  User, 
  Settings, 
  LogOut, 
  HelpCircle,
  Zap,
  Activity,
  Shield
} from 'lucide-react';
import { cn } from '@/lib/utils';

export const ERPLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [notifications, setNotifications] = useState(3);
  const location = useLocation();

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Get current module info based on path
  const getCurrentModuleInfo = () => {
    const path = location.pathname;
    if (path.includes('/core')) return { name: 'Core', color: 'bg-blue-500' };
    if (path.includes('/sales')) return { name: 'Vendas', color: 'bg-green-500' };
    if (path.includes('/financial')) return { name: 'Financeiro', color: 'bg-yellow-500' };
    if (path.includes('/inventory')) return { name: 'Estoque', color: 'bg-purple-500' };
    if (path.includes('/crm')) return { name: 'CRM', color: 'bg-pink-500' };
    if (path.includes('/operations')) return { name: 'Operações', color: 'bg-orange-500' };
    if (path.includes('/integrations')) return { name: 'Integrações', color: 'bg-indigo-500' };
    return { name: 'Dashboard ERP', color: 'bg-gray-500' };
  };

  const currentModule = getCurrentModuleInfo();

  return (
    <div className="h-screen bg-gray-50 flex overflow-hidden">
      {/* Sidebar */}
      <div className={cn(
        'transition-all duration-300 flex-shrink-0',
        sidebarOpen ? 'w-64' : 'w-0'
      )}>
        <div className={cn(
          'h-full transition-all duration-300',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}>
          <ERPNavigation />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Left Section */}
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleSidebar}
                className="p-2"
              >
                {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
              </Button>

              {/* Breadcrumb */}
              <div className="flex items-center gap-2">
                <div className={cn('w-3 h-3 rounded-full', currentModule.color)}></div>
                <span className="font-semibold text-gray-900">{currentModule.name}</span>
                <Badge variant="outline" className="ml-2">
                  Sprint 1
                </Badge>
              </div>
            </div>

            {/* Center Section - Search */}
            <div className="flex-1 max-w-md mx-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Buscar no ERP..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center gap-2">
              {/* System Status */}
              <div className="flex items-center gap-2 px-3 py-1 bg-green-100 rounded-full">
                <Activity className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-700">Online</span>
              </div>

              {/* Notifications */}
              <Button variant="ghost" size="sm" className="relative p-2">
                <Bell className="h-4 w-4" />
                {notifications > 0 && (
                  <Badge 
                    variant="destructive" 
                    className="absolute -top-1 -right-1 h-5 w-5 text-xs p-0 flex items-center justify-center"
                  >
                    {notifications}
                  </Badge>
                )}
              </Button>

              {/* User Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="p-1">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src="/avatar.jpg" />
                      <AvatarFallback>AD</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>
                    <div className="flex flex-col">
                      <span>Administrador</span>
                      <span className="text-xs text-gray-500">admin@novosistema.com</span>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <User className="mr-2 h-4 w-4" />
                    Perfil
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    Configurações
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Shield className="mr-2 h-4 w-4" />
                    Permissões
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <HelpCircle className="mr-2 h-4 w-4" />
                    Ajuda
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-red-600">
                    <LogOut className="mr-2 h-4 w-4" />
                    Sair
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto">
          <div className="h-full">
            <Outlet />
          </div>
        </main>

        {/* Bottom Status Bar */}
        <footer className="bg-white border-t border-gray-200 px-4 py-2">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-4">
              <span>ERP NovoSistema v2.0.0</span>
              <span>•</span>
              <span>Sprint 1 - Consolidação</span>
              <span>•</span>
              <div className="flex items-center gap-1">
                <Zap className="h-3 w-3 text-green-500" />
                <span>Sistema Online</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span>Última sincronização: há 2 min</span>
              <span>•</span>
              <span>74% Implementado</span>
            </div>
          </div>
        </footer>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};