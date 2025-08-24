import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTriger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  Users, 
  ShoppingCart, 
  DollarSign, 
  Package, 
  Heart, 
  Settings,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';

interface ModuleStatus {
  id: string;
  name: string;
  status: 'active' | 'partial' | 'inactive';
  completion: number;
  lastUpdate: string;
  icon: React.ReactNode;
  description: string;
}

interface KPIData {
  title: string;
  value: string | number;
  change: string;
  trend: 'up' | 'down' | 'stable';
  icon: React.ReactNode;
}

export const ERPDashboard: React.FC = () => {
  const [modules, setModules] = useState<ModuleStatus[]>([
    {
      id: 'core',
      name: 'Core',
      status: 'active',
      completion: 90,
      lastUpdate: '2 min ago',
      icon: <Settings className="h-5 w-5" />,
      description: 'Dashboard, Eventos, Usuários, Auth'
    },
    {
      id: 'sales',
      name: 'Vendas',
      status: 'active', 
      completion: 85,
      lastUpdate: '5 min ago',
      icon: <ShoppingCart className="h-5 w-5" />,
      description: 'PDV, Pedidos, Ingressos, Produtos'
    },
    {
      id: 'financial',
      name: 'Financeiro',
      status: 'partial',
      completion: 45,
      lastUpdate: '1 hour ago',
      icon: <DollarSign className="h-5 w-5" />,
      description: 'Pagamentos, Bancário, Faturamento'
    },
    {
      id: 'inventory',
      name: 'Estoque',
      status: 'active',
      completion: 85,
      lastUpdate: '10 min ago',
      icon: <Package className="h-5 w-5" />,
      description: 'Produtos, Movimentações, Inventário'
    },
    {
      id: 'crm',
      name: 'CRM',
      status: 'partial',
      completion: 55,
      lastUpdate: '30 min ago',
      icon: <Users className="h-5 w-5" />,
      description: 'Clientes, Fidelidade, Marketing'
    },
    {
      id: 'operations',
      name: 'Operações',
      status: 'inactive',
      completion: 20,
      lastUpdate: '2 days ago',
      icon: <BarChart3 className="h-5 w-5" />,
      description: 'Mesas, Equipamentos, Layout'
    }
  ]);

  const [kpis, setKpis] = useState<KPIData[]>([
    {
      title: 'Receita Hoje',
      value: 'R$ 12.430',
      change: '+12.5%',
      trend: 'up',
      icon: <DollarSign className="h-4 w-4" />
    },
    {
      title: 'Vendas Ativas',
      value: 89,
      change: '+4.2%', 
      trend: 'up',
      icon: <ShoppingCart className="h-4 w-4" />
    },
    {
      title: 'Clientes Online',
      value: 234,
      change: '-2.1%',
      trend: 'down',
      icon: <Users className="h-4 w-4" />
    },
    {
      title: 'Satisfação',
      value: '94%',
      change: '+1.8%',
      trend: 'up',
      icon: <Heart className="h-4 w-4" />
    }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'partial': return 'bg-yellow-500';  
      case 'inactive': return 'bg-gray-400';
      default: return 'bg-gray-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Ativo';
      case 'partial': return 'Parcial';
      case 'inactive': return 'Inativo';
      default: return 'Desconhecido';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'partial': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'inactive': return <AlertCircle className="h-4 w-4 text-gray-400" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Zap className="h-8 w-8 text-blue-600" />
            Sistema ERP - NovoSistema
          </h1>
          <p className="text-gray-600 mt-1">Dashboard Executivo em Tempo Real</p>
        </div>
        <Badge variant="outline" className="px-3 py-1">
          Sprint 1 - Consolidação
        </Badge>
      </div>

      {/* KPIs Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, index) => (
          <Card key={index} className="bg-white shadow-lg hover:shadow-xl transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{kpi.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
                  <div className="flex items-center mt-2">
                    <TrendingUp className={`h-4 w-4 ${kpi.trend === 'up' ? 'text-green-500' : 'text-red-500'}`} />
                    <span className={`text-sm ml-1 ${kpi.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                      {kpi.change}
                    </span>
                  </div>
                </div>
                <div className="p-3 bg-blue-100 rounded-full">
                  {kpi.icon}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content */}
      <Tabs defaultValue="modules" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 bg-white shadow-sm">
          <TabsTriger value="modules">Módulos ERP</TabsTriger>
          <TabsTriger value="analytics">Analytics</TabsTriger>
          <TabsTriger value="settings">Configurações</TabsTriger>
        </TabsList>

        {/* Módulos ERP */}
        <TabsContent value="modules">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.map((module) => (
              <Card key={module.id} className="bg-white shadow-lg hover:shadow-xl transition-all cursor-pointer group">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {module.icon}
                      <CardTitle className="text-lg">{module.name}</CardTitle>
                    </div>
                    {getStatusIcon(module.status)}
                  </div>
                  <CardDescription className="text-sm">
                    {module.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {/* Status */}
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Status:</span>
                      <Badge variant="outline" className="flex items-center gap-1">
                        <div className={`w-2 h-2 rounded-full ${getStatusColor(module.status)}`}></div>
                        {getStatusText(module.status)}
                      </Badge>
                    </div>

                    {/* Progress */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span>Implementação</span>
                        <span>{module.completion}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all ${
                            module.completion >= 80 ? 'bg-green-500' : 
                            module.completion >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${module.completion}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Last Update */}
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Última atualização:</span>
                      <span>{module.lastUpdate}</span>
                    </div>

                    {/* Action Button */}
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="w-full group-hover:bg-blue-50"
                      onClick={() => {
                        // Navigate to module
                        window.location.href = `/erp/${module.id}`;
                      }}
                    >
                      Acessar Módulo
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Analytics */}
        <TabsContent value="analytics">
          <Card className="bg-white shadow-lg">
            <CardHeader>
              <CardTitle>Analytics em Tempo Real</CardTitle>
              <CardDescription>
                Métricas e insights do sistema ERP
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Analytics Avançado
                </h3>
                <p className="text-gray-600 mb-4">
                  Dashboards interativos e relatórios executivos serão implementados no Sprint 2
                </p>
                <Badge variant="outline">Em Desenvolvimento</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings */}
        <TabsContent value="settings">
          <Card className="bg-white shadow-lg">
            <CardHeader>
              <CardTitle>Configurações do Sistema</CardTitle>
              <CardDescription>
                Configurações globais e permissões do ERP
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Settings className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Configurações Avançadas
                </h3>
                <p className="text-gray-600 mb-4">
                  Sistema de permissões granulares e configurações será implementado no Sprint 1
                </p>
                <Badge variant="outline">Sprint 1 - Em Andamento</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Footer Stats */}
      <Card className="bg-white shadow-lg">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-green-600">74%</p>
              <p className="text-sm text-gray-600">ERP Implementado</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">38</p>
              <p className="text-sm text-gray-600">Routers Ativos</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">6</p>
              <p className="text-sm text-gray-600">Módulos ERP</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-600">99.9%</p>
              <p className="text-sm text-gray-600">Uptime</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};