import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTriger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Split, 
  Plus, 
  Trash2, 
  Calculator, 
  Send, 
  Users, 
  Percent,
  DollarSign,
  ArrowRight,
  CheckCircle,
  AlertTriangle,
  Clock,
  BarChart3
} from 'lucide-react';

interface SplitRecipient {
  id: string;
  account_id: string;
  account_name: string;
  recipient_type: 'main_account' | 'commission' | 'fee' | 'supplier' | 'partner';
  amount?: number;
  percentage?: number;
  description?: string;
}

interface SplitSimulation {
  transaction_amount: number;
  total_split_amount: number;
  total_fees: number;
  net_amount: number;
  recipients_breakdown: any[];
  warnings: string[];
}

export const SplitPaymentManager: React.FC = () => {
  const [transactionAmount, setTransactionAmount] = useState<string>('');
  const [splitType, setSplitType] = useState<'percentage' | 'fixed_amount'>('percentage');
  const [recipients, setRecipients] = useState<SplitRecipient[]>([]);
  const [simulation, setSimulation] = useState<SplitSimulation | null>(null);
  const [loading, setLoading] = useState(false);
  const [description, setDescription] = useState('');

  // Adicionar destinatário padrão ao carregar
  useEffect(() => {
    addRecipient();
  }, []);

  const addRecipient = () => {
    const newRecipient: SplitRecipient = {
      id: Date.now().toString(),
      account_id: '',
      account_name: '',
      recipient_type: 'main_account',
      percentage: splitType === 'percentage' ? 100 : undefined,
      amount: splitType === 'fixed_amount' ? 0 : undefined,
      description: ''
    };
    setRecipients([...recipients, newRecipient]);
  };

  const removeRecipient = (id: string) => {
    setRecipients(recipients.filter(r => r.id !== id));
  };

  const updateRecipient = (id: string, field: string, value: any) => {
    setRecipients(recipients.map(r => 
      r.id === id ? { ...r, [field]: value } : r
    ));
  };

  const getRecipientTypeLabel = (type: string) => {
    const labels = {
      'main_account': 'Conta Principal',
      'commission': 'Comissão',
      'fee': 'Taxa',
      'supplier': 'Fornecedor',
      'partner': 'Parceiro'
    };
    return labels[type as keyof typeof labels] || type;
  };

  const getRecipientTypeColor = (type: string) => {
    const colors = {
      'main_account': 'bg-blue-100 text-blue-700',
      'commission': 'bg-green-100 text-green-700',
      'fee': 'bg-orange-100 text-orange-700',
      'supplier': 'bg-purple-100 text-purple-700',
      'partner': 'bg-pink-100 text-pink-700'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-700';
  };

  const simulateSplit = async () => {
    if (!transactionAmount || recipients.length === 0) return;
    
    setLoading(true);
    
    // Simular API call
    setTimeout(() => {
      const amount = parseFloat(transactionAmount);
      let totalSplit = 0;
      
      if (splitType === 'percentage') {
        totalSplit = amount;
      } else {
        totalSplit = recipients.reduce((sum, r) => sum + (r.amount || 0), 0);
      }
      
      const fees = totalSplit * 0.02; // 2% de taxa simulada
      const netAmount = totalSplit - fees;
      
      setSimulation({
        transaction_amount: amount,
        total_split_amount: totalSplit,
        total_fees: fees,
        net_amount: netAmount,
        recipients_breakdown: recipients.map(r => ({
          ...r,
          calculated_amount: splitType === 'percentage' ? 
            amount * ((r.percentage || 0) / 100) : 
            r.amount || 0,
          fees: (splitType === 'percentage' ? 
            amount * ((r.percentage || 0) / 100) : 
            r.amount || 0) * 0.02
        })),
        warnings: []
      });
      
      setLoading(false);
    }, 1000);
  };

  const processSplit = async () => {
    setLoading(true);
    // Implementar processamento real
    setTimeout(() => {
      setLoading(false);
    }, 2000);
  };

  const getTotalPercentage = () => {
    return recipients.reduce((sum, r) => sum + (r.percentage || 0), 0);
  };

  const getTotalAmount = () => {
    return recipients.reduce((sum, r) => sum + (r.amount || 0), 0);
  };

  const isValidSplit = () => {
    if (splitType === 'percentage') {
      return Math.abs(getTotalPercentage() - 100) < 0.01;
    } else {
      return getTotalAmount() <= parseFloat(transactionAmount || '0');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Split className="h-6 w-6" />
            Split de Pagamentos
          </h1>
          <p className="text-gray-600">Divida pagamentos automaticamente entre múltiplos destinatários</p>
        </div>
        <Badge variant="outline" className="bg-blue-50 text-blue-700">
          Sistema Inteligente
        </Badge>
      </div>

      <Tabs defaultValue="create" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTriger value="create">Criar Split</TabsTriger>
          <TabsTriger value="history">Histórico</TabsTriger>
          <TabsTriger value="rules">Regras</TabsTriger>
        </TabsList>

        {/* Criar Split */}
        <TabsContent value="create">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Configuração */}
            <Card>
              <CardHeader>
                <CardTitle>Configuração do Split</CardTitle>
                <CardDescription>
                  Configure o valor total e o tipo de divisão
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="amount">Valor Total da Transação</Label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="amount"
                      type="number"
                      placeholder="0,00"
                      className="pl-10"
                      value={transactionAmount}
                      onChange={(e) => setTransactionAmount(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <Label>Tipo de Divisão</Label>
                  <Select value={splitType} onValueChange={(value: 'percentage' | 'fixed_amount') => setSplitType(value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="percentage">
                        <div className="flex items-center gap-2">
                          <Percent className="h-4 w-4" />
                          Por Percentual
                        </div>
                      </SelectItem>
                      <SelectItem value="fixed_amount">
                        <div className="flex items-center gap-2">
                          <DollarSign className="h-4 w-4" />
                          Valor Fixo
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="description">Descrição (Opcional)</Label>
                  <Textarea
                    id="description"
                    placeholder="Descrição da transação"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>

                {/* Destinatários */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Destinatários ({recipients.length})</Label>
                    <Button variant="outline" size="sm" onClick={addRecipient}>
                      <Plus className="h-4 w-4 mr-1" />
                      Adicionar
                    </Button>
                  </div>

                  {recipients.map((recipient, index) => (
                    <div key={recipient.id} className="p-4 border rounded-lg space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Destinatário {index + 1}</span>
                        {recipients.length > 1 && (
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => removeRecipient(recipient.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <Label>Conta de Destino</Label>
                          <Input
                            placeholder="ID da conta"
                            value={recipient.account_id}
                            onChange={(e) => updateRecipient(recipient.id, 'account_id', e.target.value)}
                          />
                        </div>
                        <div>
                          <Label>Tipo</Label>
                          <Select 
                            value={recipient.recipient_type} 
                            onValueChange={(value) => updateRecipient(recipient.id, 'recipient_type', value)}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="main_account">Conta Principal</SelectItem>
                              <SelectItem value="commission">Comissão</SelectItem>
                              <SelectItem value="fee">Taxa</SelectItem>
                              <SelectItem value="supplier">Fornecedor</SelectItem>
                              <SelectItem value="partner">Parceiro</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {splitType === 'percentage' ? (
                          <div>
                            <Label>Percentual (%)</Label>
                            <Input
                              type="number"
                              min="0"
                              max="100"
                              step="0.01"
                              value={recipient.percentage || ''}
                              onChange={(e) => updateRecipient(recipient.id, 'percentage', parseFloat(e.target.value) || 0)}
                            />
                          </div>
                        ) : (
                          <div>
                            <Label>Valor (R$)</Label>
                            <Input
                              type="number"
                              min="0"
                              step="0.01"
                              value={recipient.amount || ''}
                              onChange={(e) => updateRecipient(recipient.id, 'amount', parseFloat(e.target.value) || 0)}
                            />
                          </div>
                        )}
                        <div>
                          <Label>Descrição</Label>
                          <Input
                            placeholder="Descrição opcional"
                            value={recipient.description || ''}
                            onChange={(e) => updateRecipient(recipient.id, 'description', e.target.value)}
                          />
                        </div>
                      </div>

                      <Badge className={getRecipientTypeColor(recipient.recipient_type)}>
                        {getRecipientTypeLabel(recipient.recipient_type)}
                      </Badge>
                    </div>
                  ))}

                  {/* Validação */}
                  {recipients.length > 0 && (
                    <div className="p-3 bg-gray-50 rounded-lg">
                      {splitType === 'percentage' ? (
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Total dos percentuais:</span>
                          <span className={`font-bold ${isValidSplit() ? 'text-green-600' : 'text-red-600'}`}>
                            {getTotalPercentage().toFixed(2)}%
                          </span>
                        </div>
                      ) : (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Total dos valores:</span>
                            <span className="font-bold">{formatCurrency(getTotalAmount())}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Valor restante:</span>
                            <span className={`font-bold ${isValidSplit() ? 'text-green-600' : 'text-red-600'}`}>
                              {formatCurrency(parseFloat(transactionAmount || '0') - getTotalAmount())}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    onClick={simulateSplit}
                    disabled={!transactionAmount || recipients.length === 0 || loading}
                    className="flex-1"
                  >
                    <Calculator className="h-4 w-4 mr-2" />
                    Simular Split
                  </Button>
                  <Button 
                    onClick={processSplit}
                    disabled={!simulation || !isValidSplit() || loading}
                    className="flex-1"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Processar Split
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Simulação */}
            <Card>
              <CardHeader>
                <CardTitle>Simulação do Split</CardTitle>
                <CardDescription>
                  Prévia dos valores que cada destinatário receberá
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!simulation ? (
                  <div className="text-center py-12 text-gray-500">
                    <Calculator className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p>Configure os destinatários e clique em "Simular Split" para ver a divisão</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Resumo */}
                    <div className="p-4 bg-blue-50 rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Valor da Transação:</span>
                        <span className="font-bold">{formatCurrency(simulation.transaction_amount)}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Total Distribuído:</span>
                        <span className="font-bold">{formatCurrency(simulation.total_split_amount)}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Taxas Totais:</span>
                        <span className="font-bold text-red-600">{formatCurrency(simulation.total_fees)}</span>
                      </div>
                      <div className="flex items-center justify-between border-t pt-2">
                        <span className="font-medium">Valor Líquido:</span>
                        <span className="font-bold text-green-600">{formatCurrency(simulation.net_amount)}</span>
                      </div>
                    </div>

                    {/* Breakdown por destinatário */}
                    <div className="space-y-3">
                      <h4 className="font-medium">Distribuição por Destinatário:</h4>
                      {simulation.recipients_breakdown.map((recipient, index) => (
                        <div key={recipient.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <div className="font-medium">Destinatário {index + 1}</div>
                            <div className="text-sm text-gray-500">
                              {recipient.account_id} • {getRecipientTypeLabel(recipient.recipient_type)}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold">{formatCurrency(recipient.calculated_amount)}</div>
                            <div className="text-xs text-red-600">-{formatCurrency(recipient.fees)} taxa</div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Warnings */}
                    {simulation.warnings.length > 0 && (
                      <Alert>
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <ul className="list-disc list-inside">
                            {simulation.warnings.map((warning, index) => (
                              <li key={index}>{warning}</li>
                            ))}
                          </ul>
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Histórico */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Splits</CardTitle>
              <CardDescription>
                Acompanhe todas as divisões de pagamento realizadas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Histórico em Desenvolvimento
                </h3>
                <p className="text-gray-600 mb-4">
                  Listagem e análise de splits processados será implementada em breve
                </p>
                <Badge variant="outline">Sprint 2 - Em Desenvolvimento</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Regras */}
        <TabsContent value="rules">
          <Card>
            <CardHeader>
              <CardTitle>Regras Personalizadas</CardTitle>
              <CardDescription>
                Crie regras automáticas para splits recorrentes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Sistema de Regras
                </h3>
                <p className="text-gray-600 mb-4">
                  Criação e gestão de regras automáticas de split será implementada em breve
                </p>
                <Badge variant="outline">Sprint 2 - Em Desenvolvimento</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};