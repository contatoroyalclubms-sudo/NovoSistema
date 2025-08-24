# Script para iniciar o frontend
Write-Host "=== INICIANDO FRONTEND ===" -ForegroundColor Green

$FrontendPath = "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\frontend"

Write-Host "Navegando para diretório frontend..." -ForegroundColor Yellow
Set-Location $FrontendPath

# Verificar se dependências estão instaladas
if (!(Test-Path "node_modules")) {
    Write-Host "Instalando dependências do Frontend..." -ForegroundColor Yellow
    npm install
}

Write-Host "Executando Frontend na porta 5173..." -ForegroundColor Yellow
Write-Host "Acesse: http://localhost:5173" -ForegroundColor Cyan

npm run dev
