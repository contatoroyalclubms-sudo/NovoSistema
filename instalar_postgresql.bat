@echo off
echo ========================================
echo    INSTALACAO RAPIDA POSTGRESQL
echo ========================================
echo.

echo [METODO 1] Tentando via WINGET...
winget install PostgreSQL.PostgreSQL
if %errorlevel% equ 0 (
    echo SUCCESS: PostgreSQL instalado via Winget!
    goto :test
)

echo.
echo [METODO 2] Winget falhou, baixe manualmente:
echo.
echo 1. Acesse: https://www.postgresql.org/download/windows/
echo 2. Baixe PostgreSQL 15.x
echo 3. Execute como Administrador
echo 4. Use senha: postgres123
echo.
echo Pressione qualquer tecla apos instalar...
pause

:test
echo.
echo ========================================
echo         TESTANDO POSTGRESQL
echo ========================================
echo.

echo Testando se PostgreSQL foi instalado...
psql --version
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: PostgreSQL funcionando!
    echo.
    echo Testando conexao...
    psql -U postgres -c "SELECT version();"
    if %errorlevel% equ 0 (
        echo.
        echo PERFEITO: PostgreSQL totalmente funcional!
        echo.
        echo PROXIMO PASSO:
        echo Execute: setup_postgresql_db.ps1
    ) else (
        echo.
        echo AVISO: PostgreSQL instalado mas conexao falhou
        echo Verifique se o servico esta rodando
    )
) else (
    echo.
    echo ERRO: PostgreSQL nao encontrado
    echo Tente reinstalar ou adicionar ao PATH
)

echo.
echo ========================================
echo          INSTALACAO CONCLUIDA
echo ========================================
pause
