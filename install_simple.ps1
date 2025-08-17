# SCRIPT SIMPLES DE INSTALAÇÃO - EXECUTE EM POWERSHELL ADMIN
# Versão corrigida sem auto-elevação

Write-Host "=== INSTALAÇÃO DE FERRAMENTAS PARA O PROJETO ===" -ForegroundColor Green
Write-Host "⚠️  CERTIFIQUE-SE DE ESTAR EXECUTANDO COMO ADMINISTRADOR!" -ForegroundColor Yellow
Write-Host ""

# Verificar se está executando como Admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (!$isAdmin) {
    Write-Host "❌ ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Como abrir PowerShell como Admin:" -ForegroundColor Yellow
    Write-Host "1. Pressione Win + X" -ForegroundColor Gray
    Write-Host "2. Clique em 'Terminal (Administrador)'" -ForegroundColor Gray
    Write-Host "3. Execute este script novamente" -ForegroundColor Gray
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ Executando como Administrador" -ForegroundColor Green
Write-Host ""

Set-Location "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"

# Função para verificar se comando existe
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# 1. CHOCOLATEY
Write-Host "🍫 VERIFICANDO CHOCOLATEY..." -ForegroundColor Yellow
if (!(Test-CommandExists "choco")) {
    Write-Host "   Instalando Chocolatey..." -ForegroundColor Cyan
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "   ✅ Chocolatey instalado!" -ForegroundColor Green
        
        # Recarregar PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        refreshenv
    }
    catch {
        Write-Host "   ❌ Erro ao instalar Chocolatey: $_" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "   ✅ Chocolatey já instalado" -ForegroundColor Green
}

Write-Host ""

# 2. PYTHON
Write-Host "🐍 VERIFICANDO PYTHON..." -ForegroundColor Yellow
if (!(Test-CommandExists "python")) {
    Write-Host "   Instalando Python 3.12..." -ForegroundColor Cyan
    choco install python312 -y
    Write-Host "   ✅ Python instalado!" -ForegroundColor Green
}
else {
    Write-Host "   ✅ Python já instalado" -ForegroundColor Green
}

Write-Host ""

# 3. NODE.JS
Write-Host "🟢 VERIFICANDO NODE.JS..." -ForegroundColor Yellow
if (!(Test-CommandExists "node")) {
    Write-Host "   Instalando Node.js LTS..." -ForegroundColor Cyan
    choco install nodejs-lts -y
    Write-Host "   ✅ Node.js instalado!" -ForegroundColor Green
}
else {
    Write-Host "   ✅ Node.js já instalado" -ForegroundColor Green
}

Write-Host ""

# 4. POSTGRESQL
Write-Host "🐘 VERIFICANDO POSTGRESQL..." -ForegroundColor Yellow
if (!(Test-CommandExists "psql")) {
    Write-Host "   Instalando PostgreSQL 15..." -ForegroundColor Cyan
    choco install postgresql15 -y
    Write-Host "   ✅ PostgreSQL instalado!" -ForegroundColor Green
}
else {
    Write-Host "   ✅ PostgreSQL já instalado" -ForegroundColor Green
}

Write-Host ""

# 5. GIT
Write-Host "🔧 VERIFICANDO GIT..." -ForegroundColor Yellow
if (!(Test-CommandExists "git")) {
    Write-Host "   Instalando Git..." -ForegroundColor Cyan
    choco install git -y
    Write-Host "   ✅ Git instalado!" -ForegroundColor Green
}
else {
    Write-Host "   ✅ Git já instalado" -ForegroundColor Green
}

Write-Host ""

# Recarregar PATH após todas as instalações
Write-Host "🔄 ATUALIZANDO VARIÁVEIS DE AMBIENTE..." -ForegroundColor Cyan
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# 6. POETRY
Write-Host "📝 VERIFICANDO POETRY..." -ForegroundColor Yellow
if (!(Test-CommandExists "poetry")) {
    Write-Host "   Instalando Poetry..." -ForegroundColor Cyan
    try {
        # Aguardar Python estar disponível
        Start-Sleep -Seconds 3
        (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
        Write-Host "   ✅ Poetry instalado!" -ForegroundColor Green
    }
    catch {
        Write-Host "   ⚠️  Erro ao instalar Poetry automaticamente" -ForegroundColor Yellow
        Write-Host "   💡 Instale manualmente: pip install poetry" -ForegroundColor Gray
    }
}
else {
    Write-Host "   ✅ Poetry já instalado" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== VERIFICAÇÃO FINAL ===" -ForegroundColor Green
Write-Host ""

# Verificar todas as ferramentas
$ferramentas = @(
    @{Nome = "Python"; Comando = "python --version" },
    @{Nome = "Node.js"; Comando = "node --version" },
    @{Nome = "NPM"; Comando = "npm --version" },
    @{Nome = "PostgreSQL"; Comando = "psql --version" },
    @{Nome = "Git"; Comando = "git --version" },
    @{Nome = "Poetry"; Comando = "poetry --version" },
    @{Nome = "Chocolatey"; Comando = "choco --version" }
)

foreach ($ferramenta in $ferramentas) {
    Write-Host "$($ferramenta.Nome):" -NoNewline -ForegroundColor Yellow
    try {
        $resultado = Invoke-Expression $ferramenta.Comando 2>&1
        if ($resultado -and $resultado -notlike "*not recognized*" -and $resultado -notlike "*não*reconhecido*") {
            $versao = $resultado.ToString().Split("`n")[0].Trim()
            Write-Host " ✅ $versao" -ForegroundColor Green
        }
        else {
            Write-Host " ❌ Não funcionando" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " ❌ Erro: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 INSTALAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. FECHE este PowerShell Administrador" -ForegroundColor Yellow
Write-Host "2. ABRA um terminal normal (sem privilégios de Admin)" -ForegroundColor Yellow
Write-Host "3. Navegue até o projeto e configure:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # Configurar Backend:" -ForegroundColor Gray
Write-Host "   cd 'c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\backend'" -ForegroundColor Gray
Write-Host "   poetry install" -ForegroundColor Gray
Write-Host "   poetry run uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Em outro terminal, configurar Frontend:" -ForegroundColor Gray
Write-Host "   cd 'c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\frontend'" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = Read-Host
