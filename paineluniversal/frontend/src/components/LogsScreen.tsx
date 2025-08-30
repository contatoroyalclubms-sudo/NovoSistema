import React, { useState, useEffect } from 'react';

interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  logger: string;
  message: string;
  module?: string;
  function?: string;
  line?: number;
  extras?: any;
}

interface LogStats {
  total_logs: number;
  new_alerts: number;
  today_logs: number;
  error_logs: number;
  warning_logs: number;
  memory_usage_mb: number;
  log_file_size_mb: number;
}

interface Alert {
  id: string;
  level: string;
  message: string;
  timestamp: string;
  status: string;
  type: string;
}

interface LogsScreenProps {
  isAdmin?: boolean;
}

const LogsScreen: React.FC<LogsScreenProps> = ({ isAdmin = false }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<LogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedLevel, setSelectedLevel] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(10); // segundos

  const logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];
  const levelColors = {
    DEBUG: '#6c757d',
    INFO: '#0dcaf0',
    WARNING: '#ffc107',
    ERROR: '#dc3545',
    CRITICAL: '#6f42c1'
  };

  // Função para buscar dados do dashboard
  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/logs/dashboard');
      const result = await response.json();

      if (result.success) {
        setStats(result.data.stats);
        setLogs(result.data.recent_logs);
        setAlerts(result.data.new_alerts);
      }
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  // Função para buscar logs com filtros
  const fetchLogs = async () => {
    try {
      let url = '/api/logs/recent?limit=100';
      if (selectedLevel) {
        url += `&level=${selectedLevel}`;
      }

      const response = await fetch(url);
      const result = await response.json();

      if (result.success) {
        setLogs(result.data);
      }
    } catch (error) {
      console.error('Erro ao buscar logs:', error);
    }
  };

  // Função para buscar logs por palavra-chave
  const searchLogs = async () => {
    if (!searchQuery.trim()) {
      fetchLogs();
      return;
    }

    try {
      const response = await fetch(`/api/logs/search?query=${encodeURIComponent(searchQuery)}&limit=100`);
      const result = await response.json();

      if (result.success) {
        setLogs(result.data);
      }
    } catch (error) {
      console.error('Erro na busca:', error);
    }
  };

  // Função para reconhecer alertas
  const acknowledgeAlert = async (alertId: string) => {
    try {
      const response = await fetch('/api/logs/alerts/acknowledge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ alert_id: alertId }),
      });

      const result = await response.json();

      if (result.success) {
        setAlerts(alerts.filter(alert => alert.id !== alertId));
      }
    } catch (error) {
      console.error('Erro ao reconhecer alerta:', error);
    }
  };

  // Função para gerar logs de teste (apenas admin)
  const generateTestLogs = async () => {
    try {
      const response = await fetch('/api/logs/test', { method: 'POST' });
      const result = await response.json();

      if (result.success) {
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Erro ao gerar logs de teste:', error);
    }
  };

  // Função para executar limpeza de logs antigos
  const cleanupOldLogs = async () => {
    try {
      const response = await fetch('/api/logs/cleanup', { method: 'POST' });
      const result = await response.json();

      if (result.success) {
        alert('Limpeza de logs antigos iniciada em background');
      }
    } catch (error) {
      console.error('Erro na limpeza:', error);
    }
  };

  // Função para formatar timestamp
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };

  // Função para obter classe CSS do nível
  const getLevelClass = (level: string) => {
    return `log-level log-level-${level.toLowerCase()}`;
  };

  // Effects
  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    if (selectedLevel || searchQuery) {
      const timer = setTimeout(() => {
        if (searchQuery) {
          searchLogs();
        } else {
          fetchLogs();
        }
      }, 500);

      return () => clearTimeout(timer);
    } else {
      fetchLogs();
    }
  }, [selectedLevel, searchQuery]);

  // Auto-refresh
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchDashboardData, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  if (loading) {
    return (
      <div className="logs-screen" style={{ padding: '20px', background: '#f8f9fa', minHeight: '100vh' }}>
        <div className="loading" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '400px', color: '#666' }}>
          <div className="spinner" style={{
            width: '40px',
            height: '40px',
            border: '4px solid #e3e3e3',
            borderTop: '4px solid #007bff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            marginBottom: '15px'
          }}></div>
          <p>Carregando sistema de logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="logs-screen" style={{ padding: '20px', background: '#f8f9fa', minHeight: '100vh' }}>
      <div className="logs-header" style={{ marginBottom: '20px' }}>
        <h2 style={{ color: '#333', marginBottom: '20px', fontSize: '24px', fontWeight: 600 }}>
          Sistema de Logs Avançado
        </h2>
        
        {/* Estatísticas */}
        {stats && (
          <div className="stats-grid" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '15px',
            marginBottom: '20px'
          }}>
            <div className="stat-card" style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              textAlign: 'center',
              borderLeft: '4px solid #0dcaf0'
            }}>
              <div className="stat-value" style={{ fontSize: '24px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                {stats.total_logs}
              </div>
              <div className="stat-label" style={{ fontSize: '14px', color: '#666', textTransform: 'uppercase', fontWeight: 500 }}>
                Total de Logs
              </div>
            </div>
            <div className="stat-card" style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              textAlign: 'center',
              borderLeft: '4px solid #ffc107'
            }}>
              <div className="stat-value" style={{ fontSize: '24px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                {stats.new_alerts}
              </div>
              <div className="stat-label" style={{ fontSize: '14px', color: '#666', textTransform: 'uppercase', fontWeight: 500 }}>
                Novos Alertas
              </div>
            </div>
            <div className="stat-card" style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              textAlign: 'center',
              borderLeft: '4px solid #0dcaf0'
            }}>
              <div className="stat-value" style={{ fontSize: '24px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                {stats.today_logs}
              </div>
              <div className="stat-label" style={{ fontSize: '14px', color: '#666', textTransform: 'uppercase', fontWeight: 500 }}>
                Logs Hoje
              </div>
            </div>
            <div className="stat-card" style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              textAlign: 'center',
              borderLeft: '4px solid #dc3545'
            }}>
              <div className="stat-value" style={{ fontSize: '24px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                {stats.error_logs}
              </div>
              <div className="stat-label" style={{ fontSize: '14px', color: '#666', textTransform: 'uppercase', fontWeight: 500 }}>
                Erros
              </div>
            </div>
          </div>
        )}

        {/* Alertas */}
        {alerts.length > 0 && (
          <div className="alerts-section" style={{
            background: 'white',
            padding: '20px',
            borderRadius: '8px',
            marginBottom: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ color: '#dc3545', marginBottom: '15px', fontSize: '18px' }}>
              Alertas Críticos ({alerts.length})
            </h3>
            <div className="alerts-list" style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {alerts.map(alert => (
                <div key={alert.id} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px',
                  marginBottom: '10px',
                  borderRadius: '6px',
                  borderLeft: '4px solid #dc3545',
                  background: '#fdf2f2'
                }}>
                  <div className="alert-content" style={{ flex: 1 }}>
                    <div className="alert-level" style={{
                      fontWeight: 'bold',
                      fontSize: '12px',
                      textTransform: 'uppercase',
                      marginBottom: '4px'
                    }}>
                      {alert.level}
                    </div>
                    <div className="alert-message" style={{ color: '#333', marginBottom: '4px' }}>
                      {alert.message}
                    </div>
                    <div className="alert-time" style={{ fontSize: '12px', color: '#666' }}>
                      {formatTimestamp(alert.timestamp)}
                    </div>
                  </div>
                  <button 
                    style={{
                      background: '#28a745',
                      color: 'white',
                      border: 'none',
                      padding: '6px 12px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                    onClick={() => acknowledgeAlert(alert.id)}
                  >
                    Reconhecer
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Controles */}
      <div className="logs-controls" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'white',
        padding: '15px 20px',
        borderRadius: '8px',
        marginBottom: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        flexWrap: 'wrap',
        gap: '15px'
      }}>
        <div className="filters" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <select 
            value={selectedLevel} 
            onChange={(e) => setSelectedLevel(e.target.value)}
            style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '14px' }}
          >
            <option value="">Todos os Níveis</option>
            {logLevels.map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Buscar nos logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '14px', minWidth: '200px' }}
          />
        </div>

        <div className="refresh-controls" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '14px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>

          <select 
            value={refreshInterval} 
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            disabled={!autoRefresh}
            style={{ padding: '8px 12px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '14px' }}
          >
            <option value={5}>5s</option>
            <option value={10}>10s</option>
            <option value={30}>30s</option>
            <option value={60}>1min</option>
          </select>

          <button onClick={fetchDashboardData} style={{
            background: '#007bff',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px'
          }}>
            Atualizar
          </button>
        </div>

        {isAdmin && (
          <div className="admin-controls" style={{ display: 'flex', gap: '10px' }}>
            <button onClick={generateTestLogs} style={{
              background: '#17a2b8',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}>
              Gerar Logs de Teste
            </button>
            <button onClick={cleanupOldLogs} style={{
              background: '#ffc107',
              color: '#333',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}>
              Limpar Logs Antigos
            </button>
          </div>
        )}
      </div>

      {/* Lista de Logs */}
      <div className="logs-container" style={{
        background: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        height: '600px',
        overflow: 'hidden'
      }}>
        <div className="logs-list" style={{ height: '100%', overflowY: 'auto', padding: '10px' }}>
          {logs.map(log => (
            <div key={log.id} style={{
              display: 'grid',
              gridTemplateColumns: '150px 80px 120px 1fr',
              gap: '10px',
              padding: '8px 0',
              borderBottom: '1px solid #eee',
              alignItems: 'start',
              fontSize: '13px'
            }}>
              <div style={{ color: '#666', fontFamily: 'monospace' }}>
                {formatTimestamp(log.timestamp)}
              </div>
              <div style={{
                fontWeight: 'bold',
                textAlign: 'center',
                padding: '2px 6px',
                borderRadius: '3px',
                fontSize: '11px',
                textTransform: 'uppercase',
                background: levelColors[log.level as keyof typeof levelColors],
                color: log.level === 'WARNING' ? '#333' : 'white'
              }}>
                {log.level}
              </div>
              <div style={{ color: '#495057', fontFamily: 'monospace', fontSize: '12px' }}>
                {log.logger}
              </div>
              <div style={{ color: '#333', wordBreak: 'break-word' }}>
                {log.message}
              </div>
              {log.extras && (
                <div style={{
                  gridColumn: '1 / -1',
                  marginTop: '5px',
                  padding: '10px',
                  background: '#f8f9fa',
                  borderRadius: '4px',
                  borderLeft: '3px solid #007bff'
                }}>
                  <pre style={{
                    margin: 0,
                    fontSize: '11px',
                    color: '#495057',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}>
                    {JSON.stringify(log.extras, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>

        {logs.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            <p>Nenhum log encontrado com os filtros aplicados.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LogsScreen;
