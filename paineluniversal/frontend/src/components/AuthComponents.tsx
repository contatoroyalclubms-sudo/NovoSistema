import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './LoginScreen';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string[];
  fallbackPath?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole = [],
  fallbackPath = '/login'
}) => {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();

  // Mostrar loading enquanto verifica autenticação
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
            Verificando autenticação...
          </p>
        </div>
      </div>
    );
  }

  // Não autenticado - redirecionar para login
  if (!isAuthenticated || !user) {
    return <Navigate to={fallbackPath} state={{ from: location }} replace />;
  }

  // Verificar roles se especificados
  if (requiredRole.length > 0 && !requiredRole.includes(user.role)) {
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
          textAlign: 'center',
          maxWidth: '400px'
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            backgroundColor: '#fef2f2',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <span style={{ fontSize: '24px' }}>🚫</span>
          </div>
          <h2 style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#1e293b',
            margin: '0 0 8px 0'
          }}>
            Acesso Negado
          </h2>
          <p style={{
            color: '#64748b',
            margin: '0 0 24px 0'
          }}>
            Você não tem permissão para acessar esta página.
          </p>
          <p style={{
            fontSize: '14px',
            color: '#9ca3af',
            margin: 0
          }}>
            Role necessária: {requiredRole.join(', ')}<br />
            Sua role atual: {user.role}
          </p>
          <button
            onClick={() => window.history.back()}
            style={{
              marginTop: '16px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '8px 16px',
              cursor: 'pointer'
            }}
          >
            Voltar
          </button>
        </div>
      </div>
    );
  }

  // Autenticado e autorizado - mostrar conteúdo
  return <>{children}</>;
};

interface UserMenuProps {
  user: {
    username: string;
    full_name: string;
    role: string;
    email: string;
  };
  onLogout: () => void;
}

export const UserMenu: React.FC<UserMenuProps> = ({ user, onLogout }) => {
  const [isOpen, setIsOpen] = React.useState(false);

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return '#dc2626';
      case 'manager': return '#ea580c';
      case 'user': return '#059669';
      default: return '#6b7280';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin': return 'Administrador';
      case 'manager': return 'Gerente';
      case 'user': return 'Usuário';
      case 'guest': return 'Visitante';
      default: return role;
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '8px 12px',
          cursor: 'pointer',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}
      >
        <div style={{
          width: '32px',
          height: '32px',
          backgroundColor: '#3b82f6',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '14px',
          fontWeight: 'bold'
        }}>
          {user.full_name.charAt(0).toUpperCase()}
        </div>
        <div style={{ textAlign: 'left' }}>
          <p style={{
            margin: 0,
            fontSize: '14px',
            fontWeight: '500',
            color: '#1f2937'
          }}>
            {user.full_name}
          </p>
          <p style={{
            margin: 0,
            fontSize: '12px',
            color: getRoleColor(user.role),
            fontWeight: '500'
          }}>
            {getRoleLabel(user.role)}
          </p>
        </div>
        <span style={{
          fontSize: '12px',
          color: '#6b7280',
          transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform 0.2s'
        }}>
          ▼
        </span>
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: 0,
          marginTop: '4px',
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          boxShadow: '0 10px 15px rgba(0, 0, 0, 0.1)',
          minWidth: '200px',
          zIndex: 50
        }}>
          <div style={{ padding: '12px', borderBottom: '1px solid #f3f4f6' }}>
            <p style={{
              margin: 0,
              fontSize: '14px',
              fontWeight: '500',
              color: '#1f2937'
            }}>
              {user.full_name}
            </p>
            <p style={{
              margin: 0,
              fontSize: '12px',
              color: '#6b7280'
            }}>
              @{user.username}
            </p>
            <p style={{
              margin: 0,
              fontSize: '12px',
              color: '#6b7280'
            }}>
              {user.email}
            </p>
          </div>
          
          <div style={{ padding: '8px' }}>
            <button
              onClick={() => {
                setIsOpen(false);
                onLogout();
              }}
              style={{
                width: '100%',
                textAlign: 'left',
                padding: '8px 12px',
                backgroundColor: 'transparent',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px',
                color: '#dc2626'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fef2f2'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              🚪 Sair
            </button>
          </div>
        </div>
      )}

      {/* Overlay para fechar menu ao clicar fora */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 40
          }}
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default ProtectedRoute;
