# COMPARACAO SCRIPT LINUX vs WINDOWS

## SCRIPT LINUX ORIGINAL (dnf/RHEL):

```bash
#!/bin/bash
sudo dnf install epel-release -y
sudo dnf install postgresql15-server postgresql15 -y
sudo postgresql-15-setup initdb
sudo systemctl enable postgresql-15
sudo systemctl start postgresql-15
sudo dnf install python3.12 python3.12-pip -y
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install nodejs -y
curl -sSL https://install.python-poetry.org | python3 -
```

## EQUIVALENTE WINDOWS CRIADO:

```powershell
# Chocolatey = EPEL
choco install postgresql15 -y
Set-Service postgresql* -StartupType Automatic
choco install python312 -y
choco install nodejs-lts -y
(Invoke-WebRequest poetry-installer) | python -
```

## MAPEAMENTO COMANDO A COMANDO:

| Linux (dnf/RHEL)                       | Windows (PowerShell/Choco)           |
| -------------------------------------- | ------------------------------------ | ---------------------------- |
| `sudo dnf install epel-release`        | `Install Chocolatey`                 |
| `sudo dnf install postgresql15-server` | `choco install postgresql15`         |
| `sudo postgresql-15-setup initdb`      | `Configuracao automatica`            |
| `sudo systemctl enable postgresql-15`  | `Set-Service -StartupType Automatic` |
| `sudo systemctl start postgresql-15`   | `Start-Service`                      |
| `sudo dnf install python3.12`          | `choco install python312`            |
| `curl NodeSource setup + dnf nodejs`   | `choco install nodejs-lts`           |
| `curl poetry installer                 | python3`                             | `Invoke-WebRequest + python` |

## COMO EXECUTAR:

### OPCAO 1 - Script Equivalente:

```powershell
# Como Administrador:
.\install_linux_equivalent.ps1
```

### OPCAO 2 - Comandos Diretos:

```powershell
# Como Administrador:
choco install postgresql15 python312 nodejs-lts git -y
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### OPCAO 3 - Arquivo Batch:

```cmd
# Clique direito -> Executar como Admin:
install_tools.bat
```

---

**RESULTADO: As mesmas ferramentas do script Linux, adaptadas para Windows!**
