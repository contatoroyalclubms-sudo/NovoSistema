# Script para verificar e instalar ferramentas no Windows
# Execute este script no PowerShell como Administrador

Write-Host "=== INSTALAÇÃO DE FERRAMENTAS PARA O PROJETO ===" -ForegroundColor Green
Write-Host ""

# 1. Instalar Chocolatey (gerenciador de pacotes para Windows)
Write-Host "1. INSTALANDO CHOCOLATEY..." -ForegroundColor Yellow
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Instalando Chocolatey..." -ForegroundColor Cyan
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Host "Chocolatey instalado!" -ForegroundColor Green
}
else {
    Write-Host "Chocolatey já está instalado!" -ForegroundColor Green
}

# 2. Instalar Python 3.12+
Write-Host ""
Write-Host "2. INSTALANDO PYTHON 3.12..." -ForegroundColor Yellow
choco install python312 -y

# 3. Instalar Node.js 20+
Write-Host ""
Write-Host "3. INSTALANDO NODE.JS 20..." -ForegroundColor Yellow
choco install nodejs -y

# 4. Instalar PostgreSQL
Write-Host ""
Write-Host "4. INSTALANDO POSTGRESQL..." -ForegroundColor Yellow
choco install postgresql --params '/Password:postgres123' -y

# 5. Instalar Git
Write-Host ""
Write-Host "5. INSTALANDO GIT..." -ForegroundColor Yellow
choco install git -y

# 6. Instalar ferramentas adicionais
Write-Host ""
Write-Host "6. INSTALANDO FERRAMENTAS ADICIONAIS..." -ForegroundColor Yellow
choco install curl wget -y

# 7. Instalar Poetry (após Python estar disponível)
Write-Host ""
Write-Host "7. INSTALANDO POETRY..." -ForegroundColor Yellow
Write-Host "Aguarde o Python ser reconhecido no PATH..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Recarregar o PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Instalar Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

Write-Host ""
Write-Host "=== VERIFICANDO INSTALAÇÕES ===" -ForegroundColor Green
Write-Host ""

# Verificar versões
Write-Host "Python:" -ForegroundColor Yellow
python --version

Write-Host "Node.js:" -ForegroundColor Yellow
node --version

Write-Host "NPM:" -ForegroundColor Yellow
npm --version

Write-Host "PostgreSQL:" -ForegroundColor Yellow
psql --version

Write-Host "Git:" -ForegroundColor Yellow
git --version

Write-Host "Poetry:" -ForegroundColor Yellow
poetry --version

Write-Host ""
Write-Host "=== INSTALAÇÃO CONCLUÍDA ===" -ForegroundColor Green
Write-Host "Reinicie o terminal para garantir que todas as ferramentas estejam disponíveis." -ForegroundColor Cyan
