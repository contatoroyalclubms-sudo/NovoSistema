# 🚀 Guia Completo de Instalação e Configuração

## Sistema Universal de Gestão de Eventos

Este guia irá te ajudar a configurar e executar o Sistema de Gestão de Eventos em diferentes ambientes.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação Rápida](#instalação-rápida)
3. [Instalação Manual](#instalação-manual)
4. [Configuração do Ambiente](#configuração-do-ambiente)
5. [Executando o Sistema](#executando-o-sistema)
6. [Docker](#docker)
7. [Solução de Problemas](#solução-de-problemas)
8. [Scripts Úteis](#scripts-úteis)

## 🔧 Pré-requisitos

### Instalação Automática

Para instalar automaticamente todas as dependências, execute:

**Windows:**

```powershell
# Execute como Administrador
powershell -ExecutionPolicy Bypass -File "setup.ps1"
```

**Linux/macOS:**

```bash
chmod +x setup.sh
./setup.sh
```

### Instalação Manual

#### Dependências Obrigatórias

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Poetry** - [Instalação](https://python-poetry.org/docs/#installation)
- **Git** - [Download](https://git-scm.com/)

#### Dependências Opcionais

- **Docker & Docker Compose** - Para execução em containers
- **Make** - Para comandos automatizados (Linux/macOS)

## ⚡ Instalação Rápida

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd NovoSistema
```

### 2. Execute o Script de Setup

```powershell
# Windows
.\setup.ps1

# Linux/macOS
./setup.sh
```

### 3. Inicie o Sistema

```powershell
# Windows
.\start-dev.ps1

# Linux/macOS
./start-dev.sh
```

### 4. Acesse a Aplicação

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🔧 Instalação Manual

### 1. Configurar PostgreSQL

#### Windows

```powershell
# Instalar PostgreSQL
choco install postgresql15 --params '/Password:postgres'

# Ou baixar do site oficial e instalar
# https://www.postgresql.org/download/windows/
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS

```bash
brew install postgresql@15
brew services start postgresql@15
```

### 2. Configurar Banco de Dados

```sql
-- Conectar como postgres
sudo -u postgres psql

-- Criar usuário e banco
CREATE USER eventos_user WITH PASSWORD 'eventos_2024_secure!';
CREATE DATABASE eventos_db OWNER eventos_user;
GRANT ALL PRIVILEGES ON DATABASE eventos_db TO eventos_user;

-- Conectar ao banco eventos_db
\c eventos_db

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";
```

### 3. Configurar Backend (Python)

```bash
cd backend

# Instalar Poetry (se não instalado)
curl -sSL https://install.python-poetry.org | python3 -

# Configurar Poetry
poetry config virtualenvs.in-project true

# Instalar dependências
poetry install --with dev

# Copiar e configurar .env
cp .env.example .env
# Editar .env com suas configurações
```

### 4. Configurar Frontend (React)

```bash
cd frontend

# Instalar dependências
npm install

# Copiar e configurar .env
cp .env.example .env
# Editar .env com suas configurações
```

## 🔧 Configuração do Ambiente

### Arquivo .env do Backend (backend/.env)

```env
# Database
DATABASE_URL=postgresql://eventos_user:eventos_2024_secure!@localhost:5432/eventos_db

# Security
SECRET_KEY=your-super-secret-key-change-in-production-eventos2024!
ENVIRONMENT=development
DEBUG=true

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0
```

### Arquivo .env do Frontend (frontend/.env)

```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# App Configuration
VITE_APP_NAME="Sistema de Gestão de Eventos"
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=development
```

## 🚀 Executando o Sistema

### Opção 1: Scripts de Inicialização (Recomendado)

**Windows:**

```powershell
.\start-dev.ps1
```

**Linux/macOS:**

```bash
./start-dev.sh
```

### Opção 2: Comandos Separados

**Backend:**

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm run dev
```

### Opção 3: Usando Makefile (Linux/macOS)

```bash
make dev          # Inicia desenvolvimento
make test         # Executa testes
make build        # Build para produção
make help         # Mostra ajuda
```

### Opção 4: PowerShell Functions (Windows)

```powershell
# Carregar funções utilitárias
. .\dev-commands.ps1

# Comandos disponíveis
Initialize-Project    # Setup completo
Start-Development     # Inicia desenvolvimento
Run-Tests            # Executa testes
Test-Health          # Verifica saúde
Show-Help            # Mostra ajuda
```

## 🐳 Docker

### Desenvolvimento com Docker

```bash
# Iniciar todos os serviços
docker-compose up --build

# Iniciar em background
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### Produção com Docker

```bash
# Copiar arquivo de ambiente
cp .env.example.prod .env.prod
# Editar .env.prod com valores de produção

# Iniciar em produção
docker-compose -f docker-compose.prod.yml up --build
```

### Serviços Incluídos

- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e sessões
- **Backend** - API FastAPI
- **Frontend** - Interface React
- **Nginx** - Proxy reverso e load balancer
- **Prometheus** - Monitoramento (profile: monitoring)
- **Grafana** - Dashboards (profile: monitoring)
- **PgAdmin** - Gerenciamento de banco (profile: tools)

### Profiles Docker

```bash
# Desenvolvimento básico
docker-compose up

# Com ferramentas de desenvolvimento
docker-compose --profile tools up

# Com monitoramento
docker-compose --profile monitoring up

# Completo
docker-compose --profile tools --profile monitoring up
```

## 🔍 Solução de Problemas

### PostgreSQL não inicia

```bash
# Windows
net start postgresql-x64-15

# Linux
sudo systemctl start postgresql
sudo systemctl status postgresql

# macOS
brew services start postgresql@15
```

### Erro de permissão no PostgreSQL

```sql
-- Conectar como postgres e executar:
GRANT ALL PRIVILEGES ON DATABASE eventos_db TO eventos_user;
GRANT ALL ON SCHEMA public TO eventos_user;
```

### Porta já em uso

```bash
# Verificar processos usando as portas
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/macOS

# Matar processo se necessário
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Linux/macOS
```

### Problemas com Node.js/npm

```bash
# Limpar cache npm
npm cache clean --force

# Reinstalar dependências
rm -rf node_modules package-lock.json
npm install

# Verificar versão do Node
node --version  # Deve ser 18+
```

### Problemas com Poetry

```bash
# Reinstalar ambiente virtual
poetry env remove python
poetry install --with dev

# Verificar ambiente
poetry env info
poetry show
```

### Erro de CORS

Verifique se o `ALLOWED_ORIGINS` no backend inclui a URL do frontend:

```env
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### Banco não conecta

1. Verifique se PostgreSQL está rodando
2. Confirme usuário e senha
3. Teste conexão manual:

```bash
psql -h localhost -U eventos_user -d eventos_db
```

## 📜 Scripts Úteis

### Windows (PowerShell)

```powershell
.\setup.ps1           # Setup inicial completo
.\start-dev.ps1       # Inicia desenvolvimento
.\backup-db.ps1       # Backup do banco
.\reset-env.ps1       # Reseta ambiente
```

### Linux/macOS (Bash)

```bash
./setup.sh            # Setup inicial completo
./start-dev.sh         # Inicia desenvolvimento
./backup-db.sh         # Backup do banco
./reset-env.sh         # Reseta ambiente
```

### Comandos Make (Linux/macOS)

```bash
make help             # Ajuda
make install          # Instalar dependências
make dev              # Desenvolvimento
make test             # Executar testes
make build            # Build produção
make docker-dev       # Docker desenvolvimento
make docker-prod      # Docker produção
make db-backup        # Backup banco
make health           # Verificar saúde
```

### PowerShell Functions (Windows)

```powershell
# Carregar primeiro
. .\dev-commands.ps1

# Então usar:
init                  # Alias para Initialize-Project
dev                   # Alias para Start-Development
test                  # Alias para Run-Tests
help                  # Alias para Show-Help
```

## 🔧 Comandos de Manutenção

### Atualizar Dependências

```bash
# Backend
cd backend
poetry update

# Frontend
cd frontend
npm update
```

### Executar Migrações

```bash
cd backend
poetry run alembic upgrade head
```

### Criar Nova Migração

```bash
cd backend
poetry run alembic revision --autogenerate -m "Descrição da migração"
```

### Backup do Banco

```bash
# Manual
pg_dump -h localhost -U eventos_user -d eventos_db > backup.sql

# Usando script
.\backup-db.ps1      # Windows
./backup-db.sh       # Linux/macOS
```

### Monitoramento

- **Grafana:** http://localhost:3001 (admin/admin123)
- **Prometheus:** http://localhost:9090
- **PgAdmin:** http://localhost:5050 (admin@eventos.local/admin123)

## 📊 URLs Importantes

### Desenvolvimento

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **API Schema:** http://localhost:8000/openapi.json

### Docker com Monitoramento

- **Grafana:** http://localhost:3001
- **Prometheus:** http://localhost:9090
- **PgAdmin:** http://localhost:5050

### Health Checks

- **Backend Health:** http://localhost:8000/health
- **Frontend:** http://localhost:3000

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs:** `docker-compose logs` ou arquivos em `logs/`
2. **Execute health check:** Scripts incluem verificação de saúde
3. **Consulte este guia:** Solução de problemas comuns incluída
4. **Reset o ambiente:** Use `reset-env.ps1` ou `reset-env.sh`

## 🎉 Pronto!

Agora você tem o Sistema de Gestão de Eventos funcionando!

**Próximos passos:**

1. Explore a documentação da API em http://localhost:8000/docs
2. Configure os dados iniciais através da interface
3. Personalize conforme suas necessidades

Boa codificação! 🚀
