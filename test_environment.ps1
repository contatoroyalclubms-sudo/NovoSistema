# TESTE DO SISTEMA DE DESENVOLVIMENTO
# Verificacao completa do ambiente configurado

Write-Host "🔍 TESTANDO AMBIENTE DE DESENVOLVIMENTO..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# TESTE 1: VERIFICAR FERRAMENTAS INSTALADAS
Write-Host "`n📋 1. VERIFICANDO FERRAMENTAS INSTALADAS:" -ForegroundColor Yellow

$tools = @{
    "Python" = { python --version }
    "Node.js" = { node --version }
    "Poetry" = { poetry --version }
    "Git" = { git --version }
    "PostgreSQL" = { psql --version }
}

foreach ($tool in $tools.Keys) {
    try {
        $version = & $tools[$tool] 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $tool`: $version" -ForegroundColor Green
        } else {
            Write-Host "❌ $tool`: Nao encontrado" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ $tool`: Erro na verificacao" -ForegroundColor Red
    }
}

# TESTE 2: VERIFICAR SERVICOS
Write-Host "`n🔧 2. VERIFICANDO SERVICOS:" -ForegroundColor Yellow

try {
    $pgService = Get-Service postgresql* -ErrorAction SilentlyContinue
    if ($pgService) {
        $status = $pgService.Status
        if ($status -eq "Running") {
            Write-Host "✅ PostgreSQL: $status" -ForegroundColor Green
        } else {
            Write-Host "⚠️  PostgreSQL: $status (tente: Start-Service $($pgService.Name))" -ForegroundColor Orange
        }
    } else {
        Write-Host "❌ PostgreSQL: Servico nao encontrado" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ PostgreSQL: Erro na verificacao do servico" -ForegroundColor Red
}

# TESTE 3: TESTAR CONEXAO POSTGRESQL
Write-Host "`n🐘 3. TESTANDO POSTGRESQL:" -ForegroundColor Yellow

# Tentar conectar como postgres
try {
    $testQuery = "SELECT version();"
    $result = psql -U postgres -c $testQuery 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Conexao PostgreSQL (postgres): OK" -ForegroundColor Green
        
        # Verificar se banco eventos_db existe
        $dbCheck = psql -U postgres -c "\l" 2>$null | Select-String "eventos_db"
        if ($dbCheck) {
            Write-Host "✅ Banco eventos_db: Encontrado" -ForegroundColor Green
            
            # Testar conexao com eventos_user
            $env:PGPASSWORD = 'eventos_2024_secure!'
            $userTest = psql -h localhost -U eventos_user -d eventos_db -c "SELECT current_user;" 2>$null
            Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Usuario eventos_user: OK" -ForegroundColor Green
            } else {
                Write-Host "❌ Usuario eventos_user: Falha na conexao" -ForegroundColor Red
                Write-Host "   Execute: setup_postgresql_db.ps1" -ForegroundColor Gray
            }
        } else {
            Write-Host "❌ Banco eventos_db: Nao encontrado" -ForegroundColor Red
            Write-Host "   Execute: setup_postgresql_db.ps1" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Conexao PostgreSQL: Falha" -ForegroundColor Red
        Write-Host "   Verifique se o servico esta rodando" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ PostgreSQL: Comando psql nao encontrado" -ForegroundColor Red
    Write-Host "   Adicione PostgreSQL ao PATH" -ForegroundColor Gray
}

# TESTE 4: VERIFICAR ESTRUTURA DO PROJETO
Write-Host "`n📁 4. VERIFICANDO ESTRUTURA DO PROJETO:" -ForegroundColor Yellow

$projectPaths = @(
    "paineluniversal\backend\pyproject.toml",
    "paineluniversal\frontend\package.json",
    "paineluniversal\backend\app\main.py",
    "paineluniversal\frontend\src\App.tsx"
)

foreach ($path in $projectPaths) {
    if (Test-Path $path) {
        Write-Host "✅ $path" -ForegroundColor Green
    } else {
        Write-Host "❌ $path" -ForegroundColor Red
    }
}

# TESTE 5: TESTAR DEPENDENCIAS PYTHON
Write-Host "`n🐍 5. TESTANDO DEPENDENCIAS PYTHON:" -ForegroundColor Yellow

if (Test-Path "paineluniversal\backend") {
    Push-Location "paineluniversal\backend"
    
    try {
        $poetryCheck = poetry check 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Poetry: Configuracao valida" -ForegroundColor Green
            
            # Verificar se dependencias estao instaladas
            $poetryShow = poetry show 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Dependencias: Instaladas" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Dependencias: Execute 'poetry install'" -ForegroundColor Orange
            }
        } else {
            Write-Host "❌ Poetry: Configuracao invalida" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Poetry: Erro na verificacao" -ForegroundColor Red
    }
    
    Pop-Location
}

# TESTE 6: TESTAR DEPENDENCIAS FRONTEND
Write-Host "`n⚛️  6. TESTANDO DEPENDENCIAS FRONTEND:" -ForegroundColor Yellow

if (Test-Path "paineluniversal\frontend") {
    Push-Location "paineluniversal\frontend"
    
    if (Test-Path "node_modules") {
        Write-Host "✅ Node modules: Instalados" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Node modules: Execute 'npm install'" -ForegroundColor Orange
    }
    
    if (Test-Path "package-lock.json") {
        Write-Host "✅ Package lock: Encontrado" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Package lock: Execute 'npm install'" -ForegroundColor Orange
    }
    
    Pop-Location
}

# RESUMO FINAL
Write-Host "`n🎯 RESUMO DO TESTE:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

Write-Host "`n🚀 PARA INICIAR O DESENVOLVIMENTO:" -ForegroundColor Green
Write-Host "1. Backend:  cd paineluniversal\backend && poetry install && poetry run uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "2. Frontend: cd paineluniversal\frontend && npm install && npm run dev" -ForegroundColor White
Write-Host "3. PostgreSQL: Certifique-se que o servico esta rodando" -ForegroundColor White

Write-Host "`n📚 SCRIPTS DISPONIVEIS:" -ForegroundColor Blue
Write-Host "- install_final.ps1: Instalar ferramentas de desenvolvimento" -ForegroundColor White
Write-Host "- setup_postgresql_db.ps1: Configurar banco de dados" -ForegroundColor White
Write-Host "- postgresql_service_manager.ps1: Gerenciar servico PostgreSQL" -ForegroundColor White

Write-Host "`n✨ TESTE CONCLUIDO!" -ForegroundColor Magenta
