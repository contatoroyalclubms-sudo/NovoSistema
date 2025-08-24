import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ERPLayout } from '@/layouts/ERPLayout';
import { ERPDashboard } from '@/components/erp/ERPDashboard';

// Lazy load dos componentes ERP para performance
const CoreModule = React.lazy(() => import('@/pages/erp/CoreModule'));
const SalesModule = React.lazy(() => import('@/pages/erp/SalesModule'));
const FinancialModule = React.lazy(() => import('@/pages/erp/FinancialModule'));
const InventoryModule = React.lazy(() => import('@/pages/erp/InventoryModule'));
const CRMModule = React.lazy(() => import('@/pages/erp/CRMModule'));
const OperationsModule = React.lazy(() => import('@/pages/erp/OperationsModule'));
const IntegrationsModule = React.lazy(() => import('@/pages/erp/IntegrationsModule'));

// Componente de Loading
const LoadingComponent = () => (
  <div className="flex items-center justify-center h-64">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
);

// Wrapper com Suspense para lazy loading
const LazyWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <React.Suspense fallback={<LoadingComponent />}>
    {children}
  </React.Suspense>
);

export const ERPRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/erp" element={<ERPLayout />}>
        {/* Dashboard Principal */}
        <Route index element={<Navigate to="/erp/dashboard" replace />} />
        <Route path="dashboard" element={<ERPDashboard />} />

        {/* Módulo Core */}
        <Route path="core/*" element={
          <LazyWrapper>
            <CoreModule />
          </LazyWrapper>
        } />

        {/* Módulo Sales */}
        <Route path="sales/*" element={
          <LazyWrapper>
            <SalesModule />
          </LazyWrapper>
        } />

        {/* Módulo Financial */}
        <Route path="financial/*" element={
          <LazyWrapper>
            <FinancialModule />
          </LazyWrapper>
        } />

        {/* Módulo Inventory */}
        <Route path="inventory/*" element={
          <LazyWrapper>
            <InventoryModule />
          </LazyWrapper>
        } />

        {/* Módulo CRM */}
        <Route path="crm/*" element={
          <LazyWrapper>
            <CRMModule />
          </LazyWrapper>
        } />

        {/* Módulo Operations */}
        <Route path="operations/*" element={
          <LazyWrapper>
            <OperationsModule />
          </LazyWrapper>
        } />

        {/* Módulo Integrations */}
        <Route path="integrations/*" element={
          <LazyWrapper>
            <IntegrationsModule />
          </LazyWrapper>
        } />
      </Route>
    </Routes>
  );
};