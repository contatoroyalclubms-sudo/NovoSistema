# 📚 FASE 7: Documentação e Deploy

## 📋 Checklist de Implementação

### 1. API Documentation

#### 1.1 OpenAPI Enhancement
- [ ] **Arquivo:** `backend/app/main.py` (melhorias na documentação)
- [ ] Descrições detalhadas de endpoints
- [ ] Exemplos de request/response
- [ ] Documentação de códigos de erro
- [ ] Guias de autenticação

#### 1.2 Interactive Documentation
- [ ] **Pasta:** `docs/api/`
- [ ] Swagger UI customizado
- [ ] Redoc personalizado
- [ ] Postman collections
- [ ] SDK documentation

### 2. User Documentation

#### 2.1 User Guides
- [ ] **Arquivo:** `docs/user-guide/installation.md`
- [ ] **Arquivo:** `docs/user-guide/user-manual.md`
- [ ] **Arquivo:** `docs/user-guide/api-reference.md`
- [ ] **Arquivo:** `docs/user-guide/troubleshooting.md`
- [ ] **Arquivo:** `docs/user-guide/faq.md`

#### 2.2 Developer Documentation
- [ ] **Arquivo:** `docs/development/setup.md`
- [ ] **Arquivo:** `docs/development/architecture.md`
- [ ] **Arquivo:** `docs/development/contributing.md`
- [ ] **Arquivo:** `docs/development/testing.md`

### 3. Production Deploy

#### 3.1 CI/CD Pipeline
- [ ] **Arquivo:** `.github/workflows/ci.yml`
- [ ] **Arquivo:** `.github/workflows/deploy.yml`
- [ ] Automated testing
- [ ] Build process
- [ ] Deployment stages
- [ ] Rollback procedures

#### 3.2 Monitoring Setup
- [ ] **Pasta:** `monitoring/`
- [ ] Health checks
- [ ] Performance monitoring
- [ ] Error tracking
- [ ] Log aggregation

## 📖 Templates - Documentation

### Enhanced OpenAPI Configuration
```python
# backend/app/main.py (melhorias na documentação)
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Sistema de Gestão de Eventos",
    description="""
    ## Sistema Universal de Gestão de Eventos
    
    Esta API fornece funcionalidades completas para gestão de eventos, incluindo:
    
    * **Autenticação** - Sistema JWT com 2FA opcional
    * **Eventos** - CRUD completo com vinculação de promoters
    * **Vendas** - Sistema completo de transações e PDV
    * **Check-ins** - Check-in inteligente via CPF
    * **Financeiro** - Controle de caixa e movimentações
    * **Gamificação** - Rankings e conquistas
    * **Relatórios** - Exportação em múltiplos formatos
    
    ### Autenticação
    
    A API utiliza JWT (JSON Web Tokens) para autenticação. Para obter um token:
    
    1. Faça POST em `/api/auth/login` com CPF e senha
    2. Use o token retornado no header `Authorization: Bearer {token}`
    
    ### Códigos de Status
    
    * `200` - Sucesso
    * `201` - Criado com sucesso
    * `400` - Erro de validação
    * `401` - Não autenticado
    * `403` - Sem permissão
    * `404` - Não encontrado
    * `422` - Erro de validação de dados
    * `500` - Erro interno do servidor
    
    ### Rate Limiting
    
    A API possui rate limiting de 60 requests por minuto por IP.
    
    ### Suporte
    
    Para suporte técnico, entre em contato através de:
    * Email: suporte@eventos.com
    * Documentação: https://docs.eventos.com
    """,
    version="1.0.0",
    contact={
        "name": "Equipe de Desenvolvimento",
        "email": "dev@eventos.com",
        "url": "https://eventos.com/contato"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    servers=[
        {
            "url": "https://api.eventos.com",
            "description": "Servidor de Produção"
        },
        {
            "url": "https://staging-api.eventos.com",
            "description": "Servidor de Staging"
        },
        {
            "url": "http://localhost:8000",
            "description": "Desenvolvimento Local"
        }
    ]
)

# Customizar OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Adicionar exemplos para modelos comuns
    openapi_schema["components"]["examples"] = {
        "UsuarioExample": {
            "summary": "Exemplo de usuário",
            "value": {
                "nome": "João Silva",
                "email": "joao@exemplo.com",
                "cpf": "123.456.789-01",
                "telefone": "(11) 99999-9999",
                "tipo": "promoter"
            }
        },
        "EventoExample": {
            "summary": "Exemplo de evento",
            "value": {
                "nome": "Festa de Ano Novo",
                "descricao": "Celebração de Ano Novo com música ao vivo",
                "data_evento": "2024-12-31T22:00:00",
                "local": "Club XYZ",
                "endereco": "Rua das Festas, 123",
                "limite_idade": 18,
                "capacidade_maxima": 500
            }
        }
    }
    
    # Adicionar tags com descrições
    openapi_schema["tags"] = [
        {
            "name": "Autenticação",
            "description": "Endpoints para login, logout e gestão de tokens"
        },
        {
            "name": "Eventos",
            "description": "CRUD de eventos e vinculação de promoters"
        },
        {
            "name": "Usuários",
            "description": "Gestão de usuários do sistema"
        },
        {
            "name": "PDV",
            "description": "Sistema de ponto de venda"
        },
        {
            "name": "Check-ins",
            "description": "Sistema de check-in de participantes"
        },
        {
            "name": "Dashboard",
            "description": "Métricas e relatórios em tempo real"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Documentação customizada
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentação Interativa",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentação",
        redoc_js_url="https://unpkg.com/redoc@2.0.0/bundles/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico"
    )
```

### User Manual Template
```markdown
# Manual do Usuário - Sistema de Gestão de Eventos

## Índice

1. [Introdução](#introdução)
2. [Primeiros Passos](#primeiros-passos)
3. [Gestão de Eventos](#gestão-de-eventos)
4. [Sistema de Vendas](#sistema-de-vendas)
5. [Check-in de Participantes](#check-in-de-participantes)
6. [Relatórios e Analytics](#relatórios-e-analytics)
7. [Configurações](#configurações)
8. [Solução de Problemas](#solução-de-problemas)

## Introdução

O Sistema de Gestão de Eventos é uma plataforma completa para organização e controle de eventos. Com ele você pode:

- Criar e gerenciar eventos
- Controlar vendas de ingressos
- Fazer check-in de participantes
- Acompanhar métricas em tempo real
- Gerar relatórios detalhados
- Gerenciar equipe de promoters

## Primeiros Passos

### 1. Acesso ao Sistema

1. Acesse o sistema através do link fornecido
2. Digite seu CPF no formato `000.000.000-00`
3. Digite sua senha
4. Clique em "Entrar"

> **Dica:** Se você esqueceu sua senha, clique em "Esqueci minha senha" para receber um código de recuperação via WhatsApp.

### 2. Navegação Inicial

Após o login, você verá o **Dashboard** com as principais métricas:

- **Total de Eventos** - Eventos ativos
- **Vendas do Dia** - Vendas realizadas hoje
- **Check-ins Realizados** - Participantes que já fizeram check-in
- **Receita Total** - Receita acumulada

### 3. Menu Principal

O menu lateral contém as principais funcionalidades:

- 🏠 **Dashboard** - Visão geral das métricas
- 🎉 **Eventos** - Gestão de eventos
- 💰 **Vendas** - Sistema de vendas de ingressos
- ✅ **Check-in** - Check-in de participantes
- 📊 **Relatórios** - Relatórios e analytics
- ⚙️ **Configurações** - Configurações do sistema

## Gestão de Eventos

### Criando um Novo Evento

1. Clique em **"Eventos"** no menu lateral
2. Clique no botão **"+ Novo Evento"**
3. Preencha as informações:
   - **Nome do Evento** - Nome que aparecerá nos ingressos
   - **Descrição** - Detalhes do evento (opcional)
   - **Data e Hora** - Quando o evento acontecerá
   - **Local** - Nome do local
   - **Endereço** - Endereço completo
   - **Idade Mínima** - Idade mínima para participar
   - **Capacidade** - Número máximo de participantes
4. Clique em **"Salvar"**

### Gerenciando Listas de Ingressos

Cada evento pode ter diferentes tipos de lista:

- **VIP** - Ingressos premium
- **Free** - Entrada gratuita
- **Pagante** - Ingressos pagos
- **Promoter** - Lista de promoters
- **Aniversário** - Lista especial para aniversariantes
- **Desconto** - Lista com desconto

Para criar uma nova lista:

1. Acesse o evento desejado
2. Clique na aba **"Listas"**
3. Clique em **"+ Nova Lista"**
4. Configure o tipo, preço e limite de vendas
5. Salve as alterações

### Vinculando Promoters

1. No evento, clique na aba **"Promoters"**
2. Clique em **"+ Vincular Promoter"**
3. Selecione o promoter
4. Defina a meta de vendas
5. Configure a comissão (%)
6. Confirme a vinculação

## Sistema de Vendas

### Vendendo Ingressos

1. Acesse **"Vendas"** no menu
2. Selecione o evento
3. Escolha a lista de ingressos
4. Preencha os dados do comprador:
   - Nome completo
   - CPF (obrigatório para check-in)
   - Email
   - Telefone
5. Selecione a forma de pagamento
6. Confirme a venda

### PDV (Ponto de Venda)

O PDV permite vendas no local do evento:

1. Acesse **"PDV"** no menu
2. Selecione o evento
3. Adicione produtos ao carrinho
4. Processe o pagamento
5. Imprima o comprovante

### Comandas

Para eventos com consumação:

1. No PDV, clique em **"Nova Comanda"**
2. Digite o CPF do participante
3. Adicione créditos à comanda
4. O participante pode consumir até o limite

## Check-in de Participantes

### Check-in Manual

1. Acesse **"Check-in"** no menu
2. Digite o CPF do participante
3. Verifique as informações exibidas
4. Clique em **"Confirmar Check-in"**

### Check-in por QR Code

1. Use o leitor de QR Code
2. Aponte para o QR Code do ingresso
3. O sistema confirmará automaticamente

### Check-in Mobile

Para check-in em dispositivos móveis:

1. Acesse **"Check-in Mobile"**
2. Use a câmera para ler QR Codes
3. Funciona offline (sincroniza quando volta online)

## Relatórios e Analytics

### Dashboard Avançado

O dashboard avançado mostra:

- Gráficos de vendas por período
- Performance de promoters
- Métricas de check-in
- Análise financeira

### Exportando Relatórios

1. Acesse **"Relatórios"**
2. Selecione o tipo de relatório:
   - Vendas por evento
   - Performance de promoters
   - Check-ins por horário
   - Relatório financeiro
3. Configure o período
4. Escolha o formato (PDF, Excel, CSV)
5. Clique em **"Exportar"**

## Configurações

### Configurações Gerais

- **Dados da Empresa** - Logo, nome, CNPJ
- **Notificações** - Configurar alertas
- **Integrações** - WhatsApp, N8N

### Gestão de Usuários

Apenas administradores podem:

- Criar novos usuários
- Definir permissões
- Ativar/desativar contas

### Backup e Segurança

- Backup automático diário
- Logs de auditoria
- Conformidade com LGPD

## Solução de Problemas

### Problemas Comuns

**Não consigo fazer login**
- Verifique se o CPF está no formato correto
- Confirme se a senha está correta
- Tente recuperar a senha via WhatsApp

**Check-in não funciona**
- Verifique se o CPF foi cadastrado na venda
- Confirme se o evento está ativo
- Verifique a conexão com a internet

**Relatório não carrega**
- Aguarde alguns segundos (relatórios grandes podem demorar)
- Tente reduzir o período consultado
- Verifique se você tem permissão para o relatório

### Contato para Suporte

- **Email:** suporte@eventos.com
- **WhatsApp:** (11) 99999-9999
- **Horário:** Segunda a Sexta, 9h às 18h

---

*Última atualização: Dezembro 2024*
```

## 🚀 CI/CD Pipeline

### GitHub Actions CI
```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: eventos_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      working-directory: ./backend
      run: |
        poetry install
    
    - name: Run linting
      working-directory: ./backend
      run: |
        poetry run flake8 app/
        poetry run black --check app/
        poetry run isort --check-only app/
    
    - name: Run security check
      working-directory: ./backend
      run: |
        poetry run safety check
        poetry run bandit -r app/
    
    - name: Run tests
      working-directory: ./backend
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/eventos_test
        REDIS_URL: redis://localhost:6379
        SECRET_KEY: test-secret-key
      run: |
        poetry run pytest --cov=app --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
        name: backend-coverage

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: './frontend/package-lock.json'
    
    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Run linting
      working-directory: ./frontend
      run: |
        npm run lint
        npm run type-check
    
    - name: Run tests
      working-directory: ./frontend
      run: npm run test:coverage
    
    - name: Build
      working-directory: ./frontend
      run: npm run build
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info
        flags: frontend
        name: frontend-coverage

  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

### Deployment Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/')
    
    environment: production
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push backend image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: eventos-backend
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG ./backend
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
    
    - name: Build and push frontend image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: eventos-frontend
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG ./frontend
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service \
          --cluster eventos-cluster \
          --service eventos-backend-service \
          --force-new-deployment
        
        aws ecs update-service \
          --cluster eventos-cluster \
          --service eventos-frontend-service \
          --force-new-deployment
    
    - name: Wait for deployment
      run: |
        aws ecs wait services-stable \
          --cluster eventos-cluster \
          --services eventos-backend-service eventos-frontend-service
    
    - name: Run smoke tests
      run: |
        curl -f https://api.eventos.com/healthz
        curl -f https://eventos.com
    
    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      if: always()
```

## 📊 Cronograma Fase 7

| Tarefa | Estimativa | Status |
|--------|------------|--------|
| Enhanced OpenAPI documentation | 1 dia | ⏳ |
| User manual creation | 2 dias | ⏳ |
| Developer documentation | 1 dia | ⏳ |
| CI/CD pipeline setup | 2 dias | ⏳ |
| Monitoring implementation | 1 dia | ⏳ |
| Production deployment | 1 dia | ⏳ |

**Total:** 8 dias (1.6 semanas)

## 🎯 Documentation Checklist

- [ ] **API Docs** - 100% endpoints documentados
- [ ] **User Manual** - Guia completo para usuários
- [ ] **Developer Guide** - Documentação técnica
- [ ] **Deployment Guide** - Instruções de deploy
- [ ] **Troubleshooting** - Soluções para problemas comuns
- [ ] **Video Tutorials** - Tutoriais em vídeo (opcional)