#!/bin/bash

echo "=== VERIFICAÇÃO PRÉ-DEPLOY RAILWAY ==="
echo "Timestamp: $(date)"
echo "----------------------------------------"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de erros
ERRORS=0

# Função para verificar arquivo
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2 FALTANDO"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Função para verificar diretório
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2 FALTANDO"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

echo ""
echo "1. VERIFICANDO ESTRUTURA DO PROJETO"
echo "------------------------------------"
check_dir "paineluniversal/frontend" "Frontend directory"
check_dir "paineluniversal/backend" "Backend directory"
check_dir "mcp-agents" "MCP Agents directory"
check_dir "railway-configs" "Railway configs directory"

echo ""
echo "2. VERIFICANDO ARQUIVOS ESSENCIAIS"
echo "-----------------------------------"
check_file "railway.json" "railway.json (configuração principal)"
check_file "paineluniversal/frontend/package.json" "Frontend package.json"
check_file "paineluniversal/backend/requirements.txt" "Backend requirements.txt"
check_file "railway-configs/Dockerfile.frontend" "Dockerfile frontend"
check_file "railway-configs/Dockerfile.backend" "Dockerfile backend"

echo ""
echo "3. VERIFICANDO CONFIGURAÇÕES MCP"
echo "---------------------------------"
check_file "mcp-agents/README.md" "MCP README"
check_file "mcp-agents/configs/railway.config.js" "Railway config"
check_file "mcp-agents/configs/deployment.json" "Deployment config"

echo ""
echo "4. VERIFICANDO COMANDOS DE BUILD"
echo "---------------------------------"
if [ -f "paineluniversal/frontend/package.json" ]; then
    if grep -q '"build"' paineluniversal/frontend/package.json; then
        echo -e "${GREEN}✓${NC} Frontend build command presente"
    else
        echo -e "${RED}✗${NC} Frontend build command FALTANDO"
        ERRORS=$((ERRORS + 1))
    fi
    
    if grep -q '"serve"' paineluniversal/frontend/package.json; then
        echo -e "${GREEN}✓${NC} Frontend serve command presente"
    else
        echo -e "${YELLOW}!${NC} Frontend serve command ausente (opcional)"
    fi
fi

echo ""
echo "5. VARIÁVEIS DE AMBIENTE NECESSÁRIAS"
echo "-------------------------------------"
echo "As seguintes variáveis devem ser configuradas no Railway:"
echo "  - NODE_ENV=production"
echo "  - PORT (automaticamente definido pelo Railway)"
echo "  - DATABASE_URL (se usando banco de dados)"
echo "  - JWT_SECRET (para autenticação)"
echo "  - API_URL (URL do backend para o frontend)"

echo ""
echo "6. VERIFICANDO AGENTES MCP"
echo "---------------------------"
check_file "mcp-agents/agents/railway-monitor/index.js" "Railway Monitor Agent"
check_file "mcp-agents/agents/deploy-manager/index.js" "Deploy Manager Agent"
check_file "mcp-agents/agents/system-validator/index.js" "System Validator Agent"

echo ""
echo "======================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ SISTEMA PRONTO PARA DEPLOY!${NC}"
    echo "Todos os arquivos e configurações estão presentes."
else
    echo -e "${RED}✗ SISTEMA NÃO ESTÁ PRONTO${NC}"
    echo "Encontrados $ERRORS erro(s) que precisam ser corrigidos."
    echo ""
    echo "PRÓXIMOS PASSOS:"
    echo "1. Corrija os arquivos/diretórios faltantes"
    echo "2. Execute este script novamente"
    echo "3. Após todos os checks passarem, faça o deploy"
fi
echo "======================================="

exit $ERRORS