@echo off
echo === INSTALACAO AUTOMATICA DE FERRAMENTAS ===
echo Baseado nos scripts Linux/macOS/Windows fornecidos
echo.

echo 1. Verificando Chocolatey...
choco --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    CHOCOLATEY NAO ENCONTRADO - INSTALANDO...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    echo    CHOCOLATEY INSTALADO!
) else (
    echo    CHOCOLATEY OK
)

echo.
echo 2. Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    PYTHON NAO ENCONTRADO - INSTALANDO...
    choco install python312 -y
    echo    PYTHON INSTALADO!
) else (
    echo    PYTHON OK
)

echo.
echo 3. Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    NODE.JS NAO ENCONTRADO - INSTALANDO...
    choco install nodejs-lts -y
    echo    NODE.JS INSTALADO!
) else (
    echo    NODE.JS OK
)

echo.
echo 4. Verificando PostgreSQL...
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    POSTGRESQL NAO ENCONTRADO - INSTALANDO...
    choco install postgresql15 -y
    echo    POSTGRESQL INSTALADO!
) else (
    echo    POSTGRESQL OK
)

echo.
echo 5. Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    GIT NAO ENCONTRADO - INSTALANDO...
    choco install git -y
    echo    GIT INSTALADO!
) else (
    echo    GIT OK
)

echo.
echo 6. Instalando Poetry...
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    POETRY NAO ENCONTRADO - INSTALANDO...
    powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
    echo    POETRY INSTALADO!
) else (
    echo    POETRY OK
)

echo.
echo === VERIFICACAO FINAL ===
echo Python:
python --version
echo Node.js:
node --version
echo NPM:
npm --version
echo PostgreSQL:
psql --version
echo Git:
git --version
echo Poetry:
poetry --version

echo.
echo === INSTALACAO CONCLUIDA ===
echo PROXIMO PASSO: Configure o projeto backend e frontend
echo Backend: cd backend ^&^& poetry install ^&^& poetry run uvicorn app.main:app --reload
echo Frontend: cd frontend ^&^& npm install ^&^& npm run dev
pause
