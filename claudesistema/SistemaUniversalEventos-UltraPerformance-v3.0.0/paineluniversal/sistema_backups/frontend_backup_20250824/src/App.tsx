import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import { AuthProvider } from '@/contexts/AuthContext';
import { ERPRoutes } from '@/routes/ERPRoutes';

// Import existing components (mantendo compatibilidade)
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { EventosPage } from '@/pages/EventosPage';
import { PDVPage } from '@/pages/PDVPage';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Rota de Login */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Redirect raiz para ERP Dashboard */}
            <Route path="/" element={<Navigate to="/erp/dashboard" replace />} />
            
            {/* Rotas ERP (Nova estrutura modular) */}
            <Route path="/erp/*" element={
              <ProtectedRoute>
                <ERPRoutes />
              </ProtectedRoute>
            } />
            
            {/* Rotas Legacy (mantidas para compatibilidade) */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } />
            
            <Route path="/eventos" element={
              <ProtectedRoute>
                <EventosPage />
              </ProtectedRoute>
            } />
            
            <Route path="/pdv" element={
              <ProtectedRoute>
                <PDVPage />
              </ProtectedRoute>
            } />
            
            {/* Redirect para rotas não encontradas */}
            <Route path="*" element={<Navigate to="/erp/dashboard" replace />} />
          </Routes>
          
          {/* Toast notifications */}
          <Toaster position="top-right" />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;