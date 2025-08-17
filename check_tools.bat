@echo off
echo === VERIFICACAO DE FERRAMENTAS ===
echo.

echo PYTHON:
python --version 2>nul
if %errorlevel% neq 0 (
    echo   PYTHON NAO ENCONTRADO
) else (
    echo   PYTHON OK
)

echo.
echo NODE.JS:
node --version 2>nul
if %errorlevel% neq 0 (
    echo   NODE.JS NAO ENCONTRADO
) else (
    echo   NODE.JS OK
)

echo.
echo NPM:
npm --version 2>nul
if %errorlevel% neq 0 (
    echo   NPM NAO ENCONTRADO
) else (
    echo   NPM OK
)

echo.
echo POSTGRESQL:
psql --version 2>nul
if %errorlevel% neq 0 (
    echo   POSTGRESQL NAO ENCONTRADO
) else (
    echo   POSTGRESQL OK
)

echo.
echo GIT:
git --version 2>nul
if %errorlevel% neq 0 (
    echo   GIT NAO ENCONTRADO
) else (
    echo   GIT OK
)

echo.
echo POETRY:
poetry --version 2>nul
if %errorlevel% neq 0 (
    echo   POETRY NAO ENCONTRADO
) else (
    echo   POETRY OK
)

echo.
echo CHOCOLATEY:
choco --version 2>nul
if %errorlevel% neq 0 (
    echo   CHOCOLATEY NAO ENCONTRADO
) else (
    echo   CHOCOLATEY OK
)

echo.
echo === VERIFICACAO CONCLUIDA ===
pause
