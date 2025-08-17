import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { useToast } from '../../hooks/use-toast';
import { BarChart3, Users, TrendingUp, Award, Crown } from 'lucide-react';
import { listaService, dashboardService } from '../../services/api';

interface DashboardListasModalProps {
  isOpen: boolean;
  onClose: () => void;
  eventoId: number | null;
}

const DashboardListasModal: React.FC<DashboardListasModalProps> = ({
  isOpen,
  onClose,
  eventoId
}) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [dashboard, setDashboard] = useState<any>(null);
  const [ranking, setRanking] = useState<any[]>([]);

  useEffect(() => {
    if (isOpen && eventoId) {
      carregarDashboard();
      carregarRanking();
    }
  }, [isOpen, eventoId]);

  const carregarDashboard = async () => {
    if (!eventoId) return;
    
    try {
      setLoading(true);
      const dashboardData = await listaService.obterDashboard(eventoId);
      setDashboard(dashboardData);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao carregar dashboard",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const carregarRanking = async () => {
    if (!eventoId) return;
    
    try {
      const rankingData = await dashboardService.obterRankingPromoters(eventoId, 10);
      setRanking(rankingData);
    } catch (error) {
      console.error('Erro ao carregar ranking:', error);
    }
  };

  const getBadgeIcon = (posicao: number) => {
    if (posicao === 1) return <Crown className="h-5 w-5 text-yellow-500" />;
    if (posicao === 2) return <Award className="h-5 w-5 text-gray-400" />;
    if (posicao === 3) return <Award className="h-5 w-5 text-orange-500" />;
    return <span className="text-gray-500">#{posicao}</span>;
  };

  const getBadgeColor = (posicao: number) => {
    if (posicao === 1) return 'bg-yellow-100 text-yellow-800';
    if (posicao === 2) return 'bg-gray-100 text-gray-800';
    if (posicao === 3) return 'bg-orange-100 text-orange-800';
    return 'bg-blue-100 text-blue-800';
  };

  if (!eventoId) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Dashboard de Listas e Promoters
          </DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Carregando dashboard...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {dashboard && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-blue-600">{dashboard.total_listas}</p>
                        <p className="text-sm text-gray-600">Total de Listas</p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-green-600">{dashboard.total_convidados}</p>
                        <p className="text-sm text-gray-600">Total Convidados</p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-purple-600">{dashboard.total_presentes}</p>
                        <p className="text-sm text-gray-600">Presentes</p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-orange-600">{dashboard.taxa_presenca_geral}%</p>
                        <p className="text-sm text-gray-600">Taxa Presença</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {dashboard.listas_mais_ativas && dashboard.listas_mais_ativas.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="h-5 w-5" />
                        Listas Mais Ativas
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {dashboard.listas_mais_ativas.map((lista: any, index: number) => (
                          <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-md">
                            <div>
                              <h4 className="font-semibold">{lista.nome}</h4>
                              <p className="text-sm text-gray-600 capitalize">{lista.tipo}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-semibold text-blue-600">{lista.convidados}</p>
                              <p className="text-sm text-gray-600">convidados</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}

            {ranking && ranking.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Ranking de Promoters
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {ranking.map((promoter: any, index: number) => (
                      <div key={promoter.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-4">
                          <div className="flex items-center gap-2">
                            {getBadgeIcon(index + 1)}
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getBadgeColor(index + 1)}`}>
                              {index + 1}º
                            </span>
                          </div>
                          <div>
                            <h4 className="font-semibold">{promoter.nome}</h4>
                            <p className="text-sm text-gray-600">
                              {promoter.total_vendas} vendas • {promoter.total_checkins} check-ins
                            </p>
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <p className="font-semibold text-green-600">
                            R$ {promoter.receita_total?.toFixed(2) || '0.00'}
                          </p>
                          <p className="text-sm text-gray-600">
                            {promoter.taxa_conversao?.toFixed(1) || '0.0'}% conversão
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        <div className="flex justify-end pt-4">
          <Button variant="outline" onClick={onClose}>
            Fechar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default DashboardListasModal;
