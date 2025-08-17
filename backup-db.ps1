# Script para backup do banco de dados
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "backup_eventos_$date.sql"

Write-Host "🗄️ Criando backup do banco de dados..." -ForegroundColor Blue

# Criar diretório de backups se não existir
if (-not (Test-Path "backups")) {
    New-Item -ItemType Directory -Path "backups"
}

$env:PGPASSWORD = "eventos_2024_secure!"
pg_dump -h localhost -U eventos_user -d eventos_db | Out-File -FilePath "backups\$backupFile" -Encoding utf8

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backup criado: backups\$backupFile" -ForegroundColor Green
}
else {
    Write-Host "❌ Erro ao criar backup" -ForegroundColor Red
    exit 1
}
