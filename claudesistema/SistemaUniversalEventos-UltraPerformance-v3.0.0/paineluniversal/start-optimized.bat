@echo off
cls
echo.
echo ==============================================================================
echo                     SISTEMA UNIVERSAL DE EVENTOS v3.0.0
echo                           ULTRA-PERFORMANCE EDITION
echo ==============================================================================
echo.

echo [*] Verificando ambiente...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale Python 3.9+
    pause
    exit /b 1
)
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado! Instale Node.js 18+
    pause
    exit /b 1
)

echo [✓] Ambiente verificado com sucesso!
echo.

echo [*] Iniciando Backend (porta 8000)...
cd /d "%~dp0"
start /min cmd /c "python simple_auth_server.py"
echo [✓] Backend iniciado!
timeout /t 2 /nobreak >nul

echo.
echo [*] Preparando Frontend...
cd frontend
if not exist node_modules (
    echo    - Instalando dependencias (primeira vez)...
    npm install >nul 2>&1
)

echo    - Instalando dependencias faltantes...
npm install @vitejs/plugin-react-swc @swc/plugin-styled-jsx --save-dev >nul 2>&1
echo [✓] Frontend preparado!

echo.
echo [*] Iniciando Frontend (porta 4200)...
start /min cmd /c "npm run dev"
echo [✓] Frontend iniciado!

timeout /t 3 /nobreak >nul

echo.
echo ==============================================================================
echo                          SISTEMA INICIADO COM SUCESSO!
echo ==============================================================================
echo.
echo   Backend API:     http://localhost:8000
echo   Frontend App:    http://localhost:4200
echo.
echo   Credenciais de teste:
echo   Email: admin@teste.com
echo   Senha: admin123
echo.
echo ==============================================================================
echo.

echo [*] Abrindo navegador...
timeout /t 2 /nobreak >nul
start http://localhost:4200

echo.
echo Sistema rodando! Pressione qualquer tecla para PARAR todos os servicos...
pause >nul

echo.
echo [*] Encerrando servicos...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
echo [✓] Servicos encerrados!
echo.
pause