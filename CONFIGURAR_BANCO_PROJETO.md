# ✅ POSTGRESQL JÁ INSTALADO - CONFIGURAÇÃO

## 🔍 VERIFICAÇÃO E CONFIGURAÇÃO

### PASSO 1: TESTAR SE ESTÁ FUNCIONANDO

Execute estes comandos para verificar:

```cmd
psql --version
psql -U postgres -c "SELECT version();"
```

### PASSO 2: VERIFICAR SERVIÇO

```cmd
# Verificar se o serviço está rodando
net start | findstr postgres

# Se não estiver rodando, iniciar:
net start postgresql-x64-15
```

### PASSO 3: CONFIGURAR BANCO DO PROJETO

Execute o script de configuração:

```powershell
.\setup_postgresql_db.ps1
```

### OU CONFIGURAR MANUALMENTE:

```sql
-- Conectar como postgres
psql -U postgres

-- Criar usuário do projeto
CREATE USER eventos_user WITH PASSWORD 'eventos_2024_secure!';

-- Criar banco do projeto
CREATE DATABASE eventos_db OWNER eventos_user;

-- Dar todas as permissões
GRANT ALL PRIVILEGES ON DATABASE eventos_db TO eventos_user;

-- Conectar ao banco
\c eventos_db

-- Dar permissões no schema
GRANT ALL ON SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eventos_user;

-- Instalar extensões
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Sair
\q
```

### PASSO 4: TESTAR CONEXÃO DO PROJETO

```cmd
# Testar conexão com usuário do projeto
set PGPASSWORD=eventos_2024_secure!
psql -h localhost -U eventos_user -d eventos_db -c "SELECT current_user, current_database();"
```

---

## 🚀 PRÓXIMO PASSO: TESTAR O SISTEMA COMPLETO

### BACKEND:

```cmd
cd paineluniversal\backend
poetry install
poetry run uvicorn app.main:app --reload
```

### FRONTEND:

```cmd
cd paineluniversal\frontend
npm install
npm run dev
```

### ACESSAR:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

---

## 🎯 STATUS ATUAL DO PROJETO:

✅ **POETRY**: Funcionando (v2.1.4)  
✅ **POSTGRESQL**: Instalado  
❓ **PYTHON**: Precisa confirmar  
❓ **NODE.JS**: Precisa confirmar

**VOCÊ ESTÁ MUITO PERTO DE TER TUDO FUNCIONANDO!** 🎉
