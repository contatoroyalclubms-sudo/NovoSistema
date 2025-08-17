# 🐘 CORREÇÃO: INSTALAR POSTGRESQL

## 🎯 PROBLEMA IDENTIFICADO:

PostgreSQL não está instalado ou funcionando

## 🔧 SOLUÇÃO IMEDIATA:

### MÉTODO 1: INSTALAÇÃO OFICIAL (RECOMENDADO)

#### PASSO 1: DOWNLOAD

1. Acesse: **https://www.postgresql.org/download/windows/**
2. Clique em **"Download the installer"**
3. Baixe **PostgreSQL 15.x** para Windows x86-64

#### PASSO 2: INSTALAÇÃO

1. **Execute o arquivo** como Administrador
2. **Configurações importantes**:
   - ✅ Porta: `5432` (padrão)
   - ✅ Senha do postgres: `postgres123`
   - ✅ Superuser: `postgres`
   - ✅ Locale: `Default`
   - ✅ Instalar todos os componentes

#### PASSO 3: VERIFICAÇÃO

Após instalar, teste no terminal:

```cmd
psql --version
```

---

### MÉTODO 2: WINGET (ALTERNATIVA RÁPIDA)

Se você tem Windows 10/11:

```cmd
winget install PostgreSQL.PostgreSQL
```

---

### MÉTODO 3: SCOOP (ALTERNATIVA AO CHOCOLATEY)

#### Instalar Scoop primeiro:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

#### Depois instalar PostgreSQL:

```cmd
scoop install postgresql
```

---

## ⚙️ CONFIGURAÇÃO APÓS INSTALAÇÃO:

### 1. ADICIONAR AO PATH (se necessário):

```powershell
$env:PATH += ";C:\Program Files\PostgreSQL\15\bin"
```

### 2. INICIAR SERVIÇO:

```cmd
# Windows Service
net start postgresql-x64-15

# Ou via Services.msc
services.msc
```

### 3. TESTAR CONEXÃO:

```cmd
# Teste básico
psql --version

# Teste de conexão
psql -U postgres

# Teste com comando
psql -U postgres -c "SELECT version();"
```

---

## 🏁 CONFIGURAR BANCO DO PROJETO:

Após PostgreSQL funcionar, execute:

### CRIAR USUÁRIO E BANCO:

```sql
-- Conectar como postgres
psql -U postgres

-- Criar usuário
CREATE USER eventos_user WITH PASSWORD 'eventos_2024_secure!';

-- Criar banco
CREATE DATABASE eventos_db OWNER eventos_user;

-- Dar permissões
GRANT ALL PRIVILEGES ON DATABASE eventos_db TO eventos_user;

-- Sair
\q
```

### OU USAR SCRIPT AUTOMATIZADO:

```powershell
.\setup_postgresql_db.ps1
```

---

## ✅ VERIFICAÇÃO FINAL:

Teste estes comandos:

```cmd
# 1. Versão
psql --version

# 2. Conexão admin
psql -U postgres -c "SELECT version();"

# 3. Conexão do projeto
set PGPASSWORD=eventos_2024_secure!
psql -h localhost -U eventos_user -d eventos_db -c "SELECT current_user;"
```

**Resultado esperado:**

```
psql (PostgreSQL) 15.x
PostgreSQL 15.x on x86_64-pc-windows
eventos_user
```

---

## 🚨 TROUBLESHOOTING:

### SE "psql não reconhecido":

- Reinicie o terminal
- Adicione ao PATH: `C:\Program Files\PostgreSQL\15\bin`

### SE "serviço não inicia":

- Abra `services.msc`
- Procure "postgresql"
- Clique direito > Iniciar

### SE "conexão falha":

- Verifique senha
- Confirme porta 5432
- Teste: `telnet localhost 5432`

---

**QUAL MÉTODO VOCÊ PREFERE TENTAR PRIMEIRO?**
