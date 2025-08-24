# MANUAL DE TESTE DO SISTEMA
# Execute este arquivo para verificar se tudo está funcionando

Write-Host "=== TESTE MANUAL DO SISTEMA ===" -ForegroundColor Green

Write-Host "`n1. VERIFICANDO SERVIÇOS ATIVOS..." -ForegroundColor Cyan

# Verificar Frontend (porta 5173)
Write-Host "Testando Frontend (porta 5173)..."
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 3
    Write-Host "✅ Frontend - OK (Status: $($frontendResponse.StatusCode))" -ForegroundColor Green
}
catch {
    Write-Host "❌ Frontend - Não está rodando" -ForegroundColor Red
    Write-Host "Execute: .\start_frontend.ps1" -ForegroundColor Yellow
}

# Verificar Backend (porta 8001)
Write-Host "Testando Backend (porta 8001)..."
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8001" -UseBasicParsing -TimeoutSec 3
    Write-Host "✅ Backend - OK (Status: $($backendResponse.StatusCode))" -ForegroundColor Green
}
catch {
    Write-Host "❌ Backend - Não está rodando" -ForegroundColor Red
    Write-Host "Execute: python simple_auth_server.py" -ForegroundColor Yellow
}

Write-Host "`n2. TESTANDO API DE AUTENTICAÇÃO..." -ForegroundColor Cyan

# Testar Login
Write-Host "Testando login na API..."
try {
    $loginData = @{
        email    = "admin@teste.com"
        password = "123456"
    } | ConvertTo-Json
    
    $headers = @{ "Content-Type" = "application/json" }
    
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/login" -Method POST -Body $loginData -Headers $headers
    
    if ($loginResponse.access_token) {
        Write-Host "✅ Login API - Token recebido" -ForegroundColor Green
        
        # Testar endpoint protegido
        Write-Host "Testando endpoint protegido..."
        $authHeaders = @{
            "Authorization" = "Bearer $($loginResponse.access_token)"
            "Content-Type"  = "application/json"
        }
        
        $userResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/me" -Method GET -Headers $authHeaders
        Write-Host "✅ Endpoint Protegido - Usuário: $($userResponse.email)" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Erro no teste de autenticação: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n3. INSTRUÇÕES PARA TESTE COMPLETO..." -ForegroundColor Cyan

Write-Host "`nPara testar o sistema completo:" -ForegroundColor White
Write-Host "1. Certifique-se que ambos os serviços estão rodando" -ForegroundColor Yellow
Write-Host "2. Abra: http://localhost:5173" -ForegroundColor Cyan
Write-Host "3. Use as credenciais:" -ForegroundColor Yellow
Write-Host "   Email: admin@teste.com" -ForegroundColor White
Write-Host "   Senha: 123456" -ForegroundColor White
Write-Host "4. Verifique se o login funciona e redireciona para o dashboard" -ForegroundColor Yellow

Write-Host "`nComandos úteis:" -ForegroundColor White
Write-Host "- Iniciar Frontend: .\start_frontend.ps1" -ForegroundColor Cyan
Write-Host "- Iniciar Backend: python simple_auth_server.py" -ForegroundColor Cyan
Write-Host "- Este teste: .\manual_test.ps1" -ForegroundColor Cyan

Write-Host "`n=== FIM DO TESTE ===" -ForegroundColor Green
