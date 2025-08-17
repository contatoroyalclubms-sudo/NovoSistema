#!/bin/bash

# Script de backup automatizado para PostgreSQL
# Este script é executado dentro do container de backup

set -e

# Configurações
DB_HOST="${DB_HOST:-postgres}"
DB_NAME="${DB_NAME:-eventos_db}"
DB_USER="${DB_USER:-eventos_user}"
DB_PASSWORD="${DB_PASSWORD}"
BACKUP_DIR="/backups"
LOG_DIR="/logs"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${DATE}.sql.gz"
LOG_FILE="${LOG_DIR}/backup_${DATE}.log"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Função de erro
error() {
    log "ERROR: $1"
    exit 1
}

# Verificar variáveis obrigatórias
if [ -z "$DB_PASSWORD" ]; then
    error "DB_PASSWORD não definida"
fi

log "🗄️ Iniciando backup do banco de dados $DB_NAME"

# Verificar conectividade com o banco
log "🔍 Verificando conectividade com o banco..."
export PGPASSWORD="$DB_PASSWORD"

if ! pg_isready -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t 30; then
    error "Não foi possível conectar ao banco de dados"
fi

log "✅ Conectividade verificada"

# Criar backup
log "📦 Criando backup comprimido..."
if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" --verbose --no-password \
    --exclude-table-data="audit.*" \
    --exclude-table-data="logs.*" | gzip > "$BACKUP_FILE"; then
    
    log "✅ Backup criado com sucesso: $(basename "$BACKUP_FILE")"
    
    # Verificar tamanho do arquivo
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "📊 Tamanho do backup: $BACKUP_SIZE"
    
    # Verificar integridade do arquivo comprimido
    if gzip -t "$BACKUP_FILE"; then
        log "✅ Integridade do backup verificada"
    else
        error "Backup corrompido"
    fi
    
else
    error "Falha ao criar backup"
fi

# Criar link simbólico para o backup mais recente
ln -sf "$(basename "$BACKUP_FILE")" "${BACKUP_DIR}/latest.sql.gz"
log "🔗 Link simbólico atualizado: latest.sql.gz"

# Executar cleanup de backups antigos
log "🧹 Executando cleanup de backups antigos..."
/scripts/cleanup.sh

log "🎉 Backup concluído com sucesso!"

# Opcional: Enviar notificação (webhook, email, etc.)
if [ -n "$WEBHOOK_URL" ]; then
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"Backup de $DB_NAME concluído com sucesso\", \"file\": \"$(basename "$BACKUP_FILE")\", \"size\": \"$BACKUP_SIZE\"}" \
        || log "⚠️ Falha ao enviar notificação"
fi
