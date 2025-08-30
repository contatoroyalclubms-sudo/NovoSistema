/**
 * Advanced Dashboard Component - Sprint 5
 * Sistema Universal de Gestão de Eventos
 * 
 * Modern React dashboard with:
 * - Real-time metrics
 * - Interactive charts
 * - Responsive design
 * - WebSocket integration
 * - Performance optimization
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Users, Calendar, DollarSign, CheckCircle,
  Activity, AlertTriangle, Zap, BarChart3, PieChart as PieChartIcon
} from 'lucide-react';
import { useWebSocket } from '../../hooks/useWebSocket';

interface DashboardData {
  overview: {
    total_eventos: number;
    eventos_ativos: number;
    total_participantes: number;
    eventos_ultimo_mes: number;
    checkins_ultimo_mes: number;
    taxa_presenca_media: number;
    crescimento_eventos: number;
    crescimento_participantes: number;
  };
  events: {
    por_status: Record<string, number>;
    por_tipo: Array<{ tipo: string; count: number }>;
    top_eventos: Array<{ nome: string; id: string; participantes: number }>;
    proximos_eventos: Array<{ nome: string; data_inicio: string; participantes: number }>;
  };
  financial: {
    receita_total: number;
    receita_mes_atual: number;
    ticket_medio: number;
    crescimento_receita: number;
    por_forma_pagamento: Array<{ forma: string; valor: number; percentual: number }>;
    receita_diaria: Array<{ data: string; receita: number }>;
    top_produtos: Array<{ produto: string; receita: number }>;
  };
  checkin: {
    total_checkins: number;
    taxa_sucesso: number;
    tempo_medio_permanencia: number;
    por_tipo: Array<{ tipo: string; count: number }>;
    por_hora: Array<{ hora: number; count: number }>;
    eventos_alta_presenca: Array<{ nome: string; taxa_presenca: number }>;
  };
  gamification: {
    total_pontos_distribuidos: number;
    total_conquistas_desbloqueadas: number;
    top_usuarios_mes: Array<{ nome: string; pontos: number }>;
    top_acoes: Array<{ acao: string; count: number }>;
    badges_distribuicao: Array<{ badge: string; count: number }>;
  };
  alerts: Array<{
    type: string;
    title: string;
    description: string;
    severity: string;
  }>;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  color: string;
  format?: 'number' | 'currency' | 'percentage';
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  change, 
  icon, 
  color,
  format = 'number' 
}) => {
  const formatValue = (val: string | number) => {
    const numVal = typeof val === 'string' ? parseFloat(val) : val;
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('pt-BR', {
          style: 'currency',
          currency: 'BRL'
        }).format(numVal);
      case 'percentage':
        return `${numVal.toFixed(1)}%`;
      default:
        return new Intl.NumberFormat('pt-BR').format(numVal);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{formatValue(value)}</p>
          {change !== undefined && (
            <div className="flex items-center mt-2">
              {change >= 0 ? (
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
              )}
              <span className={`text-sm font-medium ${
                change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {Math.abs(change).toFixed(1)}%
              </span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

interface ChartSectionProps {
  title: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}

const ChartSection: React.FC<ChartSectionProps> = ({ title, children, action }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <div className="flex items-center justify-between mb-6">
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      {action}
    </div>
    {children}
  </div>
);

interface AlertProps {
  alerts: DashboardData['alerts'];
}

const AlertsPanel: React.FC<AlertProps> = ({ alerts }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Alertas do Sistema</h3>
    <div className="space-y-3">
      {alerts.length === 0 ? (
        <p className="text-gray-500 text-center py-4">Nenhum alerta ativo</p>
      ) : (
        alerts.map((alert, index) => (
          <div key={index} className={`p-3 rounded-lg border-l-4 ${
            alert.severity === 'high' ? 'border-red-400 bg-red-50' :
            alert.severity === 'medium' ? 'border-yellow-400 bg-yellow-50' :
            'border-blue-400 bg-blue-50'
          }`}>
            <div className="flex items-start">
              <AlertTriangle className={`h-5 w-5 mt-0.5 ${
                alert.severity === 'high' ? 'text-red-500' :
                alert.severity === 'medium' ? 'text-yellow-500' :
                'text-blue-500'
              }`} />
              <div className="ml-3">
                <h4 className="text-sm font-medium text-gray-900">{alert.title}</h4>
                <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  </div>
);

const COLORS = {
  primary: '#3b82f6',
  secondary: '#10b981',
  tertiary: '#f59e0b',
  quaternary: '#ef4444',
  quinary: '#8b5cf6'
};

export const AdvancedDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'events' | 'financial' | 'operations'>('overview');

  // WebSocket para atualizações em tempo real
  const { isConnected, sendMessage } = useWebSocket({
    onMessage: (message) => {
      if (message.type === 'dashboard_update') {
        setDashboardData(prev => prev ? { ...prev, ...message.data } : message.data);
      }
    }
  });

  // Buscar dados do dashboard
  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/analytics/dashboard');
      
      if (!response.ok) {
        throw new Error('Falha ao carregar dados do dashboard');
      }
      
      const data = await response.json();
      setDashboardData(data.dashboard);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
    
    // Configurar atualizações automáticas
    const interval = setInterval(fetchDashboardData, 30000); // 30 segundos
    
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  // Configurar WebSocket para atualizações em tempo real
  useEffect(() => {
    if (isConnected) {
      sendMessage({
        type: 'subscribe_dashboard',
        data: { metrics: ['overview', 'events', 'financial', 'checkin'] }
      });
    }
  }, [isConnected, sendMessage]);

  // Dados processados para gráficos
  const processedData = useMemo(() => {
    if (!dashboardData) return null;

    const { financial, checkin, events, gamification } = dashboardData;

    return {
      revenueChart: financial.receita_diaria.map(item => ({
        data: new Date(item.data).toLocaleDateString('pt-BR', { 
          month: 'short', 
          day: 'numeric' 
        }),
        receita: item.receita
      })),
      
      checkinByHour: checkin.por_hora.map(item => ({
        hora: `${item.hora}:00`,
        checkins: item.count
      })),
      
      eventsByType: events.por_tipo.map(item => ({
        name: item.tipo,
        value: item.count
      })),
      
      paymentMethods: financial.por_forma_pagamento.map(item => ({
        name: item.forma,
        value: item.valor,
        percentage: item.percentual
      })),
      
      topEvents: events.top_eventos.slice(0, 5)
    };
  }, [dashboardData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <AlertTriangle className="h-16 w-16 text-red-500 mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Erro ao carregar dashboard</h2>
        <p className="text-gray-600 mb-4">{error}</p>
        <button 
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  if (!dashboardData) return null;

  const { overview, events, financial, checkin, gamification, alerts } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Visão geral do sistema • 
                <span className={`ml-2 inline-flex items-center ${
                  isConnected ? 'text-green-600' : 'text-red-600'
                }`}>
                  <div className={`w-2 h-2 rounded-full mr-1 ${
                    isConnected ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  {isConnected ? 'Tempo real' : 'Desconectado'}
                </span>
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={fetchDashboardData}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Atualizar
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="mt-6 border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'overview', name: 'Visão Geral', icon: BarChart3 },
                { id: 'events', name: 'Eventos', icon: Calendar },
                { id: 'financial', name: 'Financeiro', icon: DollarSign },
                { id: 'operations', name: 'Operações', icon: Activity }
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {tab.name}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            
            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Total de Eventos"
                value={overview.total_eventos}
                change={overview.crescimento_eventos}
                icon={<Calendar className="h-6 w-6 text-white" />}
                color="bg-blue-500"
              />
              
              <MetricCard
                title="Participantes"
                value={overview.total_participantes}
                change={overview.crescimento_participantes}
                icon={<Users className="h-6 w-6 text-white" />}
                color="bg-green-500"
              />
              
              <MetricCard
                title="Receita Total"
                value={financial.receita_total}
                change={financial.crescimento_receita}
                icon={<DollarSign className="h-6 w-6 text-white" />}
                color="bg-yellow-500"
                format="currency"
              />
              
              <MetricCard
                title="Taxa de Presença"
                value={overview.taxa_presenca_media}
                icon={<CheckCircle className="h-6 w-6 text-white" />}
                color="bg-purple-500"
                format="percentage"
              />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Revenue Chart */}
              <ChartSection title="Receita Diária (Últimos 30 dias)">
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={processedData?.revenueChart}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="data" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value) => [
                        new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(Number(value)),
                        'Receita'
                      ]}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="receita" 
                      stroke={COLORS.primary} 
                      fill={COLORS.primary}
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartSection>

              {/* Check-ins by Hour */}
              <ChartSection title="Check-ins por Horário">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={processedData?.checkinByHour}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hora" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="checkins" fill={COLORS.secondary} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartSection>

              {/* Events by Type */}
              <ChartSection title="Eventos por Tipo">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={processedData?.eventsByType}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {processedData?.eventsByType.map((_, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={Object.values(COLORS)[index % Object.values(COLORS).length]} 
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </ChartSection>

              {/* Alerts Panel */}
              <AlertsPanel alerts={alerts} />
            </div>
          </div>
        )}

        {/* Events Tab */}
        {activeTab === 'events' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Top Events */}
              <ChartSection title="Top Eventos">
                <div className="space-y-3">
                  {processedData?.topEvents.map((event, index) => (
                    <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                          {index + 1}
                        </span>
                        <span className="ml-3 font-medium text-gray-900">{event.nome}</span>
                      </div>
                      <span className="text-sm text-gray-600">{event.participantes} participantes</span>
                    </div>
                  ))}
                </div>
              </ChartSection>

              {/* Upcoming Events */}
              <ChartSection title="Próximos Eventos">
                <div className="space-y-3">
                  {events.proximos_eventos.slice(0, 5).map((event, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-gray-900">{event.nome}</div>
                        <div className="text-sm text-gray-600">
                          {new Date(event.data_inicio).toLocaleDateString('pt-BR')}
                        </div>
                      </div>
                      <span className="text-sm text-gray-600">{event.participantes} participantes</span>
                    </div>
                  ))}
                </div>
              </ChartSection>
            </div>
          </div>
        )}

        {/* Financial Tab */}
        {activeTab === 'financial' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                title="Receita Total"
                value={financial.receita_total}
                change={financial.crescimento_receita}
                icon={<DollarSign className="h-6 w-6 text-white" />}
                color="bg-green-500"
                format="currency"
              />
              
              <MetricCard
                title="Receita do Mês"
                value={financial.receita_mes_atual}
                icon={<TrendingUp className="h-6 w-6 text-white" />}
                color="bg-blue-500"
                format="currency"
              />
              
              <MetricCard
                title="Ticket Médio"
                value={financial.ticket_medio}
                icon={<BarChart3 className="h-6 w-6 text-white" />}
                color="bg-purple-500"
                format="currency"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Payment Methods */}
              <ChartSection title="Formas de Pagamento">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={processedData?.paymentMethods}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percentage }) => `${name}: ${percentage.toFixed(1)}%`}
                    >
                      {processedData?.paymentMethods.map((_, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={Object.values(COLORS)[index % Object.values(COLORS).length]} 
                        />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value) => [
                        new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(Number(value)),
                        'Valor'
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </ChartSection>

              {/* Top Products */}
              <ChartSection title="Top Produtos">
                <div className="space-y-3">
                  {financial.top_produtos.slice(0, 5).map((product, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        <span className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                          {index + 1}
                        </span>
                        <span className="ml-3 font-medium text-gray-900">{product.produto}</span>
                      </div>
                      <span className="text-sm font-medium text-green-600">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(product.receita)}
                      </span>
                    </div>
                  ))}
                </div>
              </ChartSection>
            </div>
          </div>
        )}

        {/* Operations Tab */}
        {activeTab === 'operations' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                title="Total Check-ins"
                value={checkin.total_checkins}
                icon={<CheckCircle className="h-6 w-6 text-white" />}
                color="bg-green-500"
              />
              
              <MetricCard
                title="Taxa de Sucesso"
                value={checkin.taxa_sucesso}
                icon={<Zap className="h-6 w-6 text-white" />}
                color="bg-blue-500"
                format="percentage"
              />
              
              <MetricCard
                title="Tempo Médio"
                value={`${checkin.tempo_medio_permanencia} min`}
                icon={<Activity className="h-6 w-6 text-white" />}
                color="bg-purple-500"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Check-in Types */}
              <ChartSection title="Check-ins por Tipo">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={checkin.por_tipo}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="tipo" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill={COLORS.secondary} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartSection>

              {/* High Attendance Events */}
              <ChartSection title="Eventos com Alta Presença">
                <div className="space-y-3">
                  {checkin.eventos_alta_presenca.slice(0, 5).map((event, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="font-medium text-gray-900">{event.nome}</span>
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full" 
                            style={{ width: `${Math.min(event.taxa_presenca, 100)}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-green-600">
                          {event.taxa_presenca.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </ChartSection>
            </div>

            {/* Gamification Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <MetricCard
                title="Pontos Distribuídos"
                value={gamification.total_pontos_distribuidos}
                icon={<Zap className="h-6 w-6 text-white" />}
                color="bg-yellow-500"
              />
              
              <MetricCard
                title="Conquistas"
                value={gamification.total_conquistas_desbloqueadas}
                icon={<CheckCircle className="h-6 w-6 text-white" />}
                color="bg-purple-500"
              />
              
              <ChartSection title="Top Usuários do Mês">
                <div className="space-y-2">
                  {gamification.top_usuarios_mes.slice(0, 3).map((user, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900">{user.nome}</span>
                      <span className="text-sm text-yellow-600 font-medium">{user.pontos} pts</span>
                    </div>
                  ))}
                </div>
              </ChartSection>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvancedDashboard;