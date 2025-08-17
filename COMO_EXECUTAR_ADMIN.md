# =========================================================================

# COMO EXECUTAR POWERSHELL COMO ADMINISTRADOR

# =========================================================================

## MÉTODO MAIS SIMPLES:

1. Pressione as teclas: Win + X
2. Clique em "Terminal (Administrador)" ou "Windows PowerShell (Administrador)"
3. Na janela que abrir, digite:

```powershell
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"
.\install_as_admin.ps1
```

## OU MÉTODO ALTERNATIVO:

1. Pressione: Win + R
2. Digite: powershell
3. Pressione: Ctrl + Shift + Enter (para abrir como Admin)
4. Execute os comandos acima

# =========================================================================

# COMANDO ÚNICO PARA COPIAR E COLAR:

# =========================================================================

Set-Location "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"; .\install_as_admin.ps1

# =========================================================================

# SE O SCRIPT NÃO FUNCIONAR, EXECUTE MANUALMENTE:

# =========================================================================

# 1. Instalar Chocolatey

Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. Instalar todas as ferramentas

choco install python312 nodejs-lts postgresql15 git -y

# 3. Instalar Poetry

(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# 4. Verificar instalações

python --version; node --version; npm --version; psql --version; git --version; poetry --version

# =========================================================================
