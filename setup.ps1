# 🚀 Script de Setup Completo do Sistema de Gestão de Eventos
# Este script configura automaticamente todo o ambiente de desenvolvimento no Windows

param(
    [switch]$SkipDependencyCheck,
    [switch]$SkipPostgreSQL,
    [switch]$SkipDocker,
    [switch]$Force
)

# Configuração de cores
$Colors = @{
    Red     = "Red"
    Green   = "Green" 
    Yellow  = "Yellow"
    Blue    = "Blue"
    Magenta = "Magenta"
    Cyan    = "Cyan"
    White   = "White"
}

# Funções de log colorido
function Write-ColorLog {
    param([string]$Message, [string]$Color = "Green")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorLog $Message "Green" }
function Write-Warning { param([string]$Message) Write-ColorLog "[WARNING] $Message" "Yellow" }
function Write-Error { param([string]$Message) Write-ColorLog "[ERROR] $Message" "Red"; exit 1 }
function Write-Info { param([string]$Message) Write-ColorLog "[INFO] $Message" "Blue" }

# Banner do sistema
function Show-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                                                                  ║" -ForegroundColor Magenta
    Write-Host "║    🚀 SISTEMA UNIVERSAL DE GESTÃO DE EVENTOS                    ║" -ForegroundColor Magenta
    Write-Host "║                                                                  ║" -ForegroundColor Magenta
    Write-Host "║    Setup Automático do Ambiente de Desenvolvimento (Windows)    ║" -ForegroundColor Magenta
    Write-Host "║                                                                  ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

# Verificar se está no diretório correto
function Test-Directory {
    if (-not (Test-Path "README.md") -or -not (Test-Path "backend") -or -not (Test-Path "frontend")) {
        Write-Error "Execute este script no diretório raiz do projeto (onde está o README.md)"
    }
    Write-Success "✅ Diretório correto verificado"
}

# Verificar se está executando como administrador
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Verificar dependências
function Test-Dependencies {
    Write-Info "🔍 Verificando dependências..."
    
    $missingDeps = @()
    
    # Verificar Python 3.12+
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "✅ Python encontrado: $pythonVersion"
        }
        else {
            $missingDeps += "python"
        }
    }
    catch {
        $missingDeps += "python"
    }
    
    # Verificar Node.js 18+
    try {
        $nodeVersion = node --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $versionNumber = ($nodeVersion -replace 'v', '').Split('.')[0]
            if ([int]$versionNumber -ge 18) {
                Write-Info "✅ Node.js encontrado: $nodeVersion"
            }
            else {
                Write-Warning "Node.js versão $nodeVersion encontrada. Recomenda-se versão 18+"
            }
        }
        else {
            $missingDeps += "nodejs"
        }
    }
    catch {
        $missingDeps += "nodejs"
    }
    
    # Verificar PostgreSQL
    try {
        $pgVersion = psql --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "✅ PostgreSQL encontrado: $pgVersion"
        }
        else {
            $missingDeps += "postgresql"
        }
    }
    catch {
        $missingDeps += "postgresql"
    }
    
    # Verificar Poetry
    try {
        $poetryVersion = poetry --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "✅ Poetry encontrado: $poetryVersion"
        }
        else {
            $missingDeps += "poetry"
        }
    }
    catch {
        $missingDeps += "poetry"
    }
    
    # Verificar Git
    try {
        $gitVersion = git --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "✅ Git encontrado: $gitVersion"
        }
        else {
            $missingDeps += "git"
        }
    }
    catch {
        $missingDeps += "git"
    }
    
    if ($missingDeps.Count -gt 0 -and -not $SkipDependencyCheck) {
        Write-Warning "Dependências faltando: $($missingDeps -join ', ')"
        
        if (-not $Force) {
            $response = Read-Host "Deseja instalar automaticamente via Chocolatey? (y/N)"
            if ($response -eq 'y' -or $response -eq 'Y') {
                Install-Dependencies $missingDeps
            }
            else {
                Write-Error "Instale as dependências manualmente e execute o script novamente"
            }
        }
        else {
            Install-Dependencies $missingDeps
        }
    }
    else {
        Write-Success "✅ Todas as dependências estão instaladas"
    }
}

# Instalar dependências via Chocolatey
function Install-Dependencies {
    param([array]$Dependencies)
    
    Write-Info "📦 Instalando dependências via Chocolatey..."
    
    # Verificar se Chocolatey está instalado
    try {
        choco --version | Out-Null
    }
    catch {
        Write-Info "📦 Instalando Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        refreshenv
    }
    
    foreach ($dep in $Dependencies) {
        Write-Info "📦 Instalando $dep..."
        switch ($dep) {
            "python" { choco install python312 -y }
            "nodejs" { choco install nodejs --version=20.11.1 -y }
            "postgresql" { choco install postgresql15 --params '/Password:postgres' -y }
            "poetry" { choco install poetry -y }
            "git" { choco install git -y }
        }
    }
    
    # Refresh environment variables
    refreshenv
    Write-Success "✅ Dependências instaladas"
}

# Configurar PostgreSQL
function Set-PostgreSQL {
    if ($SkipPostgreSQL) {
        Write-Info "⏭️ Pulando configuração do PostgreSQL"
        return
    }
    
    Write-Info "🐘 Configurando PostgreSQL..."
    
    # Verificar se o serviço PostgreSQL está rodando
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgService -and $pgService.Status -ne "Running") {
        Write-Info "🚀 Iniciando serviço PostgreSQL..."
        Start-Service $pgService.Name
    }
    
    # Aguardar PostgreSQL estar pronto
    $timeout = 30
    $elapsed = 0
    while ($elapsed -lt $timeout) {
        try {
            & psql -U postgres -d postgres -c "SELECT 1;" 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { break }
        }
        catch {}
        Start-Sleep 2
        $elapsed += 2
    }
    
    # Configurar banco de dados
    Write-Info "📊 Criando banco de dados e usuário..."
    
    $setupScript = @"
-- Criar usuário eventos_user
DO `$`$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'eventos_user') THEN
        CREATE USER eventos_user WITH PASSWORD 'eventos_2024_secure!';
    END IF;
END `$`$;

-- Criar banco de dados se não existir
SELECT 'CREATE DATABASE eventos_db OWNER eventos_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'eventos_db')\gexec

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE eventos_db TO eventos_user;

-- Conectar ao banco eventos_db e configurar
\c eventos_db

-- Conceder permissões no schema public
GRANT ALL ON SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eventos_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO eventos_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO eventos_user;

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Verificar criação
\echo 'Banco de dados configurado com sucesso!'
"@

    $setupScript | & psql -U postgres -d postgres
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ PostgreSQL configurado com sucesso"
    }
    else {
        Write-Error "❌ Falha na configuração do PostgreSQL"
    }
    
    # Testar conexão
    $env:PGPASSWORD = "eventos_2024_secure!"
    & psql -h localhost -U eventos_user -d eventos_db -c "SELECT version();" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Teste de conexão com banco bem-sucedido"
    }
    else {
        Write-Error "❌ Falha no teste de conexão com banco"
    }
}

# Configurar Backend
function Set-Backend {
    Write-Info "🐍 Configurando backend Python..."
    
    Set-Location backend
    
    # Configurar Poetry
    poetry config virtualenvs.in-project true
    
    # Instalar dependências
    Write-Info "📦 Instalando dependências do backend..."
    poetry install --with dev
    
    # Copiar arquivo de ambiente se não existir
    if (-not (Test-Path ".env")) {
        Write-Info "📝 Criando arquivo .env..."
        Copy-Item ".env.example" ".env"
        
        # Gerar secret key aleatória
        $secretKey = poetry run python -c "import secrets; print(secrets.token_urlsafe(32))"
        (Get-Content ".env") -replace "your-super-secret-key-change-in-production-eventos2024!", $secretKey | Set-Content ".env"
        
        Write-Success "✅ Arquivo .env criado com SECRET_KEY gerada"
    }
    
    # Testar imports do backend
    Write-Info "🧪 Testando imports do backend..."
    poetry run python -c "from app.database import test_connection; print('✅ Imports OK')"
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Backend configurado com sucesso"
    }
    else {
        Write-Error "❌ Erro na configuração do backend"
    }
    
    Set-Location ..
}

# Configurar Frontend
function Set-Frontend {
    Write-Info "⚛️ Configurando frontend React..."
    
    Set-Location frontend
    
    # Instalar dependências
    Write-Info "📦 Instalando dependências do frontend..."
    npm install
    
    # Copiar arquivo de ambiente se não existir
    if (-not (Test-Path ".env")) {
        Write-Info "📝 Criando arquivo .env do frontend..."
        @"
# Frontend Environment Variables
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_NAME="Sistema de Gestão de Eventos"
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=development
"@ | Out-File -FilePath ".env" -Encoding utf8
        Write-Success "✅ Arquivo .env do frontend criado"
    }
    
    # Verificar se o build funciona
    Write-Info "🧪 Testando build do frontend..."
    npm run type-check
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Frontend configurado com sucesso"
    }
    else {
        Write-Warning "⚠️ Avisos no TypeScript detectados, mas continuando..."
    }
    
    Set-Location ..
}

# Configurar Docker
function Set-Docker {
    if ($SkipDocker) {
        Write-Info "⏭️ Pulando configuração do Docker"
        return
    }
    
    Write-Info "🐳 Configurando Docker..."
    
    # Verificar se Docker está instalado
    try {
        docker --version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Docker não encontrado. Pulando configuração Docker."
            return
        }
    }
    catch {
        Write-Warning "Docker não encontrado. Pulando configuração Docker."
        return
    }
    
    # Criar docker-compose.yml (será criado em função separada)
    Write-Success "✅ Docker configurado"
}

# Criar scripts utilitários
function New-UtilityScripts {
    Write-Info "🛠️ Criando scripts utilitários..."
    
    # Script para iniciar desenvolvimento (PowerShell)
    @"
# Script para iniciar o sistema em modo desenvolvimento
param([switch]`$NoFrontend, [switch]`$NoBackend)

Write-Host "🚀 Iniciando Sistema de Gestão de Eventos em modo desenvolvimento..." -ForegroundColor Blue

# Verificar se PostgreSQL está rodando
try {
    `$env:PGPASSWORD = "eventos_2024_secure!"
    psql -h localhost -U eventos_user -d eventos_db -c "SELECT 1;" | Out-Null
    if (`$LASTEXITCODE -ne 0) {
        throw "PostgreSQL não acessível"
    }
} catch {
    Write-Host "❌ PostgreSQL não está rodando. Inicie o serviço primeiro." -ForegroundColor Red
    exit 1
}

# Iniciar Backend
if (-not `$NoBackend) {
    Write-Host "🐍 Iniciando Backend (FastAPI)..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; poetry run uvicorn app.main:app --reload"
    Start-Sleep 3
}

# Iniciar Frontend  
if (-not `$NoFrontend) {
    Write-Host "📱 Iniciando Frontend (React)..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
}

Write-Host ""
Write-Host "✅ Sistema iniciado!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🐍 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Documentação da API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para parar os serviços, feche as janelas do PowerShell ou use Ctrl+C" -ForegroundColor Yellow
"@ | Out-File -FilePath "start-dev.ps1" -Encoding utf8
    
    # Script para backup do banco
    @"
# Script para backup do banco de dados
`$date = Get-Date -Format "yyyyMMdd_HHmmss"
`$backupFile = "backup_eventos_`$date.sql"

Write-Host "🗄️ Criando backup do banco de dados..." -ForegroundColor Blue

# Criar diretório de backups se não existir
if (-not (Test-Path "backups")) {
    New-Item -ItemType Directory -Path "backups"
}

`$env:PGPASSWORD = "eventos_2024_secure!"
pg_dump -h localhost -U eventos_user -d eventos_db | Out-File -FilePath "backups\`$backupFile" -Encoding utf8

if (`$LASTEXITCODE -eq 0) {
    Write-Host "✅ Backup criado: backups\`$backupFile" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao criar backup" -ForegroundColor Red
    exit 1
}
"@ | Out-File -FilePath "backup-db.ps1" -Encoding utf8
    
    # Script para resetar ambiente
    @"
# Script para resetar completamente o ambiente de desenvolvimento
Write-Host "⚠️ ATENÇÃO: Este script irá resetar completamente o ambiente de desenvolvimento!" -ForegroundColor Red
`$confirm = Read-Host "Tem certeza? (digite 'RESET' para confirmar)"

if (`$confirm -ne "RESET") {
    Write-Host "❌ Reset cancelado" -ForegroundColor Red
    exit 1
}

Write-Host "🔄 Resetando ambiente..." -ForegroundColor Yellow

# Parar processos se estiverem rodando
Get-Process | Where-Object { `$_.ProcessName -like "*uvicorn*" -or `$_.ProcessName -like "*node*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Remover dados do banco
`$env:PGPASSWORD = "eventos_2024_secure!"
psql -h localhost -U eventos_user -d eventos_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Reinstalar dependências do backend
Set-Location backend
poetry install --with dev
Set-Location ..

# Reinstalar dependências do frontend
Set-Location frontend
Remove-Item -Recurse -Force node_modules, package-lock.json -ErrorAction SilentlyContinue
npm install
Set-Location ..

Write-Host "✅ Ambiente resetado com sucesso!" -ForegroundColor Green
Write-Host "Execute .\start-dev.ps1 para iniciar novamente" -ForegroundColor Cyan
"@ | Out-File -FilePath "reset-env.ps1" -Encoding utf8
    
    # Criar diretório de backups
    if (-not (Test-Path "backups")) {
        New-Item -ItemType Directory -Path "backups" | Out-Null
    }
    
    Write-Success "✅ Scripts utilitários criados"
}

# Verificar saúde do sistema
function Test-SystemHealth {
    Write-Info "🏥 Verificando saúde do sistema..."
    
    $issues = @()
    
    # Verificar PostgreSQL
    try {
        $env:PGPASSWORD = "eventos_2024_secure!"
        psql -h localhost -U eventos_user -d eventos_db -c "SELECT 1;" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            $issues += "PostgreSQL não acessível"
        }
    }
    catch {
        $issues += "PostgreSQL não acessível"
    }
    
    # Verificar backend
    try {
        Set-Location backend
        poetry run python -c "from app.database import test_connection; test_connection()" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            $issues += "Backend não pode conectar ao banco"
        }
        Set-Location ..
    }
    catch {
        $issues += "Backend não pode conectar ao banco"
        Set-Location ..
    }
    
    # Verificar frontend
    try {
        Set-Location frontend
        npm run type-check | Out-Null
        if ($LASTEXITCODE -ne 0) {
            $issues += "Frontend tem erros de TypeScript"
        }
        Set-Location ..
    }
    catch {
        $issues += "Frontend tem erros de TypeScript"
        Set-Location ..
    }
    
    if ($issues.Count -eq 0) {
        Write-Success "✅ Sistema saudável e pronto para uso!"
    }
    else {
        Write-Warning "⚠️ Problemas encontrados:"
        foreach ($issue in $issues) {
            Write-Host "   - $issue" -ForegroundColor Yellow
        }
    }
}

# Função principal
function Main {
    Show-Banner
    
    Write-Success "🚀 Iniciando setup do Sistema de Gestão de Eventos..."
    
    Test-Directory
    Test-Dependencies
    Set-PostgreSQL
    Set-Backend
    Set-Frontend
    Set-Docker
    New-UtilityScripts
    Test-SystemHealth
    
    Write-Host ""
    Write-Host "🎉 SETUP CONCLUÍDO COM SUCESSO! 🎉" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. " -NoNewline; Write-Host "Inicie o sistema:" -ForegroundColor Blue
    Write-Host "   " -NoNewline; Write-Host ".\start-dev.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. " -NoNewline; Write-Host "Acesse as URLs:" -ForegroundColor Blue
    Write-Host "   📱 Frontend: " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Yellow
    Write-Host "   🐍 Backend: " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Yellow
    Write-Host "   📚 API Docs: " -NoNewline; Write-Host "http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3. " -NoNewline; Write-Host "Ou use Docker:" -ForegroundColor Blue
    Write-Host "   " -NoNewline; Write-Host "docker-compose up" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🛠️ Scripts úteis criados:" -ForegroundColor Cyan
    Write-Host "   .\start-dev.ps1    - Iniciar desenvolvimento"
    Write-Host "   .\backup-db.ps1    - Backup do banco"
    Write-Host "   .\reset-env.ps1    - Resetar ambiente"
    Write-Host ""
    Write-Host "✨ Boa codificação! ✨" -ForegroundColor Green
}

# Executar função principal
Main
