#!/usr/bin/env pwsh

Write-Host "=== INSTALAÇÃO AUTOMÁTICA DE FERRAMENTAS - WINDOWS ===" -ForegroundColor Green
Write-Host "Baseado nos scripts para CentOS/RHEL/Rocky, macOS e Windows fornecidos" -ForegroundColor Cyan
Write-Host ""

# Função para verificar comando
function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Função para instalar ferramenta via Chocolatey
function Install-Tool {
    param([string]$Package, [string]$Name)
    Write-Host "📦 Instalando $Name..." -ForegroundColor Yellow
    try {
        choco install $Package -y
        Write-Host "  ✅ $Name instalado com sucesso!" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Erro ao instalar $Name" -ForegroundColor Red
    }
}

# 1. INSTALAR CHOCOLATEY (equivalente ao Homebrew no macOS)
Write-Host "🍫 CHOCOLATEY (Gerenciador de Pacotes):" -ForegroundColor Yellow
if (!(Test-Command "choco")) {
    Write-Host "  📥 Instalando Chocolatey..." -ForegroundColor Cyan
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "  ✅ Chocolatey instalado com sucesso!" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Erro ao instalar Chocolatey" -ForegroundColor Red
        exit 1
    }
}
else {
    $chocoVersion = choco --version 2>&1
    Write-Host "  ✅ Chocolatey já instalado: v$chocoVersion" -ForegroundColor Green
}

Write-Host ""

# 2. INSTALAR POSTGRESQL 15+ (equivalente aos scripts Linux/macOS)
Write-Host "� POSTGRESQL 15+:" -ForegroundColor Yellow
if (!(Test-Command "psql")) {
    Install-Tool "postgresql15" "PostgreSQL 15"
    Write-Host "  🔧 Configurando PostgreSQL..." -ForegroundColor Cyan
    Write-Host "  💡 Senha padrão será configurada como 'postgres'" -ForegroundColor Gray
}
else {
    try {
        $psqlVersion = psql --version 2>&1
        Write-Host "  ✅ PostgreSQL já instalado: $psqlVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "  ⚠️  PostgreSQL encontrado mas com problemas de configuração" -ForegroundColor Yellow
    }
}

Write-Host ""

# 3. INSTALAR PYTHON 3.12+ (equivalente aos scripts Linux/macOS)
Write-Host "� PYTHON 3.12+:" -ForegroundColor Yellow
if (!(Test-Command "python")) {
    Install-Tool "python312" "Python 3.12"
    Write-Host "  🔄 Atualizando PATH..." -ForegroundColor Cyan
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}
else {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "  ✅ Python já instalado: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Erro ao obter versão do Python" -ForegroundColor Red
    }
}

Write-Host ""

# 4. INSTALAR NODE.JS 20+ (equivalente aos scripts Linux/macOS)
Write-Host "🟢 NODE.JS 20+:" -ForegroundColor Yellow
if (!(Test-Command "node")) {
    Install-Tool "nodejs-lts" "Node.js LTS"
}
else {
    try {
        $nodeVersion = node --version 2>&1
        Write-Host "  ✅ Node.js já instalado: $nodeVersion" -ForegroundColor Green
        $npmVersion = npm --version 2>&1
        Write-Host "  ✅ NPM já instalado: v$npmVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Erro ao obter versão do Node.js" -ForegroundColor Red
    }
}

Write-Host ""

# 5. INSTALAR POETRY (equivalente aos scripts Linux/macOS)
Write-Host "📝 POETRY:" -ForegroundColor Yellow
if (!(Test-Command "poetry")) {
    Write-Host "  📥 Instalando Poetry..." -ForegroundColor Cyan
    try {
        # Garantir que Python está disponível
        Start-Sleep -Seconds 2
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        
        (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
        Write-Host "  ✅ Poetry instalado com sucesso!" -ForegroundColor Green
        Write-Host "  💡 Reinicie o terminal para usar o Poetry" -ForegroundColor Gray
    }
    catch {
        Write-Host "  ❌ Erro ao instalar Poetry" -ForegroundColor Red
        Write-Host "  💡 Instale manualmente: pip install poetry" -ForegroundColor Gray
    }
}
else {
    try {
        $poetryVersion = poetry --version 2>&1
        Write-Host "  ✅ Poetry já instalado: $poetryVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Erro ao obter versão do Poetry" -ForegroundColor Red
    }
}

Write-Host ""

# 6. INSTALAR GIT (se não estiver instalado)
Write-Host "🔧 GIT:" -ForegroundColor Yellow
if (!(Test-Command "git")) {
    Install-Tool "git" "Git"
}
else {
    try {
        $gitVersion = git --version 2>&1
        Write-Host "  ✅ Git já instalado: $gitVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Erro ao obter versão do Git" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== VERIFICAÇÃO FINAL DAS INSTALAÇÕES ===" -ForegroundColor Green
Write-Host ""

# Verificação final
Write-Host "🔍 Verificando todas as ferramentas..." -ForegroundColor Cyan
Write-Host ""

$tools = @(
    @{Name = "Python"; Command = "python"; Flag = "--version" },
    @{Name = "Node.js"; Command = "node"; Flag = "--version" },
    @{Name = "NPM"; Command = "npm"; Flag = "--version" },
    @{Name = "PostgreSQL"; Command = "psql"; Flag = "--version" },
    @{Name = "Poetry"; Command = "poetry"; Flag = "--version" },
    @{Name = "Git"; Command = "git"; Flag = "--version" },
    @{Name = "Chocolatey"; Command = "choco"; Flag = "--version" }
)

$allInstalled = $true

foreach ($tool in $tools) {
    Write-Host "$($tool.Name):" -ForegroundColor Yellow -NoNewline
    if (Test-Command $tool.Command) {
        try {
            $version = & $tool.Command $tool.Flag 2>&1
            Write-Host " ✅ $version" -ForegroundColor Green
        }
        catch {
            Write-Host " ⚠️  Instalado mas com problemas" -ForegroundColor Yellow
            $allInstalled = $false
        }
    }
    else {
        Write-Host " ❌ Não encontrado" -ForegroundColor Red
        $allInstalled = $false
    }
}

Write-Host ""

if ($allInstalled) {
    Write-Host "🎉 TODAS AS FERRAMENTAS INSTALADAS COM SUCESSO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 PRÓXIMOS PASSOS PARA CONFIGURAR O PROJETO:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Configurar Backend Python:" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor Gray
    Write-Host "   poetry install" -ForegroundColor Gray
    Write-Host "   poetry run python create_financeiro_tables.py" -ForegroundColor Gray
    Write-Host "   poetry run python seed_financeiro_data.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Configurar Frontend React:" -ForegroundColor Yellow
    Write-Host "   cd frontend" -ForegroundColor Gray
    Write-Host "   npm install" -ForegroundColor Gray
    Write-Host "   npm run dev" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Iniciar PostgreSQL:" -ForegroundColor Yellow
    Write-Host "   # PostgreSQL será iniciado automaticamente" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Executar Backend:" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor Gray
    Write-Host "   poetry run uvicorn app.main:app --reload" -ForegroundColor Gray
}
else {
    Write-Host "⚠️  Algumas ferramentas não foram instaladas corretamente." -ForegroundColor Yellow
    Write-Host "💡 Reinicie o PowerShell como Administrador e execute este script novamente." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== INSTALAÇÃO CONCLUÍDA ===" -ForegroundColor Green
Write-Host "💡 DICA: Reinicie o terminal para garantir que todas as variáveis de ambiente estejam atualizadas." -ForegroundColor Gray
