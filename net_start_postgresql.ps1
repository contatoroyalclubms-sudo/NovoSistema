# COMANDO ESPECIFICO POSTGRESQL - NET START
# Baseado no comando fornecido pelo usuario

Write-Host "=== COMANDO NET START POSTGRESQL ===" -ForegroundColor Green
Write-Host "Equivalente Windows para iniciar PostgreSQL" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta executando como Admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (!$isAdmin) {
    Write-Host "ERRO: Este comando precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Equivalente ao 'sudo' necessario para net start" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Como executar como Admin:" -ForegroundColor Yellow
    Write-Host "1. Win + X -> Terminal (Administrador)" -ForegroundColor Gray
    Write-Host "2. Execute este script novamente" -ForegroundColor Gray
    pause
    exit 1
}

Write-Host "OK - Executando como Administrador" -ForegroundColor Green
Write-Host ""

# COMANDO EXATO DO USUARIO: net start postgresql-x64-15
Write-Host "EXECUTANDO: net start postgresql-x64-15" -ForegroundColor Yellow
Write-Host "Baseado no comando fornecido pelo usuario" -ForegroundColor Cyan
Write-Host ""

try {
    # Tentar o comando exato fornecido
    net start postgresql-x64-15
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK - Servico postgresql-x64-15 iniciado com sucesso!" -ForegroundColor Green
    }
    else {
        Write-Host "Aviso - Codigo de saida: $LASTEXITCODE" -ForegroundColor Yellow
        Write-Host "Tentando alternativas..." -ForegroundColor Cyan
        
        # Tentar outras variações comuns
        $servicesToTry = @(
            "postgresql-x64-15",
            "postgresql-15",
            "PostgreSQL"
        )
        
        foreach ($serviceName in $servicesToTry) {
            Write-Host "Tentando: net start $serviceName" -ForegroundColor Cyan
            try {
                net start $serviceName 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "OK - Servico $serviceName iniciado!" -ForegroundColor Green
                    break
                }
            }
            catch {
                Write-Host "Falhou: $serviceName" -ForegroundColor Gray
            }
        }
    }
}
catch {
    Write-Host "ERRO ao executar net start: $_" -ForegroundColor Red
}

Write-Host ""

# Verificar status usando PowerShell também
Write-Host "VERIFICANDO STATUS COM POWERSHELL:" -ForegroundColor Yellow
try {
    $pgServices = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue
    if ($pgServices) {
        foreach ($service in $pgServices) {
            $status = if ($service.Status -eq "Running") { "RODANDO" } else { "PARADO" }
            $color = if ($service.Status -eq "Running") { "Green" } else { "Red" }
            Write-Host "   $($service.Name): $status" -ForegroundColor $color
        }
    }
    else {
        Write-Host "   Nenhum servico PostgreSQL encontrado" -ForegroundColor Red
    }
}
catch {
    Write-Host "   Erro ao verificar servicos: $_" -ForegroundColor Red
}

Write-Host ""

# Comandos equivalentes
Write-Host "COMANDOS EQUIVALENTES:" -ForegroundColor Cyan
Write-Host ""
Write-Host "COMANDO ORIGINAL (fornecido pelo usuario):" -ForegroundColor Yellow
Write-Host "net start postgresql-x64-15" -ForegroundColor White
Write-Host ""
Write-Host "ALTERNATIVAS POWERSHELL:" -ForegroundColor Yellow
Write-Host "Start-Service postgresql-x64-15" -ForegroundColor White
Write-Host "Start-Service 'postgresql*'" -ForegroundColor White
Write-Host ""
Write-Host "VERIFICAR STATUS:" -ForegroundColor Yellow
Write-Host "net start | findstr postgresql" -ForegroundColor White
Write-Host "Get-Service postgresql*" -ForegroundColor White
Write-Host ""
Write-Host "PARAR SERVICO:" -ForegroundColor Yellow
Write-Host "net stop postgresql-x64-15" -ForegroundColor White
Write-Host "Stop-Service postgresql-x64-15" -ForegroundColor White

Write-Host ""

# Informações adicionais
Write-Host "COMENTARIO DO USUARIO:" -ForegroundColor Cyan
Write-Host "'O servico ja deve estar rodando apos a instalacao'" -ForegroundColor Gray
Write-Host ""
Write-Host "OBSERVACAO:" -ForegroundColor Yellow
Write-Host "Se o PostgreSQL foi instalado via Chocolatey, o servico pode ter" -ForegroundColor Gray
Write-Host "nomes ligeiramente diferentes. Use Get-Service postgresql* para" -ForegroundColor Gray
Write-Host "ver todos os servicos PostgreSQL disponiveis." -ForegroundColor Gray

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = Read-Host
