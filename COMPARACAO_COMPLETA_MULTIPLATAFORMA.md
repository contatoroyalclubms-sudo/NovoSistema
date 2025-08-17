# COMPARACAO COMPLETA: LINUX vs MACOS vs WINDOWS

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

## SCRIPT MACOS ORIGINAL (Homebrew):

```bash
#!/bin/bash
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
brew install postgresql@15
brew services start postgresql@15
brew install python@3.12
brew install node@20
curl -sSL https://install.python-poetry.org | python3 -
```

## EQUIVALENTE WINDOWS CRIADO:

```powershell
# Verificar/Instalar Chocolatey (= Homebrew/EPEL)
if (!(Test-CommandExists "choco")) {
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Instalar ferramentas (comandos equivalentes)
choco install postgresql15 -y      # = brew install postgresql@15 / dnf install postgresql15
choco install python312 -y         # = brew install python@3.12 / dnf install python3.12
choco install nodejs-lts -y        # = brew install node@20 / dnf install nodejs
(Invoke-WebRequest poetry) | python # = curl poetry | python3 (IDENTICO!)

# Configurar servicos
Start-Service postgresql*           # = brew services start / systemctl start
Set-Service -StartupType Automatic  # = brew services / systemctl enable
```

## TABELA DE EQUIVALENCIAS:

| Funcao          | Linux (dnf/RHEL)                       | macOS (Homebrew)                    | Windows (Chocolatey)                 |
| --------------- | -------------------------------------- | ----------------------------------- | ------------------------------------ |
| **Gerenciador** | `sudo dnf install epel-release`        | `brew install`                      | `choco install`                      |
| **PostgreSQL**  | `sudo dnf install postgresql15-server` | `brew install postgresql@15`        | `choco install postgresql15`         |
| **Iniciar PG**  | `sudo systemctl start postgresql-15`   | `brew services start postgresql@15` | `Start-Service postgresql*`          |
| **Auto-start**  | `sudo systemctl enable postgresql-15`  | `brew services` (automatico)        | `Set-Service -StartupType Automatic` |
| **Python**      | `sudo dnf install python3.12`          | `brew install python@3.12`          | `choco install python312`            |
| **Node.js**     | `curl NodeSource + dnf nodejs`         | `brew install node@20`              | `choco install nodejs-lts`           |
| **Poetry**      | `curl poetry \| python3`               | `curl poetry \| python3`            | `Invoke-WebRequest poetry \| python` |
| **Verificacao** | `psql --version`                       | `psql --version`                    | `psql --version`                     |

## ARQUIVOS CRIADOS:

### SCRIPTS EQUIVALENTES:

- `install_linux_equivalent.ps1` - Baseado no script dnf/RHEL
- `install_macos_equivalent.ps1` - Baseado no script Homebrew/macOS
- `install_fixed.ps1` - Versao simplificada sem emojis
- `install_tools.bat` - Versao batch para maxima compatibilidade

### COMO EXECUTAR (ESCOLHA UM):

#### OPCAO 1 - Equivalente Linux:

```powershell
.\install_linux_equivalent.ps1
```

#### OPCAO 2 - Equivalente macOS:

```powershell
.\install_macos_equivalent.ps1
```

#### OPCAO 3 - Versao Simples:

```powershell
.\install_fixed.ps1
```

#### OPCAO 4 - Arquivo Batch:

```cmd
# Clique direito -> Executar como Admin
install_tools.bat
```

#### OPCAO 5 - Comandos Diretos:

```powershell
# Como Administrador:
choco install postgresql15 python312 nodejs-lts git -y
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

---

## RESULTADO FINAL:

**O mesmo ambiente de desenvolvimento em Linux, macOS e Windows!**

✅ PostgreSQL 15+  
✅ Python 3.12+  
✅ Node.js 20+  
✅ Poetry  
✅ Git

**Multiplataforma = Mesmo codigo, mesmas ferramentas, mesma experiencia!** 🚀
