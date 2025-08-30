#!/bin/bash

echo "========================================="
echo "   MCP AGENTS - SETUP SCRIPT"
echo "========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Iniciando setup dos agentes MCP...${NC}"
echo ""

# 1. Verificar Node.js
echo "1. Verificando Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✓${NC} Node.js instalado: $NODE_VERSION"
else
    echo -e "${YELLOW}!${NC} Node.js não encontrado. Instale Node.js 18+ para continuar."
    exit 1
fi

# 2. Instalar dependências dos agentes
echo ""
echo "2. Instalando dependências dos agentes..."
cd mcp-agents

# Criar package.json se não existir
if [ ! -f "package.json" ]; then
    echo "Criando package.json..."
    cat > package.json << 'EOF'
{
  "name": "mcp-agents",
  "version": "1.0.0",
  "description": "MCP Agents for Sistema MEEP",
  "main": "index.js",
  "scripts": {
    "monitor": "node agents/railway-monitor/index.js",
    "deploy": "node agents/deploy-manager/index.js",
    "validate": "node agents/system-validator/index.js",
    "test": "echo 'Running agent tests...' && node scripts/test-agents.js"
  },
  "dependencies": {
    "node-fetch": "^3.3.2",
    "dotenv": "^16.3.1",
    "chalk": "^5.3.0"
  },
  "devDependencies": {
    "jest": "^29.7.0"
  }
}
EOF
    echo -e "${GREEN}✓${NC} package.json criado"
fi

# Instalar dependências
echo "Instalando dependências npm..."
npm install

# 3. Criar arquivo de configuração de ambiente
echo ""
echo "3. Configurando ambiente..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Railway Configuration
RAILWAY_PROJECT_ID=41555273-319a-4fd5-af0e-b743861c29fa
RAILWAY_SERVICE_URL=sistema-meep-production.up.railway.app
RAILWAY_ENVIRONMENT=production

# Agent Configuration
AGENT_LOG_LEVEL=info
AGENT_TIMEOUT=30000
AGENT_RETRY_COUNT=3

# Monitoring
MONITOR_INTERVAL=60000
HEALTH_CHECK_ENABLED=true
EOF
    echo -e "${GREEN}✓${NC} Arquivo .env criado"
else
    echo -e "${YELLOW}!${NC} Arquivo .env já existe"
fi

# 4. Criar script de teste dos agentes
echo ""
echo "4. Criando scripts de teste..."
mkdir -p scripts
cat > scripts/test-agents.js << 'EOF'
const RailwayMonitor = require('../agents/railway-monitor');
const DeployManager = require('../agents/deploy-manager');
const SystemValidator = require('../agents/system-validator');

async function testAgents() {
    console.log('🧪 Testando agentes MCP...\n');
    
    try {
        // Testar Railway Monitor
        console.log('📊 Testando Railway Monitor...');
        const monitorStatus = await RailwayMonitor.checkStatus();
        console.log('✅ Railway Monitor:', monitorStatus.status);
        
        // Testar Deploy Manager
        console.log('\n🚀 Testando Deploy Manager...');
        const deployConfig = await DeployManager.prepareDeploy();
        console.log('✅ Deploy Manager configurado');
        
        // Testar System Validator
        console.log('\n🔍 Testando System Validator...');
        const validation = await SystemValidator.validateComplete();
        console.log('✅ System Validator:', validation.overallStatus);
        
        console.log('\n✨ Todos os agentes estão funcionando corretamente!');
    } catch (error) {
        console.error('❌ Erro ao testar agentes:', error.message);
        process.exit(1);
    }
}

testAgents();
EOF

echo -e "${GREEN}✓${NC} Scripts de teste criados"

# 5. Criar launcher principal
echo ""
echo "5. Criando launcher principal..."
cat > index.js << 'EOF'
const RailwayMonitor = require('./agents/railway-monitor');
const DeployManager = require('./agents/deploy-manager');
const SystemValidator = require('./agents/system-validator');

console.log('🚀 MCP Agents - Sistema MEEP');
console.log('============================\n');

async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    
    switch(command) {
        case 'monitor':
            console.log('📊 Iniciando monitoramento...');
            const status = await RailwayMonitor.checkStatus();
            console.log(JSON.stringify(status, null, 2));
            break;
            
        case 'deploy':
            console.log('🚀 Preparando deploy...');
            const config = await DeployManager.prepareDeploy();
            console.log(JSON.stringify(config, null, 2));
            break;
            
        case 'validate':
            console.log('🔍 Validando sistema...');
            const validation = await SystemValidator.validateComplete();
            console.log(JSON.stringify(validation, null, 2));
            break;
            
        case 'report':
            console.log('📋 Gerando relatório...');
            const report = await SystemValidator.generateReport();
            console.log(JSON.stringify(report, null, 2));
            break;
            
        default:
            console.log('Uso: node index.js [comando]');
            console.log('\nComandos disponíveis:');
            console.log('  monitor  - Monitora status do Railway');
            console.log('  deploy   - Prepara configuração de deploy');
            console.log('  validate - Valida sistema completo');
            console.log('  report   - Gera relatório de validação');
    }
}

main().catch(console.error);
EOF

echo -e "${GREEN}✓${NC} Launcher principal criado"

# 6. Tornar scripts executáveis
echo ""
echo "6. Configurando permissões..."
chmod +x ../railway-configs/check-deploy.sh
chmod +x setup.sh
chmod +x monitor.sh 2>/dev/null || true

echo -e "${GREEN}✓${NC} Permissões configuradas"

# 7. Resumo final
echo ""
echo "========================================="
echo -e "${GREEN}✅ SETUP CONCLUÍDO COM SUCESSO!${NC}"
echo "========================================="
echo ""
echo "📁 Estrutura criada:"
echo "   mcp-agents/"
echo "   ├── agents/          (Agentes MCP)"
echo "   ├── configs/         (Configurações)"
echo "   ├── scripts/         (Scripts auxiliares)"
echo "   ├── package.json     (Dependências)"
echo "   ├── .env            (Variáveis de ambiente)"
echo "   └── index.js        (Launcher principal)"
echo ""
echo "🚀 Como usar:"
echo "   cd mcp-agents"
echo "   node index.js monitor   # Monitorar Railway"
echo "   node index.js deploy    # Preparar deploy"
echo "   node index.js validate  # Validar sistema"
echo "   npm test               # Testar agentes"
echo ""
echo "📝 Próximos passos:"
echo "   1. Configure as variáveis no arquivo .env"
echo "   2. Execute npm test para verificar os agentes"
echo "   3. Use os comandos acima para gerenciar o sistema"
echo ""