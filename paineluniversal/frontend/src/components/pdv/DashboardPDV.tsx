import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { pdvService } from '@/services/api';
import { AlertTriangle, TrendingUp, Users, Package, DollarSign, Clock } from 'lucide-react';

const toNumber = (value: any): number => {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') return parseFloat(value) || 0;
  return 0;
};

interface DashboardPDVProps {
  eventoId: number;
}

const DashboardPDV: React.FC<DashboardPDVProps> = ({ eventoId }) => {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const data = await pdvService.obterDashboardPDV(eventoId);
        setDashboard(data);
        setLastUpdate(new Date().toLocaleTimeString('pt-BR'));
      } catch (error) {
        console.error('Erro ao carregar dashboard PDV:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
    
    const interval = setInterval(fetchDashboard, 30000);
    
    return () => clearInterval(interval);
  }, [eventoId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Carregando dashboard PDV...</p>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="text-center p-8">
        <p className="text-red-600">Erro ao carregar dashboard PDV</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Dashboard PDV</h2>
        <Badge variant="outline" className="text-xs">
          <Clock className="h-3 w-3 mr-1" />
          Última atualização: {lastUpdate}
        </Badge>
      </div>

      {dashboard.produtos_em_falta > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <strong>{dashboard.produtos_em_falta} produto(s)</strong> com estoque baixo ou esgotado. 
            Verifique o estoque para evitar perdas de vendas.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-green-700">
              <TrendingUp className="h-4 w-4 mr-2" />
              Vendas Hoje
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{dashboard.vendas_hoje}</div>
            <div className="text-sm text-green-600 font-medium">
              R$ {toNumber(dashboard.valor_vendas_hoje).toFixed(2)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Vendas realizadas hoje
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-red-700">
              <Package className="h-4 w-4 mr-2" />
              Produtos em Falta
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {dashboard.produtos_em_falta}
            </div>
            <div className="text-sm text-red-600 font-medium">
              Requer atenção
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Estoque baixo/esgotado
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-blue-700">
              <Users className="h-4 w-4 mr-2" />
              Comandas Ativas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">{dashboard.comandas_ativas}</div>
            <div className="text-sm text-blue-600 font-medium">
              Em circulação
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Comandas com saldo
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center text-purple-700">
              <DollarSign className="h-4 w-4 mr-2" />
              Caixas Abertos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">{dashboard.caixas_abertos}</div>
            <Badge variant={dashboard.caixas_abertos > 0 ? "default" : "secondary"} className="mt-2">
              {dashboard.caixas_abertos > 0 ? "Operando" : "Fechados"}
            </Badge>
            <div className="text-xs text-gray-500 mt-1">
              Status dos caixas
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Produtos Mais Vendidos
          </CardTitle>
        </CardHeader>
        <CardContent>
          {dashboard.produtos_mais_vendidos?.length > 0 ? (
            <div className="space-y-3">
              {dashboard.produtos_mais_vendidos.map((produto: any, index: number) => (
                <div key={index} className="flex justify-between items-center p-3 border rounded-lg bg-gray-50">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline" className="font-bold">
                      #{index + 1}
                    </Badge>
                    <div>
                      <div className="font-medium">{produto.nome}</div>
                      <div className="text-sm text-gray-500">{produto.quantidade} vendidos</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-green-600">R$ {toNumber(produto.receita).toFixed(2)}</div>
                    <div className="text-xs text-gray-500">receita</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Package className="h-12 w-12 mx-auto mb-2 text-gray-300" />
              <p>Nenhuma venda registrada ainda</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardPDV;
