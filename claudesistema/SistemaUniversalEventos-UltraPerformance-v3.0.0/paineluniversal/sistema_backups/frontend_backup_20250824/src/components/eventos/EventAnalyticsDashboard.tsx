import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  UsersIcon,
  CurrencyDollarIcon,
  CalendarDaysIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  FunnelIcon,
  ClockIcon,
  MapPinIcon,
  StarIcon
} from '@heroicons/react/24/outline';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar
} from 'recharts';

interface EventMetrics {
  total_events: number;
  active_events: number;
  total_participants: number;
  total_checkins: number;
  total_revenue: number;
  avg_rating: number;
  conversion_rate: number;
  checkin_rate: number;
  growth_rate: number;
  top_events: EventSummary[];
  revenue_by_month: RevenueData[];
  checkin_by_hour: CheckinData[];
  event_types_distribution: EventTypeData[];
  geographic_distribution: GeographicData[];
  feedback_sentiment: SentimentData;
}

interface EventSummary {
  id: string;
  nome: string;
  total_participants: number;
  total_revenue: number;
  checkin_rate: number;
  rating: number;
  status: string;
  data_inicio: string;
}

interface RevenueData {
  month: string;
  revenue: number;
  events: number;
  participants: number;
}

interface CheckinData {
  hour: number;
  checkins: number;
  label: string;
}

interface EventTypeData {
  type: string;
  count: number;
  revenue: number;
  participants: number;
}

interface GeographicData {
  city: string;
  events: number;
  participants: number;
  revenue: number;
}

interface SentimentData {
  positive: number;
  neutral: number;
  negative: number;
  total_reviews: number;
}

interface EventAnalyticsDashboardProps {
  eventId?: string;
  dateRange?: { start: Date; end: Date };
  onExportData?: () => void;
}

const EventAnalyticsDashboard: React.FC<EventAnalyticsDashboardProps> = ({
  eventId,
  dateRange,
  onExportData
}) => {
  const [metrics, setMetrics] = useState<EventMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('revenue');

  // Mock data - substituir por chamadas à API
  const mockMetrics: EventMetrics = {
    total_events: 45,
    active_events: 12,
    total_participants: 2834,
    total_checkins: 2456,
    total_revenue: 87450.50,
    avg_rating: 4.3,
    conversion_rate: 73.5,
    checkin_rate: 86.7,
    growth_rate: 12.5,
    top_events: [
      {
        id: '1',
        nome: 'Tech Conference 2024',
        total_participants: 450,
        total_revenue: 22500,
        checkin_rate: 92.3,
        rating: 4.8,
        status: 'finalizado',
        data_inicio: '2024-01-15T09:00:00Z'
      },
      {
        id: '2',
        nome: 'Workshop React Avançado',
        total_participants: 120,
        total_revenue: 8400,
        checkin_rate: 95.0,
        rating: 4.9,
        status: 'finalizado',
        data_inicio: '2024-01-22T14:00:00Z'
      },
      {
        id: '3',
        nome: 'Networking Night',
        total_participants: 200,
        total_revenue: 4000,
        checkin_rate: 78.5,
        rating: 4.2,
        status: 'finalizado',
        data_inicio: '2024-01-28T19:00:00Z'
      }
    ],
    revenue_by_month: [
      { month: 'Jan', revenue: 15000, events: 8, participants: 420 },
      { month: 'Fev', revenue: 22000, events: 12, participants: 650 },
      { month: 'Mar', revenue: 18500, events: 10, participants: 580 },
      { month: 'Abr', revenue: 31500, events: 15, participants: 890 }
    ],
    checkin_by_hour: [
      { hour: 8, checkins: 45, label: '08:00' },
      { hour: 9, checkins: 120, label: '09:00' },
      { hour: 10, checkins: 85, label: '10:00' },
      { hour: 11, checkins: 60, label: '11:00' },
      { hour: 14, checkins: 95, label: '14:00' },
      { hour: 15, checkins: 110, label: '15:00' },
      { hour: 16, checkins: 75, label: '16:00' },
      { hour: 19, checkins: 150, label: '19:00' },
      { hour: 20, checkins: 180, label: '20:00' }
    ],
    event_types_distribution: [
      { type: 'Conferência', count: 15, revenue: 45000, participants: 1200 },
      { type: 'Workshop', count: 12, revenue: 18000, participants: 480 },
      { type: 'Networking', count: 8, revenue: 8000, participants: 640 },
      { type: 'Show', count: 6, revenue: 12000, participants: 360 },
      { type: 'Festa', count: 4, revenue: 4450, participants: 154 }
    ],
    geographic_distribution: [
      { city: 'São Paulo', events: 18, participants: 1200, revenue: 42000 },
      { city: 'Rio de Janeiro', events: 12, participants: 800, revenue: 28000 },
      { city: 'Belo Horizonte', events: 8, participants: 450, revenue: 12500 },
      { city: 'Brasília', events: 7, participants: 384, revenue: 4950 }
    ],
    feedback_sentiment: {
      positive: 78.5,
      neutral: 15.2,
      negative: 6.3,
      total_reviews: 456
    }
  };

  useEffect(() => {
    const loadMetrics = async () => {
      setIsLoading(true);
      // Simular carregamento
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMetrics(mockMetrics);
      setIsLoading(false);
    };

    loadMetrics();
  }, [eventId, dateRange, timeRange]);

  // Cores para gráficos
  const chartColors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

  // Componente de métrica
  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    change?: number;
    icon: React.ElementType;
    color?: string;
    format?: 'currency' | 'percentage' | 'number';
  }> = ({ title, value, change, icon: Icon, color = 'blue', format = 'number' }) => {
    const formatValue = (val: string | number) => {
      if (format === 'currency') {
        return typeof val === 'number' ? `R$ ${val.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : val;
      } else if (format === 'percentage') {
        return typeof val === 'number' ? `${val.toFixed(1)}%` : val;
      }
      return typeof val === 'number' ? val.toLocaleString('pt-BR') : val;
    };

    const colorClasses = {
      blue: 'bg-blue-50 text-blue-600',
      green: 'bg-green-50 text-green-600',
      yellow: 'bg-yellow-50 text-yellow-600',
      purple: 'bg-purple-50 text-purple-600',
      red: 'bg-red-50 text-red-600'
    };

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-sm border p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{formatValue(value)}</p>
            {change !== undefined && (
              <div className="flex items-center mt-2">
                {change > 0 ? (
                  <TrendingUpIcon className="w-4 h-4 text-green-500 mr-1" />
                ) : (
                  <TrendingDownIcon className="w-4 h-4 text-red-500 mr-1" />
                )}
                <span className={`text-sm ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {Math.abs(change)}%
                </span>
              </div>
            )}
          </div>
          
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-6 h-6" />
          </div>
        </div>
      </motion.div>
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-32 rounded-lg"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-64 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-center py-12">
        <ChartBarIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">Não foi possível carregar as métricas</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics de Eventos</h1>
          <p className="text-gray-600 mt-1">
            {eventId ? 'Métricas do evento selecionado' : 'Visão geral de todos os eventos'}
          </p>
        </div>
        
        <div className="flex items-center space-x-4 mt-4 lg:mt-0">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Últimos 7 dias</option>
            <option value="30d">Últimos 30 dias</option>
            <option value="90d">Últimos 90 dias</option>
            <option value="1y">Último ano</option>
          </select>
          
          {onExportData && (
            <button
              onClick={onExportData}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
              Exportar
            </button>
          )}
        </div>
      </div>

      {/* Métricas principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total de Eventos"
          value={metrics.total_events}
          change={metrics.growth_rate}
          icon={CalendarDaysIcon}
          color="blue"
        />
        
        <MetricCard
          title="Participantes"
          value={metrics.total_participants}
          change={15.3}
          icon={UsersIcon}
          color="green"
        />
        
        <MetricCard
          title="Receita Total"
          value={metrics.total_revenue}
          change={8.7}
          icon={CurrencyDollarIcon}
          color="yellow"
          format="currency"
        />
        
        <MetricCard
          title="Taxa de Check-in"
          value={metrics.checkin_rate}
          change={2.1}
          icon={ClockIcon}
          color="purple"
          format="percentage"
        />
      </div>

      {/* Gráficos principais */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Receita por mês */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white rounded-lg shadow-sm border p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Receita por Mês</h3>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="revenue">Receita</option>
              <option value="events">Eventos</option>
              <option value="participants">Participantes</option>
            </select>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={metrics.revenue_by_month}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip
                formatter={(value, name) => {
                  if (name === 'revenue') return [`R$ ${value.toLocaleString('pt-BR')}`, 'Receita'];
                  return [value, name === 'events' ? 'Eventos' : 'Participantes'];
                }}
              />
              <Area 
                type="monotone" 
                dataKey={selectedMetric} 
                stroke="#3B82F6" 
                fill="#3B82F6" 
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Check-ins por horário */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white rounded-lg shadow-sm border p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Check-ins por Horário</h3>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metrics.checkin_by_hour}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="checkins" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Distribuições e rankings */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Distribuição por tipo de evento */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white rounded-lg shadow-sm border p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Tipos de Eventos</h3>
          
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={metrics.event_types_distribution}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="count"
                nameKey="type"
                label={({ type, value }) => `${type}: ${value}`}
              >
                {metrics.event_types_distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Top eventos */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white rounded-lg shadow-sm border p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Top Eventos</h3>
          
          <div className="space-y-4">
            {metrics.top_events.map((event, index) => (
              <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full text-sm font-medium">
                    {index + 1}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 text-sm">{event.nome}</h4>
                    <p className="text-xs text-gray-500">{event.total_participants} participantes</p>
                  </div>
                </div>
                
                <div className="text-right">
                  <p className="text-sm font-medium text-green-600">
                    R$ {event.total_revenue.toLocaleString('pt-BR')}
                  </p>
                  <div className="flex items-center text-xs text-gray-500">
                    <StarIcon className="w-3 h-3 text-yellow-400 mr-1" />
                    {event.rating.toFixed(1)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Análise de sentimento */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white rounded-lg shadow-sm border p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Feedback dos Eventos</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Positivo</span>
              <span className="text-sm font-medium text-green-600">{metrics.feedback_sentiment.positive}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full" 
                style={{ width: `${metrics.feedback_sentiment.positive}%` }}
              ></div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Neutro</span>
              <span className="text-sm font-medium text-yellow-600">{metrics.feedback_sentiment.neutral}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-yellow-500 h-2 rounded-full" 
                style={{ width: `${metrics.feedback_sentiment.neutral}%` }}
              ></div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Negativo</span>
              <span className="text-sm font-medium text-red-600">{metrics.feedback_sentiment.negative}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-red-500 h-2 rounded-full" 
                style={{ width: `${metrics.feedback_sentiment.negative}%` }}
              ></div>
            </div>
            
            <div className="pt-2 border-t">
              <p className="text-xs text-gray-500">
                Total: {metrics.feedback_sentiment.total_reviews} avaliações
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Distribuição geográfica */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-white rounded-lg shadow-sm border p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Distribuição Geográfica</h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 text-sm font-medium text-gray-700">Cidade</th>
                <th className="text-right py-2 text-sm font-medium text-gray-700">Eventos</th>
                <th className="text-right py-2 text-sm font-medium text-gray-700">Participantes</th>
                <th className="text-right py-2 text-sm font-medium text-gray-700">Receita</th>
              </tr>
            </thead>
            <tbody>
              {metrics.geographic_distribution.map((city, index) => (
                <tr key={index} className="border-b border-gray-100">
                  <td className="py-3 text-sm text-gray-900">{city.city}</td>
                  <td className="py-3 text-sm text-gray-600 text-right">{city.events}</td>
                  <td className="py-3 text-sm text-gray-600 text-right">{city.participants}</td>
                  <td className="py-3 text-sm text-green-600 text-right font-medium">
                    R$ {city.revenue.toLocaleString('pt-BR')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
};

export default EventAnalyticsDashboard;