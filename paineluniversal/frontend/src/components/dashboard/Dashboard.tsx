import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { dashboardService, eventoService, Evento } from '../../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { 
  Calendar, 
  Users, 
  DollarSign, 
  TrendingUp, 
  Clock,
  Trophy,
  BarChart3
} from 'lucide-react';

interface DashboardData {
  total_eventos: number;
  total_vendas: number;
  total_checkins: number;
  receita_total: number;
  eventos_hoje: number;
  vendas_hoje: number;
}

interface RankingPromoter {
  promoter_id: number;
  nome_promoter: string;
  total_vendas: number;
  receita_gerada: number;
  posicao: number;
}

const Dashboard: React.FC = () => {
  const { usuario } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [ranking, setRanking] = useState<RankingPromoter[]>([]);
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [eventoSelecionado, setEventoSelecionado] = useState<string>('todos');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarDados();
    carregarEventos();
  }, []);

  useEffect(() => {
    if (eventoSelecionado && eventoSelecionado !== 'todos') {
      carregarDadosEvento(parseInt(eventoSelecionado));
    } else {
      carregarDados();
    }
  }, [eventoSelecionado]);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const [resumo, rankingData] = await Promise.all([
        dashboardService.obterResumo(),
        dashboardService.obterRankingPromoters()
      ]);
      
      setDashboardData(resumo);
      setRanking(rankingData);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const carregarDadosEvento = async (eventoId: number) => {
    try {
      setLoading(true);
      const [resumo, rankingData] = await Promise.all([
        dashboardService.obterResumo(eventoId),
        dashboardService.obterRankingPromoters(eventoId)
      ]);
      
      setDashboardData(resumo);
      setRanking(rankingData);
    } catch (error) {
      console.error('Erro ao carregar dados do evento:', error);
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

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Bem-vindo, {usuario?.nome}! Aqui está o resumo das suas atividades.
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <Select value={eventoSelecionado} onValueChange={setEventoSelecionado}>
            <SelectTrigger className="w-64">
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
          
          <Button onClick={() => window.location.reload()} variant="outline">
            <BarChart3 className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Eventos</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.total_eventos || 0}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData?.eventos_hoje || 0} eventos hoje
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Vendas</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.total_vendas || 0}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData?.vendas_hoje || 0} vendas hoje
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Check-ins Realizados</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.total_checkins || 0}</div>
            <p className="text-xs text-muted-foreground">
              Pessoas presentes
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
              {formatCurrency(dashboardData?.receita_total || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Faturamento acumulado
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ranking de Promoters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Trophy className="h-5 w-5 mr-2" />
              Ranking de Promoters
            </CardTitle>
            <CardDescription>
              Top promoters por número de vendas
            </CardDescription>
          </CardHeader>
          <CardContent>
            {ranking.length > 0 ? (
              <div className="space-y-4">
                {ranking.slice(0, 5).map((promoter) => (
                  <div key={promoter.promoter_id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full text-sm font-bold">
                        {promoter.posicao}
                      </div>
                      <div>
                        <p className="font-medium">{promoter.nome_promoter}</p>
                        <p className="text-sm text-gray-500">
                          {promoter.total_vendas} vendas
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">
                        {formatCurrency(promoter.receita_gerada)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                Nenhum dado de vendas disponível
              </p>
            )}
          </CardContent>
        </Card>

        {/* Gráfico de vendas por hora (placeholder) */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="h-5 w-5 mr-2" />
              Vendas nas Últimas 24h
            </CardTitle>
            <CardDescription>
              Distribuição de vendas por hora
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>Dados de vendas em tempo real</p>
                <p className="text-sm">Em desenvolvimento</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Eventos recentes */}
      <Card>
        <CardHeader>
          <CardTitle>Eventos Recentes</CardTitle>
          <CardDescription>
            Últimos eventos criados no sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          {eventos.length > 0 ? (
            <div className="space-y-4">
              {eventos.slice(0, 5).map((evento) => (
                <div key={evento.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className="font-medium">{evento.nome}</h3>
                    <p className="text-sm text-gray-500">{evento.local}</p>
                    <p className="text-xs text-gray-400">
                      {new Date(evento.data_evento).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      evento.status === 'ativo' 
                        ? 'bg-green-100 text-green-800'
                        : evento.status === 'cancelado'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {evento.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Nenhum evento encontrado
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
