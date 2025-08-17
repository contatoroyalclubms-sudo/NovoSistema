@echo off
echo ==========================================
echo      TESTE DE INSTALACAO - VERIFICACAO
echo ==========================================
echo.

echo Verificando se as ferramentas estao instaladas...
echo.

echo [1] Python:
python --version 2>nul
if %errorlevel% equ 0 (
    echo    STATUS: JA INSTALADO
) else (
    echo    STATUS: NAO ENCONTRADO - PRECISA INSTALAR
)

echo.
echo [2] Node.js:
node --version 2>nul
if %errorlevel% equ 0 (
    echo    STATUS: JA INSTALADO
) else (
    echo    STATUS: NAO ENCONTRADO - PRECISA INSTALAR
)

echo.
echo [3] Git:
git --version 2>nul
if %errorlevel% equ 0 (
    echo    STATUS: JA INSTALADO
) else (
    echo    STATUS: NAO ENCONTRADO - PRECISA INSTALAR
)

echo.
echo [4] PostgreSQL:
psql --version 2>nul
if %errorlevel% equ 0 (
    echo    STATUS: JA INSTALADO
) else (
    echo    STATUS: NAO ENCONTRADO - PRECISA INSTALAR
)

echo.
echo [5] Chocolatey:
choco --version 2>nul
if %errorlevel% equ 0 (
    echo    STATUS: JA INSTALADO
) else (
    echo    STATUS: NAO ENCONTRADO - PRECISA INSTALAR
)

echo.
echo [6] Poetry:
poetry --version 2>nul
if %errorlevel% equ 0 (
    echo    STATUS: JA INSTALADO
) else (
    echo    STATUS: NAO ENCONTRADO - PRECISA INSTALAR
)

echo.
echo ==========================================
echo              ANALISE
echo ==========================================
echo.

echo Se alguma ferramenta mostrar "NAO ENCONTRADO":
echo 1. Execute como ADMINISTRADOR: install_as_admin.ps1
echo 2. Ou instale manualmente cada ferramenta
echo.

echo Se todas estiverem instaladas:
echo 1. Va para: cd paineluniversal\backend
echo 2. Execute: poetry install  
echo 3. Execute: poetry run uvicorn app.main:app --reload
echo 4. Em outro terminal: cd paineluniversal\frontend
echo 5. Execute: npm install
echo 6. Execute: npm run dev
echo.

echo ==========================================
echo            TESTE FINALIZADO
echo ==========================================

pause
