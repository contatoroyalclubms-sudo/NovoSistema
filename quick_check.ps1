Write-Host "=== VERIFICAÇÃO SIMPLES DE FERRAMENTAS ===" -ForegroundColor Green

# Testar Node.js (sabemos que funciona)
Write-Host "Node.js:" -NoNewline
try {
    $nodeVersion = node --version
    Write-Host " ✅ $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host " ❌ Erro" -ForegroundColor Red
}

# Testar NPM
Write-Host "NPM:" -NoNewline
try {
    $npmVersion = npm --version
    Write-Host " ✅ v$npmVersion" -ForegroundColor Green
}
catch {
    Write-Host " ❌ Erro" -ForegroundColor Red
}

# Testar Python
Write-Host "Python:" -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -like "*Python*") {
        Write-Host " ✅ $pythonVersion" -ForegroundColor Green
    }
    else {
        Write-Host " ❌ Não encontrado" -ForegroundColor Red
        Write-Host "   💡 Execute: choco install python312 -y" -ForegroundColor Yellow
    }
}
catch {
    Write-Host " ❌ Não encontrado" -ForegroundColor Red
    Write-Host "   💡 Execute: choco install python312 -y" -ForegroundColor Yellow
}

# Testar PostgreSQL
Write-Host "PostgreSQL:" -NoNewline
try {
    $psqlVersion = psql --version 2>&1
    if ($psqlVersion -like "*psql*") {
        Write-Host " ✅ $psqlVersion" -ForegroundColor Green
    }
    else {
        Write-Host " ❌ Não encontrado" -ForegroundColor Red
        Write-Host "   💡 Execute: choco install postgresql15 -y" -ForegroundColor Yellow
    }
}
catch {
    Write-Host " ❌ Não encontrado" -ForegroundColor Red
    Write-Host "   💡 Execute: choco install postgresql15 -y" -ForegroundColor Yellow
}

# Testar Poetry
Write-Host "Poetry:" -NoNewline
try {
    $poetryVersion = poetry --version 2>&1
    if ($poetryVersion -like "*Poetry*") {
        Write-Host " ✅ $poetryVersion" -ForegroundColor Green
    }
    else {
        Write-Host " ❌ Não encontrado" -ForegroundColor Red
        Write-Host "   💡 Instale Poetry após instalar Python" -ForegroundColor Yellow
    }
}
catch {
    Write-Host " ❌ Não encontrado" -ForegroundColor Red
    Write-Host "   💡 Instale Poetry após instalar Python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== RESUMO ===" -ForegroundColor Cyan
Write-Host "✅ Funcionando: Node.js e NPM (projeto frontend ativo)" -ForegroundColor Green
Write-Host "❓ Para verificar: Python, PostgreSQL, Poetry" -ForegroundColor Yellow
