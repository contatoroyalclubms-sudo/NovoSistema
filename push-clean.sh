#!/bin/bash
# Script para fazer push do branch limpo

echo "=== EXECUTANDO PUSH SEGURO ==="

# Verificar diretório atual
echo "Diretório atual:"
pwd

# Verificar status do Git
echo "Status do Git:"
git status

# Adicionar todos os arquivos
echo "Adicionando arquivos..."
git add .

# Fazer commit
echo "Fazendo commit..."
git commit -m "🔒 SECURITY: Complete backend without exposed keys

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
- CI/CD workflows configured"

# Fazer push
echo "Fazendo push para GitHub..."
git push -u origin clean-branch

echo "=== CONCLUÍDO ==="
echo "Verifique: https://github.com/contatoroyalclubms-sudo/NovoSistema"
