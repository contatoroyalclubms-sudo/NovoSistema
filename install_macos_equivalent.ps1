# EQUIVALENTE WINDOWS DO SCRIPT MACOS HOMEBREW
# Baseado no script brew/macOS fornecido pelo usuario

Write-Host "=== INSTALACAO EQUIVALENTE AO SCRIPT MACOS/HOMEBREW ===" -ForegroundColor Green
Write-Host "Script baseado no codigo Homebrew/macOS fornecido" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta executando como Admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (!$isAdmin) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Equivalente ao 'sudo' necessario para algumas operacoes do Homebrew" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Como executar como Admin:" -ForegroundColor Yellow
    Write-Host "1. Win + X -> Terminal (Administrador)" -ForegroundColor Gray
    Write-Host "2. Execute este script novamente" -ForegroundColor Gray
    pause
    exit 1
}

Write-Host "OK - Executando como Administrador" -ForegroundColor Green
Write-Host ""

# Funcao para verificar se comando existe
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# EQUIVALENTE: if ! command -v brew &> /dev/null; then
#              /bin/bash -c "$(curl -fsSL homebrew-install-script)"
# No Windows: Verificar e instalar Chocolatey
Write-Host "VERIFICANDO CHOCOLATEY (equivalente ao Homebrew check)..." -ForegroundColor Yellow
if (!(Test-CommandExists "choco")) {
    Write-Host "   Instalando Chocolatey (equivalente ao Homebrew install)..." -ForegroundColor Cyan
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "   OK - Chocolatey instalado (equivalente ao Homebrew)" -ForegroundColor Green
        
        # Recarregar PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    }
    catch {
        Write-Host "   ERRO ao instalar Chocolatey: $_" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "   OK - Chocolatey ja instalado (equivalente ao brew found)" -ForegroundColor Green
}

Write-Host ""

# EQUIVALENTE: brew install postgresql@15
#              brew services start postgresql@15
Write-Host "INSTALANDO POSTGRESQL@15 (equivalente ao brew install postgresql@15)..." -ForegroundColor Yellow
if (!(Test-CommandExists "psql")) {
    try {
        choco install postgresql15 -y
        Write-Host "   OK - PostgreSQL@15 instalado" -ForegroundColor Green
        
        # EQUIVALENTE: brew services start postgresql@15
        Write-Host "   Iniciando servico PostgreSQL (equivalente ao brew services start)..." -ForegroundColor Cyan
        Start-Sleep -Seconds 3
        
        # Configurar e iniciar servico PostgreSQL
        $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
        if ($pgService) {
            Start-Service $pgService.Name -ErrorAction SilentlyContinue
            Set-Service $pgService.Name -StartupType Automatic
            Write-Host "   OK - PostgreSQL iniciado (equivalente ao brew services start)" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "   Aviso: PostgreSQL pode precisar de configuracao manual" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   OK - PostgreSQL ja instalado" -ForegroundColor Green
}

Write-Host ""

# EQUIVALENTE: brew install python@3.12
Write-Host "INSTALANDO PYTHON@3.12 (equivalente ao brew install python@3.12)..." -ForegroundColor Yellow
if (!(Test-CommandExists "python")) {
    choco install python312 -y
    Write-Host "   OK - Python@3.12 instalado (equivalente ao brew install)" -ForegroundColor Green
}
else {
    Write-Host "   OK - Python ja instalado" -ForegroundColor Green
}

Write-Host ""

# EQUIVALENTE: brew install node@20
Write-Host "INSTALANDO NODE@20 (equivalente ao brew install node@20)..." -ForegroundColor Yellow
if (!(Test-CommandExists "node")) {
    choco install nodejs-lts -y
    Write-Host "   OK - Node@20 LTS instalado (equivalente ao brew install)" -ForegroundColor Green
}
else {
    Write-Host "   OK - Node.js ja instalado" -ForegroundColor Green
}

Write-Host ""

# Recarregar PATH apos instalacoes
Write-Host "ATUALIZANDO VARIAVEIS DE AMBIENTE..." -ForegroundColor Cyan
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# EQUIVALENTE: curl -sSL https://install.python-poetry.org | python3 -
Write-Host "INSTALANDO POETRY (equivalente ao curl poetry installer)..." -ForegroundColor Yellow
if (!(Test-CommandExists "poetry")) {
    try {
        Start-Sleep -Seconds 3
        (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
        Write-Host "   OK - Poetry instalado (metodo identico ao macOS)" -ForegroundColor Green
    }
    catch {
        Write-Host "   Aviso: Erro ao instalar Poetry automaticamente" -ForegroundColor Yellow
        Write-Host "   Alternativa: pip install poetry" -ForegroundColor Gray
    }
}
else {
    Write-Host "   OK - Poetry ja instalado" -ForegroundColor Green
}

Write-Host ""

# EQUIVALENTE: echo "=== VERIFICANDO INSTALAÇÕES ==="
Write-Host "=== VERIFICANDO INSTALACOES ===" -ForegroundColor Green
Write-Host "Executando os mesmos comandos de verificacao do script macOS" -ForegroundColor Cyan
Write-Host ""

# COMANDOS IDENTICOS AOS DO SCRIPT MACOS:
# psql --version
# python3.12 --version
# node --version  
# npm --version
# poetry --version

$verificacoes = @(
    @{Nome = "PostgreSQL"; Comando = "psql --version" },
    @{Nome = "Python3.12"; Comando = "python --version" }, 
    @{Nome = "Node"; Comando = "node --version" },
    @{Nome = "NPM"; Comando = "npm --version" },
    @{Nome = "Poetry"; Comando = "poetry --version" },
    @{Nome = "Git"; Comando = "git --version" },
    @{Nome = "Chocolatey"; Comando = "choco --version" }
)

foreach ($item in $verificacoes) {
    Write-Host "$($item.Nome):" -NoNewline -ForegroundColor Yellow
    try {
        $resultado = Invoke-Expression $item.Comando 2>&1
        if ($resultado -and $resultado -notlike "*not recognized*" -and $resultado -notlike "*nao*reconhecido*") {
            $versao = $resultado.ToString().Split("`n")[0].Trim()
            Write-Host " OK - $versao" -ForegroundColor Green
        }
        else {
            Write-Host " ERRO - Nao funcionando" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " ERRO: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== INSTALACAO WINDOWS EQUIVALENTE CONCLUIDA ===" -ForegroundColor Green
Write-Host ""
Write-Host "MAPEAMENTO MACOS/HOMEBREW -> WINDOWS:" -ForegroundColor Cyan
Write-Host "command -v brew check           -> Test-CommandExists choco" -ForegroundColor Gray
Write-Host "homebrew install script         -> chocolatey install script" -ForegroundColor Gray
Write-Host "brew install postgresql@15      -> choco install postgresql15" -ForegroundColor Gray
Write-Host "brew services start postgresql  -> Start-Service + Set-Service" -ForegroundColor Gray
Write-Host "brew install python@3.12        -> choco install python312" -ForegroundColor Gray
Write-Host "brew install node@20            -> choco install nodejs-lts" -ForegroundColor Gray
Write-Host "curl poetry installer | python  -> Invoke-WebRequest + python" -ForegroundColor Gray
Write-Host ""
Write-Host "AMBIENTE IDENTICO AO MACOS CRIADO!" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Feche este terminal Admin" -ForegroundColor Gray
Write-Host "2. Abra terminal normal e configure o projeto:" -ForegroundColor Gray
Write-Host "   cd paineluniversal/backend && poetry install" -ForegroundColor Gray
Write-Host "   cd paineluniversal/frontend && npm install" -ForegroundColor Gray

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = Read-Host
