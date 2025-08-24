import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  roles?: string[];
  permissions?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  roles,
  permissions 
}) => {
  const { isAuthenticated, isLoading, user, hasRole, hasPermission } = useAuth();
  const location = useLocation();

  // Mostra loading enquanto verifica autenticação
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  // Se não autenticado, redireciona para login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Verifica se tem os roles necessários
  if (roles && !hasRole(roles)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-2">Acesso Negado</h2>
          <p className="text-gray-600">Você não tem permissão para acessar esta página.</p>
          <p className="text-sm text-gray-500 mt-2">
            Roles necessários: {roles.join(', ')}
          </p>
        </div>
      </div>
    );
  }

  // Verifica se tem as permissões necessárias
  if (permissions && !permissions.every(permission => hasPermission(permission))) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-2">Acesso Negado</h2>
          <p className="text-gray-600">Você não tem as permissões necessárias para acessar esta página.</p>
          <p className="text-sm text-gray-500 mt-2">
            Permissões necessárias: {permissions.join(', ')}
          </p>
        </div>
      </div>
    );
  }

  // Se passou por todas as verificações, renderiza o componente
  return <>{children}</>;
};
