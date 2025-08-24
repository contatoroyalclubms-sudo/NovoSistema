import React, { useState } from 'react'
import { Link, useLocation, Outlet } from 'react-router-dom'
import { Button } from '../ui/button'
import { authService } from '../../services/auth'
import { 
  Home, 
  Calendar, 
  ShoppingCart, 
  Package, 
  Users, 
  BarChart3, 
  Settings, 
  LogOut,
  Menu,
  X,
  Bell
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Eventos', href: '/eventos', icon: Calendar },
  { name: 'PDV', href: '/pdv', icon: ShoppingCart },
  { name: 'Estoque', href: '/estoque', icon: Package },
  { name: 'Usuários', href: '/usuarios', icon: Users },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Relatórios', href: '/relatorios', icon: BarChart3 },
  { name: 'Notificações', href: '/notifications', icon: Bell },
  { name: 'Configurações', href: '/configuracoes', icon: Settings },
]

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const user = authService.getCurrentUser()

  const handleLogout = async () => {
    try {
      await authService.logout()
      window.location.href = '/login'
    } catch (error) {
      console.error('Erro ao fazer logout:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar para mobile */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div 
            className="fixed inset-0 bg-gray-600 bg-opacity-75"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 flex w-full max-w-xs flex-col bg-white shadow-xl">
            <div className="flex h-16 shrink-0 items-center justify-between px-6">
              <h1 className="text-xl font-bold text-gray-900">Sistema Painel</h1>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-6 w-6" />
              </Button>
            </div>
            <nav className="flex flex-1 flex-col px-6 py-4">
              <ul className="space-y-1">
                {navigation.map((item) => (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={`group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold ${
                        location.pathname === item.href
                          ? 'bg-gray-100 text-blue-600'
                          : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                      }`}
                      onClick={() => setSidebarOpen(false)}
                    >
                      <item.icon className="h-6 w-6 shrink-0" />
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
          </div>
        </div>
      )}

      {/* Sidebar para desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-gray-200 bg-white px-6">
          <div className="flex h-16 shrink-0 items-center">
            <h1 className="text-xl font-bold text-gray-900">Sistema Painel</h1>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul className="space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={`group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold ${
                          location.pathname === item.href
                            ? 'bg-gray-100 text-blue-600'
                            : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                        }`}
                      >
                        <item.icon className="h-6 w-6 shrink-0" />
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
              <li className="mt-auto">
                <div className="flex items-center gap-x-3 p-2 text-sm font-semibold text-gray-700">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200">
                    <span className="text-xs font-medium text-gray-600">
                      {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <span className="sr-only">Seu perfil</span>
                  <span>{user?.full_name || user?.username}</span>
                </div>
                <Button
                  variant="ghost"
                  className="w-full justify-start mt-2"
                  onClick={handleLogout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sair
                </Button>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Header para mobile */}
      <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:hidden">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSidebarOpen(true)}
        >
          <Menu className="h-5 w-5" />
        </Button>
        <div className="h-6 w-px bg-gray-200" />
        <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
          <div className="relative flex flex-1 items-center">
            <h1 className="text-lg font-semibold text-gray-900">Sistema Painel</h1>
          </div>
          <div className="flex items-center gap-x-4 lg:gap-x-6">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
            >
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Conteúdo principal */}
      <main className="lg:pl-72">
        <div className="px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
