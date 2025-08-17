# Script PowerShell para fazer push do branch limpo

Write-Host "=== EXECUTANDO PUSH SEGURO ===" -ForegroundColor Green

# Verificar diretório atual
Write-Host "Diretório atual:" -ForegroundColor Yellow
Get-Location

# Verificar status do Git
Write-Host "Status do Git:" -ForegroundColor Yellow
git status

# Adicionar todos os arquivos
Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
git add .

# Fazer commit
Write-Host "Fazendo commit..." -ForegroundColor Yellow
git commit -m @"
🔒 SECURITY: Complete backend without exposed keys

✨ Features:
- Complete WhatsApp router implementation (602 lines)
- Complete Listas/tickets router (177 lines) 
- Complete N8N automation router (658 lines)
- Complete Transações/payments router
- Complete Usuários/auth router
- Enhanced security with proper API key management
- PostgreSQL integration scripts
- Docker configurations
- Development environment setup

🛡️ Security:
- Removed all exposed OpenAI API keys
- Added .gitignore protection for credentials  
- Clean commit history without sensitive data

📁 Project Structure:
- Backend FastAPI with complete routers
- Frontend React with modern UI
- Database PostgreSQL integration
- Docker containerization ready
- CI/CD workflows configured
"@

# Fazer push
Write-Host "Fazendo push para GitHub..." -ForegroundColor Yellow
git push -u origin clean-branch

Write-Host "=== CONCLUÍDO ===" -ForegroundColor Green
Write-Host "Verifique: https://github.com/contatoroyalclubms-sudo/NovoSistema" -ForegroundColor Cyan

Read-Host "Pressione Enter para continuar"
