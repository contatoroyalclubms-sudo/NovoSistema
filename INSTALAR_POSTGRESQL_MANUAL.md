# ========================================================

# INSTALAÇÃO MANUAL DO POSTGRESQL - SEM CHOCOLATEY

# ========================================================

## MÉTODO 1: DOWNLOAD DIRETO (RECOMENDADO)

### PASSO 1: BAIXAR POSTGRESQL

1. Acesse: https://www.postgresql.org/download/windows/
2. Clique em "Download the installer"
3. Baixe a versão 15.x para Windows x86-64

### PASSO 2: INSTALAR

1. Execute o arquivo baixado como ADMINISTRADOR
2. Configurações recomendadas:
   - Porta: 5432 (padrão)
   - Senha do postgres: `postgres123`
   - Locale: Default
   - Componentes: Marque todos

### PASSO 3: VERIFICAR

Após instalação, teste no terminal:

```cmd
psql --version
```

---

## MÉTODO 2: WINGET (ALTERNATIVA)

Se você tem Windows 10/11 recente:

```cmd
winget install PostgreSQL.PostgreSQL
```

---

## MÉTODO 3: SCOOP (ALTERNATIVA AO CHOCOLATEY)

### Instalar Scoop:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

### Instalar PostgreSQL via Scoop:

```cmd
scoop install postgresql
```

---

## CONFIGURAÇÃO APÓS INSTALAÇÃO

### ADICIONAR AO PATH (se necessário):

```powershell
$env:PATH += ";C:\Program Files\PostgreSQL\15\bin"
```

### INICIAR SERVIÇO:

```cmd
net start postgresql-x64-15
```

### TESTAR CONEXÃO:

```cmd
psql -U postgres
```

---

## RESOLVER CHOCOLATEY (OPCIONAL)

### REINSTALAR CHOCOLATEY:

```powershell
# Remover instalação anterior
Remove-Item -Path $env:ChocolateyInstall -Recurse -Force

# Reinstalar
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

---

## VERIFICAÇÃO FINAL

Após instalar PostgreSQL, teste:

```cmd
psql --version
psql -U postgres -c "SELECT version();"
```

Resultado esperado:

```
psql (PostgreSQL) 15.x
PostgreSQL 15.x on x86_64-pc-windows, compiled by Visual C++
```
