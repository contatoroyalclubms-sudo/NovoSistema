import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { BarChart3, TrendingUp, Users, Target, Calendar, Award } from 'lucide-react';
import { gamificacaoService } from '../../services/api';
import { useToast } from '../../hooks/use-toast';

interface MetricasModalProps {
  isOpen: boolean;
  onClose: () => void;
  promoter: any;
}

const MetricasModal: React.FC<MetricasModalProps> = ({ isOpen, onClose, promoter }) => {
  const { toast } = useToast();
  const [metricas, setMetricas] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && promoter) {
      carregarMetricas();
    }
  }, [isOpen, promoter]);

  const carregarMetricas = async () => {
    try {
      setLoading(true);
      const mockMetricas = {
        promoter_id: promoter.promoter_id,
        promoter_nome: promoter.nome_promoter,
        periodo_inicio: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        periodo_fim: new Date().toISOString().split('T')[0],
        total_vendas: promoter.total_vendas,
        receita_gerada: promoter.receita_gerada,
        total_convidados: promoter.total_vendas + 20,
        total_presentes: Math.floor(promoter.total_vendas * (promoter.taxa_presenca / 100)),
        taxa_presenca: promoter.taxa_presenca,
        taxa_conversao: promoter.taxa_conversao,
        crescimento_vendas: promoter.crescimento_mensal,
        posicao_vendas: promoter.posicao_atual,
        posicao_presenca: promoter.posicao_atual + 1,
        posicao_geral: promoter.posicao_atual,
        badge_atual: promoter.badge_principal,
        conquistas_recentes: []
      };
      setMetricas(mockMetricas);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar métricas",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Métricas Detalhadas - {promoter?.nome_promoter}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Carregando métricas...</p>
            </div>
          ) : metricas ? (
            <>
              {/* Período */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Calendar className="h-4 w-4" />
                    Período Analisado
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">
                    {new Date(metricas.periodo_inicio).toLocaleDateString('pt-BR')} até{' '}
                    {new Date(metricas.periodo_fim).toLocaleDateString('pt-BR')}
                  </p>
                </CardContent>
              </Card>

              {/* Métricas Principais */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center text-blue-700">
                      <Target className="h-4 w-4 mr-2" />
                      Total Vendas
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-600">
                      {metricas.total_vendas}
                    </div>
                    <div className="text-xs text-gray-500">
                      Posição: #{metricas.posicao_vendas}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center text-green-700">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Receita Gerada
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">
                      {formatCurrency(metricas.receita_gerada)}
                    </div>
                    <div className="text-xs text-gray-500">
                      Média por venda: {formatCurrency(metricas.receita_gerada / metricas.total_vendas)}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center text-purple-700">
                      <Users className="h-4 w-4 mr-2" />
                      Taxa Presença
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-purple-600">
                      {metricas.taxa_presenca}%
                    </div>
                    <div className="text-xs text-gray-500">
                      {metricas.total_presentes} de {metricas.total_convidados} convidados
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center text-orange-700">
                      <Award className="h-4 w-4 mr-2" />
                      Badge Atual
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-orange-600 capitalize">
                      {metricas.badge_atual}
                    </div>
                    <div className="text-xs text-gray-500">
                      Posição geral: #{metricas.posicao_geral}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Métricas Detalhadas */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Análise Detalhada</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3">Performance de Vendas</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Total de Convidados:</span>
                          <span className="font-medium">{metricas.total_convidados}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Vendas Confirmadas:</span>
                          <span className="font-medium">{metricas.total_vendas}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Taxa de Conversão:</span>
                          <span className="font-medium">{metricas.taxa_conversao}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Crescimento:</span>
                          <span className={`font-medium ${metricas.crescimento_vendas >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {metricas.crescimento_vendas >= 0 ? '+' : ''}{metricas.crescimento_vendas}%
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold mb-3">Rankings</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Posição em Vendas:</span>
                          <span className="font-medium">#{metricas.posicao_vendas}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Posição em Presença:</span>
                          <span className="font-medium">#{metricas.posicao_presenca}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Posição Geral:</span>
                          <span className="font-medium">#{metricas.posicao_geral}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Barra de Progresso */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Progresso para Próximo Badge</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Badge Atual: {metricas.badge_atual.toUpperCase()}</span>
                      <span>Próximo: {getProximoBadge(metricas.badge_atual).toUpperCase()}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${calcularProgressoBadge(metricas)}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-600">
                      {getDescricaoProgresso(metricas)}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <div className="text-center py-8">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500">Nenhuma métrica encontrada</p>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose}>
            Fechar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

const getProximoBadge = (badgeAtual: string): string => {
  const badges = ['bronze', 'prata', 'ouro', 'platina', 'diamante', 'lenda'];
  const index = badges.indexOf(badgeAtual);
  return index < badges.length - 1 ? badges[index + 1] : 'lenda';
};

const calcularProgressoBadge = (metricas: any): number => {
  const vendas = metricas.total_vendas;
  const presenca = metricas.taxa_presenca;
  
  switch (metricas.badge_atual) {
    case 'bronze':
      return Math.min(100, (vendas / 50) * 100);
    case 'prata':
      return Math.min(100, (vendas / 100) * 100);
    case 'ouro':
      return Math.min(100, ((vendas / 200) * 50) + ((presenca / 80) * 50));
    case 'platina':
      return Math.min(100, ((vendas / 500) * 50) + ((presenca / 90) * 50));
    case 'diamante':
      return Math.min(100, (vendas / 1000) * 100);
    default:
      return 100;
  }
};

const getDescricaoProgresso = (metricas: any): string => {
  const vendas = metricas.total_vendas;
  const presenca = metricas.taxa_presenca;
  
  switch (metricas.badge_atual) {
    case 'bronze':
      return `Faltam ${Math.max(0, 50 - vendas)} vendas para badge Prata`;
    case 'prata':
      return `Faltam ${Math.max(0, 100 - vendas)} vendas para badge Ouro`;
    case 'ouro':
      const vendasFaltam = Math.max(0, 200 - vendas);
      const presencaFalta = Math.max(0, 80 - presenca);
      return `Para Platina: ${vendasFaltam} vendas e ${presencaFalta.toFixed(1)}% presença`;
    case 'platina':
      const vendasDiamante = Math.max(0, 500 - vendas);
      const presencaDiamante = Math.max(0, 90 - presenca);
      return `Para Diamante: ${vendasDiamante} vendas e ${presencaDiamante.toFixed(1)}% presença`;
    case 'diamante':
      return `Faltam ${Math.max(0, 1000 - vendas)} vendas para badge Lenda`;
    default:
      return 'Parabéns! Você alcançou o nível máximo!';
  }
};

export default MetricasModal;
