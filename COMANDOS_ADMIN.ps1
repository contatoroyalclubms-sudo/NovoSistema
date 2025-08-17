# =============================================================================
# COMANDO PARA EXECUTAR POWERSHELL COMO ADMINISTRADOR
# =============================================================================

# MÉTODO 1: Abrir PowerShell como Administrador pelo menu
# 1. Pressione Win + X
# 2. Clique em "Windows PowerShell (Admin)" ou "Terminal (Admin)"
# 3. Execute o comando abaixo:

cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\check_tools.ps1

# =============================================================================

# MÉTODO 2: Comando direto para abrir PowerShell Admin
# Execute este comando no Run (Win + R):
powershell -Command "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File \"c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\check_tools.ps1\"' -Verb RunAs"

# =============================================================================

# MÉTODO 3: Script para auto-elevar privilégios
# Salve como run_as_admin.ps1 e execute:

if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process PowerShell -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Aqui executa com privilégios de administrador
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"
.\check_tools.ps1

# =============================================================================

# MÉTODO 4: Instalação manual das ferramentas (se os scripts não funcionarem)

# 1. Instalar Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. Instalar Python 3.12
choco install python312 -y

# 3. Instalar Node.js 20
choco install nodejs-lts -y

# 4. Instalar PostgreSQL 15
choco install postgresql15 -y

# 5. Instalar Git
choco install git -y

# 6. Instalar Poetry (após Python)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# 7. Verificar instalações
python --version
node --version
npm --version
psql --version
poetry --version
git --version

# =============================================================================
