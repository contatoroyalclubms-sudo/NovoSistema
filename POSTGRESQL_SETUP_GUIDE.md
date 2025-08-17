# CONFIGURACAO POSTGRESQL - SISTEMA DE EVENTOS

# Equivalente Windows ao script bash fornecido

## SCRIPT BASH ORIGINAL:

```bash
#!/bin/bash
echo "🚀 Configurando PostgreSQL para o Sistema de Eventos..."

sudo -u postgres psql << EOF
CREATE USER eventos_user WITH PASSWORD 'eventos_2024_secure!';
CREATE DATABASE eventos_db OWNER eventos_user;
GRANT ALL PRIVILEGES ON DATABASE eventos_db TO eventos_user;
\c eventos_db
GRANT ALL ON SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eventos_user;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";
\l
\du
EOF

PGPASSWORD='eventos_2024_secure!' psql -h localhost -U eventos_user -d eventos_db -c "SELECT version();"
```

## EQUIVALENTE WINDOWS:

### SCRIPT AUTOMATIZADO:

Execute: `setup_postgresql_db.ps1`

### COMANDOS MANUAIS:

#### 1. CONFIGURACAO INICIAL:

```powershell
# Criar arquivo SQL com comandos:
@"
CREATE USER eventos_user WITH PASSWORD 'eventos_2024_secure!';
CREATE DATABASE eventos_db OWNER eventos_user;
GRANT ALL PRIVILEGES ON DATABASE eventos_db TO eventos_user;
"@ | Out-File setup_inicial.sql

# Executar:
psql -U postgres -f setup_inicial.sql
```

#### 2. CONFIGURACAO DO BANCO:

```powershell
# Criar arquivo SQL para o banco:
@"
GRANT ALL ON SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eventos_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eventos_user;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";
"@ | Out-File setup_banco.sql

# Executar no banco eventos_db:
psql -U postgres -d eventos_db -f setup_banco.sql
```

#### 3. TESTE DE CONEXAO:

```powershell
# Equivalente ao PGPASSWORD:
$env:PGPASSWORD='eventos_2024_secure!'
psql -h localhost -U eventos_user -d eventos_db -c "SELECT version();"
Remove-Item Env:PGPASSWORD
```

## MAPEAMENTO COMPLETO:

| BASH                    | WINDOWS POWERSHELL                                |
| ----------------------- | ------------------------------------------------- |
| `sudo -u postgres psql` | `psql -U postgres`                                |
| `psql << EOF ... EOF`   | `commands \| Out-File temp.sql; psql -f temp.sql` |
| `PGPASSWORD='...' psql` | `$env:PGPASSWORD='...'; psql`                     |
| `if [ $? -eq 0 ]`       | `if ($LASTEXITCODE -eq 0)`                        |
| `echo "✅ Success"`     | `Write-Host "✅ Success" -ForegroundColor Green`  |
| `exit 1`                | `exit 1`                                          |

## INFORMACOES DE CONEXAO:

**Banco de Dados:** `eventos_db`  
**Usuario:** `eventos_user`  
**Senha:** `eventos_2024_secure!`  
**Host:** `localhost`

## COMANDOS DE VERIFICACAO:

### LISTAR BANCOS:

```powershell
psql -U postgres -c "\l"
```

### LISTAR USUARIOS:

```powershell
psql -U postgres -c "\du"
```

### TESTAR CONEXAO:

```powershell
$env:PGPASSWORD='eventos_2024_secure!'
psql -h localhost -U eventos_user -d eventos_db -c "SELECT current_database(), current_user;"
Remove-Item Env:PGPASSWORD
```

### VERIFICAR EXTENSOES:

```powershell
$env:PGPASSWORD='eventos_2024_secure!'
psql -h localhost -U eventos_user -d eventos_db -c "\dx"
Remove-Item Env:PGPASSWORD
```

## TROUBLESHOOTING:

### SE PSQL NAO FOR RECONHECIDO:

```powershell
# Adicionar PostgreSQL ao PATH:
$env:PATH += ";C:\Program Files\PostgreSQL\15\bin"
```

### SE CONEXAO FALHAR:

```powershell
# Verificar servico:
Get-Service postgresql*

# Iniciar se necessario:
Start-Service postgresql*

# Testar conexao local:
psql -U postgres
```

### ALTERAR SENHA DO POSTGRES:

```powershell
psql -U postgres -c "ALTER USER postgres PASSWORD 'nova_senha';"
```

---

**RESULTADO: O mesmo banco configurado, mas usando comandos Windows!** 🚀🐘
