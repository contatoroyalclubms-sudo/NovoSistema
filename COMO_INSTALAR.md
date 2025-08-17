# INSTRUCOES PARA INSTALAR AS FERRAMENTAS

## PROBLEMA IDENTIFICADO:

- Voce esta em C:\WINDOWS\system32 (diretorio errado)
- Existe um erro no perfil do PowerShell

## SOLUCAO SIMPLES:

### OPCAO 1 - Usar arquivo .bat (RECOMENDADO):

1. Abra o Explorer do Windows
2. Navegue ate: `c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema`
3. Clique com botao direito em `install_tools.bat`
4. Selecione "Executar como administrador"

### OPCAO 2 - Via PowerShell:

```powershell
# 1. Navegar para o projeto primeiro:
cd "c:\Users\User\OneDrive\Desktop\projetos github\NovoSistema"

# 2. Executar o script:
.\install_fixed.ps1
```

### OPCAO 3 - Comandos diretos:

```powershell
# Como Administrador, execute:
choco install python312 nodejs-lts postgresql15 git -y
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

## CORRIGIR ERRO DO PERFIL (OPCIONAL):

Se quiser corrigir o erro do perfil do PowerShell:

```powershell
notepad $PROFILE
# Procure por linha com erro de sintaxe e corrija
```

## PROXIMOS PASSOS APOS INSTALACAO:

1. Backend: `cd paineluniversal\backend && poetry install`
2. Frontend: `cd paineluniversal\frontend && npm install`
3. Executar: Backend (`poetry run uvicorn app.main:app --reload`) + Frontend (`npm run dev`)

---

**RECOMENDACAO: Use o arquivo install_tools.bat - e mais simples e confiavel!**
