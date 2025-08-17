# TESTE SIMPLIFICADO DO AMBIENTE
# Versao sem emojis para melhor compatibilidade

Write-Host "TESTANDO AMBIENTE DE DESENVOLVIMENTO..." -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# TESTE 1: VERIFICAR FERRAMENTAS INSTALADAS
Write-Host ""
Write-Host "1. VERIFICANDO FERRAMENTAS INSTALADAS:" -ForegroundColor Yellow

$tools = @("python", "node", "npm", "git", "psql", "poetry", "choco")

foreach ($tool in $tools) {
    Write-Host "$tool : " -NoNewline -ForegroundColor Yellow
    try {
        $result = cmd /c "$tool --version 2>nul"
        if ($LASTEXITCODE -eq 0 -and $result) {
            Write-Host "OK - $($result.Split("`n")[0])" -ForegroundColor Green
        } else {
            Write-Host "NAO ENCONTRADO" -ForegroundColor Red
        }
    } catch {
        Write-Host "ERRO" -ForegroundColor Red
    }
}

# TESTE 2: VERIFICAR SERVICOS POSTGRESQL
Write-Host ""
Write-Host "2. VERIFICANDO SERVICOS:" -ForegroundColor Yellow

try {
    $pgService = Get-Service postgresql* -ErrorAction SilentlyContinue
    if ($pgService) {
        $status = $pgService.Status
        Write-Host "PostgreSQL: $status" -ForegroundColor $(if ($status -eq "Running") { "Green" } else { "Yellow" })
        if ($status -ne "Running") {
            Write-Host "   Para iniciar: Start-Service $($pgService.Name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "PostgreSQL: SERVICO NAO ENCONTRADO" -ForegroundColor Red
    }
} catch {
    Write-Host "PostgreSQL: ERRO NA VERIFICACAO" -ForegroundColor Red
}

# TESTE 3: VERIFICAR CONEXAO POSTGRESQL
Write-Host ""
Write-Host "3. TESTANDO POSTGRESQL:" -ForegroundColor Yellow

try {
    $testResult = cmd /c "psql -U postgres -c `"SELECT version();`" 2>nul"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Conexao PostgreSQL: OK" -ForegroundColor Green
        
        # Verificar banco eventos_db
        $dbCheck = cmd /c "psql -U postgres -c `"\l`" 2>nul" | Select-String "eventos_db"
        if ($dbCheck) {
            Write-Host "Banco eventos_db: ENCONTRADO" -ForegroundColor Green
        } else {
            Write-Host "Banco eventos_db: NAO ENCONTRADO" -ForegroundColor Red
            Write-Host "   Execute: setup_postgresql_db.ps1" -ForegroundColor Gray
        }
    } else {
        Write-Host "Conexao PostgreSQL: FALHA" -ForegroundColor Red
        Write-Host "   Verifique se o servico esta rodando" -ForegroundColor Gray
    }
} catch {
    Write-Host "PostgreSQL: COMANDO PSQL NAO ENCONTRADO" -ForegroundColor Red
    Write-Host "   Adicione PostgreSQL ao PATH" -ForegroundColor Gray
}

# TESTE 4: VERIFICAR ESTRUTURA DO PROJETO
Write-Host ""
Write-Host "4. VERIFICANDO ESTRUTURA DO PROJETO:" -ForegroundColor Yellow

$projectPaths = @(
    "paineluniversal\backend\pyproject.toml",
    "paineluniversal\frontend\package.json",
    "paineluniversal\backend\app\main.py",
    "paineluniversal\frontend\src\App.tsx"
)

foreach ($path in $projectPaths) {
    if (Test-Path $path) {
        Write-Host "OK: $path" -ForegroundColor Green
    } else {
        Write-Host "FALTANDO: $path" -ForegroundColor Red
    }
}

# TESTE 5: VERIFICAR DEPENDENCIAS PYTHON
Write-Host ""
Write-Host "5. TESTANDO DEPENDENCIAS PYTHON:" -ForegroundColor Yellow

if (Test-Path "paineluniversal\backend") {
    Push-Location "paineluniversal\backend"
    
    try {
        $poetryResult = cmd /c "poetry check 2>nul"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Poetry: CONFIGURACAO VALIDA" -ForegroundColor Green
            
            if (Test-Path ".venv") {
                Write-Host "Ambiente virtual: ENCONTRADO" -ForegroundColor Green
            } else {
                Write-Host "Ambiente virtual: EXECUTE 'poetry install'" -ForegroundColor Orange
            }
        } else {
            Write-Host "Poetry: CONFIGURACAO INVALIDA" -ForegroundColor Red
        }
    } catch {
        Write-Host "Poetry: ERRO NA VERIFICACAO" -ForegroundColor Red
    }
    
    Pop-Location
} else {
    Write-Host "Diretorio backend: NAO ENCONTRADO" -ForegroundColor Red
}

# TESTE 6: VERIFICAR DEPENDENCIAS FRONTEND
Write-Host ""
Write-Host "6. TESTANDO DEPENDENCIAS FRONTEND:" -ForegroundColor Yellow

if (Test-Path "paineluniversal\frontend") {
    Push-Location "paineluniversal\frontend"
    
    if (Test-Path "node_modules") {
        Write-Host "Node modules: INSTALADOS" -ForegroundColor Green
    } else {
        Write-Host "Node modules: EXECUTE 'npm install'" -ForegroundColor Orange
    }
    
    if (Test-Path "package-lock.json") {
        Write-Host "Package lock: ENCONTRADO" -ForegroundColor Green
    } else {
        Write-Host "Package lock: EXECUTE 'npm install'" -ForegroundColor Orange
    }
    
    Pop-Location
} else {
    Write-Host "Diretorio frontend: NAO ENCONTRADO" -ForegroundColor Red
}

# RESUMO FINAL
Write-Host ""
Write-Host "RESUMO DO TESTE:" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan

Write-Host ""
Write-Host "PARA INICIAR O DESENVOLVIMENTO:" -ForegroundColor Green
Write-Host "1. Backend:  cd paineluniversal\backend && poetry install && poetry run uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "2. Frontend: cd paineluniversal\frontend && npm install && npm run dev" -ForegroundColor White
Write-Host "3. PostgreSQL: Certifique-se que o servico esta rodando" -ForegroundColor White

Write-Host ""
Write-Host "SCRIPTS DISPONIVEIS:" -ForegroundColor Blue
Write-Host "- install_as_admin.ps1: Instalar ferramentas (como admin)" -ForegroundColor White
Write-Host "- setup_postgresql_db.ps1: Configurar banco de dados" -ForegroundColor White
Write-Host "- postgresql_service_manager.ps1: Gerenciar servico PostgreSQL" -ForegroundColor White

Write-Host ""
Write-Host "TESTE CONCLUIDO!" -ForegroundColor Magenta
