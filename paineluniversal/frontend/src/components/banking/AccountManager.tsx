/**
 * Account Manager - Advanced Banking Account Management
 * Sistema Universal de Gestão de Eventos
 * 
 * Features:
 * - Multi-account creation and management
 * - Real-time balance tracking and transactions
 * - Account hierarchy and relationships
 * - Limit management and controls
 * - Multi-currency support
 * - Account analytics and insights
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Switch } from '../ui/switch';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { Textarea } from '../ui/textarea';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import {
  Plus,
  Settings,
  Edit,
  Trash2,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  Copy,
  Download,
  MoreVertical,
  CreditCard,
  Wallet,
  Building,
  PiggyBank,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Euro,
  Shield,
  Activity,
  BarChart3,
  Target,
  Zap,
  RefreshCw
} from 'lucide-react';

// Types
interface BankAccount {
  id: string;
  accountNumber: string;
  accountType: 'personal' | 'business' | 'escrow' | 'savings' | 'investment';
  currency: 'BRL' | 'USD' | 'EUR';
  balance: number;
  availableBalance: number;
  blockedBalance: number;
  pendingBalance: number;
  status: 'active' | 'suspended' | 'blocked' | 'closed';
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  dailyLimit: number;
  monthlyLimit: number;
  parentAccountId?: string;
  subAccounts?: BankAccount[];
  metadata: {
    description?: string;
    purpose?: string;
    tags?: string[];
    createdAt: string;
    updatedAt: string;
    lastTransactionAt?: string;
  };
  limits: {
    dailyTransactionLimit: number;
    monthlyTransactionLimit: number;
    singleTransactionLimit: number;
    dailyWithdrawalLimit: number;
  };
  features: {
    autoSweep: boolean;
    autoInvest: boolean;
    overdraftProtection: boolean;
    fraudProtection: boolean;
  };
}

interface AccountCreationData {
  accountType: 'personal' | 'business' | 'escrow' | 'savings' | 'investment';
  currency: 'BRL' | 'USD' | 'EUR';
  initialBalance: number;
  dailyLimit: number;
  monthlyLimit: number;
  parentAccountId?: string;
  description?: string;
  purpose?: string;
  tags?: string[];
}

interface AccountAnalytics {
  transactionCount: number;
  totalInflow: number;
  totalOutflow: number;
  averageBalance: number;
  balanceTrend: Array<{ date: string; balance: number }>;
  topTransactionTypes: Array<{ type: string; count: number; amount: number }>;
  monthlyStats: Array<{ month: string; inflow: number; outflow: number; netFlow: number }>;
}

const AccountManager: React.FC = () => {
  // State
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<BankAccount | null>(null);
  const [analytics, setAnalytics] = useState<AccountAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [createAccountData, setCreateAccountData] = useState<AccountCreationData>({
    accountType: 'personal',
    currency: 'BRL',
    initialBalance: 0,
    dailyLimit: 5000,
    monthlyLimit: 50000,
    description: '',
    purpose: '',
    tags: []
  });

  // Fetch accounts data
  const fetchAccounts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/banking/accounts');
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.accounts || []);
      }
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch account analytics
  const fetchAccountAnalytics = useCallback(async (accountId: string) => {
    try {
      const response = await fetch(`/api/v1/banking/accounts/${accountId}/analytics`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  }, []);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  useEffect(() => {
    if (selectedAccount) {
      fetchAccountAnalytics(selectedAccount.id);
    }
  }, [selectedAccount, fetchAccountAnalytics]);

  // Account operations
  const createAccount = async () => {
    try {
      const response = await fetch('/api/v1/banking/accounts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(createAccountData)
      });

      if (response.ok) {
        setIsCreateDialogOpen(false);
        fetchAccounts();
        setCreateAccountData({
          accountType: 'personal',
          currency: 'BRL',
          initialBalance: 0,
          dailyLimit: 5000,
          monthlyLimit: 50000,
          description: '',
          purpose: '',
          tags: []
        });
      }
    } catch (error) {
      console.error('Failed to create account:', error);
    }
  };

  const updateAccount = async (accountId: string, updates: Partial<BankAccount>) => {
    try {
      const response = await fetch(`/api/v1/banking/accounts/${accountId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        fetchAccounts();
      }
    } catch (error) {
      console.error('Failed to update account:', error);
    }
  };

  const toggleAccountStatus = async (accountId: string, action: 'block' | 'unblock') => {
    try {
      const response = await fetch(`/api/v1/banking/accounts/${accountId}/${action}`, {
        method: 'POST'
      });

      if (response.ok) {
        fetchAccounts();
      }
    } catch (error) {
      console.error('Failed to toggle account status:', error);
    }
  };

  // Render functions
  const getAccountIcon = (accountType: string) => {
    switch (accountType) {
      case 'personal': return <CreditCard className="h-5 w-5" />;
      case 'business': return <Building className="h-5 w-5" />;
      case 'savings': return <PiggyBank className="h-5 w-5" />;
      case 'investment': return <TrendingUp className="h-5 w-5" />;
      case 'escrow': return <Shield className="h-5 w-5" />;
      default: return <Wallet className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'suspended': return 'bg-yellow-100 text-yellow-800';
      case 'blocked': return 'bg-red-100 text-red-800';
      case 'closed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };

  const renderAccountCard = (account: BankAccount) => (
    <Card 
      key={account.id}
      className={`cursor-pointer transition-all hover:shadow-md border-2 ${
        selectedAccount?.id === account.id ? 'border-blue-500 ring-2 ring-blue-100' : 'border-transparent hover:border-gray-200'
      }`}
      onClick={() => setSelectedAccount(account)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
              {getAccountIcon(account.accountType)}
            </div>
            <div>
              <CardTitle className="text-lg">{account.accountType.toUpperCase()}</CardTitle>
              <CardDescription className="font-mono">***{account.accountNumber.slice(-4)}</CardDescription>
            </div>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Account Actions</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => setIsEditDialogOpen(true)}>
                <Edit className="mr-2 h-4 w-4" />
                Edit Account
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => toggleAccountStatus(account.id, account.status === 'blocked' ? 'unblock' : 'block')}>
                {account.status === 'blocked' ? <Unlock className="mr-2 h-4 w-4" /> : <Lock className="mr-2 h-4 w-4" />}
                {account.status === 'blocked' ? 'Unblock' : 'Block'} Account
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <Download className="mr-2 h-4 w-4" />
                Export Statement
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Copy className="mr-2 h-4 w-4" />
                Copy Account Number
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {/* Status and Risk Badges */}
          <div className="flex gap-2">
            <Badge className={getStatusColor(account.status)}>
              {account.status}
            </Badge>
            <Badge className={getRiskLevelColor(account.riskLevel)}>
              {account.riskLevel} risk
            </Badge>
            <Badge variant="outline" className="flex items-center gap-1">
              {account.currency === 'BRL' ? <DollarSign className="h-3 w-3" /> : 
               account.currency === 'EUR' ? <Euro className="h-3 w-3" /> : 
               <DollarSign className="h-3 w-3" />}
              {account.currency}
            </Badge>
          </div>

          {/* Balance Information */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Total Balance</span>
              <span className="text-lg font-bold">
                {formatCurrency(account.balance, account.currency)}
              </span>
            </div>
            
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Available</span>
              <span className="text-green-600 font-medium">
                {formatCurrency(account.availableBalance, account.currency)}
              </span>
            </div>
            
            {account.blockedBalance > 0 && (
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Blocked</span>
                <span className="text-red-600 font-medium">
                  {formatCurrency(account.blockedBalance, account.currency)}
                </span>
              </div>
            )}
            
            {account.pendingBalance > 0 && (
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Pending</span>
                <span className="text-yellow-600 font-medium">
                  {formatCurrency(account.pendingBalance, account.currency)}
                </span>
              </div>
            )}
          </div>

          {/* Limit Usage */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Daily Limit Usage</span>
              <span>{((account.balance / account.dailyLimit) * 100).toFixed(1)}%</span>
            </div>
            <Progress 
              value={(account.balance / account.dailyLimit) * 100}
              className="h-2"
            />
          </div>

          {/* Features */}
          <div className="flex gap-1 flex-wrap">
            {account.features.autoSweep && (
              <Badge variant="secondary" className="text-xs">Auto Sweep</Badge>
            )}
            {account.features.autoInvest && (
              <Badge variant="secondary" className="text-xs">Auto Invest</Badge>
            )}
            {account.features.fraudProtection && (
              <Badge variant="secondary" className="text-xs">Fraud Protection</Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderAccountDetails = () => {
    if (!selectedAccount) {
      return (
        <Card className="h-96 flex items-center justify-center">
          <div className="text-center">
            <CreditCard className="mx-auto h-12 w-12 text-muted-foreground" />
            <p className="mt-4 text-lg font-medium">No Account Selected</p>
            <p className="text-muted-foreground">Select an account to view details</p>
          </div>
        </Card>
      );
    }

    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-blue-100 text-blue-600">
                {getAccountIcon(selectedAccount.accountType)}
              </div>
              <div>
                <CardTitle className="text-xl">
                  {selectedAccount.accountType.toUpperCase()} Account
                </CardTitle>
                <CardDescription>
                  {selectedAccount.accountNumber} • Created {new Date(selectedAccount.metadata.createdAt).toLocaleDateString()}
                </CardDescription>
              </div>
            </div>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(true)}>
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
          </div>
        </CardHeader>

        <CardContent>
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="limits">Limits</TabsTrigger>
              <TabsTrigger value="features">Features</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Balance</p>
                        <p className="text-2xl font-bold">
                          {formatCurrency(selectedAccount.balance, selectedAccount.currency)}
                        </p>
                      </div>
                      <Wallet className="h-8 w-8 text-blue-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Available</p>
                        <p className="text-2xl font-bold text-green-600">
                          {formatCurrency(selectedAccount.availableBalance, selectedAccount.currency)}
                        </p>
                      </div>
                      <CheckCircle className="h-8 w-8 text-green-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Blocked</p>
                        <p className="text-2xl font-bold text-red-600">
                          {formatCurrency(selectedAccount.blockedBalance, selectedAccount.currency)}
                        </p>
                      </div>
                      <Lock className="h-8 w-8 text-red-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Status</p>
                        <p className="text-2xl font-bold capitalize">{selectedAccount.status}</p>
                      </div>
                      <Activity className="h-8 w-8 text-blue-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {selectedAccount.metadata.description && (
                <Card>
                  <CardContent className="p-4">
                    <h4 className="font-medium mb-2">Description</h4>
                    <p className="text-muted-foreground">{selectedAccount.metadata.description}</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="limits" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Transaction Limits</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between">
                      <span>Daily Limit</span>
                      <span className="font-mono">{formatCurrency(selectedAccount.limits.dailyTransactionLimit, selectedAccount.currency)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Monthly Limit</span>
                      <span className="font-mono">{formatCurrency(selectedAccount.limits.monthlyTransactionLimit, selectedAccount.currency)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Single Transaction</span>
                      <span className="font-mono">{formatCurrency(selectedAccount.limits.singleTransactionLimit, selectedAccount.currency)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Daily Withdrawal</span>
                      <span className="font-mono">{formatCurrency(selectedAccount.limits.dailyWithdrawalLimit, selectedAccount.currency)}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Limit Usage</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Daily Usage</span>
                        <span>65%</span>
                      </div>
                      <Progress value={65} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Monthly Usage</span>
                        <span>42%</span>
                      </div>
                      <Progress value={42} className="h-2" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="features" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Account Features</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="auto-sweep">Auto Sweep</Label>
                        <p className="text-sm text-muted-foreground">
                          Automatically move excess funds to investment accounts
                        </p>
                      </div>
                      <Switch 
                        id="auto-sweep"
                        checked={selectedAccount.features.autoSweep}
                        onCheckedChange={(checked) => 
                          updateAccount(selectedAccount.id, {
                            features: { ...selectedAccount.features, autoSweep: checked }
                          })
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="auto-invest">Auto Invest</Label>
                        <p className="text-sm text-muted-foreground">
                          Automatically invest surplus funds based on risk profile
                        </p>
                      </div>
                      <Switch 
                        id="auto-invest"
                        checked={selectedAccount.features.autoInvest}
                        onCheckedChange={(checked) => 
                          updateAccount(selectedAccount.id, {
                            features: { ...selectedAccount.features, autoInvest: checked }
                          })
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="overdraft">Overdraft Protection</Label>
                        <p className="text-sm text-muted-foreground">
                          Allow transactions that exceed available balance
                        </p>
                      </div>
                      <Switch 
                        id="overdraft"
                        checked={selectedAccount.features.overdraftProtection}
                        onCheckedChange={(checked) => 
                          updateAccount(selectedAccount.id, {
                            features: { ...selectedAccount.features, overdraftProtection: checked }
                          })
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="fraud-protection">Fraud Protection</Label>
                        <p className="text-sm text-muted-foreground">
                          Enhanced fraud detection and prevention
                        </p>
                      </div>
                      <Switch 
                        id="fraud-protection"
                        checked={selectedAccount.features.fraudProtection}
                        onCheckedChange={(checked) => 
                          updateAccount(selectedAccount.id, {
                            features: { ...selectedAccount.features, fraudProtection: checked }
                          })
                        }
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Security Settings</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span>Risk Level</span>
                      <Badge className={getRiskLevelColor(selectedAccount.riskLevel)}>
                        {selectedAccount.riskLevel}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Two-Factor Authentication</span>
                      <Badge variant="default">Enabled</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Transaction Notifications</span>
                      <Badge variant="default">Enabled</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Login Alerts</span>
                      <Badge variant="default">Enabled</Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="analytics" className="space-y-4">
              {analytics ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Transaction Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Total Transactions</span>
                          <span className="font-medium">{analytics.transactionCount}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Total Inflow</span>
                          <span className="text-green-600 font-medium">
                            {formatCurrency(analytics.totalInflow, selectedAccount.currency)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Total Outflow</span>
                          <span className="text-red-600 font-medium">
                            {formatCurrency(analytics.totalOutflow, selectedAccount.currency)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Average Balance</span>
                          <span className="font-medium">
                            {formatCurrency(analytics.averageBalance, selectedAccount.currency)}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Top Transaction Types</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {analytics.topTransactionTypes.map((type, index) => (
                          <div key={index} className="flex justify-between items-center">
                            <span className="capitalize">{type.type}</span>
                            <div className="text-right">
                              <p className="font-medium">{type.count} transactions</p>
                              <p className="text-sm text-muted-foreground">
                                {formatCurrency(type.amount, selectedAccount.currency)}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <Card className="h-64 flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground" />
                    <p className="mt-4 text-lg font-medium">Loading Analytics</p>
                    <p className="text-muted-foreground">Preparing account insights...</p>
                  </div>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Account Manager</h1>
          <p className="text-muted-foreground">
            Manage your banking accounts, limits, and features
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchAccounts}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Account
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Accounts List */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold">Your Accounts</h2>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-4">
                    <div className="h-24 bg-gray-200 rounded"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {accounts.map(renderAccountCard)}
            </div>
          )}
        </div>

        {/* Account Details */}
        <div className="lg:col-span-3">
          {renderAccountDetails()}
        </div>
      </div>

      {/* Create Account Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Create New Account</DialogTitle>
            <DialogDescription>
              Set up a new banking account with custom settings
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="accountType">Account Type</Label>
                <Select
                  value={createAccountData.accountType}
                  onValueChange={(value: any) => 
                    setCreateAccountData({ ...createAccountData, accountType: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="personal">Personal</SelectItem>
                    <SelectItem value="business">Business</SelectItem>
                    <SelectItem value="savings">Savings</SelectItem>
                    <SelectItem value="investment">Investment</SelectItem>
                    <SelectItem value="escrow">Escrow</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="currency">Currency</Label>
                <Select
                  value={createAccountData.currency}
                  onValueChange={(value: any) => 
                    setCreateAccountData({ ...createAccountData, currency: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="BRL">BRL - Brazilian Real</SelectItem>
                    <SelectItem value="USD">USD - US Dollar</SelectItem>
                    <SelectItem value="EUR">EUR - Euro</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="initialBalance">Initial Balance</Label>
              <Input
                id="initialBalance"
                type="number"
                min="0"
                step="0.01"
                value={createAccountData.initialBalance}
                onChange={(e) => 
                  setCreateAccountData({ 
                    ...createAccountData, 
                    initialBalance: parseFloat(e.target.value) || 0 
                  })
                }
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="dailyLimit">Daily Limit</Label>
                <Input
                  id="dailyLimit"
                  type="number"
                  min="0"
                  value={createAccountData.dailyLimit}
                  onChange={(e) => 
                    setCreateAccountData({ 
                      ...createAccountData, 
                      dailyLimit: parseFloat(e.target.value) || 0 
                    })
                  }
                />
              </div>

              <div>
                <Label htmlFor="monthlyLimit">Monthly Limit</Label>
                <Input
                  id="monthlyLimit"
                  type="number"
                  min="0"
                  value={createAccountData.monthlyLimit}
                  onChange={(e) => 
                    setCreateAccountData({ 
                      ...createAccountData, 
                      monthlyLimit: parseFloat(e.target.value) || 0 
                    })
                  }
                />
              </div>
            </div>

            <div>
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                placeholder="Account purpose and description"
                value={createAccountData.description || ''}
                onChange={(e) => 
                  setCreateAccountData({ 
                    ...createAccountData, 
                    description: e.target.value 
                  })
                }
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={createAccount}>
                Create Account
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AccountManager;