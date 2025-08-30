import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  BarChart3, 
  Users, 
  ShoppingCart, 
  DollarSign, 
  Package, 
  Heart, 
  Settings,
  Home,
  Zap,
  ChevronDown,
  ChevronRight,
  Layout,
  Printer,
  Webhook,
  BrainCircuit,
  TrendingUp,
  MessageSquare,
  MapPin,
  CreditCard
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ERPModule {
  id: string;
  name: string;
  icon: React.ReactNode;
  path: string;
  status: 'active' | 'partial' | 'inactive';
  completion: number;
  submodules?: ERPSubmodule[];
}

interface ERPSubmodule {
  id: string;
  name: string;
  path: string;
  status: 'active' | 'partial' | 'inactive';
}

export const ERPNavigation: React.FC = () => {
  const location = useLocation();
  const [expandedModules, setExpandedModules] = useState<string[]>(['core']);

  const modules: ERPModule[] = [
    {
      id: 'dashboard',
      name: 'Dashboard ERP',
      icon: <Home className="h-4 w-4" />,
      path: '/erp/dashboard',
      status: 'active',
      completion: 100
    },
    {
      id: 'core',
      name: 'Core',
      icon: <Settings className="h-4 w-4" />,
      path: '/erp/core',
      status: 'active',
      completion: 90,
      submodules: [
        { id: 'events', name: 'Eventos', path: '/erp/core/events', status: 'active' },
        { id: 'users', name: 'Usuários', path: '/erp/core/users', status: 'active' },
        { id: 'auth', name: 'Autenticação', path: '/erp/core/auth', status: 'active' },
        { id: 'config', name: 'Configurações', path: '/erp/core/config', status: 'partial' }
      ]
    },
    {
      id: 'sales',
      name: 'Vendas',
      icon: <ShoppingCart className="h-4 w-4" />,
      path: '/erp/sales',
      status: 'active',
      completion: 85,
      submodules: [
        { id: 'pdv', name: 'PDV', path: '/erp/sales/pdv', status: 'active' },
        { id: 'orders', name: 'Pedidos', path: '/erp/sales/orders', status: 'active' },
        { id: 'tickets', name: 'Ingressos', path: '/erp/sales/tickets', status: 'partial' },
        { id: 'menu', name: 'Cardápio', path: '/erp/sales/menu', status: 'active' }
      ]
    },
    {
      id: 'financial',
      name: 'Financeiro',
      icon: <DollarSign className="h-4 w-4" />,
      path: '/erp/financial',
      status: 'partial',
      completion: 45,
      submodules: [
        { id: 'payments', name: 'Pagamentos', path: '/erp/financial/payments', status: 'active' },
        { id: 'digital-account', name: 'Conta Digital', path: '/erp/financial/digital-account', status: 'inactive' },
        { id: 'banking', name: 'Bancário', path: '/erp/financial/banking', status: 'inactive' },
        { id: 'billing', name: 'Faturamento', path: '/erp/financial/billing', status: 'partial' },
        { id: 'receivables', name: 'Antecipação', path: '/erp/financial/receivables', status: 'inactive' }
      ]
    },
    {
      id: 'inventory',
      name: 'Estoque',
      icon: <Package className="h-4 w-4" />,
      path: '/erp/inventory',
      status: 'active',
      completion: 85,
      submodules: [
        { id: 'stock', name: 'Controle', path: '/erp/inventory/stock', status: 'active' },
        { id: 'products', name: 'Produtos', path: '/erp/inventory/products', status: 'active' },
        { id: 'movements', name: 'Movimentações', path: '/erp/inventory/movements', status: 'active' },
        { id: 'reports', name: 'Relatórios', path: '/erp/inventory/reports', status: 'active' }
      ]
    },
    {
      id: 'crm',
      name: 'CRM',
      icon: <Users className="h-4 w-4" />,
      path: '/erp/crm',
      status: 'partial',
      completion: 55,
      submodules: [
        { id: 'customers', name: 'Clientes', path: '/erp/crm/customers', status: 'partial' },
        { id: 'loyalty', name: 'Fidelidade', path: '/erp/crm/loyalty', status: 'active' },
        { id: 'marketing', name: 'Marketing', path: '/erp/crm/marketing', status: 'partial' },
        { id: 'satisfaction', name: 'Satisfação', path: '/erp/crm/satisfaction', status: 'inactive' },
        { id: 'analytics', name: 'Analytics', path: '/erp/crm/analytics', status: 'partial' }
      ]
    },
    {
      id: 'operations',
      name: 'Operações',
      icon: <MapPin className="h-4 w-4" />,
      path: '/erp/operations',
      status: 'inactive',
      completion: 20,
      submodules: [
        { id: 'layout', name: 'Layout', path: '/erp/operations/layout', status: 'inactive' },
        { id: 'tables', name: 'Mesas', path: '/erp/operations/tables', status: 'inactive' },
        { id: 'equipment', name: 'Equipamentos', path: '/erp/operations/equipment', status: 'inactive' },
        { id: 'printers', name: 'Impressoras', path: '/erp/operations/printers', status: 'inactive' }
      ]
    },
    {
      id: 'integrations',
      name: 'Integrações',
      icon: <Webhook className="h-4 w-4" />,
      path: '/erp/integrations',
      status: 'active',
      completion: 80,
      submodules: [
        { id: 'apis', name: 'APIs', path: '/erp/integrations/apis', status: 'active' },
        { id: 'whatsapp', name: 'WhatsApp', path: '/erp/integrations/whatsapp', status: 'active' },
        { id: 'n8n', name: 'N8N', path: '/erp/integrations/n8n', status: 'active' },
        { id: 'webhooks', name: 'Webhooks', path: '/erp/integrations/webhooks', status: 'active' }
      ]
    }
  ];

  const toggleModule = (moduleId: string) => {
    setExpandedModules(prev => 
      prev.includes(moduleId) 
        ? prev.filter(id => id !== moduleId)
        : [...prev, moduleId]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'partial': return 'bg-yellow-500';
      case 'inactive': return 'bg-gray-400';
      default: return 'bg-gray-400';
    }
  };

  const isCurrentPath = (path: string) => {
    return location.pathname === path;
  };

  const isModuleActive = (module: ERPModule) => {
    return location.pathname.startsWith(module.path);
  };

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Zap className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">ERP Sistema</h2>
            <p className="text-xs text-gray-500">NovoSistema v2.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-2">
          {modules.map((module) => {
            const isExpanded = expandedModules.includes(module.id);
            const isActive = isModuleActive(module);
            const hasSubmodules = module.submodules && module.submodules.length > 0;

            return (
              <div key={module.id} className="space-y-1">
                {/* Main Module */}
                <div
                  className={cn(
                    'flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors',
                    isActive 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'hover:bg-gray-100 text-gray-700'
                  )}
                  onClick={() => hasSubmodules ? toggleModule(module.id) : window.location.href = module.path}
                >
                  <div className="flex items-center gap-2 flex-1">
                    {module.icon}
                    <span className="font-medium text-sm">{module.name}</span>
                    <div className={`w-2 h-2 rounded-full ${getStatusColor(module.status)}`}></div>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    <Badge variant="outline" className="text-xs px-1 py-0">
                      {module.completion}%
                    </Badge>
                    {hasSubmodules && (
                      isExpanded ? 
                        <ChevronDown className="h-4 w-4" /> : 
                        <ChevronRight className="h-4 w-4" />
                    )}
                  </div>
                </div>

                {/* Submodules */}
                {hasSubmodules && isExpanded && (
                  <div className="ml-6 space-y-1">
                    {module.submodules!.map((submodule) => (
                      <NavLink
                        key={submodule.id}
                        to={submodule.path}
                        className={({ isActive }) =>
                          cn(
                            'flex items-center justify-between p-2 rounded-md text-sm transition-colors',
                            isActive
                              ? 'bg-blue-50 text-blue-600 border-l-2 border-blue-600'
                              : 'text-gray-600 hover:bg-gray-50'
                          )
                        }
                      >
                        <span>{submodule.name}</span>
                        <div className={`w-1.5 h-1.5 rounded-full ${getStatusColor(submodule.status)}`}></div>
                      </NavLink>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </ScrollArea>

      {/* Footer Stats */}
      <div className="p-4 border-t border-gray-200">
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-500">Implementação ERP</span>
            <span className="font-semibold text-gray-900">74%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: '74%' }}></div>
          </div>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Sprint 1 - Em Andamento</span>
            <Badge variant="outline" className="text-xs">
              Ativo
            </Badge>
          </div>
        </div>
      </div>
    </div>
  );
};