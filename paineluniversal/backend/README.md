# Sistema de Gestão Universal - Backend API

## 🚀 Visão Geral

Backend completo em FastAPI para sistema de gestão de eventos, PDV, estoque e gamificação com integração de IA.

## ✨ Principais Funcionalidades

### 🎯 **Sistema de Eventos**

- CRUD completo de eventos
- Upload de imagens
- Sistema de convidados e listas
- Notificações em tempo real
- Estatísticas avançadas

### 🛒 **Sistema PDV & Estoque**

- Gestão completa de produtos
- Controle de estoque em tempo real
- Movimentações e relatórios
- Categorização de produtos
- Alertas de estoque baixo

### 🎮 **Sistema de Gamificação**

- Sistema de XP e níveis
- Badges e conquistas
- Rankings de promoters
- Métricas de performance

### 🤖 **Integração com IA (OpenAI)**

- Geração automática de descrições de eventos
- Copy de marketing personalizado
- Análise de feedback
- Geração de ideias de eventos

### 📊 **Relatórios e Analytics**

- Relatórios financeiros
- Análise de vendas
- Métricas de performance
- Dashboards interativos

## 🛠️ Instalação

### 1. **Pré-requisitos**

```bash
# Python 3.8+
python --version

# pip atualizado
python -m pip install --upgrade pip
```

### 2. **Clonagem e Setup**

```bash
# Clonar repositório
git clone <repository-url>
cd NovoSistema/paineluniversal/backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. **Instalação Rápida**

```bash
# Executar script de instalação
install_deps.bat

# OU instalar manualmente:
pip install fastapi uvicorn sqlalchemy psycopg2-binary
pip install pydantic python-multipart
pip install openai python-jose[cryptography] passlib[bcrypt]
```

### 4. **Configuração**

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar variáveis de ambiente
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

## 🔧 Configuração de Ambiente

### **Variáveis de Ambiente (.env)**

```env
# Banco de Dados
DATABASE_URL=postgresql://postgres:password@localhost:5432/sistema_eventos
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/sistema_eventos

# Segurança
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=1500
OPENAI_TEMPERATURE=0.7

# Configurações da API
API_V1_STR=/api/v1
PROJECT_NAME=Sistema de Gestão Universal
DEBUG=True

# Upload de Arquivos
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
```

## 🚀 Execução

### **Desenvolvimento**

```bash
# Iniciar servidor de desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Com logs detalhados
uvicorn app.main:app --reload --log-level debug
```

### **Produção**

```bash
# Usar Gunicorn para produção
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📚 Estrutura da API

### **Endpoints Principais**

#### 🎯 **Eventos**

```
GET    /api/v1/eventos/                 # Listar eventos
POST   /api/v1/eventos/                 # Criar evento
GET    /api/v1/eventos/{id}             # Obter evento
PUT    /api/v1/eventos/{id}             # Atualizar evento
DELETE /api/v1/eventos/{id}             # Deletar evento

# IA para Eventos
POST   /api/v1/eventos/{id}/ai/generate-description    # Gerar descrição
POST   /api/v1/eventos/{id}/ai/generate-marketing      # Gerar copy marketing
POST   /api/v1/eventos/{id}/ai/analyze-feedback        # Analisar feedback
```

#### 🛒 **Estoque**

```
GET    /api/v1/estoque/produtos/        # Listar produtos
POST   /api/v1/estoque/produtos/        # Criar produto
GET    /api/v1/estoque/produtos/{id}    # Obter produto
PUT    /api/v1/estoque/produtos/{id}    # Atualizar produto

GET    /api/v1/estoque/relatorio/       # Relatório de estoque
GET    /api/v1/estoque/alertas/         # Alertas de estoque
POST   /api/v1/estoque/movimentacao/    # Registrar movimentação
```

#### 🎮 **Gamificação**

```
GET    /api/v1/gamificacao/ranking/     # Ranking de promoters
GET    /api/v1/gamificacao/conquistas/  # Conquistas disponíveis
POST   /api/v1/gamificacao/xp/          # Adicionar XP
GET    /api/v1/gamificacao/dashboard/   # Dashboard de gamificação
```

#### 💰 **PDV**

```
POST   /api/v1/pdv/venda/               # Processar venda
GET    /api/v1/pdv/vendas/              # Listar vendas
GET    /api/v1/pdv/relatorio/           # Relatório de vendas
POST   /api/v1/pdv/caixa/abrir/         # Abrir caixa
POST   /api/v1/pdv/caixa/fechar/        # Fechar caixa
```

### **Status e Monitoramento**

```
GET    /api/v1/eventos/system/status    # Status do sistema
GET    /docs                            # Documentação Swagger
GET    /redoc                           # Documentação ReDoc
```

## 🔐 Autenticação

### **Login**

```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

### **Uso do Token**

```bash
# Header de Authorization
Authorization: Bearer <seu-jwt-token>
```

## 🤖 Integração OpenAI

### **Configuração**

```python
# Configurar chave da API no .env
OPENAI_API_KEY=sk-proj-your-key-here

# Ou configurar programaticamente
from app.core.openai_config import OpenAIConfig
config = OpenAIConfig()
```

### **Funcionalidades IA**

- **Descrições de Eventos**: Geração automática baseada em título, categoria e local
- **Copy de Marketing**: Adaptado para diferentes plataformas (Facebook, Instagram, LinkedIn)
- **Análise de Feedback**: Análise de sentimento e insights de comentários
- **Ideias de Eventos**: Sugestões baseadas em categoria, público-alvo e orçamento

## 📊 Banco de Dados

### **Modelos Principais**

- **Usuario**: Gestão de usuários e permissões
- **Evento**: Eventos e suas propriedades
- **Produto**: Produtos para PDV e estoque
- **VendaPDV**: Transações de venda
- **MovimentoEstoque**: Movimentações de estoque
- **PromoterXP**: Sistema de gamificação

### **Migrações**

```bash
# Executar migrações
alembic upgrade head

# Criar nova migração
alembic revision --autogenerate -m "Descrição da mudança"
```

## 🧪 Testes

### **Validação do Sistema**

```bash
# Executar validação completa
python -m app.services.validation_service

# Testar endpoint de status
curl http://localhost:8000/api/v1/eventos/system/status
```

### **Testes Unitários**

```bash
# Instalar pytest
pip install pytest pytest-asyncio

# Executar testes
pytest tests/
```

## 📈 Monitoramento

### **Logs**

```python
# Configuração de logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### **Métricas**

- Response times por endpoint
- Uso de recursos
- Erros e exceções
- Estatísticas de uso da IA

## 🔧 Troubleshooting

### **Problemas Comuns**

#### 1. **Erro de Importação**

```bash
# Verificar se está no ambiente virtual
which python
pip list
```

#### 2. **Erro de Conexão com Banco**

```bash
# Verificar configuração DATABASE_URL
echo $DATABASE_URL
```

#### 3. **OpenAI não Funciona**

```bash
# Verificar chave da API
python -c "from app.services.openai_service import OpenAIService; print(OpenAIService().config.get_api_key())"
```

### **Debug Mode**

```bash
# Ativar modo debug
export DEBUG=True
uvicorn app.main:app --reload --log-level debug
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Changelog

### **v2.0.0** (Atual)

- ✅ Sistema completo de eventos
- ✅ Integração OpenAI para IA
- ✅ Sistema PDV e estoque
- ✅ Gamificação com XP e badges
- ✅ Relatórios e analytics
- ✅ Sistema de autenticação JWT

### **v1.0.0**

- ✅ CRUD básico de eventos
- ✅ Sistema de usuários
- ✅ API REST básica

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

- **Email**: support@example.com
- **Documentação**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Status**: [http://localhost:8000/api/v1/eventos/system/status](http://localhost:8000/api/v1/eventos/system/status)

---

**Desenvolvido com ❤️ usando FastAPI + OpenAI**
