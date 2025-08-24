@echo off
cls
echo.
echo ========================================================================
echo                    INICIANDO SISTEMA DE EVENTOS
echo                         MODO DE TESTE
echo ========================================================================
echo.

echo [1] Preparando ambiente...
cd /d "C:\Users\User\OneDrive\Desktop\projetos github\claudesistema\SistemaUniversalEventos-UltraPerformance-v3.0.0\paineluniversal"

echo.
echo [2] Verificando Python...
python --version
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo [3] Verificando Node.js...
node --version
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado!
    pause
    exit /b 1
)

echo.
echo [4] Iniciando Backend Simples...
cd backend
if exist simple_auth_server.py (
    echo Usando servidor de autenticacao simples...
    start cmd /k "python simple_auth_server.py"
) else if exist backend_simples.py (
    echo Usando backend simples...
    start cmd /k "python backend_simples.py"
) else (
    echo Tentando iniciar backend principal...
    start cmd /k "python -m uvicorn app.main_simple:app --reload --port 8000"
)

timeout /t 3 /nobreak >nul

echo.
echo [5] Iniciando Frontend...
cd ..\frontend
echo Instalando dependencias basicas...
npm install @vitejs/plugin-react-swc @swc/plugin-styled-jsx --save-dev --silent 2>nul
timeout /t 2 /nobreak >nul

echo Iniciando servidor de desenvolvimento...
start cmd /k "npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo ========================================================================
echo                    SISTEMA INICIADO COM SUCESSO!
echo ========================================================================
echo.
echo Backend rodando em: http://localhost:8000
echo Frontend rodando em: http://localhost:4200
echo.
echo Aguarde alguns segundos e o navegador abrira automaticamente...
timeout /t 5 /nobreak >nul

start http://localhost:4200

echo.
echo Pressione qualquer tecla para encerrar todos os servicos...
pause >nul

taskkill /F /IM node.exe 2>nul
taskkill /F /IM python.exe 2>nul

echo.
echo Servicos encerrados!
pause