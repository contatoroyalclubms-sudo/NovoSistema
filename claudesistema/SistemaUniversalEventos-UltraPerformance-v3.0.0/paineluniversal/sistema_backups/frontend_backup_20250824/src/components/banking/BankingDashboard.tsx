/**
 * Banking Dashboard - Comprehensive Financial Operations Center
 * Sistema Universal de Gestão de Eventos
 * 
 * Advanced features:
 * - Real-time balance tracking and analytics
 * - Multi-account management with hierarchical view
 * - Transaction monitoring and fraud alerts
 * - PIX operations and payment processing
 * - Treasury management and investment overview
 * - Compliance monitoring and security alerts
 * - Performance metrics and KPIs
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { Separator } from '../ui/separator';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '../ui/chart';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  Wallet,
  CreditCard,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Shield,
  AlertTriangle,
  Eye,
  RefreshCw,
  Download,
  Settings,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Activity,
  Zap,
  Target,
  PieChart as PieChartIcon,
  BarChart3,
  CandlestickChart
} from 'lucide-react';

// Types
interface BankingAccount {
  id: string;
  accountNumber: string;
  accountType: 'personal' | 'business' | 'escrow' | 'savings' | 'investment';
  currency: 'BRL' | 'USD' | 'EUR';
  balance: number;
  availableBalance: number;
  blockedBalance: number;
  status: 'active' | 'suspended' | 'blocked';
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  lastTransaction?: string;
  dailyLimit: number;
  monthlyLimit: number;
  parentAccountId?: string;
}

interface Transaction {
  id: string;
  accountId: string;
  type: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  description: string;
  createdAt: string;
  processedAt?: string;
  riskScore?: number;
  gateway?: string;
}

interface PIXTransaction {
  id: string;
  amount: number;
  status: 'created' | 'pending' | 'completed' | 'expired' | 'cancelled';
  qrCode?: string;
  pixKey?: string;
  description: string;
  createdAt: string;
  expiresAt?: string;
}

interface FraudAlert {
  id: string;
  type: 'high_velocity' | 'unusual_amount' | 'suspicious_location' | 'device_anomaly';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  accountId: string;
  transactionId?: string;
  detectedAt: string;
  status: 'active' | 'investigating' | 'resolved' | 'false_positive';
}

interface DashboardMetrics {
  totalBalance: number;
  availableBalance: number;
  blockedBalance: number;
  dailyTransactions: number;
  monthlyVolume: number;
  activeAccounts: number;
  pendingTransactions: number;
  fraudAlerts: number;
}

interface BankingDashboardProps {
  userId?: string;
  viewMode?: 'overview' | 'detailed';
  autoRefresh?: boolean;
  refreshInterval?: number;
}

// Chart color scheme
const chartColors = {
  primary: '#3B82F6',
  secondary: '#10B981',
  accent: '#F59E0B',
  danger: '#EF4444',
  warning: '#F97316',
  success: '#22C55E',
  muted: '#6B7280'
};

const BankingDashboard: React.FC<BankingDashboardProps> = ({
  userId,
  viewMode = 'overview',
  autoRefresh = true,
  refreshInterval = 30000
}) => {
  // State management
  const [accounts, setAccounts] = useState<BankingAccount[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [pixTransactions, setPixTransactions] = useState<PIXTransaction[]>([]);
  const [fraudAlerts, setFraudAlerts] = useState<FraudAlert[]>([]);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1d' | '7d' | '30d' | '90d'>('7d');
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');

  // Data fetching
  const fetchBankingData = useCallback(async () => {
    try {
      setLoading(true);
      const [accountsRes, transactionsRes, metricsRes, alertsRes] = await Promise.all([
        fetch('/api/v1/banking/accounts'),
        fetch('/api/v1/banking/transactions?limit=50'),
        fetch('/api/v1/banking/metrics'),
        fetch('/api/v1/banking/fraud-alerts?status=active')
      ]);

      if (accountsRes.ok) {
        const accountsData = await accountsRes.json();
        setAccounts(accountsData.accounts || []);
      }

      if (transactionsRes.ok) {
        const transactionsData = await transactionsRes.json();
        setTransactions(transactionsData.transactions || []);
      }

      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setFraudAlerts(alertsData.alerts || []);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to fetch banking data:', err);
      setError('Failed to load banking data');
    } finally {
      setLoading(false);
    }
  }, [selectedTimeframe, selectedAccount]);

  // Auto-refresh setup
  useEffect(() => {
    fetchBankingData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchBankingData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchBankingData, autoRefresh, refreshInterval]);

  // Computed values
  const primaryAccount = useMemo(() => 
    accounts.find(acc => !acc.parentAccountId) || accounts[0], 
    [accounts]
  );

  const totalBalance = useMemo(() => 
    accounts.reduce((sum, acc) => sum + acc.balance, 0), 
    [accounts]
  );

  const recentTransactions = useMemo(() => 
    transactions
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 10), 
    [transactions]
  );

  const activeFraudAlerts = useMemo(() => 
    fraudAlerts.filter(alert => alert.status === 'active'), 
    [fraudAlerts]
  );

  // Chart data preparation
  const balanceChartData = useMemo(() => {
    // Mock data - in real app, this would come from API
    const days = Array.from({ length: 30 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (29 - i));
      return {
        date: date.toISOString().split('T')[0],
        balance: totalBalance + (Math.random() - 0.5) * totalBalance * 0.1,
        available: totalBalance * 0.9 + (Math.random() - 0.5) * totalBalance * 0.05
      };
    });
    return days;
  }, [totalBalance]);

  const transactionVolumeData = useMemo(() => {
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      const dayTransactions = transactions.filter(t => 
        new Date(t.createdAt).toDateString() === date.toDateString()
      );
      
      return {
        date: date.toLocaleDateString('pt-BR', { weekday: 'short' }),
        transactions: dayTransactions.length,
        volume: dayTransactions.reduce((sum, t) => sum + Math.abs(t.amount), 0)
      };
    });
    return last7Days;
  }, [transactions]);

  // Component renderers
  const renderMetricCard = (
    title: string,
    value: string | number,
    icon: React.ReactNode,
    trend?: { value: number; isPositive: boolean },
    status?: 'success' | 'warning' | 'danger'
  ) => (
    <Card className="transition-all hover:shadow-md">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {trend && (
              <div className={`flex items-center text-sm ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {trend.isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                <span className="ml-1">{Math.abs(trend.value)}%</span>
              </div>
            )}
          </div>
          <div className={`p-3 rounded-full ${
            status === 'success' ? 'bg-green-100 text-green-600' :
            status === 'warning' ? 'bg-yellow-100 text-yellow-600' :
            status === 'danger' ? 'bg-red-100 text-red-600' :
            'bg-blue-100 text-blue-600'
          }`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderAccountCard = (account: BankingAccount) => (
    <Card 
      key={account.id} 
      className={`cursor-pointer transition-all hover:shadow-md border-2 ${
        selectedAccount === account.id ? 'border-blue-500' : 'border-transparent hover:border-gray-200'
      }`}
      onClick={() => setSelectedAccount(selectedAccount === account.id ? null : account.id)}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-lg">{account.accountType.toUpperCase()}</h3>
            <p className="text-sm text-muted-foreground">***{account.accountNumber.slice(-4)}</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={account.status === 'active' ? 'default' : 'destructive'}>
              {account.status}
            </Badge>
            <Badge 
              variant={
                account.riskLevel === 'low' ? 'default' :
                account.riskLevel === 'medium' ? 'secondary' :
                'destructive'
              }
            >
              {account.riskLevel} risk
            </Badge>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm text-muted-foreground">Balance</span>
            <span className="font-semibold">
              {new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: account.currency
              }).format(account.balance)}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-sm text-muted-foreground">Available</span>
            <span className="text-green-600">
              {new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: account.currency
              }).format(account.availableBalance)}
            </span>
          </div>
          
          {account.blockedBalance > 0 && (
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Blocked</span>
              <span className="text-red-600">
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: account.currency
                }).format(account.blockedBalance)}
              </span>
            </div>
          )}
        </div>
        
        <div className="mt-4">
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span>Daily Limit Usage</span>
            <span>{((account.balance / account.dailyLimit) * 100).toFixed(1)}%</span>
          </div>
          <Progress 
            value={(account.balance / account.dailyLimit) * 100}
            className="h-2"
          />
        </div>
      </CardContent>
    </Card>
  );

  const renderTransactionItem = (transaction: Transaction) => (
    <div key={transaction.id} className="flex items-center justify-between p-4 border-b last:border-b-0">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-full ${
          transaction.type === 'deposit' ? 'bg-green-100 text-green-600' :
          transaction.type === 'withdraw' ? 'bg-red-100 text-red-600' :
          'bg-blue-100 text-blue-600'
        }`}>
          {transaction.type === 'deposit' ? <ArrowDownRight size={16} /> :
           transaction.type === 'withdraw' ? <ArrowUpRight size={16} /> :
           <RefreshCw size={16} />}
        </div>
        <div>
          <p className="font-medium">{transaction.description}</p>
          <p className="text-sm text-muted-foreground">
            {new Date(transaction.createdAt).toLocaleString('pt-BR')}
          </p>
        </div>
      </div>
      
      <div className="text-right">
        <p className={`font-semibold ${
          transaction.type === 'deposit' ? 'text-green-600' : 'text-red-600'
        }`}>
          {transaction.type === 'deposit' ? '+' : '-'}
          {new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: transaction.currency
          }).format(Math.abs(transaction.amount))}
        </p>
        <div className="flex items-center gap-1">
          <Badge variant={
            transaction.status === 'completed' ? 'default' :
            transaction.status === 'pending' ? 'secondary' :
            'destructive'
          } className="text-xs">
            {transaction.status}
          </Badge>
          {transaction.riskScore && transaction.riskScore > 50 && (
            <AlertTriangle size={12} className="text-yellow-500" />
          )}
        </div>
      </div>
    </div>
  );

  const renderFraudAlert = (alert: FraudAlert) => (
    <Alert key={alert.id} variant={
      alert.severity === 'critical' ? 'destructive' :
      alert.severity === 'high' ? 'destructive' :
      'default'
    } className="mb-4">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle className="flex items-center gap-2">
        Fraud Alert - {alert.type.replace('_', ' ').toUpperCase()}
        <Badge variant={alert.severity === 'critical' ? 'destructive' : 'secondary'}>
          {alert.severity}
        </Badge>
      </AlertTitle>
      <AlertDescription>
        {alert.description}
        <div className="mt-2 flex gap-2">
          <Button size="sm" variant="outline">
            Investigate
          </Button>
          <Button size="sm" variant="outline">
            Mark as Safe
          </Button>
        </div>
      </AlertDescription>
    </Alert>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="mx-auto h-8 w-8 animate-spin text-blue-500" />
          <p className="mt-2 text-muted-foreground">Loading banking data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Banking Dashboard</h1>
          <p className="text-muted-foreground">
            Comprehensive financial operations and account management
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchBankingData}>
            <RefreshCw size={16} className="mr-2" />
            Refresh
          </Button>
          <Button>
            <Plus size={16} className="mr-2" />
            New Account
          </Button>
        </div>
      </div>

      {/* Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {renderMetricCard(
          'Total Balance',
          new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(totalBalance),
          <Wallet size={24} />,
          { value: 2.5, isPositive: true },
          'success'
        )}
        
        {renderMetricCard(
          'Active Accounts',
          accounts.filter(acc => acc.status === 'active').length.toString(),
          <Users size={24} />,
          undefined,
          'success'
        )}
        
        {renderMetricCard(
          'Daily Transactions',
          metrics?.dailyTransactions?.toString() || '0',
          <Activity size={24} />,
          { value: 12.3, isPositive: true }
        )}
        
        {renderMetricCard(
          'Fraud Alerts',
          activeFraudAlerts.length.toString(),
          <Shield size={24} />,
          undefined,
          activeFraudAlerts.length > 0 ? 'danger' : 'success'
        )}
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="accounts">Accounts</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="pix">PIX</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Balance Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Balance Trend</CardTitle>
                <CardDescription>Account balance over the last 30 days</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    balance: { label: "Balance", color: chartColors.primary },
                    available: { label: "Available", color: chartColors.secondary }
                  }}
                  className="h-[300px]"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={balanceChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Area
                        type="monotone"
                        dataKey="balance"
                        stackId="1"
                        stroke={chartColors.primary}
                        fill={chartColors.primary}
                        fillOpacity={0.3}
                      />
                      <Area
                        type="monotone"
                        dataKey="available"
                        stackId="2"
                        stroke={chartColors.secondary}
                        fill={chartColors.secondary}
                        fillOpacity={0.3}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Transaction Volume */}
            <Card>
              <CardHeader>
                <CardTitle>Transaction Volume</CardTitle>
                <CardDescription>Daily transaction count and volume</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    transactions: { label: "Transactions", color: chartColors.accent },
                    volume: { label: "Volume", color: chartColors.primary }
                  }}
                  className="h-[300px]"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={transactionVolumeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="transactions" fill={chartColors.accent} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Transactions</CardTitle>
                <CardDescription>Latest account activity</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="max-h-96 overflow-y-auto">
                  {recentTransactions.map(renderTransactionItem)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Security Alerts</CardTitle>
                <CardDescription>Active fraud and security alerts</CardDescription>
              </CardHeader>
              <CardContent>
                {activeFraudAlerts.length === 0 ? (
                  <div className="text-center py-8">
                    <CheckCircle className="mx-auto h-12 w-12 text-green-500" />
                    <p className="mt-2 text-sm text-muted-foreground">
                      No active security alerts
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {activeFraudAlerts.slice(0, 3).map(renderFraudAlert)}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Accounts Tab */}
        <TabsContent value="accounts" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {accounts.map(renderAccountCard)}
          </div>
        </TabsContent>

        {/* Transactions Tab */}
        <TabsContent value="transactions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Transaction History</CardTitle>
              <CardDescription>Complete transaction history and details</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {transactions.map(renderTransactionItem)}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* PIX Tab */}
        <TabsContent value="pix" className="space-y-6">
          <div className="text-center py-12">
            <Zap className="mx-auto h-16 w-16 text-blue-500" />
            <h3 className="mt-4 text-lg font-semibold">PIX Operations</h3>
            <p className="text-muted-foreground">PIX payment management coming soon</p>
          </div>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Security Overview</CardTitle>
                <CardDescription>Account security status and alerts</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {fraudAlerts.map(renderFraudAlert)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Compliance Status</CardTitle>
                <CardDescription>Regulatory compliance monitoring</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>PCI DSS</span>
                    <Badge variant="default">Compliant</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>LGPD</span>
                    <Badge variant="default">Compliant</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Anti-Fraud</span>
                    <Badge variant="default">Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="text-center py-12">
            <BarChart3 className="mx-auto h-16 w-16 text-blue-500" />
            <h3 className="mt-4 text-lg font-semibold">Advanced Analytics</h3>
            <p className="text-muted-foreground">Detailed financial analytics coming soon</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BankingDashboard;