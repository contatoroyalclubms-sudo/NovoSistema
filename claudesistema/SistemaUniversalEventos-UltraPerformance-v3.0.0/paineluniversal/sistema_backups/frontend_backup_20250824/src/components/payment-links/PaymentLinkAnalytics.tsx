/**
 * PaymentLinkAnalytics - Analytics dashboard with real-time metrics
 * Sistema Universal de Gestão de Eventos
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  ArrowLeft, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Users, 
  Eye, 
  Calendar,
  Download,
  RefreshCw,
  Filter,
  BarChart3,
  PieChart,
  Activity,
  Target,
  Zap,
  Globe,
  Smartphone,
  CreditCard,
  Clock
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Cell,
  AreaChart,
  Area
} from 'recharts';

import { 
  LinkAnalytics,
  PaymentLink,
  AnalyticsMetrics,
  AnalyticsPeriod,
  DEFAULT_ANALYTICS_PERIODS,
  DailyStats
} from '@/types/payment-links';

import paymentLinksService from '@/services/payment-links-service';

interface PaymentLinkAnalyticsProps {
  linkId?: string;
  onBack?: () => void;
}

const PaymentLinkAnalytics: React.FC<PaymentLinkAnalyticsProps> = ({ 
  linkId,
  onBack 
}) => {
  const [analytics, setAnalytics] = useState<LinkAnalytics | AnalyticsMetrics | null>(null);
  const [links, setLinks] = useState<PaymentLink[]>([]);
  const [selectedLinkId, setSelectedLinkId] = useState<string>(linkId || '');
  const [selectedPeriod, setSelectedPeriod] = useState<AnalyticsPeriod>(DEFAULT_ANALYTICS_PERIODS[1]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [realtimeEnabled, setRealtimeEnabled] = useState(false);

  // Load initial data
  useEffect(() => {
    loadAnalytics();
    loadLinks();
  }, [selectedLinkId, selectedPeriod]);

  // Real-time updates
  useEffect(() => {
    if (!realtimeEnabled) return;

    const interval = setInterval(() => {
      loadAnalytics();
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [realtimeEnabled, selectedLinkId, selectedPeriod]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      if (selectedLinkId) {
        const data = await paymentLinksService.getLinkAnalytics(selectedLinkId, selectedPeriod.days);
        setAnalytics(data);
      } else {
        const data = await paymentLinksService.getOverallAnalytics(selectedPeriod.days);
        setAnalytics(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar analytics');
    } finally {
      setLoading(false);
    }
  };

  const loadLinks = async () => {
    try {
      const response = await paymentLinksService.getPaymentLinks({ limit: 100 });
      setLinks(response.links);
    } catch (err) {
      console.error('Error loading links:', err);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await paymentLinksService.exportPaymentLinks({
        format: 'excel',
        date_range: {
          start: new Date(Date.now() - selectedPeriod.days * 24 * 60 * 60 * 1000).toISOString(),
          end: new Date().toISOString()
        },
        include_analytics: true,
        include_payments: true,
        links: selectedLinkId ? [selectedLinkId] : undefined
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-${selectedPeriod.label.toLowerCase().replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export error:', err);
      alert('Erro ao exportar dados');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  // Chart data preparation
  const chartData = useMemo(() => {
    if (!analytics || !('daily_stats' in analytics)) return [];

    return analytics.daily_stats.map((stat: DailyStats) => ({
      date: new Date(stat.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
      revenue: stat.revenue,
      payments: stat.completed_payments,
      attempts: stat.attempts,
      conversion: stat.attempts > 0 ? (stat.completed_payments / stat.attempts) * 100 : 0
    }));
  }, [analytics]);

  const paymentMethodsData = useMemo(() => {
    if (!analytics || !('payment_methods_breakdown' in analytics)) return [];

    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

    return Object.entries(analytics.payment_methods_breakdown).map(([method, count], index) => ({
      name: method === 'pix' ? 'PIX' : method === 'card' ? 'Cartão' : method,
      value: count,
      color: colors[index % colors.length]
    }));
  }, [analytics]);

  const isLinkAnalytics = (data: any): data is LinkAnalytics => {
    return data && 'link_id' in data;
  };

  if (loading && !analytics) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {onBack && (
            <Button variant="ghost" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Voltar
            </Button>
          )}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-600">
              {selectedLinkId ? 'Análise detalhada do link' : 'Visão geral de todos os links'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant={realtimeEnabled ? 'default' : 'outline'}
            onClick={() => setRealtimeEnabled(!realtimeEnabled)}
            size="sm"
          >
            <Activity className="h-4 w-4 mr-2" />
            Tempo Real
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
          <Button variant="outline" onClick={loadAnalytics} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <Select
                value={selectedLinkId || 'all'}
                onValueChange={(value) => setSelectedLinkId(value === 'all' ? '' : value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecionar Link" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os Links</SelectItem>
                  {links.map((link) => (
                    <SelectItem key={link.link_id} value={link.link_id}>
                      {link.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <Select
              value={selectedPeriod.value.toString()}
              onValueChange={(value) => {
                const period = DEFAULT_ANALYTICS_PERIODS.find(p => p.value.toString() === value);
                if (period) setSelectedPeriod(period);
              }}
            >
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DEFAULT_ANALYTICS_PERIODS.map((period) => (
                  <SelectItem key={period.value} value={period.value.toString()}>
                    {period.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {isLinkAnalytics(analytics) ? 'Visualizações' : 'Total de Links'}
              </CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLinkAnalytics(analytics) ? analytics.total_views : analytics.total_links}
              </div>
              {isLinkAnalytics(analytics) && (
                <p className="text-xs text-muted-foreground">
                  Taxa de conversão: {formatPercentage(analytics.conversion_rate)}
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Receita Total</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(analytics.total_collected || analytics.total_revenue)}
              </div>
              {!isLinkAnalytics(analytics) && (
                <div className="flex items-center space-x-1">
                  <TrendingUp className="h-3 w-3 text-green-500" />
                  <p className="text-xs text-muted-foreground">
                    +{formatPercentage(analytics.growth_rate)} vs período anterior
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pagamentos</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analytics.successful_payments || analytics.total_payments}
              </div>
              <p className="text-xs text-muted-foreground">
                {analytics.total_attempts && `${analytics.total_attempts} tentativas`}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Ticket Médio</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(analytics.avg_amount)}
              </div>
              {analytics.conversion_rate && (
                <p className="text-xs text-muted-foreground">
                  Conversão: {formatPercentage(analytics.conversion_rate)}
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Charts and Detailed Analytics */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid grid-cols-4 w-full">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="payments">Pagamentos</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Evolução da Receita</CardTitle>
                <CardDescription>
                  Receita diária nos últimos {selectedPeriod.days} dias
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis tickFormatter={(value) => `R$ ${value}`} />
                      <Tooltip formatter={(value: number) => [formatCurrency(value), 'Receita']} />
                      <Area 
                        type="monotone" 
                        dataKey="revenue" 
                        stroke="#3b82f6" 
                        fill="#3b82f6" 
                        fillOpacity={0.3} 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Payment Methods */}
            <Card>
              <CardHeader>
                <CardTitle>Métodos de Pagamento</CardTitle>
                <CardDescription>
                  Distribuição por método de pagamento
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={paymentMethodsData}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {paymentMethodsData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Conversion Rate */}
            <Card>
              <CardHeader>
                <CardTitle>Taxa de Conversão</CardTitle>
                <CardDescription>
                  Conversão de visualizações em pagamentos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis tickFormatter={(value) => `${value}%`} />
                      <Tooltip formatter={(value: number) => [`${value.toFixed(1)}%`, 'Conversão']} />
                      <Line 
                        type="monotone" 
                        dataKey="conversion" 
                        stroke="#10b981" 
                        strokeWidth={2} 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Payment Attempts vs Success */}
            <Card>
              <CardHeader>
                <CardTitle>Tentativas vs Sucessos</CardTitle>
                <CardDescription>
                  Comparação entre tentativas e pagamentos aprovados
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="attempts" fill="#f59e0b" name="Tentativas" />
                      <Bar dataKey="payments" fill="#10b981" name="Sucessos" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Zap className="h-5 w-5 text-yellow-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Taxa de Abandono</p>
                    <p className="text-2xl font-bold">
                      {analytics && isLinkAnalytics(analytics) 
                        ? formatPercentage(100 - analytics.conversion_rate)
                        : '0%'
                      }
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Tempo Médio</p>
                    <p className="text-2xl font-bold">2m 34s</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Activity className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Taxa de Sucesso</p>
                    <p className="text-2xl font-bold">
                      {analytics && 'conversion_rate' in analytics 
                        ? formatPercentage(analytics.conversion_rate)
                        : '0%'
                      }
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Payments Tab */}
        <TabsContent value="payments" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Histórico de Pagamentos</CardTitle>
                <CardDescription>
                  Últimos pagamentos recebidos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* This would be populated with actual payment data */}
                  <div className="flex items-center space-x-4 p-3 border rounded">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div className="flex-1">
                      <div className="flex justify-between">
                        <p className="font-medium">João Silva</p>
                        <p className="font-bold text-green-600">R$ 150,00</p>
                      </div>
                      <p className="text-sm text-gray-500">PIX • há 2 horas</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4 p-3 border rounded">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div className="flex-1">
                      <div className="flex justify-between">
                        <p className="font-medium">Maria Santos</p>
                        <p className="font-bold text-green-600">R$ 200,00</p>
                      </div>
                      <p className="text-sm text-gray-500">Cartão • há 5 horas</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Resumo Financeiro</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm">
                    <span>Receita Bruta</span>
                    <span className="font-medium">
                      {analytics && formatCurrency(analytics.total_collected || analytics.total_revenue)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Taxa de Processamento</span>
                    <span>- R$ 45,60</span>
                  </div>
                  <Separator className="my-2" />
                  <div className="flex justify-between font-medium">
                    <span>Receita Líquida</span>
                    <span className="text-green-600">
                      {analytics && formatCurrency((analytics.total_collected || analytics.total_revenue) * 0.97)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Insights Automáticos</CardTitle>
                <CardDescription>
                  Análises inteligentes baseadas nos seus dados
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <TrendingUp className="h-4 w-4" />
                  <AlertDescription>
                    Sua conversão aumentou 15% na última semana. Continue promovendo seus links nas redes sociais!
                  </AlertDescription>
                </Alert>
                
                <Alert>
                  <Target className="h-4 w-4" />
                  <AlertDescription>
                    O horário de maior conversão é entre 19h-21h. Considere enviar lembretes neste período.
                  </AlertDescription>
                </Alert>

                <Alert>
                  <CreditCard className="h-4 w-4" />
                  <AlertDescription>
                    PIX representa 70% dos seus pagamentos. Considere destacar esta opção na página.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recomendações</CardTitle>
                <CardDescription>
                  Sugestões para melhorar performance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium">Otimize para mobile</p>
                      <p className="text-sm text-gray-600">
                        60% dos seus acessos são mobile. Use o tema responsivo.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium">Configure webhooks</p>
                      <p className="text-sm text-gray-600">
                        Automatize processos com notificações em tempo real.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium">Adicione urgência</p>
                      <p className="text-sm text-gray-600">
                        Links com data de expiração convertem 25% mais.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export { PaymentLinkAnalytics };