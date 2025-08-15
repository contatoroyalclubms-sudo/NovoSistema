import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { 
  LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { 
  TrendingUp, Users, DollarSign, Calendar, Trophy,
  Download, RefreshCw, AlertTriangle, Gift, CreditCard
} from 'lucide-react';
import { dashboardService, eventoService } from '../../services/api';
import { websocketService } from '../../services/websocket';

interface DashboardAvancadoData {
  total_eventos: number;
  total_vendas: number;
  total_checkins: number;
  receita_total: number;
  taxa_conversao: number;
  vendas_hoje: number;
  vendas_semana: number;
  vendas_mes: number;
  receita_hoje: number;
  receita_semana: number;
  receita_mes: number;
  checkins_hoje: number;
  checkins_semana: number;
  taxa_presenca: number;
  fila_espera: number;
  cortesias: number;
  inadimplentes: number;
  aniversariantes_mes: number;
  consumo_medio: number;
}

interface RankingPromoter {
  promoter_id: number;
  nome_promoter: string;
  total_vendas: number;
  receita_gerada: number;
  total_checkins: number;
  taxa_presenca: number;
  taxa_conversao: number;
  posicao: number;
  badge: string;
}

const DashboardAvancado: React.FC = () => {
  const [data, setData] = useState<DashboardAvancadoData | null>(null);
  const [eventos, setEventos] = useState<any[]>([]);
  const [ranking, setRanking] = useState<RankingPromoter[]>([]);
  const [filtros, setFiltros] = useState({
    evento_id: null as number | null,
    periodo: '30d',
    tipo_lista: 'todos'
  });
  const [loading, setLoading] = useState(true);
  const [graficos, setGraficos] = useState<any>({
    vendas_tempo: [],
    vendas_lista: []
  });
  const { toast } = useToast();

  useEffect(() => {
    carregarDados();
    carregarEventos();
  }, []);

  useEffect(() => {
    carregarDados();
    if (filtros.evento_id) {
      conectarWebSocket();
    }
  }, [filtros]);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const [dashboardData, graficosVendasTempo, graficosVendasLista, rankingData] = await Promise.all([
        dashboardService.obterDashboardAvancado(filtros),
        dashboardService.obterGraficosVendasTempo(filtros.periodo, filtros.evento_id || undefined),
        dashboardService.obterGraficosVendasLista(filtros.evento_id || undefined),
        dashboardService.obterRankingAvancado(filtros.evento_id || undefined)
      ]);
      
      setData(dashboardData);
      setGraficos({
        vendas_tempo: graficosVendasTempo,
        vendas_lista: graficosVendasLista
      });
      setRanking(rankingData);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      toast({
        title: "Erro",
        description: "Erro ao carregar dados do dashboard",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const carregarEventos = async () => {
    try {
      const eventosData = await eventoService.listar();
      setEventos(eventosData);
    } catch (error) {
      console.error('Erro ao carregar eventos:', error);
    }
  };

  const conectarWebSocket = () => {
    if (filtros.evento_id) {
      websocketService.connect(filtros.evento_id);
      websocketService.on('dashboard_update', () => {
        carregarDados();
      });
      websocketService.on('venda_realizada', () => {
        carregarDados();
      });
      websocketService.on('checkin_update', () => {
        carregarDados();
      });
    }
  };

  const exportarRelatorio = async (formato: 'pdf' | 'csv' | 'excel') => {
    try {
      const response = await dashboardService.exportarDashboard(formato, filtros);
      const blob = new Blob([response], { 
        type: formato === 'excel' 
          ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          : formato === 'pdf' 
          ? 'application/pdf' 
          : 'text/csv'
      });
      
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `dashboard_${new Date().toISOString().split('T')[0]}.${formato}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
      
      toast({
        title: "Sucesso",
        description: `Relatório ${formato.toUpperCase()} exportado com sucesso`,
      });
    } catch (error) {
      console.error('Erro ao exportar:', error);
      toast({
        title: "Erro",
        description: "Erro ao exportar relatório",
        variant: "destructive"
      });
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const getBadgeColor = (badge: string) => {
    switch (badge) {
      case 'ouro': return 'bg-yellow-500 text-white';
      case 'prata': return 'bg-gray-400 text-white';
      case 'bronze': return 'bg-orange-600 text-white';
      default: return 'bg-blue-500 text-white';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Dashboard Inteligente</h1>
          <p className="text-gray-600">Relatórios avançados e métricas em tempo real</p>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Select 
            value={filtros.evento_id?.toString() || 'todos'} 
            onValueChange={(value) => setFiltros({...filtros, evento_id: value === 'todos' ? null : parseInt(value)})}
          >
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Todos os eventos" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="todos">Todos os eventos</SelectItem>
              {eventos.map((evento) => (
                <SelectItem key={evento.id} value={evento.id.toString()}>
                  {evento.nome}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select value={filtros.periodo} onValueChange={(value) => setFiltros({...filtros, periodo: value})}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">24 horas</SelectItem>
              <SelectItem value="7d">7 dias</SelectItem>
              <SelectItem value="30d">30 dias</SelectItem>
            </SelectContent>
          </Select>
          
          <Button onClick={carregarDados} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          
          <div className="flex gap-1">
            <Button onClick={() => exportarRelatorio('pdf')} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-1" />
              PDF
            </Button>
            <Button onClick={() => exportarRelatorio('excel')} variant="outline" size="sm">
              Excel
            </Button>
            <Button onClick={() => exportarRelatorio('csv')} variant="outline" size="sm">
              CSV
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <TrendingUp className="h-4 w-4 mr-1" />
              Vendas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{data?.total_vendas || 0}</div>
            <p className="text-xs text-gray-500">+{data?.vendas_hoje || 0} hoje</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <Users className="h-4 w-4 mr-1" />
              Check-ins
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{data?.total_checkins || 0}</div>
            <p className="text-xs text-gray-500">+{data?.checkins_hoje || 0} hoje</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <DollarSign className="h-4 w-4 mr-1" />
              Receita
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {formatCurrency(data?.receita_total || 0)}
            </div>
            <p className="text-xs text-gray-500">
              +{formatCurrency(data?.receita_hoje || 0)} hoje
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <Trophy className="h-4 w-4 mr-1" />
              Conversão
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{data?.taxa_conversao || 0}%</div>
            <p className="text-xs text-gray-500">Taxa presença</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <Gift className="h-4 w-4 mr-1" />
              Cortesias
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-pink-600">{data?.cortesias || 0}</div>
            <p className="text-xs text-gray-500">Entradas grátis</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <AlertTriangle className="h-4 w-4 mr-1" />
              Inadimplentes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{data?.inadimplentes || 0}</div>
            <p className="text-xs text-gray-500">Pendências</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              Aniversários
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{data?.aniversariantes_mes || 0}</div>
            <p className="text-xs text-gray-500">Este mês</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <CreditCard className="h-4 w-4 mr-1" />
              Consumo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-indigo-600">
              {formatCurrency(data?.consumo_medio || 0)}
            </div>
            <p className="text-xs text-gray-500">Ticket médio</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Vendas ao Longo do Tempo</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={graficos.vendas_tempo || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="data" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="vendas" stroke="#8884d8" strokeWidth={2} name="Vendas" />
                <Line type="monotone" dataKey="receita" stroke="#82ca9d" strokeWidth={2} name="Receita (R$)" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Vendas por Lista</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={graficos.vendas_lista || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {(graficos.vendas_lista || []).map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.fill || '#8884d8'} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Trophy className="h-5 w-5 mr-2" />
            Ranking de Promoters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {ranking.length > 0 ? (
              ranking.map((promoter) => (
                <div key={promoter.promoter_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <Badge className={`${getBadgeColor(promoter.badge)} w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold`}>
                      {promoter.posicao}
                    </Badge>
                    <div>
                      <h3 className="font-semibold">{promoter.nome_promoter}</h3>
                      <p className="text-sm text-gray-600">
                        {promoter.total_vendas} vendas • {promoter.total_checkins} check-ins
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">
                      {formatCurrency(promoter.receita_gerada)}
                    </div>
                    <div className="text-sm text-gray-600">
                      {promoter.taxa_presenca}% presença
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Trophy className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Nenhum promoter encontrado</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardAvancado;
