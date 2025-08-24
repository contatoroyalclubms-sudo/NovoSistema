import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Settings, Users, Shield, Cog, CheckCircle, Clock } from 'lucide-react';

const CoreDashboard = () => (
  <div className="p-6 space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Módulo Core</h1>
        <p className="text-gray-600">Funcionalidades principais do sistema</p>
      </div>
      <Badge variant="outline" className="bg-green-50 text-green-700">
        90% Implementado
      </Badge>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Gestão de Eventos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-sm text-gray-600">
              Sistema completo de criação e gestão de eventos com templates personalizáveis.
            </p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm">Implementado</span>
              </div>
              <Button size="sm" variant="outline">
                Acessar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Sistema de Usuários
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-sm text-gray-600">
              Controle de usuários com permissões granulares e auditoria completa.
            </p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm">Implementado</span>
              </div>
              <Button size="sm" variant="outline">
                Acessar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cog className="h-5 w-5" />
            Autenticação
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-sm text-gray-600">
              Sistema robusto de autenticação JWT com middleware de segurança.
            </p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm">Implementado</span>
              </div>
              <Button size="sm" variant="outline">
                Configurar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Configurações
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-sm text-gray-600">
              Configurações avançadas do sistema e personalizações globais.
            </p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-yellow-500" />
                <span className="text-sm">Em desenvolvimento</span>
              </div>
              <Button size="sm" variant="outline" disabled>
                Em breve
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
);

const CoreModule = () => {
  return (
    <Routes>
      <Route index element={<CoreDashboard />} />
      <Route path="events" element={<div className="p-6">Gestão de Eventos - Em construção...</div>} />
      <Route path="users" element={<div className="p-6">Gestão de Usuários - Em construção...</div>} />
      <Route path="auth" element={<div className="p-6">Configurações de Autenticação - Em construção...</div>} />
      <Route path="config" element={<div className="p-6">Configurações do Sistema - Em construção...</div>} />
      <Route path="*" element={<Navigate to="/erp/core" replace />} />
    </Routes>
  );
};

export default CoreModule;