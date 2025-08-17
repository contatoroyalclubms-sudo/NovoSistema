Write-Host "=== TESTE SIMPLES DE FERRAMENTAS ===" -ForegroundColor Green
Write-Host ""

# Teste 1: Python
Write-Host "PYTHON:" -NoNewline -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK - $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host " NAO ENCONTRADO" -ForegroundColor Red
    }
} catch {
    Write-Host " ERRO" -ForegroundColor Red
}

# Teste 2: Node.js
Write-Host "NODE.JS:" -NoNewline -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK - $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host " NAO ENCONTRADO" -ForegroundColor Red
    }
} catch {
    Write-Host " ERRO" -ForegroundColor Red
}

# Teste 3: NPM
Write-Host "NPM:" -NoNewline -ForegroundColor Yellow
try {
    $npmVersion = npm --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK - $npmVersion" -ForegroundColor Green
    } else {
        Write-Host " NAO ENCONTRADO" -ForegroundColor Red
    }
} catch {
    Write-Host " ERRO" -ForegroundColor Red
}

# Teste 4: Git
Write-Host "GIT:" -NoNewline -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK - $gitVersion" -ForegroundColor Green
    } else {
        Write-Host " NAO ENCONTRADO" -ForegroundColor Red
    }
} catch {
    Write-Host " ERRO" -ForegroundColor Red
}

# Teste 5: PostgreSQL
Write-Host "POSTGRESQL:" -NoNewline -ForegroundColor Yellow
try {
    $psqlVersion = psql --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK - $psqlVersion" -ForegroundColor Green
    } else {
        Write-Host " NAO ENCONTRADO" -ForegroundColor Red
    }
} catch {
    Write-Host " ERRO" -ForegroundColor Red
}

# Teste 6: Poetry
Write-Host "POETRY:" -NoNewline -ForegroundColor Yellow
try {
    $poetryVersion = poetry --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK - $poetryVersion" -ForegroundColor Green
    } else {
        Write-Host " NAO ENCONTRADO" -ForegroundColor Red
    }
} catch {
    Write-Host " ERRO" -ForegroundColor Red
}

# Teste 7: Chocolatey
Write-Host "CHOCOLATEY:" -NoNewline -ForegroundColor Yellow
try {
    $chocoVersion = choco --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK - $chocoVersion" -ForegroundColor Green
    } else {
        Write-Host " NAO ENCONTRADO" -ForegroundColor Red
    }
} catch {
    Write-Host " ERRO" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== TESTE CONCLUIDO ===" -ForegroundColor Green
