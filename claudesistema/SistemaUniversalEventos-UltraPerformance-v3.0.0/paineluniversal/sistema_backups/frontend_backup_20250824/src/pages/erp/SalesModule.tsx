import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ShoppingCart, Package, Ticket, Menu, CheckCircle } from 'lucide-react';

const SalesModule = () => {
  return (
    <Routes>
      <Route index element={
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Módulo Vendas</h1>
              <p className="text-gray-600">PDV, Pedidos, Ingressos e Produtos</p>
            </div>
            <Badge variant="outline" className="bg-green-50 text-green-700">
              85% Implementado
            </Badge>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShoppingCart className="h-5 w-5" />
                  PDV Ultra-moderno
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <p className="text-sm text-gray-600">
                    Sistema PDV completo com interface otimizada e múltiplas formas de pagamento.
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Implementado</span>
                    </div>
                    <Button size="sm" variant="outline">
                      Acessar PDV
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      } />
      <Route path="*" element={<Navigate to="/erp/sales" replace />} />
    </Routes>
  );
};

export default SalesModule;