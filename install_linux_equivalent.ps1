# EQUIVALENTE WINDOWS DO SCRIPT LINUX FORNECIDO
# Baseado no script dnf/RHEL fornecido pelo usuario

Write-Host "=== INSTALACAO EQUIVALENTE AO SCRIPT LINUX ===" -ForegroundColor Green
Write-Host "Script baseado no codigo dnf/RHEL fornecido" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta executando como Admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (!$isAdmin) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Equivalente ao 'sudo' no Linux" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Como executar como Admin:" -ForegroundColor Yellow
    Write-Host "1. Win + X -> Terminal (Administrador)" -ForegroundColor Gray
    Write-Host "2. Execute este script novamente" -ForegroundColor Gray
    pause
    exit 1
}

Write-Host "OK - Executando como Administrador (equivalente ao sudo)" -ForegroundColor Green
Write-Host ""

# Funcao para verificar se comando existe
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# EQUIVALENTE: sudo dnf install epel-release -y
# No Windows: Instalar Chocolatey (gerenciador de pacotes)
Write-Host "INSTALANDO CHOCOLATEY (equivalente ao EPEL)..." -ForegroundColor Yellow
if (!(Test-CommandExists "choco")) {
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "OK - Chocolatey instalado (equivalente ao epel-release)" -ForegroundColor Green
        
        # Recarregar PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    }
    catch {
        Write-Host "ERRO ao instalar Chocolatey: $_" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "OK - Chocolatey ja instalado" -ForegroundColor Green
}

Write-Host ""

# EQUIVALENTE: sudo dnf install postgresql15-server postgresql15 -y
Write-Host "INSTALANDO POSTGRESQL 15+ (equivalente ao dnf install postgresql15)..." -ForegroundColor Yellow
if (!(Test-CommandExists "psql")) {
    try {
        choco install postgresql15 -y
        Write-Host "OK - PostgreSQL 15 instalado" -ForegroundColor Green
        
        # EQUIVALENTE: sudo postgresql-15-setup initdb + systemctl enable/start
        Write-Host "   Configurando PostgreSQL (equivalente ao initdb + systemctl)..." -ForegroundColor Cyan
        Start-Sleep -Seconds 3
        
        # Tentar iniciar servico PostgreSQL
        $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
        if ($pgService) {
            Start-Service $pgService.Name -ErrorAction SilentlyContinue
            Set-Service $pgService.Name -StartupType Automatic
            Write-Host "   OK - PostgreSQL iniciado e configurado para iniciar automaticamente" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "   Aviso: PostgreSQL pode precisar de configuracao manual" -ForegroundColor Yellow
    }
}
else {
    Write-Host "OK - PostgreSQL ja instalado" -ForegroundColor Green
}

Write-Host ""

# EQUIVALENTE: sudo dnf install python3.12 python3.12-pip -y
Write-Host "INSTALANDO PYTHON 3.12+ (equivalente ao dnf install python3.12)..." -ForegroundColor Yellow
if (!(Test-CommandExists "python")) {
    choco install python312 -y
    Write-Host "OK - Python 3.12 instalado (com pip incluido)" -ForegroundColor Green
}
else {
    Write-Host "OK - Python ja instalado" -ForegroundColor Green
}

Write-Host ""

# EQUIVALENTE: curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
#              sudo dnf install nodejs -y
Write-Host "INSTALANDO NODE.JS 20+ (equivalente ao setup NodeSource + dnf install)..." -ForegroundColor Yellow
if (!(Test-CommandExists "node")) {
    choco install nodejs-lts -y
    Write-Host "OK - Node.js 20+ LTS instalado" -ForegroundColor Green
}
else {
    Write-Host "OK - Node.js ja instalado" -ForegroundColor Green
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
        Write-Host "OK - Poetry instalado" -ForegroundColor Green
    }
    catch {
        Write-Host "Aviso: Erro ao instalar Poetry automaticamente" -ForegroundColor Yellow
        Write-Host "Alternativa: pip install poetry" -ForegroundColor Gray
    }
}
else {
    Write-Host "OK - Poetry ja instalado" -ForegroundColor Green
}

Write-Host ""

# EQUIVALENTE: echo "=== VERIFICANDO INSTALAÇÕES ==="
Write-Host "=== VERIFICANDO INSTALACOES ===" -ForegroundColor Green
Write-Host "Equivalente aos comandos de verificacao do script Linux" -ForegroundColor Cyan
Write-Host ""

# EQUIVALENTE AOS COMANDOS DE VERIFICACAO DO SCRIPT ORIGINAL:
# psql --version
# python3.12 --version  
# node --version
# npm --version
# poetry --version

$verificacoes = @(
    @{Nome = "PostgreSQL"; Comando = "psql --version" },
    @{Nome = "Python"; Comando = "python --version" },
    @{Nome = "Node.js"; Comando = "node --version" },
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
Write-Host "MAPEAMENTO LINUX -> WINDOWS:" -ForegroundColor Cyan
Write-Host "sudo dnf install epel-release    -> choco (Chocolatey)" -ForegroundColor Gray
Write-Host "sudo dnf install postgresql15    -> choco install postgresql15" -ForegroundColor Gray
Write-Host "sudo postgresql-15-setup initdb  -> Configuracao automatica Windows" -ForegroundColor Gray
Write-Host "sudo systemctl enable/start      -> Set-Service + Start-Service" -ForegroundColor Gray
Write-Host "sudo dnf install python3.12      -> choco install python312" -ForegroundColor Gray
Write-Host "curl NodeSource + dnf nodejs     -> choco install nodejs-lts" -ForegroundColor Gray
Write-Host "curl poetry installer | python   -> Invoke-WebRequest + python" -ForegroundColor Gray
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Feche este terminal Admin" -ForegroundColor Gray
Write-Host "2. Abra terminal normal e configure o projeto:" -ForegroundColor Gray
Write-Host "   cd paineluniversal/backend && poetry install" -ForegroundColor Gray
Write-Host "   cd paineluniversal/frontend && npm install" -ForegroundColor Gray

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = Read-Host
