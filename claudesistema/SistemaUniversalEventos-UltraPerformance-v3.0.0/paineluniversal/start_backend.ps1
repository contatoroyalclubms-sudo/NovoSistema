# Script para iniciar o backend
param(
    [string]$Mode = "mock"  # "mock" para mock backend, "full" para backend completo
)

Write-Host "=== INICIANDO BACKEND ===" -ForegroundColor Green

$BackendPath = "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\backend"
$MockBackendPath = "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\mock-backend"

if ($Mode -eq "mock") {
    Write-Host "Iniciando Mock Backend (Node.js)..." -ForegroundColor Yellow
    Set-Location $MockBackendPath
    
    # Verificar se dependências estão instaladas
    if (!(Test-Path "node_modules")) {
        Write-Host "Instalando dependências do Mock Backend..." -ForegroundColor Yellow
        npm install
    }
    
    Write-Host "Executando Mock Backend na porta 8000..." -ForegroundColor Yellow
    npm start
}
else {
    Write-Host "Iniciando Backend FastAPI (Python)..." -ForegroundColor Yellow
    Set-Location $BackendPath
    
    # Ativar ambiente virtual Poetry
    Write-Host "Ativando ambiente Poetry..." -ForegroundColor Yellow
    poetry install
    
    Write-Host "Executando FastAPI na porta 8000..." -ForegroundColor Yellow
    poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}
