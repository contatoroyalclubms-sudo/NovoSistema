# 🧪 COMANDOS DE TESTE CORRETOS

## ✅ PROBLEMA IDENTIFICADO:

Você precisa estar no diretório correto para cada comando

## 🎯 COMANDOS CORRETOS:

### BACKEND (Terminal 1):

```powershell
# Navegar para backend
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\backend"

# Verificar se está no lugar certo
Test-Path pyproject.toml

# Iniciar backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### FRONTEND (Terminal 2):

```powershell
# Navegar para frontend
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\frontend"

# Verificar se está no lugar certo
Test-Path package.json

# Instalar dependências (se necessário)
npm install

# Iniciar frontend
npm run dev
```

---

## 🔧 SCRIPT AUTOMATIZADO:

### INICIAR BACKEND:

```powershell
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\backend"
if (Test-Path pyproject.toml) {
    Write-Host "✅ Backend encontrado, iniciando..." -ForegroundColor Green
    poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} else {
    Write-Host "❌ Arquivo pyproject.toml não encontrado!" -ForegroundColor Red
    Write-Host "Diretório atual: $(Get-Location)" -ForegroundColor Yellow
}
```

### INICIAR FRONTEND:

```powershell
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\frontend"
if (Test-Path package.json) {
    Write-Host "✅ Frontend encontrado, iniciando..." -ForegroundColor Green
    npm run dev
} else {
    Write-Host "❌ Arquivo package.json não encontrado!" -ForegroundColor Red
    Write-Host "Diretório atual: $(Get-Location)" -ForegroundColor Yellow
}
```

---

## 🚀 COMANDOS PARA EXECUTAR AGORA:

### 1. TESTE BACKEND:

```powershell
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\backend"
poetry run python -c "import app.main; print('✅ Backend OK!')"
```

### 2. TESTE FRONTEND:

```powershell
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal\frontend"
npm --version
```

---

## 📍 VERIFICAÇÃO DE DIRETÓRIOS:

Execute para verificar estrutura:

```powershell
Get-ChildItem "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema\paineluniversal" -Name
```

Resultado esperado:

- backend
- frontend

**EXECUTE ESTES COMANDOS UM POR VEZ NO TERMINAL!** 🎯
