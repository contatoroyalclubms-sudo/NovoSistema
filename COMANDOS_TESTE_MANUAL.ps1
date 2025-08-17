# ===================================================
# COMANDOS PARA TESTAR O AMBIENTE MANUALMENTE
# ===================================================
# Copie e execute estes comandos um por vez no terminal

# 1. VERIFICAR FERRAMENTAS
Write-Host "=== TESTE DE FERRAMENTAS ===" -ForegroundColor Green
python --version
node --version  
npm --version
git --version
psql --version
poetry --version
choco --version

# 2. VERIFICAR SERVICOS
Write-Host "`n=== VERIFICAR SERVICOS ===" -ForegroundColor Green
Get-Service postgresql*

# 3. TESTAR POSTGRESQL
Write-Host "`n=== TESTAR POSTGRESQL ===" -ForegroundColor Green
psql -U postgres -c "SELECT version();"

# 4. LISTAR BANCOS
Write-Host "`n=== LISTAR BANCOS ===" -ForegroundColor Green  
psql -U postgres -c "\l"

# 5. VERIFICAR ESTRUTURA
Write-Host "`n=== ESTRUTURA DO PROJETO ===" -ForegroundColor Green
Test-Path "paineluniversal\backend\pyproject.toml"
Test-Path "paineluniversal\frontend\package.json" 
Test-Path "paineluniversal\backend\app\main.py"
Test-Path "paineluniversal\frontend\src\App.tsx"

# 6. VERIFICAR DEPENDENCIAS
Write-Host "`n=== DEPENDENCIAS ===" -ForegroundColor Green
Test-Path "paineluniversal\frontend\node_modules"
Test-Path "paineluniversal\backend\.venv"

# 7. SE PRECISAR INSTALAR DEPENDENCIAS:
Write-Host "`n=== COMANDOS DE INSTALACAO ===" -ForegroundColor Yellow
Write-Host "Frontend: cd paineluniversal\frontend && npm install" -ForegroundColor Gray
Write-Host "Backend:  cd paineluniversal\backend && poetry install" -ForegroundColor Gray

# 8. PARA INICIAR O DESENVOLVIMENTO:
Write-Host "`n=== INICIAR DESENVOLVIMENTO ===" -ForegroundColor Blue
Write-Host "Terminal 1 - Backend:" -ForegroundColor Gray
Write-Host "  cd paineluniversal\backend" -ForegroundColor Gray
Write-Host "  poetry run uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "" -ForegroundColor Gray
Write-Host "Terminal 2 - Frontend:" -ForegroundColor Gray  
Write-Host "  cd paineluniversal\frontend" -ForegroundColor Gray
Write-Host "  npm run dev" -ForegroundColor Gray
Write-Host "" -ForegroundColor Gray
Write-Host "Acesse: http://localhost:5173" -ForegroundColor Gray
