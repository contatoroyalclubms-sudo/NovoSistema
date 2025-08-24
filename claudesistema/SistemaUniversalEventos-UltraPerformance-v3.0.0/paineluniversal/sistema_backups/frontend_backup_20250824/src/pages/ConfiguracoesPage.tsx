import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { authService } from '../services/auth'
import { Settings, User, Key, Bell, Shield, Database } from 'lucide-react'

export default function ConfiguracoesPage() {
  const [user, setUser] = useState(authService.getCurrentUser())
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage('As senhas não coincidem')
      return
    }

    if (passwordData.newPassword.length < 6) {
      setMessage('A nova senha deve ter pelo menos 6 caracteres')
      return
    }

    try {
      setLoading(true)
      setMessage('')
      
      await authService.changePassword(passwordData.currentPassword, passwordData.newPassword)
      
      setMessage('Senha alterada com sucesso!')
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      })
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Erro ao alterar senha')
    } finally {
      setLoading(false)
    }
  }

  const handleLogoutAllDevices = async () => {
    if (confirm('Deseja realmente fazer logout de todos os dispositivos?')) {
      try {
        await authService.logout()
        window.location.href = '/login'
      } catch (error) {
        console.error('Erro ao fazer logout:', error)
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Settings className="h-8 w-8 mr-3" />
        <h1 className="text-3xl font-bold text-gray-900">Configurações</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Informações do Perfil */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="h-5 w-5 mr-2" />
              Perfil do Usuário
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Nome de Usuário</label>
              <Input
                value={user?.username || ''}
                disabled
                className="mt-1"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-700">Email</label>
              <Input
                value={user?.email || ''}
                disabled
                className="mt-1"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-700">Nome Completo</label>
              <Input
                value={user?.full_name || ''}
                disabled
                className="mt-1"
              />
            </div>

            <div className="pt-4">
              <p className="text-sm text-gray-500">
                Para alterar informações do perfil, entre em contato com o administrador.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Alteração de Senha */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Key className="h-5 w-5 mr-2" />
              Alterar Senha
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              {message && (
                <div className={`p-3 rounded ${
                  message.includes('sucesso') 
                    ? 'bg-green-50 border border-green-200 text-green-700'
                    : 'bg-red-50 border border-red-200 text-red-700'
                }`}>
                  {message}
                </div>
              )}

              <Input
                type="password"
                label="Senha Atual"
                value={passwordData.currentPassword}
                onChange={(e) => setPasswordData(prev => ({ 
                  ...prev, 
                  currentPassword: e.target.value 
                }))}
                required
                disabled={loading}
              />

              <Input
                type="password"
                label="Nova Senha"
                value={passwordData.newPassword}
                onChange={(e) => setPasswordData(prev => ({ 
                  ...prev, 
                  newPassword: e.target.value 
                }))}
                required
                disabled={loading}
                placeholder="Mínimo 6 caracteres"
              />

              <Input
                type="password"
                label="Confirmar Nova Senha"
                value={passwordData.confirmPassword}
                onChange={(e) => setPasswordData(prev => ({ 
                  ...prev, 
                  confirmPassword: e.target.value 
                }))}
                required
                disabled={loading}
              />

              <Button
                type="submit"
                disabled={loading}
                className="w-full"
              >
                {loading ? 'Alterando...' : 'Alterar Senha'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Configurações de Segurança */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              Segurança
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium">Status da Conta</h4>
                <p className="text-sm text-gray-500">
                  {user?.is_active ? 'Ativa' : 'Inativa'}
                </p>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                user?.is_active 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {user?.is_active ? 'Ativa' : 'Inativa'}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium">Tipo de Usuário</h4>
                <p className="text-sm text-gray-500">
                  {user?.is_superuser ? 'Administrador' : 'Usuário Padrão'}
                </p>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                user?.is_superuser 
                  ? 'bg-purple-100 text-purple-800' 
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {user?.is_superuser ? 'Admin' : 'User'}
              </div>
            </div>

            <div className="pt-4 border-t">
              <Button
                variant="destructive"
                onClick={handleLogoutAllDevices}
                className="w-full"
              >
                Fazer Logout de Todos os Dispositivos
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Configurações do Sistema */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="h-5 w-5 mr-2" />
              Sistema
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Backend URL</span>
                <span className="text-sm text-gray-500">localhost:8000</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Frontend URL</span>
                <span className="text-sm text-gray-500">localhost:4200</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Versão</span>
                <span className="text-sm text-gray-500">2.0.0</span>
              </div>
            </div>

            <div className="pt-4 border-t">
              <p className="text-xs text-gray-500">
                Sistema Universal de Gestão de Eventos
                <br />
                Desenvolvido com React + FastAPI
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Preferências */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Bell className="h-5 w-5 mr-2" />
              Preferências
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="text-sm font-medium">Notificações</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Novos eventos</span>
                    <input type="checkbox" defaultChecked className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Vendas concluídas</span>
                    <input type="checkbox" defaultChecked className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Estoque baixo</span>
                    <input type="checkbox" defaultChecked className="rounded" />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-sm font-medium">Interface</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Tema escuro</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Modo compacto</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Autoatualização</span>
                    <input type="checkbox" defaultChecked className="rounded" />
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t mt-6">
              <Button variant="outline" className="mr-3">
                Restaurar Padrões
              </Button>
              <Button>
                Salvar Preferências
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
