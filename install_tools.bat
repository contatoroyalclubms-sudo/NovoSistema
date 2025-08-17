@echo off
echo === INSTALACAO SIMPLES DE FERRAMENTAS ===
echo.
echo Verificando privilegios de administrador...

net session >nul 2>&1
if %errorLevel% == 0 (
    echo OK - Executando como Administrador
) else (
    echo ERRO: Este script precisa ser executado como Administrador!
    echo.
    echo Como executar como Admin:
    echo 1. Clique com botao direito no arquivo install_tools.bat
    echo 2. Selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo Instalando Chocolatey...
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

echo.
echo Instalando ferramentas...
choco install python312 -y
choco install nodejs-lts -y
choco install postgresql15 -y
choco install git -y

echo.
echo Instalando Poetry...
powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"

echo.
echo === VERIFICACAO FINAL ===
echo.
python --version
node --version
npm --version
psql --version
git --version
poetry --version
choco --version

echo.
echo === INSTALACAO CONCLUIDA ===
echo.
echo PROXIMOS PASSOS:
echo 1. Abra um novo terminal normal (nao Admin)
echo 2. Navegue ate: c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema
echo 3. Configure o backend: cd paineluniversal\backend && poetry install
echo 4. Configure o frontend: cd paineluniversal\frontend && npm install
echo.
pause
