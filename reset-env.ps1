# Script para resetar completamente o ambiente de desenvolvimento
Write-Host "⚠️ ATENÇÃO: Este script irá resetar completamente o ambiente de desenvolvimento!" -ForegroundColor Red
$confirm = Read-Host "Tem certeza? (digite 'RESET' para confirmar)"

if ($confirm -ne "RESET") {
    Write-Host "❌ Reset cancelado" -ForegroundColor Red
    exit 1
}

Write-Host "🔄 Resetando ambiente..." -ForegroundColor Yellow

# Parar processos se estiverem rodando
Get-Process | Where-Object { $_.ProcessName -like "*uvicorn*" -or $_.ProcessName -like "*node*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Remover dados do banco
$env:PGPASSWORD = "eventos_2024_secure!"
psql -h localhost -U eventos_user -d eventos_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Reinstalar dependências do backend
Set-Location backend
poetry install --with dev
Set-Location ..

# Reinstalar dependências do frontend
Set-Location frontend
Remove-Item -Recurse -Force node_modules, package-lock.json -ErrorAction SilentlyContinue
npm install
Set-Location ..

Write-Host "✅ Ambiente resetado com sucesso!" -ForegroundColor Green
Write-Host "Execute .\start-dev.ps1 para iniciar novamente" -ForegroundColor Cyan
