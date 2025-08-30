/**
 * PaymentLinksManager - Main dashboard for payment links management
 * Sistema Universal de Gestão de Eventos
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  RefreshCw, 
  BarChart3, 
  Link as LinkIcon,
  DollarSign,
  TrendingUp,
  Users,
  Eye,
  AlertCircle,
  CheckCircle2,
  Clock,
  XCircle
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';

import { 
  PaymentLink,
  PaymentLinksListResponse,
  LinkStatus,
  PaymentType,
  PaymentLinkFilters,
  AnalyticsMetrics
} from '@/types/payment-links';

import paymentLinksService from '@/services/payment-links-service';
import { PaymentLinkList } from './PaymentLinkList';
import { PaymentLinkCreator } from './PaymentLinkCreator';
import { PaymentLinkAnalytics } from './PaymentLinkAnalytics';

interface PaymentLinksManagerProps {
  className?: string;
}

const PaymentLinksManager: React.FC<PaymentLinksManagerProps> = ({ className = '' }) => {
  // State management
  const [links, setLinks] = useState<PaymentLink[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLinks, setSelectedLinks] = useState<string[]>([]);
  const [currentView, setCurrentView] = useState<'list' | 'create' | 'analytics'>('list');
  const [editingLink, setEditingLink] = useState<PaymentLink | null>(null);
  
  // Filters and search
  const [filters, setFilters] = useState<PaymentLinkFilters>({
    limit: 50,
    offset: 0
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<LinkStatus | 'all'>('all');
  const [typeFilter, setTypeFilter] = useState<PaymentType | 'all'>('all');

  // Pagination
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // Load data
  useEffect(() => {
    loadPaymentLinks();
    loadAnalytics();
  }, [filters]);

  // Filter links based on search and filters
  const filteredLinks = useMemo(() => {
    let filtered = links;

    if (searchTerm) {
      filtered = filtered.filter(link => 
        link.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        link.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(link => link.status === statusFilter);
    }

    if (typeFilter !== 'all') {
      filtered = filtered.filter(link => link.payment_type === typeFilter);
    }

    return filtered;
  }, [links, searchTerm, statusFilter, typeFilter]);

  const loadPaymentLinks = async () => {
    try {
      setLoading(true);
      setError(null);

      const response: PaymentLinksListResponse = await paymentLinksService.getPaymentLinks({
        ...filters,
        offset: (currentPage - 1) * itemsPerPage,
        limit: itemsPerPage
      });

      setLinks(response.links);
      setTotalCount(response.total_count);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar links');
      console.error('Error loading payment links:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      const analyticsData = await paymentLinksService.getOverallAnalytics(30);
      setAnalytics(analyticsData);
    } catch (err) {
      console.error('Error loading analytics:', err);
    }
  };

  const handleCreateLink = () => {
    setEditingLink(null);
    setCurrentView('create');
  };

  const handleEditLink = (link: PaymentLink) => {
    setEditingLink(link);
    setCurrentView('create');
  };

  const handleDeleteLink = async (linkId: string) => {
    if (!confirm('Tem certeza que deseja excluir este link de pagamento?')) {
      return;
    }

    try {
      await paymentLinksService.deletePaymentLink(linkId);
      await loadPaymentLinks();
      setSelectedLinks(prev => prev.filter(id => id !== linkId));
    } catch (err) {
      console.error('Error deleting link:', err);
      alert('Erro ao excluir link de pagamento');
    }
  };

  const handleToggleStatus = async (linkId: string, newStatus: LinkStatus) => {
    try {
      await paymentLinksService.toggleLinkStatus(linkId, newStatus);
      await loadPaymentLinks();
    } catch (err) {
      console.error('Error toggling status:', err);
      alert('Erro ao alterar status do link');
    }
  };

  const handleBulkAction = async (action: string) => {
    if (selectedLinks.length === 0) {
      alert('Selecione pelo menos um link para realizar esta ação');
      return;
    }

    try {
      switch (action) {
        case 'delete':
          if (confirm(`Confirma a exclusão de ${selectedLinks.length} links?`)) {
            await paymentLinksService.bulkDelete(selectedLinks);
            await loadPaymentLinks();
            setSelectedLinks([]);
          }
          break;
        
        case 'activate':
          await paymentLinksService.bulkUpdateStatus(selectedLinks, LinkStatus.ACTIVE);
          await loadPaymentLinks();
          setSelectedLinks([]);
          break;
        
        case 'deactivate':
          await paymentLinksService.bulkUpdateStatus(selectedLinks, LinkStatus.INACTIVE);
          await loadPaymentLinks();
          setSelectedLinks([]);
          break;
      }
    } catch (err) {
      console.error('Error in bulk action:', err);
      alert('Erro ao executar ação em lote');
    }
  };

  const handleExport = async () => {
    try {
      const blob = await paymentLinksService.exportPaymentLinks({
        format: 'excel',
        date_range: {
          start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          end: new Date().toISOString()
        },
        include_analytics: true,
        include_payments: true
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `payment-links-${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export error:', err);
      alert('Erro ao exportar dados');
    }
  };

  const getStatusIcon = (status: LinkStatus) => {
    switch (status) {
      case LinkStatus.ACTIVE:
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case LinkStatus.INACTIVE:
        return <XCircle className="h-4 w-4 text-red-500" />;
      case LinkStatus.EXPIRED:
        return <Clock className="h-4 w-4 text-orange-500" />;
      case LinkStatus.COMPLETED:
        return <CheckCircle2 className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: LinkStatus) => {
    switch (status) {
      case LinkStatus.ACTIVE:
        return 'bg-green-100 text-green-800 border-green-200';
      case LinkStatus.INACTIVE:
        return 'bg-red-100 text-red-800 border-red-200';
      case LinkStatus.EXPIRED:
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case LinkStatus.COMPLETED:
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Render different views
  if (currentView === 'create') {
    return (
      <PaymentLinkCreator
        initialData={editingLink ? {
          title: editingLink.title,
          description: editingLink.description,
          amount: editingLink.amount,
          min_amount: editingLink.min_amount,
          max_amount: editingLink.max_amount,
          payment_type: editingLink.payment_type,
          expires_at: editingLink.expires_at,
          max_uses: editingLink.max_uses,
          theme: editingLink.theme,
          custom_css: editingLink.custom_css,
          logo_url: editingLink.logo_url,
          success_url: editingLink.success_url,
          cancel_url: editingLink.cancel_url,
          enable_split: editingLink.enable_split,
          split_recipients: editingLink.split_recipients,
          collect_customer_info: editingLink.collect_customer_info,
          send_receipt: editingLink.send_receipt,
          allow_installments: editingLink.allow_installments,
          webhook_url: editingLink.webhook_url,
          metadata: editingLink.metadata
        } : undefined}
        onSubmit={async (data) => {
          try {
            if (editingLink) {
              await paymentLinksService.updatePaymentLink(editingLink.link_id, data);
            } else {
              await paymentLinksService.createPaymentLink(data);
            }
            await loadPaymentLinks();
            setCurrentView('list');
            setEditingLink(null);
          } catch (err) {
            throw err;
          }
        }}
        onCancel={() => {
          setCurrentView('list');
          setEditingLink(null);
        }}
        mode={editingLink ? 'edit' : 'create'}
      />
    );
  }

  if (currentView === 'analytics') {
    return (
      <PaymentLinkAnalytics
        onBack={() => setCurrentView('list')}
      />
    );
  }

  // Main dashboard view
  return (
    <div className={`p-6 space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Links de Pagamento</h1>
          <p className="text-gray-600">Crie e gerencie links de pagamento dinâmicos</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => setCurrentView('analytics')}
            className="flex items-center space-x-2"
          >
            <BarChart3 className="h-4 w-4" />
            <span>Analytics</span>
          </Button>
          <Button
            variant="outline"
            onClick={handleExport}
            className="flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Exportar</span>
          </Button>
          <Button
            onClick={handleCreateLink}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Criar Link</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Links</CardTitle>
              <LinkIcon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_links}</div>
              <p className="text-xs text-muted-foreground">
                {analytics.active_links} ativos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Receita Total</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                R$ {analytics.total_revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </div>
              <p className="text-xs text-muted-foreground">
                +{analytics.growth_rate.toFixed(1)}% vs mês anterior
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pagamentos</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_payments}</div>
              <p className="text-xs text-muted-foreground">
                {analytics.conversion_rate.toFixed(1)}% taxa de conversão
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Valor Médio</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                R$ {analytics.avg_amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </div>
              <p className="text-xs text-muted-foreground">
                Por pagamento
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Pesquisar links..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as LinkStatus | 'all')}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os Status</SelectItem>
                <SelectItem value={LinkStatus.ACTIVE}>Ativo</SelectItem>
                <SelectItem value={LinkStatus.INACTIVE}>Inativo</SelectItem>
                <SelectItem value={LinkStatus.EXPIRED}>Expirado</SelectItem>
                <SelectItem value={LinkStatus.COMPLETED}>Completo</SelectItem>
              </SelectContent>
            </Select>

            <Select value={typeFilter} onValueChange={(value) => setTypeFilter(value as PaymentType | 'all')}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os Tipos</SelectItem>
                <SelectItem value={PaymentType.SINGLE}>Único</SelectItem>
                <SelectItem value={PaymentType.FLEXIBLE}>Flexível</SelectItem>
                <SelectItem value={PaymentType.RECURRING}>Recorrente</SelectItem>
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              onClick={loadPaymentLinks}
              disabled={loading}
              className="flex items-center space-x-2"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Atualizar</span>
            </Button>
          </div>

          {/* Bulk Actions */}
          {selectedLinks.length > 0 && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-blue-800">
                  {selectedLinks.length} link(s) selecionado(s)
                </span>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleBulkAction('activate')}
                  >
                    Ativar
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleBulkAction('deactivate')}
                  >
                    Desativar
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleBulkAction('delete')}
                  >
                    Excluir
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Payment Links List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Seus Links de Pagamento</CardTitle>
              <CardDescription>
                {filteredLinks.length} de {totalCount} links
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, index) => (
                <div key={index} className="flex items-center space-x-4">
                  <Skeleton className="h-12 w-12 rounded" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-[250px]" />
                    <Skeleton className="h-4 w-[200px]" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <PaymentLinkList
              links={filteredLinks}
              selectedLinks={selectedLinks}
              onSelectionChange={setSelectedLinks}
              onEdit={handleEditLink}
              onDelete={handleDeleteLink}
              onToggleStatus={handleToggleStatus}
              onViewAnalytics={(linkId) => {
                // Navigate to analytics view for specific link
                setCurrentView('analytics');
              }}
            />
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalCount > itemsPerPage && (
        <div className="flex items-center justify-center space-x-2">
          <Button
            variant="outline"
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            Anterior
          </Button>
          <span className="text-sm text-gray-600">
            Página {currentPage} de {Math.ceil(totalCount / itemsPerPage)}
          </span>
          <Button
            variant="outline"
            onClick={() => setCurrentPage(prev => prev + 1)}
            disabled={currentPage >= Math.ceil(totalCount / itemsPerPage)}
          >
            Próxima
          </Button>
        </div>
      )}
    </div>
  );
};

export { PaymentLinksManager };