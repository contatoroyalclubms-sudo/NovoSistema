import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { 
  Plus, Filter, Download, Upload, TrendingUp, 
  TrendingDown, DollarSign, FileText, Eye, Edit, Receipt
} from 'lucide-react';
import { financeiroService, eventoService } from '../../services/api';
import MovimentacaoModal from './MovimentacaoModal';
import ComprovanteModal from './ComprovanteModal';

interface MovimentacaoFinanceira {
  id: number;
  tipo: string;
  categoria: string;
  descricao: string;
  valor: number;
  status: string;
  usuario_responsavel_nome: string;
  promoter_nome?: string;
  numero_documento?: string;
  comprovante_url?: string;
  criado_em: string;
  data_vencimento?: string;
  data_pagamento?: string;
  metodo_pagamento?: string;
}

interface DashboardFinanceiro {
  evento_id: number;
  saldo_atual: number;
  total_entradas: number;
  total_saidas: number;
  total_vendas: number;
  lucro_prejuizo: number;
  status_caixa: string;
}

const CaixaEvento: React.FC = () => {
  const { toast } = useToast();
  
  const [eventos, setEventos] = useState<any[]>([]);
  const [eventoSelecionado, setEventoSelecionado] = useState<number | null>(null);
  const [dashboard, setDashboard] = useState<DashboardFinanceiro | null>(null);
  const [movimentacoes, setMovimentacoes] = useState<MovimentacaoFinanceira[]>([]);
  const [loading, setLoading] = useState(false);
  const [filtros, setFiltros] = useState({
    tipo: '',
    categoria: '',
    status: '',
    data_inicio: '',
    data_fim: ''
  });
  
  const [movimentacaoModal, setMovimentacaoModal] = useState<{ open: boolean; movimentacao: MovimentacaoFinanceira | null }>({ open: false, movimentacao: null });
  const [comprovanteModal, setComprovanteModal] = useState<{ open: boolean; movimentacao: MovimentacaoFinanceira | null }>({ open: false, movimentacao: null });

  useEffect(() => {
    carregarEventos();
  }, []);

  useEffect(() => {
    if (eventoSelecionado) {
      carregarDashboard();
      carregarMovimentacoes();
    }
  }, [eventoSelecionado, filtros]);

  const carregarEventos = async () => {
    try {
      const eventosData = await eventoService.listar();
      setEventos(eventosData.filter(e => e.status === 'ativo'));
      if (eventosData.length > 0) {
        setEventoSelecionado(eventosData[0].id);
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar eventos",
        variant: "destructive"
      });
    }
  };

  const carregarDashboard = async () => {
    if (!eventoSelecionado) return;
    
    try {
      const dashboardData = await financeiroService.obterDashboard(eventoSelecionado);
      setDashboard(dashboardData);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar dashboard financeiro",
        variant: "destructive"
      });
    }
  };

  const carregarMovimentacoes = async () => {
    if (!eventoSelecionado) return;
    
    try {
      setLoading(true);
      const movimentacoesData = await financeiroService.listarMovimentacoes(
        eventoSelecionado, 
        filtros
      );
      setMovimentacoes(movimentacoesData);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar movimentações",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportar = async (formato: 'pdf' | 'excel' | 'csv') => {
    if (!eventoSelecionado) return;
    
    try {
      const blob = await financeiroService.exportarRelatorio(
        eventoSelecionado, 
        formato,
        filtros.data_inicio,
        filtros.data_fim
      );
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `financeiro_evento_${eventoSelecionado}.${formato === 'excel' ? 'xlsx' : formato}`;
      a.click();
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Sucesso",
        description: `Relatório exportado em ${formato.toUpperCase()}`,
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao exportar relatório",
        variant: "destructive"
      });
    }
  };

  const getTipoColor = (tipo: string) => {
    const colors: { [key: string]: string } = {
      'entrada': 'bg-green-100 text-green-800',
      'saida': 'bg-red-100 text-red-800',
      'ajuste': 'bg-blue-100 text-blue-800',
      'repasse_promoter': 'bg-purple-100 text-purple-800',
      'receita_vendas': 'bg-emerald-100 text-emerald-800',
      'receita_listas': 'bg-teal-100 text-teal-800'
    };
    return colors[tipo] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      'pendente': 'bg-yellow-100 text-yellow-800',
      'aprovada': 'bg-green-100 text-green-800',
      'cancelada': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  return (
    <div className="space-y-6 p-4">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Caixa do Evento & Financeiro</h1>
          <p className="text-gray-600">Gestão completa das finanças do evento</p>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Button 
            onClick={() => setMovimentacaoModal({ open: true, movimentacao: null })}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Nova Movimentação
          </Button>
          
          <Button 
            variant="outline"
            onClick={() => handleExportar('excel')}
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Exportar Excel
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Selecionar Evento</CardTitle>
        </CardHeader>
        <CardContent>
          <select
            className="w-full p-2 border rounded-md"
            value={eventoSelecionado || ''}
            onChange={(e) => setEventoSelecionado(parseInt(e.target.value))}
          >
            <option value="">Selecione um evento</option>
            {eventos.map((evento) => (
              <option key={evento.id} value={evento.id}>
                {evento.nome} - {new Date(evento.data_evento).toLocaleDateString('pt-BR')}
              </option>
            ))}
          </select>
        </CardContent>
      </Card>

      {dashboard && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center text-blue-700">
                <DollarSign className="h-4 w-4 mr-2" />
                Saldo Atual
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${dashboard.saldo_atual >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(dashboard.saldo_atual)}
              </div>
              <Badge variant={dashboard.status_caixa === 'aberto' ? "default" : "secondary"} className="mt-2">
                Caixa {dashboard.status_caixa}
              </Badge>
            </CardContent>
          </Card>

          <Card className="shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center text-green-700">
                <TrendingUp className="h-4 w-4 mr-2" />
                Total Entradas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {formatCurrency(dashboard.total_entradas)}
              </div>
              <div className="text-sm text-green-600 font-medium">
                + Vendas: {formatCurrency(dashboard.total_vendas)}
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center text-red-700">
                <TrendingDown className="h-4 w-4 mr-2" />
                Total Saídas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">
                {formatCurrency(dashboard.total_saidas)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Despesas e repasses
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center text-purple-700">
                <FileText className="h-4 w-4 mr-2" />
                Lucro/Prejuízo
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${dashboard.lucro_prejuizo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(dashboard.lucro_prejuizo)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Resultado final
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <Label>Tipo</Label>
              <select
                className="w-full mt-1 p-2 border rounded-md"
                value={filtros.tipo}
                onChange={(e) => setFiltros({ ...filtros, tipo: e.target.value })}
              >
                <option value="">Todos os tipos</option>
                <option value="entrada">Entrada</option>
                <option value="saida">Saída</option>
                <option value="ajuste">Ajuste</option>
                <option value="repasse_promoter">Repasse Promoter</option>
              </select>
            </div>
            
            <div>
              <Label>Categoria</Label>
              <Input
                placeholder="Ex: Bebidas, Segurança..."
                value={filtros.categoria}
                onChange={(e) => setFiltros({ ...filtros, categoria: e.target.value })}
              />
            </div>
            
            <div>
              <Label>Status</Label>
              <select
                className="w-full mt-1 p-2 border rounded-md"
                value={filtros.status}
                onChange={(e) => setFiltros({ ...filtros, status: e.target.value })}
              >
                <option value="">Todos</option>
                <option value="pendente">Pendente</option>
                <option value="aprovada">Aprovada</option>
                <option value="cancelada">Cancelada</option>
              </select>
            </div>
            
            <div>
              <Label>Data Início</Label>
              <Input
                type="date"
                value={filtros.data_inicio}
                onChange={(e) => setFiltros({ ...filtros, data_inicio: e.target.value })}
              />
            </div>
            
            <div>
              <Label>Data Fim</Label>
              <Input
                type="date"
                value={filtros.data_fim}
                onChange={(e) => setFiltros({ ...filtros, data_fim: e.target.value })}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Movimentações Financeiras</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Carregando movimentações...</p>
            </div>
          ) : movimentacoes.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500">Nenhuma movimentação encontrada</p>
              <Button 
                onClick={() => setMovimentacaoModal({ open: true, movimentacao: null })}
                className="mt-4"
              >
                Criar primeira movimentação
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {movimentacoes.map((movimentacao) => (
                <div key={movimentacao.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className={getTipoColor(movimentacao.tipo)}>
                          {movimentacao.tipo.toUpperCase()}
                        </Badge>
                        <Badge className={getStatusColor(movimentacao.status)}>
                          {movimentacao.status.toUpperCase()}
                        </Badge>
                        {movimentacao.comprovante_url && (
                          <Badge variant="outline" className="text-blue-600">
                            <Receipt className="h-3 w-3 mr-1" />
                            Comprovante
                          </Badge>
                        )}
                      </div>
                      
                      <h3 className="font-semibold">{movimentacao.categoria}</h3>
                      <p className="text-gray-600 text-sm">{movimentacao.descricao}</p>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3 text-sm">
                        <div>
                          <span className="text-gray-500">Valor:</span>
                          <p className={`font-semibold ${movimentacao.tipo === 'entrada' ? 'text-green-600' : 'text-red-600'}`}>
                            {movimentacao.tipo === 'entrada' ? '+' : '-'}{formatCurrency(movimentacao.valor)}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-500">Responsável:</span>
                          <p className="font-medium">{movimentacao.usuario_responsavel_nome}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Data:</span>
                          <p>{new Date(movimentacao.criado_em).toLocaleDateString('pt-BR')}</p>
                        </div>
                        {movimentacao.numero_documento && (
                          <div>
                            <span className="text-gray-500">Documento:</span>
                            <p className="font-mono text-xs">{movimentacao.numero_documento}</p>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex gap-2 ml-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setMovimentacaoModal({ open: true, movimentacao })}
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                      
                      {movimentacao.comprovante_url ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setComprovanteModal({ open: true, movimentacao })}
                        >
                          <Eye className="h-3 w-3" />
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setComprovanteModal({ open: true, movimentacao })}
                        >
                          <Upload className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <MovimentacaoModal
        isOpen={movimentacaoModal.open}
        onClose={() => setMovimentacaoModal({ open: false, movimentacao: null })}
        movimentacao={movimentacaoModal.movimentacao}
        eventoId={eventoSelecionado}
        onSuccess={() => {
          carregarMovimentacoes();
          carregarDashboard();
        }}
      />
      
      <ComprovanteModal
        isOpen={comprovanteModal.open}
        onClose={() => setComprovanteModal({ open: false, movimentacao: null })}
        movimentacao={comprovanteModal.movimentacao}
        onSuccess={carregarMovimentacoes}
      />
    </div>
  );
};

export default CaixaEvento;
