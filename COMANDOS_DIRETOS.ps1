# COMANDOS DIRETOS - BASEADO NO SCRIPT DO USUARIO
# Execute linha por linha como Administrador

Write-Host "=== COMANDOS BASEADOS NO SEU SCRIPT ===" -ForegroundColor Green
Write-Host "Execute estes comandos um por vez como Administrador" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. INSTALAR CHOCOLATEY:" -ForegroundColor Cyan
Write-Host 'Set-ExecutionPolicy Bypass -Scope Process -Force' -ForegroundColor White
Write-Host '[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072' -ForegroundColor White
Write-Host "Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" -ForegroundColor White

Write-Host ""
Write-Host "2. INSTALAR POSTGRESQL:" -ForegroundColor Cyan
Write-Host 'choco install postgresql15 -y' -ForegroundColor White

Write-Host ""
Write-Host "3. INSTALAR PYTHON 3.12+:" -ForegroundColor Cyan
Write-Host 'choco install python312 -y' -ForegroundColor White

Write-Host ""
Write-Host "4. INSTALAR NODE.JS 20+:" -ForegroundColor Cyan
Write-Host 'choco install nodejs-lts -y' -ForegroundColor White

Write-Host ""
Write-Host "5. INSTALAR GIT:" -ForegroundColor Cyan
Write-Host 'choco install git -y' -ForegroundColor White

Write-Host ""
Write-Host "6. INSTALAR POETRY:" -ForegroundColor Cyan
Write-Host "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -" -ForegroundColor White

Write-Host ""
Write-Host "7. VERIFICAR INSTALAÇÕES:" -ForegroundColor Cyan
Write-Host 'psql --version' -ForegroundColor White
Write-Host 'python --version' -ForegroundColor White
Write-Host 'node --version' -ForegroundColor White
Write-Host 'npm --version' -ForegroundColor White
Write-Host 'poetry --version' -ForegroundColor White

Write-Host ""
Write-Host "=== COMANDO UNICO (TUDO DE UMA VEZ) ===" -ForegroundColor Green
Write-Host "Se preferir, execute este comando unico:" -ForegroundColor Yellow
Write-Host ""
Write-Host "choco install postgresql15 python312 nodejs-lts git -y; (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -" -ForegroundColor White

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = Read-Host
