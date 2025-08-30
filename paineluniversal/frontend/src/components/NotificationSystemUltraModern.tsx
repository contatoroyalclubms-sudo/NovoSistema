import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  Mail, 
  MessageCircle, 
  Smartphone, 
  Send, 
  Check, 
  X, 
  Clock, 
  Activity,
  BarChart3,
  Settings,
  Zap,
  Globe,
  Shield,
  Sparkles,
  Rocket,
  TrendingUp,
  Users,
  Eye,
  Play,
  Pause,
  RefreshCw,
  Download,
  Upload,
  Filter,
  Search,
  ChevronDown,
  ChevronRight,
  Star,
  Target,
  Database,
  Server,
  Cpu
} from 'lucide-react';
import { RealTimeDashboard, NeuralVisualization } from './AdvancedComponents';

// Interfaces
interface NotificationStats {
  total_notifications: number;
  success_rate: number;
  last_24h: number;
  queue_size: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_priority: Record<string, number>;
  is_processing: boolean;
}

interface NotificationTypes {
  types: string[];
  priorities: string[];
  statuses: string[];
}

interface SystemHealth {
  status: string;
  service: string;
  version: string;
  queue_size: number;
  is_processing: boolean;
  total_notifications: number;
  success_rate: number;
  timestamp: string;
}

// Componentes Visuais Ultra Modernos
const GlowCard: React.FC<{ children: React.ReactNode; className?: string; glow?: boolean }> = ({ 
  children, 
  className = '', 
  glow = false 
}) => (
  <div className={`
    relative bg-gradient-to-br from-white via-gray-50 to-blue-50 
    backdrop-blur-sm border border-white/20 rounded-2xl p-6 
    shadow-[0_8px_32px_rgba(0,0,0,0.1)] 
    ${glow ? 'shadow-[0_0_40px_rgba(59,130,246,0.3)]' : ''}
    hover:shadow-[0_12px_48px_rgba(0,0,0,0.15)] 
    hover:scale-[1.02] 
    transition-all duration-500 ease-out
    ${className}
  `}>
    {glow && (
      <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 via-purple-400/20 to-pink-400/20 rounded-2xl blur-xl -z-10" />
    )}
    {children}
  </div>
);

const MetricCard: React.FC<{ 
  icon: React.ReactNode; 
  title: string; 
  value: string | number; 
  subtitle: string;
  trend?: 'up' | 'down' | 'stable';
  color: string;
}> = ({ icon, title, value, subtitle, trend = 'stable', color }) => (
  <GlowCard className="relative overflow-hidden">
    <div className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${color} opacity-10 rounded-full transform translate-x-8 -translate-y-8`} />
    
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-2">
          <div className={`p-2 rounded-lg bg-gradient-to-br ${color} text-white shadow-lg`}>
            {icon}
          </div>
          <h3 className="font-semibold text-gray-700">{title}</h3>
        </div>
        
        <div className="space-y-1">
          <p className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            {value}
          </p>
          <p className="text-sm text-gray-500 flex items-center gap-1">
            {trend === 'up' && <TrendingUp className="w-3 h-3 text-green-500" />}
            {trend === 'down' && <TrendingUp className="w-3 h-3 text-red-500 rotate-180" />}
            {trend === 'stable' && <Activity className="w-3 h-3 text-blue-500" />}
            {subtitle}
          </p>
        </div>
      </div>
      
      <div className="flex flex-col items-end gap-1">
        <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${color} animate-pulse`} />
        <div className="text-xs text-gray-400">Live</div>
      </div>
    </div>
  </GlowCard>
);

const StatusIndicator: React.FC<{ 
  status: 'healthy' | 'warning' | 'error'; 
  label: string;
  pulse?: boolean;
}> = ({ status, label, pulse = true }) => {
  const colors = {
    healthy: 'from-green-400 to-emerald-500',
    warning: 'from-yellow-400 to-orange-500',
    error: 'from-red-400 to-pink-500'
  };
  
  return (
    <div className="flex items-center gap-2">
      <div className={`
        w-3 h-3 rounded-full bg-gradient-to-r ${colors[status]} 
        ${pulse ? 'animate-pulse' : ''}
        shadow-lg
      `} />
      <span className="text-sm font-medium text-gray-700">{label}</span>
    </div>
  );
};

const AnimatedButton: React.FC<{
  onClick: () => void;
  icon: React.ReactNode;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  loading?: boolean;
  disabled?: boolean;
}> = ({ 
  onClick, 
  icon, 
  children, 
  variant = 'primary', 
  loading = false,
  disabled = false 
}) => {
  const variants = {
    primary: 'from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700',
    secondary: 'from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700',
    success: 'from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700',
    danger: 'from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        relative group flex items-center justify-center gap-2 px-6 py-3
        bg-gradient-to-r ${variants[variant]}
        text-white font-semibold rounded-xl
        shadow-[0_4px_20px_rgba(0,0,0,0.3)]
        hover:shadow-[0_8px_30px_rgba(0,0,0,0.4)]
        hover:scale-105
        active:scale-95
        transition-all duration-300 ease-out
        disabled:opacity-50 disabled:cursor-not-allowed
        overflow-hidden
      `}
    >
      <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      {loading ? (
        <RefreshCw className="w-5 h-5 animate-spin" />
      ) : (
        <div className="transition-transform duration-300 group-hover:scale-110">
          {icon}
        </div>
      )}
      
      <span className="relative z-10">{children}</span>
      
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
    </button>
  );
};

const NotificationSystemUltraModern: React.FC = () => {
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [types, setTypes] = useState<NotificationTypes | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [testResult, setTestResult] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'overview' | 'testing' | 'analytics' | 'settings'>('overview');
  const [realTimeMode, setRealTimeMode] = useState(true);
  
  // Form data para teste
  const [testForm, setTestForm] = useState({
    type: 'email',
    email: 'test@example.com',
    phone: '+5567999999999',
    pushToken: 'test-token-123',
    subject: 'Teste Ultra Moderno',
    content: 'Esta é uma notificação do sistema ultra moderno! 🚀✨'
  });

  // Carregar dados em tempo real
  useEffect(() => {
    loadData();
    
    if (realTimeMode) {
      const interval = setInterval(loadData, 5000); // Atualizar a cada 5 segundos
      return () => clearInterval(interval);
    }
  }, [realTimeMode]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Carregar dados em paralelo
      const [healthRes, statsRes, typesRes] = await Promise.all([
        fetch('http://localhost:8005/api/notifications/health'),
        fetch('http://localhost:8005/api/notifications/stats'),
        fetch('http://localhost:8005/api/notifications/types')
      ]);
      
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setHealth(healthData);
      }
      
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData.data);
      }
      
      if (typesRes.ok) {
        const typesData = await typesRes.json();
        setTypes(typesData.data);
      }
      
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const testNotification = async (type: string) => {
    try {
      setTestResult('🚀 Enviando...');
      
      let response;
      
      if (type === 'email') {
        response = await fetch('http://localhost:8005/api/notifications/test/email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: testForm.email,
            subject: testForm.subject,
            content: testForm.content
          })
        });
      } else if (type === 'sms') {
        response = await fetch('http://localhost:8005/api/notifications/test/sms', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone: testForm.phone,
            message: testForm.content
          })
        });
      } else if (type === 'push') {
        response = await fetch('http://localhost:8005/api/notifications/test/push', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token: testForm.pushToken,
            title: testForm.subject,
            body: testForm.content
          })
        });
      }
      
      if (response?.ok) {
        const result = await response.json();
        setTestResult(`✨ ${result.message}`);
        loadData(); // Recarregar dados
        
        // Limpar resultado após 5 segundos
        setTimeout(() => setTestResult(''), 5000);
      } else {
        setTestResult('❌ Erro ao enviar notificação');
      }
      
    } catch (error) {
      setTestResult('💥 Erro de conexão');
    }
  };

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 flex items-center justify-center">
        <GlowCard glow className="text-center p-12">
          <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Carregando Sistema Neural
          </h2>
          <p className="text-gray-600">Inicializando matriz de notificações...</p>
        </GlowCard>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      {/* Header Ultra Moderno */}
      <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white">
        <div className="absolute inset-0 bg-black/20" />
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-72 h-72 bg-white/10 rounded-full -translate-x-36 -translate-y-36 animate-pulse" />
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-white/5 rounded-full translate-x-48 translate-y-48 animate-pulse delay-1000" />
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-white/20 rounded-2xl backdrop-blur-sm">
                  <Bell className="w-8 h-8" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold mb-2">
                    Sistema de Notificações
                    <span className="ml-3 text-2xl">🚀</span>
                  </h1>
                  <p className="text-xl text-white/80">
                    Plataforma Neural de Comunicação Ultra Avançada
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-6">
                <StatusIndicator 
                  status={health?.status === 'healthy' ? 'healthy' : 'error'} 
                  label={`Sistema ${health?.status || 'Unknown'}`}
                />
                <StatusIndicator 
                  status={health?.is_processing ? 'healthy' : 'warning'} 
                  label={`Processamento ${health?.is_processing ? 'Ativo' : 'Inativo'}`}
                />
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4" />
                  <span className="text-sm">v{health?.version || '1.0.0'}</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <button
                onClick={() => setRealTimeMode(!realTimeMode)}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg backdrop-blur-sm
                  ${realTimeMode 
                    ? 'bg-white/20 text-white' 
                    : 'bg-white/10 text-white/60'
                  }
                  transition-all duration-300
                `}
              >
                {realTimeMode ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                Tempo Real
              </button>
              
              <button
                onClick={loadData}
                className="p-2 bg-white/20 rounded-lg backdrop-blur-sm hover:bg-white/30 transition-colors"
              >
                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navegação por Tabs */}
      <div className="bg-white/50 backdrop-blur-sm border-b border-white/20 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: 'Visão Geral', icon: Activity },
              { id: 'testing', label: 'Testes', icon: Zap },
              { id: 'analytics', label: 'Analytics', icon: BarChart3 },
              { id: 'settings', label: 'Configurações', icon: Settings }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  flex items-center gap-2 px-4 py-4 font-semibold transition-all duration-300
                  ${activeTab === tab.id
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-blue-600'
                  }
                `}
              >
                <tab.icon className="w-5 h-5" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Dashboard em Tempo Real */}
            <RealTimeDashboard />
            
            {/* Métricas Principais */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                icon={<Target className="w-5 h-5" />}
                title="Total"
                value={stats?.total_notifications || 0}
                subtitle="Notificações"
                trend="up"
                color="from-blue-500 to-blue-600"
              />
              
              <MetricCard
                icon={<Star className="w-5 h-5" />}
                title="Taxa Sucesso"
                value={`${stats?.success_rate || 0}%`}
                subtitle="De entregas"
                trend="stable"
                color="from-green-500 to-green-600"
              />
              
              <MetricCard
                icon={<Clock className="w-5 h-5" />}
                title="Últimas 24h"
                value={stats?.last_24h || 0}
                subtitle="Enviadas"
                trend="up"
                color="from-yellow-500 to-yellow-600"
              />
              
              <MetricCard
                icon={<Activity className="w-5 h-5" />}
                title="Fila"
                value={stats?.queue_size || 0}
                subtitle="Processando"
                trend="stable"
                color="from-purple-500 to-purple-600"
              />
            </div>

            {/* Gráficos e Análises */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Visualização Neural */}
              <NeuralVisualization />

              {/* Métricas Distribuídas */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Distribuição por Tipo */}
                <GlowCard>
                  <div className="flex items-center gap-2 mb-4">
                    <BarChart3 className="w-5 h-5 text-blue-600" />
                    <h3 className="font-semibold text-gray-800">Por Tipo</h3>
                  </div>
                  
                  <div className="space-y-3">
                    {Object.entries(stats?.by_type || {}).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {type === 'email' && <Mail className="w-4 h-4 text-blue-500" />}
                          {type === 'sms' && <MessageCircle className="w-4 h-4 text-green-500" />}
                          {type === 'push' && <Smartphone className="w-4 h-4 text-purple-500" />}
                          <span className="capitalize font-medium">{type}</span>
                        </div>
                        <span className="font-bold text-gray-700">{count}</span>
                      </div>
                    ))}
                  </div>
                </GlowCard>

                {/* Status */}
                <GlowCard>
                  <div className="flex items-center gap-2 mb-4">
                    <Shield className="w-5 h-5 text-green-600" />
                    <h3 className="font-semibold text-gray-800">Status</h3>
                  </div>
                  
                  <div className="space-y-3">
                    {Object.entries(stats?.by_status || {}).map(([status, count]) => (
                      <div key={status} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {status === 'sent' && <Check className="w-4 h-4 text-green-500" />}
                          {status === 'failed' && <X className="w-4 h-4 text-red-500" />}
                          {status === 'pending' && <Clock className="w-4 h-4 text-yellow-500" />}
                          <span className="capitalize font-medium">{status}</span>
                        </div>
                        <span className="font-bold text-gray-700">{count}</span>
                      </div>
                    ))}
                  </div>
                </GlowCard>
              </div>
            </div>

            {/* Sistema */}
            <GlowCard glow>
              <div className="flex items-center gap-2 mb-4">
                <Server className="w-5 h-5 text-purple-600" />
                <h3 className="font-semibold text-gray-800">Sistema Neural</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Versão</span>
                    <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
                      v{health?.version || '1.0.0'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">CPU</span>
                    <div className="flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-blue-500" />
                      <span className="text-sm font-medium">34%</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Memória</span>
                    <span className="text-sm font-medium">2.1GB</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Throughput</span>
                    <span className="text-sm font-medium text-green-600">1.2K/min</span>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Latência</span>
                    <span className="text-sm font-medium text-blue-600">12ms</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Última Atualização</span>
                    <span className="text-xs text-gray-500">
                      {health?.timestamp ? new Date(health.timestamp).toLocaleTimeString() : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </GlowCard>
          </div>
        )}

        {activeTab === 'testing' && (
          <div className="space-y-8">
            <GlowCard>
              <div className="flex items-center gap-2 mb-6">
                <Zap className="w-6 h-6 text-yellow-500" />
                <h2 className="text-2xl font-bold text-gray-800">Laboratório de Testes</h2>
              </div>

              {/* Formulário de Teste */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700">
                      📧 Email
                    </label>
                    <input
                      type="email"
                      value={testForm.email}
                      onChange={(e) => setTestForm({...testForm, email: e.target.value})}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                      placeholder="seu@email.com"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700">
                      📱 Telefone
                    </label>
                    <input
                      type="tel"
                      value={testForm.phone}
                      onChange={(e) => setTestForm({...testForm, phone: e.target.value})}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                      placeholder="+55 67 99999-9999"
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700">
                      🎯 Assunto
                    </label>
                    <input
                      type="text"
                      value={testForm.subject}
                      onChange={(e) => setTestForm({...testForm, subject: e.target.value})}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700">
                      🔔 Push Token
                    </label>
                    <input
                      type="text"
                      value={testForm.pushToken}
                      onChange={(e) => setTestForm({...testForm, pushToken: e.target.value})}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                      placeholder="token-device-123"
                    />
                  </div>
                </div>
              </div>
              
              <div className="mb-8">
                <label className="block text-sm font-medium mb-2 text-gray-700">
                  💬 Conteúdo
                </label>
                <textarea
                  value={testForm.content}
                  onChange={(e) => setTestForm({...testForm, content: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                  rows={4}
                  placeholder="Digite sua mensagem aqui..."
                />
              </div>

              {/* Botões de Teste */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <AnimatedButton
                  onClick={() => testNotification('email')}
                  icon={<Mail className="w-5 h-5" />}
                  variant="primary"
                >
                  Testar Email
                </AnimatedButton>
                
                <AnimatedButton
                  onClick={() => testNotification('sms')}
                  icon={<MessageCircle className="w-5 h-5" />}
                  variant="success"
                >
                  Testar SMS
                </AnimatedButton>
                
                <AnimatedButton
                  onClick={() => testNotification('push')}
                  icon={<Smartphone className="w-5 h-5" />}
                  variant="secondary"
                >
                  Testar Push
                </AnimatedButton>
              </div>

              {/* Resultado do Teste */}
              {testResult && (
                <GlowCard className={`${
                  testResult.includes('✨') || testResult.includes('✅')
                    ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200' 
                    : testResult.includes('🚀')
                    ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200'
                    : 'bg-gradient-to-r from-red-50 to-pink-50 border-red-200'
                }`}>
                  <p className="font-semibold text-lg">{testResult}</p>
                </GlowCard>
              )}
            </GlowCard>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-8">
            <GlowCard>
              <div className="text-center py-12">
                <BarChart3 className="w-16 h-16 mx-auto mb-4 text-blue-500" />
                <h3 className="text-2xl font-bold text-gray-800 mb-2">
                  Analytics Avançado
                </h3>
                <p className="text-gray-600">
                  Métricas detalhadas e visualizações em tempo real em desenvolvimento
                </p>
              </div>
            </GlowCard>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-8">
            <GlowCard>
              <div className="text-center py-12">
                <Settings className="w-16 h-16 mx-auto mb-4 text-gray-500" />
                <h3 className="text-2xl font-bold text-gray-800 mb-2">
                  Configurações Avançadas
                </h3>
                <p className="text-gray-600">
                  Painel de configurações em desenvolvimento
                </p>
              </div>
            </GlowCard>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationSystemUltraModern;
