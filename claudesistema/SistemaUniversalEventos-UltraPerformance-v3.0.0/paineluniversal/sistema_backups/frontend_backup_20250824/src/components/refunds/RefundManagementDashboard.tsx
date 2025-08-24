/**
 * Refund Management Dashboard - Central de Gestão de Estornos
 * Sistema Universal de Gestão de Eventos
 * 
 * Dashboard abrangente para gestão de estornos com recursos avançados:
 * - Visão geral de estornos em tempo real
 * - Análise de IA e detecção de fraude
 * - Workflows automáticos e aprovação
 * - Analytics e relatórios
 * - Gestão de chargebacks
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../ui/card';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTab 
} from '../ui/tabs';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  DollarSign,
  Shield,
  Brain,
  Zap,
  Eye,
  Filter,
  Download,
  RefreshCw,
  AlertCircle
} from 'lucide-react';

// Types
interface RefundCase {
  id: string;
  transactionId: string;
  customerId: number;
  amount: number;
  currency: string;
  status: RefundStatus;
  reason: RefundReason;
  priority: RefundPriority;
  createdAt: Date;
  updatedAt: Date;
  dueDate?: Date;
  approvedBy?: string;
  riskScore: number;
  aiRecommendation: string;
  processingTime?: number;
  gateway: string;
  paymentMethod: string;
}

enum RefundStatus {
  REQUESTED = 'requested',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  REJECTED = 'rejected',
  FAILED = 'failed'
}

enum RefundReason {
  CUSTOMER_REQUEST = 'customer_request',
  EVENT_CANCELLED = 'event_cancelled',
  DUPLICATE_PAYMENT = 'duplicate_payment',
  FRAUD_PREVENTION = 'fraud_prevention',
  TECHNICAL_ERROR = 'technical_error'
}

enum RefundPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
  CRITICAL = 'critical'
}

interface RefundMetrics {
  totalRefunds: number;
  pendingApproval: number;
  processing: number;
  completed: number;
  rejected: number;
  totalAmount: number;
  avgProcessingTime: number;
  fraudPrevented: number;
  autoApprovalRate: number;
  chargebacksPrevented: number;
}

interface AIInsights {
  fraudDetected: number;
  anomaliesFound: number;
  patternsIdentified: string[];
  riskTrends: Array<{ date: string; risk: number }>;
  recommendations: string[];
}

const RefundManagementDashboard: React.FC = () => {
  // State
  const [refunds, setRefunds] = useState<RefundCase[]>([]);
  const [metrics, setMetrics] = useState<RefundMetrics | null>(null);
  const [aiInsights, setAIInsights] = useState<AIInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [activeTab, setActiveTab] = useState('overview');
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    gateway: 'all',
    riskLevel: 'all'
  });

  // Effects
  useEffect(() => {
    loadRefundData();
    const interval = setInterval(loadRefundData, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, [selectedTimeRange, filters]);

  // Data Loading
  const loadRefundData = async () => {
    try {
      setLoading(true);
      
      // Load refund cases
      const refundsResponse = await fetch('/api/refunds', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const refundsData = await refundsResponse.json();
      
      // Load metrics
      const metricsResponse = await fetch('/api/refunds/metrics', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const metricsData = await metricsResponse.json();
      
      // Load AI insights
      const aiResponse = await fetch('/api/refunds/ai-insights', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const aiData = await aiResponse.json();
      
      setRefunds(refundsData.refunds || []);
      setMetrics(metricsData);
      setAIInsights(aiData);
    } catch (error) {
      console.error('Erro ao carregar dados de estornos:', error);
    } finally {
      setLoading(false);
    }
  };

  // Computed values
  const filteredRefunds = useMemo(() => {
    return refunds.filter(refund => {
      if (filters.status !== 'all' && refund.status !== filters.status) return false;
      if (filters.priority !== 'all' && refund.priority !== filters.priority) return false;
      if (filters.gateway !== 'all' && refund.gateway !== filters.gateway) return false;
      if (filters.riskLevel !== 'all') {
        const riskLevel = refund.riskScore > 0.7 ? 'high' : refund.riskScore > 0.4 ? 'medium' : 'low';
        if (riskLevel !== filters.riskLevel) return false;
      }
      return true;
    });
  }, [refunds, filters]);

  const urgentCases = useMemo(() => {
    return refunds.filter(refund => 
      refund.priority === RefundPriority.URGENT || 
      refund.priority === RefundPriority.CRITICAL ||
      (refund.dueDate && new Date(refund.dueDate) <= new Date(Date.now() + 24 * 60 * 60 * 1000))
    );
  }, [refunds]);

  // Handlers
  const handleApproveRefund = async (refundId: string) => {
    try {
      await fetch(`/api/refunds/${refundId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ approved_by: 'current_user' })
      });
      
      await loadRefundData();
    } catch (error) {
      console.error('Erro ao aprovar estorno:', error);
    }
  };

  const handleRejectRefund = async (refundId: string, reason: string) => {
    try {
      await fetch(`/api/refunds/${refundId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          rejected_by: 'current_user',
          reason: reason
        })
      });
      
      await loadRefundData();
    } catch (error) {
      console.error('Erro ao rejeitar estorno:', error);
    }
  };

  const getStatusColor = (status: RefundStatus) => {
    switch (status) {
      case RefundStatus.COMPLETED: return 'bg-green-500';
      case RefundStatus.PROCESSING: return 'bg-blue-500';
      case RefundStatus.PENDING_APPROVAL: return 'bg-yellow-500';
      case RefundStatus.REJECTED: return 'bg-red-500';
      case RefundStatus.FAILED: return 'bg-red-600';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityColor = (priority: RefundPriority) => {
    switch (priority) {
      case RefundPriority.CRITICAL: return 'bg-red-500';
      case RefundPriority.URGENT: return 'bg-orange-500';
      case RefundPriority.HIGH: return 'bg-yellow-500';
      case RefundPriority.MEDIUM: return 'bg-blue-500';
      case RefundPriority.LOW: return 'bg-gray-500';
    }
  };

  const getRiskColor = (riskScore: number) => {
    if (riskScore > 0.8) return 'text-red-600 bg-red-50';
    if (riskScore > 0.6) return 'text-orange-600 bg-orange-50';
    if (riskScore > 0.4) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Carregando dados de estornos...</span>
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
              <Shield className="h-8 w-8 text-blue-600" />
              Central de Estornos
            </h1>
            <p className="text-gray-600 mt-1">
              Gestão inteligente de estornos com IA e prevenção de fraude
            </p>
          </div>
          
          <div className="flex gap-3">
            <Button variant="outline" onClick={loadRefundData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Atualizar
            </Button>
            <Button>
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
          </div>
        </div>
        
        {/* Urgent Alerts */}
        {urgentCases.length > 0 && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <span className="font-semibold text-red-800">
                {urgentCases.length} caso(s) urgente(s) requerem atenção imediata
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Metrics Cards */}
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
              <div className="mt-2">
                <span className="text-sm text-gray-600">
                  R$ {metrics.totalAmount.toLocaleString('pt-BR', { 
                    minimumFractionDigits: 2 
                  })}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Pendente Aprovação</p>
                  <p className="text-2xl font-bold text-yellow-600">{metrics.pendingApproval}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="mt-2">
                <Progress value={(metrics.pendingApproval / metrics.totalRefunds) * 100} className="h-2" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Taxa de Aprovação Auto</p>
                  <p className="text-2xl font-bold text-green-600">{metrics.autoApprovalRate}%</p>
                </div>
                <Zap className="h-8 w-8 text-green-600" />
              </div>
              <div className="flex items-center mt-2">
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                <span className="text-sm text-green-600">+12% este mês</span>
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

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTab value="overview">Visão Geral</TabsTab>
          <TabsTab value="pending">Pendentes</TabsTab>
          <TabsTab value="ai-insights">IA & Analytics</TabsTab>
          <TabsTab value="chargebacks">Chargebacks</TabsTab>
          <TabsTab value="reports">Relatórios</TabsTab>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Refunds */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Estornos Recentes</CardTitle>
                <CardDescription>
                  Últimos estornos processados no sistema
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredRefunds.slice(0, 10).map((refund) => (
                    <div key={refund.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(refund.status)}`} />
                        <div>
                          <p className="font-medium">#{refund.id.slice(0, 8)}</p>
                          <p className="text-sm text-gray-600">
                            R$ {refund.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Badge className={getPriorityColor(refund.priority)}>
                          {refund.priority}
                        </Badge>
                        <Badge className={getRiskColor(refund.riskScore)}>
                          Risk: {(refund.riskScore * 100).toFixed(0)}%
                        </Badge>
                      </div>
                      
                      <div className="flex gap-2">
                        {refund.status === RefundStatus.PENDING_APPROVAL && (
                          <>
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => handleApproveRefund(refund.id)}
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Aprovar
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleRejectRefund(refund.id, 'Manual rejection')}
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Rejeitar
                            </Button>
                          </>
                        )}
                        <Button size="sm" variant="ghost">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* AI Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  Insights de IA
                </CardTitle>
              </CardHeader>
              <CardContent>
                {aiInsights && (
                  <div className="space-y-4">
                    <div className="p-3 bg-purple-50 rounded-lg">
                      <p className="text-sm font-medium text-purple-800">
                        {aiInsights.fraudDetected} tentativas de fraude detectadas
                      </p>
                    </div>
                    
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm font-medium text-blue-800">
                        {aiInsights.anomaliesFound} anomalias identificadas
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium mb-2">Padrões Identificados:</h4>
                      <ul className="space-y-1">
                        {aiInsights.patternsIdentified.map((pattern, index) => (
                          <li key={index} className="text-xs text-gray-600 flex items-center gap-1">
                            <AlertCircle className="h-3 w-3" />
                            {pattern}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium mb-2">Recomendações:</h4>
                      <ul className="space-y-1">
                        {aiInsights.recommendations.map((rec, index) => (
                          <li key={index} className="text-xs text-green-700 flex items-center gap-1">
                            <CheckCircle className="h-3 w-3" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="pending" className="mt-6">
          {/* Pending Approvals Component */}
          <Card>
            <CardHeader>
              <CardTitle>Estornos Pendentes de Aprovação</CardTitle>
              <CardDescription>
                {metrics?.pendingApproval || 0} estornos aguardando aprovação manual
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Implementation for pending refunds management */}
              <div className="text-center py-8 text-gray-500">
                Componente de aprovações pendentes será implementado aqui
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ai-insights" className="mt-6">
          {/* AI Insights Component */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Análise de IA em Tempo Real</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  Dashboards de IA e analytics avançados
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Modelos Preditivos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  Modelos de ML para previsão de risco
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="chargebacks" className="mt-6">
          {/* Chargeback Management Component */}
          <Card>
            <CardHeader>
              <CardTitle>Gestão de Chargebacks</CardTitle>
              <CardDescription>
                Prevenção e gestão de contestações de cartão
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                Sistema de gestão de chargebacks será implementado aqui
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="mt-6">
          {/* Reports Component */}
          <Card>
            <CardHeader>
              <CardTitle>Relatórios e Analytics</CardTitle>
              <CardDescription>
                Relatórios detalhados e análises de performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                Sistema de relatórios avançados será implementado aqui
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RefundManagementDashboard;