/**
 * Refund Request Form - Formulário Inteligente de Solicitação de Estorno
 * Sistema Universal de Gestão de Eventos
 * 
 * Formulário avançado com recursos de IA:
 * - Validação inteligente em tempo real
 * - Sugestões automáticas de motivo
 * - Análise de elegibilidade instantânea
 * - Upload de documentos comprobatórios
 * - Previsão de tempo de processamento
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
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
  AlertCircle,
  CheckCircle,
  Clock,
  Upload,
  Brain,
  Shield,
  Info,
  Zap,
  DollarSign,
  Calendar,
  FileText,
  AlertTriangle,
  Loader2
} from 'lucide-react';

// Validation Schema
const refundRequestSchema = z.object({
  transactionId: z.string().min(1, 'ID da transação é obrigatório'),
  amount: z.number().min(0.01, 'Valor deve ser maior que zero'),
  reason: z.string().min(1, 'Motivo do estorno é obrigatório'),
  description: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high', 'urgent']),
  supportingDocuments: z.array(z.any()).optional(),
  customerContact: z.string().email().optional(),
});

type RefundRequestFormData = z.infer<typeof refundRequestSchema>;

// Types
interface Transaction {
  id: string;
  amount: number;
  currency: string;
  date: Date;
  paymentMethod: string;
  gateway: string;
  status: string;
  customerEmail: string;
}

interface EligibilityAnalysis {
  eligible: boolean;
  confidence: number;
  riskScore: number;
  reasons: string[];
  warnings: string[];
  estimatedProcessingTime: number;
  autoApprovalProbability: number;
}

interface RefundReason {
  code: string;
  label: string;
  description: string;
  category: string;
  suggestedPriority: string;
  requiresDocuments: boolean;
}

const refundReasons: RefundReason[] = [
  {
    code: 'customer_request',
    label: 'Solicitação do Cliente',
    description: 'Cliente solicita cancelamento por motivos pessoais',
    category: 'customer',
    suggestedPriority: 'medium',
    requiresDocuments: false
  },
  {
    code: 'event_cancelled',
    label: 'Evento Cancelado',
    description: 'Evento foi cancelado pela organização',
    category: 'operational',
    suggestedPriority: 'high',
    requiresDocuments: true
  },
  {
    code: 'duplicate_payment',
    label: 'Pagamento Duplicado',
    description: 'Cliente foi cobrado mais de uma vez',
    category: 'technical',
    suggestedPriority: 'high',
    requiresDocuments: false
  },
  {
    code: 'fraud_prevention',
    label: 'Prevenção de Fraude',
    description: 'Transação suspeita identificada',
    category: 'security',
    suggestedPriority: 'urgent',
    requiresDocuments: true
  },
  {
    code: 'technical_error',
    label: 'Erro Técnico',
    description: 'Falha no sistema durante processamento',
    category: 'technical',
    suggestedPriority: 'high',
    requiresDocuments: false
  },
  {
    code: 'quality_issue',
    label: 'Problema de Qualidade',
    description: 'Produto/serviço não atende às expectativas',
    category: 'quality',
    suggestedPriority: 'medium',
    requiresDocuments: true
  }
];

interface RefundRequestFormProps {
  transactionId?: string;
  onSuccess?: (refundId: string) => void;
  onCancel?: () => void;
}

const RefundRequestForm: React.FC<RefundRequestFormProps> = ({
  transactionId: initialTransactionId,
  onSuccess,
  onCancel
}) => {
  // Form state
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [eligibilityAnalysis, setEligibilityAnalysis] = useState<EligibilityAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);

  // Form setup
  const {
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid }
  } = useForm<RefundRequestFormData>({
    resolver: zodResolver(refundRequestSchema),
    defaultValues: {
      transactionId: initialTransactionId || '',
      priority: 'medium',
      supportingDocuments: []
    },
    mode: 'onChange'
  });

  // Watch form values
  const watchedTransactionId = watch('transactionId');
  const watchedAmount = watch('amount');
  const watchedReason = watch('reason');

  // Effects
  useEffect(() => {
    if (watchedTransactionId) {
      loadTransactionDetails(watchedTransactionId);
    }
  }, [watchedTransactionId]);

  useEffect(() => {
    if (transaction && watchedAmount && watchedReason) {
      analyzeEligibility();
    }
  }, [transaction, watchedAmount, watchedReason]);

  useEffect(() => {
    if (watchedReason) {
      const reason = refundReasons.find(r => r.code === watchedReason);
      if (reason) {
        setValue('priority', reason.suggestedPriority as any);
        generateAISuggestions(reason);
      }
    }
  }, [watchedReason, setValue]);

  // Load transaction details
  const loadTransactionDetails = async (transactionId: string) => {
    try {
      const response = await fetch(`/api/transactions/${transactionId}`);
      if (response.ok) {
        const transactionData = await response.json();
        setTransaction(transactionData);
        setValue('amount', transactionData.amount);
      }
    } catch (error) {
      console.error('Erro ao carregar detalhes da transação:', error);
    }
  };

  // Analyze eligibility with AI
  const analyzeEligibility = async () => {
    if (!transaction || !watchedAmount || !watchedReason) return;

    setIsAnalyzing(true);
    try {
      const response = await fetch('/api/refunds/analyze-eligibility', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transactionId: transaction.id,
          amount: watchedAmount,
          reason: watchedReason,
          originalTransaction: transaction
        })
      });

      if (response.ok) {
        const analysis = await response.json();
        setEligibilityAnalysis(analysis);
      }
    } catch (error) {
      console.error('Erro na análise de elegibilidade:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Generate AI suggestions
  const generateAISuggestions = async (reason: RefundReason) => {
    try {
      const response = await fetch('/api/refunds/ai-suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          reason: reason.code,
          category: reason.category,
          transaction: transaction
        })
      });

      if (response.ok) {
        const suggestions = await response.json();
        setAiSuggestions(suggestions.suggestions || []);
      }
    } catch (error) {
      console.error('Erro ao gerar sugestões de IA:', error);
    }
  };

  // Handle file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const newFiles = Array.from(event.target.files);
      setUploadedFiles(prev => [...prev, ...newFiles]);
      setValue('supportingDocuments', [...uploadedFiles, ...newFiles]);
    }
  };

  // Remove uploaded file
  const removeFile = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(newFiles);
    setValue('supportingDocuments', newFiles);
  };

  // Submit form
  const onSubmit = async (data: RefundRequestFormData) => {
    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('transactionId', data.transactionId);
      formData.append('amount', data.amount.toString());
      formData.append('reason', data.reason);
      formData.append('priority', data.priority);
      if (data.description) {
        formData.append('description', data.description);
      }
      if (data.customerContact) {
        formData.append('customerContact', data.customerContact);
      }

      // Append files
      uploadedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file);
      });

      const response = await fetch('/api/refunds/request', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        onSuccess?.(result.refundId);
      } else {
        throw new Error('Falha ao solicitar estorno');
      }
    } catch (error) {
      console.error('Erro ao submeter solicitação:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get eligibility status
  const getEligibilityStatus = () => {
    if (!eligibilityAnalysis) return null;

    if (eligibilityAnalysis.eligible && eligibilityAnalysis.confidence > 0.8) {
      return {
        icon: <CheckCircle className="h-5 w-5 text-green-500" />,
        text: 'Elegível para Estorno',
        color: 'bg-green-50 border-green-200 text-green-800'
      };
    } else if (eligibilityAnalysis.eligible) {
      return {
        icon: <AlertTriangle className="h-5 w-5 text-yellow-500" />,
        text: 'Elegível com Ressalvas',
        color: 'bg-yellow-50 border-yellow-200 text-yellow-800'
      };
    } else {
      return {
        icon: <AlertCircle className="h-5 w-5 text-red-500" />,
        text: 'Não Elegível',
        color: 'bg-red-50 border-red-200 text-red-800'
      };
    }
  };

  const eligibilityStatus = getEligibilityStatus();

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <DollarSign className="h-6 w-6 text-blue-600" />
            Solicitar Estorno
          </CardTitle>
          <CardDescription>
            Preencha os dados para solicitar o estorno de uma transação
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Transaction Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="transactionId">ID da Transação *</Label>
                <Controller
                  name="transactionId"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      placeholder="Digite o ID da transação"
                      error={errors.transactionId?.message}
                    />
                  )}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="amount">Valor do Estorno *</Label>
                <Controller
                  name="amount"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="0,00"
                      onChange={(e) => field.onChange(parseFloat(e.target.value))}
                      error={errors.amount?.message}
                    />
                  )}
                />
              </div>
            </div>

            {/* Transaction Details */}
            {transaction && (
              <Card className="bg-gray-50">
                <CardContent className="p-4">
                  <h4 className="font-medium mb-3">Detalhes da Transação</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Valor Original:</span>
                      <p className="font-medium">
                        R$ {transaction.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-600">Data:</span>
                      <p className="font-medium">{new Date(transaction.date).toLocaleDateString('pt-BR')}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Método:</span>
                      <p className="font-medium">{transaction.paymentMethod}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Gateway:</span>
                      <p className="font-medium">{transaction.gateway}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Reason Selection */}
            <div className="space-y-2">
              <Label htmlFor="reason">Motivo do Estorno *</Label>
              <Controller
                name="reason"
                control={control}
                render={({ field }) => (
                  <Select onValueChange={field.onChange} value={field.value}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o motivo do estorno" />
                    </SelectTrigger>
                    <SelectContent>
                      {refundReasons.map((reason) => (
                        <SelectItem key={reason.code} value={reason.code}>
                          <div className="flex items-center gap-2">
                            <span>{reason.label}</span>
                            <Badge variant="outline" className="text-xs">
                              {reason.category}
                            </Badge>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
              {errors.reason && (
                <p className="text-sm text-red-600">{errors.reason.message}</p>
              )}
            </div>

            {/* Priority */}
            <div className="space-y-2">
              <Label htmlFor="priority">Prioridade</Label>
              <Controller
                name="priority"
                control={control}
                render={({ field }) => (
                  <Select onValueChange={field.onChange} value={field.value}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Baixa</SelectItem>
                      <SelectItem value="medium">Média</SelectItem>
                      <SelectItem value="high">Alta</SelectItem>
                      <SelectItem value="urgent">Urgente</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Descrição Adicional</Label>
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <Textarea
                    {...field}
                    placeholder="Descreva detalhes adicionais sobre a solicitação..."
                    rows={4}
                  />
                )}
              />
            </div>

            {/* AI Suggestions */}
            {aiSuggestions.length > 0 && (
              <Card className="bg-purple-50 border-purple-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Brain className="h-5 w-5 text-purple-600" />
                    <h4 className="font-medium text-purple-800">Sugestões de IA</h4>
                  </div>
                  <ul className="space-y-2">
                    {aiSuggestions.map((suggestion, index) => (
                      <li key={index} className="text-sm text-purple-700 flex items-start gap-2">
                        <Zap className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        {suggestion}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* File Upload */}
            <div className="space-y-2">
              <Label>Documentos Comprobatórios</Label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="mt-4">
                    <Label htmlFor="file-upload" className="cursor-pointer">
                      <span className="text-blue-600 hover:text-blue-500">
                        Clique para fazer upload
                      </span>
                      <span className="text-gray-500"> ou arraste arquivos aqui</span>
                    </Label>
                    <input
                      id="file-upload"
                      type="file"
                      multiple
                      className="sr-only"
                      onChange={handleFileUpload}
                      accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                    />
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    PDF, JPG, PNG, DOC até 10MB cada
                  </p>
                </div>
              </div>

              {/* Uploaded Files */}
              {uploadedFiles.length > 0 && (
                <div className="space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        <span className="text-sm">{file.name}</span>
                        <span className="text-xs text-gray-500">
                          ({(file.size / 1024 / 1024).toFixed(2)} MB)
                        </span>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                      >
                        ×
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Eligibility Analysis */}
            {isAnalyzing && (
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
                    <span className="text-blue-800">Analisando elegibilidade com IA...</span>
                  </div>
                </CardContent>
              </Card>
            )}

            {eligibilityAnalysis && eligibilityStatus && (
              <Card className={`border ${eligibilityStatus.color}`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      {eligibilityStatus.icon}
                      <span className="font-medium">{eligibilityStatus.text}</span>
                    </div>
                    <Badge variant="outline">
                      Confiança: {(eligibilityAnalysis.confidence * 100).toFixed(0)}%
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <span className="text-sm text-gray-600">Risco:</span>
                      <div className="flex items-center gap-2">
                        <Progress value={eligibilityAnalysis.riskScore * 100} className="h-2" />
                        <span className="text-sm">{(eligibilityAnalysis.riskScore * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Aprovação Auto:</span>
                      <div className="flex items-center gap-2">
                        <Progress value={eligibilityAnalysis.autoApprovalProbability * 100} className="h-2" />
                        <span className="text-sm">{(eligibilityAnalysis.autoApprovalProbability * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Tempo Estimado:</span>
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span className="text-sm">{eligibilityAnalysis.estimatedProcessingTime}min</span>
                      </div>
                    </div>
                  </div>

                  {eligibilityAnalysis.warnings.length > 0 && (
                    <Alert>
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        <ul className="list-disc list-inside">
                          {eligibilityAnalysis.warnings.map((warning, index) => (
                            <li key={index}>{warning}</li>
                          ))}
                        </ul>
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            )}
          </form>
        </CardContent>

        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
          <Button
            onClick={handleSubmit(onSubmit)}
            disabled={!isValid || isSubmitting || (eligibilityAnalysis && !eligibilityAnalysis.eligible)}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Processando...
              </>
            ) : (
              'Solicitar Estorno'
            )}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default RefundRequestForm;