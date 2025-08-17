# 🚀 Sistema Universal de Gestão de Eventos
# Scripts de inicialização e automação

# ============================================================================
# 🐳 COMANDOS DOCKER
# ============================================================================

# Inicia todo o ambiente em Docker (desenvolvimento)
function Start-DockerDev {
    Write-Host "🐳 Iniciando ambiente Docker para desenvolvimento..." -ForegroundColor Blue
    docker-compose up --build
}

# Inicia todo o ambiente em Docker (produção)
function Start-DockerProd {
    Write-Host "🐳 Iniciando ambiente Docker para produção..." -ForegroundColor Blue
    docker-compose -f docker-compose.prod.yml up --build
}

# Para todos os containers
function Stop-Docker {
    Write-Host "🛑 Parando containers Docker..." -ForegroundColor Yellow
    docker-compose down
}

# Limpa containers e volumes
function Clean-Docker {
    Write-Host "🧹 Limpando containers e volumes..." -ForegroundColor Yellow
    docker-compose down -v --remove-orphans
    docker system prune -f
}

# ============================================================================
# 🔧 COMANDOS DE DESENVOLVIMENTO
# ============================================================================

# Instala todas as dependências
function Install-Dependencies {
    Write-Host "📦 Instalando dependências..." -ForegroundColor Blue
    
    Set-Location backend
    poetry install --with dev
    Set-Location ..
    
    Set-Location frontend
    npm install
    Set-Location ..
    
    Write-Host "✅ Dependências instaladas!" -ForegroundColor Green
}

# Executa testes
function Run-Tests {
    Write-Host "🧪 Executando testes..." -ForegroundColor Blue
    
    Set-Location backend
    poetry run pytest -v
    Set-Location ..
    
    Set-Location frontend
    npm run test
    Set-Location ..
    
    Write-Host "✅ Testes concluídos!" -ForegroundColor Green
}

# Verifica tipos TypeScript
function Check-Types {
    Write-Host "🔍 Verificando tipos TypeScript..." -ForegroundColor Blue
    Set-Location frontend
    npm run type-check
    Set-Location ..
}

# Formata código
function Format-Code {
    Write-Host "✨ Formatando código..." -ForegroundColor Blue
    
    Set-Location backend
    poetry run black app/
    poetry run isort app/
    Set-Location ..
    
    Set-Location frontend
    npm run format
    Set-Location ..
    
    Write-Host "✅ Código formatado!" -ForegroundColor Green
}

# ============================================================================
# 🗄️ COMANDOS DE BANCO DE DADOS
# ============================================================================

# Executa migrações
function Run-Migrations {
    Write-Host "🗄️ Executando migrações..." -ForegroundColor Blue
    Set-Location backend
    poetry run alembic upgrade head
    Set-Location ..
    Write-Host "✅ Migrações executadas!" -ForegroundColor Green
}

# Cria nova migração
function New-Migration {
    param([string]$Message = "Nova migração")
    Write-Host "🗄️ Criando nova migração: $Message" -ForegroundColor Blue
    Set-Location backend
    poetry run alembic revision --autogenerate -m "$Message"
    Set-Location ..
}

# ============================================================================
# 📊 COMANDOS DE MONITORAMENTO
# ============================================================================

# Verifica saúde do sistema
function Test-Health {
    Write-Host "🏥 Verificando saúde do sistema..." -ForegroundColor Blue
    
    try {
        $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        Write-Host "✅ Backend: $($backendHealth.status)" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Backend não está respondendo" -ForegroundColor Red
    }
    
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get
        Write-Host "✅ Frontend: Online" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Frontend não está respondendo" -ForegroundColor Red
    }
}

# Abre ferramentas de monitoramento
function Open-Monitoring {
    Write-Host "📊 Abrindo ferramentas de monitoramento..." -ForegroundColor Blue
    Start-Process "http://localhost:3001"  # Grafana
    Start-Process "http://localhost:9090"  # Prometheus
    Start-Process "http://localhost:8000/docs"  # API Docs
}

# ============================================================================
# 🔐 COMANDOS DE SEGURANÇA
# ============================================================================

# Verifica vulnerabilidades
function Test-Security {
    Write-Host "🔒 Verificando vulnerabilidades..." -ForegroundColor Blue
    
    Set-Location backend
    poetry run safety check
    Set-Location ..
    
    Set-Location frontend
    npm audit
    Set-Location ..
}

# ============================================================================
# 📚 COMANDOS DE DOCUMENTAÇÃO
# ============================================================================

# Gera documentação
function Build-Documentation {
    Write-Host "📚 Gerando documentação..." -ForegroundColor Blue
    Set-Location backend
    poetry run python -m pydoc -w app/
    Set-Location ..
    Write-Host "✅ Documentação gerada!" -ForegroundColor Green
}

# ============================================================================
# 🎯 COMANDOS PRINCIPAIS
# ============================================================================

# Setup inicial completo
function Initialize-Project {
    Write-Host "⚡ Iniciando setup completo do projeto..." -ForegroundColor Blue
    
    Install-Dependencies
    Run-Migrations
    Test-Health
    
    Write-Host "🎉 Projeto inicializado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
    Write-Host "  1. Execute: Start-Development" -ForegroundColor Yellow
    Write-Host "  2. Acesse: http://localhost:3000" -ForegroundColor Yellow
    Write-Host "  3. API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
}

# Inicia desenvolvimento completo
function Start-Development {
    Write-Host "🚀 Iniciando desenvolvimento..." -ForegroundColor Blue
    & ".\start-dev.ps1"
}

# Limpa tudo e reinicia
function Reset-Environment {
    Write-Host "🔄 Resetando ambiente..." -ForegroundColor Yellow
    & ".\reset-env.ps1"
}

# ============================================================================
# 📋 AJUDA E ALIASES
# ============================================================================

function Show-Help {
    Write-Host ""
    Write-Host "🚀 Sistema Universal de Gestão de Eventos" -ForegroundColor Magenta
    Write-Host "===============================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "🎯 COMANDOS PRINCIPAIS:" -ForegroundColor Cyan
    Write-Host "  Initialize-Project        ⚡ Setup inicial completo" -ForegroundColor Green
    Write-Host "  Start-Development         🚀 Inicia desenvolvimento" -ForegroundColor Green
    Write-Host "  Reset-Environment         🔄 Reseta ambiente" -ForegroundColor Green
    Write-Host ""
    Write-Host "🐳 DOCKER:" -ForegroundColor Cyan
    Write-Host "  Start-DockerDev           🐳 Inicia Docker (dev)" -ForegroundColor Green
    Write-Host "  Start-DockerProd          🐳 Inicia Docker (prod)" -ForegroundColor Green
    Write-Host "  Stop-Docker               🛑 Para containers" -ForegroundColor Green
    Write-Host "  Clean-Docker              🧹 Limpa containers" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔧 DESENVOLVIMENTO:" -ForegroundColor Cyan
    Write-Host "  Install-Dependencies      📦 Instala dependências" -ForegroundColor Green
    Write-Host "  Run-Tests                 🧪 Executa testes" -ForegroundColor Green
    Write-Host "  Check-Types               🔍 Verifica tipos TS" -ForegroundColor Green
    Write-Host "  Format-Code               ✨ Formata código" -ForegroundColor Green
    Write-Host ""
    Write-Host "🗄️ BANCO DE DADOS:" -ForegroundColor Cyan
    Write-Host "  Run-Migrations            🗄️ Executa migrações" -ForegroundColor Green
    Write-Host "  New-Migration             🗄️ Nova migração" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 MONITORAMENTO:" -ForegroundColor Cyan
    Write-Host "  Test-Health               🏥 Verifica saúde" -ForegroundColor Green
    Write-Host "  Open-Monitoring           📊 Abre monitoramento" -ForegroundColor Green
    Write-Host "  Test-Security             🔒 Verifica segurança" -ForegroundColor Green
    Write-Host ""
    Write-Host "📚 OUTROS:" -ForegroundColor Cyan
    Write-Host "  Build-Documentation       📚 Gera documentação" -ForegroundColor Green
    Write-Host "  Show-Help                 📋 Mostra esta ajuda" -ForegroundColor Green
    Write-Host ""
}

# Aliases para comandos comuns
Set-Alias -Name "init" -Value Initialize-Project
Set-Alias -Name "dev" -Value Start-Development
Set-Alias -Name "reset" -Value Reset-Environment
Set-Alias -Name "test" -Value Run-Tests
Set-Alias -Name "install" -Value Install-Dependencies
Set-Alias -Name "help" -Value Show-Help

# Mostrar ajuda ao carregar
Write-Host "💡 Digite 'help' para ver todos os comandos disponíveis" -ForegroundColor Yellow

# Verificar se está no diretório correto
if (-not (Test-Path "README.md") -or -not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "⚠️ Este arquivo deve ser executado no diretório raiz do projeto" -ForegroundColor Red
}
else {
    Write-Host "✅ Ambiente carregado! Projeto detectado." -ForegroundColor Green
}
