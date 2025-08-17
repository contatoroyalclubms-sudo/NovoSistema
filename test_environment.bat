@echo off
echo ========================================
echo    TESTE DO AMBIENTE DE DESENVOLVIMENTO
echo ========================================
echo.

echo 1. VERIFICANDO FERRAMENTAS INSTALADAS:
echo ----------------------------------------

echo Python:
python --version 2>nul
if %errorlevel% equ 0 (
    echo    [OK] Python encontrado
) else (
    echo    [ERRO] Python nao encontrado
)

echo.
echo Node.js:
node --version 2>nul
if %errorlevel% equ 0 (
    echo    [OK] Node.js encontrado
) else (
    echo    [ERRO] Node.js nao encontrado
)

echo.
echo NPM:
npm --version 2>nul
if %errorlevel% equ 0 (
    echo    [OK] NPM encontrado
) else (
    echo    [ERRO] NPM nao encontrado
)

echo.
echo Git:
git --version 2>nul
if %errorlevel% equ 0 (
    echo    [OK] Git encontrado
) else (
    echo    [ERRO] Git nao encontrado
)

echo.
echo PostgreSQL:
psql --version 2>nul
if %errorlevel% equ 0 (
    echo    [OK] PostgreSQL encontrado
) else (
    echo    [ERRO] PostgreSQL nao encontrado
)

echo.
echo Poetry:
poetry --version 2>nul
if %errorlevel% equ 0 (
    echo    [OK] Poetry encontrado
) else (
    echo    [ERRO] Poetry nao encontrado
)

echo.
echo Chocolatey:
choco --version 2>nul
if %errorlevel% equ 0 (
    echo    [OK] Chocolatey encontrado
) else (
    echo    [ERRO] Chocolatey nao encontrado
)

echo.
echo 2. VERIFICANDO ESTRUTURA DO PROJETO:
echo -------------------------------------

if exist "paineluniversal\backend\pyproject.toml" (
    echo    [OK] Backend configurado
) else (
    echo    [ERRO] Backend nao encontrado
)

if exist "paineluniversal\frontend\package.json" (
    echo    [OK] Frontend configurado
) else (
    echo    [ERRO] Frontend nao encontrado
)

if exist "paineluniversal\backend\app\main.py" (
    echo    [OK] App principal encontrada
) else (
    echo    [ERRO] App principal nao encontrada
)

echo.
echo 3. VERIFICANDO DEPENDENCIAS:
echo -----------------------------

if exist "paineluniversal\frontend\node_modules" (
    echo    [OK] Node modules instalados
) else (
    echo    [AVISO] Execute: cd paineluniversal\frontend ^&^& npm install
)

if exist "paineluniversal\backend\.venv" (
    echo    [OK] Ambiente Python ativo
) else (
    echo    [AVISO] Execute: cd paineluniversal\backend ^&^& poetry install
)

echo.
echo ========================================
echo              RESUMO
echo ========================================
echo.
echo PARA INICIAR O DESENVOLVIMENTO:
echo.
echo 1. Backend:
echo    cd paineluniversal\backend
echo    poetry install
echo    poetry run uvicorn app.main:app --reload
echo.
echo 2. Frontend (em outro terminal):
echo    cd paineluniversal\frontend  
echo    npm install
echo    npm run dev
echo.
echo 3. Acessar: http://localhost:5173
echo.
echo SCRIPTS DISPONIVEIS:
echo - install_as_admin.ps1 (executar como admin)
echo - setup_postgresql_db.ps1
echo - test_environment_simple.ps1
echo.
echo ========================================
echo           TESTE CONCLUIDO
echo ========================================

pause
