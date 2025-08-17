# INSTALAÇÃO MANUAL PASSO A PASSO

# Use este guia se os scripts automatizados não funcionarem

## 📋 LISTA DE FERRAMENTAS NECESSÁRIAS

1. **Chocolatey** (Gerenciador de pacotes do Windows)
2. **Python 3.12+**
3. **Node.js 20+**
4. **PostgreSQL 15+**
5. **Git**
6. **Poetry** (Gerenciador de dependências Python)

---

## 🔥 INSTALAÇÃO MANUAL

### 1. CHOCOLATEY

1. Abra PowerShell como **Administrador**
2. Execute:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 2. INSTALAR FERRAMENTAS COM CHOCOLATEY

```powershell
# Python
choco install python312 -y

# Node.js
choco install nodejs-lts -y

# PostgreSQL
choco install postgresql15 -y

# Git
choco install git -y
```

### 3. POETRY (após instalar Python)

```powershell
# Feche e reabra o terminal para carregar o Python
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 4. CONFIGURAR PROJETO

#### BACKEND:

```powershell
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\backend"
poetry install
poetry run uvicorn app.main:app --reload
```

#### FRONTEND (em outro terminal):

```powershell
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\frontend"
npm run dev
```

---

## ⚡ COMANDO ÚNICO (se preferir)

```powershell
# Execute tudo de uma vez (como Admin):
choco install python312 nodejs-lts postgresql15 git -y; (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

---

## 🔍 VERIFICAR INSTALAÇÃO

```powershell
python --version
node --version
npm --version
psql --version
git --version
poetry --version
choco --version
```

---

## 🚨 PROBLEMAS COMUNS

### Se o Poetry não funcionar:

```powershell
pip install poetry
```

### Se o PostgreSQL não iniciar:

```powershell
# Instalar como serviço
choco install postgresql15 --params '/Password:postgres /Port:5432'
```

### Se os comandos não forem reconhecidos:

1. Feche todos os terminais
2. Abra um novo terminal
3. Teste novamente

---

## 🎯 VERIFICAÇÃO FINAL

Depois de tudo instalado, teste:

```powershell
# Teste Backend
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\backend"
poetry --version
poetry install

# Teste Frontend
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\frontend"
npm --version
npm run dev
```

🚀 **Pronto! Seu ambiente de desenvolvimento está configurado!**
