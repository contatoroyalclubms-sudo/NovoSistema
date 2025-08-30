import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../../hooks/use-toast';
import { useIsMobile } from '../../hooks/use-mobile';
import { 
  Trophy, Crown, Medal, Star, TrendingUp, TrendingDown, 
  Download, Filter, Search, Award, Target, Zap,
  Users, Calendar, BarChart3, Gift, Flame
} from 'lucide-react';
import { gamificacaoService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import ConquistasModal from './ConquistasModal';
import MetricasModal from './MetricasModal';

interface RankingPromoter {
  promoter_id: number;
  nome_promoter: string;
  avatar_url?: string;
  badge_principal: string;
  nivel_experiencia: number;
  total_vendas: number;
  receita_gerada: number;
  taxa_presenca: number;
  taxa_conversao: number;
  crescimento_mensal: number;
  posicao_atual: number;
  posicao_anterior?: number;
  conquistas_total: number;
  conquistas_mes: number;
  eventos_ativos: number;
  streak_vendas: number;
  pontuacao_total: number;
}

interface DashboardGamificacao {
  ranking_geral: RankingPromoter[];
  conquistas_recentes: any[];
  metricas_periodo: any;
  badges_disponiveis: any[];
  alertas_gamificacao: any[];
  estatisticas_gerais: any;
}

const RankingModule: React.FC = () => {
  const { usuario } = useAuth();
  const { toast } = useToast();
  const isMobile = useIsMobile();
  
  const [dashboard, setDashboard] = useState<DashboardGamificacao | null>(null);
  const [ranking, setRanking] = useState<RankingPromoter[]>([]);
  const [loading, setLoading] = useState(false);
  const [filtros, setFiltros] = useState({
    evento_id: '',
    periodo_inicio: '',
    periodo_fim: '',
    badge_nivel: '',
    tipo_ranking: 'geral',
    limit: 20
  });
  
  const [conquistasModal, setConquistasModal] = useState({ open: false, promoter: null });
  const [metricasModal, setMetricasModal] = useState({ open: false, promoter: null });

  useEffect(() => {
    carregarDashboard();
    carregarRanking();
  }, []);

  useEffect(() => {
    carregarRanking();
  }, [filtros]);

  const carregarDashboard = async () => {
    try {
      const dashboardData = await gamificacaoService.obterDashboard();
      setDashboard(dashboardData);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar dashboard de gamificação",
        variant: "destructive"
      });
    }
  };

  const carregarRanking = async () => {
    try {
      setLoading(true);
      const rankingData = await gamificacaoService.obterRanking(filtros);
      setRanking(rankingData);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar ranking",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportar = async (formato: 'excel' | 'csv' | 'pdf') => {
    try {
      const blob = await gamificacaoService.exportarRanking(formato, filtros);
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ranking_promoters.${formato === 'excel' ? 'xlsx' : formato}`;
      a.click();
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Sucesso",
        description: `Ranking exportado em ${formato.toUpperCase()}`,
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao exportar ranking",
        variant: "destructive"
      });
    }
  };

  const getBadgeIcon = (badge: string) => {
    const icons = {
      'lenda': <Crown className="h-5 w-5 text-purple-600" />,
      'diamante': <Star className="h-5 w-5 text-blue-600" />,
      'platina': <Award className="h-5 w-5 text-gray-400" />,
      'ouro': <Trophy className="h-5 w-5 text-yellow-500" />,
      'prata': <Medal className="h-5 w-5 text-gray-500" />,
      'bronze': <Target className="h-5 w-5 text-orange-600" />
    };
    return icons[badge] || <Target className="h-5 w-5 text-gray-400" />;
  };

  const getBadgeColor = (badge: string) => {
    const colors = {
      'lenda': 'bg-purple-100 text-purple-800 border-purple-200',
      'diamante': 'bg-blue-100 text-blue-800 border-blue-200',
      'platina': 'bg-gray-100 text-gray-800 border-gray-200',
      'ouro': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'prata': 'bg-gray-100 text-gray-600 border-gray-200',
      'bronze': 'bg-orange-100 text-orange-800 border-orange-200'
    };
    return colors[badge] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const getPosicaoChange = (atual: number, anterior?: number) => {
    if (!anterior) return null;
    
    const diff = anterior - atual;
    if (diff > 0) {
      return <TrendingUp className="h-4 w-4 text-green-600" />;
    } else if (diff < 0) {
      return <TrendingDown className="h-4 w-4 text-red-600" />;
    }
    return null;
  };

  return (
    <div className="space-y-6 p-4">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Trophy className="h-8 w-8 text-yellow-500" />
            Ranking & Gamificação
          </h1>
          <p className="text-gray-600">Sistema de ranking e conquistas para promoters</p>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Button 
            onClick={() => handleExportar('excel')}
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Excel
          </Button>
          
          <Button 
            variant="outline"
            onClick={() => handleExportar('csv')}
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            CSV
          </Button>
        </div>
      </div>

      {dashboard && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center text-blue-700">
                <Users className="h-4 w-4 mr-2" />
                Total Promoters
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {dashboard.metricas_periodo.total_promoters}
              </div>
              <div className="text-sm text-blue-600 font-medium">
                Ativos no período
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center text-green-700">
                <Gift className="h-4 w-4 mr-2" />
                Conquistas Semana
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {dashboard.metricas_periodo.conquistas_semana}
              </div>
              <div className="text-sm text-green-600 font-medium">
                Novos badges
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center text-yellow-700">
                <Trophy className="h-4 w-4 mr-2" />
                Badges Ouro
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">
                {dashboard.metricas_periodo.badge_ouro}
              </div>
              <div className="text-sm text-yellow-600 font-medium">
                Top performers
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center text-purple-700">
                <BarChart3 className="h-4 w-4 mr-2" />
                Crescimento Médio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                {dashboard.metricas_periodo.crescimento_medio}%
              </div>
              <div className="text-sm text-purple-600 font-medium">
                Mês atual
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtros de Ranking
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <Label>Tipo de Ranking</Label>
              <select
                className="w-full mt-1 p-2 border rounded-md"
                value={filtros.tipo_ranking}
                onChange={(e) => setFiltros({ ...filtros, tipo_ranking: e.target.value })}
              >
                <option value="geral">Geral</option>
                <option value="vendas">Por Vendas</option>
                <option value="presenca">Por Presença</option>
                <option value="crescimento">Por Crescimento</option>
              </select>
            </div>
            
            <div>
              <Label>Badge Mínimo</Label>
              <select
                className="w-full mt-1 p-2 border rounded-md"
                value={filtros.badge_nivel}
                onChange={(e) => setFiltros({ ...filtros, badge_nivel: e.target.value })}
              >
                <option value="">Todos os badges</option>
                <option value="bronze">Bronze+</option>
                <option value="prata">Prata+</option>
                <option value="ouro">Ouro+</option>
                <option value="platina">Platina+</option>
                <option value="diamante">Diamante+</option>
                <option value="lenda">Lenda</option>
              </select>
            </div>
            
            <div>
              <Label>Data Início</Label>
              <Input
                type="date"
                value={filtros.periodo_inicio}
                onChange={(e) => setFiltros({ ...filtros, periodo_inicio: e.target.value })}
              />
            </div>
            
            <div>
              <Label>Data Fim</Label>
              <Input
                type="date"
                value={filtros.periodo_fim}
                onChange={(e) => setFiltros({ ...filtros, periodo_fim: e.target.value })}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Ranking de Promoters
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Carregando ranking...</p>
            </div>
          ) : ranking.length === 0 ? (
            <div className="text-center py-8">
              <Trophy className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500">Nenhum promoter encontrado</p>
            </div>
          ) : (
            <div className="space-y-4">
              {ranking.map((promoter, index) => (
                <div key={promoter.promoter_id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className="flex items-center gap-2">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                          index === 0 ? 'bg-yellow-500' : 
                          index === 1 ? 'bg-gray-400' : 
                          index === 2 ? 'bg-orange-600' : 'bg-gray-600'
                        }`}>
                          {promoter.posicao_atual}
                        </div>
                        {getPosicaoChange(promoter.posicao_atual, promoter.posicao_anterior)}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-lg">{promoter.nome_promoter}</h3>
                          <Badge className={`${getBadgeColor(promoter.badge_principal)} flex items-center gap-1`}>
                            {getBadgeIcon(promoter.badge_principal)}
                            {promoter.badge_principal.toUpperCase()}
                          </Badge>
                          {promoter.streak_vendas > 0 && (
                            <Badge variant="outline" className="text-orange-600">
                              <Flame className="h-3 w-3 mr-1" />
                              {promoter.streak_vendas}x
                            </Badge>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Vendas:</span>
                            <p className="font-semibold text-blue-600">{promoter.total_vendas}</p>
                          </div>
                          <div>
                            <span className="text-gray-500">Receita:</span>
                            <p className="font-semibold text-green-600">{formatCurrency(promoter.receita_gerada)}</p>
                          </div>
                          <div>
                            <span className="text-gray-500">Presença:</span>
                            <p className="font-semibold">{promoter.taxa_presenca}%</p>
                          </div>
                          <div>
                            <span className="text-gray-500">Conquistas:</span>
                            <p className="font-semibold text-purple-600">
                              {promoter.conquistas_total} 
                              {promoter.conquistas_mes > 0 && (
                                <span className="text-green-600"> (+{promoter.conquistas_mes})</span>
                              )}
                            </p>
                          </div>
                        </div>
                        
                        <div className="mt-2">
                          <div className="flex justify-between text-xs text-gray-500 mb-1">
                            <span>Nível {Math.floor(promoter.nivel_experiencia / 10)}</span>
                            <span>{promoter.pontuacao_total} pts</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${promoter.nivel_experiencia}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 ml-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setConquistasModal({ open: true, promoter })}
                      >
                        <Award className="h-3 w-3" />
                      </Button>
                      
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setMetricasModal({ open: true, promoter })}
                      >
                        <BarChart3 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {dashboard && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Sistema de Badges
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dashboard.badges_disponiveis.map((badge, index) => (
                <div key={index} className="border rounded-lg p-4 text-center">
                  <div className="text-3xl mb-2">{badge.icone}</div>
                  <h3 className="font-semibold">{badge.nome}</h3>
                  <p className="text-sm text-gray-600">{badge.descricao}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <ConquistasModal
        isOpen={conquistasModal.open}
        onClose={() => setConquistasModal({ open: false, promoter: null })}
        promoter={conquistasModal.promoter}
      />
      
      <MetricasModal
        isOpen={metricasModal.open}
        onClose={() => setMetricasModal({ open: false, promoter: null })}
        promoter={metricasModal.promoter}
      />
    </div>
  );
};

export default RankingModule;
