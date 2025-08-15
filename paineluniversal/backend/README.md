# Backend - Sistema de Gestão de Eventos

API FastAPI para o sistema de gestão de eventos.

## 🛠️ Tecnologias

- Python 3.12+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Poetry
- JWT Authentication

## 🚀 Como Executar

```bash
# Instalar dependências
poetry install

# Executar migrações
poetry run python create_*.py

# Desenvolvimento
poetry run uvicorn app.main:app --reload

# Testes
poetry run pytest --cov=app
```

## 📁 Estrutura

```
app/
├── routers/          # Endpoints da API
├── services/         # Lógica de negócio
├── models.py         # Modelos SQLAlchemy
├── schemas.py        # Schemas Pydantic
├── database.py       # Configuração do banco
├── auth.py           # Autenticação JWT
├── middleware.py     # Middlewares
└── main.py           # Aplicação principal
```

## 🔧 Configuração

Crie um arquivo .env com as seguintes variáveis:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📊 Endpoints Principais

- /auth - Autenticação
- /eventos - Gestão de eventos
- /checkins - Check-ins
- /pdv - PDV e vendas
- /dashboard - Dashboard e relatórios
- /gamificacao - Sistema de gamificação
