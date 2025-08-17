# GUIA DE INSTALAÇÃO DE FERRAMENTAS - WINDOWS

## 🛠️ FERRAMENTAS NECESSÁRIAS PARA O PROJETO

### 📋 **LISTA DE VERIFICAÇÃO**

Baseado no script Linux fornecido, aqui estão as ferramentas equivalentes para Windows:

### 1️⃣ **CHOCOLATEY** (Gerenciador de Pacotes)

```powershell
# Execute no PowerShell como Administrador
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 2️⃣ **PYTHON 3.12+**

```powershell
choco install python312 -y
# OU baixar diretamente de: https://www.python.org/downloads/
```

### 3️⃣ **NODE.JS 20+**

```powershell
choco install nodejs -y
# OU baixar diretamente de: https://nodejs.org/
```

### 4️⃣ **POSTGRESQL 15+**

```powershell
choco install postgresql --params '/Password:postgres123' -y
# OU baixar diretamente de: https://www.postgresql.org/download/windows/
```

### 5️⃣ **POETRY** (Gerenciador de dependências Python)

```powershell
# Após instalar Python
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 6️⃣ **GIT**

```powershell
choco install git -y
# OU baixar diretamente de: https://git-scm.com/download/win
```

### 7️⃣ **FERRAMENTAS ADICIONAIS**

```powershell
choco install curl wget -y
```

---

## 🔍 **COMO VERIFICAR AS INSTALAÇÕES**

Execute estes comandos no PowerShell ou CMD:

```batch
python --version
node --version
npm --version
psql --version
poetry --version
git --version
choco --version
```

---

## 🚀 **SCRIPT DE INSTALAÇÃO AUTOMÁTICA**

**OPÇÃO 1: Manual (Recomendado)**
Execute cada comando individualmente no PowerShell como Administrador.

**OPÇÃO 2: Script Automático**

```powershell
# Execute no PowerShell como Administrador
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"
.\install_tools.ps1
```

---

## ⚠️ **OBSERVAÇÕES IMPORTANTES**

1. **Execute como Administrador**: Alguns comandos requerem privilégios de administrador
2. **Reinicie o Terminal**: Após instalações, feche e abra novamente o terminal
3. **Variáveis de Ambiente**: Algumas ferramentas podem precisar ser adicionadas ao PATH manualmente
4. **PostgreSQL**: A senha padrão será 'postgres123' se usar o Chocolatey

---

## 🎯 **VERIFICAÇÃO RÁPIDA**

Para verificar rapidamente se tudo está instalado:

```batch
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"
.\check_tools.bat
```

---

## 📝 **STATUS ATUAL DO PROJETO**

Com base no que observei:

- ✅ **Node.js**: Funcional (projeto React rodando)
- ✅ **NPM**: Funcional (dependências instaladas)
- ✅ **Git**: Provavelmente instalado (repositório funcionando)
- ❓ **Python**: Precisa verificação
- ❓ **PostgreSQL**: Precisa verificação
- ❓ **Poetry**: Precisa verificação

Execute a verificação para confirmar o status exato!
