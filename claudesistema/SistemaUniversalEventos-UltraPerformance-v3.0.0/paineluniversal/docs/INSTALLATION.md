# 🛠️ GUIA COMPLETO DE INSTALAÇÃO

## 📋 **Pré-requisitos**

### Sistema Operacional Suportado

- ✅ Windows 10/11
- ✅ macOS 12+
- ✅ Ubuntu 20.04+
- ✅ Debian 11+
- ✅ CentOS 8+

### Software Necessário

- 🐍 **Python 3.11+** - [Download](https://python.org/downloads)
- 📦 **Node.js 18+** - [Download](https://nodejs.org/download)
- 🎯 **Git** - [Download](https://git-scm.com/downloads)
- 🗄️ **PostgreSQL 14+** (Opcional) - [Download](https://postgresql.org/download)

### Hardware Recomendado

- 💾 RAM: Mínimo 4GB, Recomendado 8GB+
- 💿 Armazenamento: 2GB livres
- 🖥️ CPU: Dual-core 2.0GHz+

---

## 🚀 **Instalação Rápida (Recomendado)**

### 1️⃣ **Clone do Repositório**

```bash
# Clone o repositório
git clone https://github.com/contatoroyalclubms-sudo/NovoSistema.git
cd NovoSistema

# Verifique se está na branch correta
git checkout main
```

### 2️⃣ **Configuração Automática (Windows)**

```powershell
# Execute o script de instalação automática
.\scripts\installation\install-windows.ps1
```

### 3️⃣ **Configuração Automática (Linux/macOS)**

```bash
# Torne o script executável
chmod +x scripts/installation/install-linux.sh

# Execute a instalação
./scripts/installation/install-linux.sh
```

### 4️⃣ **Verificação da Instalação**

```bash
# Teste se tudo está funcionando
.\scripts\development\health-check.ps1  # Windows
./scripts/development/health-check.sh   # Linux/macOS
```

---

## 🔧 **Instalação Manual Detalhada**

### 📚 **Etapa 1: Configuração do Backend**

#### 1.1 Navegue para o diretório do backend

```bash
cd paineluniversal/backend
```

#### 1.2 Crie e ative o ambiente virtual

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 1.3 Instale as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 1.4 Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
# Exemplo de configuração mínima:
```

**.env:**

```env
# Configurações básicas
APP_NAME="Sistema Universal de Eventos"
DEBUG=True
SECRET_KEY="sua-chave-secreta-muito-segura-aqui"

# Banco de dados (SQLite para desenvolvimento)
DATABASE_URL="sqlite:///./eventos.db"
# Para PostgreSQL: DATABASE_URL="postgresql://user:password@localhost/eventos_db"

# Redis (opcional para desenvolvimento)
REDIS_URL="redis://localhost:6379"

# JWT
JWT_SECRET_KEY="sua-jwt-secret-key-aqui"
JWT_ALGORITHM="HS256"
JWT_EXPIRE_MINUTES=30

# API Externa (opcional)
WHATSAPP_API_TOKEN=""
N8N_WEBHOOK_URL=""
```

#### 1.5 Configure o banco de dados

```bash
# Crie as tabelas
python -m alembic upgrade head

# Popule com dados de exemplo
python seed_database.py
```

### 🌐 **Etapa 2: Configuração do Frontend**

#### 2.1 Navegue para o diretório do frontend

```bash
cd ../frontend  # Se estiver em backend/
# ou
cd paineluniversal/frontend  # Se estiver na raiz
```

#### 2.2 Instale as dependências

```bash
npm install
# ou
yarn install
```

#### 2.3 Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env.local
```

**.env.local:**

```env
# API Backend
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws

# Configurações da aplicação
VITE_APP_NAME="Sistema Universal de Eventos"
VITE_APP_VERSION="2.0.0"

# Features opcionais
VITE_ENABLE_GAMIFICATION=true
VITE_ENABLE_WHATSAPP=true
VITE_ENABLE_ANALYTICS=true
```

### 🗄️ **Etapa 3: Configuração do Banco PostgreSQL (Opcional)**

#### 3.1 Instale o PostgreSQL

**Windows:**

```powershell
# Use o chocolatey
choco install postgresql

# Ou baixe do site oficial
# https://www.postgresql.org/download/windows/
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**

```bash
# Use o Homebrew
brew install postgresql
brew services start postgresql
```

#### 3.2 Configure o banco

```bash
# Execute o script de configuração
.\scripts\database\setup-postgresql.ps1  # Windows
./scripts/database/setup-postgresql.sh   # Linux/macOS
```

#### 3.3 Atualize a string de conexão

```env
# No arquivo .env do backend
DATABASE_URL="postgresql://eventos_user:senha123@localhost/eventos_db"
```

---

## 🚀 **Executando o Sistema**

### 🎯 **Método 1: Execução Manual**

#### Terminal 1 - Backend:

```bash
cd paineluniversal/backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
python -m uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 - Frontend:

```bash
cd paineluniversal/frontend
npm run dev
```

### 🎯 **Método 2: Scripts Automatizados**

**Windows:**

```powershell
.\scripts\development\start-dev.ps1
```

**Linux/macOS:**

```bash
./scripts/development/start-dev.sh
```

### 🎯 **Método 3: Docker (Recomendado para Produção)**

```bash
# Desenvolvimento
docker-compose -f docker-compose.dev.yml up -d

# Produção
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🌐 **Acessando o Sistema**

Após a inicialização bem-sucedida:

- **🖥️ Frontend:** http://localhost:3000
- **⚡ Backend API:** http://localhost:8000
- **📚 Documentação API:** http://localhost:8000/docs
- **📊 Dashboard Admin:** http://localhost:3000/admin

### 🔐 **Credenciais Padrão**

**Administrador:**

- Email: `admin@sistema.com`
- Senha: `admin123`

**Usuário Demo:**

- Email: `demo@sistema.com`
- Senha: `demo123`

---

## 🧪 **Verificação da Instalação**

### ✅ **Testes Básicos**

```bash
# Teste o backend
curl http://localhost:8000/health

# Teste a autenticação
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}'

# Teste o frontend (deve retornar HTML)
curl http://localhost:3000
```

### ✅ **Script de Verificação Completa**

```bash
# Execute o script de verificação
.\scripts\utilities\verify-installation.ps1  # Windows
./scripts/utilities/verify-installation.sh   # Linux/macOS
```

---

## 🐛 **Solução de Problemas Comuns**

### ❌ **Erro: Python não encontrado**

**Solução:**

```bash
# Windows - Instale do Microsoft Store ou python.org
# Verifique a instalação
python --version
```

### ❌ **Erro: Node.js não encontrado**

**Solução:**

```bash
# Instale do site oficial: nodejs.org
# Verifique a instalação
node --version
npm --version
```

### ❌ **Erro: Porta já em uso**

**Solução:**

```bash
# Windows - Encontre e mate o processo
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
sudo lsof -ti:8000 | xargs kill -9
```

### ❌ **Erro: Banco de dados não conecta**

**Solução:**

```bash
# Verifique se o PostgreSQL está rodando
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Teste a conexão
psql -h localhost -U eventos_user -d eventos_db
```

### ❌ **Erro: Dependências não instalam**

**Solução:**

```bash
# Limpe o cache
pip cache purge
npm cache clean --force

# Reinstale
pip install -r requirements.txt --force-reinstall
npm install --force
```

---

## 🔄 **Atualizando o Sistema**

```bash
# Atualize o código
git pull origin main

# Atualize dependências do backend
cd paineluniversal/backend
pip install -r requirements.txt --upgrade

# Atualize dependências do frontend
cd ../frontend
npm update

# Execute migrações se necessário
cd ../backend
python -m alembic upgrade head
```

---

## 📞 **Suporte**

Se você encontrar problemas durante a instalação:

1. 📖 Consulte nossa [seção de troubleshooting](TROUBLESHOOTING.md)
2. 🔍 Verifique as [issues no GitHub](https://github.com/contatoroyalclubms-sudo/NovoSistema/issues)
3. 💬 Entre em contato no nosso Discord
4. 📧 Envie um email para suporte@sistema.com

---

**⚡ Instalação rápida concluída! Seu sistema está pronto para uso! 🎉**
