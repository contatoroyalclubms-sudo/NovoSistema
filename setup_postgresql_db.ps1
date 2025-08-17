# CONFIGURACAO POSTGRESQL PARA SISTEMA DE EVENTOS - WINDOWS
# Equivalente ao script bash fornecido pelo usuario

Write-Host "🚀 Configurando PostgreSQL para o Sistema de Eventos..." -ForegroundColor Green
Write-Host "Script baseado no codigo bash fornecido" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta executando como Admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (!$isAdmin) {
    Write-Host "AVISO: Recomendado executar como Administrador" -ForegroundColor Yellow
    Write-Host "Mas podemos tentar continuar..." -ForegroundColor Gray
}

# Configuracoes do banco (baseadas no script original)
$DB_NAME = "eventos_db"
$DB_USER = "eventos_user"
$DB_PASSWORD = "eventos_2024_secure!"

Write-Host "CONFIGURACOES:" -ForegroundColor Yellow
Write-Host "  Banco: $DB_NAME" -ForegroundColor White
Write-Host "  Usuario: $DB_USER" -ForegroundColor White
Write-Host "  Senha: $DB_PASSWORD" -ForegroundColor White
Write-Host ""

# Verificar se PostgreSQL esta rodando
Write-Host "Verificando se PostgreSQL esta rodando..." -ForegroundColor Yellow
try {
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgService -and $pgService.Status -eq "Running") {
        Write-Host "OK - PostgreSQL esta rodando: $($pgService.Name)" -ForegroundColor Green
    }
    else {
        Write-Host "AVISO - PostgreSQL pode nao estar rodando" -ForegroundColor Yellow
        Write-Host "Tentando iniciar..." -ForegroundColor Cyan
        Start-Service postgresql* -ErrorAction SilentlyContinue
    }
}
catch {
    Write-Host "Erro ao verificar servico PostgreSQL: $_" -ForegroundColor Red
}

Write-Host ""

# EQUIVALENTE: sudo -u postgres psql
# No Windows: psql -U postgres (como administrador do banco)
Write-Host "Executando comandos SQL..." -ForegroundColor Yellow
Write-Host "Equivalente ao: sudo -u postgres psql" -ForegroundColor Cyan

# Criar arquivo SQL temporario com os comandos
$sqlCommands = @"
-- Criar usuario eventos_user
CREATE USER eventos_user WITH PASSWORD 'eventos_2024_secure!';

-- Criar banco de dados  
CREATE DATABASE eventos_db OWNER eventos_user;

-- Conceder permissoes
GRANT ALL PRIVILEGES ON DATABASE eventos_db TO eventos_user;
"@

$sqlFile = "temp_setup.sql"
$sqlCommands | Out-File -FilePath $sqlFile -Encoding UTF8

try {
    Write-Host "   Executando comandos iniciais..." -ForegroundColor Cyan
    
    # Tentar conectar como postgres (usuario padrao)
    $result = psql -U postgres -f $sqlFile 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   OK - Comandos iniciais executados" -ForegroundColor Green
    }
    else {
        Write-Host "   Aviso - Possivel problema: $result" -ForegroundColor Yellow
        Write-Host "   Tentando alternativa sem especificar usuario..." -ForegroundColor Cyan
        psql -f $sqlFile 2>&1
    }
}
catch {
    Write-Host "   Erro ao executar comandos SQL: $_" -ForegroundColor Red
}

# Comandos para o banco eventos_db
$sqlCommandsDB = @"
-- Conectar ao banco eventos_db e configurar permissoes
-- Conceder permissoes no schema public
GRANT ALL ON SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eventos_user;

-- Criar extensoes necessarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Verificar criacao
\l
\du
"@

$sqlFileDB = "temp_setup_db.sql"
$sqlCommandsDB | Out-File -FilePath $sqlFileDB -Encoding UTF8

try {
    Write-Host "   Configurando banco eventos_db..." -ForegroundColor Cyan
    
    # Conectar ao banco eventos_db
    $result = psql -U postgres -d eventos_db -f $sqlFileDB 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   OK - Banco eventos_db configurado" -ForegroundColor Green
    }
    else {
        Write-Host "   Aviso - Problema na configuracao do banco: $result" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   Erro ao configurar banco: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ PostgreSQL configurado com sucesso!" -ForegroundColor Green
Write-Host ""

# EQUIVALENTE: PGPASSWORD='eventos_2024_secure!' psql -h localhost -U eventos_user -d eventos_db -c "SELECT version();"
Write-Host "🧪 Testando conexao..." -ForegroundColor Yellow
Write-Host "Equivalente ao teste PGPASSWORD do script original" -ForegroundColor Cyan

try {
    # No Windows, definir variavel de ambiente temporariamente
    $env:PGPASSWORD = $DB_PASSWORD
    
    $testResult = psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT version();" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Teste de conexao bem-sucedido!" -ForegroundColor Green
        Write-Host "Resultado:" -ForegroundColor Cyan
        Write-Host $testResult -ForegroundColor White
    }
    else {
        Write-Host "❌ Erro na conexao. Verifique as configuracoes." -ForegroundColor Red
        Write-Host "Detalhes: $testResult" -ForegroundColor Gray
        
        # Comandos de diagnostico
        Write-Host ""
        Write-Host "DIAGNOSTICO:" -ForegroundColor Yellow
        Write-Host "1. Verifique se o PostgreSQL esta rodando:" -ForegroundColor Gray
        Write-Host "   Get-Service postgresql*" -ForegroundColor White
        Write-Host "2. Teste conexao local:" -ForegroundColor Gray
        Write-Host "   psql -U postgres" -ForegroundColor White
        Write-Host "3. Liste bancos:" -ForegroundColor Gray
        Write-Host "   psql -U postgres -c '\l'" -ForegroundColor White
    }
    
    # Limpar variavel de ambiente
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
}
catch {
    Write-Host "❌ Erro ao testar conexao: $_" -ForegroundColor Red
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
}

# Limpeza dos arquivos temporarios
try {
    Remove-Item $sqlFile -ErrorAction SilentlyContinue
    Remove-Item $sqlFileDB -ErrorAction SilentlyContinue
}
catch {
    # Ignorar erros de limpeza
}

Write-Host ""
Write-Host "=== INFORMACOES DE CONEXAO ===" -ForegroundColor Green
Write-Host "Host: localhost" -ForegroundColor White
Write-Host "Banco: $DB_NAME" -ForegroundColor White
Write-Host "Usuario: $DB_USER" -ForegroundColor White
Write-Host "Senha: $DB_PASSWORD" -ForegroundColor White
Write-Host ""
Write-Host "COMANDO DE TESTE MANUAL:" -ForegroundColor Yellow
Write-Host "`$env:PGPASSWORD='$DB_PASSWORD'; psql -h localhost -U $DB_USER -d $DB_NAME" -ForegroundColor White

Write-Host ""
Write-Host "=== MAPEAMENTO BASH -> WINDOWS ===" -ForegroundColor Cyan
Write-Host "sudo -u postgres psql          -> psql -U postgres" -ForegroundColor Gray
Write-Host "PGPASSWORD='...' psql          -> `$env:PGPASSWORD='...'; psql" -ForegroundColor Gray
Write-Host "if [ `$? -eq 0 ]                -> if (`$LASTEXITCODE -eq 0)" -ForegroundColor Gray
Write-Host "echo commands | psql           -> commands | Out-File temp.sql; psql -f temp.sql" -ForegroundColor Gray

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = Read-Host
