# COMANDOS POSTGRESQL PARA WINDOWS

# Equivalentes aos comandos systemctl do Linux

## SEUS COMANDOS LINUX:

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
```

## EQUIVALENTES WINDOWS:

```powershell
# Como Administrador:
Start-Service postgresql*
Set-Service postgresql* -StartupType Automatic
Get-Service postgresql*
```

## SCRIPT AUTOMATIZADO:

Execute o arquivo: `postgresql_service_manager.ps1`

## COMANDOS MANUAIS COMPLETOS:

### INICIAR POSTGRESQL:

```powershell
# Equivalente: sudo systemctl start postgresql
Start-Service postgresql*
```

### HABILITAR AUTO-INICIO:

```powershell
# Equivalente: sudo systemctl enable postgresql
Set-Service postgresql* -StartupType Automatic
```

### VERIFICAR STATUS:

```powershell
# Equivalente: sudo systemctl status postgresql
Get-Service postgresql*
```

### COMANDOS ADICIONAIS:

#### PARAR POSTGRESQL:

```powershell
# Equivalente: sudo systemctl stop postgresql
Stop-Service postgresql*
```

#### REINICIAR POSTGRESQL:

```powershell
# Equivalente: sudo systemctl restart postgresql
Restart-Service postgresql*
```

#### DESABILITAR AUTO-INICIO:

```powershell
# Equivalente: sudo systemctl disable postgresql
Set-Service postgresql* -StartupType Manual
```

## MAPEAMENTO COMPLETO:

| Linux (systemctl)                      | Windows (PowerShell)                             |
| -------------------------------------- | ------------------------------------------------ |
| `sudo systemctl start postgresql`      | `Start-Service postgresql*`                      |
| `sudo systemctl stop postgresql`       | `Stop-Service postgresql*`                       |
| `sudo systemctl restart postgresql`    | `Restart-Service postgresql*`                    |
| `sudo systemctl enable postgresql`     | `Set-Service postgresql* -StartupType Automatic` |
| `sudo systemctl disable postgresql`    | `Set-Service postgresql* -StartupType Manual`    |
| `sudo systemctl status postgresql`     | `Get-Service postgresql*`                        |
| `sudo systemctl is-active postgresql`  | `(Get-Service postgresql*).Status`               |
| `sudo systemctl is-enabled postgresql` | `(Get-Service postgresql*).StartType`            |

## EXEMPLOS DE USO:

### CONFIGURACAO INICIAL (EXECUTAR UMA VEZ):

```powershell
# Como Administrador:
Start-Service postgresql*
Set-Service postgresql* -StartupType Automatic
```

### VERIFICACAO DIARIA:

```powershell
Get-Service postgresql*
```

### DIAGNOSTICO COMPLETO:

```powershell
Get-Service postgresql* | Format-Table Name, Status, StartType, DisplayName
```

---

**RESULTADO: Os mesmos comandos do Linux, adaptados para Windows!** 🚀
