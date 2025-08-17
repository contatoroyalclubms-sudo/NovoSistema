# TESTE SIMPLES DO SCRIPT DE INSTALACAO
Write-Host "INICIANDO TESTE..." -ForegroundColor Green

# Testar funcao de verificacao de admin
function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

$isAdmin = Test-Admin
Write-Host "Executando como Admin: $isAdmin" -ForegroundColor $(if($isAdmin) {"Green"} else {"Yellow"})

# Testar caminho do script
$scriptPath = $PSCommandPath
Write-Host "Script Path PSCommandPath: $scriptPath" -ForegroundColor Cyan

if (!$scriptPath) {
    $scriptPath = $MyInvocation.MyCommand.Definition
    Write-Host "Script Path MyCommand: $scriptPath" -ForegroundColor Cyan
}

if (!$scriptPath) {
    $scriptPath = "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\install_as_admin.ps1"
    Write-Host "Script Path Fixo: $scriptPath" -ForegroundColor Cyan
}

Write-Host "Caminho final do script: $scriptPath" -ForegroundColor White

# Testar se Chocolatey existe
$chocoExists = Get-Command choco -ErrorAction SilentlyContinue
if ($chocoExists) {
    Write-Host "Chocolatey: JA INSTALADO" -ForegroundColor Green
    choco --version
} else {
    Write-Host "Chocolatey: NAO ENCONTRADO" -ForegroundColor Yellow
}

# Testar algumas ferramentas basicas
$tools = @("python", "node", "git", "psql")
Write-Host "`nTestando ferramentas existentes:" -ForegroundColor Cyan

foreach ($tool in $tools) {
    try {
        $version = & $tool --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "$tool : FUNCIONANDO - $($version.Split("`n")[0])" -ForegroundColor Green
        } else {
            Write-Host "$tool : NAO ENCONTRADO" -ForegroundColor Red
        }
    } catch {
        Write-Host "$tool : ERRO" -ForegroundColor Red
    }
}

Write-Host "`nTESTE CONCLUIDO!" -ForegroundColor Magenta
