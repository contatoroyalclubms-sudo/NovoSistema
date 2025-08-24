/**
 * Refund Analytics Dashboard - Dashboard de Analytics e Insights de Estornos
 * Sistema Universal de Gestão de Eventos
 * 
 * Dashboard completo com analytics avançados:
 * - Métricas de performance em tempo real
 * - Análise de tendências e padrões
 * - Dashboards interativos com charts
 * - Insights de IA e machine learning
 * - Alertas e recomendações automáticas
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTab } from '../ui/tabs';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Shield,
  Clock,
  Users,
  AlertTriangle,
  CheckCircle,
  Brain,
  Zap,
  Target,
  Activity,
  BarChart3,
  PieChart as PieChartIcon,
  Download,
  RefreshCw,
  Calendar,
  Filter,
  Eye,
  Settings
} from 'lucide-react';

// Types
interface RefundMetrics {
  totalRefunds: number;
  totalAmount: number;
  avgProcessingTime: number;
  successRate: number;
  fraudPrevented: number;
  autoApprovalRate: number;
  avgRiskScore: number;
  chargebacksPrevented: number;
  dailyTrend: number;
  weeklyTrend: number;
  monthlyTrend: number;
}

interface RefundTrendData {
  date: string;
  refunds: number;
  amount: number;
  approved: number;
  rejected: number;
  avgRiskScore: number;
  processingTime: number;
}

interface RefundCategoryData {
  category: string;
  count: number;
  amount: number;
  percentage: number;
  avgRiskScore: number;
  successRate: number;
}

interface FraudAnalytics {
  totalFraudAttempts: number;
  fraudPrevented: number;
  falsePositives: number;
  truePositives: number;
  modelAccuracy: number;
  topFraudIndicators: Array<{ indicator: string; frequency: number }>;
}

interface AIInsights {
  predictions: {
    nextWeekVolume: number;
    riskTrendDirection: 'up' | 'down' | 'stable';
    recommendedActions: string[];
  };
  patterns: {
    seasonalTrends: Array<{ period: string; impact: number }>;
    customerBehavior: Array<{ pattern: string; frequency: number }>;
    gatewayPerformance: Array<{ gateway: string; performance: number }>;
  };
  anomalies: Array<{
    type: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
    timestamp: Date;
  }>;
}

interface RefundAnalyticsDashboardProps {
  timeRange?: string;
  refreshInterval?: number;
}

const RefundAnalyticsDashboard: React.FC<RefundAnalyticsDashboardProps> = ({
  timeRange = '30d',
  refreshInterval = 60000 // 1 minute
}) => {
  // State
  const [metrics, setMetrics] = useState<RefundMetrics | null>(null);
  const [trendData, setTrendData] = useState<RefundTrendData[]>([]);
  const [categoryData, setCategoryData] = useState<RefundCategoryData[]>([]);
  const [fraudAnalytics, setFraudAnalytics] = useState<FraudAnalytics | null>(null);
  const [aiInsights, setAIInsights] = useState<AIInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState(timeRange);
  const [activeTab, setActiveTab] = useState('overview');

  // Load analytics data
  useEffect(() => {
    loadAnalyticsData();
    const interval = setInterval(loadAnalyticsData, refreshInterval);
    return () => clearInterval(interval);
  }, [selectedTimeRange, refreshInterval]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Load all analytics data in parallel
      const [metricsRes, trendRes, categoryRes, fraudRes, aiRes] = await Promise.all([
        fetch(`/api/refunds/analytics/metrics?timeRange=${selectedTimeRange}`),
        fetch(`/api/refunds/analytics/trends?timeRange=${selectedTimeRange}`),
        fetch(`/api/refunds/analytics/categories?timeRange=${selectedTimeRange}`),
        fetch(`/api/refunds/analytics/fraud?timeRange=${selectedTimeRange}`),
        fetch(`/api/refunds/analytics/ai-insights?timeRange=${selectedTimeRange}`)
      ]);

      const [metricsData, trendData, categoryData, fraudData, aiData] = await Promise.all([
        metricsRes.json(),
        trendRes.json(),
        categoryRes.json(),
        fraudRes.json(),
        aiRes.json()
      ]);

      setMetrics(metricsData);
      setTrendData(trendData);
      setCategoryData(categoryData);
      setFraudAnalytics(fraudData);
      setAIInsights(aiData);
    } catch (error) {
      console.error('Erro ao carregar analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Chart colors
  const chartColors = {
    primary: '#3b82f6',
    secondary: '#10b981',
    accent: '#f59e0b',
    danger: '#ef4444',
    warning: '#f97316',
    info: '#06b6d4'
  };

  const pieColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  // Calculated metrics
  const trendAnalysis = useMemo(() => {
    if (!trendData || trendData.length < 2) return null;
    
    const recent = trendData.slice(-7); // Last 7 days
    const previous = trendData.slice(-14, -7); // Previous 7 days
    
    const recentAvg = recent.reduce((sum, day) => sum + day.refunds, 0) / recent.length;
    const previousAvg = previous.reduce((sum, day) => sum + day.refunds, 0) / previous.length;
    
    const changePercent = previousAvg > 0 ? ((recentAvg - previousAvg) / previousAvg) * 100 : 0;
    
    return {
      trend: changePercent > 5 ? 'up' : changePercent < -5 ? 'down' : 'stable',
      changePercent: Math.abs(changePercent),
      direction: changePercent > 0 ? 'increase' : 'decrease'
    };
  }, [trendData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin mr-2" />
        <span>Carregando analytics...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-blue-600" />
              Analytics de Estornos
            </h1>
            <p className="text-gray-600 mt-1">
              Insights avançados e analytics em tempo real do sistema de estornos
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">Últimos 7 dias</SelectItem>
                <SelectItem value="30d">Últimos 30 dias</SelectItem>
                <SelectItem value="90d">Últimos 90 dias</SelectItem>
                <SelectItem value="1y">Último ano</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" onClick={loadAnalyticsData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Atualizar
            </Button>
            
            <Button>
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total de Estornos</p>
                  <p className="text-2xl font-bold">{metrics.totalRefunds.toLocaleString()}</p>
                </div>
                <DollarSign className="h-8 w-8 text-blue-600" />
              </div>
              <div className="mt-2 flex items-center">
                {trendAnalysis && (
                  <>
                    {trendAnalysis.trend === 'up' ? (
                      <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                    ) : trendAnalysis.trend === 'down' ? (
                      <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                    ) : (
                      <Activity className="h-4 w-4 text-gray-500 mr-1" />
                    )}
                    <span className={`text-sm ${trendAnalysis.trend === 'up' ? 'text-green-600' : trendAnalysis.trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
                      {trendAnalysis.changePercent.toFixed(1)}% vs período anterior
                    </span>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Valor Total</p>
                  <p className="text-2xl font-bold">
                    R$ {metrics.totalAmount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-green-600" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">
                  Taxa de Sucesso: {metrics.successRate.toFixed(1)}%
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Tempo Médio</p>
                  <p className="text-2xl font-bold">{Math.round(metrics.avgProcessingTime)}min</p>
                </div>
                <Clock className="h-8 w-8 text-orange-600" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">
                  Auto-aprovação: {metrics.autoApprovalRate.toFixed(1)}%
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Fraude Prevenida</p>
                  <p className="text-2xl font-bold text-red-600">{metrics.fraudPrevented}</p>
                </div>
                <Shield className="h-8 w-8 text-red-600" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-green-600">
                  {metrics.chargebacksPrevented} chargebacks evitados
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Analytics Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTab value="overview">Visão Geral</TabsTab>
          <TabsTab value="trends">Tendências</TabsTab>
          <TabsTab value="categories">Categorias</TabsTab>
          <TabsTab value="fraud">Anti-Fraude</TabsTab>
          <TabsTab value="ai-insights">IA & Insights</TabsTab>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Refund Volume Trend */}
            <Card>
              <CardHeader>
                <CardTitle>Volume de Estornos</CardTitle>
                <CardDescription>Tendência de volume nos últimos períodos</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="refunds"
                      stroke={chartColors.primary}
                      strokeWidth={2}
                      name="Estornos"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Success vs Rejection Rates */}
            <Card>
              <CardHeader>
                <CardTitle>Taxa de Aprovação vs Rejeição</CardTitle>
                <CardDescription>Comparação de aprovações e rejeições</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="approved"
                      stackId="1"
                      stroke={chartColors.secondary}
                      fill={chartColors.secondary}
                      name="Aprovados"
                    />
                    <Area
                      type="monotone"
                      dataKey="rejected"
                      stackId="1"
                      stroke={chartColors.danger}
                      fill={chartColors.danger}
                      name="Rejeitados"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Risk Score Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Distribuição de Risk Score</CardTitle>
                <CardDescription>Distribuição dos scores de risco ao longo do tempo</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip formatter={(value: any) => [`${(value * 100).toFixed(0)}%`, 'Risk Score']} />
                    <Line
                      type="monotone"
                      dataKey="avgRiskScore"
                      stroke={chartColors.warning}
                      strokeWidth={2}
                      name="Risk Score Médio"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Processing Time Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Tempo de Processamento</CardTitle>
                <CardDescription>Evolução do tempo médio de processamento</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value: any) => [`${value}min`, 'Tempo Médio']} />
                    <Bar
                      dataKey="processingTime"
                      fill={chartColors.info}
                      name="Tempo de Processamento (min)"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Trends Tab */}
        <TabsContent value="trends" className="mt-6">
          <div className="grid grid-cols-1 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Análise de Tendências Avançada</CardTitle>
                <CardDescription>
                  Análise detalhada de tendências com múltiplas métricas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={500}>
                  <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="refunds"
                      stroke={chartColors.primary}
                      strokeWidth={2}
                      name="Volume de Estornos"
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="amount"
                      stroke={chartColors.secondary}
                      strokeWidth={2}
                      name="Valor Total (R$)"
                    />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="processingTime"
                      stroke={chartColors.warning}
                      strokeWidth={2}
                      name="Tempo Processamento (min)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Categories Tab */}
        <TabsContent value="categories" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Category Distribution Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Distribuição por Categoria</CardTitle>
                <CardDescription>Percentual de estornos por categoria</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ category, percentage }) => `${category} (${percentage.toFixed(1)}%)`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Category Performance Table */}
            <Card>
              <CardHeader>
                <CardTitle>Performance por Categoria</CardTitle>
                <CardDescription>Métricas detalhadas de cada categoria</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {categoryData.map((category, index) => (
                    <div key={category.category} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{category.category}</h4>
                        <Badge style={{ backgroundColor: pieColors[index % pieColors.length] }}>
                          {category.count} casos
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Valor Total:</span>
                          <p className="font-medium">
                            R$ {category.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-600">Taxa de Sucesso:</span>
                          <p className="font-medium">{category.successRate.toFixed(1)}%</p>
                        </div>
                        <div>
                          <span className="text-gray-600">Risk Score Médio:</span>
                          <p className="font-medium">{(category.avgRiskScore * 100).toFixed(0)}%</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Fraud Analytics Tab */}
        <TabsContent value="fraud" className="mt-6">
          {fraudAnalytics && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Fraud Prevention Metrics */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-red-600" />
                    Métricas Anti-Fraude
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-red-50 rounded-lg">
                      <p className="text-sm text-gray-600">Tentativas de Fraude</p>
                      <p className="text-xl font-bold text-red-600">{fraudAnalytics.totalFraudAttempts}</p>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg">
                      <p className="text-sm text-gray-600">Fraudes Prevenidas</p>
                      <p className="text-xl font-bold text-green-600">{fraudAnalytics.fraudPrevented}</p>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Precisão do Modelo</span>
                      <span className="text-sm font-bold">{(fraudAnalytics.modelAccuracy * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={fraudAnalytics.modelAccuracy * 100} className="h-2" />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Verdadeiros Positivos:</span>
                      <p className="font-medium">{fraudAnalytics.truePositives}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Falsos Positivos:</span>
                      <p className="font-medium">{fraudAnalytics.falsePositives}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Top Fraud Indicators */}
              <Card>
                <CardHeader>
                  <CardTitle>Principais Indicadores de Fraude</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {fraudAnalytics.topFraudIndicators.map((indicator, index) => (
                      <div key={indicator.indicator} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="w-6 h-6 rounded-full p-0 flex items-center justify-center text-xs">
                            {index + 1}
                          </Badge>
                          <span className="text-sm">{indicator.indicator}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-red-500 h-2 rounded-full"
                              style={{ width: `${(indicator.frequency / Math.max(...fraudAnalytics.topFraudIndicators.map(i => i.frequency))) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">{indicator.frequency}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* AI Insights Tab */}
        <TabsContent value="ai-insights" className="mt-6">
          {aiInsights && (
            <div className="space-y-6">
              {/* AI Predictions */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-purple-600" />
                    Previsões de IA
                  </CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-medium text-purple-800 mb-2">Volume Próxima Semana</h4>
                    <p className="text-2xl font-bold text-purple-600">
                      {aiInsights.predictions.nextWeekVolume}
                    </p>
                    <p className="text-sm text-purple-600">estornos previstos</p>
                  </div>
                  
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-800 mb-2">Tendência de Risco</h4>
                    <div className="flex items-center gap-2">
                      {aiInsights.predictions.riskTrendDirection === 'up' ? (
                        <TrendingUp className="h-5 w-5 text-red-500" />
                      ) : aiInsights.predictions.riskTrendDirection === 'down' ? (
                        <TrendingDown className="h-5 w-5 text-green-500" />
                      ) : (
                        <Activity className="h-5 w-5 text-blue-500" />
                      )}
                      <span className="font-medium capitalize">
                        {aiInsights.predictions.riskTrendDirection}
                      </span>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-medium text-green-800 mb-2">Ações Recomendadas</h4>
                    <p className="text-2xl font-bold text-green-600">
                      {aiInsights.predictions.recommendedActions.length}
                    </p>
                    <p className="text-sm text-green-600">recomendações ativas</p>
                  </div>
                </CardContent>
              </Card>

              {/* Patterns and Anomalies */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Padrões Identificados</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Tendências Sazonais</h4>
                      <div className="space-y-2">
                        {aiInsights.patterns.seasonalTrends.map((trend, index) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span>{trend.period}</span>
                            <Badge variant={trend.impact > 0 ? "default" : "secondary"}>
                              {trend.impact > 0 ? '+' : ''}{trend.impact.toFixed(1)}%
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <Separator />
                    
                    <div>
                      <h4 className="font-medium mb-2">Comportamento do Cliente</h4>
                      <div className="space-y-2">
                        {aiInsights.patterns.customerBehavior.map((pattern, index) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span>{pattern.pattern}</span>
                            <span className="font-medium">{pattern.frequency}x</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Anomalias Detectadas</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {aiInsights.anomalies.length > 0 ? (
                      <div className="space-y-3">
                        {aiInsights.anomalies.map((anomaly, index) => (
                          <Alert key={index}>
                            <div className="flex items-start gap-2">
                              {anomaly.severity === 'high' ? (
                                <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5" />
                              ) : anomaly.severity === 'medium' ? (
                                <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5" />
                              ) : (
                                <AlertTriangle className="h-4 w-4 text-blue-500 mt-0.5" />
                              )}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-medium text-sm">{anomaly.type}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {anomaly.severity}
                                  </Badge>
                                </div>
                                <AlertDescription className="text-xs">
                                  {anomaly.description}
                                </AlertDescription>
                                <p className="text-xs text-gray-500 mt-1">
                                  {new Date(anomaly.timestamp).toLocaleString('pt-BR')}
                                </p>
                              </div>
                            </div>
                          </Alert>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-4 text-gray-500">
                        <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                        <p className="text-sm">Nenhuma anomalia detectada</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* AI Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-yellow-500" />
                    Recomendações da IA
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {aiInsights.predictions.recommendedActions.map((action, index) => (
                      <div key={index} className="p-3 border rounded-lg flex items-start gap-3">
                        <Target className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="text-sm font-medium">{action}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            Recomendação baseada em análise preditiva
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RefundAnalyticsDashboard;