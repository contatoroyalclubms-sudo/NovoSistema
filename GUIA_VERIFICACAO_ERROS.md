# ============================================================================

# GUIA MANUAL: COMO VERIFICAR SE HÁ ERROS NO SCRIPT DE INSTALAÇÃO

# ============================================================================

## 🔍 PASSO 1: VERIFICAR FERRAMENTAS EXISTENTES

Abra um **PowerShell** ou **CMD** e execute estes comandos:

```cmd
python --version
node --version
npm --version
git --version
psql --version
poetry --version
choco --version
```

**RESULTADO ESPERADO:**

- Se algum comando **funcionar** = Ferramenta já instalada ✅
- Se algum comando **der erro** = Ferramenta precisa ser instalada ❌

---

## 🛡️ PASSO 2: EXECUTAR SCRIPT COMO ADMINISTRADOR

### Método 1: Botão Direito

1. **Clique com botão direito** no arquivo `install_as_admin.ps1`
2. Selecione **"Executar com PowerShell"**
3. Se aparecer UAC, clique **"SIM"**

### Método 2: PowerShell Admin

1. **Abra PowerShell como Administrador**
2. Digite: `cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"`
3. Digite: `Set-ExecutionPolicy Bypass -Scope Process`
4. Digite: `.\install_as_admin.ps1`

### Método 3: CMD Admin

1. **Abra CMD como Administrador**
2. Digite: `cd /d "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"`
3. Digite: `powershell -ExecutionPolicy Bypass -File install_as_admin.ps1`

---

## ⚠️ POSSÍVEIS ERROS E SOLUÇÕES

### ERRO 1: "Execution Policy"

```
SOLUÇÃO:
Set-ExecutionPolicy Bypass -Scope Process -Force
```

### ERRO 2: "Chocolatey não instalou"

```
SOLUÇÃO MANUAL:
1. Abra PowerShell como Admin
2. Execute:
   Set-ExecutionPolicy Bypass -Scope Process -Force
   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
   iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```

### ERRO 3: "Python não funciona após instalação"

```
SOLUÇÃO:
1. Feche TODOS os terminais
2. Abra um NOVO terminal
3. Teste: python --version
```

### ERRO 4: "Poetry não instala"

```
SOLUÇÃO MANUAL:
pip install poetry
```

### ERRO 5: "PostgreSQL não inicia"

```
SOLUÇÃO:
1. Abra "Serviços" do Windows (services.msc)
2. Procure por "postgresql"
3. Clique com botão direito > Iniciar
```

---

## 🧪 PASSO 3: TESTAR FERRAMENTAS APÓS INSTALAÇÃO

Execute estes comandos em um **NOVO terminal** (não Admin):

```cmd
python --version
node --version
npm --version
git --version
psql --version
poetry --version
```

**TODOS devem funcionar!**

---

## 🚀 PASSO 4: INICIAR O DESENVOLVIMENTO

Se todas as ferramentas funcionarem:

### Terminal 1 - Backend:

```cmd
cd "paineluniversal\backend"
poetry install
poetry run uvicorn app.main:app --reload
```

### Terminal 2 - Frontend:

```cmd
cd "paineluniversal\frontend"
npm install
npm run dev
```

### Acessar:

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000/docs

---

## 📋 CHECKLIST DE VERIFICAÇÃO

- [ ] **Chocolatey instalado**: `choco --version`
- [ ] **Python funcionando**: `python --version`
- [ ] **Node.js funcionando**: `node --version`
- [ ] **Git funcionando**: `git --version`
- [ ] **PostgreSQL funcionando**: `psql --version`
- [ ] **Poetry funcionando**: `poetry --version`
- [ ] **Backend iniciando**: `cd backend && poetry install`
- [ ] **Frontend iniciando**: `cd frontend && npm install`

---

## 🆘 SE NADA FUNCIONAR

Execute este comando para **instalação manual**:

```cmd
# Via Chocolatey (se instalado):
choco install python nodejs postgresql git -y

# Via instaladores diretos:
# 1. Python: https://python.org/downloads
# 2. Node.js: https://nodejs.org
# 3. Git: https://git-scm.com
# 4. PostgreSQL: https://postgresql.org/download
```

---

**💡 DICA: Sempre feche e abra um NOVO terminal após instalar ferramentas!**
