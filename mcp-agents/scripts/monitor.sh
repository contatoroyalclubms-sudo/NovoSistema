#!/bin/bash

echo "========================================="
echo "   MCP RAILWAY MONITOR"
echo "========================================="
echo ""

# Configurações
INTERVAL=${1:-60}  # Intervalo em segundos (padrão: 60)
MAX_CHECKS=${2:-0}  # Número máximo de verificações (0 = infinito)

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Contador
CHECKS=0

echo -e "${BLUE}Iniciando monitoramento...${NC}"
echo "Intervalo: ${INTERVAL}s"
if [ $MAX_CHECKS -gt 0 ]; then
    echo "Máximo de verificações: $MAX_CHECKS"
fi
echo ""

# Função de monitoramento
monitor() {
    CHECKS=$((CHECKS + 1))
    echo "----------------------------------------"
    echo "Verificação #$CHECKS - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "----------------------------------------"
    
    # Executar agente de monitoramento
    cd ../..
    node mcp-agents/index.js monitor
    
    # Verificar status
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Sistema operacional${NC}"
    else
        echo -e "${RED}✗ Problema detectado${NC}"
    fi
    
    echo ""
}

# Loop de monitoramento
while true; do
    monitor
    
    # Verificar se atingiu o máximo de checks
    if [ $MAX_CHECKS -gt 0 ] && [ $CHECKS -ge $MAX_CHECKS ]; then
        echo -e "${BLUE}Monitoramento concluído após $CHECKS verificações${NC}"
        break
    fi
    
    # Aguardar próximo ciclo
    echo "Próxima verificação em ${INTERVAL}s... (Ctrl+C para parar)"
    sleep $INTERVAL
done