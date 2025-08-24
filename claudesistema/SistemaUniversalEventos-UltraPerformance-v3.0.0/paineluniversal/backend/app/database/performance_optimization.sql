-- Database Performance Optimization - Sprint 5
-- Sistema Universal de Gestão de Eventos
-- 
-- This file contains:
-- - Performance indexes for faster queries
-- - Materialized views for analytics
-- - Partitioning strategies
-- - Query optimization hints
-- - Database statistics updates

-- ================================
-- PERFORMANCE INDEXES
-- ================================

-- Eventos table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_status_data_inicio 
ON eventos (status, data_inicio) 
WHERE status IN ('ativo', 'planejamento');

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_empresa_status 
ON eventos (empresa_id, status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_created_at_desc 
ON eventos (created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_data_inicio_fim 
ON eventos (data_inicio, data_fim);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_tipo_empresa 
ON eventos (tipo_evento, empresa_id);

-- Usuarios table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuarios_empresa_tipo 
ON usuarios (empresa_id, tipo);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuarios_email_ativo 
ON usuarios (email, ativo) 
WHERE ativo = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuarios_created_at 
ON usuarios (created_at DESC);

-- Participantes table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participantes_evento_status 
ON participantes (evento_id, status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participantes_usuario_evento 
ON participantes (usuario_id, evento_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participantes_data_inscricao 
ON participantes (data_inscricao DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participantes_status_checkin 
ON participantes (status, data_checkin) 
WHERE status = 'presente';

-- Check-in logs indexes  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkin_logs_evento_sucesso 
ON checkin_logs (evento_id, sucesso, tentativa_em DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkin_logs_participante_tentativa 
ON checkin_logs (participante_id, tentativa_em DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkin_logs_tipo_sucesso 
ON checkin_logs (tipo_checkin, sucesso);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkin_logs_tentativa_em_desc 
ON checkin_logs (tentativa_em DESC);

-- Transações table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transacoes_evento_status 
ON transacoes (evento_id, status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transacoes_data_transacao_desc 
ON transacoes (data_transacao DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transacoes_forma_pagamento_status 
ON transacoes (forma_pagamento, status) 
WHERE status = 'aprovada';

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transacoes_usuario_vendedor 
ON transacoes (usuario_vendedor_id, data_transacao DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transacoes_valor_status 
ON transacoes (valor_liquido DESC, status) 
WHERE status = 'aprovada';

-- Gamificação indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pontuacao_usuario_created 
ON pontuacao (usuario_id, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pontuacao_tipo_acao_created 
ON pontuacao (tipo_acao, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pontuacao_evento_usuario 
ON pontuacao (evento_id, usuario_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ranking_mes_xp 
ON ranking_gamificacao (mes_referencia, xp_total DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ranking_empresa_mes 
ON ranking_gamificacao (empresa_id, mes_referencia, xp_total DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conquistas_usuario_desbloqueada 
ON promoter_conquista (usuario_id, desbloqueada, data_desbloqueio DESC) 
WHERE desbloqueada = true;

-- ================================
-- COMPOSITE INDEXES FOR COMPLEX QUERIES
-- ================================

-- Para queries de analytics por período
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_eventos_periodo 
ON eventos (empresa_id, data_inicio, status, created_at);

-- Para queries de dashboard
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dashboard_participantes 
ON participantes (evento_id, status, data_inscricao, data_checkin);

-- Para queries de relatórios financeiros
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_financial_reports 
ON transacoes (evento_id, data_transacao, status, forma_pagamento, valor_liquido);

-- Para queries de gamificação temporal
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gamification_temporal 
ON pontuacao (usuario_id, created_at, tipo_acao, pontos_total);

-- ================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- ================================

-- View para dashboard de eventos
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_eventos_dashboard AS
SELECT 
    e.empresa_id,
    e.status,
    e.tipo_evento,
    DATE(e.data_inicio) as data_evento,
    COUNT(*) as total_eventos,
    COUNT(DISTINCT p.id) as total_participantes,
    COUNT(CASE WHEN p.status = 'presente' THEN 1 END) as total_presentes,
    COALESCE(AVG(CASE WHEN p.status = 'presente' THEN 1.0 ELSE 0.0 END) * 100, 0) as taxa_presenca,
    COALESCE(SUM(t.valor_liquido), 0) as receita_total,
    COUNT(DISTINCT t.id) as total_transacoes,
    MAX(e.updated_at) as last_updated
FROM eventos e
LEFT JOIN participantes p ON e.id = p.evento_id
LEFT JOIN transacoes t ON e.id = t.evento_id AND t.status = 'aprovada'
WHERE e.created_at >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY e.empresa_id, e.status, e.tipo_evento, DATE(e.data_inicio);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_eventos_dashboard_unique 
ON mv_eventos_dashboard (empresa_id, status, tipo_evento, data_evento);

-- View para métricas de check-in por hora
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_checkin_metrics AS
SELECT 
    cl.evento_id,
    DATE(cl.tentativa_em) as data_checkin,
    EXTRACT(HOUR FROM cl.tentativa_em) as hora_checkin,
    cl.tipo_checkin,
    COUNT(*) as total_tentativas,
    COUNT(CASE WHEN cl.sucesso THEN 1 END) as total_sucessos,
    COALESCE(AVG(CASE WHEN cl.sucesso THEN 1.0 ELSE 0.0 END) * 100, 0) as taxa_sucesso,
    AVG(EXTRACT(EPOCH FROM cl.updated_at - cl.tentativa_em)) as tempo_medio_processamento
FROM checkin_logs cl
WHERE cl.tentativa_em >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY cl.evento_id, DATE(cl.tentativa_em), EXTRACT(HOUR FROM cl.tentativa_em), cl.tipo_checkin;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_checkin_metrics_unique 
ON mv_checkin_metrics (evento_id, data_checkin, hora_checkin, tipo_checkin);

-- View para ranking de gamificação mensal
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ranking_mensal AS
WITH pontos_mensais AS (
    SELECT 
        p.usuario_id,
        u.nome,
        u.empresa_id,
        DATE_TRUNC('month', p.created_at) as mes_ref,
        SUM(p.pontos_total) as pontos_mes,
        COUNT(p.id) as total_acoes,
        COUNT(DISTINCT p.tipo_acao) as tipos_acao_unicos
    FROM pontuacao p
    JOIN usuarios u ON p.usuario_id = u.id
    WHERE p.created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '12 months'
    GROUP BY p.usuario_id, u.nome, u.empresa_id, DATE_TRUNC('month', p.created_at)
),
ranking_calculado AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY empresa_id, mes_ref ORDER BY pontos_mes DESC) as posicao_empresa,
        ROW_NUMBER() OVER (PARTITION BY mes_ref ORDER BY pontos_mes DESC) as posicao_geral
    FROM pontos_mensais
)
SELECT * FROM ranking_calculado;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_ranking_mensal_unique 
ON mv_ranking_mensal (usuario_id, mes_ref);

-- View para métricas financeiras agregadas
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_financial_metrics AS
SELECT 
    t.evento_id,
    e.empresa_id,
    DATE(t.data_transacao) as data_transacao,
    t.forma_pagamento,
    t.status,
    COUNT(*) as total_transacoes,
    SUM(t.valor_bruto) as receita_bruta,
    SUM(t.valor_liquido) as receita_liquida,
    AVG(t.valor_liquido) as ticket_medio,
    MIN(t.valor_liquido) as menor_transacao,
    MAX(t.valor_liquido) as maior_transacao,
    COUNT(DISTINCT t.usuario_comprador_id) as compradores_unicos
FROM transacoes t
JOIN eventos e ON t.evento_id = e.id
WHERE t.data_transacao >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY t.evento_id, e.empresa_id, DATE(t.data_transacao), t.forma_pagamento, t.status;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_financial_metrics_unique 
ON mv_financial_metrics (evento_id, data_transacao, forma_pagamento, status);

-- ================================
-- PARTIAL INDEXES (Para dados específicos)
-- ================================

-- Index apenas para eventos ativos dos últimos 6 meses
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_ativos_recentes 
ON eventos (empresa_id, data_inicio) 
WHERE status = 'ativo' AND data_inicio >= CURRENT_DATE - INTERVAL '6 months';

-- Index apenas para transações aprovadas dos últimos 12 meses
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transacoes_aprovadas_recentes 
ON transacoes (evento_id, data_transacao DESC, valor_liquido) 
WHERE status = 'aprovada' AND data_transacao >= CURRENT_DATE - INTERVAL '12 months';

-- Index apenas para check-ins bem-sucedidos dos últimos 3 meses
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkins_sucesso_recentes 
ON checkin_logs (evento_id, tentativa_em DESC, participante_id) 
WHERE sucesso = true AND tentativa_em >= CURRENT_DATE - INTERVAL '3 months';

-- Index apenas para pontuações dos últimos 6 meses
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pontuacao_recente 
ON pontuacao (usuario_id, created_at DESC, pontos_total) 
WHERE created_at >= CURRENT_DATE - INTERVAL '6 months';

-- ================================
-- EXPRESSION INDEXES (Para queries específicas)
-- ================================

-- Index para busca case-insensitive por nome
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuarios_nome_lower 
ON usuarios (LOWER(nome));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_nome_lower 
ON eventos (LOWER(nome));

-- Index para queries por ano/mês
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_ano_mes 
ON eventos (EXTRACT(YEAR FROM data_inicio), EXTRACT(MONTH FROM data_inicio));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transacoes_ano_mes 
ON transacoes (EXTRACT(YEAR FROM data_transacao), EXTRACT(MONTH FROM data_transacao));

-- Index para queries por dia da semana
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkins_dia_semana 
ON checkin_logs (EXTRACT(DOW FROM tentativa_em), evento_id);

-- ================================
-- FUNCTIONS FOR REFRESH MATERIALIZED VIEWS
-- ================================

-- Função para refresh automático das views materializadas
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_eventos_dashboard;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_checkin_metrics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ranking_mensal;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_financial_metrics;
END;
$$ LANGUAGE plpgsql;

-- ================================
-- AUTOMATED STATISTICS UPDATES
-- ================================

-- Função para atualizar estatísticas das tabelas principais
CREATE OR REPLACE FUNCTION update_table_statistics()
RETURNS void AS $$
BEGIN
    ANALYZE eventos;
    ANALYZE usuarios;
    ANALYZE participantes;
    ANALYZE checkin_logs;
    ANALYZE transacoes;
    ANALYZE pontuacao;
    ANALYZE ranking_gamificacao;
    ANALYZE promoter_conquista;
END;
$$ LANGUAGE plpgsql;

-- ================================
-- STORED PROCEDURES FOR COMMON QUERIES
-- ================================

-- Procedure otimizada para dashboard de eventos
CREATE OR REPLACE FUNCTION get_evento_dashboard_metrics(
    p_empresa_id INTEGER DEFAULT NULL,
    p_start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    total_eventos BIGINT,
    eventos_ativos BIGINT,
    total_participantes BIGINT,
    total_presentes BIGINT,
    taxa_presenca NUMERIC,
    receita_total NUMERIC,
    crescimento_eventos NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH current_period AS (
        SELECT 
            COUNT(DISTINCT e.id) as eventos,
            COUNT(CASE WHEN e.status = 'ativo' THEN 1 END) as ativos,
            COUNT(DISTINCT p.id) as participantes,
            COUNT(CASE WHEN p.status = 'presente' THEN 1 END) as presentes,
            COALESCE(SUM(t.valor_liquido), 0) as receita
        FROM mv_eventos_dashboard e
        LEFT JOIN participantes p ON e.empresa_id = p.evento_id  -- Simplified join
        LEFT JOIN transacoes t ON e.empresa_id = t.evento_id     -- Simplified join
        WHERE (p_empresa_id IS NULL OR e.empresa_id = p_empresa_id)
        AND e.data_evento BETWEEN p_start_date AND p_end_date
    ),
    previous_period AS (
        SELECT COUNT(DISTINCT e.id) as eventos_anterior
        FROM mv_eventos_dashboard e
        WHERE (p_empresa_id IS NULL OR e.empresa_id = p_empresa_id)
        AND e.data_evento BETWEEN p_start_date - INTERVAL '30 days' AND p_start_date
    )
    SELECT 
        cp.eventos,
        cp.ativos,
        cp.participantes,
        cp.presentes,
        CASE WHEN cp.participantes > 0 
             THEN ROUND((cp.presentes::NUMERIC / cp.participantes) * 100, 2)
             ELSE 0 END,
        cp.receita,
        CASE WHEN pp.eventos_anterior > 0 
             THEN ROUND(((cp.eventos - pp.eventos_anterior)::NUMERIC / pp.eventos_anterior) * 100, 2)
             ELSE 0 END
    FROM current_period cp, previous_period pp;
END;
$$ LANGUAGE plpgsql;

-- Procedure para métricas de gamificação
CREATE OR REPLACE FUNCTION get_user_gamification_summary(
    p_usuario_id INTEGER,
    p_periodo VARCHAR DEFAULT 'month'
)
RETURNS TABLE (
    total_pontos BIGINT,
    pontos_periodo BIGINT,
    posicao_ranking INTEGER,
    total_conquistas BIGINT,
    badge_atual VARCHAR,
    nivel_atual INTEGER
) AS $$
DECLARE
    start_date DATE;
BEGIN
    -- Definir período
    CASE p_periodo
        WHEN 'day' THEN start_date := CURRENT_DATE;
        WHEN 'week' THEN start_date := DATE_TRUNC('week', CURRENT_DATE);
        WHEN 'month' THEN start_date := DATE_TRUNC('month', CURRENT_DATE);
        WHEN 'year' THEN start_date := DATE_TRUNC('year', CURRENT_DATE);
        ELSE start_date := DATE_TRUNC('month', CURRENT_DATE);
    END CASE;

    RETURN QUERY
    WITH user_stats AS (
        SELECT 
            COALESCE(SUM(p.pontos_total), 0) as total_pts,
            COALESCE(SUM(CASE WHEN p.created_at >= start_date THEN p.pontos_total ELSE 0 END), 0) as periodo_pts,
            COUNT(DISTINCT pc.id) as conquistas
        FROM pontuacao p
        LEFT JOIN promoter_conquista pc ON pc.usuario_id = p.usuario_id AND pc.desbloqueada = true
        WHERE p.usuario_id = p_usuario_id
    ),
    ranking_pos AS (
        SELECT 
            ROW_NUMBER() OVER (ORDER BY pontos_mes DESC) as posicao
        FROM mv_ranking_mensal 
        WHERE usuario_id = p_usuario_id 
        AND mes_ref = DATE_TRUNC('month', CURRENT_DATE)
    ),
    user_ranking AS (
        SELECT badge_atual, nivel_atual 
        FROM ranking_gamificacao 
        WHERE usuario_id = p_usuario_id 
        AND mes_referencia = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
        LIMIT 1
    )
    SELECT 
        us.total_pts,
        us.periodo_pts,
        COALESCE(rp.posicao::INTEGER, 999),
        us.conquistas,
        COALESCE(ur.badge_atual, 'bronze'),
        COALESCE(ur.nivel_atual, 1)
    FROM user_stats us
    LEFT JOIN ranking_pos rp ON true
    LEFT JOIN user_ranking ur ON true;
END;
$$ LANGUAGE plpgsql;

-- ================================
-- MAINTENANCE PROCEDURES
-- ================================

-- Procedure para limpeza de dados antigos
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Manter apenas 3 anos de logs de check-in
    DELETE FROM checkin_logs 
    WHERE tentativa_em < CURRENT_DATE - INTERVAL '3 years';
    
    -- Manter apenas 5 anos de transações
    DELETE FROM transacoes 
    WHERE data_transacao < CURRENT_DATE - INTERVAL '5 years';
    
    -- Manter apenas 2 anos de pontuações
    DELETE FROM pontuacao 
    WHERE created_at < CURRENT_DATE - INTERVAL '2 years';
    
    -- Manter apenas 2 anos de ranking
    DELETE FROM ranking_gamificacao 
    WHERE mes_referencia < TO_CHAR(CURRENT_DATE - INTERVAL '2 years', 'YYYY-MM');
END;
$$ LANGUAGE plpgsql;

-- ================================
-- PERFORMANCE MONITORING QUERIES
-- ================================

-- View para monitorar performance de queries
CREATE OR REPLACE VIEW v_query_performance AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    most_common_vals,
    most_common_freqs
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY tablename, attname;

-- View para monitorar uso de indexes
CREATE OR REPLACE VIEW v_index_usage AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_blks_read,
    idx_blks_hit,
    CASE WHEN idx_tup_read > 0 
         THEN (idx_tup_fetch::float / idx_tup_read * 100)::numeric(5,2) 
         ELSE 0 END as selectivity_percentage
FROM pg_stat_user_indexes
JOIN pg_stat_user_tables USING (schemaname, tablename)
ORDER BY schemaname, tablename, indexname;

-- ================================
-- AUTOMATED TASKS (CRON JOBS)
-- ================================

-- Script de exemplo para cron jobs (executar via sistema operacional)
/*
# Atualizar views materializadas a cada hora
0 * * * * psql -d eventos_db -c "SELECT refresh_analytics_views();"

# Atualizar estatísticas a cada 6 horas  
0 */6 * * * psql -d eventos_db -c "SELECT update_table_statistics();"

# Limpeza de dados antigos semanalmente (domingo 2AM)
0 2 * * 0 psql -d eventos_db -c "SELECT cleanup_old_data();"

# Reindexação mensal (primeira segunda-feira do mês 3AM)
0 3 1-7 * 1 psql -d eventos_db -c "REINDEX DATABASE eventos_db;"
*/

-- ================================
-- COMMENTS FOR DOCUMENTATION
-- ================================

COMMENT ON FUNCTION refresh_analytics_views() IS 'Atualiza todas as materialized views para analytics em tempo real';
COMMENT ON FUNCTION update_table_statistics() IS 'Atualiza estatísticas do PostgreSQL para otimização de queries';
COMMENT ON FUNCTION get_evento_dashboard_metrics(INTEGER, DATE, DATE) IS 'Retorna métricas otimizadas para dashboard de eventos';
COMMENT ON FUNCTION get_user_gamification_summary(INTEGER, VARCHAR) IS 'Retorna resumo completo de gamificação do usuário';
COMMENT ON FUNCTION cleanup_old_data() IS 'Remove dados antigos para manter performance do banco';

COMMENT ON MATERIALIZED VIEW mv_eventos_dashboard IS 'View materializada com métricas agregadas de eventos para dashboard';
COMMENT ON MATERIALIZED VIEW mv_checkin_metrics IS 'View materializada com métricas de check-in por hora e tipo';
COMMENT ON MATERIALIZED VIEW mv_ranking_mensal IS 'View materializada com ranking de gamificação mensal';
COMMENT ON MATERIALIZED VIEW mv_financial_metrics IS 'View materializada com métricas financeiras agregadas';