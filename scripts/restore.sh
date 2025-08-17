#!/bin/bash

# Script de restauração de backup PostgreSQL

set -e

# Configurações
DB_HOST="${DB_HOST:-postgres}"
DB_NAME="${DB_NAME:-eventos_db}"
DB_USER="${DB_USER:-eventos_user}"
DB_PASSWORD="${DB_PASSWORD}"
BACKUP_DIR="/backups"
LOG_DIR="/logs"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/restore_${DATE}.log"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Função de erro
error() {
    log "ERROR: $1"
    exit 1
}

# Ajuda
show_help() {
    echo "Uso: $0 [BACKUP_FILE]"
    echo ""
    echo "Restaura um backup do banco de dados PostgreSQL"
    echo ""
    echo "Argumentos:"
    echo "  BACKUP_FILE    Arquivo de backup para restaurar (opcional, usa latest.sql.gz se não especificado)"
    echo ""
    echo "Exemplos:"
    echo "  $0                                    # Restaura o backup mais recente"
    echo "  $0 backup_eventos_db_20241201.sql.gz # Restaura backup específico"
}

# Verificar argumentos
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Determinar arquivo de backup
if [ -n "$1" ]; then
    BACKUP_FILE="${BACKUP_DIR}/$1"
else
    BACKUP_FILE="${BACKUP_DIR}/latest.sql.gz"
fi

# Verificar se arquivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    error "Arquivo de backup não encontrado: $BACKUP_FILE"
fi

# Verificar variáveis obrigatórias
if [ -z "$DB_PASSWORD" ]; then
    error "DB_PASSWORD não definida"
fi

log "🔄 Iniciando restauração do banco de dados $DB_NAME"
log "📁 Arquivo de backup: $(basename "$BACKUP_FILE")"

# Verificar conectividade com o banco
log "🔍 Verificando conectividade com o banco..."
export PGPASSWORD="$DB_PASSWORD"

if ! pg_isready -h "$DB_HOST" -U "$DB_USER" -d "postgres" -t 30; then
    error "Não foi possível conectar ao PostgreSQL"
fi

log "✅ Conectividade verificada"

# Confirmar restauração
log "⚠️ ATENÇÃO: Esta operação irá SOBRESCREVER o banco de dados $DB_NAME"
log "📄 Arquivo: $(basename "$BACKUP_FILE")"
log "📊 Tamanho: $(du -h "$BACKUP_FILE" | cut -f1)"

# Em ambiente interativo, pedir confirmação
if [ -t 0 ]; then
    read -p "Confirma a restauração? (digite 'CONFIRMO' para prosseguir): " confirm
    if [ "$confirm" != "CONFIRMO" ]; then
        log "❌ Restauração cancelada pelo usuário"
        exit 1
    fi
fi

# Verificar integridade do backup
log "🔍 Verificando integridade do backup..."
if ! gzip -t "$BACKUP_FILE"; then
    error "Arquivo de backup corrompido"
fi

log "✅ Integridade verificada"

# Fazer backup de segurança antes da restauração
SAFETY_BACKUP="${BACKUP_DIR}/safety_backup_before_restore_${DATE}.sql.gz"
log "💾 Criando backup de segurança atual..."

if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" --no-password | gzip > "$SAFETY_BACKUP"; then
    log "✅ Backup de segurança criado: $(basename "$SAFETY_BACKUP")"
else
    log "⚠️ Falha ao criar backup de segurança, mas continuando..."
fi

# Encerrar conexões ativas com o banco
log "🔌 Encerrando conexões ativas com o banco..."
psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "
    SELECT pg_terminate_backend(pid) 
    FROM pg_stat_activity 
    WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();
" || log "⚠️ Aviso ao encerrar conexões"

# Dropar e recriar banco
log "🗑️ Removendo banco existente..."
psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "DROP DATABASE IF EXISTS $DB_NAME;"

log "🆕 Criando novo banco..."
psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Restaurar backup
log "📥 Restaurando backup..."
if gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" --quiet; then
    log "✅ Backup restaurado com sucesso!"
else
    error "Falha na restauração do backup"
fi

# Verificar restauração
log "🔍 Verificando restauração..."
TABLE_COUNT=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')

if [ "$TABLE_COUNT" -gt 0 ]; then
    log "✅ Restauração verificada: $TABLE_COUNT tabelas encontradas"
else
    error "Nenhuma tabela encontrada após restauração"
fi

# Atualizar estatísticas do banco
log "📊 Atualizando estatísticas do banco..."
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "ANALYZE;" || log "⚠️ Aviso ao atualizar estatísticas"

log "🎉 Restauração concluída com sucesso!"
log "💾 Backup de segurança mantido em: $(basename "$SAFETY_BACKUP")"

# Opcional: Enviar notificação
if [ -n "$WEBHOOK_URL" ]; then
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"Restauração de $DB_NAME concluída com sucesso\", \"backup_file\": \"$(basename "$BACKUP_FILE")\"}" \
        || log "⚠️ Falha ao enviar notificação"
fi
