# EQUIVALENTE WINDOWS DOS COMANDOS SYSTEMCTL POSTGRESQL
# Baseado nos comandos Linux fornecidos pelo usuario

Write-Host "=== GERENCIAMENTO DE SERVICOS POSTGRESQL NO WINDOWS ===" -ForegroundColor Green
Write-Host "Equivalente aos comandos systemctl do Linux" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta executando como Admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (!$isAdmin) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Equivalente ao 'sudo' necessario para systemctl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Como executar como Admin:" -ForegroundColor Yellow
    Write-Host "1. Win + X -> Terminal (Administrador)" -ForegroundColor Gray
    Write-Host "2. Execute este script novamente" -ForegroundColor Gray
    pause
    exit 1
}

Write-Host "OK - Executando como Administrador (equivalente ao sudo)" -ForegroundColor Green
Write-Host ""

# EQUIVALENTE: sudo systemctl start postgresql
Write-Host "INICIANDO POSTGRESQL (equivalente ao systemctl start)..." -ForegroundColor Yellow
try {
    $pgServices = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgServices) {
        foreach ($service in $pgServices) {
            Write-Host "   Iniciando servico: $($service.Name)" -ForegroundColor Cyan
            Start-Service $service.Name -ErrorAction SilentlyContinue
            Write-Host "   OK - $($service.Name) iniciado" -ForegroundColor Green
        }
    }
    else {
        Write-Host "   Aviso: Nenhum servico PostgreSQL encontrado" -ForegroundColor Yellow
        Write-Host "   Verifique se o PostgreSQL esta instalado" -ForegroundColor Gray
    }
}
catch {
    Write-Host "   ERRO ao iniciar PostgreSQL: $_" -ForegroundColor Red
}

Write-Host ""

# EQUIVALENTE: sudo systemctl enable postgresql
Write-Host "HABILITANDO POSTGRESQL (equivalente ao systemctl enable)..." -ForegroundColor Yellow
try {
    $pgServices = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgServices) {
        foreach ($service in $pgServices) {
            Write-Host "   Configurando inicio automatico: $($service.Name)" -ForegroundColor Cyan
            Set-Service $service.Name -StartupType Automatic
            Write-Host "   OK - $($service.Name) configurado para iniciar automaticamente" -ForegroundColor Green
        }
    }
    else {
        Write-Host "   Aviso: Nenhum servico PostgreSQL encontrado para configurar" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ERRO ao configurar PostgreSQL: $_" -ForegroundColor Red
}

Write-Host ""

# EQUIVALENTE: sudo systemctl status postgresql
Write-Host "VERIFICANDO STATUS POSTGRESQL (equivalente ao systemctl status)..." -ForegroundColor Yellow
try {
    $pgServices = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgServices) {
        foreach ($service in $pgServices) {
            Write-Host "   Servico: $($service.Name)" -ForegroundColor White
            Write-Host "   Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
            Write-Host "   Inicio: $($service.StartType)" -ForegroundColor Cyan
            Write-Host "   ----------------------------------------" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "   ERRO: Nenhum servico PostgreSQL encontrado" -ForegroundColor Red
        Write-Host "   PostgreSQL pode nao estar instalado" -ForegroundColor Gray
    }
}
catch {
    Write-Host "   ERRO ao verificar status: $_" -ForegroundColor Red
}

Write-Host ""

# Comandos adicionais para diagnostico
Write-Host "INFORMACOES ADICIONAIS:" -ForegroundColor Cyan
Write-Host ""

# Verificar se PostgreSQL esta respondendo
Write-Host "Testando conexao PostgreSQL..." -ForegroundColor Yellow
try {
    $testConnection = psql --version 2>&1
    if ($testConnection) {
        Write-Host "   OK - Cliente PostgreSQL disponivel: $($testConnection.Split("`n")[0])" -ForegroundColor Green
    }
}
catch {
    Write-Host "   Aviso: Cliente psql nao encontrado no PATH" -ForegroundColor Yellow
}

# Listar todos os servicos PostgreSQL
Write-Host ""
Write-Host "Todos os servicos PostgreSQL no sistema:" -ForegroundColor Yellow
try {
    $allPgServices = Get-Service | Where-Object {$_.Name -like "*postgres*" -or $_.DisplayName -like "*PostgreSQL*"}
    if ($allPgServices) {
        $allPgServices | Format-Table Name, Status, StartType, DisplayName -AutoSize
    }
    else {
        Write-Host "   Nenhum servico PostgreSQL encontrado" -ForegroundColor Red
    }
}
catch {
    Write-Host "   Erro ao listar servicos" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== MAPEAMENTO LINUX -> WINDOWS ===" -ForegroundColor Green
Write-Host ""
Write-Host "COMANDOS EQUIVALENTES:" -ForegroundColor Cyan
Write-Host "sudo systemctl start postgresql    -> Start-Service postgresql*" -ForegroundColor Gray
Write-Host "sudo systemctl enable postgresql   -> Set-Service -StartupType Automatic" -ForegroundColor Gray
Write-Host "sudo systemctl status postgresql   -> Get-Service postgresql*" -ForegroundColor Gray
Write-Host "sudo systemctl stop postgresql     -> Stop-Service postgresql*" -ForegroundColor Gray
Write-Host "sudo systemctl restart postgresql  -> Restart-Service postgresql*" -ForegroundColor Gray
Write-Host ""
Write-Host "COMANDOS MANUAIS PARA USO FUTURO:" -ForegroundColor Yellow
Write-Host "Start-Service postgresql*          # Iniciar" -ForegroundColor White
Write-Host "Stop-Service postgresql*           # Parar" -ForegroundColor White
Write-Host "Restart-Service postgresql*        # Reiniciar" -ForegroundColor White
Write-Host "Get-Service postgresql*            # Ver status" -ForegroundColor White
Write-Host "Set-Service postgresql* -StartupType Automatic  # Auto-iniciar" -ForegroundColor White

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = Read-Host
