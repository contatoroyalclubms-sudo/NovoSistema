# Script que automaticamente solicita privilégios de administrador
param([switch]$Elevated)

function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (!(Test-Admin)) {
    Write-Host "🔐 SOLICITANDO PRIVILEGIOS DE ADMINISTRADOR..." -ForegroundColor Yellow
    Write-Host "Uma janela UAC pode aparecer - clique em SIM" -ForegroundColor Cyan
    
    $scriptPath = $PSCommandPath
    if (!$scriptPath) {
        $scriptPath = $MyInvocation.MyCommand.Definition
    }
    if (!$scriptPath) {
        $scriptPath = "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\install_as_admin.ps1"
    }
    
    Start-Process PowerShell -ArgumentList "-ExecutionPolicy Bypass -File `"$scriptPath`" -Elevated" -Verb RunAs
    exit
}

Write-Host "🛡️  EXECUTANDO COMO ADMINISTRADOR" -ForegroundColor Green
Write-Host ""

Set-Location "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"

Write-Host "=== INSTALAÇÃO AUTOMÁTICA DE FERRAMENTAS ===" -ForegroundColor Green
Write-Host "Equivalente aos scripts Linux/macOS fornecidos" -ForegroundColor Cyan
Write-Host ""

# 1. Instalar Chocolatey
Write-Host "🍫 INSTALANDO CHOCOLATEY..." -ForegroundColor Yellow
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "✅ Chocolatey instalado!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Erro ao instalar Chocolatey" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✅ Chocolatey já instalado" -ForegroundColor Green
}

# Atualizar PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host ""

# 2. Instalar Python 3.12
Write-Host "🐍 INSTALANDO PYTHON 3.12..." -ForegroundColor Yellow
try {
    choco install python312 -y --force
    Write-Host "✅ Python 3.12 instalado!" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Possível problema na instalação do Python" -ForegroundColor Yellow
}

Write-Host ""

# 3. Instalar Node.js 20
Write-Host "🟢 INSTALANDO NODE.JS 20..." -ForegroundColor Yellow
try {
    choco install nodejs-lts -y --force
    Write-Host "✅ Node.js LTS instalado!" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Possível problema na instalação do Node.js" -ForegroundColor Yellow
}

Write-Host ""

# 4. Instalar PostgreSQL 15
Write-Host "🐘 INSTALANDO POSTGRESQL 15..." -ForegroundColor Yellow
try {
    choco install postgresql15 -y --force
    Write-Host "✅ PostgreSQL 15 instalado!" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Possível problema na instalação do PostgreSQL" -ForegroundColor Yellow
}

Write-Host ""

# 5. Instalar Git
Write-Host "🔧 INSTALANDO GIT..." -ForegroundColor Yellow
try {
    choco install git -y --force
    Write-Host "✅ Git instalado!" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Possível problema na instalação do Git" -ForegroundColor Yellow
}

Write-Host ""

# Atualizar PATH novamente
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# 6. Instalar Poetry
Write-Host "📝 INSTALANDO POETRY..." -ForegroundColor Yellow
try {
    Start-Sleep -Seconds 3  # Aguardar Python estar disponível
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    Write-Host "✅ Poetry instalado!" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Possível problema na instalação do Poetry" -ForegroundColor Yellow
    Write-Host "💡 Tente manualmente: pip install poetry" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🔄 REINICIANDO SERVIÇOS..." -ForegroundColor Cyan

# Iniciar PostgreSQL se não estiver rodando
try {
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgService) {
        Start-Service $pgService.Name -ErrorAction SilentlyContinue
        Write-Host "✅ PostgreSQL iniciado" -ForegroundColor Green
    }
}
catch {
    Write-Host "⚠️  PostgreSQL pode precisar ser iniciado manualmente" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== VERIFICAÇÃO FINAL ===" -ForegroundColor Green
Write-Host ""

$tools = @("python", "node", "npm", "psql", "git", "poetry", "choco")

foreach ($tool in $tools) {
    Write-Host "$tool :" -NoNewline -ForegroundColor Yellow
    try {
        $version = & $tool --version 2>&1
        if ($version) {
            Write-Host " ✅ $($version.Split("`n")[0])" -ForegroundColor Green
        }
        else {
            Write-Host " ❌ Não funcionando" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " ❌ Não encontrado" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 INSTALAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. FECHE este PowerShell" -ForegroundColor Yellow
Write-Host "2. ABRA um novo terminal normal (não Admin)" -ForegroundColor Yellow
Write-Host "3. Execute os comandos do projeto:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # Backend:" -ForegroundColor Gray
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   poetry install" -ForegroundColor Gray
Write-Host "   poetry run uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Frontend (em outro terminal):" -ForegroundColor Gray
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
