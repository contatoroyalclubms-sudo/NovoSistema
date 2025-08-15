import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { dashboardService } from '@/services/api';

interface RealTimeData {
  evento_id: number;
  timestamp: string;
  vendas_ultima_hora: number;
  checkins_ultima_hora: number;
  ranking_promoters: any[];
  status_evento: string;
}

interface RealTimeDashboardProps {
  eventoId: number;
}

const RealTimeDashboard: React.FC<RealTimeDashboardProps> = ({ eventoId }) => {
  const [data, setData] = useState<RealTimeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    const fetchRealTimeData = async () => {
      try {
        const response = await dashboardService.obterDadosTempoReal(eventoId);
        setData(response);
        setLastUpdate(new Date().toLocaleTimeString('pt-BR'));
      } catch (error) {
        console.error('Erro ao buscar dados em tempo real:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRealTimeData();

    const interval = setInterval(fetchRealTimeData, 30000);

    return () => clearInterval(interval);
  }, [eventoId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Carregando dados em tempo real...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center p-8">
        <p className="text-red-600">Erro ao carregar dados em tempo real</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Dashboard em Tempo Real</h3>
        <Badge variant="outline" className="text-xs">
          Última atualização: {lastUpdate}
        </Badge>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Vendas (1h)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{data.vendas_ultima_hora}</div>
            <Badge variant="outline" className="mt-1">
              Última hora
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Check-ins (1h)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{data.checkins_ultima_hora}</div>
            <Badge variant="outline" className="mt-1">
              Última hora
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Status Evento</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant={data.status_evento === 'ativo' ? 'default' : 'secondary'}>
              {data.status_evento.toUpperCase()}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Top Promoter</CardTitle>
          </CardHeader>
          <CardContent>
            {data.ranking_promoters.length > 0 ? (
              <div>
                <div className="font-semibold text-sm">{data.ranking_promoters[0].nome_promoter}</div>
                <div className="text-xs text-gray-500">{data.ranking_promoters[0].total_vendas} vendas</div>
              </div>
            ) : (
              <div className="text-sm text-gray-500">Nenhuma venda</div>
            )}
          </CardContent>
        </Card>
      </div>

      {data.ranking_promoters.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Ranking Promoters (Top 5)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.ranking_promoters.slice(0, 5).map((promoter, index) => (
                <div key={index} className="flex justify-between items-center py-1">
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline" className="w-6 h-6 rounded-full p-0 flex items-center justify-center text-xs">
                      {index + 1}
                    </Badge>
                    <span className="text-sm font-medium">{promoter.nome_promoter}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold">{promoter.total_vendas} vendas</div>
                    <div className="text-xs text-gray-500">R$ {promoter.receita_total}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default RealTimeDashboard;
