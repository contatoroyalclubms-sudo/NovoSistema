# 🚀 GUIA COMPLETO: SISTEMA DE EVENTOS ULTRA-MODERNO

## Setup de Desenvolvimento Cross-Platform

### 📋 RESUMO EXECUTIVO

Este projeto oferece um **sistema completo de eventos ultra-moderno** com:

- **Frontend**: React 18 + TypeScript + Vite + Design Neural
- **Backend**: FastAPI + Python + PostgreSQL
- **Design**: Sistema neural com gradientes e glass morphism
- **Cross-Platform**: Scripts de instalação para Windows, Linux e macOS

---

## 🎯 INÍCIO RÁPIDO

### 1️⃣ INSTALAR AMBIENTE (Windows)

```powershell
# Opção 1: Script automático
.\install_final.ps1

# Opção 2: Manual via Chocolatey
choco install python nodejs postgresql git -y
pip install poetry
```

### 2️⃣ CONFIGURAR BANCO DE DADOS

```powershell
# Executar script de setup
.\setup_postgresql_db.ps1

# Ou configurar manualmente:
psql -U postgres -c "CREATE USER eventos_user WITH PASSWORD 'eventos_2024_secure!';"
psql -U postgres -c "CREATE DATABASE eventos_db OWNER eventos_user;"
```

### 3️⃣ INICIAR DESENVOLVIMENTO

```powershell
# Terminal 1 - Backend
cd paineluniversal\backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd paineluniversal\frontend
npm install
npm run dev
```

### 4️⃣ ACESSAR SISTEMA

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

---

## 🛠️ FERRAMENTAS NECESSÁRIAS

| Ferramenta     | Versão | Windows    | Linux   | macOS    |
| -------------- | ------ | ---------- | ------- | -------- |
| **Python**     | 3.12+  | Chocolatey | dnf/yum | Homebrew |
| **Node.js**    | 20+    | Chocolatey | dnf/yum | Homebrew |
| **PostgreSQL** | 15+    | Chocolatey | dnf/yum | Homebrew |
| **Git**        | Latest | Chocolatey | dnf/yum | Homebrew |
| **Poetry**     | Latest | pip        | pip     | pip      |

---

## 📦 SCRIPTS DE INSTALAÇÃO

### 🪟 Windows

```powershell
# Script principal baseado em seu código
.\install_final.ps1

# Equivalente ao Linux (dnf/RHEL)
.\install_linux_equivalent.ps1

# Equivalente ao macOS (Homebrew)
.\install_macos_equivalent.ps1
```

### 🐧 Linux (RHEL/CentOS/Fedora)

```bash
# Instalar dependências
sudo dnf update -y
sudo dnf install python3.12 python3-pip nodejs npm postgresql postgresql-server git -y

# Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### 🍎 macOS

```bash
# Instalar Homebrew (se necessário)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar dependências
brew install python@3.12 node postgresql git
pip3 install poetry
```

---

## 🐘 CONFIGURAÇÃO POSTGRESQL

### Dados de Conexão

- **Banco**: `eventos_db`
- **Usuário**: `eventos_user`
- **Senha**: `eventos_2024_secure!`
- **Host**: `localhost`
- **Porta**: `5432`

### Scripts Disponíveis

```powershell
# Setup completo do banco
.\setup_postgresql_db.ps1

# Gerenciar serviço PostgreSQL
.\postgresql_service_manager.ps1

# Testar ambiente completo
.\test_environment.ps1
```

### Comandos Manuais

```powershell
# Iniciar PostgreSQL
Start-Service postgresql*

# Conectar como admin
psql -U postgres

# Testar conexão do usuário
$env:PGPASSWORD='eventos_2024_secure!'
psql -h localhost -U eventos_user -d eventos_db -c "SELECT version();"
```

---

## 🎨 SISTEMA DE DESIGN NEURAL

### Características

- **Cores**: Gradientes neurais (azul → roxo → rosa)
- **Efeitos**: Glass morphism, backdrop blur
- **Bordas**: Zero bordas brancas (100% neural)
- **Tipografia**: Fontes modernas e legíveis
- **Responsivo**: Mobile-first design

### Componentes Principais

- **UltraModernPDV**: Sistema PDV com IA
- **Dashboard Neural**: Analytics em tempo real
- **Checkin Inteligente**: QR codes e reconhecimento
- **Sistema Financeiro**: Gestão de caixa avançada

---

## 🚀 ESTRUTURA DO PROJETO

```
paineluniversal/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app principal
│   │   ├── models.py        # Modelos SQLAlchemy
│   │   ├── database.py      # Configuração DB
│   │   └── routers/         # Endpoints API
│   └── pyproject.toml       # Dependências Python
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── services/        # APIs e WebSocket
│   │   └── contexts/        # Contextos globais
│   └── package.json         # Dependências Node
└── scripts/
    ├── install_final.ps1           # Setup Windows
    ├── setup_postgresql_db.ps1     # Config banco
    └── test_environment.ps1        # Teste ambiente
```

---

## 🔧 COMANDOS DE DESENVOLVIMENTO

### Backend (FastAPI)

```bash
cd paineluniversal/backend

# Instalar dependências
poetry install

# Iniciar desenvolvimento
poetry run uvicorn app.main:app --reload

# Executar migrações
poetry run python create_financeiro_tables.py
poetry run python seed_financeiro_data.py

# Executar testes
poetry run pytest tests/
```

### Frontend (React)

```bash
cd paineluniversal/frontend

# Instalar dependências
npm install

# Iniciar desenvolvimento
npm run dev

# Build para produção
npm run build

# Executar testes
npm test
```

---

## 🔍 VERIFICAÇÃO DO AMBIENTE

### Teste Automático

```powershell
# Executar teste completo
.\test_environment.ps1
```

### Verificação Manual

```powershell
# Verificar versões
python --version    # Python 3.12+
node --version      # Node 20+
psql --version      # PostgreSQL 15+
poetry --version    # Poetry latest

# Verificar serviços
Get-Service postgresql*

# Testar banco
psql -U postgres -c "\l"
```

---

## 🌐 URLS DO SISTEMA

| Serviço         | URL                        | Descrição           |
| --------------- | -------------------------- | ------------------- |
| **Frontend**    | http://localhost:5173      | Interface principal |
| **Backend API** | http://localhost:8000      | API REST            |
| **API Docs**    | http://localhost:8000/docs | Swagger UI          |
| **WebSocket**   | ws://localhost:8000/ws     | Tempo real          |

---

## 🎯 PRÓXIMOS PASSOS

1. **Executar**: `.\test_environment.ps1`
2. **Configurar**: Banco de dados se necessário
3. **Iniciar**: Backend e frontend
4. **Acessar**: http://localhost:5173
5. **Desenvolver**: Seu sistema ultra-moderno! 🚀

---

## 📞 SUPORTE

### Troubleshooting Comum

- **PowerShell**: Execute como administrador
- **PostgreSQL**: Verifique se o serviço está rodando
- **Poetry**: Reinstale se houver problemas
- **Node**: Limpe node_modules e reinstale

### Comandos de Reset

```powershell
# Reset completo do ambiente
Remove-Item node_modules -Recurse -Force
Remove-Item .venv -Recurse -Force
npm install
poetry install
```

---

**🎉 SISTEMA NEURAL ULTRA-MODERNO PRONTO PARA DESENVOLVIMENTO!**
