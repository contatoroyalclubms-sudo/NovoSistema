# COMANDOS NET START POSTGRESQL PARA WINDOWS

## SEU COMANDO:

```cmd
# O serviço já deve estar rodando após a instalação
net start postgresql-x64-15
```

## EQUIVALENTES E ALTERNATIVAS:

### COMANDO DIRETO (NET):

```cmd
# Como Administrador:
net start postgresql-x64-15
```

### COMANDO POWERSHELL:

```powershell
# Como Administrador:
Start-Service postgresql-x64-15
```

### VERIFICAR SE ESTÁ RODANDO:

```cmd
# Listar serviços ativos:
net start | findstr postgresql
```

```powershell
# Ver todos os serviços PostgreSQL:
Get-Service postgresql*
```

### COMANDOS RELACIONADOS:

#### PARAR SERVIÇO:

```cmd
net stop postgresql-x64-15
```

```powershell
Stop-Service postgresql-x64-15
```

#### REINICIAR SERVIÇO:

```cmd
net stop postgresql-x64-15
net start postgresql-x64-15
```

```powershell
Restart-Service postgresql-x64-15
```

#### AUTO-INÍCIO:

```powershell
# Configurar para iniciar automaticamente:
Set-Service postgresql-x64-15 -StartupType Automatic
```

## SCRIPT AUTOMATIZADO:

Execute o arquivo: `net_start_postgresql.ps1`

## VARIAÇÕES COMUNS DO NOME DO SERVIÇO:

Dependendo da instalação, o serviço pode ter nomes diferentes:

- `postgresql-x64-15` (mais comum)
- `postgresql-15`
- `PostgreSQL`
- `postgresql-x64-14` (versão anterior)

## DIAGNÓSTICO COMPLETO:

### LISTAR TODOS OS SERVIÇOS POSTGRESQL:

```powershell
Get-Service | Where-Object {$_.Name -like "*postgres*" -or $_.DisplayName -like "*PostgreSQL*"}
```

### VERIFICAR STATUS DETALHADO:

```powershell
Get-Service postgresql* | Format-Table Name, Status, StartType, DisplayName -AutoSize
```

### INICIAR TODOS OS SERVIÇOS POSTGRESQL:

```powershell
Get-Service postgresql* | Start-Service
```

## EXEMPLO DE USO COMPLETO:

```powershell
# 1. Verificar se existe
Get-Service postgresql*

# 2. Iniciar se necessário
Start-Service postgresql-x64-15

# 3. Configurar auto-início
Set-Service postgresql-x64-15 -StartupType Automatic

# 4. Verificar status final
Get-Service postgresql-x64-15
```

---

**OBSERVAÇÃO**: Como você mencionou, "o serviço já deve estar rodando após a instalação", então este comando é principalmente para casos onde o serviço foi parado manualmente.

**DICA**: Use `Get-Service postgresql*` primeiro para ver o nome exato do serviço na sua instalação.
