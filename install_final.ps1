# SCRIPT FINAL - BASEADO NO CODIGO FORNECIDO PELO USUARIO
# Versao limpa e otimizada

Write-Host "=== INSTALACAO DE FERRAMENTAS - VERSAO FINAL ===" -ForegroundColor Green
Write-Host "Baseado no script PowerShell fornecido pelo usuario" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta executando como Admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (!$isAdmin) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Como executar como Admin:" -ForegroundColor Yellow
    Write-Host "1. Win + X -> Terminal (Administrador)" -ForegroundColor Gray
    Write-Host "2. Execute este script novamente" -ForegroundColor Gray
    pause
    exit 1
}

Write-Host "OK - Executando como Administrador" -ForegroundColor Green
Write-Host ""

# INSTALAR CHOCOLATEY (codigo exato do usuario)
Write-Host "Instalando Chocolatey..." -ForegroundColor Yellow
try {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Host "OK - Chocolatey instalado" -ForegroundColor Green
}
catch {
    Write-Host "ERRO ao instalar Chocolatey: $_" -ForegroundColor Red
    exit 1
}

# Recarregar PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ""

# INSTALAR POSTGRESQL (codigo exato do usuario)
Write-Host "Instalando PostgreSQL..." -ForegroundColor Yellow
try {
    choco install postgresql15 -y
    Write-Host "OK - PostgreSQL instalado" -ForegroundColor Green
}
catch {
    Write-Host "Aviso: Possivel problema na instalacao do PostgreSQL" -ForegroundColor Yellow
}

Write-Host ""

# INSTALAR PYTHON 3.12+ (codigo exato do usuario)
Write-Host "Instalando Python 3.12+..." -ForegroundColor Yellow
try {
    choco install python312 -y
    Write-Host "OK - Python 3.12 instalado" -ForegroundColor Green
}
catch {
    Write-Host "Aviso: Possivel problema na instalacao do Python" -ForegroundColor Yellow
}

Write-Host ""

# INSTALAR NODE.JS 20+ (codigo exato do usuario)
Write-Host "Instalando Node.js 20+..." -ForegroundColor Yellow
try {
    choco install nodejs-lts -y
    Write-Host "OK - Node.js LTS instalado" -ForegroundColor Green
}
catch {
    Write-Host "Aviso: Possivel problema na instalacao do Node.js" -ForegroundColor Yellow
}

Write-Host ""

# Recarregar PATH novamente
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# INSTALAR POETRY (codigo adaptado do usuario - usando 'python' em vez de 'py')
Write-Host "Instalando Poetry..." -ForegroundColor Yellow
try {
    Start-Sleep -Seconds 3  # Aguardar Python estar disponivel
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    Write-Host "OK - Poetry instalado" -ForegroundColor Green
}
catch {
    Write-Host "Aviso: Erro ao instalar Poetry automaticamente" -ForegroundColor Yellow
    Write-Host "Alternativa: pip install poetry" -ForegroundColor Gray
}

Write-Host ""

# Instalar Git (adicional - necessario para o projeto)
Write-Host "Instalando Git..." -ForegroundColor Yellow
try {
    choco install git -y
    Write-Host "OK - Git instalado" -ForegroundColor Green
}
catch {
    Write-Host "Aviso: Git pode ja estar instalado" -ForegroundColor Yellow
}

Write-Host ""

# VERIFICAR INSTALAÇÕES (codigo exato do usuario)
Write-Host "=== VERIFICANDO INSTALAÇÕES ===" -ForegroundColor Green
Write-Host ""

# Comandos de verificacao do usuario
try {
    $psqlVersion = psql --version 2>&1
    Write-Host "PostgreSQL: $psqlVersion" -ForegroundColor Green
}
catch {
    Write-Host "PostgreSQL: ERRO - Nao encontrado" -ForegroundColor Red
}

try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python: ERRO - Nao encontrado" -ForegroundColor Red
}

try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "Node.js: ERRO - Nao encontrado" -ForegroundColor Red
}

try {
    $npmVersion = npm --version 2>&1
    Write-Host "NPM: $npmVersion" -ForegroundColor Green
}
catch {
    Write-Host "NPM: ERRO - Nao encontrado" -ForegroundColor Red
}

try {
    $poetryVersion = poetry --version 2>&1
    Write-Host "Poetry: $poetryVersion" -ForegroundColor Green
}
catch {
    Write-Host "Poetry: ERRO - Nao encontrado" -ForegroundColor Red
}

try {
    $gitVersion = git --version 2>&1
    Write-Host "Git: $gitVersion" -ForegroundColor Green
}
catch {
    Write-Host "Git: ERRO - Nao encontrado" -ForegroundColor Red
}

try {
    $chocoVersion = choco --version 2>&1
    Write-Host "Chocolatey: $chocoVersion" -ForegroundColor Green
}
catch {
    Write-Host "Chocolatey: ERRO - Nao encontrado" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== INSTALACAO CONCLUIDA ===" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Feche este terminal Admin" -ForegroundColor Gray
Write-Host "2. Abra um terminal normal e configure o projeto:" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Backend:" -ForegroundColor Cyan
Write-Host "   cd paineluniversal/backend" -ForegroundColor Gray
Write-Host "   poetry install" -ForegroundColor Gray
Write-Host "   poetry run uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Frontend (em outro terminal):" -ForegroundColor Cyan
Write-Host "   cd paineluniversal/frontend" -ForegroundColor Gray
Write-Host "   npm install && npm run dev" -ForegroundColor Gray

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = Read-Host
