import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTriger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  ArrowUpRight, 
  ArrowDownLeft,
  Eye,
  EyeOff,
  RefreshCw,
  Send,
  Download,
  CreditCard,
  Wallet,
  Activity,
  Clock,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

interface DigitalAccount {
  account_id: string;
  balance: number;
  available_balance: number;
  blocked_balance: number;
  daily_limit: number;
  monthly_limit: number;
  status: 'active' | 'suspended' | 'blocked';
}

interface Transaction {
  transaction_id: string;
  transaction_type: 'deposit' | 'withdraw' | 'transfer' | 'payment' | 'refund';
  amount: number;
  balance_before: number;
  balance_after: number;
  description: string;
  status: 'pending' | 'completed' | 'failed' | 'cancelled';
  created_at: string;
  processed_at?: string;
}

export const DigitalAccountDashboard: React.FC = () => {
  const [account, setAccount] = useState<DigitalAccount | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [showBalance, setShowBalance] = useState(true);
  const [transferAmount, setTransferAmount] = useState('');
  const [transferDestination, setTransferDestination] = useState('');
  const [transferDescription, setTransferDescription] = useState('');

  // Simular dados para demonstração
  useEffect(() => {
    setAccount({
      account_id: 'acc_123456789',
      balance: 15432.50,
      available_balance: 15432.50,
      blocked_balance: 0,
      daily_limit: 5000.00,
      monthly_limit: 50000.00,
      status: 'active'
    });

    setTransactions([
      {
        transaction_id: 'tx_001',
        transaction_type: 'deposit',
        amount: 1500.00,
        balance_before: 13932.50,
        balance_after: 15432.50,
        description: 'Recebimento PDV - Evento Premium',
        status: 'completed',
        created_at: '2025-08-22T10:30:00Z',
        processed_at: '2025-08-22T10:30:05Z'
      },
      {
        transaction_id: 'tx_002', 
        transaction_type: 'transfer',
        amount: 750.00,
        balance_before: 14682.50,
        balance_after: 13932.50,
        description: 'Transferência para fornecedor',
        status: 'completed',
        created_at: '2025-08-22T09:15:00Z',
        processed_at: '2025-08-22T09:15:03Z'
      },
      {
        transaction_id: 'tx_003',
        transaction_type: 'payment',
        amount: 250.00,
        balance_before: 14932.50,
        balance_after: 14682.50,
        description: 'Pagamento de taxa de processamento',
        status: 'completed',
        created_at: '2025-08-22T08:45:00Z'
      }
    ]);
  }, []);

  const getTransactionIcon = (type: string, amount: number) => {
    if (type === 'deposit' || type === 'refund') {
      return <ArrowDownLeft className="h-4 w-4 text-green-600" />;
    }
    return <ArrowUpRight className="h-4 w-4 text-red-600" />;
  };

  const getTransactionColor = (type: string) => {
    if (type === 'deposit' || type === 'refund') {
      return 'text-green-600';
    }
    return 'text-red-600';
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      completed: { variant: 'default' as const, color: 'bg-green-100 text-green-700', icon: CheckCircle },
      pending: { variant: 'secondary' as const, color: 'bg-yellow-100 text-yellow-700', icon: Clock },
      failed: { variant: 'destructive' as const, color: 'bg-red-100 text-red-700', icon: AlertTriangle },
      cancelled: { variant: 'outline' as const, color: 'bg-gray-100 text-gray-700', icon: AlertTriangle }
    };

    const config = statusConfig[status as keyof typeof statusConfig];
    const Icon = config?.icon || CheckCircle;

    return (
      <Badge variant={config?.variant || 'outline'} className={`${config?.color} flex items-center gap-1`}>
        <Icon className="h-3 w-3" />
        {status === 'completed' ? 'Concluída' : 
         status === 'pending' ? 'Pendente' : 
         status === 'failed' ? 'Falhou' : 'Cancelada'}
      </Badge>
    );
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(dateString));
  };

  const handleTransfer = async () => {
    if (!transferAmount || !transferDestination) return;
    
    setLoading(true);
    // Implementar lógica de transferência
    setTimeout(() => {
      setLoading(false);
      setTransferAmount('');
      setTransferDestination('');
      setTransferDescription('');
    }, 2000);
  };

  const refreshBalance = async () => {
    setLoading(true);
    // Implementar refresh do saldo
    setTimeout(() => setLoading(false), 1000);
  };

  if (!account) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Conta Digital</h1>
          <p className="text-gray-600">Gerencie sua carteira digital em tempo real</p>
        </div>
        <Badge variant="outline" className="bg-green-50 text-green-700">
          Sistema Ativo
        </Badge>
      </div>

      {/* Saldo Principal */}
      <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Wallet className="h-5 w-5" />
                <span className="text-sm opacity-90">Saldo Disponível</span>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="text-white hover:bg-white/20 p-1"
                  onClick={() => setShowBalance(!showBalance)}
                >
                  {showBalance ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                </Button>
              </div>
              <div className="text-3xl font-bold">
                {showBalance ? formatCurrency(account.available_balance) : '••••••'}
              </div>
              {account.blocked_balance > 0 && (
                <div className="text-sm opacity-75 mt-1">
                  Bloqueado: {showBalance ? formatCurrency(account.blocked_balance) : '••••'}
                </div>
              )}
            </div>
            <div className="text-right">
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-white hover:bg-white/20"
                onClick={refreshBalance}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
              <div className="text-xs opacity-75 mt-2">
                ID: {account.account_id.slice(-8)}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Limites e Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Limite Diário</span>
            </div>
            <div className="text-lg font-bold text-gray-900 mt-1">
              {formatCurrency(account.daily_limit)}
            </div>
            <div className="text-xs text-gray-500">Disponível hoje</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium">Limite Mensal</span>
            </div>
            <div className="text-lg font-bold text-gray-900 mt-1">
              {formatCurrency(account.monthly_limit)}
            </div>
            <div className="text-xs text-gray-500">Restante no mês</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium">Status</span>
            </div>
            <div className="text-lg font-bold text-green-600 mt-1 capitalize">
              {account.status === 'active' ? 'Ativa' : account.status}
            </div>
            <div className="text-xs text-gray-500">Conta verificada</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs de Funcionalidades */}
      <Tabs defaultValue="transactions" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTriger value="transactions">Transações</TabsTriger>
          <TabsTriger value="transfer">Transferir</TabsTriger>
          <TabsTriger value="analytics">Analytics</TabsTriger>
        </TabsList>

        {/* Transações */}
        <TabsContent value="transactions">
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Transações</CardTitle>
              <CardDescription>
                Últimas movimentações da sua conta digital
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {transactions.map((transaction) => (
                  <div key={transaction.transaction_id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center gap-3">
                      {getTransactionIcon(transaction.transaction_type, transaction.amount)}
                      <div>
                        <div className="font-medium text-gray-900">
                          {transaction.description}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatDate(transaction.created_at)}
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right flex items-center gap-3">
                      <div>
                        <div className={`font-bold ${getTransactionColor(transaction.transaction_type)}`}>
                          {transaction.transaction_type === 'deposit' || transaction.transaction_type === 'refund' ? '+' : '-'}
                          {formatCurrency(transaction.amount)}
                        </div>
                        <div className="text-xs text-gray-500">
                          Saldo: {formatCurrency(transaction.balance_after)}
                        </div>
                      </div>
                      {getStatusBadge(transaction.status)}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-center mt-6">
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Baixar Extrato
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Transferências */}
        <TabsContent value="transfer">
          <Card>
            <CardHeader>
              <CardTitle>Transferir Fundos</CardTitle>
              <CardDescription>
                Transfira dinheiro para outras contas de forma segura
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="destination">Conta de Destino</Label>
                    <Input
                      id="destination"
                      placeholder="ID da conta ou chave PIX"
                      value={transferDestination}
                      onChange={(e) => setTransferDestination(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="amount">Valor</Label>
                    <Input
                      id="amount"
                      type="number"
                      placeholder="0,00"
                      value={transferAmount}
                      onChange={(e) => setTransferAmount(e.target.value)}
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="description">Descrição (Opcional)</Label>
                  <Input
                    id="description"
                    placeholder="Descrição da transferência"
                    value={transferDescription}
                    onChange={(e) => setTransferDescription(e.target.value)}
                  />
                </div>

                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Transferências PIX são instantâneas e gratuitas. Outras transferências podem ter taxa de R$ 1,00.
                  </AlertDescription>
                </Alert>

                <Button 
                  onClick={handleTransfer} 
                  disabled={!transferAmount || !transferDestination || loading}
                  className="w-full"
                >
                  {loading ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4 mr-2" />
                  )}
                  Transferir {transferAmount && formatCurrency(parseFloat(transferAmount))}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics */}
        <TabsContent value="analytics">
          <Card>
            <CardHeader>
              <CardTitle>Analytics da Conta</CardTitle>
              <CardDescription>
                Análise detalhada das movimentações financeiras
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <TrendingUp className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Analytics em Desenvolvimento
                </h3>
                <p className="text-gray-600 mb-4">
                  Gráficos detalhados e insights financeiros serão implementados em breve
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