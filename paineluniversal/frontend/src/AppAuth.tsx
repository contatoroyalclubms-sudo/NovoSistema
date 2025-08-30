import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider, useAuth } from './components/LoginScreen'
import { ProtectedRoute } from './components/AuthComponents'
import LoginScreen from './components/LoginScreen'
import MainLayout from './components/layout/MainLayout'
import DashboardPage from './pages/DashboardPage'
import EventosPage from './pages/EventosPage'
import PDVPage from './pages/PDVPage'
import RelatoriosPage from './pages/RelatoriosPage'
import ConfiguracoesPage from './pages/ConfiguracoesPage'
import AnalyticsPage from './pages/AnalyticsPage'
import LogsPage from './pages/LogsPage'
import QRCheckInPage from './pages/QRCheckInPage'
import './App.css'

// Configuração do React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
      refetchOnWindowFocus: false,
    },
  },
})

// Componente principal de rotas com autenticação
const AppRoutes: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f8fafc'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '32px',
          boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid #e5e7eb',
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }} />
          <p style={{ color: '#64748b', margin: 0 }}>
            Carregando Sistema Universal...
          </p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Rota de login */}
      <Route 
        path="/login" 
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginScreen />
        } 
      />

      {/* Rotas protegidas */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <DashboardPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/eventos" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <EventosPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/pdv" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <PDVPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/relatorios" 
        element={
          <ProtectedRoute requiredRole={['admin', 'manager']}>
            <MainLayout>
              <RelatoriosPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/analytics" 
        element={
          <ProtectedRoute requiredRole={['admin', 'manager']}>
            <MainLayout>
              <AnalyticsPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/logs" 
        element={
          <ProtectedRoute requiredRole={['admin']}>
            <MainLayout>
              <LogsPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/qr-checkin" 
        element={
          <ProtectedRoute>
            <MainLayout>
              <QRCheckInPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/configuracoes" 
        element={
          <ProtectedRoute requiredRole={['admin', 'manager']}>
            <MainLayout>
              <ConfiguracoesPage />
            </MainLayout>
          </ProtectedRoute>
        } 
      />

      {/* Redirecionamentos */}
      <Route 
        path="/" 
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
        } 
      />
      
      {/* Rota 404 */}
      <Route 
        path="*" 
        element={
          <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f8fafc'
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '32px',
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
              textAlign: 'center',
              maxWidth: '400px'
            }}>
              <h1 style={{
                fontSize: '48px',
                margin: '0 0 16px 0'
              }}>
                404
              </h1>
              <h2 style={{
                fontSize: '20px',
                fontWeight: 'bold',
                color: '#1e293b',
                margin: '0 0 8px 0'
              }}>
                Página não encontrada
              </h2>
              <p style={{
                color: '#64748b',
                margin: '0 0 24px 0'
              }}>
                A página que você está procurando não existe.
              </p>
              <button
                onClick={() => window.history.back()}
                style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '12px 24px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                Voltar
              </button>
            </div>
          </div>
        } 
      />
    </Routes>
  );
};

// Componente principal da aplicação
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthProvider>
          <div style={{
            minHeight: '100vh',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
          }}>
            <AppRoutes />
          </div>
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
