#!/bin/bash

# Script de limpeza de backups antigos

set -e

# Configurações
BACKUP_DIR="/backups"
LOG_DIR="/logs"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/cleanup_${DATE}.log"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🧹 Iniciando limpeza de backups antigos"
log "📁 Diretório: $BACKUP_DIR"
log "⏰ Retenção: $RETENTION_DAYS dias"

# Verificar se diretório existe
if [ ! -d "$BACKUP_DIR" ]; then
    log "❌ Diretório de backup não encontrado: $BACKUP_DIR"
    exit 1
fi

# Contar backups atuais
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f | wc -l)
log "📊 Total de backups encontrados: $TOTAL_BACKUPS"

# Encontrar backups antigos
OLD_BACKUPS=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS)

if [ -z "$OLD_BACKUPS" ]; then
    log "✅ Nenhum backup antigo encontrado para limpeza"
    exit 0
fi

# Contar backups antigos
OLD_COUNT=$(echo "$OLD_BACKUPS" | wc -l)
log "🗑️ Backups antigos encontrados: $OLD_COUNT"

# Calcular espaço a ser liberado
SPACE_TO_FREE=0
while IFS= read -r file; do
    if [ -f "$file" ]; then
        SIZE=$(du -b "$file" | cut -f1)
        SPACE_TO_FREE=$((SPACE_TO_FREE + SIZE))
        log "📄 Marcado para remoção: $(basename "$file") ($(du -h "$file" | cut -f1))"
    fi
done <<< "$OLD_BACKUPS"

# Converter para formato legível
SPACE_MB=$((SPACE_TO_FREE / 1024 / 1024))
log "💽 Espaço a ser liberado: ${SPACE_MB}MB"

# Remover backups antigos
REMOVED_COUNT=0
while IFS= read -r file; do
    if [ -f "$file" ]; then
        if rm "$file"; then
            log "✅ Removido: $(basename "$file")"
            REMOVED_COUNT=$((REMOVED_COUNT + 1))
        else
            log "❌ Erro ao remover: $(basename "$file")"
        fi
    fi
done <<< "$OLD_BACKUPS"

# Limpar logs antigos também
log "🧹 Limpando logs antigos..."
OLD_LOGS=$(find "$LOG_DIR" -name "*.log" -type f -mtime +$RETENTION_DAYS)

if [ -n "$OLD_LOGS" ]; then
    OLD_LOGS_COUNT=$(echo "$OLD_LOGS" | wc -l)
    log "🗑️ Logs antigos encontrados: $OLD_LOGS_COUNT"
    
    while IFS= read -r logfile; do
        if [ -f "$logfile" ]; then
            if rm "$logfile"; then
                log "✅ Log removido: $(basename "$logfile")"
            else
                log "❌ Erro ao remover log: $(basename "$logfile")"
            fi
        fi
    done <<< "$OLD_LOGS"
else
    log "✅ Nenhum log antigo encontrado"
fi

# Limpar backups de segurança muito antigos (dobro do período de retenção)
SAFETY_RETENTION=$((RETENTION_DAYS * 2))
OLD_SAFETY_BACKUPS=$(find "$BACKUP_DIR" -name "safety_backup_*.sql.gz" -type f -mtime +$SAFETY_RETENTION)

if [ -n "$OLD_SAFETY_BACKUPS" ]; then
    OLD_SAFETY_COUNT=$(echo "$OLD_SAFETY_BACKUPS" | wc -l)
    log "🗑️ Backups de segurança muito antigos: $OLD_SAFETY_COUNT"
    
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            if rm "$file"; then
                log "✅ Backup de segurança removido: $(basename "$file")"
            else
                log "❌ Erro ao remover backup de segurança: $(basename "$file")"
            fi
        fi
    done <<< "$OLD_SAFETY_BACKUPS"
else
    log "✅ Nenhum backup de segurança muito antigo encontrado"
fi

# Verificar espaço em disco após limpeza
AVAILABLE_SPACE=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $4}')
USED_SPACE=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $3}')

log "💽 Espaço disponível após limpeza: $AVAILABLE_SPACE"
log "💽 Espaço utilizado: $USED_SPACE"

# Contar backups restantes
REMAINING_BACKUPS=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f | wc -l)
log "📊 Backups restantes: $REMAINING_BACKUPS"

log "🎉 Limpeza concluída!"
log "📊 Resumo:"
log "   - Backups removidos: $REMOVED_COUNT"
log "   - Espaço liberado: ${SPACE_MB}MB"
log "   - Backups restantes: $REMAINING_BACKUPS"

# Verificar se há poucos backups restantes
if [ "$REMAINING_BACKUPS" -lt 7 ]; then
    log "⚠️ ATENÇÃO: Poucos backups restantes ($REMAINING_BACKUPS). Considere ajustar a política de retenção."
fi

# Opcional: Enviar relatório
if [ -n "$WEBHOOK_URL" ]; then
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"Limpeza de backups concluída\", \"removed\": $REMOVED_COUNT, \"remaining\": $REMAINING_BACKUPS, \"space_freed_mb\": $SPACE_MB}" \
        || log "⚠️ Falha ao enviar relatório"
fi
