# 🧪 DOCUMENTAÇÃO DE TESTES

## Visão Geral do Framework de Testes

O sistema de eventos possui um framework abrangente de testes que garante qualidade, performance e confiabilidade em todos os níveis da aplicação.

### 📊 Estatísticas de Cobertura

| Tipo de Teste   | Cobertura      | Quantidade   | Tempo Médio |
| --------------- | -------------- | ------------ | ----------- |
| **Unitários**   | 95%+           | 150+ testes  | 2-3 min     |
| **Integração**  | 85%+           | 50+ testes   | 5-8 min     |
| **E2E**         | 80%+           | 25+ cenários | 10-15 min   |
| **Performance** | 100% endpoints | 30+ métricas | 3-5 min     |

---

## 🎯 Tipos de Teste

### 1. **Testes Unitários** (`tests/unit/`)

Testam componentes isolados do sistema.

#### **Estrutura:**

```
tests/unit/
├── test_auth.py           # Sistema de autenticação
├── test_events.py         # Gerenciamento de eventos
├── test_users.py          # Gestão de usuários
├── test_inscricoes.py     # Sistema de inscrições
├── test_checkins.py       # Check-ins e validações
├── test_gamificacao.py    # Sistema de gamificação
├── test_pdv.py           # Ponto de venda
├── test_whatsapp.py      # Integração WhatsApp
└── test_n8n.py           # Integração N8N
```

#### **Cobertura:**

- ✅ Todos os modelos de dados
- ✅ Serviços de negócio
- ✅ Validators e schemas
- ✅ Utilitários e helpers
- ✅ Funções de segurança

#### **Exemplo de Execução:**

```bash
# Executar todos os testes unitários
python -m pytest tests/unit/ -v

# Com coverage
python -m pytest tests/unit/ --cov=app --cov-report=html

# Teste específico
python -m pytest tests/unit/test_auth.py::TestAuthService::test_login_success -v
```

### 2. **Testes de Integração** (`tests/integration/`)

Testam interação entre componentes e sistemas externos.

#### **Cobertura:**

- 🔗 APIs RESTful completas
- 🔗 Integração banco de dados
- 🔗 Sistema de cache (Redis)
- 🔗 WebSockets em tempo real
- 🔗 Serviços externos (WhatsApp, N8N)
- 🔗 Sistema de arquivos
- 🔗 Autenticação e autorização

#### **Cenários Testados:**

```python
# Fluxo completo de evento
1. Criar evento (Admin)
2. Listar eventos públicos
3. Inscrever usuário
4. Realizar check-in
5. Gerar estatísticas
6. Enviar notificações

# Fluxo de gamificação
1. Ação do usuário
2. Cálculo de pontos
3. Verificação de conquistas
4. Atualização de ranking
```

### 3. **Testes End-to-End** (`tests/e2e/`)

Simulam jornadas completas de usuário no navegador.

#### **Ferramentas:**

- **Selenium WebDriver** - Automação do navegador
- **Chrome Headless** - Execução sem interface
- **Screenshots** - Captura para debug
- **Responsividade** - Testes mobile/tablet

#### **Jornadas Testadas:**

##### **👤 Jornada do Organizador:**

```
1. Login → Dashboard
2. Criar Evento → Formulário completo
3. Gerenciar Inscrições
4. Configurar Notificações
5. Visualizar Relatórios
6. Sistema PDV
```

##### **👥 Jornada do Participante:**

```
1. Navegar Eventos (sem login)
2. Cadastro de Usuário
3. Login → Perfil
4. Inscrição em Evento
5. Download de Ingresso
6. Sistema de Gamificação
```

##### **📱 Responsividade:**

```
- Mobile (375px) - iPhone
- Tablet (768px) - iPad
- Desktop (1920px) - PC
```

### 4. **Testes de Performance** (`tests/performance/`)

Avaliam desempenho, escalabilidade e limites do sistema.

#### **Métricas Monitoradas:**

```python
THRESHOLDS = {
    "api_response_time": 1.0,        # segundos
    "database_query_time": 0.5,      # segundos
    "redis_operation_time": 0.1,     # segundos
    "memory_usage_mb": 512,          # MB
    "cpu_usage_percent": 80,         # %
    "concurrent_users": 100,         # usuários
    "requests_per_second": 1000,     # RPS
    "error_rate_threshold": 0.01     # 1%
}
```

#### **Tipos de Teste:**

- **Carga Crescente** - 1→100 usuários simultâneos
- **Stress Test** - Limites do sistema
- **Endurance** - Carga sustentada (30min+)
- **Spike** - Picos súbitos de tráfego

---

## 🛠️ Configuração e Execução

### **Pré-requisitos**

```bash
# Instalar dependências
pip install -r requirements-test.txt

# Dependências principais
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-html>=3.1.0
pytest-xdist>=3.0.0
selenium>=4.0.0
locust>=2.0.0
```

### **Estrutura de Configuração**

#### **1. conftest.py** - Configuração Global

```python
# Fixtures compartilhadas
# Configuração de banco de dados
# Mocks de serviços externos
# Utilitários de teste
```

#### **2. pytest.ini** - Configuração Pytest

```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Testes unitários",
    "integration: Testes de integração",
    "e2e: Testes end-to-end",
    "performance: Testes de performance"
]
```

### **Scripts de Execução**

#### **🚀 Execução Completa**

```bash
# Todos os testes
python run_tests.py --type all

# Execução rápida (sem E2E/Performance)
python run_tests.py --quick

# Apenas unitários com coverage
python run_tests.py --type unit --verbose
```

#### **🎯 Execução Específica**

```bash
# Por tipo
python run_tests.py --type integration
python run_tests.py --type e2e --skip-e2e false
python run_tests.py --type performance

# Por marcador
pytest -m "unit and auth"
pytest -m "integration and not slow"
pytest -m "e2e and responsivo"
```

#### **📊 Com Relatórios**

```bash
# Gerar relatórios HTML
python run_tests.py --type all --open-report

# Coverage detalhado
pytest --cov-report=html --cov-report=term-missing
```

---

## 📁 Estrutura de Arquivos

```
tests/
├── conftest.py                 # Configuração global
├── pytest.ini                 # Configuração pytest
├── fixtures/
│   └── test_data.py           # Dados de teste
├── unit/                      # Testes unitários
│   ├── test_auth.py
│   ├── test_events.py
│   ├── test_users.py
│   ├── test_inscricoes.py
│   ├── test_checkins.py
│   ├── test_gamificacao.py
│   ├── test_pdv.py
│   ├── test_whatsapp.py
│   └── test_n8n.py
├── integration/               # Testes integração
│   └── test_api_integration.py
├── e2e/                       # Testes E2E
│   └── test_user_journeys.py
└── performance/               # Testes performance
    └── test_load_performance.py

# Relatórios (gerados)
test-results/
├── consolidated-report.html    # Relatório principal
├── unit-tests-report.html     # Unitários
├── integration-tests-report.html
├── e2e-tests-report.html
├── performance-tests-report.html
├── coverage/                  # Coverage HTML
└── screenshots/               # Screenshots E2E
```

---

## 🔧 Fixtures e Utilitários

### **Fixtures Principais**

#### **Banco de Dados**

```python
@pytest.fixture
def db_session():
    # Sessão isolada para cada teste

@pytest.fixture
def admin_user(db_session):
    # Usuário administrador

@pytest.fixture
def regular_user(db_session):
    # Usuário participante
```

#### **Autenticação**

```python
@pytest.fixture
def admin_headers(admin_token):
    # Headers autenticados admin

@pytest.fixture
def user_headers(user_token):
    # Headers autenticados usuário
```

#### **Dados de Teste**

```python
@pytest.fixture
def valid_event_data():
    # Dados válidos para evento

@pytest.fixture
def sample_event(db_session, admin_user):
    # Evento criado no banco

@pytest.fixture
def multiple_events(db_session, admin_user):
    # Lote de eventos para testes
```

### **Mocks de Serviços**

#### **WhatsApp Service**

```python
@pytest.fixture
def mock_whatsapp_service():
    mock = Mock()
    mock.send_message = AsyncMock(return_value={
        "success": True,
        "message_id": "msg_123"
    })
    return mock
```

#### **Redis Cache**

```python
@pytest.fixture
def mock_redis_service():
    mock = Mock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    return mock
```

---

## 📊 Relatórios e Métricas

### **Coverage Report**

- **HTML**: `htmlcov/index.html`
- **Terminal**: Resumo com linhas não cobertas
- **XML**: Para integração CI/CD

### **Relatório Consolidado**

```json
{
  "timestamp": "2024-01-20T10:30:00",
  "total_duration": 125.45,
  "summary": {
    "unit_tests": true,
    "integration_tests": true,
    "e2e_tests": true,
    "performance_tests": true,
    "security_analysis": true
  }
}
```

### **Métricas de Performance**

```json
{
  "response_times": {
    "mean": 0.25,
    "p95": 0.45,
    "p99": 0.78
  },
  "throughput": {
    "rps": 850,
    "concurrent_users": 50
  },
  "resources": {
    "memory_peak_mb": 245,
    "cpu_avg_percent": 35
  }
}
```

---

## 🚨 Troubleshooting

### **Problemas Comuns**

#### **1. Falha de Dependências**

```bash
# Reinstalar dependências
pip install -r requirements-test.txt --force-reinstall
```

#### **2. Selenium WebDriver**

```bash
# Chrome não encontrado
sudo apt-get install google-chrome-stable  # Linux
# ou baixar ChromeDriver manualmente
```

#### **3. Banco de Dados**

```bash
# Reset do banco de teste
rm test.db
python -c "from app.core.database import init_db; init_db()"
```

#### **4. Performance Tests Falhando**

```python
# Ajustar thresholds em conftest.py
PERFORMANCE_THRESHOLDS = {
    "api_response_time": 2.0,  # Aumentar limite
    # ...
}
```

### **Debug de Testes**

#### **Modo Verbose**

```bash
pytest -v -s tests/unit/test_auth.py
```

#### **Debug com PDB**

```python
def test_login():
    import pdb; pdb.set_trace()
    # Debug interativo
```

#### **Screenshots E2E**

```python
# Automático em falhas
utils.take_screenshot(driver, "failure_login")
```

---

## 📈 CI/CD Integration

### **GitHub Actions**

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run tests
        run: python run_tests.py --type all --quick
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### **Métricas de Qualidade**

- **Coverage mínimo**: 80%
- **Performance**: < 1s response time
- **Security**: Zero vulnerabilidades críticas
- **Code Quality**: Flake8 + Black compliance

---

## 🎯 Roadmap de Testes

### **Fase Atual** ✅

- [x] Framework completo implementado
- [x] Testes unitários (95% coverage)
- [x] Testes de integração
- [x] Testes E2E básicos
- [x] Testes de performance
- [x] Relatórios automatizados

### **Próximas Melhorias** 🚀

- [ ] Testes de acessibilidade (WCAG)
- [ ] Testes de segurança avançados
- [ ] Testes de compatibilidade (browsers)
- [ ] Testes de carga distribuída
- [ ] Monitoramento contínuo
- [ ] Visual regression testing

---

## 📞 Suporte

Para dúvidas sobre o framework de testes:

1. **Documentação**: Este arquivo
2. **Exemplos**: Consultar testes existentes
3. **Debug**: Usar modo verbose (`-v -s`)
4. **Issues**: Criar issue no repositório

**Contato**: Equipe de Desenvolvimento
