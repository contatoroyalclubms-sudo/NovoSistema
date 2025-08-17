-- Script de inicialização do banco de dados PostgreSQL
-- Este script é executado automaticamente quando o container é criado

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Configurar timezone padrão
SET timezone TO 'America/Sao_Paulo';

-- Configurar locale para português brasileiro
SET lc_messages TO 'pt_BR.UTF-8';
SET lc_monetary TO 'pt_BR.UTF-8';
SET lc_numeric TO 'pt_BR.UTF-8';
SET lc_time TO 'pt_BR.UTF-8';

-- Configurações de performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Configurações de conexão
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- Criar schema para auditoria (se necessário)
CREATE SCHEMA IF NOT EXISTS audit;

-- Função para auditoria automática
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Log de mudanças será implementado conforme necessário
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Configurações de segurança
-- Revogar permissões desnecessárias do schema public
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE 'Banco de dados PostgreSQL configurado com sucesso!';
    RAISE NOTICE 'Extensões instaladas: uuid-ossp, pgcrypto, unaccent';
    RAISE NOTICE 'Timezone configurado: America/Sao_Paulo';
    RAISE NOTICE 'Configurações de performance aplicadas';
END $$;
