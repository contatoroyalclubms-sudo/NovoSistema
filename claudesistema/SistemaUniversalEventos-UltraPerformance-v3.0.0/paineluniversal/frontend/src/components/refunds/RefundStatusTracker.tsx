/**
 * Refund Status Tracker - Rastreamento em Tempo Real de Estornos
 * Sistema Universal de Gestão de Eventos
 * 
 * Componente avançado para rastreamento de status com recursos:
 * - Timeline visual de progresso
 * - Atualizações em tempo real via WebSocket
 * - Notificações push e email
 * - Estimativas de tempo precisas
 * - Integração com AI para insights
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { Separator } from '../ui/separator';
import { 
  CheckCircle,
  Clock,
  AlertTriangle,
  XCircle,
  Loader2,
  Bell,
  MessageSquare,
  Download,
  RefreshCw,
  Eye,
  Calendar,
  User,
  DollarSign,
  FileText,
  Brain,
  Shield,
  Zap,
  TrendingUp,
  Activity
} from 'lucide-react';

// Types
interface RefundStatus {
  id: string;
  transactionId: string;
  refundId: string;
  amount: number;
  currency: string;
  status: RefundStatusType;
  currentStep: number;
  totalSteps: number;
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  estimatedCompletionTime?: Date;
  priority: RefundPriority;
  gateway: string;
  paymentMethod: string;
  reason: string;
  riskScore: number;
  timeline: RefundTimelineEvent[];
  metadata: Record<string, any>;
}

enum RefundStatusType {
  REQUESTED = 'requested',
  VALIDATING = 'validating',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  REJECTED = 'rejected',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

enum RefundPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
  CRITICAL = 'critical'
}

interface RefundTimelineEvent {
  id: string;
  timestamp: Date;
  status: RefundStatusType;
  description: string;
  details?: string;
  actor?: string;
  automated: boolean;
  duration?: number;
  metadata?: Record<string, any>;
}

interface RefundTrackerProps {
  refundId: string;
  showTimeline?: boolean;
  showAIInsights?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const RefundStatusTracker: React.FC<RefundTrackerProps> = ({
  refundId,
  showTimeline = true,
  showAIInsights = true,
  autoRefresh = true,
  refreshInterval = 30000 // 30 seconds
}) => {
  // State
  const [refundStatus, setRefundStatus] = useState<RefundStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [notifications, setNotifications] = useState<string[]>([]);
  const [aiInsights, setAIInsights] = useState<any>(null);

  // WebSocket connection
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Load refund status
  const loadRefundStatus = useCallback(async () => {
    try {
      setError(null);
      const response = await fetch(`/api/refunds/${refundId}/status`);
      
      if (!response.ok) {
        throw new Error('Falha ao carregar status do estorno');
      }
      
      const data = await response.json();
      setRefundStatus(data);
      
      // Load AI insights if enabled
      if (showAIInsights) {
        loadAIInsights(refundId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [refundId, showAIInsights]);

  // Load AI insights
  const loadAIInsights = async (refundId: string) => {
    try {
      const response = await fetch(`/api/refunds/${refundId}/ai-insights`);
      if (response.ok) {
        const insights = await response.json();
        setAIInsights(insights);
      }
    } catch (error) {
      console.error('Erro ao carregar insights de IA:', error);
    }
  };

  // Setup WebSocket connection
  useEffect(() => {
    if (autoRefresh) {
      const websocket = new WebSocket(`ws://localhost:8000/ws/refunds/${refundId}`);
      
      websocket.onopen = () => {
        console.log('WebSocket conectado');
        setWsConnected(true);
      };
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'refund_status_update') {
          setRefundStatus(data.refund);
          setNotifications(prev => [...prev, `Status atualizado: ${data.refund.status}`]);
        }
        
        if (data.type === 'refund_timeline_update') {
          setRefundStatus(prev => prev ? {
            ...prev,
            timeline: data.timeline
          } : null);
        }
      };
      
      websocket.onclose = () => {
        console.log('WebSocket desconectado');
        setWsConnected(false);
      };
      
      websocket.onerror = (error) => {
        console.error('Erro no WebSocket:', error);
        setWsConnected(false);
      };
      
      setWs(websocket);
      
      return () => {
        websocket.close();
      };
    }
  }, [refundId, autoRefresh]);

  // Auto-refresh fallback
  useEffect(() => {
    if (!wsConnected && autoRefresh) {
      const interval = setInterval(loadRefundStatus, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [wsConnected, autoRefresh, refreshInterval, loadRefundStatus]);

  // Initial load
  useEffect(() => {
    loadRefundStatus();
  }, [loadRefundStatus]);

  // Dismiss notification
  const dismissNotification = (index: number) => {
    setNotifications(prev => prev.filter((_, i) => i !== index));
  };

  // Get status configuration
  const getStatusConfig = (status: RefundStatusType) => {
    const configs = {
      [RefundStatusType.REQUESTED]: {
        color: 'bg-blue-500',
        textColor: 'text-blue-700',
        bgColor: 'bg-blue-50',
        icon: <Clock className="h-4 w-4" />,
        label: 'Solicitado',
        description: 'Estorno solicitado e em análise inicial'
      },
      [RefundStatusType.VALIDATING]: {
        color: 'bg-yellow-500',
        textColor: 'text-yellow-700',
        bgColor: 'bg-yellow-50',
        icon: <Brain className="h-4 w-4" />,
        label: 'Validando',
        description: 'IA analisando elegibilidade e risco'
      },
      [RefundStatusType.PENDING_APPROVAL]: {
        color: 'bg-orange-500',
        textColor: 'text-orange-700',
        bgColor: 'bg-orange-50',
        icon: <User className="h-4 w-4" />,
        label: 'Aguardando Aprovação',
        description: 'Análise manual necessária'
      },
      [RefundStatusType.APPROVED]: {
        color: 'bg-green-500',
        textColor: 'text-green-700',
        bgColor: 'bg-green-50',
        icon: <CheckCircle className="h-4 w-4" />,
        label: 'Aprovado',
        description: 'Estorno aprovado para processamento'
      },
      [RefundStatusType.PROCESSING]: {
        color: 'bg-blue-500',
        textColor: 'text-blue-700',
        bgColor: 'bg-blue-50',
        icon: <Loader2 className="h-4 w-4 animate-spin" />,
        label: 'Processando',
        description: 'Processando através do gateway'
      },
      [RefundStatusType.COMPLETED]: {
        color: 'bg-green-600',
        textColor: 'text-green-800',
        bgColor: 'bg-green-50',
        icon: <CheckCircle className="h-4 w-4" />,
        label: 'Concluído',
        description: 'Estorno processado com sucesso'
      },
      [RefundStatusType.REJECTED]: {
        color: 'bg-red-500',
        textColor: 'text-red-700',
        bgColor: 'bg-red-50',
        icon: <XCircle className="h-4 w-4" />,
        label: 'Rejeitado',
        description: 'Estorno rejeitado após análise'
      },
      [RefundStatusType.FAILED]: {
        color: 'bg-red-600',
        textColor: 'text-red-800',
        bgColor: 'bg-red-50',
        icon: <AlertTriangle className="h-4 w-4" />,
        label: 'Falhou',
        description: 'Erro no processamento do estorno'
      },
      [RefundStatusType.CANCELLED]: {
        color: 'bg-gray-500',
        textColor: 'text-gray-700',
        bgColor: 'bg-gray-50',
        icon: <XCircle className="h-4 w-4" />,
        label: 'Cancelado',
        description: 'Estorno cancelado pelo solicitante'
      }
    };
    
    return configs[status];
  };

  // Get priority configuration
  const getPriorityConfig = (priority: RefundPriority) => {
    const configs = {
      [RefundPriority.LOW]: { color: 'bg-gray-500', label: 'Baixa' },
      [RefundPriority.MEDIUM]: { color: 'bg-blue-500', label: 'Média' },
      [RefundPriority.HIGH]: { color: 'bg-yellow-500', label: 'Alta' },
      [RefundPriority.URGENT]: { color: 'bg-orange-500', label: 'Urgente' },
      [RefundPriority.CRITICAL]: { color: 'bg-red-500', label: 'Crítica' }
    };
    
    return configs[priority];
  };

  // Calculate progress percentage
  const calculateProgress = (status: RefundStatusType, currentStep: number, totalSteps: number) => {
    if (status === RefundStatusType.COMPLETED) return 100;
    if (status === RefundStatusType.REJECTED || status === RefundStatusType.FAILED || status === RefundStatusType.CANCELLED) return 0;
    return Math.round((currentStep / totalSteps) * 100);
  };

  // Format time remaining
  const formatTimeRemaining = (estimatedTime?: Date) => {
    if (!estimatedTime) return 'Tempo não estimado';
    
    const now = new Date();
    const diff = estimatedTime.getTime() - now.getTime();
    
    if (diff <= 0) return 'Em atraso';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}min restantes`;
    } else {
      return `${minutes}min restantes`;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          <span>Carregando status do estorno...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8">
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {error}
              <Button
                variant="outline"
                size="sm"
                onClick={loadRefundStatus}
                className="ml-2"
              >
                Tentar novamente
              </Button>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!refundStatus) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-gray-500">
          Estorno não encontrado
        </CardContent>
      </Card>
    );
  }

  const statusConfig = getStatusConfig(refundStatus.status);
  const priorityConfig = getPriorityConfig(refundStatus.priority);
  const progress = calculateProgress(refundStatus.status, refundStatus.currentStep, refundStatus.totalSteps);

  return (
    <div className="space-y-6">
      {/* Notifications */}
      {notifications.length > 0 && (
        <div className="space-y-2">
          {notifications.map((notification, index) => (
            <Alert key={index}>
              <Bell className="h-4 w-4" />
              <AlertDescription className="flex items-center justify-between">
                {notification}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => dismissNotification(index)}
                >
                  ×
                </Button>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* Main Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-3">
                <div className={`p-2 rounded-full ${statusConfig.bgColor}`}>
                  {statusConfig.icon}
                </div>
                Estorno #{refundStatus.refundId.slice(0, 8)}
                <div className="flex items-center gap-1">
                  {wsConnected && (
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  )}
                  <span className="text-xs text-gray-500">
                    {wsConnected ? 'Tempo Real' : 'Offline'}
                  </span>
                </div>
              </CardTitle>
              <CardDescription>
                Transação: {refundStatus.transactionId}
              </CardDescription>
            </div>
            
            <div className="flex items-center gap-2">
              <Badge className={priorityConfig.color}>
                {priorityConfig.label}
              </Badge>
              <Button variant="outline" size="sm" onClick={loadRefundStatus}>
                <RefreshCw className="h-4 w-4 mr-1" />
                Atualizar
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Status and Progress */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge className={`${statusConfig.color} text-white`}>
                  {statusConfig.label}
                </Badge>
                <span className="text-sm text-gray-600">
                  {statusConfig.description}
                </span>
              </div>
              <span className="text-sm font-medium">
                {refundStatus.currentStep} de {refundStatus.totalSteps} etapas
              </span>
            </div>
            
            <Progress value={progress} className="h-3" />
            
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>Progresso: {progress}%</span>
              <span>{formatTimeRemaining(refundStatus.estimatedCompletionTime)}</span>
            </div>
          </div>

          {/* Refund Details */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-gray-500" />
              <div>
                <span className="text-xs text-gray-500">Valor</span>
                <p className="font-medium">
                  R$ {refundStatus.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-gray-500" />
              <div>
                <span className="text-xs text-gray-500">Risco</span>
                <p className="font-medium">{(refundStatus.riskScore * 100).toFixed(0)}%</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-gray-500" />
              <div>
                <span className="text-xs text-gray-500">Gateway</span>
                <p className="font-medium">{refundStatus.gateway}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <div>
                <span className="text-xs text-gray-500">Criado</span>
                <p className="font-medium">
                  {new Date(refundStatus.createdAt).toLocaleDateString('pt-BR')}
                </p>
              </div>
            </div>
          </div>

          {/* AI Insights */}
          {showAIInsights && aiInsights && (
            <Card className="bg-purple-50 border-purple-200">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Brain className="h-4 w-4 text-purple-600" />
                  Insights de IA
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {aiInsights.prediction && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Probabilidade de Sucesso:</span>
                    <div className="flex items-center gap-2">
                      <Progress value={aiInsights.prediction * 100} className="w-16 h-2" />
                      <span className="text-sm font-medium">
                        {(aiInsights.prediction * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                )}
                
                {aiInsights.recommendations && aiInsights.recommendations.length > 0 && (
                  <div>
                    <h5 className="text-xs font-medium mb-1">Recomendações:</h5>
                    <ul className="text-xs space-y-1">
                      {aiInsights.recommendations.map((rec: string, index: number) => (
                        <li key={index} className="flex items-start gap-1">
                          <Zap className="h-3 w-3 mt-0.5 text-purple-600 flex-shrink-0" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>

      {/* Timeline */}
      {showTimeline && refundStatus.timeline && refundStatus.timeline.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Histórico de Eventos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {refundStatus.timeline.map((event, index) => {
                const eventStatusConfig = getStatusConfig(event.status);
                const isLast = index === refundStatus.timeline.length - 1;
                
                return (
                  <div key={event.id} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className={`p-2 rounded-full ${eventStatusConfig.bgColor} ${eventStatusConfig.textColor}`}>
                        {eventStatusConfig.icon}
                      </div>
                      {!isLast && (
                        <div className="w-0.5 h-8 bg-gray-300 my-1" />
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="text-sm font-medium">{event.description}</h4>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          {event.automated && (
                            <Badge variant="outline" className="text-xs">
                              <Zap className="h-3 w-3 mr-1" />
                              Auto
                            </Badge>
                          )}
                          <span>{new Date(event.timestamp).toLocaleString('pt-BR')}</span>
                        </div>
                      </div>
                      
                      {event.details && (
                        <p className="text-sm text-gray-600">{event.details}</p>
                      )}
                      
                      {event.actor && (
                        <p className="text-xs text-gray-500 mt-1">
                          Por: {event.actor}
                        </p>
                      )}
                      
                      {event.duration && (
                        <p className="text-xs text-gray-500 mt-1">
                          Duração: {event.duration}min
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <Card>
        <CardContent className="flex items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Baixar Comprovante
            </Button>
            <Button variant="outline" size="sm">
              <FileText className="h-4 w-4 mr-2" />
              Visualizar Detalhes
            </Button>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <MessageSquare className="h-4 w-4 mr-2" />
              Suporte
            </Button>
            <Button variant="outline" size="sm">
              <Bell className="h-4 w-4 mr-2" />
              Notificar
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RefundStatusTracker;