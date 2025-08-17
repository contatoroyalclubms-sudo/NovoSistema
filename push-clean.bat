@echo off
REM Script para fazer push do branch limpo no Windows

echo === EXECUTANDO PUSH SEGURO ===

REM Verificar diretório atual
echo Diretório atual:
cd

REM Verificar status do Git
echo Status do Git:
git status

REM Adicionar todos os arquivos
echo Adicionando arquivos...
git add .

REM Fazer commit
echo Fazendo commit...
git commit -m "🔒 SECURITY: Complete backend without exposed keys - ✨ Features: Complete WhatsApp router (602 lines), Complete Listas router (177 lines), Complete N8N automation router (658 lines), Complete backend routers, Enhanced security, PostgreSQL integration, Docker configs - 🛡️ Security: Removed all exposed OpenAI API keys, Added gitignore protection, Clean commit history"

REM Fazer push
echo Fazendo push para GitHub...
git push -u origin clean-branch

echo === CONCLUÍDO ===
echo Verifique: https://github.com/contatoroyalclubms-sudo/NovoSistema
pause
