# Script completo de teste do sistema
param(
    [string]$TestType = "quick"  # "quick" para teste rápido, "full" para teste completo
)

Write-Host "=== TESTE DO SISTEMA COMPLETO ===" -ForegroundColor Green
Write-Host "Tipo de teste: $TestType" -ForegroundColor Yellow

$ProjectPath = "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal"
$FrontendPath = "$ProjectPath\frontend"
$BackendPath = "$ProjectPath\backend"
$MockBackendPath = "$ProjectPath\mock-backend"

# Função para testar URL
function Test-Url {
    param($Url, $Description)
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $Description - OK" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ $Description - Status: $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ $Description - Erro: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Função para testar API Login
function Test-ApiLogin {
    try {
        $loginData = @{
            email    = "admin@teste.com"
            password = "123456"
        } | ConvertTo-Json
        
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/login" -Method POST -Body $loginData -Headers $headers
        
        if ($response.access_token) {
            Write-Host "✅ API Login - Token recebido" -ForegroundColor Green
            return @{success = $true; token = $response.access_token }
        }
        else {
            Write-Host "❌ API Login - Token não recebido" -ForegroundColor Red
            return @{success = $false }
        }
    }
    catch {
        Write-Host "❌ API Login - Erro: $($_.Exception.Message)" -ForegroundColor Red
        return @{success = $false }
    }
}

# Função para testar endpoint protegido
function Test-ProtectedEndpoint {
    param($Token)
    try {
        $headers = @{
            "Authorization" = "Bearer $Token"
            "Content-Type"  = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/me" -Method GET -Headers $headers
        
        if ($response.email) {
            Write-Host "✅ Endpoint Protegido - Usuário: $($response.email)" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ Endpoint Protegido - Dados não recebidos" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Endpoint Protegido - Erro: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "`n1. VERIFICANDO SERVIÇOS..." -ForegroundColor Cyan

# Testar se PostgreSQL está rodando
Write-Host "`nTestando PostgreSQL..." -ForegroundColor Yellow
try {
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgService -and $pgService.Status -eq "Running") {
        Write-Host "✅ PostgreSQL - Serviço rodando" -ForegroundColor Green
    }
    else {
        Write-Host "❌ PostgreSQL - Serviço não encontrado ou parado" -ForegroundColor Red
        Write-Host "Execute: net start postgresql-x64-17" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ PostgreSQL - Erro ao verificar serviço" -ForegroundColor Red
}

Write-Host "`n2. TESTANDO CONECTIVIDADE..." -ForegroundColor Cyan

# Testar Backend
$backendOk = Test-Url "http://localhost:8001" "Backend API"

# Testar Frontend
$frontendOk = Test-Url "http://localhost:5173" "Frontend"

# Se backend não estiver rodando, tentar iniciar mock
if (-not $backendOk) {
    Write-Host "`nBackend não está rodando. Tentando iniciar Mock Backend..." -ForegroundColor Yellow
    
    Set-Location $MockBackendPath
    if (Test-Path "package.json") {
        # Iniciar mock backend em background
        Start-Process -FilePath "node" -ArgumentList "server.js" -NoNewWindow
        Start-Sleep 3
        $backendOk = Test-Url "http://localhost:8000" "Mock Backend"
    }
}

Write-Host "`n3. TESTANDO AUTENTICAÇÃO..." -ForegroundColor Cyan

if ($backendOk) {
    # Testar documentação da API
    Test-Url "http://localhost:8001/docs" "Documentação Swagger"
    
    # Testar login
    $loginResult = Test-ApiLogin
    
    if ($loginResult.success) {
        # Testar endpoint protegido
        Test-ProtectedEndpoint $loginResult.token
    }
}
else {
    Write-Host "❌ Não é possível testar autenticação - Backend não está rodando" -ForegroundColor Red
}

Write-Host "`n4. VERIFICANDO ARQUIVOS DE CONFIGURAÇÃO..." -ForegroundColor Cyan

# Verificar .env do backend
if (Test-Path "$BackendPath\.env") {
    Write-Host "✅ Backend .env - Existe" -ForegroundColor Green
}
else {
    Write-Host "❌ Backend .env - Não encontrado" -ForegroundColor Red
}

# Verificar package.json do frontend
if (Test-Path "$FrontendPath\package.json") {
    Write-Host "✅ Frontend package.json - Existe" -ForegroundColor Green
}
else {
    Write-Host "❌ Frontend package.json - Não encontrado" -ForegroundColor Red
}

# Verificar node_modules do frontend
if (Test-Path "$FrontendPath\node_modules") {
    Write-Host "✅ Frontend dependências - Instaladas" -ForegroundColor Green
}
else {
    Write-Host "❌ Frontend dependências - Não instaladas" -ForegroundColor Red
    Write-Host "Execute: npm install (no diretório frontend)" -ForegroundColor Yellow
}

Write-Host "`n5. RESUMO DOS TESTES..." -ForegroundColor Cyan

Write-Host "`nPara iniciar o sistema completo:" -ForegroundColor White
Write-Host "1. Backend: .\start_backend.ps1" -ForegroundColor Yellow
Write-Host "2. Frontend: .\start_frontend.ps1" -ForegroundColor Yellow
Write-Host "3. Acesse: http://localhost:5173" -ForegroundColor Cyan
Write-Host "4. Login: admin@teste.com / 123456" -ForegroundColor Cyan

Write-Host "`nURLs importantes:" -ForegroundColor White
Write-Host "- Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "- Backend API: http://localhost:8001" -ForegroundColor Cyan
Write-Host "- API Docs: http://localhost:8001/docs" -ForegroundColor Cyan

if ($TestType -eq "full") {
    Write-Host "`n6. TESTE COMPLETO - ABRINDO NAVEGADOR..." -ForegroundColor Cyan
    Start-Process "http://localhost:5173"
    Start-Process "http://localhost:8000/docs"
}
