# Script para iniciar o sistema em modo desenvolvimento
param([switch]$NoFrontend, [switch]$NoBackend)

Write-Host "🚀 Iniciando Sistema de Gestão de Eventos em modo desenvolvimento..." -ForegroundColor Blue

# Verificar se PostgreSQL está rodando
try {
    $env:PGPASSWORD = "eventos_2024_secure!"
    psql -h localhost -U eventos_user -d eventos_db -c "SELECT 1;" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL não acessível"
    }
}
catch {
    Write-Host "❌ PostgreSQL não está rodando. Inicie o serviço primeiro." -ForegroundColor Red
    exit 1
}

# Iniciar Backend
if (-not $NoBackend) {
    Write-Host "🐍 Iniciando Backend (FastAPI)..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; poetry run uvicorn app.main:app --reload"
    Start-Sleep 3
}

# Iniciar Frontend  
if (-not $NoFrontend) {
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
