# 🛠️ FASE 2: Infraestrutura e DevOps

## 📋 Checklist de Implementação

### 1. Containerização Docker

#### 1.1 Backend Dockerfile
- [ ] **Arquivo:** `paineluniversal/backend/Dockerfile`
- [ ] Multi-stage build para otimização
- [ ] Poetry para gestão de dependências
- [ ] Health checks configurados

#### 1.2 Frontend Dockerfile  
- [ ] **Arquivo:** `paineluniversal/frontend/Dockerfile`
- [ ] Build otimizado com Nginx
- [ ] Compressão de assets
- [ ] Cache layers configurados

#### 1.3 Docker Compose
- [ ] **Arquivo:** `paineluniversal/docker-compose.yml` (produção)
- [ ] **Arquivo:** `paineluniversal/docker-compose.dev.yml` (desenvolvimento)
- [ ] PostgreSQL configurado
- [ ] Redis para cache
- [ ] Volumes persistentes
- [ ] Networks isoladas

### 2. Configuração de Ambiente

#### 2.1 Environment Variables
- [ ] **Backend:** `backend/.env.example`
- [ ] **Frontend:** `frontend/.env.example`
- [ ] Documentação das variáveis
- [ ] Validação de configurações

#### 2.2 Scripts de Automação
- [ ] **Setup:** `setup.sh`
- [ ] **Desenvolvimento:** `start-dev.sh`
- [ ] **Produção:** `deploy.sh`
- [ ] **Backup:** `backup.sh`

### 3. Database Setup

#### 3.1 Migrações
- [ ] **Arquivo:** `backend/alembic.ini`
- [ ] Configuração do Alembic
- [ ] Scripts de migração automática
- [ ] Rollback procedures

#### 3.2 Seeds e Dados Iniciais
- [ ] **Arquivo:** `backend/seeds/initial_data.py`
- [ ] Empresa padrão
- [ ] Usuário admin
- [ ] Dados de exemplo
- [ ] Conquistas padrão

## 🐳 Templates Docker

### Backend Dockerfile
```dockerfile
# paineluniversal/backend/Dockerfile
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
# paineluniversal/frontend/Dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy environment script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost || exit 1

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose
```yaml
# paineluniversal/docker-compose.yml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://eventos_user:eventos_pass@postgres:5432/eventos_db
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api
    depends_on:
      - backend
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: eventos_db
      POSTGRES_USER: eventos_user
      POSTGRES_PASSWORD: eventos_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U eventos_user -d eventos_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: eventos_network
```

## 📜 Scripts de Automação

### Setup Script
```bash
#!/bin/bash
# paineluniversal/setup.sh

echo "🚀 Configurando Sistema de Eventos..."

# Verificar dependências
command -v docker >/dev/null 2>&1 || { echo "❌ Docker não encontrado. Instale o Docker primeiro."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose não encontrado."; exit 1; }

# Criar arquivos .env se não existirem
if [ ! -f backend/.env ]; then
    echo "📝 Criando backend/.env..."
    cp backend/.env.example backend/.env
    echo "⚠️  Configure as variáveis em backend/.env"
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Criando frontend/.env..."
    cp frontend/.env.example frontend/.env
fi

# Gerar SECRET_KEY se não existir
if ! grep -q "SECRET_KEY=" backend/.env; then
    SECRET_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY=$SECRET_KEY" >> backend/.env
    echo "✅ SECRET_KEY gerada automaticamente"
fi

# Build e start containers
echo "🐳 Construindo containers..."
docker-compose build

echo "🚀 Iniciando serviços..."
docker-compose up -d postgres redis

# Aguardar banco estar pronto
echo "⏳ Aguardando PostgreSQL..."
sleep 10

# Executar migrações
echo "📊 Executando migrações..."
docker-compose exec backend poetry run python create_initial_data.py

echo "✅ Setup concluído!"
echo ""
echo "🌐 URLs:"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Para iniciar o desenvolvimento:"
echo "./start-dev.sh"
```

### Development Script
```bash
#!/bin/bash
# paineluniversal/start-dev.sh

echo "🔧 Iniciando ambiente de desenvolvimento..."

# Verificar se containers estão rodando
if ! docker-compose ps | grep -q "Up"; then
    echo "🐳 Iniciando containers de infraestrutura..."
    docker-compose up -d postgres redis
    sleep 5
fi

# Iniciar backend em modo desenvolvimento
echo "🐍 Iniciando backend..."
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Aguardar backend iniciar
sleep 3

# Iniciar frontend
echo "⚛️  Iniciando frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Ambiente de desenvolvimento iniciado!"
echo ""
echo "🌐 URLs:"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 Para parar os serviços:"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo "docker-compose down"

# Aguardar interrupção
trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait
```

## 📊 Cronograma Fase 2

| Tarefa | Estimativa | Status |
|--------|------------|--------|
| Dockerfile backend | 1 dia | ⏳ |
| Dockerfile frontend | 1 dia | ⏳ |
| Docker Compose | 1 dia | ⏳ |
| Scripts de automação | 1 dia | ⏳ |
| Configuração de ambiente | 1 dia | ⏳ |
| Testes de deploy | 1 dia | ⏳ |
| Documentação | 1 dia | ⏳ |

**Total:** 7 dias (1 semana)