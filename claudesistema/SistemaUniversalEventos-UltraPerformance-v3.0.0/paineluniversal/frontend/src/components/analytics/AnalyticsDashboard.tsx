import React, { useState, useEffect } from 'react';
import './AnalyticsDashboard.css';

interface DashboardMetrics {
  periodo: string;
  data_inicio: string;
  data_fim: string;
  eventos: {
    total: number;
    ativos: number;
    capacidade_total: number;
  };
  checkins: {
    total: number;
    participantes_unicos: number;
  };
  vendas: {
    total: number;
    receita: number;
    ticket_medio: number;
  };
  whatsapp: {
    total_mensagens: number;
    entregues: number;
    lidas: number;
    taxa_entrega: number;
    taxa_leitura: number;
  };
}

interface RealTimeStats {
  timestamp: string;
  checkins_ultima_hora: number;
  vendas_ultima_hora: number;
  receita_ultima_hora: number;
  mensagens_ultima_hora: number;
  eventos_ativos_agora: number;
}

const AnalyticsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [realTimeStats, setRealTimeStats] = useState<RealTimeStats | null>(null);
  const [periodo, setPeriodo] = useState('7d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = 'http://localhost:8003/api';

  // Buscar métricas do dashboard
  const fetchMetrics = async (selectedPeriodo: string = periodo) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/analytics/dashboard-metrics?periodo=${selectedPeriodo}`);
      if (!response.ok) throw new Error('Erro ao buscar métricas');
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  // Buscar estatísticas em tempo real
  const fetchRealTimeStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/analytics/real-time-stats`);
      if (!response.ok) throw new Error('Erro ao buscar estatísticas em tempo real');
      const data = await response.json();
      setRealTimeStats(data);
    } catch (err) {
      console.error('Erro ao buscar stats em tempo real:', err);
    }
  };

  useEffect(() => {
    fetchMetrics();
    fetchRealTimeStats();

    // Atualizar estatísticas em tempo real a cada 30 segundos
    const interval = setInterval(fetchRealTimeStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const handlePeriodoChange = (newPeriodo: string) => {
    setPeriodo(newPeriodo);
    fetchMetrics(newPeriodo);
  };

  if (loading) {
    return (
      <div className="analytics-dashboard">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Carregando analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-dashboard">
        <div className="error-message">
          <h3>Erro ao carregar analytics</h3>
          <p>{error}</p>
          <button onClick={() => fetchMetrics()} className="retry-button">
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h2>📊 Dashboard Analytics</h2>
        <div className="period-selector">
          <label>Período:</label>
          <select 
            value={periodo} 
            onChange={(e) => handlePeriodoChange(e.target.value)}
            className="period-select"
          >
            <option value="1d">Último dia</option>
            <option value="7d">Últimos 7 dias</option>
            <option value="30d">Últimos 30 dias</option>
            <option value="90d">Últimos 90 dias</option>
          </select>
        </div>
      </div>

      {/* Estatísticas em tempo real */}
      {realTimeStats && (
        <div className="real-time-stats">
          <h3>🕐 Tempo Real (Última Hora)</h3>
          <div className="stats-grid">
            <div className="stat-card real-time">
              <div className="stat-value">{realTimeStats.checkins_ultima_hora}</div>
              <div className="stat-label">Check-ins</div>
            </div>
            <div className="stat-card real-time">
              <div className="stat-value">{realTimeStats.vendas_ultima_hora}</div>
              <div className="stat-label">Vendas</div>
            </div>
            <div className="stat-card real-time">
              <div className="stat-value">R$ {realTimeStats.receita_ultima_hora.toFixed(2)}</div>
              <div className="stat-label">Receita</div>
            </div>
            <div className="stat-card real-time">
              <div className="stat-value">{realTimeStats.mensagens_ultima_hora}</div>
              <div className="stat-label">Mensagens</div>
            </div>
            <div className="stat-card real-time">
              <div className="stat-value">{realTimeStats.eventos_ativos_agora}</div>
              <div className="stat-label">Eventos Ativos</div>
            </div>
          </div>
        </div>
      )}

      {/* Métricas principais */}
      {metrics && (
        <>
          <div className="metrics-overview">
            <h3>📈 Visão Geral ({metrics.data_inicio} a {metrics.data_fim})</h3>
            <div className="stats-grid">
              <div className="stat-card events">
                <div className="stat-value">{metrics.eventos.total}</div>
                <div className="stat-label">Eventos Total</div>
                <div className="stat-detail">{metrics.eventos.ativos} ativos</div>
              </div>
              <div className="stat-card checkins">
                <div className="stat-value">{metrics.checkins.total}</div>
                <div className="stat-label">Check-ins</div>
                <div className="stat-detail">{metrics.checkins.participantes_unicos} únicos</div>
              </div>
              <div className="stat-card sales">
                <div className="stat-value">R$ {metrics.vendas.receita.toFixed(2)}</div>
                <div className="stat-label">Receita Total</div>
                <div className="stat-detail">{metrics.vendas.total} vendas</div>
              </div>
              <div className="stat-card whatsapp">
                <div className="stat-value">{metrics.whatsapp.total_mensagens}</div>
                <div className="stat-label">Mensagens WhatsApp</div>
                <div className="stat-detail">{metrics.whatsapp.taxa_entrega.toFixed(1)}% entrega</div>
              </div>
            </div>
          </div>

          {/* Gráficos - Em desenvolvimento */}
          <div className="charts-section">
            <div className="chart-container">
              <h4>Atividades por Tipo</h4>
              <div className="chart-placeholder">
                <div className="chart-item">
                  <span className="chart-label">Vendas</span>
                  <span className="chart-value">{metrics.vendas.total}</span>
                </div>
                <div className="chart-item">
                  <span className="chart-label">Check-ins</span>
                  <span className="chart-value">{metrics.checkins.total}</span>
                </div>
                <div className="chart-item">
                  <span className="chart-label">Mensagens</span>
                  <span className="chart-value">{metrics.whatsapp.total_mensagens}</span>
                </div>
              </div>
            </div>

            <div className="chart-container">
              <h4>Taxa de Entrega WhatsApp</h4>
              <div className="chart-placeholder">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{width: `${metrics.whatsapp.taxa_entrega}%`}}
                  ></div>
                </div>
                <div className="progress-text">
                  {metrics.whatsapp.taxa_entrega.toFixed(1)}% de entrega
                </div>
                <div className="progress-details">
                  {metrics.whatsapp.entregues} de {metrics.whatsapp.total_mensagens} mensagens
                </div>
              </div>
            </div>
          </div>

          {/* Métricas detalhadas */}
          <div className="detailed-metrics">
            <div className="metric-section">
              <h4>🎫 Eventos</h4>
              <div className="metric-details">
                <div>Total: <strong>{metrics.eventos.total}</strong></div>
                <div>Ativos: <strong>{metrics.eventos.ativos}</strong></div>
                <div>Capacidade Total: <strong>{metrics.eventos.capacidade_total}</strong></div>
              </div>
            </div>

            <div className="metric-section">
              <h4>💰 Vendas</h4>
              <div className="metric-details">
                <div>Total de Vendas: <strong>{metrics.vendas.total}</strong></div>
                <div>Receita: <strong>R$ {metrics.vendas.receita.toFixed(2)}</strong></div>
                <div>Ticket Médio: <strong>R$ {metrics.vendas.ticket_medio.toFixed(2)}</strong></div>
              </div>
            </div>

            <div className="metric-section">
              <h4>📱 WhatsApp</h4>
              <div className="metric-details">
                <div>Mensagens: <strong>{metrics.whatsapp.total_mensagens}</strong></div>
                <div>Entregues: <strong>{metrics.whatsapp.entregues}</strong></div>
                <div>Lidas: <strong>{metrics.whatsapp.lidas}</strong></div>
                <div>Taxa Entrega: <strong>{metrics.whatsapp.taxa_entrega.toFixed(1)}%</strong></div>
                <div>Taxa Leitura: <strong>{metrics.whatsapp.taxa_leitura.toFixed(1)}%</strong></div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
